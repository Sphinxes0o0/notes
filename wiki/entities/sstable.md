---
type: entity
tags: [storage, SSTable, compaction, LevelDB, file-format]
created: 2026-05-28
sources: [bookmark-leveldb-handbook]
---

# SSTable

## 定义

SSTable（Sorted String Table）是LSM-tree的磁盘存储格式，以固定大小Block为单位组织，存储有序的key-value键值对，并配备布隆过滤器和索引块加速查找。

## 关键要点

### 文件结构
```
┌─────────────────────────────────────────────┐
│  Data Block 1 (4KB)  │ key-value data        │
│  Data Block 2 (4KB)  │ key-value data        │
│  ...                 │                        │
│  Data Block N (4KB)  │                        │
├─────────────────────────────────────────────┤
│  Filter Block        │ Bloom filter per 2KB  │
├─────────────────────────────────────────────┤
│  Meta Index Block    │ filter block offsets   │
├─────────────────────────────────────────────┤
│  Index Block         │ data block max-key+offset │
├─────────────────────────────────────────────┤
│  Footer (48B)        │ meta/index block ptrs  │
└─────────────────────────────────────────────┘
```

### Data Block
- key-value对按key排序存储
- **前缀压缩**：相邻key共享前缀，仅存储差异部分
- **Restart Point**：每16个entry存储完整key，用于加速查找
- 压缩算法：Snappy（默认）

### Filter Block
- 布隆过滤器数据，每2KB数据创建一个过滤器（Base Lg=11）
- 查询时先查Filter Block快速判断key是否不存在

### Index Block
- 每个Data Block的索引：最大key + 起始偏移 + block大小
- 二分查找定位目标Data Block

### Footer（48字节）
- 指向Meta Index Block和Index Block的起始偏移
- 尾部Magic Word校验

### Compaction 机制
- **Minor Compaction**：MemTable → SSTable（内存→磁盘）
- **Major Compaction**：多层SSTable合并，删除过期版本
- **触发条件**：
  - 0层文件数 > 4
  - Level i 总大小 > 10^i MB
  - seekLeft 减到0（文件长期未被访问）
- **seekLeft采样**：每16KB访问一次，未命中则递减

### 读写操作
- **写**：Data Block积累 → Filter Block更新 → Index Block追加 → Footer写入
- **读**：查Footer → 定位Index Block → 二分查找Data Block → 解压 → 遍历key-value

## 相关概念

- [[lsm-tree]] — SSTable是LSM-tree的磁盘载体
- [[bloomfilter]] — SSTable内置布隆过滤器加速查询（LevelDB Handbook单独章节）
- [[cache]] — LevelDB Handbook覆盖，LRU分片缓存
- [[linux/kernel/block/linux-kernel-block-core]] — Linux块设备层与SSTable的顺序写有相似思想

## 来源详情

- [[sources/bookmark-leveldb-handbook]] — LevelDB Handbook：SSTable格式/读写/Compaction详解
