---
type: entity
tags: [cpp, stl, functors]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL Functors

## 定义

函数对象（Functor）是实现了 `operator()` 的对象，使得对象可以像函数一样被调用。包括普通函数、lambda 表达式、类的实例、以及指向成员函数的指针。

## 关键要点

### 函数对象分类

| 类型 | 说明 | 示例 |
|------|------|------|
| 纯函数 | 无状态函数 | `int(*)(int, int)` |
| 函数对象 | 重载 operator() | `std::greater<int>` |
| Lambda | C++11 简化语法 | `[](int x){ return x > 0; }` |
| 成员函数指针 | 需 bind 到对象 | `&Type::member` |

### 预定义函数对象

```cpp
#include <functional>
std::negate<int>{}           // -x
std::plus<int>{}              // x + y
std::minus<int>{}             // x - y
std::multiplies<int>{}        // x * y
std::divides<int>{}           // x / y
std::modulus<int>{}           // x % y
std::equal_to<int>{}          // x == y
std::not_equal_to<int>{}     // x != y
std::greater<int>{}            // x > y
std::less<int>{}              // x < y
std::greater_equal<int>{}     // x >= y
std::less_equal<int>{}        // x <= y
std::logical_and<int>{}       // x && y
std::logical_or<int>{}        // x || y
std::logical_not<int>{}      // !x
```

### 函数适配器

```cpp
#include <functional>
std::bind(std::plus<int>(), std::placeholders::_1, 42);  // x + 42
std::not1(std::ptr_fun(pred_func));                      // !pred(x)
std::not2(std::ptr_fun(binary_pred));                   // !pred(x, y)
std::mem_fun(&Type::method);                            // 成员函数适配
```

### Lambda vs 函数对象

```cpp
// Lambda（编译器生成函数对象）
auto is_odd = [](int x) { return x % 2 == 1; };

// 等价的显式函数对象
struct IsOdd {
    bool operator()(int x) const { return x % 2 == 1; }
};
```

### 算法中的函数对象注意事项

```cpp
// 按值传递，需可拷贝
std::sort(v.begin(), v.end(), std::greater<int>{});

// 自定义函数对象应有 const operator()
// 若需保存状态，考虑 lambda 或设计为函数对象

// 用 ref() 包装避免拷贝
std::for_each(v.begin(), v.end(), std::ref(myFunctor));
```

## Effective STL 要点 (Items 33-40)

- Item 33: 用 lambda 代替 std::bind 或手写函数对象
- Item 34: 用函数对象而非函数作为算法参数
- Item 35: 优先使用成员函数而非独立函数
- Item 36: 用 std::bind 代替 lambda 当需要状态化仿函数
- Item 37: 用 lambdA 代替 std::bind 以外的 bind
- Item 38: 理解按值传递 vs 按引用传递仿函数
- Item 39: 用 void* 代替需要转换的算法参数
- Item 40: 用功能类似的非STL算法替代手写

## 相关概念
- [[entities/cpp/cpp-stl-algorithms]] — 算法常以函数对象作为策略参数
- [[entities/cpp/cpp-stl-iterators]] — 迭代器配合函数对象使用
- [[entities/cpp/lambda-expressions]] — C++11 Lambda 是函数对象的简化形式
- [[entities/cpp/cpp-stl-containers]] — 容器可存储函数对象
