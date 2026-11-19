# net/sctp - SCTP 传输协议

## 1. 模块架构

### 1.1 功能概述

SCTP (Stream Control Transmission Protocol) 是可靠的面向消息的传输协议，支持多流和多宿主。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/sctp/socket.c` | SCTP socket 实现 |
| `net/sctp/associola.c` | 关联管理 |
| `net/sctp/outqueue.c` | 输出队列 |
| `include/net/sctp.h` | SCTP 定义 |

## 2. 核心数据结构

### 2.1 struct sctp_association

```c
// include/net/sctp/associola.h:120
struct sctp_association {
    struct list_head as_node;
    struct sctp_ep_common *ep;

    __u16 rwnd;                      // 接收窗口
    __u32 outstanding_bytes;         // 未确认字节
    __u32 cacc_mode;                 // CACC 模式

    struct {
        __u16 pathmtu;              // 路径 MTU
        __u8  pstate;               // 路径状态
        __u8  cwnd;                 // 拥塞窗口
        __u8  ssthresh;             // 慢启动阈值
        __u8  partial_bytes_acked;
    } cfsctp;

    struct sctp_transport **transport;
    int send_paths;

    struct sctp_ulpevent *stream;
    struct sctp_stream_out *out;
    struct sctp_stream_in *in;
};
```

### 2.2 struct sctp_transport

```c
// include/net/sctp/transport.h:40
struct sctp_transport {
    struct list_head transports;
    struct sctp_association *asoc;

    struct sockaddr_storage ipaddr;   // 目的地址
    struct net_device *dev;          // 网络设备

    __u32 rto;                       // RTO 值
    __u32 rtt;                       // 往返时间
    __u32 srtt;                      // 平滑 RTT

    __u32 cwnd;                      // 拥塞窗口
    __u32 ssthresh;                  // 慢启动阈值

    __u32 partial_bytes_acked;
    __u32 flight_size;               // 已发送未确认

    unsigned long error_count;
    __u8  state;                    // 状态
};
```

## 3. 初始化

### 3.1 sctp_init()

```c
// net/sctp/protocol.c:800
static int __init sctp_init(void)
{
    // 1. 注册协议
    inet_register_protosw(&sctp_stream_protosw, SOCK_STREAM, IPPROTO_SCTP);
    inet_register_protosw(&sctp_dgram_protosw, SOCK_DGRAM, IPPROTO_SCTP);

    // 2. 初始化表
    sctp_eps_bind_bucket_init();
    sctp_assoc_hashtable_init();

    // 3. 注册通知
    sock_register(&sctp_family_ops);

    return 0;
}
```

### 3.2 sctp_family_ops

```c
// net/sctp/socket.c:100
static const struct proto_ops sctp_stream_ops = {
    .family = PF_INET,
    .owner = THIS_MODULE,
    .release = sctp_release,
    .bind = sctp_bind,
    .connect = sctp_connect,
    .accept = sctp_accept,
    .listen = sctp_listen,
    .sendmsg = sctp_sendmsg,
    .recvmsg = sctp_recvmsg,
    .shutdown = sctp_shutdown,
};
```

## 4. 四路握手

### 4.1 INIT

```c
// net/sctp/sm_statefuns.c:200
sctp_disposition_t sctp_sf_do_5_1B_init(struct net *net,
                                          struct sctp_endpoint *ep,
                                          struct sctp_association *asoc,
                                          struct sctp_chunk *chunk,
                                          void **argp,
                                          gfp_t gfp)
{
    struct sctp_init_chunk *init = (struct sctp_init_chunk *)chunk->skb->data;

    // 创建关联
    asoc = sctp_make_temp_asoc(ep, chunk, gfp);

    // 保存参数
    asoc->init = init->init_tag;
    asoc->a_rwnd = ntohs(init->a_rwnd);
    asoc->num_out_streams = ntohs(init->num_ostreams);
    asoc->num_in_streams = ntohs(init->num_istreams);

    // 发送 INIT-ACK
    sctp_outq_tail(&asoc->outqueue);
}
```

### 4.2 INIT-ACK

```c
// net/sctp/sm_statefuns.c:300
sctp_disposition_t sctp_sf_do_5_1C_init_ack(struct net *net, ...)
{
    struct sctp_chunk *chunk;

    // 创建 INIT-ACK
    chunk = sctp_make_init_ack(asoc, chunk, GFP_ATOMIC);

    // 保存状态
    sctp_add_cmd_sf(commands, SCTP_CMD_REPLY, chunk);
}
```

### 4.3 COOKIE-ECHO / COOKIE-ACK

```c
// net/sctp/sm_statefuns.c:400
sctp_disposition_t sctp_sf_do_5_1D_ce(struct net *net, ...)
{
    // 验证 cookie
    if (!sctp_verify_cookie(asoc, chunk))
        return SCTP_DISPOSITION_NOMEM;

    // 创建 association
    sctp_add_cmd_sf(commands, SCTP_CMD_NEW_ASOC, asoc);

    // 发送 COOKIE-ACK
    sctp_add_cmd_sf(commands, SCTP_CMD_REPLY, chunk);
}
```

## 5. 数据传输

### 5.1 sctp_sendmsg()

```c
// net/sctp/socket.c:800
static int sctp_sendmsg(struct sock *sk, struct msghdr *msg, size_t msg_len)
{
    struct sctp_association *asoc;
    struct sctp_chunk *chunk;
    struct sctp_datahdr chunkhdr;

    // 获取关联
    asoc = sctp_association_get(sk, msg);

    // 构建数据块
    chunkhdr.stream = stream;
    chunkhdr.ssn = asoc->out.out_curr_msg;
    chunkhdr.tsn = asoc->next_tsn++;
    chunkhdr.payload = data;

    // 发送
    sctp_outq_tail(&asoc->outqueue, chunk);

    return msg_len;
}
```

### 5.2 sctp_recvmsg()

```c
// net/sctp/socket.c:900
static int sctp_recvmsg(struct sock *sk, struct msghdr *msg, size_t len,
                        int noblock, int flags, int *addr_len)
{
    struct sctp_association *asoc;
    struct sctp_ulpevent *event;

    // 获取事件
    event = sctp_ulpevent_receive(asoc, noblock);
    if (!event)
        return -EAGAIN;

    // 复制数据
    err = copy_to_user(msg->msg_iov, event->data, event->len);

    return event->len;
}
```

## 6. 多宿主

### 6.1 主路径选择

```c
// net/sctp/transport.c:200
static struct sctp_transport *sctp_unpacked_primary(struct sctp_association *asoc)
{
    struct sctp_transport *primary;

    // 选择主路径
    list_for_each_entry(primary, &asoc->transport, transports) {
        if (primary->state == SCTP_ACTIVE)
            return primary;
    }

    return NULL;
}
```

### 6.2 故障转移

```c
// 路径故障时自动切换到备用路径
// 当主路径恢复时，可能切回主路径
```
