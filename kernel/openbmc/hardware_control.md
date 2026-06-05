# OpenBMC 硬件控制子系统深度分析

## 概述

OpenBMC（Open Baseboard Management Controller）是 Linux 基金会旗下的开源项目，旨在为 BMC（基板管理控制器）固件提供一套完整的开源软件栈。OpenBMC 硬件控制子系统是整个管理系统中最核心的部分，负责服务器物理层面的监控、控制与告警管理。这些子系统通过 D-Bus 总线进行进程间通信，采用事件驱动的架构模式，实现了电源管理、风扇控制、热管理、LED 指示和看门狗监控等关键功能。

在 OpenBMC 架构中，硬件控制子系统位于中间层位置，上层对接 Redfish/IPMI/REST 等管理接口，下层直接与 Linux 内核和硬件抽象层交互。Phosphor 框架是 OpenBMC 的核心开发框架，提供了标准化的事件处理、对象管理和服务注册机制。所有硬件控制服务都遵循统一的设计模式：读取传感器数据、执行控制逻辑、发布 D-Bus 属性变更、记录事件日志。

---

## 一、phosphor-powerd 电源控制子系统

### 1.1 架构概述

phosphor-powerd 是 OpenBMC 电源管理的核心守护进程，负责服务器的电源开/关/重启/复位控制以及电源状态监控。该子系统采用模块化设计，将不同类型的电源设备（电源模块、电源冗余组、电源 sequencer）分解为独立的应用程序，通过 D-Bus 进行协调控制。

电源控制架构分为三个主要层次。第一层是硬件抽象层，通过 sysfs 和 HWMON（硬件监控接口）与底层电源硬件通信，支持 PMBus 协议访问电源模块的电压、电流、功率等参数。第二层是 D-Bus 接口层，暴露标准化的电源管理对象路径和属性接口，如 `/xyz/openbmc_project/state/chassis0` 等。第三层是应用逻辑层，实现具体的电源控制策略，如冷冗余（Cold Redundancy）管理和上电时序控制。

### 1.2 核心组件

**phosphor-chassis-power** 是多机箱电源监控模块，专注于 chassis 级别的电源故障检测和恢复。该模块受 JSON 配置文件驱动，配置文件指定了需要监控的电源输入、输出状态以及故障处理策略。当检测到电源故障时，模块会自动触发预定义的恢复动作序列，包括告警上报、事件记录和可能的系统降级运行。

**phosphor-power-sequencer** 负责机箱上电和下电的顺序控制。电源时序控制是服务器硬件安全的关键环节，必须严格按照规定的顺序打开或关闭各路电源，避免因电压毛刺或浪涌导致硬件损坏。sequencer 模块读取 JSON 配置文件中定义的时序参数，通过 GPIO 或 I2C 控制电源 rail 的开关时延。

**phosphor-power-supply** 是新一代电源供应器监控模块，支持更高级的电源状态轮询和故障预测功能。该模块通过 `xyz.openbmc_project.Inventory.Decorator.Asset` 接口与 FRU（现场可替换单元）库存系统集成，读取电源模块的序列号、型号和制造商信息。

**cold-redundancy** 模块专门管理电源供应器的冷冗余模式。在冷冗余配置中，多个电源模块同时工作但负载不均衡，当主电源模块故障时，备用模块立即接管全部负载。cold-redundancy 模块还支持定期轮换主电源角色，以均衡各模块的使用时长。

### 1.3 D-Bus 接口定义

电源控制的主要 D-Bus 接口包括 `xyz.openbmc_project.State.Chassis` 用于机箱电源状态控制，`xyz.openbmc_project.Control.Power` 用于电源策略管理。典型的对象路径如 `/xyz/openbmc_project/state/chassis0` 表示主机箱的电源状态对象。

属性接口定义了 `CurrentPowerState`（当前电源状态：on/off/standby）、`RequestedPowerState`（请求的电源状态）以及 `PowerUpTimeout`（上电超时时间）等关键参数。控制接口则提供 `PowerOn`、`PowerOff`、`PowerReset`、`GracefulShutdown` 等方法调用。

### 1.4 控制流程与状态机

电源状态机定义了从硬件初始化到稳定运行的完整生命周期。机箱电源状态转换包括 `Off`（关机）-> `On`（开机）-> `Running`（运行）以及反向的 `Running` -> `Off`。每个状态转换都伴随着超时检测和错误处理机制。

