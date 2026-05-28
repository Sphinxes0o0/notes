---
type: entity
tags: [storage, LSM-tree, key-value, write-optimized, database]
created: 2026-05-28
sources: [bookmark-leveldb-handbook]
---

# LSM-tree

## 定义

LSM-tree（Log Structured Merge Tree）是一种写优化的存储数据结构，通过将随机写转化为顺序写（日志写入+内存存储）来提供高写入吞吐量，适合写多读少的场景。核心思想：写入时先记日志、再存内存，满了再合并到磁盘。

## 关键要点

### 核心架构
```
写入 → WAL (日志) → MemTable (内存跳表) → Immutable MemTable → SSTable (磁盘)
```
- **WAL（Write-Ahead Log）**：崩溃恢复用，顺序写入
- **MemTable**：内存有序结构（跳表实现），支持快速读写
- **Immutable MemTable**：只读快照，用于 Minor Compaction

### 写入路径
1. 写入WAL（持久化保证）
2. 写入MemTable（内存操作，低延迟）
3. MemTable写满 → 冻结为Immutable MemTable
4. 后台 Minor Compaction 将Immutable MemTable 持久化为 SSTable

### 读路径（相对复杂）
- 先查MemTable（最新数据）
- 再查Immutable MemTable
- 最后从层0到层N依次查找SSTable
- **问题**：最差情况可能遍历所有文件

### 与 B+tree 的对比
| 特性 | LSM-tree | B+tree |
|------|---------|--------|
| 写放大 | 低（顺序写为主） | 高（随机写+节点分裂） |
| 读放大 | 高（需合并多层） | 低（单路径查找） |
| 空间放大 | 低（合并压缩） | 中（节点分裂碎片） |
| 适用场景 | 写密集 | 读密集 |

### 变种
- **LevelDB/RocksDB**：Leveled Compaction（分层）
- **Cassandra**：Size-Tiered Compaction
- **WiredTiger**：B+tree + LSM混合

## 相关概念

- [[sstable]] — LSM-tree的磁盘文件格式，Compaction的产物
- [[kernel-bypass-dpdk]] — 存储系统高性能路径（SPDK/DPDK）可参考LSM写优化思想
- [[cache-memory-design]] — 存储层次中SSD层的顺序写特性是LSM-tree的设计基础

## 来源详情

- [[sources/bookmark-leveldb-handbook]] — LevelDB Handbook：LSM-tree架构与读写流程
