# Linux 内核 Netfilter 子系统分析文档

## 1. net/netfilter/ - 核心 Netfilter 基础设施

### 1.1 nf_hook_ops 结构体

**文件**: `include/linux/netfilter.h:98-111`

```c
struct nf_hook_ops {
    struct list_head	list;
    struct rcu_head		rcu;

    /* User fills in from here down. */
    nf_hookfn		*hook;          // 钩子函数指针
    struct net_device	*dev;           // 网络设备
    void			*priv;          // 私有数据
    u8			pf;              // 协议族 (NFPROTO_IPV4, NFPROTO_IPV6 等)
    enum nf_hook_ops_type	hook_ops_type:8;
    unsigned int		hooknum;        // 钩子编号 (NF_INET_LOCAL_IN 等)
    /* Hooks are ordered in ascending priority. */
    int			priority;        // 优先级，数值越小优先级越高
};
```

**相关结构**:

```c
// include/linux/netfilter.h:113-141
struct nf_hook_entry {
    nf_hookfn	*hook;
    void		*priv;
};

struct nf_hook_entries {
    u16		num_hook_entries;
    struct nf_hook_entry	hooks[];
    // 尾部还包含 orig_ops 指针数组和 rcu_head
};
```

### 1.2 nf_register_net_hook() / nf_unregister_net_hook()

**文件**: `net/netfilter/core.c`

#### nf_register_net_hook() (第 554-581 行)

```c
int nf_register_net_hook(struct net *net, const struct nf_hook_ops *reg)
{
    int err;

    if (reg->pf == NFPROTO_INET) {
        if (reg->hooknum == NF_INET_INGRESS) {
            err = __nf_register_net_hook(net, NFPROTO_INET, reg);
            if (err < 0)
                return err;
        } else {
            // 对于 IPv4/IPv6 通用钩子，同时注册到 IPv4 和 IPv6
            err = __nf_register_net_hook(net, NFPROTO_IPV4, reg);
            if (err < 0)
                return err;

            err = __nf_register_net_hook(net, NFPROTO_IPV6, reg);
            if (err < 0) {
                __nf_unregister_net_hook(net, NFPROTO_IPV4, reg);
                return err;
            }
        }
    } else {
        err = __nf_register_net_hook(net, reg->pf, reg);
        if (err < 0)
            return err;
    }

    return 0;
}
```

#### __nf_register_net_hook() (第 393-456 行)

```c
static int __nf_register_net_hook(struct net *net, int pf,
                  const struct nf_hook_ops *reg)
{
    struct nf_hook_entries *p, *new_hooks;
    struct nf_hook_entries __rcu **pp;
    int err;

    // ...

    pp = nf_hook_entry_head(net, pf, reg->hooknum, reg->dev);
    if (!pp)
        return -EINVAL;

    mutex_lock(&nf_hook_mutex);

    p = nf_entry_dereference(*pp);
    new_hooks = nf_hook_entries_grow(p, reg);  // 将新钩子添加到链表

    if (!IS_ERR(new_hooks)) {
        hooks_validate(new_hooks);
        rcu_assign_pointer(*pp, new_hooks);    // 原子替换钩子链表
    }

    mutex_unlock(&nf_hook_mutex);
    ...
}
```

#### nf_unregister_net_hook() (第 526-538 行)

```c
void nf_unregister_net_hook(struct net *net, const struct nf_hook_ops *reg)
{
    if (reg->pf == NFPROTO_INET) {
        if (reg->hooknum == NF_INET_INGRESS) {
            __nf_unregister_net_hook(net, NFPROTO_INET, reg);
        } else {
            __nf_unregister_net_hook(net, NFPROTO_IPV4, reg);
            __nf_unregister_net_hook(net, NFPROTO_IPV6, reg);
        }
    } else {
        __nf_unregister_net_hook(net, reg->pf, reg);
    }
}
```

### 1.3 nf_hook_slow()

**文件**: `net/netfilter/core.c:616-646`

