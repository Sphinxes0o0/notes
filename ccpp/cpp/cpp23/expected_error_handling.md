---
title: C++23 std::expected 错误处理最佳实践
date: 2026-06-04 09:00:00
tags:
    - cpp
    - cpp23
    - error-handling
    - expected
    - monad
---

# C++23 `std::expected` 错误处理最佳实践

## 1. 背景：C++ 错误处理的演进

### 1.1 三种主要范式

C++ 在过去三十年里形成了三种主要的错误处理范式，每一种都有其历史合理性与现实局限：

**1. 错误码 (errno / return code)**

这是 C 语言的遗产。函数通过返回值或输出参数报告错误，调用方显式检查。优点是**控制流显式、零开销、跨语言兼容**；缺点是容易被忽略，错误信息贫乏，传播链冗长。

```cpp
// C 风格
if (FILE* fp = fopen("data.txt", "r")) {
    // ... 处理文件
    fclose(fp);
} else {
    fprintf(stderr, "fopen failed: %s\n", strerror(errno));
}
```

**2. 异常 (exceptions)**

C++98 引入的 `try` / `throw` / `catch` 机制，目的是**把正常路径与错误路径在源代码上分离开来**。异常的优点是错误可以"自动"沿着调用栈向上传播，错误信息（异常对象）可以携带任意丰富的数据。其缺点同样显著：

- 抛异常的开销在某些实现下并非真正的 zero-cost（编译器无法内联含 `try` 的函数）；
- 控制流隐式，源代码阅读时无法一眼看清"哪里可能出错"；
- 在嵌入式、实时系统、跨 DLL/共享库边界等场景下，异常机制要么不可用，要么语义模糊；
- RAII 析构中不应再抛异常，否则直接 `std::terminate`。

**3. `std::optional<T>` (C++17)**

`std::optional` 表达"可能有值、可能无值"的二态语义，被许多人用作"轻量级错误处理"。其致命缺陷是**无值时无法携带错误信息**——调用方只知道"出错了"，但不知道为什么错，怎么修。

**4. `std::expected<T, E>` (C++23)**

C++23 正式纳入的 `std::expected<T, E>` (P0323R12) 弥补了 `optional` 的缺陷：除了"成功值"之外，还可以携带任意类型的"错误值"。这使得 C++ 终于拥有了一个**类型安全、可组合、显式控制流、零开销**的错误处理原语，与 Rust 的 `Result<T, E>` 几乎一一对应。

### 1.2 与 Rust `Result` 的血缘

P0323 的设计深受 Rust `Result<T, E>` 的影响。事实上，Rust 标准库的 `Result` 与 C++ 的 `std::expected` 在语义、API 形态、单子 (monadic) 操作链上几乎完全同构。差异仅在：

- Rust 用 `Ok` / `Err` 枚举变体名，C++ 用 `value` / `unexpected`；
- Rust 借助 `?` 运算符做语法级错误传播，C++23 仍未标准化 `?` (P0798R4 仍在演进)；
- Rust 的 `Result` 是 `enum`，C++ 的 `expected` 是 class template。

理解这一点对于已经熟悉 Rust 的开发者尤其重要——可以直接把 Rust 的错误处理心智模型平移到 C++。

---

## 2. `std::expected<T, E>` API 全景

`std::expected` 定义在头文件 `<expected>` 中 (C++23)，命名空间 `std`。其核心类型与操作如下。

### 2.1 核心类型

```cpp
namespace std {
    // 主模板：T = 成功值类型，E = 错误类型
    template<class T, class E>
    class expected;

    // void 特化：仅承载错误
    template<class E>
    class expected<void, E>;

    // 标记类型：用于原地构造 unexpected
    struct unexpect_t { explicit unexpect_t() = default; };
    inline constexpr unexpect_t unexpect{};

    // 错误包装器
    template<class E>
    class unexpected;

    // 错误类型不抛异常的 bad_expected_access
    template<class E>
    class bad_expected_access;
}
```

构造方式：

