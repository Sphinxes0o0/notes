# OpenBMC 子系统文档索引

## 概述

OpenBMC 是基于 Linux 的开源 BMC 固件栈，核心设计基于 Phosphor D-Bus 框架。本文档索引涵盖 OpenBMC 的 8 大核心子系统的深度分析。

**源码仓库**: https://github.com/openbmc

---

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [phosphor_dbus_services.md](phosphor_dbus_services.md) | Phosphor D-Bus 服务层: 状态管理/日志/传感器/FRU/LED | openbmc/phosphor-dbus-interfaces |
| [ipmi_protocol_stack.md](ipmi_protocol_stack.md) | IPMI 协议栈: 命令/KCS/SMIC/FRU/SEL/SDR | openbmc/ipmid |
| [redfish_interface.md](redfish_interface.md) | Redfish 接口: REST API/JSON Schema/Session | openbmc/redfish-core |
| [kvm_virtualmedia.md](kvm_virtualmedia.md) | KVM/虚拟介质: VNC/NBD/USB Gadget | openbmc/phosphor-kvm |
| [hardware_control.md](hardware_control.md) | 硬件控制: 电源/风扇/热/PID/LED/看门狗 | openbmc/phosphor-power |
| [boot_firmware_update.md](boot_firmware_update.md) | 启动控制/固件更新: 双镜像/Flash布局 | openbmc/phosphor-boot |
| [security_subsystem.md](security_subsystem.md) | 安全子系统: 证书/加密/用户/PAM/SSH | openbmc/phosphor-certificate-manager |
| [network_comm_services.md](network_comm_services.md) | 通信/网络服务: 网络/Web UI/D-Bus | openbmc/phosphor-networkd |

---

## 1. Phosphor D-Bus 服务层 (phosphor_dbus_services.md)