```c
/* Returns 1 if okfn() needs to be executed by the caller,
 * -EPERM for NF_DROP, 0 otherwise.  Caller must hold rcu_read_lock. */
int nf_hook_slow(struct sk_buff *skb, struct nf_hook_state *state,
         const struct nf_hook_entries *e, unsigned int s)
{
    unsigned int verdict;
    int ret;

    for (; s < e->num_hook_entries; s++) {
        verdict = nf_hook_entry_hookfn(&e->hooks[s], skb, state);
        switch (verdict & NF_VERDICT_MASK) {
        case NF_ACCEPT:
            break;
        case NF_DROP:
            kfree_skb_reason(skb, SKB_DROP_REASON_NETFILTER_DROP);
            ret = NF_DROP_GETERR(verdict);
            if (ret == 0)
                ret = -EPERM;
            return ret;
        case NF_QUEUE:
            ret = nf_queue(skb, state, s, verdict);
            if (ret == 1)
                continue;
            return ret;
        case NF_STOLEN:
            return NF_DROP_GETERR(verdict);
        default:
            WARN_ON_ONCE(1);
            return 0;
        }
    }

    return 1;  // 继续执行 okfn()
}
```

**执行流程**:
1. 遍历钩子链表中的每个钩子
2. 调用 `nf_hook_entry_hookfn()` 执行钩子函数
3. 根据返回的判决值处理:
   - `NF_ACCEPT`: 继续下一个钩子
   - `NF_DROP`: 释放数据包，返回错误
   - `NF_QUEUE`: 进入用户空间队列
   - `NF_STOLEN`: 数据包被"偷走"，不释放

---

## 2. net/ipv4/netfilter/iptable_filter - 数据包过滤

### 2.1 ipt_do_table() - 数据包过滤核心函数

**文件**: `net/ipv4/netfilter/ip_tables.c:222-362`

```c
unsigned int
ipt_do_table(void *priv,
         struct sk_buff *skb,
         const struct nf_hook_state *state)
{
    const struct xt_table *table = priv;
    unsigned int hook = state->hook;
    const struct iphdr *ip;
    unsigned int verdict = NF_DROP;
    const char *indev, *outdev;
    const void *table_base;
    struct ipt_entry *e, **jumpstack;
    unsigned int stackidx, cpu;
    const struct xt_table_info *private;
    struct xt_action_param acpar;
    unsigned int addend;

    /* 初始化 */
    stackidx = 0;
    ip = ip_hdr(skb);
    indev = state->in ? state->in->name : nulldevname;
    outdev = state->out ? state->out->name : nulldevname;

    acpar.fragoff = ntohs(ip->frag_off) & IP_OFFSET;
    acpar.thoff   = ip_hdrlen(skb);
    acpar.hotdrop = false;
    acpar.state   = state;

    local_bh_disable();
    addend = xt_write_recseq_begin();
    private = READ_ONCE(table->private);
    cpu        = smp_processor_id();
    table_base = private->entries;
    jumpstack  = (struct ipt_entry **)private->jumpstack[cpu];

    // 获取该 hook 的第一条规则入口
    e = get_entry(table_base, private->hook_entry[hook]);

    do {
        const struct xt_entry_target *t;
        const struct xt_entry_match *ematch;
        struct xt_counters *counter;

        // 步骤1: IP 头匹配检查
        if (!ip_packet_match(ip, indev, outdev, &e->ip, acpar.fragoff)) {
no_match:
            e = ipt_next_entry(e);
            continue;
        }

        // 步骤2: 扩展匹配 (match extensions)
        xt_ematch_foreach(ematch, e) {
            acpar.match     = ematch->u.kernel.match;
            acpar.matchinfo = ematch->data;
            if (!acpar.match->match(skb, &acpar))
                goto no_match;
        }

        // 更新计数器
        counter = xt_get_this_cpu_counter(&e->counters);
        ADD_COUNTER(*counter, skb->len, 1);

        // 获取目标
        t = ipt_get_target_c(e);

        // 标准目标 (ACCEPT, DROP, CONTINUE 等)
        if (!t->u.kernel.target->target) {
            int v;
            v = ((struct xt_standard_target *)t)->verdict;

            if (v < 0) {
                // 负数 verdict: 返回或出栈
                if (v != XT_RETURN) {
                    verdict = (unsigned int)(-v) - 1;
                    break;
                }
                // XT_RETURN: 从用户链栈弹出
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
                if (unlikely(stackidx >= private->stacksize)) {
                    verdict = NF_DROP;
                    break;
                }
                jumpstack[stackidx++] = e;
            }
            e = get_entry(table_base, v);
            continue;
        }

        // 自定义目标函数
        acpar.target   = t->u.kernel.target;
        acpar.targinfo = t->data;
        verdict = t->u.kernel.target->target(skb, &acpar);

        if (verdict == XT_CONTINUE) {
            // 继续检查下一条规则
            ip = ip_hdr(skb);
            e = ipt_next_entry(e);
        } else {
            // 判决终止
            break;
        }
    } while (!acpar.hotdrop);

    xt_write_recseq_end(addend);
    local_bh_enable();

    if (acpar.hotdrop)
        return NF_DROP;
    else return verdict;
}
```

