---
type: entity
tags: [android, HAL, 硬件抽象层, Treble]
created: 2026-05-25
sources: [notes-android]
---

# HAL — 硬件抽象层

## 定义

HAL（Hardware Abstraction Layer，硬件抽象层）定义了 Android 框架与设备硬件之间的标准接口。在 Treble 架构前，HAL 以传统 C 头文件（`libhardware`）实现；Treble 后，HAL 以 HIDL 或 Stable AIDL 定义，支持绑定式/直通式部署。

## HAL 类型体系

### 绑定式 HAL（Binderized HAL）

- 以 HIDL 定义，通过 **hwbinder** IPC 与框架通信
- 所有搭载 Android O+ 的设备必须支持
- 示例：`android.hardware.camera@3.4`、`android.hardware.wifi@1.0`

### 直通式 HAL（Passthrough HAL）

- 以 HIDL 封装的传统 HAL，通过 `dlopen` 在同一进程加载
- 必需列表（Android O+ 设备）：`graphics.mapper@1.0`、`renderscript@1.0`
- 可选：可作为绑定式或直通式部署

### SP-HAL（Same-Process HAL）

- **Google 控制**，厂商不可修改
- 包括：OpenGL ES、Vulkan、`android.hidl.memory@1.0`、`graphics.mapper@1.0`

### 传统 HAL / 旧版 HAL

- Android 8.0 前使用，已弃用
- 头文件在 `hardware/libhardware/include/hardware/`

## 动态生命周期

Android 9+ 支持 HAL 动态关停（无客户端时自动关闭）和自动重启：
- 使用 `LazyServiceRegistrar` 而非 `registerAsService`
- 客户端持有引用时保留，释放后调用 `flushCommands()`
- 无需 `init` 干预，hwservicemanager 自动管理

## 相关概念

- [[treble-architecture]] — HAL 是 Treble 架构的关键层
- [[hidl]] — 绑定式/直通式 HAL 通过 HIDL 定义
- [[vndk]] — SP-HAL 属于 VNDK 的一部分
- [[vintf]] — 设备清单声明 HAL 接口版本，供 VINTF 校验
- [[stable-aidl]] — AIDL 替代 HIDL 成为新的 HAL 定义方式

## 来源详情

- [[notes-android]] — 03_hal.md（HAL 类型详解、动态生命周期）
