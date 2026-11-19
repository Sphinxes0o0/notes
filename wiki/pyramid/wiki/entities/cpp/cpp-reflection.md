---
type: entity
tags: [cpp, cpp26, reflection, metaprogramming, serialization]
created: 2026-05-22
sources: [pdf-cpp-slides]
---

# C++ Reflection

## Definition

C++26 introduces **compile-time reflection** via P2996, enabling programs to query and manipulate type information (member names, types, access levels) at compile time using the `^^` operator (reflection) and `[: :]` splice operator.

## Key Mechanisms

### Reflection Operator (`^^`)
Lifts an expression or type name into the **reflection domain**, yielding a `std::meta::info` value — a handle representing the reflected entity.

```cpp
int x = 0;
constexpr auto r = ^^x;        // r is std::meta::info
constexpr auto t = ^^int;      // t is std::meta::info for type int
```

### Splice Operator (`[: expr :]`)
Splices a `std::meta::info` value back into the **source code** at compile time, substituting the reflected entity.

```cpp
int i = 42;
return [: ^^i :];  // expands to: return i;  (at compile time)
```

The combination `[: ^^expr :]` is equivalent to the original expression (lifts then splices back).

### Meta Functions
Compile-time functions operating on `std::meta::info`:

```cpp
std::meta::nonstatic_data_members_of(
    ^^MyStruct,
    std::meta::access_context::unchecked()
)
// → vector<info> of all data members (including private)
```

Key meta functions:
- `nonstatic_data_members_of(type, access_context)` — returns member descriptors
- `type_of(info)` — gets the type of a reflected member
- `info_of(type)` — gets `std::meta::info` from a type name

All meta functions are **`consteval`** — reflection is purely compile-time, zero runtime overhead.

### Access Context
Controls visibility when querying members:
- `access_context::current()` — respects access rules of the call site
- `access_context::unprivileged()` — same as `current()` but for unprivileged queries
- `access_context::unchecked()` — bypasses private/protected checks (use for serialization tools)

## Use Cases

### Auto-Generated Serialization (Bloomberg Case Study)
Instead of writing hand-rolled `std::formatter` specializations per message type, a single template uses reflection:

```cpp
struct json_formatter {
    template <typename T>
    auto format(const T& obj, auto& ctx) const {
        // [: std::meta::nonstatic_data_members_of(... :)]
        // → generates member access code at compile time
    }
};
template <typename T> struct std::formatter<T> : json_formatter {};
```

This eliminates boilerplate: adding a new member to a struct automatically updates all formatters.

### Use Cases Beyond Serialization
- **ORM / data mapping** — reflect struct fields to database columns
- **Testing frameworks** — auto-generate comparison operators, printers
- **Plugin systems** — runtime registration of types via compile-time registration
- **IDL/code generation** — replace external IDL compilers with in-language reflection

## Relationship to Existing C++ Features

- **Templates + `decltype`** — existing type introspection is limited; reflection gives *names*, not just types
- **`std::type_info`** — runtime only, limited; reflection is compile-time and richer
- **Macro-based reflection** (Boost.Hana, BOOST_REFLECT) — external libraries; P2996 is language-native
- **`constexpr`/`consteval`** — reflection computations are `consteval`; no runtime cost
- **`if constexpr`** — compile-time branching on type traits; reflection gives structural decomposition

## Key Insight

C++ reflection is **value-based** (reflecting expressions) vs. type-based (reflecting types). The `^^` operator works on expressions, and `[: :]` splices back into expressions, making it compositional — reflection of a member can be passed to functions, stored in containers, and manipulated at compile time.

## Related Concepts
- [[entities/cpp/cpp-serialization]] — reflection enables automated serialization without boilerplate
- [[entities/cpp/cpp-stl-functors]] — meta functions as compile-time function objects
- [[entities/cpp/cpp20-features]] — C++20 Modules address physical design (separate compilation); reflection complements modules for code generation
- [[entities/cpp/constexpr]] — both enable compile-time computation; reflection operates on compile-time values
- [[entities/cpp/variadic-templates]] — reflection on aggregate types can iterate members using parameter packs
