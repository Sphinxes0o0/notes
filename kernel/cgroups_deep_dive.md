# Linux Cgroups 深度架构分析 v2

## 1. 概述

本文档是 Linux cgroups 子系统的第二轮深度分析，重点关注 CSS（cgroup_subsys_state）机制、控制器资源跟踪算法、cgroup v2 层级架构、任务迁移与引用计数、以及 cgroup fs (cgroupfs) 实现细节。

## 2. CSS（cgroup Subsys State）机制

### 2.1 CSS 结构

```c
/**
 * struct cgroup_subsys_state - 控制器状态
 *
 * 每个 cgroup 的每个控制器都有一个 CSS 实例
 */
struct cgroup_subsys_state {
    /* 指向父 CSS */
    struct cgroup_subsys_state *parent;

    /* 指向所属的 cgroup */
    struct cgroup *cgroup;

    /* 控制器 */
    struct cgroup_subsys *ss;

    /* 引用计数 */
    int refcnt;

    /* 唯一的 CSS ID */
    int id;

    /* CSS flags */
    unsigned long flags;

    /* 控制器特定数据 */
    void *state;

    /* 系统调用的工作队列 */
    struct work_struct dput_work;
};

/**
 * struct cgroup - cgroup 本体
 */
struct cgroup {
    /* 引用计数 */
    refcount_t refcount;

    /* 层级 ID */
    int level;

    /* 层级根 */
    struct cgroup_root *root;

    /* 父 cgroup */
    struct cgroup *parent;

    /* 子 cgroup 链表 */
    struct list_head children;

    /* CSS 数组（每个控制器一个） */
    struct cgroup_subsys_state *subsys[CGROUP_SUBSYS_COUNT];

    /* 子树状态 */
    bool subtree_cset_needs_branch_check;
    bool subtree_control_has_changed;

    /* dentry */
    struct dentry *dentry;

    /* 计数 */
    atomic_long_t resident_csets[CGROUP_SUBSYS_COUNT];
};
```

### 2.2 CSS 链表管理

```c
/**
 * cgroup_for_each_child - 遍历子 cgroup
 *
 * 使用方法：
 * cgroup_for_each_child(child, parent) {
 *     // 处理 child
 * }
 */
#define cgroup_for_each_child(child, parent)                    \
    list_for_each_entry(child, &(parent)->children, sibling)

/**
 * cgroup_for_each_descendant_pre - 先序遍历后代
 *
 * 使用方法：
 * cgroup_for_each_descendant_pre(desc, root) {
 *     // 前序处理
 * }
 */
#define cgroup_for_each_descendant_pre(desc, root)                    \
    css_for_each_descendant_pre(css_from_cgroup(root),               \
                                css_from_cgroup(desc))

/**
 * css_for_each_descendant_pre - CSS 先序遍历
 *
 * 实现：使用栈模拟递归
 */
static struct cgroup_subsys_state *
css_for_each_descendant_pre(struct cgroup_subsys_state *css,
                           struct cgroup_subsys_state *stop)
{
    css->parent->children;  /* trigger css_from_desc() */
    return css_next_descendant_pre(css, stop);
}
```

### 2.3 CSS 引用计数

```c
/**
 * css_get - 增加 CSS 引用
 *
 * 引用计数管理：
 * - 任务加入 cgroup 时增加引用
 * - 任务离开 cgroup 时减少引用
 * - refcnt == 0 时可以释放
 */
void css_get(struct cgroup_subsys_state *css)
{
    if (css)
        refcount_inc(&css->refcnt);
}

/**
 * css_tryget - 尝试获取 CSS 引用
 *
 * 如果 CSS 正在被释放，返回 NULL
 */
bool css_tryget(struct cgroup_subsys_state *css)
{
    if (css)
        return refcount_inc_not_zero(&css->refcnt);
    return false;
}

/**
 * css_put - 释放 CSS 引用
 *
 * 当 refcnt 降到 0 时，触发释放
 */
void css_put(struct cgroup_subsys_state *css)
{
    if (css && refcount_dec_and_test(&css->refcnt)) {
        /* 延迟释放到工作队列 */
        schedule_work(&css->dput_work);
    }
}
```

