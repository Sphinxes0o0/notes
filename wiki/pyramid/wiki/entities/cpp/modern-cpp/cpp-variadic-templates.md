---
type: entity
tags: [cpp11, cpp14, cpp17, templates, parameter-pack, variadic, fold-expressions]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Variadic Templates

## Definition

**Variadic templates** use parameter packs (`typename... Args` or `Args...`) to accept zero or more arguments of arbitrary type. Introduced in C++11.

## Key Concepts

### Parameter Packs (C++11)

```c++
template <typename... T>
struct arity {
  constexpr static int value = sizeof...(T);  // sizeof... operator
};
static_assert(arity<>::value == 0);
static_assert(arity<char, short, int>::value == 3);

// Variadic function
template <typename First, typename... Args>
auto sum(const First first, const Args... args) -> First {
  auto values = {first, args...};  // pack expansion
  First total{0};
  for (auto v : values) total += v;
  return total;
}
sum(1, 2, 3, 4, 5);  // 15
```

### Pack Expansion (C++11)

`args...` expands the pack in various contexts:

```c++
// Forward to another function
template <typename... Args>
void forward(Args&&... args) {
  f(std::forward<Args>(args)...);
}

// Template template parameters
template <typename... Args>
struct tuple { /* ... */ };
template <template <typename...> class Container, typename... Args>
void adapt(Container<Args...>& c) { }
```

### Fold Expressions (C++17)

Unary and binary folds over parameter packs:

```c++
template <typename... Args>
bool logicalAnd(Args... args) {
  return (true && ... && args);     // unary right fold
}

template <typename... Args>
auto sum(Args... args) {
  return (... + args);               // unary left fold
}
sum(1.0, 2.0f, 3);  // 6.0
```

Binary fold — one side is expanded, one is not:
```c++
template <typename... Args>
auto prepend(Args... args) {
  return (args + ... + 0);          // binary fold: args... op 0
}
```

### Compile-Time Integer Sequences (C++14)

```c++
std::make_integer_sequence<int, 3>;   // int_sequence<0, 1, 2>
std::index_sequence_for<T...>;        // index_sequence<0, 1, 2...>

// Practical: array to tuple
template <typename Array, std::size_t... I>
auto a2t_impl(const Array& a, std::index_sequence<I...>) {
  return std::make_tuple(a[I]...);
}
template <typename T, std::size_t N>
auto a2t(const std::array<T, N>& a) {
  return a2t_impl(a, std::make_index_sequence<N>{});
}
```

### Non-Type Template Parameters with auto (C++17)

```c++
template <auto... seq>
struct my_integer_sequence { /* ... */ };

my_integer_sequence<0, 1, 2>;   // deduces int
my_integer_sequence<0ULL, 1ULL>; // deduces unsigned long long
```

### Variadic Class Templates (C++11)

```c++
template <typename T>
struct holder { T value; };

template <typename... Ts>
struct tuple { /* recursively defined */ };
```

### Variadic Aliases (C++11)

```c++
template <typename T>
using Vec = std::vector<T>;

template <typename... Args>
using CommonType = std::common_type_t<Args...>;
```

## Related Concepts

- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — forwarding references preserve pack value categories
- [[cpp-concepts]] — constraining variadic templates with concepts
- [[entities/cpp/modern-cpp/cpp-constexpr]] — variadics work in constexpr contexts
- [[cpp-constexpr#if-constexpr]] — if constexpr for compile-time branching on parameter packs
