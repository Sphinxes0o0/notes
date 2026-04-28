# Linux Netfilter 子系统深度分析 R2

## 概述

本文档深入分析 Linux Kernel Netfilter 子系统 (nf_tables) 的核心设计，涵盖数据结构关系、查找算法、包匹配流程和动态集合机制。

---

## 1. nf_tables 核心数据结构和关系

### 1.1 数据结构层次图

```
nft_table (表)
  |
  +-- nft_chain (链表)
  |     |
  |     +-- rules (nft_rule 链表)
  |     |     |
  |     |     +-- nft_expr[] (表达式数组)
  |     |           |
  |     |           +-- nft_expr_ops.eval() (评估函数)
  |     |
  |     +-- blob_gen_0 / blob_gen_1 (规则二进制blob)
  |     +-- nft_base_chain (基链，可挂载到 Netfilter Hook)
  |
  +-- nft_set[] (集合)
  +-- nft_object[] (状态ful 对象)
  +-- nft_flowtable[] (流表)
```

### 1.2 nft_table 结构 (nf_tables.h:1311)

```c
struct nft_table {
    struct list_head        list;           // 全局表链表节点
    struct rhltable         chains_ht;      // 链哈希表 (rhashtable)
    struct list_head        chains;         // 链的链表
    struct list_head        sets;           // 集合链表
    struct list_head        objects;        // 状态ful对象链表
    struct list_head        flowtables;     // 流表链表
    u64                     hgenerator;     // Handle 生成器
    u64                     handle;         // 表的唯一句柄
    u32                     use;            // 引用计数
    u16                     family:6,       // 协议族 (AF_INET 等)
                                flags:8,
                                genmask:2;  // 代际掩码
    u32                     nlpid;          // Netlink Port ID
    char                    *name;          // 表名
    u16                     udlen;         // 用户数据长度
    u8                      *udata;         // 用户数据
    u8                      validate_state;  // 验证状态
};
```

### 1.3 nft_chain 结构 (nf_tables.h:1142)

```c
struct nft_chain {
    struct nft_rule_blob       __rcu *blob_gen_0;  // 当前代规则blob
    struct nft_rule_blob       __rcu *blob_gen_1;  // 下一代规则blob
    struct list_head           rules;              // 规则链表
    struct list_head           list;               // 表中链的链表节点
    struct rhlist_head         rhlhead;            // 哈希表节点
    struct nft_table           *table;             // 所属表
    u64                        handle;             // 链句柄
    u32                        use;                // 引用计数
    u8                         flags:5,            // NFT_CHAIN_BASE/HW_OFFLOAD/BINDING
                                bound:1,
                                genmask:2;
    char                       *name;               // 链名
    u16                        udlen;
    u8                         *udata;
    struct nft_rule_blob       *blob_next;         // 提交阶段临时blob
    struct nft_chain_validate_state vstate;         // 验证状态
};
```

**nft_chain 与 nft_table 关系**: 通过 `chain->table` 指针反向引用，`table->chains` 链表正向遍历。

### 1.4 nft_rule 结构 (nf_tables.h:1002)

```c
struct nft_rule {
    struct list_head    list;           // 链中规则的链表节点
    u64                 handle:42,      // 规则唯一句柄
                        genmask:2,     // 代际掩码
                        dlen:12,       // 表达式数据长度
                        udata:1;       // 用户数据标志
    unsigned char       data[]          // 表达式数据 (柔性数组)
        __attribute__((aligned(__alignof__(struct nft_expr))));
};
```

### 1.5 nft_expr 结构 (nf_tables.h:409)

```c
struct nft_expr {
    const struct nft_expr_ops   *ops;   // 表达式操作函数集
    unsigned char                data[]  // 表达式私有数据 (柔性数组)
        __attribute__((aligned(__alignof__(u64))));
};
```

### 1.6 nft_expr_ops 结构 (nf_tables.h:953)

