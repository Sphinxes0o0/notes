---
type: entity
tags: [cpp, stl, containers]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL Containers

## 定义

STL 容器是标准库提供的数据结构，实现了对数据的存储、组织和访问。分为序列容器、关联容器和容器适配器三大类。

## 关键要点

### 序列容器

| 容器 | 存储方式 | 随机访问 | 插入删除 | 典型场景 |
|------|----------|----------|----------|----------|
| vector | 连续 | O(1) | 末尾O(1)，其他O(n) | 需高效遍历，大量末尾操作 |
| deque | 块状连续 | O(1) | 两端O(1) | 需高效两端操作 |
| list | 双向链表 | 不支持 | O(1) | 需频繁中间插入删除 |
| array | 固定数组 | O(1) | 不支持 | 固定大小数组 |

### 关联容器

- **有序**: set, multiset, map, multimap — 红黑树实现，O(log n) 查找
- **无序**: unordered_set, unordered_map — 哈希表实现，O(1) 平均查找

### 容器选择原则

1. **vector/string 优先** — 连续存储，缓存友好，性能最优
2. **deque 用于前后操作** — 块状存储，兼顾首尾效率
3. **list 用于频繁中间插入** — 指针链接，O(1) 插入删除
4. **set/map 用于有序需求** — 红黑树维护排序
5. **unordered_* 用于高效查找** — 哈希表，O(1) 平均复杂度

### 迭代器失效规则

- **vector/deque**: 重新分配或插入点之前的迭代器可能失效
- **list**: 删除时只失效被删元素的迭代器
- **关联容器**: 只删除被删元素的迭代器

## Effective STL 要点 (Items 1-10)

- Item 1: 谨慎选择容器类型
- Item 2: 不要毫无必要地写 `vector::erase`
- Item 3: 理解 deep copy vs shallow copy
- Item 4: 用 empty() 而非 size() == 0
- Item 5: 用 range成员函数而非单元素操作
- Item 6: 警惕迭代器解析
- Item 7: 当心 transform 和 for_each 的副作用
- Item 8: 用 iterator 代替 const_iterator
- Item 9: 用 distance 和 advance 处理 iterator arithmetic
- Item 10: 理解 reserve vs capacity

## 相关概念
- [[entities/cpp/cpp-stl-iterators]] — 容器通过迭代器访问元素
- [[entities/cpp/cpp-stl-algorithms]] — 算法作用于容器元素
- [[entities/cpp/cpp-stl-string]] — string 是特殊容器
- [[entities/cpp/cpp-stl-allocators]] — 容器通过分配器管理内存
