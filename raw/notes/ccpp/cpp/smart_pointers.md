---
title: C++ 智能指针
date: 2024-01-15 20:30:00
tags:
    - cpp
    - smart-pointer
---

## 1. RAII 原则

### 1.1 资源获取即初始化

RAII（Resource Acquisition Is Initialization）是一种 C++ 编程惯用法，核心思想是：**将资源的获取与对象的初始化绑定在一起，资源的释放与对象的销毁绑定在一起**。

```cpp
class FileHandler {
    FILE* file;
public:
    FileHandler(const char* filename) {
        file = fopen(filename, "r");
        if (!file) throw std::runtime_error("Failed to open file");
    }

    ~FileHandler() {
        if (file) fclose(file);
    }

    // ...
};
```

在构造函数中获取资源（打开文件），在析构函数中释放资源（关闭文件）。当对象离开作用域时，析构函数自动被调用，资源得到正确释放。

### 1.2 原理和好处

**原理**：
- C++ 的对象构造和析构是自动发生的
- 栈上对象的析构在离开作用域时自动执行
- 通过将资源管理封装在对象中，实现自动资源管理

**好处**：
- **异常安全**：即使发生异常，析构函数也会被调用，资源不会泄漏
- **简洁性**：无需手动管理资源，减少代码量
- **可靠性**：资源释放时机确定，减少人为错误
- **可维护性**：代码逻辑更清晰，资源管理集中

## 2. unique_ptr

### 2.1 独占所有权语义

`unique_ptr` 是独占所有权的智能指针，同一时刻只能有一个 `unique_ptr` 拥有某个对象。

```cpp
#include <memory>

std::unique_ptr<int> ptr1 = std::make_unique<int>(42);
// std::unique_ptr<int> ptr2 = ptr1;  // 编译错误：无法复制
std::unique_ptr<int> ptr2 = std::move(ptr1);  // 可以移动
```

### 2.2 无法复制，只能移动

`unique_ptr` 的拷贝构造函数和拷贝赋值运算符被删除（deleted），只能进行移动操作。

```cpp
class MoveOnly {
public:
    MoveOnly() = default;
    MoveOnly(const MoveOnly&) = delete;
    MoveOnly& operator=(const MoveOnly&) = delete;
    MoveOnly(MoveOnly&&) noexcept = default;
    MoveOnly& operator=(MoveOnly&&) noexcept = default;
};
```

### 2.3 使用场景

- **管理独占的资源**：如文件句柄、锁等
- **作为函数的返回值**：从函数返回独占所有权的对象
- **在容器中存储指针**（C++17 起可用 `std::optional` 或使用 `vector<unique_ptr<T>>`）
- **管理动态分配的数组**：`std::unique_ptr<T[]>`

```cpp
// 独占管理文件资源
std::unique_ptr<FILE, decltype(&fclose)> filePtr(
    fopen("data.txt", "r"), fclose);

// 管理动态数组
std::unique_ptr<int[]> arr = std::make_unique<int[]>(10);
```

## 3. shared_ptr

### 3.1 引用计数机制

`shared_ptr` 通过引用计数来共享所有权。每当有一个新的 `shared_ptr` 指向对象时，引用计数加 1；当一个 `shared_ptr` 被销毁或指向另一个对象时，引用计数减 1。当引用计数降为 0 时，对象被删除。

```cpp
std::shared_ptr<int> ptr1 = std::make_shared<int>(42);
std::cout << ptr1.use_count() << std::endl;  // 输出 1

{
    std::shared_ptr<int> ptr2 = ptr1;  // 共享所有权
    std::cout << ptr1.use_count() << std::endl;  // 输出 2
}  // ptr2 被销毁，引用计数回到 1

std::cout << ptr1.use_count() << std::endl;  // 输出 1
```

### 3.2 线程安全问题

`shared_ptr` 的引用计数本身是线程安全的，但是：

