---
type: entity
tags: [distributed-systems, replication, partitioning, transactions, consensus, data-engineering]
created: 2026-05-28
sources: [ebook-ddia]
---

# Distributed Systems Index

> 分布式系统核心概念索引，基于 DDIA (Designing Data-Intensive Applications)

## Entities (4)

| Entity | Description | Source |
|--------|-------------|--------|
| [[entities/distributed-systems/replication]] | 单主/多主/无主复制，复制滞后，CRDT，LWW | Ch6 |
| [[entities/distributed-systems/partitioning]] | 哈希/范围/一致性哈希分片，二级索引，请求路由 | Ch7 |
| [[entities/distributed-systems/transactions]] | ACID，MVCC，隔离级别，2PC，可串行化 | Ch8 |
| [[entities/distributed-systems/distributed-consensus]] | Raft，Paxos，ZooKeeper，线性一致性，CAP | Ch10 |

## Source

- [[sources/ebook-ddia]] — DDIA 完整 14 章节

## 核心概念地图

```
复制 (Ch6)
    ↓
分片 (Ch7) ←→ 复制
    ↓
事务 (Ch8)
    ↓
分布式麻烦 (Ch9)
    ↓
一致性与共识 (Ch10)
    ↓
批处理 (Ch11) ←→ 流处理 (Ch12)
```

## 相关页面

- [[sources/ebook-systems-approach]] — Systems Approach (Peterson & Davie)，网络与分布式系统教材
- [[sources/workflow-engine]] — Sogou Workflow (分布式任务流引擎)
- [[wiki/os-index]] — 操作系统基础（进程/线程/内存等）
