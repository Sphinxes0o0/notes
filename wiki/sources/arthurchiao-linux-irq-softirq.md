---
type: source
source-type: web
title: "Linux Interrupt and Softirq Fundamentals"
author: "Arthur Chiao"
date: 2022
url: https://arthurchiao.art/blog/linux-irq-softirq-zh/
summary: "Linux kernel interrupt architecture: hard IRQ handling, softirq subsystem, tasklets, workqueues, ksoftirqd per-CPU threads, and deferred interrupt handling patterns."
tags: [linux, kernel, interrupt, softirq, tasklet, workqueue, irq]
created: 2026-05-28
---

# Linux Interrupt and Softirq Fundamentals

## Core Architecture

### Hard IRQ (IRQ)
CPU receives interrupt signal → pauses current work → executes ISR from Interrupt Vector Table → resumes.

**Types:**
- I/O interrupts (shared IRQ lines, must be fast)
- Timer interrupts (system timekeeping)
- Interprocessor interrupts (IPI, CPU-to-CPU)

**Fundamental problem:** ISR must be very fast, yet may need complex logic (e.g., network packet processing).

**Solution:** Split interrupt handling:
- **Top half**: Critical work in hardirq context
- **Bottom half**: Deferred work (softirq/tasklet/workqueue)

### Softirq Subsystem
Per-CPU `ksoftirqd` kernel threads process deferred interrupt work via `__do_softirq()`.

**10 softirq types in Linux 5.10:**
```
HI_SOFTIRQ (tasklet high priority)
TIMER_SOFTIRQ
NET_TX_SOFTIRQ
NET_RX_SOFTIRQ ← Network RX
BLOCK_SOFTIRQ
IRQ_POLL_SOFTIRQ
TASKLET_SOFTIRQ (tasklet normal)
SCHED_SOFTIRQ
HRTIMER_SOFTIRQ
RCU_SOFTIRQ
```

**Triggering flow:**
1. `open_softirq()` — register handler
2. `raise_softirq()` — mark pending, wake ksoftirqd
3. `ksoftirqd` scheduler runs handler

**CPU starvation prevention:** Budget mechanism (`MAX_SOFTIRQ_TIME`).

## Three Deferred Execution Mechanisms

| Feature | softirq | tasklet | workqueue |
|---------|---------|---------|-----------|
| Creation | Static (compile-time) | Dynamic (runtime) | Dynamic (runtime) |
| Context | Softirq | Softirq | Kernel process |
| Migration | Bound to raised CPU | Cannot migrate | Configurable |
| Atomicity | Yes | Yes | No (can sleep) |

**Key insight:** Tasklets are dynamic but built on softirqs (HI_SOFTIRQ/TASKLET_SOFTIRQ). Workqueues run in process context allowing sleeping.

## Network Context
- **NET_RX_SOFTIRQ** handles incoming packets via `net_rx_action()`
- **NET_TX_SOFTIRQ** handles outgoing packets via `net_tx_action()`

## Related Pages
- [[entities/linux/kernel/irq-softirq]] — Entity page
- [[entities/linux/network/net-stack-implementation-rx]] — Where softirq processes RX
- [[entities/linux/network/net-stack-tuning-rx]] — Softirq tuning parameters
