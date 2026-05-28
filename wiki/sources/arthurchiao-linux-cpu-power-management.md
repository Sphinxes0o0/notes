---
type: source
source-type: web
title: "Linux Server Power and Performance Management: CPU Hardware Basics"
author: "Arthur Chiao"
date: 2022
url: https://arthurchiao.art/blog/linux-cpu-1-zh/
summary: "Linux CPU power management hardware concepts: CPU topology, P-states/C-states, frequency control, TDP, and hyper-threading fundamentals for server power management."
tags: [linux, cpu, power-management, performance, hardware]
created: 2026-05-28
---

# Linux Server Power and Performance Management: CPU Hardware Basics

## Core Content

### CPU Topology Hierarchy
- **Package**: Physical socket on motherboard containing cores
- **Core**: Hardware processor units, each can execute independently
- **Hyper-Threading**: Hardware threads sharing L1 cache within a core; doubles logical CPU count
- **Logical CPU**: Scheduling unit the Linux kernel manages; each has own run queue

### Frequency Concepts
- **P-State**: Voltage-frequency combination stored in MSR (Model Specific Registers). Higher frequency = higher voltage = more power
- **LFM/HFM**: Low Frequency Mode / High Frequency Mode — min/max frequencies in P-state table
- **Base Frequency**: Marketing term for HFM (p-state maximum)
- **Turbo/Boost**: Dynamic overclocking when some cores idle. Constraint: "higher turbo frequency = fewer cores can operate at that frequency"
- **TDP**: Thermal Design Power — average power at base frequency

### Key Insight
Kernel task scheduling operates on **logical CPUs**, not physical cores. With hyper-threading, sibling hardware threads can run at **different frequencies**.

## Key Takeaways
- Linux scheduler works on logical CPUs, not physical cores
- Modern CPUs with HT show sibling threads can have different frequencies
- TDP is baseline consumption; turbo operations exceed TDP and need better cooling
- Turbo boost is limited by total power/thermal budget across all cores

## Related Pages
- [[entities/linux/kernel/cpu-power-management]] — Entity page with detailed power management
- [[entities/linux/kernel/irq-softirq]] — Related IRQ handling concepts
- [[entities/linux/network/net-stack-implementation-rx]] — Network RX path (CPU state impacts packet processing latency)

## Images

![CPU Package Structure](attachments/arthurchiao/linux-cpu-power-management/cpu-package.png)
*Figure: CPU Package — physical socket containing cores and shared resources*

![Package, Die, Core, HT Hierarchy](attachments/arthurchiao/linux-cpu-power-management/pkg-core.png)
*Figure: CPU topology hierarchy: Package → Die → Core → Logical CPU (HT)*

![Hyper-Threading](attachments/arthurchiao/linux-cpu-power-management/hyper-threading.png)
*Figure: Hyper-Threading — sibling threads sharing L1 cache within a core*

![P-State vs Speed Shift](attachments/arthurchiao/linux-cpu-power-management/P-state-vs-speed-shift.png)
*Figure: P-State voltage/frequency relationship — higher frequency = higher voltage = more power*

![Turbo Frequency](attachments/arthurchiao/linux-cpu-power-management/i9-9900k-turbo-freq.png)
*Figure: Turbo boost — dynamic overclocking when some cores idle*

## CPU Topology Architecture

```mermaid
flowchart TD
    subgraph Package["Package (Socket)"]
        subgraph Die1["Die / Chip"]
            subgraph Core1["Core 0"]
                HT1[Logical CPU 0<br/>HW Thread 1]
                HT2[Logical CPU 1<br/>HW Thread 2]
            end
            subgraph Core2["Core 1"]
                HT3[Logical CPU 2]
                HT4[Logical CPU 3]
            end
        end
        CACHE[L3 Cache<br/>Shared]
    end

    P_STATE[P-State<br/>Voltage/Frequency]
    C_STATE[C-State<br/>Power Saving]
    TURBO[Turbo Boost<br/>Dynamic Overclocking]

    HT1 --- HT2
    HT3 --- HT4
    Core1 --- CACHE
    Core2 --- CACHE

    style Package fill:#e3f2fd
    style Die1 fill:#fff3e0
    style Core1 fill:#e8f5e9
    style Core2 fill:#e8f5e9
```
