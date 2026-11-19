---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Auto Type Deduction (auto类型推导)

## 定义

C++11引入的`auto`和`decltype`实现了自动类型推导。`auto`根据初始化表达式推断类型（类似模板推导），`decltype`推导表达式的类型而不执行表达式，`decltype(auto)`保留表达式的引用语义。

## 关键要点

- **auto**：根据初始化值推断类型，忽略顶层const和引用
- **decltype(expr)**：保留表达式的所有类型属性（const、引用等）
- **decltype(auto)**：C++14引入，完美保留decltype的推导规则
- **trailing return type**：`auto f() -> decltype(x+y)`
- **泛型lambda**：C++14起参数支持auto

## 代码示例

```cpp
// auto基本用法
auto i = 5;           // int
auto arr = new auto(10); // int*

// decltype用于模板
template<typename T, typename U>
auto add2(T x, U y) -> decltype(x+y) {
    return x + y;
}

// decltype(auto)保留引用语义
std::string lookup1();    // 返回值
std::string& lookup2();   // 返回引用

decltype(auto) look_up_a_string_2() {
    return lookup2(); // 推导出string&，保留引用
}

// C++14泛型lambda
auto add = [](auto x, auto y) { return x + y; };
```

## 相关概念
- [[entities/cpp/constexpr]] - constexpr与类型推导结合
- [[entities/cpp/move-semantics]] - decltype处理移动语义
- [[entities/cpp/lambda-expressions]] - Lambda中的auto参数

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 2.3: auto与decltype
