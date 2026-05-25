---
type: source
source-type: github
title: "Linux Kernel 动手实验笔记"
date: 2026-05-25
path: raw/github/notes/kernel/handson/
summary: "Linux Kernel 动手实验：Rust 实现 RISC-V 裸机管理程序（boot/heap/trap）+ C 语言实现 1000 行操作系统（kernel/shell/user/disk）"
---

# Linux Kernel 动手实验笔记

## 核心内容

**两套实验项目：**

### 1. Rust RISC-V 裸机管理程序（hypervisor）

`1000lines/hypervisor/` — 用 Rust 实现 RISC-V 裸机环境下的管理程序/最小系统：

| 文件 | 主题 |
|------|------|
| src/main.rs | 入口点，boot 函数跳转到 main |
| src/trap.rs | trap 处理函数（CSR scause/sepc/stval 解析）|
| src/allocator.rs | 简单堆内存分配器 |
| src/print.rs | 打印宏 |
| hypervisor.ld | 链接脚本（.text.boot 等段）|
| Cargo.toml | no_std + alloc 依赖 |

**关键点：**
- `#![no_std]` 纯裸机环境
- `#![no_main]` + `#[unsafe(no_mang)]` 入口点
- RISC-V CSR 读写内联汇编：`csrr`, `csrw`
- `wfi`（Wait for Interrupt）空闲循环
- `unimp` 非法指令触发 trap

### 2. C 语言 1000 行操作系统（os）

`1000lines/os/` — 用纯 C 实现一个迷你操作系统：

| 文件 | 主题 |
|------|------|
| kernel.c / kernel.h | 内核核心 |
| user.c / user.h | 用户态模拟 |
| shell.c | 简单 shell |
| common.c / common.h | 公共定义 |
| kernel.ld / user.ld | 分离链接脚本 |
| disk/hello.txt, meow.txt | 虚拟磁盘内容 |
| run.sh | 运行脚本 |

## 来源详情

- **来源路径**: `raw/github/notes/kernel/handson/`
- **领域**: 操作系统实现、RISC-V、裸机编程、Rust no_std、系统编程
