---
type: source
source-type: web
title: "Tip of the Week #103: Flags Are Globals"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/103
summary: "abseil C++ Tips of the Week #103: Flags Are Globals."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: c4b207702ad138568422dce6aa61f988
---

> 原文：<https://abseil.io/tips/103> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#103: Flags Are Globals

\
\

*by [Matt Armstrong](/cdn-cgi/l/email-protection#deb3bfacb3adaaacb1b0b99eb9b1b1b9b2bbf0bdb1b3)*

Define flags at global scope in a `.cc` file. Declare them at most once in a corresponding `.h` file.

## Why Declare Things In Header Files?

Using header files is a reflex for most of us, so we may have forgotten why they are used:

1.  Declaring something in a header file makes it easy to `#include` elsewhere. The entire program sees the same declaration.
2.  Including this header in the `.cc` that defines the same entity ensures the definition matches declaration.
3.  The header file serves as documentation for a package’s public API. Using anything but a package’s public API is poor form.
4.  Including headers, instead of re-declaring entities, helps both tools and humans perform dependency analysis.

## Abseil Flags Are As Vulnerable As Any Other Global

You can do this incorrectly with no link-time error. First, place the following in a `.cc` file:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// Defining --my_flag in a .cc file.
ABSL_FLAG(std::string, my_flag, "", "My flag is a string.");
```

</div>

</div>

And the following, erroneous, declaration of the flag in a different `.cc` file (perhaps a test):

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// Declared in error: type should be std::string.
extern absl::Flag<int64> FLAGS_my_flag;
```

</div>

</div>

The program is ill-formed, and whatever happens is the result of [undefined behavior](http://en.cppreference.com/w/cpp/language/ub). In my test program, this code compiled, linked, and crashed when the flag was accessed.

## Recommendations

Design with command line flags as you would global variables.

1.  Avoid flags if you can. See http://abseil.io/tips/45.
2.  If you are using a flag to make a test easier to write, with no intent to ever set it in production, consider adding test-only APIs to your classes.
3.  Consider treating flags as private static variables. If other packages need to access them, wrap them in functions.
4.  Define your flags at global scope, not within a namespace, to get link errors when flag names conflict.
5.  If a flag is accessed in multiple files, declare it in one `.h` file corresponding to its definition.
6.  Use the `ABSL_FLAG(type, ...)` macro to define flags.

## In Conclusion

Flags are global variables. Use them judiciously. Use and declare them as you would any other global variable.


