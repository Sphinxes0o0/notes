---
type: source
source-type: github
title: "Linux Kernel Locking Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/notes/locking/linux_kernel/
summary: "Linux内核锁子系统：spinlock、mutex、rwsem、percpu、lockdep调试"
tags: [linux-kernel, locking]
sources: [notes-kernel-locking]
created: 2026-05-20
---

# Linux Kernel Locking Subsystem Notes

## 来源信息

- **路径**: raw/notes/locking/linux_kernel/
- **文件数**: 3个文档（index + 2个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **locking_subsystem.md**: spinlock、mutex、rwsem、percpu API概览
- **locking_deep_dive_r2.md**: MCS队列、mutex活锁、rwsem优化、lockdep环检测

## 关键概念

- 自旋锁: preempt_disable + 循环等待
- mutex乐观自旋: MCS队列确保单一等待者自旋
- percpu_counter: 批量更新减少锁竞争
- lockdep: 依赖追踪检测死锁

## 相关页面
- [[entities/linux/kernel/locking/linux-kernel-locking-core]]
