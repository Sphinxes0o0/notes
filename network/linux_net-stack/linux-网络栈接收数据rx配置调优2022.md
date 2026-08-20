---
title: "Linux 网络栈接收数据（RX）：配置调优（2022）"
description: "**注意**: 修改会 down/up 网卡, 短暂丢包."
---
# Linux 网络栈接收数据（RX）：配置调优（2022）

> 来源: [arthurchiao.art](https://arthurchiao.art/blog/linux-net-stack-tuning-rx-zh/)
> 原文: 28KB / 637 行, 落本地 `/tmp/achieved/raw/linux-net-stack/`

## 概述

- **作者**: Arthur Chiao
- **范围**: Linux 5.10 网络栈 RX 各层调优, 10 章节
- **基线**: Mellanox mlx5_core 25Gbps 驱动
- **风格**: 监控先行 → 定位瓶颈层 → 改参数 → 对比基线

## ⚠️ 调优铁律

1. **必须先有监控** (Prometheus + Grafana) 确认基线
2. 远程机器调网络 = 失联高风险
3. **永远不在生产直接调**, 先线下/灰度验证
4. 大部分 `ethtool` 修改配置会 **down/up 网卡** → 丢包, 谨慎

## 1. 网卡驱动层调优

### 1.1 RX 队列数量 (`ethtool -l/-L`)

```bash
# 查询
$ sudo ethtool -l eth0
Channel parameters for eth0:
Pre-set maximums:    RX: 0  TX: 0  Combined: 40
Current hardware:    RX: 0  TX: 0  Combined: 40

# 修改 (combined 模式 RX+TX 一起改, mlx5 支持)
$ sudo ethtool -L eth0 combined 8
# 部分网卡支持独立 RX/TX
$ sudo ethtool -L eth0 rx 8
```

**注意**: 修改会 down/up 网卡, 短暂丢包.

### 1.2 RX 队列大小 (`ethtool -g/-G`)

每个 descriptor 对应一个包, **大 → 抗突发, 小 → 低延迟**.

```bash
$ sudo ethtool -g eth0
Pre-set maximums:    RX: 4096
Current hardware:    RX: 512        # 当前只用 512

# 调大到最大
$ sudo ethtool -G eth0 rx 4096
```

### 1.4 RX 队列权重 (`ethtool -x/-X`)

```bash
# 前两个 queue 均匀分发
$ sudo ethtool -X eth0 equal 2
# 自定义权重 6:2
$ sudo ethtool -X eth0 weight 6 2
```

### 1.5 RSS 哈希字段 (`ethtool -n/-N`)

```bash
# 查询 UDPv4 哈希使用字段
$ sudo ethtool -n eth0 rx-flow-hash udp4
UDP over IPV4 flows use these fields:
  IP SA  IP DA                  # 只用源/目的 IP

# 加上端口 (sdfn = source-dest-IP-and-port)
$ sudo ethtool -N eth0 rx-flow-hash udp4 sdfn
```

**字段**: `s`=源 IP, `d`=目的 IP, `f`=源端口, `n`=目的端口

### 1.6 ntuple 过滤 (`ethtool -u/-U`)

细粒度 flow → 队列/CPU 绑定 (类似 OVS 流表).

## 2-3. 网卡收包 + DMA ring buffer

详见 [RX 原理篇 §2/§3](./linux-网络栈接收数据rx原理及内核实现2022.md).

## 4-5. IRQ + softirq 调优

### 4.1 IRQ 亲和性

```bash
# 查 IRQ 分布
$ cat /proc/interrupts | grep eth0
   114:  0  0  1234567  0  0  0  0  0  ...   IR-PCI-MSI  eth0
# ↑ 数字 1234567 是 CPU 3 收到的中断数

# 把 IRQ 114 绑到 CPU 4-7
$ echo 0xf0 > /proc/irq/114/smp_affinity      # 0xf0 = bit 4-7

# 多个网卡 IRQ 各自分开 CPU
$ cat /proc/irq/default_smp_affinity           # 默认所有 CPU
```

### 5.1 RPS (Receive Packet Steering) — 软件多队列

单队列网卡模拟多队列: 内核软中断分布到多 CPU.

```bash
# 计算 mask
$ echo $((1 << 4))      # 0x10 = CPU 4

# 启用 RPS
$ echo 0f > /sys/class/net/eth0/queues/rx-0/rps_cpus
$ echo 4096 > /sys/class/net/eth0/queues/rx-0/rps_flow_cnt
```

### 5.2 RFS (Receive Flow Steering)

RPS 改进版: 软中断发到**应用所在 CPU**, 减少 cache miss.

```bash
$ echo 4096 > /proc/sys/net/core/rps_sock_flow_entries
$ echo 4096 > /sys/class/net/eth0/queues/rx-0/rps_flow_cnt
```

### 5.3 监控

```bash
$ cat /proc/softirqs
   CPU0  CPU1  CPU2  CPU3
NET_RX  1234  2345  3456  4567
SCHED   ...
```

## 6-9. 协议栈调优

### L2 层

| 参数 | 说明 |
|---|---|
| MTU | 巨型帧 (jumbo frame) 9000, 减少包数 |
| ring buffer | 同 1.2, 大 → 抗突发 |

### L3 (IPv4)

```bash
$ sysctl -w net.ipv4.ip_forward=1
$ sysctl -w net.ipv4.ip_no_pmtu_disc=0     # 默认 0 = 启用 PMTU 发现
$ sysctl -w net.ipv4.tcp_mtu_probing=0     # 0=不探测, 1=总是
```

**PMTU 黑洞**: 路径中某设备禁止 ICMP, PMTU 发现失败 → 大包丢. 临时方案 `ip_no_pmtu_disc=1` + 调小 MTU.

### L4 (UDP/TCP)

```bash
# socket 缓冲
$ sysctl -w net.core.rmem_default=212992
$ sysctl -w net.core.rmem_max=212992
$ sysctl -w net.core.wmem_default=212992
$ sysctl -w net.core.wmem_max=212992

# TCP 自动调整窗口
$ sysctl -w net.ipv4.tcp_rmem="4096 87380 6291456"
$ sysctl -w net.ipv4.tcp_wmem="4096 65536 6291456"

# 单 socket
$ setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &buf, sizeof(buf));
```

### backlog

```bash
$ sysctl -w net.core.netdev_max_backlog=2000
$ sysctl -w net.core.somaxconn=128
```

## 10. 全局调优 (非网络, 但影响网络)

### 10.1 CPU governor

```bash
$ cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
powersave        # ← 错!
performance      # ← 对
# 改:
$ echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

**C-state**: CPU 闲置时进入低功耗, 唤醒有延迟. 网络敏感场景禁用.

```bash
$ cpupower idle-set -d 1   # 禁用 C1 以下
# 或 GRUB: intel_idle.max_cstate=0
```

### 10.2 CPU 隔离 (`isolcpus`)

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="isolcpus=4,5,6,7"   # CPU 4-7 隔离, 只跑收包
```

### 10.3 NUMA 亲和

```bash
# 查网卡所在 node
$ cat /sys/class/net/eth0/device/numa_node
1

# 进程绑到 node 1
$ numactl --cpunodebind=1 --membind=1 ./myapp

# 软中断绑到 node 1 的 CPU
$ echo 0f0 > /proc/irq/114/smp_affinity
```

### 10.4 BIOS 设置

- C-state disable
- 关闭 turbo boost (延迟敏感)
- PCIe ACS disable (NUMA 直通优化)
- 关闭 SR-IOV 中断聚合

## 调优决策树

```
丢包了?
├─ 链路层 (driver drop) → 改 ring buffer / 多队列
├─ 协议栈 (UDP socket drop) → 改 socket buffer / backlog
└─ 应用层 (recv 没读完) → 改应用代码

延迟高?
├─ 软中断高 → RPS/RFS / 隔离 CPU
├─ C-state 干扰 → 禁 C-state
└─ NUMA 远端 → 绑 NUMA node
```

## 关键 takeaway

- **监控先行**: 无监控调优 = 盲猜
- **从下往上**: 网卡 → IRQ → softirq → 协议栈 → socket
- **生产禁忌**: 远程调 / 一次大改 / 不用监控验证
- **现代工具**: BPF/XDP (Cilium) 比 sysctl 强大, 性能瓶颈期考虑 eBPF

## 关联阅读

- [Linux 网络栈 RX 原理](./linux-网络栈接收数据rx原理及内核实现2022.md)
- [Linux 中断 (IRQ/softirq) 基础](https://arthurchiao.art/blog/linux-irq-softirq-zh/)
- [Linux 网络栈监控](https://arthurchiao.art/blog/monitoring-network-stack/)

---
*完整 28KB 原文含全部 ethtool 输出样例, 各层 sysctl 详解, 实操命令, BIOS 设置, 决策树 — 落本地供深读.*
