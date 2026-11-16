---
type: source
source-type: web
title: "Tip of the Week #131: Special Member Functions and \`= default\`"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/131
summary: "abseil C++ Tips of the Week #131: Special Member Functions and \`= default\."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 8bc7a2e28f98271171120eb718770767
---

> 原文：<https://abseil.io/tips/131> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#131: Special Member Functions and \`= default\`

\
\

Originally posted as totw/131 on 2017-03-24

By James Dennett [(<span class="__cf_email__" cfemail="3a505e5f54545f4e4e7a5d55555d565f14595557">\[email protected\]</span>)](/cdn-cgi/l/email-protection#bed4dadbd0d0dbcacafed9d1d1d9d2db90ddd1d3)

Since the beginning of time, C++ has supported compiler-declared versions of some so-called *special member functions*: the default constructor, destructor, copy constructor and copy assignment operators. C++11 added move construction and move assignment to the list, and added syntax (`=default` and `=delete`) to give control over when those defaults are declared and defined.

## What Does `=default` Do, and Why Would We Use It?

Writing `=default` is our way to tell the compiler “do what you would normally have done for this special member function”. Why might we want to do this rather than writing an implementation by hand or leaving the compiler to declare one for us?

- We can change the access level (e.g., make a constructor `protected` instead of `public`), make a destructor virtual, or reinstate a function that would be suppressed (e.g., a default constructor for a class that has other user-declared constructors) and still get the compiler to generate the function for us.
- Compiler-defined copy and move operations don’t need maintenance every time members are added or removed, if copying/moving the members is sufficient.
- Compiler-provided special member functions can be *trivial* (when all of the operations they invoke are themselves trivial), which can make them faster and safer.
- Types with defaulted constructors can be *aggregates*, and hence support *aggregate initialization*, whereas those with user-provided constructors cannot.
- Explicitly declaring a defaulted member gives us a place to document the semantics of the resulting function.
- In a class template, `=default` is a simple way to declare an operation conditionally, based on whether some underlying type provides it.

When we use `=default` on the initial declaration of a special member function, the compiler will check whether it can synthesize an inline definition for that function. If it can, it does. If it can’t, the function is actually declared as *deleted*, just as if we’d written `=delete`. That’s just what we’d need for transparently wrapping a class (say, if we’re defining a class template), but it can be surprising to readers.

If a function’s initial declaration uses `=default`, or if the compiler declares a special member function that is not user-declared, an appropriate `noexcept` specification is deduced, potentially allowing faster code.

## How Does It Work?

Before C++11, if we needed a default constructor and already had other constructors, we’d have written one as:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class A {
 public:
  A() {}  // User-provided, non-trivial constructor makes A a non-aggregate.
};
```

</div>

</div>

From C++11 onwards we have more options.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class C {
 public:
  C() = default;  // misleading: C has a deleted default constructor
 private:
  const int i;  // const => must always be initialized.
};

class D {
 public:
  D() = default;  // unsurprising, but not explicit: D has a default constructor
 private:
  std::unique_ptr<int> p;  // std::unique_ptr has a default constructor
};
```

</div>

</div>

Clearly we shouldn’t write code like `class C`: in a non-template, use `=default` only if you intend the class to support the operation (and then test that it does). *`clang-tidy`* includes a check for this.

When `=default` is used *after* the first declaration of a special member function (i.e., outside of the class), it has a simpler meaning: it tells the compiler to define the function, and to give an error if it is unable to do so. When `=default` is used outside of the class, the defaulted function will not be trivial: triviality is determined by the first declaration (so that all clients agree on whether the operation is trivial or not).

If you don’t need your class to be an aggregate and you don’t need the constructor to be trivial then defaulting the constructor outside of the class definition, like examples `E` and `F` below, is often a good choice. Its meaning is clear to readers, and is checked by the compiler. For the special case of defaulting a *default* constructor or a destructor we could write `{}` instead of `=default`, but for other defaulted operations the compiler-generated implementation is less simple, and for consistency it’s good to write `=default` in all applicable cases.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class E {
 public:
  E();  // promises to have a default constructor, but...
 private:
  const int i;  // const => must always be initialized.
};
inline E::E() = default;  // compilation error here: would not initialize `i`

class F {
 public:
  F();  // promises to have a default constructor
 private:
  std::unique_ptr<int> p;  // std::unique_ptr has a default constructor
};
inline F::F() = default;  // works as expected
```

</div>

</div>

## Recommendations

Prefer `=default` over writing an equivalent implementation by hand, even if that implementation is just `{}`. Optionally, omit `=default` from the initial declaration and provide a separate defaulted implementation.

Be cautious about defaulting move operations. Moved-from objects must still satisfy the invariants of their type, and the default implementations will usually not preserve relationships between fields.

Outside of templates, write `=delete` instead if `=default` wouldn’t provide an implementation.


