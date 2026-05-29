---
type: source
source-type: web
title: "Building a Language VM in C (Iridium)"
author: "SubnetZero"
date: 2024-01-01
summary: "从硬件基础到完整VM：用C构建语言虚拟机，Part 00-33+覆盖寄存器/汇编/指令集/字节码"
path: raw/web/building-language-vm
---

# Building a Language VM in C (Iridium)

## 核心内容

### 课程结构（33+ Parts）

**Part 00 — 计算机硬件速成**（本来源覆盖）
- 程序编译流程：源码 → 汇编 → 目标文件 → 可执行文件
- GCC 编译器、汇编器、链接器的工作原理
- CPU 寄存器作为高速存储
- JVM / CLR / Python VM 的对比
- VM 执行的优缺点（速度、资源开销）

**Part 01+ — 简单 VM 实现**
- 指令集设计
- 字节码解释器
- 寄存器 VM vs 栈 VM

### 关键概念
- **Language VM**：执行字节码的虚拟计算机，与物理 CPU 类似
- **JVM / CLR 类比**：write once, run anywhere 的跨平台方案
- **编译 vs 解释**：编译器将源码转为机器码/字节码，解释器逐条执行
- **寄存器抽象**：比栈更高效，但指令更复杂

### Iridium VM 特点
- 自定义指令集（非 x86）
- 纯 C 实现
- 完整源码公开

## 相关页面

- [[virtual-machine]] — 语言虚拟机通用概念
- [[interpreter]] — 解释器与 VM 的关系
- [[compiler-from-scratch]] — 编译器前端（词法/语法/语义分析）

## 来源详情

- 网站: [blog.subnetzero.io](https://blog.subnetzero.io/post/building-language-vm-part-00/)
- 系列: Part 00 ~ Part 33+