```c
struct nft_expr_ops {
    void        (*eval)(const struct nft_expr *expr,
                        struct nft_regs *regs,
                        const struct nft_pktinfo *pkt);  // 评估函数
    int         (*clone)(struct nft_expr *dst, const struct nft_expr *src, gfp_t gfp);
    unsigned int size;                                      // 表达式总大小

    int         (*init)(const struct nft_ctx *ctx, const struct nft_expr *expr,
                        const struct nlattr * const tb[]);
    void        (*activate)(const struct nft_ctx *ctx, const struct nft_expr *expr);
    void        (*deactivate)(const struct nft_ctx *ctx, const struct nft_expr *expr,
                              enum nft_trans_phase phase);
    void        (*destroy)(const struct nft_ctx *ctx, const struct nft_expr *expr);
    // ... 其他方法
    const struct nft_expr_type   *type;
    void                *data;
};
```

### 1.7 nft_base_chain 结构 (nf_tables.h:1244)

```c
struct nft_base_chain {
    struct nf_hook_ops           ops;                     // Netfilter Hook 操作
    struct list_head             hook_list;               // Hook 列表 (NETDEV 族)
    const struct nft_chain_type  *type;                   // 链类型
    u8                           policy;                  // 默认策略 (NF_ACCEPT/DROP)
    u8                           flags;
    struct nft_stats __percpu   *stats;                   // 统计计数器
    struct nft_chain             chain;                   // 嵌入的 nft_chain
    struct flow_block            flow_block;              // 流表块 (Offload)
};
```

---

## 2. nft_chain 查找与添加

### 2.1 nft_chain_lookup() (nf_tables_api.c:1890)

```c
static struct nft_chain *nft_chain_lookup(struct net *net,
                                          struct nft_table *table,
                                          const struct nlattr *nla, u8 genmask)
{
    char search[NFT_CHAIN_MAXNAMELEN + 1];
    struct rhlist_head *tmp, *list;
    struct nft_chain *chain;

    nla_strscpy(search, nla, sizeof(search));

    rcu_read_lock();
    list = rhltable_lookup(&table->chains_ht, search, nft_chain_ht_params);
    if (!list)
        goto out_unlock;

    rhl_for_each_entry_rcu(chain, tmp, list, rhlhead) {
        if (nft_active_genmask(chain, genmask))
            goto out_unlock;
    }
    chain = ERR_PTR(-ENOENT);
out_unlock:
    rcu_read_unlock();
    return chain;
}
```

**算法分析**:
- 使用 `rhltable_lookup()` 在 O(1) 平均时间复杂度内通过链名查找
- `rhashtable` 支持哈希冲突时的链表解决 (rhlist)
- `genmask` 参数用于区分不同"代际"的链 (事务处理机制)
- `nft_active_genmask()` 宏检查链在当前代际是否活跃

**rhashtable 参数** (nf_tables_api.c:58):
```c
static const struct rhashtable_params nft_chain_ht_params = {
    .head_offset    = offsetof(struct nft_chain, rhlhead),
    .key_offset     = offsetof(struct nft_chain, name),
    .hashfn         = nft_chain_hash,
    .obj_hashfn     = nft_chain_hash_obj,
    .obj_cmpfn      = nft_chain_hash_cmp,
    .automatic_shrinking = true,
};
```

### 2.2 nft_chain_lookup_byhandle() (nf_tables_api.c:1866)

```c
static struct nft_chain *
nft_chain_lookup_byhandle(const struct nft_table *table, u64 handle, u8 genmask)
{
    struct nft_chain *chain;

    list_for_each_entry_rcu(chain, &table->chains, list,
                            lockdep_commit_lock_is_held(table->table->net)) {
        if (chain->handle == handle &&
            nft_active_genmask(chain, genmask))
            return chain;
    }
    return ERR_PTR(-ENOENT);
}
```

**算法分析**: 通过 64 位 `handle` 遍历链表查找，时间复杂度 O(n)。

### 2.3 nft_trans_chain_add() (nf_tables_api.c:618)

```c
static struct nft_trans *nft_trans_chain_add(struct nft_ctx *ctx, int msg_type)
{
    struct nft_trans *trans;

    trans = nft_trans_alloc_chain(ctx, msg_type);
    if (trans == NULL)
        return ERR_PTR(-ENOMEM);

    if (msg_type == NFT_MSG_NEWCHAIN) {
        nft_activate_next(ctx->net, ctx->chain);  // 设置 genmask

        if (ctx->nla[NFTA_CHAIN_ID]) {
            nft_trans_chain_id(trans) = ntohl(nla_get_be32(ctx->nla[NFTA_CHAIN_ID]));
        }
    }
    nft_trans_commit_list_add_tail(ctx->net, trans);  // 加入提交链表

    return trans;
}
```

