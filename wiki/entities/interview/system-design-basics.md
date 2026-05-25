---
type: entity
tags: [面试, 系统设计, 架构, 可扩展性]
created: 2026-05-20
sources: [notes-overview-interview, pdf-algorithms-books]
---

# 系统设计基础 (System Design Basics)

## 定义

系统设计面试考察候选人设计大规模分布式系统的能力，适用于有 4 年以上工作经验的候选人。

## 核心概念

### 可扩展性 (Scalability)

- **垂直扩展 (Scale Up)**：增加单台服务器容量，简单但有上限
- **水平扩展 (Scale Out)**：增加服务器数量，更复杂但无上限

### 负载均衡

将请求分发到多个服务器：
- Round Robin（轮询）
- Least Connections（最少连接）
- IP Hash（IP 哈希）

### 数据库扩展

- **读写分离**：主库（写）→ 从库（读）
- **分片 (Sharding)**：按用户 ID、时间范围、哈希分片
- **NoSQL**：Key-Value、Document、Column、Graph

### 缓存策略

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| Cache-Aside | 应用自行管理 | 读多写少 |
| Read-Through | 缓存自动加载 | 通用场景 |
| Write-Through | 同步写缓存和DB | 一致性要求高 |
| Write-Behind | 异步写入DB | 写入性能要求高 |

**缓存淘汰算法**：LRU、LFU、FIFO

### 消息队列

解耦和异步处理：生产者 → 消息队列 → 消费者
- RabbitMQ、Kafka、SQS、Redis Pub/Sub

## 设计流程

### Step 1: 理解问题与范围
- 明确功能需求
- 询问用户规模（DAU、并发量）
- 确定性能要求

### Step 2: 粗略设计
- 画出核心组件
- 明确数据流
- 识别瓶颈

### Step 3: 深入设计
- API 设计
- 数据库 Schema
- 缓存策略
- 扩展方案

### Step 4: 权衡与讨论
- 可用性 vs 一致性
- 复杂度 vs 性能
- 成本 vs 效率

## 常见系统设计题

### 1. 设计短链接服务
- 长链接 → 短链接（哈希/自增ID）
- 短链接 → 长链接（查询+重定向）

### 2. 设计推特/微博
- 核心挑战：主页时间线生成（Pull vs Push 模型）

### 3. 设计聊天系统
- WebSocket 实时通信
- 离线消息队列

### 4. 设计搜索建议/自动补全
- 前缀 → Trie 树 → 候选集 → 排序

### 5. 设计限流器
- 计数器、滑动窗口、令牌桶、漏桶

## CAP 定理

分布式系统最多同时满足两个：
- **C (Consistency)** — 一致性
- **A (Availability)** — 可用性
- **P (Partition Tolerance)** — 分区容错

常见选择：CP (Redis)、AP (Cassandra)

## 一致性哈希

解决数据分片时的负载均衡问题：
- 将服务器和数据映射到同一个环上
- 数据顺时针找最近的服务器
- 新增/删除只影响局部数据

## 相关概念

- [[entities/interview/interview-preparation]] — 面试准备方法论
- [[entities/design-patterns/structural-patterns]] — 门面模式（API 网关）

## 来源详情

- github-sphinxes0o0-notes-interview — `03_系统设计基础`
