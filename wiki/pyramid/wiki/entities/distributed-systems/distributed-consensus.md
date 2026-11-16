---
type: entity
tags: [distributed-systems, consensus, Raft, Paxos, ZooKeeper, linearizability, CAP]
created: 2026-05-28
sources: [ebook-ddia]
---

# Distributed Consensus (分布式共识)

## 定义

共识算法让一群节点就某个值（或一系列值）达成一致决定，是分布式系统实现容错、一致性的核心。共识必须满足：一致同意、完整性、有效性、终止。

## 线性一致性 (Linearizability)

让系统看起来像只有一份数据副本，所有操作都是原子的。

**依赖线性一致性的场景：**
- **领导者选举**: 确保只有一个主节点
- **唯一性约束**: 用户名唯一性检查
- **跨通道时序依赖**: 避免竞态条件

### CAP 定理

网络分区时，只能在**一致性 (C)** 和**可用性 (A)** 之间二选一：
- CP 系统：放弃可用性（如 ZooKeeper）
- AP 系统：放弃一致性（如 Cassandra）

## 共识算法

### Raft

将共识问题分解为三个子问题：**领导者选举、日志复制、安全性**

| 角色 | 职责 |
|------|------|
| Leader | 接受写入，复制日志 |
| Follower | 被动接收日志条目 |
| Candidate | 选举时的临时角色 |

**领导者选举：**
- 选举超时 (150-300ms)，防止 Split Vote
- 选举 term 递增，只投票给 term ≥ 自己的

**日志复制：**
- 必须多数节点确认才能提交
- Commit Index 推进机制

### Paxos

- **Phase 1 (Prepare)**: Acceptor 承诺不再响应旧提案
- **Phase 2 (Accept)**: Proposer 提交值
- 两轮 RPC 实现复杂，ZooKeeper 使用 ZAB 变体

### Viewstamped Replication (VSR)

- 类似于 Paxos，但节点身份为 view 内主节点
- 视图切换处理故障

## 协调服务

ZooKeeper / etcd / Consul 提供：

| 功能 | 用途 |
|------|------|
| 锁与租约 | 分布式锁 (排他锁、读写锁) |
| 栅栏令牌 | 序列化入口点 |
| 故障检测 | 心跳 + ZAB 协议 |
| 变更通知 | Watch 机制 |

**应用场景：**
- 服务注册与发现
- 分布式锁 (Kafka、Kubernetes)
- 配置管理
- Leader 选举

## 分布式事务中的共识

共识本质上是"正确完成的单主复制"：
- 2PC 依赖协调者共识
- Saga 模式通过补偿事务避免全局锁
- 共识协议 (Raft) 提供更安全的分布式事务

## 相关概念

- [[entities/distributed-systems/replication]] — 共识与复制协同（领导者选举）
- [[entities/distributed-systems/transactions]] — 分布式事务依赖共识
- [[entities/distributed-systems/distributed-troubles]] — 共识解决的正是这些问题
- [[entities/linux/kernel/linux-kernel-locking-core]] — 内核锁原语（单机对比分布式共识）

## 来源详情

- [[sources/ebook-ddia]] — Ch10 一致性与共识
