---
type: source
source-type: pdf
title: "BPF: Turning Linux into a Microservices-aware OS (Thomas Graf)"
author: "Thomas Graf"
date: 2018
size: medium
path: raw/PDFs/papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf
summary: "Thomas Graf扩展版演讲：Linux微服务感知操作系统，Cilium Hubble可观测性，Cilium功能矩阵(网络/LB/安全/Mesh加速)"
tags: [ebpf, cilium, hubble, kubernetes, microservices, networking, service-mesh]
---

# BPF: Turning Linux into a Microservices-aware OS

## 核心内容

**Author:** Thomas Graf (Cilium 创始人) | 2018

### 背景与动机

继 Rethinking the Linux Kernel 之后，Thomas Graf 在此演讲中进一步扩展 eBPF 愿景，深度解析 Cilium 如何让 Linux 真正感知微服务。

**核心问题：** 在微服务架构中，Linux 内核只知道 IP 地址、端口、进程，但：
- Pod IP 是临时的（重建后变化）
- 多个服务共享同一主机
- 传统 iptables 规则无法区分具体服务身份

### Hubble: Kubernetes 网络可观测性

**Hubble** — 基于 eBPF 的 Kubernetes 网络可视化工具。

```bash
# 观测最近1分钟的L7 DNS事件，输出JSON格式
hubble observe --since 1m -t l7 -j \
  | jq 'select(.l7.dns.rcode==3) | .destination.namespace + "/" + .destination.pod_name'
```

**功能：**
- **L7 可视化** — HTTP/gRPC/Kafka/DNS 请求级别可见性
- **L3-L4 流量** — 连接追踪、带宽监控
- **安全事件** — 策略违规告警
- **服务依赖图** — 服务间调用关系自动拓扑

### Cilium 功能矩阵

#### 容器网络

| 功能 | 说明 |
|------|------|
| CNI 插件 | Kubernetes 网络插件 |
| 路由模式 | 支持多种网络模式（路由/Overlay/IPv6）|
| 多集群 | 跨集群网络连通性 |
| NAT46/64 | IPv4/IPv6 互通 |

#### Service 负载均衡

- L3-L4 负载均衡（替代 kube-proxy iptables）
- 扩展至 kube-proxy 之外的功能
- 性能：eBPF 查找 O(1) vs iptables O(n)

#### 安全（Identity-based）

- **L3-L4 安全策略** — 基于 Kubernetes Pod 身份
- **L7 API 感知** — HTTP/gRPC/Kafka 协议层策略
- 不依赖 IP（IP 会变）

#### Service Mesh 加速

**Envoy sidecar vs BPF：**
- Envoy：每请求经过用户态代理（两次上下文切换）
- Cilium BPF：内核直传（无 sidecar）
- 性能提升：~3.5x 吞吐量

```
传统 sidecar: Pod A → Envoy A → Network → Envoy B → Pod B
Cilium BPF:    Pod A → [BPF] → Network → [BPF] → Pod B
```

### eBPF 在 Cilium 中的核心应用

| 组件 | eBPF 技术 |
|------|---------|
| 网络策略 | TC (traffic control) eBPF |
| 负载均衡 | L4LB (XDP/TC) |
| 加密通信 | WireGuard (加密隧道) |
| 可观测性 | sockops / sk_msg hooks |
| 网络隔离 | namespace-aware hooks |

## 关键引用

> "Linux was not designed for microservices. eBPF makes it possible to extend the kernel to understand service identity."

> "Hubble provides per-pod, per-service network visibility directly from the kernel."

## 相关页面

- [[entities/linux/ebpf/ebpf-networking]] — eBPF 网络与 Cilium
- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-security-observability]] — eBPF 安全可观测性
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
