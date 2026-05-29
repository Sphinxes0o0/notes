---
type: source
source-type: web
title: "蜗窝科技 Linux内核分析"
author: "蜗窝科技"
date: 2026-05-28
size: medium
path: http://www.wowotech.net/sort/linux_kenrel
summary: "Linux内核各子系统深度分析博客，涵盖块设备、内存管理、调度、网络等，基于Kernel 4.14 ARM64架构"
tags: [linux-kernel, arm64, memory-management, block, scheduling, networking]
created: 2026-05-28
---

# 蜗窝科技 Linux内核分析

来源: [wowotech.net](http://www.wowotech.net/sort/linux_kenrel) — Linux内核深度技术博客

## 核心内容

基于 Linux Kernel 4.14 (ARM64/Contex-A53) 的内核源码分析博客系列。

### 主要话题

| 分类 | 内容 |
|------|------|
| 块设备层 | bio/request/blk-mq/I/O调度器 |
| 内存管理 | 物理内存管理、slab分配器、vmalloc |
| 调度器 | CFS、实时调度、负载均衡 |
| 网络协议栈 | Socket、TCP/IP、Netfilter |
| 虚拟化 | KVM、Virtio |
| 电源管理 | CPU idle/cpufreq |
| 调试技术 | tracepoint、ftrace、perf |

## 资源特点

- **架构视角**: ARM64 为主，关注嵌入式场景
- **源码导向**: 大量内核源码引用和解读
- **图文并茂**: "A picture is worth a thousand words"
- **系列文章**: 每话题多篇递进式深入分析

## 关键页面

- [[wiki/kernel-block-index]] — 块设备层索引
- [[wiki/kernel-mm-index]] — 内存管理索引
- [[wiki/kernel-sched-index]] — 调度器索引
- [[wiki/kernel-net-index]] — 网络子系统索引

## 相关页面

- [[notes-kernel]] — Sphinx 内核笔记（更全面，涵盖 mm/sched/block/net）
- [[bookmark-linux-inside]] — Linux Inside（另一内核入门经典）
- [[bookmark-linux-kernel-labs]] — Linux Kernel Labs（教学向）
