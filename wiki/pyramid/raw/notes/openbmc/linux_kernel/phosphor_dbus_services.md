# OpenBMC Phosphor D-Bus 服务层深度分析

## 1. 概述

OpenBMC（Open Baseboard Management Controller）是 Linux 基金会旗下的开源 BMC 固件项目，旨在为服务器和网络设备提供标准化的带外管理解决方案。OpenBMC 使用 D-Bus 作为核心的进程间通信（IPC）机制，所有服务通过 D-Bus 进行解耦通信，形成了 Phosphor 服务层架构。

**核心架构层次：**

```
客户端 (ipmitool/Redfish/REST)
         ↓
phosphor-ipmi-host (IPMI 协议栈)
         ↓
    D-Bus 总线
         ↓
传感器服务 | 电源服务 | 日志服务 | FRU 服务 | 状态管理
```

**关键组件仓库：**

| 组件 | 仓库地址 |
|------|----------|
| D-Bus 接口定义 | github.com/openbmc/phosphor-dbus-interfaces |
| sdbusplus 封装库 | github.com/openbmc/sdbusplus |
| 状态管理器 | github.com/openbmc/phosphor-state-manager |
| 日志服务 | github.com/openbmc/phosphor-logging |
| 传感器管理 | github.com/openbmc/entity-manager |
| FRU 清单 | github.com/openbmc/phosphor-fru-inventory |
| LED 管理 | github.com/openbmc/phosphor-led-manager |
| PEF 事件过滤 | github.com/openbmc/phosphor-pef |

---

## 2. D-Bus 核心概念

### 2.1 三大核心元素

**服务名（Service Name）**

格式：`xyz.openbmc_project.组件名.子组件名`

示例：
- `xyz.openbmc_project.State.Host` - 主机状态服务
- `xyz.openbmc_project.Sensor.Manager` - 传感器服务
- `xyz.openbmc_project.Logging.Manager` - 日志管理服务

**对象路径（Object Path）**

格式：`/xyz/openbmc_project/类别/子类别/实例`

示例：
- `/xyz/openbmc_project/state/host0` - 主机状态对象
- `/xyz/openbmc_project/sensors/temperature/cpu0` - CPU 温度传感器
- `/xyz/openbmc_project/inventory/system/chassis` - 系统机箱清单

**接口（Interface）**

包含方法（Methods）、属性（Properties）和信号（Signals）：

```yaml
interfaces:
  xyz.openbmc_project.Sensor.Value:
    Value:
      type: double
  xyz.openbmc_project.Sensor.Threshold.Warning:
    WarningHigh:
      type: double
```

### 2.2 数据类型映射

| D-Bus Signature | C++ 类型 |
|-----------------|----------|
| s | std::string |
| i | int32_t |
| u | uint32_t |
| b | bool |
| d | double |
| a | std::vector<std::string> |
| v | std::variant |

### 2.3 Object Mapper（对象映射器）

Object Mapper 是 OpenBMC 的服务注册中心，提供动态服务发现功能：

| 方法 | 功能 |
|------|------|
| GetObject | 查找实现特定对象路径和接口的服务 |
| GetSubTree | 在子树中查找匹配接口的所有对象/服务/接口 |
| GetSubTreePaths | 返回匹配的对象路径（不含服务信息） |
| GetAncestors | 查找实现特定接口对象的所有祖先 |

---

## 3. phosphor-state-manager（系统状态机）

### 3.1 服务概述

phosphor-state-manager 负责跟踪和控制 BMC、Chassis（机箱）和 Host（主机）的状态，是 OpenBMC 电源管理和启动序列的核心组件。

### 3.2 数据结构

**状态类型定义：**

```cpp
// BMC 状态
enum class BMCState {
    NotReady = 0,  // BMC 未就绪
    Ready = 1      // BMC 就绪
};

// 机箱电源状态
enum class PowerState {
    Off = 0,       // 电源关闭
    On = 1         // 电源开启
};

// 主机运行状态
enum class HostState {
    Off = 0,              // 主机关闭
    Running = 1,          // 主机运行中
    Quiesced = 2,         // 主机静止（等待维护）
    DiagnosticMode = 3    // 诊断模式
};
```

