---
type: entity
tags: [Linux, RISC-V, 裸机, Rust, hypervisor, 操作系统]
created: 2026-05-25
sources: [notes-kernel-handson]
---

# 动手实验：Rust RISC-V 裸机管理程序

## 定义

一个用 Rust (`#![no_std]`) 实现的 RISC-V 裸机管理程序/最小系统，涵盖 boot 跳转、堆分配器、trap 处理等核心组件。

## 核心组件

### boot 入口点

```rust
#[unsafe(link_section = ".text.boot")]
pub extern "C" fn boot() -> ! {
    asm!(
        "la sp, __stack_top",   // 初始化栈指针
        "j {main}",            // 跳转到 main
        main = sym main,
        options(noreturn)
    );
}
```
- 使用 link_section 将 boot 函数放到特定段
- 手动初始化栈顶，跳转到 Rust main

### trap 处理（trap.rs）

解析 RISC-V CSR（Control and Status Registers）：

```rust
let scause = read_csr!("scause");  // trap 原因
let sepc    = read_csr!("sepc");    // 发生 trap 的 PC
let stval   = read_csr!("stval");   // 附加信息

// scause 0x8000_0000_0000_0000 位为 1 表示中断
match scause {
    0  => "instruction address misaligned",
    2  => "illegal instruction",  // unimp 触发此类型
    8  => "environment call from U-mode",
    11 => "environment call from M-mode",
    ...
}
```

### 内存分配器（allocator.rs）

简单堆内存分配器（与 `__heap` / `__heap_end` 符号配合）。

### 打印宏（print.rs）

`println!` 宏用于裸机环境输出。

## 关键设计

- **no_std + alloc**：禁用标准库但可用 `alloc` crate（Vec 等动态集合）
- **#![no_main]**：`boot()` 是真正的入口，非 Rust `main`
- **内联汇编**：RISC-V CSR 读写通过 `core::arch::asm!` 实现
- **wfi 空闲循环**：`Wait for Interrupt`，降低功耗等待外设中断

## 相关概念

- [[notes-kernel-handson]] — 源码来源
- [[linux-kernel-virt-kvm]] — KVM 虚拟化与本 hypervisor 概念相关
- [[rust-language]] — Rust no_std/嵌入式编程能力

## 来源详情

- [[notes-kernel-handson]] — `1000lines/hypervisor/src/`
