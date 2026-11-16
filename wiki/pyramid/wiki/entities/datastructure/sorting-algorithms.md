---
type: entity
tags: [数据结构, 排序算法, 算法]
created: 2026-05-20
sources: [notes-overview-datastructure, pdf-algorithms-books]
---

# 排序算法 (Sorting Algorithms)

## 定义

排序是让一组**无序数据变成有序**的过程，默认通常指从小到大的排列顺序。

## 关键要点

### 排序算法衡量标准

1. **时间复杂度**：最好、最坏、平均
2. **空间复杂度**：O(1) 称为原地排序
3. **稳定性**：相等元素排序后顺序是否保持不变

### 四大经典排序算法

| 算法 | 最好 | 最坏 | 平均 | 空间 | 稳定性 |
|------|------|------|------|------|--------|
| 冒泡排序 | O(n) | O(n²) | O(n²) | O(1) | 稳定 |
| 插入排序 | O(n) | O(n²) | O(n²) | O(1) | 稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n log n) | O(n) | 稳定 |
| 快速排序 | O(n log n) | O(n²) | O(n log n) | O(1) | 不稳定 |

### 算法思想对比

- **冒泡/插入排序**：暴力 O(n²)，适合小数据
- **归并排序**：分治法，O(n log n)，需额外空间
- **快速排序**：分治法，O(n log n) 平均，原地排序但不稳定

### 分治法排序

归并和快排都采用分治思想：
1. **分解**：将数组不断二分
2. **解决**：递归处理子问题
3. **合并**：合并有序子数组

## 排序算法选择策略

- 数据规模小 → O(n²) 算法足够（差异仅几十毫秒）
- 数据规模大 → 选择 O(n log n) 算法
- 需要稳定排序 → 选择归并排序
- 空间受限 → 选择快速排序

## 相关概念

- [[entities/datastructure/algorithm-complexity]] — 复杂度分析
- [[entities/datastructure/recursion-and-divide-conquer]] — 分治法的详细讨论
- [[entities/interview/problem-solving-patterns]] — 排序在解题中的应用

## 来源详情

- github-sphinxes0o0-notes-datastructure — `13_排序_经典排序算法原理解析与优劣对比`
