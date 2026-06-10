---
type: source
source-type: web
title: "Tip of the Week #24: Copies, Abbrv."
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/24
summary: "abseil C++ Tips of the Week #24: Copies, Abbrv.."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: e5b1fbc3b7749080328957b5f2ecfd4a
---

> 原文：<https://abseil.io/tips/24> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#24: Copies, Abbrv.

\
\

Originally posted as TotW \#24 on Nov 26, 2012

*by Titus Winters, [(<span class="__cf_email__" cfemail="2d594459585e6d4a42424a4148034e4240">\[email protected\]</span>)](/cdn-cgi/l/email-protection#1b6f726f6e685b7c767a727735787476) and Chandler Carruth [(<span class="__cf_email__" cfemail="701318111e141c15021330171f1f171c155e131f1d">\[email protected\]</span>)](/cdn-cgi/l/email-protection#b6d5ded7d8d2dad3c4d5f6d1d9d9d1dad398d5d9db)*

*“To copy others is necessary, but to copy oneself is pathetic.” - Pablo Picasso*

Note: see also [TotW \#55](/tips/55) and [TotW \#77](/tips/77) for guidance on name counting and copies vs. moves.

## One Name, No Copy; Two Names, Two Copies

When evaluating whether copies get made within any given scope (including cases triggering RVO), check how many names your data refers to.

**You will have two copies of the data at any point where you have two live names for those copies.** To a good first approximation, the compiler will (and often must) elide copies in all other cases.

Between the move semantics of STL containers (introduced automatically with the switch to C++11) and copy constructor elision by the compiler, we are rapidly converging on this rule providing not merely a lower bound on the number of copies, but a guarantee. If your benchmarks show that more copies are being made, it is **likely a compiler bug**; your compiler probably needs a fix.

So if your code is structured such that there are two names for the data at some point during the execution, you should expect a copy. If you avoid introducing a name which could possibly refer to the data, you’ll help ensure the compiler can remove the copy.

## Examples

Let’s look at some examples of how this works in practice:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::string build();

std::string foo(std::string arg) {
  return arg;  // no copying here, only one name for the data “arg”.
}

void bar() {
  std::string local = build();  // only 1 instance -- only 1 name

  // no copying, a reference won’t incur a copy
  std::string& local_ref = local;

  // one copy operation, there are now two named collections of data.
  std::string second = foo(local);
}
```

</div>

</div>

Most of the time, none of this matters. It is far more important to ensure that your code is readable and consistent, rather than worrying about copies and performance. As always: profile before you optimize. But, if you find yourself writing code from scratch – and can provide a clean and consistent API that returns its values – don’t discount code that seems like it would make copies: everything you learned about copies in C++ a decade ago is wrong.


