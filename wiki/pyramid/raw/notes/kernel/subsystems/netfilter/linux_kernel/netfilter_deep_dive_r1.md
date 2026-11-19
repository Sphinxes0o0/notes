# Linux 内核 Netfilter 子系统深度分析

## 第一轮分析报告

---

## 目录

1. [概述](#1-概述)
2. [Connection Tracking 核心](#2-connection-tracking-核心)
3. [NAT (网络地址转换)](#3-nat-网络地址转换)
4. [Conntrack 协议支持](#4-conntrack-协议支持)
5. [Nftables 表达式](#5-nftables-表达式)
6. [Xtables 匹配/目标](#6-xtables-匹配目标)
7. [性能优化](#7-性能优化)

---

## 1. 概述

Netfilter 是 Linux 内核提供的一个数据包过滤和修改框架,位于网络堆栈的关键路径上。它通过在协议栈的多个位置插入"钩子"(hooks)来实现对数据包的处理。

### 1.1 核心组件

| 组件 | 路径 | 功能 |
|------|------|------|
| nf_conntrack | net/netfilter/nf_conntrack*.c | 连接跟踪 |
| nf_nat | net/netfilter/nf_nat*.c | 网络地址转换 |
| nftables | net/netfilter/nft*.c | 新一代规则引擎 |
| xtables | net/netfilter/xt_*.c | 传统 iptables 兼容层 |

### 1.2 Netfilter 钩子点

```
                                    NF_INET_POST_ROUTING
                                    ^
                                    |
+------------+    +--------+    +------+    +------+    +-----------+    +------------+
| NF_INET_   | -> |  Routing | -> | PREROUTING | -> | FORWARD | -> | POSTROUTING| -> |
| LOCAL_OUT  |    +--------+    +------+     |    +------+    +-----------+    |
+------------+                             |                              |
                                          v                              v
                                    +-------------+              +----------------+
                                    | NF_INET_   |              | NF_INET_       |
                                    | LOCAL_IN    |              | POST_ROUTING   |
                                    +-------------+              +----------------+
```

---

## 2. Connection Tracking 核心

### 2.1 struct nf_conn 完整结构

**位置**: `include/net/netfilter/nf_conntrack.h:74-125`

```c
struct nf_conn {
    /* 引用计数: 1=在哈希表中, 1=每个关联的skb, 1=作为master的连接 */
    struct nf_conntrack ct_general;     // 第85行

    spinlock_t lock;                    // 第87行: 保护协议特定状态
    u32 timeout;                       // 第89行: jiffies32,超时时间

#ifdef CONFIG_NF_CONNTRACK_ZONES
    struct nf_conntrack_zone zone;      // 第92行: 连接跟踪区域
#endif

    /* 原始方向和回复方向的元组哈希 */
    struct nf_conntrack_tuple_hash tuplehash[IP_CT_DIR_MAX];  // 第96行

    unsigned long status;               // 第99行: 连接状态位图

    possible_net_t ct_net;              // 第101行: 所属网络命名空间

#if IS_ENABLED(CONFIG_NF_NAT)
    struct hlist_node nat_bysource;    // 第104行: NAT按源哈希
#endif

    /* 期望连接的主连接 */
    struct nf_conn *master;            // 第110行

#if defined(CONFIG_NF_CONNTRACK_MARK)
    u_int32_t mark;                    // 第113行: 连接标记
#endif

#ifdef CONFIG_NF_CONNTRACK_SECMARK
    u_int32_t secmark;                 // 第117行: 安全标记
#endif

    struct nf_ct_ext *ext;             // 第121行: 扩展属性

    /* 协议特定数据,必须是最后一个成员 */
    union nf_conntrack_proto proto;     // 第124行
};
```

### 2.2 struct nf_conntrack_tuple 元组结构

**位置**: `include/net/netfilter/nf_conntrack_tuple.h`

```c
struct nf_conntrack_tuple {
    /* 源地址信息 */
    struct nf_conntrack_man {
        union nf_inet_addr {
            __be32 ip;          // IPv4 地址
            struct in6_addr in6; // IPv6 地址
            __u32 all[8];       // 通用数组
        } u3;
        u16 l3num;               // 第三层协议号 (AF_INET=2, AF_INET6=10)
        union nf_conntrack_man_proto {
            __be16 all;
            struct { __be16 port; } tcp;
            struct { __be16 port; } udp;
            struct { __be16 id; } icmp;
            struct { __be16 port; } dccp;
            struct { __be16 port; } sctp;
            struct { __be16 key; } gre;
        } u;
    } src;

    /* 目标信息 */
    struct {
        union nf_inet_addr u3;
        u16 l3num;
        union nf_conntrack_man_proto u;
        u8 protonum;              // 第四层协议号 (IPPROTO_TCP=6, UDP=17)
        u8 dir;                   // 方向: IP_CT_DIR_ORIGINAL 或 IP_CT_DIR_REPLY
    } dst;
};
```

### 2.3 nf_conntrack_hash 哈希表分析

**位置**: `net/netfilter/nf_conntrack_core.c:63`

```c
struct hlist_nulls_head *nf_conntrack_hash __read_mostly;
EXPORT_SYMBOL_GPL(nf_conntrack_hash);
```

**哈希计算** (第210-246行):

```c
static u32 hash_conntrack_raw(const struct nf_conntrack_tuple *tuple,
                              unsigned int zoneid,
                              const struct net *net)
{
    siphash_key_t key;
    get_random_once(&nf_conntrack_hash_rnd, sizeof(nf_conntrack_hash_rnd));

    key = nf_conntrack_hash_rnd;
    key.key[0] ^= zoneid;           // 混入zone ID
    key.key[1] ^= net_hash_mix(net); // 混入网络命名空间

    return siphash((void *)tuple,
            offsetofend(struct nf_conntrack_tuple, dst.__nfct_hash_offsetend),
            &key);
}
```

**哈希表大小计算** (第2631-2669行):
- 默认: `nr_pages * PAGE_SIZE / 16384 / sizeof(struct hlist_head)`
- 大于4GB内存: 262144 桶
- 大于1GB内存: 65536 桶
- 最小: 1024 桶
- 最大因子: 1 (保持平均哈希链长为2)

### 2.4 连接跟踪状态机

**位置**: `include/uapi/linux/netfilter/nf_conntrack_common.h:7-35`

```c
enum ip_conntrack_info {
    IP_CT_ESTABLISHED,        // 0: 已建立连接(任意方向)
    IP_CT_RELATED,            // 1: 相关连接(ICMP错误或期望连接)
    IP_CT_NEW,                // 2: 新连接(仅原始方向)
    IP_CT_IS_REPLY,           // 3: 标志,表示回复方向

    // 组合值:
    IP_CT_ESTABLISHED_REPLY = IP_CT_ESTABLISHED + IP_CT_IS_REPLY,  // 4
    IP_CT_RELATED_REPLY = IP_CT_RELATED + IP_CT_IS_REPLY,          // 5
    IP_CT_UNTRACKED = 7,   // 绕过跟踪
};
```

**连接状态位** (第42-130行):

```c
enum ip_conntrack_status {
    IPS_EXPECTED_BIT = 0,       // 期望连接
    IPS_SEEN_REPLY_BIT = 1,     // 已见回复
    IPS_ASSURED_BIT = 2,        // 已确认(不会早期删除)
    IPS_CONFIRMED_BIT = 3,      // 已确认(已离开本机)
    IPS_SRC_NAT_BIT = 4,        // 源NAT需要
    IPS_DST_NAT_BIT = 5,        // 目标NAT需要
    IPS_SEQ_ADJUST_BIT = 6,     // TCP序列号调整
    IPS_SRC_NAT_DONE_BIT = 7,   // 源NAT已完成
    IPS_DST_NAT_DONE_BIT = 8,   // 目标NAT已完成
    IPS_DYING_BIT = 9,          // 正在删除
    IPS_FIXED_TIMEOUT_BIT = 10, // 固定超时
    IPS_TEMPLATE_BIT = 11,      // 模板(用于helper)
    IPS_OFFLOAD_BIT = 14,       // 已卸载到flow table
    IPS_HW_OFFLOAD_BIT = 15,    // 已卸载到硬件
};
```

### 2.5 期望连接 (Expectation)

**位置**: `include/net/netfilter/nf_conntrack_expect.h:29-50`

```c
struct nf_conntrack_expect {
    struct nf_conntrack_tuple tuple;     // 期望的元组
    struct nf_conntrack_tuple_mask mask; // 掩码(用于通配符匹配)
    struct nf_conntrack_zone zone;
    refcount_t use;
    unsigned int flags;
    unsigned int class;

    /* 期望建立后的回调函数 */
    void (*expectfn)(struct nf_conn *new,
                      struct nf_conntrack_expect *this);

    struct nf_conntrack_helper __rcu *helper;
    struct net *net;
    struct rcu_head rcu;
    struct timer_list timeout;
    struct hlist_node hnode;  // 全局期望哈希
    struct hlist_node lnode;  // master连接的期望列表
    struct nf_conn *master;   // 主连接
};
```

**期望标志**:
- `NF_CT_EXPECT_PERMANENT`: 永久期望
- `NF_CT_EXPECT_INACTIVE`: 非活跃
- `NF_CT_EXPECT_USERSPACE`: 用户空间helper

---

## 3. NAT (网络地址转换)

### 3.1 NAT 转换类型

**位置**: `include/uapi/linux/netfilter/nf_nat.h`

```c
/* NAT Range 标志 */
#define NF_NAT_RANGE_MAP_IPS         (1 << 0)  // IP映射
#define NF_NAT_RANGE_PROTO_SPECIFIED  (1 << 1)  // 协议指定
#define NF_NAT_RANGE_PROTO_RANDOM     (1 << 2)  // 随机端口
#define NF_NAT_RANGE_PERSISTENT       (1 << 3)  // 持久映射
#define NF_NAT_RANGE_PROTO_RANDOM_FULLY (1 << 4) // 完全随机
#define NF_NAT_RANGE_PROTO_OFFSET    (1 << 5)  // 端口偏移
#define NF_NAT_RANGE_NETMAP          (1 << 6)  // 1:1 NAT
```

### 3.2 struct nf_nat_range2 完整结构

**位置**: `include/uapi/linux/netfilter/nf_nat.h:46-53`

```c
struct nf_nat_range2 {
    unsigned int flags;                    // 转换类型标志
    union nf_inet_addr min_addr;           // 最小地址
    union nf_inet_addr max_addr;           // 最大地址
    union nf_conntrack_man_proto min_proto; // 最小协议(port)
    union nf_conntrack_man_proto max_proto; // 最大协议(port)
    union nf_conntrack_man_proto base_proto; // 基础协议(用于偏移)
};
```

### 3.3 NAT 钩子流程

**位置**: `net/netfilter/nf_nat_core.c:866-891`

```c
unsigned int nf_nat_packet(struct nf_conn *ct,
                          enum ip_conntrack_info ctinfo,
                          unsigned int hooknum,
                          struct sk_buff *skb)
{
    enum nf_nat_manip_type mtype = HOOK2MANIP(hooknum);  // 第871行
    enum ip_conntrack_dir dir = CTINFO2DIR(ctinfo);
    unsigned long statusbit;

    // 确定NAT操作类型和状态位
    if (mtype == NF_NAT_MANIP_SRC)
        statusbit = IPS_SRC_NAT;
    else
        statusbit = IPS_DST_NAT;

    // 回复方向时反转状态位
    if (dir == IP_CT_DIR_REPLY)
        statusbit ^= IPS_NAT_MASK;

    // 执行NAT转换
    if (ct->status & statusbit)
        verdict = nf_nat_manip_pkt(skb, ct, mtype, dir);

    return verdict;
}
```

**Hooknum到NAT类型映射** (`HOOK2MANIP`):
- `NF_INET_PRE_ROUTING`: `NF_NAT_MANIP_DST` (目标NAT)
- `NF_INET_LOCAL_OUT`: `NF_NAT_MANIP_DST` (目标NAT)
- `NF_INET_POST_ROUTING`: `NF_NAT_MANIP_SRC` (源NAT)

### 3.4 NAT 唯一元组查找

**位置**: `net/netfilter/nf_nat_core.c:570-686`

```c
static void nf_nat_l4proto_unique_tuple(struct nf_conntrack_tuple *tuple,
                const struct nf_nat_range2 *range,
                enum nf_nat_manip_type maniptype,
                const struct nf_conn *ct)
{
    // 端口范围选择:
    // - 未指定范围: 优先使用 >1024 的端口
    // - 指定范围: 使用指定范围
    // - 冲突时: 使用 get_random_u16() 随机选择

    // 重试逻辑 (第674-685行):
    // 1. 尝试从当前偏移开始遍历
    // 2. 如果失败,减半搜索窗口
    // 3. 最多次尝试 NF_NAT_MAX_ATTEMPTS (128) 次
}
```

### 3.5 NAT 钩子函数

**位置**: `net/netfilter/nf_nat_core.c:903-976`

```c
unsigned int nf_nat_inet_fn(void *priv, struct sk_buff *skb,
                            const struct nf_hook_state *state)
{
    struct nf_conn *ct;
    enum ip_conntrack_info ctinfo;
    struct nf_conn_nat *nat;
    enum nf_nat_manip_type maniptype = HOOK2MANIP(state->hook);

    ct = nf_ct_get(skb, &ctinfo);
    if (!ct)
        return NF_ACCEPT;

    nat = nfct_nat(ct);

    switch (ctinfo) {
    case IP_CT_RELATED:
    case IP_CT_RELATED_REPLY:
    case IP_CT_NEW:
        // 新连接或相关连接
        if (!nf_nat_initialized(ct, maniptype)) {
            // 调用NAT hook查找规则
            // 如果没有规则,分配null binding
        }
        break;
    default:
        // ESTABLISHED: 直接执行NAT
        break;
    }

do_nat:
    return nf_nat_packet(ct, ctinfo, state->hook, skb);
}
```

---

## 4. Conntrack 协议支持

### 4.1 TCP 状态机

**位置**: `net/netfilter/nf_conntrack_proto_tcp.c:37-48`

```c
static const char *const tcp_conntrack_names[] = {
    "NONE",        // 0: 初始状态
    "SYN_SENT",    // 1: SYN已发送
    "SYN_RECV",    // 2: SYN-ACK已接收
    "ESTABLISHED", // 3: 已建立
    "FIN_WAIT",    // 4: FIN等待
    "CLOSE_WAIT",  // 5: 关闭等待
    "LAST_ACK",    // 6: 最后ACK
    "TIME_WAIT",   // 7: 时间等待
    "CLOSE",       // 8: 关闭
    "SYN_SENT2",   // 9: 双重打开
};
```

**TCP超时配置** (第61-76行):

| 状态 | 超时 |
|------|------|
| SYN_SENT | 2分钟 |
| SYN_RECV | 60秒 |
| ESTABLISHED | 5天 |
| FIN_WAIT | 2分钟 |
| CLOSE_WAIT | 60秒 |
| LAST_ACK | 30秒 |
| TIME_WAIT | 2分钟 |
| CLOSE | 10秒 |
| SYN_SENT2 | 2分钟 |
| RETRANS | 5分钟 |
| UNACK | 5分钟 |

**TCP连接跟踪状态转换表** (第134-262行):

```
原始方向 (tcp_conntracks[0]):
- SYN: NONE->SYN_SENT, SYN_SENT->SYN_SENT, TIME_WAIT->SYN_SENT, CLOSE->SYN_SENT
- SYN-ACK: SYN_SENT->INVALID, SYN_RECV->SYN_RECV, SYN_SENT2->SYN_RECV
- FIN: SYN_RECV->FIN_WAIT, ESTABLISHED->FIN_WAIT, etc.
- ACK: NONE->ESTABLISHED, SYN_RECV->ESTABLISHED, FIN_WAIT->CLOSE_WAIT, etc.
- RST: 任何状态->CLOSE

回复方向 (tcp_conntracks[1]):
- SYN: SYN_SENT->SYN_SENT2, SYN_SENT2->SYN_SENT2, etc.
```

### 4.2 UDP 处理

**位置**: `net/netfilter/nf_conntrack_proto_udp.c:27-30`

```c
static const unsigned int udp_timeouts[UDP_CT_MAX] = {
    [UDP_CT_UNREPLIED] = 30*HZ,   // 30秒
    [UDP_CT_REPLIED] = 120*HZ,    // 120秒
};
```

**UDP状态标志**:
- `IPS_SEEN_REPLY`: 已见回复 -> 使用较长超时
- `IPS_ASSURED`: 已确认 -> 优先保留
- `IPS_NAT_CLASH`: NAT冲突 -> 快速超时

---

## 5. Nftables 表达式

### 5.1 寄存器模型

**位置**: `include/uapi/linux/netfilter/nf_tables.h:22-47`

```c
enum nft_registers {
    NFT_REG_VERDICT,    // 0: 裁决寄存器
    NFT_REG_1,         // 1: 数据寄存器 (16字节)
    NFT_REG_2,         // 2: 数据寄存器 (16字节)
    NFT_REG_3,         // 3: 数据寄存器 (16字节)
    NFT_REG_4,         // 4: 数据寄存器 (16字节)
    __NFT_REG_MAX,

    // 32位寄存器
    NFT_REG32_00 = 8,  // 8-23: 32位寄存器
    ...
    NFT_REG32_15 = 23,
};
```

**裁决值** (第64-70行):

```c
enum nft_verdicts {
    NFT_CONTINUE = -1,   // 继续评估当前规则
    NFT_BREAK = -2,      // 终止当前规则评估
    NFT_JUMP = -3,       // 压栈并跳转
    NFT_GOTO = -4,       // 无栈跳转
    NFT_RETURN = -5,     // 返回调用链
};
```

### 5.2 nft_cmp 表达式

**位置**: `net/netfilter/nft_cmp.c:19-24`

```c
struct nft_cmp_expr {
    struct nft_data data;   // 比较值
    u8 sreg;                // 源寄存器
    u8 len;                 // 长度
    enum nft_cmp_ops op:8;  // 操作: EQ, NEQ, LT, LTE, GT, GTE
};
```

**评估函数** (第26-64行):

```c
void nft_cmp_eval(const struct nft_expr *expr,
                  struct nft_regs *regs,
                  const struct nft_pktinfo *pkt)
{
    const struct nft_cmp_expr *priv = nft_expr_priv(expr);
    int d;

    d = memcmp(&regs->data[priv->sreg], &priv->data, priv->len);
    switch (priv->op) {
    case NFT_CMP_EQ:
        if (d != 0) goto mismatch;
        break;
    case NFT_CMP_NEQ:
        if (d == 0) goto mismatch;
        break;
    // ...
    }
    return;

mismatch:
    regs->verdict.code = NFT_BREAK;
}
```

### 5.3 nft_set_pipapo 算法 (高性能集合查找)

**位置**: `net/netfilter/nft_set_pipapo.c`

PIPAPO (Pile Packet Policies) 是一种高性能的数据包分类算法。

**核心概念**:
- 将位域分组 (通常4位或8位为一组)
- 每个分组创建一个查找表
- 使用位图跟踪匹配的规则

**匹配流程** (第416-508行):

```c
static struct nft_pipapo_elem *pipapo_get_slow(const struct nft_pipapo_match *m,
                                               const u8 *data, u8 genmask,
                                               u64 tstamp)
{
    local_bh_disable();
    scratch = *raw_cpu_ptr(m->scratch);

    pipapo_resmap_init(m, res_map);  // 初始化为全1

    nft_pipapo_for_each_field(f, i, m) {
        // 1. 对每个分组执行查找并AND
        if (likely(f->bb == 8))
            pipapo_and_field_buckets_8bit(f, res_map, data);
        else
            pipapo_and_field_buckets_4bit(f, res_map, data);

        // 2. 重填下一字段的位图
        b = pipapo_refill(res_map, f->bsize, f->rules, fill_map, f->mt, last);

        // 3. 交换位图索引
        swap(res_map, fill_map);
    }

    local_bh_enable();
    return NULL;
}
```

**关键特性**:
- 支持AVX2硬件加速 (第532-537行)
- Per-CPU scratch区域避免锁竞争
- 使用RCU保护并发访问

---

## 6. Xtables 匹配/目标

### 6.1 xt_match 结构

**位置**: `include/linux/netfilter/x_tables.h`

```c
struct xt_match {
    char name[XT_FUNCTION_MAXNAMELEN-1];  // 匹配名称
    u8 revision;

    // 匹配函数
    bool (*match)(const struct sk_buff *skb,
                  struct xt_action_param *);

    // 检查函数 (初始化时调用)
    int (*checkentry)(const struct xt_mtchk_param *);

    // 销毁函数 (卸载时调用)
    void (*destroy)(const struct xt_mtdtor_param *);

    void *me;                    // 指向自身模块
    u8 family;                   // 协议族: NFPROTO_IPV4, NFPROTO_IPV6, etc.
    size_t matchsize;            // matchinfo大小
    size_t usersize;             // 用户空间大小
#ifdef CONFIG_COMPAT
    compat_uptr_t compat_match;
#endif
    struct module *me;
};
```

### 6.2 xt_target 结构

**位置**: `include/linux/netfilter/x_tables.h`

```c
struct xt_target {
    char name[XT_FUNCTION_MAXNAMELEN-1];
    u8 revision;

    // 目标函数
    unsigned int (*target)(struct sk_buff *skb,
                           const struct xt_action_param *);

    // 检查函数
    int (*checkentry)(const struct xt_tgchk_param *);

    // 销毁函数
    void (*destroy)(const struct xt_tgdtr_param *);

    void *me;
    u8 family;
    size_t targetsize;
    size_t usersize;
    unsigned int (*compat_target)(...);
    struct module *me;
};
```

### 6.3 xt_state 匹配

**位置**: `net/netfilter/xt_state.c:20-36`

```c
static bool state_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct xt_state_info *sinfo = par->matchinfo;
    enum ip_conntrack_info ctinfo;
    unsigned int statebit;
    struct nf_conn *ct = nf_ct_get(skb, &ctinfo);

    if (ct)
        statebit = XT_STATE_BIT(ctinfo);  // 从ctinfo获取状态位
    else if (ctinfo == IP_CT_UNTRACKED)
        statebit = XT_STATE_UNTRACKED;
    else
        statebit = XT_STATE_INVALID;

    return (sinfo->statemask & statebit);  // 检查掩码
}
```

**状态位映射**:

| ctinfo | 状态位 |
|--------|--------|
| IP_CT_NEW | XT_STATE_BIT(0) = 1<<0 = 1 |
| IP_CT_ESTABLISHED | XT_STATE_BIT(1) = 1<<1 = 2 |
| IP_CT_RELATED | XT_STATE_BIT(2) = 1<<2 = 4 |
| IP_CT_IS_REPLY | 附加到上述值 |

### 6.4 xt_conntrack 匹配

**位置**: `net/netfilter/xt_conntrack.c`

支持更细粒度的连接跟踪匹配:

```c
struct xt_conntrack_mtinfo2 {
    union nf_inet_addr origsrc_addr;   // 原始源地址
    union nf_inet_addr origsrc_mask;
    union nf_inet_addr origdst_addr;
    union nf_inet_addr origdst_mask;
    union nf_inet_addr replsrc_addr;
    union nf_inet_addr replsrc_mask;
    union nf_inet_addr repldst_addr;
    union nf_inet_addr repldst_mask;
    __be16 origsrc_port;              // 原始源端口
    __be16 origdst_port;
    __be16 replsrc_port;
    __be16 repldst_port;
    u_int8_t l4proto;                // 协议号
    u_int16_t match_flags;          // 比较标志
    u_int16_t invert_flags;         // 反转标志
    u_int16_t state_mask;           // 状态掩码
    u_int16_t status_mask;          // 状态掩码
};
```

**匹配标志**:
- `XT_CONNTRACK_STATE`: 连接状态
- `XT_CONNTRACK_DIRECTION`: 方向
- `XT_CONNTRACK_ORIGSRC`: 原始源地址
- `XT_CONNTRACK_ORIGDST`: 原始目标地址
- `XT_CONNTRACK_REPLSRC`: 回复源地址
- `XT_CONNTRACK_REPLDST`: 回复目标地址
- `XT_CONNTRACK_PROTO`: 协议
- `XT_CONNTRACK_STATUS`: 连接状态位

---

## 7. 性能优化

### 7.1 锁优化

**位置**: `net/netfilter/nf_conntrack_core.c:57-58, 104-127`

```c
/* 分段锁 - 减少锁竞争 */
spinlock_t nf_conntrack_locks[CONNTRACK_LOCKS];  // 默认为4096
#define CONNTRACK_LOCKS 4096

void nf_conntrack_lock(spinlock_t *lock) __acquires(lock)
{
    spin_lock(lock);

    // 检查是否需要全局锁
    if (likely(smp_load_acquire(&nf_conntrack_locks_all) == false))
        return;

    // 快速路径失败,获取全局锁
    spin_unlock(lock);
    spin_lock(&nf_conntrack_locks_all_lock);
    spin_lock(lock);
    spin_unlock(&nf_conntrack_locks_all_lock);
}
```

### 7.2 哈希预计算

**位置**: `net/netfilter/nf_conntrack_core.c:1698`

```c
/* 保存reply方向的哈希值以便确认时重用 */
*(unsigned long *)(&ct->tuplehash[IP_CT_DIR_REPLY].hnnode.pprev) = hash;
```

在确认时不需要重新计算哈希,直接使用预存值。

### 7.3 RCU 和 SLAB_TYPESAFE_BY_RCU

**位置**: `net/netfilter/nf_conntrack_core.c:2671-2674`

```c
nf_conntrack_cachep = kmem_cache_create("nf_conntrack",
                sizeof(struct nf_conn),
                NFCT_INFOMASK + 1,
                SLAB_TYPESAFE_BY_RCU | SLAB_HWCACHE_ALIGN, NULL);
```

`SLAB_TYPESAFE_BY_RCU` 允许在 RCU 宽限期内的回收slab对象被重用,减少内存分配开销。

### 7.4 早期删除策略

**位置**: `net/netfilter/nf_conntrack_core.c:1493-1511`

```c
static bool gc_worker_can_early_drop(const struct nf_conn *ct)
{
    const struct nf_conntrack_l4proto *l4proto;
    u8 protonum = nf_ct_protonum(ct);

    // 非ASSURED的连接可以早期删除
    if (!test_bit(IPS_ASSURED_BIT, &ct->status))
        return true;

    // 协议特定检查
    l4proto = nf_ct_l4proto_find(protonum);
    if (l4proto->can_early_drop && l4proto->can_early_drop(ct))
        return true;

    return false;
}
```

### 7.5 NAT 哈希表

**位置**: `net/netfilter/nf_nat_core.c:38-40, 820-827`

```c
/* NAT按源哈希 - 加速相同源的连接查找 */
static struct hlist_head *nf_nat_bysource __read_mostly;

/* 添加入口 */
static unsigned int srchash = hash_by_src(net, zone,
                &ct->tuplehash[IP_CT_DIR_ORIGINAL].tuple);
spin_lock_bh(&nf_nat_locks[srchash % CONNTRACK_LOCKS]);
hlist_add_head_rcu(&ct->nat_bysource, &nf_nat_bysource[srchash]);
spin_unlock_bh(&nf_nat_locks[srchash % CONNTRACK_LOCKS]);
```

### 7.6 Per-CPU 计数器和统计

**位置**: `net/netfilter/nf_conntrack_core.c:633-642`

```c
static void nf_ct_add_to_ecache_list(struct nf_conn *ct)
{
    struct nf_conntrack_net *cnet = nf_ct_pernet(nf_ct_net(ct));

    spin_lock(&cnet->ecache.dying_lock);
    hlist_nulls_add_head_rcu(&ct->tuplehash[IP_CT_DIR_ORIGINAL].hnnode,
                 &cnet->ecache.dying_list);
    spin_unlock(&cnet->ecache.dying_lock);
}
```

---

## 数据流图

### 连接跟踪数据包流程

```
nf_conntrack_in()
    |
    +---> get_l4proto()           获取L4协议
    |
    +---> nf_conntrack_handle_icmp()  处理ICMP错误
    |
    +---> resolve_normal_ct()     查找或创建连接
    |       |
    |       +---> hash_conntrack_raw()    计算哈希
    |       |
    |       +---> __nf_conntrack_find_get()  查找现有连接
    |       |
    |       +---> init_conntrack()    创建新连接
    |           |
    |           +---> nf_ct_find_expectation()  查找期望
    |           |
    |           +---> __nf_conntrack_alloc()   分配连接
    |           |
    |           +---> nf_conntrack_hash_check_insert()  插入哈希表
    |
    +---> nf_conntrack_handle_packet()  处理数据包
    |       |
    |       +---> nf_conntrack_tcp_packet()   TCP处理
    |       |
    |       +---> nf_conntrack_udp_packet()   UDP处理
    |       |
    |       +---> nf_conntrack_icmp_packet()  ICMP处理
    |
    +---> nf_ct_set()  设置skb的连接跟踪信息
    |
    +---> __nf_conntrack_confirm()  确认连接(加入哈希表)
```

### NAT 数据包流程

```
nf_nat_inet_fn()
    |
    +---> nf_ct_get()           获取连接
    |
    +---> 检查ctinfo类型
    |       |
    |       +---> IP_CT_NEW/IP_CT_RELATED:
    |       |   +---> 检查NAT是否已初始化
    |       |   +---> 调用NAT lookup hooks
    |       |   +---> 如果无规则,分配null binding
    |       |
    |       +---> IP_CT_ESTABLISHED:
    |           +---> 直接执行NAT
    |
    +---> nf_nat_packet()       执行实际NAT转换
    |       |
    |       +---> HOOK2MANIP()  确定SNAT/DNAT
    |       |
    |       +---> nf_nat_manip_pkt()  修改数据包
```

---

## 附录: 关键文件路径

| 文件 | 功能 |
|------|------|
| `net/netfilter/nf_conntrack_core.c` | 连接跟踪核心 |
| `net/netfilter/nf_conntrack_proto_tcp.c` | TCP协议跟踪 |
| `net/netfilter/nf_conntrack_proto_udp.c` | UDP协议跟踪 |
| `net/netfilter/nf_conntrack_expect.c` | 期望连接管理 |
| `net/netfilter/nf_nat_core.c` | NAT核心 |
| `net/netfilter/nft_cmp.c` | nftables比较表达式 |
| `net/netfilter/nft_set_pipapo.c` | PIPAPO集合算法 |
| `net/netfilter/xt_state.c` | iptables state匹配 |
| `net/netfilter/xt_conntrack.c` | iptables conntrack匹配 |
| `include/net/netfilter/nf_conntrack.h` | 连接跟踪核心结构 |
| `include/uapi/linux/netfilter/nf_conntrack_common.h` | 连接跟踪通用定义 |

---

## 版本信息

- 分析版本: Linux Kernel master (2026-04-26)
- 文档版本: R1
- 分析人: Claude Code

