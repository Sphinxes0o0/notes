# Netlink 
最初从Linux 2.2 引入, 当时名为 `AF_NETLINK`, 目的是为了提供一种更灵活的用户空间进程与内核空间通信的方法.
通过使用 `socket` 打开并注册一个 `netlink socket`, 就可以与内核建立双向通信.

* RFC 359

* 实现：
  * net/netlink
    * af_netlink.c
    * af_netlink.h
    * genetlink.c
    * diag.c
  * libnl 库


内核中创建 `Netlink` 使用 `netlink_kernel_create()`, 
用户空间则是和普通的 `socket` 一致.

用户和内核创建的 `Netlink socket` 都将创建一个` netlink_sock`,
用户态使用 `netlink_create()`处理,
内核态使用 `__netlink_kernel_create()`处理.

最终都将调用 `__netlink_create()` ,通过调用 `sk_alloc()` 分配 `socket`

## sockaddr_nl

> include/uapi/linux/netlink.h

```c
struct sockaddr_nl {
    __kernel_sa_family_t    nl_family;
    unsigned short          nl_pad;
    __u32                   nl_pid;
    __u32                   nl_groups;
};
```

* nl_family： AF_NETLINK

* nl_pad: 总是为0

* nl_pid: 单播地址

对于内核总是为0, 用户空间会将其设置为 pid;

应用于其他子系统： SELinux, audit, uevent;

`rtnetlink`, 用于 路由消息, 邻接消息，链路消息。

* nl_groups: 组播组

## 内核 Netlink

### Netlink 消息报头

### NETLINK_ROUTE

## 通用 Netlink



