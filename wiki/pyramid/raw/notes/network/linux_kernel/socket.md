# Socket 层 - 通用套接字层

## 1. 模块架构

### 1.1 功能概述

Socket 层是 Linux 网络栈的核心抽象，提供了应用程序与内核网络子系统之间的接口。它屏蔽了底层协议细节，提供了统一的 socket API。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/socket.c` | BSD socket 实现 (约 2700 行) |
| `net/core/sock.c` | 通用 sock 实现 (约 6500 行) |
| `include/linux/net.h` | socket 核心定义 |
| `include/net/sock.h` | sock 结构定义 |

## 2. 核心数据结构

### 2.1 struct socket

```c
// include/linux/net.h:184
struct socket {
    socket_state            state;              // SS_* 状态
    unsigned long           flags;             // SOCK_NOSPACE, etc.
    struct fasync_struct   *fasync_list;      // 异步唤醒列表
    struct file             *file;             // 关联的文件
    struct sock             *sk;               // 关联的 sock
    const struct proto_ops  *ops;             // 协议操作函数集
};
```

### 2.2 struct proto_ops

```c
// include/linux/net.h:130
struct proto_ops {
    int                     family;              // 协议族

    // 绑定和连接
    int                     (*bind)(struct socket *sock,
                                     struct sockaddr *addr, int addr_len);
    int                     (*connect)(struct socket *sock,
                                       struct sockaddr *vaddr,
                                       int addr_len, int flags);

    // 监听和接受
    int                     (*listen)(struct socket *sock, int backlog);
    int                     (*accept)(struct socket *sock,
                                      struct socket *newsock, int flags,
                                      bool kern);

    // 数据传输
    int                     (*sendmsg)(struct socket *sock,
                                        struct msghdr *m, size_t total_len);
    int                     (*recvmsg)(struct socket *sock,
                                        struct msghdr *m, size_t total_len,
                                        int flags);

    // 关闭
    int                     (*release)(struct socket *sock);
    int                     (*shutdown)(struct socket *sock, int how);

    // 套接字选项
    int                     (*getsockopt)(struct socket *sock, int level,
                                           int optname, char __user *optval,
                                           int __user *optlen);
    int                     (*setsockopt)(struct socket *sock, int level,
                                           int optname, char __user *optval,
                                           unsigned int optlen);

    // 其他
    int                     (*poll)(struct file *file, struct socket *sock,
                                    struct poll_table_struct *wait);
    int                     (*ioctl)(struct socket *sock, unsigned int cmd,
                                      unsigned long arg);
    int                     (*getname)(struct socket *sock,
                                       struct sockaddr *addr,
                                       int peer);
};
```

### 2.3 struct sock (通用套接字)

```c
// include/net/sock.h:237
struct sock {
    // 链表
    struct sock             *sk_next;            // 下一个 sock
    struct sock             *sk_bind_node;       // 绑定哈希节点
    struct sk_buff_head     sk_receive_queue;   // 接收队列
    struct sk_buff_head     sk_write_queue;     // 发送队列
    struct sk_buff_head     sk_error_queue;    // 错误队列

    // 引用计数
    refcount_t              sk_refcnt;           // 引用计数

    // 协议
    __u8                    sk_protocol;        // 协议 (IPPROTO_*)
    unsigned short          sk_type;             // 套接字类型
    int                     sk_family;           // 协议族

    // 状态
    volatile unsigned char  sk_state;           // TCP: TCP_*_STATE
    unsigned char           sk_shutdown;         // 发送/接收关闭标志
    unsigned long           sk_flags;            // SO_* 选项

    // 地址
    struct {
        sk_buff_data_t     skc_tx_queue_mapping; // TX 队列映射
        sk_buff_data_t     skc_rx_queue_mapping; // RX 队列映射
    };
    union {
        struct {
            __be32          skc_rcv_saddr;      // 接收地址
            __be32          skc_v4_rcv_saddr;   // IPv4 接收地址
        };
        struct in6_addr    skc_v6_rcv_saddr;   // IPv6 接收地址
    };
    __be16                  skc_num;             // 源端口

    // 路由
    struct dst_entry        *sk_dst_cache;       // 路由缓存
    unsigned long           sk_dst_pending_confirm; // 路由确认
    u32                     sk_tx_queue_mapping; // TX 队列

    // 内存管理
    atomic_t                sk_wmem_alloc;       // 发送内存分配
    atomic_t                sk_rmem_alloc;       // 接收内存分配
    unsigned int            sk_forward_alloc;    // 转发分配
    unsigned int            sk_sndbuf;           // 发送缓冲区大小
    unsigned int            sk_rcvbuf;           // 接收缓冲区大小

