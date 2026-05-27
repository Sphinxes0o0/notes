---
type: entity
tags: [cpp11, cpp14, cpp17, cpp20, lambda, closure, functional]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Lambda Expressions

## Definition

A **lambda** is an unnamed function object (closure) that can capture variables from its enclosing scope. Introduced in C++11.

## Syntax

```c++
[ capture-list ] ( params ) specifiers -> ret_type { body }
```

## Key Concepts

### Capture List Variants (C++11)

| Capture | Meaning |
|---------|---------|
| `[]` | captures nothing |
| `[=]` | capture local objects by value |
| `[&]` | capture local objects by reference |
| `[this]` | capture `this` by reference |
| `[a, &b]` | capture `a` by value, `b` by reference |
| `[=, *this]` | capture `this` by value (C++17) |

```c++
int x = 1;
auto getX = [=] { return x; };       // captures by value (copy)
auto addX = [&](int y) { x += y; };   // captures by reference, mutable
auto getXRef = [&]() -> int& { return x; };
```

### Generic Lambdas (C++14)

`auto` in lambda parameters enables polymorphism:

```c++
auto identity = [](auto x) { return x; };
int three = identity(3);              // OK
std::string foo = identity("foo");   // OK
```

### Lambda Capture Initializers (C++14)

Create new variables inside capture list, evaluated at lambda creation:

```c++
auto f = [x = factory(2)] { return x; };  // returns 20

// Move-only capture
auto p = std::make_unique<int>(1);
auto task = [p = std::move(p)] { *p = 5; };  // OK: p is move-constructed

// Rename captures
auto x = 1;
auto g = [&r = x, x = x * 10] { ++r; return r + x; };
g();  // x becomes 2, returns 12
```

### Mutable Lambdas

By default, value-captures cannot be modified (const operator generated). `mutable` allows modification:

```c++
int x = 1;
auto f = [x]() mutable { x = 2; };  // OK: mutable allows modification
f();                                 // x in lambda = 2; outer x still = 1
```

### Lambda Capture `this` by Value (C++17)

Problem: capturing `this` by reference in async code risks dangling reference if object dies.

```c++
struct MyObj {
  int value{123};
  auto getCopy() { return [*this] { return value; }; }   // C++17: copy of *this
  auto getRef()  { return [this]  { return value; }; }    // Dangerous: reference to *this
};
```

### Template Syntax for Lambdas (C++20)

Familiar template syntax inside lambda parameter list:

```c++
auto f = []<typename T>(std::vector<T> v) { /* ... */ };
```

### Lambda Capture of Parameter Pack (C++20)

Capture variadic parameters by value or reference:

```c++
template <typename... Args>
auto f(Args&&... args) {
  return [...args = std::forward<Args>(args)] { /* use args... */ };
  // or by reference: [&...args = std::forward<Args>(args)]
}
```

### constexpr Lambdas (C++17)

Lambdas can be `constexpr` — evaluated at compile-time:

```c++
auto identity = [](int n) constexpr { return n; };
static_assert(identity(123) == 123);

constexpr auto add = [](int x, int y) {
  return [=] { return x + y; };  // nested lambda
};
static_assert(add(1, 2)() == 3);
```

### Ref-Qualified Member Functions (C++11)

Lambdas don't directly use ref-qualifiers, but the pattern appears in callable objects:

```c++
struct Foo {
  Bar& getBar() &  { return bar; }
  Bar&& getBar() && { return std::move(bar); }
};
```

## Related Concepts

- [[cpp-stl-functional]] — std::invoke, std::bind_front, std::not_fn
- [[cpp-auto-type-deduction]] — generic lambdas use auto
- [[cpp-constexpr]] — constexpr lambdas
- [[cpp-concurrency]] — lambdas in thread creation and async
