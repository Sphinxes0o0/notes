# Netfilter xt_RATEEST

## 1. 模块架构

### 1.1 功能概述

xt_RATEEST 用于速率估计，是 TC 速率估计的 Netfilter 接口。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/netfilter/xt_RATEEST.c` | RATEEST 实现 |
| `include/uapi/linux/netfilter/xt_RATEEST.h` | 用户空间接口 |

## 2. 核心数据结构

### 2.1 struct xt_rateest_info

```c
// include/uapi/linux/netfilter/xt_RATEEST.h:15
struct xt_rateest_info {
    char name[IFNAMSIZ];      // 估计器名称
    __u8  interval;           // 采样间隔 (指数)
    __u8  ewma_log;          // EWMA 对数
};
```

## 3. 实现

### 3.1 xt_rateest_mt()

```c
// net/netfilter/xt_RATEEST.c:100
static bool xt_rateest_mt(const struct sk_buff *skb,
                          struct xt_action_param *par)
{
    const struct xt_rateest_info *info = par->matchinfo;
    struct xt_rateest *est;

    // 查找或创建速率估计器
    est = xt_rateest_find(info->name);
    if (!est)
        return false;

    // 更新计数
    spin_lock_bh(&est->lock);
    est->stats.pkts++;
    est->stats.bytes += skb->len;
    spin_unlock_bh(&est->lock);

    return true;
}
```

### 3.2 xt_rateest_target()

```c
// net/netfilter/xt_RATEEST.c:150
static unsigned int xt_rateest_tg(struct sk_buff *skb,
                                   const struct xt_action_param *par)
{
    const struct xt_rateest_info *info = par->targinfo;
    struct xt_rateest *est;

    est = xt_rateest_get(info->name, info->interval, info->ewma_log);
    if (!est)
        return XT_DROP;

    // 更新统计
    spin_lock_bh(&est->lock);
    est->stats.pkts++;
    est->stats.bytes += skb->len;
    spin_unlock_bh(&est->lock);

    return XT_CONTINUE;
}
```

## 4. 速率估计器

### 4.1 struct xt_rateest

```c
// net/netfilter/xt_RATEEST.c:50
struct xt_rateest {
    char name[IFNAMSIZ];

    struct {
        atomic64_t bytes;     // 字节计数
        atomic64_t pkts;     // 包计数
    } stats;

    struct {
        u32 bps;             // 字节每秒
        u32 pps;             // 包每秒
    } rate;

    spinlock_t lock;
    struct timer_list timer;

    struct hlist_node list;
};
```

## 5. 使用示例

### 5.1 创建估计器

```bash
# 创建速率估计器
iptables -t mangle -A INPUT -j RATEEST --rateest-name test --rateest-interval 1s --rateest-ewma-log 5

# 匹配估计器
iptables -t mangle -A OUTPUT -m rateest --rateest test --rateest-bps 1mbit -j ACCEPT
```

### 5.2 带宽限制

```bash
# 基于速率估计进行限速
iptables -t mangle -A FORWARD -m rateest --rateest test --rateest-bps 10mbit -j DROP
```

## 6. 与 TC 集成

```c
// xt_RATEEST 与 TC 的 sch_htb 或 sch_fq_codel 配合使用
// 可以在 iptables 中估计速率，然后在 TC 中应用策略
```
