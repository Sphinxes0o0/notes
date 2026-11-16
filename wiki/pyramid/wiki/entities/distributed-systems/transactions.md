---
type: entity
tags: [distributed-systems, transactions, ACID, isolation-levels, MVCC, 2PC, serializability]
created: 2026-05-28
sources: [ebook-ddia]
---

# Transactions (事务)

## 定义

事务是数据库管理系统将多个读写操作组织为一个逻辑单元的执行机制，保证 ACID 特性。事务简化了应用层的错误处理，是分布式系统一致性的核心保障。

## ACID 特性

| 特性 | 含义 | 实现要点 |
|------|------|----------|
| **Atomicity (原子性)** | 全部成功或全部失败 | 日志/Undo-redo |
| **Consistency (一致性)** | 数据始终满足约束 | 应用层不变量 |
| **Isolation (隔离性)** | 并发事务彼此隔离 | 锁/MVCC |
| **Durability (持久性)** | 提交后不丢失 | WAL + 复制 |

## 隔离级别

| 隔离级别 | 脏读 | 脏写 | 读取偏差 | 幻读 | 丢失更新 | 写偏差 |
|----------|------|------|----------|------|----------|--------|
| 读未提交 | 可能 | 可能 | 可能 | 可能 | 可能 | 可能 |
| 读已提交 | 防止 | 可能 | 可能 | 可能 | 可能 | 可能 |
| 快照隔离/可重复读 | 防止 | 防止 | 防止 | 防止 | 可能 | 可能 |
| 可串行化 | 防止 | 防止 | 防止 | 防止 | 防止 | 防止 |

### 读已提交 (Read Committed)

- 防止脏读：读取时只能看到已提交的数据
- 防止脏写：写入时只覆盖已提交的数据
- 实现：行级锁 (写排他锁)

### 快照隔离 (Snapshot Isolation)

- 每个事务从数据库的一致快照读取 (MVCC)
- 写入时检测冲突 (先提交者胜出)
- 问题：**写偏差 (Write Skew)** 和 **幻读 (Phantom Read)**

### 可串行化 (Serializable)

三种实现方式：

1. **实际串行执行**: 单线程按串行顺序执行 (e.g., Redis, VoltDB)
2. **两阶段锁定 (2PL)**: 悲观锁，串行化
3. **可串行化快照隔离 (SSI)**: 乐观锁，基于 predicate 乐观并发

## 分布式事务

### 两阶段提交 (2PC)

| 阶段 | 协调者行为 |
|------|-----------|
| **准备阶段** | 向所有节点发送"准备"请求 |
| **提交阶段** | 所有节点投票"是"则发送提交 |

**问题：**
- 协调者单点故障 → 阻塞
- 网络分区时可能造成不一致

### 三阶段提交 (3PC)

- 超时机制避免阻塞
- 仍无法完全避免数据不一致

## 防止丢失更新

- **原子写操作**: `UPDATE SET x = x + 1 WHERE id = ?` (原子性)
- **显式锁定**: `SELECT FOR UPDATE`
- **自动检测丢失更新**: 快照隔离下的 `SELECT` 重放
- **条件写入**: 写入前检查版本号

## 相关概念

- [[entities/distributed-systems/replication]] — 复制与事务的交集（多副本一致性）
- [[entities/distributed-systems/distributed-consensus]] — 共识算法是分布式事务的基础
- [[entities/distributed-systems/partitioning]] — 跨分片事务的复杂性
- [[entities/distributed-systems/distributed-troubles]] — 分布式系统的其他挑战

## 来源详情

- [[sources/ebook-ddia]] — Ch8 事务
