---
type: entity
tags: [linux, kernel, cpu, power-management, performance, c-states, p-states]
created: 2026-05-28
sources: [arthurchiao-linux-cpu-power-management]
---

# CPU Power Management

## Definition

Linux CPU power management covers hardware-level frequency control (P-states), idle state management (C-states), thermal design (TDP), and hyper-threading topology — all affecting server performance and power consumption.

## Key Concepts

### CPU Topology
- **Package**: Physical socket on motherboard
- **Core**: Hardware processor unit (can execute independently)
- **Logical CPU**: Scheduling unit Linux kernel manages (each has own run queue)
- **Hyper-Threading**: Hardware threads sharing L1 cache within a core

### Frequency States
- **P-State**: Voltage-frequency combination (higher freq = higher voltage = more power)
- **LFM/HFM**: Low/High Frequency Mode — min/max in P-state table
- **Turbo/Boost**: Dynamic overclocking when cores idle; higher turbo = fewer active cores allowed

### Thermal Design
- **TDP**: Thermal Design Power — average consumption at base frequency
- Turbo operations **exceed TDP**, requiring better cooling

### Key Insight
Linux scheduler operates on **logical CPUs**, not physical cores. With hyper-threading, sibling threads can run at **different frequencies** — contradicting assumptions about core-level uniformity.

## Practical Takeaways
- Disable CPU power saving for consistent packet processing latency
- `AMD_pstat=disable idle=poll noohz=off iommu=pt` for latency-sensitive workloads
- CPU power states directly impact softirq response time

## Related Pages

- [[entities/linux/kernel/irq-softirq]] — Softirq handling affected by CPU idle states
- [[entities/linux/network/net-stack-tuning-rx]] — RX tuning where CPU power state matters
- [[entities/linux/network/net-stack-implementation-rx]] — Softirq processing latency
