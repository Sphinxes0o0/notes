---
type: source
source-type: pdf
title: "eBPF基础"
author: "方院生"
date: 2023
size: small
path: raw/PDFs/books/eBPF基础.pdf
summary: "eBPF 入门书：原理/工具链/CO-RE/常用场景（网络/安全/观测）"
---

# eBPF基础

## 核心内容

- **eBPF 原理**：虚拟机架构、Map 类型、尾调用、Helper 函数
- **工具链**：clang+llvm 编译、bpftool、libbpf、bcc
- **CO-RE**：BTF、CO-RE 实现跨内核兼容的原理
- **程序类型**：XDP/TC/tracepoint/kprobe/uprobe/raw_tracepoint 等
- **应用场景**：网络加速、防火墙规则、系统追踪、安全审计
- **实践**：最小 eBPF 程序、Ring Buffer、RingBuf vs Perf Buffer

## 相关页面
- [[pdf-book-ebpf-beginners-guide]]
- [[pdf-ebpf-technical-practice]]
- [[pdf-bpf-rethinking-kernel]]
- [[pdf-bpf-security-auditing-google]]