## 3. 控制器架构

### 3.1 控制器结构

```c
/**
 * struct cgroup_subsys - 控制器定义
 *
 * 定义控制器的行为和操作
 */
struct cgroup_subsys {
    /* 控制器名称 */
    const char *name;

    /* 层级 ID */
    int id;

    /* 初始化 */
    int (*css_online)(struct cgroup_subsys_state *css);
    void (*css_offline)(struct cgroup_subsys_state *css);

    /* 释放 */
    void (*css_released)(struct cgroup_subsys_state *css);

    /* 回收 */
    void (*css_free)(struct cgroup_subsys_state *css);

    /* 任务附加/分离 */
    int (*can_attach)(struct cgroup_subsys_state *css,
                      struct task_struct *task);
    void (*cancel_attach)(struct cgroup_subsys_state *css,
                          struct task_struct *task);
    void (*attach)(struct cgroup_subsys_state *css,
                   struct cgroup_subsys_state *old_css,
                   struct task_struct *task);
    void (*post_attach)(void);

    /* 任务睡眠/唤醒 */
    void (*task_sleep)(struct task_struct *task);
    void (*task_woken)(struct cgroup_subsys_state *css,
                       struct task_struct *task);

    /* 退出 */
    void (*exit)(struct cgroup_subsys_state *css,
                 struct cgroup_subsys_state *old_css,
                 struct task_struct *task);

    /* 支撑 */
    void (*bind)(struct cgroup_subsys_state *root_css);

    /* 伪文件支持 */
    struct cftype *(*dfl_cftypes)(struct cgroup_subsys *ss);
    struct cftype *(*legacy_cftypes)(struct cgroup_subsys *ss);
};

/* 控制器数组 */
extern struct cgroup_subsys * const cgroup_subsys[];

/* 控制器列表 */
#define SUBSYS(_x) extern struct cgroup_subsys _x ## _cgrp_subsys;
CGROUP_SUBSYS_LIST
```

### 3.2 CPU 控制器

```c
/**
 * struct cpu_cgroup - CPU 控制器状态
 *
 * 实现 CPU 带宽控制和优先级
 */
struct cpu_cgroup {
    struct cgroup_subsys_state css;

    /* 权重 */
    unsigned int weight;
    unsigned int bandwidth_weight;

    /* 限制 */
    u64 cpu_cfs_quota_us;     // 带宽上限（微秒）
    u64 cpu_cfs_period_us;    // 周期（微秒）
    u64 cpu_rt_runtime_us;    // RT 运行时上限

    /* 本地统计 */
    u64 throttled_count;
    u64 throttle_count;

    /* 调度实体 */
    struct sched_entity se;
    struct cfs_rq cfs;
};
```

### 3.3 Memory 控制器

```c
/**
 * struct mem_cgroup - Memory 控制器状态
 *
 * 实现内存限制和统计
 */
struct mem_cgroup {
    struct cgroup_subsys_state css;

    /* 限制 */
    unsigned long memory_limit;           // 字节限制
    unsigned long soft_limit;            // 软限制
    unsigned long move_charge_at_immigrate; // 迁移时收费

    /* 统计 */
    atomic64_t memory_stat[MEMCG_NR_STAT];
    atomic64_t memory_events[MEMCG_NR_EVENTS];

    /* 使用量 */
    struct {
        atomic_long_t usage;
        unsigned long high;
        unsigned long max;
        unsigned long low;
    } memory;

    /* 交换限制 */
    unsigned long swap_limit;

    /* LRU 链表 */
    struct list_lru lruvec_lru;

    /* 内存阈值 */
    struct mem_cgroup_threshold *threshold;
    struct rb_root_cached threshold_root;

    /* OOM 事件 */
    wait_queue_head_t oom_waitq;
    struct oom_control {
        struct mem_cgroup *memcg;
        bool awakened;
    } oom;
};
```

