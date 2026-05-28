---
type: entity
tags: [distributed-systems, replication, data-engineering, consistency, CAP]
created: 2026-05-28
sources: [ebook-ddia]
---

# Replication (复制)

## 定义

在多个节点上保留同一份数据的副本，以提高容错性和读取吞吐量。是分布式数据系统的基石技术之一。

## 关键要点

### 复制拓扑

| 拓扑 | 特点 | 典型场景 |
|------|------|----------|
| **单主复制** | 1 leader + N followers，写经 leader | MySQL/PostgreSQL 主从 |
| **多主复制** | 多地区各有 leader，本地写异步复制 | 全局部署的 Web 应用 |
| **无主复制** | 任意节点接受写入 (Dynamo 风格) | Cassandra, Riak |

### 单主复制细节

**同步 vs 异步：**
- **同步复制**: follower 确认后才返回客户端，保证 follower 有最新数据；但写入可能阻塞
- **异步复制**: leader 可继续处理写入，但故障时可能丢失数据

**复制滞后问题与解决方案：**
- **读己之写 (Read-your-writes)**: 客户端写后读主节点，或通过 `sync_to_master` 标记
- **单调读 (Monotonic reads)**: 同一用户按顺序读取，不见时间倒退（非线性化）
- **一致前缀读 (Consistent prefix reads)**: 防止因果关系违规（如"先看到回复再看到提问"）

### 多主复制

**写入冲突解决策略：**
- **冲突避免**: 所有写入经同一 leader 处理
- **最后写入胜利 (LWW)**: 使用最大时间戳，可能丢失数据
- **CRDT (无冲突复制数据类型)**: G-Counter, PN-Counter, OR-Set 等，支持合并
- **操作变换 (Operational Transformation)**: 协作文档编辑（如 Google Docs）

### 无主复制 (Dynamo 风格)

**仲裁读写：**
- n 个副本，每次写入 w 个节点确认，每次读取 r 个节点
- 只要 **w + r > n**，保证读取到最新值
- 例：n=3, w=2, r=2 → 任意 1 节点宕机仍可服务

**修复机制：**
- 读修复 (Read repair): 读取时检测过期副本并修复
- 反熵 (Anti-entropy): 后台同步进程修复不一致

### 复制日志

- **基于语句**: `STATEMENT` 格式，问题：非确定性函数 (NOW(), RAND())
- **基于 WAL**: PostgreSQL/VIX，对象级但格式紧耦合
- **基于行**: Row-based replication，MySQL DML
- **基于触发器**: 自定义应用逻辑，灵活但开销大

## 相关概念

- [[entities/distributed-systems/partitioning]] — 分片与复制通常结合使用
- [[entities/distributed-systems/transactions]] — 跨节点的事务需要协调复制
- [[entities/distributed-systems/distributed-consensus]] — 共识算法解决复制冲突
- [[entities/distributed-systems/distributed-troubles]] — 复制滞后、网络分区问题

## 来源详情

- [[sources/ebook-ddia]] — Ch6 复制
