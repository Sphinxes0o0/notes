---
type: entity
tags: [linux, kernel, interrupt, softirq, tasklet, workqueue, irq]
created: 2026-05-28
sources: [arthurchiao-linux-irq-softirq]
---

# IRQ and Softirq

## Definition

Linux kernel interrupt architecture: hardware interrupts (IRQ) that must execute fast, and deferred processing via softirq/tasklet/workqueue mechanisms for complex or lengthy work.

## Architecture

### Hard IRQ (Top Half)
CPU receives interrupt → pauses work → executes ISR from Interrupt Vector Table → resumes. Must be **very fast** to avoid losing events.

**Types:**
- I/O interrupts (shared IRQ lines, PCI)
- Timer interrupts
- Interprocessor interrupts (IPI, CPU-to-CPU)

### Softirq (Bottom Half)
Per-CPU `ksoftirqd` kernel threads process deferred work via `__do_softirq()`. 10 types in Linux 5.10:

| Softirq | Purpose |
|---------|---------|
| `NET_RX_SOFTIRQ` | Network RX processing |
| `NET_TX_SOFTIRQ` | Network TX processing |
| `HI_SOFTIRQ` | High-priority tasklets |
| `TASKLET_SOFTIRQ` | Normal tasklets |
| `TIMER_SOFTIRQ` | Timer deferred work |
| `RCU_SOFTIRQ` | RCU callback processing |

### Three Deferred Mechanisms

| Feature | softirq | tasklet | workqueue |
|---------|---------|---------|-----------|
| Creation | Static (compile-time) | Dynamic | Dynamic |
| Context | Softirq | Softirq | Kernel process |
| Can sleep | No | No | Yes |

## Key Concepts
- **Budget mechanism**: `MAX_SOFTIRQ_TIME` prevents softirqs from starving user processes
- **time_squeeze**: In `/proc/net/softnet_stat` — softirq budget exhausted but packets remain in ring
- **Two trigger paths**: ksoftirqd thread OR after hard IRQ handler exits via `irq_exit()`

## Related Pages

- [[entities/linux/kernel/cpu-power-management]] — CPU idle states affect softirq latency
- [[entities/linux/network/net-stack-implementation-rx]] — NET_RX_SOFTIRQ processes incoming packets
- [[entities/linux/network/net-stack-tuning-rx]] — Softirq budget tuning
