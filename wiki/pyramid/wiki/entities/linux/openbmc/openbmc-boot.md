---
type: entity
tags: [openbmc, boot, firmware-update, u-boot, flash-layout, dual-image, entity-manager]
created: 2026-05-22
sources: [notes-openbmc]
---

# OpenBMC 启动与固件更新

## 定义

OpenBMC 启动控制与固件更新子系统管理主机启动顺序、BMC/BIOS 固件的安全升级，以及运行时板级配置。核心组件包括 phosphor-boot-manager、phosphor-bmc-update（A/B 双镜像）、entity-manager 和 obmc-trigger。

## 关键要点

### 启动控制 (phosphor-boot-manager)

**启动源类型**:
- `Network` (PXE)、`HDD`、`USB`、`BIOS`、`UEFI`、`Diag`、`CDROM`、`Floppy`

**启动模式**:
- `Regular`（正常）、`Setup`（BIOS设置）、`ForcePxe`、`HardwareReset`、`FlashUpdate`

**D-Bus 接口路径**: `/xyz/openbmc_project/state/host0`，属性包括 BootSource、BootMode、BootOrder、BootProgress。

**IPMI 集成**: 通过 Set System Boot Options (NetFn=0x00, Cmd=0x08) 设置启动选项。

### A/B 双镜像固件更新

核心设计原则：
- 两套完整 BMC 镜像（Image A / Image B），当前运行标记为 "functional"
- 更新写入非 active 镜像，验证后重启切换
- 旧镜像保留作为回退选项，直到新镜像验证成功
- 版本 ID = 版本字符串的 SHA-512 哈希前 8 个十六进制字符

**更新流程状态机**: IDLE → VERIFYING（签名验证）→ ACTIVATING（Flash写入）→ READY（等待重启）→ ACTIVE

**更新方式对比**:

| 方式 | 速度 | 安全性 | 适用场景 |
|------|------|--------|----------|
| Redfish HTTP Push | 中等 | 高(TLS) | 常规更新 |
| REST API | 中等 | 高(TLS) | 自动化 |
| IPMI (LPC/PCI) | 快 | 中 | 快速/紧急 |
| SCP | 快 | 中 | 开发调试 |
| TFTP | 快 | 低 | 内网 |

### Flash 布局

```
SPI Flash
├── U-Boot (512KB-1MB)          # 引导程序，管理双镜像切换
├── Image A                     # 活动镜像
│   ├── image-u-boot
│   ├── image-kernel (4-8MB)   # Linux 内核
│   ├── image-rofs (16-32MB)   # squashfs 只读根文件系统
│   ├── image-rwfs (8-16MB)    # overlayfs 可写层
│   └── image-journalfs
├── Image B                     # 备用镜像（同上）
└── U-Boot env (128KB)          # 环境变量、NVRAM
```

overlayfs 结构：squashfs (lower, ro) + UBIFS/JFFS2 (upper, rw) → 合并视图。

### entity-manager 板级配置

JSON 驱动的运行时配置管理：
- **Entity**: 物理可检测组件（PSU、风扇、TPM）
- **Probe**: D-Bus 接口规则，检测实体存在（如读取 FRU EEPROM）
- **Exposes**: 将检测到的实体功能发布到 D-Bus
- **触发重检测**: 主机上电、驱动器/PSU 插拔事件

### systemd 启动目标层次

```
obmc-host-start@0.target
├── obmc-chassis-poweron@0.target → 应用机箱电源
├── obmc-host-startmin@0.target   → 最小启动服务
└── phosphor-reset-host-reboot-attempts@0.service
```

关键目标还包括：`obmc-host-shutdown`（软关机）、`obmc-chassis-hard-poweroff`（硬断电）、`obmc-host-quiesce`（错误处理）。

### obmc-trigger 触发器

响应系统事件并执行预定义操作：电源触发、热触发、启动触发、更新触发。与 phosphor-state-manager 紧密集成。

## 相关概念

- [[entities/linux/openbmc/openbmc-overview]] — OpenBMC 整体架构，硬件控制子系统是启动管理的基础
- [[entities/linux/openbmc/openbmc-ipmi]] — IPMI 固件更新命令、BIOS 远程配置
- [[entities/linux/openbmc/openbmc-redfish]] — Redfish UpdateService 实现 HTTP 固件推送
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — 内核内存管理，Flash 文件系统依赖
