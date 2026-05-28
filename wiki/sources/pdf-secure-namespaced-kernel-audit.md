---
type: source
source-type: pdf
title: Secure Namespaced Kernel Audit for Containers
author: Unknown (2021)
date: 2021
size: medium
path: raw/PDFs/papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf
summary: Extends the Linux Audit subsystem to operate within container namespaces, enabling per-container audit without host-level privilege escalation.
created: 2026-05-27
tags: []
---
# Secure Namespaced Kernel Audit for Containers

## Core Content

This paper addresses a fundamental gap in container isolation: standard Linux Audit (auditd) operates at the host level, meaning containers cannot independently manage, query, or filter their own audit logs without host root privileges. The authors propose **namespaced audit**, integrating audit subsystem awareness into Linux namespace isolation.

### Key Contributions

- **Problem**: Containers are isolated via namespaces (PID, mount, network, etc.) but audit events are collected host-wide. Containerized applications wanting audit logs must either: (a) run privileged, or (b) accept host-level event flood.
- **Architecture**: Extend the kernel's audit subsystem to be namespace-aware. Each container can have its own audit filter rules, audit daemon (inside the container), and event stream — all without host privileges.
- **Implementation**: Patch to the Linux kernel audit subsystem. Key changes:
  - Audit netlink socket is made namespace-scoped.
  - Per-namespace audit rules stored in a namespace-local data structure.
  - Filter logic checks the task's container membership before applying rules.
  - Container-init process acts as the audit daemon for that namespace.
- **Security**: Uses seccomp and capability bounding to prevent a compromised container from spoofing audit events or escaping namespace boundaries.
- **Performance**: Evaluated overhead <5% on syscall-heavy workloads.

### Key Findings

- Linux namespace isolation is incomplete without audit isolation.
- Namespaced audit enables compliance frameworks (PCI-DSS, SOC 2) to be satisfied per-container.
- The approach requires kernel modification but is architecturally minimal.

## Source Details

- **Path**: raw/PDFs/papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf
- **Size**: 773.4 KB
- **Domain**: Kernel security, containers, Linux audit subsystem