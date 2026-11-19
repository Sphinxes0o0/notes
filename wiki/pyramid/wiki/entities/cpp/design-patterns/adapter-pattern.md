---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-28
sources: [github-liuzengh-design-pattern]
---

# Adapter Pattern (适配器模式)

## GoF 定义

将一个类的接口转换成客户期望的另一个接口，使原本不兼容的类可以协同工作。

## C++ 实现

```cpp
// 目标接口
class Target {
public:
    virtual void request() = 0;
};

// 需要适配的类
class Adaptee {
public:
    void specificRequest() { /* ... */ }
};

// 适配器
class Adapter : public Target {
    Adaptee* adaptee;
public:
    Adapter(Adaptee* a) : adaptee(a) {}
    void request() override { adaptee->specificRequest(); }
};
```

## 相关模式

- [[facade-pattern]]
- [[bridge-pattern]]
- [[decorator-pattern]]