```cpp
std::expected<int, std::errc> a = 42;                  // 成功
std::expected<int, std::errc> b = std::unexpected{std::errc::invalid_argument};
std::expected<int, std::errc> c{std::in_place, 42};    // 原地构造 T
std::expected<std::string, MyError> d{std::unexpect, MyError{"I/O"}};
```

### 2.2 观察器 (observers)

```cpp
T& value() &;             // 持有 expected 时取 T（若无值则抛 bad_expected_access）
T&& value() &&;
const T& value() const&;
E& error() &;             // 取错误（若无错误则 UB）
bool has_value() const noexcept;
explicit operator bool() const noexcept;  // 等价于 has_value()
T value_or(U&& fallback) const&;          // 无值时返回 fallback
```

### 2.3 单子操作 (monadic operations)

C++23 还引入了一组**单子风格的链式操作** (P2505, P2249)，允许在不拆开 `expected` 的前提下做映射、错误传播、错误转换：

```cpp
// 对成功值做映射（不进入错误分支时直接透传）
template<class F> auto and_then(F&& f) &;       // f(T) -> expected<U, E>
template<class F> auto transform(F&& f) &;      // f(T) -> U
template<class F> auto or_else(F&& f) &;        // f(E) -> expected<T, F_error>
template<class F> auto transform_error(F&& f) &;// f(E) -> F_error
```

这些操作是 `std::expected` 真正"现代化"的关键——它们使得错误处理可以像数据流一样被组合。

### 2.4 最小可运行示例

```cpp
// 编译：g++ -std=c++23 -O2 expected_demo.cpp
#include <expected>
#include <iostream>
#include <string>

enum class ParseError { Empty, InvalidNumber, OutOfRange };

std::expected<int, ParseError> parse_int(std::string_view s) {
    if (s.empty()) return std::unexpected{ParseError::Empty};
    int v = 0;
    for (char c : s) {
        if (c < '0' || c > '9') return std::unexpected{ParseError::InvalidNumber};
        v = v * 10 + (c - '0');
    }
    return v;
}

int main() {
    auto r = parse_int("123")
        .transform([](int x){ return x * 2; })
        .and_then([](int x) -> std::expected<int, ParseError> {
            if (x > 1000) return std::unexpected{ParseError::OutOfRange};
            return x;
        });

    if (r) std::cout << "ok: " << r.value() << "\n";
    else   std::cout << "err code: " << static_cast<int>(r.error()) << "\n";
}
```

---

## 3. 错误处理策略对比

### 3.1 `std::expected` vs `std::optional`

| 维度 | `std::optional<T>` | `std::expected<T, E>` |
|------|-------------------|----------------------|
| 状态 | `disengaged` / `engaged` | `value` / `unexpected` |
| 错误信息 | 无 | 任意类型 `E` |
| 典型场景 | "找不到元素" | "操作失败的根因" |
| 错误传播链 | 丢失 | 可保留 |
| 体积 | 略小 (bool + T) | 略大 (bool + 变体) |

**结论**：如果你需要让调用方知道"**为什么**失败"，就用 `expected`；如果仅仅是"有没有"的二态，optional 仍更轻量。

### 3.2 `std::expected` vs exceptions

| 维度 | `std::expected` | exceptions |
|------|-----------------|-----------|
| 控制流 | 显式（返回值） | 隐式（栈展开） |
| 性能 | 成功路径 zero-overhead | 部分实现下 try-frame 有开销 |
| 错误携带 | 任意类型 `E` | 任意类型异常对象 |
| 忽略难度 | 难忽略（必须检查返回值） | 极易忽略（可省略 catch） |
| 跨 ABI | 安全 | 跨 DLL 边界有 type_identity 问题 |
| 嵌入/实时 | 友好 | 受限 |

**结论**：在性能敏感、错误必须显式处理、跨 ABI、嵌入式等场景，`expected` 是更优选择；在业务逻辑深层层层透传、错误是"异常情况"的场景，exception 仍然合理。

### 3.3 `std::expected` vs Rust `Result<T, E>`

