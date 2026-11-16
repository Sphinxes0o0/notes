---
type: source
source-type: web
title: "Tip of the Week #130: Namespace Naming"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/130
summary: "abseil C++ Tips of the Week #130: Namespace Naming."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: fd58669f47f1019c01558fabad6aee8d
---

> 原文：<https://abseil.io/tips/130> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#130: Namespace Naming

\
\

Originally posted as totw/130 on 2017-02-17

By Titus Winters [(<span class="__cf_email__" cfemail="e3978a979690a3848c8c848f86cd808c8e">\[email protected\]</span>)](/cdn-cgi/l/email-protection#72061b06070132151d1d151e175c111d1f)

*The precision of naming takes away from the uniqueness of seeing* — Pierre Bonnard

The earliest commit of the Google C++ Style Guide contains the guidance that many people are still using for namespace naming. Roughly, this can be summarized as “namespaces are derived from package paths.” Following on the heels of Java’s package naming requirements, this makes a lot of sense: we want to be able to uniquely identify symbols in C++ and we want there to be uniqueness and consistency in namespace choice.

Except in actuality, we don’t. We just didn’t realize for almost a decade.

## Name Lookup

Let’s start with how name lookup works in C++ and how it’s different from Java.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
namespace foo {
namespace bar {
void f() {
  Baz b;
}
}
}
```

</div>

</div>

In C++, lookup on an unqualified name (`Baz`) will search expanding scopes for a symbol of the same name: first in `f()` (the function), then in `bar`, then in `foo`, then in the global namespace.

In Java, there is no such thing as an unqualified symbol: either a symbol is a qualified name:

<div class="language-java highlighter-rouge">

<div class="highlight">

```cpp
public void f() {
  com.google.foo.bar.Baz b = new com.google.foo.bar.Baz();
}
```

</div>

</div>

Or it is imported, either as a single package member or via wildcard:

<div class="language-java highlighter-rouge">

<div class="highlight">

```cpp
import com.google.foo.bar.Baz;
import com.google.foo.bar.*;
```

</div>

</div>

In no case is `Baz` looked for outside of the package that is explicitly provided: wildcards don’t descend into child packages, nor is search extended into parent packages. As it turns out, this difference in how parent packages/namespaces are handled within Java and C++ is fundamental to why structural namespace naming (making the namespace structure match the package hierarchy) is a mistake within C++.

## The Problem

The fundamental problem for building namespaces out of packages is that we rarely rely on fully-qualified lookup in C++, normally writing `std::unique_ptr` rather than `::std::unique_ptr`. Coupled with lookup in enclosing namespaces, this means that for code in a deeply nested package (`::division::section::team::subteam::project`, for example) any symbol that is not fully qualified (`std::unique_ptr`) can in fact reference any of

- `::std::unique_ptr`
- `::division::std::unique_ptr`
- `::division::section::std::unique_ptr`
- `::division::section::team::std::unique_ptr`
- `::division::section::team::subteam::std::unique_ptr`
- `::division::section::team::subteam::project::std::unique_ptr`

And what’s worse: unqualified search starts at the bottom of that list *and stops as soon as there is a namespace match*. This means that your build can be broken if any of your transitive includes add a previously unused namespace that matches the leading namespace of any symbol you use out of an unqualified namespace. Strictly speaking, this doesn’t even have to be a build break: if someone adds something with a matching name and a syntactically-compatible API, the implementation of that API may be completely incompatible and cause widespread havoc at runtime. Obviously this isn’t too bad with `std` - nobody should ever be adding a nested namespace `std` - but what about more common namespaces? How about things like `testing`?

Names aren’t chosen to be unique. Since teams commonly create local utility packages to handle common tasks relating to the infrastructure they rely on, we wind up with local `util` and `pipeline` packages - and sub-namespaces. This is a recipe for unnecessary and unintended collisions.

For comparison, the problem in Java is far reduced: if you wildcard-import from two packages in Java and one adds a new symbol with the same name as the other package, your build can break. This is easily and completely solved by forbidding wildcard imports as is done in many Java styles.

## Two Consistent Options, Three Approaches

There are two features that prevent this build-break-at-a-distance:

- If no leaf namespace (`search::foo::bar`) matches any top-level namespace (`::bar`) or a sub-namespace of any parent of that leaf (`search::bar`), no name collisions will occur.
- If there are no unqualified lookups, there will be no problems.

There are (at least) three ways to achieve this:

- Always fully qualify everything outside of the current namespace. This is very verbose and sort of weird: nothing in C++ (including the standard library) is written with leading `::` on every symbol.
- Build some tooling to identify introduction of new namespaces and ensure that it doesn’t overlap with any other namespace in the same hierarchy. That is, do not add `search::bar` if there is a `::bar` or a `search::foo::bar`.
- Don’t nest deeply: a single top-level namespace per project gets the same result without long/complicated names, with less exposure to accidents, without causing surprise for new engineers, and without the need to build any tooling.

The current style guide suggests the [last option](http://google.github.io/styleguide/cppguide.html#Namespace_Names), but allows for the old style (namespaces match package names) if necessary. This is largely because the Google didn’t want to cause too much anxiety or trigger anyone re-namespacing things. That said, if we had it to do over again in a fresh codebase we would unambiguously say this: one top-level namespace for public interfaces per project. Ensure uniqueness of namespaces via a common database. Thus we get (only) top-level namespaces like `absl`, and can have no ambiguity in lookup (barring collision between local symbols and those in the global namespace, but modern rules discourage the global namespace anyway).

Because there is so much code that existed before this change, and so much code following the old pattern even after this change, we find ourselves in a sort of half-way space, with some namespaces that often need to be fully qualified (`::util`), and some that are obviously unique and never need to be (`std`).

## But It Keeps Things Organized!

I regularly hear people express that small/nested namespaces “keep things organized.” Putting things in their place feels right - why lump together something like `StrCat()` and `make_unique()` other than being in Abseil these have nothing to do with one another! Wouldn’t an `absl::strings::utilities` namespace help differentiate from `absl::smart_ptrs`?

In other languages this would probably be good - better organization with no downside. However, because of how lookup works (expanding into successive layers of containing namespace scopes) your fine-grained namespace is impacted by every symbol (and sub-namespace) added in every parent namespace. That is: while you don’t exactly “contain” the names from parent namespaces, name/namespace collisions matter nearly as much as if you do. Small/deeply-nested namespaces don’t *shield* you from this, they *exacerbate* it.

## Best Practices

Practically speaking, the following is the best we can do given the realities of most codebases:

- Have a database of some form for a codebase to identify the unique namespaces.
- When introducing a new namespace, use that database and introduce it as a top-level.
- If for some reason the above is impossible, never *ever* introduce a sub-namespace that matches a well-known top-level namespace. No sub-namespaces for `absl`, `testing`, `util`, etc. Try to give sub-namespaces unique names that are unlikely to collide with future top-levels.
- When declaring namespace aliases and using-declarations, use fully qualified names, unless you are referring to a name inside the current namespace, as per [TotW 119](/tips/119).
- For code in `util` or other commonly-abused namespaces, try to avoid full qualification, but qualify if necessary.

The advice in [TotW 119](/tips/119) also helps, for `.cc` files: our concern with fully-qualifying is not that it is bad, but that it is *weird* compared to C++ code in the rest of the world. Limited use in using-declarations strikes an acceptable balance. However, even complete adherence to this suggestion doesn’t fully mitigate the dangers from unqualified name lookup because we still have header files and don’t want to fully qualify every symbol in every header.


