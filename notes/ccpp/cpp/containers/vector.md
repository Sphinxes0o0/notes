# std::vector 详解

## 概述

`std::vector` 是 C++ STL 中最常用的序列容器，它是一个动态数组，可以在运行时改变大小。vector 在内存中连续存储元素，支持高效的随机访问。

## 特性

- **底层数据结构**：动态数组
- **时间复杂度**：
  - 随机读改：O(1)
  - 尾部插入、删除：O(1) 摊销
  - 头部或中间插入、删除：O(n)
- **有序性**：无序（保持插入顺序）
- **重复性**：可重复
- **随机访问**：支持
- **大小**：运行时可变

## 函数一览

|             方法             |     分类       |                                      含义                                       |
|:----------------------------:|:-------------:|:------------------------------------------------------------------------------:|
| begin/end                    | iterators     | 返回指向首/尾后元素的迭代器                                                        |
| rbegin/rend                  | iterators     | 返回反向迭代器                                                                    |
| cbegin/cend                  | iterators     | 返回常量迭代器                                                                    |
| crbegin/crend                | iterators     | 返回常量反向迭代器                                                                |
| size                         | capacity      | 返回容器中元素的数量                                                              |
| max_size                     | capacity      | 返回容器可容纳的最大元素数                                                        |
| capacity                     | capacity      | 返回当前分配的存储容量                                                            |
| empty                        | capacity      | 检查容器是否为空                                                                  |
| reserve                      | capacity      | 预留存储容量                                                                      |
| shrink_to_fit                | capacity      | 缩减容量以适应大小                                                                |
| operator[]                   | element access| 返回指定位置元素的引用（不检查边界）                                               |
| at                          | element access| 返回指定位置元素的引用（检查边界）                                                 |
| front                       | element access| 返回首元素的引用                                                                  |
| back                        | element access| 返回末元素的引用                                                                  |
| data                        | element access| 返回指向底层数组的指针                                                            |
| assign                      | modifiers     | 分配给容器新的内容                                                                |
| push_back                   | modifiers     | 将元素添加到末尾                                                                  |
| pop_back                    | modifiers     | 移除末元素                                                                        |
| insert                      | modifiers     | 在指定位置插入元素                                                                |
| erase                       | modifiers     | 移除指定位置的元素                                                                |
| swap                        | modifiers     | 与另一vector交换内容                                                              |
| clear                       | modifiers     | 清除所有元素                                                                      |
| emplace                     | modifiers     | 在指定位置构造元素                                                                |
| emplace_back                | modifiers     | 在末尾构造元素                                                                    |

## 源码实现

```cpp
namespace std {
    template<class T, class Alloc = allocator<T>>
    class vector {
    public:
        // types
        using value_type             = T;
        using allocator_type         = Alloc;
        using pointer                = typename allocator_traits<Alloc>::pointer;
        using const_pointer          = typename allocator_traits<Alloc>::const_pointer;
        using reference              = value_type&;
        using const_reference        = const value_type&;
        using size_type              = size_t;
        using difference_type        = ptrdiff_t;
        using iterator               = /* implementation-defined */;
        using const_iterator         = /* implementation-defined */;
        using reverse_iterator       = std::reverse_iterator<iterator>;
        using const_reverse_iterator = std::reverse_iterator<const_iterator>;

        // constructors
        vector() noexcept(noexcept(Alloc()));
        explicit vector(const Alloc& alloc) noexcept;
        explicit vector(size_type count, const T& value = T(), const Alloc& alloc = Alloc());
        template<class InputIt>
        vector(InputIt first, InputIt last, const Alloc& alloc = Alloc());
        vector(const vector& other);
        vector(vector&& other) noexcept;
        vector(std::initializer_list<T> init, const Alloc& alloc = Alloc());

        // destructor
        ~vector();

        // assignment
        vector& operator=(const vector& other);
        vector& operator=(vector&& other) noexcept;
        vector& operator=(std::initializer_list<T> ilist);

        void assign(size_type count, const T& value);
        template<class InputIt>
        void assign(InputIt first, InputIt last);
        void assign(std::initializer_list<T> ilist);

        allocator_type get_allocator() const noexcept;

        // element access
        reference at(size_type pos);
        const_reference at(size_type pos) const;
        reference operator[](size_type pos);
        const_reference operator[](size_type pos) const;
        reference front();
        const_reference front() const;
        reference back();
        const_reference back() const;
        T* data() noexcept;
        const T* data() const noexcept;

        // iterators
        iterator begin() noexcept;
        const_iterator begin() const noexcept;
        const_iterator cbegin() const noexcept;
        iterator end() noexcept;
        const_iterator end() const noexcept;
        const_iterator cend() const noexcept;
        reverse_iterator rbegin() noexcept;
        const_reverse_iterator rbegin() const noexcept;
        const_reverse_iterator crbegin() const noexcept;
        reverse_iterator rend() noexcept;
        const_reverse_iterator rend() const noexcept;
        const_reverse_iterator crend() const noexcept;

        // capacity
        [[nodiscard]] bool empty() const noexcept;
        size_type size() const noexcept;
        size_type max_size() const noexcept;
        void reserve(size_type new_cap);
        size_type capacity() const noexcept;
        void shrink_to_fit();

        // modifiers
        void clear() noexcept;
        iterator insert(const_iterator pos, const T& value);
        iterator insert(const_iterator pos, T&& value);
        iterator insert(const_iterator pos, size_type count, const T& value);
        template<class InputIt>
        iterator insert(const_iterator pos, InputIt first, InputIt last);
        iterator insert(const_iterator pos, std::initializer_list<T> ilist);
        template<class... Args>
        iterator emplace(const_iterator pos, Args&&... args);
        iterator erase(const_iterator pos);
        iterator erase(const_iterator first, const_iterator last);
        void push_back(const T& value);
        void push_back(T&& value);
        template<class... Args>
        reference emplace_back(Args&&... args);
        void pop_back();
        void resize(size_type count);
        void resize(size_type count, const value_type& value);
        void swap(vector& other) noexcept;
    };
}
```

