# OpenBMC Redfish 接口深度分析

## 1. 概述

OpenBMC（Open Board Management Controller）是一个开源的 BMC（Baseboard Management Controller）固件项目，旨在为服务器硬件管理提供标准化接口。Redfish 是 DMTF（Distributed Management Task Force）制定的 RESTful 硬件管理接口标准，OpenBMC 通过实现 Redfish 接口提供了现代化的硬件管理能力。

### 1.1 Redfish 标准背景

Redfish 标准于 2015 年首次发布，旨在解决传统 IPMI（Intelligent Platform Management Interface）协议的局限性：

| 特性 | IPMI | Redfish |
|------|------|---------|
| 架构 | 静态模型 | 可扩展的面向对象模型 |
| 传输 | 仅 UDP | HTTPS/JSON |
| 安全性 | 弱 | TLS + 会话认证 |
| 可扩展性 | 有限 | 完全可扩展 |
| 现代化程度 | 1990年代设计 | 2015年后设计 |

### 1.2 OpenBMC Redfish 组件架构

OpenBMC 的 Redfish 实现由多个核心组件构成：

```
redfish-core/          # Redfish REST API 核心框架
├── lib/
│   ├── routes/        # REST API 路由定义
│   ├── handlers/      # 请求处理器
│   └── middleware/    # 中间件（认证、日志）
├── service_root.cpp    # /redfish/v1 服务根
├── systems.cpp         # /redfish/v1/Systems
├── chassis.cpp         # /redfish/v1/Chassis
└── managers.cpp        # /redfish/v1/Managers

redfish-interfaces/    # Redfish 接口定义（Schema）
redfish-tools/         # Schema 生成和验证工具
```

---

## 2. redfish-core 核心框架分析

### 2.1 框架结构

redfish-core 是 OpenBMC Redfish 实现的核心库，提供了 HTTP 服务器、路由管理、请求处理和响应序列化的基础设施。

**核心目录结构：**

```
redfish-core/
├── include/
│   └── redfish-core/
│       ├── lib/
│       │   ├── http_status.hpp       # HTTP 状态码定义
│       │   ├── encode_json.hpp       # JSON 编码辅助
│       │   ├── errors.hpp            # 错误处理
│       │   └──utility.hpp            # 工具函数
│       └── service/
│           ├── root.hpp              # 服务根
│           ├── systems.hpp           # 系统资源
│           └── chassis.hpp           # 机箱资源
├── lib/
│   ├── service_root.cpp
│   ├── systems.cpp
│   ├── chassis.cpp
│   └── managers.cpp
└── main.cpp                          # 入口
```

### 2.2 HTTP 服务架构

redfish-core 使用 Boost.Beast 作为 HTTP 服务器底层，结合 Crow 作为高级框架：

```cpp
// 典型的 Redfish HTTP 服务器初始化
#include <boost/beast.hpp>
#include <crow.h>

int main() {
    crow::SimpleApp app;

    // Redfish 中间件链
    app.template register_middleware<SessionAuthMiddleware>();
    app.template register_middleware<CORSMiddleware>();

    // 注册 Redfish 路由
    setupRedfishRoutes(app);

    app.bindaddr("0.0.0.0").port(443).ssl()
       .multithreaded().run();
}
```

### 2.3 路由系统

Redfish API 采用分层路由结构：

```cpp
// /redfish/v1 路由组
CROW_ROUTE(app, "/redfish/v1")
    .methods(crow::HTTPMethod::GET)
    (getServiceRoot);

// /redfish/v1/Systems 路由组
CROW_ROUTE(app, "/redfish/v1/Systems")
    .methods(crow::HTTPMethod::GET)
    (getSystemsCollection);

// /redfish/v1/Systems/<id> 单个系统
CROW_ROUTE(app, "/redfish/v1/Systems/<str>")
    .methods(crow::HTTPMethod::GET)
    (getSystemById);
```

### 2.4 处理器模式

每个 Redfish 资源都有对应的处理器类：

