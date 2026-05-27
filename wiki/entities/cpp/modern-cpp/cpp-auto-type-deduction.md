---
type: entity
tags: [cpp11, cpp14, type-system, auto, decltype]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ auto / Type Deduction

## Definition

C++ provides multiple mechanisms for deducing types at compile time: `auto` (C++11), `decltype` (C++11), `decltype(auto)` (C++14), and **forwarding references** `T&&` (C++11).

## Key Concepts

### auto (C++11)

Deduces type from initializer. Removes verbosity, especially for complex iterator/types.

```c++
auto a = 3.14;          // double
auto b = 1;             // int
auto& c = b;            // int&
auto&& e = 1;            // int&& (rvalue ref)
auto&& f = b;           // int&  (lvalue ref, forwarding ref collapses)
```

Trailing return type with `auto`:
```c++
template <typename X, typename Y>
auto add(X x, Y y) -> decltype(x + y) { return x + y; }
```

### decltype (C++11)

Returns the declared type of an expression — preserves cv-qualifiers and references.

```c++
int a = 1;
const int& c = a;
decltype(c) d = a;       // const int&

int&& f = 1;
decltype(f) g = 1;       // int&&

decltype((a)) h = g;    // int& — parens force lvalue reference
```

### decltype(auto) (C++14)

Deduces type like `auto` but preserves references and cv-qualifiers — essential for generic forwarding:

```c++
const int x = 0;
auto x1 = x;            // int (drops const and ref)
decltype(auto) x2 = x;  // const int (keeps both)

int y = 0;
int& y1 = y;
auto y2 = y1;           // int (drops ref)
decltype(auto) y3 = y1; // int& (keeps ref)
```

### Forwarding References (C++11)

`T&&` with template type deduction — binds to lvalue or rvalue, enabling **perfect forwarding**:

```c++
template <typename T>
void f(T&& t) { }       // forwarding reference

int x = 0;
f(0);                   // T=int,  deduces T=int&&  → int&& param
f(x);                    // T=int&, deduces T=int&  → int&  param
```

Reference collapsing rules:
- `T& &` → `T&`
- `T& &&` → `T&`
- `T&& &` → `T&`
- `T&& &&` → `T&&`

### Return Type Deduction (C++14)

Functions and lambdas can deduce return type with `auto`:

```c++
auto f(int i) { return i; }           // deduces int

template <typename T>
auto& g(T& t) { return t; }          // deduces T&

auto h = [](auto& x) -> auto& { return f(x); };  // returns reference
```

## C++17 auto Deduction from Braced Init

C++17 changed `auto x {v}` — now deduces to the element type, not `initializer_list`:

```c++
auto x1 {1, 2, 3};    // ERROR: not a single element
auto x2 = {1, 2, 3};  // std::initializer_list<int>
auto x3 {3};          // int (was std::initializer_list<int> in C++11)
```

## Related Concepts

- [[cpp-move-semantics]] — forwarding is used with std::forward
- [[cpp-constexpr]] — auto/constexpr interaction
- [[cpp-lambda-expressions]] — generic lambdas use auto parameters
- [[cpp-variadic-templates]] — forwarding references with parameter packs
