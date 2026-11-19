---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-28
sources: [github-liuzengh-design-pattern]
---

# Decorator Pattern (装饰器模式)

## GoF 定义

动态地给对象添加一些额外的职责，比继承更加灵活。

## C++ 实现

```cpp
class Component {
public:
    virtual void operation() = 0;
};

class ConcreteComponent : public Component {
public:
    void operation() override { cout << "ConcreteComponent"; }
};

class Decorator : public Component {
    Component* component;
public:
    Decorator(Component* c) : component(c) {}
    void operation() override { component->operation(); }
};

class ConcreteDecorator : public Decorator {
public:
    ConcreteDecorator(Component* c) : Decorator(c) {}
    void addedBehavior() { cout << " + Added"; }
    void operation() override {
        Decorator::operation();
        addedBehavior();
    }
};
```

## 相关模式

- [[adapter-pattern]]
- [[strategy-pattern]]
- [[composite-pattern]]