```cpp
class SystemsHandler : public CrowHandler {
public:
    crow::response getSystemsCollection() {
        crow::json::wvalue result;
        result["@odata.type"] = "#ComputerSystemCollection.ComputerSystemCollection";
        result["@odata.id"] = "/redfish/v1/Systems";
        result["Name"] = "Computer System Collection";
        result["Members"] = getSystemMembers();
        result["Members@odata.count"] = getSystemCount();
        return crow::response(result);
    }

    crow::response getSystemById(const std::string& id) {
        // 返回单个系统详细信息
    }
};
```

---

## 3. REST API 路径结构

### 3.1 服务根（Service Root）

**路径**: `/redfish/v1/`

服务根是 Redfish API 的入口点，返回 API 的元信息：

```json
{
    "@odata.type": "#ServiceRoot.v1_14_0.ServiceRoot",
    "@odata.id": "/redfish/v1",
    "Id": "RootService",
    "Name": "Root Service",
    "RedfishVersion": "1.15.0",
    "UUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Systems": {
        "@odata.id": "/redfish/v1/Systems"
    },
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Registries": {
        "@odata.id": "/redfish/v1/Registries"
    },
    "JSONSchemas": {
        "@odata.id": "/redfish/v1/JSONSchemas"
    }
}
```

### 3.2 系统集合（Systems Collection）

**路径**: `/redfish/v1/Systems/`

返回所有托管系统的集合：

```json
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.id": "/redfish/v1/Systems",
    "Name": "Computer System Collection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/system1"
        }
    ],
    "Members@odata.count": 1,
    "Description": "Collection of Computer Systems"
}
```

### 3.3 单个系统（Single System）

**路径**: `/redfish/v1/Systems/{ComputerSystemId}`

返回特定计算机系统的详细信息：

```json
{
    "@odata.type": "#ComputerSystem.v1_18_0.ComputerSystem",
    "@odata.id": "/redfish/v1/Systems/system1",
    "Id": "system1",
    "Name": "OpenBMC Server",
    "SystemType": "Physical",
    "Summary": {
        "Status": {
            "Health": "OK",
            "State": "Enabled"
        }
    },
    "ProcessorSummary": {
        "Count": 4,
        "Model": "ARM Cortex-A72",
        "Status": {"Health": "OK"}
    },
    "MemorySummary": {
        "TotalSystemMemoryGiB": 8,
        "Status": {"Health": "OK"}
    },
    "BiosVersion": "v2.0.0",
    "PowerState": "On",
    "PhysicalSecurity": {
        "IntrusionSensorNumber": 1,
        "IntrusionSensor": "Normal",
        "IntrusionSensorSupported": true
    },
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "IndicatorLED": "Off",
    "Model": "OpenBMC BMC",
    "Manufacturer": "OpenBMC Project",
    "SerialNumber": "abc123456789",
    "PartNumber": "OpenBMC-001",
    "AssetTag": "OPENBMC-ASSET",
    "SKU": "",
    "HostName": "bmc-host",
    "Boot": {
        "BootSourceOverrideEnabled": "Disabled",
        "BootSourceOverrideTarget": "None",
        "BootSourceOverrideMode": "UEFI"
    },
    "Processors": {
        "@odata.id": "/redfish/v1/Systems/system1/Processors"
    },
    "Memory": {
        "@odata.id": "/redfish/v1/Systems/system1/Memory"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Systems/system1/Storage"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Systems/system1/EthernetInterfaces"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Systems/system1/LogServices"
    },
    "NetworkInterfaces": {
        "@odata.id": "/redfish/v1/Systems/system1/NetworkInterfaces"
    },
    "Bios": {
        "@odata.id": "/redfish/v1/Systems/system1/Bios"
    },
    "Actions": {
        "#ComputerSystem.Reset": {
            "target": "/redfish/v1/Systems/system1/Actions/ComputerSystem.Reset"
        }
    }
}
```

### 3.4 机箱集合（Chassis Collection）

**路径**: `/redfish/v1/Chassis/`

返回所有机箱（包含 BMC 所在的主板）：

```json
{
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "@odata.id": "/redfish/v1/Chassis",
    "Name": "Chassis Collection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Chassis/chassis1"
        },
        {
            "@odata.id": "/redfish/v1/Chassis/mb_root"
        }
    ],
    "Members@odata.count": 2
}
```

### 3.5 单个机箱（Single Chassis）

**路径**: `/redfish/v1/Chassis/{ChassisId}`

