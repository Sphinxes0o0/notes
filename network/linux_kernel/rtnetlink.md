# rtnetlink - 路由 Netlink 接口

## 1. 模块架构

### 1.1 功能概述

rtnetlink 是用户空间配置网络路由、邻居、地址等资源的内核接口。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/rtnetlink.c` | rtnetlink 实现 |
| `net/ipv4/fib_frontend.c` | IPv4 路由 rtnetlink |
| `net/ipv6/fib6_rules.c` | IPv6 路由 rtnetlink |
| `include/linux/rtnetlink.h` | rtnetlink 定义 |

## 2. 消息类型

### 2.1 消息格式

```c
// include/linux/rtnetlink.h:50
struct nlmsghdr {
    __u32 nlmsg_len;    // 消息长度
    __u16 nlmsg_type;   // 消息类型
    __u16 nlmsg_flags;  // 标志
    __u32 nlmsg_seq;    // 序列号
    __u32 nlmsg_pid;    // PID
};
```

### 2.2 消息类型

```c
// include/linux/rtnetlink.h:100
enum {
    RTM_NEWLINK,     // 创建/更新链路
    RTM_DELLINK,     // 删除链路
    RTM_GETLINK,     // 获取链路信息
    RTM_NEWADDR,     // 添加地址
    RTM_DELADDR,     // 删除地址
    RTM_NEWROUTE,    // 添加路由
    RTM_DELROUTE,    // 删除路由
    RTM_GETROUTE,    // 获取路由
    RTM_NEWNEIGH,    // 添加邻居
    RTM_DELNEIGH,    // 删除邻居
    RTM_GETNEIGH,    // 获取邻居
    RTM_NEWRULE,     // 添加规则
    RTM_DELRULE,     // 删除规则
    RTM_GETRULE,    // 获取规则
};
```

## 3. 链路操作

### 3.1 创建链路

```c
// net/core/rtnetlink.c:500
static int rtnl_newlink(struct sk_buff *skb, struct nlmsghdr *nlh)
{
    struct ifinfomsg *ifm;
    struct nlattr *tb[IFLA_MAX+1];
    struct net_device *dev;

    // 解析属性
    nlmsg_parse(nlh, sizeof(*ifm), tb, IFLA_MAX, ifla_policy);

    // 分配设备
    dev = alloc_netdev(sizeof(struct rtnl_link_ops), ...);

    // 设置属性
    if (tb[IFLA_ADDRESS])
        memcpy(dev->dev_addr, nla_data(tb[IFLA_ADDRESS]), ...);

    // 注册设备
    register_netdevice(dev);

    // 发送响应
    rtnl_notify(dev);
}
```

### 3.2 删除链路

```c
// net/core/rtnetlink.c:600
static int rtnl_dellink(struct sk_buff *skb, struct nlmsghdr *nlh)
{
    struct ifinfomsg *ifm;
    struct net_device *dev;

    // 查找设备
    dev = __dev_get_by_index(genl_info_ifindex(info));
    if (!dev)
        return -ENODEV;

    // 注销设备
    unregister_netdevice(dev);
}
```

## 4. 地址操作

### 4.1 RTM_NEWADDR

```c
// net/core/rtnetlink.c:1000
static int rtnl_newaddr(struct sk_buff *skb, struct nlmsghdr *nlh)
{
    struct ifaddrmsg *ifa;
    struct nlattr *tb[IFA_MAX+1];
    struct net_device *dev;

    // 解析消息
    nlmsg_parse(nlh, sizeof(*ifa), tb, IFA_MAX, ifa_policy);

    // 获取设备
    dev = __dev_get_by_index(ifa->ifa_index);
    if (!dev)
        return -ENODEV;

    // 添加地址
    if (ifa->ifa_family == AF_INET)
        inet_rtm_newaddr(net, dev, tb);
    else if (ifa->ifa_family == AF_INET6)
        inet6_rtm_newaddr(net, dev, tb);
}
```

## 5. 路由操作

### 5.1 RTM_NEWROUTE

```c
// net/ipv4/fib_frontend.c:500
int inet_rtm_newroute(struct net *net, struct sk_buff *skb,
                      struct nlmsghdr *nlh)
{
    struct rtmsg *rtm;
    struct nlattr *tb[RTA_MAX+1];
    struct fib_config cfg = {};

    // 解析
    nlmsg_parse(nlh, sizeof(*rtm), tb, RTA_MAX, rtm_policy);

    cfg.fc_family = rtm->rtm_family;
    cfg.fc_dst_len = rtm->rtm_dst_len;
    cfg.fc_src_len = rtm->rtm_src_len;

    // 设置属性
    if (tb[RTA_GATEWAY])
        cfg.fc_gw = nla_get_be32(tb[RTA_GATEWAY]);

    // 添加路由
    return fib_new_rtable(net, &cfg);
}
```

### 5.2 RTM_GETROUTE

```c
// net/ipv4/fib_frontend.c:600
int inet_rtm_getroute(struct sk_buff *in_skb, struct nlmsghdr *nlh)
{
    struct rtmsg *rtm;
    struct fib_result res;

    // 查找路由
    fib_lookup(net, &fl4, &res);

    // 构建响应
    rtnl_fill_info(res, skb, NETLINK_CB(in_skb).portid,
                   nlh->nlmsg_seq, RTM_NEWROUTE);
}
```

## 6. 邻居操作

### 6.1 RTM_NEWNEIGH

```c
// net/core/rtnetlink.c:2000
static int rtnl_newneigh(struct sk_buff *skb, struct nlmsghdr *nlh)
{
    struct ndmsg *ndm;
    struct nlattr *tb[NDA_MAX+1];
    struct neighbour *neigh;

    // 解析
    nlmsg_parse(nlh, sizeof(*ndm), tb, NDA_MAX, nd_policy);

    // 创建或更新邻居
    neigh = __neigh_lookup(ndm->ndm_family, pkey, dev, 1);

    // 更新状态
    if (ndm->ndm_state)
        neigh->nud_state = ndm->ndm_state;

    // 更新硬件地址
    if (tb[NDA_LLADDR])
        neigh_update(neigh, nla_data(tb[NDA_LLADDR]));
}
```

## 7. iproute2 使用

### 7.1 ip link

```bash
# 显示接口
ip link show

# 设置地址
ip link set eth0 address 00:11:22:33:44:55

# 启用/禁用
ip link set eth0 up/down
```

### 7.2 ip addr

```bash
# 显示地址
ip addr show

# 添加地址
ip addr add 192.168.1.1/24 dev eth0

# 删除地址
ip addr del 192.168.1.1/24 dev eth0
```

### 7.3 ip route

```bash
# 显示路由
ip route show

# 添加路由
ip route add 10.0.0.0/8 via 192.168.1.1 dev eth0

# 删除路由
ip route del 10.0.0.0/8
```

### 7.4 ip neigh

```bash
# 显示邻居
ip neigh show

# 添加邻居
ip neigh add 192.168.1.2 lladdr 00:11:22:33:44:55 dev eth0

# 删除邻居
ip neigh del 192.168.1.2 dev eth0
```
