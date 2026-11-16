---
type: entity
tags: [rust, programming-language, systems-programming, memory-safety, ownership]
created:2026-06-08
sources: [pdf-book-programming-rust, handson-rust-interpreters]
---

# Rust Programming Language

## 定义

Rust 是由 Mozilla研究院 Graydon Hoare发起、现由 Rust Foundation维护的系统级编程语言，以**零成本抽象、内存安全、并发安全、所有权系统**为核心设计目标，定位是 C/C++ 的现代化替代。Rust 通过编译期所有权检查（ownership/borrow checker）实现无 GC 的内存安全，避免缓冲区溢出、use-after-free、数据竞争等常见系统级错误。

##关键要点

- **Ownership**：每个值有唯一所有者，赋值/传参时 move；离开作用域自动 drop
- **Borrowing**：引用分为 `&T`（不可变，多重）/ `&mut T`（可变，排他），编译期检查别名+可变性
- **Lifetime**：借用有效期的标注，省略规则（lifetime elision）覆盖大多数场景
- **Trait**：类似 Haskell typeclass、Go interface，但支持静态分派和默认实现
- **Zero-cost abstraction**：迭代器/闭包/泛型全部内联，无运行时开销

##核心概念

- **Cargo**：包管理与构建工具（`Cargo.toml`、`Cargo.lock`、workspaces）
- **async/await**：`Future` trait + tokio/async-std运行时
- **unsafe**：5 个 superpowers（解引用裸指针、调用 unsafe 函数、访问/修改可变静态、访问 union字段、实现 unsafe trait）
- **macros**：`macro_rules!` + procedural macros（编译期 AST 操作）
- **no_std**：嵌入式场景，无标准库
- **embedded Rust**：RTIC、HAL、PAC、probe-rs工具链

## 相关页面

- [[entities/rust/rust-language]] — Rust语言参考
- [[entities/rust/embedded-rust-drivers]] —嵌入式驱动开发
- [[entities/rust/embedded-rust-rtic]] — RTIC实时框架
- [[sources/pdf-book-programming-rust]] — Programming Rust (O'Reilly)
- [[sources/handson-rust-interpreters]] — Writing Interpreters in Rust
