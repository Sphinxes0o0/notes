---
type: entity
tags: [linux, ebpf, networking, cilium, tc, sock-ops, container]
created: 2026-05-22
sources: [pdf-ebpf-books, pdf-ebpf-papers]
---

# eBPF Networking

## 定义

eBPF 在 Linux 网络领域提供了从 NIC 驱动层（XDP）到 Socket 层的多层次可编程性，使 Linux 内核成为"微内核（microkernel）+ eBPF 可组合服务层"的现代化架构。Cilium 项目是 eBPF 网络领域的标杆实现，在 Kubernetes 环境中替代 iptables kube-proxy 实现 L3-L4 网络安全和负载均衡。

## 多层次 Hook

| 层次 | Hook 点 | 程序类型 | 性能 | 可见性 |
|------|---------|---------|------|--------|
| **XDP** | NIC 驱动 RX 最早期 | `BPF_PROG_TYPE_XDP` | ~20 Mpps | 原始数据包 |
| **TC Ingress** | `__netif_receive_skb_core()` → `sch_handle_ingress()` | `BPF_PROG_TYPE_SCHED_CLS` | ~5 Mpps | skb（解析后） |
| **TC Egress** | `__dev_queue_xmit()` → `sch_handle_egress()` | `BPF_PROG_TYPE_SCHED_CLS` | ~5 Mpps | skb |
| **Socket Filter** | Raw socket 数据复制路径 | `BPF_PROG_TYPE_SOCKET_FILTER` | — | socket 元数据 |
| **Sock_ops** | TCP socket 操作（3次握手~4次挥手） | `BPF_PROG_TYPE_SOCK_OPS` | — | socket 状态 |
| **LSM** | 安全关键路径 | `BPF_PROG_TYPE_LSM` | — | 安全上下文 |

## TC (Traffic Control) 深度解析

### 为什么需要 TC + eBPF

- XDP 仅支持 RX（接收），TC 覆盖 Ingress + Egress 双向
- TC skb 上下文比 xdp_buff 丰富（mark, pkt_type, protocol, priority, queue_mapping, napi_id, cb[], hash, VLAN 元数据）
- 支持虚拟设备（veth），XDP 不支持（因为 skb 克隆）

### TC + eBPF 核心概念

```
clsact qdisc (pseudo qdisc, no actual queueing)
  ├── ingress hook  ← sch_handle_ingress()
  └── egress hook   ← sch_handle_egress()
```

**关键优势：sch_clsact 无锁执行**（不在 root qdisc 锁下），支持抢占，可安全附加到虚拟设备。

**Direct-Action (da) 模式：** 推荐模式。BPF 程序直接返回 action verdict（`TC_ACT_OK`/`TC_ACT_SHOT`），无需调用外部 tc action 模块。da 模式下单个 cls_bpf filter 可替代整条 tc 规则链。

### TC BPF 程序上下文

`struct __sk_buff` 可访问的字段：len, mark, queue_mapping, protocol, priority, ingress_ifindex, ifindex, tc_index, data, data_end, napi_id, hash, remote_ip4, local_ip4, remote_port, local_port 等。

## Cilium 深度解析

### 为什么需要 Cilium

**Linux 内核不知道：**
- 容器或 Kubernetes Pod（内核只有 namespace/cgroup）
- 服务暴露需求（是否应暴露到集群外）
- API 调用关系（只感知到 L4 端口）

**Kernel "DARK AGE" 问题：**
- 微服务架构下内核无法感知服务身份和安全需求
- 替代方案（Unikernel/DPDK/gVisor）代价过高

### Cilium 核心功能

**容器网络：**
- CNI/CNM 插件
- IPv4/IPv6/NAT46/direct routing/encapsulation
- 多集群路由

**Service Load Balancing：**
- L3-L4 高度可扩展负载均衡（替代 kube-proxy）
- 基于 eBPF 的 conntrack 感知实现
- 多集群 service affinity（优先同 zone）

**安全（Identity-based）：**
- 基于容器/Pod 身份而非 IP 的 L3-L4 网络安全策略
- API-aware 安全（HTTP/gRPC/Kafka/Cassandra/memcached）
- DNS-aware 策略
- kTLS（Kernel TLS）SSL 数据可见性

**Servicemesh 加速：**
- Envoy sidecar 代理 vs BPF-based servicemesh 加速
- 约 3.5x 性能提升

### Hubble (Cilium 的可观测性层)

Hubble 使用 eBPF 追踪所有网络流量，提供：
- L7 DNS 请求可视化
- 实时网络流拓扑（service graph）
- 高级网络指标和告警
- 基于 BPF Map 的高效数据采集

## Sock_ops

BPF 程序拦截 socket 操作，动态设置 TCP 参数。15 个 hook 点覆盖 TCP 生命周期各阶段：
- 优化：更合适的 buffer size（基于 RTT）
- 降低 SYN RTO/SYN-ACK RTO 减少重传等待时间
- ECN 支持 → DCTCP 拥塞控制

## Socket Filter vs XDP vs TC 对比

| 维度 | Socket Filter | XDP | TC |
|------|---------------|-----|-----|
| Hook 位置 | Raw socket | NIC 驱动 | netif TX/RX |
| 数据可见性 | socket 元数据 | 原始包 | skb |
| 方向 | 入向过滤 | RX only | Ingress + Egress |
| 性能 | 中等 | 最高 | 高 |
| 适用设备 | 所有 socket | 支持 XDP 的 NIC | 所有设备 |

## 相关概念

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-xdp]] — XDP 高速数据路径
- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控（Falco/KRSI）
- [[kernel-net-index]] — Linux 网络子系统（Netfilter/Conntrack/sk_buff）
- [[kernel-protocols-index]] — 网络协议（TCP/路由）

## 来源详情

- [[sources/pdf-ebpf-books]] — 《eBPF基础》第3.4-3.7节网络性能优化与访问控制
- [[sources/pdf-ebpf-papers]] — Rethinking the Linux Kernel (Thomas Graf, Cilium)
- [[sources/pdf-ebpf-papers]] — BPF: Turning Linux into a Microservices-aware OS (Thomas Graf)
- [[sources/achieved-ebpf-android]] — Android eBPF Doze模式网络控制实现
- [[sources/reading-ebpf-how-ebpf-work]] — eBPF深入理解：TC SCHED_CLS/SCHED_ACT/Socket Filter/Sock_ops程序类型
- [[sources/reading-linux-advanced-routing-tc]] — Linux高级路由与TC：iproute2/qdisc(TBF/HTB/RED/netem)/classifier(u32/fw)/Netfilter集成
- [[sources/reading-linux-tc-traffic-control]] — Linux TC流量控制：qdisc(netem/tbf/fq_codel)/NIDS测试仿真
