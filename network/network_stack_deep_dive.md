# Linux 网络栈深度架构分析 v2

## 1. 概述

本文档是 Linux 网络栈的第二轮深度分析，重点关注 Socket 层实现细节、TCP 状态机与拥塞控制算法、UDP 协议实现、IP 层路由与转发、Netfilter 钩子机制、以及网络内存管理（sk_buff）等核心实现。

## 2. Socket 层深入

### 2.1 Socket 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Socket Layer Architecture                              │
│                                                                      │
│  用户空间                                                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  socket() → connect() → send() → recv() → close()          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  struct socket                                               │  │
│  │  - struct file *file                                        │  │
│  │  - struct sock *sk                                          │  │
│  │  - struct proto_ops *ops (协议操作)                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  struct sock                                                 │  │
│  │  - struct sk_buff_head sk_write_queue                      │  │
│  │  - struct sk_buff_head sk_receive_queue                     │  │
│  │  - struct inet_sock *inet (IPv4)                          │  │
│  │  - struct tcp_sock *tcp_sk (TCP)                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Socket 创建流程

```c
/**
 * __sock_create - 创建 socket
 *
 * @family: 协议族 (AF_INET, AF_INET6, etc.)
 * @type: 套接字类型 (SOCK_STREAM, SOCK_DGRAM)
 * @protocol: 协议 (IPPROTO_TCP, IPPROTO_UDP, etc.)
 */
int __sock_create(struct net *net, int family, int type, int protocol,
                 struct socket **res, int kern)
{
    struct socket *sock;
    const struct net_proto_family *pf;
    struct proto *prot;
    int err;

    /* 分配 socket 结构 */
    sock = sock_alloc();
    if (!sock)
        return -ENOMEM;

    /* 设置类型 */
    sock->type = type;

    /* 查找协议族 */
    pf = rcu_dereference(net_families[family]);
    if (!pf) {
        err = -EAFNOSUPPORT;
        goto out;
    }

    /* 查找协议 */
    prot = rcu_dereference(proto[family][type][protocol]);
    if (!prot) {
        err = -EPROTONOSUPPORT;
        goto out;
    }

    /* 调用协议族的 create 方法 */
    err = pf->create(net, sock, protocol, kern);
    if (err)
        goto out;

    *res = sock;
    return 0;
}

/**
 * inet_create - 创建 INET socket
 */
static int inet_create(struct net *net, struct socket *sock, int protocol, int kern)
{
    struct sock *sk;
    struct inet_protosw *answer;
    struct list_head *pos;
    int try_loading_module = 2;

    /* 查找匹配的协议 */
    list_for_each_rcu(pos, &inetsw[sock->type]) {
        answer = list_entry(pos, struct inet_protosw, list);
        if (protocol == answer->protocol) {
            if (protocol != IPPROTO_IP)
                break;
        }
    }

    /* 创建 sock 结构 */
    sk = sk_alloc(net, family, GFP_KERNEL, answer->prot, kern);
    if (!sk)
        return -ENOMEM;

    /* 初始化 sock */
    sock_init_data(sock, sk);

    /* 协议特定初始化 */
    err = answer->prot->init(sk);
    if (err)
        goto out;

    return 0;
out:
    sk_free(sk);
    return err;
}
```

### 2.3 Socket 缓冲区管理

```c
/**
 * struct sock - 网络核心数据结构
 *
 * 包含：
 * - 接收/发送队列
 * - 协议特定数据
 * - 锁和状态
 */
struct sock {
    /* 套接字状态 */
    __u8 sk_shutdown : 2,
         sk_no_check : 2,
         sk_userlocks : 4;

    /* 队列 */
    struct sk_buff_head sk_receive_queue;   // 接收队列
    struct sk_buff_head sk_write_queue;    // 发送队列
    struct sk_buff_head sk_async_queue;     // 异步队列

    /* 缓冲限制 */
    int sk_rcvbuf;            // 接收缓冲区大小
    int sk_sndbuf;            // 发送缓冲区大小
    int sk_forward_alloc;     // 预分配空间

    /* 内存压力 */
    atomic_t sk_drops;        // 丢包计数
    int sk_rcvlowat;         // 接收低水位

    /* 协议特定 */
    struct proto *sk_prot;    // 协议操作
    union {
        struct inet_sock *inet;
        struct unix_sock *unix;
    } sk_protinfo;

    /* 状态 */
    __u8 sk_state;
    __u16 sk_shutdown;

    /* 锁 */
    struct socket *sk_socket;
    struct mutex sk_lock;
    struct {
        struct sk_buff_head head;
        struct sk_buff *tail;
    } sk_backlog;

    /* 定时器 */
    struct timer_list sk_timer;

    /* 回调 */
    void (*sk_data_ready)(struct sock *sk);
    void (*sk_write_space)(struct sock *sk);
    void (*sk_error_report)(struct sock *sk);
};
```