电源控制的核心流程如下：当收到开机请求时，首先检查硬件安全条件（电源模块电压稳定、风扇运转正常），然后按照配置的时序打开各路电源 rail，系统完成 POST（开机自检）后进入运行状态。关机流程则先通知操作系统进行优雅关闭，超时后强制切断电源。

---

## 二、phosphor-fan-presence 风扇存在检测和控制

### 2.1 架构概述

phosphor-fan-presence 实现了风扇模组的存在检测和基础控制功能，是 OpenBMC 热管理系统的最前端模块。该子系统采用事件驱动的架构，通过监听 GPIO 电平变化或 tach 反馈信号来检测风扇的插入和拔出事件，并更新 inventory 系统中的风扇存在状态。

fan-presence 架构的核心设计理念是解耦和可配置。解耦体现在存在检测逻辑与具体硬件平台无关，通过 JSON 配置适配不同服务器主板的 GPIO 布局和传感器布局。可配置体现在检测阈值、去抖动时间、事件响应动作都可以通过配置文件调整，无需修改代码。

### 2.2 核心组件

**Fan Presence Detection** 是存在检测模块，监听风扇模块的 GPIO 引脚电平变化。当检测到从「插入」变为「拔出」或反向变化时，模块会通过 D-Bus 更新对应 inventory 对象的 `Present` 属性，同时发布 PropertyChanged 信号通知其他订阅服务。

**Fan Monitoring** 是功能状态监控模块，持续检测风扇转速是否在正常范围内。每个风扇对象都有 `Functional` 属性，当转速低于最低阈值或检测到卡转故障时，该属性被设为 false。模块还会在检测到风扇故障时触发系统保护动作，如强制关机或降频运行。

**Cooling Type** 冷却类型检测模块通过 GPIO 或其他硬件接口判断系统使用的是风冷还是水冷散热。这一信息对于后续的热管理策略选择至关重要，水冷系统的风扇转速调节曲线与风冷系统有明显差异。

### 2.3 D-Bus 接口与对象结构

风扇相关的 D-Bus 接口主要位于 `/xyz/openbmc_project/inventory/system/chassis` 路径下，每个风扇单元对应一个子路径。风扇对象实现了 `xyz.openbmc_project.Inventory.Item` 接口，提供 `Present` 和 `Functional` 两个关键布尔属性。

```yaml
接口: xyz.openbmc_project.Inventory.Item.Fan
路径: /xyz/openbmc_project/inventory/system/chassis/fan0
属性:
  - Present: boolean  # 风扇是否物理存在
  - Functional: boolean  # 风扇是否正常工作
```

### 2.4 配置方式

系统使用 JSON 格式的配置文件定义风扇布局和检测参数。配置文件中指定每个风扇的 GPIO 编号、检测方向（高电平有效/低电平有效）、去抖动时间窗口等。JSON 配置方式已取代早期 YAML 配置文件，成为推荐的配置方法。

---

## 三、phosphor-thermal 温度监控和风扇转速调节

### 3.1 架构概述

phosphor-thermal 是 OpenBMC 热管理的核心子系统，负责收集温度传感器数据、计算热区域状态、调节风扇转速以维持系统温度在安全范围内。thermal 子系统的设计借鉴了工业控制领域的 PID（比例-积分-微分）控制理论，通过闭环反馈实现精确的温度管理。

thermal 架构采用分层设计。最底层是传感器接口层，负责从 HWMON 或其他内核接口读取温度数据。中间层是策略计算层，运行 PID 或步进控制算法，根据当前温度与目标温度的偏差计算所需的散热量。最上层是执行器接口层，将控制输出转换为 PWM 占空比或风扇目标转速值，写入硬件控制器。

### 3.2 核心组件

**phosphor-pid-control** 是 PID 闭环控制模块，实现了工业标准的 PID 控制算法。该模块支持单传感器单执行器的简单配置，也支持多传感器聚合输入、多执行器协同输出的复杂配置。PID 参数（比例系数、积分时间、微分时间）可通过 JSON 配置文件调整，以适应不同散热需求。

