---
type: source
source-type: pdf
title: "Fast-Packet-Processing using eBPF and XDP (UFMG)"
author: "Marcos A. M. Vieira"
date: 2021
size: medium
path: raw/PDFs/papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf
summary: "UFMG论文：XDP高速数据包处理技术，BPF指令格式详解，XDP~20Mpps vs TC~5Mpps vs Netfilter~1Mpps性能对比"
tags: [ebpf, xdp, networking, packet-processing, performance, linux]
---

# Fast-Packet-Processing using eBPF and XDP

## 核心内容

**Author:** Marcos A. M. Vieira | UFMG (Universidade Federal de Minas Gerais)

### BPF 指令格式详解

eBPF 是 64 位 RISC 风格指令集，固定 8 字节指令格式：

```
+----------------+--------+--------+----------------+----------------+
| opcode (8bit)  | dst_r  | src_r  | offset (16bit) |  imm (32bit)  |
+----------------+--------+--------+----------------+----------------+
```

**指令类别（7 类）：**
| 类别 | 助记符 | 功能 |
|------|--------|------|
| LD | BPF_LD | 加载操作 |
| LDX | BPF_LDX | 加载扩展（寄存器）|
| ST | BPF_ST | 存储操作（立即数）|
| STX | BPF_STX | 存储操作（寄存器）|
| ALU | BPF_ALU | 算术逻辑（32/64位）|
| ALU64 | BPF_ALU64 | 64位算术逻辑 |
| JMP | BPF_JMP | 跳转/条件跳转 |

**寄存器约定（11 个 64-bit 寄存器）：**
- `R0` — 函数返回值/syscall 返回值
- `R1-R5` — 函数参数（最多 5 个）
- `R6-R9` — callee-saved 寄存器
- `R10` — 栈指针（只读）

### XDP 架构

**XDP (eXpress Data Path)** — 在网卡驱动层处理数据包，无需经过内核网络栈。

```
数据包到达网卡
    ↓
XDP 程序执行（驱动层，DMA 之后）
    ├── XDP_DROP     → 直接丢弃
    ├── XDP_PASS     → 交给内核网络栈
    ├── XDP_REDIRECT → 重定向到其他网卡/队列/bpf_map
    └── XDP_TX       → 原路发回
```

**XDP 附加模式：**
- **Generic XDP** — 内核网络栈处理后再执行（兼容性好，性能差）
- **Native XDP** — 网卡驱动层直接执行（性能最优，需驱动支持）
- **Offload XDP** — SmartNIC 硬件执行（最高性能）

### 性能对比

| 技术 | 吞吐量 | 位置 | 灵活性 |
|------|--------|------|--------|
| **XDP** | ~20 Mpps | 驱动层 | 高 |
| **TC (eBPF)** | ~5 Mpps | netdev 层 | 高 |
| **Netfilter/iptables** | ~1 Mpps | 网络栈 | 高 |
| **Kernel bypass (DPDK)** | ~100 Mpps+ | 用户态轮询 | 低 |

**云厂商案例：**
- Cloudflare 用 XDP 处理 3 Mpps+ DDoS 流量（iptables 仅 1 Mpps）
- Facebook 用 XDP 实现 Katran L4 负载均衡
- Cilium 用 XDP 实现 Kubernetes 网络策略

### 完整 XDP 示例

```c
// XDP drop-all 程序
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

SEC("xdp")
int xdp_drop_all(struct xdp_md *ctx) {
    return XDP_DROP;  // 丢弃所有包
}
```

编译部署流程：
```bash
clang -O2 -target bpf -c prog.bpf.c -o prog.o
ip link set dev eth0 xdp obj prog.o sec xdp
```

## 关键引用

> "XDP allows packets to be reflected, filtered or redirected without traversing the networking stack."

> "The BPF verifier guarantees that every loaded program terminates and is safe to run."

## 相关页面

- [[entities/linux/ebpf/ebpf-xdp]] — XDP 高速数据面
- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[kernel-net-index]] — Linux 网络子系统
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