## 3. TCP 协议实现

### 3.1 TCP 状态机

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TCP State Machine                                      │
│                                                                      │
│  CLOSED ──────► LISTEN                                               │
│     │                │                                                 │
│     │            LISTEN ───► SYN_SENT                                │
│     │                │                                                 │
│     │            ┌─── SYN ───► ESTABLISHED ───► CLOSE_WAIT         │
│     │            │         │                   │                       │
│     │            │         │                   ▼                       │
│     │            │         │              CLOSE_WAIT ───► LAST_ACK   │
│     │            │         │                   │                       │
│     │            │         │                   ▼                       │
│     │            │         │                 FIN_WAIT_1 ───► FIN_WAIT_2│
│     │            │         │                   │                       │
│     │            │         │                   ▼                       │
│     │            │         │                CLOSING ───► TIME_WAIT  │
│     │            │         │                                                │
│     │            │         │                 FIN_WAIT_2 ──► TIME_WAIT │
│     │            │         │                                               │
└─────────────────────────────────────────────────────────────────────┘
```

状态转换关键事件：
- SYN_SENT: 发送 SYN
- SYN_RECV: 收到 SYN + 发送 ACK
- ESTABLISHED: 三次握手完成
- FIN_WAIT_1: 发送 FIN
- FIN_WAIT_2: 收到 ACK
- TIME_WAIT: 等待 2MSL

### 3.2 TCP 选项处理

```c
/**
 * tcp_parse_options - 解析 TCP 选项
 *
 * TCP 选项格式：
 * KIND(1) LENGTH(1) VALUE(n)
 *
 * 常见选项：
 * - MSS: KIND=2, LENGTH=4, VALUE=2 bytes
 * - Window Scale: KIND=3, LENGTH=3, VALUE=1 byte
 * - SACK: KIND=4, LENGTH=2
 * - Timestamp: KIND=8, LENGTH=10, VALUE=8 bytes
 */
struct tcp_options_received {
    /* MSS */
    u16 mss_clamp;         // 最大段大小
    u16 mss;               // 当前 MSS

    /* Window Scale */
    u8 saw_tstamp;         // 是否有时间戳
    u8 snd_wscale;         // 发送方窗口扩展
    u8 rcv_wscale;         // 接收方窗口扩展

    /* SACK */
    u8 sack_ok;            // 是否支持 SACK
    u8 dsack;             // 重复 SACK

    /* Timestamps */
    u64 ts_recent;         // 最近时间戳
    u64 ts_recent_stamp;   // 最近时间戳时间

    /* TFO */
    u8 is_tfo : 1;
};
```

### 3.3 TCP 头部结构

```c
/**
 * struct tcphdr - TCP 头部
 *
 * 固定头部：20 字节
 */
struct tcphdr {
    __be16 source;         // 源端口
    __be16 dest;           // 目标端口
    __be32 seq;            // 序列号
    __be32 ack_seq;        // 确认号

#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u16   doff:4,       // 数据偏移（4位 = 头部长度）
            res1:4,
            fin:1,        // FIN 标志
            syn:1,        // SYN 标志
            rst:1,       // RST 标志
            psh:1,       // PSH 标志
            ack:1,       // ACK 标志
            urg:1,       // URG 标志
            ece:1,       // ECN 回显
            cwr:1;       // 拥塞窗口减少
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u16   res1:4,
            doff:4,
            cwr:1,
            ece:1,
            urg:1,
            ack:1,
            psh:1,
            rst:1,
            syn:1,
            fin:1;
#endif

