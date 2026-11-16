---
type: source
created: 2026-05-22
source-type: github
tags: [openbmc, bmc, hardware]
title: "OpenBMC 深度技术分析笔记"
author: "Sphinx Shi"
date: 2026-05-22
size: large
path: raw/notes/openbmc/linux_kernel/
summary: "OpenBMC 开源 BMC 固件栈深度分析：硬件控制、安全子系统、Redfish 接口、IPMI 协议栈、启动控制与固件更新，共5篇技术文档"
sources: [notes-openbmc]
---

# OpenBMC 深度技术分析笔记

## 核心内容

本来源包含 5 篇 OpenBMC 技术深度分析文档，覆盖 OpenBMC 固件栈的核心子系统：

### 1. 硬件控制子系统 (hardware_control.md)
- **phosphor-powerd**: 电源开/关/重启控制，冷冗余管理，PMBus 协议
- **phosphor-fan-presence**: 风扇存在检测和控制，GPIO 事件驱动
- **phosphor-thermal**: PID 温度监控和风扇转速调节，热区管理
- **phosphor-led-manager**: LED 指示灯控制，优先级机制解决多任务冲突
- **phosphor-watchdog**: 看门狗定时器，双重角色（BMC 自身 + 主机监控）
- **PEL 平台事件日志**: 结构化事件日志，支持优先级和事件关联

### 2. 安全子系统 (security_subsystem.md)
- **phosphor-certificate-manager**: X.509 证书管理，HTTPS/LDAPS 基础设施
- **phosphor-cryptolib**: 基于 OpenSSL 的加密原语封装（AES、RSA、ECC、SHA）
- **phosphor-user-manager**: PAM 集成认证，LDAP，TOTP 多因素认证
- **phosphor-single-root**: 受控单用户模式，物理访问紧急恢复
- **SSH 密钥管理**: authorized_keys 公钥认证
- **Secure Boot + IMA/EVM**: UEFI 安全启动链，文件完整性度量

### 3. Redfish 接口 (redfish_interface.md)
- **redfish-core**: Boost.Beast + Crow HTTP 服务器，分层路由
- **REST API 路径**: ServiceRoot → Systems/Chassis/Managers 层级结构
- **会话认证**: X-Auth-Token + Cookie 双通道，PAM 集成
- **OEM 扩展**: Intel OEM 路径（BIOS 日志、备份恢复、SecureBoot）
- **JSON Schema**: 语义化版本控制，运行时验证

### 4. IPMI 协议栈 (ipmi_protocol_stack.md)
- **IPMI 帧格式**: NetFn/LUN + CMD + Data + CC 结构
- **KCS/SMIC 接口**: 状态机驱动，I/O 端口通信
- **Linux 内核 IPMI 架构**: 4 层分层（字符设备 → 消息处理器 → SMI 接口 → 状态机）
- **FRU 解析器**: EEPROM 存储，多区域结构（Header/Chassis/Board/Product）
- **SEL 事件日志**: 16 字节记录格式，持久化存储
- **SDR 传感器**: 传感器元数据仓库，支持多种记录类型

### 5. 启动控制与固件更新 (boot_firmware_update.md)
- **phosphor-boot-manager**: 启动源/模式管理，IPMI 集成
- **phosphor-bmc-update**: A/B 双镜像方案，签名验证，UBI/静态布局
- **Redfish 固件更新 API**: HTTP Push + SimpleUpdate + TFTP
- **entity-manager**: JSON 驱动板级配置，Probe/Exposes 模式
- **Flash 布局**: U-Boot → kernel → squashfs(ro) → overlayfs(rw) 分层

## 关键引用

- OpenBMC 官方: https://github.com/openbmc
- IPMI 2.0 规范, Redfish DSP0266
- Linux 内核 IPMI 驱动: `drivers/char/ipmi/`

## 相关页面

- [[entities/linux/openbmc/openbmc-overview]]
- [[entities/linux/openbmc/openbmc-ipmi]]
- [[entities/linux/openbmc/openbmc-redfish]]
- [[entities/linux/openbmc/openbmc-boot]]
