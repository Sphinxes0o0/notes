---
type: source
source-type: web
title: "Tip of the Week #11: Return Policy"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/11
summary: "abseil C++ Tips of the Week #11: Return Policy."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 0776d4e0df19b3f25264251ace4db598
---

> 原文：<https://abseil.io/tips/11> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#11: Return Policy

\
\

Originally posted as TotW \#11 on August 16, 2012

*by Paul S. R. Chisholm [(<span class="__cf_email__" cfemail="5d2d732e732f733e35342e353231301d3a32323a3138733e3230">\[email protected\]</span>)](/cdn-cgi/l/email-protection#60104e134e124e03080913080f0c0d20070d01090c4e030f0d)*

*Frodo: There’ll be none left for the return journey.* *Sam: I don’t think there will be a return journey, Mr. Frodo.* – The Lord of the Rings: The Return of the King (novel by J.R.R. Tolkien, screenplay by Fran Walsh, Philippa Boyens, & Peter Jackson)

Note: this tip, though still relevant, preceded the introduction of move semantics in C++11. Please read this tip with the advice from [TotW \#77](/tips/77) also in mind.

Many older C++ codebases show patterns that are somewhat fearful of copying objects. Happily, we can “copy” without copying, thanks to something called [“return value optimization”](https://en.wikipedia.org/wiki/Return_value_optimization) (RVO).

RVO is a long-standing feature of almost all C++ compilers. Consider the following C++98 code, which has a copy constructor and an assignment operator. These functions are so expensive, the developer had them print a message every time they’re used:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
class SomeBigObject {
 public:
  SomeBigObject() { ... }
  SomeBigObject(const SomeBigObject& s) {
    printf("Expensive copy …\n", …);
    …
  }
  SomeBigObject& operator=(const SomeBigObject& s) {
    printf("Expensive assignment …\n", …);
    …
    return *this;
  }
  ~SomeBigObject() { ... }
  …
};
```

</div>

</div>

(Note that we’re intentionally avoiding discussion of move operations here. See [TotW \#77](/tips/77) for more information.)

Would you recoil in horror if this class had a factory method such as the following?

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
static SomeBigObject SomeBigObjectFactory(...) {
  SomeBigObject local;
  ...
  return local;
}
```

</div>

</div>

Looks inefficient, doesn’t it? What happens if we run the following?

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
SomeBigObject obj = SomeBigObject::SomeBigObjectFactory(...);
```

</div>

</div>

Simple answer: You probably expect there to be at least two objects created: the object returned from the called function, and the object in the calling function. Both are copies, so the program prints two messages about expensive operations. Real-world answer: No message is printed – because the copy constructor and assignment operator were never called!

How’d that happen? A lot of C++ programmers write “efficient code” that creates an object and passes that object’s address to a function, which uses that pointer or reference to operate on the original object. Well, under the circumstances described below, the compiler can transform such “an inefficient copy” into that “efficient code”!

When the compiler sees a variable in the calling function (that will be constructed from the return value), and a variable in the called function (that will be returned), it realizes it doesn’t need both variables. Under the covers, the compiler passes the address of the calling function’s variable to the called function.

To quote the C++98 standard, “Whenever a temporary class object is copied using a copy constructor … an implementation is permitted to treat the original and the copy as two different ways of referring to the same object and not perform a copy at all, even if the class copy constructor or destructor have side effects. For a function with a class return type, if the expression in the return statement is the name of a local object … an implementation is permitted to omit creating the temporary object to hold the function return value …” (Section 12.8 \[class.copy\], paragraph 15 of the C++98 standard. The C++11 standard has similar language in section 12.8, paragraph 31, but it’s more complicated.)

Worried that “permitted” isn’t a very strong promise? Fortunately, all modern C++ compilers perform RVO by default, even in debug builds, even for non-inlined functions.

## How Can You Ensure the Compiler Performs RVO?

The called function should define a single variable for the return value:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
SomeBigObject SomeBigObject::SomeBigObjectFactory(...) {
  SomeBigObject local;
  …
  return local;
}
```

</div>

</div>

The calling function should assign the returned value to a new variable:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// No message about expensive operations:
SomeBigObject obj = SomeBigObject::SomeBigObjectFactory(...);
```

</div>

</div>

That’s it!

The compiler can’t do RVO if the calling function reuses an existing variable to store the return value (though move semantics would apply for move-enabled types in this case):

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// RVO won’t happen here; prints message "Expensive assignment ...":
obj = SomeBigObject::SomeBigObjectFactory(s2);
```

</div>

</div>

The compiler also can’t do RVO if the called function uses more than one variable for the return value:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// RVO won’t happen here:
static SomeBigObject NonRvoFactory(...) {
  SomeBigObject object1, object2;
  object1.DoSomethingWith(...);
  object2.DoSomethingWith(...);
  if (flag) {
    return object1;
  } else {
    return object2;
  }
}
```

</div>

</div>

But it’s okay if the called function uses one variable and returns it in multiple places:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// RVO will happen here:
SomeBigObject local;
if (...) {
  local.DoSomethingWith(...);
  return local;
} else {
  local.DoSomethingWith(...);
  return local;
}
```

</div>

</div>

That’s probably all you **need** to know about RVO.

## One More Thing: Temporaries

RVO works with temporary objects, not just named variables. You can benefit from RVO when the called function returns a temporary object:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// RVO works here:
SomeBigObject SomeBigObject::ReturnsTempFactory(...) {
  return SomeBigObject::SomeBigObjectFactory(...);
}
```

</div>

</div>

You can also benefit from RVO when the calling function immediately uses the returned value (which is stored in a temporary object):

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// No message about expensive operations:
EXPECT_EQ(SomeBigObject::SomeBigObjectFactory(...).Name(), s);
```

</div>

</div>

A final note: If your code needs to make copies, then make copies, whether or not the copies can be optimized away. Don’t trade correctness for efficiency.