    __be16 window;         // 窗口大小
    __sum16 check;        // 校验和
    __be16 urg_ptr;       // 紧急指针
};
```

### 3.4 TCP 发送流程

```c
/**
 * tcp_sendmsg - 发送数据
 *
 * 流程：
 * 1. 检查是否可发送（窗口、拥塞窗口）
 * 2. 复制用户数据到 sk_buff
 * 3. 加入发送队列
 * 4. 触发 ACK
 */
int tcp_sendmsg(struct sock *sk, struct msghdr *msg, size_t size)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct sk_buff *skb;
    int flags, err;

    flags = msg->msg_flags;

    while (size > 0) {
        /* 获取发送缓冲区 */
        skb = tcp_write_queue_tail(sk);
        if (tcp_send_head(sk)) {
            /* 检查是否可以追加到现有 skb */
            skb = skb_peek_tail(&sk->sk_write_queue);
        }

        /* 检查拥塞窗口 */
        if (tp->snd_cwnd < tp->snd_ssthresh) {
            /* 慢启动 */
            tp->snd_cwnd_cnt += tcp_mss_cache;
        } else {
            /* 拥塞避免 */
            tp->snd_cwnd_cnt += tcp_mss_cache * tp->snd_cwnd;
        }

        /* 检查发送窗口 */
        if (tcp_snd_wnd_test(tp, skb, mss_now)) {
            /* 可以发送 */
            err = tcp_push(sk, flags, size, tp->mss_cache, tp->nonagle);
        }
    }

    return size - remaining;
}

/**
 * tcp_push - 推送数据到网络层
 */
static int tcp_push(struct sock *sk, int flags, int payload_len,
                   int mss_now, int nonagle)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct sk_buff *skb;

    /* 如果需要发送 ACK 或 FIN */
    if (tcp_send_head(sk) != NULL) {
        tcp_nagle_push(sk);
        return 0;
    }

    /* 设置 PSH 标志 */
    return tcp_transmit_skb(sk, skb, 1, flags);
}
```

## 4. UDP 协议实现

### 4.1 UDP 头部

```c
/**
 * struct udphdr - UDP 头部
 *
 * 固定头部：8 字节
 */
struct udphdr {
    __be16 source;         // 源端口
    __be16 dest;           // 目标端口
    __be16 len;           // 长度（包括头部）
    __sum16 check;        // 校验和
};
```

### 4.2 UDP 发送/接收

```c
/**
 * udp_sendmsg - UDP 发送
 */
int udp_sendmsg(struct sock *sk, struct msghdr *msg, size_t len)
{
    struct inet_sock *inet = inet_sk(sk);
    struct udp_sock *up = udp_sk(sk);
    struct flowi4 *fl4;
    struct ipcm_cookie ipc;
    int ulen;
    struct rtable *rt;
    int connected;

    /* 计算 UDP 长度 */
    ulen = len + sizeof(struct udphdr);

    /* 查找路由 */
    fl4 = &inet->cork.fl.u.ip4;
    rt = ip_route_connect(fl4, usin->sin_addr, inet->inet_saddr,
                         IPPROTO_UDP, up->sport, usin->sin_port,
                         sk->sk_bound_dev_if, O_NONBLOCK);

    /* 构建 UDP 头部 */
    struct udphdr *uh = udp_hdr(skb);
    uh->source = htons(up->sport);
    uh->dest = htons(up->dport);
    uh->len = htons(ulen);
    uh->check = 0;

    /* 发送 */
    return ip_send_skb(sock_net(sk), skb);
}

/**
 * udp_recvmsg - UDP 接收
 */
