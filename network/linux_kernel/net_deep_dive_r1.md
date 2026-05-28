# Linux Net 子系统深度分析 R1

## 目录
1. [Socket Layer](#1-socket-layer)
2. [sk_buff 数据结构](#2-sk_buff-数据结构)
3. [Netdevice 网络设备](#3-netdevice-网络设备)
4. [Routing 路由子系统](#4-routing-路由子系统)
5. [Netfilter Hooks](#5-netfilter-hooks)
6. [TCP/UDP 协议实现](#6-tcpudp-协议实现)
7. [知识点关联表格](#7-知识点关联表格)

---

## 1. Socket Layer

### 1.1 struct socket 数据结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/net.h:116-128`

```c
struct socket {
    socket_state        state;          // SS_FREE, SS_UNCONNECTED, SS_CONNECTING, SS_CONNECTED
    short               type;           // SOCK_STREAM, SOCK_DGRAM, SOCK_RAW 等
    unsigned long       flags;
    struct file         *file;          // 关联的文件结构
    struct sock         *sk;            // 关联的 inet sock
    const struct proto_ops *ops;        // 协议操作集
    struct socket_wq    *wq;            // 等待队列
};
```

### 1.2 struct sock 数据结构

**源码位置**: `/Users/sphinx/github/linux/include/net/sock.h:360-450`

```c
struct sock {
    struct sock_common  __sk_common;     // 公共成员
    
    /* 接收/发送队列 */
    struct sk_buff_head sk_receive_queue; // 接收数据队列
    struct sk_buff_head sk_write_queue;   // 发送数据队列
    
    /* backlog 队列 */
    struct {
        atomic_t rmem_alloc;
        int      len;
        struct sk_buff *head;
        struct sk_buff *tail;
    } sk_backlog;
    
    /* 协议特定操作 */
    const struct proto *sk_prot;        // 协议操作集
    const struct proto_ops *sk_ops;     // Socket 操作集
    
    /* 状态和选项 */
    __u8           sk_state;            // TCP: ESTABLISHED, LISTEN, CLOSE_WAIT 等
    unsigned short sk_type;            // SOCK_STREAM, SOCK_DGRAM
    int            sk_protocol;        // IPPROTO_TCP, IPPROTO_UDP
    
    /* 内存管理 */
    atomic_t       sk_drops;           // 丢包计数
    int            sk_rcvbuf;          // 接收缓冲区大小
    
    /* 定时器 */
    struct timer_list sk_timer;        // 重传定时器
};
```

### 1.3 sock_alloc() 函数

**源码位置**: `/Users/sphinx/github/linux/net/socket.c:632-650`

```c
struct socket *sock_alloc(void)
{
    struct inode *inode;
    struct socket *sock;

    inode = new_inode_pseudo(sock_mnt->mnt_sb);
    if (!inode)
        return NULL;

    sock = SOCKET_I(inode);
    inode->i_ino = get_next_ino();
    inode->i_mode = S_IFSOCK | S_IRWXUGO;
    inode->i_uid = current_fsuid();
    inode->i_gid = current_fsgid();
    inode->i_op = &sockfs_inode_ops;

    return sock;
}
```

### 1.4 inet_bind() 函数

**源码位置**: `/Users/sphinx/github/linux/net/ipv4/af_inet.c:473-530`

```c
int __inet_bind(struct sock *sk, struct sockaddr *uaddr, int addr_len, u32 flags)
{
    struct sockaddr_in *addr = (struct sockaddr_in *)uaddr;
    struct inet_sock *inet = inet_sk(sk);
    struct net *net = sock_net(sk);
    unsigned short snum;
    
    if (addr->sin_family != AF_INET)
        return -EAFNOSUPPORT;
    
    snum = ntohs(addr->sin_port);
    
    err = inet_bind_hash(sk, inet, snum, tb_id);
    
    return err;
}
```

---

## 2. sk_buff 数据结构

### 2.1 struct sk_buff 核心结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/skbuff.h:885-980`

```c
struct sk_buff {
    /* 双向链表指针 */
    union {
        struct {
            struct sk_buff *next;      // 下一个 skb
            struct sk_buff *prev;      // 上一个 skb
            union {
                struct net_device *dev;
                unsigned long dev_scratch;
            };
        };
        struct rb_node rbnode;
        struct list_head list;
    };

    struct sock *sk;
    union {
        ktime_t tstamp;
        u64 skb_mstamp_ns;
    };

    char cb[48] __aligned(8);         // 控制缓冲区

    unsigned int len;                  // 数据总长度
    unsigned int data_len;            // 数据长度(非线性部分)
    __u16 mac_len;                  // MAC 头长度
    __u16 hdr_len;                  // 可写头长度

    /* 克隆状态 */
    __u8 cloned:1;
    __u8 nohdr:1;
    __u8 fclone:2;
};
```

### 2.2 skb_put / skb_push 函数

```c
// skb_put - 在尾部添加数据
static inline void *__skb_put(struct sk_buff *skb, unsigned int len)
{
    void *tmp = skb_tail_pointer(skb);
    skb->tail += len;
    skb->len  += len;
    return tmp;
}

// skb_push - 在头部添加数据
static inline void *__skb_push(struct sk_buff *skb, unsigned int len)
{
    skb->data -= len;
    skb->len  += len;
    return skb->data;
}
```

### 2.3 skb_shared_info 结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/skbuff.h:593-630`

```c
struct skb_shared_info {
    __u8        flags;
    __u8        nr_frags;           // 碎片数量
    unsigned short gso_size;        // GSO 大小
    unsigned short gso_segs;        // GSO 段数
    struct sk_buff *frag_list;      // 碎片列表
    
    atomic_t dataref;               // 数据引用计数
};
```

---

## 3. Netdevice 网络设备

### 3.1 struct net_device 数据结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/netdevice.h:2109-2200`

```c
struct net_device {
    /* TX 热路径 */
    unsigned long priv_flags:32;
    const struct net_device_ops *netdev_ops;
    struct netdev_queue *_tx;
    unsigned int real_num_tx_queues;
    unsigned int mtu;
    unsigned short hard_header_len;
    
    /* 统计信息 */
    union {
        struct pcpu_lstats __percpu *lstats;
        struct pcpu_sw_netstats __percpu *tstats;
    };
    
    unsigned int flags;
    struct netdev_rx_queue *_rx;
    rx_handler_func_t __rcu *rx_handler;
    
    char name[IFNAMSIZ];
    int ifindex;
};
```

### 3.2 dev_queue_xmit() 发送流程

**源码位置**: `/Users/sphinx/github/linux/net/core/dev.c:4760-4893`

```c
int __dev_queue_xmit(struct sk_buff *skb, struct net_device *sb_dev)
{
    struct net_device *dev = skb->dev;
    struct netdev_queue *txq;
    struct Qdisc *q;
    
    skb_reset_mac_header(skb);
    txq = skb_get_tx_queue(dev, skb);
    
    rcu_read_lock_bh();
    
    q = rcu_dereference(txq->qdisc);
    
    if (q->enqueue == NULL) {
        rc = dev_hard_start_xmit(skb, dev, txq);
    } else {
        rc = q->enqueue(skb, q, &to_free) & &rc;
        if (to_free)
            kfree_skb_list(to_free);
        qdisc_run(txq);
    }
    
    rcu_read_unlock_bh();
    return rc;
}
```

---

## 4. Routing 路由子系统

### 4.1 struct rtable 数据结构

**源码位置**: `/Users/sphinx/github/linux/include/net/route.h:57-78`

```c
struct rtable {
    struct dst_entry dst;
    
    int rt_genid;
    unsigned int rt_flags;
    __u16 rt_type;
    __u8 rt_is_input:1;
    __u8 rt_uses_gateway:1;
    
    int rt_iif;
    
    union {
        __be32 rt_gw4;
        struct in6_addr rt_gw6;
    };
};
```

### 4.2 fib_lookup() 路由查找

**源码位置**: `/Users/sphinx/github/linux/net/ipv4/fib_frontend.c:280-308`

```c
int fib_lookup(struct net *net, const struct flowi4 *flp,
               struct fib_result *res, unsigned int flags)
{
    struct fib_table *tb;
    
    tb = fib_get_table(net, RT_TABLE_MAIN);
    if (!tb)
        return -ENOENT;
    
    return fib_table_lookup(tb, flp, res, flags);
}
```

---

## 5. Netfilter Hooks

### 5.1 struct nf_hook_ops 数据结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/netfilter.h:98-111`

```c
struct nf_hook_ops {
    struct list_head list;
    struct rcu_head rcu;
    
    nf_hookfn *hook;
    struct net_device *dev;
    void *priv;
    u8 pf;
    unsigned int hooknum;
    int priority;
};
```

### 5.2 Hook 点定义

```c
enum nf_INET_hooks {
    NF_INET_PRE_ROUTING,    // 0 - 接收后,路由查找前
    NF_INET_LOCAL_IN,       // 1 - 目的地是本机
    NF_INET_FORWARD,        // 2 - 转发
    NF_INET_LOCAL_OUT,     // 3 - 本机发送
    NF_INET_POST_ROUTING,   // 4 - 发送前
    NF_INET_NUMHOOKS
};
```

---

## 6. TCP/UDP 协议实现

### 6.1 TCP 状态机

```c
enum {
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
    TCP_CLOSING,
    TCP_NEW_SYN_RECV,
};
```

### 6.2 struct udp_sock

**源码位置**: `/Users/sphinx/github/linux/include/net/udp.h:40-50`

```c
struct udp_sock {
    struct sock sk;
    struct udp_hslot *udp_table;
    int bind_portaddr_hash;
    bool no_check6_tx;
    bool no_check6_rx;
    atomic_t hchgs;
};
```

### 6.3 UDP 校验和计算

```c
static inline __wsum udp_csum_outgoing(struct sock *sk, struct sk_buff *skb)
{
    __wsum csum = csum_partial(skb_transport_header(skb),
                               sizeof(struct udphdr), 0);
    return csum;
}

static inline __sum16 udp_v4_check(int len, __be32 saddr,
                                   __be32 daddr, __wsum base)
{
    return csum_tcpudp_magic(saddr, daddr, len, IPPROTO_UDP, base);
}
```

---

## 7. 知识点关联表格

### 7.1 数据结构关联表

| 结构体 | 文件位置 | 关联结构 |
|--------|----------|----------|
| `struct socket` | `include/linux/net.h:116` | `struct sock` |
| `struct sock` | `include/net/sock.h:360` | `struct sk_buff`, `struct inet_sock` |
| `struct sk_buff` | `include/linux/skbuff.h:885` | `struct net_device`, `struct sock` |
| `struct net_device` | `include/linux/netdevice.h:2109` | `struct netdev_queue`, `struct Qdisc` |
| `struct rtable` | `include/net/route.h:57` | `struct dst_entry` |

### 7.2 核心函数调用链

| 功能路径 | 函数调用链 |
|----------|------------|
| Socket 创建 | `socket()` → `sock_alloc()` → `inet_create()` |
| 数据发送 | `sendmsg()` → `inet_sendmsg()` → `tcp_sendmsg()`/`udp_sendmsg()` |
| 包发送设备 | `dev_queue_xmit()` → `__dev_queue_xmit()` → `sch_handle_egress()` |
| 包接收设备 | `netif_receive_skb()` → `__netif_receive_skb()` → `rx_handler()` |
| 路由查找 | `fib_lookup()` → `fib_table_lookup()` |

### 7.3 TCP/UDP 核心函数对比

| 功能 | TCP | UDP |
|------|-----|-----|
| 发送函数 | `tcp_sendmsg()` | `udp_sendmsg()` |
| 接收函数 | `tcp_recvmsg()` | `udp_recvmsg()` |
| 连接建立 | `tcp_v4_connect()` | 不需要连接 |
| 监听 | `inet_listen()` | 不支持 |
| 校验和 | `tcp_v4_check()` | `udp_v4_check()` |

---

## 总结

Linux Net 子系统是一个复杂的分层架构:

1. **Socket Layer** 提供统一的 BSD Socket 接口,支持多种协议
2. **sk_buff** 实现高效的包缓冲管理,支持克隆和复制
3. **Netdevice** 提供网络设备的抽象,支持发送和接收队列
4. **Routing** 实现灵活的路由查找和输出路径
5. **Netfilter** 提供强大的包过滤框架
6. **TCP/UDP** 实现可靠的传输协议

---

**文档版本**: R1  
**分析源码版本**: Linux Kernel (latest)  
**生成时间**: 2026-04-27
