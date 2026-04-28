# net/rxrpc - RxRPC 远程调用

## 1. 模块架构

### 1.1 功能概述

RxRPC 是用于内核到内核远程调用的协议，提供可靠的数据传输。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/rxrpc/af_rxrpc.c` | RxRPC socket 实现 |
| `net/rxrpc/call.c` | 调用管理 |
| `net/rxrpc/input.c` | 数据输入 |
| `include/net/af_rxrpc.h` | RxRPC 定义 |

## 2. 核心数据结构

### 2.1 struct rxrpc_call

```c
// include/net/af_rxrpc.h:100
struct rxrpc_call {
    struct rcu_head rcu;

    struct rxrpc_sock *rxkad;
    struct rxrpc_peer *peer;

    __u32 call_id;                   // 调用 ID
    __u32 service_id;               // 服务 ID

    __u8 state;                     // 调用状态
    __u8 interruptibility;          // 可中断性

    unsigned long flags;
    unsigned long ack_at;           // 下次 ACK 时间
    unsigned long expire_at;        // 过期时间

    struct sk_buff *tx_queue;       // 发送队列
    struct sk_buff *rx_queue;       // 接收队列

    __u32 acks_reason;              // ACK 原因
    __u8  acks[20];                 // ACK 数组

    atomic_t usage;
    refcount_t ref;
};
```

### 2.2 struct rxrpc_peer

```c
// include/net/af_rxrpc.h:60
struct rxrpc_peer {
    struct hlist_node hash_node;
    struct sockaddr_rxrpc srx;

    struct key *key;                 // 安全密钥
    __u32 if_mtu;                   // 接口 MTU
    __u32 mtu;                      // 实际 MTU
    __u32 rtt;                      // 往返时间

    unsigned short service_id;      // 服务 ID

    struct list_head error_queue;   // 错误队列
    struct list_head call_queue;    // 调用队列
};
```

### 2.3 struct rxrpc_sock

```c
// include/net/af_rxrpc.h:150
struct rxrpc_sock {
    struct sock sk;
    struct rxrpc_local *local;      // 本地端点

    struct list_head listen_call;   // 监听调用
    struct list_head to_be_accepted;// 待接受
    struct list_head service_conns; // 服务连接

    __u16 service_id;              // 服务 ID
    struct key *key;                // 安全密钥
};
```

## 3. 调用状态

```c
// include/net/af_rxrpc.h:80
enum rxrpc_call_state {
    RXRPC_CALL_COMPLETE,        // 完成
    RXRPC_CALL_SERVER_BUSY,     // 服务器忙
    RXRPC_CALL_REMOTING_ABORT,  // 远程中止
    RXRPC_CALL_CLIENT_SEND_REPLY,// 客户端发送回复
    RXRPC_CALL_SERVER_SEND_REPLY,// 服务器发送回复
    RXRIC_CALL_SERVER_RECVING,   // 服务器接收中
    RXRPC_CALL_CLIENT_RECVING,   // 客户端接收中
    RXRPC_CALL_CLIENT_SENDING,   // 客户端发送中
    RXRPC_CALL_SERVER_ACKS,      // 服务器等待 ACK
};
```

## 4. 发送数据

### 4.1 rxrpc_send_data()

```c
// net/rxrpc/output.c:200
static int rxrpc_send_data(struct rxrpc_call *call,
                           struct msghdr *msg, size_t len)
{
    struct sk_buff *skb;
    struct rxrpc_packet *pkt;

    // 创建数据包
    skb = alloc_skb(len + sizeof(*pkt), GFP_KERNEL);
    pkt = skb_put(skb, sizeof(*pkt));

    // 设置包头
    pkt->type = RXRPC_PACKET_DATA;
    pkt->callNumber = call->call_id;
    pkt->serviceId = call->service_id;

    // 复制数据
    err = memcpy_from_msg(skb_put(skb, len), msg, len);

    // 加入发送队列
    skb_queue_tail(&call->tx_queue, skb);

    // 发送
    rxrpc_transmit(call);

    return len;
}
```

## 5. 接收数据

### 5.1 rxrpc_data_rcv()

```c
// net/rxrpc/input.c:200
static void rxrpc_data_rcv(struct rxrpc_call *call,
                           struct sk_buff *skb)
{
    struct rxrpc_packet *pkt = (struct rxrpc_packet *)skb->data;

    // 检查序列号
    if (ntohl(pkt->seq) != call->rx_expect_seq)
        goto out;

    // 加入接收队列
    skb_queue_tail(&call->rx_queue, skb);
    call->rx_expect_seq++;

    // 更新接收窗口
    if (call->state == RXRPC_CALL_CLIENT_RECVING)
        rxrpc_rotate_call(call);

out:
    // 发送 ACK
    rxrpc_send_ack(call);
}
```

## 6. 超时和重传

### 6.1 rxrpc_propose_ack()

```c
// net/rxrpc/input.c:400
void rxrpc_propose_ack(struct rxrpc_call *call, __u8 reason)
{
    call->acks_reason = reason;

    // 设置 ACK 定时器
    if (!test_and_set_bit(RXRPC_CALL_NEED_ACK, &call->flags))
        rxrpc_set_timer(call, rxrpc_ACK_timeout);
}
```

### 6.2 rxrpc_resend()

```c
// net/rxrpc/output.c:400
static void rxrpc_resend(struct rxrpc_call *call)
{
    struct sk_buff *skb;

    // 重发未确认的数据
    skb_queue_walk(&call->tx_queue, skb) {
        if (test_bit(RXRPC_SKB_MARK_LOST, &skb->mark)) {
            rxrpc_send_packet(call, skb);
        }
    }
}
```

## 7. 安全

### 7.1 密钥类型

```c
// 支持以下密钥类型:
// - rxkad: Kerberos 5 安全
// - rxk5: Kerberos 5 (新版)
// - rxrpc-afs: AFS 密钥
```

### 7.2 加密

```c
// 数据加密
static int rxrpc_encrypt(struct rxrpc_call *call, struct sk_buff *skb)
{
    return call->key->ops->encrypt(call->key, skb);
}
```
