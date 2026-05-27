---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Chain of Responsibility Pattern (责任链模式)

## GoF 定义

使多个对象都有机会处理请求，从而避免请求的发送者和接收者耦合。

## C++ 实现

### 指针链

```cpp
struct Creature { string name; int attack, defense; };

class CreatureModifier {
    CreatureModifier* next{nullptr};
protected:
    Creature& creature;
public:
    explicit CreatureModifier(Creature& c) : creature(c) {}
    void add(CreatureModifier* cm) {
        if (next) next->add(cm);
        else next = cm;
    }
    virtual void handle() { if (next) next->handle(); }
};

class DoubleAttackModifier : public CreatureModifier {
public:
    explicit DoubleAttackModifier(Creature& c) : CreatureModifier(c) {}
    void handle() override {
        creature.attack *= 2;
        CreatureModifier::handle();
    }
};

// 使用
Creature goblin{"Goblin", 1, 1};
CreatureModifier root{goblin};
DoubleAttackModifier r1{goblin}, r2{goblin};
root.add(&r1);
root.add(&r2);
root.handle();  // goblin attack = 4
```

### 事件代理（信号槽）

```cpp
struct Game { signal<void(Query&)> queries; };

struct Query {
    string creature_name;
    enum Argument { attack, defense } argument;
    int result;
};

class Creature {
    Game& game;
public:
    int get_attack() const {
        Query q{name, Query::attack, attack};
        game.queries(q);
        return q.result;
    }
};

class DoubleAttackModifier : public CreatureModifier {
    connection conn;
public:
    DoubleAttackModifier(Game& g, Creature& c) : CreatureModifier(g, c) {
        conn = g.queries.connect([&](Query& q) {
            if (q.creature_name == creature.name && q.argument == Query::attack)
                q.result *= 2;
        });
    }
    ~DoubleAttackModifier() { conn.disconnect(); }
};
```

## 关键点

- 链可以是仅追加链表（指针）或集中式信号槽
- 每个 Handler 必须调用基类 `handle()` 传递链
- 事件代理模式结合了中介者和观察者

## 相关模式

- [[command-pattern]]
- [[mediator-pattern]]
