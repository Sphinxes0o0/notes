# neighbour - 邻居子系统

## 1. 模块架构

### 1.1 功能概述

邻居子系统实现了 ARP (IPv4) 和 NDP (IPv6) 的核心功能，维护从 IP 地址到 MAC 地址的映射。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/neighbour.c` | 邻居表实现 |
| `include/net/neighbour.h` | 邻居定义 |
| `net/ipv4/arp.c` | ARP 实现 |
| `net/ipv6/ndisc.c` | NDisc 实现 |

## 2. 核心数据结构

### 2.1 struct neighbour

```c
// include/net/neighbour.h:113
struct neighbour {
    struct сосед next;        // 哈希链表
    struct rcu_head rcu;
    struct net_device *dev;   // 网络设备
    unsigned char   *ha;     // 硬件地址
    struct hh_cache *hh;
    __u8           primary_key[0];  // IP 地址作为主键
};
```

### 2.2 struct neigh_table

```c
// include/net/neighbour.h:180
struct neigh_table {
    int family;                    // AF_INET/AF_INET6
    unsigned int key_len;          // 键长度
    __be16 protocol;              // 协议

    // 哈希表
    struct neigh_hash __rcu **hash_buckets;
    unsigned int        hash_buckets_log;
    unsigned int        hash_size;

    // 构造函数
    int (*constructor)(struct neighbour *);

    // 哈希函数
    u32 (*hash)(const void *pkey, const struct net_device *dev);

    // 验证
    int (*key_eq)(const struct neighbour *n, const void *pkey);

    // 状态和统计
    atomic_t         entries;
    atomic_t         allocs;
    int              max_clean_probes;
    int              gc_thresh;

    // 统计
    struct neigh_statistics __percpu *stats;

    // 参数
    struct neigh_parms parms;

    // 哈希表锁
    spinlock_t       lock;

    // 最近最少使用链表
    struct list_head   lru_list;

    // ID
    char            id[16];
};
```

### 2.3 NUD 状态

```c
// include/uapi/linux/neighbour.h:34
enum {
    NUD_INCOMPLETE   = 0x01,  // 地址解析进行中
    NUD_REACHABLE    = 0x02,  // 最近确认可达
    NUD_STALE        = 0x04,  // 可达时间过期
    NUD_DELAY        = 0x08,  // 等待确认
    NUD_PROBE        = 0x10,  // 主动探测
    NUD_FAILED       = 0x20,  // 解析失败
    NUD_NOARP        = 0x40,  // 不需要解析
    NUD_PERMANENT    = 0x80,  // 永久条目
};
```

## 3. ARP/NDISC 初始化

### 3.1 ARP 表初始化

```c
// net/ipv4/arp.c
static struct neigh_table arp_table = {
    .family = AF_INET,
    .key_len = 4,  // IPv4 地址长度
    .protocol = cpu_to_be16(ETH_P_IP),
    .hash = arp_hash,
    .key_eq = arp_key_eq,
    .constructor = arp_constructor,
    .id = "arp_cache",
};
```

### 3.2 NDisc 表初始化

```c
// net/ipv6/ndisc.c
struct neigh_table nd_tbl = {
    .family = AF_INET6,
    .key_len = 16,  // IPv6 地址长度
    .protocol = cpu_to_be16(ETH_P_IPV6),
    .hash = ndisc_hash,
    .key_eq = ndisc_key_eq,
    .constructor = ndisc_constructor,
    .id = "ndisc_cache",
};
```

## 4. 邻居查找

### 4.1 neigh_lookup()

```c
// net/core/neighbour.c:1280
struct neighbour *neigh_lookup(struct neigh_table *tbl, const void *pkey,
                              struct net_device *dev)
{
    struct neighbour *n;
    u32 hash_val;

    // 计算哈希
    hash_val = tbl->hash(pkey, dev) & (tbl->hash_size - 1);

    // 查找
    rcu_read_lock();
    n = lookup_neigh(tbl, pkey, hash_val);
    if (n && !atomic_inc_not_zero(&n->refcnt))
        n = NULL;
    rcu_read_unlock();