int udp_recvmsg(struct sock *sk, struct msghdr *msg, size_t len, int flags)
{
    struct sk_buff *skb;
    int copied;

    /* 从队列取出一个包 */
    skb = skb_recv_datagram(sk, flags, &err);

    /* 复制数据到用户空间 */
    copied = skb->len;
    if (copied > len) {
        copied = len;
        msg->msg_flags |= MSG_TRUNC;
    }

    /* 复制数据 */
    err = skb_copy_datagram_msg(skb, 0, msg, copied);

    return copied;
}
```

## 5. IP 层深入

### 5.1 IP 头部

```c
/**
 * struct iphdr - IP 头部
 *
 * IPv4 头部：20-60 字节（取决于选项）
 */
struct iphdr {
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u8  ihl:4,          // IP 头部长度（4位 = 字数）
          version:4;       // IP 版本（4）
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u8  version:4,
          ihl:4;
#endif
    __u8  tos;            // 服务类型
    __be16 tot_len;       // 总长度
    __be16 id;           // 标识
    __be16 frag_off;     // 分片偏移
    __u8  ttl;           // 生存时间
    __u8  protocol;      // 协议
    __sum16 check;       // 校验和
    __be32 saddr;        // 源地址
    __be32 daddr;        // 目标地址
};
```

### 5.2 路由查找

```c
/**
 * ip_route_output_flow - 路由查找
 *
 * 查找步骤：
 * 1. 查找本地路由缓存 (fib_lookup)
 * 2. 确定输出接口
 * 3. 确定下一跳地址
 * 4. 缓存结果
 */
int ip_route_output_flow(struct net *net, struct flowi4 *fl4,
                        const struct sock *sk)
{
    struct fib_result res;
    struct rtable *rt;

    /* 查找路由 */
    err = fib_lookup(net, &fl4->flowi4_u, &res, 0);
    if (err)
        return err;

    /* 创建路由缓存条目 */
    rt = rt_dst_alloc(&res);
    if (!rt)
        return -ENOBUFS;

    /* 设置目标 */
    rt->dst.output = ip_output;
    fl4->daddr = rt->rt_gateway;

    return 0;
}

/**
 * fib_lookup - FIB 查找
 *
 * 使用最长前缀匹配（LPM）
 */
int fib_lookup(struct net *net, struct flowi4 *fl,
               struct fib_result *res, unsigned int flags)
{
    struct fib_table *tb;

    /* 遍历所有 FIB 表 */
    for_each_fib_table(tb) {
        if (fib_table_lookup(tb, fl, res, flags) == 0)
            return 0;
    }

    return -ENETUNREACH;
}
```

### 5.3 IP 分片与重组

```c
/**
 * ip_fragment - IP 分片
 *
 * 当 MTU 小于数据包大小时分片
 */
int ip_fragment(struct net *net, struct sock *sk, struct sk_buff *skb,
                unsigned int mtu, int *frag_off)
{
    struct iphdr *iph;
    struct sk_buff *frag;
    int offset;
    int err = 0;

    iph = ip_hdr(skb);
    offset = iph->ihl * 4;

    /* 对每个分片 */
    while (tot_len > mtu) {
        /* 创建分片 skb */
        frag = alloc_skb(mtu + offset, GFP_ATOMIC);
        if (!frag)
            return -ENOMEM;

        /* 复制头部 */
        skb_copy_from_linear_data(skb, skb_put(frag, offset), offset);

        /* 设置分片偏移 */
        iph = ip_hdr(frag);
        iph->frag_off = htons(offset >> 3);

        /* 最后一个分片设置 MF 标志 */
        if (tot_len - mtu <= 0)
            iph->frag_off |= htons(IP_MF);

        /* 复制数据 */
        skb_copy_from_linear_data_offset(skb, offset,
                                        skb_put(frag, mtu - offset),
                                        mtu - offset);
        offset += mtu - offset;
        tot_len -= mtu;

        /* 发送分片 */
        err = ip_local_out(net, frag);
    }

    return err;
}
```

## 6. sk_buff 结构深入

### 6.1 sk_buff 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    sk_buff Layout                                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  sk_buff (控制数据)                                         │  │
│  │  - struct sock *sk                                          │  │
│  │  - struct net_device *dev                                  │  │
│  │  - unsigned int len, data_len                               │  │
│  │  - __u16 queue_mapping                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  线性数据区 (linear data)                                   │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ MAC头部 │ IP头部 │ TCP/UDP头部 │ 应用数据            │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  分页数据区 (paged data)                                    │  │
│  │  - struct page *pages                                       │  │
│  │  - unsigned int frag_list_len                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 sk_buff 结构

```c
/**
 * struct sk_buff - Socket Buffer
 *
 * 网络数据包的核心数据结构
 */
