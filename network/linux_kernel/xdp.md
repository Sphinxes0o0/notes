# XDP 传输层

## 1. 模块架构

### 1.1 功能概述

AF_XDP 是一种高性能的 Socket API，允许应用程序直接访问 XDP 帧。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/xdp/xsk.c` | AF_XDP 实现 |
| `include/net/xdp.h` | XDP 定义 |
| `net/xdp/xsk_queue.h` | XSK 队列 |

## 2. AF_XDP Socket

### 2.1 struct xdp_sock

```c
// include/net/xdp_sock.h:40
struct xdp_sock {
    struct sock     sk;
    struct net_device *dev;

    struct xsk_queue *tx;
    struct xsk_queue *rx;

    struct xdp_umem *umem;

    __u32     queue_id;
    bool      bound;
};
```

### 2.2 struct xdp_umem

```c
// include/net/xdp_sock.h:80
struct xdp_umem {
    void *buffer;
    struct xdp_desc *descs;
    u32 len;

    struct xsk_queue *fq;
    struct xsk_queue *cq;

    u64 headroom;
    u64 chunk_size;
    u32 npgs;
};
```

## 3. 工作原理

### 3.1 零拷贝机制

```
应用程序                  驱动
    |                       |
    |   注册 UMEM (内存区)   |
    +----------------------->|
    |                       |
    |   填充 Free 队列      |
    +----------------------->|
    |                       |
    |   NIC DMA 读取帧      <--+
    |                       |
    |   接收完成            |
    |   填充 Rx 队列        +---> DMA 写入
    |<-----------------------+
    |                       |
    |   消费 Rx 描述符       |
    |                       |
    |   释放 (放入 Free 队列)|
    +----------------------->|
```

### 3.2 模式

```c
// XDP 模式
enum {
    XDP_MODE_UNKNOWN = 0,
    XDP_MODE_UMEM,         // 共享 UMEM
    XDP_MODE_RXQ,          // 每个队列一个 socket
    XDP_MODE_ZEROCOPY,     // 零拷贝模式
    XDP_MODE_COPY,          // 拷贝模式
};
```

## 4. Socket 创建

### 4.1 socket()

```c
// net/xdp/xsk.c:500
static int xsk_create(struct net *net, struct socket *sock, int protocol)
{
    struct xdp_sock *xs;

    // 分配 xdp_sock
    xs = kzalloc(sizeof(*xs), GFP_KERNEL);
    if (!xs)
        return -ENOMEM;

    sock_init_data(sock, &xs->sk);
    sock->ops = &xsk_ops;

    return 0;
}
```

### 4.2 bind()

```c
// net/xdp/xsk.c:600
static int xsk_bind(struct socket *sock, struct sockaddr *addr, int addr_len)
{
    struct xdp_sock *xs = xdp_sk(sock);
    struct net_device *dev;

    // 获取设备
    dev = dev_get_by_index(net, ifindex);
    if (!dev)
        return -ENODEV;

    // 检查 XDP 支持
    if (!dev->netdev_ops->ndo_xdp_send)
        return -EOPNOTSUPP;

    xs->dev = dev;
    xs->queue_id = queue_id;
    xs->bound = true;

    return 0;
}
```

## 5. 发送/接收

### 5.1 sendmsg()

```c
// net/xdp/xsk.c:700
static int xsk_sendmsg(struct socket *sock, struct msghdr *m, size_t len)
{
    struct xdp_sock *xs = xdp_sk(sock);
    struct xsk_queue *tx = xs->tx;

    while (ndescs--) {
        // 获取描述符
        struct xdp_desc desc = xsk_tx_desc_get(tx);

        // 复制数据
        iov = memcpy_fromiovec(desc.addr, msg->msg_iov, len);

        // 发送
        xsk_tx_desc_ready(tx, desc);
    }

    // 触发发送
    dev->netdev_ops->ndo_xdp_send(dev, xs);
}
```

### 5.2 recvmsg()

```c
// net/xdp/xsk.c:800
static int xsk_recvmsg(struct socket *sock, struct msghdr *m, size_t len,
                        int flags)
{
    struct xdp_sock *xs = xdp_sk(sock);
    struct xsk_queue *rx = xs->rx;

    while (ndescs--) {
        // 获取接收描述符
        struct xdp_desc desc = xsk_rx_desc_get(rx);

        // 复制数据
        memcpyiovec(m->msg_iov, desc.addr, len);

        // 释放描述符
        xsk_rx_desc_release(rx, desc);
    }
}
```

## 6. UMEM 操作

### 6.1 mmap()

```c
// net/xdp/xsk.c:900
static int xsk_mmap(struct file *filp, struct socket *sock,
                     struct vm_area_struct *vma)
{
    struct xdp_sock *xs = xdp_sk(sock->sk);

    // 映射 UMEM 到用户空间
    return remap_vmalloc_range(vma, xs->umem->buffer, vma->vm_pgoff);
}
```

## 7. 使用示例

### 7.1 C 程序

```c
#include <linux/if_xdp.h>
#include <sys/socket.h>
#include <sys/mman.h>

int main() {
    int sock = socket(AF_XDP, SOCK_RAW, 0);
    struct sockaddr_xdp addr = {
        .sxdp_family = AF_XDP,
        .sxdp_ifindex = if_nametoindex("eth0"),
        .sxdp_queue_id = 0,
    };

    bind(sock, (struct sockaddr *)&addr, sizeof(addr));

    // 获取文件描述符
    struct xdp_mmap_offsets off;
    socklen_t len = sizeof(off);
    getsockopt(sock, SOL_XDP, XDP_MMAP_OFFSETS, &off, &len);

    // 映射 UMEM
    void *umem = mmap(NULL, UMEM_SIZE, PROT_READ | PROT_WRITE,
                      MAP_SHARED, sock, XDP_UMEM_REG);
}
```

## 8. 性能

### 8.1 基准

```
AF_INET:      ~500K pps
AF_XDP:       ~10M pps
AF_XDP+Zerocopy: ~15M pps
```

### 8.2 使用场景

```
1. 高性能负载均衡
2. 数据包采样
3. 网络测量
4. 内核旁路应用
```
