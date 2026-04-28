# dst_entry - 路由缓存条目

## 1. 模块架构

### 1.1 功能概述

`dst_entry` 是内核路由子系统的核心数据结构，用于缓存路由查找结果。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/dst.c` | dst_entry 实现 |
| `include/net/dst.h` | dst_entry 定义 |
| `include/net/route.h` | IPv4 路由 |
| `include/net/ip6_fib.h` | IPv6 路由 |

## 2. 核心数据结构

### 2.1 struct dst_entry

```c
// include/net/dst.h:64
struct dst_entry {
    struct rcu_head     rcu;
    struct dst_entry    *child;         // 子路由
    struct dst_entry    *next;          // 哈希链表

    unsigned long       expires;        // 过期时间
    unsigned short      flags;          // 标志
    unsigned short      obsolete;       // 废弃标志
    int                 error;          // 错误码

    struct net_device   *dev;          // 输出设备
    struct dst_ops      *ops;           // 操作函数

    // 输入/输出回调
    int (*input)(struct sk_buff *);
    int (*output)(struct sk_buff *);

    // 邻居
    struct neighbour    *neighbour;

    // 统计
    unsigned long       lastuse;
    unsigned long       rate_tokens;
    int                 rate;
    struct list_head    dst_list;       // dst 链表
};
```

### 2.2 struct dst_ops

```c
// include/net/dst.h:120
struct dst_ops {
    unsigned short family;              // 地址族
    unsigned int kmem_cachep;
    unsigned int flags;

    // 销毁
    void (*destroy)(struct dst_entry *);

    // 绑定
    void (*ifdown)(struct dst_entry *, struct net_device *dev, int how);

    // 发送
    struct dst_entry *(*link_failure)(struct sk_buff *);

    // 重新评估
    int (*local_out)(struct net *net, struct sock *sk, struct sk_buff *skb);

    // Neighbor
    struct neighbour* (*neigh_lookup)(const struct dst_entry *dst,
                                      struct flowi *fl,
                                      __be32 saddr);

    // 克隆
    struct dst_entry* (*clone)(struct dst_entry *dst);

    struct module       *owner;
};
```

## 3. IPv4 dst_entry

### 3.1 struct rtable

```c
// include/net/route.h:70
struct rtable {
    struct dst_entry    dst;            // 必须是第一个
    int                 rt_genid;       // 路由代际
    unsigned int        rt_flags;       // 路由标志
    __u16               rt_type;        // 路由类型
    __be32              rt_dst;         // 目的地址
    __be32              rt_src;        // 源地址
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

### 3.2 IPv4 dst_ops

```c
// net/ipv4/route.c:600
static struct dst_ops ipv4_dst_ops = {
    .family = AF_INET,
    .kmem_cachep = &rtable_cache,
    .flags = DST_HOST,
    .destroy = ip_rt_dst_destroy,
    .ifdown = ip_rt_ifdown,
    .link_failure = ip_rt_link_failure,
    .local_out = ip_local_out,
    .neigh_lookup = ip_neigh_gw_output,
    .clone = ip_rt_clone,
    .owner = THIS_MODULE,
};
```

## 4. IPv6 dst_entry

### 4.1 struct rt6_info

```c
// include/net/ip6_fib.h:180
struct rt6_info {
    struct dst_entry    dst;            // 必须是第一个
    struct rt6key       rt6i_dst;      // 目的地址
    struct rt6key       rt6i_src;       // 源地址
    struct in6_addr     rt6i_gateway;   // 网关
    struct inet6_dev   *rt6i_idev;     // 输入设备

    unsigned int        rt6i_flags;     // 标志

    struct fib6_table  *rt6i_table;    // 路由表
    struct fib6_node   *rt6i_node;     // FIB 节点
    struct rt6_info    *rt6i_next;     // 哈希链表
};
```

### 4.2 rt6_dst_ops

```c
// net/ipv6/route.c:400
static struct dst_ops rt6_dst_ops = {
    .family = AF_INET6,
    .kmem_cachep = &rt6_info_cache,
    .flags = DST_HOST | DST_IP6,
    .destroy = ip6_dst_destroy,
    .ifdown = ip6_dst_ifdown,
    .link_failure = ip6_link_failure,
    .local_out = ip6_local_out,
    .neigh_lookup = ip6_neigh_lookup,
    .clone = ip6_rt_clone,
    .owner = THIS_MODULE,
};
```

## 5. 缓存管理

### 5.1 dst_cache

```c
// include/net/dst.h:200
struct dst_cache {
    struct dst_cache_pcpu {
        struct dst_entry *dst;
        unsigned long lastuse;
    } __percpu *pcpu;
};
```

### 5.2 dst_cache_get()

```c
// net/core/dst.c:200
struct dst_entry *dst_cache_get(struct dst_cache *dst_cache)
{
    struct dst_cache_pcpu *cpu;
    struct dst_entry *dst;

    cpu = get_cpu_var(dst_cache->pcpu);
    dst = rcu_dereference(cpu->dst);

    if (dst && !dst->obsolete &&
        time_before(jiffies, dst->lastuse + DST_CACHE_TIMEOUT))
        return dst;

    return NULL;
}
```

### 5.3 dst_cache_set()

```c
// net/core/dst.c:250
void dst_cache_set(struct dst_cache *dst_cache, struct dst_entry *dst)
{
    struct dst_cache_pcpu *cpu;

    cpu = this_cpu_ptr(dst_cache->pcpu);
    rcu_assign_pointer(cpu->dst, dst);
    cpu->lastuse = jiffies;
}
```

## 6. 垃圾回收

### 6.1 dst_gc()

```c
// net/core/dst.c:300
static void dst_gc(void)
{
    struct dst_entry *dst, *next;
    unsigned long now = jiffies;

    spin_lock_bh(&dst_default_lock);

    // 遍历 dst_list
    list_for_each_entry_safe(dst, next, &dst_list, dst_list) {
        // 检查过期
        if (dst->expires && time_after_eq(now, dst->expires)) {
            // 释放
            dst_release(dst);
        }
    }

    spin_unlock_bh(&dst_default_lock);
}
```

### 6.2 触发条件

```c
// 触发 GC 的条件:
// 1. 路由缓存条目超过阈值
// 2. 定时器周期性检查
// 3. 内存压力时
```

## 7. 使用流程

### 7.1 查找

```c
// dst = ip_route_output(dev_net(dev), daddr, saddr, tos, mark);
// dst_output() 调用 dst->output()
```

### 7.2 释放

```c
// 使用后必须释放
dst_release(dst);

// 如果 refcnt 为 0，会调用 ops->destroy()
```

## 8. DST 标志

```c
// include/net/dst.h:30
#define DST_HOST         0x0001   // 主机路由
#define DST_NOPOLICY     0x0004   // 不进行策略路由
#define DST_NOXFRM       0x0008   // 不进行 ipsec 转换
#define DST_NOCACHE      0x0010   // 不缓存
#define DST_FAKE_RTABLE  0x0020   // 假路由表
```
