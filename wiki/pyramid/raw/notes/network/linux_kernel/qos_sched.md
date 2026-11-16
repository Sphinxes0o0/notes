# net/sched - QoS 调度框架

## 1. 模块架构

### 1.1 功能概述

Linux 流量控制 (TC) 子系统提供了 QoS 调度框架，支持复杂的流量整形、优先级控制和队列管理。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/sched/sch_api.c` | Qdisc API |
| `net/sched/sch_generic.c` | 通用 qdisc 基础设施 |
| `net/sched/cls_api.c` | 分类器 API |
| `net/sched/sch_fifo.c` | FIFO qdisc |
| `net/sched/sch_prio.c` | PRIO qdisc |
| `net/sched/sch_htb.c` | HTB qdisc |

## 2. 核心数据结构

### 2.1 struct Qdisc

```c
// include/net/sch_generic.h:66
struct Qdisc {
    // 操作函数
    int (*enqueue)(struct sk_buff *skb, struct Qdisc *sch, struct sk_buff **to_free);
    struct sk_buff *(*dequeue)(struct Qdisc *);
    struct sk_buff *(*peek)(struct Qdisc *);

    // 标志
    u32 flags;
#define TCQ_F_BUILTIN       1   // 内置，不能删除
#define TCQ_F_CAN_BYPASS    4   // 空时跳过
#define TCQ_F_MQROOT        8   // 多队列根
#define TCQ_F_ONETXQUEUE    0x10  // 单 TX 队列
#define TCQ_F_NOLOCK         0x100  // 无锁

    u32 limit;                  // 队列长度限制
    const struct Qdisc_ops *ops;  // 操作函数集
    u32 handle;                // 句柄 (如 1:)
    u32 parent;               // 父 qdisc 句柄
    struct netdev_queue *dev_queue;  // 关联的网络设备队列

    // 统计
    struct gnet_stats_basic_sync __percpu *bstats;
    struct gnet_stats_queue qstats;

    // 数据包队列
    struct qdisc_skb_head   q;
};
```

### 2.2 struct Qdisc_ops

```c
// include/net/sch_generic.h:304
struct Qdisc_ops {
    struct Qdisc_ops *next;           // 链表
    const struct Qdisc_class_ops *cl_ops;  // 类操作 (如果有)
    char id[IFNAMSIZ];                // 名称 (如 "htb", "fq_codel")
    int priv_size;                    // 私有数据大小

    // 核心操作
    int (*enqueue)(struct sk_buff *skb, struct Qdisc *sch, struct sk_buff **to_free);
    struct sk_buff *(*dequeue)(struct Qdisc *);
    struct sk_buff *(*peek)(struct Qdisc *);

    // 生命周期
    int (*init)(struct Qdisc *sch, struct nlattr *arg);
    void (*reset)(struct Qdisc *);
    void (*destroy)(struct Qdisc *);
    int (*change)(struct Qdisc *sch, struct nlattr *arg);

    // 调试
    int (*dump)(struct Qdisc *, struct sk_buff *);
    int (*dump_stats)(struct Qdisc *, struct gnet_dump *);