**Stepwise** 步进控制模块是 PID 控制的一种简化替代方案，适用于散热需求相对简单的场景。步进控制将温度范围划分为多个区间，每个区间对应一个固定的风扇转速。这种方式计算开销小，响应速度快，但控制精度不如 PID。

**Thermal Zone** 热区管理模块负责将系统划分为多个热区，每个热区包含若干温度传感器和风扇。典型的服务器可能划分为 CPU 热区、内存热区、GPU 热区等，不同热区可以有不同的目标温度和散热优先级。

### 3.3 JSON 配置规范

thermal 子系统的配置文件位于 `/usr/share/swampd/config.json`，包含 sensors 和 zones 两个顶层字段。sensors 数组定义每个传感器的基本信息：

```json
{
  "sensors": [
    {
      "name": "fan1",
      "type": "fan",
      "readPath": "/xyz/openbmc_project/sensors/fan_tach/fan1",
      "writePath": "/sys/devices/platform/ahb:apb/1e786000.pwm-tacho-controller/hwmon/**/pwm1",
      "min": 0,
      "max": 255,
      "ignoreDbusMinMax": true
    }
  ],
  "zones": [
    {
      "name": "system_zone",
      "sensors": ["temp1", "temp2"],
      "fans": ["fan1", "fan2"],
      "targetTemperature": 45
    }
  ]
}
```

### 3.4 控制流程

温度控制的主循环流程如下：首先读取所有相关温度传感器的当前值，计算加权平均温度或取最大值作为热区当前温度。然后将当前温度与目标温度进行比较，计算温度偏差。PID 控制器根据偏差值和控制参数计算输出值，最后将输出值转换为 PWM 占空比写入风扇控制器。

在自动调节模式下，系统会周期性地调整风扇转速以响应温度变化。调整幅度受限于「变化率限制」，防止风扇转速剧烈波动产生噪声或机械磨损。当温度持续超过警告阈值时，系统会记录事件日志并可能触发降频或关机保护。

---

## 四、phosphor-led-manager LED 指示灯控制

### 4.1 架构概述

phosphor-led-manager 负责管理系统面板上的 LED 指示灯，通过不同的灯光模式（常亮、闪烁、熄灭）组合来指示系统状态。在服务器系统中，LED 是最直观的状态展示方式，运维人员可以通过前面板的 LED 快速判断服务器的运行状况和故障类型。

LED 管理的核心挑战在于解决多任务请求冲突问题。系统中可能有多个应用需要同时控制同一个 LED，例如故障管理程序需要将故障 LED 点亮为红色常亮，而标识程序需要将定位 LED 点亮为蓝色闪烁。LED manager 通过优先级机制解决这一冲突，高优先级的请求会覆盖低优先级的请求。

### 4.2 核心组件

**Manager** 是 LED 管理的核心服务，运行在 systemd 环境下，作为 D-Bus service 暴露 LED 组控制接口。Manager 加载时读取 JSON 配置文件，构建 LED 组和成员的层级关系，并注册到 D-Bus 总线供外部调用。

**fault-monitor** 是故障监控模块，订阅系统故障事件并自动控制相关 LED。当检测到电源故障、风扇故障、温度过高等事件时，fault-monitor 会自动 assert 对应的 LED 组，将故障状态通过 LED 展示出来。

### 4.3 D-Bus 接口定义

LED 组在 D-Bus 上的路径为 `/xyz/openbmc_project/led/groups/<group_name>`，如 `/xyz/openbmc_project/led/groups/enclosure_identify` 表示机箱定位 LED 组。

```yaml
接口: xyz.openbmc_project.Led.Group
路径: /xyz/openbmc_project/led/groups/<group_name>
属性:
  - Asserted: boolean  # LED 组是否被激活

方法:
  - Log()  # 记录 LED 状态变更到事件日志
```

LED 物理控制则通过 `xyz.openbmc_project.Led.Physical` 接口与 phosphor-led-sysfs 协作，将软件层的 LED 状态转换为实际硬件的 GPIO 控制。

### 4.4 优先级机制

LED 优先级机制确保多个请求同时发生时，系统能够做出确定性的响应。每个 LED 可以配置三种优先级状态：On（点亮优先级）、Blink（闪烁优先级）、Off（熄灭优先级）。当一个组请求 LED 处于某一状态时，只有当请求的优先级高于 LED 当前状态优先级时，更改才会生效。

