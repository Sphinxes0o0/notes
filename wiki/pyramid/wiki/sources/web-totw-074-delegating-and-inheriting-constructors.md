---
type: source
source-type: web
title: "Tip of the Week #74: Delegating and Inheriting Constructors"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/74
summary: "abseil C++ Tips of the Week #74: Delegating and Inheriting Constructors."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 1fc87deb68ac432168fbb22f754fa030
---

> 原文：<https://abseil.io/tips/74> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#74: Delegating and Inheriting Constructors

\
\

Originally posted as totw/74 on 2014-04-21

By Bradley White [(<span class="__cf_email__" cfemail="395b4e4e795e56565e555c175a5654">\[email protected\]</span>)](/cdn-cgi/l/email-protection#fc9e8b8bbc9b93939b9099d29f9391)

*“Delegating work works, provided the one delegating works, too.” – Robert Half*

When a class has multiple constructors there is often a need to perform similar initialization in each variant. To avoid code duplication, many older classes resort to defining a private `SharedInit()` method that is called from the constructors. For example:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class C {
 public:
  C(int x, string s) { SharedInit(x, s); }
  explicit C(int x) { SharedInit(x, ""); }
  explicit C(string s) { SharedInit(0, s); }
  C() { SharedInit(0, ""); }
 private:
  void SharedInit(int x, string s) { … }
};
```

</div>

</div>

C++11 provides a new mechanism, delegating constructors, for dealing with such situations more clearly by allowing one constructor to be defined in terms of another. It is also an efficiency gain if the class has members that are expensive to default-initialize.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class C {
 public:
  C(int x, string s) { … }
  explicit C(int x) : C(x, "") {}
  explicit C(string s) : C(0, s) {}
  C() : C(0, "") {}
};
```

</div>

</div>

Note that if you delegate to another constructor you cannot also use a member initialization list – all initialization is done by the delegated constructor. Don’t go overboard though. If all the shared code does is set members, separate member-initialization lists or in-class initializers are probably clearer than using delegating constructors. Use good judgement.

Aside: an object is not considered complete until the delegating constructor returns; in practice, this only matters if the constructors can throw, as they leave the delegated-from objects in an incomplete state.

Another, less common form of constructor code duplication occurs when extending the behavior of a multi-constructor class through a wrapper. For example, consider a “veneer” subclass of C that just adds a new member function.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class D : public C {
 public:
  void NewMethod();
};
```

</div>

</div>

But what of the constructors for D? We’d like to simply re-use those from C rather than writing out all the forwarding boilerplate, and C++11 allows for this via the new *inheriting constructors* mechanism.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class D : public C {
 public:
  using C::C;  // inherit all constructors from C
  void NewMethod();
};
```

</div>

</div>

This new form of “using” for constructors matches its previous use for member functions.

Note, however, that constructors should really only be inherited when the derived class does not add new data members that need to be initialized explicitly. Indeed, the style guide cautions against inheriting constructors unless the new members (if any) have in-class initialization.

So, go ahead and use C++11’s delegating and inheriting constructors when they reduce duplication, eliminate forwarding boilerplate, or otherwise make your classes simpler and clearer.


