---
type: source
tags: [arm, architecture, cpu, trustzone, books]
source-type: pdf
title: "ARM体系结构与计算机架构书籍合集（4册）"
author: "Arm Limited, John L. Hennessy/David A. Patterson, etc."
date: 2026-05
size: large
path: raw/PDFs/books/
summary: "4册ARM/硬件体系结构权威文档：ARMv8 Architecture Reference Manual (DDI0487Fc/F.M)、Cortex-A9 TRM、计算机体系结构量化研究方法 第五版"
---

# ARM体系结构与计算机架构书籍合集

## 书目一览

### 1. Arm Architecture Reference Manual — Armv8, for Armv8-A (DDI0487F.c)
- **发布**: Arm Limited, 2020 (ID072120)
- **页数**: 8248
- **内容**: Armv8-A架构权威参考手册
  - **Part A**: Armv8架构介绍与概览（数据类型、SIMD/FP、内存模型）
  - **Part A2**: Armv8-A架构扩展（Armv8.0-8.6, Cryptographic Extension）
  - 后续Part：指令集描述、系统寄存器、异常模型、内存管理（MMU/TLB）、调试架构
- **涵盖**: AArch64和AArch32执行状态
- **状态**: PDF完整文本，超大型文档

### 2. Arm Architecture Reference Manual for A-profile (DDI0487 M.a.a)
- **发布**: Arm Limited, 2025 (Dec)
- **页数**: 16825
- **版本**: Armv9.6 EAC release
- **内容**: 最新的A-profile架构参考手册（兼容Armv8.0-8.9 + Armv9.0-9.6）
  - SVE（可扩展向量扩展）、SME（可扩展矩阵扩展）
  - MEC、RAS、RME、BRBE、ETE、TRBE
  - MPAM（内存分区与监控）
  - 涵盖从Armv8.0到Armv9.6的全部特性
- **状态**: PDF完整文本，超大型文档（最新版）

### 3. Cortex-A9 Technical Reference Manual (DDI0388H)
- **发布**: Arm Limited, 2012 (r4p0)
- **页数**: 213
- **内容**: Cortex-A9处理器技术参考手册
  - **第1章**: 处理器介绍（特性、接口、配置选项）
  - **第2章**: 功能描述（时钟/复位、电源管理）
  - **第3章**: 编程模型（ThumbEE、Jazelle、SIMD、Security Extensions、MP Extensions）
  - **第4章**: 系统控制（寄存器汇总与描述）
  - **第6章**: MMU（TLB组织、内存访问序列）
  - **第7章**: L1内存系统（指令/数据端、DSB、数据预取、奇偶校验）
  - **第8章**: L2内存接口
- **特点**: 经典ARM Cortex-A系列处理器参考
- **状态**: PDF完整文本

### 4. 计算机体系结构：量化研究方法（第五版）
- **作者**: John L. Hennessy & David A. Patterson (2017 ACM Turing Award)
- **出版**: 第五版（中文版）
- **页数**: 612
- **内容**: 计算机体系结构权威教材
  - 量化设计方法、指令集设计、流水线、存储层次
  - 多核/多处理器、GPU架构、能耗优化
  - 最新版增加领域专用架构（DSA）、深度学习加速器
- **特点**: 图灵奖得主经典之作，体系结构领域圣经
- **状态**: 图片扫描版，无可提取文本

## 相关页面

- [[qemu-index]] — QEMU模拟器（模拟ARM处理器）
- [[entities/linux/qemu/qemu-cpu]] — QEMU CPU模拟
- [[sys-prog-index]] — 系统编程导航
- [[os-index]] — 操作系统基础（与体系结构紧密相关）
