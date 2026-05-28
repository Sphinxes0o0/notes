---
type: entity
tags: [cpp17, structured-bindings, decomposition, tie, pair, tuple]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Structured Bindings & Decomposition

## Definition

**Structured bindings** (C++17) unpack tuple-like objects into named variables in one statement: `auto [x, y, z] = expr`. Also covers `std::tie` (C++11) and class template argument deduction (CTAD).

## Key Concepts

### Structured Bindings (C++17)

Works with `std::tuple`, `std::pair`, `std::array`, and aggregate types:

```c++
using Coordinate = std::pair<int, int>;
Coordinate origin() { return {0, 0}; }

const auto [x, y] = origin();   // x=0, y=0

// Reference bindings
for (const auto& [key, value] : myMap) { /* ... */ }

// Deduction guides (C++17 CTAD)
std::vector v{1, 2, 3};  // std::vector<int>

std::mutex mtx;
auto lck = std::lock_guard{mtx};  // std::lock_guard<std::mutex>
```

### std::tie (C++11)

Creates tuple of lvalue references — useful for unpacking:

```c++
std::string playerName;
std::tie(std::ignore, playerName, std::ignore) =
    std::make_tuple(91, "John Tavares", "NYI");

// With pairs
std::string yes, no;
std::tie(yes, no) = std::make_pair("yes", "no");
```

### Class Template Argument Deduction (C++17)

Compiler deduces template arguments from constructor:

```c++
std::vector v{1, 2, 3};             // deduces std::vector<int>
std::mutex mtx;
auto lck = std::lock_guard{mtx};     // std::lock_guard<std::mutex>
auto p = new std::pair{1.0, 2.0};     // std::pair<double, double>*
```

Deduction guides for user-defined types:
```c++
template <typename T>
struct container {
  container(T t) {}
  template <typename Iter>
  container(Iter b, Iter e);
};

template <typename Iter>
container(Iter, Iter) -> container<typename std::iterator_traits<Iter>::value_type>;

container a{7};                      // container<int>
std::vector<double> v{1.0, 2.0};
auto b = container{v.begin(), v.end()};  // container<double>
```

### Designated Initializers (C++20)

C-style designated initializer for aggregates:

```c++
struct A { int x; int y; int z = 123; };
A a{.x = 1, .z = 2};    // a.x=1, a.y=0 (default), a.z=2
```

### Selection Statements with Initializer (C++17)

Tighten scope of variables used in conditions:

```c++
// Before: variable leaks out of if
{
  std::lock_guard<std::mutex> lk(mx);
  if (v.empty()) v.push_back(val);
}

// After: lock_guard scoped to if
if (std::lock_guard<std::mutex> lk{mx}; v.empty()) {
  v.push_back(val);
}

// switch with initializer
switch (auto gadget = makeGadget(); gadget.status()) {
  case OK: gadget.zip(); break;
}
```

### Nested Namespaces (C++17)

```c++
namespace A::B::C { int i; }  // instead of A { namespace B { namespace C { ... } } }
```

## std::array (C++11)

Fixed-size container built on C-style array:

```c++
std::array<int, 3> a = {2, 1, 3};
std::sort(a.begin(), a.end());  // {1, 2, 3}
```

## std::tuple (C++11)

Fixed-size heterogeneous collection:

```c++
auto player = std::make_tuple(51, "Frans Nielsen", "NYI");
std::get<0>(player);  // 51
std::get<1>(player);  // "Frans Nielsen"
```

## Related Concepts

- [[cpp-variadic-templates]] — tuples are variadic
- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — CTAD uses auto deduction
- [[cpp-stl-functional]] — std::tie used with std::bind_front
