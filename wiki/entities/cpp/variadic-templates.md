---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Variadic Templates (模板变参)

## 定义

C++11引入的模板变参允许模板接受任意数量的模板参数。通过`sizeof...(args)`获取参数个数，通过参数包展开实现递归或迭代处理。

## 关键要点

- **模板参数包**：`template<typename... Args>`
- **函数参数包**：`void foo(Args... args)`
- **展开方式**：模式展开`f(args...)`、展开到初始化列表`{f(args)...}`
- **sizeof...**：获取参数包中参数数量
- **C++17折叠表达式**：`std::cout << (args + ...);`

## 代码示例

```cpp
// 基本变参模板
template<typename... Args> void printf(const std::string &str, Args... args);

// 递归展开
template<typename T0>
void printf1(T0 value) {
    std::cout << value << std::endl;
}
template<typename T, typename... Ts>
void printf1(T value, Ts... args) {
    std::cout << value << std::endl;
    printf1(args...);
}

// C++17折叠表达式
template<typename... T>
auto sum(T... t) {
    return (t + ...); // 折叠为 t1 + t2 + t3 + ...
}

// 变参lambda捕获（C++14）
auto f = [...xs = std::move(x), ...ys = std::move(y)]() {
    // 使用xs和ys
};
```

## 相关概念
- [[entities/cpp/auto-type-deduction]] - auto推导变参模板
- [[entities/cpp/constexpr]] - constexpr函数使用变参模板
- [[entities/cpp/lambda-expressions]] - Lambda的变参捕获

## 来源详情
- [[sources/pdf-modern-cpp-tutorial]] - Chapter 2.5: 变参模板