**事务机制**:
- 所有表/链/规则的创建、删除操作都通过 `nft_trans` 事务对象暂存
- 提交阶段 (`nf_tables_commit()`) 才真正执行变更
- `nft_activate_next()` 设置对象的 `genmask` 位

### 2.4 nft_chain_add() (nf_tables_api.c:2679)

```c
int nft_chain_add(struct nft_table *table, struct nft_chain *chain)
{
    int err;

    err = rhltable_insert_key(&table->chains_ht, chain->name,
                              &chain->rhlhead, nft_chain_ht_params);
    if (err)
        return err;

    list_add_tail_rcu(&chain->list, &table->chains);  // 加入链表

    return 0;
}
```

---

## 3. nft_rule 查找与匹配流程

### 3.1 nft_rule_lookup() (nf_tables_api.c:3658)

```c
static struct nft_rule *nft_rule_lookup(const struct net *net,
                                       const struct nft_chain *chain,
                                       const struct nlattr *nla)
{
    if (nla == NULL)
        return ERR_PTR(-EINVAL);

    return __nft_rule_lookup(net, chain, be64_to_cpu(nla_get_be64(nla)));
}

static struct nft_rule *__nft_rule_lookup(const struct net *net,
                                          const struct nft_chain *chain,
                                          u64 handle)
{
    struct nft_rule *rule;

    list_for_each_entry_rcu(rule, &chain->rules, list,
                            lockdep_commit_lock_is_held(net)) {
        if (handle == rule->handle)
            return rule;
    }
    return ERR_PTR(-ENOENT);
}
```

**算法分析**: 遍历规则链表 O(n)，通过 64 位 `handle` 精确匹配。

### 3.2 nft_do_chain() 匹配流程 (nf_tables_core.c:250)

```c
unsigned int nft_do_chain(struct nft_pktinfo *pkt, void *priv)
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
    if (genbit)
        blob = rcu_dereference(chain->blob_gen_1);
    else
        blob = rcu_dereference(chain->blob_gen_0);

    rule = (struct nft_rule_dp *)blob->data;
next_rule:
    regs.verdict.code = NFT_CONTINUE;
    for (; !rule->is_last ; rule = nft_rule_next(rule)) {
        nft_rule_dp_for_each_expr(expr, last, rule) {
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
            nft_trace_copy_nftrace(pkt, &info);
            continue;
        case NFT_CONTINUE:
            nft_trace_packet(pkt, &regs.verdict, &info, rule,
                             NFT_TRACETYPE_RULE);
            continue;
        }
        break;
    }

    nft_trace_verdict(pkt, &info, rule, &regs);

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
        chain = regs.verdict.chain;
        goto do_chain;
    case NFT_CONTINUE:
    case NFT_RETURN:
        break;
    default:
        WARN_ON_ONCE(1);
    }

    if (stackptr > 0) {
        stackptr--;
        rule = jumpstack[stackptr].rule;
        goto next_rule;
    }

    nft_trace_packet(pkt, &regs.verdict, &info, NULL, NFT_TRACETYPE_POLICY);

    if (static_branch_unlikely(&nft_counters_enabled))
        nft_update_chain_stats(basechain, pkt);

    if (nft_base_chain(basechain)->policy == NF_DROP)
        return NF_DROP_REASON(pkt->skb, SKB_DROP_REASON_NETFILTER_DROP, EPERM);

    return nft_base_chain(basechain)->policy;
}
```

**匹配流程图**:

```
数据包进入
    |
    v
选择 blob_gen_0 或 blob_gen_1
    |
    v
获取第一条规则 (rule = blob->data)
    |
    v
for (规则未结束) {
    |
    +-- 遍历规则中的表达式
    |       |
    |       +-- 调用 expr->ops->eval()
    |       |       |
    |       |       v
    |       |    更新 regs.verdict.code
    |       |
    |       +-- 如果 verdict != NFT_CONTINUE, break
    |
    v
    处理 verdict:
    - NFT_BREAK: 继续下一条规则
    - NFT_CONTINUE: 继续当前规则下一表达式
    - NFT_JUMP/GOTO: 跳转到目标链 (JUMP 保存返回点)
    - NFT_RETURN: 返回调用链
    - NF_ACCEPT/DROP: 返回最终裁决
}
    |
    v
如果没有更多规则，返回链的默认策略
```

**关键优化 - Fast Expressions** (nf_tables_core.c:277-284):

```c
if (expr->ops == &nft_cmp_fast_ops)
    nft_cmp_fast_eval(expr, &regs);
else if (expr->ops == &nft_cmp16_fast_ops)
    nft_cmp16_fast_eval(expr, &regs);
else if (expr->ops == &nft_bitwise_fast_ops)
    nft_bitwise_fast_eval(expr, &regs);
else if (expr->ops != &nft_payload_fast_ops ||
         !nft_payload_fast_eval(expr, &regs, pkt))
    expr_call_ops_eval(expr, &regs, pkt);
```

对于简单的比较和位运算表达式，使用内联快速路径避免间接函数调用。

### 3.3 Jump Stack (nf_tables_core.c:199)

```c
struct nft_jumpstack {
    const struct nft_rule_dp *rule;  // NFT_JUMP 返回点
};

#define NFT_JUMP_STACK_SIZE 16  // 最大嵌套深度
```

**NFT_JUMP vs NFT_GOTO**:
- `NFT_JUMP`: 压栈保存返回点，支持 `NFT_RETURN` 返回
- `NFT_GOTO`: 不压栈，直接跳转，用于性能关键路径

---

## 4. nft_expr 表达式系统

### 4.1 表达式生命周期

```
用户空间创建表达式
        |
        v
nft_expr_init()     <-- 初始化私有数据
        |
        v
nft_rule_add()      <-- 添加到规则
        |
        v
nft_do_chain()      <-- 执行时调用 eval()
        |
        v
nft_expr_destroy()  <-- 规则删除时销毁
```

### 4.2 核心表达式 ops (nf_tables_core.c:218)

```c
X(e, nft_payload_eval);    // 载荷提取
X(e, nft_cmp_eval);        // 比较运算
X(e, nft_counter_eval);    // 计数器
X(e, nft_meta_get_eval);   // 元数据
X(e, nft_lookup_eval);      // 集合查找
X(e, nft_ct_get_fast_eval); // 连接跟踪
X(e, nft_range_eval);      // 范围匹配
X(e, nft_immediate_eval);  // 立即 verdict
X(e, nft_byteorder_eval);  // 字节序
X(e, nft_dynset_eval);     // 动态集合
X(e, nft_rt_get_eval);     // 路由
X(e, nft_bitwise_eval);    // 位运算
X(e, nft_objref_eval);     // 对象引用
```

### 4.3 表达式注册机制 (nf_tables_api.c:3304)

```c
int nft_register_expr(struct nft_expr_type *type)
{
    if (type->family == NFPROTO_UNSPEC)
        list_add_tail_rcu(&type->list, &nf_tables_expressions);
    else
        list_add_tail_rcu(&type->list, &nf_tables_expressions);
}
```

---

## 5. nft_dynset 动态集合

### 5.1 nft_dynset 数据结构 (nft_dynset.c:15)

```c
struct nft_dynset {
    struct nft_set          *set;           // 关联的集合
    struct nft_set_ext_tmpl tmpl;           // 元素扩展模板
    enum nft_dynset_ops     op:8;           // 操作: ADD/UPDATE/DELETE
    u8                      sreg_key;       // 源寄存器 (Key)
    u8                      sreg_data;      // 源寄存器 (Data)
    bool                    invert;         // 结果取反
    bool                    expr;           // 是否包含表达式
    u8                      num_exprs;      // 表达式数量
    u64                     timeout;        // 超时值
    struct nft_expr         *expr_array[NFT_SET_EXPR_MAX];
    struct nft_set_binding  binding;        // 集合绑定
};
```

### 5.2 nft_dynset_new() (nft_dynset.c:55)

