---
title: RAII 资源获取即初始化
date: 2024-01-15 21:00:00
tags:
    - cpp
    - raii
---

## 1. RAII 原理

### 1.1 核心思想

RAII（Resource Acquisition Is Initialization，资源获取即初始化）是一种 C++ 编程惯用法，其核心思想是：

- **资源获取 = 对象构造**：将资源的获取与对象的初始化绑定在一起
- **资源释放 = 对象析构**：将资源的释放与对象的销毁绑定在一起
- **自动管理**：利用 C++ 自动调用析构函数的机制，实现资源的自动释放

```cpp
class FileHandler {
    FILE* file;
public:
    FileHandler(const char* filename) {
        file = fopen(filename, "w");
        if (!file) throw std::runtime_error("Failed to open file");
    }

    ~FileHandler() {
        if (file) {
            fclose(file);
        }
    }

    FILE* get() const { return file; }
};
```

### 1.2 为什么能做到自动释放

C++ 的对象析构函数在以下情况下会自动被调用：

- **栈对象离开作用域**：最常见的情况
- **异常传播**：栈展开过程中，本地对象被销毁
- **线程结束**：线程局部的栈对象被销毁

```cpp
void process() {
    FileHandler fh("data.txt");  // 构造函数获取资源

    // 使用文件...
    // 即使这里抛出异常，析构函数也会被调用

}  // fh 离开作用域，析构函数自动释放资源
```

### 1.3 资源不仅仅指内存

RAII 中的"资源"是广义的概念：

- 内存（堆分配）
- 文件句柄
- 线程句柄
- 网络 sockets
- 锁
- 数据库连接
- 图形设备上下文

## 2. RAII 示例

### 2.1 智能指针

智能指针是 RAII 最典型的应用：

```cpp
#include <memory>

void smart_pointer_example() {
    // unique_ptr - 独占所有权
    auto ptr1 = std::make_unique<int>(42);

    // shared_ptr - 共享所有权
    auto ptr2 = std::make_shared<int>(42);

    // 离开作用域时自动释放
}
```

### 2.2 文件句柄管理

封装文件句柄，确保文件正确关闭：

```cpp
class FileGuard {
    std::string filename;
    FILE* file;
public:
    FileGuard(const std::string& name, const char* mode)
        : filename(name), file(nullptr) {
        file = fopen(name.c_str(), mode);
        if (!file) {
            throw std::runtime_error("Cannot open file: " + filename);
        }
    }

    ~FileGuard() {
        if (file) {
            std::cout << "Closing file: " << filename << std::endl;
            fclose(file);
        }
    }

    FILE* get() const { return file; }
};

void file_usage() {
    FileGuard fg("test.txt", "w");
    fprintf(fg.get(), "Hello, RAII!\n");
    // 即使发生异常，文件也会正确关闭
}
```

### 2.3 锁的自动释放

使用 RAII 封装互斥锁，避免死锁：

```cpp
#include <mutex>

class LockGuard {
    std::mutex& mtx;
public:
    explicit LockGuard(std::mutex& m) : mtx(m) {
        mtx.lock();
    }

    ~LockGuard() {
        mtx.unlock();
    }

    // 防止拷贝和移动
    LockGuard(const LockGuard&) = delete;
    LockGuard& operator=(const LockGuard&) = delete;
};

std::mutex global_mutex;
int shared_data = 0;

void safe_increment() {
    LockGuard guard(global_mutex);
    ++shared_data;
    // 离开作用域时自动解锁
}
```

## 3. RAII 的优势

### 3.1 异常安全

即使在代码执行过程中抛出异常，RAII 也能保证资源被正确释放：

```cpp
void dangerous_without_raii() {
    FILE* f = fopen("data.txt", "r");
    // 如果这里抛出异常，f 永远不会被关闭
    parse(f);
    fclose(f);
}

void safe_with_raii() {
    auto file = std::unique_ptr<FILE, decltype(&fclose)>(
        fopen("data.txt", "r"), fclose);

    // 即使这里抛出异常，file 也会被正确关闭
    parse(file.get());
    // 离开作用域自动调用 fclose
}
```

### 3.2 简化错误处理

不需要在每个错误处理路径上显式释放资源：

```cpp
// 没有 RAII - 需要多处释放
void complex_flow_without_raii() {
    int* data = new int[100];
    FILE* f = fopen("config.txt", "r");

    if (!f) {
        delete[] data;  // 容易遗漏
        return;
    }

    if (something_wrong) {
        delete[] data;  // 容易遗漏
        fclose(f);      // 容易遗漏
        return;
    }

    // 正常流程...

    delete[] data;      // 需要多处释放
    fclose(f);
}

// 使用 RAII - 单一释放点
void complex_flow_with_raii() {
    std::unique_ptr<int[]> data(new int[100]);
    std::unique_ptr<FILE, decltype(&fclose)> file(
        fopen("config.txt", "r"), fclose);

    if (!file) return;

    if (something_wrong) return;

    // 正常流程...
    // 单一退出点，两个资源都会自动释放
}
```

### 3.3 防止资源泄漏

资源获取和释放的位置清晰明确，降低遗漏风险：

```cpp
// 容易泄漏的情况
void leak_example() {
    auto ptr = new int[100];

    if (condition()) return;  // 泄漏！

    delete[] ptr;
}

// 不会泄漏的情况
void no_leak_example() {
    auto ptr = std::make_unique<int[]>(100);

    if (condition()) return;  // 正常释放

    delete[] ptr;
}
```

## 4. RAII 在 STL 中的应用

### 4.1 std::lock_guard

最简单的锁管理 RAII 包装器：