| 维度 | C++ `std::expected` | Rust `Result<T, E>` |
|------|---------------------|---------------------|
| 状态标签 | `has_value()` | `is_ok()` / `is_err()` |
| 错误包装 | `std::unexpected<E>{e}` | `Err(e)` |
| 取值 | `.value()` / `.error()` | `.unwrap()` / `.unwrap_err()` / `?` |
| 单子操作 | `and_then` / `or_else` / `transform` / `transform_error` | `.and_then` / `.or_else` / `.map` / `.map_err` |
| 语法糖 | 无（草案 P0798 提议 `?`） | `?` 运算符 |
| 语言层 panic | 无 | `panic!` / `.unwrap()` |

**结论**：两者语义一一对应，迁移成本几乎为零，唯一显著差距是 C++23 暂未提供 `?` 语法糖。

---

## 4. 实践模式

### 4.1 返回类型别名

在大型项目中，重复书写 `std::expected<T, MyError>` 既冗长又难读。**惯例是为每个模块定义 `Result` 类型别名**：

```cpp
namespace fs {
    enum class Error { NotFound, PermissionDenied, IoError, InvalidPath };

    template<class T>
    using Result = std::expected<T, Error>;

    Result<std::string> read_file(std::filesystem::path p);
    Result<void>        write_file(std::filesystem::path p, std::string_view s);
}
```

调用方代码：

```cpp
auto content = fs::read_file("/etc/hostname");
if (!content) {
    switch (content.error()) {
        case fs::Error::NotFound: /* ... */ break;
        case fs::Error::PermissionDenied: /* ... */ break;
        default: /* ... */
    }
}
```

### 4.2 错误类型选择：错误枚举 vs `std::error_code`

两种主流风格：

**风格 A：模块级 `enum class` + `Result<T>` 别名**

- 优点：零开销、ABI 友好、错误集合是闭合的（编译器能穷尽警告）；
- 缺点：缺乏可扩展性，跨模块错误聚合需要转换层。

**风格 B：`std::error_code` (来自 `<system_error>`)**

- 优点：与 POSIX/操作系统错误天然映射，可扩展（任意 domain），与 `std::system_error` 互操作；
- 缺点：分配堆上 `error_category` 单例，首次使用有冷启动开销；体积比 enum 大。

**经验法则**：

- **库内部** 用风格 A 更快、更干净；
- **模块边界 / 系统集成层** 用风格 B 便于与 POSIX 错误互通；
- 在 C++23 项目里可以**两者并存**——内部 API 用 enum 风格的 `Result<T, MyError>`，对外的 `to_error_code()` 接口暴露 `std::error_code`。

### 4.3 错误传播：`?` 的现状与替代品

Rust 开发者最爱的 `?` 运算符——"如果出错就立刻返回，否则解包"——在 C++23 中**仍未进入标准**。提案 P0798R4 ("Monadic operations for `std::expected`") 仍在演进。

在没有 `?` 的情况下，社区有三种替代方案：

**(a) 宏**：模仿 Rust `?` 的 `TRY(expr)` / `EVAL(expr)` 宏：

```cpp
#define TRY(expr) \
    ({ auto&& _r = (expr); \
       if (!_r) return std::unexpected{_r.error()}; \
       std::move(*_r); })
```

**(b) 显式 `if` 链**：

```cpp
auto a = step1();
if (!a) return std::unexpected{a.error()};
auto b = step2(*a);
if (!b) return std::unexpected{b.error()};
return step3(*b);
```

**(c) 协程 + 等待器** (C++20 起的 `co_await` 可实现 `?` 语义，但需要引入协程)。

**建议**：在团队代码里统一一种风格。宏最简洁但有 hygiene 问题；显式 `if` 最清晰，是 P0798 落地前的**最佳实践**。

---

## 5. 完整例子

### 5.1 文件读取：链式 `and_then`

