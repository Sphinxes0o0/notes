---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-26
sources: [github-liuzengh-design-pattern]
---

# Observer Pattern (观察者模式)

## GoF 定义

定义一对多依赖关系，当一个对象状态改变时，所有依赖者自动收到通知。

## C++ 实现

```cpp
class Observer {
public:
    virtual void update(const string& msg) = 0;
};

class Subject {
    vector<weak_ptr<Observer>> observers;
public:
    void attach(shared_ptr<Observer> o) { observers.push_back(o); }
    void notify(const string& msg) {
        for (auto& w : observers)
            if (auto o = w.lock()) o->update(msg);
    }
};
```

## 关键点

- 用 `weak_ptr` 避免循环引用
- 现代 C++ 可用 `std::function` + lambda 替代继承

## 相关模式

- [[strategy-pattern]]
- [[mediator-pattern]]
