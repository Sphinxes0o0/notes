# Linux 内核声音子系统 (Sound Subsystem) 分析文档

## 目录

1. [概述](#1-概述)
2. [ALSA vs OSS 架构](#2-alsa-vs-oss-架构)
3. [ALSA 核心数据结构](#3-alsa-核心数据结构)
4. [PCM 接口详解](#4-pcm-接口详解)
5. [ALSA 驱动架构 (ASoC)](#5-alsa-驱动架构-asoc)
6. [OSS 兼容层](#6-oss-兼容层)
7. [缓冲区管理](#7-缓冲区管理)
8. [参考文献](#8-参考文献)

---

## 1. 概述

Linux 内核声音子系统是负责音频设备驱动和应用层音频数据交互的核心框架。主要包括:

- **ALSA (Advanced Linux Sound Architecture)**: 现代 Linux 主流音频架构
- **OSS (Open Sound System)**: 传统的声音系统,目前主要作为兼容层存在

### 1.1 源码位置

```
/Users/sphinx/github/linux/sound/
├── core/          # ALSA 核心代码
├── oss/           # OSS 兼容层 (实际在 core/oss/)
├── soc/           # ASoC (ALSA System on Chip) 驱动框架
├── pci/           # PCI 音频设备驱动
├── usb/           # USB 音频设备驱动
├── firewire/      # FireWire 音频设备驱动
└── ...
```

### 1.2 核心文件说明

| 文件路径 | 功能说明 |
|---------|---------|
| `sound/core/init.c` | 声卡初始化和管理 |
| `sound/core/pcm.c` | PCM 设备抽象层 |
| `sound/core/pcm_native.c` | PCM 原生 (Native) API 实现 |
| `sound/core/pcm_lib.c` | PCM 库函数 (读写操作) |
| `sound/core/control.c` | 混音器控制接口 |
| `sound/core/memalloc.c` | DMA 缓冲区分配 |
| `sound/sound_core.c` | 声音核心类注册 |
| `sound/soc/soc-core.c` | ASoC 核心框架 |

---

## 2. ALSA vs OSS 架构

### 2.1 架构对比图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户空间应用                               │
├─────────────────────────────────────────────────────────────────┤
│                     ALSA Library (libasound)                     │
│                    (alsa-lib 用户空间库)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐          │
│  │   ALSA Native    │              │  OSS Emulation   │          │
│  │   (/dev/snd/*)   │              │  (/dev/dsp, etc) │          │
│  └────────┬─────────┘              └────────┬─────────┘          │
│           │                                 │                     │
├───────────┴─────────────────────────────────┴───────────────────┤
│                         ALSA Core                                 │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  sound/core/                                            │    │
│  │  ├── init.c        - 声卡注册/注销                       │    │
│  │  ├── pcm.c         - PCM 设备管理                       │    │
│  │  ├── pcm_native.c  - Native PCM API (ioctl)             │    │
│  │  ├── pcm_lib.c     - PCM 读写库函数                      │    │
│  │  ├── control.c     - Mixer 控制接口                     │    │
│  │  └── memalloc.c    - DMA 内存分配                       │    │
│  └──────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  ASoC Drivers  │  │   PCI Drivers  │  │   USB Drivers   │   │
│  │  (soc/*)       │  │   (pci/*)     │  │   (usb/*)      │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                        Hardware (CODEC/DMA/CPU)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 OSS 兼容层

OSS 兼容层位于 `sound/core/oss/`,提供对传统 OSS API 的支持:

```c
// sound/core/oss/pcm_oss.c
static int snd_pcm_oss_get_rate(struct snd_pcm_oss_file *pcm_oss_file);
static int snd_pcm_oss_get_channels(struct snd_pcm_oss_file *pcm_oss_file);
static int snd_pcm_oss_get_format(struct snd_pcm_oss_file *pcm_oss_file);
```

**关键特点**:
- 通过 `CONFIG_SND_OSSEMUL` 配置启用
- 将 OSS API 调用转换为 ALSA 内部调用
- 支持 `/dev/dsp`, `/dev/audio` 等传统设备节点

---

## 3. ALSA 核心数据结构

### 3.1 struct snd_card (声卡结构)

**定义位置**: `include/sound/core.h` (第 80-148 行)

```c
struct snd_card {
    int number;                  /* 声卡编号 (索引到 snd_cards) */

    char id[16];                /* 声卡 ID 字符串 */
    char driver[16];            /* 驱动名称 */
    char shortname[32];         /* 声卡短名称 */
    char longname[80];          /* 声卡完整名称 */
    char mixername[80];         /* 混音器名称 */
    char components[128];       /* 声卡组件列表 */

    struct module *module;      /* 顶层模块 */

    void *private_data;         /* 私有数据 */
    void (*private_free)(struct snd_card *card);  /* 私有数据释放回调 */

    struct list_head devices;   /* 设备链表 */

    unsigned int last_numid;    /* 最后使用的数字 ID */
    struct rw_semaphore controls_rwsem;  /* 控制锁 */
    rwlock_t controls_rwlock;   /* 控制查找锁 */
    int controls_count;         /* 控制项数量 */
    struct list_head controls;  /* 所有控制项 */
    struct list_head ctl_files; /* 活跃的控制文件 */

    struct snd_info_entry *proc_root;    /* /proc 入口 */
    struct device card_dev;    /* 声卡设备对象 (sysfs) */

#ifdef CONFIG_PM
    unsigned int power_state;   /* 电源状态 */
    atomic_t power_ref;
#endif

#if IS_ENABLED(CONFIG_SND_MIXER_OSS)
    struct snd_mixer_oss *mixer_oss;    /* OSS 混音器 */
#endif
};
```

**创建声卡**:
```c
// sound/core/init.c (第 171-194 行)
int snd_card_new(struct device *parent, int idx, const char *xid,
                 struct module *module, int extra_size,
                 struct snd_card **card_ret);
```

### 3.2 struct snd_pcm (PCM 设备)

**定义位置**: `include/sound/pcm.h` (第 534-554 行)

```c
struct snd_pcm {
    struct snd_card *card;          /* 所属声卡 */
    struct list_head list;          /* PCM 设备链表 */
    int device;                     /* 设备编号 */

    unsigned int info_flags;        /* 信息标志 */
    unsigned short dev_class;       /* 设备类 */
    unsigned short dev_subclass;    /* 设备子类 */

    char id[64];                    /* PCM ID */
    char name[80];                  /* PCM 名称 */

    struct snd_pcm_str streams[2];  /* 0=Playback, 1=Capture */

    struct mutex open_mutex;        /* 打开互斥锁 */
    wait_queue_head_t open_wait;    /* 打开等待队列 */

    void *private_data;             /* 私有数据 */
    void (*private_free)(struct snd_pcm *pcm);  /* 释放回调 */

    bool internal;                  /* 内部 PCM 标志 */
    bool nonatomic;                 /* 非原子操作标志 */
};
```

**PCM 流结构** (`struct snd_pcm_str`):
```c
struct snd_pcm_str {
    int stream;                     /* 流方向 (Playback/Capture) */
    struct snd_pcm *pcm;
    unsigned int substream_count;    /* 子流数量 */
    unsigned int substream_opened;   /* 已打开的子流数 */
    struct snd_pcm_substream *substream;  /* 子流链表 */
};
```

### 3.3 struct snd_pcm_substream (子流)

**定义位置**: `include/sound/pcm.h` (第 464-508 行)

```c
struct snd_pcm_substream {
    struct snd_pcm *pcm;            /* 所属 PCM 设备 */
    struct snd_pcm_str *pstr;       /* 所属流 */

    void *private_data;             /* 私有数据 (复制自 pcm->private_data) */
    int number;                     /* 子流编号 */
    char name[32];                  /* 子流名称 */

    int stream;                     /* 流方向 (SNDRV_PCM_STREAM_*) */

    /* 硬件操作函数集 */
    const struct snd_pcm_ops *ops;

    /* 运行时信息 */
    struct snd_pcm_runtime *runtime;  /* 运行时数据 (关键!) */

    struct snd_timer *timer;        /* 定时器 */
    unsigned timer_running: 1;        /* 定时器运行标志 */

    long wait_time;                  /* 等待时间 (毫秒) */

    /* 链接的子流 */
    struct snd_pcm_substream *next;
    struct list_head link_list;
    struct snd_pcm_group *group;    /* 当前组 */

    int ref_count;                   /* 引用计数 */
    atomic_t mmap_count;            /* mmap 引用计数 */

    unsigned int f_flags;            /* 文件标志 */
    void (*pcm_release)(struct snd_pcm_substream *);
    struct pid *pid;                 /* 所属进程 PID */

    unsigned int hw_opened: 1;       /* 硬件已打开标志 */
};
```

### 3.4 struct snd_pcm_runtime (运行时数据)

运行时数据是 PCM 子流中最重要的数据结构之一,包含音频数据缓冲区的所有信息:

```c
struct snd_pcm_runtime {
    /* 状态信息 */
    snd_pcm_state_t state;          /* 当前状态 */
    volatile snd_pcm_uframes_t hw_ptr;   /* 硬件指针 */
    snd_pcm_uframes_t hw_ptr_base;   /* 硬件指针基址 */
    snd_pcm_uframes_t hw_ptr_interrupt; /* 中断时的硬件指针 */

    /* 应用指针 */
    struct snd_pcm_mmap_control *control;  /* 应用指针控制 */

    /* 硬件参数 */
    struct snd_pcm_hardware hw;      /* 硬件能力 */
    struct snd_pcm_sw_params sw_params;  /* 软件参数 */

    /* 缓冲区信息 */
    snd_pcm_uframes_t buffer_size;   /* 缓冲区大小 (帧) */
    snd_pcm_uframes_t period_size;   /* 周期大小 (帧) */
    snd_pcm_uframes_t periods;       /* 周期数量 */
    snd_pcm_uframes_t period_step;   /* 周期步进 */

    /* DMA 缓冲区 */
    void *dma_area;                  /* DMA 缓冲区地址 (虚拟) */
    dma_addr_t dma_addr;             /* DMA 缓冲区物理地址 */
    size_t dma_bytes;                 /* DMA 缓冲区大小 (字节) */

    /* 格式信息 */
    snd_pcm_format_t format;         /* 采样格式 */
    unsigned int rate;               /* 采样率 */
    unsigned int channels;           /* 声道数 */
    size_t frame_bytes;              /* 每帧字节数 */

    /* 传输信息 */
    snd_pcm_uframes_t boundary;      /* 边界 (用于指针回绕) */

    /* 静音处理 */
    snd_pcm_uframes_t silence_size;  /* 静音区大小 */
    snd_pcm_uframes_t silence_threshold; /* 静音阈值 */
    snd_pcm_uframes_t silence_filled; /* 已填充的静音量 */

    /* 时间信息 */
    snd_pcm_uframes_t delay;         /* 延迟 (帧) */
};
```

### 3.5 重要关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                        struct snd_card                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ devices (list_head) ──────────────────────────────────┐│    │
│  └─────────────────────────────────────────────────────────┘│    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        struct snd_pcm                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ card ──────────► snd_card                               │    │
│  │ streams[2] ─────┬──────────────────────────────────┐   │    │
│  │                 │                                  │   │    │
│  │  [0] Playback  │  [1] Capture                     │   │    │
│  └─────────────────┼──────────────────────────────────┘   │    │
└─────────────────────┼─────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   struct snd_pcm_substream                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ pcm ────────────► snd_pcm                              │    │
│  │ pstr ───────────► snd_pcm_str                          │    │
│  │ ops ────────────► snd_pcm_ops (硬件操作函数集)          │    │
│  │ runtime ───────► snd_pcm_runtime (关键!)               │    │
│  │ timer ─────────► snd_timer                            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. PCM 接口详解

### 4.1 PCM 硬件参数 (snd_pcm_hw_params)

**定义位置**: `include/sound/pcm.h`

```c
struct snd_pcm_hw_params {
    unsigned int flags;              /* 标志 */
    struct snd_mask masks[SNDRV_PCM_HW_PARAM_LAST_MASK -
                           SNDRV_PCM_HW_PARAM_FIRST_MASK + 1];
    struct snd_interval intervals[SNDRV_PCM_HW_PARAM_LAST_INTERVAL -
                                   SNDRV_PCM_HW_PARAM_FIRST_INTERVAL + 1];
    unsigned int rmask;              /* 请求的掩码 */
    unsigned int cmask;              /* 已改变的掩码 */
    unsigned int info;               /* 支持的信息 */
    unsigned int msbits;             /* 主采样位数 */
    unsigned int rate_num;           /* 分子 */
    unsigned int rate_den;           /* 分母 */
    snd_pcm_uframes_t fifo_size;     /* FIFO 大小 */
    unsigned char reserved[64];      /* 保留 */
};
```

**参数类型枚举**:
```c
typedef int __bitwise snd_pcm_hw_param_t;
#define SNDRV_PCM_HW_PARAM_ACCESS         ((__force snd_pcm_hw_param_t) 0)
#define SNDRV_PCM_HW_PARAM_FORMAT         ((__force snd_pcm_hw_param_t) 1)
#define SNDRV_PCM_HW_PARAM_SUBFORMAT      ((__force snd_pcm_hw_param_t) 2)
#define SNDRV_PCM_HW_PARAM_SAMPLE_BITS     ((__force snd_pcm_hw_param_t) 8)
#define SNDRV_PCM_HW_PARAM_FRAME_BITS      ((__force snd_pcm_hw_param_t) 9)
#define SNDRV_PCM_HW_PARAM_CHANNELS        ((__force snd_pcm_hw_param_t) 10)
#define SNDRV_PCM_HW_PARAM_RATE            ((__force snd_pcm_hw_param_t) 11)
#define SNDRV_PCM_HW_PARAM_PERIOD_TIME     ((__force snd_pcm_hw_param_t) 15)
#define SNDRV_PCM_HW_PARAM_PERIOD_SIZE     ((__force snd_pcm_hw_param_t) 16)
#define SNDRV_PCM_HW_PARAM_BUFFER_TIME     ((__force snd_pcm_hw_param_t) 17)
#define SNDRV_PCM_HW_PARAM_BUFFER_SIZE     ((__force snd_pcm_hw_param_t) 18)
#define SNDRV_PCM_HW_PARAM_PERIODS         ((__force snd_pcm_hw_param_t) 19)
```

### 4.2 硬件操作函数集 (snd_pcm_ops)

**定义位置**: `include/sound/pcm.h` (第 55-79 行)

```c
struct snd_pcm_ops {
    int (*open)(struct snd_pcm_substream *substream);
    int (*close)(struct snd_pcm_substream *substream);

    int (*ioctl)(struct snd_pcm_substream *substream,
                 unsigned int cmd, void *arg);

    int (*hw_params)(struct snd_pcm_substream *substream,
                     struct snd_pcm_hw_params *params);

    int (*hw_free)(struct snd_pcm_substream *substream);

    int (*prepare)(struct snd_pcm_substream *substream);

    int (*trigger)(struct snd_pcm_substream *substream, int cmd);

    int (*sync_stop)(struct snd_pcm_substream *substream);

    snd_pcm_uframes_t (*pointer)(struct snd_pcm_substream *substream);

    int (*get_time_info)(struct snd_pcm_substream *substream,
                         struct timespec64 *system_ts,
                         struct timespec64 *audio_ts, ...);

    int (*fill_silence)(struct snd_pcm_substream *substream, int channel,
                        unsigned long pos, unsigned long bytes);

    int (*copy)(struct snd_pcm_substream *substream, int channel,
                unsigned long pos, struct iov_iter *iter, unsigned long bytes);

    struct page *(*page)(struct snd_pcm_substream *substream,
                         unsigned long offset);

    int (*mmap)(struct snd_pcm_substream *substream,
                struct vm_area_struct *vma);

    int (*ack)(struct snd_pcm_substream *substream);
};
```

### 4.3 snd_pcm_hw_params() 函数

**功能**: 设置硬件参数

**实现位置**: `sound/core/pcm_native.c`

```c
static int snd_pcm_hw_params(struct snd_pcm_substream *substream,
                            struct snd_pcm_hw_params *params)
{
    struct snd_pcm_runtime *runtime = substream->runtime;
    int err;

    /* 参数精炼 (refine) */
    err = snd_pcm_hw_refine(substream, params);
    if (err < 0)
        return err;

    /* 调用驱动的 hw_params 回调 */
    if (substream->ops->hw_params) {
        err = substream->ops->hw_params(substream, params);
        if (err < 0)
            return err;
    }

    /* 更新运行时参数 */
    runtime->hw = *hw;
    runtime->buffer_size = buffer_size;
    runtime->period_size = period_size;
    runtime->periods = periods;
    runtime->rate = rate;
    runtime->channels = channels;
    runtime->format = format;

    return 0;
}
```

### 4.4 PCM 读写函数

**读写函数族**:

| 函数 | 说明 |
|-----|------|
| `snd_pcm_lib_write()` | 交错式写入 (interleaved) |
| `snd_pcm_lib_read()` | 交错式读取 (interleaved) |
| `snd_pcm_lib_writev()` | 非交错式写入 (non-interleaved) |
| `snd_pcm_lib_readv()` | 非交错式读取 (non-interleaved) |
| `snd_pcm_kernel_write()` | 内核空间写入 |
| `snd_pcm_kernel_read()` | 内核空间读取 |

**实现位置**: `include/sound/pcm.h` (第 1187-1220 行)

```c
// 交错式写入
static inline snd_pcm_sframes_t
snd_pcm_lib_write(struct snd_pcm_substream *substream,
                   const void __user *buf, snd_pcm_uframes_t frames)
{
    return __snd_pcm_lib_xfer(substream, (void __force *)buf,
                               true, frames, false);
}

// 非交错式写入
static inline snd_pcm_sframes_t
snd_pcm_lib_writev(struct snd_pcm_substream *substream,
                    void __user **bufs, snd_pcm_uframes_t frames)
{
    return __snd_pcm_lib_xfer(substream, (void *)bufs,
                               false, frames, false);
}

// 内核空间写入
static inline snd_pcm_sframes_t
snd_pcm_kernel_write(struct snd_pcm_substream *substream,
                      const void *buf, snd_pcm_uframes_t frames)
{
    return __snd_pcm_lib_xfer(substream, (void *)buf,
                               true, frames, true);
}
```

**核心传输函数**: `__snd_pcm_lib_xfer()`

**实现位置**: `sound/core/pcm_lib.c` (第 2271-2379 行)

```c
snd_pcm_sframes_t __snd_pcm_lib_xfer(struct snd_pcm_substream *substream,
                                     void *data, bool interleaved,
                                     snd_pcm_uframes_t size, bool in_kernel)
{
    struct snd_pcm_runtime *runtime = substream->runtime;
    snd_pcm_uframes_t xfer = 0;
    snd_pcm_uframes_t offset = 0;
    snd_pcm_uframes_t avail;
    pcm_copy_f writer;
    pcm_transfer_f transfer;
    bool nonblock;
    bool is_playback;
    int err;

    err = pcm_sanity_check(substream);
    if (err < 0)
        return err;

    is_playback = substream->stream == SNDRV_PCM_STREAM_PLAYBACK;

    /* 根据交错模式选择写入函数 */
    if (interleaved) {
        writer = interleaved_copy;
    } else {
        writer = noninterleaved_copy;
    }

    /* 设置传输函数 */
    if (substream->ops->copy)
        transfer = substream->ops->copy;
    else
        transfer = is_playback ? default_write_copy : default_read_copy;

    nonblock = !!(substream->f_flags & O_NONBLOCK);

    snd_pcm_stream_lock_irq(substream);

    /* 检查状态 */
    err = pcm_accessible_state(runtime);
    if (err < 0)
        goto _end_unlock;

    runtime->twake = runtime->control->avail_min ? : 1;
    if (runtime->state == SNDRV_PCM_STATE_RUNNING)
        snd_pcm_update_hw_ptr(substream);

    /* 启动捕获流 */
    if (!is_playback && runtime->state == SNDRV_PCM_STATE_PREPARED &&
        size >= runtime->start_threshold) {
        err = snd_pcm_start(substream);
        if (err < 0)
            goto _end_unlock;
    }

    avail = snd_pcm_avail(substream);

    /* 主循环: 处理所有数据 */
    while (size > 0) {
        snd_pcm_uframes_t frames, appl_ptr, appl_ofs;
        snd_pcm_uframes_t cont;

        if (!avail) {
            /* 等待可用空间 */
            if (nonblock) {
                err = -EAGAIN;
                goto _end_unlock;
            }
            err = wait_for_avail(substream, &avail);
            if (err < 0)
                goto _end_unlock;
        }

        frames = size > avail ? avail : size;
        appl_ptr = READ_ONCE(runtime->control->appl_ptr);
        appl_ofs = appl_ptr % runtime->buffer_size;
        cont = runtime->buffer_size - appl_ofs;
        if (frames > cont)
            frames = cont;

        /* 执行数据传输 */
        snd_pcm_stream_unlock_irq(substream);
        err = do_transfer(substream, 0, appl_ofs, data, frames, transfer, in_kernel);
        snd_pcm_stream_lock_irq(substream);

        if (err < 0)
            goto _end_unlock;

        /* 更新指针 */
        appl_ptr += frames;
        if (appl_ptr >= runtime->boundary)
            appl_ptr -= runtime->boundary;
        runtime->control->appl_ptr = appl_ptr;

        size -= frames;
        xfer += frames;
        avail -= frames;
    }

_end_unlock:
    snd_pcm_stream_unlock_irq(substream);
    return xfer > 0 ? (snd_pcm_sframes_t)xfer : err;
}
```

---

## 5. ALSA 驱动架构 (ASoC)

### 5.1 ASoC 概述

ASoC (ALSA System on Chip) 是为嵌入式系统设计的音频驱动框架,将音频设备分为三个独立组件:

- **Codec Driver**: 音频编解码器 (ADC/DAC/放大器等)
- **Platform Driver**: 平台相关驱动 (DMA/SoC 内核)
- **Machine Driver**: 机器特定驱动 (连接 codec 和 platform)

### 5.2 ASoC 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户空间应用                               │
├─────────────────────────────────────────────────────────────────┤
│                      ALSA Library                                │
├─────────────────────────────────────────────────────────────────┤
│                        ALSA Core                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  sound/core/                                           │    │
│  │  pcm_native.c, pcm_lib.c, control.c, ...               │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                     ASoC (sound/soc/)                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  soc-core.c    - ASoC 核心                              │    │
│  │  soc-pcm.c     - PCM DPCM 处理                         │    │
│  │  soc-dapm.c    - DAPM (动态音频电源管理)                 │    │
│  │  soc-dai.c     - DAI (数字音频接口) 管理                │    │
│  │  soc-ops.c     - 操作函数                              │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Machine    │    │   Platform   │    │    Codec     │     │
│  │   Driver     │    │   Driver     │    │    Driver    │     │
│  │              │    │              │    │              │     │
│  │ - 绑定 DAI   │    │ - DMA 驱动   │    │ - CODEC 寄存器│    │
│  │ - 配置路由   │    │ - I2S/PCM    │    │ - 音量控制   │    │
│  │ - 注册声卡   │    │ - CPU DAI    │    │ - Jack 检测  │    │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                        Hardware                                   │
│     ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│     │   CPU    │◄──►│   SoC    │◄──►│   CODEC  │              │
│     │   SoC    │    │   DMA    │    │  (音频芯片)│              │
│     └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 struct snd_soc_card (声卡结构)

**定义位置**: `include/sound/soc.h` (第 972 行起)

```c
struct snd_soc_card {
    const char *name;               /* 声卡名称 */
    const char *long_name;          /* 完整名称 */
    const char *driver_name;        /* 驱动名称 */
    const char *components;         /* 组件列表 */

    struct device *dev;              /* 设备指针 */
    struct snd_card *snd_card;      /* ALSA 声卡 */
    struct module *owner;           /* 模块所有者 */

    struct mutex mutex;              /* 互斥锁 */
    struct mutex dapm_mutex;         /* DAPM 互斥锁 */

    /* DAI 链接 */
    struct snd_soc_dai_link *dai_link;
    int num_links;                   /* DAI 链接数量 */

    /* 组件 */
    struct snd_soc_component *components;
    int num_components;

    /* 绑定/探测 */
    int (*probe)(struct snd_soc_card *card);
    int (*late_probe)(struct snd_soc_card *card);
    int (*remove)(struct snd_soc_card *card);

    /* 电源管理 */
    int (*suspend_pre)(struct snd_soc_card *card);
    int (*suspend_post)(struct snd_soc_card *card);
    int (*resume_pre)(struct snd_soc_card *card);
    int (*resume_post)(struct snd_soc_card *card);

    /* DAPM 路径 */
    struct snd_soc_dapm_context dapm;
    struct snd_soc_dapm_widget *widgets;
    struct snd_soc_dapm_route *routes;

    /* 混音器控制 */
    struct snd_kcontrol *controls;
    const struct snd_soc_control_probe *controls_probe;
    int num_controls;

    /* 用于蓝线音频的 jack 报告 */
    struct snd_soc_jack *jack;

    /* DMI 信息 */
#ifdef CONFIG_DMI
    char dmi_longname[80];
#endif
};
```

### 5.4 struct snd_soc_pcm_runtime (PCM 运行时)

**定义位置**: `include/sound/soc.h` (第 1143-1193 行)

```c
struct snd_soc_pcm_runtime {
    struct device *dev;              /* 设备 */
    struct snd_soc_card *card;      /* 所属声卡 */
    struct snd_soc_dai_link *dai_link;  /* DAI 链接 */

    struct snd_pcm_ops ops;         /* PCM 操作函数集 */

    /* 动态 PCM BE 运行时数据 */
    struct snd_soc_dpcm_runtime dpcm[SNDRV_PCM_STREAM_LAST + 1];

    long pmdown_time;               /* 断电延迟时间 */

    /* 运行时设备 */
    struct snd_pcm *pcm;            /* PCM 设备 */
    struct snd_compr *compr;        /* 压缩设备 */

    /* DAIs = cpu_dai + codec_dai */
    struct snd_soc_dai **dais;
    void *private_data;             /* 私有数据 */
};
```

### 5.5 DAI (数字音频接口)

**定义位置**: `include/sound/soc-dai.h`

```c
struct snd_soc_dai_driver {
    const char *name;               /* DAI 名称 */
    unsigned int id;                /* DAI ID */

    /* 播放/捕获流 */
    struct snd_soc_pcm_stream playback;
    struct snd_soc_pcm_stream capture;

    /* 对称参数 */
    unsigned int symmetric_rate:1;
    unsigned int symmetric_channels:1;
    unsigned int symmetric_sample_bits:1;

    /* 操作函数 */
    struct snd_soc_dai_ops *ops;
    struct snd_soc_dai_driver *auto_dai;
};
```

### 5.6 DAPM (动态音频电源管理)

DAPM 是 ASoC 中的电源管理机制,根据音频路径的电源状态自动切换:

```c
/* 路径类型 */
enum snd_soc_dapm_type {
    snd_soc_dapm_input,     /* 输入 */
    snd_soc_dapm_output,    /* 输出 */
    snd_soc_dapm_mux,       /* 多路复用器 */
    snd_soc_dapm mixer,     /* 混音器 */
    snd_soc_dapm_pga,       /* 可编程增益放大器 */
    snd_soc_dapm_adc,       /* ADC */
    snd_soc_dapm_dac,       /* DAC */
    snd_soc_dapm_micbias,   /* 麦克风偏置 */
    snd_soc_dapm_vmid,      /* 电压基准 */
    snd_soc_dapm_supply,    /* 电源供应 */
    snd_soc_dapm_regulator_supply, /* 稳压器 */
    snd_soc_dapm_clock_supply,     /* 时钟供应 */
    /* ... 更多类型 */
};
```

---

## 6. OSS 兼容层

### 6.1 soundcore 核心

**定义位置**: `sound/sound_core.c`

soundcore 是 OSS 和 ALSA 共用的底层接口:

```c
/* sound/sound_core.c (第 37-41 行) */
const struct class sound_class = {
    .name = "sound",
    .devnode = sound_devnode,
};
```

**设备注册**:
```c
/* sound/sound_core.c */
static int soundcore_open(struct inode *inode, struct file *file)
{
    /* 根据次设备号路由到对应的驱动 */
    int minor = iminor(inode);
    struct sound_unit *unit;

    /* 查找注册的单元 */
    for (unit = chains[minor >> 4]; unit; unit = unit->next) {
        if (unit->unit_minor == minor)
            return fops_get(unit->unit_fops)->open(inode, file);
    }
    return -ENODEV;
}
```

### 6.2 OSS PCM 模拟

**实现位置**: `sound/core/oss/pcm_oss.c`

OSS 兼容层将 OSS API 映射到 ALSA API:

```c
/* OSS 格式到 ALSA 格式的转换 */
static int oss_format_to_alsa(int format)
{
    switch (format) {
    case AFMT_MU_LAW:    return SNDRV_PCM_FORMAT_MU_LAW;
    case AFMT_A_LAW:     return SNDRV_PCM_FORMAT_A_LAW;
    case AFMT_U8:        return SNDRV_PCM_FORMAT_U8;
    case AFMT_S16_LE:    return SNDRV_PCM_FORMAT_S16_LE;
    case AFMT_S16_BE:    return SNDRV_PCM_FORMAT_S16_BE;
    case AFMT_S8:        return SNDRV_PCM_FORMAT_S8;
    case AFMT_U16_LE:    return SNDRV_PCM_FORMAT_U16_LE;
    case AFMT_U16_BE:    return SNDRV_PCM_FORMAT_U16_BE;
    /* ... */
    default:             return -EINVAL;
    }
}
```

### 6.3 OSS 设备映射

| OSS 设备 | ALSA 设备 | 说明 |
|---------|----------|------|
| `/dev/dsp` | `/dev/snd/pcmC0D0p` | 主播放设备 |
| `/dev/dsp1` | `/dev/snd/pcmC0D1p` | 第二个播放设备 |
| `/dev/audio` | `/dev/snd/pcmC0D0p` | 主音频设备 |
| `/dev/mixer` | `/dev/snd/controlC0` | 混音器设备 |
| `/dev/sequencer` | `/dev/snd/seq` | 序列器设备 |

---

## 7. 缓冲区管理

### 7.1 DMA 缓冲区分配

**实现位置**: `sound/core/memalloc.c`

```c
/* DMA 缓冲区分配操作 */
struct snd_malloc_ops {
    void *(*alloc)(struct snd_dma_buffer *dmab, size_t size);
    void (*free)(struct snd_dma_buffer *dmab);
    dma_addr_t (*get_addr)(struct snd_dma_buffer *dmab, size_t offset);
    struct page *(*get_page)(struct snd_dma_buffer *dmab, size_t offset);
    int (*mmap)(struct snd_dma_buffer *dmab, struct vm_area_struct *area);
    void (*sync)(struct snd_dma_buffer *dmab, enum snd_dma_sync_mode mode);
};

/* 分配 DMA 缓冲区 */
int snd_dma_alloc_dir_pages(int type, struct device *device,
                            enum dma_data_direction dir, size_t size,
                            struct snd_dma_buffer *dmab);
```

### 7.2 环形缓冲区结构

```
┌─────────────────────────────────────────────────────────────────┐
│                    PCM 环形缓冲区 (Ring Buffer)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Period 0                              │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │              音频数据帧                            │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Period 1                              │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │              音频数据帧                            │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Period N-1                            │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │              音频数据帧                            │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│   ◄────────── buffer_size (总大小) ──────────►                   │
│   ◄── period_size ──►  (每个周期的大小)                          │
│   periods = buffer_size / period_size                             │
└─────────────────────────────────────────────────────────────────┘

指针关系:
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│   hw_ptr: 硬件写入位置 (由 DMA 中断更新)                          │
│   appl_ptr: 应用读取/写入位置 (由应用程序更新)                     │
│                                                                   │
│   available = hw_ptr - appl_ptr (播放)                            │
│   available = buffer_size - (hw_ptr - appl_ptr) (录音)            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 缓冲区参数计算

```c
/* 帧大小计算 */
frame_bytes = channels * bytes_per_sample;

/* 缓冲区大小计算 */
buffer_bytes = period_size * periods * frame_bytes;

/* 可用空间计算 */
snd_pcm_uframes_t snd_pcm_avail(struct snd_pcm_substream *substream)
{
    struct snd_pcm_runtime *runtime = substream->runtime;
    snd_pcm_uframes_t avail;

    if (runtime->state == SNDRV_PCM_STATE_RUNNING)
        snd_pcm_update_hw_ptr(substream);

    avail = runtime->hw_ptr_wrap * runtime->boundary +
            runtime->status->hw_ptr -
            runtime->control->appl_ptr;

    if (avail > runtime->boundary)
        avail -= runtime->boundary;

    return avail;
}
```

---

## 8. 参考文献

### 8.1 内核源码文件

| 文件 | 说明 |
|-----|------|
| `include/sound/core.h` | ALSA 核心定义 |
| `include/sound/pcm.h` | PCM 定义 |
| `include/sound/soc.h` | ASoC 核心定义 |
| `include/sound/soc-dai.h` | DAI 定义 |
| `include/sound/soc-dapm.h` | DAPM 定义 |
| `sound/core/init.c` | 声卡初始化 |
| `sound/core/pcm.c` | PCM 设备管理 |
| `sound/core/pcm_native.c` | PCM Native API |
| `sound/core/pcm_lib.c` | PCM 库函数 |
| `sound/core/memalloc.c` | DMA 内存分配 |
| `sound/sound_core.c` | 声音核心类 |
| `sound/soc/soc-core.c` | ASoC 核心 |
| `sound/soc/soc-pcm.c` | ASoC PCM |
| `sound/soc/soc-dapm.c` | DAPM 实现 |
| `sound/core/oss/pcm_oss.c` | OSS 兼容层 |

### 8.2 用户空间接口

- **ALSA Library (alsa-lib)**: 用户空间 API 库
- **ALSA Utilities (alsa-utils)**: amixer, aplay, arecord 等工具
- **PulseAudio**: 高级音频服务
- **PipeWire**: 新一代多媒体框架

### 8.3 配置选项

```makefile
# Kconfig 相关选项
CONFIG_SND=y                # ALSA 核心
CONFIG_SND_CORE=y           # ALSA 核心
CONFIG_SND_PCM=y            # PCM 支持
CONFIG_SND_TIMER=y          # 定时器支持
CONFIG_SND_HWDEP=y          # 硬件依赖设备
CONFIG_SND_OSSEMUL=y        # OSS 兼容层
CONFIG_SND_MIXER_OSS=y      # OSS 混音器
CONFIG_SND_PCM_OSS=y        # OSS PCM
CONFIG_SND_SOC=y            # ASoC 支持
CONFIG_SND_SOC_CORE=y       # ASoC 核心
```

---

## 附录 A: 关键数据结构关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户空间应用                                   │
│                   (aplay, arecord, etc.)                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ALSA Library (libasound)                        │
│              snd_pcm_writei(), snd_pcm_readi(), etc.               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ALSA Kernel Interface                             │
│                   (/dev/snd/pcmC0D0p, etc.)                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ALSA Core                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ pcm_native.c                                                │   │
│  │   - snd_pcm_ioctl()    (ioctl 入口)                         │   │
│  │   - snd_pcm_hw_params() (参数设置)                          │   │
│  │   - snd_pcm_prepare()   (准备)                              │   │
│  │   - snd_pcm_trigger()   (触发)                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ pcm_lib.c                                                   │   │
│  │   - __snd_pcm_lib_xfer()  (数据传输)                        │   │
│  │   - snd_pcm_playback_silence() (静音填充)                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    snd_pcm_substream                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ runtime->                                                     │   │
│  │   - hw (snd_pcm_hardware)    硬件能力                        │   │
│  │   - buffer_size, period_size 缓冲区参数                      │   │
│  │   - dma_area                 DMA 缓冲区虚拟地址              │   │
│  │   - format, rate, channels   音频格式参数                    │   │
│  │   - control->appl_ptr        应用指针                        │   │
│  │   - status->hw_ptr          硬件指针                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ops->                                                        │   │
│  │   - pointer()     返回当前硬件指针                          │   │
│  │   - trigger()     启动/停止 DMA                             │   │
│  │   - copy()       数据拷贝函数 (可选)                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Hardware                                     │
│        CPU (DMA) ◄──────────────────────► CODEC                     │
│     (I2S/PCM)                          (ADC/DAC)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

*文档版本: 1.0*
*生成时间: 2026-04-26*
*内核版本: Linux 7.0 (master branch)*
