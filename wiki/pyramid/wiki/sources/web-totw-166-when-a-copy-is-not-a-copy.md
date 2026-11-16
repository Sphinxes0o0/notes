---
type: source
source-type: web
title: "Tip of the Week #166: When a Copy is not a Copy"
author: "Richard Smith"
date: 2012
url: https://abseil.io/tips/166
summary: "abseil C++ Tips of the Week #166: When a Copy is not a Copy."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 9a637225a825c6dd076bd167746db5aa
---

> 原文：<https://abseil.io/tips/166> · 作者：Richard Smith · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#166: When a Copy is not a Copy

\
\

Originally posted as TotW \#166 on August 28, 2019

*By [Richard Smith](/cdn-cgi/l/email-protection#f2809b919a938096819f9b869ab2959d9d959e97dc919d9f)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/166](https://abseil.io/tips/166)

*“Entia non sunt multiplicanda praeter necessitatem.” (“Entities should not be multiplied without necessity”) – William of Ockham*

*“If you don’t know where you’re going, you’re probably going wrong.” – Terry Pratchett*

## Overview

Starting in C++17, objects are created “in place” when possible.

```cpp

class BigExpensiveThing {
 public:
  static BigExpensiveThing Make() {
    // ...
    return BigExpensiveThing();
  }
  // ...
 private:
  BigExpensiveThing();
  std::array<OtherThing, 12345> data_;
};

BigExpensiveThing MakeAThing() {
  return BigExpensiveThing::Make();
}

void UseTheThing() {
  BigExpensiveThing thing = MakeAThing();
  // ...
}
```

How many times does this copy or move a `BigExpensiveThing`?

Prior to C++17, the answer was [up to](/tips/117) three: one for each `return` statement, and one more when initializing `thing`. This makes some sense: each function potentially puts the `BigExpensiveThing` in a different place, so a move may be needed in order to put the value where the ultimate caller wants it. In practice, however, the object was always constructed “in place” in the variable `thing`, with no moves being performed, and the C++ language rules permitted these move operations to be “elided” to facilitate this optimization.

Since C++17, this code is guaranteed to perform zero copies or moves. In fact, the above code is valid even if `BigExpensiveThing` is not moveable. The constructor call in `BigExpensiveThing::Make` directly constructs the local variable `thing` in `UseTheThing`.

So what’s going on?

When the compiler sees an expression like `BigExpensiveThing()`, it does not immediately create a temporary object. Instead, it treats that expression as instructions for how to initialize some eventual object, but defers creating (formally, “materializing”) a temporary object for as long as possible.

Generally, creation of an object is deferred until the object is given a name. The named object (`thing` in the above example) is directly initialized using the instructions found by evaluating the initializer. If the name is a reference, a temporary object will be materialized to hold the value.

As a consequence, objects are constructed directly in the right place, instead of being constructed somewhere else and then copied. This behavior is sometimes referred to as “guaranteed copy elision”, but that’s inaccurate: there was never a copy in the first place.

All you need to know is: objects are not copied until after they are first given a name. There is no extra cost in returning by value.

(Even after being given a name, local variables might still not be copied when returned from a function, due to the Named Return Value Optimization. See [Tip 11](/tips/11) for details.)

## Gritty Details: When Unnamed Objects Are Copied

There are two corner cases where a use of an object with no name results in a copy anyway:

- Constructing base classes: in the base class initializer list of a constructor, copies will be made even when constructing from an unnamed expression of the base class type. This is because classes may have a somewhat different layout and representation when used as base classes (due to virtual base classes and vpointer values), so initializing base classes directly may not result in a correct representation.

```cpp

class DerivedThing : public BigExpensiveThing {
 public:
  DerivedThing() : BigExpensiveThing(MakeAThing()) {}  // might copy data_
};
```

- Passing or returning small trivial objects: when a sufficiently small object that is trivially copyable is passed to or returned from a function, it may be passed in registers, and hence may have a different address before and after it is passed.

```cpp

struct Strange {
  int n;
  int *p = &n
};
void f(Strange s) {
  CHECK(s.p == &s.n);  // might fail
}
void g() { f(Strange{0}); }
```

## Gritty Details: Value Category

There are two flavors of expression in C++:

- Those that produce a value, such as `1`, or `MakeAThing()` – expressions that you might consider to have a non-reference type.
- Those that produce the location of some existing object, such as `s` or `thing.data_[5]` – expressions that you might consider to have a reference type.

This division is called the “value category”; the former are *prvalues* and the latter are *glvalues*. When we talked about objects without a name above, what we were really referring to was prvalue expressions.

All prvalue expressions are evaluated in some context that determines where they put their value, and the execution of the prvalue expression initializes that location with its value.

For example, in

```cpp

  BigExpensiveThing thing = MakeAThing();
```

the prvalue expression `MakeAThing()` is evaluated as the initializer of the `thing` variable, so `MakeAThing()` will directly initialize `thing`. The constructor passes a pointer to `thing` into `MakeAThing()`, and the `return` statement in `MakeAThing()` initializes whatever the pointer points to. Similarly, in

```cpp

  return BigExpensiveThing();
```

the compiler has a pointer to an object to initialize, and initializes that object directly by calling the `BigExpensiveThing` constructor.

## Related Reading

- [Tip \#11: Return Policy](/tips/11)
- [Tip \#24: Copies, Abbrv.](/tips/24)
- [Tip \#77: Temporaries, moves, and copies](/tips/77)
- [Tip \#117: Copy Elision and Pass-by-Value](/tips/117)


