---
type: source
source-type: pdf
title: "深入理解Linux内核"
author: "Daniel P. Bovet, Marco Cesati"
date: 2000
size: medium
path: raw/PDFs/books/深入理解Linuxkenrle.pdf
summary: "Understanding the Linux Kernel, Bovet/Cesati，Linux内核设计与实现经典教材"
---

# 深入理解Linux内核

## 核心内容

Linux 内核经典教材（Bovet & Cesati）：

- **进程调度**：O(1) 调度器、CFS 等
- **内存管理**：页表、slab 分配器、vm_area_struct
- **虚拟文件系统（VFS）**：统一文件操作接口
- **块设备子系统**：I/O 调度算法
- **进程间通信**：IPC 机制
- **时间管理**：jiffies、定时器
- **内核同步**：自旋锁、信号量

## 关键要点

- O'Reilly 经典，从设计角度解读 Linux 内核实现
- 侧重 x86 架构，涵盖 2.6 版内核核心子系统
- 适合作为内核学习第二本书（继 Linux 0.12 完全注释之后）

## 相关页面
- [[pdf-book-linux-kernel-0-12]]
- [[pdf-book-computer-systems-perspective]]
- [[pdf-book-linux-sysprog]]