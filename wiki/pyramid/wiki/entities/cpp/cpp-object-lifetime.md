---
type: entity
tags: [cpp, object-lifetime, memory-management]
created: 2026-05-22
sources: [notes-ccpp]
---

# C++ 对象生命周期与分配策略

## 定义

C++ 中对象的建立分为静态建立（栈上，编译器分配/释放）和动态建立（堆上，`new`/`delete` 手动管理）。通过控制构造/析构函数访问权限和 `operator new` 可见性，可以强制限制对象的分配位置（堆 only 或栈 only）。

## 关键要点

- **静态建立（栈）**：编译器自动在栈空间分配内存，直接调用构造函数。例如 `A a;`，离开作用域自动析构
- **动态建立（堆）**：使用 `new` 关键字，底层先调用 `operator new()` 分配堆内存，再调用构造函数。例如 `A* p = new A();`
- **限制堆 only**：让编译器无法在栈上分配 — 将析构函数设为 `private`，编译器检查析构访问性后拒绝栈分配；或使用 `protected` 构造函数 + `public static` 工厂方法（类似单例模式，支持继承）
- **限制栈 only**：阻止 `new` 操作 — 将 `operator new(size_t)` 和 `operator delete(void*)` 设为 `private`，禁止堆分配
- **继承考虑**：析构函数设为 `private` 会阻断继承（派生类无法访问基类析构），应改用 `protected` 以支持多态

## 代码示例

```cpp
// 方法一：限制堆 only — 私有析构函数
class HeapOnly {
public:
    HeapOnly() {}
    void destroy() { delete this; }  // 类内可访问私有析构
private:
    ~HeapOnly() {}  // 编译器拒绝栈分配
};
// HeapOnly obj;       // 编译错误
// HeapOnly* p = new HeapOnly(); // OK，但需 p->destroy() 释放

// 方法二：限制堆 only — protected 构造 + 静态工厂（支持继承）
class HeapOnlyV2 {
protected:
    HeapOnlyV2() {}
    ~HeapOnlyV2() {}
public:
    static HeapOnlyV2* create() { return new HeapOnlyV2(); }
    void destroy() { delete this; }
};

// 限制栈 only — 私有 operator new/delete
class StackOnly {
private:
    void* operator new(size_t t) { return nullptr; }
    void operator delete(void* ptr) {}
public:
    StackOnly() {}
    ~StackOnly() {}
};
// StackOnly* p = new StackOnly(); // 编译错误
// StackOnly obj;                  // OK
```

## 设计意图

| 策略 | 适用场景 |
|------|----------|
| 堆 only | 对象生命周期需超过创建作用域；工厂模式产出；多态基类需动态分配 |
| 栈 only | 小型临时对象；性能敏感场景（避免堆分配开销）；RAII 资源管理 |

## 相关概念
- [[entities/cpp/raii]] — RAII 利用栈对象自动析构管理资源，栈 only 策略天然适合 RAII
- [[entities/cpp/smart-pointers]] — 智能指针封装了堆对象的生命周期管理，替代手动堆分配
- [[entities/cpp/move-semantics]] — 移动语义允许堆资源在栈对象间高效转移
- [[entities/cpp/cpp-serialization]] — 序列化/反序列化常涉及动态创建堆对象

## 来源详情
- [[sources/notes-ccpp]] — object_creation_heap_or_stack.md：堆-only 与栈-only 对象创建限制策略
