---
type: source
source-type: web
title: "Tip of the Week #107: Reference Lifetime Extension"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/107
summary: "abseil C++ Tips of the Week #107: Reference Lifetime Extension."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 4fe2cf93a6a2b6c7ca18ad1a9a3b1005
---

> 原文：<https://abseil.io/tips/107> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#107: Reference Lifetime Extension

\
\

Originally posted as totw/107 on 2015-12-10

By Titus Winters (<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="7e0a170a0b0d3e19111119121b501d1113">[email protected]</a>)

There have been some reports of confusion about references and lifetimes after [TotW 101](/tips/101), so in this Tip we’ll dive more into the question, “When does reference lifetime extension apply?”

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
string Foo::GetName();

const string& name = obj.GetName();  // Is this safe/legal?
```

</div>

</div>

In short, lifetimes of temporaries (referents) will be extended *if and only if*

- A local `const T&` (or `T&&`, although Google style generally ignores that) is initialized to the result of an expression (usually a function call) returning a temporary `T` *or* the `T` subobject of a temporary (e.g. a struct containing `T`).

The standard-ese may be a little tricky to unpack, so lets discuss some of the edge cases to clarify:

- This doesn’t work when assigning to `T&`, it must be `const T&`. (It’s a compilation error.)
- This doesn’t work if there is a (non-polymorphic) type conversion at play. For instance, assigning to `const absl::string_view&` from `string` does not extend the lifetime of the `string`. (You also don’t want `const absl::string_view&` in the first place, but that’s a separate issue).
- This doesn’t work when you’re getting the subobject indirectly: the compiler doesn’t look through function calls (getters or the like). The subobject form only works when you’re directly assigning from a public member variable subobject of the temporary. (So it doesn’t come up often because we don’t have many expressions that return temporary structs.)
- The case where type conversion is allowed is when assigning to a `T&` from a temporary of `U` when `T` is a parent class of `U`. Please don’t do that: it’s even more confusing for readers than the other cases.

If the lifetime of the temporary is extended, it will last until the reference goes out of scope. If the lifetime of the temporary isn’t extended in the above fashion, the `T` being referred to is destroyed at the end of the statement (when we get to the next `;`).

As per [TotW 101](/tips/101) you probably shouldn’t rely on lifetime extension in the explicit case of reference-initialization: it’s not gaining you much/any performance, and it is subtle, fragile, and prone to cause extra work for your reviewers and future maintainers.

There are subtle cases where lifetime extension *is* happening and is necessary and beneficial (like ranged-for over a temporary container), but again, the extension is only for the result of the temporary expression, not any sub-expressions. For instance, these work:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::vector<int> GetInts();
for (int i : GetInts()) { }  // lifetime extension on the vector is important

// Return string_views of size 1 for each char in this string.
std::vector<absl::string_view> Explode(const string& s);

// Lifetime extension kicks in on the vector, but *not* on the temporary string!
for (absl::string_view s : Explode(StrCat("oo", "ps"))) { }  // WRONG
```

</div>

</div>

This does not work:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
MyProto GetProto();

// Lifetime extension *doesn't work* here: sub_protos (a repeated field)
// is destroyed by MyProto going out of scope, and the lifetime extension rules
// don't kick in here to magically lifetime extend the MyProto returned by
// GetProto().  The sub-object lifetime extension only works for simple
// is-a-member-of relationships: the compiler doesn't see that sub_protos()
// itself returning a reference to an sub-object of the outer temporary.
for (const SubProto& p : GetProto().sub_protos()) { }  // WRONG
```

</div>

</div>


