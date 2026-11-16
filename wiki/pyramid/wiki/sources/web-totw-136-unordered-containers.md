---
type: source
source-type: web
title: "Tip of the Week #136: Unordered Containers"
author: "Matt Kulukundis"
date: 2012
url: https://abseil.io/tips/136
summary: "abseil C++ Tips of the Week #136: Unordered Containers."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 4e0a688a63715a34beb085b7bf38ba62
---

> 原文：<https://abseil.io/tips/136> · 作者：Matt Kulukundis · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#136: Unordered Containers

\
\

Originally posted as TotW \#136 on June 23, 2017

*By [Matt Kulukundis](/cdn-cgi/l/email-protection#513a373c11363e3e363d347f323e3c)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/136](https://abseil.io/tips/136)

*“Sometimes, when the material is really good, you put expectations on yourself to make it the best possible show. You’re not just serving up the regular hash and doing your job and going home.”* — Peter Dinklage

TL;DR: See https://abseil.io/docs/cpp/guides/container for official and up-to-date recommendations. This tip *introduced* the new types, but is not the canonical reference.

## Introducing `absl::*_hash_map`

There is a new family of associative containers in town. They boast improvements to efficiency and provide early access to APIs from C++17. They also provide developers with direct control over their implementation and default hash functions, which is important for the long term evolution of a code base. New code should prefer these types over `std::unordered_map` . All of the maps and sets in this family have APIs that are nearly identical to `std::unordered_map`, so transitioning to them is easy.

For every `absl::*_hash_map` there is also an `absl::*_hash_set`; however, the diagrams will only depict the `map` case and we will often refer to just the `map`.

### `absl::flat_hash_map` and `absl::flat_hash_set`

<img src="/img/flat_hash_map.svg" style="margin:5px;width:50%" alt="Flat Hash Map Memory Layout" />

These should be your default choice. They store their `value_type` inside the main array. Because they move data when they rehash, elements don’t get pointer stability. If you need pointer stability or your values are large, consider using `absl::node_hash_map` instead, or `absl::flat_hash_map<Key, std::unique_ptr<Value>>`, possibly.

Warning: Because of pointer instability after `rehash()` code like `map["a"] = map["b"]` will access invalidated memory.

### `absl::node_hash_map` and `absl::node_hash_set`

<img src="/img/node_hash_map.svg" style="margin:5px;width:50%" alt="Node Hash Map Memory L ayout" />

These allocate their `value_type` in nodes outside of the main array (like `std::unordered_map`). Because of the separate allocation, they provide pointer stability (the address of objects stored in the map does not change) for the stored data and empty slots only require 8 bytes. Additionally, they can store things that are neither moveable nor copyable.

We generally recommend that you use `absl::flat_hash_map<K, std::unique_ptr<V>>` instead of `absl::node_hash_map<K, V>`, and similarly for `node_hash_set`.


