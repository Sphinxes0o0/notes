---
type: source
source-type: pdf
title: "Rethinking the Linux Kernel — eBPF as a Microkernel (Thomas Graf, 2020)"
author: "Thomas Graf"
date: 2020
size: medium
path: raw/PDFs/papers/bpf-rethinkingthelinuxkernel-200303183208.pdf
summary: "Cilium创始人Thomas Graf里程碑演讲：eBPF将Linux内核转变为微内核+可组合服务层，解决内核分层抽象代价和20年API碎片化问题"
tags: [ebpf, cilium, linux-kernel, networking, kubernetes, microkernel]
---

# Rethinking the Linux Kernel — eBPF as a Microkernel

## 核心内容

**Author:** Thomas Graf (Cilium 创始人) | 2020

### Linux 内核的问题

**分层抽象代价：**
- TCP/IP 协议栈每层都有独立抽象（socket → inet_sock → tcp_sock → sk_buff）
- 穿越每层都要付出转换开销
- 无法绕过——每层都理解不同层次的元数据

**20 年 API 碎片化：**
- iptables (netfilter)、seccomp、tc (traffic control)、ovsctl (Open vSwitch)
- 每套工具有独立配置语言、数据模型、调试工具
- 运维人员需要掌握全部

**内核不知容器：**
- Linux 内核只知道 namespace / cgroup
- 不知道 Kubernetes Pod、Service、Label
- 不知道应用层协议（HTTP/gRPC/Kafka）

### eBPF 作为解决方案

**核心公式：**
```
沙盒 VM + Verifier 安全校验 + JIT 本地编译 = 内核可编程性
```

**eBPF Map 类型一览：**
| 类型 | 用途 | 原子支持 |
|------|------|---------|
| Hash Map | 键值存储 | 是 |
| Array Map | 索引数组 | 是 |
| LRU Hash | 自动淘汰 | 是 |
| Ring Buffer | 事件流 | 否 |
| Stack Trace | 栈回溯 | 否 |
| LPM Trie | 前缀匹配 | 是 |

**可组合服务层：**
- 100% 模块化：每个 eBPF 程序专注单一功能
- 快速迭代：无需等待内核上游周期
- 数据平面与控制平面分离

### Cilium 让 Linux 感知 Kubernetes

```
Kubernetes Pod/Label/Service
        ↓ (Cilium agent)
eBPF 程序附加到内核 hook
        ↓
内核现在知道：Pod 身份 ≠ IP 地址
```

**解决的问题：**
- 网络策略不再依赖 IP（Pod IP 临时）
- 身份基于 Kubernetes NetworkPolicy
- 服务负载均衡替代 kube-proxy

### 生态项目

- **Katran** (Facebook) — L4 负载均衡
- **bcc / bpftrace** — 追踪工具
- **Falco** — 运行时安全
- **Cilium** — Kubernetes 网络与安全

## 关键引用

> "eBPF is a highly efficient sandboxed virtual machine in the Linux kernel making the Linux kernel programmable at native execution speed."

> "The kernel does not know about containers or Kubernetes pods — there is no container ID in the kernel."

## 相关页面

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-networking]] — eBPF 网络与 Cilium
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
