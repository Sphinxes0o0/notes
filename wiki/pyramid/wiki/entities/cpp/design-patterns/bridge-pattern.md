---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Bridge Pattern (桥接模式)

## GoF 定义

将抽象部分与实现部分分离，使它们可以独立变化。

## C++ 实现

### Pimpl 编程技法

```cpp
struct Person {
    string name;
    void greet();
    Person();
    ~Person();
    class PersonImpl;
    PersonImpl* impl;
};

struct Person::PersonImpl {
    void greet(Person* p);
};

void Person::greet() { impl->greet(this); }
```

### 形状 × 渲染器（经典桥接）

```cpp
struct Renderer {
    virtual void render_circle(float x, float y, float radius) = 0;
};

struct VectorRenderer : Renderer {
    void render_circle(float x, float y, float radius) override {
        cout << "Drawing a vector circle of radius " << radius << endl;
    }
};

struct RasterRenderer : Renderer {
    void render_circle(float x, float y, float radius) override {
        cout << "Rasterizing circle of radius " << radius << endl;
    }
};

struct Shape {
protected:
    Renderer& renderer;
    Shape(Renderer& r) : renderer{r} {}
public:
    virtual void draw() = 0;
    virtual void resize(float factor) = 0;
};

struct Circle : Shape {
    float x, y, radius;
    Circle(Renderer& r, float x, float y, float rad)
        : Shape{r}, x{x}, y{y}, radius{rad} {}
    void draw() override { renderer.render_circle(x, y, radius); }
    void resize(float factor) override { radius *= factor; }
};
```

## 关键点

- `Shape` 持有 `Renderer` 引用，桥接抽象与实现
- Pimpl 将实现细节隐藏在 `.cpp` 中，保护二进制兼容性
- 与中介者模式区别：桥接双方相互知道对方存在

## 相关模式

- [[adapter-pattern]]
- [[mediator-pattern]]
