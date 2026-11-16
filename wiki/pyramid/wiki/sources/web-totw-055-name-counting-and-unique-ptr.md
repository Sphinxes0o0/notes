---
type: source
source-type: web
title: "Tip of the Week #55: Name Counting and unique_ptr"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/55
summary: "abseil C++ Tips of the Week #55: Name Counting and unique_ptr."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: df3ddc49ac670006f41a4db18087263f
---

> 原文：<https://abseil.io/tips/55> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#55: Name Counting and unique_ptr

\
\

Originally published as totw/55 on 2013-09-12

*by Titus Winters [(<span class="__cf_email__" cfemail="8bffe2fffef8cbece4e4ece7eea5e8e4e6">\[email protected\]</span>)](/cdn-cgi/l/email-protection#a4d0cdd0d1d7e4c3cbcbc3c8c18ac7cbc9)*

Updated 2017-10-20

Quicklink: [abseil.io/tips/55](https://abseil.io/tips/55)

*“Though we may know Him by a thousand names, He is one and the same to us all.” - Mahatma Gandhi*

Colloquially, a “name” for a value is any value-typed variable (not a pointer, nor a reference), in any scope, that holds a particular data value. (For the spec-lawyers, if we say “name” we’re essentially talking about lvalues.) Because of `std::unique_ptr`’s specific behavioral requirements, we need to make sure that any value held in a `std::unique_ptr` only has one name.

It’s important to note that the C++ language committee picked a very apt name for `std::unique_ptr`. Any non-null pointer value stored in a `std::unique_ptr` must occur in only one `std::unique_ptr` at any time; the standard library is designed to enforce this. Many common problems compiling code that uses `std::unique_ptr` can be resolved by learning to recognize how to count the names for a `std::unique_ptr`: one is OK, but multiple names for the same pointer value are not.

Let’s count some names. At each line number, count the number of names alive at that point (whether in scope or not) that refer to a `std::unique_ptr` containing the same pointer. If you find any line with more than one name for the same pointer value, that’s an error!

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::unique_ptr<Foo> NewFoo() {
  return std::unique_ptr<Foo>(new Foo(1));
}

void AcceptFoo(std::unique_ptr<Foo> f) { f->PrintDebugString(); }

void Simple() {
  AcceptFoo(NewFoo());
}

void DoesNotBuild() {
  std::unique_ptr<Foo> g = NewFoo();
  AcceptFoo(g); // DOES NOT COMPILE!
}

void SmarterThanTheCompilerButNot() {
  Foo* j = new Foo(2);
  // Compiles, BUT VIOLATES THE RULE and will double-delete at runtime.
  std::unique_ptr<Foo> k(j);
  std::unique_ptr<Foo> l(j);
}
```

</div>

</div>

In `Simple()`, the unique pointer allocated with `NewFoo()` only ever has one name by which you could refer it: the name “f” inside `AcceptFoo()`.

Contrast this with `DoesNotBuild()`: the unique pointer allocated with `NewFoo()` has two names which refer to it: `DoesNotBuild()`’s “g” and `AcceptFoo()`’s “f”.

This is the classic uniqueness violation: at any given point in the execution, any value held by a `std::unique_ptr` (or more generally, any move-only type) can only be referred to by a single distinct name. Anything that looks like a copy introducing an additional name is forbidden and won’t compile:

<div class="language-text highlighter-rouge">

<div class="highlight">

```cpp
scratch.cc: error: call to deleted constructor of std::unique_ptr<Foo>'
  AcceptFoo(g);
```

</div>

</div>

Even if the compiler doesn’t catch you, the runtime behavior of `std::unique_ptr` will. Any time where you “outsmart” the compiler (see `SmarterThanTheCompilerButNot()`) and introduce multiple `std::unique_ptr` names, it may compile (for now) but you’ll get a run-time memory problem.

Now the question becomes: how do we remove a name? C++11 provides a solution for that as well, in the form of `std::move()`.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
 void EraseTheName() {
   std::unique_ptr<Foo> h = NewFoo();
   AcceptFoo(std::move(h)); // Fixes DoesNotBuild with std::move
}
```

</div>

</div>

The call to `std::move()` is effectively a name-eraser: conceptually you can stop counting “h” as a name for the pointer value. This now passes the distinct-names rule: on the unique pointer allocated with `NewFoo()` has a single name (“h”), and within the call to `AcceptFoo()` there is again only a single name (“f”). By using `std::move()` we promise that we will not read from “h” again until we assign a new value to it.

Name counting is a handy trick in modern C++ for those that aren’t expert in the subtleties of lvalues, rvalues, etc: it can help you recognize the possibility of unnecessary copies, and it will help you use `std::unique_ptr` properly. After counting, if you discover a point where there are too many names, use `std::move` to erase the no-longer-necessary name.


