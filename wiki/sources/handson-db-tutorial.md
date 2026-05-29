---
type: source
source-type: web
title: "Write a SQLite Clone from Scratch in C"
author: "cstack"
date: 2024-01-01
summary: "用C语言从零实现SQLite：数据存储/B-Tree/事务/索引/虚拟机的数据库内核教程"
path: raw/web/db_tutorial
---

# Write a SQLite Clone from Scratch in C

## 核心内容

### 15个Part，从REPL到完整B-Tree

| Part | Topic | 关键实现 |
|------|-------|---------|
| 1 | REPL | 简单的命令行解释器 |
| 2 | SQL Compiler + VM | 简易SQL编译器，生成虚拟机指令 |
| 3 | 单表数据库（内存） | Append-only，内存存储 |
| 4 | 测试 + Bug | 测试驱动开发 |
| 5 | 磁盘持久化 | 文件I/O，数据落盘 |
| 6 | Cursor 抽象 | 遍历结果集的游标抽象 |
| 7 | B-Tree 入门 | 多路平衡树 vs 二叉树 |
| 8 | B-Tree 叶节点格式 | 页面布局、cell 数组 |
| 9 | 二分查找 + 重复键 | B-Tree 搜索优化 |
| 10 | 叶节点分裂 | 分裂算法、上溢处理 |
| 11 | B-Tree 递归搜索 | 自顶向下查找 |
| 12 | 多级B-Tree扫描 | 跨页遍历 |
| 13 | 更新父节点 | 分裂后父节点更新 |
| 14 | 内部节点分裂 | 递归分裂，B-Tree 生长 |
| 15 | 后续方向 | 索引、事务、MVCC |

### 核心概念
- **B-Tree vs B+Tree**：SQLite 用 B-Tree（叶节点也存数据），不同于 MySQL 的 B+Tree（数据只在叶节点）
- **Cursor**：遍历抽象，隐藏 B-Tree 内部结构
- **WAL 思想**：Part 5 的 Append-only 实际是 WAL 前身
- **事务回滚**：未提交的页不刷盘，实现原子性

### 为什么选这个教程
- 极简代码量（~2000行），每个Part可独立运行
- 从 SQL 到存储引擎的全链路覆盖
- 零依赖，纯 C 实现

## 相关页面

- [[sstable]] — LSM-tree 的磁盘格式，与 B-Tree 是两种存储范式
- [[database-internals]] — 数据库内核通用概念
- [[trees-and-graphs]] — B-Tree 的图论基础

## 来源详情

- 网站: [cstack.github.io/db_tutorial](https://cstack.github.io/db_tutorial/)
- GitHub: [cstack/db_tutorial](https://github.com/cstack/db_tutorial)
