# Linux 内核网络子系统 - Socket Core 分析文档

## 目录
1. [net/socket.c 分析](#1-netsocketc-分析)
2. [net/core/sock.c 分析](#2-netcoresockc-分析)
3. [内存分配与释放路径](#3-内存分配与释放路径)

---

## 1. net/socket.c 分析

### 1.1 socket() 系统调用

**文件**: `net/socket.c:1759-1762`

```c
SYSCALL_DEFINE3(socket, int, family, int, type, int, protocol)
{
	return __sys_socket(family, type, protocol);
}
```

**实际实现** - `__sys_socket()`: 行 1742-1757

```c
int __sys_socket(int family, int type, int protocol)
{
	struct socket *sock;
	int flags;

	sock = __sys_socket_create(family, type,
				   update_socket_protocol(family, type, protocol));
	if (IS_ERR(sock))
		return PTR_ERR(sock);

	flags = type & ~SOCK_TYPE_MASK;
	if (SOCK_NONBLOCK != O_NONBLOCK && (flags & SOCK_NONBLOCK))
		flags = (flags & ~SOCK_NONBLOCK) | O_NONBLOCK;

	return sock_map_fd(sock, flags & (O_CLOEXEC | O_NONBLOCK));
}
```

### 1.2 socket 创建核心函数

**`__sock_create()` - 真正创建 socket**: 行 1534-1647

```c
int __sock_create(struct net *net, int family, int type, int protocol,
		 struct socket **res, int kern)
{
	int err;
	struct socket *sock;
	const struct net_proto_family *pf;

	if (family < 0 || family >= NPROTO)
		return -EAFNOSUPPORT;
	if (type < 0 || type >= SOCK_MAX)
		return -EINVAL;

	sock = sock_alloc();  // 行 1569
	if (!sock) {
		net_warn_ratelimited("socket: no more sockets\n");
		return -ENFILE;
	}

	sock->type = type;

	rcu_read_lock();
	pf = rcu_dereference(net_families[family]);
	if (!pf)
		goto out_release;

	err = pf->create(net, sock, protocol, kern);
	if (err < 0)
		goto out_module_put;

	*res = sock;
	return 0;
}
```

### 1.3 `sock_alloc()` - 分配 struct socket

**文件**: `net/socket.c:632-651`

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

**关键点**: socket 与 inode 通过 `struct socket_alloc` 嵌入在一起:

**文件**: `include/net/sock.h:1530-1533`

```c
struct socket_alloc {
	struct socket socket;
	struct inode vfs_inode;
};
```

**宏定义** (行 1535-1542):
```c
static inline struct socket *SOCKET_I(struct inode *inode)
{
	return &container_of(inode, struct socket_alloc, vfs_inode)->socket;
}

static inline struct inode *SOCK_INODE(struct socket *socket)
{
	return &container_of(socket, struct socket_alloc, socket)->vfs_inode;
}
```

### 1.4 `sock_alloc_file()` - 分配文件并建立关联

**行**: 476-502

```c
struct file *sock_alloc_file(struct socket *sock, int flags, const char *dname)
{
	struct file *file;

	if (!dname)
		dname = sock->sk ? sock->sk->sk_prot_creator->name : "";

	file = alloc_file_pseudo(SOCK_INODE(sock), sock_mnt, dname,
				O_RDWR | (flags & O_NONBLOCK),
				&socket_file_ops);
	if (IS_ERR(file)) {
		sock_release(sock);
		return file;
	}

	file->f_mode |= FMODE_NOWAIT;
	sock->file = file;           // socket -> file
	file->private_data = sock;   // file -> socket 双向关联
	stream_open(SOCK_INODE(sock), file);
	file_set_fsnotify_mode(file, FMODE_NONOTIFY_PERM);
	return file;
}
```

### 1.5 `sock_map_fd()` - 分配文件描述符

**行**: 504-521

```c
static int sock_map_fd(struct socket *sock, int flags)
{
	struct file *newfile;
	int fd = get_unused_fd_flags(flags);
	if (unlikely(fd < 0)) {
		sock_release(sock);
		return fd;
	}

	newfile = sock_alloc_file(sock, flags, NULL);
	if (!IS_ERR(newfile)) {
		fd_install(fd, newfile);  // 建立 fd -> file 映射
		return fd;
	}

	put_unused_fd(fd);
	return PTR_ERR(newfile);
}
```

### 1.6 `sock_release()` - 释放 socket

**行**: 688-692

```c
void sock_release(struct socket *sock)
{
	__sock_release(sock, NULL);
}
```

**`__sock_release()` 实际释放逻辑**: 行 653-678

```c
static void __sock_release(struct socket *sock, struct inode *inode)
{
	const struct proto_ops *ops = READ_ONCE(sock->ops);

	if (ops) {
		struct module *owner = ops->owner;

		if (inode)
			inode_lock(inode);
		ops->release(sock);        // 调用协议特定的 release
		sock->sk = NULL;
		if (inode)
			inode_unlock(inode);
		sock->ops = NULL;
		module_put(owner);
	}

	if (sock->wq.fasync_list)
		pr_err("%s: fasync list not empty!\n", __func__);

	if (!sock->file) {
		iput(SOCK_INODE(sock));
		return;
	}
	WRITE_ONCE(sock->file, NULL);
}
```

**`sock_close()` - 文件关闭时调用**: 行 1453-1457

```c
static int sock_close(struct inode *inode, struct file *filp)
{
	__sock_release(SOCKET_I(inode), inode);
	return 0;
}
```

### 1.7 struct socket 定义

**文件**: `include/linux/net.h:116-128`

```c
struct socket {
	socket_state		state;
	short			type;
	unsigned long		flags;
	struct file		*file;
	struct sock		*sk;
	const struct proto_ops	*ops;
	struct socket_wq	wq;
};
```

### 1.8 socket_file_ops - 文件操作函数表

**行**: 156-173

```c
static const struct file_operations socket_file_ops = {
	.owner =	THIS_MODULE,
	.read_iter =	sock_read_iter,
	.write_iter =	sock_write_iter,
	.poll =		sock_poll,
	.unlocked_ioctl = sock_ioctl,
	.mmap =		sock_mmap,
	.release =	sock_close,
	.fasync =	sock_fasync,
	.splice_write = splice_to_socket,
	.splice_read =	sock_splice_read,
	.splice_eof =	sock_splice_eof,
	.show_fdinfo =	sock_show_fdinfo,
};
```

---

## 2. net/core/sock.c 分析

### 2.1 struct sock 定义

**文件**: `include/net/sock.h:360-559`

`struct sock` 是内核网络协议栈的核心数据结构:

```c
struct sock {
	/* 第一个成员: sock_common, 所有协议共享 */
	struct sock_common	__sk_common;
#define sk_node			__sk_common.skc_node
#define sk_refcnt		__sk_common.skc_refcnt
#define sk_hash			__sk_common.skc_hash
#define sk_family		__sk_common.skc_family
#define sk_state		__sk_common.skc_state
#define sk_prot			__sk_common.skc_prot

	/* 接收队列 */
	struct {
		atomic_t	rmem_alloc;
		int		len;
		struct sk_buff	*head;
		struct sk_buff	*tail;
	} sk_backlog;

	/* 等待队列 */
	union {
		struct socket_wq __rcu	*sk_wq;
		struct socket_wq	*sk_wq_raw;
	};

	/* 回调函数 */
	void			(*sk_data_ready)(struct sock *sk);
	void			(*sk_write_space)(struct sock *sk);
	void			(*sk_error_report)(struct sock *sk);
	int			(*sk_destruct)(struct sock *sk);

	/* 重要成员 */
	struct socket		*sk_socket;
	u16			sk_protocol;
	u16			sk_type;
	int			sk_rcvbuf;
	int			sk_sndbuf;

	/* 锁 */
	socket_lock_t		sk_lock;
	rwlock_t		sk_callback_lock;

	/* 引用计数 */
	refcount_t		sk_wmem_alloc;
	refcount_t		sk_refcnt;

	/* 状态标志 */
	u8			sk_gso_disabled : 1,
				sk_kern_sock : 1,
				sk_no_check_tx : 1,
				sk_no_check_rx : 1;
	u8			sk_shutdown;
};
```

### 2.2 struct sock_common 定义

**行**: 151-206

```c
struct sock_common {
	union {
		__addrpair	skc_addrpair;
		struct {
			__be32	skc_daddr;
			__be32	skc_rcv_saddr;
		};
	};
	union {
		unsigned int	skc_hash;
		__u16		skc_u16hashes[2];
	};
	union {
		__portpair	skc_portpair;
		struct {
			__be16	skc_dport;
			__u16	skc_num;
		};
	};

	unsigned short		skc_family;
	unsigned char		skc_state;
	unsigned char		skc_reuse;
	unsigned char		skc_reuseport;
	int			skc_bound_dev_if;
	struct proto		*skc_prot;
	struct net		*skc_net;

	struct hlist_node	skc_node;
	struct hlist_nulls_node skc_nulls_node;
	struct hlist_node	skc_bind_node;

	refcount_t		skc_refcnt;
};
```

### 2.3 `inet_stream_ops` - TCP 流套接字操作表

**文件**: `net/ipv4/af_inet.c:1066-1098`

```c
const struct proto_ops inet_stream_ops = {
	.family		   = PF_INET,
	.owner		   = THIS_MODULE,
	.release	   = inet_release,
	.bind		   = inet_bind,
	.connect	   = inet_stream_connect,
	.accept		   = inet_accept,
	.getname	   = inet_getname,
	.poll		   = tcp_poll,
	.ioctl		   = inet_ioctl,
	.listen		   = inet_listen,
	.shutdown	   = inet_shutdown,
	.setsockopt	   = sock_common_setsockopt,
	.getsockopt	   = sock_common_getsockopt,
	.sendmsg	   = inet_sendmsg,
	.recvmsg	   = inet_recvmsg,
	.splice_read	   = tcp_splice_read,
};
```

### 2.4 `inet_dgram_ops` - UDP 数据报套接字操作表

**行**: 1101-1127

```c
const struct proto_ops inet_dgram_ops = {
	.family		   = PF_INET,
	.owner		   = THIS_MODULE,
	.release	   = inet_release,
	.bind		   = inet_bind,
	.connect	   = inet_dgram_connect,
	.accept		   = sock_no_accept,
	.getname	   = inet_getname,
	.poll		   = udp_poll,
	.ioctl		   = inet_ioctl,
	.listen		   = sock_no_listen,
	.shutdown	   = inet_shutdown,
	.setsockopt	   = sock_common_setsockopt,
	.getsockopt	   = sock_common_getsockopt,
	.sendmsg	   = inet_sendmsg,
	.recvmsg	   = inet_recvmsg,
};
```

### 2.5 `sock_sendmsg()` - 发送消息

**文件**: `net/socket.c:753-771`

```c
int sock_sendmsg(struct socket *sock, struct msghdr *msg)
{
	struct sockaddr_storage *save_addr = (struct sockaddr_storage *)msg->msg_name;
	struct sockaddr_storage address;
	int save_len = msg->msg_namelen;
	int ret;

	if (msg->msg_name) {
		memcpy(&address, msg->msg_name, msg->msg_namelen);
		msg->msg_name = &address;
	}

	ret = __sock_sendmsg(sock, msg);
	msg->msg_name = save_addr;
	msg->msg_namelen = save_len;

	return ret;
}
```

**`__sock_sendmsg()`** (行 737-743):
```c
static int __sock_sendmsg(struct socket *sock, struct msghdr *msg)
{
	int err = security_socket_sendmsg(sock, msg, msg_data_left(msg));
	return err ?: sock_sendmsg_nosec(sock, msg);
}
```

**`sock_sendmsg_nosec()`** (行 725-735):
```c
static inline int sock_sendmsg_nosec(struct socket *sock, struct msghdr *msg)
{
	int ret = INDIRECT_CALL_INET(READ_ONCE(sock->ops)->sendmsg, inet6_sendmsg,
				     inet_sendmsg, sock, msg,
				     msg_data_left(msg));
	return ret;
}
```

### 2.6 `sock_recvmsg()` - 接收消息

**行**: 1096-1102

```c
int sock_recvmsg(struct socket *sock, struct msghdr *msg, int flags)
{
	int err = security_socket_recvmsg(sock, msg, msg_data_left(msg), flags);
	return err ?: sock_recvmsg_nosec(sock, msg, flags);
}
```

**`sock_recvmsg_nosec()`** (行 1075-1085):
```c
static inline int sock_recvmsg_nosec(struct socket *sock, struct msghdr *msg,
				     int flags)
{
	int ret = INDIRECT_CALL_INET(READ_ONCE(sock->ops)->recvmsg,
				     inet6_recvmsg,
				     inet_recvmsg, sock, msg,
				     msg_data_left(msg), flags);
	return ret;
}
```

### 2.7 `sock_init_data()` - 初始化 struct sock

**行**: 3767-3775

```c
void sock_init_data(struct socket *sock, struct sock *sk)
{
	kuid_t uid = sock ?
		SOCK_INODE(sock)->i_uid :
		make_kuid(sock_net(sk)->user_ns, 0);

	sock_init_data_uid(sock, sk, uid);
}
```

**`sock_init_data_uid()`** - 实际初始化 (行 3696-3764):

```c
void sock_init_data_uid(struct socket *sock, struct sock *sk, kuid_t uid)
{
	sk_init_common(sk);
	sk->sk_send_head	=	NULL;

	timer_setup(&sk->sk_timer, NULL, 0);

	sk->sk_allocation	=	GFP_KERNEL;
	sk->sk_rcvbuf		=	READ_ONCE(sysctl_rmem_default);
	sk->sk_sndbuf		=	READ_ONCE(sysctl_wmem_default);
	sk->sk_state		=	TCP_CLOSE;

	sk_set_socket(sk, sock);

	sock_set_flag(sk, SOCK_ZAPPED);

	if (sock) {
		sk->sk_type	=	sock->type;
		RCU_INIT_POINTER(sk->sk_wq, &sock->wq);
		sock->sk	=	sk;
	} else {
		RCU_INIT_POINTER(sk->sk_wq, NULL);
	}

	sk->sk_uid	=	uid;

	sk->sk_state_change	=	sock_def_wakeup;
	sk->sk_data_ready	=	sock_def_readable;
	sk->sk_write_space	=	sock_def_write_space;
	sk->sk_error_report	=	sock_def_error_report;
	sk->sk_destruct		=	sock_def_destruct;

	refcount_set(&sk->sk_refcnt, 1);
}
```

**`sk_set_socket()`** (sock.h 行 2099-2109):
```c
static inline void sk_set_socket(struct sock *sk, struct socket *sock)
{
	WRITE_ONCE(sk->sk_socket, sock);
	if (sock) {
		WRITE_ONCE(sk->sk_uid, SOCK_INODE(sock)->i_uid);
		WRITE_ONCE(sk->sk_ino, SOCK_INODE(sock)->i_ino);
	} else {
		WRITE_ONCE(sk->sk_ino, 0);
	}
}
```

---

## 3. 内存分配与释放路径

### 3.1 Socket 分配路径

```
socket() [sys_socket]
  └─> __sys_socket()
       ├─> __sys_socket_create()
       │   └─> sock_create()
       │       └─> __sock_create()
       │           ├─> sock_alloc()           // 分配 struct socket + inode
       │           └─> pf->create()           // 调用协议特定创建 (inet_create)
       │               ├─> sk_alloc()        // 分配 struct sock
       │               └─> sock_init_data()
       │
       └─> sock_map_fd()
           ├─> get_unused_fd_flags()
           └─> sock_alloc_file()
               └─> alloc_file_pseudo()
               └─> fd_install()
```

### 3.2 `sk_alloc()` - struct sock 分配

**文件**: `net/core/sock.c:2296-2337`

```c
struct sock *sk_alloc(struct net *net, int family, gfp_t priority,
		      struct proto *prot, int kern)
{
	struct sock *sk;

	sk = sk_prot_alloc(prot, priority | __GFP_ZERO, family);
	if (sk) {
		sk->sk_family = family;
		sk->sk_prot = sk->sk_prot_creator = prot;
		sk->sk_kern_sock = kern;
		sock_lock_init(sk);
		refcount_set(&sk->sk_wmem_alloc, SK_WMEM_ALLOC_BIAS);
		mem_cgroup_sk_alloc(sk);
	}
	return sk;
}
```

### 3.3 `sk_prot_alloc()` - 底层分配

**行**: 2231-2265

```c
static struct sock *sk_prot_alloc(struct proto *prot, gfp_t priority, int family)
{
	struct sock *sk;
	struct kmem_cache *slab;

	slab = prot->slab;
	if (slab != NULL) {
		sk = kmem_cache_alloc(slab, priority & ~__GFP_ZERO);
		if (!sk)
			return sk;
	} else {
		sk = kmalloc(prot->obj_size, priority);
	}

	if (sk != NULL) {
		if (security_sk_alloc(sk, family, priority))
			goto out_free;
		if (!try_module_get(prot->owner))
			goto out_free_sec;
	}
	return sk;

out_free_sec:
	security_sk_free(sk);
out_free:
	if (slab != NULL)
		kmem_cache_free(slab, sk);
	else
		kfree(sk);
	return NULL;
}
```

### 3.4 Socket 释放路径

```
close(fd)
  └─> sock_close()
       └─> __sock_release()
            ├─> ops->release()
            │   └─> sk_common_release()
            │       ├─> sk->sk_prot->destroy()
            │       ├─> sk->sk_prot->unhash()
            │       ├─> sock_orphan()
            │       └─> sock_put()
            │
            ├─> sock->sk = NULL
            └─> iput(SOCK_INODE(sock))
```

### 3.5 `sk_common_release()` - 协议层释放

**行**: 3977-4010

```c
void sk_common_release(struct sock *sk)
{
	if (sk->sk_prot->destroy)
		sk->sk_prot->destroy(sk);

	sk->sk_prot->unhash(sk);

	sock_orphan(sk);

	xfrm_sk_free_policy(sk);

	sock_put(sk);
}
```

### 3.6 `sk_prot_free()` - 底层释放

**行**: 2267-2286

```c
static void sk_prot_free(struct proto *prot, struct sock *sk)
{
	struct kmem_cache *slab;
	struct module *owner;

	owner = prot->owner;
	slab = prot->slab;

	cgroup_sk_free(&sk->sk_cgrp_data);
	mem_cgroup_sk_free(sk);
	security_sk_free(sk);
	sk_owner_put(sk);

	if (slab != NULL)
		kmem_cache_free(slab, sk);
	else
		kfree(sk);
	module_put(owner);
}
```

---

## 4. 数据结构关系

```
用户进程
    │
    │ fd = socket()
    ▼
┌─────────────────────────────────────────────────────────────┐
│  struct socket (net/socket.c)                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ state, type, flags                                 │     │
│  │ *file ──────────────────────────────────────┐      │     │
│  │ *sk ────────────────────────────────────────│─►    │     │
│  │ *ops ───────────────────────────────────────│─►    │     │
│  │ wq (wait queue)                            │      │     │
│  └────────────────────────────────────────────│──────┘     │
└────────────────────────────────────────────────│────────────┘
                                                │
                   ┌───────────────────────────┘
                   ▼
┌───────────────────────────────────────────────────────────────────┐
│  struct sock (include/net/sock.h)                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ struct sock_common __sk_common (hash, port, addr, etc.)     │   │
│  │ *sk_socket ◄────────────────────────────────────────────── │   │
│  │ sk_receive_queue, sk_write_queue                           │   │
│  │ *sk_prot (tcp_prot/udp_prot/etc.)                         │   │
│  │ sk_destruct, sk_data_ready, sk_write_space, etc.          │   │
│  │ sk_refcnt (引用计数)                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 5. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| __sys_socket | net/socket.c | 1742-1757 |
| __sock_create | net/socket.c | 1534-1647 |
| sock_alloc | net/socket.c | 632-651 |
| sock_alloc_file | net/socket.c | 476-502 |
| sock_map_fd | net/socket.c | 504-521 |
| sock_release | net/socket.c | 688-692 |
| __sock_release | net/socket.c | 653-678 |
| sock_close | net/socket.c | 1453-1457 |
| struct socket | include/linux/net.h | 116-128 |
| struct sock | include/net/sock.h | 360-559 |
| inet_stream_ops | net/ipv4/af_inet.c | 1066-1098 |
| inet_dgram_ops | net/ipv4/af_inet.c | 1101-1127 |
| sock_sendmsg | net/socket.c | 753-771 |
| sock_recvmsg | net/socket.c | 1096-1102 |
| sock_init_data | net/core/sock.c | 3767-3775 |
| sk_alloc | net/core/sock.c | 2296-2337 |
| sk_prot_alloc | net/core/sock.c | 2231-2265 |
| sk_common_release | net/core/sock.c | 3977-4010 |
| sk_prot_free | net/core/sock.c | 2267-2286 |
