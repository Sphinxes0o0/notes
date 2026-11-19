---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Flyweight Pattern (享元模式)

## GoF 定义

运用共享技术有效地支持大量细粒度对象。

## C++ 实现

### 手动字符串驻留

```cpp
typedef uint32_t key;
struct User {
    User(const string& first_name, const string& last_name)
        : first_name{add(first_name)}, last_name{add(last_name)} {}
protected:
    key first_name, last_name;
    static bimap<key, string> names;
    static key seed;
    static key add(const string& s) {
        auto it = names.right.find(s);
        if (it == names.right.end())
            return names.insert({++seed, s}), seed;
        return it->second;
    }
};
```

### Boost.Flyweight

```cpp
struct User2 {
    flyweight<string> first_name, last_name;
    User2(const string& f, const string& l) : first_name{f}, last_name{l} {}
};
// "Doe" 字符串在所有 User2 实例间共享
```

### 格式化文本区间

```cpp
class BetterFormattedText {
public:
    struct TextRange { int start, end; bool capitalize; };
    TextRange& get_range(int start, int end) {
        formatting.emplace_back(TextRange{start, end});
        return *formatting.rbegin();
    }
private:
    string plain_text;
    vector<TextRange> formatting;  // 享元集合
};
```

## 关键点

- 内部状态（可共享）vs 外部状态（上下文相关）
- `string_view` / `boost::flyweight` 是现代 C++ 的享元实践
- 区间覆盖允许重叠，适合文本格式化场景

## 相关模式

- [[composite-pattern]]
- [[state-pattern]]
