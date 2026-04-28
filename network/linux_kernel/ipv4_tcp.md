# IPv4 TCP 实现

## 1. 模块架构

### 1.1 功能概述

TCP 是面向连接的可靠传输协议，提供可靠、有序、双工的字节流服务。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv4/tcp.c` | 核心 TCP 函数 |
| `net/ipv4/tcp_input.c` | TCP 输入处理 |
| `net/ipv4/tcp_output.c` | TCP 输出处理 |
| `net/ipv4/tcp_timer.c` | TCP 定时器 |
| `net/ipv4/tcp_ipv4.c` | IPv4 特定 TCP |

## 2. TCP 头结构

### 2.1 struct tcphdr

```c
// include/uapi/linux/tcp.h:25
struct tcphdr {
    __be16  source;         // 源端口
    __be16  dest;           // 目的端口
    __be32  seq;            // 序列号
    __be32  ack_seq;        // 确认序列号
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u16   res1:4,        // 保留
            doff:4,         // 数据偏移 (TCP 头长度)
            fin:1,          // FIN 标志
            syn:1,          // SYN 标志
            rst:1,          // RST 标志
            psh:1,          // PSH 标志
            ack:1,          // ACK 标志
            urg:1,          // URG 标志
            ece:1,          // ECN Echo
            cwr:1;          // Congestion Window Reduced
#endif
    __be16  window;         // 窗口大小
    __sum16 check;          // 校验和
    __be16  urg_ptr;        // 紧急指针
};
```

## 3. TCP Socket 结构

### 3.1 struct tcp_sock

```c
// include/linux/tcp.h:197
struct tcp_sock {
    struct inet_connection_sock inet_conn;  // 基类

    /* TX 热路径 (只读) */
    u32    max_window;       // 最大窗口
    u32    rcv_ssthresh;    // 接收窗口慢启动阈值
    u16    gso_segs;        // GSO 段数

    /* TXRX 热路径 (读写) */
    u32    tsoffset;        // TSO 偏移
    u32    snd_wnd;         // 发送窗口
    u32    mss_cache;       // MSS 缓存
    u32    snd_cwnd;        // 拥塞窗口
    u32    prr_out;         // PRR 发送输出
    u32    lost_out;        // 丢失计数
    u32    sacked_out;      // SACKed 计数

    /* RX 热路径 */
    u32    copied_seq;       // 已复制序列号
    u32    snd_wl1;         // 上次窗口更新的序列号
    u32    rttvar_us;      // RTT 变化
    struct rb_root out_of_order_queue;  // 乱序队列

    /* TX 发送队列 */
    u32    segs_out;        // 已发送段数
    u32    bytes_sent;      // 已发送字节
    u32    write_seq;       // 写序列号
    u32    pushed_seq;      // 已推送序列号
    struct list_head tsorted_sent_queue;  // 时间排序的发送队列
    struct sk_buff *highest_sack;        // 最高 SACK 块

    /* 关键序列号 */
    u32    rcv_nxt;        // 接收下一序列号
    u32    snd_nxt;        // 发送下一序列号
    u32    snd_una;        // 未确认的发送序列号
    u32    snd_wnd;        // 发送窗口
    u32    rcv_wnd;        // 接收窗口
    u32    snd_cwnd;        // 拥塞窗口

    /* 拥塞控制 */
    u32    snd_ssthresh;   // 慢启动阈值
    enum tcp_ca_state ca_state;  // 拥塞状态
};
```

## 4. TCP 状态机

### 4.1 TCP 状态

```c
// include/net/tcp_states.h:12
enum tcp_state {
    TCP_ESTABLISHED = 1,
    TCP_SYN_SENT,
    TCP_SYN_RECV,
    TCP_FIN_WAIT1,
    TCP_FIN_WAIT2,
    TCP_TIME_WAIT,
    TCP_CLOSE,
    TCP_CLOSE_WAIT,
    TCP_LAST_ACK,
    TCP_LISTEN,
    TCP_NEW_SYN_RECV,
};
```

### 4.2 状态转换图

```
            TCP_NEW_SYN_RECV -> TCP_SYN_RECV -> TCP_ESTABLISHED
                   |                  |                |
                   v                  v                v
              TCP_LISTEN         TCP_SYN_SENT <-----+--> TCP_FIN_WAIT1
                                                       |         |
                                                       v         v
                                                 TCP_CLOSING   TCP_FIN_WAIT2
                                                       |         |
                                                       v         v
                                                 TCP_TIME_WAIT TCP_CLOSE_WAIT
                                                       |         |
                                                       +----> TCP_LAST_ACK
                                                             |
                                                             v
                                                           TCP_CLOSE
