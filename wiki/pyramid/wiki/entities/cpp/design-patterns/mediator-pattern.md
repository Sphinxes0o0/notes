---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Mediator Pattern (中介者模式)

## GoF 定义

用一个中介对象来封装一系列对象交互，使各对象不需要显式相互引用。

## C++ 实现

### 聊天室

```cpp
struct Person {
    string name;
    ChatRoom* room = nullptr;
    vector<string> chat_log;
    void receive(const string& origin, const string& msg);
    void say(const string& msg) const { room->broadcast(name, msg); }
    void pm(const string& who, const string& msg) const;
};

struct ChatRoom {
    vector<Person*> people;
    void join(Person* p) {
        string msg = p->name + " joins the chat";
        broadcast("room", msg);
        p->room = this;
        people.push_back(p);
    }
    void broadcast(const string& origin, const string& msg) {
        for (auto p : people) if (p->name != origin) p->receive(origin, msg);
    }
    void message(const string& origin, const string& who, const string& msg) {
        auto target = find_if(people.begin(), people.end(),
            [&](Person* p){ return p->name == who; });
        if (target != people.end()) (*target)->receive(origin, msg);
    }
};

ChatRoom room;
Person john{"john"}, jane{"jane"};
room.join(&john); room.join(&jane);
john.say("hi room");
jane.say("oh, hey john");
```

### 中介者 + 事件（观察者模式结合）

```cpp
struct Game {
    signal<void(EventData*)> events;
};

struct Player {
    string name; int goals_scored = 0;
    Game& game;
    void score() {
        goals_scored++;
        game.events.notify(/* PlayerScoredData */);
    }
};

struct Coach {
    Game& game;
    explicit Coach(Game& g) {
        game.events.connect([](EventData* e) {
            auto* ps = dynamic_cast<PlayerScoredData*>(e);
            if (ps && ps->goals_scored_so_far < 3)
                cout << "coach says: well done, " << ps->player_name << "\n";
        });
    }
};
```

## 关键点

- 中介者集中管理组件间通信，避免网状依赖
- 聊天室是最直观的例子
- 结合事件系统后，中介者可支持发布-订阅

## 相关模式

- [[observer-pattern]]
- [[chain-of-responsibility-pattern]]