## 4. cgroup v2 层级

### 4.1 cgroup v2 vs v1

```
┌─────────────────────────────────────────────────────────────────────┐
│                    cgroup v1 vs v2 Architecture                        │
│                                                                      │
│  cgroup v1 (多层级):                                                │
│  ┌─────────┐                                                       │
│  │  Root   │                                                       │
│  └────┬────┘                                                       │
│       │                                                              │
│  ┌────┴────┐                                                       │
│  │   A     │ (cpu)                                                 │
│  └────┬────┘                                                       │
│       │                    ┌─────────┐                              │
│  ┌────┴────┐               │   A     │ (memory)                    │
│  │   B     │               └────┬────┘                              │
│  └────┬────┘                    │                                   │
│       │                    ┌────┴────┐                              │
│  ┌────┴────┐               │   B     │                              │
│  │   C     │               └─────────┘                              │
│  └─────────┘                                                       │
│                                                                      │
│  cgroup v2 (单层级，统一树):                                         │
│  ┌─────────┐                                                       │
│  │  Root   │ (所有控制器)                                           │
│  └────┬────┘                                                       │
│       │                                                              │
│  ┌────┴────┐                                                       │
│  │   A     │                                                       │
│  └────┬────┘                                                       │
│       │                                                              │
│  ┌────┴────┐                                                       │
│  │   B     │                                                       │
│  └────┬────┘                                                       │
│       │                                                              │
│  ┌────┴────┐                                                       │
│  │   C     │                                                       │
│  └─────────┘                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 cgroup v2 根结构

```c
/**
 * struct cgroup_root - cgroup 层级根
 *
 * cgroup v2 只有一个根
 */
struct cgroup_root {
    /* 层级 ID */
    int level;

    /* 根 cgroup */
    struct cgroup cgroup;

    /* 控制器掩码 */
    u16 subsys_mask;

    /* 控制器标志 */
    u16 flags;

    /* 根目录 */
    struct dentry *root_dentry;

    /* 超级块 */
    struct super_block *sb;

    /* cgroupfs 特定 */
    struct kernfs_root *kf_root;
};

/**
 * cgroup_root - 全局根 cgroup
 */
struct cgroup_root cgroup_root = {
    .cgroup = {
        .root = &cgroup_root,
        .level = 0,
    },
};
```

### 4.3 cgroup v2 控制器启用

```c
/*
 * cgroup v2 控制器启用
 *
 * 通过 cgroup.subtree_control 启用控制器
 *
 * 例如：
 *   echo +cpu +memory > /sys/fs/cgroup/A/cgroup.subtree_control
 *
 * 启用后，该 cgroup 的所有子 cgroup 都受控制器限制
 */
static int cgroup_attach(struct cgroup *dst_cgrp,
                        struct cgroup *src_cgrp,
                        struct task_struct *leader,
                        struct list_head *tg_list)
{
    struct css_set *src_cset, *dst_cset;
    struct task_struct *task;
    int ret;

    /* 移动每个任务 */
    list_for_each_entry(task, tg_list, cg_list) {
        /* 获取源 CSS */
        src_cset = task_css_set(task);

        /* 分配新的 CSS */
        dst_cset = allocate_cset(dst_cgrp, src_cset);

        /* 替换任务 CSS */
        ret = reassign_css_set(task, dst_cset);
        if (ret)
            return ret;
    }

    return 0;
}
```

## 5. 任务迁移

### 5.1 CSS Set 结构

```c
/**
 * struct css_set - CSS 集合
 *
 * 代表一个 cgroup CSS 的组合
 */
struct css_set {
    /* 引用计数 */
    refcount_t refcount;

    /* CSS 数组 */
    struct cgroup_subsys_state *subsys[CGROUP_SUBSYS_COUNT];

    /* 任务链表 */
    struct list_head task_list;

    /* 哈希链表 */
    struct hlist_node hlist;

