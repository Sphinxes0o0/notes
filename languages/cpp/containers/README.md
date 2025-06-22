# STL 容器详解

本目录包含了 C++ STL 容器的详细分析和介绍。

## 容器分类

### 序列容器 (Sequence Containers)
- [array](array.md) - 固定大小数组
- [vector](vector.md) - 动态数组
- [deque](deque.md) - 双端队列
- [forward_list](forward_list.md) - 单向链表
- [list](list.md) - 双向链表

### 容器适配器 (Container Adapters)
- [stack](stack.md) - 栈
- [queue](queue.md) - 队列
- [priority_queue](priority_queue.md) - 优先队列

### 关联容器 (Associative Containers)
- [set](set.md) - 集合
- [multiset](multiset.md) - 多重集合
- [map](map.md) - 映射
- [multimap](multimap.md) - 多重映射

### 无序关联容器 (Unordered Associative Containers)
- [unordered_set](unordered_set.md) - 无序集合
- [unordered_multiset](unordered_multiset.md) - 无序多重集合
- [unordered_map](unordered_map.md) - 无序映射
- [unordered_multimap](unordered_multimap.md) - 无序多重映射

## 容器对比表

|        容器        |    底层数据结构   |                         时间复杂度                        | 有无序 | 可不可重复 |                                     其他                                       |
|:------------------:|:--------------:|:----------------------------------------------------:|:------:|:----------:|:----------------------------------------------------------------------------:|
| array              | 数组              | 随机读改 O(1)                                             | 无序   | 可重复     | 支持随机访问                                                                 |
| vector             | 数组              | 随机读改、尾部插入、尾部删除 O(1) 头部插入、头部删除 O(n) | 无序   | 可重复     | 支持随机访问                                                                    |
| deque              | 双端队列          | 头尾插入、头尾删除 O(1)                                   | 无序   | 可重复     | 一个中央控制器 + 多个缓冲区，支持首尾快速增删，支持随机访问                       |
| forward_list       | 单向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| list               | 双向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| stack              | deque / list      | 顶部插入、顶部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| queue              | deque / list      | 尾部插入、头部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| priority_queue     | vector + max-heap | 插入、删除 O(log2n)                                       | 有序   | 可重复     | vector容器+heap处理规则                                                      |
| set                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multiset           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| map                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multimap           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| unordered_set      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multiset | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |
| unordered_map      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multimap | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |

## 选择指南

### 什么时候选择哪个容器？

1. **需要随机访问**：`vector`, `deque`, `array`
2. **频繁头尾操作**：`deque`
3. **频繁中间插入删除**：`list`, `forward_list`
4. **需要排序**：`set`, `map`
5. **快速查找**：`unordered_set`, `unordered_map`
6. **LIFO 操作**：`stack`
7. **FIFO 操作**：`queue`
8. **优先级操作**：`priority_queue` 