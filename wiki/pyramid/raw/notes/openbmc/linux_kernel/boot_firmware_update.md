# OpenBMC 启动控制/固件更新深度分析

## 目录

1. [系统概述](#1-系统概述)
2. [phosphor-boot-manager 启动顺序控制](#2-phosphor-boot-manager-启动顺序控制)
3. [phosphor-bmc-update BMC固件升级](#3-phosphor-bmc-update-bmc固件升级)
4. [entity-manager 板级配置管理](#4-entity-manager-板级配置管理)
5. [obmc-trigger 触发器管理](#5-obmc-trigger-触发器管理)
6. [BIOS/UEFI远程配置](#6-biosuefi远程配置)
7. [Flash布局详解](#7-flash布局详解)
8. [知识点关联表格](#8-知识点关联表格)

---

## 1. 系统概述

### 1.1 OpenBMC架构简介

OpenBMC是Linux Foundation项目,是一个基于Yocto、OpenEmbedded、systemd和D-Bus的Linux发行版,专门为管理控制器(BMC)设计。它实现了IPMI 2.0兼容性和DCMI支持,提供基于D-Bus的接口、REST接口和Web用户界面。

**核心技术栈:**
- **构建系统**: bitbake, 基于Yocto/OpenEmbedded
- **初始化系统**: systemd
- **进程间通信**: D-Bus (sdbus++)
- **服务架构**: Phosphor系列守护进程
- **API接口**: REST (基于bmcweb)、Redfish (DSP0266)
- **网络协议**: IPMI 2.0, SOL (Serial Over LAN)

### 1.2 状态机体系

OpenBMC定义了三类核心状态实体,每类都有独立的状态机:

**BMC状态:**
- 路径: `/xyz/openbmc_project/state/bmc<instance>`
- 状态: `NotReady`(启动中) → `Ready`(服务就绪) → `Quiesced`(关键服务故障)
- 可请求转换: `Reboot`

**Host状态:**
- 路径: `/xyz/openbmc_project/state/host<instance>`
- 状态: `Off`, `Running`, `TransitioningToRunning`, `TransitioningToOff`, `Quiesced`, `DiagnosticMode`
- 可请求转换: `Off`, `On`, `Reboot`, `GracefulWarmReboot`, `ForceWarmReboot`

**Chassis状态:**
- 路径: `/xyz/openbmc_project/state/chassis<instance>`
- 状态: `On`, `Off`, `BrownOut`, `UninterruptiblePowerSupply`
- 可请求转换: `On`, `Off`, `PowerCycle`

**实例编号约定:**
- 实例0 (`bmc0`, `chassis0`, `host0`) 代表完整系统
- 多主机系统从1开始编号

### 1.3 systemd集成架构

OpenBMC使用systemd管理服务依赖和启动顺序:

**核心启动目标:**
```
default.target → multi-user.target (Phosphor OpenBMC默认)
```

**主机管理目标层次:**
```
obmc-host-start@0.target
├── obmc-host-startmin@0.target
│   ├── obmc-chassis-poweron@0.target
│   │   ├── op-power-start@0.service
│   │   └── op-wait-power-on@0.service
│   └── start_host@0.service
└── phosphor-reset-host-reboot-attempts@0.service
```

**关键systemd目标:**
| 目标 | 用途 |
|------|------|
| `obmc-host-start@.target` | 主要启动驱动 |
| `obmc-host-startmin@.target` | 最小启动服务(重启场景) |
| `obmc-chassis-poweron@.target` | 应用chassis电源 |
| `obmc-host-shutdown@.target` | 软关机(通知主机) |
| `obmc-chassis-hard-poweroff@.target` | 立即切断电源 |
| `obmc-host-reboot@.target` | 软关机+开机组合 |
| `obmc-host-quiesce@.target` | 主机错误处理 |
| `obmc-chassis-emergency-poweroff@.target` | 关键热/电源错误 |

---

## 2. phosphor-boot-manager 启动顺序控制

### 2.1 组件概述

phosphor-boot-manager是OpenBMC中负责管理主机启动顺序和启动源的守护进程。它通过D-Bus接口提供启动选项的配置和查询功能。

### 2.2 启动源类型 (BootSource)

OpenBMC支持多种启动源,通过`xyz.openbmc_project.BootTypes.BootSource`接口定义:

| 启动源 | 描述 | 用途 |
|--------|------|------|
| `Network` | 网络启动(PXE) | 远程部署和启动 |
| `HDD` | 硬盘启动 | 本地操作系统启动 |
| `USB` | USB设备启动 | 外接介质启动 |
| `BIOS` | 传统BIOS启动 | 兼容模式 |
| `UEFI` | UEFI启动 | 现代固件模式 |
| `Diag` | 诊断分区 | 硬件诊断 |
| `CDROM` | 光驱启动 | 介质安装 |
| `Floppy` | 软盘启动 | 遗留支持 |

### 2.3 启动模式 (BootMode)

启动模式通过`xyz.openbmc_project.BootTypes.BootMode`接口定义:

| 模式 | 描述 |
|------|------|
| `Regular` | 正常启动 |
| `Setup` | 进入BIOS/UEFI设置界面 |
| `ForcePxe` | 强制从PXE启动 |
| `HardwareReset` | 硬件复位 |
| `SoftwareReset` | 软件复位 |
| `Audit` | 审计模式 |
| `Manufacturing` | 制造模式 |
| `FlashUpdate` | Flash更新模式 |
| `CDROM` | 光驱启动模式 |

### 2.4 D-Bus接口定义

**Boot属性接口:**
```
/xyz/openbmc_project/state/host0
  - xyz.openbmc_project.State.Host.CurrentHostState
  - xyz.openbmc_project.Boot.Source
  - xyz.openbmc_project.Boot.Mode
  - xyz.openbmc_project.Boot.Order
  - xyz.openbmc_project.Boot.Progress
```

**关键属性:**
- `BootSource`: 当前启动源
- `BootMode`: 当前启动模式
- `BootOrder`: 启动顺序列表(优先级从高到低)
- `BootProgress`: 启动进度状态

### 2.5 启动顺序状态机

```
                    ┌─────────────────┐
                    │    BootOrder    │
                    │   (PXE→HDD→USB) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌────────┐     ┌────────┐     ┌────────┐
         │  PXE   │     │  HDD   │     │  USB   │
         │ Attempt│     │ Attempt│     │ Attempt│
         └────┬───┘     └────┬───┘     └────┬───┘
              │              │              │
              ▼              ▼              ▼
         ┌─────────────────────────────┐
         │     Boot Attempt Failed?    │
         └──────────────┬──────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
         ┌────────┐          ┌──────────────┐
         │ Try    │          │ Boot Success │
         │ Next   │          │   (Running)   │
         └────────┘          └──────────────┘
```

### 2.6 IPMI启动选项集成

IPMI提供启动选项命令(Set System Boot Options, NetFn=0x00, Cmd=0x08):

**OEM扩展启动选项:**
- 启动源选择位(4-7位)
- 启动模式位(0-3位)
- 启动有效标志位(位5)

**通过IPMI设置启动顺序示例:**
```bash
# 设置下次启动从PXE
busctl set-property xyz.openbmc_project.Boot.Manager \
    /xyz/openbmc_project/state/host0 \
    xyz.openbmc_project.Boot.Source \
    BootSource s "Network"

# 强制PXE启动
ipmitool raw 0x00 0x08 0x05 0xe0 0x00 0x00 0x00 0x00
```

---

## 3. phosphor-bmc-update BMC固件升级

### 3.1 双镜像A/B分区方案

OpenBMC使用A/B风格的双镜像存储实现安全的固件更新:

**核心设计原则:**
- 两套完整的BMC镜像存储区(镜像A和镜像B)
- 当前运行镜像标记为"functional"
- 更新写入非active镜像
- 功能镜像切换需要重启BMC
- 旧镜像保留作为回退选项直到新镜像验证成功

**镜像关联结构:**
```
/xyz/openbmc_project/software/
├── functional (指向当前运行的镜像)
├── alternate (指向备用镜像)
└── <version_id> (各镜像版本对象)
```

### 3.2 代码更新流程

**更新流程状态机:**
```
┌─────────────┐
│   IDLE      │
└──────┬──────┘
       │ 用户请求激活
       ▼
┌─────────────┐
│ VERIFYING   │ ──→ 签名验证失败 → FAILED
└──────┬──────┘
       │ 验证通过
       ▼
┌─────────────┐
│ ACTIVATING  │ ──→ Flash写入失败 → FAILED
└──────┬──────┘
       │ 写入完成
       ▼
┌─────────────┐
│   READY     │ ←→ 用户请求回退 → A/B切换
└──────┬──────┘
       │ BMC重启
       ▼
┌─────────────┐
│  ACTIVE     │ ──→ 运行时故障 → 回退到旧镜像
└─────────────┘
```

### 3.3 更新流程详解

**Step 1: 获取镜像**
从OpenBMC构建系统获取BMC镜像tar包(UBI或static layout格式)

**Step 2: 传输镜像**
支持多种传输方式:
- **SCP**: 直接复制到BMC的`/tmp/images/`
- **REST Upload**: 使用REST API上传端点
- **TFTP**: POST到`/xyz/openbmc_project/software`的`DownloadViaTFTP`方法

**Step 3: 版本识别**
版本ID是版本字符串的SHA-512哈希的前8个十六进制字符:
```bash
# 列出可用镜像
ls /tmp/images/

# 通过REST查询版本
curl -k -H "Cookie: ..." https://$BMC_IP/xyz/openbmc_project/software/enumerate
```

**Step 4: 激活镜像**
```bash
# 使用busctl激活
busctl set-property xyz.openbmc_project.Software.Manager \
    /xyz/openbmc_project/software/<version_id> \
    xyz.openbmc_project.Software.Activation \
    RequestedActivation s \
    "xyz.openbmc_project.Software.Activation.RequestedActivations.Active"
```

**Step 5: 进度监控**
```bash
# 监控ActivationProgress属性
busctl monitor --match "type='signal',interface='xyz.openbmc_project.Software.ActivationProgress'"
```

**Step 6: 重启生效**
```bash
# 激活完成后重启BMC
busctl reboot
```

### 3.4 MANIFEST文件验证

每个镜像包含MANIFEST文件,定义镜像元数据:

| 字段 | 描述 |
|------|------|
| `Purpose` | 镜像用途(BMC, Host BIOS等) |
| `Version` | 版本字符串 |
| `KeyType` | 签名密钥类型 |
| `HashType` | 哈希算法类型 |
| `MachineName` | 目标机器名称 |

激活时验证`MachineName`必须匹配`OPENBMC_TARGET_MACHINE`环境变量。

### 3.5 镜像布局

**UBI布局结构:**
```
MTD设备
├── UBI卷: image-u-boot      (U-Boot bootloader)
├── UBI卷: image-kernel      (Linux kernel)
├── UBI卷: image-rofs        (squashfs, 只读根文件系统)
├── UBI卷: image-rwfs        (overlayfs, 可写层)
└── UBI卷: image-journalfs   (日志分区)
```

**静态布局结构:**
```
MTD分区
├── image-u-boot  (U-Boot)
├── image-kernel  (内核)
├── image-rofs    (squashfs)
└── image-rwfs    (JFFS2)
```

### 3.6 Redfish固件更新API

**API端点:**
- **UpdateService**: `https://${bmc}/redfish/v1/UpdateService`
- **HttpPushUri**: 直接上传镜像的URI
- **SimpleUpdate Action**: `https://${bmc}/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate`

**直接上传流程:**
```bash
# 1. 获取HttpPushUri
GET /redfish/v1/UpdateService

# 2. 配置ApplyTime
POST /redfish/v1/UpdateService/HttpPushUriOptions/HttpPushUriApplyTime
{
    "HttpPushUriApplyTime": "Immediate"  # 或 "OnReset"
}

# 3. 上传镜像
POST /redfish/v1/UpdateService/HttpPushUri
<二进制镜像数据>
```

**远程下载流程(TFTP):**
```bash
POST /redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate
{
    "ImageURI": "tftp://server/path/image.tar",
    "TransferProtocol": "TFTP"
}
```

### 3.7 IPMI Flash更新

`phosphor-ipmi-flash`实现安全的带内固件更新:

**数据传输方式:**
| 方式 | 速度 | 用途 |
|------|------|------|
| IPMI数据包 | ~3小时(32MiB) | 紧急/备份 |
| PCI/Net桥接 | <1分钟 | 快速更新 |
| LPC内存区 | 数分钟 | 中速更新 |

**更新流程:**
1. IPMI OEM处理器接收镜像
2. 触发`verify_image`服务
3. 用户轮询验证结果(可超过10秒)
4. 镜像必须使用生产或开发密钥签名

**配置选项:**
- `--enable-static-layout`: 静态flash布局更新
- `--enable-tarball-ubi`: UBI tarball更新
- `--enable-host-bios`: BIOS更新支持
- `--enable-net-bridge`: 网络传输

---

## 4. entity-manager 板级配置管理

### 4.1 组件概述

entity-manager是OpenBMC中负责运行时JSON驱动系统配置管理的组件。它管理物理系统组件并将它们映射到BMC内的软件资源,实现灵活的运行时调整。

### 4.2 核心概念

**Entity (实体):**
物理上可分离的、可检测的服务器组件,可以添加或移除。

**Exposes (暴露):**
实体的功能暴露,包括传感器、PID控制参数、CPU信息等。

**Probe (探测):**
D-Bus接口规则,用于检测实体的存在。

### 4.3 配置组织结构

**配置目录:** `./configurations`
**设计原则:** 每个支持的设备型号一个配置文件

**配置检测流程:**
```
fru-device扫描I2C总线 → IPMI FRU EEPROM检测
         ↓
发现FRU → 查询entity-manager配置
         ↓
匹配Probe规则 → 创建inventory对象
         ↓
发布Exposes到D-Bus
```

### 4.4 支持的检测守护进程

| 守护进程 | 检测方法 | 用途 |
|----------|----------|------|
| `fru-device` | I2C总线FRU EEPROM扫描 | IPMI FRU存储 |
| `peci-pcie` | PCIe设备读取 | CPU/PCIe设备 |
| `smbios-mdr` | x86 SMBIOS表解析 | BIOS信息 |

### 4.5 配置重检测触发

配置可以在以下事件发生时重新检测:
- 主机电源开启
- 驱动器插入/拔出
- PSU插入/拔出

### 4.6 JSON配置Schema

**示例配置结构:**
```json
{
  "Probe": {
    "Interface": "xyz.openbmc_project.Inventory.Item.Tpm",
    "Property": "Present",
    "Value": true
  },
  "Exposes": [
    {
      "Name": "TPM",
      "Interface": "xyz.openbmc_project.Inventory.Item.Tpm",
      "Properties": {
        "Version": "1.2",
        "Manufacturer": "Infineon"
      }
    }
  ]
}
```

### 4.7 D-Bus接口

**服务名:** `xyz.openbmc_project.EntityManager`
**路径:** `/xyz/openbmc_project/entity`

**关联接口:**
- 配置文件发布到D-Bus后,其他守护进程(如dbus-sensors)消费Exposes记录

### 4.8 兼容软件

| 软件 | 交互方式 |
|------|----------|
| `bmcweb` | Redfish API |
| `intel-ipmi-oem` | IPMI SDR/FRU命令 |
| `dbus-sensors` | D-Bus传感器接口 |

---

## 5. obmc-trigger 触发器管理

### 5.1 组件概述

obmc-trigger是OpenBMC中管理各种系统触发器的守护进程。触发器用于响应特定系统事件并执行预定义的操作序列。

### 5.2 触发器类型

**电源触发器:**
- 电源按钮按下
- 电源故障恢复
- 电源序列完成

**热触发器:**
- 温度阈值超限
- 风扇故障
- 热紧急事件

**启动触发器:**
- 启动顺序完成
- 启动失败
- 启动超时

**更新触发器:**
- 固件更新完成
- 镜像激活成功
- 回退触发

### 5.3 触发器配置

触发器通过systemd unit文件或D-Bus接口配置:

```bash
# 查看触发器状态
busctl tree xyz.openbmc_project.Trigger

# 手动触发事件
busctl call xyz.openbmc_project.Trigger \
    /xyz/openbmc_project/trigger/boot_failure \
    xyz.openbmc_project.Trigger.Manager \
    Trigger
```

### 5.4 与状态管理器集成

触发器与phosphor-state-manager紧密集成:
- 状态变化触发相应的触发器
- 触发器可以请求状态转换
- 错误状态触发错误处理序列

---

## 6. BIOS/UEFI远程配置

### 6.1 IPMI BIOS配置

OpenBMC通过IPMI OEM命令支持BIOS/UEFI设置远程配置:

**支持的配置操作:**
- 读取当前BIOS设置
- 修改启动选项
- 重置BIOS默认设置
- 保存/恢复BIOS配置

### 6.2 主机代码更新

OpenBMC使用squashfs镜像通过op-build构建来更新主机固件(BIOS):

**更新流程:**
1. 获取BIOS镜像tar包(从op-build构建)
2. 使用SCP/REST/TFTP传输到BMC
3. 识别版本ID(SHA-512哈希前8字符)
4. 激活镜像(写入PNOR chip的UBI卷)
5. 监控进度
6. 验证完成

**镜像传输方式:**
| 方式 | 命令 |
|------|------|
| SCP | `scp bios.tar $BMC:/tmp/images/` |
| REST | `POST /xyz/openbmc_project/software/action/upload` |
| TFTP | `busctl call ... DownloadViaTFTP` |

### 6.3 BIOS设置持久化

BIOS设置存储在:
- **PNOR分区**: 包含BIOS配置数据
- **VPD (Vital Product Data)**: 永久存储配置

**固件修补:**
分区二进制文件可以通过复制到`/usr/local/share/pnor/`进行修补,文件名需与目标分区名相同(如`ATTR_TMP`)。

### 6.4 Redfish BIOS配置

通过Redfish `Systems/system`端点管理BIOS设置:

```bash
# 获取BIOS设置
GET /redfish/v1/Systems/system/Bios

# 获取BIOS版本
GET /redfish/v1/Systems/system/Bios/BiosVersion

# 重置为默认
POST /redfish/v1/Systems/system/Bios/Actions/Bios.ResetBios
```

---

## 7. Flash布局详解

### 7.1 总体布局

OpenBMC系统通常存储在SPI Flash中,采用分层布局:

```
┌─────────────────────────────────────────────────────────────┐
│                     Flash Memory                            │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐                                        │
│ │   Bootloader    │  U-Boot bootloader                     │
│ │   (U-Boot)      │  存储启动命令和环境变量                │
│ └─────────────────┘                                        │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐                    │
│ │   Flash0        │ │   Flash1        │  双镜像存储        │
│ │   (Image A)     │ │   (Image B)     │                    │
│ ├─────────────────┤ ├─────────────────┤                    │
│ │ image-u-boot    │ │ image-u-boot    │  U-Boot副本        │
│ │ image-kernel    │ │ image-kernel    │  Linux内核        │
│ │ image-rofs      │ │ image-rofs      │  squashfs根文件系统│
│ │ image-rwfs      │ │ image-rwfs      │  可写层            │
│ │ image-journalfs │ │ image-journalfs │  日志分区          │
│ └─────────────────┘ └─────────────────┘                    │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐                                        │
│ │   Persist Data  │  持久化数据区                          │
│ │   (U-Boot env)  │  环境变量、NVRAM                       │
│ └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Bootloader层 (U-Boot)

**U-Boot职责:**
- 初始化硬件(DDR、串口、SPI控制器)
- 从Flash加载内核和设备树
- 提供启动菜单(在配置时)
- 管理启动环境变量
- 支持Flash切换(双镜像)

**关键环境变量:**
```
bootcmd          # 启动命令
bootargs        # 内核参数
bootdevice      # 启动设备选择
mtdparts        # MTD分区定义
uboot_firmware  # 当前固件版本
```

### 7.3 内核镜像

**镜像格式:** uImage (U-Boot格式) 或 Image (原生Linux)

**加载过程:**
```
U-Boot → 读取image-kernel到内存 → 验证签名 → 传递dtb地址 → 启动内核
```

**内核配置:**
- 启用OpenBMC特定驱动(I2C、GPIO、SPI等)
- 设备树包含BMC硬件描述
- initramfs包含最小启动环境

### 7.4 根文件系统布局

#### 7.4.1 只读层 (squashfs)

**压缩方式:** xz压缩

**目录结构(FHS兼容):**
```
/
├── bin           # 链接到/bin/busybox
├── boot          # 内核镜像、设备树
├── dev           # 设备节点
├── etc           # 配置文件(overlay覆盖)
├── home          # 用户主目录
├── lib           # 共享库
├── media         # 可移除介质
├── mnt           # 挂载点
├── opt           # 可选应用
├── proc          # procfs
├── run           # 运行时数据(tmpfs)
├── sbin          # 系统管理程序
├── srv           # 服务数据
├── sys           # sysfs
├── tmp           # tmpfs
├── usr           # 用户程序
└── var           # 可变数据(overlay覆盖)
```

#### 7.4.2 可写层 (overlayfs + UBIFS/JFFS2)

**overlayfs结构:**
```
overlayfs (upper)     ← UBIFS或JFFS2
    └── etc/              覆盖原始/etc
    └── home/             覆盖原始/home
    └── var/              覆盖原始/var

squashfs (lower)      ← squashfs镜像
    └── etc/              只读基础配置
    └── home/              只读主目录
    └── var/              只读可变数据
```

**UBI卷配置(典型):**
| 卷名 | 用途 | 大小(典型) |
|------|------|-----------|
| `ubi:rootfs` | squashfs镜像(roofs) | 16-32MB |
| `ubi:vol` | UBIFS卷(/var, /home等) | 8-16MB |

### 7.5 辅助文件系统

| 文件系统 | 挂载点 | 类型 | 用途 |
|----------|--------|------|------|
| tmpfs | /tmp, /run | tmpfs | 临时文件,运行时数据 |
| procfs | /proc | proc | 进程信息 |
| sysfs | /sys | sysfs | 设备模型 |
| devpts | /dev/pts | devpts | 终端复用 |

### 7.6 Flash布局类型

#### 7.6.1 静态布局 (非UBI)

**特点:**
- 直接写入命名分区
- 分区大小在构建时固定
- 简单但不够灵活

**分区表:**
```
image-u-boot     - U-Boot镜像
image-kernel    - Linux内核
image-rofs      - squashfs只读文件系统
image-rwfs      - JFFS2可写文件系统
image-journalfs - 日志分区(可选)
```

#### 7.6.2 UBI布局

**特点:**
- 使用UBI(Unsorted Block Images)
- 动态卷大小调整
- 磨损均衡支持
- 更适合频繁写入

**UBI卷:**
```
ubi:rootfs      - squashfs镜像(只读,通过ubiblock访问)
ubi:vol        - UBIFS卷(可写,挂载为/var)
```

### 7.7 镜像回退机制

**双镜像回退流程:**
```
当前: Image A (functional)
目标: 更新到 Image B

Step 1: 写入Image B
Step 2: 验证Image B完整性
Step 3: 设置Image B为"ready"状态
Step 4: BMC重启
Step 5: U-Boot检测到"ready"状态
Step 6: 从Image B启动
Step 7: Image B稳定运行
Step 8: Image A变为"alternate"

故障回退:
- 如果Image B启动失败
- U-Boot检测启动失败标记
- 自动切换回Image A
- 记录错误到SEL
```

---

## 8. 知识点关联表格

### 8.1 组件关联表

| 组件 | 功能 | 依赖项 | D-Bus路径 |
|------|------|--------|-----------|
| phosphor-boot-manager | 启动顺序控制 | systemd, D-Bus | `/xyz/openbmc_project/state/host*` |
| phosphor-bmc-update | BMC固件升级 | U-Boot, MTD | `/xyz/openbmc_project/software` |
| phosphor-state-manager | 状态管理 | systemd | `/xyz/openbmc_project/state/*` |
| entity-manager | 板级配置 | FRU设备,I2C | `/xyz/openbmc_project/entity` |
| obmc-trigger | 触发器管理 | systemd | `/xyz/openbmc_project/trigger/*` |
| phosphor-host-manager | 主机管理 | IPMI, D-Bus | `/xyz/openbmc_project/state/host*` |

### 8.2 状态转换表

| 当前状态 | 目标状态 | 触发条件 | 执行动作 |
|----------|----------|----------|----------|
| NotReady | Ready | 所有服务启动完成 | 更新BMC状态 |
| Ready | Quiesced | 关键服务失败 | 停止非关键服务 |
| Off | Running | 启动序列完成 | 主机OS开始执行 |
| Running | Quiesced | 严重错误 | 主机进入错误模式 |
| Active | Ready | 镜像激活完成 | 等待重启 |
| Ready | Active | BMC重启完成 | 新镜像运行 |

### 8.3 Flash区域与组件映射

| Flash区域 | 内容 | 大小(典型) | 访问方式 |
|-----------|------|-----------|----------|
| U-Boot | 引导程序 | 512KB-1MB | 直接内存映射 |
| kernel | Linux内核 | 4-8MB | MTD读取 |
| rofs | squashfs | 16-32MB | ubiblock/mtdblock |
| rwfs | 可写层 | 8-16MB | UBIFS/JFFS2 |
| env | 环境变量 | 128KB | U-Boot环境 |

### 8.4 启动源与协议映射

| 启动源 | 协议 | IPMI值 | 用途 |
|--------|------|--------|------|
| Network/PXE | DHCP + TFTP | 0x02 | 网络引导 |
| HDD | SATA/NVMe | 0x01 | 本地磁盘 |
| USB | USB HID | 0x03 | 外接设备 |
| CDROM | ATAPI | 0x05 | 光驱启动 |
| BIOS Setup | N/A | 0x00 | 设置界面 |

### 8.5 更新方式对比

| 更新方式 | 速度 | 安全性 | 适用场景 |
|----------|------|--------|----------|
| Redfish HTTP | 中等 | 高(TLS) | 常规更新 |
| REST API | 中等 | 高(TLS) | 自动化脚本 |
| IPMI | 慢 | 中 | 紧急恢复 |
| SCP | 快 | 中(需密钥) | 开发调试 |
| TFTP | 快 | 低 | 内网更新 |

### 8.6 文件系统挂载顺序

```
1. /dev            - devtmpfs
2. /proc           - procfs
3. /sys            - sysfs
4. /               - squashfs (lower)
5. /var            - UBIFS/UBIFS (upper, overlay)
6. /home           - UBIFS (upper, overlay)
7. /etc            - UBIFS (upper, overlay)
8. /tmp            - tmpfs
9. /run            - tmpfs
10. /var/log       - tmpfs 或持久化
```

### 8.7 核心D-Bus服务总结

| 服务名 | 接口前缀 | 用途 |
|--------|----------|------|
| `xyz.openbmc_project.State.BMC` | BMC状态 | BMC生命周期 |
| `xyz.openbmc_project.State.Host` | Host状态 | 主机状态管理 |
| `xyz.openbmc_project.State.Chassis` | Chassis状态 | 电源管理 |
| `xyz.openbmc_project.Boot` | 启动选项 | 启动配置 |
| `xyz.openbmc_project.BootTypes` | 启动类型 | 启动源定义 |
| `xyz.openbmc_project.Software` | 软件版本 | 固件管理 |
| `xyz.openbmc_project.Inventory` | 资产清单 | 硬件清单 |
| `xyz.openbmc_project.LED` | LED控制 | 状态指示 |
| `xyz.openbmc_project.Trigger` | 触发器 | 事件响应 |
| `xyz.openbmc_project.EntityManager` | 实体管理 | 板级配置 |

---

## 参考资源

### 官方仓库
- https://github.com/openbmc/phosphor-boot
- https://github.com/openbmc/phosphor-bmc-update
- https://github.com/openbmc/entity-manager
- https://github.com/openbmc/phosphor-state-manager
- https://github.com/openbmc/docs

### 架构文档
- OpenBMC Architecture Documentation
- phosphor-dbus-interfaces YAML definitions
- systemd OpenBMC integration guide

### 相关协议
- IPMI 2.0 Specification
- Redfish DSP0266
- D-Bus Specification
