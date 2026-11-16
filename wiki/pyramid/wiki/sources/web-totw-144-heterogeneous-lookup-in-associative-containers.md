---
type: source
source-type: web
title: "Tip of the Week #144: Heterogeneous Lookup in Associative Containers"
author: "Samuel Benzaquen"
date: 2012
url: https://abseil.io/tips/144
summary: "abseil C++ Tips of the Week #144: Heterogeneous Lookup in Associative Containers."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 9a9c6dcd37517988c02724b689e5db78
---

> 原文：<https://abseil.io/tips/144> · 作者：Samuel Benzaquen · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#144: Heterogeneous Lookup in Associative Containers

\
\

Originally posted as TotW \#144 on March 23, 2018

*By [Samuel Benzaquen](/cdn-cgi/l/email-protection#fa89989f94809bba9d95959d969fd4999597)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/144](https://abseil.io/tips/144)

## Introduction

Associative containers associate an element with a key. Inserting into or looking up an element from the container requires an equivalent key. In general, containers require the keys to be of a specific type, which can lead to inefficiencies at call sites that need to convert between near-equivalent types (like `std::string` and `absl::string_view`).

To avoid this unnecessary work, some containers provide *heterogeneous lookup*. This feature allows callers to pass keys of any type (as long as the user-specified comparator functor supports them). See [std::map::find](http://en.cppreference.com/w/cpp/container/map/find) for an example of this feature in an STL container.

## Transparent Functors

A transparent functor is one that accepts more than one particular type. It *must* publicize this fact by providing an `is_transparent` inner type. The actual definition of this inner type is not relevant as it is used merely as a tag. It is common to use a `using` declaration of `is_transparent` set to `void`.

When a container detects a transparent functor their lookup functions will forward the user specified value intact instead of converting it to `key_type` first (through implicit or explicit conversion).

Implicitly supporting heterogeneous lookup can be dangerous, as the relationship between values might not be maintained after conversions. For example, `1.0 < 1.1`, but `static_cast<int>(1.0) == static_cast<int>(1.1)`. Thus, using a `double` to look up a value in a `std::set<int>` could lead to incorrect results. These potential bugs are the reason this feature is opt-in.

## Using Heterogeneous Lookup For Performance

One common reason for using heterogeneous lookup is performance. We could construct the `key_type`, but doing so requires non-trivial work that we would rather avoid. For example:

```cpp

std::map<std::string, int> m = ...;
absl::string_view some_key = ...;
// Construct a temporary `std::string` to do the query.
// The allocation + copy + deallocation might dominate the find() call.
auto it = m.find(std::string(some_key));
```

Instead, we can use a transparent comparator like so:

```cpp

struct StringCmp {
  using is_transparent = void;
  bool operator()(absl::string_view a, absl::string_view b) const {
    return a < b;
  }
};

std::map<std::string, int, StringCmp> m = ...;
absl::string_view some_key = ...;
// The comparator `StringCmp` will accept any type that is implicitly
// convertible to `absl::string_view` and says so by declaring the
// `is_transparent` tag.
// We can pass `some_key` to `find()` without converting it first to
// `std::string`. In this case, that avoids the unnecessary memory allocation
// required to construct the `std::string` instance.
auto it = m.find(some_key);
```

## What Else Is It Good For?

Cases exist where it is impossible or inconvenient to create a valid `key_type` object just to do a lookup. In those cases, we might want to use an alternative type that is much easier to produce, but contains the necessary information for the lookup. For example:

```cpp

struct ThreadCmp {
  using is_transparent = void;
  // Regular overload.
  bool operator()(const std::thread& a, const std::thread& b) const {
    return a.get_id() < b.get_id();
  }
  // Transparent overloads
  bool operator()(const std::thread& a, std::thread::id b) const {
    return a.get_id() < b;
  }
  bool operator()(std::thread::id a, const std::thread& b) const {
    return a < b.get_id();
  }
  bool operator()(std::thread::id a, std::thread::id b) const {
    return a < b;
  }
};

std::set<std::thread, ThreadCmp> threads = ...;
// Can't construct an instance of `std::thread` with the same id, just to do the lookup.
// But we can look up by id instead.
std::thread::id id = ...;
auto it = threads.find(id);
```

## STL Container Support and Alternatives

The standard ordered containers (`std::{map,set,multimap,multiset}`) support heterogeneous lookup. The standard *unordered* containers (`std::unordered_{map,set,multimap,multiset}`) do not support heterogeneous lookup until `C++20`.

The new family of [Swiss Tables](https://abseil.io/docs/cpp/guides/container), however, support heterogeneous lookup for both string-like types (`std::string`, `absl::string_view`, etc.) and smart pointers (`T*`,`std::shared_ptr`, `std::unique_ptr`). They require both the hasher and the equality function to be tagged as transparent. All other key types require explicit opt-in from the user.

The [B-Tree](https://abseil.io/docs/cpp/guides/container) containers (`absl::btree_{set,map,multiset,multimap}`) also support heterogeneous lookup.

[Protocol Buffers’](protobuf) associative map’s implementation, `google::protobuf::Map`, supports heterogeneous lookup when the map is keyed with `std::string` using string-like keys (any type that is convertible to `absl::string_view`).


