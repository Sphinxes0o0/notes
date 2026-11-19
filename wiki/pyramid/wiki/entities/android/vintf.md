---
type: entity
tags: [android, VINTF, OTA, 兼容性]
created: 2026-05-25
sources: [notes-android]
---

# VINTF — 供应商接口对象

## 定义

VINTF（Vendor Interface Object）是 Android 8.0+ 的设备抽象层，汇总设备信息（HAL 接口、内核版本、SEPolicy 版本等）并通过可查询 API 提供给框架。确保设备清单与框架兼容性矩阵（FCM）在 OTA 时能正确校验匹配。

## 核心组件

### 设备清单（Device Manifest）

供应商分区声明其提供的 HAL 接口：
- `android.hardware.camera@3.4`
- `android.hardware.nfc@1.0` / `@2.0`
- `android.hardware.drm@1.0`（多实例：`clearkey` 等）

以 XML 格式定义，包含 `transport`（hwbinder/passthrough）、`version`、`interface`、`instance` 等字段。

### 框架兼容性矩阵（FCM — Framework Compatibility Matrix）

框架声明对设备的要求（Android 版本冻结时生成）：
- 所需 HAL 版本范围（如 `camera: 1.0-4` 表示 1.0~4 皆可）
- 内核版本与配置要求（`CONFIG_ANDROID`、`CONFIG_ARM64` 等）
- SELinux 版本要求
- VNDK 版本要求

### 设备清单 + FCM 匹配

OTA 时校验：
```
设备清单.目标 FCM 版本 == FCM.版本
设备清单.HAL 版本 ∈ FCM.HAL 版本范围
设备清单.内核版本 ≥ FCM.内核最低版本
```

## VINTF 生命周期

```
构建时：assemble_vintf 工具验证清单/矩阵有效性
安装时：VINTF 对象读取 /vendor/etc/vintf/manifest.xml
OTA时：框架拉取设备 VINTF → 校验 FCM 匹配 → 决定是否允许升级
```

## 相关概念

- [[treble-architecture]] — Treble 架构的两大支柱之一（另一个是 HIDL）
- [[hidl]] — 设备清单中声明的 HAL 接口由 HIDL 定义
- [[vndk]] — VINTF 同时汇总 VNDK 版本信息
- [[stable-aidl]] — Stable AIDL 接口也通过 VINTF 清单管理

## 来源详情

- [[notes-android]] — 12_vintf.md（详尽的清单/矩阵/XML Schema/匹配规则）