## 使用示例

```cpp
#include <vector>
#include <iostream>
#include <algorithm>
#include <iterator>

int main() {
    // 1. 构造函数
    std::vector<int> v1;                      // 空vector
    std::vector<int> v2(5);                   // 5个默认值
    std::vector<int> v3(5, 42);              // 5个42
    std::vector<int> v4{1, 2, 3, 4, 5};      // 初始化列表
    std::vector<int> v5(v4.begin(), v4.end()); // 迭代器范围
    std::vector<int> v6(v4);                  // 拷贝构造

    // 2. 基本操作
    v1.push_back(10);
    v1.push_back(20);
    v1.push_back(30);
    
    std::cout << "v1 size: " << v1.size() << std::endl;
    std::cout << "v1 capacity: " << v1.capacity() << std::endl;
    
    // 3. 访问元素
    std::cout << "v1[0] = " << v1[0] << std::endl;
    std::cout << "v1.at(1) = " << v1.at(1) << std::endl;
    std::cout << "v1.front() = " << v1.front() << std::endl;
    std::cout << "v1.back() = " << v1.back() << std::endl;
    
    // 4. 迭代器使用
    std::cout << "v4 elements: ";
    for (auto it = v4.begin(); it != v4.end(); ++it) {
        std::cout << *it << " ";
    }
    std::cout << std::endl;
    
    // 5. 范围for循环
    std::cout << "v4 elements (range-for): ";
    for (const auto& elem : v4) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 6. 插入和删除
    v4.insert(v4.begin() + 2, 99);  // 在位置2插入99
    std::cout << "After insert: ";
    for (const auto& elem : v4) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    v4.erase(v4.begin() + 2);       // 删除位置2的元素
    std::cout << "After erase: ";
    for (const auto& elem : v4) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 7. 容量管理
    std::vector<int> v7;
    v7.reserve(100);  // 预留容量
    std::cout << "v7 capacity after reserve: " << v7.capacity() << std::endl;
    
    // 8. emplace操作（原地构造）
    std::vector<std::pair<int, std::string>> v8;
    v8.emplace_back(1, "one");      // 直接构造pair
    v8.push_back({2, "two"});       // 先构造临时对象再移动
    
    // 9. 与STL算法配合
    std::vector<int> v9{5, 2, 8, 1, 9, 3};
    std::sort(v9.begin(), v9.end());
    std::cout << "After sort: ";
    for (const auto& elem : v9) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 10. 查找
    auto it = std::find(v9.begin(), v9.end(), 5);
    if (it != v9.end()) {
        std::cout << "Found 5 at position: " << std::distance(v9.begin(), it) << std::endl;
    }
    
    return 0;
}
```

## 内存管理机制

### 动态扩容策略

vector 采用指数增长策略来管理内存：

1. **初始容量**：通常为0或1
2. **扩容时机**：当 `size() == capacity()` 时需要扩容
3. **扩容倍数**：通常是1.5倍或2倍
4. **重新分配**：分配新内存，移动所有元素，释放旧内存

```cpp
// 扩容示例
std::vector<int> v;
for (int i = 0; i < 10; ++i) {
    std::cout << "Before push: size=" << v.size() 
              << ", capacity=" << v.capacity() << std::endl;
    v.push_back(i);
    std::cout << "After push: size=" << v.size() 
              << ", capacity=" << v.capacity() << std::endl;
}
```

### 迭代器失效

以下操作会导致迭代器失效：

1. **重新分配内存**：`push_back`, `insert`, `resize` 等
2. **删除元素**：`erase`, `pop_back`, `clear` 等

```cpp
std::vector<int> v{1, 2, 3, 4, 5};
auto it = v.begin() + 2;  // 指向元素3
v.push_back(6);           // 可能导致重新分配
// it 现在可能失效，不应再使用
```

## 优缺点分析

### 优点

1. **随机访问**：O(1) 时间复杂度访问任意元素
2. **缓存友好**：连续内存布局，良好的空间局部性
3. **动态大小**：运行时可变大小
4. **标准接口**：兼容STL算法和其他容器
5. **高效尾部操作**：push_back 和 pop_back 是 O(1) 摊销时间

### 缺点

1. **头部操作昂贵**：头部插入删除是 O(n)
2. **内存重新分配**：可能导致性能波动
3. **内存浪费**：capacity 通常大于 size
4. **迭代器失效**：某些操作会使迭代器失效

## 适用场景

- 需要随机访问元素
- 主要在尾部进行插入删除操作
- 需要与C风格API交互（通过data()获取指针）
- 元素数量变化较大
- 需要缓存友好的数据结构

## 性能优化建议

1. **预留容量**：如果知道大概大小，使用 `reserve()` 预留容量
2. **避免频繁重分配**：批量操作优于逐个操作
3. **使用emplace**：优先使用 `emplace_back` 而非 `push_back`
4. **及时shrink**：不再需要大容量时使用 `shrink_to_fit()`

```cpp
// 优化示例
std::vector<std::string> v;
v.reserve(1000);  // 预留容量

// 使用emplace_back避免临时对象
v.emplace_back("Hello World");  // 直接构造
// 而不是 v.push_back(std::string("Hello World"));
``` 