---
type: source
source-type: pdf
title: "Creating and Countering the Next Generation of Linux Rootkits using eBPF"
author: "BlueFog / Doyensec Research"
date: 2023
size: medium
path: raw/PDFs/papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf
summary: "Demonstrates how eBPF can be weaponized to build kernel-level rootkits with unprecedented stealth, then proposes detection countermeasures using eBPF-based integrity monitoring."
created: 2026-05-27
---

# Creating and Countering the Next Generation of Linux Rootkits using eBPF

## Core Content

This research from BlueFog/Doyensec (presented at a security conference) explores the dual-use nature of eBPF in the Linux kernel. It serves as both a red team demonstration and a blue team playbook.

### Attack Surface: eBPF as a Rootkit Vector

The authors implement proof-of-concept eBPF rootkits demonstrating capabilities previously requiring kernel module compilation:

- **Syscall Hooking**: eBPF programs attached to raw tracepoints (e.g., `sys_enter`) can intercept and modify syscall arguments before the kernel processes them — silently rewriting `execve()` arguments, redirecting file reads, or suppressing log output.
- **Network Stack Interception**: Programs attached to XDP or tc (traffic control) hooks can inspect, modify, or drop packets at wire-speed before the kernel's network stack sees them.
- **Stealth**: eBPF programs run in a restricted verifier environment, but the verifier only checks the program itself — not its intended use. Rootkits pass verification while operating maliciously.
- **Persistence**: eBPF programs persist across some reboots via `bpffs` mounting and `bpf()` system call persistence tricks.

### Countermeasures: eBPF-Based Detection

The authors propose defensive techniques:

- **eBPF-based integrity monitoring**: Use eBPF to continuously monitor its own usage — detect newly loaded programs, unusual attachment points, and suspicious map access patterns.
- **Restricting eBPF**: ` CAP_SYS_ADMIN` is the main gate. Proposals include finer-grained capabilities, allowing eBPF for monitoring but not for interception.
- **Kernel lockdown modes**: Align eBPF restrictions with existing lockdown levels.
- **Detection indicators**: New programs loading at runtime, unexpected tracepoint attachments, modifications to syscall argument buffers.

### Key Findings

- eBPF's power-to-risk ratio is extremely high — it effectively provides kernel-level code execution with a much lower barrier to entry than kernel modules.
- The kernel's eBPF subsystem effectively has two attack surfaces: the verifier (bypass), and the attach mechanism (abuse within allowed bounds).
- Defense requires treating eBPF like any other kernel subsystem: restrict capabilities, monitor integrity, and log usage.

## Source Details

- **Organization**: BlueFog / Doyensec Research
- **Path**: raw/PDFs/papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf
- **Size**: 1.8 MB
- **Domain**: Linux security, eBPF, rootkits, kernel exploitation