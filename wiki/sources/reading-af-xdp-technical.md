---
type: source
source-type: web
title: "AF_XDP技术详解"
author: "RexRock"
date: 2023-01-01
size: small
path: https://rexrock.github.io/post/af_xdp1/
summary: "AF_XDP零拷贝架构：UMEM/chunk/ring模型，bpf_redirect_map，XDP程序hook，对比DPDK"
nids-relevance: 5
---

# AF_XDP技术详解

## 核心内容

### AF_XDP架构
- 利用`bpf_redirect_map()`将packet直接重定向到用户态内存
- 使用`BPF_MAP_TYPE_XSKMAP`关联queue ID和socket fd
- **零拷贝**: RX和TX共享同一UMEM，无需在用户态和内核间复制packet

### UMEM内存模型
UMEM将内存划分为固定大小的chunk，四个ring管理packet流：

| Ring | 方向 | 用途 |
|------|------|------|
| **FILL RING** | 用户→内核 | 缓冲供给 |
| **COMPLETION RING** | 内核→用户 | 发送完成确认 |
| **RX RING** | 入向 | 入向packet |
| **TX RING** | 出向 | 出向packet |

用户通过`mmap()`访问这些ring，通过`getsockopt()`获取kernel结构体偏移。

### XDP Program Hook

```c
if (bpf_map_lookup_elem(&xsks_map, &index))
    return bpf_redirect_map(&xsks_map, index, 0);
```

XDP程序检查queue是否有绑定的AF_XDP socket，有则重定向。

### 驱动支持
需要驱动级XDP支持`XDP_REDIRECT`功能。已用于：OVS、DPDK、Cilium。

### 对比DPDK

| 特性 | AF_XDP | DPDK |
|------|--------|------|
| 内存 | 不需要专用大页 | 需要大页 |
| API复杂度 | 简单 | 复杂 |
| 内核集成 | 可与内核栈协作 | 完全旁路内核 |
| 适用场景 | NIDS、防火墙 | 超高性能NFV |

## 关键引用

> "RX和TX可以共享同一UMEM，因此不必在RX和TX之间复制数据包"

## NIDS架构关联

- **Inline NIDS**: 用户态直接访问packet，最小延迟，适合全流量检测
- **主动响应**: AF_XDP支持完整TX path，方便做主动响应（如reset恶意连接）
- **对比XDP-only**: 纯XDP难以做主动响应（只能丢包），AF_XDP弥补了这个缺陷

## 相关页面

- [[wiki/entities/kernel-bypass-dpdk]] — Kernel bypass对比
- [[wiki/entities/linux-ebpf-fundamentals]] — XDP/eBPF基础
- [[wiki/sources/reading-ebpf-how-ebpf-work]] — eBPF深入理解
- [[wiki/synthesis/topic-nids-architecture]] — NIDS架构综合