### 3.3 D-Bus 接口

**BMC 状态接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.State.BMC` | CurrentBMCState | 当前 BMC 状态 |
| | RequestedBMCTransition | 请求的 BMC 转换（Reboot） |

**机箱状态接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.State.Chassis` | CurrentPowerState | 当前电源状态（On/Off） |
| | RequestedPowerTransition | 请求的电源转换（On/Off） |

**主机状态接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.State.Host` | CurrentHostState | 当前主机状态 |
| | RequestedHostTransition | 请求的主机转换（On/Off/Reboot） |

### 3.4 核心源文件

| 文件 | 功能 |
|------|------|
| `bmc_state_manager.cpp/hpp` | BMC 状态管理实现 |
| `chassis_state_manager.cpp/hpp` | 机箱电源状态管理 |
| `host_state_manager.cpp/hpp` | 主机软件状态管理 |
| `discover_system_state.cpp` | 系统状态发现 |
| `host_check_main.cpp` | 主机可用性检查 |
| `systemd_target_monitor.cpp` | systemd 目标监控 |

### 3.5 调用流程

**开机流程：**

```
1. 电源开启 → 检查 pgood 值
2. 创建 /run/openbmc/chassis@0-on 文件
3. 发送命令检测主机响应
4. 主机响应 → 创建 /run/openbmc/host@0-on
5. 启动 obmc-host-start@0.target
6. 主机状态变为 Running
```

**BMC 重启恢复策略：**

```
BMC 重启时：
  - 仅在机箱和主机都关闭时执行恢复操作
  - 状态文件在电源/主机停止时删除
  - 确保状态始终反映真实硬件状态
```

### 3.6 systemd 集成

phosphor-state-manager 通过 systemd target 管理启动序列：

| Target | 功能 |
|--------|------|
| `obmc-host-start@0.target` | 启动主机 |
| `obmc-host-stop@0.target` | 停止主机 |
| `obmc-chassis-start@0.target` | 启动机箱电源 |
| `obmc-bmc-start@0.target` | 启动 BMC 服务 |

---

## 4. phosphor-log-manager（日志管理和 SEL）

### 4.1 服务概述

phosphor-log-manager 是 OpenBMC 的中央日志服务，负责收集、存储和管理系统事件日志，同时支持 IPMI SEL（System Event Log）规范。

### 4.2 核心接口

**日志创建接口：**

| 接口 | 方法 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Logging.Create` | Create | 创建新日志条目 |
| `xyz.openc_project.Logging.Manager` | Clear | 清空所有日志 |
| | Delete | 删除指定日志 |

**日志属性：**

```yaml
xyz.openbmc_project.Logging.Entry:
  Id: uint32_t           # 日志唯一 ID
  Timestamp: uint64_t    # 时间戳（毫秒）
  Severity: string       # 严重级别 (Critical/Warning/Info)
  Message: string         # 日志消息
  AdditionalData: vector<string>  # 附加数据
```

### 4.3 日志严重级别

| 级别 | 值 | 说明 |
|------|-----|------|
| Emergency | 0 | 系统不可用 |
| Alert | 1 | 需要立即处理 |
| Critical | 2 | 临界条件 |
| Error | 3 | 错误条件 |
| Warning | 4 | 警告条件 |
| Notice | 5 | 正常但重要 |
| Info | 6 | 信息性消息 |
| Debug | 7 | 调试级别 |

### 4.4 phosphor-sel-logger 集成

phosphor-sel-logger 是 SEL 专用日志记录器：

```cpp
// 关键方法
IpmiSelAdd()  // 添加 IPMI SEL 记录

// 日志标识
MESSAGE_ID = "b370836ccf2f4850ac5bee185b77893a"

// 元数据字段
IPMI_SEL_RECORD_ID = Two byte unique SEL record identifier
```

### 4.5 调用流程

```
1. 事件源（传感器/服务）通过 D-Bus 发送信号
2. phosphor-sel-logger 接收 IPMI SEL 事件
3. 转换为标准日志格式
4. 转发至 phosphor-log-manager
5. 存储至 journal（日志系统）
6. Redfish/IPMI 可查询日志
```

### 4.6 架构设计

