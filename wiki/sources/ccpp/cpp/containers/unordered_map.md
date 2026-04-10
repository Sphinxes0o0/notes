# std::unordered_map 详解

## 概述

`std::unordered_map` 是基于哈希表实现的关联容器，存储键值对，其中每个键都是唯一的。它提供平均 O(1) 时间复杂度的插入、删除和查找操作。

## 特性

- **底层数据结构**：哈希表（通常使用开放定址法或链式哈希）
- **时间复杂度**：
  - 插入、删除、查找：O(1) 平均，O(n) 最坏
- **有序性**：无序（元素顺序不确定）
- **重复性**：键不可重复，值可重复
- **随机访问**：不支持（不是序列容器）
- **大小**：运行时可变

## 主要函数

|             方法             |     分类       |                                      含义                                       |
|:----------------------------:|:-------------:|:------------------------------------------------------------------------------:|
| begin/end                    | iterators     | 返回指向首/尾后元素的前向迭代器                                                    |
| cbegin/cend                  | iterators     | 返回常量迭代器                                                                    |
| size                         | capacity      | 返回容器中元素的数量                                                              |
| max_size                     | capacity      | 返回容器可容纳的最大元素数                                                        |
| empty                        | capacity      | 检查容器是否为空                                                                  |
| operator[]                   | element access| 访问或插入指定键的元素                                                            |
| at                          | element access| 访问指定键的元素（检查存在性）                                                     |
| insert                      | modifiers     | 插入元素                                                                          |
| emplace                     | modifiers     | 原地构造插入元素                                                                  |
| erase                       | modifiers     | 移除指定元素                                                                      |
| swap                        | modifiers     | 与另一unordered_map交换内容                                                       |
| clear                       | modifiers     | 清除所有元素                                                                      |
| find                        | lookup        | 查找指定键的元素                                                                  |
| count                       | lookup        | 返回匹配特定键的元素数量                                                          |
| equal_range                 | lookup        | 返回匹配特定键的元素范围                                                          |
| bucket_count                | hash policy   | 返回桶的数量                                                                      |
| max_bucket_count            | hash policy   | 返回桶的最大数量                                                                  |
| bucket_size                 | hash policy   | 返回指定桶中元素的数量                                                            |
| bucket                      | hash policy   | 返回指定键所在的桶                                                                |
| load_factor                 | hash policy   | 返回平均负载因子                                                                  |
| max_load_factor             | hash policy   | 返回或设置最大负载因子                                                            |
| rehash                      | hash policy   | 设置桶的数量                                                                      |
| reserve                     | hash policy   | 预留存储空间                                                                      |

## 使用示例

```cpp
#include <unordered_map>
#include <iostream>
#include <string>
#include <vector>

int main() {
    // 1. 基本操作
    std::unordered_map<std::string, int> umap;
    
    // 插入元素的多种方式
    umap["apple"] = 5;
    umap.insert({"banana", 3});
    umap.insert(std::make_pair("orange", 7));
    umap.emplace("grape", 12);
    
    std::cout << "Basic operations:" << std::endl;
    for (const auto& pair : umap) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    // 2. 查找操作
    auto it = umap.find("banana");
    if (it != umap.end()) {
        std::cout << "Found banana: " << it->second << std::endl;
    }
    
    // 检查键是否存在
    if (umap.count("apple") > 0) {
        std::cout << "Apple exists" << std::endl;
    }
    
    // 3. 安全访问 vs 直接访问
    try {
        int apple_count = umap.at("apple");        // 安全访问
        std::cout << "Apple count: " << apple_count << std::endl;
        
        int cherry_count = umap.at("cherry");      // 抛出异常
    } catch (const std::out_of_range& e) {
        std::cout << "Cherry not found!" << std::endl;
    }
    
    // operator[] 会插入不存在的键
    int kiwi_count = umap["kiwi"];  // 插入kiwi，值为0
    std::cout << "Kiwi count after []: " << kiwi_count << std::endl;
    
    // 4. 删除操作
    umap.erase("banana");           // 按键删除
    auto iter = umap.find("orange");
    if (iter != umap.end()) {
        umap.erase(iter);           // 按迭代器删除
    }
    
    std::cout << "After erasing:" << std::endl;
    for (const auto& pair : umap) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    // 5. 哈希表信息
    std::cout << "\nHash table info:" << std::endl;
    std::cout << "Size: " << umap.size() << std::endl;
    std::cout << "Bucket count: " << umap.bucket_count() << std::endl;
    std::cout << "Load factor: " << umap.load_factor() << std::endl;
    std::cout << "Max load factor: " << umap.max_load_factor() << std::endl;
    
    // 查看每个元素在哪个桶中
    for (const auto& pair : umap) {
        std::cout << pair.first << " is in bucket " << umap.bucket(pair.first) << std::endl;
    }
    
    // 6. 性能优化：预留空间
    std::unordered_map<int, std::string> large_map;
    large_map.reserve(1000);  // 预留空间，减少rehash
    
    for (int i = 0; i < 100; ++i) {
        large_map[i] = "value_" + std::to_string(i);
    }
    
    // 7. 自定义哈希函数
    struct Person {
        std::string name;
        int age;
        
        bool operator==(const Person& other) const {
            return name == other.name && age == other.age;
        }
    };
    
    // 自定义哈希函数
    struct PersonHash {
        std::size_t operator()(const Person& p) const {
            std::hash<std::string> hasher;
            return hasher(p.name) ^ (std::hash<int>{}(p.age) << 1);
        }
    };
    
    std::unordered_map<Person, int, PersonHash> person_map;
    person_map[{"Alice", 25}] = 100;
    person_map[{"Bob", 30}] = 200;
    person_map[{"Alice", 30}] = 150;  // 不同的Alice
    
    std::cout << "\nPerson map:" << std::endl;
    for (const auto& pair : person_map) {
        std::cout << pair.first.name << "(" << pair.first.age << "): " 
                  << pair.second << std::endl;
    }
    
    // 8. 单词计数示例
    std::vector<std::string> words = {"apple", "banana", "apple", "orange", "banana", "apple"};
    std::unordered_map<std::string, int> word_count;
    
    for (const std::string& word : words) {
        word_count[word]++;  // 自动初始化为0然后递增
    }
    
    std::cout << "\nWord count:" << std::endl;
    for (const auto& pair : word_count) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    return 0;
}
```

