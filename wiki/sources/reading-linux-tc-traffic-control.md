---
type: source
source-type: web
title: "Linux TC流量控制"
author: "NoPanic"
date: 2024-01-01
size: small
path: https://www.ilikejobs.com/posts/what-is-tc/
summary: "Linux TC流量控制：qdisc(pfifo_fast/netem/tbf/htb/fq_codel)/classifier(u32/fw)/NIDS测试仿真"
nids-relevance: 4
---

# Linux TC流量控制 (NoPanic)

## 核心内容

### Queuing Disciplines (qdisc)

| qdisc | 用途 |
|-------|------|
| `pfifo_fast` | 默认FIFO队列 |
| `netem` | 网络仿真（延迟、丢包、重排、损坏、复制） |
| `tbf` | Token Bucket Filter（带宽限速） |
| `htb` | Hierarchical Token Bucket（复杂带宽分配） |
| `cbq` | Class-Based Queue |
| `prio` | Priority Queue |
| `fq_codel` | Fair Queueing CoDel（减少bufferbloat） |
| `cake` | 高级队列管理 |

### Filters & Classifiers
- **u32**: 基于协议/IP/端口分类
- **fw**: 基于firewall mark分类

### 流量控制操作

```bash
# 带宽限速
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms

# 延迟仿真
tc qdisc add dev eth0 root netem delay 100ms 10ms

# 丢包
tc qdisc add dev eth0 root netem loss 1%

# 重排
tc qdisc add dev eth0 root netem delay 10ms reorder 25%
```

### NIDS Testing仿真

| 场景 | 命令 | NIDS测试目的 |
|------|------|-------------|
| 丢包 | `netem loss 1%` | 检测NIDS在高丢包率下表现 |
| 延迟 | `netem delay 100ms` | 测试NIDS端到端延迟容忍度 |
| 重排 | `netem reorder 25%` | 验证TCP重组鲁棒性 |
| 限速 | `tbf rate 10mbit` | 测试NIDS在高负载下是否丢包 |

## NIDS架构关联

1. **网络损伤仿真**: 用`netem`模拟真实网络条件测试NIDS检测准确性
2. **限速压测**: `tbf`限速压测NIDS在高负载下的检测能力
3. **流量分类**: u32/fw隔离suspicious flows独立分析
4. **协议重构验证**: 延迟/重排测试NIDS的TCP协议重组能力

## 相关页面

- [[reading-linux-advanced-routing-tc]] — lartc.org更全面的HOWTO
- [[arthurchiao-tc-da-mode]] — TC eBPF direct-action mode
- [[wiki/synthesis/topic-nids-architecture]] — NIDS架构综合
