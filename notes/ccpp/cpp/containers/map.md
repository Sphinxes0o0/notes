# std::map 详解

## 概述

`std::map` 是一个有序的关联容器，它包含键值对，其中每个键都是唯一的。元素按照键的比较函数进行排序。

## 特性

- **底层数据结构**：红黑树（自平衡二叉搜索树）
- **时间复杂度**：
  - 插入、删除、查找：O(log n)
- **有序性**：有序（按键排序）
- **重复性**：键不可重复，值可重复
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
| operator[]                   | element access| 访问或插入指定键的元素                                                            |
| at                          | element access| 访问指定键的元素（检查存在性）                                                     |
| insert                      | modifiers     | 插入元素或提示插入                                                                |
| emplace                     | modifiers     | 原地构造插入元素                                                                  |
| erase                       | modifiers     | 移除指定元素                                                                      |
| swap                        | modifiers     | 与另一map交换内容                                                                 |
| clear                       | modifiers     | 清除所有元素                                                                      |
| find                        | lookup        | 查找指定键的元素                                                                  |
| count                       | lookup        | 返回匹配特定键的元素数量                                                          |
| lower_bound                 | lookup        | 返回指向首个不小于给定键的元素的迭代器                                              |
| upper_bound                 | lookup        | 返回指向首个大于给定键的元素的迭代器                                                |
| equal_range                 | lookup        | 返回匹配特定键的元素范围                                                          |

## 使用示例

```cpp
#include <map>
#include <iostream>
#include <string>

int main() {
    // 1. 构造函数
    std::map<std::string, int> m1;                          // 空map
    std::map<std::string, int> m2{{"apple", 5}, {"banana", 3}, {"orange", 7}};  // 初始化列表
    
    // 2. 插入元素的多种方式
    m1["apple"] = 10;           // operator[]
    m1.insert({"banana", 5});   // insert with pair
    m1.insert(std::make_pair("orange", 8));  // insert with make_pair
    m1.emplace("grape", 12);    // emplace
    
    std::cout << "m1 contents:" << std::endl;
    for (const auto& pair : m1) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    // 3. 查找和访问
    auto it = m1.find("banana");
    if (it != m1.end()) {
        std::cout << "Found banana: " << it->second << std::endl;
    }
    
    // 使用at进行安全访问
    try {
        int apple_count = m1.at("apple");
        std::cout << "Apple count: " << apple_count << std::endl;
        
        int cherry_count = m1.at("cherry");  // 抛出异常
    } catch (const std::out_of_range& e) {
        std::cout << "Cherry not found!" << std::endl;
    }
    
    // 4. count检查存在性
    if (m1.count("apple") > 0) {
        std::cout << "Apple exists in map" << std::endl;
    }
    
    // 5. 范围查找
    std::map<int, std::string> m3{{1, "one"}, {3, "three"}, {5, "five"}, {7, "seven"}, {9, "nine"}};
    
    auto lower = m3.lower_bound(3);
    auto upper = m3.upper_bound(7);
    
    std::cout << "Elements from 3 to 7:" << std::endl;
    for (auto it = lower; it != upper; ++it) {
        std::cout << it->first << ": " << it->second << std::endl;
    }
    
    // 6. 删除操作
    m1.erase("banana");                    // 按键删除
    auto iter = m1.find("orange");
    if (iter != m1.end()) {
        m1.erase(iter);                    // 按迭代器删除
    }
    
    std::cout << "After erasing:" << std::endl;
    for (const auto& pair : m1) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    // 7. 自定义比较函数
    std::map<std::string, int, std::greater<std::string>> m4{
        {"apple", 5}, {"banana", 3}, {"orange", 7}
    };
    
    std::cout << "Reverse order map:" << std::endl;
    for (const auto& pair : m4) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    // 8. 使用结构体作为键
    struct Person {
        std::string name;
        int age;
        
        bool operator<(const Person& other) const {
            if (name != other.name) return name < other.name;
            return age < other.age;
        }
    };
    
    std::map<Person, int> person_map;
    person_map[{"Alice", 25}] = 100;
    person_map[{"Bob", 30}] = 200;
    person_map[{"Alice", 30}] = 150;
    
    std::cout << "Person map:" << std::endl;
    for (const auto& pair : person_map) {
        std::cout << pair.first.name << "(" << pair.first.age << "): " 
                  << pair.second << std::endl;
    }
    
    return 0;
}
```

## 红黑树特性

map内部使用红黑树实现，具有以下特性：

1. **自平衡**：自动保持树的平衡，避免退化为链表
2. **有序性**：中序遍历得到有序序列
3. **高度保证**：树高度不超过2*log(n+1)

```
红黑树示例（简化）:
        [5:black]
       /         \
   [3:red]     [7:black]
   /    \       /      \
[1:b] [4:b] [6:r]   [9:r]
```

## operator[] vs at() vs find()

```cpp
std::map<std::string, int> m{{"existing", 42}};

// operator[] - 如果键不存在会创建
int val1 = m["existing"];     // 返回42
int val2 = m["new_key"];      // 创建新元素，值为0

// at() - 如果键不存在会抛出异常
int val3 = m.at("existing");  // 返回42
// int val4 = m.at("missing"); // 抛出 std::out_of_range

// find() - 返回迭代器，最安全的查找方式
auto it = m.find("existing");
if (it != m.end()) {
    int val5 = it->second;    // 安全访问
}
```

## 性能分析

### 时间复杂度

| 操作 | 平均时间复杂度 | 最坏时间复杂度 |
|------|----------------|----------------|
| 插入 | O(log n) | O(log n) |
| 删除 | O(log n) | O(log n) |
| 查找 | O(log n) | O(log n) |
| 遍历 | O(n) | O(n) |

### 空间复杂度

- **存储开销**：每个节点需要额外存储颜色信息和指针
- **内存布局**：节点在内存中不连续

## 优缺点分析

### 优点

1. **自动排序**：元素按键自动排序
2. **唯一性保证**：键的唯一性由容器保证
3. **稳定性能**：所有操作都是O(log n)
4. **范围查询**：支持高效的范围查询操作

### 缺点

1. **内存开销**：相比unordered_map有额外开销
2. **插入性能**：插入比hash表慢
3. **缓存不友好**：树结构对缓存不友好

## 适用场景

- 需要保持键的有序性
- 需要进行范围查询
- 需要稳定的性能保证
- 键的比较操作定义良好
- 不需要极致的查找性能

## 与其他容器比较

| 特性 | map | unordered_map | vector |
|------|-----|---------------|--------|
| 有序性 | 有序 | 无序 | 保持插入顺序 |
| 查找复杂度 | O(log n) | O(1)平均 | O(n) |
| 插入复杂度 | O(log n) | O(1)平均 | O(1)尾部 |
| 内存开销 | 中等 | 高 | 低 |
| 范围查询 | 支持 | 不支持 | 不适用 | 