---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Template Method Pattern (模板方法模式)

## GoF 定义

定义算法骨架，将某些步骤延迟到子类，使子类可不改变算法结构。

## C++ 实现

### 虚方法版

```cpp
class Game {
protected:
    int current_player = 0;
    int number_of_players;
    explicit Game(int n) : number_of_players(n) {}
    virtual void start() = 0;
    virtual bool have_winner() = 0;
    virtual void take_turn() = 0;
    virtual int get_winner() = 0;
public:
    void run() {
        start();
        while (!have_winner())
            take_turn();
        cout << "Player " << get_winner() << " wins.\n";
    }
};

class Chess : public Game {
    int turns = 0, max_turns = 10;
public:
    Chess() : Game(2) {}
protected:
    void start() override { cout << "Starting a game of chess with 2 players\n"; }
    bool have_winner() override { return turns == max_turns; }
    void take_turn() override {
        cout << "Turn " << turns << " taken by player " << current_player << "\n";
        ++turns;
        current_player = (current_player + 1) % number_of_players;
    }
    int get_winner() override { return current_player; }
};

Chess chess;
chess.run();
```

## 关键点

- 模板方法用继承，策略方法用组合
- `run()` 是骨架，`start()/take_turn()` 等是延迟到子类的步骤
- 可将不需要被子类覆盖的方法设为空实现（默认 no-op）

## 相关模式

- [[strategy-pattern]]
- [[factory-pattern]]
