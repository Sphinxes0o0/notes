---
type: entity
tags: [XDP, eBPF, DPDK, 高性能网络, Linux]
created: 2026-05-28
sources: [bookmark-sdn-guide]
---

# XDP (eXpress Data Path)

## 定义

通过在数据包进入网络协议栈之前处理，提供**高性能可编程数据路径**。

## 关键要点

### 核心特性
- 在网络协议栈**之前**处理数据包
- **无锁设计**
- **批量I/O操作**
- 基于**轮询**的操作(Poll Mode Driver)
- **直接队列访问**
- 无需分配sk_buff
- 支持网络卸载
- **DDIO** (Direct Data I/O)
- 无循环的快速XDP程序执行
- 数据包转向(TX/Redirect/Drop)

### 性能数据
- ~20Mpps (百万包每秒)，DPDK级别
- TC约5Mpps
- Netfilter约1Mpps

### vs DPDK

| 方面 | XDP | DPDK |
|------|-----|------|
| 代码库 | Linux内核 | 独立用户态库 |
| 许可证 | GPL | BSD |
| CPU模式 | 轮询或中断驱动 | 轮询(100% CPU) |
| 大页 | 不必需 | 需要 |
| 专用CPU | 不需要 | 通常需要 |
| 安全模型 | 内核安全边界 | 独立网络栈 |

### 限制
- 无qdisc缓存队列，TX设备慢时直接丢包
- XDP程序专用，缺乏通用网络协议栈能力
- 需要内核版本4.8+

## 架构位置

```
NIC驱动
  ↓
XDP程序 (eBPF, 运行在网卡驱动层)
  ↓ (根据action: XDP_PASS/DROP/REDIRECT/TX)
协议栈或TX或Drop
```

## 相关概念
- [[linux-ebpf-overview]] — eBPF基础
- [[linux-ebpf-sdn-guide]] — eBPF（XDP的底层技术）
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action（XDP配合TC）
- [[kernel-bypass-dpdk]] — DPDK（另一种高性能方案）
- [[linux-net-stack-overview]] — Linux网络协议栈

## 来源详情
- [[bookmark-sdn-guide]] — SDN网络指南
