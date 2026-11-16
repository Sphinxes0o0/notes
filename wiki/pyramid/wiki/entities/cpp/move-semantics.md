---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Move Semantics (移动语义)

## 定义

C++11引入的移动语义允许高效地"移动"资源而非复制，从而消除不必要的深拷贝开销。右值引用(`T&&`)使得识别临时对象（可移动对象）成为可能。

## 关键要点

- **值类别**：左值(lvalue)、右值(rvalue)、xvalue、prvalue
- **移动构造/赋值**：接收右值引用，转移资源所有权
- **std::move**：将左值转换为右值引用，触发移动操作
- **std::forward**：完美转发，保持参数的左右值类别
- **移动语义适用场景**：临时对象、容器操作（vector::push_back）、返回值优化

## 代码示例

```cpp
// 移动构造函数
A(A&& a) : pointer(a.pointer) {
    a.pointer = nullptr; // 源对象置空，避免重复释放
}

// std::move使用
std::string str = "Hello world.";
std::vector<std::string> v;
v.push_back(std::move(str)); // str变为空，资源被"移动"

// std::forward完美转发
template<typename T>
void pass(T&& v) {
    reference(std::forward<T>(v)); // 保持原始类别
}
```

## 相关概念
- [[entities/cpp/lambda-expressions]] - Lambda中的移动捕获
- [[entities/cpp/smart-pointers]] - 智能指针利用移动语义
- [[entities/cpp/auto-type-deduction]] - decltype(auto)处理移动

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 3.3: 值类别与移动语义
