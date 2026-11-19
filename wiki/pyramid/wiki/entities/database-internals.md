---
type: entity
tags: [database, storage, b-tree, sql, transaction]
created: 2026-05-29
sources: [handson-db-tutorial]
---

# Database Internals

## 定义

数据库内核研究数据存储、索引、查询执行和事务管理的底层机制。从文件格式到算法，理解数据库如何将字节持久化并高效检索。

## 关键要点

### 存储引擎架构
```
SQL → Parser → Optimizer → Executor → Storage Engine
                                    ↓
                              Disk / Memory
```
- **行存储 vs 列存储**：行存储适合 OLTP（频繁写入），列存储适合 OLAP（分析查询）
- **Buffer Pool**：内存缓存页，减少磁盘 I/O
- **WAL（Write-Ahead Log）**：先写日志再写数据，崩溃恢复保证

### 索引结构

| 结构 | 代表 | 特点 |
|------|------|------|
| B-Tree | SQLite, InnoDB | 读写均衡，单路径查找 |
| B+Tree | MySQL | 数据只在叶节点，内部节点仅索引 |
| LSM-Tree | LevelDB, RocksDB | 写优化，读需要合并 |
| Hash Index | Memcached | O(1) 查找，无范围查询 |

### 事务（ACID）

- **Atomicity**：全成功或全失败，无中间态
- **Consistency**：约束检查，主键/外键/唯一索引
- **Isolation**：并发控制（MVCC / 2PL）
- **Durability**：WAL + 刷盘策略

### 查询执行

- **火山模型**：迭代器链，每个节点 `next()` 返回一行
- **向量化执行**：批量处理，减少函数调用开销
- **算子下推**：过滤/投影尽量靠近数据源

### 并发控制

- **MVCC（Multi-Version Concurrency Control）**：读不阻塞写，写不阻塞读
- **2PL（Two-Phase Locking）**：扩展阶段加锁，收缩阶段释放
- **SSI（Serializable Snapshot Isolation）**：乐观并发，冲突检测

## 相关概念

- [[sstable]] — LSM-tree 的磁盘格式
- [[lsm-tree]] — 写优化的存储引擎
- [[trees-and-graphs]] — B-Tree 的理论基础
- [[hash-table]] — Hash Index 的数据结构基础
- [[virtual-machine]] — 某些数据库（如 SQLite）使用内部 VM 执行 SQL 字节码

## 来源详情

- [[handson-db-tutorial]] — SQLite 从零实现：15个Part完整覆盖 B-Tree 存储引擎
