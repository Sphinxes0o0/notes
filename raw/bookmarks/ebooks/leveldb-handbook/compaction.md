# Compaction

Compaction是leveldb最为复杂的过程之一，同样也是leveldb的性能瓶颈之一。

## Compaction的作用

### 数据持久化

leveldb是典型的LSM树实现，因此需要对内存中的数据进行持久化。一次内存数据的持久化过程称为**Minor Compaction**。

### 提高读写效率

leveldb是一个写效率十分高的存储引擎。相比来说，读操作复杂不少。由于0层文件中可能存在overlap，在最差情况下，可能需要遍历所有的文件。

因此leveldb设计了**Major Compaction**，将0层中的文件合并为若干个没有数据重叠的1层文件。

### 平衡读写差异

- 当0层文件数量超过`SlowdownTrigger`时，写入速度减慢
- 当0层文件数量超过`PauseTrigger`时，写入暂停，直至Major Compaction完成

### 整理数据

leveldb在major compaction过程中，对不同版本的数据项进行合并，只保留最新版本以减少磁盘空间占用。

## Compaction过程

### Minor Compaction

一次minor compaction非常简单，其本质就是将一个内存数据库中的所有数据持久化到一个磁盘文件中。Minor compaction优先级高于major compaction。

### Major Compaction

#### 触发条件

1. **0层文件数超限**：超过预定的上限（默认为4个）
2. **非0层文件大小超限**：level i层文件的总大小超过(10 ^ i) MB
3. **文件无效读取次数过多**：seekLeft减少到0时触发

#### 采样探测

在每个sstable文件的元数据中有`seekLeft`字段，默认为文件大小除以16KB。正常的数据访问会顺带进行采样探测：若在该文件中访问不命中，则对seekLeft做减一操作。

#### 过程

1. 寻找合适的输入文件
2. 根据key重叠情况扩大输入文件集合
3. 多路合并
4. 积分计算

**积分计算**：将得分最高的层数记录，若该得分超过1，则为下一次进行合并的层数。

## 用户行为

用户在使用leveldb时，可以尽量将大批量需要写入的数据进行预排序，利用空间局部性，尽量减少多路合并的IO开销。

## 图片

- ![Minor Compaction](https://leveldb-handbook.readthedocs.io/zh/latest/_images/minor_compaction.jpeg)
- ![Major Compaction](https://leveldb-handbook.readthedocs.io/zh/latest/_images/major_compaction.jpeg)
- ![Compaction扩展](https://leveldb-handbook.readthedocs.io/zh/latest/_images/compaction_expand.jpeg)
- ![Table Merge](https://leveldb-handbook.readthedocs.io/zh/latest/_images/table_merge.jpeg)
