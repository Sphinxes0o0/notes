---
type: source
source-type: web
title: "Tip of the Week #88: Initialization: =, (), and {}"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/88
summary: "abseil C++ Tips of the Week #88: Initialization: =, (), and {}."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: dfe16affb7e0cd7b8bd834a0ae960446
---

> 原文：<https://abseil.io/tips/88> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#88: Initialization: =, (), and {}

\
\

Originally posted as TotW \#88 on Jan 27, 2015

*by Titus Winters [(<span class="__cf_email__" cfemail="c9bda0bdbcba89aea6a6aea5ace7aaa6a4">\[email protected\]</span>)](/cdn-cgi/l/email-protection#44302d30313704232b2b2328216a272b29), on behalf of the Google C++ Style Arbiters*

C++11 provided a new syntax referred to as “uniform initialization syntax” that was supposed to unify all of the various styles of initialization, avoid the [Most Vexing Parse](https://en.wikipedia.org/wiki/Most_vexing_parse), and avoid narrowing conversions. This new mechanism means we now have [yet another](https://xkcd.com/927/) syntax for initialization, with its own tradeoffs.

## C++11 Brace Initialization

Some uniform initialization syntax proponents would suggest that we use {}s and direct initialization (no use of the ‘=’, although in most cases both forms call the same constructor) for initialization of all types:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
int x{2};
std::string foo{"Hello World"};
std::vector<int> v{1, 2, 3};
```

</div>

</div>

vs. (for instance):

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
int x = 2;
std::string foo = "Hello World";
std::vector<int> v = {1, 2, 3};
```

</div>

</div>

This approach has two shortcomings. First, “uniform” is a stretch: there are cases where ambiguity still exists (for the casual reader, not the compiler) in what is being called and how.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::vector<std::string> strings{2}; // A vector of two empty strings.
std::vector<int> ints{2};            // A vector containing only the integer 2.
```

</div>

</div>

Second: this syntax is not exactly intuitive: no other common language uses something like it. The language can certainly introduce new and surprising syntax, and there are technical reasons why it’s necessary in some cases – especially in generic code. The important question is: how much should we change our habits and language understanding to take advantage of that change? Are the benefits worth the cost in changing our habits or our existing code? For uniform initialization syntax, we don’t believe in general that the benefits outweigh the drawbacks.

## Best Practices for Initialization

Instead, we recommend the following guidelines for “How do I initialize a variable?”, both to follow in your own code and to cite in your code reviews:

- **Use assignment syntax when initializing directly with the intended literal value (for example: `int`, `float`, or `std::string` values), with smart pointers such as `std::shared_ptr`, `std::unique_ptr`, with containers (`std::vector`, `std::map`, etc), when performing struct initialization, or doing copy construction.**

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  int x = 2;
  std::string foo = "Hello World";
  std::vector<int> v = {1, 2, 3};
  std::unique_ptr<Matrix> matrix = NewMatrix(rows, cols);
  MyStruct x = {true, 5.0};
  MyProto copied_proto = original_proto;
  ```

  </div>

  </div>

  instead of:

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  // Bad code
  int x{2};
  std::string foo{"Hello World"};
  std::vector<int> v{1, 2, 3};
  std::unique_ptr<Matrix> matrix{NewMatrix(rows, cols)};
  MyStruct x{true, 5.0};
  MyProto copied_proto{original_proto};
  ```

  </div>

  </div>

- **Use the traditional constructor syntax (with parentheses) when the initialization is performing some active logic, rather than simply composing values together.**

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  Frobber frobber(size, &bazzer_to_duplicate);
  std::vector<double> fifty_pies(50, 3.14);
  ```

  </div>

  </div>

  vs.

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  // Bad code

  // Could invoke an initializer list constructor, or a two-argument constructor.
  Frobber frobber{size, &bazzer_to_duplicate};

  // Makes a vector of two doubles.
  std::vector<double> fifty_pies{50, 3.14};
  ```

  </div>

  </div>

- **Use {} initialization without the = only if the above options don’t compile:**

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  class Foo {
   public:
    Foo(int a, int b, int c) : array_{a, b, c} {}

   private:
    int array_[5];
    // Requires {}s because the constructor is marked explicit
    // and the type is non-copyable.
    EventManager em{EventManager::Options()};
  };
  ```

  </div>

  </div>

- **Never mix {}s and auto.**\
  For example, don’t do this:

  <div class="language-cpp highlighter-rouge">

  <div class="highlight">

  ``` cpp
  // Bad code
  auto x{1};
  auto y = {2}; // This is a std::initializer_list<int>!
  ```

  </div>

  </div>

  (For the language lawyers: prefer copy-initialization over direct-initialization when available, and use parentheses over curly braces when resorting to direct-initialization.)

Perhaps the best overall description of the issue is Herb Sutter’s [GotW post](http://herbsutter.com/2013/05/09/gotw-1-solution/). Although he shows examples that include direct initialization of `int` with braces, his final advice is roughly compatible with what we present here with one caveat: where Herb says “where you prefer to see only the = sign”, we unambiguously prefer to see exactly that. In conjunction with more consistent use of `explicit` on multi-parameter constructors (see [Tip \#142](/tips/142)), this provides a balance between readability, explicitness, and correctness.

## Conclusion

The tradeoffs for uniform initialization syntax are not generally worth it: our compilers already warn against the Most Vexing Parse (you can use brace initialization or add parens to resolve the issue), and the safety from narrowing conversions isn’t worth the readability hit for brace-initialization (we’ll need a different solution for narrowing conversions, eventually). The Style Arbiters don’t think this issue is critical enough to make a formal rule on, especially because there are cases (notably in generic code) where brace initialization may be justified.


