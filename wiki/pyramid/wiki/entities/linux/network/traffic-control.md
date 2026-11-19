---
type: entity
tags: [Linux, 网络, 流量控制, TC, QoS]
created: 2026-05-28
sources: [bookmark-sdn-guide]
---

# Traffic Control (流量控制)

## 定义

Linux内核提供的流量限速、整形和策略控制机制，以`qdisc-class-filter`的树形结构实现对流量的分层控制。

## 关键要点

- **qdisc** (队列规则): 通过队列缓存数据包，控制网络收发速度
  - 无分类: pfifo_fast、RED、SFQ、TBF
  - 有分类: CBQ、HTB、PRIO
- **class** (类): 用来表示控制策略
- **filter** (过滤器): 将数据包划分到具体的控制策略中
- **ingress qdisc**: 受限，通常借助ifb内核模块进行ingress方向流量控制

### HTB (Hierarchy Token Bucket)
- 分层令牌桶，精确控制带宽分配
- 支持优先级、带宽上限、突发流量控制
- 示例: 限制特定IP(如192.168.0.9)流量为3mbit

### ifb (Intermediate Functional Block)
- 虚拟设备，将ingress流量重定向到egress方向再进行整形
- 解决ingress方向无法直接应用qdisc的问题

## 架构关系

```
Root qdisc
├── class (HTB)
│   ├── filter → match dst 192.168.0.9 → rate 3mbit
│   └── filter → match dst 10.0.0.0/8 → rate 10mbit
└── class (PRIO)
    └── filter → match protocol ip → next qdisc
```

## 与eBPF的关系
- tc (Traffic Control) 可挂载eBPF程序作为filter
- eBPF程序在sk_buff层面进行深度包处理
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action模式

## 相关概念
- [[linux-ebpf-overview]] — eBPF基础
- [[linux-ebpf-xdp]] — XDP快速数据路径
- [[linux-net-stack-overview]] — Linux网络协议栈
- [[load-balancing]] — 负载均衡（与TC协同实现流量分发）

## 来源详情
- [[bookmark-sdn-guide]] — SDN网络指南
