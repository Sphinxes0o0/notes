---
type: entity
tags: [android, VNDK, 供应商原生库]
created: 2026-05-25
sources: [notes-android]
---

# VNDK — 供应商原生开发套件

## 定义

VNDK（Vendor Native Development Kit）是 Android 8.0+ 引入的供应商分区专用原生库集合。定义哪些系统原生库可以被供应商分区代码直接链接，解决系统分区（system.img）与供应商分区（vendor.img）间的共享库依赖问题。

## 核心概念

### LLNDK（Linkable Vendor NDK）

供应商代码可直接链接的**系统原生库**，具有稳定 ABI。包括：
- `lib渲染库`（Vulkan/EGL/GLES）
- `lib媒体编解码器`（AVC/HEVC）
- `libdl` / `liblog` / `libutils` 等基础库

### SP-HAL（Vendor-specific HAL）

供应商实现的 HAL，**不由 Google 控制**，不受 Treble 接口约束。包括：
- `GPU 驱动`（厂商私有 OpenGL/Vulkan 实现）
- `vendor-specific 传感器 HAL`

### VNDK-SP（VNDK Supplementary）

**系统专用的 SP-HAL 库**，系统分区提供但 SP-HAL 可用。供应商代码可链接，Google 控制版本稳定性。

### 禁止规则

- 供应商代码**禁止直接链接**非 LLNDK 的系统 libs（如 libcutils、libmedia）
- 系统代码**禁止链接**供应商 libs
- LLNDK 列表由 Google 维护，随 Android 版本更新

## VNDK 版本

每个 Android 版本有对应的 VNDK 版本号（如 Android 10 → VNDK-29）。供应商分区声明其兼容的 VNDK 版本，VINTF 在 OTA 时校验版本匹配。

## 相关概念

- [[treble-architecture]] — Treble 架构的核心目标之一是系统/供应商解耦，VNDK 是关键技术
- [[vintf]] — VINTF 的设备清单包含 VNDK 版本声明，OTA 时与 FCM 校验
- [[hal]] — SP-HAL 是 VNDK 的重要组成，厂商 GPU 驱动属于此类
- [[stable-aidl]] — AIDL 接口同样面临系统/供应商库依赖问题

## 来源详情

- [[notes-android]] — 11_vndk.md
