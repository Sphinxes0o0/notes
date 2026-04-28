# AF_PACKET 套接字

## 1. 模块架构

### 1.1 功能概述

AF_PACKET 提供直接访问网络设备的能力，用于原始套接字和包捕获。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/packet/af_packet.c` | AF_PACKET 实现 |
| `include/net/packet.h` | 包定义 |
| `net/packet/rxrpc.c` | 辅助功能 |

## 2. 核心数据结构

### 2.1 struct packet_sock

```c
// include/net/packet.h:80
struct packet_sock {
    struct sock sk;
    struct packet_ring_buffer rx_ring;
    struct packet_ring_buffer tx_ring;

    struct packet_type proto;
    struct packet_mreq *mcl;

    struct net_device *dev;
    __be16 num;

    enum tpacket_versions tp_version;
    unsigned int tp_hdrlen;
    unsigned int tp_reserve;

    struct packet_mreq_max mreq;
    struct iovec *iov;
};
```

### 2.2 struct packet_mreq

```c
// include/uapi/linux/if_packet.h:20
struct packet_mreq {
    int mr_ifindex;
    unsigned short mr_type;
    unsigned short mr_alen;
    unsigned char mr_address[8];
};

#define PACKET_MR_MULTICAST  0
#define PACKET_MR_PROMISC    1
#define PACKET_MR_ALLMULTI   2
```

## 3. TPACKET 环形缓冲区

### 3.1 struct packet_ring_buffer

```c
// include/net/packet.h:50
struct packet_ring_buffer {
    struct pgv *pg_vec;
    unsigned int pg_vec_order;
    unsigned int pg_vec_pages;
    unsigned int pg_vec_len;

    struct tpacket_req req;
    atomic_t pending;
    unsigned int frame_size;
    unsigned int frame_max;

    struct page **pkt_burst;
};
```

### 3.2 struct tpacket_hdr

```c
// include/uapi/linux/if_packet.h:80
struct tpacket_hdr {
    unsigned long tp_status;
    unsigned int tp_len;
    unsigned int tp_snaplen;
    unsigned short tp_mac;
    unsigned short tp_net;
    unsigned short tp_vlan_tci;
    unsigned short tp_vlan_tpid;
    struct timespec tp_sec;
    struct timespec tp_nsec;
};
```

## 4. 套接字创建

### 4.1 packet_create()

```c
// net/packet/af_packet.c:3000
static int packet_create(struct net *net, struct socket *sock, int protocol)
{
    struct packet_sock *po;
    struct sock *sk;

    // 分配 packet_sock
    po = kzalloc(sizeof(*po), GFP_KERNEL);
    if (!po)
        return -ENOMEM;

    sock_init_data(sock, &po->sk);
    sk = &po->sk;

    // 设置协议
    po->proto.protocol = protocol;
    po->num = protocol;

    // 设置操作函数
    sock->ops = &packet_ops;
    sk->sk_destruct = packet_destruct;

    return 0;
}
```

### 4.2 packet_bind()

```c
// net/packet/af_packet.c:3100
static int packet_bind(struct socket *sock, struct sockaddr *addr, int addr_len)
{
    struct packet_sock *po = pkt_sk(sock);
    struct sockaddr_ll *sll = (struct sockaddr_ll *)addr;

    // 获取设备
    po->dev = dev_get_by_index(sock_net(sock), sll->sll_ifindex);
    if (!po->dev)
        return -ENODEV;

    // 绑定到协议
    dev_add_pack(&po->proto);

    return 0;
}
```

## 5. 发送

### 5.1 packet_sendmsg()

```c
// net/packet/af_packet.c:3200
static int packet_sendmsg(struct socket *sock, struct msghdr *msg, size_t len)
{
    struct packet_sock *po = pkt_sk(sock);
    struct sk_buff *skb;
    int err;

    // 创建 skb
    skb = sock_alloc_send_skb(&po->sk, len + LL_RESERVED_SPACE(po->dev),
                               msg->msg_flags & MSG_DONTWAIT, &err);

    // 复制数据
    err = memcpy_from_msg(skb_put(skb, len), msg, len);

    // 设置协议
    skb->protocol = po->proto.protocol;

    // 发送
    dev_queue_xmit(skb);

    return len;
}
```

## 6. 接收

### 6.1 packet_rcv()

```c
// net/packet/af_packet.c:2500
static int packet_rcv(struct sk_buff *skb, struct net_device *dev,
                      struct packet_type *pt, struct net_device *orig_dev)
{
    struct packet_sock *po = container_of(pt, struct packet_sock, proto);
    struct tpacket_hdr *h;

    // 检查是否使用环形缓冲区
    if (po->rx_ring.pg_vec) {
        // 使用 tpacket_rcv
        return tpacket_rcv(skb, pt, &po->rx_ring);
    }

    // 直接传递到 socket
    skb_push(skb, skb->data - skb_mac_header(skb));

    // 加入接收队列
    skb_queue_tail(&po->sk.sk_receive_queue, skb);

    // 唤醒等待进程
    po->sk.sk_data_ready(&po->sk);

    return 0;
}
```

### 6.2 tpacket_rcv()

```c
// net/packet/af_packet.c:2400
static int tpacket_rcv(struct sk_buff *skb, struct packet_type *pt,
                       struct packet_ring_buffer *rb)
{
    struct tpacket_hdr *h;
    int off;

    // 获取可用帧
    h = rb_get_prev_frame(rb);
    if (!h)
        return -ENOMEM;

    // 复制元数据
    h->tp_len = skb->len;
    h->tp_snaplen = skb->len;
    h->tp_sec = skb->tstamp.tv_sec;
    h->tp_nsec = skb->tstamp.tv_nsec;

    // 复制数据
    off = tpacket_fill_skb(skb, h, rb);

    // 释放 skb
    consume_skb(skb);

    return 0;
}
```

## 7. PACKET_MMAP

### 7.1 设置环形缓冲区

```c
// 使用 mmap 共享内核和用户空间内存
struct tpacket_req req = {
    .tp_block_size = 4096,
    .tp_block_nr = 256,
    .tp_frame_size = TPACKET_ALIGN(sizeof(struct tpacket_hdr)) + 2048,
    .tp_frame_nr = 256,
};

setsockopt(fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req));
```

### 7.2 用户空间访问

```c
void *mmap_rx_ring(int fd) {
    struct tpacket_req req;
    setsockopt(fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req));
    return mmap(NULL, req.tp_block_size * req.tp_block_nr,
                PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
}
```

## 8. 模式

### 8.1 recvfrom()

```c
// 使用标准 recvfrom
recvfrom(fd, buffer, size, 0, (struct sockaddr *)&addr, &len);
```

### 8.2 mmapped 模式

```c
// 高性能零拷贝接收
struct tpacket_hdr *th = ring[block_idx]->iov[frame_idx];
// 直接访问内存
```
