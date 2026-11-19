---
type: source
source-type: web
title: "Tip of the Week #101: Return Values, References, and Lifetimes"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/101
summary: "abseil C++ Tips of the Week #101: Return Values, References, and Lifetimes."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 15d25f382ba81fdba1b3f35abff2fbe6
---

> 原文：<https://abseil.io/tips/101> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#101: Return Values, References, and Lifetimes

\
\

Originally posted as totw/101 on 2015-07-29

By Titus Winters (<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="06726f72737546616969616a632865696b">[email protected]</a>)

Consider the following code snippet:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
const string& name = obj.GetName();
std::unique_ptr<Consumer> consumer(new Consumer(name));
```

</div>

</div>

In particular, I’d like to draw your attention to the `&`. Is it appropriate? What should we check? What can go wrong? I find a decent number of C++ programmers that aren’t entirely clear on references, but do generally know that they “avoid making copies.” As with most issues in C++, it’s more complicated than that.

## Case by Case: What is Being Returned and How is it Being Stored?

There are two (maybe three) important questions here:

1.  What type is returned (in this example, by `GetName()`)?
2.  What type are we storing into/initializing (in this example, what is the type of `name`)?
3.  If we are returning a reference, does the object being returned by reference have any lifetime limitations?

We’ll continue with `string` as our example type, but the same arguments generalize for most non-trivial value types.

1.  Returning `string`, initializing `string`: This is usually [RVO](https://en.wikipedia.org/wiki/Return_value_optimization) and is guaranteed to be, at worst, a move for modern types (See [TotW 77](/tips/77)).
2.  Returning `string&` or `const string&`, initializing `string`: This is a copy (there must be some long-living object which we are returning a reference to, so once we initialize a new string there are two names for that data, hence a copy. See [TotW 77](/tips/77)). Sometimes this is valuable, like if you need your `string` to outlast the lifetime guarantees provided by the function.
3.  Returning `string`, initializing `string&`: This won’t compile, as you cannot bind a reference to a temporary.
4.  Returning `const string&`, initializing `string&`: This won’t compile, as you’ve dropped the const inappropriately.
5.  Returning `const string&`, initializing `const string&`: This is no cost (you’re effectively returning just a pointer). However, you have inherited any existing lifetime restrictions: how long is that reference good for? Most accessor methods that return a reference are returning a member - at most, the reference can be valid for the life of the containing object.
6.  Returning `string&`, initializing `string&`: This is the same as \#5, but with the additional caveat: the returned reference is non-const, so any modifications to your reference will be reflected in the source.
7.  Returning `string&`, initializing `const string&`: The same as \#5.
8.  Returning `string`, initializing `const string&`: You’d think, given \#3, that this wouldn’t work. However, the language has special-case support for this: if you initialize a `const T&` with a temporary `T`, that `T` (in this case `string`) is not destroyed until the *reference* goes out of scope (in the common case of automatic or static variables).

Scenario \#8 is what allows most reflexive use of references (that is “Oh, I don’t want to copy so I’ll just assign into a reference” without necessarily thinking about what is being returned). However, because of \#1, it’s also not really doing anything for you: there probably wouldn’t have been a copy in the first place. Further, now readers of your code have to contend with your local variable being of type `const string&` instead of `string`, and thus worry about whether the underlying `string` has gone out of scope or changed.

Put another way: when code reviewing the original snippet, I have to worry about:

- Is `GetName()` returning by value or by reference?
- Does the constructor for `Consumer` take `string`, `const string&` or `string_view`?
- Does the constructor have any lifetime requirements placed on that parameter? (If it isn’t just `string`.)

However, if you just declare `name` as `string` in the first place, it’s generally no less efficient (because of RVO and move semantics), and at least as likely to be safe with respect to object lifetimes.

Additionally, if there is an object lifetime issue, it’s often simpler to spot when storing as `string`: rather than looking at the interplay between the lifetime promise of `GetName()`’s returned reference and the lifetime requirements of `SetName()`, having your own `string` means only having to look at the local code and `SetName()`.

All of which is to say: avoiding copies is fine, so long as you’re not making things more complicated. Making code more complicated when there wasn’t a copy in the first place is not a good tradeoff.


