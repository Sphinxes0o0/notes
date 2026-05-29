---
type: source
source-type: web
title: "Interactive Linux Kernel Map"
author: "Constantine Shulyupin"
date: 2026-05-28
size: small
path: https://makelinux.github.io/kernel/map/
summary: "交互式SVG内核地图，可缩放80倍，展示从硬件接口到系统调用的各内核组件关系"
tags: [linux-kernel, visualization, architecture, vfs, memory-management, networking, drivers]
created: 2026-05-28
---

# Interactive Linux Kernel Map

来源: [makelinux.github.io/kernel/map](https://makelinux.github.io/kernel/map/) — 交互式内核架构地图

## 核心内容

### 可视化覆盖范围

| 层级 | 组件 |
|------|------|
| **硬件接口** | Input devices, Storage (SCSI/SATA/NVMe/USB), Network, GPU (DRM), Sound (ALSA), V4L2, Virtio/KVM |
| **核心子系统** | VFS, mm/, block/, net/, drivers/, Security (LSM) |
| **初始化** | init/ |
| **系统接口** | 系统调用、进程调度、中断处理、文件系统、内存映射 |

### 交互特性

- **SVG矢量缩放**: 最高80倍缩放，清晰查看任意组件
- **层级导航**: 从硬件接口逐层向上到系统调用
- **超链接**: 每个组件可点击跳转
- **架构无关**: 覆盖 x86/ARM 等多架构代码路径

## 资源特点

- **全局视图**: 建立内核各子系统关系的全局观
- **可探索**: 适合快速定位某功能在内核中的位置
- **补充笔记**: 适合作为源码学习的"地图"配套使用

## 相关页面

- [[wiki/kernel-subsystems-index]] — 内核子系统总览
- [[notes-kernel]] — Sphinx 内核笔记（源码级细节）
- [[bookmark-linux-kernel-explorer]] — Reverser Kernel Explorer（另一个交互工具）
- [[bookmark-linux-inside]] — Linux Inside（文字版全局介绍）
