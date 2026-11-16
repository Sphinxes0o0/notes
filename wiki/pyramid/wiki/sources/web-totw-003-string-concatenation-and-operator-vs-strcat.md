---
type: source
source-type: web
title: "Tip of the Week #3: String Concatenation and `operator+` vs. `StrCat()`"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/3
summary: "abseil C++ Tips of the Week #3: String Concatenation and `operator+` vs. `StrCat()."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 72c7e0b759c5a399e19433f36ea8be86
---

> 原文：<https://abseil.io/tips/3> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#3: String Concatenation and `operator+` vs. `StrCat()`

\
\

Originally posted as TotW \#3 on May 11, 2012

Updated 2022-11-16

Quicklink: [abseil.io/tips/3](https://abseil.io/tips/3)

Users are often surprised when a reviewer says, “Don’t use the string concatenation operator, it’s not that efficient.” How can it be that `string::operator+` is inefficient? Isn’t it hard to get that wrong?

It turns out, such inefficiency isn’t clear cut. These two snippets have close to the same execution time, in practice:

```cpp

std::string foo = LongString1();
std::string bar = LongString2();
std::string foobar = foo + bar;

std::string foo = LongString1();
std::string bar = LongString2();
std::string foobar = absl::StrCat(foo, bar);
```

However, the same is not true for these two snippets:

```cpp

std::string foo = LongString1();
std::string bar = LongString2();
std::string baz = LongString3();
std::string foobarbaz = foo + bar + baz;

std::string foo = LongString1();
std::string bar = LongString2();
std::string baz = LongString3();
std::string foobarbaz = absl::StrCat(foo, bar, baz);
```

The reason these two cases differ can be understood when we pick apart what is happening in the expression `foo + bar + baz`. Since there are no overloads for three-argument operators in C++, this operation is necessarily going to make two calls to `string::operator+`. And between those two calls, the operation will construct (and store) a temporary string. So \`std::string foobarbaz = foo + bar

- baz\` is really equivalent to:

```cpp

std::string temp = foo + bar;
std::string foobarbaz = std::move(temp) + baz;
```

Specifically, note that the contents of `foo` and `bar` must be copied to a temporary location before they are placed within `foobarbaz`. (For more on `std::move`, see [Tip \#77](/tips/77).)

C++11 at least allows the second concatenation to happen without creating a new string object: `std::move(temp) + baz` is equivalent to `std::move(temp.append(baz))`. However, it’s possible that the buffer initially allocated for the temporary won’t be large enough to hold the final string, in which case a reallocation (and another copy) will be required. As a result, in the worst case, chains of `n` string concatenations require O(n) reallocations.

It is better instead to use `absl::StrCat()`, a nice helper function from google3/third_party/absl/strings/str_cat.h that calculates the necessary string length, reserves that size, and concatenates all of the input data into the output - a well-optimized O(n). Similarly, for cases like:

```cpp

foobar += foo + bar + baz;
```

use `absl::StrAppend()`, which performs similar optimizations:

```cpp

absl::StrAppend(&foobar, foo, bar, baz);
```

In addition, `absl::StrCat()` and `absl::StrAppend()` operate on types other than just string types: you can use `absl::StrCat`/`absl::StrAppend` to convert `int32_t`, `uint32_t`, `int64_t`, `uint64_t`, `float`, `double`, `const char*`, and `string_view`, like this:

```cpp

std::string foo = absl::StrCat("The year is ", year);
```

For additional information, see [absl::StrCat() and absl::StrAppend() for String Concatenation](https://abseil.io/docs/cpp/guides/strings#abslstrcat-and-abslstrappend-for-string-concatenation).


