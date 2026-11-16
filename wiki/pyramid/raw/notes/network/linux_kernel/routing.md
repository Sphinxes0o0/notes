# dst_entry 和路由缓存

## 1. 模块架构

### 1.1 功能概述

`dst_entry` 是 Linux 内核路由子系统的核心数据结构，用于缓存路由决策和相关的per-packet信息。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/dst.c` | dst_entry 实现 |
| `include/net/dst.h` | dst_entry 定义 |
| `net/ipv4/route.c` | IPv4 路由缓存 |
| `net/ipv6/route.c` | IPv6 路由缓存 |

## 2. 核心数据结构

### 2.1 struct dst_entry

```c
// include/net/dst.h:122
struct dst_entry {
    struct net_device       *dev;              // 输出设备
    struct dst_ops         *ops;              // 操作函数

    unsigned long          _metrics;          // 指标 (RTAX_*)
    unsigned long          expires;            // 过期时间

    // 输入/输出处理
    int (*input)(struct sk_buff *);
    int (*output)(struct net *, struct sock *, struct sk_buff *);

    unsigned short         flags;              // DST_*
    short                  obsolete;            // 废弃标志
    int                    __use;             // 使用计数
    unsigned long          lastuse;          // 最后使用时间
    union {
        struct dst_entry   *next;
        struct rcu_head     rcu_head;
    };
    short                  error;             // 错误码
    __u32                 tclassid;          // 流量类 ID

    // 用于 IPv4/IPv6 共用
#ifdef CONFIG_NET_CLS_ROUTE
    u32                    tclassid;
#endif
};
```

### 2.2 struct dst_ops

```c
// include/net/dst.h:62
struct dst_ops {
    unsigned short           family;              // AF_INET/AF_INET6
    unsigned int             gc_thresh;          // GC 阈值

    // 分配/释放
    struct dst_entry *(*check)(struct dst_entry *, __u32 cookie);
    void               (*destroy)(struct dst_entry *);
    void               (*destroy_rcu)(struct rcu_head *head);

    // MTU
    int                 (*mtu)(struct dst_entry *);
    int                 (*default_advmss)(const struct dst_entry *);

    // 指标
    struct dst_ops     *cow_metrics;
    struct dst_metrics *(*alloc_metrics)(struct dst_entry *);

    // 确认
    void               (*confirm_neigh)(struct dst_entry *, struct neighbour *);
    unsigned int       (*redirect)(struct dst_entry *, struct sock *sk,
                                   struct sk_buff *skb);

    // 更新 PMTU
    void               (*update_pmtu)(struct dst_entry *, struct sock *sk,
                                     struct sk_buff *skb, u32 mtu);
    void               (*redirect)(struct dst_entry *, struct sock *sk,
                                  struct sk_buff *skb);

    // 本地输出
    int                 (*local_out)(struct net *, struct sock *,
                                    struct sk_buff *skb);
};
```

## 3. IPv4 路由缓存

### 3.1 struct rtable

```c
// include/net/route.h:89
struct rtable {
    struct dst_entry       dst;               // 基类 (必须第一)

    int                    rt_genid;           // 生成 ID
    unsigned int           rt_flags;          // RTCF_* 标志
    __u16                  rt_type;            // RTN_* 路由类型
    __u8                   rt_is_input;        // 输入路由
    __u8                   rt_uses_gateway;   // 使用网关

    int                    rt_iif;            // 输入接口
    u8                     rt_gw_family;       // 网关地址族
    union {
        __be32             rt_gw4;           // IPv4 网关
        struct in6_addr    rt_gw6;         // IPv6 网关
    };

    u32                    rt_pmtu:31;        // PMTU
    u32                    rt_mtu_locked:1;   // MTU 锁定

