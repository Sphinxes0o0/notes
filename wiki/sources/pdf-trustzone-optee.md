---
type: source
source-type: pdf
title: TrustZone与OP-TEE技术详解
author: 帅峰云, 黄腾, 宋洋
date: 2018
size: large
path: raw/PDFs/books/手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解.pdf
summary: 手机安全和可信应用开发指南：ARM TrustZone硬件安全扩展 + OP-TEE开源TEE实现，786页权威著作
tags: [security, trustzone, op-tee, arm, tee, iot, books]
created: 2018
---
# TrustZone与OP-TEE技术详解

## 核心内容

**Authors:** 帅峰云, 黄腾, 宋洋 | 机械工业出版社 2018 | 786页

### 第一篇：基础技术篇

**第1章 可信执行环境 (TEE)：**
- 系统存在的安全问题
- TEE如何保护数据安全
- 现有TEE解决方案（智能手机/智能电视/IoT）

**第2章 ARM TrustZone技术：**
- 片上系统硬件框架
- ARMv7架构的TrustZone技术
- ARMv8架构的TrustZone技术
- AXI总线安全状态位扩展
- TZASC（TrustZone地址空间控制器）
- TZMA（TrustZone内存适配器）
- TZPC（TrustZone保护控制器）
- TZIC（TrustZone中断控制器）

### 第二篇：系统集成篇

**QEMU运行OP-TEE：**
- 启动过程详解
- 安全引导与ATF（ARM Trusted Firmware）
- BL1/BL2/BL31/BL32启动链

### OP-TEE 架构

- **REE（Rich Execution Environment）**：Linux/Android普通世界
- **TEE（Trusted Execution Environment）**：可信执行环境
- **TA（Trusted Application）**：可信应用
- **CA（Client Application）**：客户端应用
- GlobalPlatform TEE API 规范

## 相关页面
- [[entities/arm/trustzone-op-tee]] — TrustZone & OP-TEE entity
- [[entities/linux/security/linux-security-observability-ebpf]] — 安全可观测性
- [[entities/linux/kernel/index]] — 内核子系统
- [[sources/pdf-security-crypto-books]] — 安全密码学书籍合集