```
+-------------+     +------------------+     +--------------------+
| 传感器事件   | --> | phosphor-sel-log  | --> | phosphor-logging   |
+-------------+     +------------------+     +--------------------+
                           |                         |
                           v                         v
                    /run/systemd/journal    /xyz/openbmc_project/Logging
```

---

## 5. phosphor-inventory-manager（清单管理）

### 5.1 服务概述

phosphor-inventory-manager 负责管理系统硬件清单信息，包括 FRU（现场可替换单元）和资产信息，是 OpenBMC 硬件抽象层的核心组件。

### 5.2 核心接口

**清单项接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Inventory.Item` | PrettyName | 可读名称 |
| | FRU | FRU 信息对象 |
| `xyz.openbmc_project.Inventory.FRU` | SerialNumber | 序列号 |
| | Model | 型号 |
| | Manufacturer | 制造商 |
| | PartNumber | 零件号 |

**资产标签接口：**

```yaml
xyz.openbmc_project.Inventory.Item.AssetTag:
  AssetTag:
    type: string
    description: "资产标签"
```

### 5.3 对象路径结构

```
/xyz/openbmc_project/inventory/
  system/
    chassis/              # 系统机箱
    mainboard/            # 主板
  cards/
    gpu0/                 # GPU 卡 0
    gpu1/                 # GPU 卡 1
  psus/
    psu0/                 # 电源单元 0
  sensors/
    temp/                 # 温度传感器
```

### 5.4 核心数据结构

```cpp
// 清单项基类
class InventoryItem {
    std::string objectPath;     // 对象路径
    std::string prettyName;     // 显示名称
    std::string present;        // 在位状态
    FRUInfo fruInfo;            // FRU 信息
};

// FRU 信息结构
struct FRUInfo {
    std::string serialNumber;
    std::string model;
    std::string manufacturer;
    std::string partNumber;
    std::string FruDevice;      // FRU 设备路径
};
```

### 5.5 YAML 配置格式

```yaml
# inventory.yaml 示例
- name: system/chassis
  interfaces:
    xyz.openbmc_project.Inventory.Item:
      PrettyName:
        type: string
        default: "System Chassis"
    xyz.openbmc_project.Inventory.FRU:
      SerialNumber:
        type: string
      Model:
        type: string
```

### 5.6 调用流程

```
1. 启动时扫描配置的 FRU 设备
2. 通过 I2C/SMBus 读取 FRU 存储
3. 创建对应的 D-Bus 对象路径
4. 填充 FRU 信息属性
5. 注册到 Object Mapper
6. 供 Redfish/IPMI 查询
```

---

## 6. phosphor-sensor-manager（传感器管理）

### 6.1 服务概述

phosphor-sensor-manager 负责管理和暴露系统传感器数据，支持 IPMI SDR（Sensor Data Record）规范，是硬件监控数据的中枢。

### 6.2 核心接口

**传感器值接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Sensor.Value` | Value | 当前传感器值 |
| | Unit | 单位 |
| | Scale | 缩放因子 |
| `xyz.openbmc_project.Sensor.Threshold.Warning` | WarningHigh | 警告上限 |
| | WarningLow | 警告下限 |
| `xyz.openbmc_project.Sensor.Threshold.Critical` | CriticalHigh | 临界上限 |
| | CriticalLow | 临界下限 |

**传感器单位枚举：**

| 单位 | D-Bus 路径 |
|------|------------|
| Volts | `xyz.openbmc_project.Sensor.Value.Unit.Volts` |
| Amperes | `xyz.openbmc_project.Sensor.Value.Unit.Amperes` |
| Watts | `xyz.openbmc_project.Sensor.Value.Unit.Watts` |
| Celsius | `xyz.openbmc_project.Sensor.Value.Unit.Celsius` |
| RPM | `xyz.openbmc_project.Sensor.Value.Unit.RPM` |

### 6.3 sensor.yaml 配置结构

