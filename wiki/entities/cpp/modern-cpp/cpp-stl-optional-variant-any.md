---
type: entity
tags: [cpp17, cpp20, cpp23, optional, variant, any, type-safe-union]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ std::variant, std::optional, std::any

## Definition

Three type-safe union/optional wrappers introduced in C++17:
- `std::variant<T, U, ...>` — type-safe union (exactly one active)
- `std::optional<T>` — may-or-may-not-have-a-value
- `std::any` — type-erased single value of any type

## Key Concepts

### std::variant (C++17)

Type-safe union — **always** holds a value (or is valueless via `std::monostate`):

```c++
std::variant<int, double, std::string> v{12};
std::get<int>(v);     // 12
v = 3.14;
std::get<double>(v);  // 3.14

// Visitor pattern
std::visit([](auto&& arg) {
  std::cout << arg << "\n";
}, v);

// Check active type
if (std::holds_alternative<int>(v)) { /* ... */ }

// Index of active type
v.index();  // which alternative is active
```

`std::variant` is **valueless** if assignment throws (rare — only if copy/move throws during variant manipulation).

### std::optional (C++17)

Represents optional value — may be empty (`std::nullopt`):

```c++
std::optional<std::string> create(bool b) {
  if (b) return "Godzilla";
  return {};  // or std::nullopt
}

create(false).value_or("empty");  // "empty"
create(true).value();              // "Godzilla"

// Factory pattern
if (auto str = create(true)) {
  // str is in-scope only if value present
}
```

### std::optional Monadic Operations (C++23)

Chain operations without explicit checks:

```c++
std::optional<int> parse_int(const std::string&);
std::optional<int> ensure_non_negative(int);

std::optional<double> stringToSqrtDouble(const std::string& input) {
  return parse_int(input)
    .and_then(ensure_non_negative)          // chain if present
    .transform([](int x) { return std::sqrt(x); })  // transform value
    .or_else([] { return std::optional<double>{0.0}; });  // fallback
}
```

### std::any (C++17)

Type-erased container for any single value:

```c++
std::any x{5};
x.has_value();                          // true
std::any_cast<int>(x);                  // 5
std::any_cast<int&>(x) = 10;            // modify in place
std::any_cast<int>(x);                  // 10
```

Requires `type()` to retrieve — slower than variant.

### std::expected (C++23)

Represents a value or an error — monadic alternative to exceptions:

```c++
enum class Error { ParseError, NegativeNumber };

std::expected<int, Error> parse_int(const std::string&);

std::expected<double, Error> sqrt_double(const std::string& input) {
  auto parsed = parse_int(input);
  if (!parsed) return std::unexpected(parsed.error());

  if (*parsed < 0) return std::unexpected(Error::NegativeNumber);
  return std::sqrt(static_cast<double>(*parsed));
}
```

### Comparison

| Feature | variant | optional | any | expected |
|---------|---------|----------|-----|----------|
| Type safety | Yes (bounded set) | Yes (one type) | Type-erased | Yes |
| Memory | Inline (largest type) | Inline + bool | Heap if large | Inline |
| Performance | Fast (no heap) | Fast | Slower | Fast |
| Use case | Known alternatives | Nullable single type | Unknown type | Result with error |
| Empty state | std::monostate | std::nullopt | has_value() | std::unexpected |

## Related Concepts

- [[cpp-type-traits]] — type checking with std::variant
- [[cpp-stl-functional]] — std::visit for variants
- [[cpp-constexpr]] — optional and variant in constexpr contexts
