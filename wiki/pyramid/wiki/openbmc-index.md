---
type: index
tags: [openbmc, bmc, embedded-linux, server-management]
created: 2026-05-22
---

# OpenBMC — BMC 固件与服务器管理

> OpenBMC 开源基板管理控制器：硬件控制、IPMI、Redfish、安全、启动与固件更新

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/openbmc/openbmc-overview]] | OpenBMC 整体架构：硬件控制、安全子系统、技术栈总览 | openbmc, bmc, hardware-control |
| [[entities/linux/openbmc/openbmc-ipmi]] | IPMI 协议栈：KCS/SMIC 接口、FRU/SEL/SDR、内核驱动 | openbmc, ipmi, protocol |
| [[entities/linux/openbmc/openbmc-redfish]] | Redfish RESTful API：资源层级、会话认证、JSON Schema、OEM 扩展 | openbmc, redfish, rest-api |
| [[entities/linux/openbmc/openbmc-boot]] | 启动控制与固件更新：A/B 双镜像、Flash 布局、entity-manager | openbmc, boot, firmware |

## Source

| Source | Description |
|--------|-------------|
| [[sources/notes-openbmc]] | OpenBMC 深度技术分析：5 篇文档覆盖硬件控制、安全、Redfish、IPMI、启动更新 |

## Cross-References

- [[entities/linux/kernel/index]] — OpenBMC 运行在 Linux 内核之上，依赖 crypto、locking、time 等子系统
- [[os-index]] — systemd/D-Bus 是 OpenBMC 的进程管理和 IPC 基础设施
- [[entities/linux/kernel/index#networking]] — BMC 网络接口依赖内核网络栈
