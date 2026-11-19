---
type: source
source-type: web
title: "Tip of the Week #59: Joining Tuples"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/59
summary: "abseil C++ Tips of the Week #59: Joining Tuples."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: bbe5bd0c6ebc59674a1b4d8009c2f45f
---

> 原文：<https://abseil.io/tips/59> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#59: Joining Tuples

\
\

Originally published as totw/59 on 2013-10-21

*By Greg Miller [(<span class="__cf_email__" cfemail="8ce6ebe1ccebe3e3ebe0e9a2efe3e1">\[email protected\]</span>)](/cdn-cgi/l/email-protection#6c060b012c0b03030b0009420f0301)*

Updated 2018-01-24

*“Now join your hands, and with your hands your hearts.” –Henry VI, William Shakespeare*

In March, 2013 we announced the new [string joining API](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_join.h) in [Tip \#36](/tips/36). The response to the new API was quite positive, and we worked to make the API even better. Topping the list of feature requests was the ability to join arbitrary lists of possibly heterogeneous data (I can only assume that Shakespeare was referring to joining a heterogeneous collection of hands and hearts). We didn’t go with the varargs or variadic template route, but we did add support for joining `std::tuple` objects, which addresses this need quite nicely. Simply create a `std::tuple` containing your heterogeneous data, and `absl::StrJoin()` will accept it just like any other container. Here are a few examples:

<div class="language-cpp highlighter-rouge">

<div class="highlight">

```cpp
auto tup = std::make_tuple(123, "abc", 0.456);
std::string s = absl::StrJoin(tup, "-");
s = absl::StrJoin(std::make_tuple(123, "abc", 0.456), "-");

int a = 123;
std::string b = "abc";
double c = 0.456;

// Works, but copies all arguments.
s = absl::StrJoin(std::make_tuple(a, b, c), "-");
// No copies, but only works with lvalues.
s = absl::StrJoin(std::tie(a, b, c), "-");
// No copies, and works with lvalues and rvalues.
s = absl::StrJoin(std::forward_as_tuple(123, MakeFoo(), c), "-");
```

</div>

</div>

As with joining any container, the elements of the tuple are formatted using an `absl::AlphaNumFormatter` by default, but you can specify a custom [join Formatter](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_join.h#L64) if your tuple contains elements that are not handled by the default formatter. To format a tuple with multiple custom element types, your custom `Formatter` object may contain multiple overloads of `operator()`.

For example:

<div class="language-cpp highlighter-rouge">

<div class="highlight">

```cpp
struct Foo {};
struct Bar {};

struct MyFormatter {
  void operator()(string* out, const Foo& f) const {
    out->append("Foo");
  }
  void operator()(string* out, const Bar& b) const {
    out->append("Bar");
  }
};

std::string s = absl::StrJoin(std::forward_as_tuple(Foo(), Bar()), "-",
                         MyFormatter());
EXPECT_EQ(s, "Foo-Bar");
```

</div>

</div>

The goal of the `absl::StrJoin()` API is to join any collection, range, list, or group of data using an intuitive and consistent syntax. We think joining `std::tuple` objects fits nicely with this goal and adds more flexibility to the API.


