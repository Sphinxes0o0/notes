---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Lambda Expressions (Lambda表达式)

## 定义

Lambda是C++11引入的匿名函数对象，可定义即用，无需命名。语法：`[capture](params) mutable(exception) -> ret { body }`。Lambda完美替代了STL算法中的函数对象和std::bind。

## 关键要点

- **捕获方式**：
  - `[]`：不捕获
  - `[&]`：引用捕获
  - `[=]`：值捕获
  - `[=, &x]`：值捕获，x引用捕获
  - `[x = std::move(y)]`：C++14移动捕获
- **mutable**：值捕获后修改需加mutable
- **返回类型推导**：C++14起支持`auto`作为返回类型
- **泛型Lambda**：C++14起参数可用auto，类似于模板

## 代码示例

```cpp
// 基本lambda
auto add = [](int x, int y) { return x + y; };

// 值捕获与引用捕获
int value = 1;
auto copy = [value]() { return value; };     // 值捕获
auto ref = [&value]() { return value; };      // 引用捕获

// C++14移动捕获
auto important = std::make_unique<int>(1);
auto add = [v1 = 1, v2 = std::move(important)](int x, int y) -> int {
    return x + y + v1 + (*v2);
};

// C++14泛型lambda
auto generic = [](auto x, auto y) { return x + y; };
```

## 相关概念
- [[entities/cpp/move-semantics]] - Lambda中的移动捕获
- [[entities/cpp/auto-type-deduction]] - decltype用于lambda类型推导
- [[entities/cpp/smart-pointers]] - std::function包装Lambda

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 3: Lambda表达式