```c
struct nft_elem_priv *nft_dynset_new(struct nft_set *set,
                                     const struct nft_expr *expr,
                                     struct nft_regs *regs)
{
    const struct nft_dynset *priv = nft_expr_priv(expr);
    struct nft_set_ext *ext;
    void *elem_priv;
    u64 timeout;

    if (!atomic_add_unless(&set->nelems, 1, set->size))  // 检查集合大小限制
        return NULL;

    timeout = priv->timeout ? : READ_ONCE(set->timeout);
    elem_priv = nft_set_elem_init(set, &priv->tmpl,
                                  &regs->data[priv->sreg_key], NULL,  // Key
                                  &regs->data[priv->sreg_data],      // Data
                                  timeout, 0, GFP_ATOMIC);
    if (IS_ERR(elem_priv))
        goto err1;

    ext = nft_set_elem_ext(set, elem_priv);
    if (priv->num_exprs && nft_dynset_expr_setup(priv, ext) < 0)
        goto err2;

    return elem_priv;

err2:
    nft_set_elem_destroy(set, elem_priv, false);
err1:
    if (set->size)
        atomic_dec(&set->nelems);
    return NULL;
}
```

### 5.3 nft_dynset_eval() (nft_dynset.c:89)

```c
void nft_dynset_eval(const struct nft_expr *expr,
                     struct nft_regs *regs, const struct nft_pktinfo *pkt)
{
    const struct nft_dynset *priv = nft_expr_priv(expr);
    struct nft_set *set = priv->set;
    const struct nft_set_ext *ext;

    if (priv->op == NFT_DYNSET_OP_DELETE) {
        set->ops->delete(set, &regs->data[priv->sreg_key]);
        return;
    }

    ext = set->ops->update(set, &regs->data[priv->sreg_key], expr, regs);
    if (ext) {
        if (priv->op == NFT_DYNSET_OP_UPDATE &&
            nft_set_ext_exists(ext, NFT_SET_EXT_TIMEOUT) &&
            READ_ONCE(nft_set_ext_timeout(ext)->timeout) != 0) {
            timeout = priv->timeout ? : READ_ONCE(set->timeout);
            WRITE_ONCE(nft_set_ext_timeout(ext)->expiration,
                       get_jiffies_64() + timeout);
        }

        nft_set_elem_update_expr(ext, regs, pkt);

        if (priv->invert)
            regs->verdict.code = NFT_BREAK;
        return;
    }

    if (!priv->invert)
        regs->verdict.code = NFT_BREAK;  // 集合中不存在，默认中断
}
```

**动态集合操作**:
- `NFT_DYNSET_OP_ADD`: 添加元素到集合
- `NFT_DYNSET_OP_UPDATE`: 更新已存在的元素
- `NFT_DYNSET_OP_DELETE`: 从集合删除元素

### 5.4 集合查找接口 (nf_tables.h:463)

```c
struct nft_set_ops {
    const struct nft_set_ext * (*lookup)(const struct net *net,
                                          const struct nft_set *set,
                                          const u32 *key);
    const struct nft_set_ext * (*update)(struct nft_set *set,
                                          const u32 *key,
                                          const struct nft_expr *expr,
                                          struct nft_regs *regs);
    bool                (*delete)(const struct nft_set *set, const u32 *key);
    // ...
};
```

---

## 6. nft_payload 协议头提取

### 6.1 nft_payload 数据结构 (nft_payload.c 内部定义)

```c
struct nft_payload {
    enum nft_payload_bases base:8;    // 基准位置
    u32     offset;                   // 偏移
    u8      len;                      // 长度
    u8      dreg;                      // 目标寄存器
};
```

### 6.2 载荷基准位置 (nf_tables.h:799)

```c
enum nft_payload_bases {
    NFT_PAYLOAD_LL_HEADER,        // 链路层头 (MAC header)
    NFT_PAYLOAD_NETWORK_HEADER,   // 网络层头 (IP header)
    NFT_PAYLOAD_TRANSPORT_HEADER, // 传输层头 (TCP/UDP header)
    NFT_PAYLOAD_INNER_HEADER,    // 内部头 (隧道)
    NFT_PAYLOAD_TUN_HEADER,      // 隧道头
};
```

