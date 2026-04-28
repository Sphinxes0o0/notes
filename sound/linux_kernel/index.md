# Linux Sound 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [sound_subsystem.md](sound_subsystem.md) | 声音子系统: ALSA, PCM, Mixer, ASoC | sound/ |
| [sound_deep_dive_r1.md](sound_deep_dive_r1.md) | 深度分析 R1: PCM, DAPM, ASoC DAI, DMA | sound/ |
| [sound_deep_dive_r2.md](sound_deep_dive_r2.md) | 深度分析 R2: snd_pcm_hw_params, snd_pcm_lib_ioctl, DAPM widget power, ASoC component probe | sound/ |

---

## 主要内容

### 1. ALSA vs OSS
- ALSA (Advanced Linux Sound Architecture)
- OSS (Open Sound System)

### 2. 核心数据结构
- struct snd_card: 声卡
- struct snd_pcm: PCM 设备
- struct snd_pcm_substream: 子流

### 3. PCM 接口
- snd_pcm_hw_params()
- snd_pcm_readi/writei()
- DMA 缓冲区

### 4. ASoC
- Machine Driver
- Platform Driver
- Codec Driver
- DAPM (动态音频电源管理)
- DAI (数字音频接口)

### 5. OSS 兼容层
- soundcore
- PCM OSS 模拟

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| ALSA 核心 | sound/core/ |
| PCM | sound/core/pcm_lib.c |
| ASoC | sound/soc/ |
| OSS | sound/oss/ |
