---
type: entity
tags: [cpp, design-patterns, creational]
created: 2026-05-28
sources: [github-liuzengh-design-pattern]
---

# Builder Pattern (建造者模式)

## GoF 定义

将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

## C++ 实现

```cpp
class Builder {
public:
    virtual void buildPartA() = 0;
    virtual void buildPartB() = 0;
    virtual Product* getResult() = 0;
};

class ConcreteBuilder : public Builder {
    Product product;
public:
    void buildPartA() override { product.add("PartA"); }
    void buildPartB() override { product.add("PartB"); }
    Product* getResult() override { return &product; }
};

class Director {
    Builder* builder;
public:
    void setBuilder(Builder* b) { builder = b; }
    void construct() {
        builder->buildPartA();
        builder->buildPartB();
    }
};
```

## 相关模式

- [[factory-pattern]]
- [[prototype-pattern]]
- [[composite-pattern]]