```cpp
// 文件：file_read.cpp
// 编译：g++ -std=c++23 -O2 file_read.cpp
#include <cstdio>
#include <cstring>
#include <expected>
#include <filesystem>
#include <string>
#include <string_view>

namespace fs = std::filesystem;

enum class FileError {
    NotFound,
    PermissionDenied,
    ReadError,
    Empty
};

template<class T>
using Result = std::expected<T, FileError>;

namespace detail {
    inline FileError from_errno() {
        switch (errno) {
            case ENOENT: return FileError::NotFound;
            case EACCES: return FileError::PermissionDenied;
            default:     return FileError::ReadError;
        }
    }
}

// 步骤 1：按路径打开文件
Result<std::FILE*> open_file(const fs::path& p) {
    std::FILE* fp = std::fopen(p.c_str(), "rb");
    if (!fp) return std::unexpected{detail::from_errno()};
    return fp;
}

// 步骤 2：读全文
Result<std::string> read_all(std::FILE* fp) {
    std::string out;
    char buf[4096];
    for (;;) {
        std::size_t n = std::fread(buf, 1, sizeof(buf), fp);
        if (n) out.append(buf, n);
        if (n < sizeof(buf)) {
            if (std::ferror(fp)) return std::unexpected{FileError::ReadError};
            break;
        }
    }
    return out;
}

// 步骤 3：trim 空白
Result<std::string> trim(Result<std::string> in) {
    if (!in) return in;
    auto& s = *in;
    auto not_space = [](unsigned char c){ return !std::isspace(c); };
    auto beg = std::find_if(s.begin(), s.end(), not_space);
    auto end = std::find_if(s.rbegin(), s.rend(), not_space).base();
    if (beg >= end) return std::unexpected{FileError::Empty};
    return std::string(beg, end);
}

// 组合：单子链
Result<std::string> load_trimmed(const fs::path& p) {
    return open_file(p)
        .and_then([](std::FILE* fp) -> Result<std::string> {
            // RAII 关闭
            auto close = [](std::FILE* f){ std::fclose(f); };
            std::unique_ptr<std::FILE, decltype(close)> guard(fp, close);
            return read_all(fp).transform([&](std::string s){
                // 读完后由 guard 关闭
                return s;
            });
        })
        .and_then(trim);
}

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s <file>\n", argv[0]); return 1; }

    auto content = load_trimmed(argv[1]);
    if (!content) {
        std::fprintf(stderr, "failed: code=%d\n", static_cast<int>(content.error()));
        return 1;
    }
    std::printf("size=%zu\n", content->size());
    return 0;
}
```

### 5.2 JSON parser：多层 `expected` 组合

下面给出一个完整可编译的迷你 JSON 解析器骨架（覆盖 `null` / `bool` / `number` / `string` / `array` / `object`），重点展示 `expected` 在多层级语法分析中的**错误传播链**：

