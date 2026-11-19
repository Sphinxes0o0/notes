---
type: source
source-type: bookmark
title: "基于eBPF的Android设备网络优化实践与探索"
author: "kernel.meizu.com"
date: 2023-11-06
url: "https://kernel.meizu.com/2023/11/06/Optimization-practice-and-exploration-of-Android-devices-based-on-eBPF/"
summary: "Android利用eBPF实现Doze模式网络控制，通过tcp_v4_do_rcv钩子和BPF_CGROUP_RUN_PROG_SOCK_OPS实现基于UID的细粒度流量过滤"
tags: [linux, ebpf, android, networking, kernel, sock-ops, doze]
created: 2026-05-28
---

# 基于eBPF的Android设备网络优化实践与探索

## 核心内容

### eBPF架构

- **沙箱程序**：运行在内核虚拟机的字节码
- **C-like代码**：编译为字节码，附加到内核hook
- **JIT编译**：字节码转原生机器码
- **Verifier**：检查程序大小和复杂度
- **权限控制**：SELinux neverallow策略

### Android bpfloader机制

```
加载流程：
1. 从 /system/etc/bpf/ 和 /vendor/etc/bpf/ 读取 .o 文件
2. 创建 maps
3. 加载 programs
4. 程序固定到 /sys/fs/bpf/ 持久化
```

### 网络控制示例（Doze模式）

```c
// Hook: tcp_v4_do_rcv via bpf_skops_parse_hdr
BPF_CGROUP_RUN_PROG_SOCK_OPS → bpf_owner_match → DROP/ALLOW

// 过滤逻辑
if (enabledRules & (DROP_IF_SET | DROP_IF_UNSET) & (uidRules ^ DROP_IF_UNSET))
    return DROP;
```

**关键能力**：基于UID的TCP/UDP流量控制，无需修改内核源码。

### 多层次Hook

| 层次 | Hook点 | 程序类型 |
|------|--------|----------|
| XDP | NIC驱动RX最早期 | BPF_PROG_TYPE_XDP |
| TC Ingress | sch_handle_ingress | BPF_PROG_TYPE_SCHED_CLS |
| Socket Filter | Raw socket路径 | BPF_PROG_TYPE_SOCKET_FILTER |
| **Sock_ops** | TCP socket操作 | BPF_PROG_TYPE_SOCK_OPS |

## 关键引用

> "eBPF enables fine-grained kernel extensibility without kernel source modifications"

> "Android leverages eBPF for Doze mode network restrictions, enabling UID-based traffic control while maintaining system security"

## 相关页面

- [[entities/linux/ebpf/ebpf-networking]] — eBPF网络多层次Hook（XDP/TC/Sock_ops）
- [[entities/linux/network/linux-network-protocols]] — TCP协议实现细节
- [[entities/linux/kernel/net]] — Linux网络子系统
