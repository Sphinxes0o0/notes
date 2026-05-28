---
type: source
source-type: web
title: "Linux Advanced Routing & Traffic Control HOWTO"
author: "lartc.org"
date: 2024-01-01
size: medium
path: https://lartc.org/howto/index.html
summary: "Linux高级路由与流量控制：iproute2/RPDB/qdisc(TBF/HTB/RED/netem)/classifier(u32/fw)/Netfilter集成/QoS实现"
nids-relevance: 5
---

# Linux Advanced Routing & Traffic Control HOWTO

## 核心内容

### iproute2套件
`ip`命令操作：links, addresses, routes, ARP, tunnel, maddr

### 路由策略数据库 (Routing Policy Database)
- 源地址策略路由 (source policy routing)
- 多uplink场景负载均衡
- 支持OSPF/BGP动态路由 (via Zebra)

### Traffic Control (tc)

#### Queueing Disciplines (qdisc)

| qdisc | 类型 | 用途 |
|-------|------|------|
| `pfifo_fast` | Classless | 默认FIFO队列 |
| `tbf` | Classless | Token Bucket限速 |
| `sfq` | Classless | 公平队列 |
| `red` | Classless | Random Early Detection |
| `netem` | Classless | 网络仿真(延迟/丢包/重排) |
| `cbq` | Classful | Class-Based Queue |
| `htb` | Classful | Hierarchical Token Bucket |
| `prio` | Classful | Priority Queue |

#### Filters & Classifiers
- **u32**: 基于协议/IP/端口分类
- **fw**: 基于firewall mark分类
- **route**: 基于路由分类
- **hash**: 哈希分类

#### 高级qdisc
- **DSmark**: Differentiated Services标记
- **Ingress policing**: 入向流量限速
- **ATM emulation**: ATM仿真

### 安全与监控相关
- **Netfilter集成**: `fwmark`用于packet标记和追踪
- **Reverse Path Filtering**: 反欺骗
- **IPSEC隧道**: manual/自动keying, X.509
- **GRE隧道**: 封装流量

### 实用场景
- 多接口负载均衡
- 限速 (rate limiting/shaping)
- SYN flood防护
- 透明web缓存架构
- 桥接和proxy ARP配置

## NIDS架构关联

### 1. Packet Filtering
u32/fw filter直接在kernel层过滤，可用于快速丢弃已知恶意流量（IP黑名单、端口白名单）

### 2. Traffic Classification
隔离suspicious flows独立监控，分析异常流量模式

### 3. QoS for IDS
为检测流量保障带宽，避免被大流量淹没

### 4. netem仿真测试
用`netem`模拟丢包、延迟、重排测试NIDS检测准确性：
```bash
# 模拟5%丢包
tc qdisc add dev eth0 root netem loss 5%

# 模拟100ms±10ms延迟
tc qdisc add dev eth0 root netem delay 100ms 10ms
```

### 5. 连接追踪
与Netfilter/conntrack集成，追踪TCP会话状态用于入侵检测

## 相关页面

- [[wiki/sources/reading-linux-tc-traffic-control]] — NoPanic TC详解
- [[wiki/sources/notes-netfilter]] — Netfilter/iptables/nftables
- [[wiki/sources/arthurchiao-tc-da-mode]] — TC eBPF direct-action mode
- [[wiki/synthesis/topic-nids-architecture]] — NIDS架构综合
