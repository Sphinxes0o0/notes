# Linux 内核锁子系统分析文档

## 目录

1. [概述](#1-概述)
2. [自旋锁 (Spinlock)](#2-自旋锁-spinlock)
3. [互斥锁 (Mutex)](#3-互斥锁-mutex)
4. [读写信号量 (Rwsem)](#4-读写信号量-rwsem)
5. [每CPU变量 (Per-CPU)](#5-每cpu变量-per-cpu)
6. [锁调试机制](#6-锁调试机制)
7. [架构图](#7-架构图)

---

## 1. 概述

Linux 内核提供多种锁机制来解决并发访问共享资源的问题。不同锁机制适用于不同场景：

| 锁类型 | 特性 | 适用场景 |
|--------|------|----------|
| 自旋锁 | 忙等待，不睡眠 | 临界区短小、中断上下文 |
| 互斥锁 | 睡眠等待，可抢占 | 临界区较长、进程上下文 |
| 读写信号量 | 读写分离 | 读多写少场景 |
| 每CPU变量 | 无锁 | 统计计数等场景 |

---

## 2. 自旋锁 (Spinlock)

### 2.1 数据结构

**源码位置**: `include/linux/spinlock_types.h`

```c
// 基础自旋锁类型
typedef struct raw_spinlock {
    arch_spinlock_t raw_lock;
#ifdef CONFIG_DEBUG_SPINLOCK
    unsigned int magic;
#endif
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    unsigned int owner;
    unsigned int owner_cpu;
#endif
} raw_spinlock_t;

// 高级自旋锁类型 (在非PREEMPT_RT下等同于raw_spinlock)
typedef struct spinlock {
    raw_spinlock_t rlock;
} spinlock_t;
```

### 2.2 核心API

**源码位置**: `kernel/locking/spinlock.c`

#### 2.2.1 spin_lock/unlock

```c
// spin_lock - 获取自旋锁
// 源码: kernel/locking/spinlock.c, 行 152-156
static __always_inline void spin_lock(spinlock_t *lock)
{
    raw_spin_lock(&lock->rlock);
}

// spin_unlock - 释放自旋锁
// 源码: kernel/locking/spinlock.h, 行 386-389
static __always_inline void spin_unlock(spinlock_t *lock)
{
    raw_spin_unlock(&lock->rlock);
}
```

#### 2.2.2 spin_lock_irqsave

```c
// spin_lock_irqsave - 保存中断状态并获取锁
// 源码: kernel/locking/spinlock.h, 行 374-378
#define spin_lock_irqsave(lock, flags)              \
do {                                   \
    raw_spin_lock_irqsave(spinlock_check(lock), flags); \
    __release(spinlock_check(lock)); __acquire(lock);  \
} while (0)

// 底层实现: kernel/locking/spinlock.c, 行 160-164
noinline unsigned long __lockfunc _raw_spin_lock_irqsave(raw_spinlock_t *lock)
{
    return __raw_spin_lock_irqsave(lock);
}
```

#### 2.2.3 spin_trylock

```c
// spin_trylock - 非阻塞获取锁
// 源码: kernel/locking/spinlock.c, 行 136-140
noinline int __lockfunc _raw_spin_trylock(raw_spinlock_t *lock)
{
    return __raw_spin_trylock(lock);
}
```

### 2.3 底层实现机制

```c
// 内联汇编级别的锁操作
// 源码: kernel/locking/spinlock.c, 行 67-78
#define BUILD_LOCK_OPS(op, locktype)                   \
static void __lockfunc __raw_##op##_lock(locktype##_t *lock)     \
{                                    \
    for (;;) {                           \
        preempt_disable();                  \
        if (likely(do_raw_##op##_trylock(lock)))     \
            break;                      \
        preempt_enable();                 \
        arch_##op##_relax(&lock->raw_lock);      \
    }                               \
}
```

**关键特性**:
- 使用 `preempt_disable()` 禁用抢占
- 循环等待直到获取锁
- `arch_spin_relax()` 允许CPU在等待时让出资源

### 2.4 atomic_t 与 spinlock 区别

| 特性 | atomic_t | spinlock |
|------|----------|----------|
| 原理 | 硬件原子指令 | 内存总线锁/原子指令 |
| 适用操作 | 简单计数/位操作 | 复杂保护区域 |
| 上下文 | 可在中断上下文 | 不可睡眠 |
| 性能 | 更轻量 | 有额外开销 |

```c
// atomic_t 示例 - 原子递增
// 源码: include/linux/atomic.h
static inline void atomic_inc(atomic_t *v)
{
    atomic_add_return(1, v);
}

// spinlock 示例 - 保护临界区
spin_lock(&lock);
counter++;
spin_unlock(&lock);
```

---

## 3. 互斥锁 (Mutex)

### 3.1 数据结构

**源码位置**: `include/linux/mutex.h` 和 `kernel/locking/mutex.c`

```c
// 互斥锁结构体 (非PREEMPT_RT)
// 源码: include/linux/mutex.h, 行 79-84
#define __MUTEX_INITIALIZER(lockname) \
        { .owner = ATOMIC_LONG_INIT(0) \
        , .wait_lock = __RAW_SPIN_LOCK_UNLOCKED(lockname.wait_lock) \
        , .wait_list = LIST_HEAD_INIT(lockname.wait_list) \
        __DEBUG_MUTEX_INITIALIZER(lockname) \
        __DEP_MAP_MUTEX_INITIALIZER(lockname) }

struct mutex {
    atomic_long_t owner;          // 持有者任务指针
    raw_spinlock_t wait_lock;    // 保护等待列表的自旋锁
    struct list_head wait_list;  // 等待队列
#ifdef CONFIG_MUTEX_SPIN_ON_OWNER
    struct optimistic_spin_queue osq;  // MCS锁队列
#endif
#ifdef CONFIG_DEBUG_MUTEXES
    void *magic;
#endif
};
```

**owner 字段编码**:
- 低3位用于标志 (MUTEX_FLAGS)
- 其余位存储 task_struct 指针

```c
// 源码: kernel/locking/mutex.c, 行 57-60
#define MUTEX_FLAGS    0x07

static inline struct task_struct *__owner_task(unsigned long owner)
{
    return (struct task_struct *)(owner & ~MUTEX_FLAGS);
}
```

### 3.2 mutex_lock/unlock 实现

#### 3.2.1 mutex_lock

```c
// 源码: kernel/locking/mutex.c, 行 285-292
void __sched mutex_lock(struct mutex *lock)
{
    might_sleep();

    if (!__mutex_trylock_fast(lock))
        __mutex_lock_slowpath(lock);
}

// 快速路径: 乐观自旋获取
// 源码: kernel/locking/mutex.c, 行 152-163
static __always_inline bool __mutex_trylock_fast(struct mutex *lock)
{
    unsigned long curr = (unsigned long)current;
    unsigned long zero = 0UL;

    MUTEX_WARN_ON(lock->magic != lock);

    if (atomic_long_try_cmpxchg_acquire(&lock->owner, &zero, curr))
        return true;

    return false;
}
```

#### 3.2.2 mutex_unlock

```c
// 源码: kernel/locking/mutex.c, 行 546-553
void __sched mutex_unlock(struct mutex *lock)
{
#ifndef CONFIG_DEBUG_LOCK_ALLOC
    if (__mutex_unlock_fast(lock))
        return;
#endif
    __mutex_unlock_slowpath(lock, _RET_IP_);
}

// 快速路径: 原子释放
// 源码: kernel/locking/mutex.c, 行 165-170
static __always_inline bool __mutex_unlock_fast(struct mutex *lock)
{
    unsigned long curr = (unsigned long)current;

    return atomic_long_try_cmpxchg_release(&lock->owner, &curr, 0UL);
}
```

### 3.3 睡眠互斥锁特性

```c
// 慢速路径获取互斥锁
// 源码: kernel/locking/mutex.c, 行 577-770
static __always_inline int __sched
__mutex_lock_common(struct mutex *lock, unsigned int state, unsigned int subclass,
            struct lockdep_map *nest_lock, unsigned long ip,
            struct ww_acquire_ctx *ww_ctx, const bool use_ww_ctx)
{
    // 1. 乐观自旋 (如果锁持有者在CPU上运行)
    if (__mutex_trylock(lock) ||
        mutex_optimistic_spin(lock, ww_ctx, NULL)) {
        lock_acquired(&lock->dep_map, ip);
        return 0;
    }

    // 2. 获取wait_lock并加入等待队列
    raw_spin_lock_irqsave(&lock->wait_lock, flags);
    // ... 添加到等待列表 ...

    // 3. 循环等待并检查信号
    for (;;) {
        if (__mutex_trylock(lock))
            goto acquired;

        if (signal_pending_state(state, current)) {
            ret = -EINTR;
            goto err;
        }

        schedule_preempt_disabled();  // 调度其他任务
    }
acquired:
    // 获取锁后清理
    __mutex_remove_waiter(lock, &waiter);
    // ...
}
```

**关键特性**:
1. **乐观自旋 (Optimistic Spinning)**: 当锁持有者正在CPU上运行时，等待者会自旋等待
2. **MCS锁队列**: 使用MCS队列确保只有一个等待者自旋
3. **让出机制**: 如果需要调度，会调用 `schedule_preempt_disabled()`

---

## 4. 读写信号量 (Rwsem)

### 4.1 数据结构

**源码位置**: `include/linux/rwsem.h` 和 `kernel/locking/rwsem.c`

```c
// 读写信号量结构
// 源码: include/linux/rwsem.h, 行 48-67
context_lock_struct(rw_semaphore) {
    atomic_long_t count;         // 计数器
    atomic_long_t owner;        // 持有者(写入者或读者)
#ifdef CONFIG_RWSEM_SPIN_ON_OWNER
    struct optimistic_spin_queue osq;  // MCS自旋队列
#endif
    raw_spinlock_t wait_lock;   // 保护等待列表
    struct list_head wait_list;  // 等待队列
#ifdef CONFIG_DEBUG_RWSEMS
    void *magic;
#endif
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lockdep_map dep_map;
#endif
};
```

### 4.2 count 字段编码

```c
// 源码: kernel/locking/rwsem.c, 行 118-129
#define RWSEM_WRITER_LOCKED     (1UL << 0)    // 写入者已获取
#define RWSEM_FLAG_WAITERS      (1UL << 1)    // 有等待者
#define RWSEM_FLAG_HANDOFF      (1UL << 2)    // 锁交接标志
#define RWSEM_FLAG_READFAIL     (1UL << (BITS_PER_LONG - 1))  // 读失败标志

#define RWSEM_READER_SHIFT      8
#define RWSEM_READER_BIAS       (1UL << RWSEM_READER_SHIFT)  // 读者增量
```

**64位架构下的count布局**:
```
Bit  0    - 写入锁定位
Bit  1    - 等待者存在位
Bit  2    - 锁交接位
Bits 3-7  - 保留
Bits 8-62 - 55位读者计数
Bit  63   - 读失败位
```

### 4.3 down_read/up_read

```c
// 获取读锁
// 源码: kernel/locking/rwsem.c, 行 1534-1541
void __sched down_read(struct rw_semaphore *sem)
{
    might_sleep();
    rwsem_acquire_read(&sem->dep_map, 0, 0, _RET_IP_);

    LOCK_CONTENDED(sem, __down_read_trylock, __down_read);
}

// 底层读锁获取
// 源码: kernel/locking/rwsem.c, 行 1272-1275
static __always_inline void __down_read(struct rw_semaphore *sem)
{
    __down_read_common(sem, TASK_UNINTERRUPTIBLE);
}

// 源码: kernel/locking/rwsem.c, 行 1254-1270
static __always_inline int __down_read_common(struct rw_semaphore *sem, int state)
{
    int ret = 0;
    long count;

    preempt_disable();
    if (!rwsem_read_trylock(sem, &count)) {
        if (IS_ERR(rwsem_down_read_slowpath(sem, count, state))) {
            ret = -EINTR;
            goto out;
        }
        DEBUG_RWSEMS_WARN_ON(!is_rwsem_reader_owned(sem), sem);
    }
out:
    preempt_enable();
    return ret;
}

// 读锁快速路径
// 源码: kernel/locking/rwsem.c, 行 249-262
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

// 释放读锁
// 源码: kernel/locking/rwsem.c, 行 1349-1366
static inline void __up_read(struct rw_semaphore *sem)
{
    long tmp;

    DEBUG_RWSEMS_WARN_ON(sem->magic != sem, sem);
    DEBUG_RWSEMS_WARN_ON(!is_rwsem_reader_owned(sem), sem);

    preempt_disable();
    rwsem_clear_reader_owned(sem);
    tmp = atomic_long_add_return_release(-RWSEM_READER_BIAS, &sem->count);
    DEBUG_RWSEMS_WARN_ON(tmp < 0, sem);
    if (unlikely((tmp & (RWSEM_LOCK_MASK|RWSEM_FLAG_WAITERS)) ==
              RWSEM_FLAG_WAITERS)) {
        clear_nonspinnable(sem);
        rwsem_wake(sem);
    }
    preempt_enable();
}
```

### 4.4 down_write/up_write

```c
// 获取写锁
// 源码: kernel/locking/rwsem.c, 行 1587-1593
void __sched down_write(struct rw_semaphore *sem)
{
    might_sleep();
    rwsem_acquire(&sem->dep_map, 0, 0, _RET_IP_);
    LOCK_CONTENDED(sem, __down_write_trylock, __down_write);
}

// 写锁获取
// 源码: kernel/locking/rwsem.c, 行 1324-1327
static __always_inline void __down_write(struct rw_semaphore *sem)
{
    __down_write_common(sem, TASK_UNINTERRUPTIBLE);
}

// 源码: kernel/locking/rwsem.c, 行 1311-1322
static __always_inline int __down_write_common(struct rw_semaphore *sem, int state)
{
    int ret = 0;

    preempt_disable();
    if (unlikely(!rwsem_write_trylock(sem))) {
        if (IS_ERR(rwsem_down_write_slowpath(sem, state)))
            ret = -EINTR;
    }
    preempt_enable();
    return ret;
}

// 写锁尝试获取
// 源码: kernel/locking/rwsem.c, 行 264-274
static inline bool rwsem_write_trylock(struct rw_semaphore *sem)
{
    long tmp = RWSEM_UNLOCKED_VALUE;

    if (atomic_long_try_cmpxchg_acquire(&sem->count, &tmp, RWSEM_WRITER_LOCKED)) {
        rwsem_set_owner(sem);
        return true;
    }

    return false;
}

// 释放写锁
// 源码: kernel/locking/rwsem.c, 行 1371-1389
static inline void __up_write(struct rw_semaphore *sem)
{
    long tmp;

    DEBUG_RWSEMS_WARN_ON(sem->magic != sem, sem);
    DEBUG_RWSEMS_WARN_ON((rwsem_owner(sem) != current) &&
                !rwsem_test_oflags(sem, RWSEM_NONSPINNABLE), sem);

    preempt_disable();
    rwsem_clear_owner(sem);
    tmp = atomic_long_fetch_add_release(-RWSEM_WRITER_LOCKED, &sem->count);
    if (unlikely(tmp & RWSEM_FLAG_WAITERS))
        rwsem_wake(sem);
    preempt_enable();
}
```

---

## 5. 每CPU变量 (Per-CPU)

### 5.1 DEFINE_PER_CPU

**源码位置**: `include/linux/percpu.h`

```c
// 声明每CPU变量
// 源码: include/linux/percpu.h
extern void __percpu *pcpu_alloc_noprof(size_t size, size_t align, bool reserved,
                       gfp_t gfp) __alloc_size(1);

// 动态分配每CPU变量
#define __alloc_percpu_gfp(_size, _align, _gfp)       \
        alloc_hooks(pcpu_alloc_noprof(_size, _align, false, _gfp))
#define __alloc_percpu(_size, _align)         \
        alloc_hooks(pcpu_alloc_noprof(_size, _align, false, GFP_KERNEL))

// 静态定义每CPU变量
// 编译器内置宏
DEFINE_PER_CPU(int, my_counter);  // 定义名为 my_counter 的每CPU整型变量
```

### 5.2 percpu_read/write

```c
// 读取当前CPU的变量
// 源码: include/linux/percpu.h (通常为编译器内联)
#define get_cpu_var(var) (*this_cpu_ptr(&var))
#define put_cpu_var(var) do { } while (0)

// 安全读取
#define percpu_read(var) (*this_cpu_ptr(&(var)))

// 写操作
#define percpu_write(var, val) (*this_cpu_ptr(&(var)) = (val))
```

### 5.3 percpu_counter

**源码位置**: `include/linux/percpu_counter.h` 和 `mm/percpu.c`

```c
// percpu_counter 结构
// 源码: include/linux/percpu_counter.h, 行 22-29
struct percpu_counter {
    raw_spinlock_t lock;
    s64 count;                // 全局计数
#ifdef CONFIG_HOTPLUG_CPU
    struct list_head list;    // 热插拔CPU列表
#endif
    s32 __percpu *counters;   // 每CPU计数器数组
};

// 批量同步阈值
extern int percpu_counter_batch;

// 初始化计数器
// 源码: mm/percpu.c (实际实现)
int percpu_counter_init_many(struct percpu_counter *fbc, s64 amount,
                gfp_t gfp, u32 nr_counters,
                struct lock_class_key *key);

// 添加计数
// 源码: include/linux/percpu_counter.h, 行 69-72
static inline void percpu_counter_add(struct percpu_counter *fbc, s64 amount)
{
    percpu_counter_add_batch(fbc, amount, percpu_counter_batch);
}

// 读取计数 (近似值)
// 源码: include/linux/percpu_counter.h, 行 108-111
static inline s64 percpu_counter_read(struct percpu_counter *fbc)
{
    return fbc->count;
}

// 精确求和
// 源码: include/linux/percpu_counter.h, 行 103-106
static inline s64 percpu_counter_sum(struct percpu_counter *fbc)
{
    return __percpu_counter_sum(fbc);
}
```

**percpu_counter 特点**:
- 读取 `fbc->count` 是近似值(可能为负)
- 调用 `percpu_counter_sum()` 可获得精确值
- 使用批量更新减少锁竞争

---

## 6. 锁调试机制

### 6.1 lockdep - 锁依赖追踪

**源码位置**: `kernel/locking/lockdep.c`, `kernel/locking/lockdep_proc.c`

#### 6.1.1 核心功能

```c
// 检测以下类型的锁bug:
// 1. 锁反转 (Lock Inversion)
// 2. 循环锁依赖 (Circular Lock Dependencies)
// 3. 硬中断/软中断安全/非安全锁bug

// lockdep 统计信息接口
// 源码: kernel/locking/lockdep_proc.c
// /proc/lockdep - 显示所有锁类及依赖关系
// /proc/lockdep_stats - 显示统计信息
```

#### 6.1.2 使用示例

```c
// 在锁获取时记录依赖
// 源码: kernel/locking/lockdep.c
void __lockfunc _raw_spin_lock(raw_spinlock_t *lock)
{
    __raw_spin_lock(lock);
}

// 锁获取时的依赖追踪
// 源码: kernel/locking/spinlock.c, 行 375-380
void __lockfunc _raw_spin_lock_nested(raw_spinlock_t *lock, int subclass)
{
    preempt_disable();
    spin_acquire(&lock->dep_map, subclass, 0, _RET_IP_);
    LOCK_CONTENDED(lock, do_raw_spin_trylock, do_raw_spin_lock);
}
```

#### 6.1.3 lockdep 统计信息

```c
// 源码: kernel/locking/lockdep_proc.c, 行 231-393
// 显示内容:
// - lock-classes: 锁类数量
// - direct dependencies: 直接依赖数量
// - dependency chains: 依赖链数量
// - hardirq-safe/unsafe locks: 硬中断安全/非安全锁
// - softirq-safe/unsafe locks: 软中断安全/非安全锁
```

### 6.2 lock_stat - 锁统计

**源码位置**: `kernel/locking/lockdep_proc.c`, 行 396-714

#### 6.2.1 功能

```c
// /proc/lock_stat - 锁性能统计
// 显示每个锁的:
// - contentions: 争用次数
// - waittime-min/max/total/avg: 等待时间统计
// - acquisitions: 获取次数
// - holdtime-min/max/total/avg: 持有时间统计
```

#### 6.2.2 统计结构

```c
// 源码: kernel/locking/lockdep_proc.c, 行 451-458
static void seq_lock_time(struct seq_file *m, struct lock_time *lt)
{
    seq_printf(m, "%14lu", lt->nr);      // 次数
    seq_time(m, lt->min);                // 最小时间
    seq_time(m, lt->max);                // 最大时间
    seq_time(m, lt->total);              // 总时间
    seq_time(m, lt->nr ? div64_u64(lt->total, lt->nr) : 0);  // 平均时间
}
```

---

## 7. 架构图

### 7.1 自旋锁架构

```
                    spin_lock()
                         |
                         v
    +--------------------+--------------------+
    |                                        |
preempt_disable()                      __raw_spin_lock()
    |                                        |
    v                                        v
    +---------> do_raw_spin_trylock() <------+
                        |
              +---------+---------+
              |                   |
            成功                  失败
              |                   |
              v                   v
         返回              preempt_enable()
              |                   |
              |                   v
              |            arch_spin_relax()
              |                   |
              +---------+---------+
                        |
                        v
```

循环等待

### 7.2 Mutex 架构

```
                    mutex_lock()
                         |
                         v
              __mutex_trylock_fast()
                         |
          +--------------+--------------+
          |                             |
        成功                          失败
          |                             |
          v                             v
        返回                    __mutex_lock_slowpath()
                                           |
                                           v
                              +------------+------------+
                              |                         |
                    乐观自旋等待持有者              加入等待队列
                    (osq_lock + spin)              (schedule)
                              |                         |
                              +------------+------------+
                                           |
                                           v
```

唤醒释放

### 7.3 Rwsem 架构

```
                down_read()                down_write()
                    |                          |
                    v                          v
           rwsem_read_trylock()        rwsem_write_trylock()
                    |                          |
          +---------+--------+                 |
          |                 |                成功
        成功              失败                 |
          |                 |                  v
          v                 v              返回
        返回         rwsem_down_read_slowpath()
                                      (乐观自旋/加入队列)
                                              |
                                              v
                                         rwsem_wake()
                                         (批量唤醒读者)
```

### 7.4 percpu_counter 架构

```
              percpu_counter_add()
                      |
                      v
           percpu_counter_add_batch()
                      |
                      v
         +------------+------------+
         |                         |
    本地CPU更新              达到批量阈值
    (无需锁)                 (需要global lock)
         |                         |
         v                         v
     直接更新                  批量同步
    __percpu *counters         fbc->count
```

### 7.5 lockdep 依赖追踪架构

```
         lock_acquire()           lock_release()
              |                        |
              v                        v
         +---+------+              +---+------+
         |          |              |          |
    记录持有者   记录依赖关系    移除持有者   移除依赖关系
         |          |              |          |
         v          v              v          v
    +--------------------------------------------------------+
    |                     lockdep 数据库                        |
    |  +------------+    +------------+    +------------+    |
    |  |lock_classes|    |lock_chains |    |stack_trace|    |
    |  +------------+    +------------+    +------------+    |
    +--------------------------------------------------------+
              |                        |
              v                        v
         /proc/lockdep           检测循环依赖
         /proc/lockdep_stats     检测锁反转
```

---

## 附录: 关键文件列表

| 文件路径 | 功能描述 |
|----------|----------|
| `kernel/locking/spinlock.c` | 自旋锁实现 |
| `kernel/locking/mutex.c` | 互斥锁实现 |
| `kernel/locking/rwsem.c` | 读写信号量实现 |
| `mm/percpu.c` | 每CPU变量分配器 |
| `include/linux/spinlock.h` | 自旋锁头文件 |
| `include/linux/mutex.h` | 互斥锁头文件 |
| `include/linux/rwsem.h` | 读写信号量头文件 |
| `include/linux/percpu.h` | 每CPU变量头文件 |
| `include/linux/percpu_counter.h` | 每CPU计数器头文件 |
| `kernel/locking/lockdep.c` | 锁依赖追踪实现 |
| `kernel/locking/lockdep_proc.c` | 锁调试接口实现 |

---

*文档生成时间: 2026-04-26*
*内核版本: Linux (based on source analysis)*
