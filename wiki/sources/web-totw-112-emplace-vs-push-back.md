---
type: source
source-type: web
title: "Tip of the Week #112: emplace vs. push_back"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/112
summary: "abseil C++ Tips of the Week #112: emplace vs. push_back."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 2548c6947f1fff43449b8e75819e0c7c
---

> 原文：<https://abseil.io/tips/112> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#112: emplace vs. push_back

\
\

Originally posted as totw/112 on 2016-02-25

By Geoff Romer [(<span class="__cf_email__" cfemail="2f485d40424a5d6f48404048434a014c4042">\[email protected\]</span>)](/cdn-cgi/l/email-protection#4126332e2c243301262e2e262d246f222e2c)

Revised 2017-08-30

*“The less we use our power, the greater it will be.” — Thomas Jefferson*

As you may already know (and if not, [TotW 65](/tips/65)), C++11 introduced a powerful new way to insert items into containers: `emplace` methods. These let you construct an object in-place inside the container, using any of the object’s constructors. That includes the move and copy constructors, so it turns out any time you could use a `push` or `insert` method, you can use an `emplace` method instead, with no other changes:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::vector<string> my_vec;
my_vec.push_back("foo");     // This is OK, so...
my_vec.emplace_back("foo");  // This is also OK, and has the same result

std::set<string> my_set;
my_set.insert("foo");        // Same here: any insert call can be
my_set.emplace("foo");       // rewritten as an emplace call.
```

</div>

</div>

This raises an obvious question: which one should you use? Should we perhaps just discard `push_back()` and `insert()`, and use `emplace` methods all the time?

Let me answer that question by asking another: what do these two lines of code do?

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
vec1.push_back(1<<20);
vec2.emplace_back(1<<20);
```

</div>

</div>

The first line is quite straightforward: it adds the number 1048576 to the end of the vector. The second, however, is not so clear. Without knowing the type of the vector, we don’t know what constructor it’s invoking, so we can’t really say what that line is doing. For example, if `vec2` is a `std::vector<int>`, that line merely adds 1048576 to the end, as with the first line, but if `vec2` is a `std::vector<std::vector<int>>`, that second line constructs a `vector` of over a million elements, allocating several megabytes of memory in the process.

Consequently, if you have a choice between `push_back()` and `emplace_back()` with the same arguments, your code will tend to be more readable if you choose `push_back()`, because `push_back()` expresses your intent more specifically. Choosing `push_back()` is also safer: suppose you have a `std::vector<std::vector<int>>` and you want to append a number to the end of the first `vector`, but you accidentally forget the subscript. If you write `my_vec.push_back(2<<20)`, you’ll get a compile error and you’ll quickly spot the problem. On the other hand, if you write `my_vec.emplace_back(2<<20)`, the code will compile, and you won’t notice any problems until run-time.

Now, it’s true that when implicit conversions are involved, `emplace_back()` can be somewhat faster than `push_back()`. For example, in the code that we began with, `my_vec.push_back("foo")` constructs a temporary `string` from the string literal, and then moves that string into the container, whereas `my_vec.emplace_back("foo")` just constructs the `string` directly in the container, avoiding the extra move. For more expensive types, this may be a reason to use `emplace_back()` instead of `push_back()`, despite the readability and safety costs, but then again it may not. Very often the performance difference just won’t matter. As always, the rule of thumb is that you should avoid “optimizations” that make the code less safe or less clear, unless the performance benefit is big enough to show up in your application benchmarks.

So in general, if both `push_back()` and `emplace_back()` would work with the same arguments, you should prefer `push_back()`, and likewise for `insert()` vs. `emplace()`.


