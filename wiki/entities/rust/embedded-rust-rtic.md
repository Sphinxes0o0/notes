---
type: entity
tags: [embedded-rust, rtic, real-time, interrupt, concurrency, scheduler]
created: 2026-05-29
sources: [bookmark-rust-embedded-drivers]
---

# Embedded Rust RTIC

## 定义

RTIC (Real-Time Interrupt-driven Concurrency) 是嵌入式 Rust 的并发框架，通过静态优先级调度和资源管理，实现确定性的实时任务执行，避免堆分配的动态内存开销。

## 关键要点

- **任务类型**:
  - `#[task]` — 异步任务，由中断或软件触发
  - `#[idle]` — 系统空闲时运行（无任务就绪时）
  - `#[init]` — 系统启动时运行一次
- **资源管理**: `#[shared]` 共享资源带优先级协议（`lock`），`#[local]` 独占资源
- **软件任务**: 通过 `spawn()` 跨中断上下文触发任务
- **定时器**: `#[task]` 可绑定硬件定时器（`timer0`）实现周期性执行
- **静态调度**: 所有任务优先级在编译时确定，无动态调度器开销
- **栈使用**: 任务栈静态分配，无堆分配，无栈溢出风险
- **与 FreeRTOS 的区别**: RTIC 是静态单栈模型（任务间共享栈），FreeRTOS 是多栈模型
- **版本**: RTIC 0.6（基于 async/await）、RTIC 1.0（简化模型）

## 核心概念

```
app! {
    resources: { shared: u32 },    // 共享资源
    init: (),                       // 启动任务
    idle: (),                       // 空闲任务
}

#[task(resources = [shared])]
fn task1(ctx: task1::Context) {
    *ctx.resources.shared += 1;
}
```

## 相关概念

- [[embedded-rust-hal]] — RTIC 调度器底层使用 HAL 定时器和 GPIO
- [[embedded-rust-pac]] — RTIC 通过 PAC 操作 NVIC（嵌套向量中断控制器）
- [[embedded-rust-drivers]] — 驱动（DHT22 驱动中的定时读取）可在 RTIC 任务中运行
- [[rust-language]] — Rust 生命周期和所有权确保 RTIC 资源安全共享