struct sk_buff {
    /* 引用计数和长度 */
    unsigned int len;        // 总长度（线性 + 分页）
    unsigned int data_len;   // 分页数据长度
    __u16 mac_len;          // MAC 头长度
    __u16 hdr_len;         // 克隆头长度

    /* 数据指针 */
    unsigned char *head;     // 缓冲头
    unsigned char *data;     // 数据开始
    unsigned char *tail;     // 数据结束
    unsigned char *end;      // 缓冲结束

    /* 协议头指针 */
    struct skb_shared_hwtstamps *hwtstamps;
    union {
        struct tcphdr *th;
        struct udphdr *uh;
        struct icmphdr *icmph;
        struct iphdr *ipiph;
        unsigned char *raw;
    } header;

    /* 网络层头 */
    struct ipv6hdr *ipv6h;
    struct iphdr *ip_header;

    /* 传输层 */
    __be16 source_port;
    __be16 dest_port;

    /* 设备 */
    struct net_device *dev;
    unsigned long dev_scratch;

    /* 队列映射 */
    __u16 queue_mapping;

    /* 协议信息 */
    __be16 protocol;
    __u16 inner_protocol;

    /* 标记 */
    __u8 pkt_type:3;
    __u8 ignore_df:1;
    __u8 nf_trace:1;
    __u8 ip_summed:2;

    /* 分片信息 */
    __u16 frag_off;
    __u16 pending_destroy:1;

    /* 引用计数 */
    atomic_t users;

    /* 分页/片段 */
    struct page_frag page;
    struct sk_buff *frag_list;

    /* 私有数据 */
    struct sec_path *sp;
    void *security;

    /* 时间戳 */
    u64 skb_mstamp;
    ktime_t tstamp;

    /* 网络命名空间 */
    struct net *skb_main;
    struct net_device *skb_dev;
};
```

### 6.3 sk_buff 操作

```c
/**
 * skb_put - 添加数据到 sk_buff 尾部
 *
 * 返回写入位置的指针
 */
static inline unsigned char *skb_put(struct sk_buff *skb, unsigned int len)
{
    unsigned char *tmp = skb->tail;
    skb->tail += len;
    skb->len += len;
    return tmp;
}

/**
 * skb_push - 添加数据到 sk_buff 头部
 *
 * 用于添加协议头
 */
static inline unsigned char *skb_push(struct sk_buff *skb, unsigned int len)
{
    skb->data -= len;
    skb->len += len;
    return skb->data;
}

/**
 * skb_pull - 从 sk_buff 头部移除数据
 *
 * 用于解析协议头后的处理
 */
static inline unsigned char *skb_pull(struct sk_buff *skb, unsigned int len)
{
    skb->len -= len;
    return skb->data += len;
}
```

## 7. Netfilter 钩子

### 7.1 Netfilter 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Netfilter Hooks                                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    PRE_ROUTING                                │  │
│  │                    (接收后，路由前)                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               LOCAL_IN (本地接收)                            │  │
│  │               (路由后，本地交付)                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               FORWARD (转发)                                │  │
│  │               (路由后，转发)                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               LOCAL_OUT (本地发送)                           │  │
│  │               (本地生成，路由前)                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   POST_ROUTING                               │  │
│  │                   (发送前)                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 nf_hook_ops 结构

```c
/**
 * struct nf_hook_ops - Netfilter 钩子操作
 */
struct nf_hook_ops {
    /* 钩子回调函数 */
    nf_hookfn *hook;

    /* 优先级（小的先调用） */
    int priority;

    /* 协议族 */
    int pf;

    /* 钩子点 */
    unsigned int hooknum;

    /* 钩子名称 */
    const char *name;
};

