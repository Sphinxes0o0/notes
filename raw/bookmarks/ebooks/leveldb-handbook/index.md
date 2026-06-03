# LevelDB Handbook

中文 LevelDB 技术手册，涵盖架构、读写操作、日志、内存数据库、SSTable、缓存、布隆过滤器、Compaction、版本控制等核心主题。

## 目录

1. [基本概念](basic.md) - memtable、immutable memtable、log、sstable、manifest、current
2. [读写操作](rwopt.md) - 写操作、Batch、InternalKey、读操作、Snapshot
3. [日志系统](journal.md) - 日志结构、日志内容、日志写、日志读
4. [内存数据库](memorydb.md) - 跳表、内存数据库结构
5. [SSTable](sstable.md) - 文件格式、Data Block、Filter Block、Index Block、Footer
6. [缓存系统](cache.md) - LRU Cache、Dynamic-sized NonBlocking Hash Table
7. [布隆过滤器](bloomfilter.md) - 结构、数学结论、goleveldb实现
8. [Compaction](compaction.md) - Minor Compaction、Major Compaction
9. [版本控制](version.md) - Manifest、Commit、Recover、MVCC
