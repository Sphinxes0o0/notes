---
type: entity
tags: [distributed-systems, partitioning, sharding, scalability, data-engineering]
created: 2026-05-28
sources: [ebook-ddia]
---

# Partitioning / Sharding (分片)

## 定义

将数据分割成更小的分片（partition/shard），存储在不同的节点上，以实现水平扩展。是处理大规模数据集的核心技术。

## 关键要点

### 分片策略

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **按键范围分片** | 按 key 范围划分 (e.g., [a-f], [g-m]) | 范围查询高效 | 热点风险 |
| **按键哈希分片** | hash(key) mod N | 负载均匀 | 范围查询低效 |
| **一致性哈希** | 环形哈希空间，减少重平衡 | 节点变化时移动数据少 | 实现复杂 |

### 一致性哈希 (Consistent Hashing)

- 将 key 和节点都映射到同一个环形哈希空间
- 节点变化时，只需重新分配环上一小段区间
- 减少数据迁移量，适合动态扩容场景

### 请求路由

三种方式：
1. **客户端直连**: 客户端知道分片位置
2. **路由层**: 专用中间件 (e.g., MySQL Proxy, Vitess)
3. **协调节点**: 每个节点都知晓全局分布 (e.g., MongoDB mongos)

### 分片与二级索引

**本地二级索引 (Local Index):**
- 每个分片维护自己的索引
- 读取需要"分散/收集" (Scatter/Gather) 查询所有分片

**全局二级索引 (Global Index):**
- 跨所有分片的统一索引
- 写入可能影响多个索引分片
- 例：DynamoDB GSI, Cassandra SASI

### 分片挑战

- **跨分片事务**: 无法用单节点事务保护，需要 2PC 或补偿事务
- **跨分片 JOIN**: 需要应用层聚合
- **数据倾斜 (Hotspot)**: 大 key 或热点 key 导致不均匀

## 相关概念

- [[entities/distributed-systems/replication]] — 复制与分片通常结合 (每分片多副本)
- [[entities/distributed-systems/transactions]] — 跨分片事务是难点
- [[entities/distributed-systems/distributed-consensus]] — 分片路由依赖一致性协议

## 来源详情

- [[sources/ebook-ddia]] — Ch7 分片
