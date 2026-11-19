---
type: source
source-type: web
title: "Tip of the Week #141: Beware Implicit Conversions to `bool`"
author: "Samuel Freilich"
date: 2012
url: https://abseil.io/tips/141
summary: "abseil C++ Tips of the Week #141: Beware Implicit Conversions to `bool."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: b3c98d6ecc1f92fe121100c70d58fd59
---

> 原文：<https://abseil.io/tips/141> · 作者：Samuel Freilich · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#141: Beware Implicit Conversions to `bool`

\
\

Originally posted as TotW \#141 on January 19, 2018

*By [Samuel Freilich](/cdn-cgi/l/email-protection#bbc8ddc9ded2d7d2d8d3fbdcd4d4dcd7de95d8d4d6)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/141](https://abseil.io/tips/141)

## Two Kinds of Null Pointer Checks

Checking a pointer for null before dereferencing is important to avoid crashes and bugs. This can be done in two ways:

```cpp

if (foo) {
  DoSomething(*foo);
}
```

```cpp

if (foo != nullptr) {
  DoSomething(*foo);
}
```

Both of these conditionals have the same semantics given that `foo` is a pointer, but the type-checking on the latter is a little tighter. Many types in C++ can be implicitly converted to `bool`, and additional caution is required when the pointed-to type can itself be converted to `bool`.

Consider the following code which could have two very different meanings:

```cpp

bool* is_migrated = ...;

// Is this checking that `is_migrated` is not null, or was the actual
// intent to verify that `*is_migrated` is true?
if (is_migrated) {
  ...
}
```

This code is clearer:

```cpp

// Looks like a null-pointer check for a bool*
if (is_migrated != nullptr) {
  ...
}
```

Both styles are acceptable in Google C++ code. So when the underlying type is not implicitly convertible to `bool`, follow the style of surrounding code. If the value in question is a “smart pointer” like `std::unique_ptr`, the semantics and tradeoffs are the same.

## Optional Values and Scoped Assignments

What about optional (e.g. `std::optional`) values? They deserve more careful consideration.

For example:

```cpp

std::optional<bool> b = MaybeBool();
if (b) { ... }  // What happens when the function returns std::optional(false)?
```

Putting the variable declaration in the conditional of the `if` statement [limits the scope](https://google.github.io/styleguide/cppguide.html#Local_Variables) of the variable, but the value is implicitly<sup><a href="#fn:1" class="footnote" rel="footnote">1</a></sup> converted to a `bool`, so it may not be explicit which boolean property is tested.

The intent of the following code is clearer:

```cpp

std::optional<bool> b = MaybeBool();
if (b.has_value()) { ... }
```

Note that, in fact, the code snippets above are equivalent: `std::optional`’s conversion to `bool` only looks at whether the `optional` is full, not at its contents. A reader may find it counterintuitive that `optional(false)` is `true`, but it’s immediately clear that `optional(false)` has a value. Again, it’s worth extra caution when the underlying type is implicitly convertible to `bool`.

One pattern for optional return values is to put a variable declaration in the conditional of the `if` statement. This [limits the scope](https://google.github.io/styleguide/cppguide.html/#Local_Variables) of the variable, but involves an implicit conversion to `bool`:

```cpp

if (std::optional<Foo> foo = MaybeFoo()) {
  DoSomething(*foo);
}
```

**Note:** In C++17, `if` statements can contain an initializer, so the scope of the declaration can be limited while avoiding the implicit conversion:

```cpp

if (std::optional<Foo> foo = MaybeFoo(); foo.has_value()) {
  DoSomething(*foo);
}
```

## “Boolean-like” Enums

Let’s say you’ve taken the advice of [Tip \#94](/tips/94) and decided to use an `enum` in your function signature instead of a `bool` for better readability at the call sites. This kind of refactoring might introduce an implicit conversion in the function definition:

```cpp

void ParseCommandLineFlags(
    const char* usage, int* argc, char*** argv,
    StripFlagsMode strip_flags_mode) {
  if (strip_flags_mode) {  // Wait, which value was true again?
    ...
  }
}
```

You can gain additional clarity by replacing the implicit conversion with an explicit comparison:

```cpp

void ParseCommandLineFlags(
    const char* usage, int* argc, char*** argv,
    StripFlagsMode strip_flags_mode) {
  if (strip_flags_mode == kPreserveFlags) {
    ...
  }
}
```

## Summary

In summary, be aware that implicit conversions to `bool` can be unclear, so consider writing more explicit code:

- Compare pointer types to `nullptr` (especially if the pointed-at type is implicitly convertible to `bool`).
- Test container emptiness with boolean functions like `std::optional<T>::has_value()` (especially if the contained type is implicitly convertible to `bool`). Use the optional initializer form for `if` to limit the scope of variables ([Tip \#165](/tips/165)). Remember call-only interfaces though, and don’t take the address of `value()` or `has_value()`. The `testing::Optional` matcher can help in tests.
- Compare enums to specific values.