### 2.2 struct ipt_replace - 规则表替换结构

**文件**: `include/uapi/linux/netfilter_ipv4/ip_tables.h:179-207`

```c
struct ipt_replace {
    char name[XT_TABLE_MAXNAMELEN];       /* 表名 */
    unsigned int valid_hooks;               /* 有效钩子位掩码 */
    unsigned int num_entries;              /* 条目数量 */
    unsigned int size;                     /* 新规则总大小 */
    unsigned int hook_entry[NF_INET_NUMHOOKS];  /* 各钩子入口偏移 */
    unsigned int underflow[NF_INET_NUMHOOKS];    /* 各钩子下溢点偏移 */
    unsigned int num_counters;
    struct xt_counters __user *counters;   /* 旧条目计数器信息 */
    struct ipt_entry entries[];            /* 规则条目 (柔性数组) */
};
```

### 2.3 struct ipt_entry - 单条规则结构

**文件**: `include/uapi/linux/netfilter_ipv4/ip_tables.h:106-125`

```c
struct ipt_entry {
    struct ipt_ip ip;           /* IP 头匹配条件 */
    unsigned int nfcache;        /* 缓存标记 */
    __u16 target_offset;         /* 目标偏移 (ipt_entry + matches) */
    __u16 next_offset;           /* 下一条目偏移 (ipt_entry + matches + target) */
    unsigned int comefrom;       /* 回溯指针 */
    struct xt_counters counters; /* 包和字节计数器 */
    unsigned char elems[];       /* 匹配项 + 目标 (柔性数组) */
};
```

### 2.4 filter 表的 Hook 定义

**文件**: `net/ipv4/netfilter/iptable_filter.c:19-29`

```c
#define FILTER_VALID_HOOKS ((1 << NF_INET_LOCAL_IN) | \
                (1 << NF_INET_FORWARD) | \
                (1 << NF_INET_LOCAL_OUT))

static const struct xt_table packet_filter = {
    .name       = "filter",
    .valid_hooks    = FILTER_VALID_HOOKS,
    .me         = THIS_MODULE,
    .af         = NFPROTO_IPV4,
    .priority   = NF_IP_PRI_FILTER,
};
```

**Filter 表的三个钩子**:

| 钩子 | 方向 | 用途 |
|------|------|------|
| `NF_INET_LOCAL_IN` | 入站本地 | 过滤目标是本机的数据包 |
| `NF_INET_FORWARD` | 转发 | 过滤需要转发的数据包 |
| `NF_INET_LOCAL_OUT` | 出站本地 | 过滤从本机发出的数据包 |

---

## 3. net/ipv4/netfilter/iptable_nat - NAT 转换

**文件**: `net/ipv4/netfilter/iptable_nat.c`

### 3.1 NAT 表的 Hook 定义

```c
static const struct xt_table nf_nat_ipv4_table = {
    .name       = "nat",
    .valid_hooks    = (1 << NF_INET_PRE_ROUTING) |
              (1 << NF_INET_POST_ROUTING) |
              (1 << NF_INET_LOCAL_OUT) |
              (1 << NF_INET_LOCAL_IN),
    .me         = THIS_MODULE,
    .af         = NFPROTO_IPV4,
};

static const struct nf_hook_ops nf_nat_ipv4_ops[] = {
    {
        .hook       = ipt_do_table,
        .pf         = NFPROTO_IPV4,
        .hooknum    = NF_INET_PRE_ROUTING,    /* 目的 NAT */
        .priority   = NF_IP_PRI_NAT_DST,
    },
    {
        .hook       = ipt_do_table,
        .pf         = NFPROTO_IPV4,
        .hooknum    = NF_INET_POST_ROUTING,   /* 源 NAT */
        .priority   = NF_IP_PRI_NAT_SRC,
    },
    // ...
};
```