    // 回调
    struct socket           *sk_socket;          // 反向指针
    void                    (*sk_data_ready)(struct sock *sk);
    void                    (*sk_write_space)(struct sock *sk);
    void                    (*sk_error_report)(struct sock *sk);
    int                     (*sk_rcv_ready)(struct sock *sk, struct sk_buff *skb);
    void                    (*sk_state_change)(struct sock *sk);
};
```

### 2.4 inet_sock (IPv4 套接字)

```c
// include/net/inet_sock.h:34
struct inet_sock {
    struct sock             sk;                  // 基类 (必须第一)

#if IS_ENABLED(CONFIG_IPV6)
    struct ipv6_pinfo       *pinet6;             // IPv6 信息
#endif

    // IPv4 特有
    __be32                  inet_saddr;           // 源地址
    __be16                  inet_sport;          // 源端口
    unsigned short           inet_daddr;         // 目的地址
    unsigned short           inet_dport;         // 目的端口
    __u8                    inet_ttl;            // TTL
    __u8                    inet_tos;            // TOS
    __u16                   inet_id;             // ID

    // 分片
    unsigned int            frag_ref;            // 分片引用
    __u8                    inet_dscp;           // DSCP

    // 选项
    struct ip_options_rcu   *inet_opt;          // IP 选项
    struct inet_request_sock *ireq_local;       // 监听请求

    // 校验和
    __u16                   inet_no_offset;      // 校验和偏移

    // 标识
    bool                    recverr;
    bool                    is_icsk;
    bool                    freebind;
    bool                    hdrincl;
    bool                    mc_loop;
    __u8                    mc_ttl;
    __u8                    mc_index;
    __u32                   mc_list;
};
```

## 3. Socket 创建流程

### 3.1 socket() 系统调用

```c
// net/socket.c:1519
SYSCALL_DEFINE3(socket, int, family, int, type, int, protocol)
{
    return __sys_socket(family, type, protocol);
}

// net/socket.c:1478
int __sys_socket(int family, int type, int protocol)
{
    struct socket *sock;
    int fd, err;

    // 1. 创建 socket 结构
    err = sock_create(family, type, protocol, &sock, kern);
    if (err < 0) return err;

    // 2. 分配文件描述符
    fd = get_unused_fd_flags(O_RDWR | (kern ? 0 : O_CLOEXEC));
    if (fd < 0) {
        sock_release(sock);
        return fd;
    }

    // 3. 关联文件
    sock->file = sock_alloc_file(sock, fd, NULL);

    // 4. 关联到进程
    fd_install(fd, sock->file);

    return fd;
}
```

### 3.2 sock_create

```c
// net/socket.c:424
int sock_create(int family, int type, int protocol, struct socket **res, int kern)
{
    return __sock_create(current->nsproxy->net_ns, family, type,
                         protocol, res, kern);
}

// net/socket.c:402
int __sock_create(struct net *net, int family, int type, int protocol,
                  struct socket **res, int kern)
{
    struct socket *sock;
    const struct net_proto_family *pf;
    struct proto *prot;
    int err;

    // 1. 分配 socket
    sock = sock_alloc();
    if (!sock) return -ENOMEM;

    // 2. 设置类型
    sock->type = type;

    // 3. 获取协议族
    pf = rcu_dereference(net_families[family]);
    if (!pf) {
        err = -EAFNOSUPPORT;
        goto out;
    }

    // 4. 获取协议
    prot = rcu_dereference(proto[family][type][protocol]);
    if (!prot) {
        err = -EPROTONOSUPPORT;
        goto out;
    }

    // 5. 调用协议族的 create 方法
    err = pf->create(net, sock, protocol, kern);
    if (err) goto out;

