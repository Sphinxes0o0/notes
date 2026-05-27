---
type: source
source-type: pdf
title: "Think eBPF for Kernel Security Monitoring — Falco at Apple (eBPF Summit 2021)"
author: "Eric Sage & Melissa Kilby"
date: 2021
size: medium
path: raw/PDFs/papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf
summary: "Apple Falco团队eBPF Summit演讲：BPF vs内核模块优势、LSM hook、Ringbuf、高价值Syscall监控"
tags: [security, ebpf, falco, apple, runtime-security, syscall, lsm, ringbuf]
---

# Think eBPF for Kernel Security Monitoring — Falco at Apple

## 核心内容

**Authors:** Eric Sage & Melissa Kilby | eBPF Summit 2021

### 为什么 Apple 选择 BPF 而非内核模块

BPF 相比内核模块的核心优势：

| 方面 | BPF | 内核模块 |
|------|-----|---------|
| 权限范围 | 有限（通过 hook 点） | 全权限（完全内核访问）|
| 外部依赖 | 无 | 有（依赖内核版本）|
| 调试工具 | bpftool 统一 | 分散 |
| 兼容性 | CO-RE 跨版本 | 每次内核升级需重编 |
| 安全性 | Verifier 静态校验 | 无内置安全保证 |

### BPF 运行时安全监控架构

**Falco 架构：**
```
内核 eBPF 程序 → Ringbuf → Falco 用户态引擎 → 规则匹配 → 告警
```

**关键组件：**
- **eBPF probe** — 附加到 LSM hook / tracepoint / syscall entry
- **Ringbuf** — per-CPU 无锁环形缓冲区，比 perf buffer 更高效
- **规则引擎** — YAML 规则描述告警条件（syscall + 容器上下文）
- **告警通道** — stdout / gRPC / webhook / SIEM

### 高价值 Syscall 监控列表

**文件操作：** `open/creat/read/write/chmod/rename/unlink`
**进程操作：** `execve/ptrace/clone`
**网络操作：** `connect/sendto/bind/listen/accept`
**权限操作：** `setuid/setns/unshare`

### Apple 生产流水线

1. 预编译 Falco probes (`.o` BPF 对象文件)
2. 打包进 `libs` release
3. Falco release 时包含预编译 probe
4. 用户自定义 Falco rules

### BPF Hook 类型对比

| Hook 类型 | 适用场景 | 示例 |
|-----------|---------|------|
| LSM (security_*) | 访问控制、安全策略 | security_bprm_check, security_file_open |
| tracepoint | 稳定内核事件 | syscalls/sys_enter_execve |
| kprobe/kretprobe | 任意内核函数 | ext4_file_open, tcp_v4_connect |
| XDP | 网络包处理 | 高速包过滤、转发 |

## 关键引用

> "BPF programs are verified before loading — the kernel will never crash from a BPF program."

> "BPF has limited access to kernel internals, while kernel modules have full hardware access."

## 相关页面

- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控
- [[entities/linux/security/linux-security-observability-ebpf]] — eBPF 安全可观测性
- [[sources/notes-security]] — 安全工具（Masscan, Falco, Snort）
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
