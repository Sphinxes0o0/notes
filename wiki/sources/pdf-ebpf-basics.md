---
type: source
source-type: pdf
title: "eBPF基础"
author: "未知"
date: 2023
size: small
path: raw/PDFs/books/eBPF基础.pdf
summary: "eBPF入门教程：80页讲解BPF到eBPF演进、11个64位寄存器、JIT编译、Maps、BTF、CO-RE"
tags: [ebpf, linux-kernel, beginner, books]
---

# eBPF基础

## 核心内容

**Author:** 未知 | 80页 | 扫描版（完整文本）

### BPF → eBPF 演进

**BPF (Berkeley Packet Filter)：**
- 2.5版本引入，网络封包过滤
- tcpdump基于BPF

**eBPF (extended BPF)：**
- 3.18版本引入，功能增强
- 独立于网络子系统，通用数据模型

### eBPF 指令集架构

**11个64位寄存器（32位子寄存器）：**
- `r0-r9`：通用寄存器
- `r10`：栈指针
- 函数调用约定：r0=返回值，r1-r5=参数

**指令格式（7类）：**
- LD/LDX/ST/STX：加载/存储
- ALU/ALU64：算术运算
- JMP：跳转

### BPF Maps

- 键值对存储，通过文件描述符定位
- 值是不透明的Blob（任意数据）
- 多个eBPF程序可共享同一Map

### CO-RE (Compile Once, Run Everywhere)

- BTF（BPF Type Format）记录内核数据结构布局
- `bpf_core_field_exists()` 检测字段是否存在
- 线性fallback策略保证跨内核兼容性

### Pinning机制

解决Map跨进程共享问题：BPF资源 pinning 到内核匿名inode，通过路径名访问。

## 相关页面
- [[entities/linux/ebpf/ebpf-overview]] — eBPF核心架构
- [[sources/pdf-ebpf-books]] — eBPF书籍索引
- [[sources/pdf-ebpf-technical-practice]] — eBPF技术实践
- [[kernel-net-index]] — Linux网络子系统