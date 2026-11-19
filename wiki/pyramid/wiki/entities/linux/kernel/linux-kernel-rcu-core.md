---
type: entity
tags: [linux-kernel, RCU, Read-Copy-Update, 无锁同步, 并发控制]
created: 2026-05-20
sources: [notes-overview-kernel-rcu]
---

# Linux Kernel RCU (Read-Copy-Update)

## 定义

RCU（Read-Copy-Update）是Linux内核一种高效的无锁同步机制，允许读操作完全无锁并行执行，写操作延迟删除旧数据，通过宽限期（grace period）机制确保所有读者完成后再释放资源。适用于读多写少的高并发场景。

## 关键要点

### 核心原理

**无锁读取**:
- rcu_read_lock/unlock 保护区间的读操作
- rcu_dereference() 获取RCU保护的指针
- 读者之间完全无锁，可并行执行

**写者延迟删除**:
- 写者复制并修改数据，发布新指针
- 旧数据不立即释放，等待宽限期
- 宽限期结束后才调用回调释放

**宽限期检测**:
- 所有正在运行的读者必须完成
- 通过rcu_node层次结构追踪
- synchronize_rcu() 阻塞等待

### 核心数据结构

- **rcu_head**: 回调结构（next指针）
- **rcu_data**: per-CPU数据（偷睡队列、回调计数）
- **rcu_node**: 层次节点（组成树形结构）
- **rcu_state**: 全局RCU状态

### API概览

**同步接口**:
- synchronize_rcu(): 阻塞直到宽限期结束
- get_state_synchronize_rcu(): 获取当前状态
- cond_synchronize_rcu(): 条件等待

**回调接口**:
- call_rcu(): 注册宽限期结束后的回调
- rcu_barrier(): 等待所有已注册回调完成

**读取端**:
- rcu_read_lock(): 开始读取区间
- rcu_read_unlock(): 结束读取区间
- rcu_dereference(): 安全解引用

### SRCU (Sleepable RCU)

**特性**:
- srcu_read_lock/unlock 可睡眠
- 用于不能使用spinlock的上下文
- synchronize_srcu() 单独等待

### NOCB (No-CB RCU)

**设计目标**: 减少ossive lock contention
**机制**: 读者回调移到专门kthread处理

### 源码位置

| 组件 | 路径 |
|------|------|
| tree RCU | kernel/rcu/tree.c |
| srcu | kernel/rcu/srcutree.c |
| rcupdate | kernel/rcu/rcupdate.c |

## 相关概念
- [[entities/linux/kernel/linux-kernel-locking-core]] — 锁机制对比
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度与RCU关系

## 来源详情
- [[sources/notes-kernel-rcu]]
