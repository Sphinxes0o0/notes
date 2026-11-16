# Linux Kernel Sound 子系统深度分析文档

**版本**: R1
**日期**: 2026-04-26
**源码**: Linux Kernel Mainline (master branch)

---

## 目录

1. [ALSA PCM 核心](#1-alsa-pcm-核心)
2. [PCM 数据传输](#2-pcm-数据传输)
3. [DPCM (Dynamic PCM)](#3-dpcm-dynamic-pcm)
4. [DAPM (Dynamic Audio Power Management)](#4-dapm-dynamic-audio-power-management)
5. [ASoC DAI (Digital Audio Interface)](#5-asoc-dai-digital-audio-interface)
6. [性能优化](#6-性能优化)

---

## 1. ALSA PCM 核心

### 1.1 struct snd_pcm 完整结构

**文件**: `/include/sound/pcm.h:534-554`

```c
struct snd_pcm {
    struct snd_card *card;              // 所属声卡
    struct list_head list;               // 声卡 PCM 链表节点
    int device;                          // PCM 设备编号
    unsigned int info_flags;              // 信息标志
    unsigned short dev_class;            // 设备类
    unsigned short dev_subclass;         // 设备子类
    char id[64];                         // 标识符
    char name[80];                        // 设备名称
    struct snd_pcm_str streams[2];       // 播放/录制流 [SNDRV_PCM_STREAM_PLAYBACK/CAPTURE]
    struct mutex open_mutex;             // 打开互斥锁
    wait_queue_head_t open_wait;         // 等待队列
    void *private_data;                  // 私有数据
    void (*private_free) (struct snd_pcm *pcm);  // 私有析构函数
    bool internal;                        // 是否内部使用
    bool nonatomic;                       // 是否非原子操作
    bool no_device_suspend;              // 是否跳过设备挂起
};
```

**关键关系**:
```
snd_pcm
  └── streams[2] (playback + capture)
        └── snd_pcm_str
              └── substreams (子流链表)
```

### 1.2 struct snd_pcm_runtime 完整字段

**文件**: `/include/sound/pcm.h:362-453`

```c
struct snd_pcm_runtime {
    /* -- 状态 -- */
    snd_pcm_state_t state;              // 流状态: OPEN, SETUP, PREPARE, RUNNING, XRUN, DRAINING, SUSPENDED
    snd_pcm_state_t suspended_state;     // 挂起状态
    struct snd_pcm_substream *trigger_master;  // 触发主 substream
    struct timespec64 trigger_tstamp;    // 触发时间戳
    bool trigger_tstamp_latched;        // 时间戳已锁定
    int overrange;                       // 过载计数
    snd_pcm_uframes_t avail_max;         // 最大可用帧数
    snd_pcm_uframes_t hw_ptr_base;      // 缓冲区重启位置
    snd_pcm_uframes_t hw_ptr_interrupt;  // 中断时硬件位置
    unsigned long hw_ptr_jiffies;        // hw_ptr 更新时间
    unsigned long hw_ptr_buffer_jiffies; // 缓冲区时间(jiffies)
    snd_pcm_sframes_t delay;            // 额外延迟(FIFO大小)
    u64 hw_ptr_wrap;                    // hw_ptr 边界环绕偏移

    /* -- HW 参数 -- */
    snd_pcm_access_t access;            // 访问模式: RW_INTERLEAVED, RW_NONINTERLEAVED, MMAP_INTERLEAVED, MMAP_NONINTERLEAVED
    snd_pcm_format_t format;            // 采样格式: S16_LE, S32_LE, etc.
    snd_pcm_subformat_t subformat;      // 子格式
    unsigned int rate;                   // 采样率 (Hz)
    unsigned int channels;               // 声道数
    snd_pcm_uframes_t period_size;      // 周期大小 (帧)
    unsigned int periods;               // 周期数
    snd_pcm_uframes_t buffer_size;      // 缓冲区大小 (帧)
    snd_pcm_uframes_t min_align;        // 最小对齐
    size_t byte_align;                  // 字节对齐
    unsigned int frame_bits;            // 每帧比特数
    unsigned int sample_bits;           // 采样比特数
    unsigned int info;                   // 信息标志
    unsigned int rate_num;               // 采样率分子
    unsigned int rate_den;               // 采样率分母
    unsigned int no_period_wakeup:1;    // 无周期中断唤醒

    /* -- SW 参数 -- */
    int tstamp_mode;                    // 时间戳模式
    unsigned int period_step;           // 周期步进
    snd_pcm_uframes_t start_threshold;  // 自动启动阈值
    snd_pcm_uframes_t stop_threshold;   // 自动停止阈值
    snd_pcm_uframes_t silence_threshold; // 静音阈值
    snd_pcm_uframes_t silence_size;     // 静音大小
    snd_pcm_uframes_t boundary;         // 指针环绕点

    /* -- 静音内部数据 -- */
    snd_pcm_uframes_t silence_start;    // 静音起始指针
    snd_pcm_uframes_t silence_filled;   // 已填充静音

    bool std_sync_id;                   // 硬件同步ID

    /* -- mmap -- */
    struct snd_pcm_mmap_status *status;  // 状态 (用户空间只读)
    struct snd_pcm_mmap_control *control; // 控制 (用户空间读写)

    /* -- 锁定/调度 -- */
    snd_pcm_uframes_t twake;            // 传输唤醒阈值
    wait_queue_head_t sleep;            // poll 睡眠队列
    wait_queue_head_t tsleep;           // 传输睡眠队列
    struct snd_fasync *fasync;           // 异步通知
    bool stop_operating;                // 停止运行标志
    struct mutex buffer_mutex;          // 缓冲区互斥锁
    atomic_t buffer_accessing;          // 缓冲区访问计数

    /* -- 私有 -- */
    void *private_data;                 // 私有数据
    void (*private_free)(struct snd_pcm_runtime *runtime);  // 析构函数

    /* -- 硬件描述 -- */
    struct snd_pcm_hardware hw;          // 硬件能力
    struct snd_pcm_hw_constraints hw_constraints;  // 约束规则

    /* -- 定时器 -- */
    unsigned int timer_resolution;       // 定时器分辨率
    int tstamp_type;                   // 时间戳类型

    /* -- DMA -- */
    unsigned char *dma_area;             // DMA 区域(虚拟地址)
    dma_addr_t dma_addr;                // DMA 物理地址
    size_t dma_bytes;                   // DMA 区域大小
    struct snd_dma_buffer *dma_buffer_p; // 分配的缓冲区
    unsigned int buffer_changed:1;      // 缓冲区已更改

    /* -- 音频时间戳配置 -- */
    struct snd_pcm_audio_tstamp_config audio_tstamp_config;
    struct snd_pcm_audio_tstamp_report audio_tstamp_report;
    struct timespec64 driver_tstamp;    // 驱动时间戳
};
```

### 1.3 hw_params vs sw_params 区别

#### hw_params (硬件参数)

**用户空间结构** (`/include/uapi/sound/asound.h:408-425`):
```c
struct snd_pcm_hw_params {
    unsigned int flags;                  // 标志
    struct snd_mask masks[...];          // 格式掩码 (SNDRV_PCM_HW_PARAM_*)
    struct snd_interval intervals[...];  // 间隔值 (rate, channels, period_size等)
    unsigned int rmask;                  // 请求的掩码
    unsigned int cmask;                 // 更改的掩码
    unsigned int info;                   // 返回的信息标志
    unsigned int msbits;                // 有效位
    unsigned int rate_num;               // 采样率分子
    unsigned int rate_den;              // 采样率分母
    snd_pcm_uframes_t fifo_size;        // FIFO 大小
    unsigned char sync[16];              // 同步ID
};
```

**参数类型** (`/include/sound/pcm.h`):
- `SNDRV_PCM_HW_PARAM_ACCESS` - 访问模式
- `SNDRV_PCM_HW_PARAM_FORMAT` - 采样格式 (S16_LE, S32_LE等)
- `SNDRV_PCM_HW_PARAM_SUBFORMAT` - 子格式
- `SNDRV_PCM_HW_PARAM_CHANNELS` - 声道数
- `SNDRV_PCM_HW_PARAM_RATE` - 采样率
- `SNDRV_PCM_HW_PARAM_PERIOD_SIZE` - 周期大小
- `SNDRV_PCM_HW_PARAM_PERIODS` - 周期数
- `SNDRV_PCM_HW_PARAM_BUFFER_SIZE` - 缓冲区大小
- `SNDRV_PCM_HW_PARAM_BUFFER_BYTES` - 缓冲区字节大小
- `SNDRV_PCM_HW_PARAM_ACCESS` - 访问模式

#### sw_params (软件参数)

**用户空间结构** (`/include/uapi/sound/asound.h:433-448`):
```c
struct snd_pcm_sw_params {
    int tstamp_mode;                   // 时间戳模式
    unsigned int period_step;           // 周期步进
    unsigned int sleep_min;             // 最小睡眠 ticks
    snd_pcm_uframes_t avail_min;       // 唤醒所需最小可用帧 (avail_min)
    snd_pcm_uframes_t xfer_align;      // 传输对齐 (已废弃)
    snd_pcm_uframes_t start_threshold; // 自动启动阈值
    snd_pcm_uframes_t stop_threshold;  // 自动停止阈值
    snd_pcm_uframes_t silence_threshold; // 静音阈值
    snd_pcm_uframes_t silence_size;    // 静音预填充大小
    snd_pcm_uframes_t boundary;        // 指针环绕点
};
```

#### 核心区别

| 特性 | hw_params | sw_params |
|------|-----------|-----------|
| **用途** | 描述硬件能力/限制 | 描述软件行为策略 |
| **修改频率** | 每次流设置时可能改变 | 可在运行时动态调整 |
| **作用对象** | DMA 缓冲区大小、采样率等 | 启动/停止阈值、唤醒条件 |
| **典型参数** | format, rate, channels | start_threshold, avail_min |

### 1.4 缓冲区分配 (mmap, rw_ref)

#### DMA 缓冲区分配流程

**文件**: `/sound/core/pcm_memory.c:420-470`

```c
int snd_pcm_lib_malloc_pages(struct snd_pcm_substream *substream, size_t size)
{
    struct snd_card *card;
    struct snd_pcm_runtime *runtime;
    struct snd_dma_buffer *dmab = NULL;

    // 运行时检查
    if (PCM_RUNTIME_CHECK(substream))
        return -EINVAL;
    if (snd_BUG_ON(substream->dma_buffer.dev.type == SNDRV_DMA_TYPE_UNKNOWN))
        return -EINVAL;

    runtime = substream->runtime;
    card = substream->pcm->card;

    // 已有缓冲区且足够大 -> 直接使用
    if (runtime->dma_buffer_p) {
        if (runtime->dma_buffer_p->bytes >= size) {
            runtime->dma_bytes = size;
            return 0;
        }
        snd_pcm_lib_free_pages(substream);
    }

    // 预分配缓冲区足够 -> 使用预分配
    if (substream->dma_buffer.area != NULL &&
        substream->dma_buffer.bytes >= size) {
        dmab = &substream->dma_buffer;
    } else {
        // 需要新分配
        dmab = kzalloc_obj(*dmab);
        if (!dmab)
            return -ENOMEM;
        dmab->dev = substream->dma_buffer.dev;
        if (do_alloc_pages(card,
                           substream->dma_buffer.dev.type,
                           substream->dma_buffer.dev.dev,
                           substream->stream,
                           size, dmab) < 0) {
            kfree(dmab);
            return -ENOMEM;
        }
    }

    // 设置运行时缓冲区
    snd_pcm_set_runtime_buffer(substream, dmab);
    runtime->dma_bytes = size;
    return 1;
}
```

#### 预分配缓冲区类型

**文件**: `/include/sound/pcm.h`

```c
/* DMA 缓冲区类型 */
enum snd_dma_buffer_type {
    SNDRV_DMA_TYPE_UNKNOWN = 0,      // 未知类型
    SNDRV_DMA_TYPE_CONTINUOUS,       // 连续内存 (kmalloc/vmalloc)
    SNDRV_DMA_TYPE_VMALLOC,          // vmalloc 内存
    SNDRV_DMA_TYPE_DEV,              // DMA 可访问设备内存
    SNDRV_DMA_TYPE_DEV_WC,           // Write-Combine 设备内存
    SNDRV_DMA_TYPE_EXCLUSIVE,        // 独占 DMA 映射
};
```

#### mmap 机制

**文件**: `/sound/core/pcm_native.c` (pcm_mmap)

用户空间通过 `mmap()` 系统调用将 DMA 缓冲区映射到用户空间，实现零拷贝音频数据传输。

```c
// 关键 mmap 流程:
// 1. snd_pcm_mmap() - 创建 mmap 映射
// 2. snd_pcm_mmap_data() - 映射 PCM 数据缓冲区
```

---

## 2. PCM 数据传输

### 2.1 __snd_pcm_lib_xfer() 详细流程

**文件**: `/sound/core/pcm_lib.c:2271-2416`

```c
snd_pcm_sframes_t __snd_pcm_lib_xfer(struct snd_pcm_substream *substream,
                                     void *data, bool interleaved,
                                     snd_pcm_uframes_t size, bool in_kernel)
{
    struct snd_pcm_runtime *runtime = substream->runtime;
    snd_pcm_uframes_t xfer = 0;
    snd_pcm_uframes_t offset = 0;
    snd_pcm_uframes_t avail;
    pcm_copy_f writer;      // 传输函数指针
    pcm_transfer_f transfer; // 数据拷贝函数
    bool nonblock;
    bool is_playback;
    int err;

    // 1. 合理性检查
    err = pcm_sanity_check(substream);
    if (err < 0)
        return err;

    is_playback = substream->stream == SNDRV_PCM_STREAM_PLAYBACK;

    // 2. 选择交错式或非交错式传输函数
    if (interleaved) {
        writer = interleaved_copy;
    } else {
        writer = noninterleaved_copy;
    }

    // 3. 选择数据传输函数
    if (!data) {
        // 静音填充
        if (is_playback)
            transfer = fill_silence;
        else
            return -EINVAL;
    } else if (substream->ops->copy) {
        // 驱动自定义拷贝
        transfer = substream->ops->copy;
    } else {
        // 默认拷贝
        transfer = is_playback ? default_write_copy : default_read_copy;
    }

    if (size == 0)
        return 0;

    nonblock = !!(substream->f_flags & O_NONBLOCK);

    // 4. 获取流锁
    snd_pcm_stream_lock_irq(substream);

    // 5. 状态检查
    err = pcm_accessible_state(runtime);
    if (err < 0)
        goto _end_unlock;

    runtime->twake = runtime->control->avail_min ? : 1;

    // 6. 如果正在运行,更新硬件指针
    if (runtime->state == SNDRV_PCM_STATE_RUNNING)
        snd_pcm_update_hw_ptr(substream);

    // 7. 捕获流自动启动
    if (!is_playback &&
        runtime->state == SNDRV_PCM_STATE_PREPARED &&
        size >= runtime->start_threshold) {
        err = snd_pcm_start(substream);
        if (err < 0)
            goto _end_unlock;
    }

    // 8. 主传输循环
    while (size > 0) {
        snd_pcm_uframes_t frames, appl_ptr, appl_ofs;
        snd_pcm_uframes_t cont;

        // 计算可用空间
        avail = snd_pcm_avail(substream);

        if (!avail) {
            //无可用空间,等待
            if (nonblock) {
                err = -EAGAIN;
                goto _end_unlock;
            }
            // 设置唤醒条件
            runtime->twake = min_t(snd_pcm_uframes_t, size,
                    runtime->control->avail_min ? : 1);
            err = wait_for_avail(substream, &avail);
            if (err < 0)
                goto _end_unlock;
        }

        // 计算本次传输帧数
        frames = size > avail ? avail : size;
        appl_ptr = READ_ONCE(runtime->control->appl_ptr);
        appl_ofs = appl_ptr % runtime->buffer_size;
        cont = runtime->buffer_size - appl_ofs;
        if (frames > cont)
            frames = cont;

        // 9. 执行实际数据传输
        if (!atomic_inc_unless_negative(&runtime->buffer_accessing)) {
            err = -EBUSY;
            goto _end_unlock;
        }
        snd_pcm_stream_unlock_irq(substream);

        // DMA 同步
        if (!is_playback)
            snd_pcm_dma_buffer_sync(substream, SNDRV_DMA_SYNC_CPU);

        // 调用写函数传输数据
        err = writer(substream, appl_ofs, data, offset, frames,
                     transfer, in_kernel);

        if (is_playback)
            snd_pcm_dma_buffer_sync(substream, SNDRV_DMA_SYNC_DEVICE);

        snd_pcm_stream_lock_irq(substream);
        atomic_dec(&runtime->buffer_accessing);

        if (err < 0)
            goto _end_unlock;

        // 更新应用指针
        appl_ptr += frames;
        if (appl_ptr >= runtime->boundary)
            appl_ptr -= runtime->boundary;
        err = pcm_lib_apply_appl_ptr(substream, appl_ptr);
        if (err < 0)
            goto _end_unlock;

        // 更新计数器和状态
        offset += frames;
        size -= frames;
        xfer += frames;
        avail -= frames;

        // 播放流自动启动检查
        if (is_playback &&
            runtime->state == SNDRV_PCM_STATE_PREPARED &&
            snd_pcm_playback_hw_avail(runtime) >= runtime->start_threshold) {
            err = snd_pcm_start(substream);
            if (err < 0)
                goto _end_unlock;
        }
    }

_end_unlock:
    runtime->twake = 0;
    if (xfer > 0 && err >= 0)
        snd_pcm_update_state(substream, runtime);
    snd_pcm_stream_unlock_irq(substream);

    return xfer > 0 ? (snd_pcm_sframes_t)xfer : err;
}
```

### 2.2 交错式 vs 非交错式传输

#### 交错式 (Interleaved)

**文件**: `/sound/core/pcm_lib.c:2127-2143`

```c
// 交错式: L R L R L R ... (L=左声道, R=右声道)
static int interleaved_copy(struct snd_pcm_substream *substream,
                           snd_pcm_uframes_t hwoff, void *data,
                           snd_pcm_uframes_t off,
                           snd_pcm_uframes_t frames,
                           pcm_transfer_f transfer,
                           bool in_kernel)
{
    struct snd_pcm_runtime *runtime = substream->runtime;

    // 转换为字节偏移
    hwoff = frames_to_bytes(runtime, hwoff);
    off = frames_to_bytes(runtime, off);
    frames = frames_to_bytes(runtime, frames);

    // 单次传输所有声道数据
    return do_transfer(substream, 0, hwoff, data + off, frames,
                      transfer, in_kernel);
}
```

#### 非交错式 (Non-interleaved)

**文件**: `/sound/core/pcm_lib.c:2148-2177`

```c
// 非交错式: L L L L ... R R R R ... (先左声道,后右声道)
static int noninterleaved_copy(struct snd_pcm_substream *substream,
                              snd_pcm_uframes_t hwoff, void *data,
                              snd_pcm_uframes_t off,
                              snd_pcm_uframes_t frames,
                              pcm_transfer_f transfer,
                              bool in_kernel)
{
    struct snd_pcm_runtime *runtime = substream->runtime;
    int channels = runtime->channels;
    void **bufs = data;  // 每声道独立缓冲区
    int c, err;

    // 每个声道单独传输
    for (c = 0; c < channels; ++c, ++bufs) {
        if (!data || !*bufs)
            err = fill_silence(substream, c, hwoff, NULL, frames);
        else
            err = do_transfer(substream, c, hwoff, *bufs + off,
                              frames, transfer, in_kernel);
        if (err < 0)
            return err;
    }
    return 0;
}
```

### 2.3 DMA 缓冲区管理

#### 关键字段

```c
// /include/sound/pcm.h
struct snd_pcm_runtime {
    unsigned char *dma_area;      // DMA 区域虚拟地址 (用户空间可见)
    dma_addr_t dma_addr;         // DMA 物理地址 (总线地址)
    size_t dma_bytes;            // DMA 区域总字节数
    struct snd_dma_buffer *dma_buffer_p;  // 分配的缓冲区描述符
};
```

#### 缓冲区同步

**文件**: `/sound/core/pcm_lib.c:2379, 2383`

```c
// 传输前同步 (capture) - 确保 CPU 读取最新数据
snd_pcm_dma_buffer_sync(substream, SNDRV_DMA_SYNC_CPU);

// 传输后同步 (playback) - 确保 DMA 读取最新数据
snd_pcm_dma_buffer_sync(substream, SNDRV_DMA_SYNC_DEVICE);
```

### 2.4 中断驱动 vs 轮询模式

#### 中断驱动模式

当硬件完成一个周期时会触发中断,调用 `snd_pcm_period_elapsed()`:

**文件**: `/sound/core/pcm_lib.c:1933-1940`

```c
void snd_pcm_period_elapsed(struct snd_pcm_substream *substream)
{
    if (snd_BUG_ON(!substream))
        return;

    guard(pcm_stream_lock_irqsave)(substream);
    snd_pcm_period_elapsed_under_stream_lock(substream);
}
```

**更新流程** (`pcm_lib.c:1900-1918`):
1. 调用 `snd_pcm_update_hw_ptr0(substream, 1)` 更新 hw_ptr
2. 检查 overrun/underrun
3. 唤醒等待进程
4. 发送 SIGIO 信号

#### 轮询模式 (无周期中断)

当 `runtime->no_period_wakeup = true` 时:

**文件**: `/sound/core/pcm_lib.c:376-397`

```c
if (runtime->no_period_wakeup) {
    // 通过时间检测 xruns
    jdelta = curr_jiffies - runtime->hw_ptr_jiffies;
    if (jdelta < runtime->hw_ptr_buffer_jiffies / 2)
        goto no_delta_check;

    hdelta = jdelta - delta * HZ / runtime->rate;
    xrun_threshold = runtime->hw_ptr_buffer_jiffies / 2 + 1;

    // 根据时间推算丢失的周期
    while (hdelta > xrun_threshold) {
        delta += runtime->buffer_size;
        hw_base += runtime->buffer_size;
        // ...
        hdelta -= runtime->hw_ptr_buffer_jiffies;
    }
}
```

---

## 3. DPCM (Dynamic PCM)

### 3.1 dpcm 状态机

**文件**: `/include/sound/soc-dpcm.h:38-49`

```c
enum snd_soc_dpcm_state {
    SND_SOC_DPCM_STATE_NEW = 0,      // 新创建
    SND_SOC_DPCM_STATE_OPEN,          // 已打开
    SND_SOC_DPCM_STATE_HW_PARAMS,    // 硬件参数已设置
    SND_SOC_DPCM_STATE_PREPARE,      // 已准备
    SND_SOC_DPCM_STATE_START,        // 已启动
    SND_SOC_DPCM_STATE_STOP,         // 已停止
    SND_SOC_DPCM_STATE_PAUSED,       // 已暂停
    SND_SOC_DPCM_STATE_SUSPEND,      // 已挂起
    SND_SOC_DPCM_STATE_HW_FREE,      // 硬件资源已释放
    SND_SOC_DPCM_STATE_CLOSE,        // 已关闭
};
```

#### 状态转换图

```
 NEW -> OPEN -> HW_PARAMS -> PREPARE -> START
                                       |
                                       v
                                    STOP
                                       |
                   +--------+-----------+--------+
                   |        |                   |
                   v        v                   v
              HW_FREE    PAUSED              SUSPEND
                   |        |                   |
                   v        v                   v
                CLOSE    START (resume)    SUSPEND
                                           |
                                           v
                                        HW_FREE -> CLOSE
```

### 3.2 dpcm_be/dai_link 机制

**文件**: `/include/sound/soc-dpcm.h:68-83`

```c
struct snd_soc_dpcm {
    struct snd_soc_pcm_runtime *be;    // 后端运行时
    struct snd_soc_pcm_runtime *fe;    // 前端运行时

    enum snd_soc_dpcm_link_state state;  // 链接状态

    struct list_head list_be;          // BE 链表节点
    struct list_head list_fe;          // FE 链表节点

#ifdef CONFIG_DEBUG_FS
    struct dentry *debugfs_state;
#endif
};
```

**文件**: `/include/sound/soc-dpcm.h:88-104`

```c
struct snd_soc_dpcm_runtime {
    struct list_head be_clients;      // 连接的 BE 客户端链表
    struct list_head fe_clients;      // 连接的 FE 客户端链表

    int users;                         // 用户计数
    struct snd_pcm_hw_params hw_params;  // 硬件参数

    enum snd_soc_dpcm_update runtime_update;  // 运行时更新类型
    enum snd_soc_dpcm_state state;     // DPCM 状态

    int trigger_pending;               // 待处理的触发命令

    int be_start;                      // BE 启动引用计数
    int be_pause;                      // BE 暂停引用计数
    bool fe_pause;                     // FE 是否已暂停
};
```

### 3.3 FE/BE 路由

**文件**: `/sound/soc/soc-pcm.c`

#### FE/BE 链接遍历宏

```c
// 遍历所有 FE 客户端
#define for_each_dpcm_fe(be, stream, _dpcm) \
    list_for_each_entry(_dpcm, &(be)->dpcm[stream].fe_clients, list_fe)

// 遍历所有 BE 客户端
#define for_each_dpcm_be(fe, stream, _dpcm) \
    list_for_each_entry(_dpcm, &(fe)->dpcm[stream].be_clients, list_be)
```

#### 状态检查函数

**文件**: `/sound/soc/soc-pcm.c:59-101`

```c
// 检查 FE/BE 是否处于特定状态组合
static int snd_soc_dpcm_check_state(fe, be, stream, states, num_states)
{
    // 遍历 FE 关联的所有 BE
    for_each_dpcm_fe(be, stream, dpcm) {
        if (dpcm->fe == fe)
            continue;
        state = dpcm->fe->dpcm[stream].state;
        // 检查是否匹配任何目标状态
        for (i = 0; i < num_states; i++) {
            if (state == states[i])
                return 1;  // 匹配
        }
    }
    return 0;
}

// 检查是否可以启动
static int snd_soc_dpcm_can_be_start(fe, be, stream)
{
    const enum snd_soc_dpcm_state state[] = {
        SND_SOC_DPCM_STATE_START,
        SND_SOC_DPCM_STATE_PAUSED,
        SND_SOC_DPCM_STATE_SUSPEND,
    };
    return snd_soc_dpcm_check_state(fe, be, stream, state, 3);
}
```

---

## 4. DAPM (Dynamic Audio Power Management)

### 4.1 widget 树结构

**文件**: `/include/sound/soc-dapm.h:516-566`

```c
struct snd_soc_dapm_widget {
    enum snd_soc_dapm_type id;       // widget 类型
    const char *name;                  // widget 名称
    const char *sname;                 // 流名称
    struct list_head list;
    struct snd_soc_dapm_context *dapm; // 所属 DAPM 上下文

    void *priv;                        // 私有数据

    /* dapm 控制 */
    int reg;                           // 寄存器地址 (-1 = 无直接控制)
    unsigned char shift;               // 位移
    unsigned int mask;                 // 位掩码
    unsigned int on_val;               // 开启值
    unsigned int off_val;              // 关闭值

    unsigned char power:1;              // 当前电源状态
    unsigned char active:1;            // 激活状态
    unsigned char connected:1;         // 连接状态
    unsigned char new:1;               // 新状态完成
    unsigned char force:1;              // 强制状态
    unsigned char ignore_suspend:1;    // 忽略挂起
    unsigned char new_power:1;         // 本次电源状态
    unsigned char power_checked:1;     // 本次已检查
    unsigned char is_supply:1;         // 是否为电源类型
    unsigned char is_ep:2;             // 端点类型

    int (*power_check)(struct snd_soc_dapm_widget *w);  // 电源检查回调

    /* 事件 */
    unsigned short event_flags;        // 事件标志
    int (*event)(struct snd_soc_dapm_widget*, struct snd_kcontrol *, int);

    /* kcontrols */
    int num_kcontrols;
    const struct snd_kcontrol_new *kcontrol_news;
    struct snd_kcontrol **kcontrols;

    /* 输入/输出边 */
    struct list_head edges[2];         // [输入边, 输出边]

    /* DAPM 更新使用 */
    struct list_head work_list;
    struct list_head power_list;
    struct list_head dirty;
    int endpoints[2];                  // [输入端点数, 输出端点数]
};
```

#### Widget 类型

**文件**: `/include/sound/soc-dapm.h` (部分)

```c
enum snd_soc_dapm_type {
    snd_soc_dapm_dai_in,       // DAI 输入
    snd_soc_dapm_dai_out,      // DAI 输出
    snd_soc_dapm_dai_link,     // DAI 链接
    snd_soc_dapm_aif_in,       // AIF 输入
    snd_soc_dapm_aif_out,      // AIF 输出
    snd_soc_dapm_vmid,         // VMID (偏置)
    snd_soc_dapm_micbias,      // 麦克风偏置
    snd_soc_dapm_mic,          // 麦克风输入
    snd_soc_dapm_input,        // 输入引脚
    snd_soc_dapm_output,       // 输出引脚
    snd_soc_dapm_switch,       // 开关
    snd_soc_dapm_mixer,        // 混音器
    snd_soc_dapm_mixer_named_ctl,  // 命名控制混音器
    snd_soc_dapm_pga,          // 可编程增益放大器
    snd_soc_dapm_adc,          // ADC
    snd_soc_dapm_dac,          // DAC
    snd_soc_dapm_mux,          // 多路复用器
    snd_soc_dapm_demux,        // 解复用器
    snd_soc_dapm_supply,       // 电源供应
    snd_soc_dapm_regulator_supply,  // 稳压器
    snd_soc_dapm_clock_supply, // 时钟供应
    snd_soc_dapm_kcontrol,     // kcontrol widget
    // ... 更多类型
};
```

### 4.2 kcontrol 机制

**文件**: `/include/sound/soc-dapm.c:706-772`

kcontrol (内核控制) 提供了用户空间与 DAPM widget 之间的接口。

```c
// kcontrol 数据结构
struct dapm_kcontrol_data {
    struct snd_soc_dapm_widget *widget;    // 关联的 widget
    struct list_head paths;                 // 路径列表
    unsigned int value;                     // 当前值
};
```

### 4.3 path_power() 电源状态机

**文件**: `/sound/soc/soc-dapm.c:2176-2220`

```c
static void dapm_power_one_widget(struct snd_soc_dapm_widget *w,
                                  struct list_head *up_list,
                                  struct list_head *down_list)
{
    struct snd_soc_dapm_path *path;
    int power;

    // 特殊类型处理
    switch (w->id) {
    case snd_soc_dapm_pre:
        power = 0;  // pre widget 始终断电
        goto end;
    case snd_soc_dapm_post:
        power = 1;  // post widget 始终上电
        goto end;
    default:
        break;
    }

    // 调用 widget 的 power_check 回调确定电源状态
    power = dapm_widget_power_check(w);

    // 状态未变则跳过
    if (w->power == power)
        return;

    trace_snd_soc_dapm_widget_power(w, power);

    // 更新对等 widget 的电源状态
    snd_soc_dapm_widget_for_each_source_path(w, path)
        dapm_widget_set_peer_power(path->source, power, path->connect);

    // 供应类型不影响输出
    if (!w->is_supply)
        snd_soc_dapm_widget_for_each_sink_path(w, path)
            dapm_widget_set_peer_power(path->sink, power, path->connect);

end:
    // 加入对应的电源列表
    if (power)
        dapm_seq_insert(w, up_list, true);   // 上电序列
    else
        dapm_seq_insert(w, down_list, false); // 下电序列
}
```

#### 电源检查函数

**文件**: `/sound/soc/soc-dapm.c:1721-1776`

```c
static int dapm_widget_power_check(struct snd_soc_dapm_widget *w)
{
    if (w->power_checked)
        return w->power;
    if (w->force)
        return 1;
    if (w->power_check)
        return w->power_check(w);
    // 根据类型使用默认检查函数
    return dapm_generic_check_power(w);
}
```

### 4.4 事件驱动 vs 路径遍历

#### 事件驱动模式

当用户空间操作 (如播放/暂停) 触发:

**文件**: `/sound/soc/soc-dapm.c:2252-2329`

```c
static int dapm_power_widgets(struct snd_soc_card *card, int event,
                              struct snd_soc_dapm_update *update)
{
    // 遍历所有标记为 dirty 的 widget
    list_for_each_entry(w, &card->dapm_dirty, dirty) {
        dapm_power_one_widget(w, &up_list, &down_list);
    }

    // 根据事件应用序列
    switch (event) {
    case SND_SOC_DAPM_STREAM_START:
        // 启动流: 上电相关 widgets
        break;
    case SND_SOC_DAPM_STREAM_STOP:
        // 停止流: 下电 widgets
        break;
    }
}
```

#### 路径遍历 (Path Walk)

**文件**: `/sound/soc/soc-dapm.c:1550-1580`

```c
// 遍历从 widget 到活动端点的所有路径
static int dapm_is_connected_output_ep(...)
{
    // 使用 BFS/DFS 遍历路径树
    // 寻找从 source 到有效 sink 的路径
}
```

---

## 5. ASoC DAI (Digital Audio Interface)

### 5.1 struct snd_soc_dai 完整结构

**文件**: `/include/sound/soc-dai.h:438-470`

```c
struct snd_soc_dai {
    const char *name;                  // DAI 名称
    int id;                            // DAI ID
    struct device *dev;                // 设备

    struct snd_soc_dai_driver *driver; // DAI 驱动

    struct snd_soc_dai_stream stream[SNDRV_PCM_STREAM_LAST + 1];
    // stream[0] = playback, stream[1] = capture

    /* 对称性约束 */
    unsigned int symmetric_rate;
    unsigned int symmetric_channels;
    unsigned int symmetric_sample_bits;

    struct snd_soc_component *component; // 父组件

    struct list_head list;              // 链表节点

    /* 标记 */
    struct snd_pcm_substream *mark_startup;
    struct snd_pcm_substream *mark_hw_params;
    struct snd_pcm_substream *mark_trigger;

    unsigned int probed:1;              // 是否已探测

    void *priv;                        // 私有数据
};
```

#### DAI 流结构

```c
struct snd_soc_dai_stream {
    struct snd_soc_dapm_widget *widget;   // 关联的 DAPM widget

    unsigned int active;               // 活动计数
    unsigned int tdm_mask;            // TDM slot 掩码

    void *dma_data;                  // DMA 私有数据
};
```

### 5.2 DAI hw_params()

**文件**: `/sound/soc/soc-dai.c` + `/include/sound/soc-dai.h`

```c
// /include/sound/soc-dai.h:204-206
int snd_soc_dai_hw_params(struct snd_soc_dai *dai,
                          struct snd_pcm_substream *substream,
                          struct snd_pcm_hw_params *params);
```

这是 DAI 层设置硬件参数的函数,在 PCM hw_params 期间调用。

### 5.3 DAI Operations

**文件**: `/include/sound/soc-dai.h:269-366`

```c
struct snd_soc_dai_ops {
    /* 探测/移除 */
    int (*probe)(struct snd_soc_dai *dai);
    int (*remove)(struct snd_soc_dai *dai);

    /* PCM 新建 */
    int (*pcm_new)(struct snd_soc_pcm_runtime *rtd, struct snd_soc_dai *dai);

    /* 时钟配置 */
    int (*set_sysclk)(struct snd_soc_dai *dai, int clk_id,
                      unsigned int freq, int dir);
    int (*set_pll)(struct snd_soc_dai *dai, int pll_id, int source,
                   unsigned int freq_in, unsigned int freq_out);
    int (*set_clkdiv)(struct snd_soc_dai *dai, int div_id, int div);
    int (*set_bclk_ratio)(struct snd_soc_dai *dai, unsigned int ratio);

    /* 格式配置 */
    int (*set_fmt)(struct snd_soc_dai *dai, unsigned int fmt);
    int (*set_tdm_slot)(struct snd_soc_dai *dai,
                        unsigned int tx_mask, unsigned int rx_mask,
                        int slots, int slot_width);
    int (*set_channel_map)(struct snd_soc_dai *dai,
                           unsigned int tx_num, const unsigned int *tx_slot,
                           unsigned int rx_num, const unsigned int *rx_slot);

    /* 流控制 */
    int (*set_stream)(struct snd_soc_dai *dai, void *stream, int direction);
    void *(*get_stream)(struct snd_soc_dai *dai, int direction);

    /* 静音控制 */
    int (*mute_stream)(struct snd_soc_dai *dai, int mute, int stream);

    /* PCM 操作 */
    int (*startup)(struct snd_pcm_substream *, struct snd_soc_dai *);
    void (*shutdown)(struct snd_pcm_substream *, struct snd_soc_dai *);
    int (*hw_params)(struct snd_pcm_substream *,
                     struct snd_pcm_hw_params *, struct snd_soc_dai *);
    int (*hw_free)(struct snd_pcm_substream *, struct snd_soc_dai *);
    int (*prepare)(struct snd_pcm_substream *, struct snd_soc_dai *);
    int (*trigger)(struct snd_pcm_substream *, int, struct snd_soc_dai *);

    /* 延迟报告 */
    snd_pcm_sframes_t (*delay)(struct snd_pcm_substream *,
                               struct snd_soc_dai *);

    /* 格式自动选择 */
    const u64 *auto_selectable_formats;
    int num_auto_selectable_formats;
};
```

#### 操作时序

```
启动流程:
  startup() -> hw_params() -> prepare() -> trigger(START) -> 运行时

停止流程:
  trigger(STOP) -> hw_free() -> shutdown()

参数变更流程:
  hw_free() -> hw_params() -> prepare()
```

### 5.4 时钟配置流程

**文件**: `/sound/soc/soc-dai.c:38-51`

```c
int snd_soc_dai_set_sysclk(struct snd_soc_dai *dai, int clk_id,
                           unsigned int freq, int dir)
{
    int ret;

    if (dai->driver->ops && dai->driver->ops->set_sysclk)
        ret = dai->driver->ops->set_sysclk(dai, clk_id, freq, dir);
    else
        ret = snd_soc_component_set_sysclk(dai->component, clk_id, 0,
                                           freq, dir);
    return ret;
}
```

**时钟配置层级**:

1. **set_sysclk** - 设置系统/主时钟 (MCLK)
2. **set_pll** - 配置 PLL 从输入时钟生成输出时钟
3. **set_clkdiv** - 设置时钟分频器
4. **set_bclk_ratio** - 设置 BCLK 与采样率比率

---

## 6. 性能优化

### 6.1 DMA Scatter-Gather

ALSA PCM 通过 `struct snd_dma_buffer` 支持分散-聚集 DMA:

**文件**: `/include/sound/pcm.h`

```c
struct snd_dma_buffer {
    struct device *dev;              // 设备
    unsigned char *area;             // 虚拟地址
    dma_addr_t addr;                 // 物理/总线地址
    size_t bytes;                    // 缓冲区大小
    enum snd_dma_buffer_type dev.type;  // 缓冲区类型
    void *private_data;              // 私有数据
};
```

### 6.2 零拷贝机制

**mmap 零拷贝路径**:

```
用户空间                内核空间
   |                        |
   |-- mmap(PCM) --------->|  // 建立映射
   |                        |
   |  read()/write()       |  // 传统拷贝
   |                        |
   |<-- mmap 共享内存 ----->|  // 零拷贝
   |   (DMA 直接访问)        |
```

**文件**: `/sound/core/pcm_lib.c:2098-2122`

```c
// 直接 DMA 传输 (零拷贝)
static int do_transfer(struct snd_pcm_substream *substream, int c,
                       unsigned long hwoff, void *data, unsigned long bytes,
                       pcm_transfer_f transfer, bool in_kernel)
{
    struct iov_iter iter;
    int err, type;

    // 设置迭代器类型
    if (substream->stream == SNDRV_PCM_STREAM_PLAYBACK)
        type = ITER_SOURCE;
    else
        type = ITER_DEST;

    if (in_kernel) {
        // 内核内部传输
        struct kvec kvec = { data, bytes };
        iov_iter_kvec(&iter, type, &kvec, 1, bytes);
        return transfer(substream, c, hwoff, &iter, bytes);
    }

    // 用户空间 -> 内核 (零拷贝)
    err = import_ubuf(type, (__force void __user *)data, bytes, &iter);
    if (err)
        return err;
    return transfer(substream, c, hwoff, &iter, bytes);
}
```

### 6.3 缓冲区 mmap

**文件**: `/sound/core/pcm_native.c`

关键 mmap 函数:
- `snd_pcm_mmap()` - 通用 mmap 入口
- `snd_pcm_mmap_data()` - PCM 数据缓冲区映射

```c
// mmap 系统调用处理
static int snd_pcm_mmap(struct snd_pcm_substream *substream,
                        struct vm_area_struct *area)
{
    // 验证 mmap 能力
    if (!hw_support_mmap(substream))
        return -ENXIO;

    // 调用驱动特定 mmap 或使用默认
    if (substream->ops->mmap)
        return substream->ops->mmap(substream, area);
    else if (substream->ops->page)
        return snd_pcm_mmap_data(substream, file, area);
    else
        return -ENXIO;
}
```

### 6.4 中断合并

#### 周期中断模式

**文件**: `/sound/core/pcm_lib.c:343-359`

```c
// 中断处理时的双确认检测
if (in_interrupt) {
    delta = runtime->hw_ptr_interrupt + runtime->period_size;
    if (delta > new_hw_ptr) {
        hdelta = curr_jiffies - runtime->hw_ptr_jiffies;
        if (hdelta > runtime->hw_ptr_buffer_jiffies/2 + 1) {
            // 跳过期间发生了另一次中断
            hw_base += runtime->buffer_size;
            if (hw_base >= runtime->boundary) {
                hw_base = 0;
                crossed_boundary++;
            }
            new_hw_ptr = hw_base + pos;
            goto __delta;
        }
    }
}
```

#### 无周期中断模式 (polling)

**文件**: `/sound/core/pcm_lib.c:376-397`

当 `runtime->no_period_wakeup = true` 时,使用基于时间的中断合并和 xrun 检测:

```c
if (runtime->no_period_wakeup) {
    jdelta = curr_jiffies - runtime->hw_ptr_jiffies;
    if (jdelta < runtime->hw_ptr_buffer_jiffies / 2)
        goto no_delta_check;

    // 通过时间差推算错过的周期数
    hdelta = jdelta - delta * HZ / runtime->rate;
    while (hdelta > xrun_threshold) {
        delta += runtime->buffer_size;
        hw_base += runtime->buffer_size;
        // ...
    }
}
```

---

## 附录 A: 关键数据结构关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                        snd_pcm                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ streams[2]:                                                │  │
│  │   [PLAYBACK] ──> snd_pcm_str                              │  │
│  │   [CAPTURE]  ──> snd_pcm_str                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      snd_pcm_str                                │
│  substream_count: 子流数量                                      │
│  substream_opened: 已打开子流数量                                │
│  substream: 指向第一个子流的指针                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   snd_pcm_substream                             │
│  runtime: 指向运行时信息的指针                                   │
│  ops: PCM 操作函数集                                             │
│  dma_buffer: DMA 缓冲区描述符                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   snd_pcm_runtime                               │
│  state: 当前状态 (OPEN/SETUP/PREPARED/RUNNING/XRUN/DRAINING)   │
│  hw: 硬件能力描述                                               │
│  dma_area: DMA 缓冲区虚拟地址                                    │
│  dma_addr: DMA 缓冲区物理地址                                    │
│  status: 状态信息 (hw_ptr, tstamp) ──> mmap 到用户空间           │
│  control: 控制信息 (appl_ptr, avail_min) ──> mmap 到用户空间     │
│  hw_constraints: 硬件约束规则                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录 B: DPCM FE/BE 路由关系图

```
+------------------+      +------------------+
|   App (用户空间)  |      |  HW (硬件)       |
+--------+---------+      +--------+---------+
         │                         │
         │ write()/read()          │
         │ mmap()                  │
         v                         v
+------------------+      +------------------+
|  Frontend (FE)   |      |  Backend (BE)    |
|  snd_pcm_runtime |      |  snd_poc_runtime |
+--------+---------+      +--------+---------+
         │                         │
         │ dpcm_link               │
         +-------------------------+
         │   snd_soc_dpcm          │
         │   fe ──> be              │
         +-------------------------+
                   │
                   ▼
         +------------------+
         |  DAPM paths      |
         |  (widgets)       |
         +------------------+
                   │
                   ▼
         +------------------+
         |  snd_soc_dai     |
         |  (CPU/CODEC DAI) |
         +------------------+
```

---

## 附录 C: DAPM Widget 电源状态机

```
                    ┌─────────────────────────────────────┐
                    │         dapm_power_widgets()         │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  1. 确定初始 bias_level              │
                    │     (STANDBY/BIAS_ON/BIAS_OFF)       │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  2. 遍历 dapm_dirty 列表              │
                    │     调用 dapm_power_one_widget()      │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
         ┌──────────────────┐               ┌──────────────────┐
         │ power_check()    │               │ power_check()   │
         │ 返回需要上电?    │               │ 返回需要上电?   │
         └──────────────────┘               └──────────────────┘
                    │                                   │
         ┌─────────┴─────────┐             ┌─────────┴─────────┐
         │                   │             │                   │
         ▼                   ▼             ▼                   ▼
    ┌─────────┐         ┌─────────┐    ┌─────────┐         ┌─────────┐
    │ up_list │         │down_list│    │ up_list │         │down_list│
    │  追加   │         │  追加   │    │  追加   │         │  追加   │
    └─────────┘         └─────────┘    └─────────┘         └─────────┘
         │                   │             │                   │
         └─────────┬─────────┘             └─────────┬─────────┘
                   │                                   │
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                   ┌─────────────────────────────────────┐
                   │  3. 按 seq 顺序执行电源序列            │
                   │     dapm_up_seq[] / dapm_down_seq[]   │
                   └─────────────────────────────────────┘
                                     │
                                     ▼
                   ┌─────────────────────────────────────┐
                   │  4. 调用各 widget 的 power_check()    │
                   │     更新 power 状态                   │
                   └─────────────────────────────────────┘
```

---

## 附录 D: DAI 时钟配置流程

```
应用程序
    │
    ▼
snd_pcm_hw_params()
    │
    ▼
┌───────────────────────────────────────┐
│  snd_soc_pcm_hw_params()             │
│  1. FE DAI hw_params                 │
│  2. BE DAI hw_params                 │
│  3. DPCM 路由和参数同步               │
└───────────────────────────────────────┘
    │
    ├──> snd_soc_dai_set_sysclk()      // 设置 MCLK/SYSCLK
    │         │
    │         ▼
    │   ┌─────────────────────────────┐
    │   │ DAI driver->set_sysclk()  │
    │   │ 或 Component set_sysclk()  │
    │   └─────────────────────────────┘
    │
    ├──> snd_soc_dai_set_pll()         // 配置 PLL (如果需要)
    │         │
    │         ▼
    │   ┌─────────────────────────────┐
    │   │ DAI driver->set_pll()      │
    │   │ 或 Component set_pll()      │
    │   └─────────────────────────────┘
    │
    ├──> snd_soc_dai_set_clkdiv()      // 设置分频
    │         │
    │         ▼
    │   ┌─────────────────────────────┐
    │   │ DAI driver->set_clkdiv()   │
    │   └─────────────────────────────┘
    │
    └──> snd_soc_dai_set_fmt()         // 设置格式
              │
              ▼
        ┌─────────────────────────────┐
        │ DAI driver->set_fmt()      │
        │ 设置 I2S/SPDIF/DSP 格式      │
        └─────────────────────────────┘
```

---

**文档结束**
