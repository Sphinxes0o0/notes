---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Command Pattern (命令模式)

## GoF 定义

将请求封装为对象，从而允许参数化客户端，支持撤销和日志。

## C++ 实现

### 基础命令 + 撤销

```cpp
struct BankAccount {
    int balance = 0;
    bool withdraw(int amount) {
        if (balance - amount >= -500) { balance -= amount; return true; }
        return false;
    }
    void deposit(int amount) { balance += amount; }
};

struct Command {
    virtual void call() = 0;
    virtual void undo() = 0;
};

struct BankAccountCommand : Command {
    BankAccount& account;
    enum Action { deposit, withdraw } action;
    int amount;
    bool withdrawal_succeeded{false};

    BankAccountCommand(BankAccount& acc, Action a, int amt)
        : account(acc), action(a), amount(amt) {}

    void call() override {
        switch (action) {
            case deposit: account.deposit(amount); break;
            case withdraw: withdrawal_succeeded = account.withdraw(amount); break;
        }
    }
    void undo() override {
        if (action == deposit) account.withdraw(amount);
        else if (withdrawal_succeeded) account.deposit(amount);
    }
};
```

### 组合命令

```cpp
struct CompositeBankAccountCommand : vector<BankAccountCommand>, Command {
    using vector<BankAccountCommand>::vector;
    void call() override { for (auto& cmd : *this) cmd.call(); }
    void undo() override { for (auto it = rbegin(); it != rend(); ++it) it->undo(); }
};
```

### CQS（命令-查询分离）

```cpp
enum class CreatureAbility { strength, agility };
struct CreatureCommand { enum Action { set, increaseBy, decreaseBy }; Action action; CreatureAbility ability; int amount; };
struct CreatureQuery { CreatureAbility ability; };

void Creature::process_command(const CreatureCommand& cc) { /* 修改状态 */ }
int Creature::process_query(const CreatureQuery& q) const { /* 查询状态 */ }
```

## 关键点

- `call()/undo()` 接口封装动作和历史
- 组合命令支持宏操作（转账 = 取款 + 存款）
- CQS 将所有操作拆分为命令（写）和查询（读）

## 相关模式

- [[memento-pattern]]
- [[chain-of-responsibility-pattern]]
- [[composite-pattern]]
