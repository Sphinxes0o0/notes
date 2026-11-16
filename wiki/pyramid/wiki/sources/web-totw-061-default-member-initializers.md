---
type: source
source-type: web
title: "Tip of the Week #61: Default Member Initializers"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/61
summary: "abseil C++ Tips of the Week #61: Default Member Initializers."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 4b3a324a861fc1ebaf8c3ceab4f84b75
---

> 原文：<https://abseil.io/tips/61> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#61: Default Member Initializers

\
\

Originally posted as Totw \#61 on Nov 12, 2013

*by Michael Chastain [(<span class="__cf_email__" cfemail="85e8e0e6abe1e0f6eef1eaf5c5e2e8e4ece9abe6eae8">\[email protected\]</span>)](/cdn-cgi/l/email-protection#2c41494f0248495f4758435c6c4b414d4540024f4341)*

Updated October, 2016

## Declaring Default Member Initialization

A default member initializer declares a default value for a member upon construction and looks like this:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class Client {
 private:
  int chunks_in_flight_ = 0;
};
```

</div>

</div>

This default initializer propagates into all constructors for that class, even constructors that C++ synthesizes. Initializing members in this way is useful for classes with lots of data members, especially for types such as `bool`, `int`, `double`, and raw pointers. Non-static data members of these fundamental types often slip through the cracks and end up uninitialized. Non-static data members of any type may have initializers, though.

Default member initializers are also useful for declarations of simple structs with no user-written constructor:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
struct Options {
  bool use_loas = true;
  bool log_pii = false;
  int timeout_ms = 60 * 1000;
  std::array<int, 4> timeout_backoff_ms = { 10, 100, 1000, 10 * 1000 };
};
```

</div>

</div>

## Member Initialization Overrides

If a class constructor initializes a data member that already has a default initializer, the initializer in the constructor supersedes the default:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class Frobber {
 public:
  Frobber() : ptr_(nullptr), length_(0) { }
  Frobber(const char* ptr, size_t length)
    : ptr_(ptr), length_(length) { }
  Frobber(const char* ptr) : ptr_(ptr) { }
 private:
  const char* ptr_;
  // length_ has a non-static class member initializer
  const size_t length_ = strlen(ptr_);
};
```

</div>

</div>

This code is equivalent to the older code:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class Frobber {
 public:
  Frobber() : ptr_(nullptr), length_(0) { }
  Frobber(const char* ptr, size_t length)
    : ptr_(ptr), length_(length) { }
  Frobber(const char* ptr)
    : ptr_(ptr), length_(strlen(ptr_)) { }
 private:
  const char* ptr_;
  const size_t length_;
};
```

</div>

</div>

Note that the first and second `Frobber` constructors have initializers for their non-static variables; these two constructors will not use the default initializer for `length_`. The third `Frobber` constructor, however, does not have an initializer for `length_` so this constructor will use the default initializer for `length_`.

As always in C++, all non-static variables are initialized in the order of their declaration.

In the first 2 of the 3 `Frobber` constructors, the constructor provides an initializer for `length_`. The constructor initializer supersedes the default member initializer – the non-static class member initializer does not contribute to code generation for these constructors.

Note: Older documentation may refer to default member initializers as non-static data member initializers, abbreviated to NSDMIs.

## Conclusion

Default member initializers won’t make your program any faster. They will help reduce bugs from omissions, especially when someone adds a new constructor or a new data member.

Be careful not to confuse a non-static class member initializer with a static class member initializer:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class Alpha {
 private:
  static int counter_ = 0;
};
```

</div>

</div>

This is an older feature. `counter_` is static and this is a static declaration with an initializer. This is different from a non-static class member initializer, just as static member variables are different from non-static member variables.