组优先级是可选的，当多个组同时 assert 同一 LED 时，具有最高组优先级的组的请求会被采纳。这一机制确保了关键状态（如故障）始终能够正确显示。

### 4.5 配置格式

JSON 配置文件定义 LED 组的成员、默认状态和优先级：

```json
{
  "name": "enclosure_identify",
  "leds": [
    {"name": "identify_blue", "path": "/sys/class/leds/enclosure_blue"}
  ],
  "priority": {
    "On": 10,
    "Blink": 5,
    "Off": 0
  }
}
```

---

## 五、phosphor-watchdog 看门狗服务

### 5.1 架构概述

phosphor-watchdog 实现了标准的看门狗定时器功能，用于检测和恢复系统软件故障。看门狗是服务器系统可靠性的重要保障，当主系统（操作系统或应用程序）发生死锁或停止响应时，看门狗能够自动触发系统复位，将服务器恢复到已知的正常状态。

watchdog 子系统在 OpenBMC 中扮演双重角色：一方面它作为 BMC 固件的一部分运行，监控 BMC 自身应用程序的运行状态；另一方面它也通过 IPMI watchdog 命令接受主机系统的监控请求。

### 5.2 D-Bus 接口

watchdog 服务暴露的 D-Bus 接口为 `xyz.openbmc_project.Watchdog`，对象路径为 `/xyz/openbmc_project/watchdog/host0`。

```yaml
接口: xyz.openbmc_project.Watchdog
属性:
  - Enabled: boolean  # 看门狗是否启用
  - TimeRemaining: uint32  # 剩余时间（毫秒）
  - Timeout: uint32  # 超时时间（毫秒）
  - TimerAction: enum  # 超时动作（reset/power_off/restart）

方法:
  - Reset()  # 重置看门狗计时器（喂狗）
  - Stop()   # 停止看门狗
  - Start()  # 启动看门狗
```

### 5.3 工作模式

watchdog 支持多种工作模式，通过 TimerAction 属性配置。`Reset` 模式会在超时时仅重启主机操作系统；`PowerOff` 模式会切断主机电源；`Restart` 模式会发送完整的重启序列。默认的超时时间通常设置为 60 秒，给予操作系统足够的时间完成优雅关机。

watchdog 的操作遵循状态机逻辑：初始为 Stopped 状态，调用 Start 方法后进入 Running 状态，计时器倒数至零时触发配置的动作，然后根据 TimerState 判断是否需要返回 Stopped 状态或保持触发后的状态。

### 5.4 与 IPMI 集成

watchdog 服务与 IPMI 协议深度集成，支持标准的 IPMI watchdog 命令。外部管理程序可以通过 IPMI 接口查询看门狗状态、设置超时参数、启动/停止看门狗等。这一集成使得 OpenBMC 能够同时被传统 IPMI 工具和现代 Redfish/REST API 管理。

---

## 六、PEL 平台事件日志

### 6.1 概述

PEL（Platform Event Log）是 OpenBMC 新一代的事件日志格式，用于记录系统和硬件的重要事件。与传统的 SEL（System Event Log）相比，PEL 采用了更灵活、更结构化的数据组织方式，能够表达更丰富的事件语义和关联信息。

PEL 的设计目标包括：支持事件优先级和分类、支持事件关联追踪（一个故障可能引发多个相关事件）、支持事件数据的标准化编码、提供更好的可扩展性以适应未来事件类型。

### 6.2 事件数据结构

PEL 事件由多个 Section 组成，每个 Section 包含不同类别的信息：

**头部 Section** 包含事件元数据：事件ID（唯一标识符）、事件时间戳、事件版本号、生成事件的服务名称。

**传感器数据 Section** 记录与事件相关的传感器信息：传感器类型、传感器编号、事件触发时的传感器读数、传感器阈值状态。

**事件数据 Section** 包含事件特有的扩展信息：事件类ID、事件子类、具体的错误代码、附加的描述性数据。

### 6.3 事件优先级

PEL 定义了四个事件优先级级别，从高到低依次为：

| 优先级 | 名称 | 说明 | 典型用途 |
|--------|------|------|----------|
| 0 | Critical | 严重故障 | 电源故障、硬件过热 |
| 1 | Warning | 警告 | 温度偏高、风扇转速低 |
| 2 | Info | 信息 | 状态变更、配置更新 |
| 3 | Debug | 调试 | 详细诊断信息 |