    // 哈希链表
    struct rhash_head       rt_hash_node;
};
```

### 3.2 路由标志

```c
// include/uapi/linux/route.h
#define RTF_UP              0x0001  // 路由可用
#define RTF_GATEWAY         0x0002  // 使用网关
#define RTF_HOST            0x0004  // 主机路由
#define RTF_REINSTATE       0x0008  // 恢复
#define RTF_DYNAMIC         0x0010  // 动态创建
#define RTF_MODIFIED        0x0020  // 修改
#define RTF_MTU            0x0040  // MTU 设置
#define RTF_WINDOW         0x0080  // 窗口
#define RTF_IRTT           0x0100  // 初始 RTT
#define RTF_REJECT         0x0200  // 拒绝
#define RTF_DEFAULT        0x0400  // 默认路由
```

## 4. 路由查找

### 4.1 ip_route_output()

```c
// net/ipv4/route.c:2691
struct rtable *ip_route_output_key_hash(struct net *net, struct flowi4 *fl4,
                                       const struct sk_buff *skb)
{
    struct fib_result res = { .type = RTN_UNSPEC, .fi = NULL };
    struct rtable *rth;

    fl4->flowi4_iif = LOOPBACK_IFINDEX;  // 输出路由使用 loopback

    rcu_read_lock();
    rth = ip_route_output_key_hash_rcu(net, fl4, &res, skb);
    rcu_read_unlock();

    return rth;
}
```

### 4.2 ip_route_output_key_hash_rcu()

```c
// net/ipv4/route.c:2712
static struct rtable *ip_route_output_key_hash_rcu(struct net *net,
                                                   struct flowi4 *fl4,
                                                   struct fib_result *res,
                                                   const struct sk_buff *skb)
{
    // 1. 验证源地址
    if (fl4->saddr) {
        if (ipv4_is_multicast(fl4->saddr) || fl4->saddr == htonl(INADDR_BROADCAST))
            return NULL;
    }

    // 2. 查找输出设备
    if (fl4->flowi4_oif) {
        dev = dev_get_by_index(net, fl4->flowi4_oif);
        if (!dev) return NULL;
    }

    // 3. FIB 查找
    err = fib_lookup(net, fl4, res, 0);
    if (err) {
        // 无路由，使用默认
    }

    // 4. 创建路由缓存
    return __mkroute_output(res, fl4, dev, flags);
}
```

## 5. 路由缓存操作

### 5.1 创建缓存路由

```c
// net/ipv4/route.c:2562
static struct rtable *__mkroute_output(struct fib_result *res,
                                       struct flowi4 *fl4,
                                       struct net_device *dev,
                                       unsigned int flags)
{
    struct rtable *rth;

    // 分配路由
    rth = rt_dst_alloc(dev);
    if (!rth) return NULL;

    // 设置标志
    rth->rt_flags = flags;
    rth->rt_type = res->type;

    // 设置网关
    if (flags & RTF_GATEWAY) {
        rth->rt_gw_family = AF_INET;
        rth->rt_gw4 = res->fi->fib_nh->nh_gw;
    }

    // 设置输出设备
    rth->dst.dev = dev;
    dst_hold(&rth->dst);

    // 设置输入/输出处理
    rth->dst.input = ip_local_deliver;
    rth->dst.output = ip_output;

    return rth;
}
```

### 5.2 路由缓存查找

```c
// net/ipv4/route.c:2276
struct rtable *__rt_candle(struct net *net, u32 id, int oif,
                           __be32 saddr, __be32 daddr, int iif)
{
    // 计算哈希
    u32 h = rt_hash(daddr, saddr, oif, iif, rt_genid);

    // 在哈希链表中查找
    rcu_read_lock();
    hlist_for_each_entry_rcu(rth, &rt_hash_table[h], rt_hash_node) {
        if (rth->rt_genid == rt_genid &&
            rth->rt_route_iif == iif &&
            rth->rt_oif == oif &&
            rth->rt_gateway == daddr &&
            rth->rt_gateway_src == saddr) {
            dst_hold(&rth->dst);
            rcu_read_unlock();
            return rth;
        }
    }
    rcu_read_unlock();
    return NULL;
}
```

## 6. 路由缓存 GC

### 6.1 GC 触发条件

```c
// net/ipv4/route.c:2280
static int rt_cache_inited;
static unsigned int rt_hash_mask;

