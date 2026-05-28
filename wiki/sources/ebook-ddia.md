---
type: source
source-type: ebook
title: "Designing Data-Intensive Applications (DDIA)"
author: "Martin Kleppmann"
translator: "冯若航 (Vonng)"
date: 2026-05-28
size: medium
path: raw/bookmarks/ebooks/ddia/
summary: "数据密集型应用设计权威指南，涵盖数据系统架构、分布式复制/分片/事务、一致性与共识、批处理与流处理"
tags: [distributed-systems, data-engineering, replication, partitioning, transactions, consensus, CAP, OLTP, OLAP]
created: 2026-05-28
---

# Designing Data-Intensive Applications (DDIA)

来源: [ddia.vonng.com](https://ddia.vonng.com/) — Martin Kleppmann 著，冯若航 译

## 信息

- **原文**: Designing Data-Intensive Applications, O'Reilly 2017
- **译者**: 冯若航 (Vonng)
- **协议**: CC BY-NC-ND 4.0

## 核心内容

### 第一部分：数据系统基础

| 章节 | 主题 |
|------|------|
| Ch1 | 数据系统架构中的权衡 (OLTP vs OLAP, Record System vs Derived Data) |
| Ch2 | 定义非功能性需求 (可用性、性能、可扩展性) |
| Ch3 | 数据模型与查询语言 (关系型、文档型、图数据库) |
| Ch4 | 存储与检索 (LSM-Tree, B-Tree, 列式存储) |
| Ch5 | 编码与演化 (JSON/XML/Protocol Buffers/Avro, 模式演化) |

### 第二部分：分布式数据

| 章节 | 主题 |
|------|------|
| Ch6 | **复制** (单主/多主/无主，同步/异步，复制滞后问题) |
| Ch7 | **分片/分区** (哈希分片、一致性哈希、二级索引、请求路由) |
| Ch8 | **事务** (ACID、隔离级别、MVCC、2PC、可串行化) |
| Ch9 | 分布式系统的麻烦 (时钟、顺序、一致性边界) |
| Ch10 | **一致性与共识** (线性一致性、CAP、Raft、ZooKeeper) |

### 第三部分：派生数据

| 章节 | 主题 |
|------|------|
| Ch11 | 批处理 (MapReduce, Spark, Flink) |
| Ch12 | 流处理 (Kafka Streams, Apache Beam, Lambda/Kappa架构) |
| Ch13 | 流式系统的哲学 |
| Ch14 | 将事情做正确 (职业道德、数据伦理) |

## 核心概念

### 数据系统基础
- **记录系统 vs 派生数据**: 记录系统是权威真相来源，派生数据是转换/缓存的副本
- **OLTP vs OLAP**: 点查询低延迟 vs 聚合扫描大量数据
- **编码格式**: JSON/XML(人类可读) vs Protocol Buffers/Avro(二进制、高效、模式演化)

### 复制 (Ch6)
- **单主复制**: 同步(保证一致) vs 异步(高性能)；读己之写、单调读、一致前缀读
- **多主复制**: 冲突解决策略 (LWW、CRDT、操作变换)
- **无主复制**: Dynamo/Cassandra 模式，仲裁读写 (w+r>n)

### 分片/分区 (Ch7)
- **哈希分片**: 均匀分布，但范围查询效率低
- **一致性哈希**: 减少重平衡时的数据移动
- **二级索引**: 本地索引(读分散/收集) vs 全局索引(写入复杂)

### 事务 (Ch8)
- **ACID**: Atomicity(全或无), Consistency(不变式), Isolation(并发隔离), Durability(持久性)
- **隔离级别**: 读未提交 → 读已提交 → 快照隔离 → 可串行化
- **实现方式**: 实际串行执行(单线程)、2PL(悲观)、SSI(乐观)

### 一致性与共识 (Ch10)
- **CAP**: 分区时在一致性和可用性之间权衡
- **线性一致性**: 让系统看起来像只有一份数据副本
- **共识算法**: Raft、Viewstamped Replication、Zab
- **协调服务**: ZooKeeper/etcd 提供锁、租约、故障检测

### 派生数据架构
- **批处理**: MapReduce→Spark DAG→Flink流批一体
- **流处理**: Event sourcing, Kafka, LSE (Late Arrivals, Watermark)
- **Lambda**: 批+流双通道；Kappa: 纯流架构

## 相关页面

- [[sources/notes-network-fundamentals]] — 网络基础知识（分布式系统离不开网络）
- [[sources/notes-datastructure]] — 数据结构（分布式算法基础）
- [[sources/notes-interview]] — 系统设计基础（CAP、三主复制、分布式事务）
- [[sources/workflow-engine]] — Sogou Workflow (分布式任务流引擎)

## Related Concepts

- [[entities/distributed-systems]] — (待创建)
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络协议栈