```

## 5. 三次握手

### 5.1 主动连接 (客户端)

```c
// net/ipv4/tcp_output.c:4296
int tcp_connect(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct sk_buff *buff;

    // 1. 初始化连接
    tcp_connect_init(sk);

    // 2. 分配 SYN 数据包
    buff = tcp_stream_alloc_skb(sk, 0, GFP_KERNEL);

    // 3. 设置 TCP 头
    tcp_init_nondata_skb(buff, tp->write_seq, TCPHDR_SYN);

    // 4. 添加到发送队列
    __skb_queue_tail(&sk->sk_write_queue, buff);
    tcp_tso_collapse(sk, buff);

    // 5. 发送 SYN
    err = tcp_transmit_skb(sk, buff, 1, GFP_KERNEL);

    // 6. 更新序列号
    tp->snd_nxt = tp->write_seq;

    // 7. 启动重传定时器
    inet_csk_reset_xmit_timer(sk, ICSK_TIME_RETRANS, tout);

    return 0;
}
```

### 5.2 被动连接 (服务器)

```c
// net/ipv4/tcp_input.c:6370
int tcp_v4_syn_recv_sock(struct sock *sk, struct sk_buff *skb, ...)
{
    struct inet_request_sock *ireq;
    struct tcp_request_sock *treq;
    struct sock *newsk;

    // 1. 创建新的 sock
    newsk = tcp_create_openreq_child(sk, req, skb);
    if (!newsk) return NULL;

    // 2. 设置地址信息
    ireq = inet_rsk(req);
    treq = tcp_rsk(req);
    newsk->sk_v4_daddr = ireq->ir_rmt_addr;
    newsk->sk_v6_daddr = ireq->ir_v6_rmt_addr;

    // 3. 设置状态为 ESTABLISHED
    tcp_set_state(newsk, TCP_ESTABLISHED);

    // 4. 初始化序列号
    newsk->sk_rxhash = get_hash_from韵(&treq->ir_tx_hash_thash);
    tcp_sync_mss(newsk, dst_mtu(dst));

    // 5. 发送 SYN+ACK
    tcp_v4_send_synack(newsk, skb, req);

    return newsk;
}
```

## 6. 数据传输

### 6.1 tcp_sendmsg()

```c
// net/ipv4/tcp.c:1130
int tcp_sendmsg_locked(struct sock *sk, struct msghdr *msg, size_t size)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct sk_buff *skb;
    int mss_now, size_goal;
    int err;
    u32 snd_wnd;

    // 1. 等待连接建立
    if ((1 << sk->sk_state) & ~(TCPF_ESTABLISHED | TCPF_CLOSE_WAIT))
        return -ENOTCONN;

    // 2. 获取 MSS
    mss_now = tcp_send_mss(sk, &size_goal, msg->msg_flags);

    // 3. 主发送循环
    while (msg->msg_iovlen > 0) {
        // 复制数据到 skb
        skb = tcp_write_queue_tail(sk);
        if (skb && tcp_sk(sk)->urg_mode) {
            // 处理紧急数据
        }

        // 检查是否可以合并到现有 skb
        if (tcp_needs_collapse(sk, skb, mss_now)) {
            // 合并到现有 skb
            err = tcp_collapse_repeat(sk, skb, msg, size_goal);
        } else {
            // 创建新的 skb
            skb = tcp_stream_alloc_skb(sk, size_goal, msg->msg_flags);
            if (!skb) break;

            // 复制数据
            err = tcp_copy_data(msg, size, skb);
            if (err) break;

            // 添加到发送队列
            __skb_queue_tail(&sk->sk_write_queue, skb);
        }

        // 更新序列号
        tcp_push_pending_frames(sk);
    }

    return size - msg->msg_iovlen;
}
```

### 6.2 tcp_rcv_established()

```c
// net/ipv4/tcp_input.c:6519
int tcp_rcv_established(struct sock *sk, struct sk_buff *skb)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct tcphdr *th = tcp_hdr(skb);
    unsigned int len = skb->len;
    int copied;

    // 1. 快速路径检查
    if ((tcp_flag_word(th) & TCP_HP_BITS) == tp->pred_flags &&
        TCP_SKB_CB(skb)->seq == tp->rcv_nxt) {
        // 快速路径：按序到达，无拥塞
        goto fast_path;
    }