    /* 进程链表 */
    struct list_head process_list;
};

/**
 * css_set_hash - CSS Set 哈希表
 *
 * 用于快速查找给定 cgroup 组合的 CSS Set
 */
#define css_set_hash(_css) (hash_long((unsigned long)(_css), CSS_HASH_BITS))

static struct list_head *css_set_hashtable;
static int css_set_hashtable_size;
```

### 5.2 任务迁移流程

```c
/**
 * cgroup_task_migrate - 迁移任务到新的 cgroup
 *
 * @task: 要迁移的任务
 * @old_cset: 旧的 CSS Set
 * @new_cset: 新的 CSS Set
 */
void cgroup_task_migrate(struct task_struct *task,
                        struct css_set *old_cset,
                        struct css_set *new_cset)
{
    struct cgroup_subsys_state *css, *old_css;

    /* 锁定任务 */
    get_online_cpus();

    /* 通知控制器任务将要离开 */
    for (each_subsys(ss, i) {
        old_css = old_cset->subsys[i];
        css = new_cset->subsys[i];

        if (old_css != css && ss->task_sleep)
            ss->task_sleep(task);
    }

    /* 替换任务的 CSS Set */
    rcu_assign_pointer(task->cgroups, new_cset);

    /* 移动任务到新链表中 */
    list_move(&task->cg_list, &new_cset->task_list);

    /* 通知控制器任务已到达 */
    for (each_subsys(ss, i) {
        css = new_cset->subsys[i];

        if (old_css != css && ss->task_woken)
            ss->task_woken(css, task);
    });

    put_online_cpus();
}

/**
 * reassign_css_set - 重新分配任务的 CSS Set
 */
static int reassign_css_set(struct task_struct *task,
                           struct css_set *new_cset)
{
    struct css_set *old_cset;

    old_cset = task_css_set(task);

    /* 如果相同，无需操作 */
    if (old_cset == new_cset)
        return 0;

    /* 增加新 CSS Set 引用 */
    css_set_get(new_cset);

    /* 迁移任务 */
    cgroup_task_migrate(task, old_cset, new_cset);

    /* 释放旧 CSS Set 引用 */
    css_set_put(old_cset);

    return 0;
}
```

## 6. 资源限制算法

### 6.1 CPU 带宽控制

```c
/**
 * cpu_cfs_period - 设置 CPU 带宽周期
 *
 * 公式：bandwidth = quota / period
 *
 * 例如：quota=50000, period=100000
 *       bandwidth = 50% CPU
 */
static int cpu_cfs_period_write(struct kernfs_open_file *of,
                               char *buf, size_t nbytes, loff_t off)
{
    u64 period = 0;
    int err;

    err = page_counter_memparse(buf, "-1", &period);
    if (err)
        return err;

    if (period < 1 || period > 1e6)  /* 限制在 1ms - 1s */
        return -EINVAL;

    spin_lock_irq(&cgroup_threadgroup_lock());

    cgroup_subsys_state(of->kn->parent, cpu_cgroup);

    css->cpu_cfs_period_us = period;

    /* 更新调度器参数 */
    sched_cfs_period_us(css->cgroup, period);

    spin_unlock_irq(&cgroup_threadgroup_lock());

    return nbytes;
}

/**
 * cpu_cfs_quota - 设置 CPU 带宽上限
 *
 * quota = -1 表示无限制
 */
static int cpu_cfs_quota_write(struct kernfs_open_file *of,
                              char *buf, size_t nbytes, loff_t off)
{
    s64 quota = -1;
    int err;

    err = page_counter_memparse(buf, "-1", &quota);
    if (err)
        return err;

    if (quota < -1 || quota > NSEC_PER_SEC)  /* 限制在 0 - 1s */
        return -EINVAL;

    spin_lock_irq(&cgroup_threadgroup_lock());

    css->cpu_cfs_quota_us = quota;

    /* 更新调度器参数 */
    sched_cfs_quota_us(css->cgroup, quota);

    spin_unlock_irq(&cgroup_threadgroup_lock());

    return nbytes;
}
```

### 6.2 Memory 限制

```c
/**
 * mem_cgroup_usage - 获取内存使用量
 *
 * @memcg: memory cgroup
 * @swapped: 是否包含交换使用
 */
static inline u64 mem_cgroup_usage(struct mem_cgroup *memcg, bool swapped)
{
    u64 usage;

    usage = atomic_long_read(&memcg->memory.usage);

    if (swapped)
        usage += atomic_long_read(&memcg->swap.usage);

    return usage;
}

/**
 * memory_high_write - 设置内存高水位
 *
 * 当使用量超过 high 时，触发异步回收
 */
static int memory_high_write(struct kernfs_open_file *of,
                            char *buf, size_t nbytes, loff_t off)
{
    struct mem_cgroup *memcg = mem_cgroup_from_css(of_css(of));
    unsigned long high;

    /* 解析限制值 */
    err = page_counter_memparse(buf, "max", &high);
    if (err)
        return err;

    /* 设置新的 high 值 */
    WRITE_ONCE(memcg->memory.high, high);

    /* 触发回收检查 */
    memcg_schedule_reclaim(memcg);

    return nbytes;
}
```

## 7. cgroupfs 实现

### 7.1 cftype 结构

```c
/**
 * struct cftype - cgroup 伪文件类型
 *
 * 定义 cgroupfs 中的文件行为
 */
struct cftype {
    /* 文件名 */
    char name[CGROUP_FILE_NAME_MAX];

