# Unix Domain Socket

## 1. 模块架构

### 1.1 功能概述

Unix Domain Socket 是本地进程间通信的高效方式，支持流和数据报两种模式。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/unix/af_unix.c` | Unix socket 实现 |
| `net/unix/garbage.c` | Unix socket 垃圾回收 |
| `include/net/af_unix.h` | Unix socket 定义 |

## 2. 核心数据结构

### 2.1 struct unix_sock

```c
// include/net/af_unix.h:50
struct unix_sock {
    struct socket socket;
    struct unix_address *addr;
    struct path path;
    struct mutex lock;
    unsigned long flags;

    struct hlist_node link;
    struct socket *peer;

    struct list_head linklist;
    struct sk_buff_head receive_queue;
    struct sk_buff_head long_name;
};
```

### 2.2 struct unix_address

```c
// include/net/af_unix.h:30
struct unix_address {
    atomic_t refcnt;
    int len;
    unsigned int hash;
    struct sockaddr_un name;
};
```

### 2.3 struct unix_proto_ops

```c
// net/unix/af_unix.c:2500
static const struct proto_ops unix_stream_ops = {
    .family = PF_UNIX,
    .owner = THIS_MODULE,
    .release = unix_release,
    .bind = unix_bind,
    .connect = unix_stream_connect,
    .socketpair = unix_socketpair,
    .accept = unix_accept,
    .getname = unix_getname,
    .poll = unix_poll,
    .ioctl = unix_ioctl,
    .listen = unix_listen,
    .shutdown = unix_shutdown,
    .sendmsg = unix_stream_sendmsg,
    .recvmsg = unix_stream_recvmsg,
};
```

## 3. 地址

### 3.1 unix_bind()

```c
// net/unix/af_unix.c:1600
static int unix_bind(struct socket *sock, struct sockaddr *uaddr,
                     int addr_len)
{
    struct sockaddr_un *sunaddr = (struct sockaddr_un *)uaddr;
    struct unix_sock *u = unix_sk(sock);
    struct dentry *dentry;

    // 创建 socket 文件
    dentry = kern_path_create(AT_FDCWD, sunaddr->sun_path, &path, 0);
    if (IS_ERR(dentry))
        return PTR_ERR(dentry);

    // 绑定到路径
    u->path = path;
    u->addr = unix_addr(sunaddr->sun_path);

    return 0;
}
```

## 4. 连接

### 4.1 unix_stream_connect()

```c
// net/unix/af_unix.c:1800
static int unix_stream_connect(struct socket *sock,
                               struct sockaddr *uaddr, int addr_len, int flags)
{
    struct sockaddr_un *sunaddr = (struct sockaddr_un *)uaddr;
    struct socket *other;
    struct unix_sock *u, *other_u;

    // 查找目标 socket
    other = unix_find_other(sunaddr->sun_path);
    if (IS_ERR(other))
        return PTR_ERR(other);

    other_u = unix_sk(other);

    // 连接
    unix_state_lock(other);
    if (other_u->peer) {
        unix_state_unlock(other);
        return -ECONNREFUSED;
    }

    // 互相引用
    sock_hold(sock);
    other_u->peer = sock;
    u->peer = other;

    unix_state_unlock(other);
    return 0;
}
```

### 4.2 unix_accept()

```c
// net/unix/af_unix.c:1700
static int unix_accept(struct socket *sock, struct socket *newsock, int flags)
{
    struct sock *sk = sock->sk;
    struct sk_buff *skb;

    unix_state_lock(sk);

    // 从队列取出
    skb = skb_dequeue(&unix_sk(sk)->receive_queue);
    if (!skb) {
        // 等待连接
        err = unix_wait_for_accept(sock, flags);
        skb = skb_dequeue(&unix_sk(sk)->receive_queue);
    }

    // 创建新 socket
    newsock->state = SS_CONNECTED;
    newsock->ops = sock->ops;

    unix_state_unlock(sk);
    return 0;
}
```

## 5. 发送/接收

### 5.1 unix_stream_sendmsg()

```c
// net/unix/af_unix.c:2100
static int unix_stream_sendmsg(struct socket *sock,
                                struct msghdr *msg, size_t len)
{
    struct sock *sk = sock->sk;
    struct unix_sock *u = unix_sk(sk);
    struct sk_buff *skb;
    int err;

    // 创建 skb
    skb = sock_alloc_send_skb(sk, len + sizeof(struct unix_skb_parms),
                               msg->msg_flags & MSG_DONTWAIT, &err);

    // 复制数据
    err = memcpy_from_msg(skb_put(skb, len), msg, len);

    // 放入接收队列
    unix_state_lock_nested(u->peer);
    skb_queue_tail(&unix_sk(u->peer)->receive_queue, skb);
    unix_state_unlock(u->peer);

    // 唤醒等待者
    sk->sk_data_ready(sk);

    return len;
}
```

### 5.2 unix_stream_recvmsg()

```c
// net/unix/af_unix.c:2200
static int unix_stream_recvmsg(struct socket *sock,
                                struct msghdr *msg, size_t size,
                                int flags)
{
    struct sock *sk = sock->sk;
    struct sk_buff *skb;

    // 从队列取出
    skb = skb_dequeue(&unix_sk(sk)->receive_queue);
    if (!skb) {
        if (flags & MSG_DONTWAIT)
            return -EAGAIN;
        // 等待数据
    }

    // 复制数据
    err = skb_copy_datagram_msg(skb, 0, msg, skb->len);

    // 释放 skb
    consume_skb(skb);

    return err;
}
```

## 6. 垃圾回收

### 6.1 unix_gc()

```c
// net/unix/garbage.c:100
void unix_gc(void)
{
    struct unix_sock *u;
    struct hlist_node *p;
    unsigned int cycle = 0;

    // 遍历所有 Unix socket
    spin_lock(&unix_gc_lock);
    hlist_for_each_entry(u, p, &unix_sockets, link) {
        u->gc_flags |= UNIX_GC_CANDIDATE;
        u->gc_cycle = cycle;
    }

    // 标记不可达的对象
    // 清理循环引用
    spin_unlock(&unix_gc_lock);
}
```

## 7. 权限

### 7.1 SO_PEERCRED

```c
// 获取对端进程凭证
struct ucred {
    pid_t pid;     // 进程 ID
    uid_t uid;     // 用户 ID
    gid_t gid;     // 组 ID
};

// 通过 getsockopt SO_PEERCRED 获取
```
