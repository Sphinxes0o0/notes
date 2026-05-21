---
type: entity
tags: [数据结构, 算法, 复杂度分析]
created: 2026-05-20
sources: [notes-overview-datastructure]
---

# 算法复杂度分析 (Algorithm Complexity Analysis)

## 定义

复杂度是衡量代码运行效率的重要度量因素，包括**时间复杂度**和**空间复杂度**。复杂度是输入数据量 n 的函数，记作 O(f(n))。

## 关键要点

- **时间复杂度**：代码执行消耗的时间资源，与代码结构高度相关
- **空间复杂度**：代码执行消耗的存储资源，与数据结构设计相关
- **O(1)**：有限可数的资源消耗，与输入数据量 n 无关
- **O(n)**：线性相关，与输入规模成正比
- **O(log n)**：对数相关，如二分查找
- **O(n²)**：平方级，如双层嵌套循环

## 复杂度计算原则

1. **常系数无关**：O(n) 和 O(2n) 表示同样的复杂度
2. **多项式相加取高阶**：O(n²) + O(n) = O(n²)
3. **顺序执行**：O(n) + O(n) = O(n)
4. **嵌套执行**：O(n) × O(n) = O(n²)

## 复杂度与代码结构的关系

| 代码结构 | 时间复杂度 |
|---------|----------|
| 顺序语句 | O(1) |
| 单层 for 循环 | O(n) |
| 二分查找（分治） | O(log n) |
| 双层嵌套循环 | O(n²) |
| 二分策略（分治） | O(log n) |

## 为什么要降低复杂度

在大数据环境下，不同复杂度差异悬殊：
- O(n²)：10万条数据 → ~100亿次计算
- O(n)：10万条数据 → ~10万次计算
- O(log n)：10万条数据 → ~17次计算

## 相关概念

- [[entities/datastructure/linear-data-structures]] — 线性表增删查操作
- [[entities/datastructure/sorting-algorithms]] — 排序算法的复杂度对比
- [[entities/datastructure/dynamic-programming]] — DP 的复杂度分析
- [[entities/interview/problem-solving-patterns]] — 复杂度在解题中的应用

## 来源详情

- github-sphinxes0o0-notes-datastructure — `01_复杂度_如何衡量程序运行的效率`
## Related Concepts

- [[entities/interview/system-design-basics]] — 系统设计需要算法复杂度分析
