---
type: source
source-type: web
title: "Tip of the Week #86: Enumerating with Class"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/86
summary: "abseil C++ Tips of the Week #86: Enumerating with Class."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 425f7c1bf49d4a946c1bf18a38e2e23c
---

> 原文：<https://abseil.io/tips/86> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#86: Enumerating with Class

\
\

Originally posted as totw/86 on 2015-01-05

*By Bradley White [(<span class="__cf_email__" cfemail="b4d6c3c3f4d3dbdbd3d8d19ad7dbd9">\[email protected\]</span>)](/cdn-cgi/l/email-protection#6705101027000808000b024904080a)*

*“Show class, … and display character.” - Bear Bryant.*

An enumeration, or simply an **enum**, is a type that can hold one of a specified set of integers. Some values of this set can be given names, and are called the enumerators.

## Unscoped Enumerations

This concept will be familiar to C++ programmers, but prior to C++11 enumerations had two significant shortcomings: the enumeration names were:

- in the same scope as the enum type, and
- implicitly convertible to values of some integer type.

So, with C++98 …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
enum CursorDirection { kLeft, kRight, kUp, kDown };
CursorDirection d = kLeft; // OK: enumerator in scope
int i = kRight;            // OK: enumerator converts to int
```

</div>

</div>

but, …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// error: redeclarations of kLeft and kRight
enum PoliticalOrientation { kLeft, kCenter, kRight };
```

</div>

</div>

C++11 modified the behavior of unscoped enums in one way: the enumerators are now local to the enum, but continue to be exported into the enum’s scope for backwards compatibility.

So, with C++11 …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
CursorDirection d = CursorDirection::kLeft;  // OK in C++11
int i = CursorDirection::kRight;             // OK: still converts to int
```

</div>

</div>

but the declaration of `PoliticalOrientation` would still elicit errors.

## Scoped Enumerations

The implicit conversion to integer has been observed to be a common source of bugs, while the namespace pollution caused by having the enumerators in the same scope as the enum causes problems in large, multi-library projects. To address both these concerns, C++11 introduced a new concept: the **scoped enum**.

In a scoped enum, introduced by the keywords `enum class`, the enumerators are:

- only local to the enum (they are not exported into the enum’s scope), and
- not implicitly convertible to integer types.

So, (note the additional class keyword) …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
enum class CursorDirection { kLeft, kRight, kUp, kDown };
CursorDirection d = kLeft;                    // error: kLeft not in this scope
CursorDirection d2 = CursorDirection::kLeft;  // OK
int i = CursorDirection::kRight;              // error: no conversion
```

</div>

</div>

and, …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// OK: kLeft and kRight are local to each scoped enum
enum class PoliticalOrientation { kLeft, kCenter, kRight };
```

</div>

</div>

These simple changes eliminate the problems with plain enumerations, so enum class should be preferred in all new code.

Using a scoped enum does mean that you’ll have to explicitly cast to an integer type should you still want such a conversion (e.g., when logging an enumeration value, or when using bitwise operations on flag-like enumerators). Hashing with `std::hash` will continue to work though (e.g., `std::unordered_map<CursorDirection, int>`).

## Underlying Enumeration Types

C++11 also introduced the ability to specify the underlying type for both varieties of enumeration. Previously the underlying integer type of an enum was determined by examining the sign and magnitude of the enumerators, but now we can be explicit. For example, …

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// Use "int" as the underlying type for CursorDirection
enum class CursorDirection : int { kLeft, kRight, kUp, kDown };
```

</div>

</div>

Because this enumerator range is small, and if we wished to avoid wasting space when storing `CursorDirection` values, we could specify `char` instead.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// Use "char" as the underlying type for CursorDirection
enum class CursorDirection : char { kLeft, kRight, kUp, kDown };
```

</div>

</div>

The compiler will issue an error if an enumerator value exceeds the range of the underlying type.

## Conclusion

Prefer using `enum class` in new code. You’ll reduce namespace pollution, and you may avoid bugs in implicit conversions.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
enum class Parting { kSoLong, kFarewell, kAufWiedersehen, kAdieu };
```

</div>

</div>


