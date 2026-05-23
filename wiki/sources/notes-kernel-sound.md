---
type: source
source-type: github
title: "Linux Kernel Sound Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/github/notes/sound/linux_kernel/
summary: "Linux内核声音子系统：ALSA架构、PCM、ASoC、DAPM、DAI数字音频接口"
tags: [linux-kernel, sound]
sources: [notes-kernel-sound]
created: 2026-05-20
---

# Linux Kernel Sound Subsystem Notes

## 来源信息

- **路径**: raw/github/notes/sound/linux_kernel/
- **文件数**: 4个文档（index + 3个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **sound_subsystem.md**: ALSA vs OSS、PCM、ASoC概览
- **sound_deep_dive_r1.md**: PCM、DAPM、ASoC DAI、DMA
- **sound_deep_dive_r2.md**: snd_pcm_hw_params、DAPM widget power、component probe

## 关键概念

- ALSA: 当前主流架构，模块化设计
- ASoC三层: Machine + Platform + Codec
- DAPM: 动态音频电源管理，widget path自动上下电
- PCM: 采样率、位深、周期、缓冲区DMA

## 相关页面
- [[entities/linux/kernel/sound/linux-kernel-sound-core]]
