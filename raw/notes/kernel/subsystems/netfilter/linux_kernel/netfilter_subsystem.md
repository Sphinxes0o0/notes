# Linux Kernel Netfilter 子系统分析文档

## 目录

1. [Netfilter 概述](#1-netfilter-概述)
2. [核心数据结构](#2-核心数据结构)
3. [Hook 机制](#3-hook-机制)
4. [Connection Tracking (连接跟踪)](#4-connection-tracking-连接跟踪)
5. [iptables](#5-iptables)
6. [nftables](#6-nftables)
7. [Xtables 框架](#7-xtables-框架)
8. [数据包处理流程](#8-数据包处理流程)
9. [关键代码索引](#9-关键代码索引)

---

## 1. Netfilter 概述

Netfilter 是 Linux 内核提供的网络数据包过滤框架,位于网络栈的关键路径上,允许内核模块在网络数据包处理的不同阶段拦截和修改数据包。

### 1.1 HOOK 点

Netfilter 在网络协议栈的不同位置定义了多个 HOOK 点:

```
                                    ┌─────────────────────────────────────┐
                                    │          Network Stack              │
                                    │                                     │
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Ingress  │    │PREROUTING│    │          │    │ FORWARD  │    │          │    │POSTROUTING│
  │(NF_NETDEV│───▶│ (NF_INET │───▶│ 路由判决  │───▶│ (NF_INET │───▶│ 路由判决  │───▶│ (NF_INET  │
  │ _INGRESS)│    │ _PRE_ROUTING)│    │          │    │ _FORWARD)│    │          │    │ _POST_ROUTING)│
  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                          │                                           │
                                          │                                           │
                                    ┌─────▼─────┐                              ┌──────▼─────┐
                                    │  LOCAL_IN │                              │ LOCAL_OUT  │
                                    │(NF_INET   │                              │ (NF_INET   │
                                    │ _LOCAL_IN)│                              │ _LOCAL_OUT)│
                                    └─────┬─────┘                              └──────┬─────┘
                                          │                                           │
                                          ▼                                           ▼
                                    ┌──────────┐                              ┌──────────┐
                                    │  应用层  │                              │  应用层   │
                                    └──────────┘                              └──────────┘
```

**Hook 点定义** (`include/uapi/linux/netfilter.h:42-50`):

```c
enum nf_inet_hooks {
    NF_INET_PRE_ROUTING,    // 0 - 路由之前,所有入站数据包
    NF_INET_LOCAL_IN,       // 1 - 已路由,目标是本机
    NF_INET_FORWARD,        // 2 - 已路由,需要转发
    NF_INET_LOCAL_OUT,      // 3 - 本机产生的数据包
    NF_INET_POST_ROUTING,   // 4 - 即将发送之前
    NF_INET_NUMHOOKS,
    NF_INET_INGRESS = NF_INET_NUMHOOKS,  // 5 - 设备 Ingress
};
```

### 1.2 Verdict (判决值)

Hook 函数返回以下判决值 (`include/uapi/linux/netfilter.h:11-17`):

```c
#define NF_DROP 0       // 丢弃数据包
#define NF_ACCEPT 1     // 接受数据包,继续下一个 hook
#define NF_STOLEN 2     // 数据包被"偷走",不再继续处理
#define NF_QUEUE 3      // 将数据包放入队列供用户空间处理
#define NF_REPEAT 4     // 重新调用当前 hook
#define NF_STOP 5       // 已废弃,为兼容用户空间
#define NF_MAX_VERDICT NF_STOP
```

### 1.3 协议族

Netfilter 支持多种协议族 (`include/uapi/linux/netfilter.h:58-70`):

```c
enum {
    NFPROTO_UNSPEC   =  0,
    NFPROTO_INET     =  1,  // 通用 INET (横跨 IPv4/IPv6)
    NFPROTO_IPV4     =  2,
    NFPROTO_ARP      =  3,
    NFPROTO_NETDEV   =  5,
    NFPROTO_BRIDGE   =  7,
    NFPROTO_IPV6     = 10,
    NFPROTO_NUMPROTO,
};
```

---

## 2. 核心数据结构

### 2.1 struct nf_hook_ops

Hook 操作结构体,定义在 `include/linux/netfilter.h:98-111`:

```c
struct nf_hook_ops {
    struct list_head    list;       // 用于链表中链接
    struct rcu_head     rcu;        // RCU 机制

    /* 用户填充的字段 */
    nf_hookfn          *hook;       // Hook 回调函数
    struct net_device  *dev;         // 绑定的网络设备 (可选)
    void               *priv;       // 私有数据
    u8                 pf;          // 协议族 (NFPROTO_*)
    enum nf_hook_ops_type hook_ops_type:8;  // Hook 操作类型
    unsigned int       hooknum;      // Hook 编号 (NF_INET_*)
    /* Hook 按优先级升序排列 */
    int                priority;     // 优先级,越小越高
};
```

**Hook 回调函数类型** (`include/linux/netfilter.h:88-90`):

```c
typedef unsigned int nf_hookfn(void *priv,
                               struct sk_buff *skb,
                               const struct nf_hook_state *state);
```

### 2.2 struct nf_hook_state

Hook 状态结构,定义在 `include/linux/netfilter.h:78-86`:

```c
struct nf_hook_state {
    u8              hook;       // 当前 hook 编号
    u8              pf;         // 协议族
    struct net_device *in;      // 输入设备
    struct net_device *out;     // 输出设备
    struct sock     *sk;        // 关联的 sock (可选)
    struct net      *net;       // 网络命名空间
    int (*okfn)(struct net *, struct sock *, struct sk_buff *);  // 继续处理函数
};
```

### 2.3 struct nf_hook_entries

Hook 条目集合,定义在 `include/linux/netfilter.h:123-141`:

```c
struct nf_hook_entries {
    u16                 num_hook_entries;  // Hook 条目数量
    /* 变长数组,包含实际的 hook 函数 */
    struct nf_hook_entry hooks[];

    /* 尾部:原始 ops 指针数组 (仅在删除时需要) */
    /* struct nf_hook_ops *orig_ops[] */
    /* struct nf_hook_entries_rcu_head head */
};
```

### 2.4 struct sk_buff

Socket buffer,是网络数据包的核心结构体,定义在 `include/linux/skbuff.h`。关键字段:

```c
struct sk_buff {
    struct sk_buff      *next;          // 下一个 skb
    struct sk_buff      *prev;          // 上一个 skb
    struct sock         *sk;            // 所属 socket
    struct net_device   *dev;           // 关联的网络设备
    unsigned int        len;            // 数据包长度
    unsigned int        data_len;       // 数据部分长度
    __u16               protocol;       // 协议号 (以太网帧类型)
    void                *data;          // 数据指针
    void                *tail;          // 数据尾部指针
    /* Netfilter 相关字段 */
    unsigned long       _nfct;          // 连接跟踪信息
    __u32              mark;            // Netfilter mark
    __u8               nf_trace;       // 跟踪标志
    /* ... 其他字段 ... */
};
```

### 2.5 struct nf_conn

连接跟踪结构,定义在 `include/net/netfilter/nf_conntrack.h:74-125`:

```c
struct nf_conn {
    struct nf_conntrack ct_general;     // 通用连接跟踪结构

    spinlock_t         lock;            // 保护此结构的锁
    u32                timeout;         // 过期时间 (jiffies)

#ifdef CONFIG_NF_CONNTRACK_ZONES
    struct nf_conntrack_zone zone;      // 连接跟踪区域
#endif

    /* 原始方向和回复方向的 tuple */
    struct nf_conntrack_tuple_hash tuplehash[IP_CT_DIR_MAX];

    unsigned long      status;          // 连接状态位图

    possible_net_t     ct_net;          // 网络命名空间

#if IS_ENABLED(CONFIG_NF_NAT)
    struct hlist_node  nat_bysource;   // NAT 源查找
#endif

    struct nf_conn     *master;         // 主连接 (用于期望连接)

#if defined(CONFIG_NF_CONNTRACK_MARK)
    u_int32_t         mark;            // 连接标记
#endif

#ifdef CONFIG_NF_CONNTRACK_SECMARK
    u_int32_t         secmark;         // 安全标记
#endif

    struct nf_ct_ext   *ext;           // 扩展数据

    /* 协议私有数据 (必须是最后一个成员) */
    union nf_conntrack_proto proto;
};
```

### 2.6 struct nf_conntrack_tuple

连接跟踪的 tuple,定义在 `include/net/netfilter/nf_conntrack_tuple.h:37-76`:

```c
struct nf_conntrack_tuple {
    struct nf_conntrack_man src;  // 源地址信息 (可被 NAT 修改)

    struct {
        union nf_inet_addr u3;    // 目标地址
        union {
            __be16 all;
            struct { __be16 port; } tcp;
            struct { __be16 port; } udp;
            struct { __u8 type, code; } icmp;
            struct { __be16 port; } dccp;
            struct { __be16 port; } sctp;
            struct { __be16 key; } gre;
        } u;

        u_int8_t protonum;         // L4 协议号
        u_int8_t dir;             // 方向
    } dst;
};
```

### 2.7 Connection Tracking 状态

定义在 `include/uapi/linux/netfilter/nf_conntrack_common.h:7-35`:

```c
enum ip_conntrack_info {
    IP_CT_ESTABLISHED,     // 0 - 已建立连接 (任意方向)
    IP_CT_RELATED,         // 1 - 相关连接 (如 FTP 数据连接)
    IP_CT_NEW,             // 2 - 新连接
    IP_CT_IS_REPLY,        // 3 - 回复方向标志位
    IP_CT_ESTABLISHED_REPLY = IP_CT_ESTABLISHED + IP_CT_IS_REPLY,  // 4
    IP_CT_RELATED_REPLY = IP_CT_RELATED + IP_CT_IS_REPLY,          // 5
    IP_CT_NUMBER,          // 6 - 连接类型数量
    IP_CT_UNTRACKED = 7,   // 未经跟踪的连接
};
```

### 2.8 Connection Tracking 状态位

定义在 `include/uapi/linux/netfilter/nf_conntrack_common.h:42-130`:

```c
enum ip_conntrack_status {
    IPS_EXPECTED_BIT = 0,      // 期望连接
    IPS_SEEN_REPLY_BIT = 1,    // 见过回复
    IPS_ASSURED_BIT = 2,       // 确认连接
    IPS_CONFIRMED_BIT = 3,     // 已确认 (已离开本机)
    IPS_SRC_NAT_BIT = 4,       // 需要源 NAT
    IPS_DST_NAT_BIT = 5,       // 需要目标 NAT
    IPS_SEQ_ADJUST_BIT = 6,    // 需要 TCP 序列号调整
    IPS_SRC_NAT_DONE_BIT = 7,  // 源 NAT 已完成
    IPS_DST_NAT_DONE_BIT = 8,  // 目标 NAT 已完成
    IPS_DYING_BIT = 9,         // 连接正在销毁
    IPS_FIXED_TIMEOUT_BIT = 10,// 固定超时
    IPS_TEMPLATE_BIT = 11,     // 模板连接
    IPS_UNTRACKED_BIT = 12,    // 未跟踪
    IPS_NAT_CLASH_BIT = 12,    // NAT 冲突 (重用)
    IPS_HELPER_BIT = 13,       // 已设置辅助模块
    IPS_OFFLOAD_BIT = 14,      // 已卸载到流表
    IPS_HW_OFFLOAD_BIT = 15,   // 已卸载到硬件
};
```

---

## 3. Hook 机制

### 3.1 Hook 注册

Hook 通过 `nf_register_net_hook()` 注册到内核:

```c
// include/linux/netfilter.h:199
int nf_register_net_hook(struct net *net, const struct nf_hook_ops *ops);
```

内部实现 (`net/netfilter/core.c`):

```c
// net/netfilter/core.c:100-200
static struct nf_hook_entries *
nf_hook_entries_grow(const struct nf_hook_entries *old,
                     const struct nf_hook_ops *reg)
{
    // 1. 分配新的 hook 条目数组
    // 2. 按优先级插入新的 hook
    // 3. 返回更新后的条目集合
}

// 实现代码流程:
static int __nf_register_net_hook(struct net *net, int pf,
                                   unsigned int hooknum,
                                   struct nf_hook_ops *ops)
{
    struct nf_hook_entries **pp;
    // 根据协议族选择正确的 hook 数组
    switch (pf) {
    case NFPROTO_IPV4:
        pp = &net->nf.hooks_ipv4[hooknum];
        break;
    case NFPROTO_IPV6:
        pp = &net->nf.hooks_ipv6[hooknum];
        break;
    // ...
    }
    // 调用 nf_hook_entries_grow 添加 hook
}
```

### 3.2 Hook 调用流程

```c
// include/linux/netfilter.h:227-278
static inline int nf_hook(u_int8_t pf, unsigned int hook, struct net *net,
                          struct sock *sk, struct sk_buff *skb,
                          struct net_device *indev, struct net_device *outdev,
                          int (*okfn)(struct net *, struct sock *, struct sk_buff *))
{
    struct nf_hook_entries *hook_head = NULL;
    int ret = 1;

    // 使用 Jump Label 快速路径 (如果 hook 未注册)
#ifdef CONFIG_JUMP_LABEL
    if (__builtin_constant_p(pf) &&
        __builtin_constant_p(hook) &&
        !static_key_false(&nf_hooks_needed[pf][hook]))
        return 1;
#endif

    rcu_read_lock();
    // 获取对应协议族和 hook 的条目
    switch (pf) {
    case NFPROTO_IPV4:
        hook_head = rcu_dereference(net->nf.hooks_ipv4[hook]);
        break;
    case NFPROTO_IPV6:
        hook_head = rcu_dereference(net->nf.hooks_ipv6[hook]);
        break;
    // ...
    }

    if (hook_head) {
        struct nf_hook_state state;
        nf_hook_state_init(&state, hook, pf, indev, outdev, sk, net, okfn);
        ret = nf_hook_slow(skb, &state, hook_head, 0);
    }
    rcu_read_unlock();

    return ret;
}
```

### 3.3 nf_hook_slow 函数

核心 hook 处理函数 (`net/netfilter/core.c:616-648`):

```c
int nf_hook_slow(struct sk_buff *skb, struct nf_hook_state *state,
                 const struct nf_hook_entries *e, unsigned int s)
{
    unsigned int verdict;
    int ret;

    // 遍历所有注册的 hook 函数
    for (; s < e->num_hook_entries; s++) {
        // 调用单个 hook 函数
        verdict = nf_hook_entry_hookfn(&e->hooks[s], skb, state);

        switch (verdict & NF_VERDICT_MASK) {
        case NF_ACCEPT:
            break;                          // 继续下一个 hook
        case NF_DROP:
            kfree_skb_reason(skb, SKB_DROP_REASON_NETFILTER_DROP);
            ret = NF_DROP_GETERR(verdict);
            if (ret == 0)
                ret = -EPERM;
            return ret;                     // 丢弃数据包
        case NF_QUEUE:
            ret = nf_queue(skb, state, s, verdict);
            if (ret == 1)
                continue;                   // 队列处理后继续
            return ret;
        case NF_STOLEN:
            return NF_DROP_GETERR(verdict); // 数据包被偷走
        default:
            WARN_ON_ONCE(1);
            return 0;
        }
    }

    return 1;  // 所有 hook 都通过,返回 1 表示调用 okfn
}
```

---

## 4. Connection Tracking (连接跟踪)

### 4.1 概述

Connection Tracking (conntrack) 是 Netfilter 的核心组件,用于跟踪网络连接的状态。它使得 NAT 和有状态防火墙成为可能。

### 4.2 连接状态流转

```
                    ┌────────────────────────────────────────────────────────┐
                    │                   连接状态流转                          │
                    └────────────────────────────────────────────────────────┘

    ┌─────────┐     NEW (新建)      ┌─────────────┐
    │  数据包  │ ──────────────────▶│  NEW        │
    │  到达    │                    │  (IP_CT_NEW)│
    └─────────┘                    └──────┬──────┘
                                           │
                                           │ 创建 conntrack 条目
                                           │ 双向tuple哈希
                                           ▼
                                  ┌─────────────────┐
                                  │  双向通信后      │
                                  │  → ESTABLISHED  │
                                  │  (IP_CT_ESTABLISHED)│
                                  └────────┬────────┘
                                           │
                                           │ 特殊协议 (如 FTP)
                                           ▼
                                  ┌─────────────────┐
                                  │  RELATED        │
                                  │  (IP_CT_RELATED)│
                                  └─────────────────┘

    状态判断:
    - NEW:       第一个数据包,创建新跟踪条目
    - ESTABLISHED: 见过双向通信
    - RELATED:   与现有连接相关 (如 FTP 数据连接、ICMP 错误)
    - INVALID:   无法识别的数据包
```

### 4.3 Conntrack 哈希表

连接跟踪使用哈希表存储连接条目 (`net/netfilter/nf_conntrack_core.c`):

```c
// net/netfilter/nf_conntrack_core.c:63
struct hlist_nulls_head *nf_conntrack_hash __read_mostly;
EXPORT_SYMBOL_GPL(nf_conntrack_hash);

// 哈希桶数量
unsigned int nf_conntrack_htable_size;
EXPORT_SYMBOL(nf_conntrack_htable_size);

// 最大连接数
unsigned int nf_conntrack_max;
EXPORT_SYMBOL(nf_conntrack_max);
```

### 4.4 Conntrack 查找

连接跟踪的查找基于 tuple 的哈希值:

```c
// include/net/netfilter/nf_conntrack.h:168-175
static inline struct nf_conn *
nf_ct_get(const struct sk_buff *skb, enum ip_conntrack_info *ctinfo)
{
    unsigned long nfct = skb_get_nfct(skb);
    *ctinfo = nfct & NFCT_INFOMASK;
    return (struct nf_conn *)(nfct & NFCT_PTRMASK);
}
```

### 4.5 Conntrack 生命周期

```
    创建 ──▶ 确认 ──▶ 使用 ──▶ 销毁
      │         │         │
      │         │         └── 双向通信后变为 ASSURED
      │         │
      │         └── 首个数据包确认后
      │
      └── 数据包到达,查找或创建条目
```

---

## 5. iptables

### 5.1 概述

iptables 是传统的 Linux 防火墙工具,使用表 (table)、链 (chain)、规则 (rule) 的三层结构。

### 5.2 表和链

| 表名 | 功能 | 包含的链 |
|------|------|----------|
| **filter** | 数据包过滤 | INPUT, FORWARD, OUTPUT |
| **nat** | 网络地址转换 | PREROUTING, OUTPUT, POSTROUTING |
| **mangle** | 数据包修改 | 所有 5 个基本链 |
| **raw** | 关闭连接跟踪 | PREROUTING, OUTPUT |
| **security** | SELinux 标记 | INPUT, FORWARD, OUTPUT |

### 5.3 struct ipt_entry

规则条目结构 (`include/uapi/linux/netfilter_ipv4/ip_tables.h:106-125`):

```c
struct ipt_entry {
    struct ipt_ip ip;              // IP 匹配条件

    unsigned int nfcache;          // 缓存需求

    __u16 target_offset;           // target 在结构中的偏移
    __u16 next_offset;            // 下一个条目在结构中的偏移

    unsigned int comefrom;         // 回跳链的来源

    struct xt_counters counters;   // 统计数据包/字节计数

    /* matches 和 target 数据 */
    unsigned char elems[];
};
```

### 5.4 ipt_do_table 函数

iptables 规则处理的核心函数 (`net/ipv4/netfilter/ip_tables.c:223-362`):

```c
unsigned int
ipt_do_table(void *priv, struct sk_buff *skb,
             const struct nf_hook_state *state)
{
    const struct xt_table *table = priv;
    unsigned int hook = state->hook;
    const struct iphdr *ip;
    unsigned int verdict = NF_DROP;
    const char *indev, *outdev;
    const void *table_base;
    struct ipt_entry *e, **jumpstack;
    struct xt_action_param acpar;

    // 1. 初始化
    ip = ip_hdr(skb);
    indev = state->in ? state->in->name : nulldevname;
    outdev = state->out ? state->out->name : nullderdevname;

    acpar.fragoff = ntohs(ip->frag_off) & IP_OFFSET;
    acpar.thoff   = ip_hdrlen(skb);
    acpar.hotdrop = false;
    acpar.state   = state;

    local_bh_disable();
    addend = xt_write_recseq_begin();
    private = READ_ONCE(table->private);
    cpu = smp_processor_id();
    table_base = private->entries;
    jumpstack = private->jumpstack[cpu];

    // 2. 从 hook 入口点开始遍历
    e = get_entry(table_base, private->hook_entry[hook]);

    do {
        // 3. 匹配 IP 头部
        if (!ip_packet_match(ip, indev, outdev, &e->ip, acpar.fragoff)) {
 no_match:
            e = ipt_next_entry(e);
            continue;
        }

        // 4. 遍历所有 match 扩展
        xt_ematch_foreach(ematch, e) {
            acpar.match = ematch->u.kernel.match;
            acpar.matchinfo = ematch->data;
            if (!acpar.match->match(skb, &acpar))
                goto no_match;
        }

        // 5. 更新计数器
        counter = xt_get_this_cpu_counter(&e->counters);
        ADD_COUNTER(*counter, skb->len, 1);

        // 6. 获取 target
        t = ipt_get_target_c(e);

        // 7. 标准 target (verdict)
        if (!t->u.kernel.target->target) {
            v = ((struct xt_standard_target *)t)->verdict;
            if (v < 0) {
                if (v != XT_RETURN) {
                    verdict = (unsigned int)(-v) - 1;
                    break;
                }
                // 处理返回
                if (stackidx == 0) {
                    e = get_entry(table_base, private->underflow[hook]);
                } else {
                    e = jumpstack[--stackidx];
                    e = ipt_next_entry(e);
                }
                continue;
            }
            // 跳转到指定规则
            if (table_base + v != ipt_next_entry(e) &&
                !(e->ip.flags & IPT_F_GOTO)) {
                if (stackidx >= private->stacksize) {
                    verdict = NF_DROP;
                    break;
                }
                jumpstack[stackidx++] = e;
            }
            e = get_entry(table_base, v);
            continue;
        }

        // 8. 调用 target
        acpar.target = t->u.kernel.target;
        acpar.targinfo = t->data;
        verdict = t->u.kernel.target->target(skb, &acpar);

        if (verdict == XT_CONTINUE) {
            ip = ip_hdr(skb);  // target 可能修改了 skb
            e = ipt_next_entry(e);
        } else {
            break;
        }
    } while (!acpar.hotdrop);

    xt_write_recseq_end(addend);
    local_bh_enable();

    return acpar.hotdrop ? NF_DROP : verdict;
}
```

### 5.5 数据包匹配

IP 头部匹配函数 (`net/ipv4/netfilter/ip_tables.c:42-79`):

```c
static inline bool
ip_packet_match(const struct iphdr *ip,
                const char *indev, const char *outdev,
                const struct ipt_ip *ipinfo,
                int isfrag)
{
    // 1. 源/目标 IP 地址匹配
    if (NF_INVF(ipinfo, IPT_INV_SRCIP,
                (ip->saddr & ipinfo->smsk.s_addr) != ipinfo->src.s_addr) ||
        NF_INVF(ipinfo, IPT_INV_DSTIP,
                (ip->daddr & ipinfo->dmsk.s_addr) != ipinfo->dst.s_addr))
        return false;

    // 2. 输入/输出接口匹配
    if (ifname_compare_aligned(indev, ipinfo->iniface, ipinfo->iniface_mask) != 0 &&
        NF_INVF(ipinfo, IPT_INV_VIA_IN, true))
        return false;

    if (ifname_compare_aligned(outdev, ipinfo->outiface, ipinfo->outiface_mask) != 0 &&
        NF_INVF(ipinfo, IPT_INV_VIA_OUT, true))
        return false;

    // 3. 协议匹配
    if (ipinfo->proto &&
        NF_INVF(ipinfo, IPT_INV_PROTO, ip->protocol != ipinfo->proto))
        return false;

    // 4. 片段匹配
    if (NF_INVF(ipinfo, IPT_INV_FRAG,
                (ipinfo->flags & IPT_F_FRAG) && !isfrag))
        return false;

    return true;
}
```

---

## 6. nftables

### 6.1 概述

nftables 是新一代的包过滤框架,于 Linux 3.13 引入,旨在替代 iptables。它使用更灵活的表达式 (expression) 机制,而不是 iptables 的 match/target 扩展。

### 6.2 架构

```
    ┌─────────────────────────────────────────────────────────────────┐
    │                         nftables 架构                           │
    └─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  用户空间     │  libnftnl / nft tool
    └──────┬───────┘
           │ netlink
           ▼
    ┌──────────────┐
    │ nf_tables_api│  内核 netlink 接口
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────┐
    │                   Table (表)                         │
    │  ┌─────────────────────────────────────────────┐   │
    │  │              Chain (链)                       │   │
    │  │  ┌─────────────────────────────────────┐    │   │
    │  │  │         Rule (规则)                  │    │   │
    │  │  │  ┌─────────┐ ┌─────────┐ ┌───────┐  │    │   │
    │  │  │  │  Expr   │ │  Expr   │ │ Expr  │  │    │   │
    │  │  │  └─────────┘ └─────────┘ └───────┘  │    │   │
    │  │  └─────────────────────────────────────┘    │   │
    │  └─────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘
```

### 6.3 核心结构

#### nft_chain

```c
struct nft_chain {
    struct list_head        list;        // 链表链接
    struct rhlist_node      rhlnode;     // 哈希链表节点
    struct nft_table        *table;      // 所属表
    struct nft_base_chain   *basechain;   // 基础链
    u8                      padding;      // 填充
    u32                     handle;       // 句柄
    u32                     use;          // 引用计数
    char                     *name;       // 链名
    struct nft_rule_dp      __rcu *rules[];  // 规则数组
};
```

#### nft_base_chain

基础链,绑定到 Netfilter hook:

```c
struct nft_base_chain {
    struct nf_hook_ops      ops;          // Netfilter hook 操作
    struct nf_hook_entries  __rcu *rules;  // 规则条目
    u32                     policy;       // 策略 (ACCEPT/DROP)
    struct list_head        cb_list;      // 回调列表
    struct rcu_head         rcu;           // RCU 头
};
```

### 6.4 nft_do_chain 函数

nftables 规则处理核心 (`net/netfilter/nf_tables_core.c:250-347`):

```c
unsigned int
nft_do_chain(struct nft_pktinfo *pkt, void *priv)
{
    const struct nft_chain *chain = priv, *basechain = chain;
    const struct net *net = nft_net(pkt);
    const struct nft_expr *expr, *last;
    const struct nft_rule_dp *rule;
    struct nft_regs regs;
    unsigned int stackptr = 0;
    struct nft_jumpstack jumpstack[NFT_JUMP_STACK_SIZE];
    bool genbit = READ_ONCE(net->nft.gencursor);
    struct nft_rule_blob *blob;
    struct nft_traceinfo info;

    info.trace = false;
    if (static_branch_unlikely(&nft_trace_enabled))
        nft_trace_init(&info, pkt, basechain);

do_chain:
    // 获取当前代的规则 blob
    if (genbit)
        blob = rcu_dereference(chain->blob_gen_1);
    else
        blob = rcu_dereference(chain->blob_gen_0);

    rule = (struct nft_rule_dp *)blob->data;

next_rule:
    regs.verdict.code = NFT_CONTINUE;

    // 遍历规则中的表达式
    for (; !rule->is_last; rule = nft_rule_next(rule)) {
        nft_rule_dp_for_each_expr(expr, last, rule) {
            // 快速路径: 内联比较操作
            if (expr->ops == &nft_cmp_fast_ops)
                nft_cmp_fast_eval(expr, &regs);
            else if (expr->ops == &nft_cmp16_fast_ops)
                nft_cmp16_fast_eval(expr, &regs);
            else if (expr->ops == &nft_bitwise_fast_ops)
                nft_bitwise_fast_eval(expr, &regs);
            else if (expr->ops != &nft_payload_fast_ops ||
                     !nft_payload_fast_eval(expr, &regs, pkt))
                expr_call_ops_eval(expr, &regs, pkt);

            // 非 NFT_CONTINUE 时停止
            if (regs.verdict.code != NFT_CONTINUE)
                break;
        }

        switch (regs.verdict.code) {
        case NFT_BREAK:
            regs.verdict.code = NFT_CONTINUE;
            nft_trace_copy_nftrace(pkt, &info);
            continue;
        case NFT_CONTINUE:
            nft_trace_packet(pkt, &regs.verdict, &info, rule, NFT_TRACETYPE_RULE);
            continue;
        }
        break;
    }

    nft_trace_verdict(pkt, &info, rule, &regs);

    // 处理 verdict
    switch (regs.verdict.code & NF_VERDICT_MASK) {
    case NF_ACCEPT:
    case NF_QUEUE:
    case NF_STOLEN:
        return regs.verdict.code;
    case NF_DROP:
        return NF_DROP_REASON(pkt->skb, SKB_DROP_REASON_NETFILTER_DROP, EPERM);
    }

    switch (regs.verdict.code) {
    case NFT_JUMP:
        if (WARN_ON_ONCE(stackptr >= NFT_JUMP_STACK_SIZE))
            return NF_DROP;
        jumpstack[stackptr].rule = nft_rule_next(rule);
        stackptr++;
        fallthrough;
    case NFT_GOTO:
        chain = regs.verdict.chain;  // 直接切换到目标链
        goto do_chain;
    case NFT_CONTINUE:
    case NFT_RETURN:
        break;
    default:
        WARN_ON_ONCE(1);
    }

    // 从跳转栈弹出
    if (stackptr > 0) {
        stackptr--;
        rule = jumpstack[stackptr].rule;
        goto next_rule;
    }

    nft_trace_packet(pkt, &regs.verdict, &info, NULL, NFT_TRACETYPE_POLICY);

    // 链策略
    if (nft_base_chain(basechain)->policy == NF_DROP)
        return NF_DROP_REASON(pkt->skb, SKB_DROP_REASON_NETFILTER_DROP, EPERM);

    return nft_base_chain(basechain)->policy;
}
```

### 6.5 nftables Verdict

nftables 内部 verdict 定义 (`include/uapi/linux/nf_tables.h:64-70`):

```c
enum nft_verdicts {
    NFT_CONTINUE   = -1,   // 继续下一条规则
    NFT_BREAK      = -2,   // 停止当前规则,继续链中下一条规则
    NFT_JUMP       = -3,   // 跳转到指定链,压栈
    NFT_GOTO       = -4,   // 跳转到指定链,不压栈
    NFT_RETURN     = -5,   // 从当前链返回
};
```

### 6.6 nftables 表达式类型

| 表达式 | 功能 |
|--------|------|
| **nft_cmp** | 比较操作 (=, !=, <, >, etc.) |
| **nft_payload** | 提取数据包载荷 |
| **nft_meta** | 获取元数据 (mark, iif, oif, etc.) |
| **nft_ct** | 连接跟踪信息 |
| **nft_lookup** | 集合查找 |
| **nft_bitwise** | 位操作 |
| **nft_byteorder** | 字节序转换 |
| **nft_limit** | 速率限制 |
| **nft_counter** | 计数器 |
| **nft_nat** | NAT 操作 |
| **nft_log** | 日志记录 |
| **nft_reject** | 拒绝数据包 |

---

## 7. Xtables 框架

### 7.1 概述

Xtables 是 iptables/ip6tables/arptables 的通用框架,提供表注册、规则管理等公共功能。

### 7.2 xt_register_table

表注册函数 (`net/netfilter/x_tables.c:1475-1523`):

```c
struct xt_table *xt_register_table(struct net *net,
                                   const struct xt_table *input_table,
                                   struct xt_table_info *bootstrap,
                                   struct xt_table_info *newinfo)
{
    struct xt_pernet *xt_net = net_generic(net, xt_pernet_id);
    struct xt_table_info *private;
    struct xt_table *t, *table;
    int ret;

    // 分配表结构
    table = kmemdup(input_table, sizeof(struct xt_table), GFP_KERNEL);

    mutex_lock(&xt[table->af].mutex);

    // 检查表名是否已存在
    list_for_each_entry(t, &xt_net->tables[table->af], list) {
        if (strcmp(t->name, table->name) == 0) {
            ret = -EEXIST;
            goto unlock;
        }
    }

    // 设置初始表信息
    table->private = bootstrap;

    // 替换为新表
    if (!xt_replace_table(table, 0, newinfo, &ret))
        goto unlock;

    private = table->private;
    private->initial_entries = private->number;

    // 添加到表链表
    list_add(&table->list, &xt_net->tables[table->af]);
    mutex_unlock(&xt[table->af].mutex);

    return table;

unlock:
    mutex_unlock(&xt[table->af].mutex);
    kfree(table);
    return ERR_PTR(ret);
}
```

### 7.3 xt_entry_match

Match 扩展结构 (`include/uapi/linux/netfilter/x_tables.h:11-32`):

```c
struct xt_entry_match {
    union {
        struct {
            __u16 match_size;
            char name[XT_EXTENSION_MAXNAMELEN];  // "tcp", "udp", etc.
            __u8 revision;
        } user;
        struct {
            __u16 match_size;
            struct xt_match *match;  // 内核指针
        } kernel;
        __u16 match_size;
    } u;

    unsigned char data[];  // match 特定数据
};
```

### 7.4 xt_entry_target

Target 扩展结构 (`include/uapi/linux/netfilter/x_tables.h:34-55`):

```c
struct xt_entry_target {
    union {
        struct {
            __u16 target_size;
            char name[XT_EXTENSION_MAXNAMELEN];  // "DROP", "ACCEPT", etc.
            __u8 revision;
        } user;
        struct {
            __u16 target_size;
            struct xt_target *target;  // 内核指针
        } kernel;
        __u16 target_size;
    } u;

    unsigned char data[0];  // target 特定数据
};
```

### 7.5 xt_standard_target

标准 target,用于内置 verdict (`include/uapi/linux/netfilter/x_tables.h:65-68`):

```c
struct xt_standard_target {
    struct xt_entry_target target;
    int verdict;  // 负数表示 verdict,正数表示规则偏移
};
```

### 7.6 Verdict 编码

```c
// 标准 verdict
NF_ACCEPT = 1
NF_DROP = 0
XT_CONTINUE = 0xFFFFFFFF  // 继续匹配下一规则

// 标准 target verdict (负数)
#define XT_RETURN (-NF_REPEAT - 1)  // = -5, 从当前链返回

// 跳转到规则
verdict > 0: 跳转到 table + verdict 位置的规则
```

---

## 8. 数据包处理流程

### 8.1 IPv4 数据包入口流程

```
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    IPv4 数据包处理完整流程                          │
    └─────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │ 网络设备 │
    │ 接收    │
    └────┬────┘
         │
         ▼
    ┌───────────────────┐
    │ NAPI poll / 软中断 │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ netif_receive_skb │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                      NF_INET_INGRESS (Netdev Hook)               │
    │                    (可选, CONFIG_NET_NETFILTER)                   │
    └───────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                    ip_rcv / ip_rcv_core                          │
    └───────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │              NF_INET_PRE_ROUTING (PREROUTING Hook)                │
    │                                                                       │
    │  ┌──────────────┐                                                   │
    │  │ conntrack   │ ───▶ NEW ──▶ 创建 conntrack 条目                   │
    │  │ (连接跟踪)  │ ───▶ ESTABLISHED/RELATED ───▶ 查找已有条目          │
    │  └──────────────┘                                                   │
    │                                                                       │
    │  ┌──────────────┐                                                   │
    │  │    nat      │ ───▶ DNAT (目标地址转换)                           │
    │  │  (PREROUTING)│                                                    │
    │  └──────────────┘                                                   │
    └───────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  路由判决 (路由表) │
    │  fib_lookup       │
    └─────────┬─────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
    ┌─────────┐  ┌───────────────┐
    │  本机   │  │    转发       │
    │ LOCAL_IN│  │  FORWARD      │
    └────┬────┘  └───────┬───────┘
         │               │
         ▼               ▼
    ┌─────────────┐  ┌───────────────────────────────────────────────────┐
    │  NF_INET    │  │               NF_INET_FORWARD                      │
    │  _LOCAL_IN  │  │                                                   │
    │             │  │  ┌─────────────┐   ┌─────────────┐                 │
    │  mangle     │  │  │  filter    │   │   mangle    │                 │
    │  (INPUT)    │  │  │  (FORWARD) │   │  (FORWARD)  │                 │
    │             │  │  └─────────────┘   └─────────────┘                 │
    └──────┬──────┘  └───────┬───────┘
           │                 │
           ▼                 ▼
    ┌─────────────┐  ┌───────────────────────────────────────────────────┐
    │  ip_local_deliver │      │             NF_INET_POST_ROUTING           │
    │       │           │      │  (POSTROUTING Hook)                       │
    └───────┼───────────┘      │                                          │
            │                  │  ┌─────────────┐  ┌─────────────┐         │
            ▼                  │  │    nat     │  │  mangle     │         │
    ┌───────────────────┐       │  │(POSTROUTING)│  │  (mangle)   │         │
    │  传输层处理       │       │  └─────────────┘  └─────────────┘         │
    │  (TCP/UDP/ICMP)  │       └──────────────────────────────────────────┘
    └───────────────────┘                          │
                                                     ▼
                                              ┌─────────────┐
                                              │  设备输出   │
                                              │ ip_finish_output │
                                              └─────────────┘
```

### 8.2 本机发出数据包流程

```
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    本机发出数据包处理流程                            │
    └─────────────────────────────────────────────────────────────────────┘

    ┌───────────────────┐
    │  应用层 send()    │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  传输层           │
    │  tcp_sendmsg etc. │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │              NF_INET_LOCAL_OUT (OUTPUT Hook)                       │
    │                                                                       │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
    │  │    raw      │  │   conntrack  │  │    nat      │              │
    │  │  (OUTPUT)   │  │  (OUTPUT)    │  │  (OUTPUT)   │              │
    │  └──────────────┘  └──────────────┘  └──────────────┘              │
    │                                                                       │
    │  ┌──────────────┐  ┌──────────────┐                                │
    │  │   mangle     │  │   filter     │                                │
    │  │  (OUTPUT)    │  │  (OUTPUT)    │                                │
    │  └──────────────┘  └──────────────┘                                │
    └───────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  路由判决         │
    │  ip_route_output  │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │              NF_INET_POST_ROUTING (POSTROUTING Hook)               │
    │                                                                       │
    │  ┌──────────────┐  ┌──────────────┐                               │
    │  │    nat       │  │   mangle     │                               │
    │  │(POSTROUTING) │  │  (mangle)    │                               │
    │  │ (SNAT/MASQ) │  └──────────────┘                               │
    │  └──────────────┘                                                 │
    └───────────────────────────────────────────────────────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  设备输出         │
    │ dev_queue_xmit    │
    └───────────────────┘
```

---

## 9. 关键代码索引

### 9.1 核心文件

| 文件 | 功能 |
|------|------|
| `net/netfilter/core.c` | Netfilter 核心: Hook 注册/调用 |
| `net/netfilter/nf_conntrack_core.c` | 连接跟踪核心实现 |
| `net/ipv4/netfilter/ip_tables.c` | iptables 主处理 (ipt_do_table) |
| `net/ipv6/netfilter/ip6_tables.c` | ip6tables 主处理 |
| `net/netfilter/x_tables.c` | Xtables 框架 |
| `net/netfilter/nf_tables_api.c` | nftables netlink API |
| `net/netfilter/nf_tables_core.c` | nftables 核心处理 (nft_do_chain) |

### 9.2 关键头文件

| 文件 | 内容 |
|------|------|
| `include/linux/netfilter.h` | 核心 netfilter 结构 |
| `include/uapi/linux/netfilter.h` | 用户空间 API (HOOK/Verdict 定义) |
| `include/uapi/linux/netfilter/x_tables.h` | Xtables 通用结构 |
| `include/uapi/linux/netfilter_ipv4/ip_tables.h` | iptables 结构 |
| `include/net/netfilter/nf_conntrack.h` | 连接跟踪结构 |
| `include/net/netfilter/nf_conntrack_tuple.h` | Tuple 结构 |
| `include/uapi/linux/nf_tables.h` | nftables 用户空间 API |

### 9.3 Hook 调用位置

| 协议 | 文件 | Hook 点 |
|------|------|---------|
| IPv4 | `net/ipv4/ip_input.c` | ip_rcv 后 NF_INET_PRE_ROUTING |
| IPv4 | `net/ipv4/ip_input.c` | NF_INET_LOCAL_IN (路由后) |
| IPv4 | `net/ipv4/ip_forward.c` | NF_INET_FORWARD |
| IPv4 | `net/ipv4/ip_output.c` | NF_INET_LOCAL_OUT |
| IPv4 | `net/ipv4/ip_output.c` | NF_INET_POST_ROUTING |
| IPv6 | `net/ipv6/ip6_input.c` | NF_INET_PRE_ROUTING |
| IPv6 | `net/ipv6/ip6_input.c` | NF_INET_LOCAL_IN |
| IPv6 | `net/ipv6/ip6_forward.c` | NF_INET_FORWARD |
| IPv6 | `net/ipv6/ip6_output.c` | NF_INET_LOCAL_OUT |
| IPv6 | `net/ipv6/ip6_output.c` | NF_INET_POST_ROUTING |

---

## 附录 A: 常用命令参考

### A.1 iptables 命令

```bash
# 列出规则
iptables -L -n -v

# 添加规则
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 删除规则
iptables -D INPUT -p tcp --dport 22 -j ACCEPT

# NAT 表规则
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -j MASQUERADE
```

### A.2 nftables 命令

```bash
# 列出规则
nft list ruleset

# 添加表
nft add table ip filter

# 添加链
nft add chain ip filter input { type filter hook input priority 0 \; }

# 添加规则
nft add rule ip filter input tcp dport 22 accept

# NAT 规则
nft add rule ip nat postrouting meta oifname eth0 masquerade
```

### A.3 conntrack 命令

```bash
# 查看连接跟踪表
conntrack -L

# 查看特定连接
conntrack -L -p tcp --dport 22

# 删除连接
conntrack -D -p tcp --dport 22
```

---

## 附录 B: 调试接口

### B.1 Proc 文件系统

```
/proc/net/nf_conntrack       - 连接跟踪表
/proc/net/ip_tables_names    - 已注册的 iptables 表
/proc/net/ip6_tables_names   - 已注册的 ip6tables 表
/proc/sys/net/netfilter/nf_conntrack_max  - 最大连接数
/proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established - TCP 超时
```

### B.2 Netlink 接口

- **conntrack netlink**: `/proc/net/netfilter/nfnetlink_queue`
- **netfilter netlink**: `/proc/net/netfilter/nfnetlink`

---

*文档版本: 1.0*
*生成日期: 2026-04-26*
*内核版本: Linux Kernel Mainline (基于 master 分支)*
