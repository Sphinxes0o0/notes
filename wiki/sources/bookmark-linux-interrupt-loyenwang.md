---
type: source
source-type: web
title: "Linux中断子系统 by LoyenWang"
author: "LoyenWang"
date: 2026-05-28
size: small
path: https://www.cnblogs.com/LoyenWang/category/1777370.html
summary: "Linux Kernel 4.14 ARM64中断子系统深度分析：中断控制器驱动、通用中断框架、softirq、tasklet、workqueue"
tags: [linux-kernel, interrupt, arm64, softirq, tasklet, workqueue, kernel-4.14]
created: 2026-05-28
---

# Linux中断子系统

来源: [cnblogs.com/LoyenWang](https://www.cnblogs.com/LoyenWang/category/1777370.html) — ARM64中断子系统深度分析博客

## 核心内容

### 4篇系列文章（Kernel 4.14, ARM64/Contex-A53）

| 篇 | 主题 | 关键内容 |
|----|------|----------|
| Part 1 | 中断控制器及驱动分析 | 硬件中断控制器架构、驱动实现 |
| Part 2 | 通用框架处理 | 通用中断处理框架源码分析 |
| Part 3 | softirq和tasklet | 软中断机制与tasklet实现 |
| Part 4 | Workqueue | 异步工作队列机制 |

## 资源特点

- **专注中断**: 最系统的中文ARM64中断子系统分析
- **源码导向**: "Read the fucking source code!"
- **图文丰富**: "A picture is worth a thousand words"
- **ARM64首发**: 聚焦嵌入式/移动端架构

## 与现有资源互补

补充 `linux-ebpf-fundamentals.md` 中未涉及的：
- 中断控制器硬件层面
- ARM64架构特有的中断处理

## 相关页面

- [[wiki/entities/linux/kernel/irq-softirq]] — 中断实体页（基于 arthurchiao）
- [[wiki/kernel-subsystems-index]] — 内核子系统总览
- [[bookmark-linux-inside]] — Linux Inside（包含中断章节）
- [[bookmark-linux-source-code-analyze]] — liexusong（中断处理话题）
