---
type: entity
tags: [cpp11, cpp17, cpp20, functional, invoke, apply, bind, not_fn]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ STL Functional Utilities

## Definition

Standard library utilities for working with callable objects: `std::invoke`, `std::apply`, `std::bind_front`, `std::not_fn`, `std::reference_wrapper`.

## Key Concepts

### std::invoke (C++17)

Uniform invocation of any callable — works with functions, member functions, functors:

```c++
template <typename Callable, typename... Args>
decltype(auto) invoke(Callable&& c, Args&&... args) {
  return std::forward<Callable>(c)(std::forward<Args>(args)...);
}

// Works uniformly:
std::invoke(f, args...);
std::invoke(&Foo::method, foo_obj, args...);
std::invoke([](int x) { return x * 2; }, 21);  // 42
```

Use case: `std::async`, `std::thread`, general callable wrappers.

### std::apply (C++17)

Invoke callable with a tuple of arguments:

```c++
auto add = [](int x, int y) { return x + y; };
std::apply(add, std::make_tuple(1, 2));  // 3
std::apply(add, std::pair{1, 2});        // 3
```

### std::bind_front (C++20)

Binds first N arguments to a callable — simpler than `std::bind`:

```c++
const auto f = [](int a, int b, int c) { return a + b + c; };
const auto g = std::bind_front(f, 1, 1);  // f(1, 1, c)
g(1);  // 3
```

### std::not_fn (C++17)

Returns negation of predicate — replaces `std::not1` (deprecated):

```c++
const auto is_even = [](const auto n) { return n % 2 == 0; };
std::vector<int> v{0, 1, 2, 3, 4};

std::copy_if(v.begin(), v.end(), ostream_it, std::not_fn(is_even));
// prints: 1 3
```

### std::reference_wrapper (C++11)

Wraps a reference — enables storing references in containers:

```c++
int x = 123;
auto rw = std::ref(x);
++rw;            // x == 124

std::vector<std::reference_wrapper<int>> vec;
vec.push_back(std::ref(x));
```

`std::cref` for const references.

### std::bind (C++11, deprecated in C++14+, use bind_front)

Binds arguments to callable. More complex than `bind_front`:

```c++
auto bound = std::bind(f, _1, 5);  // f(_1, 5)
bound(3);  // f(3, 5)
```

### std::function (C++11)

Type-erased callable wrapper:

```c++
std::function<int(int, int)> f = [](int a, int b) { return a + b; };
f = std::multiplies<int>{};  // works too
```

## Related Concepts

- [[cpp-lambda-expressions]] — lambdas are callables
- [[cpp-auto-type-deduction]] — auto for callable type deduction
- [[cpp-concurrency]] — std::invoke in thread/async contexts
