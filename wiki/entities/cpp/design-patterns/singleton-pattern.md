---
type: entity
tags: [cpp, design-patterns, creational]
created: 2026-05-26
sources: [github-liuzengh-design-pattern]
---

# Singleton Pattern (单例模式)

## GoF 定义

确保一个类只有一个实例，并提供全局访问点。

## C++11 实现 (Meyer's Singleton)

```cpp
class Singleton {
public:
    static Singleton& getInstance() {
        static Singleton instance;  // C++11 保证线程安全
        return instance;
    }
private:
    Singleton() = default;
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
};
```

## 关键点

- C++11 `static` 局部变量初始化是线程安全的
- 删除拷贝构造和赋值运算符
- 不需要显式 mutex/lock

## 相关模式

- [[factory-pattern]]
- [[builder-pattern]]
