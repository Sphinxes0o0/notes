---
type: source
source-type: web
title: "Tip of the Week #65: Putting Things in their Place"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/65
summary: "abseil C++ Tips of the Week #65: Putting Things in their Place."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 95881d6c92a2b890cb17de532bca4ade
---

> 原文：<https://abseil.io/tips/65> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#65: Putting Things in their Place

\
\

Originally posted as totw/65 on 2013-12-12

By Hyrum Wright [(<span class="__cf_email__" cfemail="076f7e75726a476f7e75726a70756e606f7329687560">\[email protected\]</span>)](/cdn-cgi/l/email-protection#9cf4e5eee9f1dcf4e5eee9f1ebeef5fbf4e8b2f3eefb)

*“Let me ’splain. No, there is too much. Let me sum up.” –Inigo Montoya*

C++11 added a new way to insert elements into standard containers: the `emplace()` family of methods. These methods create an object directly within a container, instead of creating a temporary object and then copying or moving that object into the container. Avoiding these copies is more efficient for almost all objects, and makes it easier to store move-only objects (such as `std::unique_ptr`) in standard containers.

## The Old Way and the New Way

Let’s look at a simple example using vectors to contrast the two styles. The first example uses pre-C++11 code:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class Foo {
 public:
  Foo(int x, int y);
  …
};

void addFoo() {
  std::vector<Foo> v1;
  v1.push_back(Foo(1, 2));
}
```

</div>

</div>

Using the older `push_back()` method, two `Foo` objects are constructed: the temporary argument and the object in the vector that is move-constructed from the temporary.

We can instead use C++11’s `emplace_back()` and only one object will be constructed directly within the memory of the vector. Since the “emplace” family of functions forward their arguments to the underlying object’s constructor, we can provide the constructor arguments directly, obviating the need to create a temporary `Foo`:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
void addBetterFoo() {
  std::vector<Foo> v2;
  v2.emplace_back(1, 2);
}
```

</div>

</div>

## Using Emplace Methods for Move-Only Operations

So far, we’ve looked at cases where emplace methods improve performance, but they also make previously impossible code feasible, such as storing move-only types like `std::unique_ptr` within containers. Consider this snippet:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::vector<std::unique_ptr<Foo>> v1;
```

</div>

</div>

How would you insert values into this vector? One way would be to use `push_back()` and construct the value directly within its argument:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
v1.push_back(std::unique_ptr<Foo>(new Foo(1, 2)));
```

</div>

</div>

This syntax works, but can be a bit unwieldy. Unfortunately, the traditional way of getting around this confusion is fraught with complexity:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
Foo *f2 = new Foo(1, 2);
v1.push_back(std::unique_ptr<Foo>(f2));
```

</div>

</div>

This code compiles, but it leaves ownership of the raw pointer unclear until the insertion. What’s worse, the vector now owns the object, but `f2` still remains valid, and could accidentally be deleted later on. To an uninformed reader, this ownership pattern can be confusing, particularly if construction and insertion are not sequential events as above.

Other solutions won’t even compile, because `unique_ptr` isn’t copyable:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::unique_ptr<Foo> f(new Foo(1, 2));
v1.push_back(f);             // Does not compile!
v1.push_back(new Foo(1, 2)); // Does not compile!
```

</div>

</div>

Using emplace methods can make it more intuitive to insert the object while it’s being created. In other cases, if you need to move the `unique_ptr` into the vector, you can:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::unique_ptr<Foo> f(new Foo(1, 2));
v1.emplace_back(new Foo(1, 2));
v1.push_back(std::move(f));
```

</div>

</div>

By combining emplace with a standard iterator, you can also insert the object at an arbitrary location in the vector:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
v1.emplace(v1.begin(), new Foo(1, 2));
```

</div>

</div>

That said, in practical terms we wouldn’t want to see these ways to construct a `unique_ptr` - Use `std::make_unique` (from C++14) or `absl::make_unique` (if you’re still on C++11).

## Conclusion

We’ve used vector as an example in this Tip, but emplace methods are also available for maps, lists and other STL containers. When combined with `unique_ptr`, emplace allows for good encapsulation and makes the ownership semantics of heap-allocated objects clear in ways that weren’t possible before. Hopefully this has given you a feel for the power of the new emplace family of container methods, and a desire to use them where appropriate in your own code.


