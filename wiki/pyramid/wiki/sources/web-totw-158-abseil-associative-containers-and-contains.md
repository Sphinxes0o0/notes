---
type: source
source-type: web
title: "Tip of the Week #158: Abseil Associative containers and `contains()`"
author: "James Dennett"
date: 2012
url: https://abseil.io/tips/158
summary: "abseil C++ Tips of the Week #158: Abseil Associative containers and `contains()."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 48882ba67a0c2c844ce17c5cdba66962
---

> 原文：<https://abseil.io/tips/158> · 作者：James Dennett · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#158: Abseil Associative containers and `contains()`

\
\

Originally posted as TotW \#158 on January 3, 2019

*By [James Dennett](/cdn-cgi/l/email-protection#432927262d2d26373703242c2c242f266d202c2e)*

Updated 2020-04-20

Quicklink: [abseil.io/tips/158](https://abseil.io/tips/158)

“I cannot contain myself” – Bertrand Russell

## Does That Container Contain This Thing or Not?

When checking whether a set contains a value or a map contains a key, C++ has historically forced users to choose between writing the rather verbose

```cpp

container.find(value) != container.end()
```

or the arguably obtuse (and sometimes inefficient)

```cpp

container.count(value) != 0
```

instead of writing

```cpp

container.contains(value)
```

as we’d like to.

## `container.contains(value)` to the Rescue

The simpler syntax is part of the C++20 Standard, and Abseil’s (`absl::{flat,node}_hash_{map,set}`) and btree containers (`absl::btree_*`) support it today.

`contains` has the same support for [heterogeneous lookup](/tips/144) as `find`, so (for example) it’s possible to check whether an `absl::flat_hash_set<std::string>` contains an `absl::string_view` value without paying the costs of converting to a `std::string` object:

```cpp

constexpr absl::string_view name = "Willard Van Orman Quine";
absl::flat_hash_set<std::string> names = {std::string(name)};
assert(names.contains(name));  // No dynamic allocation here.
```

Given that most of our code that needs associative containers (whether sets or maps) should be using the Abseil hashed containers today (see [Tip \#136](/tips/136)), it should rarely be necessary to use one of the other formulations in new code.

NOTE: As described in [Tip \#132](/tips/132) (“Avoid Redundant Map Lookups”), don’t check if an item is in a container and then do another operation that implies a lookup (such as `find`, `insert` or `remove`).

## Conclusion

Querying whether an item can be found in an associative container is a common operation, and a natural syntax for it is `container.contains(value)`. Prefer that syntax when possible.


