---
type: source
source-type: github
title: "Android Treble 架构笔记"
date: 2026-05-25
tags: [android, treble, hal, hidl, vndk, vintf, stable-aidl]
created: 2026-05-28
path: raw/github/notes/android/notes/
summary: "Android Treble 架构核心文档（15篇）：系统架构、HIDL/HAL机制、VNDK/VINTF/Stable-AIDL、引导加载程序、Java SDK库"
---

# Android Treble 架构笔记

## 相关 Entity

- [[entities/android/hal]] — HAL 硬件抽象层
- [[entities/android/hidl]] — HIDL 接口定义语言
- [[entities/android/vndk]] — VNDK 供应商原生开发套件
- [[entities/android/vintf]] — VINTF 供应商接口
- [[entities/android/stable-aidl]] — Stable AIDL 机制
- [[entities/android/treble-architecture]] — Treble 架构总览

## 核心内容

Android 8.0+ 引入 Treble 架构，将 Android 平台与供应商实现解耦，实现独立升级。

**15 篇文档覆盖：**

| 文档 | 主题 |
|------|------|
| 01_Architecture | 系统架构总览（Linux 内核→HAL→ART→Java API→应用）|
| 02_modular-system | 模块化系统组件（APEX 容器格式、运行时模块、Conscrypt、DNS Resolver）|
| 03_hal | HAL 类型（绑定式/直通式/SP-HAL/传统 HAL）|
| 04_kernel | Android 通用内核要求、模块化内核、DTO 设备树叠加层 |
| 05_HIDL | HIDL 接口定义语言、C++/Java 绑定式接口 |
| 06_HIDL_C++ | HIDL C++ 实现细节（hwbinder、proxy/stub、传输错误处理）|
| 07_HIDL_Java | HIDL Java 前端（enum/struct/vector 映射、回调机制）|
| 08_configuration | ConfigStore HAL 与系统属性、Sysprop 说明文件 |
| 09_SystemSuspend | SystemSuspend HIDL 服务（WakeLock 机制、双线程模型）|
| 10_dto | 设备树叠加层 DTO（语法/编译/引导加载程序支持）|
| 11_vndk | VNDK 供应商原生开发套件（LLNDK、SP-HAL、VNDK-SP）|
| 12_vintf | VINTF 供应商接口对象（设备清单/框架清单/FCM）|
| 13_stable-aidl | 稳定 AIDL（版本控制、默认实现、跨进程调用）|
| 14_bootloader | 引导加载程序（启动原因规范、验证启动、DTB/DTBO）|
| 15_java-library | Java SDK 库（java_sdk_library 构建规则、存根库）|

## 关键架构概念

- **Treble 架构**：平台/供应商分离，Android 框架可独立升级
- **HIDL**：带版本编号的稳定接口语言，支持 C++/Java 绑定
- **VNDK**：供应商分区专用原生库集合，解决系统/供应商 libs 依赖
- **VINTF**：汇总设备信息（清单+矩阵）供 OTA 校验
- **Stable AIDL**：Android 10+ 替代 HIDL 的新 IPC 机制
- **APEX**：Android 10+ 模块化容器格式（ART/Conscrypt/DNS 等）

## 来源详情

- **来源路径**: `raw/github/notes/android/notes/`
- **文档数量**: 15 篇 .md 文档 + 配置/代码文件
- **领域**: Android 系统架构、Treble、HAL、HIDL、VNDK、VINTF
