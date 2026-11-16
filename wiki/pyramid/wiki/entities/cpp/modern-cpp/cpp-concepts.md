---
type: entity
tags: [cpp20, concepts, requires, constraints, template]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Concepts

## Definition

**Concepts** are named compile-time constraints that limit what types a template can accept. They improve error messages and provide semantic grouping of types. Introduced in C++20.

## Key Concepts

### Defining Concepts

```c++
template <typename T>
concept always_satisfied = true;

template <typename T>
concept integral = std::is_integral_v<T>;

template <typename T>
concept signed_integral = integral<T> && std::is_signed_v<T>;

template <typename T>
concept unsigned_integral = integral<T> && !signed_integral<T>;
```

### requires Clauses and Expressions

```c++
// requires clause
template <typename T>
  requires my_concept<T>
void f(T v);

// requires expression — tests validity of expressions
template <typename T>
concept callable = requires (T f) { f(); };

// Compound requirement with type constraint
template <typename T>
concept pair_like = requires(T x) {
  { *x } -> std::convertible_to<typename T::inner>;
  { x + 1 } -> std::same_as<int>;
};
```

### requires Expression Requirements Types

| Type | Syntax | What it checks |
|------|--------|----------------|
| Simple | `expr;` | Expression is valid |
| Type | `typename T;` | Type name is valid |
| Compound | `{ expr } -> constraint` | Expression valid + satisfies constraint |
| Nested | `requires { requires ...; }` | Additional constraints |

```c++
struct foo { int foo; };

// A) has inner member named value
// B) S<T> is a valid specialization
// C) Ref<T> is a valid alias
template <typename T>
concept C = requires {
  typename T::value;
  typename S<T>;
  typename Ref<T>;
};

g(foo{});  // ERROR: fails requirement A
```

### Syntactic Forms for Using Concepts

```c++
// Constrained type template parameter
template <my_concept T>
void f1(T v);

// requires clause
template <typename T>
  requires my_concept<T>
void f2(T v);

// trailing requires
template <typename T>
void f3(T v) requires my_concept<T>;

// abbreviated function template (C++20)
void f4(my_concept auto v);

// constrained non-type template parameter
template <my_concept auto v>
void f5();

// constrained lambda
auto f6 = []<my_concept T>(T v) { /* ... */ };
```

### Standard Concepts Library (C++20)

**Core language concepts:**
- `same_as<T, U>` — two types are the same
- `derived_from<T, U>` — T is derived from U
- `convertible_to<T, U>` — T implicitly convertible to U
- `common_with<T, U>` — shared common type
- `integral<T>` — T is integral type
- `default_initializable<T>` — T can be default-constructed

**Callable concepts:**
- `invocable<F, Args...>` — F can be invoked with Args
- `predicate<F, Args...>` — invocable returns bool

**Object concepts:**
- `movable<T>` — can be moved and swapped
- `copyable<T>` — can be copied, moved, swapped
- `semiregular<T>` — copyable + default constructible
- `regular<T>` — semiregular + equality_comparable

**Comparison (C++20):**
- `equality_comparable<T>` — supports ==
- `totally_ordered<T>` — supports <, <=, >, >=

### constinit vs constexpr (C++20)

`constinit` ensures compile-time initialization (dynamic init forbidden):

```c++
const char* g() { return "dynamic"; }
constexpr const char* f() { return "constant"; }

constinit const char* c = f();  // OK
constinit const char* d = g();  // ERROR: g() not constexpr
```

## Related Concepts

- [[cpp-templates]] — concepts constrain template parameters
- [[entities/cpp/modern-cpp/cpp-constexpr]] — constexpr functions in concept constraints
- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — constrained auto: `my_concept auto x`
