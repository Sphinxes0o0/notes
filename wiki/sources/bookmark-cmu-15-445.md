---
type: source
source-type: bookmark
title: "CMU 15-445/645: Intro to Database Systems"
author: "Carnegie Mellon University"
date: 2026-05-29
size: medium
path: https://15445.courses.cs.cmu.edu/fall2025/
summary: "CMU introductory database systems course covering DBMS internals: storage, indexing, query processing, transaction management, and recovery."
---

# CMU 15-445: Intro to Database Systems

## Core Content

In-person + recorded course on database management system internals. Uses C++ with BusTub educational DB.

### Key Topics
- **Storage**: Disk vs memory, page layouts, tuple storage, column stores
- **Indexing**: B+ trees, hash indexes, skiplists, R-trees, LSM-trees
- **Query Processing**: Sort-merge join, hash join, nested loop join, vectorized execution
- **Query Optimization**: Cost models, cardinality estimation, join ordering
- **Transactions**: ACID properties, isolation levels (MVCC, SSI), locking protocols
- **Recovery**: ARIES recovery algorithm, write-ahead logging, checkpoints
- **Distributed DBs**: Sharding, replication, two-phase commit

### Course Details
- Textbook: Database System Concepts (Silberschatz)
- Language: C++ (BusTub DBMS implementation)
- Format: 9 labs + midterm + final
- Public: Lectures on YouTube (CMU-DB channel)

## Why This Matters for Pyramid Wiki

- Complements [[lsm-tree]] and [[sstable]] (LSM-tree storage engine internals)
- Adds depth to [[distributed-systems]] — distributed transactions, two-phase commit
- Relevant to database systems architecture discussions
- Related to [[concurrency]] — MVCC, transaction isolation

## Related Pages
- [[lsm-tree]] - log-structured merge-tree storage
- [[sstable]] - sorted string table format
- [[distributed-consensus]] - consensus in distributed systems
- [[concurrency]] - concurrency control
