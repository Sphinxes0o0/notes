---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Composite Pattern (组合模式)

## GoF 定义

将对象组合成树形结构以表示"部分-整体"层次，让客户端对单个对象和组合对象有一致性。

## C++ 实现

### 图形对象组合

```cpp
struct GraphicObject {
    virtual void draw() = 0;
};

struct Circle : GraphicObject {
    void draw() override { cout << "Circle" << endl; }
};

struct Group : GraphicObject {
    string name;
    explicit Group(const string& n) : name(n) {}
    void draw() override {
        cout << "Group " << name << " contains:" << endl;
        for (auto&& o : objects) o->draw();
    }
    vector<GraphicObject*> objects;
};

Group root{"root"};
Circle c1, c2;
root.objects.push_back(&c1);
Group sub{"sub"};
sub.objects.push_back(&c2);
root.objects.push_back(&sub);
```

### SomeNeurons 模板（CRTP 跨类型迭代）

```cpp
template <typename Self>
struct SomeNeurons {
    template <typename T> void connect_to(T& other) {
        for (Neuron& from : *static_cast<Self*>(this))
            for (Neuron& to : other)
                from.out.push_back(&to), to.in.push_back(&from);
    }
};

struct Neuron : SomeNeurons<Neuron> {
    vector<Neuron*> in, out;
    Neuron* begin() override { return this; }
    Neuron* end() override { return this + 1; }
};

struct NeuronLayer : vector<Neuron>, SomeNeurons<NeuronLayer> {
    explicit NeuronLayer(int count) { while (count-- > 0) emplace_back(); }
};

Neuron n1, n2;
NeuronLayer layer1, layer2;
n1.connect_to(n2);
n1.connect_to(layer1);
layer1.connect_to(layer2);
```

## 关键点

- 统一接口使单对象和容器对客户端透明
- `begin()/end()` 让标量对象伪装成可迭代集合
- CRTP 模板实现跨类型 `connect_to`

## 相关模式

- [[visitor-pattern]]
- [[iterator-pattern]]