    struct module *owner;
};
```

## 3. qdisc 操作

### 3.1 enqueue 流程

```c
// sch_generic.h:922
static inline int qdisc_enqueue(struct sk_buff *skb, struct Qdisc *sch,
                                struct sk_buff **to_free)
{
    return sch->enqueue(skb, sch, to_free);
}
```

### 3.2 dequeue 流程

```c
// sch_generic.c:393
static inline struct sk_buff *qdisc_dequeue(struct Qdisc *sch)
{
    struct sk_buff *skb;

    // 尝试从 qdisc 出队
    skb = sch->dequeue(sch);
    if (!skb) {
        // 如果没有，尝试重新入队
        return NULL;
    }

    // 更新统计
    qdisc_update_stats_at_dequeue(sch, skb);

    return skb;
}
```

## 4. 分类器

### 4.1 struct tcf_proto

```c
// include/net/sch_generic.h:423
struct tcf_proto {
    struct tcf_proto __rcu *next;     // 链表
    void __rcu *root;                // 根
    int (*classify)(struct sk_buff *, const struct tcf_proto *,
                     struct tcf_result *);
    __be16 protocol;                   // 协议族
    u32 prio;                        // 优先级
    void *data;                       // 私有数据
    const struct tcf_proto_ops *ops;  // 操作函数集
    struct tcf_chain *chain;         // 所属链
    spinlock_t lock;                  // 保护锁
};
```

### 4.2 分类结果

```c
// include/net/sch_generic.h:342
struct tcf_result {
    union {
        struct {
            unsigned long class;
            u32 classid;
        };
        const struct tcf_proto *goto_tp;
    };
};
```

## 5. pfifo_fast

### 5.1 结构

```c
// net/sched/sch_generic.c:712
struct pfifo_fast_priv {
    struct skb_array q[PFIFO_FAST_BANDS];  // 3 个优先级队列
};

// 优先级到队列映射
static const int prio2band[TC_PRIO_MAX + 1] = {
    0, 1, 2, 2, 1, 1, 0, 0, ...  // 共 16 个优先级
};
```

### 5.2 入队

```c
static int pfifo_fast_enqueue(struct sk_buff *skb, struct Qdisc *qdisc,
                               struct sk_buff **to_free)
{
    struct pfifo_fast_priv *priv = qdisc_priv(qdisc);
    int band = prio2band[skb->priority & TC_PRIO_MAX];

    // 加入对应优先级队列
    if (skb_array_produce(&priv->q[band], skb))
        return qdisc_drop(skb, qdisc, to_free);

    qdisc_update_stats_at_enqueue(qdisc, pkt_len);
    return NET_XMIT_SUCCESS;
}
```

## 6. HTB (Hierarchical Token Bucket)

### 6.1 类结构

```c
// net/sched/sch_htb.c
struct htb_class {
    struct Qdisc_class_common common;
    struct psched_ratecfg rate, ceil;    // 速率和上限
    s64 tokens, ctokens;               // token 桶
    struct tcf_proto __rcu *filter_list;  // 过滤器链表
    int level;                            // 层级 (0=叶子)
    struct htb_class *parent;            // 父类

    union {
        struct {
            int deficit[TC_HTB_MAXDEPTH];  // DRR 计数器
            struct Qdisc *q;              // 子 qdisc
        } leaf;
        struct {
            struct htb_prio clprio[TC_HTB_NUMPRIO];
        } inner;
    };
};
```

### 6.2 速率控制

```c
// HTB 使用 token bucket 算法
// tokens 随时间增加，上限为 ceil
// 发送时消耗 tokens
```

## 7. fq_codel (Fair Queue CoDel)

### 7.1 流结构

```c
// net/sched/sch_fq_codel.c
struct fq_codel_flow {
    struct sk_buff *head, *tail;     // 流队列
    struct list_head flowchain;       // 流链表
    int deficit;                      // DRR 计数器
    struct codel_vars cvars;         // CoDel 状态
};

struct fq_codel_sched_data {
    struct tcf_proto __rcu *filter_list;  // 可选分类器
    struct fq_codel_flow *flows;          // 流数组 (默认 1024)
    u32 *backlogs;                       // 流 backlog
    struct list_head new_flows;           // 新流列表 (RR 优先)
    struct list_head old_flows;           // 老流列表
    struct codel_params cparams;         // CoDel 参数
};
```

## 8. 过滤器类型

### 8.1 u32

```c
// net/sched/cls_u32.c
// 基于哈希的通用分类器
// 支持多级哈希
```

### 8.2 flower

```c
// net/sched/cls_flower.c
// 基于元数据的分类器
// 支持匹配: src/dst IP, src/dst port, protocol, vlan, etc.
```

### 8.3 bpf

```c
// net/sched/cls_bpf.c
// BPF 程序分类器
// 支持用户定义的 BPF 程序
```
