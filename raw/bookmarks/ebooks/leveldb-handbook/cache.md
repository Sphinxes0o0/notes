# 缓存系统

缓存对于一个数据库读性能的影响十分巨大，倘若leveldb的每一次读取都会发生一次磁盘的IO，那么其整体效率将会非常低下。

Leveldb中使用了一种基于LRUCache的缓存机制，用于缓存：
- 已打开的sstable文件对象和相关元数据；
- sstable中的dataBlock的内容；

使得在发生读取热数据时，尽量在cache中命中，避免IO读取。

## Cache结构

leveldb中使用的cache是一种LRUcache，其结构由两部分内容组成：
- Hash table：用来存储数据；
- LRU：用来维护数据项的新旧信息；

其中Hash table是基于Yujie Liu等人的论文《Dynamic-Sized Nonblocking Hash Table》实现的。由于hash表一般需要保证插入、删除、查找等操作的时间复杂度为 O(1)。

当hash表的数据量增大时，需要对hash表进行resize，即改变hash表中bucket的个数，对所有数据进行重散列。基于该文章实现的hash table可以实现resize的过程中**不阻塞其他并发的读写请求**。

LRU中则根据Least Recently Used原则进行数据新旧信息的维护，当整个cache中存储的数据容量达到上限时，便会根据LRU算法自动删除最旧的数据。

## Dynamic-sized NonBlocking Hash Table

liu等人提出了一个新颖的概念：**一个bucket的数据是可以冻结的**。

这个特点极大地简化了hash表在resize过程中在不同bucket之间转移数据的复杂度。

### 散列

该哈希表的散列与普通的哈希表一致，都是借助散列函数，将用户需要查找、更改的数据散列到某一个哈希桶中，并在哈希桶中进行操作。由于一个哈希桶的容量是有限的（一般不大于32个数据），因此在哈希桶中进行插入、查找的时间复杂度可以视为是常量的。

### 扩大

当cache中维护的数据量太大时，会发生哈希表扩张的情况。以下两种情况是为"cache中维护的数据量过大"：
- 整个cache中，数据项（node）的个数超过预定的阈值；
- 当cache中出现了数据不平衡的情况。当某些桶的数据量超过了32个数据，即被视作数据发生散列不平衡；

一次扩张的过程为：
1. 计算新哈希表的哈希桶个数（扩大一倍）；
2. 创建一个空的哈希表，并将旧的哈希表转换为一个"过渡期"的哈希表，表中的每个哈希桶都被"冻结"；
3. 后台利用"过渡期"哈希表中的"被冻结"的哈希桶信息对新的哈希表进行内容构建；

**值得注意的是，在完成新的哈希表构建的整个过程中，哈希表并不是拒绝服务的，所有的读写操作仍然可以进行。哈希表扩张过程中，最小的封锁粒度为哈希桶级别。**

### 缩小

当哈希表中数据项的个数少于哈希桶的个数时，需要进行收缩。收缩时，哈希桶的个数变为原先的一半，2个旧哈希桶的内容被合并成一个新的哈希桶。

## LRU

Leveldb中，LRU利用一个双向循环链表来实现。每一个链表项称之为`LRUNode`。

```go
type lruNode struct {
    n   *Node // customized node
    h   *Handle
    ban bool
    next, prev *lruNode
}
```

LRU提供了以下几个接口：
- **Promote**: 若一个hash表中的节点是第一次被创建，则为该节点创建一个`LRUNode`，并将`LRUNode`置于链表的头部；若将`LRUNode`移至链表头部；若超出容量上限，根据策略清除部分节点。
- **Ban**: 将hash表节点对应的`LRUNode`从链表中删除，并"尝试"从哈希表中删除数据。

## 缓存数据

leveldb利用上述的cache结构来缓存数据。其中：
- **cache**: 来缓存已经被打开的sstable文件句柄以及元数据（默认上限为500个）；
- **bcache**: 来缓存被读过的sstable中dataBlock的数据（默认上限为8MB）；

## 参考文献

- "Dynamic-Sized Nonblocking Hash Tables", by Yujie Liu, Kunlong Zhang, and Michael Spear. ACM PODC, Jul 2014.

## 图片

- ![Cache架构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/cache_arch.jpeg)
- ![哈希选择](https://leveldb-handbook.readthedocs.io/zh/latest/_images/cache_select.jpeg)
- ![哈希表扩张](https://leveldb-handbook.readthedocs.io/zh/latest/_images/cache_expend.jpeg)