```cpp
#include <mutex>

std::mutex mtx;

void process() {
    std::lock_guard<std::mutex> lock(mtx);
    // 临界区代码
    // ...
}  // 离开作用域自动解锁
```

`std::lock_guard` 的特点：
- 简单轻量
- 不可复制，不可移动
- 作用域结束时自动解锁

### 4.2 std::unique_lock

更灵活的锁管理，支持延迟锁定：

```cpp
#include <mutex>

std::mutex mtx;

void flexible_locking() {
    std::unique_lock<std::mutex> lock(mtx);

    // 特性 1：延迟锁定
    std::unique_lock<std::mutex> lazy_lock;
    lazy_lock.lock();  // 稍后手动锁定

    // 特性 2：可以提前解锁
    lock.unlock();
    // 非临界区操作...
    lock.lock();  // 重新锁定

    // 特性 3：支持尝试锁定
    std::unique_lock<std::mutex> try_lock(mtx, std::try_to_lock);
    if (try_lock.owns_lock()) {
        // 获取锁成功
    }

    // 特性 4：支持锁的转移
    std::unique_lock<std::mutex> lock1(mtx);
    std::unique_lock<std::mutex> lock2(std::move(lock1));
}  // lock2 释放锁
```

### 4.3 std::shared_lock

用于读写锁的读锁（共享锁）：

```cpp
#include <shared_mutex>

class ReadWriteProtected {
    mutable std::shared_mutex mtx;
    int data = 0;

public:
    // 读操作 - 共享锁
    int read() const {
        std::shared_lock<std::shared_mutex> lock(mtx);
        return data;
    }

    // 写操作 - 独占锁
    void write(int value) {
        std::unique_lock<std::shared_mutex> lock(mtx);
        data = value;
    }
};
```

## 5. 实现自己的 RAII 类

### 5.1 ScopeGuard 模式

最通用的 RAII 包装模式：

```cpp
template<typename T>
class ScopeGuard {
    T resource;
    std::function<void(T)> release;

public:
    ScopeGuard(T res, std::function<void(T)> rel)
        : resource(res), release(std::move(rel)) {}

    ~ScopeGuard() {
        if (release) {
            release(resource);
        }
    }

    // 防止拷贝，允许移动
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

    ScopeGuard(ScopeGuard&& other) noexcept
        : resource(other.resource), release(std::move(other.release)) {
        other.release = nullptr;
    }

    T get() const { return resource; }
};

// 使用示例
void scope_guard_example() {
    FILE* f = fopen("data.txt", "w");
    ScopeGuard<FILE*> guard(f, [](FILE* fp) {
        if (fp) fclose(fp);
    });

    fprintf(f, "Hello!\n");

    // 提前取消释放（如果需要）
    // guard.release = nullptr;
}
```

### 5.2 通用资源包装

定义一个通用的 ResourceGuard 模板：

```cpp
template<typename T, typename ReleaseFunc>
class ResourceGuard {
    T resource;
    ReleaseFunc release_func;
    bool active = true;

public:
    ResourceGuard(T res, ReleaseFunc rel)
        : resource(res), release_func(std::move(rel)) {}

    ~ResourceGuard() {
        if (active) {
            release_func(resource);
        }
    }

    ResourceGuard(const ResourceGuard&) = delete;
    ResourceGuard& operator=(const ResourceGuard&) = delete;

    ResourceGuard(ResourceGuard&& other) noexcept
        : resource(other.resource)
        , release_func(std::move(other.release_func))
        , active(other.active) {
        other.active = false;
    }

    T get() const { return resource; }

    void release() { active = false; }
};

// 使用示例：文件句柄
void file_resource_example() {
    auto file_guard = ResourceGuard(
        fopen("test.txt", "r"),
        [](FILE* f) { if (f) fclose(f); }
    );

    if (!file_guard.get()) {
        return;
    }

    // 读取文件...
    // 自动关闭
}

// 使用示例：自定义资源
class DatabaseConnection {
public:
    void disconnect() { std::cout << "Disconnected\n"; }
};

void database_resource_example() {
    DatabaseConnection conn;
    auto db_guard = ResourceGuard(
        &conn,
        [](DatabaseConnection* c) { c->disconnect(); }
    );

    // 使用数据库连接...
    // 离开作用域自动断开
}
```

### 5.3 条件释放模式

支持在特定条件下放弃 RAII 所有权：

```cpp
template<typename T>
class ConditionalGuard {
    T resource;
    std::function<void(T)> release;
    bool owns = true;

public:
    ConditionalGuard(T res, std::function<void(T)> rel)
        : resource(res), release(std::move(rel)) {}

    ~ConditionalGuard() {
        if (owns && release) {
            release(resource);
        }
    }

    void release_ownership() { owns = false; }

    T get() const { return resource; }
};

void conditional_release_example() {
    auto guard = ConditionalGuard(
        fopen("temp.txt", "w"),
        [](FILE* f) { if (f) fclose(f); }
    );

    if (!guard.get()) {
        return;  // 自动释放
    }

    // 某些条件下转移所有权
    if (needs_transfer) {
        // 将文件句柄转移给另一部分代码
        FILE* transferred = guard.get();
        guard.release_ownership();
        // 使用 transferred...
    }
}
```

## 总结

RAII 是现代 C++ 编程的核心原则之一：

- **核心机制**：利用构造/析构函数自动管理资源
- **优势**：异常安全、简化错误处理、防止资源泄漏
- **STL 应用**：`lock_guard`、`unique_lock`、`shared_lock`
- **最佳实践**：优先使用标准库提供的 RAII 包装器，需要时自定义

掌握 RAII 模式是写出安全、可靠的 C++ 代码的基础。
