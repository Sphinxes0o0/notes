---
type: entity
tags: [linux-kernel, 声音系统, ALSA, PCM, ASoC, DAPM, 音频驱动]
created: 2026-05-20
sources: [notes-overview-kernel-sound]
---

# Linux Kernel Sound Subsystem

## 定义

Linux内核音频子系统，包含ALSA（Advanced Linux Sound Architecture）架构、OSS（Open Sound System）兼容层、ASoC（ALSA System on Chip）平台框架，提供PCM音频流、DAPM电源管理、DAI数字音频接口等核心功能。

## 关键要点

### ALSA vs OSS

| 特性 | ALSA | OSS |
|------|------|-----|
| 状态 | 当前主流 | 已废弃（仍保留兼容层） |
| API | alsa-lib | /dev/dsp |
| 混音 | 原生支持 | 通过模拟层 |
| 特点 | 内核原生，模块化 | 简单字符设备 |

### 核心数据结构

- **snd_card**: 声卡描述符，所有音频设备入口
- **snd_pcm**: PCM设备主体
- **snd_pcm_substream**: 子流（playback/capture）

### PCM接口

**关键流程**:
1. snd_pcm_hw_params(): 配置硬件参数
2. snd_pcm_readi/writei(): 读写音频数据
3. DMA缓冲区管理

**参数**:
- 采样率 (sample rate)
- 位深 (bit depth): 16bit, 24bit, 32bit
- 通道数 (channels): mono, stereo
- 周期 (period): 中断间隔
- 缓冲区 (buffer): DMA环形缓冲区

### ASoC框架

**三层架构**:
- **Machine Driver**: 绑定Platform和Codec
- **Platform Driver**: DMA、CPUDAI
- **Codec Driver**: 音频编解码器控制

**组件**:
- DAPM (Dynamic Audio Power Management): 运行时电源管理
- DAI (Digital Audio Interface): I2S, PCM, AC97等

**probe顺序**: Component → Platform → Codec → Machine

### DAPM (Dynamic Audio Power Management)

**widget**: 电源状态节点
- snd_soc_dapm_*_widget: 创建widget
- kcontrol: 控制接口

**path**: widget间连接
- snd_soc_dapm_connect(): 建立连接

**power状态机**:
- 根据path状态自动上下电
- 典型path: CPUDAI → Codec DAC → HP_OUT

### OSS兼容层

**模块**:
- soundcore: 注册声音设备
- pcm_oss: PCM OSS模拟
- snd_pcm_oss_*(): OSS兼容API

**转换**:
- open() → snd_pcm_oss_open()
- read/write → snd_pcm_oss_read/write()
- ioctl → snd_pcm_oss_ioctl()

### 源码位置

| 组件 | 路径 |
|------|------|
| ALSA核心 | sound/core/ |
| PCM | sound/core/pcm_lib.c |
| ASoC | sound/soc/ |
| OSS | sound/oss/ |

## 相关概念

- [[entities/linux/kernel/vfs/linux-kernel-vfs-core]] — 音频驱动通过 VFS 暴露设备节点
- [[entities/linux/kernel/virt/linux-kernel-virt-virtio]] — Virtio虚拟音频设备

## 来源详情
- [[sources/notes-kernel-sound]]
