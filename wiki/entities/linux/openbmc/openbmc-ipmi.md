---
type: entity
tags: [openbmc, ipmi, protocol, kcs, smic, fru, sel, sdr, kernel-driver]
created: 2026-05-22
sources: [notes-openbmc]
---

# OpenBMC IPMI 协议栈

## 定义

IPMI（Intelligent Platform Management Interface）是开放标准的硬件管理接口，OpenBMC 在用户空间通过 ipmid 守护进程实现完整的 IPMI 2.0 协议栈，Linux 内核提供 KCS/SMIC/BT 等底层传输驱动。

## 关键要点

### IPMI 消息格式

请求/响应采用 NetFn/LUN + CMD + Data 结构：
- **NetFn** (6-bit): 传感器(0x04)、应用(0x06)、固件(0x08)、存储(0x0A)、传输(0x0C)
- **CMD**: 功能命令（如 Get Sensor Reading = 0x2D）
- **CC (Completion Code)**: 响应特有，指示执行状态（0x00=成功，0xC1=无效命令）

### 传输接口

| 接口 | I/O 端口数 | 最大消息 | 复杂度 | 厂商支持 |
|------|-----------|----------|--------|---------|
| KCS | 2 | 256B | 中等 | Intel, Nuvoton |
| SMIC | 3 | 80B | 较高 | HP |
| BT | 2-3 | 256B | 高 | Intel |

KCS 状态机: IDLE → START_OP → WAIT_WRITE → WAIT_READ → IDLE，控制码包括 GET_STATUS_ABORT(0x60)、WRITE_START(0x61)、WRITE_END(0x62)、READ_BYTE(0x68)。

### Linux 内核 IPMI 架构（4 层分层）

```
用户空间 (/dev/ipmi0)
    → ipmi_devintf.c      # 字符设备，ioctl 接口
    → ipmi_msghandler.c   # 消息路由/分发，超时重试
    → ipmi_si_intf.c      # SMI 接口管理层
    → ipmi_kcs_sm.c / ipmi_smic_sm.c / ipmi_bt_sm.c  # 状态机
```

### FRU 数据（现场可替换单元）

多区域 EEPROM 存储结构：Header(格式版本+偏移) → Internal Use → Chassis Info → Board Info → Product Info → Multi-Record。每个区域 0-256B。

### SEL 事件日志

16 字节记录格式：Record ID + Type + Timestamp + Generator ID + Sensor Type/Number + Event Direction + Event Data[3]。通过 Storage NetFn (0x0A) 的 Read/Add/Clear SEL Entry 命令管理。

### SDR 传感器数据仓库

存储传感器元数据：Full Sensor(0x01)、Compact Sensor(0x02)、Event-only(0x03)、FRU Device Locator(0x11) 等。传感器读取命令为 NetFn=0x04, Cmd=0x2D。

### OpenBMC ipmid 实现

用户空间守护进程，通过 D-Bus 与 phosphor-logging、phosphor-dbus-interfaces 等服务集成。支持动态注册命令处理器，按 NetFn/CMD 分派到对应 handler。

## 相关概念

- [[entities/linux/openbmc/openbmc-overview]] — OpenBMC 整体架构与硬件控制子系统
- [[entities/linux/openbmc/openbmc-redfish]] — 现代 Redfish 接口，IPMI 的替代/补充方案
- [[entities/linux/openbmc/openbmc-boot]] — IPMI 启动选项命令 (Set System Boot Options)
- [[entities/linux/kernel/linux-kernel-ipc-core]] — Linux IPC 机制，驱动层进程间通信基础