```json
{
    "@odata.type": "#Chassis.v1_20_0.Chassis",
    "@odata.id": "/redfish/v1/Chassis/chassis1",
    "Id": "chassis1",
    "Name": "Main Chassis",
    "ChassisType": "RackMount",
    "AssetTag": "CHASSIS-001",
    "Manufacturer": "OpenBMC",
    "Model": "OpenBMC Chassis",
    "SKU": "",
    "SerialNumber": "SN123456789",
    "PartNumber": "PN987654321",
    "PowerState": "On",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "ThermalState": "OK",
    "PowerState": "On",
    "IndicatorLED": "Off",
    "EnvironmentalClass": "A1",
    "Sensors": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Sensors"
    },
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Thermal"
    },
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Power"
    },
    "PowerSubsystem": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/PowerSubsystem"
    },
    "ThermalSubsystem": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/ThermalSubsystem"
    },
    "NetworkAdapters": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/NetworkAdapters"
    },
    "Drives": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Drives"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Storage"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/LogServices"
    },
    "PCIeSlots": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/PCIeSlots"
    },
    "Controls": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Controls"
    },
    "EnvironmentMetrics": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/EnvironmentMetrics"
    },
    "Triggers": {
        "@odata.id": "/redfish/v1/Chassis/chassis1/Triggers"
    },
    "Links": {
        "ComputerSystems": [
            {
                "@odata.id": "/redfish/v1/Systems/system1"
            }
        ],
        "ManagedBy": [
            {
                "@odata.id": "/redfish/v1/Managers/bmc"
            }
        ]
    }
}
```

### 3.6 管理器集合（Managers Collection）

**路径**: `/redfish/v1/Managers/`

```json
{
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "@odata.id": "/redfish/v1/Managers",
    "Name": "Manager Collection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/bmc"
        }
    ],
    "Members@odata.count": 1
}
```

### 3.7 单个管理器（Single Manager - BMC）

**路径**: `/redfish/v1/Managers/{ManagerId}`

```json
{
    "@odata.type": "#Manager.v1_16_0.Manager",
    "@odata.id": "/redfish/v1/Managers/bmc",
    "Id": "bmc",
    "Name": "OpenBMC Manager",
    "ManagerType": "BMC",
    "Description": "Baseboard Management Controller",
    "Model": "OpenBMC",
    "Manufacturer": "OpenBMC Project",
    "FWVersion": "v2.15.0-dev",
    "UUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "PartNumber": "",
    "SerialNumber": "",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "PowerState": "On",
    "CommandShell": {
        "ServiceEnabled": true,
        "ConnectTypesSupported": ["SSH", "IPMI"],
        "ConnectTypesEnabled": ["SSH"]
    },
    "GraphicalConsole": {
        "ServiceEnabled": true,
        "ConnectTypesSupported": ["KVMIP", "VirtualMedia"],
        "ConnectTypesEnabled": ["KVMIP", "VirtualMedia"]
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/bmc/EthernetInterfaces"
    },
    "NetworkProtocol": {
        "@odata.id": "/redfish/v1/Managers/bmc/NetworkProtocol"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Managers/bmc/LogServices"
    },
    "VirtualMedia": {
        "@odata.id": "/redfish/v1/Managers/bmc/VirtualMedia"
    },
    "Sessions": {
        "@odata.id": "/redfish/v1/Managers/bmc/Sessions"
    },
    "NTP": {
        "@odata.id": "/redfish/v1/Managers/bmc/NTP"
    },
    "Actions": {
        "#Manager.Reset": {
            "target": "/redfish/v1/Managers/bmc/Actions/Manager.Reset"
        }
    }
}
```

---

## 4. Redfish JSON Schema

### 4.1 Schema 版本控制

Redfish 使用语义化版本控制（SemVer），格式为 `Major_Minor_Patch`：

```json
{
    "@odata.type": "#ComputerSystem.v1_18_0.ComputerSystem"
}
```

### 4.2 Schema 注册表

**路径**: `/redfish/v1/JSONSchemas/`

