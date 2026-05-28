---
type: source
source-type: bookmark
title: "TCP SACK/DSACK实现 — abcdxyzk"
author: "abcdxyzk"
date: 2015-03-19
url: "https://abcdxyzk.github.io/blog/2015/03/19/kernel-net-sack-dsack/"
summary: "Linux内核TCP SACK和DSACK实现深度解析，对比v18和v37版本性能差异，详细分析scoreboard标签和丢包检测算法"
tags: [linux, networking, tcp, sack, dsack, kernel, congestion-control]
created: 2026-05-28
---

# TCP SACK/DSACK实现 — abcdxyzk

## 核心内容

### SACK概述

SACK（Selective Acknowledgment）允许接收方显式确认**乱序**段。DSACK报告重复数据接收。

### 数据结构

```c
struct tcp_sack_block {
    u32 start_seq;  // 开始序列号
    u32 end_seq;    // 结束序列号
};
```

### Scoreboard标签（tcp_sock中）

| 标签 | 含义 | InFlight |
|------|------|----------|
| **S** (TCPCB_SACKED_ACKED) | 通过SACK确认 | 0 |
| **R** (TCPCB_SACKED_RETRANS) | 已重传 | 2 |
| **L** (TCPCB_LOST) | 标记为丢失 | 0 |

### 包状态矩阵

| 标签 | InFlight | 描述 |
|------|----------|------|
| 0 | 1 | 正常在飞 |
| S | 0 | 原始包已到达接收方 |
| L | 0 | 原始包网络中丢失 |
| R | 2 | 原始包和重传包都在飞 |
| L\|R | 1 | 原始包丢失，重传包在飞 |
| S\|R | 1 | 原始包到达，重传包还在飞 |

### 关键函数

| 函数 | 功能 |
|------|------|
| `tcp_sacktag_one()` | 标记单个包的scoreboard |
| `tcp_sacktag_skip()` | 找到给定序列号的skb |
| `tcp_sacktag_walk()` | 在SACK块内遍历skb |
| `tcp_mark_lost_retrans()` | 检测Recovery状态的丢失重传 |

### v18 vs v37 性能对比

| 版本 | 复杂度 | 优化技术 |
|------|--------|----------|
| **v18** | O(num_sacks × cwnd) | 无缓存，每个SACK块从头遍历 |
| **v37** | O(cwnd) | recv_sack_cache + highest_sack指针 |

### DSACK检测

1. 第一个SACK块的 start_seq < 累计ACK → 重复
2. 第一个SACK块包含在第二个块内 → 重复

### 丢失重传检测

重传时将 `snd_nxt` 保存在包的 `ack_seq` 字段。若新数据被SACK但重传的 `snd_nxt` 没有 → 重传已丢失。

## 关键引用

> "For num_sacks SACK blocks, if fast path fails, each block traverses from head. Complexity is O(num_sacks × cwnd)"

> "Version 37 dramatically improves performance by using cached SACK information to skip already-processed segments"

## 相关页面

- [[entities/linux/network/linux-network-protocols]] — TCP协议实现（包含拥塞控制）
- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络子系统
