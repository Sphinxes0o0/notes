---
title: "Linux 网络栈接收数据（RX）：原理及内核实现"
description: "主流驱动对照:"
---
# Linux 网络栈接收数据（RX）：原理及内核实现

> 来源: [arthurchiao.art](https://arthurchiao.art/blog/linux-net-stack-implementation-rx-zh/)
> 原文: 139KB / 3071 行, 落本地 `/tmp/achieved/raw/linux-net-stack/`

## 概述

- **作者**: Arthur Chiao
- **范围**: Linux 5.10 网络栈 RX (接收) 完整路径剖析
- **驱动实例**: **Mellanox ConnectX-4/5 (mlx5_core)**, 25/40Gbps 以太网卡
- **风格**: 原理 + 代码 + 流程图 (20+ 张), 实操导向

## 收包 10 步流程

```
1. 网卡驱动初始化 (probe)
2. 网卡收包
3. DMA 将包复制到 RX ring buffer
4. 触发硬件中断 (IRQ)
5. 内核调度到 ksoftirqd 线程
6. 软中断: NAPI poll() 从 ring buffer 取数据, skb 形式送协议栈
7. 协议栈 L2 处理
8. L3 处理 (IPv4)
9. L4 处理 (UDP: udp_v4_early_demux → ... → socket recv queue)
10. 唤醒等待进程
```

## 1. 网卡驱动初始化 (重点)

### 1.1 Mellanox 驱动背景

主流驱动对照:
- `igb` - Intel 1Gbps (老)
- `ixgbe` - Intel 10Gbps
- `i40e` - Intel 40Gbps
- `mlx5_core` - **Mellanox 25/40/100/200Gbps**, 历史源自 InfiniBand, 术语独特

mlx5 关键术语:
| 术语 | 含义 |
|---|---|
| WR | Work Request, HW 需执行的工作项 |
| WC | Work Completion, WR 完成信息 |
| WQ | Work Queue, 包含 WR, 调度单元 (= ring buffer) |
| SQ / RQ | Send / Receive Queue |
| QP | Queue Pair (SQ + RQ) |
| EQ | Event Queue, HW 事件队列 |

### 1.2 驱动模块注册

```c
// drivers/net/ethernet/mellanox/mlx5/core/main.c (v5.10)
static int __init init(void) {
    mlx5_register_debugfs();                // /sys/kernel/debug
    pci_register_driver(&mlx5_core_driver); // 初始化 PCI
    mlx5e_init();                           // 初始化 ethernet
}
module_init(init);
```

### 1.3 PCI probe 流程 (init_one)

```c
static int init_one(struct pci_dev *pdev, const struct pci_device_id *id) {
    struct devlink       *devlink = mlx5_devlink_alloc();
    struct mlx5_core_dev *dev     = devlink_priv(devlink);  // 私有数据

    dev->device = &pdev->dev;
    dev->pdev   = pdev;
    mlx5_mdev_init(dev, prof_sel);   // debugfs + page allocator workqueue
    mlx5_pci_init(dev, pdev, id);    // 启用 PCI, request BAR, set DMA mask, ioremap
    mlx5_load_one(dev, true);        // 初始化 IRQ table + event queue
    request_module_nowait(MLX5_IB_MOD);
    pci_save_state(pdev);
    // ...
}
```

**关键调用链**:
```
pci_register_driver → init_one() →
  mlx5_devlink_alloc()   // devlink (内核通用网络设备抽象, 含 netns) + 私有数据
  mlx5_mdev_init()       // debugfs + alloc_ordered_workqueue
  mlx5_pci_init()        // pci_enable_device, request_bar, pci_set_master, set_dma_caps, ioremap
  mlx5_load_one()        // 初始化 IRQ + EQ + 注册 mlx5_irq_int_handler
    └─ mlx5_irq_table_create()
         └─ pci_alloc_irq_vectors(MLX5_IRQ_VEC_COMP_BASE + 1, PCI_IRQ_MSIX)
         └─ request_irq(irqn, mlx5_irq_int_handler)  // 注册硬中断处理函数
```

### 1.4 硬件信息识别

```bash
$ lspci -vvv | grep Mellanox -A 50
d8:00.0 Ethernet controller: Mellanox MT27710 [ConnectX-4 Lx]
        Subsystem: ConnectX-4 Lx EN, 25GbE dual-port SFP28, PCIe3.0 x8
        Interrupt: pin A routed to IRQ 114
        Capabilities: [9c] MSI-X: Enable+ Count=64 Masked-
        Kernel driver in use: mlx5_core
```

关键信息: 网卡型号 / PCIe slot / IRQ 号 / MSI-X vector 数 / 驱动名.

## 2. 网卡收包 (硬件层)

略, 见原文 §2.

## 3. DMA → ring buffer

略, 见原文 §3.

## 4. 硬件中断 (IRQ)

mlx5 注册 `mlx5_irq_int_handler()` (硬中断处理函数). 中断触发后:
- 检查 EQ (Event Queue) 是否有事件
- napi_schedule() 触发软中断
- 返回

**注意**: 早期 NAPI 在执行时, 网卡不会重复触发 IRQ (避免中断风暴).

## 5-6. 软中断 + NAPI poll

```c
// ksoftirqd 线程 (每个 CPU 一个)
static void run_ksoftirqd(unsigned int cpu) {
    // ...
    while (softirq_pending(cpu)) {
        // ...
        do_softirq();  // 调用 net_rx_action()
    }
}
```

`net_rx_action()` 遍历 NAPI poll_list, 调用每个 NIC 的 `napi->poll()` 方法 (mlx5: `mlx5e_handle_rx_cqe`), 从 ring buffer 取包, 构造 skb, 送协议栈.

## 7-9. 协议栈 L2/L3/L4

### L2 (以太网) - `__netif_receive_skb_core()`

### L3 (IPv4) - `ip_rcv()`

### L4 (UDP) 调用链

```
udp_v4_early_demux()    // 早期解复用, 优化快速路径
  ↓
udp_v4_rcv()            // UDP 接收入口
  ↓
__udp4_lib_rcv()        // 校验 + 长度检查
  ↓
udp_unicast_rcv_skb()   // 单播处理
  ↓
udp_queue_rcv_skb()     // 加入 socket 队列
  ↓
udp_queue_rcv_one_skb()
  ↓
__udp_queue_rcv_skb()   // 实际入队
  ↓
__skb_queue_tail()      // 加入 socket->sk_receive_queue
  ↓
data ready in socket    // 唤醒等待进程
```

**关键点**: `udp_v4_early_demux` 优化路径, 包到达时直接定位 socket, 跳过部分 L3 处理.

## 调优点 (链接到 RX 调优篇)

| 阶段 | 关键 sysctl / 命令 |
|---|---|
| 网卡 | `ethtool -k/-K`, `-l/-L` (多队列), `-g/-G` (ring size) |
| IRQ | `/proc/irq/<N>/smp_affinity` (CPU 亲和性) |
| 软中断 | RPS/RFS (单队列网卡的补救) |
| 协议栈 | `net.core.rmem_*`, `net.ipv4.ip_forward` |
| socket | `SO_RCVBUF`, `SO_SNDBUF` |

## 关键 takeaway

- **RX 路径核心**: 硬中断 (IRQ) → ksoftirqd 软中断 → NAPI poll() → 协议栈 L2/L3/L4 → socket 队列
- **mlx5 高性能**: MSIX + 多 EQ + RSS 分散到多核并行处理
- **代码阅读顺序**: `main.c` (init_one) → `mlx5_irq_table.c` (中断) → `mlx5_eq.c` (事件队列) → `en_rx.c` (收包)
- **实战工具**: `dropwatch` (丢包点定位) + `bcc/funccount` (函数级耗时)

## 关联阅读

- [Linux 中断 (IRQ/softirq) 基础](https://arthurchiao.art/blog/linux-irq-softirq-zh/)
- [Linux 网络栈 RX 配置调优](https://arthurchiao.art/blog/linux-net-stack-tuning-rx-zh/)
- [Linux 网络栈监控](https://arthurchiao.art/blog/monitoring-network-stack/)
- 原文代码: `drivers/net/ethernet/mellanox/mlx5/core/` (Linux 5.10 tree)

---
*完整 139KB 原文含 20+ 张流程图, 全部 mlx5_core 源码段, PCI 设备 ID 表 (含 ConnectX-4 到 ConnectX-7 全系列), probe() 完整调用栈, devlink 数据结构, mlx5 术语详解 — 落本地供深读.*