- **多个线程同时读写同一个 `shared_ptr` 对象，需要外部加锁**
- **`shared_ptr` 的控制块（包含引用计数）是原子操作的，但对象的访问不是**

```cpp
// 线程安全的 shared_ptr 操作需要加锁
std::shared_ptr<int> globalPtr = std::make_shared<int>(42);

void safe_increment() {
    std::lock_guard<std::mutex> lock(mutex);
    if (globalPtr) {
        ++(*globalPtr);
    }
}
```

### 3.3 循环引用问题

两个 `shared_ptr` 相互引用会导致循环引用，引用计数永远无法降为 0，造成内存泄漏。

```cpp
class Node {
public:
    std::shared_ptr<Node> next;
    ~Node() { std::cout << "Node destroyed\n"; }
};

void cycle_reference() {
    std::shared_ptr<Node> node1 = std::make_shared<Node>();
    std::shared_ptr<Node> node2 = std::make_shared<Node>();

    node1->next = node2;  // node2 引用计数 +1
    node2->next = node1;  // node1 引用计数 +1

    // 离开作用域时，两个 shared_ptr 的引用计数都是 2，不会降为 0
    // 导致两个 Node 对象都无法被销毁
}
```

## 4. weak_ptr

### 4.1 解决 shared_ptr 循环引用

`weak_ptr` 是一种不参与引用计数的智能指针，它指向由 `shared_ptr` 管理的对象，但不拥有该对象。

```cpp
class Node {
public:
    std::weak_ptr<Node> next;  // 使用 weak_ptr 打破循环引用
    ~Node() { std::cout << "Node destroyed\n"; }
};

void no_cycle_reference() {
    std::shared_ptr<Node> node1 = std::make_shared<Node>();
    std::shared_ptr<Node> node2 = std::make_shared<Node>();

    node1->next = node2;
    node2->next = node1;

    // 离开作用域时，node1 和 node2 的引用计数都降为 0
    // 两个 Node 对象都被正确销毁
}
```

### 4.2 lock() 方法

`lock()` 方法尝试从 `weak_ptr` 创建一个 `shared_ptr`。如果对象仍然存在，返回有效的 `shared_ptr`；否则返回空的 `shared_ptr`。

```cpp
std::weak_ptr<int> wp;

{
    std::shared_ptr<int> sp = std::make_shared<int>(42);
    wp = sp;

    std::shared_ptr<int> locked = wp.lock();
    if (locked) {
        std::cout << *locked << std::endl;  // 输出 42
    }
}  // sp 被销毁

std::shared_ptr<int> locked = wp.lock();
if (!locked) {
    std::cout << "Object has been destroyed\n";
}
```

### 4.3 use_count()

`use_count()` 返回引用计数（但不保证原子性，仅用于调试和诊断）。

```cpp
std::shared_ptr<int> sp1 = std::make_shared<int>(10);
std::weak_ptr<int> wp = sp1;

std::cout << wp.use_count() << std::endl;  // 输出 1

std::shared_ptr<int> sp2 = sp1;
std::cout << wp.use_count() << std::endl;  // 输出 2
```

## 5. 智能指针的实现原理

### 5.1 引用计数的实现

`shared_ptr` 的引用计数通常存储在堆上的控制块中，由 `shared_ptr` 和 `weak_ptr` 共享。

```cpp
// shared_ptr 的基本结构
template<typename T>
class shared_ptr {
    T* ptr;           // 原始指针
    control_block* cb; // 控制块指针

public:
    T& operator*() { return *ptr; }
    T* operator->() { return ptr; }

private:
    // 控制块包含引用计数和删除器
    struct control_block {
        std::atomic<int> ref_count;  // 引用计数
        std::atomic<int> weak_count; // weak_ptr 引用计数
        // ...
    };
};
```

引用计数增加的场景：
- 拷贝构造 `shared_ptr`
- 拷贝赋值
- 作为函数参数传递（按值传递）

引用计数减少的场景：
- 销毁 `shared_ptr`
- 赋值给另一个 `shared_ptr`

