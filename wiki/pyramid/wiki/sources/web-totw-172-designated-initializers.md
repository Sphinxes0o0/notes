---
type: source
source-type: web
title: "Tip of the Week #172: Designated Initializers"
author: "Aaron Jacobs"
date: 2012
url: https://abseil.io/tips/172
summary: "abseil C++ Tips of the Week #172: Designated Initializers."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: b6da4314d87e9761bcf32806aadf4fd7
---

> 原文：<https://abseil.io/tips/172> · 作者：Aaron Jacobs · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#172: Designated Initializers

\
\

Originally posted as TotW \#172 on December 11, 2019

*By [Aaron Jacobs](/cdn-cgi/l/email-protection#6b010a080409180a2b0c04040c070e45080406)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/172](https://abseil.io/tips/172)

[Designated initializers](https://en.cppreference.com/w/cpp/language/aggregate_initialization#Designated_initializers) are a syntax in the C++20 standard for specifying the contents of a struct in a compact yet readable and maintainable manner. Instead of the repetitive

```cpp

struct Point {
  double x;
  double y;
  double z;
};

Point point;
point.x = 3.0;
point.y = 4.0;
point.z = 5.0;
```

one can use designated initializers to write

```cpp

Point point = {
    .x = 3.0,
    .y = 4.0,
    .z = 5.0,
};
```

This is a little less repetitive, but more importantly, can be used in more contexts. For example, it means the struct can be made `const` without resorting to awkward workarounds:

```cpp

// Make it clear to the reader (of the potentially complicated larger piece of
// code) that this struct will never change.
const Point character_position = { .x = 3.0 };
```

Or can be used directly in a function call without introducing an additional identifier into the scope:

```cpp

std::vector<Point> points;
[...]
points.push_back(Point{.x = 3.0, .y = 3.0});
points.push_back(Point{.x = 4.0, .y = 4.0});
```

## Semantics

Designated initializers are a form of [aggregate initialization](https://en.cppreference.com/w/cpp/language/aggregate_initialization), and so can be used only with [aggregates](https://en.cppreference.com/w/cpp/language/aggregate_initialization#Explanation). This means approximately “structs or classes with no user-provided constructors or virtual functions”, which in turn is approximately when we use `struct` (as opposed to `class`) in typical Google style.

The semantics of C++20 designated initializers are what you might expect given other C++ language features like member initialization lists in constructors. Explicitly mentioned fields are initialized, in order, with the expression provided, and it is permissible to leave out fields that you want to have “default” behavior for:

```cpp

Point point = {
    .x = 1.0,
    // y will be 0.0
    .z = 2.0,
};
```

What does “default” mean above? Outside of special cases like `union`s the answer is:

- If the struct definition contains a default member initializer (i.e. the field definition looks like `std::string foo = "default value";`) then that is used.
- Otherwise the field is initialized as if with `= {}`. In practice this means that for plain old data types you get the zero value, and for more complicated classes you get a default-constructed instance.

This is typically the least surprising behavior. See the [standard](http://eel.is/c++draft/dcl.init#aggr-5) for details.

## Some History and Language Trivia

Designated initializers have been a standard part of the C language since C99, and have been offered by compilers as a [non-standard extension](https://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html) since before that. But until recently they were not part of C++: a notable example where C is not a subset of C++. For this reason the Google style guide [used to say not to use them](https://google.github.io/styleguide/cppguide.html#Nonstandard_Extensions).

After two decades the situation has finally changed: designated initializers are now [part](http://eel.is/c++draft/dcl.init#aggr-3) of the C++20 standard.

The C++20 form of designated initializers has some restrictions compared to the C version:

- C++20 requires fields to be listed in the designator in the same order as they are listed in the struct definition (so `Point{.y = 1.0, .x = 2.0}` is not legal). C does not require this.
- C allows you to mix designated and non-designated initializers (`Point{1.0, .z = 2.0}`), but C++20 does not.
- C supports a syntax for sparsely initializing arrays known as “array designators”. This is not part of C++20.


