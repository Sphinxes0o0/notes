---
type: source
source-type: web
title: "Tip of the Week #161: Good Locals and Bad Locals"
author: "James Dennett"
date: 2012
url: https://abseil.io/tips/161
summary: "abseil C++ Tips of the Week #161: Good Locals and Bad Locals."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 96267f639000f9edd470dba32a3e7707
---

> 原文：<https://abseil.io/tips/161> · 作者：James Dennett · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#161: Good Locals and Bad Locals

\
\

Originally posted as TotW \#161 on April 16, 2019

*By [James Dennett](/cdn-cgi/l/email-protection#e78d83828989829393a7808888808b82c984888a)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/161](https://abseil.io/tips/161)

*We may freak out globally, but we suffer locally. – Jonathan Franzen*

## Synopsis

Local variables are great, but can be overused. We can often simplify code by restricting their use to situations in which they provide a specific benefit.

## Recommendations

Use local variables only when one or more of the following applies:

- Their name adds useful documentation.
- They simplify excessively complicated expressions.
- They factor out a repeated expression to make it clear to humans (and to a lesser extent compilers) that it’s the same value every time.
- An object’s lifetime needs to extend across multiple statements (for example, because references to the object are retained beyond the end of a single statement or because the variable holds a value that is updated during its lifetime).

In other cases, consider removing a layer of indirection by eliminating the local variable and writing the expression directly where it’s used.

## Rationale

Naming values adds a level of indirection to code comprehension unless the variable’s name fully captures the relevant aspects of its meaning. Giving a name to a value in C++ also exposes it to the rest of the scope. It also affects the “value category”, as every named variable is an lvalue even if declared as an rvalue reference and initialized from an rvalue. This can require additional uses of `std::move`, which warrant care during code review to avoid use-after-move bugs. Given these downsides, use of local variables is best reserved for situations in which it provides a specific benefit.

## Examples: Bad Uses of Local Variables

#### Eliminating a Local Variable That’s Immediately Returned

As a simple example of eliminating an unhelpful local variable, instead of

```cpp

MyType value = SomeExpression(args);
return value;
```

prefer

```cpp

return SomeExpression(args);
```

#### Inline Expressions Under Test Into GoogleTest’s `EXPECT_THAT`

```cpp

std::vector<string> actual = SortedAges(args);
EXPECT_THAT(actual, ElementsAre(21, 42, 63));
```

Here the variable name `actual` doesn’t add anything useful (`EXPECT_THAT` always takes the actual value as its first argument), it’s not simplifying a complicated expression, and its value is used once only. Inlining the expression as in

```cpp

EXPECT_THAT(SortedAges(args), ElementsAre(21, 42, 63));
```

makes it clear at a glance what’s being tested, and by avoiding giving a name to `actual` ensures that it cannot be unintentionally re-used. It also allows the testing framework to show the failing call in error output.

Note: the shorter version hides the expected type of `SortedAges`. If verifying the type is important, consider declaring a variable in order to show its type.

#### Use Matchers to Eliminate Variables in Tests.

[Matchers](https://github.com/google/googletest/blob/master/docs/reference/matchers.md) can help to avoid the need to name local variables in tests by allowing `EXPECT_THAT` to directly express everything we expect of a value. Instead of writing code like this

```cpp

std::optional<std::vector<int>> maybe_ages = GetAges(args);
ASSERT_NE(maybe_ages, std::nullopt);
std::vector<int> ages = maybe_ages.value();
ASSERT_EQ(ages.size(), 3);
EXPECT_EQ(ages[0], 21);
EXPECT_EQ(ages[1], 42);
EXPECT_EQ(ages[2], 63);
```

where we have to be careful to write `ASSERT*` instead of `EXPECT*` to avoid crashes, we can express the intent directly in code:

```cpp

EXPECT_THAT(GetAges(args),
            Optional(ElementsAre(21, 42, 63)));
```

## Examples: Good Uses of Local Variables

#### Factoring Out a Repeated Expression

```cpp

myproto.mutable_submessage()->mutable_subsubmessage()->set_foo(21);
myproto.mutable_submessage()->mutable_subsubmessage()->set_bar(42);
myproto.mutable_submessage()->mutable_subsubmessage()->set_baz(63);
```

Here the repetition makes the code verbose (sometimes requiring unfortunate line breaks), and can require more effort from readers to see that this is setting three fields of the same proto message. Using a local variable to alias the relevant message can clean it up:

```cpp

SubSubMessage& subsubmessage =
    *myproto.mutable_submessage()->mutable_subsubmessage();
subsubmessage.set_foo(21);
subsubmessage.set_bar(42);
subsubmessage.set_baz(63);
```

In some cases this can also help the compiler to generate better code as it doesn’t need to prove that the repeated expression returns the same value each time. Beware of premature optimization, though: if eliminating a common subexpression doesn’t help human readers, profile before trying to help the compiler.

#### Giving Meaningful Names to Pair and Tuple Elements

While it’s usually better to use a `struct` with meaningfully-named fields than a `pair` or a `tuple`, we can mitigate the problems with `pair` and `tuple` by binding meaningfully-named aliases to their elements. For example, instead of

```cpp

for (const auto& name_and_age : ages_by_name) {
  if (IsDisallowedName(name_and_age.first)) continue;
  if (name_and_age.second < 18) children.insert(name_and_age.first);
}
```

in C++11 we could write

```cpp

for (const auto& name_and_age : ages_by_name) {
  const std::string& name = name_and_age.first;
  const int& age = name_and_age.second;

  if (IsDisallowedName(name)) continue;
  if (age < 18) children.insert(name);
}
```

and in C++17, we can more simply use “structured bindings” to achieve the same result of giving meaningful names:

```cpp

for (const auto& [name, age] : ages_by_name) {
  if (IsDisallowedName(name)) continue;
  if (age < 18) children.insert(name);
}
```