```json
{
    "@odata.type": "#JsonSchemaFileCollection.JsonSchemaFileCollection",
    "@odata.id": "/redfish/v1/JSONSchemas",
    "Name": "JSON Schema Files",
    "Members": [
        {
            "@odata.id": "/redfish/v1/JSONSchemas/ComputerSystem"
        },
        {
            "@odata.id": "/redfish/v1/JSONSchemas/Chassis"
        }
    ]
}
```

### 4.3 资源导航属性

Redfish 使用 `@odata.id` 实现资源间导航：

```json
{
    "Systems": {
        "@odata.id": "/redfish/v1/Systems"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Systems/system1/LogServices"
    }
}
```

### 4.4 odata.type 模式

所有 Redfish 资源都包含 `@odata.type` 标识资源类型：

```
{ResourceType}.v{VersionMajor}_{VersionMinor}_{VersionPatch}.{ResourceType}
```

示例：
- `#ComputerSystem.v1_18_0.ComputerSystem`
- `#Chassis.v1_20_0.Chassis`
- `#Manager.v1_16_0.Manager`
- `#Session.v1_4_0.Session`

### 4.5 Schema 验证

OpenBMC 在运行时进行 JSON Schema 验证：

```cpp
#include <nlohmann/json.hpp>
#include <ajson/ajson.hpp>

void validateRedfishResource(const nlohmann::json& json,
                             const std::string& schemaType) {
    // 检查必需的 odata 字段
    if (!json.contains("@odata.type")) {
        throw RedfishValidationError("Missing @odata.type");
    }
    if (!json.contains("@odata.id")) {
        throw RedfishValidationError("Missing @odata.id");
    }
    if (!json.contains("Id")) {
        throw RedfishValidationError("Missing Id");
    }

    // 验证类型匹配
    std::string expected = "#" + schemaType;
    if (json["@odata.type"] != expected) {
        throw RedfishValidationError("Type mismatch");
    }
}
```

---

## 5. Session 认证机制

### 5.1 认证流程概述

Redfish 支持两种认证方式：
1. **会话令牌认证（Session Token）** - 推荐方式
2. **基本认证（Basic Auth）** - 仅用于创建会话

### 5.2 会话创建

**路径**: `POST /redfish/v1/SessionService/Sessions`

请求：
```json
{
    "UserName": "root",
    "Password": "0penBMC"
}
```

成功响应（201 Created）：
```json
{
    "@odata.type": "#Session.v1_4_0.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/session123",
    "Id": "session123",
    "Name": "User Session",
    "Description": "User Session",
    "UserName": "root",
    "Created": "2026-04-27T00:00:00Z",
    "Expires": "2026-04-27T01:00:00Z"
}
```

响应头包含会话令牌：
```
X-Auth-Token: sess_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Set-Cookie:SESSIONID=session123; Path=/
```

### 5.3 会话令牌认证

后续请求使用 `X-Auth-Token` 头或 Cookie 认证：

```bash
# 使用 X-Auth-Token
curl -H "X-Auth-Token: sess_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
     https://bmc-host/redfish/v1/Systems

# 使用 Cookie
curl -H "Cookie: SESSIONID=session123" \
     https://bmc-host/redfish/v1/Systems
```

### 5.4 会话中间件实现

```cpp
class SessionAuthMiddleware {
public:
    crow::response handle(crow::request& req) {
        // 检查是否跳过认证的路径
        if (isPublicPath(req.url)) {
            return crow::response(200);
        }

        // 获取认证令牌
        std::string token = getAuthToken(req);

        if (token.empty()) {
            return crow::response(401, "Unauthorized");
        }

        // 验证会话
        auto session = sessionManager.validateToken(token);
        if (!session) {
            return crow::response(401, "Invalid session");
        }

        // 检查会话过期
        if (session->isExpired()) {
            sessionManager.remove(token);
            return crow::response(401, "Session expired");
        }

        // 将会话信息附加到请求
        req.ctx["session"] = session;
        return crow::response(200);
    }
};
```

### 5.5 会话服务

**路径**: `/redfish/v1/SessionService/`

```json
{
    "@odata.type": "#SessionService.v1_2_0.SessionService",
    "@odata.id": "/redfish/v1/SessionService",
    "Id": "SessionService",
    "Name": "Session Service",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "ServiceEnabled": true,
    "SessionTimeout": 3600,
    "Sessions": {
        "@odata.id": "/redfish/v1/SessionService/Sessions"
    }
}
```