```yaml
PSU_VIN:                          # 传感器名称
  SensorNumber: 153               # IPMI SDR 传感器号
  interfaces:
    xyz.openbmc_project.Sensor.Value:
      Value:
        type: double
  multiplierM: 55                  # 乘数因子
  offsetB: 0                      # 偏移量
  bExp: 0                         # B 指数
  rExp: -3                        # R 指数
  path: /xyz/openbmc_project/sensors/voltage/PSU_VIN
  sensorType: 0x02                # IPMI 传感器类型
  unit: xyz.openbmc_project.Sensor.Value.Unit.Volts
```

### 6.4 数值转换公式

```
IPMI 值 = (Raw × multiplierM × 10^rExp) + offsetB
```

### 6.5 SDR 传感器类型

| sensorType | 类型 | 说明 |
|-----------|------|------|
| 0x01 | Temperature | 温度传感器 |
| 0x02 | Voltage | 电压传感器 |
| 0x03 | Current | 电流传感器 |
| 0x04 | Fan | 风扇传感器 |
| 0x06 | Power Supply | 电源传感器 |
| 0x07 | Power Unit | 电源单元 |
| 0x0C | Processor | 处理器 |
| 0x21 | Memory | 内存 |

### 6.6 调用流程

```
1. entity-manager 读取 sensor.yaml 配置
2. 根据配置初始化传感器设备（I2C/ADC/HWMon）
3. 创建 D-Bus 对象路径
4. 定期读取传感器原始值
5. 应用转换公式得到实际值
6. 更新 D-Bus 属性
7. 超过阈值时发送事件信号
```

---

## 7. phosphor-fru-inventory（FRU 设备管理）

### 7.1 服务概述

phosphor-fru-inventory 专门负责管理 FRU（Field Replaceable Unit）设备，支持 IPMI FRU 规范，提供 FRU 信息存储和读取功能。

### 7.2 核心接口

**FRU 设备接口：**

| 接口 | 方法 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Fru.Device` | Read | 读取 FRU 存储 |
| | Write | 写入 FRU 存储 |
| | ReadData | 读取 FRU 数据 |

**FRU 清单接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Fru.Inventory` | ChassisType | 机箱类型 |
| | BoardMfgDate | 板卡制造日期 |
| | BoardSerial | 板卡序列号 |

### 7.3 FRU 存储格式

IPMI FRU 信息存储在 EEPROM 中，格式如下：

| 区域 | 内容 |
|------|------|
| Common Header | 版本、长度、校验 |
| Board Area | 板卡信息（制造商、序列号、型号等） |
| Product Area | 产品信息 |
| Chassis Area | 机箱信息 |

### 7.4 YAML 配置示例

```yaml
# fru_config.yaml
- name: baseboard
  FruDevice: /dev/i2c-0
  ReadOnly: false
  fields:
    Board Manufacturer:
      type: string
      offset: 0x46
      length: 8
    Board Product Name:
      type: string
      offset: 0x56
      length: 32
    Board Serial:
      type: string
      offset: 0x76
      length: 12
```

### 7.5 调用流程

```
1. 启动时扫描配置的 FRU 设备
2. 打开 I2C 连接
3. 读取 FRU EEPROM 内容
4. 解析 FRU 格式（Common Header → Board Area → Product Area）
5. 创建 D-Bus 对象暴露数据
6. 注册到 Object Mapper
7. 供 IPMI/Redfish 查询
```

### 7.6 生成代码机制

```bash
# 编译阶段执行 fru_gen.py
python3 fru_gen.py fru_config.yaml → fru-read-gen.cpp
```

生成的代码包含：
- FRU 读取接口实现
- D-Bus 对象创建代码
- 属性填充逻辑

---

## 8. phosphor-led-manager（LED 控制）

### 8.1 服务概述

phosphor-led-manager 负责管理系统 LED 指示灯，支持 LED 组控制和单 LED 控制，是前面板状态指示和故障报警的核心组件。

### 8.2 核心接口

**LED 接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Led.Physical` | State | LED 物理状态 |
| | Asserted | 是否点亮 |
| `xyz.openbmc_project.Led.Group` | Asserted | 组断言状态 |
| | DelayRemaining | 剩余延迟时间 |

**LED 组管理器接口：**

| 接口 | 方法 | 说明 |
|------|------|------|
| `xyz.openbmc_project.Led.GroupManager` | GetLedGroups | 获取所有 LED 组 |

### 8.3 对象路径结构

```
/xyz/openbmc_project/Led/Groups/
  enclosure_identify          # 机箱定位 LED
  front_panel_id              # 前面板 ID
  sad_led                     # 系统警报面板 LED
