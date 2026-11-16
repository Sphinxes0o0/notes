---
type: entity
tags: [cpp, stl, string]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL String

## 定义

`std::string` 是 STL 提供的字符串容器，实现了对字符序列的存储、访问和操作。作为一种特殊的容器，string 兼具容器的特性和字符串专用接口。

## 关键要点

### string 实现差异

**GCC (libstdc++)**: SSO (Small String Optimization)，通常 15 字符内存储在对象内部
**MSVC**: SSO，255 字符内存储在对象内部
**COW (Copy-On-Write)**: 旧版 GCC 使用，现已废弃（线程不安全）

```cpp
// 现代实现通常是 SSO + 堆分配混合
// 短字符串直接存储在对象内部，无堆分配
// 超过阈值后堆分配存储
```

### string vs vector

| 方面 | string | vector |
|------|--------|--------|
| 元素类型 | char | 任意类型 |
| 专用接口 | substr, find_first_of, etc. | 无 |
| 字符编码 | 字节或 char16_t/char32_t | 任意类型 |
| 字面量 | "..." | {1, 2, 3} |

### 高效操作原则

```cpp
// 1. 用 reserve 预分配避免多次分配
std::string s;
s.reserve(1000);
for (int i = 0; i < 1000; ++i) {
    s += 'a';  // 无需每次重新分配
}

// 2. 用 operator+= 或 append 而非 + 拼接
s += "hello";           // 高效
s.append("hello");      // 高效
s = s + "hello";        // 低效：创建临时对象

// 3. 用 string_view (C++17) 避免不必要的拷贝
void process(std::string_view sv);  // 不拷贝
std::string s = "hello";
process(s);  // 无拷贝
```

### C++11 新增接口

```cpp
std::string s = "Hello World";

// 搜索
s.find("World");                    // 找子串
s.find_first_of("aeiou");          // 找任一元音
s.find_last_of(".txt");             // 找最后一个指定字符

// 数值转换
std::stoi("42");                    // string to int
std::stod("3.14");                  // string to double
std::to_string(42);                 // int to string

// 修改
s.erase(std::remove_if(s.begin(), s.end(),
    [](char c){ return std::isspace(c); }), s.end());
s.insert(5, "C++ ");

// 子串
std::string_view sv(s.c_str() + 6, 5);  // "World"
```

### string 与数值转换

```cpp
// 高效方式
std::ostringstream oss;
oss << 42 << " " << 3.14;
std::string s = oss.str();

// C++11 方式
std::to_string(42);
std::stoi("42");
std::stod("3.14");

// 数值到 string_view (C++17)
std::string num = "42";
int i = std::stoi(num);  // 无需临时 string
```

## Effective STL 要点 (Items 41-43)

- Item 41: 理解 string 的实现差异
- Item 42: 用 string_view 代替 const string& 当无需拥有数据
- Item 43: 用字符处理函数而非算法处理单个字符

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — string 是特殊容器
- [[entities/cpp/cpp-stl-algorithms]] — 字符串算法
- [[entities/cpp/cpp-stl-iterators]] — 字符串迭代器
- [[entities/cpp/cpp-stl-allocators]] — string 使用分配器管理内存
- [[entities/cpp/cpp20-features]] — C++20 增加了 constexpr string 和 starts_with/ends_with
