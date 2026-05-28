---
type: entity
tags: [linux, networking, tcp, sack, dsack, congestion-control, scoreboard]
created: 2026-05-28
sources: [achieved-tcp-sack-dsack]
---

# TCP SACK and DSACK

## 定义

SACK (Selective Acknowledgment) 允许接收方显式确认**乱序**接收的段，解决重复ACK导致的伪重传问题。DSACK (Duplicate SACK) 报告重复数据接收，用于检测伪重传和重排。

## 核心数据结构

### SACK Block
```c
struct tcp_sack_block {
    u32 start_seq;  // 开始序列号
    u32 end_seq;    // 结束序列号
};
```

### Scoreboard 标签

在 `tcp_sock` 中，段使用以下标签跟踪状态：

| 标签 | 含义 | InFlight | 说明 |
|------|------|----------|------|
| **S** | TCPCB_SACKED_ACKED | 0 | 已通过SACK确认 |
| **R** | TCPCB_SACKED_RETRANS | 2 | 已重传 |
| **L** | TCPCB_LOST | 0 | 标记为丢失 |

### 段状态矩阵

| 标签 | InFlight | 描述 |
|------|----------|------|
| 0 | 1 | 正常在飞 |
| S | 0 | 原始包已到达接收方 |
| L | 0 | 原始包网络中丢失 |
| R | 2 | 原始包和重传包都在飞 |
| L\|R | 1 | 原始包丢失，重传包在飞 |
| S\|R | 1 | 原始包到达，重传包还在飞 |

## 处理流程

`tcp_ack()` 在慢路径处理非空 scoreboard 时，调用 `tcp_sacktag_write_queue()` 更新包状态：

```
tcp_ack() (慢路径, 非空 scoreboard)
    ↓
tcp_sacktag_write_queue()
    ├── 快速路径：仅第一个SACK块end_seq变化
    └── 慢速路径：每个SACK块从头遍历
```

## v18 vs v37 性能优化

### v18 实现
- 每个 SACK 块从头遍历队列
- **复杂度：O(num_sacks × cwnd)**

### v37 实现
- `recv_sack_cache`：缓存上次SACK块，避免重复处理
- `highest_sack` 指针：跟踪最高SACK位置
- **复杂度：O(cwnd)**

### 缓存利用策略
- 若缓存块完全在SACK块之前 → 跳过缓存
- 若无重叠 → 独立处理
- 若有重叠 → 只处理非重叠部分

## DSACK 检测

根据 RFC 2888，DSACK 发生在：
1. 第一个 SACK 块的 start_seq < 累计 ACK → 重复数据
2. 第一个 SACK 块包含在第二个块内 → 第一个块是重复

## 丢失重传检测

重传时将 `snd_nxt` 保存在包的 `ack_seq` 字段。若新数据被SACK但重传的 `snd_nxt` 没有被确认 → 重传已丢失。

## SACK Option 解析

解析时将 SACK option 偏移保存在 `TCP_SKB_CB(skb)->sacked`：
```c
TCP_SKB_CB(skb)->sacked = (ptr - 2) - (unsigned char *) th;
```

## SACK 块验证

1. 普通 SACK/DSACK：`snd_una < start_seq < end_seq <= snd_nxt`
2. DSACK：`undo_marker <= start_seq < end_seq <= snd_una`
3. DSACK 边界跨越：需满足窗口大小约束

## 关键函数

| 函数 | 功能 |
|------|------|
| `tcp_sacktag_one()` | 标记单个包的 scoreboard |
| `tcp_sacktag_skip()` | 找到给定序列号的 skb |
| `tcp_sacktag_walk()` | 在 SACK 块内遍历 skb |
| `tcp_mark_lost_retrans()` | 检测 Recovery 状态的丢失重传 |

## 相关概念

- [[entities/linux/network/congestion-control]] — 拥塞控制（BBR等）与 SACK 的交互
- [[entities/linux/network/linux-network-protocols]] — TCP 协议实现细节
- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径（tcp_ack 处理位置）
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络子系统框架
- [[entities/linux/kernel/net/skbuff-deep-dive]] — SKB 数据结构与 scoreboard

## 来源详情

- [[sources/achieved-tcp-sack-dsack]] — abcdxyzk blog: Linux内核TCP SACK/DSACK实现深度解析
