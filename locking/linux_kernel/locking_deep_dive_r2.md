# Linux Locking 子系统深度分析 R2

## 目录
1. [spinlock 实现分析](#1-spinlock-实现分析)
2. [mutex 实现分析](#2-mutex-实现分析)
3. [rwsem 实现分析](#3-rwsem-读写信号量实现分析)
4. [percpu 机制分析](#4-percpu-机制分析)
5. [lockdep 依赖验证机制](#5-lockdep-依赖验证机制)
6. [知识点关联表](#6-知识点关联表)

---

## 1. spinlock 实现分析

### 1.1 数据结构布局

**raw_spinlock_t 结构体** (`include/linux/spinlock_types_raw.h:14-24`)
```c
context_lock_struct(raw_spinlock) {
    arch_spinlock_t raw_lock;        // 架构相关的自旋锁
#ifdef CONFIG_DEBUG_SPINLOCK
    unsigned int magic, owner_cpu;   // 调试信息
    void *owner;
#endif
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lockdep_map dep_map;      // lockdep 依赖图节点
#endif
};
```

**RAW_LOCK_INIT 初始化宏** (`include/linux/spinlock_types_raw.h:63-67`)
```c
#define __RAW_SPIN_LOCK_INITIALIZER(lockname)   \
{                                               \
    .raw_lock = __ARCH_SPIN_LOCK_UNLOCKED,      \
    SPIN_DEBUG_INIT(lockname)                   \
    RAW_SPIN_DEP_MAP_INIT(lockname) }
```

### 1.2 spin_lock/unlock 实现

**核心实现** (`kernel/locking/spinlock.c:136-213`)

spinlock 的实现采用宏展开方式，核心实现在 `spinlock_api_smp.h` 中:

```c
// spinlock.c:152-155 - spin_lock 入口
static inline void __raw_spin_lock(raw_spinlock_t *lock)
    __acquires(lock) __no_context_analysis
{
    preempt_disable();
    spin_acquire(&lock->dep_map, 0, 0, _RET_IP_);
    LOCK_CONTENDED(lock, do_raw_spin_trylock, do_raw_spin_lock);
}

// spinlock.c:164-170 - spin_unlock 实现
static inline void __raw_spin_unlock(raw_spinlock_t *lock)
    __releases(lock)
{
    spin_release(&lock->dep_map, _RET_IP_);
    do_raw_spin_unlock(lock);
    preempt_enable();
}
```

**trylock 实现** (`kernel/locking/spinlock.c:136-140`):
```c
static inline int __raw_spin_trylock(raw_spinlock_t *lock)
    __cond_acquires(true, lock)
{
    preempt_disable();
    if (do_raw_spin_trylock(lock)) {
        spin_acquire(&lock->dep_map, 0, 1, _RET_IP_);
        return 1;
    }
    preempt_enable();
    return 0;
}
```

### 1.3 x86 qspinlock (队列自旋锁)

x86 架构使用 **qspinlock** 替代传统的 ticket spinlock，通过 MCS 队列避免高速缓存行弹跳。

**qspinlock 结构** (`include/asm-generic/qspinlock_types.h:14-44`):
```c
typedef struct qspinlock {
    union {
        atomic_t val;
#ifdef __LITTLE_ENDIAN
        struct {
            u8  locked;      // 锁定字节
            u8  pending;     // 待处理位
        };
        struct {
            u16 locked_pending;
            u16 tail;        // 队尾 CPU ID
        };
#endif
    };
} arch_spinlock_t;
```

**位域定义** (`include/asm-generic/qspinlock_types.h:67-93`):
- Bit 0-7: locked byte (锁持有标志)
- Bit 8: pending (等待标志)  
- Bit 9-10: tail index (队尾索引，在 NR_CPUS >= 16K 时使用)
- Bit 11-31: tail cpu (队尾 CPU 编号 + 1)

**加锁流程** (`include/asm-generic/qspinlock.h:107-115`):
```c
static __always_inline void queued_spin_lock(struct qspinlock *lock)
{
    int val = 0;
    if (likely(atomic_try_cmpxchg_acquire(&lock->val, &val, _Q_LOCKED_VAL)))
        return;
    queued_spin_lock_slowpath(lock, val);  // 进入慢路径
}
```

**解锁流程** (`include/asm-generic/qspinlock.h:123-129`):
```c
static __always_inline void queued_spin_unlock(struct qspinlock *lock)
{
    smp_store_release(&lock->locked, 0);  // 释放语义
}
```

### 1.4 Ticket Spinlock vs MCS 队列对比

| 特性 | Ticket Spinlock | MCS Queue Spinlock (qspinlock) |
|------|-----------------|--------------------------------|
| 实现复杂度 | 简单 | 复杂 |
| 缓存行弹跳 | 所有等待者轮询同一缓存行 | 仅相邻节点交互 |
| 公平性 | FIFO 严格 | FIFO 严格 |
| 扩展性 | 差 (2^16 CPU 上限) | 好 (无实质限制) |
| 内存开销 | O(1) | O(n) 但每个节点仅 3 个字 |

Linux 现代版本默认使用 qspinlock，但通过 `arch/x86/include/asm/spinlock.h:26` 条件引入。

### 1.5 内存屏障

spinlock 实现依赖架构特定的内存序:
- **加锁**: `atomic_try_cmpxchg_acquire()` - acquire 语义确保临界区访问前的操作不会重排到临界区内
- **解锁**: `smp_store_release()` - release 语义确保临界区内的操作不会重排到临界区外

---

## 2. mutex 实现分析

### 2.1 数据结构布局

**struct mutex** (`kernel/locking/mutex.c:21` + 隐式定义):
```c
struct mutex {
    atomic_long_t owner;           // 持有者 + 标志位
    raw_spinlock_t wait_lock;      // 保护等待队列
    struct list_head wait_list;     // 等待者链表 (FIFO)
#ifdef CONFIG_MUTEX_SPIN_ON_OWNER
    struct optimistic_spin_queue osq;  // MCS 队列用于乐观自旋
#endif
#ifdef CONFIG_DEBUG_MUTEXES
    void *magic;
#endif
};
```

**owner 字段编码** (`kernel/locking/mutex.c:57-71`):
```c
// 最低 3 位为标志位
#define MUTEX_FLAG_WAITERS    0x01  // 有等待者
#define MUTEX_FLAG_HANDOFF    0x02  // 移交标志
#define MUTEX_FLAG_PICKUP     0x04  // 拾取标志

static inline struct task_struct *__owner_task(unsigned long owner)
{
    return (struct task_struct *)(owner & ~MUTEX_FLAGS);
}
```

### 2.2 fast/slow path 设计

**快速路径 (无竞争)** (`kernel/locking/mutex.c:152-163`):
```c
static __always_inline bool __mutex_trylock_fast(struct mutex *lock)
{
    unsigned long curr = (unsigned long)current;
    unsigned long zero = 0UL;

    if (atomic_long_try_cmpxchg_acquire(&lock->owner, &zero, curr))
        return true;  // 成功获取锁
    return false;
}
```

**慢速路径入口** (`kernel/locking/mutex.c:262-291`):
```c
void __sched mutex_lock(struct mutex *lock)
{
    might_sleep();
    if (!__mutex_trylock_fast(lock))    // 先尝试快速路径
        __mutex_lock_slowpath(lock);    // 失败则进入慢路径
}
```

**慢速路径核心** (`kernel/locking/mutex.c:577-770`):
```c
static __always_inline int __sched
__mutex_lock_common(struct mutex *lock, unsigned int state, ...)
{
    // ... 
    preempt_disable();
    mutex_acquire_nest(&lock->dep_map, ...);
    
    // 尝试乐观自旋
    if (__mutex_trylock(lock) ||
        mutex_optimistic_spin(lock, ww_ctx, NULL)) {
        lock_acquired(&lock->dep_map, ip);
        preempt_enable();
        return 0;
    }
    
    // 获取等待锁并加入等待队列
    raw_spin_lock_irqsave(&lock->wait_lock, flags);
    __mutex_add_waiter(lock, &waiter, &lock->wait_list);
    
    // 睡眠等待
    for (;;) {
        if (__mutex_trylock(lock))
            goto acquired;
        if (signal_pending_state(state, current)) {
            ret = -EINTR;
            goto err;
        }
        raw_spin_unlock_irqrestore_wake(&lock->wait_lock, flags, &wake_q);
        schedule_preempt_disabled();
        raw_spin_lock_irqsave(&lock->wait_lock, flags);
    }
}
```

### 2.3 mutex_trylock 实现

**trylock 核心** (`kernel/locking/mutex.c:84-118`):
```c
static inline struct task_struct *__mutex_trylock_common(struct mutex *lock, bool handoff)
{
    unsigned long owner, curr = (unsigned long)current;
    owner = atomic_long_read(&lock->owner);
    
    for (;;) {  // 循环处理竞态
        unsigned long flags = __owner_flags(owner);
        unsigned long task = owner & ~MUTEX_FLAGS;
        
        if (task) {
            if (flags & MUTEX_FLAG_PICKUP) {
                if (task != curr)
                    break;  // 被其他任务持有
                flags &= ~MUTEX_FLAG_PICKUP;
            } else if (handoff) {
                if (flags & MUTEX_FLAG_HANDOFF)
                    break;
                flags |= MUTEX_FLAG_HANDOFF;
            } else {
                break;  // 锁已被持有
            }
        } else {
            // 锁空闲，尝试获取
            task = curr;
        }
        
        // CAS 操作获取锁
        if (atomic_long_try_cmpxchg_acquire(&lock->owner, &owner, task | flags)) {
            if (task == curr)
                return NULL;  // 成功
            break;
        }
    }
    return __owner_task(owner);  // 返回当前持有者
}
```

### 2.4 osq_lock (乐观自旋队列)

**osq_node 结构** (`kernel/locking/osq_lock.c:15-19`):
```c
struct optimistic_spin_node {
    struct optimistic_spin_node *next, *prev;
    int locked;   // 1 = 锁已被持有
    int cpu;      // 编码的 CPU 编号 + 1
};
DEFINE_PER_CPU_SHARED_ALIGNED(struct optimistic_spin_node, osq_node);
```

**osq_lock 实现** (`kernel/locking/osq_lock.c:93-208`):
```c
bool osq_lock(struct optimistic_spin_queue *lock)
{
    struct optimistic_spin_node *node = this_cpu_ptr(&osq_node);
    struct optimistic_spin_node *prev, *next;
    int curr = encode_cpu(smp_processor_id());
    
    node->locked = 0;
    node->next = NULL;
    node->cpu = curr;
    
    // 原子操作入队
    old = atomic_xchg(&lock->tail, curr);
    if (old == OSQ_UNLOCKED_VAL)
        return true;  // 锁空闲，直接获取
    
    prev = decode_cpu(old);
    node->prev = prev;
    
    smp_wmb();  // 内存屏障确保 prev->next 顺序
    
    WRITE_ONCE(prev->next, node);  // 加入 MCS 队列
    
    // 等待锁或被取消
    if (smp_cond_load_relaxed(&node->locked, VAL || need_resched() || ...))
        return true;
    
    // 出队逻辑...
}
```

**osq_unlock 实现** (`kernel/locking/osq_lock.c:210-234`):
```c
void osq_unlock(struct optimistic_spin_queue *lock)
{
    struct optimistic_spin_node *node, *next;
    int curr = encode_cpu(smp_processor_id());
    
    // 快速路径：无竞争时直接解锁
    if (atomic_try_cmpxchg_release(&lock->tail, &curr, OSQ_UNLOCKED_VAL))
        return;
    
    // 通知下一个等待者
    node = this_cpu_ptr(&osq_node);
    next = xchg(&node->next, NULL);
    if (next) {
        WRITE_ONCE(next->locked, 1);  // 唤醒
        return;
    }
    next = osq_wait_next(lock, node, OSQ_UNLOCKED_VAL);
    if (next)
        WRITE_ONCE(next->locked, 1);
}
```

**活锁避免机制**: osq_lock 确保同一时刻只有一个 spinner 尝试自旋等待，通过 MCS 队列严格序列化竞争者，防止多 spinner 同时自旋导致的性能退化。

---

## 3. rwsem 读写信号量实现分析

### 3.1 数据结构布局

**struct rw_semaphore** (`kernel/locking/rwsem.c:33` + 隐式定义):
```c
struct rw_semaphore {
    atomic_long_t count;           // 计数器
    raw_spinlock_t wait_lock;     // 保护等待队列
    struct list_head wait_list;    // 等待者链表
#ifdef CONFIG_RWSEM_SPIN_ON_OWNER
    struct optimistic_spin_queue osq;  // 乐观自旋队列
#endif
    atomic_long_t owner;           // 持有者 (调试用)
#ifdef CONFIG_DEBUG_RWSEMS
    void *magic;
#endif
};
```

### 3.2 count 位域设计

**位域定义** (`kernel/locking/rwsem.c:118-129`):
```c
#define RWSEM_WRITER_LOCKED     (1UL << 0)    // 写者锁定位
#define RWSEM_FLAG_WAITERS      (1UL << 1)    // 等待者存在位
#define RWSEM_FLAG_HANDOFF      (1UL << 2)    // 移交位
#define RWSEM_FLAG_READFAIL     (1UL << (BITS_PER_LONG - 1))  // 读者失败位

#define RWSEM_READER_SHIFT      8              // 读者计数偏移
#define RWSEM_READER_BIAS       (1UL << RWSEM_READER_SHIFT)
```

**64位架构 count 位布局**:
- Bit 0: writer locked bit
- Bit 1: waiters present bit  
- Bit 2: lock handoff bit
- Bit 3-7: reserved
- Bit 8-62: 55-bit reader count
- Bit 63: read fail bit

### 3.3 read_lock/write_lock 语义

**读锁获取** (`kernel/locking/rwsem.c:249-262`):
```c
static inline bool rwsem_read_trylock(struct rw_semaphore *sem, long *cntp)
{
    *cntp = atomic_long_add_return_acquire(RWSEM_READER_BIAS, &sem->count);
    
    if (WARN_ON_ONCE(*cntp < 0))
        rwsem_set_nonspinnable(sem);
    
    if (!(*cntp & RWSEM_READ_FAILED_MASK)) {
        rwsem_set_reader_owned(sem);
        return true;
    }
    return false;
}
```

**写锁获取** (`kernel/locking/rwsem.c:264-274`):
```c
static inline bool rwsem_write_trylock(struct rw_semaphore *sem)
{
    long tmp = RWSEM_UNLOCKED_VALUE;
    
    if (atomic_long_try_cmpxchg_acquire(&sem->count, &tmp, RWSEM_WRITER_LOCKED)) {
        rwsem_set_owner(sem);
        return true;
    }
    return false;
}
```

### 3.4 Writer 乐观自旋

**写锁慢路径** (`kernel/locking/rwsem.c:1110-1208`):
```c
static struct rw_semaphore __sched *
rwsem_down_write_slowpath(struct rw_semaphore *sem, int state)
{
    // 首先尝试乐观自旋
    if (rwsem_can_spin_on_owner(sem) && rwsem_optimistic_spin(sem))
        return sem;  // 自旋获取成功
    
    // 加入等待队列
    waiter.task = current;
    waiter.type = RWSEM_WAITING_FOR_WRITE;
    
    raw_spin_lock_irq(&sem->wait_lock);
    rwsem_add_waiter(sem, &waiter);
    
    // 设置 HANDOFF 标志以便锁持有者直接移交
    if (waiter.handoff_set) {
        // 自旋等待 owner 变为 NULL
        if (rwsem_spin_on_owner(sem) == OWNER_NULL)
            goto trylock_again;
    }
    
    schedule_preempt_disabled();
}
```

**乐观自旋条件检查** (`kernel/locking/rwsem.c:704-729`):
```c
static inline bool rwsem_can_spin_on_owner(struct rw_semaphore *sem)
{
    struct task_struct *owner;
    unsigned long flags;
    
    if (need_resched())
        return false;
    
    owner = rwsem_owner_flags(sem, &flags);
    
    // 不可自旋条件:
    // 1. 锁被标记为非自旋
    // 2. 持有者是读者
    // 3. 持有者不在运行
    if ((flags & RWSEM_NONSPINNABLE) ||
        (owner && !(flags & RWSEM_READER_OWNED) && !owner_on_cpu(owner)))
        return false;
    
    return true;
}
```

### 3.5 读者批唤醒

**rwsem_mark_wake** (`kernel/locking/rwsem.c:410-567`) 实现读者批唤醒，一次最多唤醒 `MAX_READERS_WAKEUP` (0x100) 个读者。

---

## 4. percpu 机制分析

### 4.1 DEFINE_PER_CPU 实现

**宏定义** (`include/linux/percpu-defs.h:110-114`):
```c
#define DECLARE_PER_CPU(type, name) \
    DECLARE_PER_CPU_SECTION(type, name, "")

#define DEFINE_PER_CPU(type, name) \
    DEFINE_PER_CPU_SECTION(type, name, "")
```

**节段属性** (`include/linux/percpu-defs.h:47-49`):
```c
#define __PCPU_ATTRS(sec) \
    __percpu __attribute__((section(PER_CPU_BASE_SECTION sec))) \
    PER_CPU_ATTRIBUTES
```

每个 CPU 有一个独立的 percpu 副本，位于不同的内存区域。

### 4.2 percpu_read/write 实现

**per_cpu_ptr** (`include/linux/percpu-defs.h:237-241`):
```c
#define per_cpu_ptr(ptr, cpu) \
({  __verify_pcpu_ptr(ptr); \
    SHIFT_PERCPU_PTR((ptr), per_cpu_offset((cpu))); \
})
```

**this_cpu_read** (`include/linux/percpu-defs.h:499`):
```c
#define this_cpu_read(pcp) __pcpu_size_call_return(this_cpu_read_, pcp)
```

编译时根据变量大小展开为 `this_cpu_read_1/2/4/8`，直接操作当前 CPU 的 percpu 副本。

### 4.3 percpu_counter 结构

**percpu_counter** (`include/linux/percpu_counter.h:22-29`):
```c
struct percpu_counter {
    raw_spinlock_t lock;      // 保护全局计数
    s64 count;                // 全局计数 (近似值)
#ifdef CONFIG_HOTPLUG_CPU
    struct list_head list;    // 热插拔 CPU 链表
#endif
    s32 __percpu *counters;   // 每 CPU 本地计数数组
};
```

**批量同步机制**: percpu_counter 使用批量更新减少锁竞争:
- 本地更新先存入 `counters[cpu]`
- 调用 `percpu_counter_sum()` 时才累加所有本地计数到全局 `count`

### 4.4 percpu 内存屏障和同步

percpu 操作天然提供内存序保证:
- `raw_cpu_read()` / `raw_cpu_write()`: 无额外屏障，依赖 CPU 内存序
- `__this_cpu_read()` / `__this_cpu_write()`: 调试模式下检查 preempt 状态
- `this_cpu_read()` / `this_cpu_write()`: 无保护，适用于原子上下文中

**跨 CPU 同步**: 涉及跨 CPU 访问时需要显式内存屏障:
```c
// percpu 操作在跨 CPU 场景下的顺序性由以下保证
smp_mb();  // 确保所有 CPU 看到一致的内存视图
```

---

## 5. lockdep 依赖验证机制

### 5.1 依赖图构建

**核心数据结构** (`kernel/locking/lockdep.c:207-225`):
```c
// 锁类节点
struct lock_class {
    struct lockdep_subclass_key *key;
    struct list_head locks_after;     // 依赖此锁的锁列表
    struct list_head locks_before;    // 此锁依赖的锁列表
    // ...
};

// 依赖边
struct lock_list {
    struct list_head entry;
    struct lock_class *class;
    struct lock_class *links_to;      // 指向目标锁类
    u8 dep;                           // 依赖类型 (ER/SR/EN/SN)
    u16 distance;                     // 距离
    struct lock_trace *trace;         // 获取时的栈回溯
    // ...
};
```

**全局变量** (`kernel/locking/lockdep.c:207-224`):
```c
unsigned long nr_list_entries;
static struct lock_list list_entries[MAX_LOCKDEP_ENTRIES];
struct lock_class lock_classes[MAX_LOCKDEP_KEYS];

// 哈希表加速查找
#define CLASSHASH_SIZE (1UL << CLASSHASH_BITS)
static struct hlist_head classhash_table[CLASSHASH_SIZE];
```

**注册锁类** (`kernel/locking/lockdep.c:1284-1394`):
```c
static struct lock_class *register_lock_class(struct lockdep_map *lock, 
                                              unsigned int subclass, int force)
{
    // 1. 查找或分配 lock_class
    class = look_up_lock_class(lock, subclass);
    if (likely(class)) goto out_set_class_cache;
    
    // 2. 分配新类
    class = list_first_entry_or_null(&free_lock_classes, ...);
    // ...
    
    // 3. 加入全局链表和哈希表
    hlist_add_head_rcu(&class->hash_entry, hash_head);
    list_move_tail(&class->lock_entry, &all_lock_classes);
}
```

### 5.2 环检测算法 (BFS)

**循环队列** (`kernel/locking/lockdep.c:1469-1526`):
```c
struct circular_queue {
    struct lock_list *element[MAX_CIRCULAR_QUEUE_SIZE];
    unsigned int front, rear;
};

static struct circular_queue lock_cq;

static inline int __cq_enqueue(struct circular_queue *cq, struct lock_list *elem)
{
    if (__cq_full(cq)) return -1;
    cq->element[cq->rear] = elem;
    cq->rear = (cq->rear + 1) & CQ_MASK;
    return 0;
}
```

**BFS 搜索** (`kernel/locking/lockdep.c:1733-1839`):
```c
static enum bfs_result __bfs(struct lock_list *source_entry, ...)
{
    struct circular_queue *cq = &lock_cq;
    struct lock_list *lock = NULL;
    
    __cq_init(cq);
    __cq_enqueue(cq, source_entry);
    
    while ((lock = __bfs_next(lock, offset)) || (lock = __cq_dequeue(cq))) {
        if (lock_accessed(lock)) continue;  // 已访问
        mark_lock_accessed(lock);
        
        // 强依赖路径检查 -(*R)-> -(S*)-> 不是强依赖
        if (lock->parent) {
            u8 dep = lock->dep;
            bool prev_only_xr = lock->parent->only_xr;
            
            if (prev_only_xr)
                dep &= ~(DEP_SR_MASK | DEP_SN_MASK);
            if (!dep) continue;
            
            lock->only_xr = !(dep & (DEP_SN_MASK | DEP_EN_MASK));
        }
        
        if (match(lock, data))    // 找到目标
            return BFS_RMATCH;
        
        // 扩展搜索图
        list_for_each_entry_rcu(entry, &lock->class->locks_after, entry) {
            visit_lock_entry(entry, lock);
            if (__cq_enqueue(cq, entry)) return BFS_EQUEUEFULL;
        }
    }
    return BFS_RNOMATCH;
}
```

### 5.3 锁顺序验证

**check_prev_add** (`kernel/locking/lockdep.c:3121-3199`) 在每次加锁时执行验证:
```c
static int check_prev_add(struct task_struct *curr, 
                         struct held_lock *prev,
                         struct held_lock *next, ...)
{
    // 1. 检查循环依赖
    ret = check_noncircular(next, prev, trace);
    if (unlikely(bfs_error(ret) || ret == BFS_RMATCH))
        return 0;  // 检测到循环
    
    // 2. 检查 IRQ 安全性
    if (!check_irq_usage(curr, prev, next))
        return 0;
    
    // 3. 添加依赖边
    list_for_each_entry(entry, &hlock_class(prev)->locks_after, entry) {
        if (entry->class == hlock_class(next)) {
            entry->dep |= calc_dep(prev, next);  // 更新依赖类型
            return 1;
        }
    }
    // 添加新依赖边...
}
```

### 5.4 强依赖路径

**依赖类型** (`kernel/locking/lockdep.c:1620-1639`):
```c
#define DEP_SR_BIT 0  // 共享读 -> 递归读
#define DEP_ER_BIT 1   // 互斥 -> 递归读  
#define DEP_SN_BIT 2   // 共享读 -> 非递归
#define DEP_EN_BIT 3   // 互斥 -> 非递归

// 强依赖: 不包含 -(*R)-> -(S*)-> 模式
```

**hlock_conflict** (`kernel/locking/lockdep.c:1996-2003`):
```c
static inline bool hlock_conflict(struct lock_list *entry, void *data)
{
    struct held_lock *hlock = (struct held_lock *)data;
    
    return hlock_class(hlock) == entry->class &&
           (hlock->read == 0 || !entry->only_xr);
    // B -> A 是 -(E*)-> 或 A -> .. -> B 是 -(*N)->
}
```

---

## 6. 知识点关联表

| 组件 | 核心结构 | 关键算法 | 同步原语 | 典型应用 |
|------|---------|---------|---------|---------|
| **spinlock** | `raw_spinlock_t` / `qspinlock` | MCS 队列 | atomic_cmpxchg_acquire | 中断上下文、短期保护 |
| **mutex** | `struct mutex` | osq_lock 乐观自旋 | atomic_long_try_cmpxchg | 进程上下文、长期等待 |
| **rwsem** | `struct rw_semaphore` | writer optimistic spinning | atomic_long_add_return | 读多写少场景 |
| **percpu** | `DEFINE_PER_CPU` | 节段变量 | per_cpu_ptr / this_cpu_* | 每 CPU 数据 |
| **percpu_counter** | `struct percpu_counter` | 批量同步 | raw_spinlock | 近似计数 |
| **lockdep** | `lock_class` + `lock_list` | BFS 环检测 | 图遍历 + 循环队列 | 死锁检测 |

### 关键源码位置索引

| 文件 | 行号 | 描述 |
|------|------|------|
| `kernel/locking/spinlock.c` | 136-213 | spinlock trylock/lock/unlock 实现 |
| `kernel/locking/mutex.c` | 84-118 | `__mutex_trylock_common` |
| `kernel/locking/mutex.c` | 152-170 | `__mutex_trylock_fast` / `__mutex_unlock_fast` |
| `kernel/locking/mutex.c` | 444-518 | `mutex_optimistic_spin` |
| `kernel/locking/osq_lock.c` | 93-208 | `osq_lock` MCS 入队 |
| `kernel/locking/osq_lock.c` | 210-234 | `osq_unlock` |
| `kernel/locking/rwsem.c` | 118-129 | rwsem count 位域定义 |
| `kernel/locking/rwsem.c` | 249-274 | `rwsem_read_trylock` / `rwsem_write_trylock` |
| `kernel/locking/rwsem.c` | 816-932 | `rwsem_optimistic_spin` |
| `include/asm-generic/qspinlock.h` | 51-130 | qspinlock 加解锁 |
| `include/asm-generic/qspinlock_types.h` | 14-44 | qspinlock 结构体 |
| `include/linux/percpu-defs.h` | 237-257 | per_cpu_ptr / this_cpu_ptr |
| `include/linux/percpu_counter.h` | 22-29 | percpu_counter 结构体 |
| `kernel/locking/lockdep.c` | 207-224 | lockdep 核心数据结构 |
| `kernel/locking/lockdep.c` | 1733-1839 | BFS 搜索 `__bfs` |
| `kernel/locking/lockdep.c` | 3121-3199 | `check_prev_add` 验证 |
| `kernel/locking/lockdep.c` | 1469-1526 | 循环队列实现 |

---

*文档版本: R2*
*生成日期: 2026-04-26*
*分析范围: kernel/locking/spinlock.c, mutex.c, rwsem.c, mm/percpu.c, kernel/locking/lockdep.c*
