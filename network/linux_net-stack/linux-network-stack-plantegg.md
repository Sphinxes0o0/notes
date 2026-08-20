---
title: "Linux Network Stack | plantegg"
description: "plantegg (Twitter @plantegg) 的 Linux 网络栈收包流程概览, **2019 年**, 偏实战."
---
# Linux Network Stack | plantegg

> 来源: [plantegg.github.io](https://plantegg.github.io/2019/05/24/%E7%BD%91%E7%BB%9C%E5%8C%85%E7%9A%84%E6%B5%81%E8%BD%AC/)
> 原文: 22KB / 478 行, 落本地

## 文章定位

plantegg (Twitter @plantegg) 的 Linux 网络栈收包流程概览, **2019 年**, 偏实战.

## 收包流程主线 (9 步)

```
网卡 (DMA → ring buffer)
  ↓ 硬中断 (IRQ)
ksoftirqd 线程 (软中断)
  ↓ NAPI poll()
协议栈: L2 (eth) → L3 (IP) → L4 (TCP/UDP) → socket
  ↓
应用 recv()
```

## 关键控制参数

| 阶段 | 关键参数 / 工具 |
|---|---|
| 网卡驱动 | `ethtool -k/-K` (特性开关), `-l/-L` (多队列) |
| Ring buffer | `ethtool -g/-G`, RX ring 溢出 → 丢包 |
| 中断 | `/proc/irq/<N>/smp_affinity`, IRQ 亲和性 |
| 软中断 | `/proc/softirqs`, RPS/RFS |
| 协议栈 | `netstat -s`, `ss -s`, `ip -s link` |
| socket | `net.core.rmem_default/max`, `tcp_rmem`, 应用 `SO_RCVBUF` |

## 实战调优经验 (plantegg 强调)

1. **观察工具优先**: `sar -n DEV 1`, `nicstat`, `ip -s -s link show dev eth0`, `dropwatch`
2. **瓶颈定位顺序**:
   - 链路层丢包? → ring buffer / 多队列
   - 协议栈丢包? → socket 缓冲 / backlog
   - 应用层慢? → 业务代码 / DB

## 与 arthurchiao 系列对比

- plantegg 这篇是 **速览** (一篇文章覆盖全流程)
- arthurchiao 是 **深度系列** (4-5 篇分别讲原理/IRQ/RX 原理/RX 调优)
- **推荐阅读顺序**: plantegg 总览 → arthurchiao 深入

## 关键 takeaway

> 1. 收包瓶颈 80% 在 ring buffer (硬中断) + softirq (协议栈入口)
> 2. 多队列 + RSS 是单核瓶颈的标准解
> 3. 监控驱动: `dropwatch` (内核丢包点) + `bcc/funccount` 统计路径

---
*原文含完整代码段 (ethtool/sar/ss 输出样例), 各阶段调优脚本 — 落本地供细看.*