/**
 * nf_hookfn - 钩子回调函数类型
 *
 * @priv: 私有数据
 * @skb: 数据包
 * @state: 钩子状态
 *
 * 返回：
 * - NF_ACCEPT: 接受包
 * - NF_DROP: 丢弃包
 * - NF_STOLEN: 窃取包（不释放）
 * - NF_QUEUE: 放入队列
 * - NF_REPEAT: 重新调用
 */
typedef unsigned int nf_hookfn(void *priv,
                               struct sk_buff *skb,
                               const struct nf_hook_state *state);
```

### 7.3 iptables 规则链

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IPTables Tables                                    │
│                                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│  │  filter │    │   nat   │    │  mangle │    │  raw    │       │
│  ├─────────┤    ├─────────┤    ├─────────┤    ├─────────┤       │
│  │ INPUT   │    │ PREROUT │    │ PREROUT │    │ PREROUT │       │
│  │ FORWARD │    │ OUTPUT  │    │ OUTPUT  │    │ OUTPUT  │       │
│  │ OUTPUT  │    │ POSTROUT│    │ INPUT   │    │         │       │
│  │         │    │         │    │ FORWARD │    │         │       │
│  │         │    │         │    │ POSTROUT│    │         │       │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

## 8. 核心算法分析

### 8.1 TCP 拥塞控制

```c
/*
 * TCP 拥塞控制算法状态机：
 *
 *       慢启动                拥塞避免
 *    ┌──────────┐        ┌──────────┐
 *    │ cwnd <   │        │ cwnd >=  │
 *    │ ssthresh │        │ ssthresh │
 *    └────┬─────┘        └────┬─────┘
 *         │                   │
 *         ▼                   ▼
 *    ┌──────────────────────────────┐
 *    │  每个 ACK: cwnd += min(N, MSS) │
 *    └──────────────────────────────┘
 *
 * 丢包事件：
 * - 如果是 Tahoe: ssthresh = cwnd/2, cwnd = MSS (慢启动)
 * - 如果是 Reno:  ssthresh = cwnd/2, cwnd = cwnd/2 (快速恢复)
 */
```

### 8.2 TCP RTT 估计

```c
/*
 * TCP RTT 估计（Jacobson 算法）：
 *
 * RTT_var = (1 - beta) * RTT_var + beta * |RTT_sample - RTT|
 * RTT = (1 - alpha) * RTT + alpha * RTT_sample
 *
 * 其中：
 * - alpha = 0.125
 * - beta = 0.25
 *
 * RTO = RTT + 4 * RTT_var
 */
static void tcp_rtt_estimator(struct sock *sk, long sample_rtt)
{
    struct tcp_sock *tp = tcp_sk(sk);
    long m = sample_rtt;
    u32 srtt = tp->srtt;

    /* 更新 SRTT */
    m -= (srtt >> 3);
    srtt += m;

    if (m < 0) {
        m = -m;
        m -= (tp->mdev >> 2);
    } else {
        m -= (tp->mdev >> 2);
    }
    tp->mdev += m;

    if (tp->mdev > tp->mdev_max)
        tp->mdev_max = tp->mdev;

    if (tp->rttvar > tp->mdev_max)
        tp->rttvar = tp->mdev_max;

    /* 更新 RTO */
    tp->rto = (srtt >> 3) + (tp->rttvar << 2);
}
```

## 9. 参考资料

- `net/core/sock.c` - Socket 层实现
- `net/ipv4/tcp.c` - TCP 协议实现
- `net/ipv4/tcp_input.c` - TCP 输入处理
- `net/ipv4/tcp_output.c` - TCP 输出处理
- `net/ipv4/udp.c` - UDP 协议实现
- `net/ipv4/ip_output.c` - IP 输出处理
- `net/ipv4/ip_input.c` - IP 输入处理
- `net/core/skbuff.c` - sk_buff 实现
- `net/netfilter/core.c` - Netfilter 核心
- `include/net/sock.h` - Socket 核心定义
- `include/net/tcp.h` - TCP 定义
- `include/linux/skbuff.h` - sk_buff 定义
- Documentation/networking/
- "TCP/IP Illustrated" - Stevens