### 6.4 phosphor-logging 与 PEL

phosphor-logging 是 OpenBMC 的日志管理服务，负责接收、整理和持久化 PEL 事件。该服务通过 D-Bus 与各个硬件管理子系统集成，当子系统检测到需要记录的事件时，调用 logging 服务的接口提交 PEL 条目。

```yaml
接口: xyz.openbmc_project.Logging.Service
路径: /xyz/openbmc_project/logging
方法:
  - Create(critical|warning|info|debug, message, additionalData)
  - Clear()
  - Delete(EntryId)

路径: /xyz/openbmc_project/logging/entry/<id>
属性:
  - Severity: string  # 优先级
  - Message: string   # 事件消息
  - Timestamp: uint64 # Unix 时间戳
  - AdditionalData: vector<string> # 扩展数据
```

logging 服务将 PEL 条目存储在持久化存储（UBI 或文件系统）中，并通过 REST API 和 Redfish 接口向上层管理平面提供查询接口。事件日志的保留策略可通过配置调整，通常 Critical 级别的事件会永久保留，而 Debug 级别的事件在达到存储上限后会被自动清理。

---

## 七、知识关联表格

| 子系统名称 | 主要职责 | 核心进程/服务 | 关键 D-Bus 接口 | 配置文件路径 | 依赖的硬件接口 |
|-----------|---------|--------------|----------------|-------------|---------------|
| phosphor-powerd | 电源开/关/重启控制 | phosphor-chassis-power, phosphor-power-sequencer | xyz.openbmc_project.State.Chassis | JSON 配置 | GPIO, I2C/PMBus |
| phosphor-fan-presence | 风扇存在检测 | fan-presence-detect, fan-monitor | xyz.openbmc_project.Inventory.Item.Fan | JSON 配置 | GPIO, tach 反馈 |
| phosphor-thermal | 温度监控与风扇调速 | phosphor-pid-control, swampd | xyz.openbmc_project.Control.Thermal | /usr/share/swampd/config.json | HWMON, PWM |
| phosphor-led-manager | LED 指示灯控制 | led-group-manager | xyz.openbmc_project.Led.Group | JSON 配置 | GPIO, LED 控制器 |
| phosphor-watchdog | 看门狗定时器 | watchdogd | xyz.openbmc_project.Watchdog | 无 | 硬件看门狗定时器 |
| phosphor-logging | 事件日志管理 | phosphor-logging | xyz.openbmc_project.Logging | 日志存储配置 | 持久化存储 |

### 子系统间依赖关系

```
phosphor-logging (日志记录)
       ^
       | 记录事件
       |
phosphor-powerd -----> phosphor-fan-presence
       |                        |
       | 电源状态影响           | 风扇状态影响
       v                        v
phosphor-thermal <------------+
       |
       | 温度触发
       v
phosphor-led-manager (LED 指示)
       ^
       | 故障显示
       |
phosphor-watchdog (超时检测)
```

### 技术栈总结

OpenBMC 硬件控制子系统基于以下技术栈构建：

- **通信机制**: D-Bus (sd-bus/sdbusplus) 实现进程间通信
- **构建系统**: Meson + Ninja 实现跨平台编译
- **配置格式**: JSON 驱动的声明式配置（取代旧版 YAML）
- **编程语言**: C++ (核心逻辑) + Python (工具脚本)
- **硬件抽象**: sysfs/HWMON/GPIO 提供内核接口
- **服务管理**: systemd 作为进程管理框架
- **协议支持**: IPMI 2.0 + Redfish 提供外部管理接口

---

## 参考资源

- OpenBMC 官方项目: https://github.com/openbmc
- phosphor-power 仓库: https://github.com/openbmc/phosphor-power
- phosphor-fan-presence 仓库: https://github.com/openbmc/phosphor-fan-presence
- phosphor-thermal 仓库: https://github.com/openbmc/phosphor-thermal
- phosphor-led-manager 仓库: https://github.com/openbmc/phosphor-led-manager
- phosphor-watchdog 仓库: https://github.com/openbmc/phosphor-watchdog
- phosphor-logging 仓库: https://github.com/openbmc/phosphor-logging
