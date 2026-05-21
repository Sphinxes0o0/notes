---
type: entity
tags: [数据结构, 哈希表, 散列表, O(1)查找]
created: 2026-05-20
sources: [notes-overview-datastructure]
---

# 哈希表 (Hash Table)

## 定义

哈希表是一种通过**哈希函数**将键映射到数组索引的数据结构，实现平均 O(1) 的查找、插入、删除性能。

## 关键要点

### 哈希函数

将任意长度的输入转换为固定长度的输出（数组下标）：
- **直接定址法**：H(key) = a × key + b
- **除留余数法**：H(key) = key mod p
- **平方取中法**：取 key² 中间几位

### 哈希冲突处理

1. **开放寻址法**：线性探测、二次探测、双重哈希
2. **链地址法**：冲突元素形成链表（Java HashMap 用法）
3. **再哈希法**：使用第二个哈希函数

### 哈希表设计考量

- **装填因子**：α = n/m（元素数/槽数），超过 0.7-0.8 时需扩容
- **哈希函数质量**：决定冲突概率
- **冲突解决方法**：影响查找性能

## 复杂度

| 操作 | 平均 | 最坏 |
|------|------|------|
| 查找 | O(1) | O(n) |
| 插入 | O(1) | O(n) |
| 删除 | O(1) | O(n) |

## 相关概念

- [[entities/datastructure/linear-data-structures]] — 线性表对比
- [[entities/datastructure/algorithm-complexity]] — 为什么 O(1) 很重要
- [[entities/interview/problem-solving-patterns]] — 哈希表在解题中的应用

## 来源详情

- github-sphinxes0o0-notes-datastructure — `10_哈希表_如何利用好高效率查找的利器`