    /* 文件模式 */
    umode_t mode;

    /* 文件标志 */
    unsigned int flags;

    /* 操作 */
    ssize_t (*read)(struct kernfs_open_file *of, char *buf,
                    size_t nbytes, loff_t off);
    ssize_t (*write)(struct kernfs_open_file *of, const char *buf,
                     size_t nbytes, loff_t off);

    /* seqfile 支持 */
    int (*seq_show)(struct seq_file *m, void *v);

    /* poll 支持 */
    __poll_t (*poll)(struct kernfs_open_file *of,
                     struct poll_table_struct *pt);

    /* 释放 */
    void (*release)(struct kernfs_open_file *of);

    /* 属性 */
    const struct kernfs_ops *ops;

    /* 私有数据 */
    void *private;
};

/* CFTYPE flags */
#define CFTYPE_WORLD_WRITABLE        (1 << 0)
#define CFTYPE_NOT_ON_ROOT          (1 << 1)
#define CFTYPE_NO_PREFIX            (1 << 2)
#define CFTYPE_DEBUG               (1 << 3)
```

### 7.2 控制器伪文件

```c
/*
 * CPU 控制器文件：
 * - cpu.stat
 * - cpu.weight
 * - cpu.max
 * - cpu.cfs_quota_us
 * - cpu.cfs_period_us
 */

/*
 * Memory 控制器文件：
 * - memory.current
 * - memory.high
 * - memory.max
 * - memory.low
 * - memory.min
 * - memory.swap.current
 * - memory.swap.max
 * - memory.events
 */

/**
 * cgroup_file_type - 确定文件类型
 */
static int cgroup_file_type(const struct cftype *cft)
{
    if (cft->seq_show)
        return CGROUP_FILE_TYPE_SEQ;
    if (cft->read)
        return CGROUP_FILE_TYPE_REGULAR;
    return CGROUP_FILE_TYPE_UNKNOWN;
}
```

## 8. cgroup v2 特性

### 8.1 委托（Delegation）

```c
/*
 * cgroup v2 委托机制
 *
 * 允许用户拥有子 cgroup 的管理权限
 *
 * 委托操作：
 * 1. 创建子 cgroup
 * 2. 在子 cgroup 上设置资源限制
 * 3. 移动任务到子 cgroup
 *
 * 委托限制：
 * - 不能修改父 cgroup 的设置
 * - 不能移动任务到父 cgroup
 */

/**
 * cgroup_can_attach - 检查是否可以附加任务
 *
 * 检查任务是否可以移动到目标 cgroup
 */
static int cgroup_can_attach(struct cgroup_subsys_state *css,
                            struct task_struct *task)
{
    /* 检查权限 */
    if (!uid_eq(current_euid(), GLOBAL_ROOT_UID) &&
        !uid_eq(current_euid(), task_uid(task)))
        return -EPERM;

