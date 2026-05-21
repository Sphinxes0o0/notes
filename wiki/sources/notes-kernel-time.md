---
type: source
source-type: github
title: "Linux Kernel Time Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/github/notes/time/linux_kernel/
summary: "Linux内核时间子系统：tick、hrtimer、timekeeping、NTP、posix-timers"
tags: [linux-kernel, time]
created: 2026-05-20
---

# Linux Kernel Time Subsystem Notes

## 来源信息

- **路径**: raw/github/notes/time/linux_kernel/
- **文件数**: 3个文档（index + 2个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **time_subsystem.md**: tick、hrtimer、timekeeping、posix-timers概览
- **time_deep_dive_r1.md**: tick_device、timekeeper、NTP、hrtimer

## 关键概念

- jiffies: HZ频率时钟滴答
- NO_HZ Dynamic Tick: 按需tick减少功耗
- hrtimer: 红黑树管理，纳秒精度
- NTP: 网络时间协议校正

## 相关页面
- [[entities/linux/kernel/time/linux-kernel-time-core]]