### 5.6 会话删除

**路径**: `DELETE /redfish/v1/SessionService/Sessions/{SessionId}`

```bash
curl -X DELETE \
     -H "X-Auth-Token: sess_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
     https://bmc-host/redfish/v1/SessionService/Sessions/session123
```

### 5.7 账户服务

**路径**: `/redfish/v1/AccountService/`

```json
{
    "@odata.type": "#AccountService.v1_12_0.AccountService",
    "@odata.id": "/redfish/v1/AccountService",
    "Id": "AccountService",
    "Name": "Account Service",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "ServiceEnabled": true,
    "AuthFailureLoggingThreshold": 3,
    "AccountLockoutThreshold": 5,
    "AccountLockoutDuration": 30,
    "MaxPasswordLength": 20,
    "MinPasswordLength": 8,
    "PasswordExpirationDays": 0,
    "PasswordHistoryCount": 0,
    "Accounts": {
        "@odata.id": "/redfish/v1/AccountService/Accounts"
    },
    "Roles": {
        "@odata.id": "/redfish/v1/AccountService/Roles"
    }
}
```

---

## 6. Intel OEM 扩展（redfish-intel）

### 6.1 OEM 扩展机制

Redfish 允许厂商通过 OEM 扩展添加厂商特定功能。Intel OEM 扩展路径格式：

```
/redfish/v1/UpdateService/FirmwareInventory/Intel/...
/redfish/v1/Managers/bmc/Intel/...
```

### 6.2 Intel BMC OEM 扩展

Intel 在 OpenBMC 中添加了以下 OEM 路径：

**路径**: `/redfish/v1/Managers/bmc/Intel/`

```json
{
    "@odata.type": "#Intel.Oem.Manager",
    "@odata.id": "/redfish/v1/Managers/bmc/Intel",
    "IntelV按名称": "Intel BMC Oem",
    "BiosApiVersion": "1.0.0",
    "BackupRestore": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/BackupRestore"
    },
    "BiosAttributes": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/BiosAttributes"
    },
    "BiosTechLog": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/BiosTechLog"
    },
    "Certs": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/Certs"
    },
    "HiiApi": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/HiiApi"
    },
    "OemNetworks": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/OemNetworks"
    },
    "PcieErrorInj": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/PcieErrorInj"
    },
    "SecureBoot": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/SecureBoot"
    },
    "SelLogs": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/SelLogs"
    },
    "SmBios": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/SmBios"
    },
    "SpdData": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/SpdData"
    },
    "TpmInventory": {
        "@odata.id": "/redfish/v1/Managers/bmc/Intel/TpmInventory"
    },
    "UpdateService": {
        "@odata.id": "/redfish/v1/UpdateService"
    }
}
```

### 6.3 Intel BIOS 属性扩展

**路径**: `/redfish/v1/Managers/bmc/Intel/BiosTechLog`

提供对 BIOS 技术日志的访问：

```json
{
    "@odata.type": "#Intel.Oem.BiosTechLog",
    "@odata.id": "/redfish/v1/Managers/bmc/Intel/BiosTechLog",
    "Id": "BiosTechLog",
    "Name": "BIOS Technical Log",
    "Description": "Intel BIOS Technical Support Log",
    "LogEntryType": "TechSupportLog",
    "MaxLogSize": 65536,
    "Entries": [
        {
            "EntryType": "BIOS Technical Support Log",
            "Entry": "0x01: Early Boot Failure..."
        }
    ]
}
```

### 6.4 Intel 备份恢复功能

**路径**: `/redfish/v1/Managers/bmc/Intel/BackupRestore`

```json
{
    "@odata.type": "#Intel.Oem.BackupRestore",
    "@odata.id": "/redfish/v1/Managers/bmc/Intel/BackupRestore",
    "Id": "BackupRestore",
    "Name": "Backup Restore Service",
    "Description": "BMC Configuration Backup and Restore",
    "Actions": {
        "#BackupRestore.Backup": {
            "target": "/redfish/v1/Managers/bmc/Intel/BackupRestore/Actions/Backup"
        },
        "#BackupRestore.Restore": {
            "target": "/redfish/v1/Managers/bmc/Intel/BackupRestore/Actions/Restore"
        }
    }
}
```

