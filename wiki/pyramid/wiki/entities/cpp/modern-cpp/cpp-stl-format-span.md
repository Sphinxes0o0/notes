---
type: entity
tags: [cpp20, cpp23, format, span, spanstream, out_ptr, io-pointers]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ std::format, std::span, and I/O Utilities

## Definition

C++20 introduced `std::format` (string formatting) and `std::span` (non-owning array view). C++23 added `spanstream` and `std::out_ptr`/`std::inout_ptr` for C API interoperability.

## Key Concepts

### std::format (C++20)

Compile-time checked, Python-style formatting:

```c++
std::format("{}", 123);                           // "123"
std::format("{} {}", "Hello", "World");           // "Hello World"

// Custom formatter
struct fraction {
  int numerator, denominator;
};
template <>
struct std::formatter<fraction> {
  constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }
  auto format(const fraction& f, std::format_context& ctx) const {
    return std::format_to(ctx.out(), "{}/{}", f.numerator, f.denominator);
  }
};

std::format("{}", fraction{1, 2});  // "1/2"
```

### std::span (C++20)

Non-owning view of a contiguous sequence. Cheap construct/copy:

```c++
void print_ints(std::span<const int> ints) {
  for (const auto n : ints) std::cout << n << "\n";
}

print_ints(std::vector{1, 2, 3});
print_ints(std::array<int, 5>{1, 2, 3, 4, 5});
int a[10] = {};
print_ints(a);  // decays to span<int, 10>

// Dynamic vs static extent
std::span<int> dyn;           // dynamic size
std::span<int, 3> stat{arr}; // fixed size — bounds-checked at compile
```

`span` propagates const via element type: `std::span<const int>` for read-only.

### spanstream (C++23)

`strstream` replacement using `std::span` as buffer — no ownership/reallocation:

```c++
char input[] = "10 20 30";
std::ispanstream is{std::span<char>{input}};
int i;
is >> i >> i >> i;  // 10, 20, 30

char output[30]{};
std::ospanstream os{std::span<char>{output}};
os << 10 << 20 << 30;
```

### std::out_ptr / std::inout_ptr (C++23)

Bridge between C APIs and smart pointers:

```c++
// C API: writes handle to *p_handle
int c_api_create(MyHandle** p_handle);
void c_api_delete(MyHandle* handle);

struct deleter { void operator()(MyHandle* h) { c_api_delete(h); } };

std::unique_ptr<MyHandle, deleter> resource;
int err = c_api_create(std::out_ptr(resource));  // writes to unique_ptr

// For shared_ptr (inout — reads AND writes)
std::shared_ptr<MyHandle> shared_res;
int err2 = c_api_recreate(std::inout_ptr(shared_res, deleter{}));
```

### std::unreachable (C++23)

Marks code path as unreachable — undefined behavior if reached:

```c++
enum class MyEnum { A, B, C };
int to_int(MyEnum e) {
  switch (e) {
    case MyEnum::A: return 0;
    case MyEnum::B: return 1;
    case MyEnum::C: return 2;
    default: std::unreachable();
  }
}
```

### Synchronized Output Stream (C++20)

Buffered, synchronized output — prevents interleaving:

```c++
std::osyncstream{std::cout} << "Value: " << x << "\n";
```

### Math Constants (C++20)

```c++
std::numbers::pi;   // 3.14159...
std::numbers::e;    // 2.71828...
std::numbers::phi;   // golden ratio
```

### Bit Operations (C++20)

```c++
std::popcount(0b1111'0000u);  // 4
std::bit_cast<int>(float_val);  // safe reinterpret_cast
std::midpoint(1, 3);           // 2 (no overflow)
std::to_array("foo");           // std::array<char, 4>
```

## Related Concepts

- [[cpp-stl-string-view]] — string_view pairs well with span
- [[cpp-smart-pointers]] — out_ptr/inout_ptr bridge to smart pointers
- [[cpp-stl-containers]] — span as view over containers
