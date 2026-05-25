---
type: entity
tags: [android, 系统架构, Treble]
created: 2026-05-25
sources: [notes-android]
---

# Android Treble 架构

## 定义

Android 8.0 引入的**Treble 架构**，将 Android 平台（system.img）与设备特定供应商实现（vendor.img）完全解耦，使 Android 框架可独立于芯片/设备厂商升级，无需等待芯片厂提供适配。

## 关键要点

- **架构分层**：Linux 内核 → HAL（硬件抽象层）→ Android Runtime → Java API Framework → 应用
- **Binder IPC**：框架 API 与系统服务间跨进程通信机制
- **模块化升级**：框架通过 APEX 容器格式独立更新（如 ART、Conscrypt、DNS Resolver）
- **Treble 前**：HAL 以传统 C 头文件（`libhardware`）定义，供应商代码耦合系统分区
- **Treble 后**：HAL 替换为 HIDL 稳定带版本接口，支持绑定式/直通式两种模式

## 系统堆栈

```
应用层
  ↓
Java API Framework（Activity Manager / Content Provider 等）
  ↓ Binder IPC
系统服务（Window Manager / Package Manager 等）
  ↓
HAL（HIDL 绑定式/直通式）←→ VINTF 清单/矩阵
  ↓
Linux 内核（Binder / WakeLock / Low Memory Killer 等）
```

## 相关概念

- [[hidl]] — HAL 接口定义语言，替代传统 `libhardware` 头文件
- [[hal]] — 硬件抽象层，定义硬件无关接口供框架调用
- [[vndk]] — 供应商原生开发套件，允许供应商分区使用系统原生库
- [[vintf]] — 供应商接口对象，汇总设备信息供框架/供应商兼容性校验
- [[stable-aidl]] — Android 10+ 替代 HIDL 的稳定 AIDL 接口

## 来源详情

- [[notes-android]]
