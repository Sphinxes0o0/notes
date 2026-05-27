---
type: source
source-type: pdf-book
title: "Elements of Programming Interviews"
author: "Adnan Aziz, Tsung-Hsien Lee, Amit Prakash"
date: 2024-01-01
size: small
path: raw/PDFs/books/Elements of Programming Interviews.pdf
summary: "EPI 采样本：191页，面向软件工程面试的数据结构、算法、系统设计、问题解决四板斧，附 C++11 解题代码与面试策略指南。"
tags: [algorithms, data-structures, interview, system-design, problem-solving, cpp]
created: 2026-05-27
---

# Elements of Programming Interviews

> EPI 采样本（sampler），完整版见 [ElementsOfProgrammingInterviews.com](http://ElementsOfProgrammingInterviews.com)

## 核心内容

**定位**：软件工程师面试备考权威指南，聚焦四大能力维度：

| 维度 | 内容 |
|------|------|
| 数据结构 | 数组/链表/栈/队列/哈希表/树/堆/图 |
| 算法 | 排序/搜索/递归/DP/贪心/分治/回溯 |
| 系统设计 | Web搜索/文件系统/共享笔记/聊天系统 |
| 问题解决 | 四步法（理解→方案→实现→分析）|

## 面试方法论

### 四步解题法
1. **理解问题** — 边界条件、输入输出规格、corner cases
2. **穷举方案** — 先暴力解，分析复杂度找优化方向
3. **优化实现** — 选择合适数据结构，O(n) 往往可达到
4. **分析复杂度** — Time/Space，测试 corner cases

### 关键策略
- **先穷举后优化**：先写 O(n²) 暴力解，再找 DP/贪心机会
- **测试边界**：空数组、溢出、单元素、极端值
- **沟通清晰**：边想边说，展示思维过程
- **Corner case 意识**：通用解法可能在特殊输入上失败

## 数据结构模式速查

| 数据结构 | 关键点 |
|----------|--------|
| 数组/字符串 | 下标访问快，sorted 数组二分查找 |
| 链表 | 哑节点、双指针、倒数第 K 个 |
| 栈 | 匹配问题（括号）、单调栈 |
| 队列 | BFS、滑动窗口最大值 |
| 哈希表 | O(1) 查找，等价类划分 |
| 堆 | Top-K、中位数、合并有序流 |
| 二叉树 | BST 性质、递归遍历、序列化 |
| 图 | DFS/BFS、拓扑排序、最短路径 |

## 解题代码风格
- 主要语言：**C++11**（现代特性）
- 并发相关：**Java**
- 代码简洁，注释关键步骤
- 包含 randomized 测试

## 相关页面

### Interview
- [[sources/pdf-book-cracking-coding-interview]] — CTCI 第6版

### Algorithms & Data Structures
- [[datastructure-index]]

### Module Indexes
- [[interview-index]] — 编程面试模块索引
- [[datastructure-index]] — 数据结构与算法模块索引