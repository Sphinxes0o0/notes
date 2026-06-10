---
type: source
source-type: web
title: "Tip of the Week #10: Splitting Strings, not Hairs"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/10
summary: "abseil C++ Tips of the Week #10: Splitting Strings, not Hairs."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 7879c9e6be34d48290ed10d806d1e80e
---

> 原文：<https://abseil.io/tips/10> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#10: Splitting Strings, not Hairs

\
\

Originally published as totw/10 on 2012-08-16

*By Greg Miller [(<span class="__cf_email__" cfemail="9af0fdf7dafdf5f5fdf6ffb4f9f5f7">\[email protected\]</span>)](/cdn-cgi/l/email-protection#d1bbb6bc91b6bebeb6bdb4ffb2bebc)*

Updated 2018-01-24

*I tend to have an odd split in my mind. –John Cleese*

Splitting a string into substrings is a common task in any general-purpose programming language, and C++ is no exception. When the need arose at Google, many engineers found themselves wading through a morass of splitting functions in organically grown header files. You’d have hunted for the magical combination of input parameters, output parameters, and semantics that satisfies your need. After studying 50+ functions in a 600+ line header, you may have finally decided on something as tortuously named as `SplitStringViewToDequeOfStringAllowEmpty()`.

To address this, the C++ Library Team implemented a new API for splitting strings, available for use in [absl/strings/str_split.h](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_split.h)

The new API replaced many of these splitting functions with a single `absl::StrSplit()` function. This function takes an input string to be split and a delimiter on which to split the string as arguments. `absl::StrSplit()` adapts the returned collection to the type specified by the caller. `absl::StrSplit()`’s implementation is efficient because `absl::string_view`s are used internally; no copies are made unless the caller explicitly requests to store the results in a collection of string objects (which copy their data).

Enough talk, let’s see some examples:

<div class="language-plaintext highlighter-rouge">

<div class="highlight">

```cpp
// Splits on commas. Stores in vector of string_view (no copies).
std::vector<absl::string_view> v = absl::StrSplit("a,b,c", ',');

// Splits on commas. Stores in vector of string (data copied once).
std::vector<std::string> v = absl::StrSplit("a,b,c", ',');

// Splits on literal string "=>" (not either of "=" or ">")
std::vector<absl::string_view> v = absl::StrSplit("a=>b=>c", "=>");

// Splits on any of the given characters (',' or ';')
using absl::ByAnyChar;
std::vector<std::string> v = absl::StrSplit("a,b;c", ByAnyChar(",;"));

// Stores in various containers (also works w/ absl::string_view)
std::set<std::string> s = absl::StrSplit("a,b,c", ',');
std::multiset<std::string> s = absl::StrSplit("a,b,c", ',');
std::list<std::string> li = absl::StrSplit("a,b,c", ',');

// Equiv. to the mythical SplitStringViewToDequeOfStringAllowEmpty()
std::deque<std::string> d = absl::StrSplit("a,b,c", ',');

// Yields "a"->"1", "b"->"2", "c"->"3"
std::map<std::string, std::string> m = absl::StrSplit("a,1,b,2,c,3", ',');
```

</div>

</div>

For more information, take a look at [absl/strings/str_split.h](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_split.h) for details about how to use the Split API and [absl/strings/str_split_test.cc](https://github.com/abseil/abseil-cpp/blob/master/absl/strings/str_split_test.cc) for some more examples.

Thanks for reading. Now I really gotta split…


