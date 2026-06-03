# LevelDB SSTable文件格式

## 概述

LevelDB是典型的LSM树(Log Structured-Merge Tree)实现。写入数据时，先写日志文件，再应用到memtable。当memtable数据量超过阈值时，冻结成immutable memory db，创建新memtable继续使用。

**Minor Compaction目的：**
- 有效降低内存使用率
- 避免日志文件过大，系统恢复时间过长

当内存数据持久化到文件时，LevelDB按规则组织文件，这种格式称为**SSTable**。

## SSTable文件格式

### 物理结构

SSTable文件按固定大小划分块，默认每个块4KiB。每个Block存储：
- 压缩类型（默认Snappy算法）
- CRC校验码（校验数据及压缩类型）

### 逻辑结构

| 区块类型 | 功能 |
|---------|------|
| Data Block | 存储key-value数据对 |
| Filter Block | 存储布隆过滤器数据 |
| Meta Index Block | 存储filter block的索引信息 |
| Index Block | 存储每个data block的索引信息 |
| Footer | 存储meta index block及index block的索引信息 |

## Data Block结构

Data block中的key-value数据按序存储。为节省空间，不存储完整key值，而是存储**与上一个key非共享的部分**。

**Restart Point机制：** 每隔若干个key-value对（默认16），存储完整key值，用于加速查找。

**Entry格式（5部分）：**
1. key共享部分长度
2. key非共享部分长度
3. value长度
4. key非共享内容
5. value内容

## Filter Block结构

Filter block存储data block的布隆过滤器数据，加快查询效率。

**主要组成：**
- 过滤数据（filter data）
- 索引数据（filter i offset, filter offset's offset）

**Base Lg默认值为11**，表示每2KB数据创建一个新过滤器。

## Index Block结构

Index block存储所有data block的索引信息，每条记录包含：
1. data block中最大key值
2. data block起始地址偏移量
3. data block大小

## Footer结构

固定48字节，存储meta index block与index block的索引信息，尾部存储magic word。

## 读写操作

### 写操作

**发生时机：**
- Memory db持久化到磁盘
- Compaction时重组sstable

**主要流程：**
1. 将key-value数据写入datablock
2. 将过滤信息写入filterBlock
3. 若datablock超限，执行finishBlock
4. Close时完成metaIndexBlock、indexBlock、footer写入

### 读操作

**查找流程：**
1. 检查文件句柄cache
2. 读取Footer获取元数据
3. 利用index block快速定位可能的data block
4. 使用filter block过滤
5. 在目标data block中迭代查找

**定位优化：** index block中以2条记录为比较单元快速定位。

**过滤原理：**
- 过滤显示不存在 → 一定不存在
- 过滤显示存在 → 可能存在

## 文件特点

| 特点 | 说明 |
|------|------|
| 只读性 | SSTable作为compaction结果原子性产生，其余时间只读 |
| 完整性 | 索引和过滤数据直接存储在文件中，随文件创建销毁 |
| 并发友好 | 只读性使无读写冲突，引用计数实现无锁并发访问 |
| Cache一致性 | 只读保证cache数据与文件永远一致 |

## 图片

- ![SSTable物理结构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/sstable_physic.jpeg)
- ![SSTable逻辑结构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/sstable_logic.jpeg)
- ![Data Block结构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/datablock.jpeg)
- ![Entry格式](https://leveldb-handbook.readthedocs.io/zh/latest/_images/entry_format.jpeg)
- ![Filter Block格式](https://leveldb-handbook.readthedocs.io/zh/latest/_images/filterblock_format.jpeg)
- ![Index Block格式](https://leveldb-handbook.readthedocs.io/zh/latest/_images/indexblock_format.jpeg)
- ![Footer格式](https://leveldb-handbook.readthedocs.io/zh/latest/_images/footer_format.jpeg)
- ![SSTable读流程](https://leveldb-handbook.readthedocs.io/zh/latest/_images/sstable_read_procedure.jpeg)