```cpp
// 文件：mini_json.cpp
// 编译：g++ -std=c++23 -O2 mini_json.cpp
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <expected>
#include <map>
#include <memory>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

// ---------- 错误类型 ----------
enum class JsonError {
    UnexpectedEof,
    InvalidNumber,
    InvalidString,
    InvalidLiteral,   // null / true / false
    InvalidToken,
    ExpectedColon,
    ExpectedComma,
    ExpectedKey,
    TrailingData,
    NestingTooDeep,
};

// ---------- 错误位置 ----------
struct JsonErrorInfo {
    JsonError kind;
    std::size_t pos;
    std::string detail;
};

// ---------- JSON 值 ----------
struct JsonValue;
using JsonObject = std::map<std::string, std::unique_ptr<JsonValue>>;
using JsonArray  = std::vector<std::unique_ptr<JsonValue>>;

struct JsonValue {
    enum class Type { Null, Bool, Number, String, Array, Object } type = Type::Null;
    bool        b = false;
    double      n = 0.0;
    std::string s;
    JsonArray   a;
    JsonObject  o;

    static std::unique_ptr<JsonValue> make(Type t) {
        auto v = std::make_unique<JsonValue>();
        v->type = t;
        return v;
    }
};

template<class T>
using Result = std::expected<T, JsonErrorInfo>;

inline Result<std::unique_ptr<JsonValue>> fail(JsonError k, std::size_t pos,
                                              std::string d = "") {
    return std::unexpected{JsonErrorInfo{k, pos, std::move(d)}};
}

// ---------- 词法器 ----------
struct Lexer {
    std::string_view src;
    std::size_t      pos = 0;

    explicit Lexer(std::string_view s) : src(s) {}

    bool eof() const { return pos >= src.size(); }
    char peek() const { return src[pos]; }
    char get()       { return src[pos++]; }

    void skip_ws() {
        while (!eof() && (peek() == ' ' || peek() == '\t' ||
                          peek() == '\n' || peek() == '\r')) {
            ++pos;
        }
    }

    // 字面量：null / true / false
    Result<std::string> literal() {
        std::size_t start = pos;
        while (!eof() && std::isalpha(static_cast<unsigned char>(peek()))) ++pos;
        std::string word(src.substr(start, pos - start));
        if (word == "null" || word == "true" || word == "false") return word;
        return fail(JsonError::InvalidLiteral, start, word);
    }

    // 字符串："..."
    Result<std::string> parse_string() {
        if (eof() || get() != '"') return fail(JsonError::InvalidToken, pos, "expected '\"'");
        std::string out;
        while (!eof() && peek() != '"') {
            char c = get();
            if (c == '\\') {
                if (eof()) return fail(JsonError::UnexpectedEof, pos);
                char e = get();
                switch (e) {
                    case '"':  out += '"';  break;
                    case '\\': out += '\\'; break;
                    case '/':  out += '/';  break;
                    case 'n':  out += '\n'; break;
                    case 't':  out += '\t'; break;
                    case 'r':  out += '\r'; break;
                    default:   return fail(JsonError::InvalidString, pos,
                                           std::string("bad escape: \\") + e);
                }
            } else {
                out += c;
            }
        }
        if (eof()) return fail(JsonError::UnexpectedEof, pos);
        get(); // consume closing "
        return out;
    }

    // 数字
    Result<double> parse_number() {
        std::size_t start = pos;
        if (!eof() && peek() == '-') ++pos;
        while (!eof() && std::isdigit(static_cast<unsigned char>(peek()))) ++pos;
        if (!eof() && peek() == '.') {
            ++pos;
            while (!eof() && std::isdigit(static_cast<unsigned char>(peek()))) ++pos;
        }
        if (!eof() && (peek() == 'e' || peek() == 'E')) {
            ++pos;
            if (!eof() && (peek() == '+' || peek() == '-')) ++pos;
            while (!eof() && std::isdigit(static_cast<unsigned char>(peek()))) ++pos;
        }
        std::string sub(src.substr(start, pos - start));
        if (sub.empty() || sub == "-") return fail(JsonError::InvalidNumber, start, sub);
        char* endp = nullptr;
        double v = std::strtod(sub.c_str(), &endp);
        if (endp != sub.c_str() + sub.size()) {
            return fail(JsonError::InvalidNumber, start, sub);
        }
        return v;
    }
};

// ---------- 解析器 ----------
struct Parser {
    Lexer lex;
    int   depth = 0;
    static constexpr int kMaxDepth = 64;

    explicit Parser(std::string_view s) : lex(s) {}

    Result<std::unique_ptr<JsonValue>> parse_value() {
        if (++depth > kMaxDepth) return fail(JsonError::NestingTooDeep, lex.pos);
        auto result = parse_value_impl();
        --depth;
        return result;
    }

    Result<std::unique_ptr<JsonValue>> parse_value_impl() {
        lex.skip_ws();
        if (lex.eof()) return fail(JsonError::UnexpectedEof, lex.pos);
        char c = lex.peek();
        if (c == '{') return parse_object();
        if (c == '[') return parse_array();
        if (c == '"') {
            auto s = lex.parse_string();
            if (!s) return std::unexpected{s.error()};
            auto v = JsonValue::make(JsonValue::Type::String);
            v->s = std::move(*s);
            return v;
        }
        if (c == '-' || std::isdigit(static_cast<unsigned char>(c))) {
            auto n = lex.parse_number();
            if (!n) return std::unexpected{n.error()};
            auto v = JsonValue::make(JsonValue::Type::Number);
            v->n = *n;
            return v;
        }
        auto lit = lex.literal();
        if (!lit) return std::unexpected{lit.error()};
        auto v = JsonValue::make(JsonValue::Type::Null);
        if (*lit == "true")  { v->type = JsonValue::Type::Bool; v->b = true;  }
        else if (*lit == "false") { v->type = JsonValue::Type::Bool; v->b = false; }
        else if (*lit == "null")  { /* stay null */ }
        else return fail(JsonError::InvalidLiteral, lex.pos, *lit);
        return v;
    }

    Result<std::unique_ptr<JsonValue>> parse_array() {
        std::size_t start = lex.pos;
        lex.get(); // [
        auto v = JsonValue::make(JsonValue::Type::Array);
        lex.skip_ws();
        if (!lex.eof() && lex.peek() == ']') { lex.get(); return v; }
        for (;;) {
            auto elem = parse_value();
            if (!elem) return std::unexpected{elem.error()};
            v->a.push_back(std::move(*elem));
            lex.skip_ws();
            if (lex.eof()) return fail(JsonError::UnexpectedEof, lex.pos);
            char c = lex.get();
            if (c == ',') continue;
            if (c == ']') return v;
            return fail(JsonError::ExpectedComma, lex.pos, std::string(1, c));
        }
    }

    Result<std::unique_ptr<JsonValue>> parse_object() {
        std::size_t start = lex.pos;
        lex.get(); // {
        auto v = JsonValue::make(JsonValue::Type::Object);
        lex.skip_ws();
        if (!lex.eof() && lex.peek() == '}') { lex.get(); return v; }
        for (;;) {
            lex.skip_ws();
            if (lex.eof()) return fail(JsonError::UnexpectedEof, lex.pos);
            if (lex.peek() != '"') return fail(JsonError::ExpectedKey, lex.pos);
            auto k = lex.parse_string();
            if (!k) return std::unexpected{k.error()};
            lex.skip_ws();
            if (lex.eof() || lex.get() != ':') return fail(JsonError::ExpectedColon, lex.pos);
            auto val = parse_value();
            if (!val) return std::unexpected{val.error()};
            v->o.emplace(std::move(*k), std::move(*val));
            lex.skip_ws();
            if (lex.eof()) return fail(JsonError::UnexpectedEof, lex.pos);
            char c = lex.get();
            if (c == ',') continue;
            if (c == '}') return v;
            return fail(JsonError::ExpectedComma, lex.pos, std::string(1, c));
        }
    }
};

// ---------- 顶层入口 ----------
Result<std::unique_ptr<JsonValue>> parse(std::string_view src) {
    Parser p(src);
    auto v = p.parse_value();
    if (!v) return v;
    p.lex.skip_ws();
    if (!p.lex.eof()) return fail(JsonError::TrailingData, p.lex.pos);
    return v;
}

// ---------- 演示 ----------
static void print_value(const JsonValue& v, int indent = 0) {
    auto pad = [&]{ for (int i=0;i<indent;i++) std::putchar(' '); };
    switch (v.type) {
        case JsonValue::Type::Null:   std::printf("null"); break;
        case JsonValue::Type::Bool:   std::printf(v.b ? "true" : "false"); break;
        case JsonValue::Type::Number: std::printf("%g", v.n); break;
        case JsonValue::Type::String: std::printf("\"%s\"", v.s.c_str()); break;
        case JsonValue::Type::Array:
            std::printf("[\n");
            for (std::size_t i = 0; i < v.a.size(); ++i) {
                pad(); std::printf("  ");
                print_value(*v.a[i], indent + 2);
                if (i + 1 < v.a.size()) std::printf(",");
                std::printf("\n");
            }
            pad(); std::printf("]");
            break;
        case JsonValue::Type::Object:
            std::printf("{\n");
            std::size_t i = 0;
            for (auto& [k, val] : v.o) {
                pad(); std::printf("  \"%s\": ", k.c_str());
                print_value(*val, indent + 2);
                if (++i < v.o.size()) std::printf(",");
                std::printf("\n");
            }
            pad(); std::printf("}");
            break;
    }
}

int main() {
    const char* src = R"({
        "name": "demo",
        "version": 1.0,
        "tags": ["a","b","c"],
        "flags": { "experimental": true, "items": null }
    })";

    auto r = parse(src);
    if (!r) {
        std::fprintf(stderr, "parse error: kind=%d pos=%zu detail=\"%s\"\n",
                     static_cast<int>(r.error().kind), r.error().pos,
                     r.error().detail.c_str());
        return 1;
    }
    print_value(**r);
    std::printf("\n");
    return 0;
}
```