## 哈希表实现原理

### 基本结构

```cpp
// 简化的哈希表结构
template<typename Key, typename Value>
class unordered_map {
private:
    struct Node {
        std::pair<Key, Value> data;
        Node* next;  // 链式解决冲突
    };
    
    std::vector<Node*> buckets;  // 桶数组
    std::size_t size_;
    std::hash<Key> hasher;
    
public:
    // ... 各种操作
};
```

### 哈希冲突解决

常见的冲突解决方法：

1. **链式哈希（Chaining）**：
   - 每个桶是一个链表
   - 冲突元素添加到链表中
   
2. **开放定址法（Open Addressing）**：
   - 线性探测
   - 二次探测
   - 双重哈希

## 性能分析

### 时间复杂度

| 操作 | 平均时间复杂度 | 最坏时间复杂度 | 说明 |
|------|----------------|----------------|------|
| 插入 | O(1) | O(n) | 最坏情况下所有元素在同一桶 |
| 删除 | O(1) | O(n) | 同上 |
| 查找 | O(1) | O(n) | 同上 |
| 遍历 | O(n) | O(n) | 需要访问所有元素 |

### 负载因子

- **负载因子** = 元素数量 / 桶数量
- **默认最大负载因子**：通常为 1.0
- **自动rehash**：当负载因子超过最大值时触发

## 优缺点分析

### 优点

1. **快速查找**：平均 O(1) 的查找性能
2. **灵活的键类型**：支持自定义哈希函数
3. **动态大小**：可以动态增长
4. **内存高效**：相比map没有额外的树结构开销

### 缺点

1. **无序性**：元素顺序不确定
2. **哈希函数依赖**：性能严重依赖哈希函数质量
3. **最坏情况性能差**：最坏情况下退化为O(n)
4. **内存局部性差**：元素可能分布在不同位置

## 与 map 的比较

| 特性 | unordered_map | map |
|------|---------------|-----|
| 底层结构 | 哈希表 | 红黑树 |
| 平均查找时间 | O(1) | O(log n) |
| 最坏查找时间 | O(n) | O(log n) |
| 有序性 | 无序 | 有序 |
| 内存开销 | 中等 | 中等 |
| 迭代器失效 | rehash时失效 | 删除时局部失效 |
| 范围查询 | 不支持 | 支持 |

## 性能优化建议

1. **预留空间**：使用 `reserve()` 预留足够空间
2. **选择好的哈希函数**：避免哈希冲突
3. **合理设置负载因子**：平衡时间和空间
4. **避免频繁rehash**：合理估计容器大小

```cpp
// 性能优化示例
std::unordered_map<std::string, int> optimized_map;

// 1. 预留空间
optimized_map.reserve(10000);

// 2. 设置合理的最大负载因子
optimized_map.max_load_factor(0.75);

// 3. 批量插入时使用emplace
for (int i = 0; i < 1000; ++i) {
    optimized_map.emplace("key_" + std::to_string(i), i);
}
```

## 适用场景

- 需要快速查找和插入
- 不需要保持元素顺序
- 键的哈希函数易于实现且分布均匀
- 对最坏情况性能要求不严格
- 实现缓存、索引等数据结构 