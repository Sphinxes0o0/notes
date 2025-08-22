# std::list 详解

## 概述

`std::list` 是一个双向链表容器，支持在任意位置进行高效的插入和删除操作。它不支持随机访问，但提供了双向迭代能力。

## 特性

- **底层数据结构**：双向链表
- **时间复杂度**：
  - 插入、删除：O(1)（已知迭代器位置）
  - 查找：O(n)
  - 不支持随机访问
- **有序性**：无序（保持插入顺序）
- **重复性**：可重复
- **随机访问**：不支持
- **大小**：运行时可变

## 主要函数

|             方法             |     分类       |                                      含义                                       |
|:----------------------------:|:-------------:|:------------------------------------------------------------------------------:|
| begin/end                    | iterators     | 返回指向首/尾后元素的双向迭代器                                                    |
| rbegin/rend                  | iterators     | 返回反向迭代器                                                                    |
| cbegin/cend                  | iterators     | 返回常量迭代器                                                                    |
| size                         | capacity      | 返回容器中元素的数量                                                              |
| max_size                     | capacity      | 返回容器可容纳的最大元素数                                                        |
| empty                        | capacity      | 检查容器是否为空                                                                  |
| front                       | element access| 返回首元素的引用                                                                  |
| back                        | element access| 返回末元素的引用                                                                  |
| assign                      | modifiers     | 分配给容器新的内容                                                                |
| push_front                  | modifiers     | 将元素添加到开头                                                                  |
| pop_front                   | modifiers     | 移除首元素                                                                        |
| push_back                   | modifiers     | 将元素添加到末尾                                                                  |
| pop_back                    | modifiers     | 移除末元素                                                                        |
| insert                      | modifiers     | 在指定位置插入元素                                                                |
| erase                       | modifiers     | 移除指定位置的元素                                                                |
| swap                        | modifiers     | 与另一list交换内容                                                                |
| clear                       | modifiers     | 清除所有元素                                                                      |
| splice                      | operations    | 从另一个list转移元素                                                              |
| remove                      | operations    | 移除等于指定值的元素                                                              |
| remove_if                   | operations    | 移除满足条件的元素                                                                |
| unique                      | operations    | 移除连续的重复元素                                                                |
| merge                       | operations    | 合并两个已排序的list                                                              |
| sort                        | operations    | 对list进行排序                                                                    |
| reverse                     | operations    | 反转list中元素的顺序                                                              |

## 使用示例

```cpp
#include <list>
#include <iostream>
#include <algorithm>

int main() {
    // 1. 构造函数
    std::list<int> lst1;                      // 空list
    std::list<int> lst2(5);                   // 5个默认值
    std::list<int> lst3(5, 42);              // 5个42
    std::list<int> lst4{1, 2, 3, 4, 5};      // 初始化列表
    
    // 2. 添加元素
    lst1.push_back(10);
    lst1.push_front(5);
    lst1.push_back(20);
    lst1.push_front(1);
    
    std::cout << "lst1: ";
    for (const auto& elem : lst1) {
        std::cout << elem << " ";  // 输出: 1 5 10 20
    }
    std::cout << std::endl;
    
    // 3. 插入操作
    auto it = lst4.begin();
    std::advance(it, 2);  // 移动到第3个位置
    lst4.insert(it, 99);
    
    std::cout << "After insert: ";
    for (const auto& elem : lst4) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 4. list特有操作
    std::list<int> lst5{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};
    
    // 排序
    lst5.sort();
    std::cout << "After sort: ";
    for (const auto& elem : lst5) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 移除重复元素（需要先排序）
    lst5.unique();
    std::cout << "After unique: ";
    for (const auto& elem : lst5) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 移除特定值
    lst5.remove(5);
    std::cout << "After remove(5): ";
    for (const auto& elem : lst5) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 反转
    lst5.reverse();
    std::cout << "After reverse: ";
    for (const auto& elem : lst5) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 5. splice操作（拼接）
    std::list<int> lst6{100, 200, 300};
    std::list<int> lst7{400, 500};
    
    // 将lst7的所有元素移动到lst6的末尾
    lst6.splice(lst6.end(), lst7);
    std::cout << "After splice: ";
    for (const auto& elem : lst6) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    std::cout << "lst7 size after splice: " << lst7.size() << std::endl;
    
    // 6. 条件移除
    std::list<int> lst8{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    lst8.remove_if([](int n) { return n % 2 == 0; });  // 移除偶数
    std::cout << "After remove_if (even numbers): ";
    for (const auto& elem : lst8) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
```

## 链表结构

```cpp
// 简化的双向链表节点结构
template<typename T>
struct ListNode {
    T data;
    ListNode* prev;
    ListNode* next;
    
    ListNode(const T& value) : data(value), prev(nullptr), next(nullptr) {}
};

// list内部大致结构
template<typename T>
class list {
private:
    ListNode<T>* head;  // 哨兵节点
    size_t size_;
    
public:
    // ... 各种操作
};
```

## 迭代器特性

list的迭代器是双向迭代器（Bidirectional Iterator），支持：
- `++it`, `it++` （前进）
- `--it`, `it--` （后退）
- `*it` （解引用）
- `it1 == it2`, `it1 != it2` （比较）

但不支持：
- `it + n` （随机访问）
- `it[n]` （下标访问）
- `it1 < it2` （大小比较）

## 优缺点分析

### 优点

1. **高效插入删除**：在任意位置插入删除都是O(1)
2. **迭代器稳定性**：插入删除操作不会使其他迭代器失效
3. **内存高效**：按需分配，没有额外的内存浪费
4. **特有操作**：提供了splice、merge、sort等链表特有的高效操作

### 缺点

1. **无随机访问**：不能像数组一样直接访问第n个元素
2. **缓存不友好**：节点在内存中不连续，缓存性能差
3. **额外内存开销**：每个节点需要存储前后指针
4. **查找性能差**：查找元素需要O(n)时间

## 适用场景

- 需要频繁在中间位置插入删除元素
- 不需要随机访问
- 需要保持插入顺序
- 需要高效的拼接操作
- 元素大小较大（移动成本高）

## 性能建议

1. **避免频繁size()调用**：某些实现中size()是O(n)操作
2. **使用splice代替拷贝**：移动元素时优先使用splice
3. **预先排序**：如果需要unique操作，先进行sort
4. **合理使用迭代器**：充分利用迭代器的稳定性

```cpp
// 高效的元素移动示例
std::list<int> source{1, 2, 3, 4, 5};
std::list<int> dest;

// 高效：使用splice移动元素
dest.splice(dest.end(), source, source.begin());

// 低效：拷贝后删除
// dest.push_back(*source.begin());
// source.erase(source.begin());
``` 