---
type: entity
tags: [openbmc, redfish, rest-api, https, json-schema, dmtf, bmcweb]
created: 2026-05-22
sources: [notes-openbmc]
---

# OpenBMC Redfish 接口

## 定义

Redfish 是 DMTF 制定的 RESTful 硬件管理标准，OpenBMC 通过 bmcweb 组件实现完整的 Redfish API，提供 HTTPS/JSON 的现代化服务器管理能力，是对传统 IPMI 的升级替代方案。

## 关键要点

### Redfish vs IPMI 对比

| 特性 | IPMI | Redfish |
|------|------|---------|
| 架构 | 静态模型 | 可扩展面向对象模型 |
| 传输 | UDP | HTTPS/JSON |
| 安全性 | 弱 | TLS + 会话认证 |
| 可扩展性 | 有限 | 完全可扩展（OEM） |

### REST API 资源层级

```
/redfish/v1/                              # ServiceRoot
├── /Systems/{id}                         # 计算机系统
│   ├── Processors, Memory, Storage
│   ├── EthernetInterfaces, Bios
│   └── LogServices
├── /Chassis/{id}                         # 机箱
│   ├── Thermal, Power, Sensors
│   ├── NetworkAdapters, Drives
│   └── PCIeSlots, Controls
├── /Managers/{id}                        # BMC 管理器
│   ├── EthernetInterfaces, NetworkProtocol
│   ├── VirtualMedia, Sessions, NTP
│   └── LogServices
├── /AccountService                       # 账户管理
│   ├── Accounts, Roles
├── /SessionService                       # 会话管理
│   └── Sessions
├── /UpdateService                        # 固件更新
│   ├── FirmwareInventory, SoftwareInventory
├── /EventService, /TaskService           # 事件/任务
├── /Registries, /JSONSchemas             # 注册表/Schema
```

### 会话认证机制

- **创建会话**: `POST /redfish/v1/SessionService/Sessions`（Basic Auth）
- **令牌传递**: `X-Auth-Token` 请求头或 `SESSIONID` Cookie
- **会话超时**: 默认 3600 秒，可通过 SessionService 配置
- **锁户策略**: 失败阈值 3，锁定时长 30 秒
- **底层集成**: 通过 D-Bus 调用 phosphor-user-manager → PAM 认证框架

### JSON Schema 版本控制

采用语义化版本 `v{Major}_{Minor}_{Patch}`，如 `#ComputerSystem.v1_18_0.ComputerSystem`。运行时验证必需字段（`@odata.type`、`@odata.id`、`Id`）。

### OEM 扩展（Intel 示例）

Intel 在 OpenBMC 中添加的 OEM 路径：`/redfish/v1/Managers/bmc/Intel/`，提供 BIOS 技术日志、备份恢复、SecureBoot、SMBIOS、TPM Inventory 等厂商特有功能。

### 特性开关管理

通过 `redfish-disabled` 组件控制功能启用：事件通知、虚拟介质、TelemetryService 等可按需禁用，返回 HTTP 503 Disabled。

### 标准错误响应

```json
{
  "error": {
    "code": "Base.1.0.GeneralError",
    "message": "A general error occurred",
    "@Message.ExtendedInfo": [
      { "MessageId": "Base.1.0.ResourceMissing", "Severity": "Critical" }
    ]
  }
}
```

## 相关概念

- [[entities/linux/openbmc/openbmc-overview]] — OpenBMC 整体架构，Redfish 为其上层管理接口
- [[entities/linux/openbmc/openbmc-ipmi]] — 传统 IPMI 协议，Redfish 的对比和补充
- [[entities/linux/openbmc/openbmc-boot]] — 通过 Redfish UpdateService 实现固件在线更新
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] — Netfilter，BMC 网络安全基础
