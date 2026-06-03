# LevelDB 读写操作

## 写操作

LevelDB通过两步实现高性能写操作：先写日志，再应用到内存数据库。写接口包括Put和Delete，Delete会被转换成空值的Put。

### Batch结构

批量操作的每条数据编码包含：类型标记(update/delete)、key长度、key内容、可选的value长度和内容。Batches维护一个跟踪总数据加每条8字节的size值。

### InternalKey编码

InternalKey在user key后追加8字节，存储sequence number和操作类型。每次数据库操作都会分配一个唯一递增的sequence number。

### 合并写

LevelDB通过将小写操作合并成大批次来优化并发写入，减少日志文件碎片，提高整体吞吐量。

## 读操作

LevelDB提供Get和基于snapshot的读取。读取过程依次检查：当前内存数据库、冻结的内存数据库、从level 0向上的sstable文件。Level 0文件因key重叠需要顺序搜索，更高层使用元数据进行快速定位。

### Snapshot

Snapshot代表某一时刻的数据库状态，实现为sequence number。使用snapshot读取会过滤掉所有sequence number大于snapshot sequence的数据项。

## 图片

- ![写操作](https://leveldb-handbook.readthedocs.io/zh/latest/_images/write_op.jpeg)
- ![Batch](https://leveldb-handbook.readthedocs.io/zh/latest/_images/batch.jpeg)
- ![InternalKey](https://leveldb-handbook.readthedocs.io/zh/latest/_images/internalkey.jpeg)
- ![写合并](https://leveldb-handbook.readthedocs.io/zh/latest/_images/write_merge.jpeg)
- ![Snapshot](https://leveldb-handbook.readthedocs.io/zh/latest/_images/snapshot.jpeg)
- ![读操作](https://leveldb-handbook.readthedocs.io/zh/latest/_images/readop.jpeg)