### 6.3 nft_payload_eval() (nft_payload.c:159)

```c
void nft_payload_eval(const struct nft_expr *expr,
                      struct nft_regs *regs,
                      const struct nft_pktinfo *pkt)
{
    const struct nft_payload *priv = nft_expr_priv(expr);
    const struct sk_buff *skb = pkt->skb;
    u32 *dest = &regs->data[priv->dreg];
    int offset;

    if (priv->len % NFT_REG32_SIZE)
        dest[priv->len / NFT_REG32_SIZE] = 0;  // 清零高位

    switch (priv->base) {
    case NFT_PAYLOAD_LL_HEADER:
        if (!skb_mac_header_was_set(skb) || skb_mac_header_len(skb) == 0)
            goto err;

        if (skb_vlan_tag_present(skb) &&
            nft_payload_need_vlan_adjust(priv->offset, priv->len)) {
            if (!nft_payload_copy_vlan(dest, skb, priv->offset, priv->len))
                goto err;
            return;
        }
        offset = skb_mac_header(skb) - skb->data;
        break;

    case NFT_PAYLOAD_NETWORK_HEADER:
        offset = skb_network_offset(skb);
        break;

    case NFT_PAYLOAD_TRANSPORT_HEADER:
        if (!(pkt->flags & NFT_PKTINFO_L4PROTO) || pkt->fragoff)
            goto err;
        offset = nft_thoff(pkt);
        break;

    case NFT_PAYLOAD_INNER_HEADER:
        offset = nft_payload_inner_offset(pkt);
        if (offset < 0)
            goto err;
        break;

    default:
        WARN_ON_ONCE(1);
        goto err;
    }
    offset += priv->offset;

    if (skb_copy_bits(skb, offset, dest, priv->len) < 0)
        goto err;
    return;
err:
    regs->verdict.code = NFT_BREAK;  // 提取失败则中断
}
```

### 6.4 VLAN 处理 (nft_payload.c:28-72)

```c
static bool nft_payload_rebuild_vlan_hdr(const struct sk_buff *skb, int mac_off,
                                         struct vlan_ethhdr *veth)
{
    if (skb_copy_bits(skb, mac_off, veth, ETH_HLEN))
        return false;

    veth->h_vlan_proto = skb->vlan_proto;
    veth->h_vlan_TCI = htons(skb_vlan_tag_get(skb));
    veth->h_vlan_encapsulated_proto = skb->protocol;

    return true;
}
```

当数据包带有 VLAN tag 但被 offload 移除时，需要重建 VLAN 头才能正确提取字段。

### 6.5 nft_payload_fast_eval() (nf_tables_core.c:144)

```c
static bool nft_payload_fast_eval(const struct nft_expr *expr,
                                  struct nft_regs *regs,
                                  const struct nft_pktinfo *pkt)
{
    const struct nft_payload *priv = nft_expr_priv(expr);
    const struct sk_buff *skb = pkt->skb;
    u32 *dest = &regs->data[priv->dreg];
    unsigned char *ptr;

    if (priv->base == NFT_PAYLOAD_NETWORK_HEADER)
        ptr = skb_network_header(skb);
    else {
        if (!(pkt->flags & NFT_PKTINFO_L4PROTO))
            return false;
        ptr = skb->data + nft_thoff(pkt);
    }

    ptr += priv->offset;

    if (unlikely(ptr + priv->len > skb_tail_pointer(skb)))
        return false;

    *dest = 0;
    if (priv->len == 2)
        *(u16 *)dest = *(u16 *)ptr;
    else if (priv->len == 4)
        *(u32 *)dest = *(u32 *)ptr;
    else
        *(u8 *)dest = *(u8 *)ptr;
    return true;
}
```

**Fast Path 条件** (nft_payload.c:1084):
- `len <= 4` 且 `is_power_of_2(len)` 且 `offset` 对齐
- 不适用于 `NFT_PAYLOAD_LL_HEADER` 和 `NFT_PAYLOAD_INNER_HEADER`

---

## 7. 提交阶段 (Commit Phase)

### 7.1 nf_tables_commit_chain_prepare() (nf_tables_api.c:10185)

