---
type: source
source-type: pdf
title: "eBPF技术实践 v2（龙蜥社区）"
author: "龙蜥社区 (Anolis) 浪潮/阿里云/东南大学"
date: 2023
size: medium
path: raw/PDFs/books/eBPF_technical_practice_v2.pdf
summary: "龙蜥社区eBPF技术实践白皮书v2：100页系统讲解eBPF开发流程/工具链/应用场景，龙芯+阿里云+东南大学联合编写"
tags: [ebpf, linux-kernel, tools, cloud-native, books]
---

# eBPF技术实践 v2（龙蜥社区）

## 核心内容

**Authors:** 龙蜥社区（浪潮电子、阿里云、东南大学）参编 | 100页

### eBPF开发流程

```
1. Clang编译 → eBPF object文件
2. iproute2/bpftool加载 → BPF ELF loader
3. BPF Verifier → 安全性校验
4. JIT编译器 → 目标机器码
5. 挂钩子系统（networking/tracepoint/XDP）
6. 用户空间通过 BPF Map 交换数据
```

### 挂钩点类型

- **Kprobe/Kretprobe**：内核函数入口/出口
- **Tracepoint**：内核静态追踪点
- **XDP**：网络数据包处理（eXpress Data Path）
- **TC（Traffic Control）**：流量控制
- **LSM**：Linux安全模块钩子

### BPF Map 类型

- **Hash Map**：通用键值存储
- **Array**：索引数组
- **LRU Hash**：缓存淘汰
- **Ring Buffer**：高效事件传递
- **Stack Trace Map**：性能分析

### 应用场景

- 网络监控（Cilium Hubble）
- 安全审计（Falco/KRSI）
- 性能分析（bpftrace/bcc）

## 相关页面
- [[entities/linux/ebpf/ebpf-overview]] — eBPF核心架构
- [[sources/pdf-ebpf-books]] — eBPF书籍索引
- [[sources/pdf-ebpf-papers]] — eBPF论文索引
- [[kernel-net-index]] — Linux网络子系统