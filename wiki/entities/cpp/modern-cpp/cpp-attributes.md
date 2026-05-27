---
type: entity
tags: [cpp11, cpp14, cpp17, cpp20, cpp23, attributes, nodiscard, fallthrough, likely]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Attributes

## Definition

**Attributes** provide a standard syntax for annotating code with compiler hints, warnings, or semantic markers. Introduced in C++11 with a universal syntax that replaces `__attribute__`, `__declspec`, etc.

## Key Concepts

### [[nodiscard]] (C++17)

Warns when return value is discarded. Applied to functions or classes:

```c++
[[nodiscard]] bool do_something() { return is_success; }
do_something();  // warning: return value ignored

struct [[nodiscard]] error_info { /* ... */ };
error_info cause_error() { return {}; }
cause_error();  // warning: error_info ignored
```

Use case: error-returning functions, `[[nodiscard]]` allocators.

### [[fallthrough]] (C++17)

Indicates intentional fallthrough in switch:

```c++
switch (n) {
  case 1:
    [[fallthrough]];  // fallthrough to case 2 is intentional
  case 2:
    // ...
    break;
}
```

### [[maybe_unused]] (C++17)

Suppresses "unused variable" warnings:

```c++
void my_callback(std::string msg, [[maybe_unused]] bool error) {
  log(msg);
}
```

### [[likely]] / [[unlikely]] (C++20)

Hint to optimizer about branch probability:

```c++
if (n == 2) [[likely]] {
  // body expected to execute most often
}

switch (n) {
  [[likely]] case 2:  // hint: n is usually 2
    break;
}

while (unlikely_truthy_condition) [[unlikely]] {
  // body rarely executed
}
```

### [[deprecated]] (C++14)

Mark functions/types as deprecated with optional reason:

```c++
[[deprecated]]
void old_method();

[[deprecated("Use new_method instead")]]
void legacy_method();
```

### [[noexcept]] (C++11)

Specifies whether a function may throw. `noexcept(false)` = may throw; `noexcept(true)` = does not throw:

```c++
void func1() noexcept;           // does not throw
void func2() noexcept(true);    // does not throw
void func3() throw();            // legacy: does not throw
void func4() noexcept(false);   // may throw

void g() noexcept {
  f();  // OK even if f() throws — std::terminate called
}
```

### [[noreturn]] (C++11)

Indicates function never returns (e.g., `std::terminate`, `exit`):

```c++
[[noreturn]] void f() { throw "error"; }
```

### __has_include (C++17)

Conditional inclusion based on header availability:

```c++
#ifdef __has_include
#  if __has_include(<optional>)
#    include <optional>
#    define have_optional 1
#  elif __has_include(<experimental/optional>)
#    include <experimental/optional>
#    define have_optional 1
#  else
#    define have_optional 0
#  endif
#endif

// Platform-specific headers
#ifdef __has_include
#  if __has_include(<OpenGL/gl.h>)
#    include <OpenGL/gl.h>
#  elif __has_include(<GL/gl.h>)
#    include <GL/gl.h>
#  endif
#endif
```

### [[explicit(bool)]] (C++20)

Conditionally explicit constructor based on type trait:

```c++
struct foo {
  template <typename T>
  explicit(!std::is_integral_v<T>) foo(T) {}
};

foo a = 123;       // OK: integral, explicit(false) → not explicit
foo b = "123";     // ERROR: string — explicit(true)
foo c{"123"};      // OK: direct-init bypasses explicit
```

## Related Concepts

- [[cpp11-strongly-typed-enums]] — enum class underlying type control
- [[cpp-explicit-virtual-overrides]] — override/final are attribute-like
- [[cpp-concurrency]] — noexcept and thread safety
