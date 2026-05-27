# Linux RCU 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [rcu_subsystem.md](rcu_subsystem.md) | RCU: read-copy-update, synchronize_rcu | kernel/rcu/ |
| [rcu_deep_dive_r2.md](rcu_deep_dive_r2.md) | 深度分析 R2: grace period, srcu, rcu_node层次, NOCB | kernel/rcu/ |

---

## 主要内容

### 1. RCU 原理
- 无锁读取
- 写者延迟删除
- 宽限期检测

### 2. 核心数据结构
- struct rcu_head: 回调
- struct rcu_data: per-CPU 数据
- struct rcu_node: 层次节点

### 3. 同步机制
- synchronize_rcu()
- call_rcu()
- rcu_barrier()

### 4. 读取端 API
- rcu_read_lock/unlock
- rcu_dereference()

### 5. SRCU
- srcu_read_lock/unlock
- synchronize_srcu()

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| tree RCU | kernel/rcu/tree.c |
| srcu | kernel/rcu/srcutree.c |
| rcupdate | kernel/rcu/rcupdate.c |