### 3.2 NAT 工作流程

**文件**: `net/netfilter/nf_nat_core.c:866-891`

```c
unsigned int nf_nat_packet(struct nf_conn *ct,
               enum ip_conntrack_info ctinfo,
               unsigned int hooknum,
               struct sk_buff *skb)
{
    enum nf_nat_manip_type mtype = HOOK2MANIP(hooknum);
    enum ip_conntrack_dir dir = CTINFO2DIR(ctinfo);
    unsigned int verdict = NF_ACCEPT;
    unsigned long statusbit;

    // 根据 hook 确定是 SRC_NAT 还是 DST_NAT
    if (mtype == NF_NAT_MANIP_SRC)
        statusbit = IPS_SRC_NAT;
    else
        statusbit = IPS_DST_NAT;

    // 如果是回复方向，取反
    if (dir == IP_CT_DIR_REPLY)
        statusbit ^= IPS_NAT_MASK;

    // 如果连接已设置 NAT 标志，执行地址转换
    if (ct->status & statusbit)
        verdict = nf_nat_manip_pkt(skb, ct, mtype, dir);

    return verdict;
}
```

### 3.3 IP 地址操作

**文件**: `net/netfilter/nf_nat_proto.c:311-331`

```c
static bool nf_nat_ipv4_manip_pkt(struct sk_buff *skb,
                      unsigned int iphdroff,
                      const struct nf_conntrack_tuple *target,
                      enum nf_nat_manip_type maniptype)
{
    struct iphdr *iph;
    unsigned int hdroff;

    if (skb_ensure_writable(skb, iphdroff + sizeof(*iph)))
        return false;

    iph = (void *)skb->data + iphdroff;
    hdroff = iphdroff + iph->ihl * 4;

    // 调用 L4 协议特定的转换函数 (TCP/UDP 端口等)
    if (!l4proto_manip_pkt(skb, iphdroff, hdroff, target, maniptype))
        return false;

    iph = (void *)skb->data + iphdroff;

    // 修改 IP 头并更新校验和
    if (maniptype == NF_NAT_MANIP_SRC) {
        csum_replace4(&iph->check, iph->saddr, target->src.u3.ip);
        iph->saddr = target->src.u3.ip;
    } else {
        csum_replace4(&iph->check, iph->daddr, target->dst.u3.ip);
        iph->daddr = target->dst.u3.ip;
    }

    return true;
}
```

---

## 4. nftables - nft_do_chain()

**文件**: `net/netfilter/nf_tables_core.c:249-347`

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
    // 根据代际选择规则 blob
    if (genbit)
        blob = rcu_dereference(chain->blob_gen_1);
    else
        blob = rcu_dereference(chain->blob_gen_0);

    rule = (struct nft_rule_dp *)blob->data;

