# std::array 详解

## 概述

`std::array` 是 C++11 引入的固定大小数组容器，它是对传统 C 数组的封装，提供了 STL 容器的标准接口。

## 特性

- **底层数据结构**：数组
- **时间复杂度**：随机读改 O(1)
- **有序性**：无序（保持插入顺序）
- **重复性**：可重复
- **随机访问**：支持
- **大小**：编译时确定，运行时不可改变

## 函数一览

|             方法             |     分类   |                                      含义                                       |
|:----------------------------:|:---------:|:------------------------------------------------------------------------------:|
| begin                        | iterators |  返回指向数组容器中第一个元素的迭代器                                               |
| end                          | iterators |  返回指向数组容器中最后一个元素之后的理论元素的迭代器                                 |
| rbegin                       | iterators |  返回指向数组容器中最后一个元素的反向迭代器                                          |
| rend                         | iterators |  返回一个反向迭代器，指向数组中第一个元素之前的理论元素                               |
| cbegin                       | iterators |  返回指向数组容器中第一个元素的常量迭代器(const_iterator)                          |
| cend                         | iterators |  返回指向数组容器中最后一个元素之后的理论元素的常量迭代器(const_iterator)           |
| crbegin                      | iterators |  返回指向数组容器中最后一个元素的常量反向迭代器(const_reverse_iterator)            |
| crend                        | iterators |  返回指向数组中第一个元素之前的理论元素的常量反向迭代器(const_reverse_iterator)     |
| size                         | capacity  |  返回数组容器中元素的数量                                                          |
| max_size                     | capacity  |  返回数组容器可容纳的最大元素数                                                    |
| empty                        | capacity  |  返回一个布尔值，指示数组容器是否为空                                               |
| operator[]                   | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| at                           | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| front                        | element access |  返回对容器中第一个元素的引用                                                 |
| back                         | element access |  返回对容器中最后一个元素的引用                                               |
| data                         | element access |  返回指向容器中第一个元素的指针                                               |
| fill                         | modifiers |  用 val(参数)填充数组所有元素                                                |
| swap                         | modifiers |  通过 x (参数)的内容交换数组的内容                                            |

## 源码实现

```cpp
namespace std
{
    template<class T, size_t N>
    struct array
    {
        // types
        using value_type             = T;
        using pointer                = T*;
        using const_pointer          = const T*;
        using reference              = T&;
        using const_reference        = const T&;
        using size_type              = size_t;
        using difference_type        = ptrdiff_t;
        using iterator               = /* implementation-defined */;
        using const_iterator         = /* implementation-defined */;
        using reverse_iterator       = std::reverse_iterator<iterator>;
        using const_reverse_iterator = std::reverse_iterator<const_iterator>;
 
        // no explicit construct/copy/destroy for aggregate type
 
        constexpr void fill(const T& u);
        constexpr void swap(array&) noexcept(is_nothrow_swappable_v<T>);
 
        // iterators
        constexpr iterator               begin() noexcept;
        constexpr const_iterator         begin() const noexcept;
        constexpr iterator               end() noexcept;
        constexpr const_iterator         end() const noexcept;
 
        constexpr reverse_iterator       rbegin() noexcept;
        constexpr const_reverse_iterator rbegin() const noexcept;
        constexpr reverse_iterator       rend() noexcept;
        constexpr const_reverse_iterator rend() const noexcept;
 
        constexpr const_iterator         cbegin() const noexcept;
        constexpr const_iterator         cend() const noexcept;
        constexpr const_reverse_iterator crbegin() const noexcept;
        constexpr const_reverse_iterator crend() const noexcept;
 
        // capacity
        [[nodiscard]] constexpr bool empty() const noexcept;
        constexpr size_type size() const noexcept;
        constexpr size_type max_size() const noexcept;
 
        // element access
        constexpr reference       operator[](size_type n);
        constexpr const_reference operator[](size_type n) const;
        constexpr reference       at(size_type n);
        constexpr const_reference at(size_type n) const;
        constexpr reference       front();
        constexpr const_reference front() const;
        constexpr reference       back();
        constexpr const_reference back() const;
 
        constexpr T*       data() noexcept;
        constexpr const T* data() const noexcept;
    };
 
    template<class T, class... U>
        array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

## 使用示例

```cpp
#include <array>
#include <iostream>
#include <algorithm>

int main() {
    // 1. 基本声明和初始化
    std::array<int, 5> arr1;           // 声明但不初始化
    std::array<int, 5> arr2{1, 2, 3, 4, 5};  // 列表初始化
    std::array<int, 5> arr3 = {1, 2, 3};     // 部分初始化，其余为0
    
    // 2. 访问元素
    std::cout << "arr2[0] = " << arr2[0] << std::endl;  // 不检查边界
    std::cout << "arr2.at(1) = " << arr2.at(1) << std::endl;  // 检查边界
    std::cout << "Front: " << arr2.front() << std::endl;
    std::cout << "Back: " << arr2.back() << std::endl;
    
    // 3. 容量相关
    std::cout << "Size: " << arr2.size() << std::endl;
    std::cout << "Max size: " << arr2.max_size() << std::endl;
    std::cout << "Empty: " << arr2.empty() << std::endl;
    
    // 4. 迭代器
    std::cout << "Elements: ";
    for (auto it = arr2.begin(); it != arr2.end(); ++it) {
        std::cout << *it << " ";
    }
    std::cout << std::endl;
    
    // 5. 范围for循环
    std::cout << "Range-based for: ";
    for (const auto& elem : arr2) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 6. fill操作
    arr1.fill(42);
    std::cout << "After fill(42): ";
    for (const auto& elem : arr1) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 7. swap操作
    arr1.swap(arr2);
    std::cout << "After swap arr1: ";
    for (const auto& elem : arr1) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    // 8. 与STL算法配合使用
    std::sort(arr1.begin(), arr1.end());
    std::cout << "After sort: ";
    for (const auto& elem : arr1) {
        std::cout << elem << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
```

## 优缺点分析

### 优点

1. **类型安全**：相比C数组，提供了更好的类型安全性
2. **标准接口**：提供STL容器的标准接口，可以与STL算法配合使用
3. **零开销**：没有额外的内存开销，性能与C数组相当
4. **边界检查**：`at()`方法提供边界检查
5. **支持赋值**：支持整个数组的赋值操作

### 缺点

1. **固定大小**：大小在编译时确定，运行时不可更改
2. **栈分配**：通常在栈上分配，大数组可能导致栈溢出
3. **模板参数**：需要在模板参数中指定大小，不够灵活

## 适用场景

- 需要固定大小的数组
- 需要与STL算法配合使用的数组
- 替代C风格数组以获得更好的类型安全性
- 数据大小在编译时已知且不需要动态改变

## 注意事项

1. `operator[]` 不检查边界，`at()` 检查边界并抛出异常
2. 未初始化的 `std::array` 包含不确定值
3. 空 `std::array`（N=0）是合法的，但不能解引用
4. 可以使用聚合初始化，但需要注意元素数量 