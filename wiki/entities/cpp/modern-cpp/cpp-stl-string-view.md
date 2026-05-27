---
type: entity
tags: [cpp17, cpp20, string, string_view, non-owning, substring]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ std::string_view & String Utilities

## Definition

`std::string_view` (C++17) is a **non-owning** reference to a string (or substring). Provides string operations without allocation. `starts_with`/`ends_with` added in C++20.

## Key Concepts

### std::string_view (C++17)

Non-owning view — cheap to construct and copy:

```c++
std::string_view cppstr{"foo"};
std::wstring_view wcstr_v{L"baz"};

// From char array with explicit length
char array[3] = {'b', 'a', 'r'};
std::string_view array_v(array, std::size(array));  // "bar"

// From std::string
std::string s = "   trim me";
std::string_view v{s};
v.remove_prefix(std::min(v.find_first_not_of(" "), v.size()));
// v == "trim me"
```

**Key property**: No ownership. Lifetime of underlying string must outlive the view.

### starts_with / ends_with (C++20)

```c++
std::string str = "foobar";
str.starts_with("foo");  // true
str.ends_with("baz");   // false
```

For `string_view`:
```c++
std::string_view sv = "foobar";
sv.starts_with("foo");  // true
sv.ends_with("bar");    // true
```

### contains (C++23)

```c++
std::string{"foobarbaz"}.contains("bar");  // true
std::string{"foobarbaz"}.contains("bat");  // false
```

### std::to_underlying (C++23)

Convert enum to underlying integer type:

```c++
enum class MyEnum : int { A = 1, B, C };
std::to_underlying(MyEnum::A);  // 1
```

### String Conversion (C++17)

Non-allocating, non-throwing conversions:

```c++
// to_chars — convert to string (non-allocating)
std::string str;
str.resize(3);
auto [ptr, ec] = std::to_chars(str.data(), str.data() + str.size(), 123);
if (ec == std::errc{}) std::cout << str;  // "123"

// from_chars — parse from string (non-allocating)
std::string s = "456";
int n;
auto [ptr2, ec2] = std::from_chars(s.data(), s.data() + s.size(), n);
if (ec2 == std::errc{}) std::cout << n;  // 456
```

### std::byte (C++17)

Non-arithmetic byte representation — only bitwise operations:

```c++
std::byte a{0};
std::byte b{0xFF};
int i = std::to_integer<int>(b);  // 255
std::byte c = a & b;               // bitwise only
int j = std::to_integer<int>(c);   // 0
```

## string_view vs const std::string&

| Aspect | string_view | const string& |
|--------|------------|---------------|
| Ownership | None (non-owning) | Reference to owned |
| Can be null | Yes (checks `data()==nullptr`) | No ( UB if null) |
| Can rebind | Yes (cheap) | No (reference rebinds) |
| C-string compat | Yes (data(), size()) | Yes |

Use `string_view` for function parameters that accept both `std::string` and string literals.

## Related Concepts

- [[cpp-smart-pointers]] — string_view avoids unnecessary allocations
- [[cpp-stl-containers]] — string_view as a container view