next_rule:
    regs.verdict.code = NFT_CONTINUE;

    // 遍历规则中的表达式
    for (; !rule->is_last ; rule = nft_rule_next(rule)) {
        nft_rule_dp_for_each_expr(expr, last, rule) {
            // 快速匹配路径
            if (expr->ops == &nft_cmp_fast_ops)
                nft_cmp_fast_eval(expr, &regs);
            else if (expr->ops == &nft_cmp16_fast_ops)
                nft_cmp16_fast_eval(expr, &regs);
            else if (expr->ops == &nft_bitwise_fast_ops)
                nft_bitwise_fast_eval(expr, &regs);
            else if (expr->ops != &nft_payload_fast_ops ||
                 !nft_payload_fast_eval(expr, &regs, pkt))
                expr_call_ops_eval(expr, &regs, pkt);

            if (regs.verdict.code != NFT_CONTINUE)
                break;
        }

        switch (regs.verdict.code) {
        case NFT_BREAK:
            regs.verdict.code = NFT_CONTINUE;
            continue;
        case NFT_CONTINUE:
            nft_trace_packet(pkt, &regs.verdict, &info, rule,
                     NFT_TRACETYPE_RULE);
            continue;
        }
        break;
    }

    // 处理最终判决
    switch (regs.verdict.code & NF_VERDICT_MASK) {
    case NF_ACCEPT:
    case NF_QUEUE:
    case NF_STOLEN:
        return regs.verdict.code;
    case NF_DROP:
        return NF_DROP_REASON(pkt->skb, SKB_DROP_REASON_NETFILTER_DROP, EPERM);
    }

    // 处理 NFT 特定判决
    switch (regs.verdict.code) {
    case NFT_JUMP:
        if (WARN_ON_ONCE(stackptr >= NFT_JUMP_STACK_SIZE))
            return NF_DROP;
        jumpstack[stackptr].rule = nft_rule_next(rule);
        stackptr++;
        fallthrough;
    case NFT_GOTO:
        chain = regs.verdict.chain;
        goto do_chain;
    case NFT_CONTINUE:
    case NFT_RETURN:
        break;
    default:
        WARN_ON_ONCE(1);
    }

    // 用户链栈弹出
    if (stackptr > 0) {
        stackptr--;
        rule = jumpstack[stackptr].rule;
        goto next_rule;
    }

    // 返回链策略
    if (nft_base_chain(basechain)->policy == NF_DROP)
        return NF_DROP_REASON(pkt->skb, SKB_DROP_REASON_NETFILTER_DROP, EPERM);

    return nft_base_chain(basechain)->policy;
}
```

---

## 5. 总结：数据包处理流程

### 5.1 Hook 注册流程

```
用户空间 (iptables/nft)
    ↓ setsockopt(getsockopt)
内核 Netlink 套接字
    ↓
nf_tables API / ip_tables API
    ↓
xt_register_table() / xt_register_template()
    ↓
nf_register_net_hook() / __nf_register_net_hook()
    ↓
nf_hook_entries_grow() → 将钩子添加到 nf_hook_entries 链表
    ↓
rcu_assign_pointer() 原子更新
```

### 5.2 数据包处理流程

```
数据包到达网络设备
    ↓
Netfilter 核心 hook 调用 (如 ip_rcv())
    ↓
nf_hook_slow(skb, state, hooks, 0)
    ↓
遍历所有注册的钩子 (按 priority 升序)
    ↓
调用钩子函数 (如 ipt_do_table)
    ↓
规则匹配 (IP 头 → matches → target)
    ↓
返回判决 (NF_ACCEPT/NF_DROP/NF_QUEUE/NF_STOLEN)
    ↓
继续下一个钩子或终止
```

### 5.3 iptables 规则遍历

```
hook_entry[hook] → 第一条规则
    ↓
ip_packet_match() 检查 IP 头
    ↓ (不匹配)
下一规则 ← ipt_next_entry()
    ↓ (匹配)
xt_ematch_foreach() 检查扩展匹配
    ↓ (不匹配)
下一规则
    ↓ (匹配)
target->target() 执行目标
    ↓
verdict 判决:
  - NF_ACCEPT/NF_DROP: 终止
  - XT_CONTINUE: 继续下一规则
  - -NF_ACCEPT-1: 跳转到用户链
  - -NF_DROP-1: 弹出用户链栈
```

---

## 6. 关键源码位置

| 组件 | 文件 | 行号 |
|------|------|------|
| nf_hook_ops 定义 | include/linux/netfilter.h | 98-111 |
| hook 注册/注销 | net/netfilter/core.c | 393-612 |
| hook 执行 | net/netfilter/core.c | 616-646 |
| ipt_do_table | net/ipv4/netfilter/ip_tables.c | 222-362 |
| ipt_entry 定义 | include/uapi/linux/netfilter_ipv4/ip_tables.h | 106-125 |
| ipt_replace 定义 | include/uapi/linux/netfilter_ipv4/ip_tables.h | 179-207 |
| xt_table_info | include/linux/netfilter/x_tables.h | 238-258 |
| iptable_filter | net/ipv4/netfilter/iptable_filter.c | 19-99 |
| iptable_nat | net/ipv4/netfilter/iptable_nat.c | 22-57 |
| nft_do_chain | net/netfilter/nf_tables_core.c | 249-347 |
| NAT 核心 | net/netfilter/nf_nat_core.c | 866-891 |
| NAT IPv4 操作 | net/netfilter/nf_nat_proto.c | 311-401 |
