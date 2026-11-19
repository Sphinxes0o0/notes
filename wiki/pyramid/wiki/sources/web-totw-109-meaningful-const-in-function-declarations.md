---
type: source
source-type: web
title: "Tip of the Week #109: Meaningful \`const\` in Function Declarations"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/109
summary: "abseil C++ Tips of the Week #109: Meaningful \`const\` in Function Declarations."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: fe105238822a0563f1a12e9ff4a580bb
---

> 原文：<https://abseil.io/tips/109> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#109: Meaningful \`const\` in Function Declarations

\
\

Originally posted as totw/109 on 2016-01-14

By Greg Miller [(<span class="__cf_email__" cfemail="b7ddd0daf7d0d8d8d0dbd299d4d8da">\[email protected\]</span>)](/cdn-cgi/l/email-protection#2349444e63444c4c444f460d404c4e)

This document will explain when `const` is meaningful in function declarations, and when it is meaningless and best omitted. But first, let us briefly explain what is meant by the terms *declaration* and *definition*.

Consider the following code:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
void F(int);                     // 1: declaration of F(int)
void F(const int);               // 2: re-declaration of F(int)
void F(int) { /* ... */ }        // 3: definition of F(int)
void F(const int) { /* ... */ }  // 4: error: re-definition of F(int)
```

</div>

</div>

The first two lines are function *declarations*. A function *declaration* tells the compiler the function’s signature and return type. In the above example, the function’s signature is `F(int)`. The constness of the function’s parameter type is ignored, so both declarations are equivalent (See [“Overloadable declarations”](http://eel.is/c++draft/over.load).)

Lines 3 and 4 from the above code are both function *definitions*. A function *definition* is also a declaration, but a definition also contains the function’s body. Therefore, line 3 is a definition for a function with the signature `F(int)`. Similarly, line 4 is also a definition for the same function, `F(int)`, which will result in an error at link time. Multiple declarations are allowed, but only a single definition is permitted.

Even though the definitions on lines 3 and 4 *declare* and *define* the same function, there is a difference within their function bodies due to the way they are declared. From the definition on line 3, the type of the function-parameter variable within the function will be `int` (i.e., non-const). On the other hand, the definition on line 4 will produce a function-parameter variable within the function whose type is `const int`.

## Meaningful `const` in Function Declarations

Not all `const` qualifications in function declarations are ignored. To quote from “Overloadable declarations” (\[over.load\]) in the C++ standard (emphasis added):

> `const` type-specifiers **buried within a parameter type specification** are significant and can be used to distinguish overloaded function declarations

The following are examples where `const` is significant and not ignored:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
void F(const int* x);                  // 1
void F(const int& x);                  // 2
void F(std::unique_ptr<const int> x);  // 3
void F(int* x);                        // 4
```

</div>

</div>

In the above examples, the `x` parameter itself is never declared `const`. Each of the above functions accepts a parameter named `x` of a different type, thus forming a valid overload set. Line 1 declares a function that accepts a “pointer to an `int` that is `const`”. Line 2 declares a function that accepts a “reference to an `int` that is `const`”. And line 3 declares a function that accepts a “unique_ptr to an `int` that is `const`”. All of these uses of `const` are important and not ignored because they are part of the parameter type specification and are not top-level `const` qualifications that affect the parameter `x` itself.

Line 4 is interesting because it does not include the `const` keyword at all, and may at first appear to be equivalent to the declaration on line 1 given the reasons cited at the beginning of this document. The reason that this is not true and that line 4 is a valid and distinct declaration is that only top-level, or outermost, `const` qualifications of the parameter type specification are ignored.

To complete this example, let us look at a few more examples where a `const` is meaningless and ignored.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
void F(const int x);          // 1: declares F(int)
void F(int* const x);         // 2: declares F(int*)
void F(const int* const x);   // 3: declares F(const int*)
```

</div>

</div>

## Rules of Thumb

Though few of us will ever truly master all the delightful obscurities of C++, it is important that we do our best to understand the rules of the game. This will help us write code that is understood by other C++ programmers who are following the same rules and playing the same game. For this reason, it is important that we understand when `const` qualification is meaningful in a function declaration and when it is ignored.

Although there is no official guidance from the [Google C++ style guide](http://google.github.io/styleguide/cppguide.html), and there is no single generally accepted opinion, the following is one reasonable set of guidelines:

1.  Never use top-level `const` on function parameters in *declarations* that are not definitions (and be careful not to copy/paste a meaningless `const`). It is meaningless and ignored by the compiler, it is visual noise, and it could mislead readers.
2.  Do use top-level `const` on function parameters in *definitions* at your (or your team’s) discretion. You might follow the same rationale as you would for when to declare a function-local variable `const`.


