---
type: entity
tags: [networking, osi, phy, mac, ethernet, hardware, physical-layer]
created: 2026-05-22
sources: [notes-net-deep]
---

# OSI Physical Layer (PHY & MAC) — 物理层与数据链路层架构

## 定义

OSI 模型的最底两层：物理层（PHY, Layer 1）负责比特流在物理介质上的传输（编码/解码、电气特性），数据链路层（MAC, Layer 2）负责帧的封装/解封装、介质访问控制和错误检测。在 Linux 网络栈中，二者通过 MII（Media Independent Interface）标准接口连接。

## 关键要点

### 层级结构

```
+--------------------------------------------------+
| I/F (PCI/PCIe)                                    |  数据总线
+--------------------------------------------------+
| MAC (Media Access Control)                        |
|  ├─ LLC 子层 (Logical Link Control)               |  帧封装/解封装
|  └─ MAC 子层 (介质访问控制)                        |  CSMA/CD, 地址过滤
+--------------------------------------------------+
| MII / SMI                                         |  连接 MAC ↔ PHY
|  ├─ MII/GMII/RGMII  (数据通道)                    |
|  └─ SMI (MDC/MDIO)   (管理通道, 读写PHY寄存器)     |
+--------------------------------------------------+
| PHY (Physical Layer)                              |
|  ├─ PCS (物理编码子层): 8b/10b, 64b/66b 编码      |  无帧概念,纯比特流
|  ├─ PMA (物理介质附加): 串行化/解串行化             |
|  ├─ PMD (物理介质相关): 电信号 ↔ 光信号            |
|  └─ MDI (介质相关接口): 连接物理介质                |
+--------------------------------------------------+
| I/F (RJ45, SFP, etc.)                             |  物理接口
+--------------------------------------------------+
```

### MAC 层职责

- **帧封装**：添加前导码（Preamble）、SFD（Start Frame Delimiter）、目的/源 MAC 地址、EtherType、FCS（Frame Check Sequence）
- **介质访问控制**：CSMA/CD（传统以太网）、全双工流控（PAUSE 帧）
- **地址过滤**：单播/多播/广播过滤、混杂模式
- **VLAN 处理**：802.1Q 标签添加/剥离
- **校验和**：CRC32 计算与验证

### PHY 层职责

- **编码**：将 MAC 传递的比特流按物理编码规则转换（如 1000BASE-T 的 4D-PAM5）
- **电气/光信号转换**：电压驱动、光调制
- **自协商（Auto-Negotiation）**：检测对端能力和最优速率/双工模式
- **链路状态检测**：Link Up/Down 检测、错误计数
- 关键：PHY 层看不到帧和协议，只处理二进制比特流

### MII 接口族

| 接口 | 位宽 | 时钟 | 速率 |
|------|------|------|------|
| MII | 4 bit | 25 MHz | 100 Mbps |
| GMII | 8 bit | 125 MHz | 1000 Mbps |
| RGMII | 4 bit | 125 MHz (DDR) | 1000 Mbps |
| SGMII | 串行 | 1.25 Gbps | 1000 Mbps |
| XGMII | 32 bit | 156.25 MHz | 10 Gbps |

SMI（Serial Management Interface）使用 MDC（时钟）+ MDIO（数据）两线协议，通过读写 PHY 芯片的 IEEE 802.3 标准寄存器来控制和查询状态。

### 固件 vs 驱动分工

| 运行位置 | 职责 | 特点 |
|----------|------|------|
| **固件 (Firmware)** | 设备微控制器内 | 实时性要求高的功能（PHY 自协商、MAC 地址过滤）、协议无关、跨平台 |
| **驱动 (Driver)** | 主机 OS 内核 | OS 相关接口（PCI 枚举、DMA 映射、net_device 注册）、中断处理、ethtool |

理想情况：尽可能多功能放固件，减少驱动代码量和跨平台维护成本。

### 硬件数据流

```
DMA ←→ CPU/MCU    (描述符环, skb 数据拷贝)
DMA ←→ MAC        (帧缓冲, TX/RX 环形队列)
MAC ←→ PHY        (MII 数据接口)
PHY ←→ 物理介质    (RJ45/SFP)
```

## 相关概念

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Linux 内核 net_device 抽象，驱动通过此接口对接 MAC
- [[entities/linux/network/linux-network-protocols]] — 以太网帧格式与协议栈上层处理
- [[entities/linux/network/net-stack-deep-dive]] — 从 PHY 到应用层的全栈路径

## 来源详情

- [[sources/notes-net-deep]] — osi_phy_mac.md