这个例子覆盖了**典型的 `expected` 实战用法**：

- 每个底层函数返回 `Result<T, JsonErrorInfo>`，错误携带**位置 + 详细描述**；
- `parse_object` / `parse_array` 在循环里通过 `if (!...) return std::unexpected{...}` **手动传播**；
- 顶层 `parse()` 集中处理"尾部多余数据"等"上下文相关"的错误。

它演示了一个关键事实：在没有 `?` 语法糖的 C++23 里，**显式 `if` 检查是标准做法**，应当让团队代码风格保持一致。

---

## 6. 性能

### 6.1 成功路径的 zero-overhead

`std::expected<T, E>` 在 ABI 上通常被实现为：

```cpp
union { T value; E error; };
bool has_value;
```

编译器看到 `if (r.has_value()) use(r.value);` 时：

- `has_value` 的检查被规约为一个 `bool` 加载 + 一次条件跳转；
- 在**预测正确**的情况下，开销与裸 `T` 几乎相同（特别是开启 `-O2` / `-O3` 后）；
- 错误路径若从未被触发，**整个错误构造、`unexpected` 包装都不会被实例化**——C++ 模板 + 死代码消除 (DCE) 保证这一点。

### 6.2 错误路径

错误路径的代价等于"构造 `E` + 包装成 `unexpected` + 沿调用链返回"。如果 `E` 是简单的 enum 或 error_code，**单次传播的开销通常在数纳秒级**，与异常抛出（数十到数百纳秒 + 栈展开）相比要快一个数量级，且**不会触碰任何全局表、RTTI 或 unwind 表**。

