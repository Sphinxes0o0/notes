---
type: source
tags: [rust, systems-programming, beginner, ownership, concurrency]
source-type: pdf
created: 2026-05-23
sources: [pdf-rust-intro]
title: "Rust Programming Books (3 volumes)"
author: "Sphinx (notes), Jim Blandy, Jason Orendorff, Leonora F.S. Tindall; Steve Klabnik, Carol Nichols, shieber"
date: 2024
size: large
path: raw/PDFs/books/
summary: "三册 Rust 编程书籍：Let's Get Rusty! 入门指北、Programming Rust（O'Reilly 第2版中文翻译）、Rust 编程语言（官方中文版）"
---

# Rust Programming Books

## 1. Let's Get Rusty! — Rust 入门指北

**作者**: Sphinx (notes) | **日期**: 2024

Rust 入门笔记两册：基础设施搭建（rustup/cargo/工具链/IDE配置）和语言简介（所有权/借用/生命周期/并发/语法基础）。

### 核心主题

#### 基础设施
- rustup 安装与配置（国内源、补全）
- cargo 配置与 crates.io 换源
- VS Code + rust-analyzer

#### 语言简介
- **所有权** — 唯一所有者，作用域结束自动释放
- **借用** — `&T` (不可变) vs `&mut T` (可变)
- **生命周期** — 借用检查器在编译阶段确保引用安全
- **并发** — `std::sync::Mutex`、`Arc`、Rayon 库
- **特征 (Traits)** — Rust 的接口/多态机制

## 2. Programming Rust, 2nd Edition (中文翻译)

**作者**: Jim Blandy, Jason Orendorff, Leonora F.S. Tindall | **页数**: 674

O'Reilly 出品，Rust 系统级编程权威指南。从基础语法到高级并发和 unsafe 编程，翻译版涵盖完整内容。

### 核心主题
- Rust 概览：函数、测试、命令行参数、Web 服务
- 所有权、引用与生命周期（深度剖析）
- 结构体、枚举、trait 与方法
- 闭包与迭代器（零成本抽象）
- 集合与字符串处理
- 错误处理（Result/Option/panicking/故障传播）
- Cargo、模块与 crate 管理
- 测试与文档
- 标准 trait：From/Into、Deref、Drop、Sized、Clone、Iterator
- 函数式编程：迭代器链、消费器、适配器
- 智能指针：Box、Rc、Arc、Cell、RefCell
- 内部可变性模式
- 并发：线程、Mutex、屏障、通道、Rayon 数据并行
- Unsafe Rust：原始指针、FFI、内联汇编
- 宏系统：声明宏、过程宏
- 异步编程与 async/await

## 3. Rust 编程语言 (The Rust Programming Language 中文版，shieber)

**作者**: Steve Klabnik, Carol Nichols; shieber (译者) | **页数**: 412

Rust 官方教程的中文翻译版，从基础到进阶系统学习 Rust。

### 核心主题
- 入门指南：安装、Hello World、Cargo
- 常见编程概念：变量、数据类型、函数、控制流
- 所有权：栈与堆、引用与借用、切片
- 结构体与方法
- 枚举与模式匹配
- 模块系统
- 常见集合：Vector、String、HashMap
- 错误处理
- 泛型、Trait 与生命周期
- 测试
- I/O 项目：命令行程序
- 函数式特性：闭包与迭代器
- 智能指针：Box、Deref/Drop trait、Rc、RefCell
- 并发：线程、消息传递、共享状态、Send/Sync
- 模式匹配
- Unsafe Rust
- 高级类型与高级特征
- 宏

## 相关页面

- [[entities/rust/rust-language]] — Rust 概念页
- [[entities/cpp/smart-pointers]] — C++ 智能指针（所有权对比）
- [[entities/cpp/raii]] — RAII 模式（Rust 类似设计）
- [[entities/cpp/concurrency]] — C++ 并发模型对比
- [[sys-prog-index]] — 系统编程导航
- [[cpp-index]] — C++ 模块导航
