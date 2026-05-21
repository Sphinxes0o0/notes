---
type: entity
tags: [Linux内核, 锁机制, 并发控制, spinlock, mutex, 信号量, lockdep]
created: 2026-05-20
sources: [notes-overview-kernel-locking]
---

# Linux Kernel Locking Subsystem

## 定义

Linux内核并发控制核心子系统，提供自旋锁（spinlock）、互斥锁（mutex）、读写信号量（rwsem）、每CPU变量（percpu）等多种锁机制，解决多核环境下共享资源访问的竞争条件问题。

## 关键要点

### 锁类型对比

| 锁类型 | 特性 | 适用场景 |
|--------|------|----------|
| spinlock | 忙等待，不睡眠 | 临界区短小，中断上下文 |
| mutex | 睡眠等待，可抢占 | 临界区较长，进程上下文 |
| rwsem | 读写分离 | 读多写少场景 |
| percpu | 无锁 | 统计计数等 |

### 自旋锁 (spinlock)

**核心API**:
- spin_lock/unlock — 基本获取/释放
- spin_lock_irqsave — 保存中断状态并获取锁
- spin_trylock — 非阻塞尝试获取

**底层实现**:
- preempt_disable() 禁用抢占
- do_raw_spin_trylock() 循环等待
- arch_spin_relax() CPU让出资源

### 互斥锁 (mutex)

**数据结构**:
- owner字段: 持有者task_struct指针（低3位存标志）
- wait_lock: 保护等待列表的自旋锁
- wait_list: 等待队列链表
- osq: MCS锁队列（乐观自旋）

**关键特性**:
- 乐观自旋: 锁持有者在CPU上运行时等待者自旋
- MCS队列: 确保只有一个等待者自旋
- fast/slow path: trylock快速路径，失败走慢速路径

### 读写信号量 (rwsem)

**count字段编码** (64位):
- Bit 0: 写入者锁定位
- Bit 1: 等待者存在位
- Bit 2: 锁交接标志
- Bits 8-62: 读者计数（增量RWSEM_READER_BIAS）

**优化**: 读者不互斥，批量唤醒等待者

### 每CPU变量 (percpu)

**API**:
- DEFINE_PER_CPU — 静态定义
- get_cpu_var/put_cpu_var — 安全访问
- percpu_counter — 批量更新计数器

**percpu_counter特点**:
- percpu_counter_read() 返回近似值
- percpu_counter_sum() 精确求和
- 批量更新减少锁竞争

### 锁调试 (lockdep)

**功能**:
- lockdep: 检测锁依赖环、死锁、硬/软中断安全bug
- lock_stat: 锁性能统计（等待时间、持有时间）

**接口**:
- /proc/lockdep — 显示所有锁类及依赖关系
- /proc/lockdep_stats — 统计信息
- /proc/lock_stat — 锁性能统计

### 源码位置

| 组件 | 路径 |
|------|------|
| spinlock | kernel/locking/spinlock.c |
| mutex | kernel/locking/mutex.c |
| rwsem | kernel/locking/rwsem.c |
| percpu | mm/percpu.c |
| lockdep | kernel/locking/lockdep.c |

## 相关概念
- [[entities/os/os-process-thread]] — 进程与线程（锁的使用场景）
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度（与锁竞争相关）

## 来源详情
- [[sources/notes-kernel-locking]]
## Related Concepts

- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU与锁机制同为内核同步原语
- [[entities/linux/kernel/crypto/linux-kernel-crypto-core]] — 加解密操作需配合锁机制保证原子性
