---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Null Object Pattern (空对象模式)

## GoF 定义

用提供默认"无操作"行为的对象代替 `nullptr`，使客户端无需空值检查。

## C++ 实现

### 基础空对象

```cpp
struct Logger {
    virtual ~Logger() = default;
    virtual void info(const string& s) = 0;
    virtual void warn(const string& s) = 0;
};

struct ConsoleLogger : Logger {
    void info(const string& s) override { cout << "INFO: " << s << endl; }
    void warn(const string& s) override { cout << "WARNING: " << s << endl; }
};

struct NullLogger : Logger {
    void info(const string&) override { }  // 无操作
    void warn(const string&) override { }
};

// 客户端使用
shared_ptr<Logger> logger = make_shared<NullLogger>();  // 替换 nullptr
BankAccount account{make_shared<NullLogger>(), "checking", 100};
account.deposit(50);  // 安全，不会崩溃
```

### 隐式空对象（OptionalLogger 代理）

```cpp
struct OptionalLogger : Logger {
    shared_ptr<Logger> impl;
    static shared_ptr<Logger> no_logging;
    OptionalLogger(const shared_ptr<Logger>& l) : impl(l) {}
    void info(const string& s) override { if (impl) impl->info(s); }
    void warn(const string& s) override { if (impl) impl->warn(s); }
};

class BankAccount {
    shared_ptr<OptionalLogger> log;
public:
    BankAccount(const string& name, int balance,
        const shared_ptr<Logger>& logger = OptionalLogger::no_logging)
        : log{make_shared<OptionalLogger>(logger)}, name{name}, balance{balance} {}
    void deposit(int amount) {
        balance += amount;
        log->info("Deposited $" + to_string(amount));
    }
};
```

## 关键点

- 空对象保持接口签名，但实现无操作
- `shared_ptr` / `unique_ptr` 不是空对象——解引用会崩溃
- `OptionalLogger` 是代理模式 + 空对象的组合

## 相关模式

- [[proxy-pattern]]
- [[strategy-pattern]]
