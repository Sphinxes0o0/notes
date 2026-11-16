---
type: source
source-type: web
title: "Tip of the Week #134: `make_unique` and `private` Constructors."
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/134
summary: "abseil C++ Tips of the Week #134: make_unique` and `private` Constructors.."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: b232d03f9b8d8dd14a2bf96f300775cb
---

> 原文：<https://abseil.io/tips/134> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#134: `make_unique` and `private` Constructors.

\
\

Originally posted as TotW \#134 on May 10, 2017

*By Yitzhak Mandelbaum, Google Engineer*

Updated 2020-04-06

Quicklink: [abseil.io/tips/134](https://abseil.io/tips/134)

So, you read [Tip \#126](/tips/126) and are ready to leave `new` behind. Everything’s going fine until you try to use `std::make_unique` to construct an object with a private constructor, and it fails to compile. Let’s take a look at a concrete example of this problem to understand what went wrong. Then, we can discuss some solutions.

## Example: Manufacturing Widgets

You’re defining a class to represent widgets. Each widget has an identifier and those identifiers are subject to certain constraints. To ensure those constraints are always met, you declare the constructor of the `Widget` class private and provide users with a factory function, `Make`, for generating widgets with proper identifiers. (See [Tip \#42](/tips/42) for advice on why factory functions are preferable to initializer methods.)

```cpp

class Widget {
 public:
  static std::unique_ptr<Widget> Make() {
    return std::make_unique<Widget>(GenerateId());
  }

 private:
  Widget(int id) : id_(id) {}
  static int GenerateId();

  int id_;
}
```

When you try to compile, you get an error like this:

```cpp

error: calling a private constructor of class 'Widget'
    { return unique_ptr<_Tp>(new _Tp(std::forward<_Args>(__args)...)); }
                                 ^
note: in instantiation of function template specialization
'std::make_unique<Widget, int>' requested here
    return std::make_unique<Widget>(GenerateId());
                ^
note: declared private here
  Widget(int id) : id_(id) {}
  ^
```

While `Make` has access to the private constructor, `std::make_unique` does not! Note that this issue can also arise with friends. For example, a friend of `Widget` would have the same problem using `std::make_unique` to construct a `Widget`.

## Recommendations

We recommend either of these alternatives:

- Use `new` and `absl::WrapUnique`, but explain your choice. For example,

```cpp

    // Using `new` to access a non-public constructor.
    return absl::WrapUnique(new Widget(...));
```

- Consider whether the constructor may be safely exposed publicly. If so, make it public and document when direct construction is appropriate.

In many cases, marking a constructor private is over-engineering. In those cases, the best solution is to mark your constructors public and document their proper use. However, if your constructor needs to be private (say, to ensure class invariants), then use `new` and `WrapUnique`.

## Why Can’t I Just Friend `std::make_unique` (or `absl::make_unique`)?

You might be tempted to friend `std::make_unique` (or `absl::make_unique`), which would give it access to your private constructors. *This is a bad idea*, for a few reasons.

First, while a full discussion of friending practices is beyond the scope of this tip, a good rule of thumb is “no long-distance friendships”. Otherwise, you’re creating a competing declaration of the friend, one not maintained by the owner. See also the [style guide’s advice](https://google.github.io/styleguide/cppguide.html#Friends).

Second, notice that you are depending on an implementation detail of `make_unique`, namely that it directly calls `new`. If it is refactored so that it indirectly calls `new` – for example, in build modes using C++14 and later `absl::make_unique` is an alias for `std::make_unique`, and the friend declaration is useless.

Finally, by friending `make_unique`, you’ve allowed *anyone* to create your objects that way, so why not just declare your constructors public and avoid the problem altogether?

## What About `std::shared_ptr`?

The situation is somewhat different in the case of `std::shared_ptr`. There is no `absl::WrapShared` and the analog – `std::shared_ptr<T>(new T(...))` – involves two allocations, where `std::make_shared` can be done with one. If this difference is important, then consider the *passkey idiom*: have the constructor take a special token that only certain code can create. For example,

```cpp

class Widget {
  class Token {
   private:
    explicit Token() = default;
    friend Widget;
  };

 public:
  static std::shared_ptr<Widget> Make() {
    return std::make_shared<Widget>(Token{}, GenerateId());
  }

  Widget(Token, int id) : id_(id) {}

 private:
  static int GenerateId();

  int id_;
};
```

Note that we are providing an `explicit` defaulted constructor. This is needed for C++17 and earlier, as otherwise `Widget::Token` would be an aggregate and could be aggregate-initialized by `{}`, effectively bypassing the `private` access.

For a full discussion of the passkey idiom, consult either of these articles:

- [Passkey Idiom: More Useful Empty Classes](https://arne-mertz.de/2016/10/passkey-idiom/)
- [Passkey Idiom and Better Friendship in C++](http://www.spiria.com/en/blog/desktop-software/passkey-idiom-and-better-friendship-c)


