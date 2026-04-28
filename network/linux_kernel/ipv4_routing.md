# IPv4 路由子系统

## 1. 模块架构

### 1.1 功能概述

IPv4 路由子系统负责查找路由表、确定报文的下一跳，是 IP 层转发的核心。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv4/route.c` | IPv4 路由实现 |
| `include/net/route.h` | 路由定义 |
| `net/ipv4/fib_frontend.c` | FIB 前端 |

## 2. 核心数据结构

### 2.1 struct rtable

```c
// include/net/route.h:70
struct rtable {
    struct dst_entry    dst;            // 通用目标入口
    int                 rt_genid;       // 路由代际
    unsigned int        rt_flags;       // 路由标志
    __u16               rt_type;        // 路由类型
    __be32              rt_dst;         // 目的地址
    __be32              rt_src;         // 源地址
    __be32              rt_gateway;     // 网关

    struct rt_key {
        __be32           src;
        __be32           dst;
        unsigned int     iif;
        __u8             tos;
        __u8             scope;
    } rt_key;
};
```

### 2.2 路由标志

```c
// include/uapi/linux/route.h
#define RTF_UP           0x0001    // 路由可用
#define RTF_GATEWAY      0x0002    // 使用网关
#define RTF_HOST         0x0004    // 主机路由
#define RTF_REINSTATE    0x0008    // 恢复路由
#define RTF_DYNAMIC      0x0010    // 动态添加
#define RTF_MODIFIED     0x0020    // 被修改
#define RTF_MTU          0x0040    // MTU 限制
#define RTF_WINDOW       0x0080    // 窗口限制
#define RTF_CACHE        0x0100    // 缓存路由
```

## 3. 路由查找

### 3.1 ip_route_output()

```c
// net/ipv4/route.c:1980
int ip_route_output(struct net *net, struct rtable **rp,
                   __be32 daddr, __be32 saddr,
                   __u8 tos, __u32 mark)
{
    struct flowi4 fl4 = {
        .daddr = daddr,
        .saddr = saddr,
        .flowi4_tos = tos,
        .flowi4_mark = mark,
    };

    return ip_route_output_key(net, rp, &fl4);
}

int ip_route_output_key(struct net *net, struct rtable **rp,
                        struct flowi4 *fl4)
{
    // 调用 FIB 查找
    return fib_lookup(net, fl4, &fl4->flowi);
}
```

### 3.2 ip_route_output_slow()

```c
// net/ipv4/route.c:1850
static int ip_route_output_slow(struct net *net, struct rtable **rp,
                                __be32 daddr, __be32 saddr,
                                __u8 tos, __u32 mark)
{
    // 1. 本地地址处理
    if (ipv4_is_zeronet(saddr)) {
        saddr = 0;
        if (daddr == 0)
            daddr = htonl(0x7F000001);
    }

    // 2. 调用 fib_lookup
    err = fib_lookup(net, &fl4, &res);

    if (err == 0)
        *rp = &res.rth;
    return err;
}
```

## 4. 路由缓存

### 4.1 dst_entry

```c
// include/net/dst.h:64
struct dst_entry {
    struct rcu_head     rcu;
    struct net_device   *dev;          // 输出设备
    struct dst_ops      *ops;           // 操作函数

    unsigned long       expires;        // 过期时间

    struct dst_entry    *child;         // 子路由
    struct dst_entry    *next;          // 哈希链表

    unsigned int        flags;
    short               error;          // 错误码
    short               obsolete;       // 废弃标志

    int                 (*input)(struct sk_buff *);
    int                 (*output)(struct sk_buff *);
};
```

### 4.2 缓存查找

```c
// net/ipv4/route.c:2100
struct rtable *ip_route_output_flow(struct net *net, __be32 daddr,
                                    __be32 saddr, __u8 tos, __u32 mark)
{
    struct rtable *rt;

    // 先查缓存
    rt = rt_cache_get(net, daddr, saddr, tos, mark);
    if (rt)
        return rt;

    // 查路由表
    ip_route_output(net, &rt, daddr, saddr, tos, mark);

    // 加入缓存
    rt_cache_add(rt);
    return rt;
}
```

## 5. 路由查找流程

```
ip_route_output()
    |
    +-> fib_lookup()      // 查 FIB 表
    |       |
    |       +-> fib_table_lookup()
    |
    +-> rt_cache_add()    // 加入路由缓存
```

## 6. 路由类型

```c
// include/uapi/linux/route.h
enum {
    RTN_UNSPEC,       // 未知
    RTN_UNICAST,      // 单播路由
    RTN_LOCAL,        // 本地地址
    RTN_BROADCAST,    // 广播
    RTN_ANYCAST,      // 任播
    RTN_MULTICAST,    // 多播
    RTN_BLACKHOLE,    // 黑洞路由
    RTN_UNREACHABLE,  // 不可达
    RTN_PROHIBIT,     // 禁止
    RTN_THROW,        // 继续查找
    RTN_NAT,          // NAT
    RTN_XRESOLVE,     // 外部解析
};
```
