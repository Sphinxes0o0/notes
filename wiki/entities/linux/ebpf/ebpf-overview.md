---
type: entity
tags: [linux, ebpf, kernel, tracing, sandbox-vm]
created: 2026-05-22
sources: [pdf-ebpf-books, pdf-ebpf-papers]
---

# eBPF Overview

## 定义

eBPF (extended Berkeley Packet Filter) 是 Linux 内核中的一个高效沙盒虚拟机，在内核空间运行字节码，实现内核可编程化，无需修改内核源码或加载内核模块。eBPF 程序以事件驱动方式在内核 hook 点执行，安全性由 Verifier 校验器保证，执行效率由 JIT 编译器达到原生性能。

## 核心架构

### 执行流程
1. C/Rust 代码通过 LLVM/Clang 编译为 eBPF 字节码（ELF object 文件）
2. 用户态程序通过 `bpf()` 系统调用加载字节码到内核
3. **Verifier** 静态校验字节码安全性（控制流图分析、内存访问边界检查）
4. **JIT 编译器** 将字节码编译为 native 机器码（x86_64/arm64/ppc64/s390x 等）
5. 根据程序类型挂载到不同内核 hook 点，等待事件触发执行
6. 用户态通过 **eBPF Map** 与内核 BPF 程序双向通信

### 关键组件

| 组件 | 作用 |
|------|------|
| **Verifier** | 静态分析字节码，确保不崩溃内核、不死循环、不越界内存访问 |
| **JIT Compiler** | 将字节码编译为 native 机器码，达到内核原生执行速度 |
| **Maps** | 键值存储，跨 BPF 程序调用和用户态双向通信，类型包括 Array/Hash/LRU/Ringbuf/StackTrace/LPM 等 |
| **Helpers** | BPF 程序调用的内核白名单 API（最多5参数），如 `bpf_map_lookup_elem`、`bpf_ktime_get_ns`、`bpf_trace_printk` |
| **Tail Calls** | 通过 `bpf_tail_call` 将控制权从一个 BPF 程序跳转给另一个，复用 stack frame，无函数调用开销 |
| **CO-RE** | Compile Once – Run Everywhere，通过 BTF 类型信息实现跨内核版本可移植性 |
| **BTF** | BPF Type Format，紧凑的内核类型信息格式，替代 vmlinux.h，支持 CO-RE 重定位 |

### 程序类型分类

| 类别 | 程序类型 | 用途 |
|------|----------|------|
| **Tracing** | kprobe, kretprobe, tracepoint, perf_event, uprobe | 系统可观测性、性能分析 |
| **Networking** | XDP, TC, sock_ops, sk_msg, sk_skb, socket_filter, cgroup_sock | 高速网络处理、负载均衡、防火墙 |
| **Security** | LSM | 运行时安全策略强制执行 |
| **Other** | flow_dissector, lwt_in/out/xmit | 分片解析、Lightweight tunneling |

### BPF Verifier 校验流程

1. **第一阶段**：深度优先遍历控制流图，确保是有向无环图（DAG），检查函数深度和指令数上限
2. **第二阶段**：逐条检查字节码指令 — 寄存器读写属性、内存越界、helper 函数调用参数、指针类型安全

### Maps 类型一览

- `BPF_MAP_TYPE_ARRAY` / `PERCPU_ARRAY` — 数组，高性能计数
- `BPF_MAP_TYPE_HASH` / `PERCPU_HASH` / `LRU_HASH` — 哈希表，通用键值
- `BPF_MAP_TYPE_PROG_ARRAY` — 程序数组，实现 Tail Call 跳转表
- `BPF_MAP_TYPE_PERF_EVENT_ARRAY` — perf 事件，推送数据到用户态
- `BPF_MAP_TYPE_RINGBUF` — 无锁环形缓冲区（替代 perf buffer，减少内存开销）
- `BPF_MAP_TYPE_LPM_TRIE` — 最长前缀匹配，IP 范围查找
- `BPF_MAP_TYPE_DEVMAP` / `CPUMAP` — 网络设备/CPU 重定向
- `BPF_MAP_TYPE_SOCKMAP` — socket 重定向

### eBPF vs cBPF

| 维度 | cBPF (经典) | eBPF |
|------|-------------|------|
| 寄存器 | 2 个 32-bit | 11 个 64-bit (r0-r10) |
| 栈空间 | 无 | 512 字节 |
| 指令宽度 | 64-bit | 64-bit |
| JIT | 可选 | 默认启用 |
| 程序类型 | 仅网络过滤 | tracing/networking/security 全类别 |
| Maps | 无 | 完整支持 |

## 关键概念

### CO-RE 原理
CO-RE 通过 BTF 捕获内核类型信息，Clang 记录字段重定位信息（字段偏移、是否存在、类型大小），libbpf 在加载时根据目标内核 BTF 调整字节码，实现一次编译到处运行。

### BPF-BPF 函数调用
4.16+ 内核和 LLVM 6.0+ 支持，不再需要 `__always_inline`。每个函数生成独立 JIT image，JIT 最后阶段修复函数调用地址。对 CPU i-cache 友好，减小生成 object 体积。

### Tail Call 限制
- 只能尾调用相同类型的 BPF 程序
- 最多 33 次尾调用（加上初始程序共 34 次迭代上限）
- 5.10+ 开始支持与 BPF-BPF 调用混合使用（但可能栈溢出）

## 相关概念

- [[entities/linux/ebpf/ebpf-xdp]] — XDP 快速数据路径
- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控
- [[entities/linux/ebpf/ebpf-networking]] — eBPF 网络与 Cilium
- [[entities/linux/ebpf/ebpf-ecosystem]] — eBPF 生态库
- [[kernel-subsystems-index]] — Linux 内核子系统（crypto/locking/IPC/RCU）
- [[kernel-net-index]] — Linux 网络子系统（sk_buff/Netfilter/TCP）
- [[tools-index]] — 工具索引（tcpdump/bpftool）

## 来源详情

- [[sources/pdf-ebpf-books]] — 《eBPF基础》白皮书 + 《eBPF技术实践》（龙蜥社区）+ Liz Rice入门
- [[sources/pdf-ebpf-papers]] — Thomas Graf eBPF架构论文 + Cilium/Falco/Google/Apple/rootkit论文
- [[entities/linux-ebpf-fundamentals]] — eBPF基础教程（80页入门）
- [[entities/linux-ebpf-technical-practice]] — eBPF技术实践白皮书v2（龙蜥社区100页）
