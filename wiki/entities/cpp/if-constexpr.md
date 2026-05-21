---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# if constexpr (编译时分支)

## 定义

C++17引入的`if constexpr`允许在编译期根据常量表达式选择代码分支。与普通if不同，if constexpr会丢弃不满足条件的分支（不实例化），从而实现真正的编译期多态。

## 关键要点

- **编译期求值**：条件必须是编译期常量表达式
- **分支丢弃**：不满足条件的分支不会被实例化
- **std::is_integral**：判断类型是否为整型
- **替代SFINAE**：更清晰的编译期分支写法
- **配合变参模板**：实现类型列表的编译期处理

## 代码示例

```cpp
// if constexpr基本用法
template<typename T>
auto print_type_info(const T& t) {
    if constexpr (std::is_integral<T>::value) {
        return t + 1; // T为整型时编译
    } else {
        return t + 0.001; // T为浮点时编译
    }
}

// 配合变参模板实现编译期循环
template<typename T0, typename... T>
void printf2(T0 t0, T... t) {
    std::cout << t0 << std::endl;
    if constexpr (sizeof...(t) > 0) printf2(t...);
}

// 比SFINAE更清晰的写法
template<typename T>
void process(T val) {
    if constexpr (std::is_same_v<T, int>) {
        // 处理int
    } else if constexpr (std::is_same_v<T, std::string>) {
        // 处理string
    }
}
```

## 相关概念
- [[entities/cpp/constexpr]] - if constexpr是constexpr的延伸
- [[entities/cpp/variadic-templates]] - 模板与编译期分支结合
- [[entities/cpp/auto-type-deduction]] - auto与编译期类型判断

## 来源详情
- [[sources/pdf-modern-cpp-tutorial]] - Chapter 2.4: if constexpr
