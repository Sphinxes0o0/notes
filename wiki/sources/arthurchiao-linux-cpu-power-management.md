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
