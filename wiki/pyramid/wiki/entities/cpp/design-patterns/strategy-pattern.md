---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-26
sources: [github-liuzengh-design-pattern]
---

# Strategy Pattern (策略模式)

## GoF 定义

定义一系列算法，封装每个算法，使它们可以互换。策略模式让算法独立于使用它的客户端而变化。

## C++ 实现

```cpp
class SortStrategy {
public:
    virtual void sort(vector<int>& data) = 0;
};

class QuickSort : public SortStrategy {
    void sort(vector<int>& data) override { /* ... */ }
};

class MergeSort : public SortStrategy {
    void sort(vector<int>& data) override { /* ... */ }
};

class Context {
    unique_ptr<SortStrategy> strategy;
public:
    void setStrategy(unique_ptr<SortStrategy> s) { strategy = move(s); }
    void execute(vector<int>& data) { strategy->sort(data); }
};
```

## 关键点

- 用 `unique_ptr` 管理策略所有权
- 现代 C++ 可用 `std::function` 替代继承

## 相关模式

- [[observer-pattern]]
- [[factory-pattern]]
