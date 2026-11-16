---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Proxy Pattern (代理模式)

## GoF 定义

为其他对象提供一种代理以控制对这个对象的访问。

## C++ 实现

### 虚代理（延迟加载）

```cpp
struct Image { virtual void draw() = 0; };

struct Bitmap : Image {
    Bitmap(const string& filename) { cout << "Loading image from " << filename << endl; }
    void draw() override { cout << "Drawing image " << filename << endl; }
private:
    string filename;
};

struct LazyBitmap : Image {
    LazyBitmap(const string& fn) : filename(fn) {}
    ~LazyBitmap() { delete bmp; }
    void draw() override {
        if (!bmp) bmp = new Bitmap(filename);
        bmp->draw();
    }
private:
    Bitmap* bmp{nullptr};
    string filename;
};
// 构造 LazyBitmap 不加载，只有 draw() 才触发加载
```

### 属性代理

```cpp
template <typename T>
struct Property {
    T value;
    Property(const T v) { *this = v; }
    operator T() { return value; }  // getter
    T operator=(T new_value) { return value = new_value; }  // setter
};

struct Creature {
    Property<int> strength{10};
    Property<int> agility{5};
};
```

### 通信代理

```cpp
struct Pingable { virtual wstring ping(const wstring& msg) = 0; };
struct Pong : Pingable { wstring ping(const wstring& msg) override { return msg + L" pong"; } };
struct RemotePong : Pingable {  // HTTP 通信代理
    wstring ping(const wstring& msg) override {
        http_client client(U("http://localhost:9149/"));
        // ... REST call over the wire
    }
};
```

## 关键点

- 智能指针是天然代理
- 虚代理延迟实例化，适合重量级资源
- 与装饰器区别：代理不新增接口成员

## 相关模式

- [[decorator-pattern]]
- [[adapter-pattern]]