slow_path:
    // 慢速路径：处理乱序、拥塞等
    return tcp_slow_path(sk, skb);

fast_path:
    // 2. 处理 ACK
    if (len > th->doff * 4)
        tcp_data_queue(sk, skb);

    // 3. 更新窗口
    tcp_ack(sk, th, th->ack_seq);

    // 4. 复制数据到用户空间
    copied = tcp_copy_to_user(sk);
    if (copied > 0)
        tcp_cleanup_rbuf(sk, copied);

    return 0;
}
```

## 7. 四次挥手

### 7.1 主动关闭

```c
// net/ipv4/tcp.c:3660
int tcp_close(struct sock *sk, long timeout)
{
    // 1. 发送 FIN
    tcp_shutdown(sk, SEND_SHUTDOWN);

    // 2. 等待对方 ACK
    // 进入 TCP_FIN_WAIT1 或 TCP_LAST_ACK 状态

    return 0;
}

// net/ipv4/tcp_output.c:4154
void tcp_shutdown(struct sock *sk, int how)
{
    if ((how & SEND_SHUTDOWN) && sk->sk_state != TCP_LISTEN) {
        // 发送 FIN
        tcp_send_fin(sk);
    }
}
```

### 7.2 被动关闭

```c
// net/ipv4/tcp_input.c:6016
int tcp_rcv_state_process(struct sock *sk, struct sk_buff *skb)
{
    struct tcp_sock *tp = tcp_sk(sk);

    switch (sk->sk_state) {
    case TCP_CLOSE_WAIT:
        // 收到 FIN，发送 ACK
        tcp_send_ack(sk);
        break;

    case TCP_LAST_ACK:
        // 发送最后的 ACK
        tcp_send_ack(sk);
        tcp_done(sk);
        break;
    }

    return 0;
}
```

## 8. 拥塞控制

### 8.1 拥塞状态

```c
// include/uapi/linux/tcp.h:194
enum tcp_ca_state {
    TCP_CA_Open = 0,        // 正常
    TCP_CA_Disorder = 1,   // 收到重复 ACK
    TCP_CA_CWR = 2,         // 拥塞窗口缩减
    TCP_CA_Recovery = 3,     // 快速恢复
    TCP_CA_Loss = 4         // 超时丢失
};
```

### 8.2 慢启动

```c
// net/ipv4/tcp_cubic.c 或 tcp_reno.c
void tcp_slow_start(struct tcp_sock *tp)
{
    int cwnd = tcp_snd_cwnd(tp);
    int snd_cwnd_cnt = tp->snd_cwnd_cnt;

    // cwnd 每次增加一个 MSS
    cwnd += tcp_snd_cwnd(tp);
    if (cwnd > tp->snd_ssthresh)
        cwnd = tp->snd_ssthresh;

    tcp_snd_cwnd_set(tp, cwnd);
}
```

### 8.3 拥塞避免

```c
void tcp_cong_avoid_ai(struct tcp_sock *tp, u32 w, u32 acked)
{
    if (tcp_snd_cwnd(tp) >= tp->snd_ssthresh) {
        // 拥塞避免：每个 ACK 增加 cwnd / cwnd
        tp->snd_cwnd_cnt += acked;
        while (tcp_snd_cwnd(tp) >= tp->snd_cwnd_cnt * tp->mss_cache)
            tp->snd_cwnd_cnt--;
    }
}
```

## 9. 重传定时器

### 9.1 RTO 计算

```c
// net/ipv4/tcp_timer.c:534
void tcp_retransmit_timer(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);

    // 1. 进入 Loss 状态
    tcp_enter_loss(sk);

    // 2. 重传最早的未确认段
    tcp_retransmit_skb(sk, tcp_rtx_queue_head(sk));

    // 3. 指数退避
    icsk->icsk_backoff++;
    icsk->icsk_rto = min(icsk->icsk_rto << 1, TCP_RTO_MAX);
}
```

### 9.2 快速重传

```c
// net/ipv4/tcp_input.c:3328
void tcp_fastretrans_alert(struct sock *sk, int dupack, int *ack_flag)
{
    struct tcp_sock *tp = tcp_sk(sk);

    // 收到 3 个重复 ACK 时触发
    if (tp->sacked_out >= 3)
        tcp_update_scoreboard(sk);

    // 进入 Recovery 状态
    if (state == TCP_CA_Recovery) {
        // 快速重传丢失的段
        tcp_push_frames(sk);
    }
}
```
