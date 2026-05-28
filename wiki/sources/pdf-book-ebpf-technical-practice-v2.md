---
type: source
source-type: pdf
title: eBPF 权威指南：技术实践与内核源码分析（第2版）
author: 倪宏飞
date: 2022
size: medium
path: raw/PDFs/books/eBPF_technical_practice_v2.pdf
summary: eBPF 进阶实战：CO-RE/尾调用/RingBuf/安全审计/网络/可观测性
created: 2022
tags: [ebpf]
---
# eBPF 技术实践（第二版）

## 核心内容

- **CO-RE**：BTF、CO-RE、BTFGen，内核版本兼容
- **eBPF 验证器**：安全检查、跳转边界、指令限制
- **Map 类型**：Hash/Array/CPU/Socket/Stack/Perf/RingBuf
- **尾调用**：bpf_tail_call、程序链、跳转限制
- **网络**：XDP 原生驱动、TC qdisc、sk_buff 操作
- **可观测性**：USDT probes、tracepoints、perf events
- **安全**：seccomp、LSM hook、安全审计
- **工具链**：bpftool、libbpf-bootstrap、cilium/ebpf-go

## 相关页面
- [[pdf-book-ebpf-basics-cn]]
- [[pdf-book-ebpf-beginners-guide]]
- [[pdf-ebpf-technical-practice]]
- [[pdf-bpf-security-auditing-google]]