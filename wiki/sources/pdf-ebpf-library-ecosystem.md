---
---
type: source
source-type: pdf
title: "eBPF Library Ecosystem Overview in Go, Rust, Python, C and More"
author: "Kyle Quest"
date: 2021
size: small
path: raw/PDFs/papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf
summary: "eBPF生态库全景评测：BCC/libbpf vs cilium/ebpf vs aya vs bcc(Python)，功能/性能/易用性对比"
tags: [ebpf, ecosystem, golang, rust, python, c, bcc, libbpf, aya]
---

# eBPF Library Ecosystem Overview in Go, Rust, Python, C and More

## 核心内容

**Author:** Kyle Quest | 2021

### 生态库全景

eBPF 生态库按编程语言分为以下几类：

| 语言 | 库 | 定位 | 成熟度 |
|------|-----|------|--------|
| C | **BCC** (BPF Compiler Collection) | 追踪工具箱，脚本化，最流行 | 高 |
| C | **libbpf** | 官方库，低层次，CO-RE 友好 | 高 |
| Go | **cilium/ebpf** | 纯 Go，主流之选 | 高 |
| Go | **dropbox/goebpf** | 纯 Go，专注网络 | 中 |
| Go | **iovisor/gobpf** | BCC wrapper | 低 |
| Go | **aquasecurity/libbpfgo** | libbpf Go wrapper | 中 |
| Python | **bcc** (bcc-python) | BCC Python 绑定，最广泛 | 高 |
| Rust | **aya** | Rust 生态 eBPF 库，async 支持 | 高 |
| Rust | **libbpf-rs** | libbpf Rust 绑定 | 中 |
| Other | Lua / Node.js / Ruby | 脚本语言绑定 | 低 |

### 各库详细对比

#### BCC (BPF Compiler Collection)
- **特点：** 嵌入了 Python/Lua 解释器，动态编译 BPF C 代码
- **适用场景：** 快速原型、临时调试、bpftrace 底层
- **缺点：** 每次运行需编译，部署体积大

#### libbpf (官方)
- **特点：** 内核源码树官方库，预编译 BPF 对象文件，CO-RE
- **适用场景：** 生产环境、轻量级部署、长期维护项目
- **缺点：** API 层次低，需手动管理 map/program 生命周期

#### cilium/ebpf (Go)
- **特点：** 纯 Go 实现，无 C 依赖，类型安全 API
- **适用场景：** Kubernetes CNI/网络插件（cilium 本身使用）
- **缺点：** 与内核版本强相关，字段偏移需手动管理

#### aya (Rust)
- **特点：** Rust 生态原生库，async/await 支持，零 C 依赖
- **适用场景：** Rust 项目集成 eBPF，要求高性能与内存安全
- **缺点：** 生态相对年轻

### 选型决策树

```
项目类型？
├── 快速原型/调试
│   └── BCC (Python/Lua) 或 bpftrace
├── 生产网络/CNI 项目
│   ├── Go → cilium/ebpf
│   └── Rust → aya
├── 轻量级库/工具
│   └── libbpf (C)
└── Rust 原生项目
    └── aya
```

### Verdict

- **功能优先：** BCC（内置 Python/Lua，动态编译，最灵活）
- **官方/轻量：** libbpf（内核官方，预编译，无依赖）
- **Go 生态首选：** cilium/ebpf（类型安全，零 C 依赖，cilium 验证）
- **Rust 生态首选：** aya（async 支持，内存安全，零 C 依赖）

## 关键引用

> "BCC is the most feature-rich but requires embedding a compiler; libbpf is the most portable but lowest-level."

> "cilium/ebpf is the de facto standard for Go projects that need eBPF."

## 相关页面

- [[entities/linux/ebpf/ebpf-ecosystem]] — eBPF 生态库与工具
- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
