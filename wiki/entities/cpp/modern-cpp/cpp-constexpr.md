---
type: entity
tags: [cpp11, cpp14, cpp17, cpp20, cpp23, constexpr, consteval, compile-time]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ constexpr / consteval / Compile-Time Computing

## Definition

`constexpr` indicates a value or function that **may** be evaluated at compile time. `consteval` (C++20) indicates a function that **must** be evaluated at compile time. Compile-time computing reduces runtime cost.

## Key Concepts

### constexpr Variables (C++11)

```c++
constexpr int x = 123;          // compile-time constant
constexpr double pi = 3.14159;
```

### constexpr Functions (C++11 → C++14)

**C++11**: only single return statement, no branches/loops
**C++14+**: relaxed — allows if/else, loops, multiple statements:

```c++
// C++11: single return
constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }

// C++14: multiple statements, loops
constexpr int factorial(int n) {
  int result = 1;
  for (int i = 2; i <= n; ++i) result *= i;
  return result;
}

static_assert(factorial(5) == 120);  // evaluated at compile time
```

### constexpr Lambda (C++17)

Lambdas can be constexpr:

```c++
auto identity = [](int n) constexpr { return n; };
static_assert(identity(123) == 123);
```

### consteval / Immediate Functions (C++20)

`consteval` functions **must** produce a constant — used to force compile-time computation:

```c++
consteval int sqr(int n) { return n * n; }

constexpr int r = sqr(100);   // OK: compile-time
int x = 100;
int r2 = sqr(x);              // ERROR: x not a constant
```

### consteval if (C++23)

Branch selected at compile time without instantiation:

```c++
consteval int f(int i) { return i; }

constexpr int g(int i) {
  if consteval {
    return f(i);              // constant branch
  } else {
    return 42;                // runtime branch
  }
}
```

### constexpr if (C++17)

Compile-time branch — non-taken branch is not instantiated (no instantiations errors):

```c++
template <typename T>
constexpr bool isIntegral() {
  if constexpr (std::is_integral<T>::value) {
    return true;
  } else {
    return false;             // this branch is discarded for non-integral T
  }
}
```

### constexpr Virtual Functions (C++20)

Virtual functions can be constexpr:

```c++
struct X1 {
  virtual int f() const = 0;
};
struct X2 : X1 {
  constexpr virtual int f() const { return 2; }
};

constexpr X2 x2;
static_assert(x2.f() == 2);  // compile-time virtual call
```

### constexpr and Classes (C++11)

```c++
struct Complex {
  double re, im;
  constexpr Complex(double r, double i) : re{r}, im{i} {}
  constexpr double real() const { return re; }
};

constexpr Complex I{0, 1};
static_assert(Complex(1,2).real() == 1);
```

### std::is_constant_evaluated (C++20)

Check if currently evaluating in constexpr context:

```c++
constexpr bool is_ct() { return std::is_constant_evaluated(); }

constexpr bool a = is_ct();  // true
bool b = is_ct();            // false
```

## constexpr vs const vs consteval

| Specifier | When evaluated | Required at compile-time |
|-----------|----------------|--------------------------|
| `const` | runtime or compile-time | No |
| `constexpr` | compile-time if possible | No (may fall to runtime) |
| `consteval` | always compile-time | Yes |
| `constinit` (C++20) | compile-time initialization | Yes (dynamic init forbidden) |

## Related Concepts

- [[cpp-variadic-templates]] — constexpr with parameter packs
- [[cpp-auto-type-deduction]] — decltype(auto) + constexpr interaction
- [[cpp-concepts]] — constexpr in concept constraints
- [[cpp-lambda-expressions]] — constexpr lambdas
