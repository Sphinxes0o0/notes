---
type: source
source-type: web
title: "Tip of the Week #215: Stringifying Custom Types with `AbslStringify()`"
author: "Phoebe Liang"
date: 2012
url: https://abseil.io/tips/215
summary: "abseil C++ Tips of the Week #215: Stringifying Custom Types with `AbslStringify()."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 6f67f0bac995ada5b40d24cf149bd4c8
---

> 原文：<https://abseil.io/tips/215> · 作者：Phoebe Liang · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#215: Stringifying Custom Types with `AbslStringify()`

\
\

Originally posted as TotW \#215 on November 2, 2022

*By [Phoebe Liang](/cdn-cgi/l/email-protection#65150d0a000700090c040b0225020a0a0209004b060a08)*

Updated 2022-11-16

Quicklink: [abseil.io/tips/215](https://abseil.io/tips/215)

Abseil now contains a new lightweight mechanism, `AbslStringify()`, that allows users to format user-defined types as strings. User-defined types that are extended using `AbslStringify()` work out of the box with `absl::StrFormat`, `absl::StrCat` and `absl::Substitute`.

As with most type extensions, you should own the type you wish to extend.

Let’s say that we have a simple `Point` struct:

```cpp

struct Point {
  int x;
  int y;
};
```

If we want a `Point` to be formattable with `absl::StrFormat()`, `absl::StrCat()` and `absl::Substitute()`, we add a `friend` function template named `AbslStringify()`:

```cpp

struct Point {
  template <typename Sink>
  friend void AbslStringify(Sink& sink, const Point& p) {
    absl::Format(&sink, "(%d, %d)", p.x, p.y);
  }

  int x;
  int y;
};
```

Note: `AbslStringify()` utilizes a generic “sink” buffer to construct its string. This sink has an interface similar to `absl::FormatSink`, but does not support `PutPaddedString()`.

Now `absl::StrCat("The point is ", p)` and `absl::Substitute("The point is $0", p)` will just work.

Note: `absl::StrFormat()` also provides [a more customizable extension point](https://abseil.io/docs/cpp/guides/format#user-defined-formats) `AbslFormatConvert()` that is not supported by `absl::StrCat()`.

## Type Deduction with the `%v` Specifier

But what if we want to format our type using `absl::StrFormat()`? `absl::StrFormat()`’s existing type specifiers don’t support user-defined types extended with `AbslStringify()`, so we would have to do something like this:

```cpp

absl::StrFormat("The point is (%d, %d)", p.x, p.y)
```

This is obviously not ideal. It doesn’t make use of the extension at all and it duplicates the format string used in the `AbslStringify()` definition. Instead, we can use the new type specifier `%v`:

```cpp

absl::StrFormat("The point is %v", p)
```

`%v` uses type deduction to format an argument. `%v` supports the formatting of most primitive types, as well as any types extended using `AbslStringify()`. You can think of `%v` as a generic way to format a “value” of any type that `absl::StrFormat()` can deduce. `%v` can also be used directly within `AbslStringify()` definitions.

The `%v` specifier deduces the following types:

- `d` for signed integral values
- `u` for unsigned integral values
- `g` for floating point values
  - `double`
  - `float`
  - `long double`
- `s` for string values
  - `std::string`
  - `absl::string_view`
  - `std::string_view`
  - `absl::Cord`

NOTE: `const char*` is **not** supported. See below for more information.

Some examples:

```cpp

absl::StrFormat("%v", std::string{"hello"})    -> "hello"
absl::StrFormat("%v", 42)    -> "42"
absl::StrFormat("%v", uint64_t{16})    -> "16"
absl::StrFormat("%v", 1.6)  -> "1.6"
absl::StrFormat("%v", true) -> "true"
```

### Types With Special Handling

`%v` intentionally does not support `char` and `const char*` due to ambiguity in the desired output format. Boolean values are printed as `"true"` and `"false"` rather than `"1"` and `"0"`, which is how `absl::StrFormat()` and `absl::StrCat()` print booleans otherwise.

## Integration With Other Libraries

`AbslStringify()` has additional support throughout other Abseil libraries.

### Logging

Types that define `AbslStringify()` are directly loggable:

```cpp

struct Point {
  template <typename Sink>
  friend void AbslStringify(Sink& sink, const Point& p) {
    absl::Format(&sink, "(%v, %v)", p.x, p.y);
  }

  int x = 10;
  int y = 20;
};

Point p;

LOG(INFO) << p;
```

This code will produce a message in the logs like:

```cpp

I0926 09:00:00.000000   12345 main.cc:10] (10, 20)
```

It is recommended that custom types be made loggable by implementing `AbslStringify()` rather than `operator<<` as it is a universal stringification extension that also enables `absl::StrFormat`, `absl::StrCat` and `absl::Substitute` support.

### Protocol Buffer Types

Protocol buffers are formattable using `AbslStringify()`. Since `AbslStringify()` provides an overall smoother user experience over `DebugString()`, it is recommended that users use `AbslStringify()` when formatting protos as strings.

```cpp

message MyProto {
  optional string my_string = 1
}

MyProto my_proto;
my_proto.set_my_string("hello world");

absl::StrCat("My proto is: ", my_proto);
absl::StrFormat("My proto is: %v", my_proto);
LOG(INFO) << my_proto;
```

## Closing Words

Aside from user-defined types where its use is required, the `%v` type specifier is intended for use in cases where the precise formatting is not important. It is essentially a catch-all “just print it in a human readable manner” specifier. If you require any other guarantees beyond that, please use one of the more specific type specifiers.