### 6.3 与异常的对比基准

多项基准 (e.g. Sy Brand, 2023) 表明：

- 成功路径：expected ≈ 直接返回；exception 有少量 try-frame 开销；
- 错误路径：expected 比 exception 快 5–50×；
- 错误罕见时，exception 的 try-frame 开销摊薄后可忽略。

**经验**：热路径（每秒百万次调用）必须用 `expected`；冷路径（用户错误、初始化失败）用 exception 也不丢人。

### 6.4 体积

`std::expected<T, E>` 的大小 = `sizeof(T)` + `sizeof(E)` + padding + 1 byte (has_value flag)。当 `T` 与 `E` 都有非平凡对齐要求时，编译器可能插入 padding。设计上**优先让 `T` 大、`E` 小**（如 `E` 是 enum 或 error_code），可以让 padding 最小化。

---

## 7. 编译器支持现状

| 编译器 | 最低版本 | 头文件 | 备注 |
|--------|---------|--------|------|
| GCC    | 12      | `<expected>` (libstdc++) | 早期版本有 bug，建议 13+ |
| Clang  | 16 (libc++) 17+ (推荐) | `<expected>` (libc++) | libc++ 16 起可用，17 修复若干缺陷 |
| MSVC   | 19.36 / Visual Studio 2022 17.6 | `<expected>` (MSVC STL) | 早期版本有 `transform` 误编译 |
| libc++ | 16+ | 同上 | 缺若干单子操作直到 17 |
| libstdc++ | 13+ | 同上 | 最完整实现 |

**建议**：

- **生产代码**用 GCC 13 / Clang 17 / MSVC 17.8+，以获得完整的 monadic operations。
- **CI 矩阵**至少覆盖两个编译器，确保 ABI 行为一致。
- 如果要在 GCC 12 上构建，需要包含 `<expected>` 并确认 `<concepts>` 与 `<utility>` 已可用——大多数发行版 toolchain 已经满足。

---

## 8. 与 `std::error_code` / `std::system_error` 的关系