### 核心服务
| 服务 | D-Bus 路径 | 功能 |
|------|-----------|------|
| phosphor-state-manager | /xyz/openbmc_project/state/* | 电源/启动/看门狗状态机 |
| phosphor-log-manager | /xyz/openbmc_project/logging/* | SEL 日志管理 |
| phosphor-inventory-manager | /xyz/openbmc_project/inventory/* | FRU 资产信息 |
| phosphor-sensor-manager | /xyz/openbmc_project/sensors/* | 传感器数据/SDR |
| phosphor-fru-inventory | /xyz/openbmc_project/fru/* | FRU EEPROM 读写 |
| phosphor-led-manager | /xyz/openbmc_project/led/* | LED 指示控制 |
| phosphor-pef | /xyz/openbmc_project/pef/* | 事件过滤/告警 |

---

## 2. IPMI 协议栈 (ipmi_protocol_stack.md)

### 核心组件
| 组件 | 源码 | 功能 |
|------|------|------|
| ipmid | openbmc/ipmid | IPMI 命令处理 |
| ipmi-fru-parser | openbmc/ipmi-fru-parser | FRU 数据解析 |
| ipmi-sel | openbmc/ipmi-sel | SEL 事件日志 |
| ipmi-sensor | openbmc/ipmi-sensor | 传感器读取 |

### IPMI 消息格式
```
NetFn/LUN (1B) | CMD (1B) | Data (N bytes)
```

### 硬件接口
- **KCS**: Keyboard Controller Style (最常用)
- **SMIC**: Server Management Interface Card
- **BT**: Block Transfer

---

## 3. Redfish 接口 (redfish_interface.md)

### REST API 路径
| 路径 | 描述 |
|------|------|
| /redfish/v1/ | 服务根 |
| /redfish/v1/Systems | 服务器系统 |
| /redfish/v1/Chassis | 机箱 |
| /redfish/v1/Managers | BMC 管理器 |
| /redfish/v1/EventService | 事件订阅 |

### 认证机制
- Session-based 认证
- X.509 证书
- HTTP Basic Auth (禁用)

---

## 4. KVM/虚拟介质 (kvm_virtualmedia.md)

### 数据流
```
Web Browser → bmcweb → phosphor-virtualmedia → NBD Client → USB Gadget → HOST
```

### 核心组件
| 组件 | 功能 |
|------|------|
| phosphor-virtualmedia | 介质重定向 (CD/DVD/USB) |
| phosphor-kvm | KVM 会话管理 |
| obmc-ikvm | VNC/RFB 视频流 |

---

## 5. 硬件控制 (hardware_control.md)

### 子系统
| 组件 | 功能 |
|------|------|
| phosphor-powerd | 电源开/关/重启 |
| phosphor-fan-presence | 风扇检测/控制 |
| phosphor-thermal | 温度监控/PID 控制 |
| phosphor-led-manager | LED 指示 |
| phosphor-watchdog | 看门狗服务 |
| PEL | 平台事件日志 |

---

## 6. 启动控制/固件更新 (boot_firmware_update.md)

### Flash 布局
```
┌─────────────┬─────────────┬─────────────┐
│  U-Boot     │   Kernel    │  Rootfs     │
├─────────────┼─────────────┼─────────────┤
│  u-boot     │  kernel     │  squashfs   │
│  env        │  dtb        │  overlay    │
└─────────────┴─────────────┴─────────────┘
       ↑            ↑            ↑
    Bootloader    Linux      用户空间
```

### 双镜像 A/B
```
镜像 A (Active) ←→ 镜像 B (Backup)
```

---

## 7. 安全子系统 (security_subsystem.md)

### 安全机制
| 组件 | 功能 |
|------|------|
| phosphor-certificate-manager | X.509 证书管理 |
| phosphor-cryptolib | 加密服务 (AES/RSA/HMAC) |
| phosphor-user-manager | 用户/PAM 集成 |
| phosphor-single-root | 单用户模式 |
| SSH | authorized_keys 管理 |
| Secure Boot | 启动链签名验证 |

---

## 8. 通信/网络服务 (network_comm_services.md)

### 网络架构
```
┌─────────────────────────────────────┐
│    bmcweb (HTTP/HTTPS Server)       │
├─────────────────────────────────────┤
│  Redfish │ REST │ WebSocket │ KVM │
├─────────────────────────────────────┤
│      phosphor-networkd (网络配置)     │
├─────────────────────────────────────┤
│         systemd-networkd             │
├─────────────────────────────────────┤
│         eth0 / eth1                  │
└─────────────────────────────────────┘
```

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │        管理接口层                        │
                    │  IPMI │ Redfish │ REST │ Web UI │ SSH  │
                    └─────────────────┬─────────────────────┘
                                          │
                    ┌─────────────────┴─────────────────────┐
                    │         Phosphor D-Bus 服务层           │
                    │  状态 │ 日志 │ 传感器 │ FRU │ LED    │
                    └─────────────────┬─────────────────────┘
                                          │
                    ┌─────────────────┴─────────────────────┐
                    │         硬件抽象层                     │
                    │  电源 │ 风扇 │ 温度 │ I2C │ USB Gadget │
                    └─────────────────┬─────────────────────┘
                                          │
                    ┌─────────────────┴─────────────────────┐
                    │         Linux Kernel / BMC Firmware    │
                    └─────────────────────────────────────────┘
```

---

## 知识点关联表

| 层级 | 组件 | 协议/接口 | 核心文件 |
|------|------|----------|----------|
| 管理接口 | ipmid | IPMI | netfn.cpp |
| 管理接口 | bmcweb | Redfish/HTTP | main.cpp |
| 服务层 | phosphor-state-manager | D-Bus | state_manager.cpp |
| 服务层 | phosphor-log-manager | D-Bus | log_manager.cpp |
| 硬件抽象 | phosphor-powerd | D-Bus/sysfs | power_manager.cpp |
| 硬件抽象 | phosphor-fan-presence | D-Bus/I2C | fan_presence.cpp |
| 固件更新 | phosphor-bmc-update | D-Bus/Redfish | update_manager.cpp |
| 安全 | phosphor-certificate-manager | D-Bus/OpenSSL | cert_manager.cpp |

---

**文档版本**: R1
**分析源码**: OpenBMC (latest)
**生成时间**: 2026-04-27
