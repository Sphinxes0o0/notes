---
type: entity
tags: [linux-kernel, SMP, multi-core, CPU-mask, per-cpu, cpu-hotplug]
created: 2026-05-28
sources: [ebook-linux-insides]
---

# SMP (对称多处理器)

## 定义

SMP (Symmetric Multi-Processing) 是 Linux 内核支持多核处理器并行的核心机制，使多个 CPU 核心共享同一内存空间，并行执行内核代码。Linux 通过 CPU masks、per-CPU 变量、调度域等机制高效管理多核系统。

## 关键要点

### CPU Masks (CPU 掩码)

用于表示系统中 CPU 集合的位图，一位代表一个 CPU 序号。

**核心 API:**
```c
typedef struct cpumask { DECLARE_BITMAP(bits, NR_CPUS); } cpumask_t;

// 查询
num_online_cpus();     // 在线 CPU 数量
cpu_online_mask;       // 在线 CPU mask

// 遍历
for_each_cpu(cpu, mask);        // 遍历 mask 所有 CPU
for_each_cpu_not(cpu, mask);    // 遍历补集

// 操作
set_cpu_online(cpu, true);      // 上线 CPU
cpumask_set_cpu(cpu, mask);     // 设置 mask 中某位
cpumask_clear_cpu(cpu, mask);   // 清除 mask 中某位
```

**实现基础:**
- `DECLARE_BITMAP(name, bits)` → `unsigned long name[BITS_TO_LONGS(bits)]`
- `set_bit()`: `LOCK_PREFIX "bts %1,%0"` 原子设置位

### Per-CPU 变量

每个 CPU 核心拥有独立的变量副本，消除锁竞争。

**关键机制:**
```c
DECLARE_PER_CPU(type, name);           // 声明 per-CPU 变量
per_cpu_ptr(&name, cpu);              // 获取指定 CPU 的变量地址
this_cpu_ptr(&name);                  // 获取当前 CPU 的变量地址

// 编译时常量偏移
__per_cpu_offset[cpu];                // 第 cpu 个 CPU 的变量区基址
```

**使用场景:**
- `tvec_base`: per-CPU 动态定时器基数
- `irq_stack_union`: per-CPU 中断栈
- `softnet_data`: per-CPU 网络软中断数据

### CPU Hotplug (热拔插)

支持在系统运行时动态上线/下线 CPU。

**状态定义:**
```c
set_cpu_possible(cpu, true);   // 可插入的 CPU
set_cpu_present(cpu, true);    // 当前插入的 CPU
set_cpu_online(cpu, true);    // 可调度的 CPU
set_cpu_active(cpu, true);     // 活跃的 CPU
```

**通知链:**
- `CPU_DEAD`: CPU 下线时迁移 timers/tasks
- `CPU_ONLINE`: CPU 上线时重新初始化

### 同步与 SMP

**Spinlock 在 SMP 中的行为:**
```c
static inline void __raw_spin_lock(raw_spinlock_t *lock)
{
    preempt_disable();           // 禁用抢占
    spin_acquire(&lock->dep_map, 0, 0, _RET_IP_);
    LOCK_CONTENDED(lock, do_raw_spin_trylock, do_raw_spin_lock);
}
```

**Ticket Spinlock (队列自旋锁):**
- 每个等待者获取一个 ticket (tail++)
- 自旋直到 ticket == head
- `arch_spin_lock()`: `xadd()` 原子递增 tail，检测 head/tail 匹配

**QSpinlock (队列自旋锁):**
- `CONFIG_QUEUED_SPINLOCKS` 启用时使用
- `atomic_t val` 替代 ticket pair
- 更适合高竞争场景

### Per-CPU 中断栈

每个 CPU 有独立的中断栈 (16KB)：
```c
union irq_stack_union {
    char irq_stack[IRQ_STACK_SIZE];  // 16KB
    struct {
        char gs_base[40];            // per-cpu gs 基址
        unsigned long stack_canary;   // stack protector
    };
};

DECLARE_PER_CPU_FIRST(union irq_stack_union, irq_stack_union) __visible;
```

## 相关概念

- [[entities/linux/kernel/linux-kernel-locking-core]] — spinlock/ticket lock/queue spinlock
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 多核调度与负载均衡
- [[entities/linux/kernel/linux-kernel-time-core]] — per-CPU 定时器基数 (tvec_base)
- [[entities/linux/kernel/linux-kernel-rcu-core]] — RCU 无锁读取（多核同步）

## 来源详情

- [[sources/ebook-linux-insides]] — Concepts/CPU掩码 + SyncPrim/自旋锁
- [[sources/bookmark-linux-interrupt-loyenwang]] — ARM64 中断与 SMP