    *res = sock;
    return 0;

out:
    sock_release(sock);
    return err;
}
```

## 4. connect() 流程

### 4.1 inet_connect

```c
// net/ipv4/af_inet.c:724
int inet_stream_connect(struct socket *sock, struct sockaddr *uaddr,
                        int addr_len, int flags, int kern)
{
    struct sock *sk = sock->sk;
    int err;

    // 1. 处理非阻塞
    lock_sock(sk);
    if (inet->state == TCP_CLOSE)
        inet->state = TCP_SYN_SENT;

    // 2. 调用协议 connect
    err = inet->ops->connect(sock, uaddr, addr_len, flags);
    if (err) goto out;

    // 3. 等待连接建立
    err = wait_on_socket(sock, flags & O_NONBLOCK, 0);

out:
    release_sock(sk);
    return err;
}
```

## 5. bind() 流程

### 5.1 inet_bind

```c
// net/ipv4/af_inet.c:621
int inet_bind(struct socket *sock, struct sockaddr *uaddr, int addr_len, kern)
{
    struct sock *sk = sock->sk;
    struct inet_sock *inet = inet_sk(sk);
    struct sockaddr_in *addr = (struct sockaddr_in *)uaddr;
    unsigned short snum;

    // 1. 获取端口
    snum = ntohs(addr->sin_port);

    // 2. 端口重用检查
    if (snum && inet->inet_num == 0) {
        err = inet_release(sock);
        if (err) goto out;
    }

    // 3. 检查权限
    if (!kern && !ns_capable(net->user_ns, CAP_NET_BIND_SERVICE))
        if (snum < PROT_SOCK) goto out;

    // 4. 绑定到端口
    err = inet->ops->bind(sock, uaddr, addr_len);

out:
    return err;
}
```

## 6. listen() 流程

### 6.1 inet_listen

```c
// net/ipv4/af_inet.c:696
int inet_listen(struct socket *sock, int backlog)
{
    struct sock *sk = sock->sk;
    unsigned char old_state;

    lock_sock(sk);

    old_state = inet->state;
    if (old_state != TCP_CLOSE) {
        release_sock(sk);
        return -EINVAL;
    }

    // 切换到 LISTEN 状态
    inet->state = TCP_LISTEN;
    if (!inet->write_seq) {
        /* 初始化序列号 */
        inet->write_seq = secure_tcp_seq();
    }

    // 设置积压队列长度
    sk->sk_max_ack_backlog = backlog;
    sk->sk_ack_backlog = 0;

    release_sock(sk);
    return 0;
}
```

## 7. accept() 流程

### 7.1 inet_accept

```c
// net/ipv4/af_inet.c:666
int inet_accept(struct socket *sock, struct socket *newsock, int flags, bool kern)
{
    struct sock *sk = sock->sk;
    struct sock *newsk;
    int err;

    // 1. 从 accept 队列取出连接
    newsk = inet_csk_accept(sk, flags, &err, kern);
    if (!newsk) goto out;

    // 2. 关联新 socket
    newsock->state = SS_CONNECTED;
    newsock->sk = newsk;

out:
    return err;
}

// net/ipv4/inet_connection_socking.c:880
struct sock *inet_csk_accept(struct sock *sk, int flags, int *err, bool kern)
{
    struct inet_connection_sock *icsk = inet_csk(sk);
    struct request_sock *req;
    struct sock *newsk;

    // 从 accept 队列获取
    req = reqsk_queue_remove(&icsk->icsk_accept_queue);
    if (!req) {
        *err = wait_on_socket(sock, flags, timeo);
        goto out;
    }

    newsk = req->sk;
    sk_acceptq_removed(sk);

    reqsk_put(req);
    return newsk;
}
```

## 8. sendmsg()/recvmsg()

### 8.1 inet_sendmsg

```c
// net/ipv4/af_inet.c:1030
int inet_sendmsg(struct socket *sock, struct msghdr *msg, size_t size)
{
    struct sock *sk = sock->sk;

    // 调用协议特定实现
    return sk->sk_prot->sendmsg(sk, msg, size);
}
```

### 8.2 inet_recvmsg

```c
// net/ipv4/af_inet.c:1068
int inet_recvmsg(struct socket *sock, struct msghdr *msg, size_t size, int flags)
{
    struct sock *sk = sock->sk;

    // 调用协议特定实现
    return sk->sk_prot->recvmsg(sk, msg, size, flags);
}
```

## 9. 协议操作向量

### 9.1 inet_stream_ops (TCP)

```c
// net/ipv4/af_inet.c:1890
const struct proto_ops inet_stream_ops = {
    .family            = PF_INET,
    .owner            = THIS_MODULE,
    .release          = inet_release,
    .bind             = inet_bind,
    .connect          = inet_stream_connect,
    .socketpair       = sock_no_socketpair,
    .accept           = inet_accept,
    .getname          = inet_getname,
    .poll             = tcp_poll,
    .ioctl            = inet_ioctl,
    .listen           = inet_listen,
    .shutdown         = inet_shutdown,
    .setsockopt       = sock_common_setsockopt,
    .getsockopt       = sock_common_getsockopt,
    .sendmsg          = inet_sendmsg,
    .recvmsg          = inet_recvmsg,
    .mmap             = sock_no_mmap,
    .sendpage         = inet_sendpage,
    .sendmsg_locked   = tcp_sendmsg_locked,
    .recvmsg_locked   = tcp_recvmsg_locked,
};
```

### 9.2 inet_dgram_ops (UDP)

```c
// net/ipv4/af_inet.c:1856
const struct proto_ops inet_dgram_ops = {
    .family            = PF_INET,
    .owner            = THIS_MODULE,
    .release          = inet_release,
    .bind             = inet_bind,
    .connect          = inet_dgram_connect,
    .socketpair       = sock_no_socketpair,
    .accept           = sock_no_accept,
    .getname          = inet_getname,
    .poll             = udp_poll,
    .ioctl            = inet_ioctl,
    .listen           = sock_no_listen,
    .shutdown         = inet_shutdown,
    .setsockopt       = sock_common_setsockopt,
    .getsockopt       = sock_common_getsockopt,
    .sendmsg          = inet_sendmsg,
    .recvmsg          = inet_recvmsg,
    .mmap             = sock_no_mmap,
    .sendpage         = inet_sendpage,
};
```