`std::error_code` 是 C++11 引入的"通用错误码 + 域"机制；`std::system_error` 是其异常化形式。`std::expected` 与它们的**关系是互补**：

- **承载关系**：`std::expected<T, std::error_code>` 是一种惯用搭配，让 `T` 表示成功载荷，`std::error_code` 携带可扩展的错误信息（含 POSIX 码、用户自定义 category）。
- **桥接**：`std::error_code` 内部通过 `error_category` 单例实现，跨模块错误聚合时可以用 `std::error_code` 包装模块内 enum：

```cpp
enum class FsError { NotFound, PermissionDenied, Io };

struct FsErrorCategory : std::error_category {
    const char* name() const noexcept override { return "fs"; }
    std::string message(int ev) const override {
        switch (static_cast<FsError>(ev)) {
            case FsError::NotFound:          return "not found";
            case FsError::PermissionDenied:  return "permission denied";
            case FsError::Io:                return "I/O error";
        }
        return "unknown";
    }
};
inline const std::error_category& fs_category() {
    static FsErrorCategory c; return c;
}
inline std::error_code make_ec(FsError e) {
    return {static_cast<int>(e), fs_category()};
}

// 库内仍用 enum，对外暴露 expected<T, std::error_code>
std::expected<std::string, std::error_code>
read_file(const fs::path& p) {
    std::FILE* fp = std::fopen(p.c_str(), "rb");
    if (!fp) return std::unexpected{make_ec(FsError::NotFound)};
    // ...
}
```

- **互操作**：若上层仍用 `std::system_error` 抛异常，**在 `expected` → `exception` 的边界**写一个 `throw_on_error(expected)` 适配器即可：

```cpp
template<class T>
T&& throw_on_error(std::expected<T, std::error_code>&& e) {
    if (!e) throw std::system_error{e.error()};
    return std::move(*e);
}
```

---

## 9. 实践守则 (Checklist)

1. **为每个模块定义 `using Result = std::expected<T, Error>;`**——可读性 > 节省字符。
2. **优先用 enum 风格错误类型**，跨边界再转 `std::error_code`。
3. **不要把 `expected` 当 `optional` 用**——后者只表达二态。
4. **不要在析构中 `return unexpected{...}`**——析构应 noexcept，改用哨兵值或吞掉错误。
5. **错误类型应是可默认构造 + 可比较 + 平凡的**——避免 `expected` 内嵌复杂 RAII 资源。
6. **避免 `expected<T, expected<U, E>>`**——会破坏单子链，改用 `flatten`-风格的包装。
7. **大规模项目考虑实现 `TRY` 宏**——但要**配合同事评审**避免宏滥用。
8. **CI 必须包含 `expected` 编译用例**——编译器对 monadic operations 的支持仍参差不齐。
9. **文档化错误集合**——枚举风格最大的坑是"调用方漏 switch 漏 case"，靠 `-Wswitch` 与单元测试补齐。
10. **不要 `std::move(*r.value())` 之后还访问 `r`**——和 `optional` 一样，`expected` 也遵循 move-out 后 valid-but-unspecified 规则。

---

## 10. 参考文献

1. **P0323R12 — `std::expected` proposal**, Vicente Botet, JF Bastien, Jonathan Wakely, 2022. <https://wg21.link/p0323r12>
2. **cppreference — `std::expected`**. <https://en.cppreference.com/w/cpp/utility/expected>
3. **Sy Brand — "Expected: Past, Present and Future"** (2023). <https://blog.tartanllama.xyz/expected/>
4. **C++23 Standard Draft N4910**. <https://wg21.link/n4910>
5. **Andrei Alexandrescu — "Error Handling in C++"** (C++ and Beyond 2012, 历史背景). <https://channel9.msdn.com/Shows/C9-GoingNative/Andrei-Alexandrescu-Error-Handling-in-C>
6. **P0798R4 — Monadic operations for `std::expected`** (Larry Evans 等, `?` 提案). <https://wg21.link/p0798r4>
7. **P2505R5 — Monadic operations for `std::expected`**. <https://wg21.link/p2505r5>
