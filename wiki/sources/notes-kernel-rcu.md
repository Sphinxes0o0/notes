---
type: source
source-type: github
title: "Linux Kernel RCU Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/github/notes/rcu/linux_kernel/
summary: "Linux内核RCU子系统：Read-Copy-Update、无锁同步、宽限期、grace period"
tags: [linux-kernel, rcu]
created: 2026-05-20
---

# Linux Kernel RCU Subsystem Notes

## 来源信息

- **路径**: raw/github/notes/rcu/linux_kernel/
- **文件数**: 3个文档（index + 2个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **rcu_subsystem.md**: RCU原理、核心数据结构、同步/回调API
- **rcu_deep_dive_r2.md**: grace period、srcu、rcu_node层次、NOCB

## 关键概念

- 无锁读取: rcu_read_lock/unlock
- 宽限期: 所有读者完成后再释放
- srcu: Sleepable RCU，可睡眠上下文
- NOCB: No-CB RCU，减少锁竞争

## 相关页面
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]]
