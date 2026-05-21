---
type: entity
tags: [算法, 递归, 分治法]
created: 2026-05-20
sources: [notes-overview-datastructure]
---

# 递归与分治法 (Recursion & Divide and Conquer)

## 定义

**递归**：函数调用自身来解决问题的方法。
**分治法**：将原问题分解为若干独立子问题，分别解决后再合并。

## 关键要点

### 递归汉诺塔问题

经典递归问题：将 n 个圆盘从 A 柱移动到 C 柱
- 终止条件：n=1 时直接移动
- 递归步骤：借助 B 柱中转，分三步完成

### 分治法四条件

使用分治法必须满足：
1. 问题的解决难度与数据规模有关
2. 原问题可被分解
3. 子问题的解可以合并为原问题的解
4. **所有子问题相互独立**（这是与 DP 的关键区别）

### 二分查找（分治策略）

在有序数组中查找目标值：
- 复杂度：O(log n)
- 每次将搜索空间缩小一半
- 迭代实现更高效（避免递归调用开销）

### 分治排序

- **归并排序**：先二分再合并，O(n log n)
- **快速排序**：选分区点，左右递归，O(n log n) 平均

## 递归 vs 迭代

| 方面 | 递归 | 迭代 |
|------|------|------|
| 空间 | O(n) 调用栈 | O(1) |
| 代码简洁度 | 更简洁 | 较复杂 |
| 性能 | 有函数调用开销 | 无额外开销 |
| 适用场景 | 问题本身有递归结构 | 可直接循环解决 |

## 相关概念

- [[entities/datastructure/sorting-algorithms]] — 分治排序算法
- [[entities/datastructure/dynamic-programming]] — 分治法满足不了第4条件时的替代方案
- [[entities/interview/problem-solving-patterns]] — 递归在面试题中的应用

## 来源详情

- github-sphinxes0o0-notes-datastructure — `11_递归_如何利用递归求解汉诺塔问题`, `12_分治_如何利用分治法完成数据查找`
