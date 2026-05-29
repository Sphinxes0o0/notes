---
type: entity
tags: [openbmc, bmc, hardware-control, security, embedded-linux]
created: 2026-05-22
sources: [notes-openbmc]
---

# OpenBMC 概述

## 定义

OpenBMC 是 Linux 基金会旗下的开源 BMC（Baseboard Management Controller）固件项目，基于 Yocto/OpenEmbedded 构建，使用 systemd + D-Bus 架构，是服务器带外管理的完整软件栈。

## 关键要点

### 架构层次

OpenBMC 采用三层架构：
- **上层管理接口**: Redfish (RESTful JSON/HTTPS)、IPMI 2.0 (KCS/SMIC)、SSH/SOL
- **中间服务层**: Phosphor 系列守护进程，通过 D-Bus 总线通信
- **底层硬件抽象**: Linux 内核驱动（I2C、GPIO、HWMON、PWM、SPI Flash）

### 硬件控制子系统

六大核心子系统协同工作以实现完整的服务器硬件管理：

| 子系统 | 守护进程 | 核心职责 | D-Bus 关键接口 |
|--------|---------|---------|---------------|
| 电源控制 | phosphor-powerd | 开关机、冷冗余、PMBus 监控 | `xyz.openbmc_project.State.Chassis` |
| 风扇控制 | phosphor-fan-presence | 存在检测、GPIO 事件 | `xyz.openbmc_project.Inventory.Item.Fan` |
| 热管理 | phosphor-thermal | PID 温控、风扇调速、热区 | `xyz.openbmc_project.Control.Thermal` |
| LED 指示 | phosphor-led-manager | 状态指示、优先级仲裁 | `xyz.openbmc_project.Led.Group` |
| 看门狗 | phosphor-watchdog | 超时检测、自动恢复 | `xyz.openbmc_project.Watchdog` |
| 事件日志 | phosphor-logging | PEL 格式、持久化存储 | `xyz.openbmc_project.Logging` |

### 安全子系统

纵深防御的安全体系：
- **认证层**: phosphor-user-manager + PAM（本地密码、LDAP、TOTP MFA）
- **加密层**: phosphor-cryptolib（AES、RSA、ECC、SHA/HMAC）
- **证书层**: phosphor-certificate-manager（X.509 证书生命周期管理）
- **启动安全**: UEFI Secure Boot + IMA/EVM + TPM 2.0
- **恢复通道**: phosphor-single-root（受控单用户模式）

### 技术栈

- **构建系统**: BitBake (Yocto/OpenEmbedded) + Meson/Ninja
- **编程语言**: C++ (核心) + Python (工具脚本)
- **进程通信**: D-Bus (sdbusplus)
- **进程管理**: systemd
- **配置格式**: JSON 驱动（取代旧版 YAML）
- **硬件接口**: sysfs、HWMON、GPIO、I2C/PMBus

## 相关概念

- [[entities/linux/openbmc/openbmc-ipmi]] — IPMI 2.0 协议栈实现，KCS/SMIC 接口
- [[entities/linux/openbmc/openbmc-redfish]] — Redfish RESTful API 接口，会话认证
- [[entities/linux/openbmc/openbmc-boot]] — 启动控制、A/B 双镜像固件更新
- [[entities/linux/kernel/linux-kernel-locking-core]] — Linux 内核锁机制，D-Bus 内部依赖
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度器，systemd 服务调度基础
