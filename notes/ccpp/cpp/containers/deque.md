# std::deque 详解

## 概述

`std::deque`（double-ended queue，双端队列）是一个支持在两端进行高效插入和删除操作的序列容器。它提供了类似于vector的随机访问能力，但在头部操作方面性能更优。

## 特性

- **底层数据结构**：分段连续的内存块（通常使用map结构管理多个固定大小的缓冲区）
- **时间复杂度**：
  - 随机访问：O(1)
  - 头尾插入、删除：O(1)
  - 中间插入、删除：O(n)
- **有序性**：无序（保持插入顺序）
- **重复性**：可重复
- **随机访问**：支持
- **大小**：运行时可变

## 内部结构

deque 内部通常由以下部分组成：
- **中央控制器（map）**：指向各个缓冲区的指针数组
- **缓冲区（buffer）**：固定大小的连续内存块
- **迭代器**：复杂的迭代器结构，能够跨缓冲区移动

```
Map (中央控制器)
┌─────┐    ┌──────────┐
│  *  │───▶│ Buffer 1 │
├─────┤    ├──────────┤
│  *  │───▶│ Buffer 2 │
├─────┤    ├──────────┤
│  *  │───▶│ Buffer 3 │
├─────┤    ├──────────┤
│  *  │───▶│ Buffer 4 │
└─────┘    └──────────┘
```

## 主要函数

|             方法             |     分类       |                                      含义                                       |
|:----------------------------:|:-------------:|:------------------------------------------------------------------------------:|
| begin/end                    | iterators     | 返回指向首/尾后元素的迭代器                                                        |
| rbegin/rend                  | iterators     | 返回反向迭代器                                                                    |
| cbegin/cend                  | iterators     | 返回常量迭代器                                                                    |
| size                         | capacity      | 返回容器中元素的数量                                                              |
| max_size                     | capacity      | 返回容器可容纳的最大元素数                                                        |
| empty                        | capacity      | 检查容器是否为空                                                                  |
| shrink_to_fit                | capacity      | 请求移除未使用的容量                                                              |
| operator[]                   | element access| 返回指定位置元素的引用（不检查边界）                                               |
| at                          | element access| 返回指定位置元素的引用（检查边界）                                                 |
| front                       | element access| 返回首元素的引用                                                                  |
| back                        | element access| 返回末元素的引用                                                                  |
| assign                      | modifiers     | 分配给容器新的内容                                                                |
| push_front                  | modifiers     | 将元素添加到开头                                                                  |
| pop_front                   | modifiers     | 移除首元素                                                                        |
| push_back                   | modifiers     | 将元素添加到末尾                                                                  |
| pop_back                    | modifiers     | 移除末元素                                                                        |
| insert                      | modifiers     | 在指定位置插入元素                                                                |
| erase                       | modifiers     | 移除指定位置的元素                                                                |
| swap                        | modifiers     | 与另一deque交换内容                                                               |
| clear                       | modifiers     | 清除所有元素                                                                      |
| emplace_front               | modifiers     | 在开头构造元素                                                                    |
| emplace_back                | modifiers     | 在末尾构造元素                                                                    |

## 使用示例

```cpp
#include <deque>
#include <iostream>
#include <algorithm>

int main() {
    // 1. 构造函数
    std::deque<int> dq1;                      // 空deque
    std::deque<int> dq2(5);                   // 5个默认值
    std::deque<int> dq3(5, 42);              // 5个42
    std::deque<int> dq4{1, 2, 3, 4, 5};      // 初始化列表
    
    // 2. 双端操作
    dq1.push_back(10);
    dq1.push_back(20);
    dq1.push_front(5);
    dq1.push_front(1);
    
    std::cout << "After push operations: ";
    for (const auto& elem : dq1) {
        std::cout << elem << " ";  // 输出: 1 5 10 20
    }
    std::cout << std::endl;
    
    // 3. 访问元素
    std::cout << "dq1[0] = " << dq1[0] << std::endl;
    std::cout << "dq1.front() = " << dq1.front() << std::endl;
    std::cout << "dq1.back() = " << dq1.back() << std::endl;
    
    // 4. 删除操作
    dq1.pop_front();
    dq1.pop_back();
    std::cout << "After pop operations: ";
    for (const auto& elem : dq1) {
        std::cout << elem << " ";  // 输出: 5 10
    }
    std::cout << std::endl;
    
    // 5. 中间插入
    auto it = dq4.begin() + 2;
    dq4.insert(it, 99);
    std::cout << "After insert: ";
    for (const auto& elem : dq4) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 6. 范围操作
    std::deque<int> dq5{3, 1, 4, 1, 5, 9, 2, 6};
    std::sort(dq5.begin(), dq5.end());
    std::cout << "After sort: ";
    for (const auto& elem : dq5) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
```

## 优缺点分析

### 优点

1. **双端高效**：头尾插入删除都是O(1)
2. **随机访问**：支持O(1)随机访问
3. **内存效率**：比vector更节省内存（不需要预留额外空间）
4. **迭代器稳定性**：头尾操作不会使中间元素的迭代器失效

### 缺点

1. **复杂的内存布局**：不是连续存储，缓存性能不如vector
2. **迭代器开销**：迭代器结构复杂，操作开销较大
3. **中间操作昂贵**：中间插入删除仍然是O(n)

## 适用场景

- 需要在两端频繁插入删除
- 需要随机访问但不要求内存连续
- 实现队列或双端队列数据结构
- 作为其他容器适配器的底层容器

## 与vector比较

| 特性 | vector | deque |
|------|--------|-------|
| 内存布局 | 连续 | 分段连续 |
| 随机访问 | O(1) | O(1) |
| 头部插入 | O(n) | O(1) |
| 尾部插入 | O(1)摊销 | O(1) |
| 迭代器失效 | 重分配时全部失效 | 头尾操作时中间不失效 |
| 缓存性能 | 优秀 | 一般 |
| 内存开销 | 可能有预留空间 | 按需分配 | 