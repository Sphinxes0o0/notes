# 内存数据库

## 跳表

跳表由William Pugh提出，使用概率平衡简化insert/delete操作，同时保持O(log n)效率——比平衡树更容易实现。

**结构**：分层构建。底层是排序链表；每一高层作为一个"快速通道"，元素以概率p（通常0.5）出现。

**搜索**：从最高层header开始，比较值，若大于目标值则下沉到下一层。

**插入**：搜索时记录每层的前驱节点，为新节点生成随机高度，像链表一样插入。

**删除**：搜索定位节点，从每层链表中移除。

## 代码示例

```go
func (p *DB) randHeight() (h int) {
    const branching = 4
    h = 1
    for h < tMaxHeight && p.rnd.Int()%branching == 0 {
        h++
    }
    return
}
```

## 内存数据库结构

```go
type DB struct {
    cmp comparer.BasicComparer
    rnd *rand.Rand
    mu     sync.RWMutex
    kvData []byte
    nodeData  []int
    prevNode  [tMaxHeight]int
    maxHeight int
    n         int
    kvSize    int
}
```

**Key编码(internalKey)**：User key + sequence number + type (update/delete)。Sequence number用于在重复key时标识最新值。

**比较规则**：先按user key字典序比较；若相等，sequence number越大 = internalKey越小（确保最新数据被先读到）。

## 图片

- ![跳表效果](https://leveldb-handbook.readthedocs.io/zh/latest/_images/skiplist_effect.jpeg)
- ![跳表介绍](https://leveldb-handbook.readthedocs.io/zh/latest/_images/skiplist_intro.jpeg)
- ![跳表架构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/skiplist_arch.png)
- ![跳表搜索](https://leveldb-handbook.readthedocs.io/zh/latest/_images/skiplist_search.jpeg)
- ![跳表插入](https://leveldb-handbook.readthedocs.io/zh/latest/_images/skiplist_insert.jpeg)
- ![InternalKey](https://leveldb-handbook.readthedocs.io/zh/latest/_images/internalkey.jpeg)
