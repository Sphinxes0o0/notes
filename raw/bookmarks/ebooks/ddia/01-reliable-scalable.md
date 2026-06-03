# 第一章：数据系统架构中的权衡

> 没有完美的解决方案，只有权衡取舍。 — Thomas Sowell

## Analytics vs. Transactional Systems

### OLTP vs. OLAP

- **OLTP** (Online Transaction Processing): 点查询，低延迟读写
- **OLAP** (Online Analytical Processing): 聚合查询，扫描大量数据

### 数据仓库

- ETL 过程 (Extract-Transform-Load)
- 从数据仓库到数据湖的演进
- Data Lakehouse 架构

### 记录系统 vs. 派生数据

- **记录系统 (Record System)**: 权威的真实来源
- **派生数据 (Derived Data)**: 转换/缓存的副本（索引、物化视图、缓存）

### Cloud Services vs. Self-hosted

| 方面 | 自托管 | 云原生 |
|------|--------|--------|
| 控制 | 完全 | 有限 |
| 成本 | 稳定负载可预测 | 按需付费 |
| 专业知识 | 需要 | 提供商处理运维 |

### 分布式 vs. 单机系统

- 分布式系统的权衡：复杂度 vs. 可扩展性
- 对于较小的工作负载，单机简单性通常更好

### 数据系统、法律与社会

- GDPR 和隐私法规
- 数据最小化原则
- 被遗忘权 vs. 不可变日志

## 图片

![](/fig/ddia_0101.png)

![](/fig/ddia_0102.png)
