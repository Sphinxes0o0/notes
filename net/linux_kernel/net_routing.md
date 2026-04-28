# Linux 内核 IPv4 路由子系统分析

## 目录

1. [概述](#概述)
2. [核心数据结构](#核心数据结构)
   - [struct fib_result](#struct-fib_result)
   - [struct fib_info](#struct-fib_info)
   - [struct rtable](#struct-rtable)
   - [struct fib_table](#struct-fib_table)
3. [FIB 查找 (fib_lookup)](#fib-查找-fib_lookup)
4. [路由表查找 (fib_table_lookup)](#路由表查找-fib_table_lookup)
5. [输出路由 (ip_route_output)](#输出路由-ip_route_output)
6. [输入路由 (ip_route_input)](#输入路由-ip_route_input)
7. [源地址验证 (fib_validate_source)](#源地址验证-fib_validate_source)
8. [路由规则 (fib_rules)](#路由规则-fib_rules)
9. [路由缓存机制](#路由缓存机制)
10. [FIB Trie 数据结构](#fib-trie-数据结构)

---

## 概述

Linux 内核 IPv4 路由子系统负责数据包的路径决策。核心组件包括：

- **FIB (Forwarding Information Base)**: 转发信息库，存储路由信息
- **路由表**: 存储路由条目的数据结构
- **路由规则**: 用于决定使用哪个路由表的规则
- **dst_entry**: 通用目标条目结构，用于路由缓存

---

## 核心数据结构

### struct fib_result

**文件**: `/Users/sphinx/github/linux/include/net/ip_fib.h` (第 173-185 行)

```c
struct fib_result {
    __be32          prefix;          // 前缀
    unsigned char   prefixlen;       // 前缀长度
    unsigned char   nh_sel;          // 下一跳选择器
    unsigned char   type;            // 路由类型 (RTN_UNICAST, RTN_LOCAL 等)
    unsigned char   scope;            // 路由作用域
    u32             tclassid;         // 流量类别 ID
    dscp_t          dscp;             // DSCP 值
    struct fib_nh_common *nhc;       // 下一跳信息
    struct fib_info *fi;              // 路由信息
    struct fib_table *table;          // 所属路由表
    struct hlist_head *fa_head;      // fib_alias 链表头
};
```

### struct fib_info

**文件**: `/Users/sphinx/github/linux/include/net/ip_fib.h` (第 136-163 行)

```c
struct fib_info {
    struct hlist_node   fib_hash;      // FIB 信息哈希链表
    struct hlist_node   fib_lhash;     // 局部哈希链表
    struct list_head    nh_list;        // 下一跳列表
    struct net          *fib_net;       // 所属网络命名空间
    refcount_t          fib_treeref;    // 树引用计数
    refcount_t          fib_clntref;    // 清理引用计数
    unsigned int        fib_flags;      // 路由标志
    unsigned char       fib_dead;       // 是否已删除
    unsigned char       fib_protocol;   // 路由协议
    unsigned char       fib_scope;      // 路由作用域
    unsigned char       fib_type;       // 路由类型
    __be32              fib_prefsrc;    // 首选源地址
    u32                 fib_tb_id;      // 路由表 ID
    u32                 fib_priority;   // 路由优先级
    struct dst_metrics  *fib_metrics;  // 路由度量
    int                 fib_nhs;        // 下一跳数量
    bool                fib_nh_is_v6;   // 是否为 IPv6 下一跳
    bool                nh_updated;      // 下一跳是否已更新
    bool                pfsrc_removed;   // 优先源是否已移除
    struct nexthop      *nh;            // 下一跳对象
    struct rcu_head     rcu;
    struct fib_nh       fib_nh[] __counted_by(fib_nhs);  // 下一跳数组
};
```

### struct rtable

**文件**: `/Users/sphinx/github/linux/include/net/route.h` (第 57-78 行)

```c
struct rtable {
    struct dst_entry    dst;           // 通用目标条目 (必须是第一个成员)

    int                 rt_genid;      // 路由生成 ID
    unsigned int        rt_flags;      // 路由标志 (RTCF_LOCAL, RTCF_BROADCAST 等)
    __u16               rt_type;       // 路由类型
    __u8                rt_is_input;   // 是否为输入路由
    __u8                rt_uses_gateway; // 是否使用网关

    int                 rt_iif;        // 输入接口索引

    u8                  rt_gw_family;  // 网关地址族
    union {
        __be32          rt_gw4;        // IPv4 网关
        struct in6_addr rt_gw6;       // IPv6 网关
    };

    u32                 rt_mtu_locked:1,  // MTU 锁定
                        rt_pmtu:31;      // 路径 MTU
};
```

### struct fib_table

**文件**: `/Users/sphinx/github/linux/include/net/ip_fib.h` (第 257-264 行)

```c
struct fib_table {
    struct hlist_node   tb_hlist;     // 路由表哈希链表
    u32                 tb_id;        // 路由表 ID (RT_TABLE_LOCAL, RT_TABLE_MAIN 等)
    int                 tb_num_default; // 默认路由数量
    struct rcu_head     rcu;
    unsigned long       *tb_data;     // 表数据指针
    unsigned long       __data[];     // 可变长度数据
};
```

---

## FIB 查找 (fib_lookup)

### fib_lookup 函数

**文件**: `/Users/sphinx/github/linux/include/net/ip_fib.h` (第 371-406 行)

当启用 `CONFIG_IP_MULTIPLE_TABLES` 时:

```c
int __fib_lookup(struct net *net, struct flowi4 *flp,
         struct fib_result *res, unsigned int flags)
{
    struct fib_lookup_arg arg = {
        .result = res,
        .flags = flags,
    };
    int err;

    // 更新流信息，如果 oif 或 iif 属于 l3mdev 设备
    l3mdev_update_flow(net, flowi4_to_flowi(flp));

    err = fib_rules_lookup(net->ipv4.rules_ops, flowi4_to_flowi(flp), 0, &arg);
    
    // 设置流量类别 ID
    if (arg.rule)
        res->tclassid = ((struct fib4_rule *)arg.rule)->tclassid;
    else
        res->tclassid = 0;

    if (err == -ESRCH)
        err = -ENETUNREACH;

    return err;
}
```

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_rules.c` (第 84-109 行)

### fib_lookup 简化版本

当未启用 `CONFIG_IP_MULTIPLE_TABLES` 时:

```c
// 文件: include/net/ip_fib.h (第 316-334 行)

static inline int fib_lookup(struct net *net, const struct flowi4 *flp,
                 struct fib_result *res, unsigned int flags)
{
    struct fib_table *tb;
    int err = -ENETUNREACH;

    rcu_read_lock();

    tb = fib_get_table(net, RT_TABLE_MAIN);
    if (tb)
        err = fib_table_lookup(tb, flp, res, flags | FIB_LOOKUP_NOREF);

    if (err == -EAGAIN)
        err = -ENETUNREACH;

    rcu_read_unlock();

    return err;
}
```

---

## 路由表查找 (fib_table_lookup)

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_trie.c` (第 1420-1624 行)

核心查找算法 - 使用 Trie 结构进行最长前缀匹配:

```c
int fib_table_lookup(struct fib_table *tb, const struct flowi4 *flp,
             struct fib_result *res, int fib_flags)
{
    struct trie *t = (struct trie *) tb->tb_data;
    const t_key key = ntohl(flp->daddr);    // 目标地址作为键
    struct key_vector *n, *pn;
    struct fib_alias *fa;
    unsigned long index;
    t_key cindex;

    pn = t->kv;
    cindex = 0;

    n = get_child_rcu(pn, cindex);
    if (!n) {
        trace_fib_table_lookup(tb->tb_id, flp, NULL, -EAGAIN);
        return -EAGAIN;
    }

    /* 步骤 1: 在 Trie 中找到最长前缀匹配 */
    for (;;) {
        index = get_cindex(key, n);

        if (index >= (1ul << n->bits))
            break;

        if (IS_LEAF(n))
            goto found;

        if (n->slen > n->pos) {
            pn = n;
            cindex = index;
        }

        n = get_child_rcu(n, index);
        if (unlikely(!n))
            goto backtrace;
    }

    /* 步骤 2: 回溯找到最长前缀 */
    for (;;) {
        // ... 回溯逻辑 ...

        if (unlikely(prefix_mismatch(key, n)) || (n->slen == n->pos))
            goto backtrace;

        if (unlikely(IS_LEAF(n)))
            break;

        while ((n = rcu_dereference(*cptr)) == NULL) {
backtrace:
            // ... 父节点回溯逻辑 ...
        }
    }

found:
    index = key ^ n->key;

    /* 步骤 3: 处理叶子节点 */
    hlist_for_each_entry_rcu(fa, &n->leaf, fa_list) {
        struct fib_info *fi = fa->fa_info;
        struct fib_nh_common *nhc;
        int nhsel, err;

        // DSCP 匹配检查
        if (fa->fa_dscp && !fib_dscp_masked_match(fa->fa_dscp, flp))
            continue;

        // 死亡路由检查
        if (READ_ONCE(fi->fib_dead))
            continue;

        // 作用域检查
        if (fa->fa_info->fib_scope < flp->flowi4_scope)
            continue;

        fib_alias_accessed(fa);
        err = fib_props[fa->fa_type].error;
        if (unlikely(err < 0))
            return err;

        // 多路径处理
        if (unlikely(fi->nh)) {
            nhc = nexthop_get_nhc_lookup(fi->nh, fib_flags, flp, &nhsel);
            if (nhc)
                goto set_result;
            goto miss;
        }

        for (nhsel = 0; nhsel < fib_info_num_path(fi); nhsel++) {
            nhc = fib_info_nhc(fi, nhsel);

            if (!fib_lookup_good_nhc(nhc, fib_flags, flp))
                continue;
set_result:
            // 设置结果
            res->prefix = htonl(n->key);
            res->prefixlen = KEYLENGTH - fa->fa_slen;
            res->nh_sel = nhsel;
            res->nhc = nhc;
            res->type = fa->fa_type;
            res->scope = fi->fib_scope;
            res->dscp = fa->fa_dscp;
            res->fi = fi;
            res->table = tb;
            res->fa_head = &n->leaf;

            return err;
        }
    }
miss:
    goto backtrace;
}
```

---

## 输出路由 (ip_route_output)

### ip_route_output_key_hash

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 2691-2710 行)

```c
struct rtable *ip_route_output_key_hash(struct net *net, struct flowi4 *fl4,
                    const struct sk_buff *skb)
{
    struct fib_result res = {
        .type       = RTN_UNSPEC,
        .fi         = NULL,
        .table      = NULL,
        .tclassid   = 0,
    };
    struct rtable *rth;

    fl4->flowi4_iif = LOOPBACK_IFINDEX;  // 输出路由从回环设备开始

    rcu_read_lock();
    rth = ip_route_output_key_hash_rcu(net, fl4, &res, skb);
    rcu_read_unlock();

    return rth;
}
```

### ip_route_output_key_hash_rcu

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 2712-2879 行)

核心输出路由查找:

```c
struct rtable *ip_route_output_key_hash_rcu(struct net *net, struct flowi4 *fl4,
                        struct fib_result *res,
                        const struct sk_buff *skb)
{
    struct net_device *dev_out = NULL;
    int orig_oif = fl4->flowi4_oif;
    unsigned int flags = 0;
    struct rtable *rth;
    int err;

    // 处理源地址
    if (fl4->saddr) {
        if (ipv4_is_multicast(fl4->saddr) || ipv4_is_lbcast(fl4->saddr)) {
            rth = ERR_PTR(-EINVAL);
            goto out;
        }
        // ... 源地址验证 ...
    }

    // 处理输出接口
    if (fl4->flowi4_oif) {
        dev_out = dev_get_by_index_rcu(net, fl4->flowi4_oif);
        // ... 设备验证 ...
        
        // 处理多播/广播
        if (ipv4_is_local_multicast(fl4->daddr) ||
            ipv4_is_lbcast(fl4->daddr) ||
            fl4->flowi4_proto == IPPROTO_IGMP) {
            if (!fl4->saddr)
                fl4->saddr = inet_select_addr(dev_out, 0, RT_SCOPE_LINK);
            goto make_route;
        }
    }

    // 处理本地地址
    if (!fl4->daddr) {
        fl4->daddr = fl4->saddr;
        if (!fl4->daddr)
            fl4->daddr = fl4->saddr = htonl(INADDR_LOOPBACK);
        dev_out = net->loopback_dev;
        fl4->flowi4_oif = LOOPBACK_IFINDEX;
        res->type = RTN_LOCAL;
        flags |= RTCF_LOCAL;
        goto make_route;
    }

    // FIB 查找
    err = fib_lookup(net, fl4, res, 0);
    if (err) {
        res->fi = NULL;
        res->table = NULL;
        // ... 错误处理和候补路由 ...
    }

    if (res->type == RTN_LOCAL) {
        // 本地路由处理
        if (!fl4->saddr) {
            if (res->fi->fib_prefsrc)
                fl4->saddr = res->fi->fib_prefsrc;
            else
                fl4->saddr = fl4->daddr;
        }
        dev_out = l3mdev_master_dev_rcu(FIB_RES_DEV(*res)) ?: net->loopback_dev;
        orig_oif = FIB_RES_OIF(*res);
        fl4->flowi4_oif = dev_out->ifindex;
        flags |= RTCF_LOCAL;
        goto make_route;
    }

    // 选择路径 (处理多路径)
    fib_select_path(net, res, fl4, skb);

    dev_out = FIB_RES_DEV(*res);

make_route:
    rth = __mkroute_output(res, fl4, orig_oif, dev_out, flags);

out:
    return rth;
}
```

---

## 输入路由 (ip_route_input)

### ip_route_input_noref

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 2546-2559 行)

```c
enum skb_drop_reason ip_route_input_noref(struct sk_buff *skb, __be32 daddr,
                      __be32 saddr, dscp_t dscp,
                      struct net_device *dev)
{
    enum skb_drop_reason reason;
    struct fib_result res;

    rcu_read_lock();
    reason = ip_route_input_rcu(skb, daddr, saddr, dscp, dev, &res);
    rcu_read_unlock();

    return reason;
}
```

### ip_route_input_rcu

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 2493-2544 行)

```c
static enum skb_drop_reason
ip_route_input_rcu(struct sk_buff *skb, __be32 daddr, __be32 saddr,
           dscp_t dscp, struct net_device *dev,
           struct fib_result *res)
{
    /* 多播识别逻辑已从路由缓存移至此处。
     * 问题在于太多以太网卡的硬件多播过滤器有问题...
     * 现在我们尝试清除这些无用的路由缓存条目。
     */
    if (ipv4_is_multicast(daddr)) {
        enum skb_drop_reason reason = SKB_DROP_REASON_NOT_SPECIFIED;
        struct in_device *in_dev = __in_dev_get_rcu(dev);
        int our = 0;

        if (!in_dev)
            return reason;

        our = ip_check_mc_rcu(in_dev, daddr, saddr, ip_hdr(skb)->protocol);

        // ... L3 master 检查 ...

        if (our
#ifdef CONFIG_IP_MROUTE
            || (!ipv4_is_local_multicast(daddr) && IN_DEV_MFORWARD(in_dev))
#endif
           ) {
            reason = ip_route_input_mc(skb, daddr, saddr, dscp, dev, our);
        }
        return reason;
    }

    return ip_route_input_slow(skb, daddr, saddr, dscp, dev, res);
}
```

### ip_route_input_slow

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 2262-2490 行)

```c
static enum skb_drop_reason
ip_route_input_slow(struct sk_buff *skb, __be32 daddr, __be32 saddr,
            dscp_t dscp, struct net_device *dev,
            struct fib_result *res)
{
    enum skb_drop_reason reason = SKB_DROP_REASON_NOT_SPECIFIED;
    struct in_device *in_dev = __in_dev_get_rcu(dev);
    struct flow_keys *flkeys = NULL, _flkeys;
    struct net *net = dev_net(dev);
    struct ip_tunnel_info *tun_info;
    int err = -EINVAL;
    unsigned int flags = 0;
    u32 itag = 0;
    struct rtable *rth;
    struct flowi4 fl4;
    bool do_cache = true;

    // IP 在此设备上已禁用
    if (!in_dev)
        goto out;

    // 检查 Martian 源/目的地址
    // ...

    res->fi = NULL;
    res->table = NULL;

    // 构造流查找键
    fl4.flowi4_l3mdev = 0;
    fl4.flowi4_oif = 0;
    fl4.flowi4_iif = dev->ifindex;
    fl4.flowi4_mark = skb->mark;
    fl4.flowi4_dscp = dscp;
    fl4.flowi4_scope = RT_SCOPE_UNIVERSE;
    fl4.flowi4_flags = 0;
    fl4.daddr = daddr;
    fl4.saddr = saddr;
    fl4.flowi4_uid = sock_net_uid(net, NULL);
    fl4.flowi4_multipath_hash = 0;

    // FIB 查找
    err = fib_lookup(net, &fl4, res, 0);
    if (err != 0) {
        if (!IN_DEV_FORWARD(in_dev))
            err = -EHOSTUNREACH;
        goto no_route;
    }

    // 处理广播路由
    if (res->type == RTN_BROADCAST) {
        if (IN_DEV_BFORWARD(in_dev))
            goto make_route;
        if (IPV4_DEVCONF_ALL_RO(net, BC_FORWARDING))
            do_cache = false;
        goto brd_input;
    }

    // 处理本地路由
    if (res->type == RTN_LOCAL) {
        reason = fib_validate_source_reason(skb, saddr, daddr, dscp,
                            0, dev, in_dev, &itag);
        if (reason)
            goto martian_source;
        goto local_input;
    }

    // 检查转发能力
    if (!IN_DEV_FORWARD(in_dev)) {
        err = -EHOSTUNREACH;
        goto no_route;
    }

make_route:
    reason = ip_mkroute_input(skb, res, in_dev, daddr, saddr, dscp, flkeys);

out:
    return reason;

// ... 广播输入、本地输入、无路由等情况处理 ...
}
```

### __mkroute_input

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 1810-1884 行)

```c
static enum skb_drop_reason
__mkroute_input(struct sk_buff *skb, const struct fib_result *res,
        struct in_device *in_dev, __be32 daddr,
        __be32 saddr, dscp_t dscp)
{
    enum skb_drop_reason reason = SKB_DROP_REASON_NOT_SPECIFIED;
    struct fib_nh_common *nhc = FIB_RES_NHC(*res);
    struct net_device *dev = nhc->nhc_dev;
    struct fib_nh_exception *fnhe;
    struct rtable *rth;
    int err;
    struct in_device *out_dev;
    bool do_cache;
    u32 itag = 0;

    out_dev = __in_dev_get_rcu(dev);
    if (!out_dev) {
        net_crit_ratelimited("Bug in ip_route_input_slow(). Please report.\n");
        return reason;
    }

    // 源地址验证
    err = fib_validate_source(skb, saddr, daddr, dscp, FIB_RES_OIF(*res),
                  in_dev->dev, in_dev, &itag);
    if (err < 0) {
        reason = -err;
        ip_handle_martian_source(in_dev->dev, in_dev, skb, daddr, saddr);
        goto cleanup;
    }

    do_cache = res->fi && !itag;

    // 查找异常 (fnhe)
    fnhe = find_exception(nhc, daddr);
    if (do_cache) {
        if (fnhe)
            rth = rcu_dereference(fnhe->fnhe_rth_input);
        else
            rth = rcu_dereference(nhc->nhc_rth_input);
        if (rt_cache_valid(rth)) {
            skb_dst_set_noref(skb, &rth->dst);
            goto out;
        }
    }

    rth = rt_dst_alloc(out_dev->dev, 0, res->type, /* ... */);

    // ... 缓存处理 ...

    skb_dst_set(skb, &rth->dst);
    reason = SKB_NOT_DROPPED_YET;
    goto out;
}
```

---

## 源地址验证 (fib_validate_source)

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_frontend.c` (第 345-461 行)

```c
static int __fib_validate_source(struct sk_buff *skb, __be32 src, __be32 dst,
                 dscp_t dscp, int oif, struct net_device *dev,
                 int rpf, struct in_device *idev, u32 *itag)
{
    struct net *net = dev_net(dev);
    enum skb_drop_reason reason;
    struct flow_keys flkeys;
    int ret, no_addr;
    struct fib_result res;
    struct flowi4 fl4;
    bool dev_match;

    fl4.flowi4_oif = 0;
    fl4.flowi4_l3mdev = l3mdev_master_ifindex_rcu(dev);
    fl4.flowi4_iif = oif ? : LOOPBACK_IFINDEX;
    fl4.daddr = src;    // 交换：查找源地址的路由
    fl4.saddr = dst;    // 交换：目的地址作为源
    fl4.flowi4_dscp = dscp;
    fl4.flowi4_scope = RT_SCOPE_UNIVERSE;
    // ...

    no_addr = idev->ifa_list == NULL;

    fl4.flowi4_mark = IN_DEV_SRC_VMARK(idev) ? skb->mark : 0;
    if (!fib4_rules_early_flow_dissect(net, skb, &fl4, &flkeys)) {
        fl4.flowi4_proto = 0;
        fl4.fl4_sport = 0;
        fl4.fl4_dport = 0;
    } else {
        swap(fl4.fl4_sport, fl4.fl4_dport);
    }

    // 执行 FIB 查找来验证源地址
    if (fib_lookup(net, &fl4, &res, 0))
        goto last_resort;

    if (res.type != RTN_UNICAST) {
        if (res.type != RTN_LOCAL) {
            reason = SKB_DROP_REASON_IP_INVALID_SOURCE;
            goto e_inval;
        } else if (!IN_DEV_ACCEPT_LOCAL(idev)) {
            reason = SKB_DROP_REASON_IP_LOCAL_SOURCE;
            goto e_inval;
        }
    }

    fib_combine_itag(itag, &res);

    // 检查设备是否匹配
    dev_match = fib_info_nh_uses_dev(res.fi, dev);
    dev_match = dev_match || (res.type == RTN_LOCAL && dev == net->loopback_dev);
    if (dev_match) {
        ret = FIB_RES_NHC(res)->nhc_scope >= RT_SCOPE_HOST;
        return ret;
    }

    // ... 更多检查 ...

last_resort:
    if (rpf)
        goto e_rpf;
    *itag = 0;
    return 0;

e_inval:
    return -reason;
e_rpf:
    return -SKB_DROP_REASON_IP_RPFILTER;
}

int fib_validate_source(struct sk_buff *skb, __be32 src, __be32 dst,
            dscp_t dscp, int oif, struct net_device *dev,
            struct in_device *idev, u32 *itag)
{
    int r = secpath_exists(skb) ? 0 : IN_DEV_RPFILTER(idev);
    struct net *net = dev_net(dev);

    if (!r && !fib_num_tclassid_users(net) &&
        (dev->ifindex != oif || !IN_DEV_TX_REDIRECTS(idev))) {
        if (IN_DEV_ACCEPT_LOCAL(idev))
            goto ok;
        // ... 自定义本地路由检查 ...
        if (net->ipv4.fib_has_custom_local_routes ||
            fib4_has_custom_rules(net))
            goto full_check;
        if (inet_lookup_ifaddr_rcu(net, src))
            return -SKB_DROP_REASON_IP_LOCAL_SOURCE;

ok:
        *itag = 0;
        return 0;
    }

full_check:
    return __fib_validate_source(skb, src, dst, dscp, oif, dev, r, idev, itag);
}
```

---

## 路由规则 (fib_rules)

### struct fib_rules_ops

**文件**: `/Users/sphinx/github/linux/include/net/fib_rules.h` (第 64-102 行)

```c
struct fib_rules_ops {
    int             family;           // AF_INET 或 AF_INET6
    struct list_head list;           // 规则操作符列表
    int             rule_size;        // 规则结构大小
    int             addr_size;        // 地址大小
    int             unresolved_rules; // 未解析规则数
    int             nr_goto_rules;    // goto 规则数
    unsigned int    fib_rules_seq;    // 规则序列号

    // 规则动作执行
    int             (*action)(struct fib_rule *,
                      struct flowi *, int,
                      struct fib_lookup_arg *);
    
    // 规则抑制检查
    bool            (*suppress)(struct fib_rule *, int,
                        struct fib_lookup_arg *);
    
    // 规则匹配
    int             (*match)(struct fib_rule *,
                     struct flowi *, int);
    
    // 规则配置
    int             (*configure)(struct fib_rule *,
                     struct sk_buff *,
                     struct fib_rule_hdr *,
                     struct nlattr **,
                     struct netlink_ext_ack *);
    
    int             (*delete)(struct fib_rule *);
    int             (*compare)(struct fib_rule *,
                   struct fib_rule_hdr *,
                   struct nlattr **);
    int             (*fill)(struct fib_rule *, struct sk_buff *,
                    struct fib_rule_hdr *);
    size_t          (*nlmsg_payload)(struct fib_rule *);

    // 规则修改后刷新路由缓存
    void            (*flush_cache)(struct fib_rules_ops *ops);

    int             nlgroup;
    struct list_head rules_list;      // 规则列表
    struct module   *owner;
    struct net      *fro_net;
    struct rcu_head  rcu;
};
```

### fib_rules_lookup

**文件**: `/Users/sphinx/github/linux/net/core/fib_rules.c` (第 313-365 行)

```c
int fib_rules_lookup(struct fib_rules_ops *ops, struct flowi *fl,
             int flags, struct fib_lookup_arg *arg)
{
    struct fib_rule *rule;
    int err;

    rcu_read_lock();

    // 遍历所有规则
    list_for_each_entry_rcu(rule, &ops->rules_list, list) {
jumped:
        // 规则匹配检查
        if (!fib_rule_match(rule, ops, fl, flags, arg))
            continue;

        // 处理 GOTO 规则
        if (rule->action == FR_ACT_GOTO) {
            struct fib_rule *target;

            target = rcu_dereference(rule->ctarget);
            if (target == NULL) {
                continue;
            } else {
                rule = target;
                goto jumped;
            }
        } else if (rule->action == FR_ACT_NOP)
            continue;
        else
            // 执行规则动作 (如查表)
            err = INDIRECT_CALL_MT(ops->action,
                       fib6_rule_action,
                       fib4_rule_action,
                       rule, fl, flags, arg);

        // 抑制检查
        if (!err && ops->suppress && INDIRECT_CALL_MT(ops->suppress,
                          fib6_rule_suppress,
                          fib4_rule_suppress,
                          rule, flags, arg))
            continue;

        // 返回结果
        if (err != -EAGAIN) {
            if ((arg->flags & FIB_LOOKUP_NOREF) ||
                likely(refcount_inc_not_zero(&rule->refcnt))) {
                arg->rule = rule;
                goto out;
            }
            break;
        }
    }

    err = -ESRCH;
out:
    rcu_read_unlock();

    return err;
}
```

### IPv4 规则操作模板

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_rules.c` (第 470-485 行)

```c
static const struct fib_rules_ops __net_initconst fib4_rules_ops_template = {
    .family         = AF_INET,
    .rule_size      = sizeof(struct fib4_rule),
    .addr_size      = sizeof(u32),
    .action         = fib4_rule_action,
    .suppress       = fib4_rule_suppress,
    .match          = fib4_rule_match,
    .configure      = fib4_rule_configure,
    .delete         = fib4_rule_delete,
    .compare        = fib4_rule_compare,
    .fill           = fib4_rule_fill,
    .nlmsg_payload  = fib4_rule_nlmsg_payload,
    .flush_cache    = fib4_rule_flush_cache,
    .nlgroup        = RTNLGRP_IPV4_RULE,
    .owner          = THIS_MODULE,
};
```

### fib4_rule_action

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_rules.c` (第 111-145 行)

```c
INDIRECT_CALLABLE_SCOPE int fib4_rule_action(struct fib_rule *rule,
                         struct flowi *flp, int flags,
                         struct fib_lookup_arg *arg)
{
    int err = -EAGAIN;
    struct fib_table *tbl;
    u32 tb_id;

    switch (rule->action) {
    case FR_ACT_TO_TBL:
        break;
    case FR_ACT_UNREACHABLE:
        return -ENETUNREACH;
    case FR_ACT_PROHIBIT:
        return -EACCES;
    case FR_ACT_BLACKHOLE:
    default:
        return -EINVAL;
    }

    rcu_read_lock();

    // 获取目标表
    tb_id = fib_rule_get_table(rule, arg);
    tbl = fib_get_table(rule->fr_net, tb_id);
    if (tbl)
        err = fib_table_lookup(tbl, &flp->u.ip4,
                   (struct fib_result *)arg->result,
                   arg->flags);

    rcu_read_unlock();
    return err;
}
```

---

## 路由缓存机制

### 概述

在较新的 Linux 内核版本中，传统的路由缓存已被移除。现代内核使用以下机制替代：

1. **FIB Trie**: 直接进行最长前缀匹配
2. **dst_entry 缓存**: skb 的目标缓存
3. **生成 ID (Generation ID)**: 用于使缓存失效
4. **路由异常 (fib_nh_exception)**: 存储特定目的地址的异常

### rt_cache_flush

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 407-410 行)

```c
void rt_cache_flush(struct net *net)
{
    rt_genid_bump_ipv4(net);  // 增加 IPv4 路由生成 ID
}
```

### 路由异常处理

**文件**: `/Users/sphinx/github/linux/include/net/ip_fib.h` (第 61-77 行)

```c
struct fib_nh_exception {
    struct fib_nh_exception __rcu  *fnhe_next;   // 下一个异常
    int                 fnhe_genid;               // 异常生成 ID
    __be32              fnhe_daddr;               // 目的地址
    u32                 fnhe_pmtu;                // 路径 MTU
    bool                fnhe_mtu_locked;          // MTU 是否锁定
    __be32              fnhe_gw;                  // 异常网关
    unsigned long       fnhe_expires;             // 过期时间
    struct rtable __rcu *fnhe_rth_input;          // 输入路由缓存
    struct rtable __rcu *fnhe_rth_output;         // 输出路由缓存
    unsigned long       fnhe_stamp;              // 时间戳
    struct rcu_head     rcu;
};
```

### 缓存查找

**文件**: `/Users/sphinx/github/linux/net/ipv4/route.c` (第 1872-1882 行)

```c
fnhe = find_exception(nhc, daddr);
if (do_cache) {
    if (fnhe)
        rth = rcu_dereference(fnhe->fnhe_rth_input);
    else
        rth = rcu_dereference(nhc->nhc_rth_input);
    if (rt_cache_valid(rth)) {
        skb_dst_set_noref(skb, &rth->dst);
        goto out;
    }
}
```

### 历史演变

- **2.6.39 之前**: Linux 使用完整的路由缓存 (route cache)
- **3.6+**: 路由缓存被标记为废弃
- **3.6 - 4.1**: 路由缓存作为选项保留
- **4.2+**: 路由缓存代码被移除

现代内核采用"FIB-first"方法，直接在 FIB 中查找，避免了缓存同步问题。

---

## FIB Trie 数据结构

### struct key_vector

**文件**: `/Users/sphinx/github/linux/net/ipv4/fib_trie.c` (第 121-132 行)

```c
struct key_vector {
    t_key key;                    // 键值 (IP地址)
    unsigned char pos;            // 位置 (2log(KEYLENGTH) 位)
    unsigned char bits;           // 位数 (子节点数 = 2^bits)
    unsigned char slen;           // 后续长度
    union {
        // 叶节点: fib_alias 哈希链表
        struct hlist_head leaf;
        // 内部节点: 子节点指针数组
        DECLARE_FLEX_ARRAY(struct key_vector __rcu *, tnode);
    };
};
```

### Trie 结构

```c
struct trie {
    struct key_vector kv[1];      // 根节点
#ifdef CONFIG_IP_FIB_TRIE_STATS
    struct trie_use_stats __percpu *stats;  // 统计信息
#endif
};
```

### 关键宏

```c
#define IS_TRIE(n)   ((n)->pos >= KEYLENGTH)   // 是否为 Trie 根
#define IS_TNODE(n)  ((n)->bits)               // 是否为内部节点
#define IS_LEAF(n)   (!(n)->bits)              // 是否为叶节点
```

### 查找过程

1. **步骤 1**: 从根节点开始，根据目标地址位选择子节点，直到找到最长匹配
2. **步骤 2**: 回溯查找最长前缀
3. **步骤 3**: 遍历叶节点的 fib_alias 列表，找到最佳匹配

---

## 关键文件路径总结

| 文件 | 功能 |
|------|------|
| `/Users/sphinx/github/linux/net/ipv4/route.c` | 主要路由函数实现 |
| `/Users/sphinx/github/linux/net/ipv4/fib_frontend.c` | FIB 前端接口、源验证 |
| `/Users/sphinx/github/linux/net/ipv4/fib_rules.c` | IPv4 路由规则 |
| `/Users/sphinx/github/linux/net/ipv4/fib_trie.c` | FIB Trie 实现 |
| `/Users/sphinx/github/linux/net/ipv4/fib_semantics.c` | FIB 语义、路由信息管理 |
| `/Users/sphinx/github/linux/net/core/fib_rules.c` | 通用路由规则框架 |
| `/Users/sphinx/github/linux/include/net/ip_fib.h` | FIB 核心数据结构定义 |
| `/Users/sphinx/github/linux/include/net/route.h` | rtable 结构定义 |
| `/Users/sphinx/github/linux/include/net/fib_rules.h` | 路由规则操作定义 |
| `/Users/sphinx/github/linux/include/net/dst.h` | dst_entry 结构定义 |

---

## 参考

- Linux 内核源码 (6.8+)
- net/ipv4/route.c
- net/ipv4/fib_frontend.c
- net/ipv4/fib_rules.c
- net/ipv4/fib_trie.c
- include/net/ip_fib.h
- include/net/route.h
- include/net/fib_rules.h
