---
type: source
source-type: github
title: "QEMU 架构分析"
author: "notes (raw/notes)"
date: 2026-05-20
size: medium
path: raw/notes/qemu/
summary: "深入分析 QEMU 模拟器内部架构：QOM、内存管理、CPU执行、块设备层、迁移框架、网络等子系统"
tags: [linux, qemu, virtualization]
sources: [notes-qemu]
created: 2026-05-20
---

# QEMU 架构分析

## 核心内容

深入分析 QEMU 模拟器的内部架构、实现细节、设计模式和实现技巧。

### 核心子系统 (Phase 1-3)

- **QOM**: QEMU 对象模型，动态类型注册、继承、属性系统
- **内存管理**: AddressSpace、MemoryRegion、FlatView 三层结构
- **CPU 执行**: TCG 翻译、TranslationBlock、AccelClass 抽象

### 块设备层 (Phase 4)

- **BDS 图结构**: BlockDriverState 通过 BdrvChild 形成 DAG
- **QCOW2 格式**: 写时复制、快照、压缩
- **Coroutine + I/O 线程**: 异步非阻塞 I/O

### 迁移 (Phase 5)

- **VMState**: 声明式设备状态描述
- **RAM 迁移**: 脏页跟踪、precopy/postcopy
- **Multifd**: 多 fd 并行传输 + 压缩

## 关键架构模式

1. **处理器/回调调度**: QOM、迁移、块设备使用注册处理程序表
2. **访问者模式**: QAPI 代码生成
3. **状态机**: 迁移、块任务使用显式状态转换
4. **基于协程的异步 I/O**: 块设备层非阻塞操作

## 相关页面

- [[entities/linux/qemu/qemu-qom]]
- [[entities/linux/qemu/qemu-memory]]
- [[entities/linux/qemu/qemu-cpu]]
- [[entities/linux/qemu/qemu-block-layer]]
- [[entities/linux/qemu/qemu-migration]]
