---
type: entity
tags: [rust, systems-programming, memory-safety, concurrency]
created: 2026-05-23
sources: [pdf-rust-intro, pdf-cpp-modern-books]
---

# Rust Programming Language

## 定义

Rust 是由 Mozilla（现 Rust 基金会）开发的系统级编程语言，旨在提供高性能并发、内存安全和现代语言特性。通过所有权模型在编译时确保内存安全，无需垃圾回收。

## 核心特性

### 所有权模型 (Ownership)

- 每个值在任意时刻只有唯一的**所有者** (owner)
- 所有者离开作用域后值自动释放
- 通过**借用** (borrowing) 获取引用：`&T`（不可变）或 `&mut T`（可变）
- 编译时借用检查器 (Borrow Checker) 确保引用有效性

### 借用规则

1. 任意时刻：**要么一个可变引用，要么多个不可变引用**
2. 引用不能超过所有者的生命周期

### 生命周期 (Lifetimes)

- 函数签名中的生命周期标注 `'a` 帮助编译器确定引用合法范围
- 编译器在编译时检测不合法引用

### 零成本抽象

- 泛型与特征 (Traits) 在编译后**单态化** (monomorphization)，不损失运行时性能
- 默认不可变、函数式编程风格

### 安全与不安全代码

- **Safe Rust** — 默认，编译器保证内存安全
- **Unsafe Rust** — `unsafe {}` 块取消借用检查，用于底层硬件操作

## 工具链

- **rustup** — 快速搭建/切换开发环境
- **cargo** — 包管理、编译、测试
- **crates.io** — 官方包注册中心

## 相关概念

- [[entities/cpp/smart-pointers]] — 智能指针与所有权语义对比
- [[entities/cpp/raii]] — RAII 资源管理（Rust 也采用类似模式）
- [[sys-prog-index]] — 系统编程导航
- [[cpp-index]] — C++ 模块导航（对比学习）

## 来源详情

- [[sources/pdf-rust-intro]] — Rust 入门指北 + Programming Rust + Rust 编程语言（官方中文版）
- [[sources/pdf-cpp-modern-books]] — C++ 对比参考
- [[sources/pdf-cpp-concurrency]] — C++ 并发模型对比参考
