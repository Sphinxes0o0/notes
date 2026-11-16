---
type: source
source-type: web
title: "Tip of the Week #123: `absl::optional` and `std::unique_ptr`"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/123
summary: "abseil C++ Tips of the Week #123: absl::optional` and `std::unique_ptr."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 8ff8dc071f9a5c6f1986d8ea7bde7372
---

> 原文：<https://abseil.io/tips/123> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#123: `absl::optional` and `std::unique_ptr`

\
\

Originally posted as totw/123 on 2016-09-06

By Alexey Sokolov [(<span class="__cf_email__" cfemail="c4b7abafaba8abb284a3ababa3a8a1eaa7aba9">\[email protected\]</span>)](/cdn-cgi/l/email-protection#5625393d393a392016313939313a337835393b) and Etienne Dechamps [(<span class="__cf_email__" cfemail="e3868786808b828e9390a3848c8c848f86cd808c8e">\[email protected\]</span>)](/cdn-cgi/l/email-protection#8ce9e8e9efe4ede1fcffccebe3e3ebe0e9a2efe3e1)

## How to Store Values

This tip discusses several ways of storing values. Here we use class member variables as an example, but many of the points below also apply to local variables.

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
#include <memory>
#include "absl/types/optional.h"
#include ".../bar.h"

class Foo {
  ...
 private:
  Bar val_;
  absl::optional<Bar> opt_;
  std::unique_ptr<Bar> ptr_;
};
```

</div>

</div>

### As a Bare Object

This is the simplest way. `val_` is constructed and destroyed at the beginning of `Foo`’s constructor and at the end of `Foo`’s destructor, respectively. If `Bar` has a default constructor, it doesn’t even need to be initialized explicitly.

`val_` is very safe to use, because its value can’t be null. This removes a class of potential bugs.

But bare objects are not very flexible:

- The lifetime of `val_` is fundamentally tied to the lifetime of its parent `Foo` object, which is sometimes not desirable. If `Bar` supports move or swap operations, the contents of `val_` can be replaced using these operations, while any existing pointers or references to `val_` continue pointing or referring to the same `val_` object (as a container), not to the value stored in it.
- Any arguments that need to be passed to `Bar`’s constructor need to be computed inside the initializer list of `Foo`’s constructor, which can be difficult if complicated expressions are involved.

### As `absl::optional<Bar>`

This is a good middle ground between the simplicity of bare objects and the flexibility of `std::unique_ptr`. The object is stored inside `Foo` but, unlike bare objects, `absl::optional` can be empty. It can be populated at any time by assignment (`opt_ = ...`) or by constructing the object in place (`opt_.emplace(...)`).

Because the object is stored inline, the usual caveats about allocating large objects on the stack apply, just like for a bare object. Also be aware that an empty `absl::optional` uses as much memory as a populated one.

Compared to a bare object, `absl::optional` has a few downsides:

- It’s less obvious for the reader where object construction and destruction occur.
- There is a risk of accessing an object which does not exist.

### As `std::unique_ptr<Bar>`

This is the most flexible way. The object is stored outside of `Foo`. Just like `absl::optional`, a `std::unique_ptr` can be empty. However, unlike `absl::optional`, it is possible to transfer ownership of the object to something else (through a move operation), to take ownership of the object from something else (at construction or through assignment), or to assume ownership of a raw pointer (at construction or through `ptr_ = absl::WrapUnique(...)`, see [TotW 126](/tips/126).

When `std::unique_ptr` is null, it doesn’t have the object allocated, and consumes only the size of a pointer<sup><a href="#fn:deleter" class="footnote" rel="footnote">1</a></sup>.

Wrapping an object in a `std::unique_ptr` is necessary if the object may need to outlive the scope of the `std::unique_ptr` (ownership transfer).

This flexibility comes with some costs:

- Increased cognitive load on the reader:
  - It’s less obvious what’s stored inside (`Bar`, or something derived from `Bar`). However, it may also decrease the cognitive load, as the reader can focus only on the base interface held by the pointer.
  - It’s even less obvious than with `absl::optional` where object construction and destruction occur, because ownership of the object can be transferred.
- As with `absl::optional`, there is a risk of accessing an object which does not exist - the famous null pointer dereference.
- The pointer introduces an additional level of indirection, which requires a heap allocation, and is [not friendly](https://en.wikipedia.org/wiki/Locality_of_reference) to CPU caches; Whether this matters or not depends a lot on particular use cases.
- `std::unique_ptr<Bar>` is not copyable even if `Bar` is. This also prevents `Foo` from being copyable.

### Conclusion

As always, strive to avoid unnecessary complexity, and use the simplest thing that works. Prefer bare object, if it works for your case. Otherwise, try `absl::optional`. As a last resort, use `std::unique_ptr`.

|  | `Bar` | `absl::optional<Bar>` | `std::unique_ptr<Bar>` |
|----|----|----|----|
| Supports delayed construction |  | ✓ | ✓ |
| Always safe to access | ✓ |  |  |
| Can transfer ownership of `Bar` |  |  | ✓ |
| Can store subclasses of `Bar` |  |  | ✓ |
| Movable | If `Bar` is movable | If `Bar` is movable | ✓ |
| Copyable | If `Bar` is copyable | If `Bar` is copyable |  |
| Friendly to CPU caches | ✓ | ✓ |  |
| No heap allocation overhead | ✓ | ✓ |  |
| Memory usage | `sizeof(Bar)` | `sizeof(Bar) + sizeof(bool)`<sup><a href="#fn:padding" class="footnote" rel="footnote">2</a></sup> | `sizeof(Bar*)` when null, `sizeof(Bar*) + sizeof(Bar)` otherwise |
| Object lifetime | Same as enclosing scope | Restricted to enclosing scope | Unrestricted |
| Call `f(Bar*)` | `f(&val_)` | `f(&opt_.value())` or `f(&*opt_)` | `f(ptr_.get())` or `f(&*ptr_)` |
| Remove value | N/A | `opt_.reset();` or `opt_ = absl::nullopt;` | `ptr_.reset();` or `ptr_ = nullptr;` |


