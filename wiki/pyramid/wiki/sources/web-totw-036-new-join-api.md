---
type: source
source-type: web
title: "Tip of the Week #36: New Join API"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/36
summary: "abseil C++ Tips of the Week #36: New Join API."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: dac8eebf57e4364ca8317848846ced1a
---

> 原文：<https://abseil.io/tips/36> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#36: New Join API

\
\

Originally published as totw/36 on 2013-03-21

*By Greg Miller [(<span class="__cf_email__" cfemail="d6bcb1bb96b1b9b9b1bab3f8b5b9bb">\[email protected\]</span>)](/cdn-cgi/l/email-protection#fc969b91bc9b93939b9099d29f9391)*

Updated 2018-01-24

*“I got a good mind to join a club and beat you over the head with it.” – Groucho Marx*

Many of you asked for a new joining API and we heard you. We now have one joining function to replace them all, and it is spelled `absl::StrJoin()`. You simply give it a collection of objects to be joined and a separator string, and it does the rest. It will work with collections of `std::string`, `absl::string_view`, `int`, `double` – any type that `absl::StrCat()` supports. If you need to join a type that will not `StrCat()`, you can also provide a custom `Formatter` for that type; we’ll see below how the use of a `Formatter` will let us nicely join a map.

Now for some quick examples:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::vector<std::string> v = {"a", "b", "c"};
std::string s = absl::StrJoin(v, "-");
// s == "a-b-c"

std::vector<absl::string_view> v = {"a", "b", "c"};
std::string s = absl::StrJoin(v.begin(), v.end(), "-");
// s == "a-b-c"

std::vector<int> v = {1, 2, 3};
std::string s = absl::StrJoin(v, "-");
// s == "1-2-3"

const int a[] = {1, 2, 3};
std::string s = absl::StrJoin(a, "-");
// s == "1-2-3"
```

</div>

</div>

The following example passes a `Formatter` argument to format the pairs in a map, using a different separator. This makes the output nice and readable.

<div class="language-cpp highlighter-rouge">

<div class="highlight">

```cpp
std::map<std::string, int> m = {{"a", 1}, {"b", 2}, {"c", 3}};
std::string s = absl::StrJoin(m, ";", absl::PairFormatter("="));
// s == "a=1;b=2;c=3"
```

</div>

</div>

You can also pass a C++ lambda expression as a `Formatter`.

<div class="language-cpp highlighter-rouge">

<div class="highlight">

```cpp
std::vector<Foo> foos = GetFoos();

std::string s = absl::StrJoin(foos, ", ", [](std::string* out, const Foo& foo) {
  absl::StrAppend(out, foo.ToString());
});
```

</div>

</div>

Please refer to [absl/strings/str_join.h](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_join.h) for more details.


