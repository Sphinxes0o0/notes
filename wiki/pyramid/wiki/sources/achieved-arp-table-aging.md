---
type: source
source-type: bookmark
title: "Linux中arp表的老化机制"
author: "lsgxeva"
date: 2020-09-23
url: "https://www.cnblogs.com/lsgxeva/p/13749751.html"
summary: "深入分析Linux内核ARP表的三状态机制（delay/reachable/stale），以及老化时间计算公式和gc_thresh1参数的作用"
tags: [linux, networking, arp, kernel]
created: 2026-05-28
---

# Linux中arp表的老化机制

## 核心内容

### ARP表三状态机制

Linux内核维护ARP缓存表，条目有三个关键计时器状态：

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| **delay** | 等待测试可达性 | 刚收到邻居包 |
| **reachable** | 确认可达 | 收到邻居确认 |
| **stale** | 超时但未删除 | reachable超时 |

**为什么需要stale状态？** 减少网络中ARP交互开销，尽量减少ARP请求。

### 老化时间计算公式

```
Timeout = random(base_reachable_time/2, 3*base_reachable_time/2) + gc_stale_time
```

条目被置为invalid状态后，等待gc时间回收删除。

### gc_thresh1 参数

```bash
# 存在于ARP高速缓存中的最少个数
# 如果少于这个数，垃圾收集器将不会运行
# 默认值：128
```

### 重要发现

- `arping` 命令可以把 STALE 的缓存刷新为 REACHABLE
- `ping` 命令**不能**把 STALE 的缓存刷新为 REACHABLE
- 根因是 gc 时间机制，解决方案：配置 `gc_thresh1=0` 或 `ip neigh flush`

### 关键命令

| 命令 | 用途 |
|------|------|
| `ip -s neigh` | 查看完整arp条目变化流程 |
| `ip neigh show` | 查看缓存状态(REACHABLE/STALE) |
| `arp -a` | 查看arp缓存（无法显示状态） |

## 关键引用

> "arping命令无法添加新的arp缓存，但可以把STALE的缓存刷新为REACHABLE状态"

> "Linux设计ARP缓存机制的主要目的有两个：一是减少ARP交互，二是减少条目的增加和删除操作造成的开销"

## 相关页面

- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径分析（邻居子系统）
- [[entities/linux/network/linux-network-protocols]] — TCP/UDP协议实现
