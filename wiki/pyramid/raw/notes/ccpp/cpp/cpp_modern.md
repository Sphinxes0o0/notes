---
title: C++ 移动语义与完美转发
date: 2024-01-20 10:00:00
tags:
    - cpp
    - move-semantics
    - perfect-forwarding
---

## 1. 左值与右值

### 1.1 左值 (lvalue)

左值是指具有持久存储地址的表达式，可以在多条语句中持续存在。左值可以出现在赋值运算符的左侧或右侧。

**左值的特点**：
- 具有稳定的内存地址
- 可以通过取地址运算符获取其地址
- 可以作为左值或右值使用
- 通常对应有名字的变量

### 1.2 右值 (rvalue)

右值是临时的、即将被销毁的表达式，不能对其取地址。右值只能出现在赋值运算符的右侧。

**右值的特点**：
- 临时的，没有稳定的地址
- 不能对其使用取地址运算符
- 通常是字面量或临时对象
- 即将被销毁

### 1.3 右值引用

右值引用使用 `&&` 语法：

```cpp
int&& rref = 42;  // 右值引用绑定到右值
```

## 2. 移动语义

### 2.1 为什么需要移动语义

移动语义避免不必要的拷贝，提高性能：

```cpp
std::vector<int> v1(1000000, 1);
std::vector<int> v2 = v1;     // 拷贝：复制所有元素
std::vector<int> v3 = std::move(v1);  // 移动：v1 的资源转移到 v3
```

### 2.2 移动构造函数

```cpp
class Buffer {
private:
    char* data;
    size_t size;
public:
    // 移动构造函数
    Buffer(Buffer&& other) noexcept : data(other.data), size(other.size) {
        other.data = nullptr;
        other.size = 0;
    }
};
```

### 2.3 移动赋值运算符

```cpp
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = other.data;
            size = other.size;
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }
```

### 2.4 std::move 的原理

`std::move` 实际上是一个强制类型转换，将左值转换为右值引用：

```cpp
template<typename T>
typename std::remove_reference<T>::type&& move(T&& param) {
    return static_cast<typename std::remove_reference<T>::type&&>(param);
}
```

## 3. 完美转发

### 3.1 转发问题描述

函数模板参数需要保持原始值类别：

```cpp
void process(int& x) { /* 处理左值 */ }
void process(int&& x) { /* 处理右值 */ }

template<typename T>
void wrapper(T&& param) {
    process(param);  // param 永远是左值，无法转发右值
}
```

### 3.2 std::forward 的使用

`std::forward` 解决完美转发问题：

```cpp
template<typename T>
void wrapper(T&& param) {
    process(std::forward<T>(param));  // 保持原始值类别
}
```

### 3.3 通用引用

`T&&` 在模板参数推导时会绑定到任何值类别：

```cpp
template<typename T>
void func(T&& x) {  // x 是通用引用
    // 可以是左值或右值
}
```

## 4. 实际应用

### 4.1 移动语义在 STL 中的应用

```cpp
std::vector<int> v1{1, 2, 3, 4, 5};
std::vector<int> v2 = std::move(v1);  // v1 被清空
```

### 4.2 移动语义与性能优化

避免不必要的拷贝：

```cpp
// 错误：不必要的拷贝
std::vector<int> return_vector() {
    std::vector<int> v(1000);
    return v;  // 拷贝
}

// 正确：移动语义
std::vector<int> return_vector() {
    std::vector<int> v(1000);
    return std::move(v);  // 移动
}
```

### 4.3 常见的坑

1. 移动后对象处于有效但未定义的状态
2. 不要移动 const 对象
3. 移动成员函数不会自动生成

---

## 总结

- **左值**：有持久地址，可取地址
- **右值**：临时对象，不可取地址
- **移动语义**：转移资源所有权，避免拷贝
- **完美转发**：保持参数原始值类别
- **std::move**：强制转换为右值引用
- **std::forward**：条件性地保持值类别
