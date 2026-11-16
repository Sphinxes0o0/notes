---
type: entity
tags: [android, HIDL, IPC, 接口定义语言]
created: 2026-05-25
sources: [notes-android]
---

# HIDL — HAL 接口定义语言

## 定义

HIDL（HAL Interface Definition Language）是 Android 8.0 引入的接口定义语言，用于以**稳定、带版本编号**的接口连接 Android 框架与供应商 HAL 实现。替代了原有的传统 C 头文件 HAL（`libhardware`）。

## 关键要点

- **版本化接口**：接口以 `package@version` 格式（如 `android.hardware.nfc@1.0`）管理
- **双向通信**：支持 C++ 绑定式（通过 hwbinder IPC）和 Java 前端
- **三种部署模式**：
  - **绑定式（Binderized）**：框架与 HAL 跨进程，通过 hwbinder 通信
  - **直通式（Passthrough）**：HAL 在同一进程加载（`dlopen`），减少 IPC 开销
  - **SP-HAL**：Same-Process HAL，仅限 Google 控制（OpenGL/Vulkan/graphics.mapper）
- **数据类型映射**：enum → `enum class`；struct → 标准布局 C++ struct；vector → `hidl_vec`
- **传输错误处理**：`Return<T>` 类型，`isOk()` 检测远程崩溃，`linkToDeath` 注册通知

## C++ 客户端示例

```cpp
#include <android/hardware/nfc/1.0/IFoo.h>
sp<IFoo> client = IFoo::getService();
client->doThing(); // 跨进程调用
```

## Java 端数据类型转换

| HIDL 类型 | Java 类型 |
|-----------|-----------|
| `enum` (uint8_t) | `byte` 常量（无符号自动转为有符号）|
| `vec<T>` | `ArrayList<T>` |
| `struct` | Java class（字段一一映射）|
| `string` | `String`（utf-8 传输）|

## 相关概念

- [[treble-architecture]] — Treble 架构总览，HIDL 是其核心组件
- [[hal]] — HAL 类型（绑定式/直通式/SP-HAL），HIDL 接口的部署模式
- [[stable-aidl]] — Android 10+ 替代 HIDL 的新 AIDL 接口机制
- [[vintf]] — VINTF 通过设备清单记录 HIDL 接口版本信息

## 来源详情

- [[notes-android]] — 05_HIDL.md, 06_HIDL_C++.md, 07_HIDL_Java.md