// GC 触发
if (rt_entries > rt_hash_mask * 2)
    garbage_collect();
```

### 6.2 garbage_collect()

```c
// net/ipv4/route.c:2235
static int garbage_collect(void)
{
    struct rtable *rth, *next;
    unsigned int i;

    // 遍历所有哈希桶
    for (i = 0; i <= rt_hash_mask; i++) {
        spin_lock_bh(&rt_hash_table[i].lock);
        hlist_for_each_entry_safe(rth, next, rt_hash_table[i].next, rt_hash_node) {
            // 跳过正在使用的
            if (rth->dst.__use > 0) continue;

            // 过期检查
            if (!rth->dst.expires || time_after_eq(jiffies, rth->dst.expires)) {
                hlist_del_rcu(&rth->rt_hash_node);
                rt_free(rth);
            }
        }
        spin_unlock_bh(&rt_hash_table[i].lock);
    }

    return 0;
}
```

## 7. FIB 查找

### 7.1 fib_lookup()

```c
// net/ipv4/fib_lookup.h
int fib_lookup(struct net *net, const struct flowi4 *flp,
               struct fib_result *res, unsigned int flags)
{
    // 1. 获取 FIB 表
    struct fib_table *tb = fib_get_table(net, RT_TABLE_MAIN);

    // 2. 在表中查找
    return tb->tb_lookup(tb, flp, res, flags);
}
```

### 7.2 fib_result

```c
// include/net/ip_fib.h:237
struct fib_result {
    __be32              prefix;           // 匹配的前缀
    unsigned char       prefixlen;        // 前缀长度
    unsigned char       nh_sel;           // 选择的下一跳
    unsigned char       type;             // 路由类型
    unsigned char       scope;            // 路由范围
    u32                 tclassid;         // 流量类
    struct fib_info    *fi;              // FIB 信息
    struct fib_table   *table;           // 所属表
    struct hlist_head  *fa_head;        // FIB 别名链表
};
```

## 8. 路由缓存与 FIB

### 8.1 交互流程

```
应用 send()
    ↓
ip_route_output()
    ↓
FIB 查找 (fib_lookup)
    ↓
创建 dst_entry (dst_alloc)
    ↓
缓存到 rtable (rt_hash_table)
```

返回给协议栈

### 8.2 PMTU 发现

```c
// net/ipv4/route.c:1802
void ip_rt_update_pmtu(struct dst_entry *dst, struct sock *sk,
                        struct sk_buff *skb, u32 mtu)
{
    struct rtable *rt = (struct rtable *)dst;

    if (mtu < rt->rt_pmtu) {
        rt->rt_pmtu = mtu;
        rt->dst.expires = jiffies + ip_rt_mtu_expires;
    }
}
```

## 9. IPv6 dst_entry

### 9.1 struct rt6_info

```c
// include/net/ip6_route.h:78
struct rt6_info {
    struct dst_entry       dst;               // 基类

    struct fib6_info      *from;             // 指向 FIB 条目
    int                   sernum;            // 缓存序列号

    struct rt6key         rt6i_dst;          // 目的地址
    struct rt6key         rt6i_src;          // 源地址
    struct in6_addr       rt6i_gateway;     // 网关
    struct inet6_dev     *rt6i_idev;        // 输入设备

    u32                   rt6i_flags;       // 路由标志
};
```

### 9.2 rt6_info 与 rt2_info

```
rt6_info 继承自 dst_entry，添加了 IPv6 特定的字段：
- from: 指向 fib6_info 的指针
- rt6i_dst/src: IPv6 地址前缀
- rt6i_gateway: 下一跳网关
```