/xyz/openbmc_project/Led/Physical/
  bmc_led0                    # BMC LED 0
  chassis_led0                # 机箱 LED 0
```

### 8.4 LED 状态枚举

| 状态 | 值 | 说明 |
|------|-----|------|
| LED_OFF | 0 | LED 熄灭 |
| LED_DEFAULT | 1 | 默认状态 |
| LED_BLINK | 2 | LED 闪烁 |

### 8.5 核心实现

```cpp
// LED 组控制
class Group {
    bool asserted() const;           // 获取断言状态
    bool asserted(bool value);       // 设置断言状态

    // 优化：如果值未变化则立即返回
    bool assertedImpl(bool value) {
        if (value == sdbusplus::xyz::openbmc_project::Led::server::Group::asserted()) {
            return value;  // 提前返回
        }
        // 执行实际设置
        return setLedState(value);
    }
};
```

### 8.6 调用流程

```
1. Redfish/IPMI 请求设置 LED 状态
2. phosphor-led-manager 接收请求
3. 检查当前状态（优化：避免无谓操作）
4. 更新 D-Bus 属性
5. 调用底层 GPIO/硬件接口
6. 发送属性变更信号
7. LED 硬件执行状态变化
```

---

## 9. phosphor-pef（事件过滤）

### 9.1 服务概述

phosphor-pef（Platform Event Filter）负责处理和过滤平台事件，支持事件告警策略，是 IPMI 告警和事件路由的核心组件。

### 9.2 核心接口

**PEF 配置接口：**

| 接口 | 属性 | 说明 |
|------|------|------|
| `xyz.openbmc_project.PEF.Policy` | Name | 策略名称 |
| | Enabled | 是否启用 |
| | FilterRules | 过滤规则 |
| | Actions | 触发动作 |
| `xyz.openbmc_project.PEF.Settings` | PEFEnabled | 全局 PEF 开关 |
| | EventFilterCount | 事件过滤器数量 |

### 9.3 过滤规则

```yaml
FilterRules:
  - SensorType: Temperature       # 传感器类型
    SensorNumber: 0x01            # 传感器编号
    EventSeverity: Critical       # 事件严重级别
    EventDirection: Assertion     # 事件方向
```

### 9.4 告警动作

| 动作 | 值 | 说明 |
|------|-----|------|
| OEM | 0x80 | OEM 特定动作 |
| PET | 0x40 | 发送 SNMP PET 陷阱 |
| GSM | 0x20 | 全球告警 |
| LAN | 0x10 | LAN 告警 |
| Email | 0x08 | 邮件告警 |
| Log | 0x01 | 记录日志 |

### 9.5 调用流程

```
1. 事件源发送 D-Bus 信号
2. phosphor-pef 接收事件
3. 匹配过滤策略（EventFilterTable）
4. 检查事件方向和严重级别
5. 执行配置的告警动作
6. 发送告警到目标（LAN/GSM/PET）
7. 记录事件到 SEL
```

---

## 10. 知识点关联表

| 服务组件 | D-Bus 服务名 | 对象路径前缀 | 核心接口 | 依赖组件 | IPMI 对应功能 |
|----------|-------------|-------------|----------|----------|--------------|
| phosphor-state-manager | `xyz.openbmc_project.State` | `/xyz/openbmc_project/state/` | `State.BMC/Host/Chassis` | systemd | 系统状态 |
| phosphor-log-manager | `xyz.openbmc_project.Logging` | `/xyz/openbmc_project/Logging/` | `Manager/Entry/Create` | systemd-journald | SEL |
| phosphor-inventory-manager | `xyz.openbmc_project.Inventory` | `/xyz/openbmc_project/inventory/` | `Item/FRU/AssetTag` | ObjectMapper | FRU 清单 |
| phosphor-sensor-manager | `xyz.openbmc_project.Sensor` | `/xyz/openbmc_project/sensors/` | `Value/Threshold.*` | entity-manager | SDR |
| phosphor-fru-inventory | `xyz.openbmc_project.Fru` | `/xyz/openbmc_project/Fru/` | `Device/Inventory` | I2C/SMBus | FRU 设备 |
| phosphor-led-manager | `xyz.openbmc_project.Led` | `/xyz/openbmc_project/Led/` | `Physical/Group/GroupManager` | GPIO | LED 控制 |
| phosphor-pef | `xyz.openbmc_project.PEF` | `/xyz/openbmc_project/PEF/` | `Policy/Settings` | phosphor-log-manager | 事件过滤 |

### 10.1 服务间依赖关系

```
                    +---------------------+
                    |  phosphor-state-    |
                    |     manager         |
                    +----------+----------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
   +----------------+  +---------------+  +---------------+
   | chassis_power  |  | host_state    |  | bmc_state    |
   +----------------+  +---------------+  +---------------+
                               |
                               v
                    +---------------------+
                    |  phosphor-sensor-   |
                    |     manager         |
                    +----------+----------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
   +----------------+  +---------------+  +---------------+
   | entity-manager |  | phosphor-fru- |  | phosphor-led- |
   |                |  | inventory    |  | manager       |
   +----------------+  +---------------+  +---------------+
            |                  |                  |
            +------------------+------------------+
                               |
                               v
                    +---------------------+
                    |  phosphor-log-      |
                    |     manager         |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |   phosphor-pef      |
                    +---------------------+
