---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# State Pattern (状态模式)

## GoF 定义

允许对象在内部状态改变时改变其行为，看起来像是对象换了类。

## C++ 实现

### 状态驱动的状态机（经典 GoF）

```cpp
struct State {
    virtual void on(LightSwitch* ls) { cout << "Light is already on\n"; }
    virtual void off(LightSwitch* ls) { cout << "Light is already off\n"; }
};

struct OnState : State {
    void off(LightSwitch* ls) override;
};

struct OffState : State {
    void on(LightSwitch* ls) override;
};

class LightSwitch {
    State* state;
public:
    LightSwitch() { state = new OffState(); }
    ~LightSwitch() { delete state; }
    void set_state(State* s) { delete state; state = s; }
    void on() { state->on(this); }
    void off() { state->off(this); }
    friend struct OnState;
    friend struct OffState;
};

void OnState::off(LightSwitch* ls) {
    cout << "Switching light off...\n";
    ls->set_state(new OffState());
    delete this;  // 状态自删除
}
```

### 手工状态机（枚举 + Map）

```cpp
enum class State { off_hook, connecting, connected, on_hold, on_hook };
enum class Trigger { call_dialed, hung_up, call_connected, placed_on_hold, taken_off_hold };

map<State, vector<pair<Trigger, State>>> rules;
rules[State::off_hook] = {{Trigger::call_dialed, State::connecting},
                          {Trigger::stop_using_phone, State::on_hook}};

State currentState{State::off_hook};
Trigger input;
// ... 用户选择触发器
currentState = rules[currentState][input].second;
```

### Boost.MSM

```cpp
struct PhoneStateMachine : state_machine_def<PhoneStateMachine> {
    typedef OffHook initial_state;
    typedef mpl::vector<
        Row<OffHook, CallDialed, Connecting>,
        Row<Connecting, CallConnected, Connected>,
        Row<Connected, PlacedOnHold, OnHold>
    > transition_table;
};

msm::back::state_machine<PhoneStateMachine> phone;
phone.process_event(CallDialed{});
```

## 关键点

- 状态类自己触发转换（经典）或状态机集中管理（枚举+Map）
- 手工状态机最直观：枚举 + `std::map` 规则表
- Boost.MSM 支持分层状态机、守卫条件

## 相关模式

- [[strategy-pattern]]
- [[chain-of-responsibility-pattern]]