    /* 检查 cgroup 是否允许新任务 */
    if (cgroup_control(css->cgroup) & CGRP_CLONE_CHILDREN)
        return 0;

    return -EACCES;
}
```

### 8.2 线程模式（Thread Mode）

```c
/*
 * cgroup v2 线程模式
 *
 * 允许 cgroup 中的线程使用不同的 cgroup
 *
 * 线程模式下：
 * - 进程的线程可以属于不同的 cgroup
 * - 使用 threaded 模式创建子 cgroup
 */

/**
 * cgroup_threads_write - 设置线程模式
 */
static ssize_t cgroup_threads_write(struct kernfs_open_file *of,
                                    char *buf, size_t nbytes, loff_t off)
{
    int enable;

    /* 解析 enable 值 */
    enable = parse_yes_no(buf);

    spin_lock_irq(&cgroup_threadgroup_lock());

    if (enable)
        cgroup_enable_thread(css->cgroup);
    else
        cgroup_disable_thread(css->cgroup);

    spin_unlock_irq(&cgroup_threadgroup_lock());

    return nbytes;
}
```

## 9. 核心算法分析

### 9.1 CSS Set 查找

```c
/*
 * css_set 查找算法：
 *
 * 1. 计算 CSS 数组的哈希值
 * 2. 在哈希表中查找匹配的 css_set
 * 3. 如果找到，返回引用
 * 4. 如果未找到，分配新的 css_set
 *
 * 时间复杂度：O(1) 平均，O(n) 最坏
 */
struct css_set *find_css_set(struct css_set *old_cset,
                            struct cgroup *cgrp)
{
    struct css_set *cset;
    struct cgroup_subsys_state *csss[CGROUP_SUBSYS_COUNT];
    int i;

    /* 收集新的 CSS 组合 */
    for (i = 0; i < CGROUP_SUBSYS_COUNT; i++) {
        csss[i] = old_cset->subsys[i];
        if (csss[i]->cgroup == cgrp)
            csss[i] = cgrp->subsys[i];
    }

    /* 查找或创建 CSS Set */
    hash_for_each_possible(css_set_hashtable, cset, hlist,
                          css_set_hash(csss)) {
        if (match_css_set(cset, csss))
            goto found;
    }

    /* 分配新的 CSS Set */
    cset = alloc_css_set(csss);
    hash_add(css_set_hashtable, &cset->hlist, css_set_hash(csss));

found:
    css_set_get(cset);
    return cset;
}
```

### 9.2 层级遍历

```c
/*
 * cgroup 层级遍历算法：
 *
 * 1. css_for_each_descendant_pre: 先序遍历
 *    使用栈模拟递归，避免栈溢出
 *
 * 2. css_for_each_descendant_post: 后序遍历
 *    使用栈 + 标记实现
 *
 * 时间复杂度：O(n) 其中 n 是后代数量
 */
```

## 10. 参考资料

- `kernel/cgroup/cgroup.c` - cgroup 核心实现
- `kernel/cgroup/css.c` - CSS 实现
- `kernel/cgroup/cgroupfs.c` - cgroupfs 实现
- `kernel/cgroup/cgroup1.c` - cgroup v1 兼容
- `kernel/cgroup/cpu_cgroup.c` - CPU 控制器
- `kernel/cgroup/mem_cgroup.c` - Memory 控制器
- `include/linux/cgroup.h` - cgroup 头文件
- `include/linux/cgroup_defs.h` - cgroup 定义
- Documentation/cgroup-v2/
- kernel-cgroup.txt
