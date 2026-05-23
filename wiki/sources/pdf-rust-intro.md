---
type: source
tags: [rust, systems-programming, beginner]
source-type: pdf
title: "Let's Get Rusty! — Rust 入门指北"
author: "Sphinx (notes)"
date: 2024
size: small
path: raw/github/notes/resources/docs/rust/
summary: "Rust 入门笔记两册：基础设施搭建（rustup/cargo/工具链/IDE配置）和语言简介（所有权/借用/生命周期/并发/语法基础）"
---

# Let's Get Rusty! — Rust 入门指北

## 第一部分：基础设施

### 工具链安装

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### rustup 配置

- **补全**：`rustup completions zsh > ~/.zfunc/_rustup`
- **国内源**：清华大学 TUNA 镜像
  - `RUSTUP_UPDATE_ROOT`、`RUSTUP_DIST_SERVER` 环境变量

### cargo 配置

- **换源**：通过 `config.toml` 配置 sparse 稀疏索引镜像
- **crates.io** — Rust 官方 Package 管理中心

### IDE 支持

- VS Code + rust-analyzer

## 第二部分：语言简介

### 核心概念

1. **所有权** — 唯一所有者，作用域结束自动释放
2. **借用** — `&T` (不可变) vs `&mut T` (可变)
3. **生命周期** — 借用检查器在编译阶段确保引用安全
4. **并发** — `std::sync::Mutex`、`Arc`、Rayon 库
5. **特征 (Traits)** — Rust 的接口/多态机制

### 语法基础

- `let` 绑定、snake_case 命名
- 默认不可变变量
- 模式匹配 (`match`)
- 闭包 (closure) 与迭代器
- 枚举与错误处理 (`Option`/`Result`)

## 相关页面

- [[entities/rust/rust-language]] — Rust 概念页
- [[entities/cpp/smart-pointers]] — C++ 智能指针（所有权对比）
- [[entities/cpp/raii]] — RAII 模式（Rust 类似设计）
- [[sys-prog-index]] — 系统编程导航
