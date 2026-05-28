---
type: entity
tags: [cpp11, move-semantics, rvalue-reference, rule-of-5]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Move Semantics

## Definition

**Move semantics** transfers ownership of resources (heap memory, file handles, etc.) from one object to another without copying. Introduced in C++11 via **rvalue references** (`T&&`).

## Key Concepts

### Rvalue References (C++11)

Rvalue references only bind to temporaries (rvalues) — enables distinguishing move from copy:

```c++
int x = 0;
int& xl = x;        // lvalue ref
int&& xr = 0;       // rvalue ref — binds to temporary
int&& xr2 = x;      // ERROR: x is lvalue

void f(int&);
void f(int&&);

f(x);               // calls f(int&)
f(0);               // calls f(int&&)
f(std::move(x));    // calls f(int&&)
```

### std::move and std::forward (C++11)

```c++
template <typename T>
typename remove_reference<T>::type&& move(T&& arg) {
  return static_cast<typename remove_reference<T>::type&&>(arg);
}

template <typename T>
T&& forward(typename remove_reference<T>::type& arg) {
  return static_cast<T&&>(arg);
}
```

`std::move` unconditionally casts to rvalue. `std::forward<T>` preserves value category (lvalue stays lvalue ref, rvalue converts to rvalue ref).

### Special Member Functions for Move (C++11)

Rule of 5 — five special member functions that manage resources:

```c++
struct A {
  std::string s;
  A() : s{"test"} {}
  A(const A& o) : s{o.s} {}                              // copy ctor
  A(A&& o) : s{std::move(o.s)} {}                        // move ctor
  A& operator=(const A& o) { s = o.s; return *this; }   // copy assign
  A& operator=(A&& o) { s = std::move(o.s); return *this; } // move assign
};
```

### Move Semantics Benefits

1. **Performance**: Moving a `std::vector` copies only 3 pointers (data, size, capacity), not every element
2. **Non-copyable types**: `std::unique_ptr` only movable — move transfer exclusive ownership
3. **Return value optimization**: RVO makes returning local objects nearly free

```c++
std::unique_ptr<int> p1{new int(1)};
std::unique_ptr<int> p2 = std::move(p1);  // ownership transferred
// p1 is now empty; p2 owns the memory
```

### Forwarding References (Perfect Forwarding)

`T&&` in templates preserves value category through call chains:

```c++
template <typename T>
void wrapper(T&& arg) {
  inner(std::forward<T>(arg));  // forward preserves original value category
}

int x;
wrapper(x);       // T=int& → forward<int&>(x) → int&
wrapper(0);       // T=int  → forward<int>(0)  → int&&
```

## Rule of 0/3/5

| Rule | Description |
|------|-------------|
| Rule of 0 | No resources — compiler-generated special members are correct |
| Rule of 3 | Has copy/move/ctor/dtor → define all 5 (copy+move+dtor) |
| Rule of 5 | C++11 — explicitly define move ctor + move assign |

## Related Concepts

- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — forwarding references, decltype(auto)
- [[cpp-smart-pointers]] — std::unique_ptr relies on move semantics
- [[entities/cpp/modern-cpp/cpp-constexpr]] — move semantics in constexpr contexts (C++14+)
- [[raii]] — move semantics enables efficient RAII ownership transfer