    return n;
}
```

### 4.2 neigh_create()

```c
// net/core/neighbour.c:1400
struct neighbour *neigh_create(struct neigh_table *tbl, const void *pkey,
                               struct net_device *dev)
{
    struct neighbour *n;
    u32 hash_val;

    // 分配
    n = kmem_cache_alloc(tbl->kmem_cachep, GFP_ATOMIC);

    // 初始化
    n->dev = dev;
    n->primary_key = pkey;
    n->used = jiffies;

    // 调用协议特定构造函数
    err = tbl->constructor(n);

    // 添加到哈希表
    hash_val = tbl->hash(pkey, dev) & (tbl->hash_size - 1);
    __neigh_insert(hash_val, n, tbl);

    return n;
}
```

## 5. NUD 状态机

### 5.1 状态转换

```
                    +------------+
                    |  INCOMPLETE|
                    +------------+
                         |
          NS 丢失        | NS 发送
          或无响应         v
        +--------+  +--------+  +----------+
   +--->| STALE  |<-|DELAY   |<| REACHABLE|
   |    +--------+  +--------+  +----------+
   |       ^           |
   |       |           | 定时器到期
   |       |           v
   |       |       +--------+
   |       +-------| PROBE  |
   |               +--------+
   +----NA 收到------+--无响应
```

### 5.2 neigh_timer_handler()

```c
// net/core/neighbour.c:940
void neigh_timer_handler(struct timer_list *t)
{
    struct neighbour *neigh = from_timer(neigh, t, timer);

    // 根据状态处理
    switch (neigh->nud_state) {
    case NUD_INCOMPLETE:
        // 发送 NS
        neigh->ops->solicit(neigh);
        break;

    case NUD_REACHABLE:
        // 转换为 STALE
        neigh_update(neigh, NULL, NUD_STALE);
        break;

    case NUD_DELAY:
        // 发送 NS，进入 PROBE
        neigh->ops->solicit(neigh);
        neigh->nud_state = NUD_PROBE;
        break;

    case NUD_PROBE:
        // 重传 NS
        neigh->ops->solicit(neigh);
        break;
    }
}
```

## 6. ARP 实现

### 6.1 arp_solicit()

```c
// net/ipv4/arp.c:650
static void arp_solicit(struct neighbour *neigh, struct sk_buff *skb)
{
    __be32 saddr;
    u8 dst_hw[ETH_ALEN];

    // 获取源地址
    if (skb && !inet_addr_type_dev_table(net, dev, ip_hdr(skb)->saddr))
        return;

    // 发送 ARP 请求
    arp_send(ARPOP_REQUEST, ETH_P_ARP, target_ip, dev, saddr,
             broadcast_hw, dev->dev_addr, NULL);
}
```

### 6.2 arp_rcv()

```c
// net/ipv4/arp.c:1105
int arp_rcv(struct sk_buff *skb)
{
    struct arphdr *arp = arp_hdr(skb);

    // 查找或创建邻居条目
    neigh = __neigh_lookup(&arp_table, arp->ar_tip, dev);

    // 处理 ARP 操作
    switch (arp->ar_op) {
    case htons(ARPOP_REQUEST):
        // 请求：发送 ARP 回复
        arp_send_reply(arp->ar_sha, arp->ar_sip, dev, arp->ar_thi);
        break;
    case htons(ARPOP_REPLY):
        // 回复：更新邻居
        neigh->ops->update(neigh, arp);
        break;
    }
}
```

## 7. GC (垃圾回收)

### 7.1 neigh_forced_gc()

```c
// net/core/neighbour.c:1600
int neigh_forced_gc(struct neigh_table *tbl)
{
    int evicted = 0;

    spin_lock_bh(&tbl->lock);

    // 遍历 LRU 列表
    list_for_each_entry_safe(neigh, next, &tbl->lru_list, list) {
        // 跳过永久条目
        if (neigh->nud_state & NUD_PERMANENT)
            continue;

        // 跳过正在使用的
        if (neigh->refcnt > 1)
            continue;

        // 删除
        __neigh_remove(neigh);
        evicted++;
    }

    spin_unlock_bh(&tbl->lock);
    return evicted;
}
```

### 7.2 GC 触发

```c
// 条件触发:
// 1. 表大小超过 gc_thresh
// 2. 定时器周期性检查
```
