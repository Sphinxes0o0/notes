---
type: entity
tags: [cpp, design-patterns, creational]
created: 2026-05-26
sources: [github-liuzengh-design-pattern]
---

# Factory Pattern (工厂模式)

## 子类型

- **Simple Factory**: 一个工厂类根据参数创建不同产品
- **Factory Method**: 子类决定实例化哪个具体类
- **Abstract Factory**: 创建相关对象族

## C++ 实现

```cpp
// Simple Factory
class ShapeFactory {
public:
    static unique_ptr<Shape> create(const string& type) {
        if (type == "circle") return make_unique<Circle>();
        if (type == "square") return make_unique<Square>();
        return nullptr;
    }
};
```

## 相关模式

- [[singleton-pattern]]
- [[builder-pattern]]
- [[strategy-pattern]]
