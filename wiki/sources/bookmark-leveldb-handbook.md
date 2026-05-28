---
type: source
source-type: bookmark
title: "LevelDB Handbook"
author: "LevelDB Community"
date: 2024
summary: "中文LevelDB技术手册，涵盖LSM-tree架构、读写流程、日志、SSTable格式、缓存、布隆过滤器、Compaction、版本控制"
---

# LevelDB Handbook

## 核心内容

**LSM-tree 架构**
- Log Structured Merge Tree：写入先写日志再入内存，高写效率
- 写路径：Write-Ahead Log → MemTable → Immutable MemTable → SSTable
- 读路径：MemTable → 层0文件 → 层N文件（可能需遍历全部文件）

**基本概念**
- MemTable：跳表实现，内存有序 key-value
- Immutable MemTable：只读快照，用于 Minor Compaction
- log：WAL日志，crash recovery用
- sstable：键值对的有序磁盘文件
- manifest：版本元数据文件
- current：指向当前manifest的文件

**读写操作**
- Batch原子写：写操作先写入Batch，再批量应用
- InternalKey：user_key + sequence_num + value_type，MVCC支持
- Snapshot读：指定sequence一致性视图
- 读操作：MemTable→层0→层1→...→层N，可能需要合并多个SSTable

**SSTable文件格式**
- 固定4KiB Block存储：压缩类型 + CRC校验
- Data Block：key-value数据，restart point每16条记录压缩共享前缀
- Filter Block：布隆过滤器，每2KB数据一个过滤器
- Index Block：每个data block的最大key + 偏移量
- Footer：48字节，指向meta index和index block

**缓存系统**
- LRU Cache：分片锁，减少竞争
- NonBlocking Hash Table：dynamic-sized，分片并行

**布隆过滤器**
- 假阳性率：k个哈希函数，m比特位，n个元素
- LevelDB实现：k=2，m/n≈10bits/entry（Base Lg=11，每2KB数据一个过滤器）
- GoLevelDB优化：自定义哈希函数，避免乘法

**Compaction**
- Minor Compaction：MemTable持久化为SSTable
- Major Compaction：多层SSTable合并，0层→1层
- 触发条件：0层文件数>4、level i总大小>10^i MB、seekLeft归零
- seekLeft采样：每16KB访问一次，未命中则减一

**版本控制**
- Manifest：每个版本的文件列表和关键元数据
- VersionSet：所有版本的集合
- MVCC：sequence_num标识版本，写操作递增sequence
- Recovery：从日志恢复+应用manifest

## 来源详情

- 路径：`raw/bookmarks/ebooks/leveldb-handbook/`
- 章节：9章（基本概念/读写/日志/内存/缓存/布隆过滤器/Compaction/版本控制）
- 图片：38张（sstable格式/compaction流程/bloom过滤器等）