### 5.2 删除器的使用

`shared_ptr` 支持自定义删除器，删除器存储在控制块中。

```cpp
// 自定义删除器示例
auto deleter = [](FILE* fp) {
    std::cout << "Closing file\n";
    fclose(fp);
};

std::shared_ptr<FILE> filePtr(fopen("data.txt", "w"), deleter);
```

注意：删除器不是类型的一部分，以下两个类型是相同的：

```cpp
std::shared_ptr<FILE> pf1(fopen("a.txt", "r"), fclose);
std::shared_ptr<FILE> pf2(fopen("b.txt", "r"), [](FILE* f){ fclose(f); });
// pf1 和 pf2 类型相同，都是 shared_ptr<FILE>
```

### 5.3 make_shared vs new

**推荐使用 `std::make_shared`**：

```cpp
// 方式 1：make_shared（推荐）
auto sp1 = std::make_shared<int>(42);

// 方式 2：直接 new
std::shared_ptr<int> sp2(new int(42));
```

**make_shared 的优点**：
- 更高的效率：只分配一次内存（对象和控制块一起分配）
- 异常安全：避免在 new 和 shared_ptr 构造之间抛出异常

**make_shared 的缺点**：
- 无法指定自定义删除器
- 对象和控制块的生命周期绑定

## 6. 智能指针 vs 裸指针

### 6.1 安全性对比

| 特性 | 智能指针 | 裸指针 |
|------|----------|--------|
| 空指针检查 | 自动 | 手动 |
| 内存泄漏 | 几乎不可能 | 容易发生 |
| 重复释放 | 不可能 | 可能发生 |
| 悬空指针 | 不可能 | 可能发生 |
| 类型安全 | 是 | 是 |

```cpp
// 裸指针的风险
void danger() {
    int* p = new int(10);
    // 可能提前 return 或抛出异常
    // delete p;  // 容易忘记
}

// 智能指针保证安全
void safe() {
    auto p = std::make_unique<int>(10);
    // 即使抛出异常，p 也会自动释放
}
```

### 6.2 性能对比

**智能指针的额外开销**：

- **unique_ptr**：几乎零开销（仅在移动时可能产生一次拷贝）
- **shared_ptr**：存在一定的性能和空间开销
  - 原子引用计数的操作（atomic increment/decrement）
  - 控制块的大小（通常 2-3 个指针大小）
  - 线程安全带来的同步开销

```cpp
// 性能对比测试框架
void benchmark() {
    const int N = 1000000;

    // 裸指针
    int* raw = new int(0);
    for (int i = 0; i < N; ++i) {
        int* tmp = raw;
        delete raw;
        raw = new int(i);
    }

    // unique_ptr
    auto uptr = std::make_unique<int>(0);
    for (int i = 0; i < N; ++i) {
        auto tmp = std::move(uptr);
        uptr = std::make_unique<int>(i);
    }

    // shared_ptr
    auto sptr = std::make_shared<int>(0);
    for (int i = 0; i < N; ++i) {
        auto tmp = sptr;
    }
}
```

**何时使用裸指针**：
- 在性能关键代码中确定对象生命周期时
- 与 C 风格的 API 交互时（但应在接口边界转换）
- 实现智能指针本身或类似资源管理机制

**最佳实践**：
- 默认使用 `unique_ptr`
- 需要共享所有权时使用 `shared_ptr`
- 需要观察但不拥有时使用 `weak_ptr`
- 永远不要使用原始 `new` 手动管理内存

---

## 总结

智能指针是现代 C++ 内存管理的基石：

- **unique_ptr**：独占所有权，轻量高效，适用于大多数场景
- **shared_ptr**：共享所有权，通过引用计数管理，但有性能和循环引用问题
- **weak_ptr**：解决 shared_ptr 循环引用，适用于缓存和观察者模式

遵循 RAII 原则，优先使用智能指针，可以显著提高代码的安全性和可维护性。