```c
static int nf_tables_commit_chain_prepare(struct net *net, struct nft_chain *chain)
{
    // ... 计算规则总大小
    list_for_each_entry(rule, &chain->rules, list) {
        if (nft_is_active_next(net, rule)) {
            data_size += sizeof(*prule) + rule->dlen;
        }
    }

    chain->blob_next = nf_tables_chain_alloc_rules(chain, data_size);

    // 遍历规则，复制表达式到 blob
    list_for_each_entry(rule, &chain->rules, list) {
        if (!nft_is_active_next(net, rule))
            continue;

        prule->handle = rule->handle;
        prule->dlen = size;
        prule->is_last = 0;

        chain->blob_next->size += (unsigned long)(data - (void *)prule);
    }
}
```

### 7.2 nf_tables_commit_chain() (nf_tables_api.c:10295)

```c
static void nf_tables_commit_chain(struct net *net, struct nft_chain *chain)
{
    struct nft_rule_blob *g0, *g1;
    bool next_genbit;

    next_genbit = nft_gencursor_next(net);

    // 切换 blob 指针
    if (next_genbit)
        rcu_assign_pointer(chain->blob_gen_1, chain->blob_next);
    else
        rcu_assign_pointer(chain->blob_gen_0, chain->blob_next);

    chain->blob_next = NULL;

    // 释放旧的 blob
    if (g0 != g1) {
        if (next_genbit)
            nf_tables_commit_chain_free_rules_old(g1);
        else
            nf_tables_commit_chain_free_rules_old(g0);
    }
}
```

---

## 8. 知识点关联表格

| 概念 | 数据结构 | 关键函数 | 源码位置 |
|------|----------|----------|----------|
| **表** | `struct nft_table` | `nft_table_lookup()` | nf_tables_api.c:995 |
| **链** | `struct nft_chain` | `nft_chain_lookup()` | nf_tables_api.c:1890 |
| **链** | `struct nft_base_chain` | `nft_do_chain()` | nf_tables_core.c:250 |
| **规则** | `struct nft_rule` | `nft_rule_lookup()` | nf_tables_api.c:3658 |
| **表达式** | `struct nft_expr` | `expr->ops->eval()` | nf_tables_core.c:203 |
| **集合** | `struct nft_set` | `set->ops->lookup()` | nf_tables.h:463 |
| **动态集合** | `struct nft_dynset` | `nft_dynset_eval()` | nft_dynset.c:89 |
| **载荷提取** | `struct nft_payload` | `nft_payload_eval()` | nft_payload.c:159 |
| **事务** | `struct nft_trans` | `nft_trans_chain_add()` | nf_tables_api.c:618 |
| **Blob** | `struct nft_rule_blob` | `nf_tables_commit_chain()` | nf_tables_api.c:10295 |

### 代际机制 (Generation Mechanism)

```c
// nf_tables.h:1564-1578
static inline unsigned int nft_gencursor_next(const struct net *net)
{
    return net->nft.gencursor + 1 == 1 ? 1 : 0;
}

static inline u8 nft_genmask_next(const struct net *net)
{
    return 1 << nft_gencursor_next(net);
}

static inline u8 nft_genmask_cur(const struct net *net)
{
    return 1 << READ_ONCE(net->nft.gencursor);
}
```

- 使用两位掩码表示四个代际状态
- `gencursor` 在提交时切换
- 规则在 blob_gen_0 和 blob_gen_1 之间切换

---

## 9. 总结

nf_tables 子系统的核心设计要点:

1. **三层数据结构**: Table -> Chain -> Rule -> Expr 层次清晰
2. **RCU 机制**: 读侧无锁，写侧通过代际切换实现无阻塞更新
3. **表达式评估**: 通过 `nft_expr_ops.eval()` 函数指针支持可扩展表达式
4. **Fast Path**: 简单表达式使用内联函数避免间接调用开销
5. **Jump Stack**: 支持 NFT_JUMP/NFT_GOTO 实现链间跳转
6. **动态集合**: 支持运行时添加/更新/删除集合元素
7. **事务机制**: 所有变更通过事务暂存，提交阶段批量生效

---

*文档生成时间: 2026-04-26*
*源码版本: Linux Kernel Netfilter nf_tables*
