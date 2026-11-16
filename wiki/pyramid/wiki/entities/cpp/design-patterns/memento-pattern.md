---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Memento Pattern (备忘录模式)

## GoF 定义

在不破坏封装性的情况下，捕获对象内部状态并在对象外保存，以便日后恢复。

## C++ 实现

### 基础备忘录

```cpp
class Memento {
    int balance;
    friend class BankAccount;
    Memento(int b) : balance(b) {}
};

class BankAccount {
    int balance = 0;
public:
    explicit BankAccount(int b) : balance(b) {}
    Memento deposit(int amount) {
        balance += amount;
        return {balance};
    }
    void restore(const Memento& m) { balance = m.balance; }
};

// 使用
BankAccount ba{100};
auto m1 = ba.deposit(50);
auto m2 = ba.deposit(25);
ba.restore(m1);  // 回滚到 150
```

### Undo/Redo 支持

```cpp
class BankAccount2 {
    int balance = 0;
    vector<shared_ptr<Memento>> changes;
    int current = 0;
public:
    explicit BankAccount2(int b) { changes.emplace_back(make_shared<Memento>(b)); balance = b; }
    shared_ptr<Memento> deposit(int amount) {
        balance += amount;
        auto m = make_shared<Memento>(balance);
        changes.push_back(m);
        ++current;
        return m;
    }
    void restore(const shared_ptr<Memento>& m) {
        if (m) { balance = m->balance; changes.push_back(m); current = changes.size() - 1; }
    }
    shared_ptr<Memento> undo() {
        if (current > 0) { --current; balance = changes[current]->balance; }
        return {};
    }
    shared_ptr<Memento> redo() {
        if (current + 1 < changes.size()) {
            ++current; balance = changes[current]->balance;
        }
        return {};
    }
};
```

## 关键点

- Memento 是不可变的（友元类或内部类）
- `changes` 列表 + `current` 指针支持 undo/redo
- 适合实现命令历史、快照功能

## 相关模式

- [[command-pattern]]
- [[iterator-pattern]]
