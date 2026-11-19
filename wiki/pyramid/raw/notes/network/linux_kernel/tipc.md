# net/tipc - TIPC 传输服务

## 1. 模块架构

### 1.1 功能概述

TIPC (Transparent Inter-Process Communication) 是专为集群环境设计的高性能分布式通信协议。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/tipc/socket.c` | TIPC socket 实现 |
| `net/tipc/link.c` | 链路层 |
| `net/tipc/node.c` | 节点管理 |
| `include/net/tipc.h` | TIPC 定义 |

## 2. 核心数据结构

### 2.1 struct tipc_sock

```c
// include/net/tipc.h:100
struct tipc_sock {
    struct sock sk;
    struct tipc_msg *phdr;           // 协议头
    struct tipc_port *port;         // 端口

    struct list_head pubs;          // 发布者列表
    struct list_head subs;          // 订阅者列表

    __u32 conn_addr;               // 连接地址
    unsigned int probe_timeout;     // 探测超时
    struct timer_list probe_timer;  // 探测定时器
};
```

### 2.2 struct tipc_port

```c
// include/net/tipc.h:80
struct tipc_port {
    struct tipc_portid peer;
    __u32 ustipc;
    __u32 type;
    __u32 ref;
    __u32 conn_portid;

    struct list_head dispatch;
    struct tipc_sock *listener;
};
```

### 2.3 struct tipc_link

```c
// include/net/tipc.h:120
struct tipc_link {
    char name[TIPC_MAX_LINK_NAME];
    struct tipc_node *owner;

    struct net_device *dev;         // 网络设备
    struct sk_buff_head   out_queue; // 输出队列
    struct sk_buff_head   inputq;    // 输入队列

    __u32 stats;
    __u16 addr;
    unsigned long state;
};
```

## 3. 地址

### 3.1 TIPC 地址结构

```c
// 格式: Zone:Cluster:Node:Ref
// 例如: 1.2.3:10
#define TIPC_ZONE_MASK   0xFF000000
#define TIPC_CLUSTER_MASK 0x00FFF000
#define TIPC_NODE_MASK   0x00000FFF
#define TIPC_PORT_MASK   0xFFFF

// TIPC 集群内广播地址
#define TIPC_ADDR_MCAST  0xFFFFFFFF
```

## 4. 连接

### 4.1 tipc_connect()

```c
// net/tipc/socket.c:400
static int tipc_connect(struct socket *sock, struct sockaddr *addr,
                       int addrlen, int flags)
{
    struct tipc_sock *tsk = tipc_sk(sock);
    struct tipc_msg *msg = tsk->phdr;

    // 解析目标地址
    tipc_get_ports(addr, &peer);

    // 发送 CONN_REQ
    msg_set_destnode(msg, peer.zone, peer.cluster, peer.node);
    msg_set_destport(msg, peer.ref);

    // 等待 CONN_ACK
    return tipc_wait_for_cond(&tsk->sk, TIPC_CONN_WAIT);
}
```

### 4.2 tipc_accept()

```c
// net/tipc/socket.c:500
static int tipc_accept(struct socket *sock, struct socket *newsock,
                       int flags)
{
    struct tipc_sock *tsk = tipc_sk(sock);
    struct sock *newsk;
    struct tipc_sock *newtsk;

    // 等待连接
    if (tsk->connected)
        return -EINVAL;

    // 从连接队列取出
    newsk = tipc_get_conn_queue(sock);
    newtsk = tipc_sk(newsk);

    // 发送 CONN_ACK
    msg_set_conn_port(newtsk->phdr, newtsk->port.ref);

    return 0;
}
```

## 5. 消息发送

### 5.1 tipc_sendmsg()

```c
// net/tipc/socket.c:600
static int tipc_sendmsg(struct socket *sock, struct msghdr *m, size_t dsz)
{
    struct tipc_sock *tsk = tipc_sk(sock);
    struct tipc_msg *msg = tsk->phdr;
    struct sk_buff *skb;

    // 创建消息
    skb = tipc_msg_build(msg, m, dsz);
    if (!skb)
        return -ENOMEM;

    // 发送到链路层
    tipc_link_xmit(skb, &tsk->port.peer, tsk->link);

    return dsz;
}
```

### 5.2 tipc_recvmsg()

```c
// net/tipc/socket.c:700
static int tipc_recvmsg(struct socket *sock, struct msghdr *m, size_t dsz,
                        int flags)
{
    struct tipc_sock *tsk = tipc_sk(sock);
    struct sk_buff *skb;

    // 从 receive_queue 取出
    skb = skb_dequeue(&tsk->port.receiveq);
    if (!skb)
        return -EAGAIN;

    // 复制数据
    err = copy_to_user(m->msg_iov, skb->data, dsz);

    return dsz;
}
```

## 6. 链路监控

### 6.1 邻居探测

```c
// 定期发送探测消息检测邻居状态
static void tipc_link_ping(struct timer_list *t)
{
    struct tipc_link *link = from_timer(link, t, timer);

    // 发送 PING 消息
    tipc_link_send_proto(link, PROTOCOL_PING);

    // 设置超时
    mod_timer(&link->timer, jiffies + link-> tolerance);
}
```

### 6.2 故障检测

```c
// 多次探测失败认为链路故障
if (link->backoff_rcv_cnt > MAX_PING_RETRIES) {
    tipc_link_fsm(link, TIPC_LINK_DOWN);
    // 触发重新选路
}
```

## 7. 广播

### 7.1 广播组播

```c
// TIPC 支持高效的集群广播
// 使用分层广播树减少重复

struct tipc_nlist {
    struct list_head list;
    struct tipc_node *nodes;
    int count;
};
```
