---
type: entity
tags: [cpp, stl, algorithms]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL Algorithms

## 定义

STL 算法是独立于容器的函数模板，通过迭代器对容器范围内的元素进行操作。分为非修改性算法和修改性算法两大类。

## 关键要点

### 算法分类

**非修改性算法**
- `for_each` — 对范围内每个元素执行操作
- `count/count_if` — 计数满足条件的元素
- `find/find_if` — 查找满足条件的元素
- `equal` — 比较两个范围
- `search` — 在范围内搜索子序列

**修改性算法**
- `transform` — 对元素进行转换
- `copy/copy_if` — 复制元素到目标
- `replace/replace_if` — 替换满足条件的元素
- `remove/remove_if` — 移除满足条件的元素（注意返回尾后迭代器）
- `unique` — 移除相邻重复元素

**排序算法**
- `sort` — O(n log n) 快速排序，非稳定
- `stable_sort` — O(n log n) 稳定排序
- `partial_sort` — 部分排序
- `nth_element` — 找第 n 小的元素

**二分查找**（用于有序容器）
- `lower_bound` — 第一个不小于 value 的位置
- `upper_bound` — 第一个大于 value 的位置
- `equal_range` — pair<lower, upper>
- `binary_search` — 判断是否存在

### remove/erase 惯用法

```cpp
// 错误：remove 返回尾后迭代器，不真正删除
vec.erase(remove(vec.begin(), vec.end(), 42)); // 正确

// 关联容器没有 remove 成员函数，需用 erase + find
auto it = myset.find(42);
if (it != myset.end()) myset.erase(it);
```

### 算法复杂度保证

| 算法 | 时间复杂度 |
|------|------------|
| non-modifying sequence ops | O(n) |
| sort, stable_sort | O(n log n) |
| binary_search | O(log n) |
| min/max | O(n) |

## Effective STL 要点 (Items 16-32)

- Item 16: 理解 pass by value vs pass by reference
- Item 17: 用 empty() 代替检查 size() == 0
- Item 18: 用 vector/string 替代动态分配的数组
- Item 19: 理解相等性 vs 等价性
- Item 20: 避免直接用 for_each 以外的算法替代手写循环
- Item 21: 让容器的成员函数完成其职责
- Item 22: 用区间成员函数代替单元素操作
- Item 23: 考虑用算法替代手写循环
- Item 24: 当心 64 位系统的移植性
- Item 25: 熟悉非标准哈希表

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — 算法作用于容器
- [[entities/cpp/cpp-stl-iterators]] — 算法通过迭代器访问元素
- [[entities/cpp/cpp-stl-functors]] — 算法常配合函数对象使用
- [[entities/cpp/cpp-stl-string]] — 字符串容器支持的算法
- [[sources/bookmark-stl-source-analysis]] — SGI STL 源码分析，揭示 copy/rotate/sort 等算法实现细节
