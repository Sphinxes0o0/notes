# Socket 系统调用

## 1. 模块架构

### 1.1 功能概述

Socket 系统调用是用户进程与内核网络栈交互的入口点，提供创建、连接、绑定、监听等操作。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/socket.c` | Socket 核心实现 |
| `net/scm.c` | Socket Control Message |
| `include/linux/net.h` | Socket 定义 |

## 2. Socket 创建

### 2.1 sys_socket()

```c
// net/socket.c:770
int __sys_socket(int family, int type, int protocol)
{
    int fd;
    struct socket *sock;

    // 1. 创建 socket
    sock = sock_create(family, type, protocol, &sock);
    if (IS_ERR(sock))
        return PTR_ERR(sock);

    // 2. 分配文件描述符
    fd = get_unused_fd_flags(O_RDWR);
    if (fd < 0) {
        sock_release(sock);
        return fd;
    }

    // 3. 关联到文件描述符
    fd_install(fd, sock->file);

    return fd;
}
```

### 2.2 sock_create()

```c
// net/socket.c:450
int sock_create(int family, int type, int protocol, struct socket **res)
{
    return __sock_create(current->nsproxy->net_ns, family, type,
                         protocol, res, 0);
}

int __sock_create(struct net *net, int family, int type, int protocol,
                 struct socket **res, int kern)
{
    struct socket *sock;
    const struct net_proto_family *pf;

    // 1. 分配 socket
    sock = sock_alloc();
    if (!sock)
        return -ENOMEM;

    // 2. 初始化
    sock->family = family;
    sock->type = type;
    sock->protocol = protocol;

    // 3. 调用协议族特定创建函数
    pf = rcu_dereference(net_families[family]);
    err = pf->create(sock, protocol);

    *res = sock;
    return err;
}
```

## 3. 绑定和监听

### 3.1 sys_bind()

```c
// net/socket.c:850
int __sys_bind(int fd, struct sockaddr *addr, int addrlen)
{
    struct socket *sock;
    struct sockaddr_storage address;

    // 获取 socket
    sock = sockfd_lookup(fd, &err);
    if (sock) {
        // 复制地址
        err = move_addr_to_kernel(addr, addrlen, &address);
        if (!err)
            // 调用 socket->ops->bind
            err = sock->ops->bind(sock, (struct sockaddr *)&address,
                                  addrlen);
        fput(sock->file);
    }
    return err;
}
```

### 3.2 sys_listen()

```c
// net/socket.c:920
int __sys_listen(int fd, int backlog)
{
    struct socket *sock;
    int err;

    sock = sockfd_lookup(fd, &err);
    if (sock) {
        // 调用 socket->ops->listen
        err = sock->ops->listen(sock, backlog);
        fput(sock->file);
    }
    return err;
}
```

## 4. 连接

### 4.1 sys_connect()

```c
// net/socket.c:890
int __sys_connect(int fd, struct sockaddr *addr, int addrlen)
{
    struct socket *sock;
    struct sockaddr_storage address;

    sock = sockfd_lookup(fd, &err);
    if (sock) {
        err = move_addr_to_kernel(addr, addrlen, &address);
        if (!err)
            err = sock->ops->connect(sock,
                                    (struct sockaddr *)&address,
                                    addrlen, 0);
        fput(sock->file);
    }
    return err;
}
```

### 4.2 accept()

```c
// net/socket.c:960
int __sys_accept4(int fd, struct sockaddr *u_peer_sockaddr,
                  int *u_peer_addrlen, int flags)
{
    struct socket *sock, *newsock;
    struct sockaddr_storage address;
    int err;

    sock = sockfd_lookup(fd, &err);
    if (sock) {
        // 从 backlog 取出或等待新连接
        err = sock->ops->accept(sock, &newsock, flags);
        if (!err) {
            // 分配新文件描述符
            newfd = get_unused_fd_flags(flags);
            if (newfd >= 0)
                fd_install(newfd, newsock->file);
            else
                sock_release(newsock);
        }
        fput(sock->file);
    }
    return err;
}
```

## 5. 发送/接收

### 5.1 sys_sendmsg()

```c
// net/socket.c:1280
int __sys_sendmsg(int fd, struct msghdr *msg, unsigned int flags)
{
    struct socket *sock;
    struct iovec iov;
    struct sockaddr_storage address;

    sock = sockfd_lookup(fd, &err);
    if (sock) {
        // 复制 msghdr 到内核
        err = copy_msghdr_from_user(&msg_sys, msg, &iov, &address);

        if (!err)
            err = sock_sendmsg(sock, &msg_sys);
        fput(sock->file);
    }
    return err;
}
```

### 5.2 sys_recvmsg()

```c
// net/socket.c:1320
int __sys_recvmsg(int fd, struct msghdr *msg, unsigned int flags)
{
    struct socket *sock;
    struct msghdr msg_sys;
    struct iovec iov;

    sock = sockfd_lookup(fd, &err);
    if (sock) {
        // 初始化 msg_sys
        err = copy_msghdr_from_user(&msg_sys, msg, &iov, NULL);

        if (!err)
            err = sock_recvmsg(sock, &msg_sys, flags);
        fput(sock->file);
    }
    return err;
}
```

## 6. close()

```c
// net/socket.c:680
int sock_close(struct inode *inode, struct file *filp)
{
    struct socket *sock;

    sock = filp->private_data;
    sock_release(sock);
    return 0;
}

void sock_release(struct socket *sock)
{
    // 调用协议特定清理
    if (sock->ops)
        sock->ops->release(sock);

    // 释放 socket
    sock_no_release(sock);
}
```

## 7. socket 文件操作

```c
// net/socket.c:180
static const struct proto_ops socket_ops = {
    .family = PF_UNSPEC,
    .owner = THIS_MODULE,
    .release = sock_close,
    .bind = sock_bind,
    .connect = sock_connect,
    .socketpair = sock_socketpair,
    .accept = sock_accept,
    .getname = sock_getname,
    .poll = sock_poll,
    .ioctl = sock_ioctl,
    .listen = sock_listen,
    .shutdown = sock_shutdown,
    .sendmsg = sock_sendmsg,
    .recvmsg = sock_recvmsg,
    .sendpage = sock_sendpage,
    .set_sockopt = sock_setsockopt,
    .get_sockopt = sock_getsockopt,
};
```
