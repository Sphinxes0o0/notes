---
title: Coroutine 和 I/O 线程
---

# Coroutine 和 I/O 线程分析

## bdrv_co_* 函数

```c
// block/io.c

// 驱动程序读取分派
bdrv_driver_preadv()
  → 调用具体驱动实现

// 驱动程序写入分派
bdrv_driver_pwritev()
  → 调用具体驱动实现

// 对齐读取
bdrv_aligned_preadv()

// 复制时读取实现
bdrv_co_do_copy_on_readv()
```

## 协程 I/O 模式

```c
typedef struct CoroutineIOCompletion {
    Coroutine *coroutine;            // 协程
    int ret;                         // 返回值
} CoroutineIOCompletion;

static void bdrv_co_io_em_complete(void *opaque, int ret)
{
    CoroutineIOCompletion *co = opaque;
    co->ret = ret;
    aio_co_wake(co->coroutine);     // 唤醒暂停的协程
}
```

## AioTaskPool

```c
// block/aio_task.c
struct AioTaskPool {
    Coroutine *main_co;              // 主协程
    int status;                      // 状态
    int max_busy_tasks;             // 最大并发任务数
    int busy_tasks;                 // 当前忙碌任务数
    bool waiting;                   // 等待标志
};

Coroutine *aio_task_pool_new(int max_busy_tasks);
void aio_task_pool_start_task();
void aio_task_pool_wait_all();
```

## Drain 机制

```c
bdrv_co_drain_bh_cb()               // 排空完成底部处理
bdrv_co_yield_to_drain()            // 让出给排空
bdrv_drain_poll()                   // 轮询进行中的请求
```

## I/O 路径

```
同步路径:
  bdrv_preadv/pwritev()
    → bdrv_co_preadv/pwritev()

异步路径:
  bdrv_co_preadv/pwritev()
    → bdrv_driver_preadv/pwritev()
      → qemu_coroutine_yield()
        → aio_poll()
          → 恢复协程
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `io.c` | 协程 I/O 操作 |
| `aio_task.c` | AioTaskPool 并行协程 |
| `thread-pool.c` | 线程池实现 |
