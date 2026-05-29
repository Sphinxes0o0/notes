---
type: source
source-type: web
title: "Writing Interpreters in Rust: A Guide"
author: "rust-hosted-langs"
date: 2024-01-01
summary: "Rust实现解释器：自定义分配器(Sticky Immix)/安全包装/编译器/虚拟机/GC，适合有Rust基础的进阶者"
path: raw/web/rust-interpreters-book
---

# Writing Interpreters in Rust: A Guide

## 核心内容

### 5个Part，覆盖解释器全栈

**Part 1 — Allocation（分配）**
- 内存对齐（Alignment）
- 内存块获取
- 分配类型

**Part 2 — Sticky Immix Allocator**
- Bump Allocation（指针碰撞）
- 多内存块管理
- 分配 API 设计
- Sticky Immix 算法

**Part 3 — Eval-rs Interpreter**
- 安全的对象分配和解引用
- Tagged Pointers + Object Headers
- Symbols / Pairs / Arrays / Dicts
- S-Expression 解析
- Bytecode 设计
- VM 实现
- Compiler 实现

**Part 4 — Garbage Collection**（TODO）
- Tracing（追踪）
- Sweeping（清扫）
- Block Recycling（块回收）

### 推荐前置
- Bob Nystrom 的《Crafting Interpreters》
- 扎实的 Rust 基础（safe/unsafe 边界）

### 关键概念
- **Custom Allocator**：解释器独占堆，减少 GC 压力
- **Sticky Immix**：混合式算法，bump allocation + 分块回收
- **Tagged Pointer**：低频标记（immediate/b heap）节省内存
- **Safe Rust Wrapper**：unsafe 内存操作的安全抽象

## 相关页面

- [[interpreter]] — 解释器通用概念
- [[virtual-machine]] — 字节码虚拟机
- [[memory-hierarchy]] — 分配器与堆内存管理

## 来源详情

- 网站: [rust-hosted-langs.github.io/book](https://rust-hosted-langs.github.io/book/)
