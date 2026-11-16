---
type: entity
tags: [linux-kernel, block-layer, io-scheduler, elevator, deadline, bfq]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel I/O Scheduler Framework

## 定义

I/O 调度器 (Elevator) 对块设备上的 I/O 请求进行排序和合并，以优化磁盘吞吐量和响应时间。Linux 提供 plug 机制和多种调度器 (mq-deadline、bfq、none)。

## 关键要点

- **elevator_mq_ops**: 调度器操作接口，核心是 `dispatch_request()`
- **mq-deadline**: 期限调度器，按 sector 排序 + FIFO 过期机制，保证延迟 bound
- **BFQ (Budget Fair Queueing)**: 预算公平队列调度器，按预算比例分配带宽，适合桌面和交互场景
- **none**: 无调度器，请求按 FIFO 直接下发，最大化吞吐量
- **plug**: 批量合并机制，延迟 request 分发以增加合并机会
- **blk_mq_sched_dispatch_requests()**: 分发入口，调用调度器的 dispatch_request()

## 调度器对比

| 调度器 | 策略 | 优先级 | 延迟保证 | 适用场景 |
|--------|------|--------|----------|----------|
| mq-deadline | Sector 排序 + 过期 | 3级 (RT/BE/IDLE) | 有 | 通用、SSD、NVMe |
| bfq | 预算公平 | 多级 (cgroup) | 有 | 桌面、交互、低延迟 |
| none | 无 (FIFO) | 无 | 无 | 高速存储、直接访问 |

## mq-deadline 调度器

### 核心结构
```c
struct deadline_data {
    struct list_head dispatch;     // 待分发队列
    struct dd_per_prio per_prio[DD_PRIO_COUNT]; // 3种优先级
    enum dd_data_dir last_dir;    // 上次方向
    unsigned int batching;        // 批次计数
    unsigned int starved;         // 读饥饿计数
    int fifo_expire[DD_DIR_COUNT]; // 过期时间
    int writes_starved;          // 写饥饿上限
};

struct dd_per_prio {
    struct rb_root sort_list[DD_DIR_COUNT];  // 按 sector 排序
    struct list_head fifo_list[DD_DIR_COUNT]; // 按 FIFO 时间排序
};
```

### 分发流程
```
dd_dispatch_request()
    1. 优先处理 dispatch 列表
    2. 检查优先级老化请求
    3. 按优先级顺序选择:
       - 检查批次限制，继续同方向
       - 选择数据方向 (读/写)
       - 从红黑树选 sector 相邻请求
       - 或从 FIFO 取最早请求
```

## BFQ 调度器

- **bfq_queue**: 每个进程的 I/O 队列，有预算 (budget)
- **budget fair**: 按预算比例分配带宽
- **strict guarantees**: 单请求模式确保调度顺序
- **waker**: 检测同步 I/O 模式，减少饥饿

## 相关概念

- [[entities/linux/kernel/block/linux-kernel-block-mq]] — blk-mq 调度器集成接口
- [[entities/linux/kernel/block/linux-kernel-block-core]] — 块层核心数据结构

## 来源详情

- [[sources/notes-kernel]] — block_scheduler.md
