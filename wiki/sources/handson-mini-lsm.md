---
type: source
source-type: web
title: "Build Your Own LSM-Tree in a Week (mini-lsm)"
author: "SkyZH"
date: 2024-01-01
summary: "Rust实现完整LSM-Tree存储引擎：Week 1覆盖SSTable/MemTable/WAL/Compaction，Week 2覆盖MVCC与并发控制"
path: raw/web/mini-lsm
---

# Build Your Own LSM-Tree in a Week (mini-lsm)

## 核心内容

### Week 1 — 存储格式基础

| Day | Topic | 关键实现 |
|-----|-------|---------|
| 1 | SSTable 格式 | 有序键值对磁盘文件，稀疏索引 |
| 2 | MemTable | 跳表（SkipList）实现，支持快速读写 |
| 3 | WAL (Write-Ahead Log) | 崩溃恢复，顺序写入日志 |
| 4 | 读路径 | MemTable + SSTable 多层合并查找 |
| 5 | 写路径 | WAL + MemTable，MemTable 满后 flush |
| 6 | Compaction 策略 | Leveled vs Size-Tiered，空间/读/写放大 |
| 7 | Review | 整体架构串讲 |

### Week 2 — MVCC 与并发控制

| Day | Topic | 关键实现 |
|-----|-------|---------|
| 8-9 | MVCC 基础 | 多版本快照，事务 ID 标记 |
| 10-11 | 并发控制 | 2PL 或乐观锁 |
| 12-13 | Compaction + MVCC | 合并时的版本清理 |
| 14 | Review | 整体架构串讲 |

### 核心理念
- **Rust 所有权模型**：天然适合表达可变/共享状态
- **手把手**：每天 2-3 小时，7 天完成 Week 1
- **mini-lsm-lab**：配套实验框架，可运行测试

### 与 LevelDB Handbook 对比
- LevelDB Handbook 偏理论，mini-lsm 偏实战
- mini-lsm 用 Rust 实现（内存安全），LevelDB 用 C++
- mini-lsm 有完整的 Week 2 MVCC 内容

## 相关页面

- [[lsm-tree]] — LSM-tree 核心概念：写优化、Compaction 策略
- [[sstable]] — LSM-tree 的磁盘文件格式
- [[database-internals]] — 数据库内核通用概念

## 来源详情

- 网站: [skyzh.github.io/mini-lsm](https://skyzh.github.io/mini-lsm/)
- 配套: [mini-lsm-lab](https://skyzh.github.io/mini-lsm/)
