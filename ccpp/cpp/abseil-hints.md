---
search: false
title: "Abseil Performance Hints"
description: "abseil 团队的 [Performance Hints](https://abseil.io/fast/hints.html)，C++ 性能优化的\"3%\"哲学 + 8 大章实战。"
---
# Abseil Performance Hints

> 原文：<https://abseil.io/fast/hints.html> · 抓取：2026-06-10 · 内容许可：CC BY 4.0（abseil.io 文档）

abseil 团队的 [Performance Hints](https://abseil.io/fast/hints.html)，C++ 性能优化的"3%"哲学 + 8 大章实战。
本笔记为**完整原文转录**，所有 H2/H3 锚点保留，可直接 anchor 跳转。

## 目录

- [The importance of thinking about performance](#the-importance-of-thinking-about-performance)
- [Estimation](#estimation)
- [Measurement](#measurement)
- [API considerations](#api-considerations)
- [Algorithmic improvements](#algorithmic-improvements)
- [Better memory representation](#better-memory-representation)
- [Reduce allocations](#reduce-allocations)
- [Avoid unnecessary work](#avoid-unnecessary-work)
- [Code size considerations](#code-size-considerations)
- [Parallelization and synchronization](#parallelization-and-synchronization)
- [Protocol Buffer advice](#protobuf-advice)
- [C++-Specific advice](#c-specific-advice)
- [Bulk operations](#bulk-operations)
- [CLs that demonstrate multiple techniques](#cls-that-demonstrate-multiple-techniques)
- [Further reading](#further-reading)
- [Suggested citation](#suggested-citation)
- [Acknowledgments](#acknowledgments)

---


## 分篇阅读

正文按原章节顺序分篇，旧章节链接仍可跳转。

- [The importance of thinking about performance](./abseil-hints/01-sections)
- [Algorithmic improvements](./abseil-hints/02-sections)
- [Bit vectors instead of sets](./abseil-hints/03-sections)
- [Avoid unnecessary work](./abseil-hints/04-sections)
- [Precompute expensive information once](./abseil-hints/05-sections)
- [Use caching to avoid repeated work](./abseil-hints/06-sections)
- [Avoid logging on hot code paths](./abseil-hints/07-sections)
- [Reduce template instantiations](./abseil-hints/08-sections)
- [SIMD Instructions](./abseil-hints/09-sections)
- [absl::btree_map/absl::btree_set](./abseil-hints/10-sections)
- [Bulk operations](./abseil-hints/11-sections)
- [Suggested citation](./abseil-hints/12-sections)

<script setup>
import LegacyAnchorRedirect from "../../.vitepress/components/LegacyAnchorRedirect.vue"
import targets from "./abseil-hints/legacy-anchors.json"
</script>

<LegacyAnchorRedirect :targets="targets" />
