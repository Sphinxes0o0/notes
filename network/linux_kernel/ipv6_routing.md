# IPv6 路由子系统

## 1. 模块架构

### 1.1 功能概述

IPv6 路由子系统负责查表和转发，与 IPv4 类似但使用不同的数据结构和查找算法。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv6/route.c` | IPv6 路由实现 |
| `net/ipv6/fib6_rules.c` | IPv6 路由策略 |
| `net/ipv6/ip6_fib.c` | IPv6 FIB |

## 2. 核心数据结构

### 2.1 struct rt6_info

```c
// include/net/ip6_fib.h:180
struct rt6_info {
    struct dst_entry    dst;            // 通用目标入口
    struct rt6key       rt6i_dst;       // 目的地址
    struct rt6key       rt6i_src;       // 源地址
    struct in6_addr     rt6i_gateway;   // 网关
    struct inet6_dev   *rt6i_idev;     // 输入设备

    unsigned int        rt6i_flags;     // 标志

    struct fib6_table  *rt6i_table;    // 路由表
    struct fib6_node   *rt6i_node;     // FIB 节点

    struct rt6_info    *rt6i_next;     // 哈希链表
};
```

### 2.2 struct rt6key

```c
// include/net/ip6_fib.h:150
struct rt6key {
    struct in6_addr addr;              // 地址
    unsigned int    plen;               // 前缀长度
};
```

### 2.3 struct fib6_table

```c
// include/net/ip6_fib.h:60
struct fib6_table {
    struct hlist_node tb6_hlist;       // 哈希链表
    u32             tb6_id;           // 表 ID
    unsigned int    tb6_stamp;
    int             (*tb6_lookup)(struct fib6_table *,
                                  struct flowi6 *,
                                  struct fib6_result *,
                                  int);
    int             (*tb6_insert)(struct fib6_table *,
                                  struct fib6_result *,
                                  struct fib6_info *,
                                  gfp_t);
    void            *tb6_data;
};
```

### 2.4 struct fib6_node

```c
// include/net/ip6_fib.h:100
struct fib6_node {
    struct fib6_node   *parent;        // 父节点
    struct fib6_node   *left;          // 左子节点
    struct fib6_node   *right;         // 右子节点
    struct fib6_node   *subtree;

    struct rt6_info     *leaf;         // 叶子节点

    struct list_head    info_list;     // 路由信息列表

    __be32              key[4];         // IPv6 地址
    unsigned char       bitlen;        // 位长度
    unsigned char       flags;         // 标志
};
```

## 3. 路由查找

### 3.1 ip6_route_output()

```c
// net/ipv6/route.c:2100
struct dst_entry *ip6_route_output(struct net *net, const struct sock *sk,
                                   struct flowi6 *fl6)
{
    struct dst_entry *dst;

    // 调用 fib6_lookup
    fib6_lookup(net, &fl6->flowi6_iif, fl6, &fl6->daddr, &res);

    dst = &res.rt6->dst;
    dst = dst_output(net, sk, dst, fl6);
    return dst;
}
```

### 3.2 fib6_lookup()

```c
// net/ipv6/ip6_fib.c:400
int fib6_lookup(struct net *net, int oif, struct in6_addr *daddr,
                struct in6_addr *saddr, struct fib6_result *res)
{
    struct fib6_table *table;
    struct fib6_node *fn;

    // 获取路由表
    table = fib6_get_table(net, RT6_TABLE_MAIN);
    if (!table)
        return -ENETUNREACH;

    // 从根开始遍历
    fn = fib6_locate(table, daddr);

    // 匹配最长前缀
    while (fn) {
        if (fn->leaf)
            break;
        fn = fib6_walk_continue(fn);
    }

    // 返回结果
    *res = fib_SELECT_DEFAULT(fn);
}
```

## 4. 路由类型

```c
// include/uapi/linux/fib_rule.h
enum {
    RTN_UNSPEC,       // 未知
    RTN_UNICAST,      // 单播
    RTN_LOCAL,        // 本地地址
    RTN_BROADCAST,    // 广播
    RTN_ANYCAST,      // 任播
    RTN_MULTICAST,    // 多播
    RTN_BLACKHOLE,    // 黑洞
    RTN_UNREACHABLE,  // 不可达
    RTN_PROHIBIT,     // 禁止
    RTN_THROW,        // 继续查找
    RTN_NAT,          // NAT
};
```

## 5. 路由缓存

### 5.1 rt6_cache_alloc()

```c
// net/ipv6/route.c:800
struct rt6_info *rt6_cache_alloc(void)
{
    struct rt6_info *rt;

    rt = kmalloc(sizeof(*rt), GFP_ATOMIC);
    if (!rt)
        return NULL;

    memset(rt, 0, sizeof(*rt));
    dst_init(&rt->dst, &rt6_dst_ops, 1);

    return rt;
}
```

### 5.2 rt6_insert_route()

```c
// net/ipv6/route.c:900
int rt6_insert_route(struct fib6_table *table, struct rt6_info *rt)
{
    struct fib6_node *fn;

    // 插入到 fib6_node
    fn = fib6_locate(table, &rt->rt6i_dst.addr);

    // 添加到路由链表
    list_add_rcu(&rt->rt6i_rr链表, &fn->leaf_list);

    return 0;
}
```

## 6. 邻居发现路由

```c
// 路由器发现添加的路由
// net/ipv6/route.c:1200
void rt6_add_dflt_router(struct net_device *dev, struct in6_addr *addr)
{
    struct rt6_info *rt;

    // 创建默认路由
    rt = rt6_cache_alloc();
    rt->rt6i_flags = RTF_UP | RTF_GATEWAY;
    rt->rt6i_gateway = *addr;
    rt->rt6i_dev = dev;

    // 插入路由表
    rt6_insert_route(table, rt);
}
```

## 7. 路由表操作

### 7.1 添加路由

```c
// net/ipv6/route.c:1500
int ip6_route_add(struct fib6_config *cfg)
{
    struct rt6_info *rt;
    struct fib6_table *table;

    // 创建路由
    rt = rt6_alloc();
    if (!rt)
        return -ENOMEM;

    // 设置参数
    rt->rt6i_dst = cfg->fc_dst;
    rt->rt6i_src = cfg->fc_src;
    rt->rt6i_gateway = cfg->fc_gateway;

    // 获取表并插入
    table = fib6_get_table(cfg->fc_table);
    return fib6_add(table, fn, rt, cfg);
}
```

### 7.2 删除路由

```c
// net/ipv6/route.c:1600
int ip6_route_del(struct fib6_config *cfg)
{
    struct fib6_table *table;
    struct fib6_node *fn;

    table = fib6_get_table(cfg->fc_table);
    fn = fib6_locate(table, &cfg->fc_dst);

    if (fn)
        return fib6_del(table, fn, rt);
}
```
