# Linux Locking 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [locking_subsystem.md](locking_subsystem.md) | 锁: spinlock, mutex, rwsem, percpu | kernel/locking/ |
| [locking_deep_dive_r2.md](locking_deep_dive_r2.md) | 深度分析 R2: MCS队列, mutex活锁, rwsem优化, lockdep环检测 | kernel/locking/ |

---

## 主要内容

### 1. 自旋锁 (spinlock)
- spin_lock/unlock
- spin_lock_irqsave

### 2. 互斥锁 (mutex)
- struct mutex
- 快速路径和慢速路径
- MCS 队列

### 3. 读写信号量 (rwsem)
- struct rw_semaphore
- down_read/up_read
- down_write/up_write

### 4. 每CPU变量 (percpu)
- DEFINE_PER_CPU
- percpu_read/write

### 5. 锁调试
- lockdep: 依赖追踪
- lock_stat: 统计

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| spinlock | kernel/locking/spinlock.c |
| mutex | kernel/locking/mutex.c |
| rwsem | kernel/locking/rwsem.c |
| percpu | mm/percpu.c |
| lockdep | kernel/locking/lockdep.c |
