---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-28
sources: [github-liuzengh-design-pattern]
---

# Visitor Pattern (访问者模式)

## GoF 定义

表示一个作用于某对象结构中的各元素的操作，使可以在不改变各元素类的前提下定义作用于这些元素的新操作。

## C++ 实现

```cpp
class Element;
class Visitor {
public:
    virtual void visit(Element* e) = 0;
};

class Element {
public:
    virtual void accept(Visitor* v) = 0;
};

class ConcreteElement : public Element {
public:
    void accept(Visitor* v) override { v->visit(this); }
    void specificOperation() { cout << "ConcreteElement"; }
};

class ConcreteVisitor : public Visitor {
public:
    void visit(Element* e) override {
        cout << "Visiting ";
        dynamic_cast<ConcreteElement*>(e)->specificOperation();
    }
};
```

## 相关模式

- [[composite-pattern]]
- [[iterator-pattern]]
- [[interpreter-pattern]]