```

### 10.2 外部访问路径

| 访问方式 | 路径 | 对应服务 |
|----------|------|----------|
| IPMI | IPMB/LAN | phosphor-ipmi-host |
| Redfish | HTTPS REST API | phosphor-rest-dbus |
| SSH | CLI | phosphor-obmc-console |
| D-Bus | System Bus | 各 phosphor-* 服务 |

---

## 11. 开发实践要点

### 11.1 sdbusplus 开发流程

```bash
# 1. 定义 YAML 接口（phosphor-dbus-interfaces）
vim yaml/xyz/openbmc_project/Example/Demo.interface.yaml

# 2. 生成 C++ 代码
sdbusplus-tool generate interface yaml/xyz/openbmc_project/Example/Demo.interface.yaml

# 3. 实现服务端
class Demo : public sdbusplus::xyz::openbmc_project::Example::server::Demo {
    int myMethod(int arg) override;
};

# 4. 注册服务
bus.request_name("xyz.openbmc_project.Example");
```

### 11.2 常用调试命令

```bash
# 列出所有服务
busctl list

# 查看对象树
busctl tree xyz.openbmc_project.State.Host

# 查看接口详情
busctl introspect xyz.openbmc_project.State.Host /xyz/openbmc_project/state/host0

# 调用方法
busctl call xyz.openbmc_project.State.Host /xyz/openbmc_project/state/host0 \
    xyz.openbmc_project.State.Host RequestedHostTransition s 1

# 读取属性
busctl get-property xyz.openbmc_project.Sensor.Value /xyz/openbmc_project/sensors/temperature/cpu0 \
    xyz.openbmc_project.Sensor.Value Value

# 监控 D-Bus 消息
busctl monitor
```

### 11.3 Object Mapper 使用

```cpp
// 查找服务
auto service = objmap.getService("xyz.openbmc_project.State.Host",
                                  "/xyz/openbmc_project/state/host0");

// 获取子树
auto subtree = objmap.getSubTree("/xyz/openbmc_project/sensors/",
                                  0,  // 深度限制
                                  "xyz.openbmc_project.Sensor.Value");
```

---

## 12. 总结

OpenBMC Phosphor D-Bus 服务层构成了现代 BMC 固件的基础架构，通过标准化的 D-Bus 接口实现了服务间的解耦通信。本文分析的七个核心服务覆盖了系统状态管理、日志记录、硬件清单、传感器监控、FRU 设备管理、LED 控制和事件过滤等关键功能模块。

这些服务共同构成了一个完整的带外管理系统，支持 IPMI、Redfish 等标准管理协议，为数据中心服务器提供了灵活、可扩展的硬件管理能力。理解这些服务的架构设计和实现细节，对于 OpenBMC 开发者和系统集成工程师至关重要。