---

## 7. redfish-disabled 禁用特性管理

### 7.1 禁用特性机制

OpenBMC 通过 redfish-disabled 组件管理可选的 Redfish 功能启用/禁用状态。

### 7.2 禁用特性配置文件

特性开关配置位置：
- `/etc/phosphor-confd/featuremask.json`
- `/var/overload/featuremask.d/`

### 7.3 典型禁用特性

```json
{
    "features": {
        "redfish_eventing": {
            "enabled": false,
            "reason": "Not supported on this platform"
        },
        "virtual_media": {
            "enabled": true,
            "reason": ""
        },
        "account_service": {
            "enabled": true,
            "reason": ""
        },
        "session_service": {
            "enabled": true,
            "reason": ""
        },
        "update_service": {
            "enabled": true,
            "reason": ""
        },
        "TelemetryService": {
            "enabled": false,
            "reason": "Resource constraint"
        },
        "EventService": {
            "enabled": true,
            "reason": ""
        },
        "TaskService": {
            "enabled": true,
            "reason": ""
        }
    }
}
```

### 7.4 禁用特性路由处理

```cpp
class FeatureDisabledMiddleware {
public:
    crow::response handle(crow::request& req) {
        std::string path = req.url;

        // 检查路径对应的特性
        if (isFeatureDisabled(path)) {
            return crow::response(503, R"({
                "error": {
                    "code": "Base.1.0.Disabled",
                    "message": "This feature is disabled"
                }
            })");
        }
        return crow::response(200);
    }
};
```

---

## 8. 数据模型关联

### 8.1 资源层级结构

```
ServiceRoot (/redfish/v1)
├── Systems (/redfish/v1/Systems)
│   └── {system_id} - ComputerSystem
│       ├── Processors
│       ├── Memory
│       ├── Storage
│       ├── EthernetInterfaces
│       ├── LogServices
│       └── Bios
├── Chassis (/redfish/v1/Chassis)
│   └── {chassis_id} - Chassis
│       ├── Thermal
│       ├── Power
│       ├── Sensors
│       ├── NetworkAdapters
│       ├── Drives
│       └── LogServices
├── Managers (/redfish/v1/Managers)
│   └── {manager_id} - Manager
│       ├── EthernetInterfaces
│       ├── NetworkProtocol
│       ├── VirtualMedia
│       ├── LogServices
│       └── Sessions
├── AccountService (/redfish/v1/AccountService)
│   ├── Accounts
│   └── Roles
├── SessionService (/redfish/v1/SessionService)
│   └── Sessions
├── UpdateService (/redfish/v1/UpdateService)
│   ├── FirmwareInventory
│   └── SoftwareInventory
├── TaskService (/redfish/v1/TaskService)
│   └── Tasks
├── EventService (/redfish/v1/EventService)
│   └── Subscriptions
├── Registries (/redfish/v1/Registries)
└── JSONSchemas (/redfish/v1/JSONSchemas)
```

### 8.2 资源间关联（Links）

Redfish 资源通过 `Links` 属性建立关联：

```json
{
    "Links": {
        "ComputerSystems": [
            {"@odata.id": "/redfish/v1/Systems/system1"}
        ],
        "ManagedBy": [
            {"@odata.id": "/redfish/v1/Managers/bmc"}
        ],
        "ContainedBy": {
            "@odata.id": "/redfish/v1/Chassis/chassis1"
        }
    }
}
```

---

## 9. 错误处理机制

### 9.1 错误响应格式

Redfish 定义了标准错误格式：

```json
{
    "error": {
        "code": "Base.1.0.GeneralError",
        "message": "A general error occurred",
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_1_0.Message",
                "MessageId": "Base.1.0.ResourceMissing",
                "Message": "The requested resource /redfish/v1/Systems/invalid was not found.",
                "Severity": "Critical",
                "Resolution": "Provide a valid resource identifier."
            }
        ]
    }
}
```

### 9.2 HTTP 状态码映射

