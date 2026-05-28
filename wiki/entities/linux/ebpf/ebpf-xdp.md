---
type: entity
tags: [linux, ebpf, xdp, networking, ddos, packet-processing]
created: 2026-05-22
sources: [pdf-ebpf-books, pdf-ebpf-papers]
---

# eBPF XDP

## 定义

XDP (eXpress Data Path) 是 Linux 网络接收路径上最早的 eBPF hook 点，在 NIC 驱动刚收到数据包时即触发执行，无需经过内核网络协议栈，是 Linux 最高性能的网络数据面处理框架。理论处理量可达 20Mpps（百万包/秒），远高于 Netfilter (~1Mpps) 和 TC (~5Mpps)。

## 工作原理

```
Packet arrives at NIC
       ↓
Driver RX ring (DMA to memory)
       ↓
XDP hook ← eBPF program executes HERE (earliest possible point)
       ↓
  XDP action returned: DROP / PASS / TX / REDIRECT / ABORTED
       ↓
(If PASS) → Linux network stack (skb allocation, GRO, TCP/IP processing)
```

## XDP vs 网络处理层级性能对比

| 层级 | 理论处理量 |
|------|-----------|
| XDP (eBPF) | ~20 Mpps |
| TC (eBPF) | ~5 Mpps |
| Netfilter (iptables) | ~1 Mpps |

## XDP 程序类型上下文

XDP 使用 `struct xdp_md` 作为 BPF context：
- `data` — 数据包起始指针
- `data_end` — 数据包结束指针
- `data_meta` — 元数据指针（可用于 XDP→TC 传递）
- `data_hard_start` — 可用 headroom 起始（用于封装）
- `rxq` — 接收队列信息

## XDP Actions

| Action | 值 | 含义 | 典型场景 |
|--------|-----|------|----------|
| `XDP_DROP` | 1 | 丢弃数据包 | DDoS 防御、防火墙 |
| `XDP_PASS` | 2 | 送入内核协议栈 | 正常处理 |
| `XDP_TX` | 3 | 从同一网卡发回 | Hairpinned LB |
| `XDP_REDIRECT` | 4 | 重定向到其他 NIC/CPU | 负载均衡、转发 |
| `XDP_ABORTED` | 0 | 处理错误 | 调试追踪 |

## XDP 操作模式

| 模式 | 说明 | 性能 | 生产可用 |
|------|------|------|----------|
| **xdpdrv** (native) | 运行在驱动接收路径最早期 | 最高 | 是（4.8+，主流 10G+ 驱动） |
| **xdpoffload** | offload 到 SmartNIC（Netronome nfp 等） | 最高 | 需硬件支持 |
| **xdpgeneric** | generic XDP，skb 已生成后的 hook | 最低 | 否（仅作测试） |

## XDP 辅助函数

```c
// Map 操作
bpf_map_lookup_elem() / bpf_map_update_elem() / bpf_map_delete_elem()
bpf_redirect_map()       // 重定向到 map 中指定目标

// 数据包操作
bpf_xdp_adjust_head()    // 调整数据包头（添加/移除封装头）
bpf_xdp_adjust_meta()    // 调整元数据区
bpf_skb_store_bytes()    // 写入数据到数据包

// 其他
bpf_ktime_get_ns()       // 获取纳秒时间戳
bpf_trace_printk()        // 调试打印（生产环境不推荐）
bpf_tail_call()           // 尾调用链
```

## 典型应用场景

### DDoS 缓解
Cloudflare 最早使用 XDP，在配置良好的服务器上 iptables 仅处理 1Mpps，XDP 可处理 3Mpps+ DDoS 流量。思路：**部分内核旁路（partial kernel bypass）** — 部分 NIC 队列附到内核，部分队列附到用户态程序决定丢弃。

### 负载均衡
- **Facebook Katran**：L4 负载均衡器，XDP 实现高性能数据包处理
- **XDP_TX**：hairpinned LB，从同一网卡发回修改后的包
- **XDP_REDIRECT + CPUMAP**：将包重定向到其他 CPU 队列处理

### 高速包过滤防火墙
在网络数据到达最早点判断丢弃，无需经过整个协议栈。

### 流量镜像采样
通过 `bpf_xdp_event_output()` 将截断/完整包内容推送到 perf ring buffer，用户态低开销采集。

## XDP Offload 到 SmartNIC

多阶段处理策略：
- 部分程序 offload 到网卡（Netronome NFP），部分留在主机
- 通过 XDP/SKB metadata 在 offload 程序和主机程序间通信
- XDP 和 TC offload **不能同时开启**

## 局限性

- **仅支持 RX hook**（接收路径），TX 方向需配合 TC
- 不支持 `veth` 虚拟设备（因为 TCP/IP 栈大量使用 skb 克隆，XDP 无法处理克隆 skb）
- 需线性化（linearize）整个数据包到单个 DMA 内存页
- 无循环（需 `#pragma unroll` 或 Tail Call 模拟）

## 相关概念

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构（Verifier/JIT/Maps/CO-RE）
- [[entities/linux/ebpf/ebpf-networking]] — TC 流量控制与 Cilium
- [[kernel-net-index]] — Linux 网络子系统（sk_buff/Netfilter/Conntrack）
- [[kernel-protocols-index]] — 网络协议（TCP/IP/路由）

## 来源详情

- [[sources/pdf-ebpf-books]] — 《eBPF基础》第2.1.3节 XDP 技术实践
- [[sources/pdf-ebpf-papers]] — Fast-Packet-Processing using eBPF and XDP (UFMG, EVComp 2020)
- [[sources/reading-ebpf-how-ebpf-work]] — eBPF深入理解：BPF_PROG_TYPE_XDP/~10-20Mpps/XDP vs TC hook点性能对比
- [[sources/reading-af-xdp-technical]] — AF_XDP零拷贝：bpf_redirect_map/XSKMAP/UMEM ring/对比DPDK