| HTTP 状态码 | Redfish 含义 | 使用场景 |
|------------|-------------|----------|
| 200 | OK | 成功获取资源 |
| 201 | Created | 成功创建资源（如会话） |
| 204 | No Content | 成功删除/更新 |
| 400 | Bad Request | 无效请求参数 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 已认证但无权限 |
| 404 | Not Found | 资源不存在 |
| 405 | Method Not Allowed | 不支持该 HTTP 方法 |
| 409 | Conflict | 资源状态冲突 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用（功能禁用） |

---

## 10. 知识点关联表格

| 知识点 | 分类 | 说明 | 关联文件/路径 |
|--------|------|------|---------------|
| redfish-core | 核心框架 | REST API 框架，提供路由、处理器、中间件 | lib/routes/, lib/handlers/ |
| redfish-interfaces | Schema 定义 | Redfish 资源类型和属性定义 | include/redfish-core/lib/ |
| redfish-tools | 工具集 | Schema 生成、验证工具 | tools/gen_schema.py |
| /redfish/v1/ | REST 路径 | Redfish API 服务根入口 | service_root.cpp |
| /redfish/v1/Systems | REST 路径 | 计算机系统集合 | systems.cpp |
| /redfish/v1/Chassis | REST 路径 | 机箱/主板集合 | chassis.cpp |
| /redfish/v1/Managers | REST 路径 | BMC 管理器集合 | managers.cpp |
| @odata.type | 数据模型 | 资源类型标识符 | Schema 定义 |
| @odata.id | 数据模型 | 资源导航链接 | 跨资源引用 |
| Session Token | 认证机制 | 会话令牌认证方式 | SessionService |
| X-Auth-Token | 认证机制 | HTTP 认证头 | 中间件实现 |
| Cookie/SESSIONID | 认证机制 | 基于 Cookie 的会话 | 会话管理 |
| redfish-intel | OEM 扩展 | Intel 厂商特定扩展 | Intel/Oem/ 路径 |
| redfish-disabled | 功能管理 | 特性启用/禁用管理 | featuremask.json |
| JSON Schema | 序列化 | Redfish 资源 JSON 格式验证 | validate_redfish.cpp |
| 304.0 错误码 | 错误处理 | 资源不存在错误 | error_messages.hpp |
| 503 Service Unavailable | 错误处理 | 功能被禁用错误 | middleware |
| Bootstrap | 启动流程 | REST API 服务器初始化 | main.cpp |
| Middleware Chain | 中间件 | 认证、CORS、日志中间件链 | middleware/*.cpp |
| CORS | Web 安全 | 跨域请求支持 | CORSMiddleware |
| NTP | 时间同步 | BMC NTP 配置 | Managers/{id}/NTP |
| VirtualMedia | 远程媒体 | 虚拟 CD/USB 挂载 | Managers/{id}/VirtualMedia |
| UpdateService | 固件更新 | 固件升级服务 | UpdateService/ |
| TaskService | 异步任务 | 长时间运行任务的跟踪 | TaskService/Tasks/ |
| EventService | 事件订阅 | 异步事件通知机制 | EventService/Subscriptions/ |

---

## 11. 总结

OpenBMC Redfish 接口实现是一个完整的 RESTful 管理系统，遵循 DMTF Redfish 标准规范。核心组件包括：

1. **redfish-core**：提供 HTTP 服务器、路由系统、请求处理器和中间件基础设施
2. **redfish-interfaces**：定义所有 Redfish 资源的类型和属性（Schema）
3. **redfish-tools**：提供 Schema 生成、验证和工具支持
4. **redfish-disabled**：管理可选功能的启用/禁用状态

REST API 采用分层结构，从 `/redfish/v1/` 服务根开始，通过 `@odata.id` 导航属性连接各个资源集合和单个资源。认证采用会话令牌机制，通过 `X-Auth-Token` 头或 Cookie 进行身份验证。

Intel OEM 扩展在标准 Redfish 路径基础上添加了 Intel 特定的 BIOS 管理、备份恢复、证书管理等功能。错误处理遵循 Redfish 标准格式，提供一致的错误信息结构。

---

## 参考资料

- DMTF Redfish Specification: https://www.dmtf.org/dsp/DSP0266
- OpenBMC Project: https://github.com/openbmc
- Redfish Schema: https://redfish.dmtf.org/schemas
- OpenBMC Redfish Documentation: https://github.com/openbmc/docs/tree/master/Redfish
