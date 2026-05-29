---
type: source
source-type: bookmark
title: "Linux Namespace and Cgroup — Container Isolation Fundamentals"
author: "public0821 (SegmentFault)"
date: 2026-05-29
size: medium
path: https://segmentfault.com/a/1190000009732550
summary: "Deep dive into Linux Namespace (resource isolation) and Cgroup (resource control) — the two pillars of container technology."
---

# Linux Namespace and Cgroup

## Core Content

Comprehensive series covering Linux container isolation primitives: Namespace for isolation, Cgroup for resource limits.

### Namespace Series
1. **Overview**: What namespaces are and why they matter
2. **UTS Namespace** (CLONE_NEWUTS): Hostname/domain isolation
3. **IPC Namespace** (CLONE_NEWIPC): System V IPC, POSIX message queues
4. **Mount Namespace** (CLONE_NEWNS): Filesystem mount points
5. **PID Namespace** (CLONE_NEWPID): Process ID isolation
6. **Network Namespace** (CLONE_NEWNET): network interfaces, routing tables, iptables
7. **User Namespace** (CLONE_NEWUSER): UID/GID mapping, privilege isolation
8. **Container Demo**: Building a simple container using namespaces

### Cgroup Series
1. **Overview**: Control groups architecture
2. **Creating/Managing**: cgroup filesystem, cgcreate/cgdelete
3. **PIDs Subsystem**: Limiting process counts
4. **Memory Subsystem**: Memory limits, OOM handling
5. **CPU Subsystem**: CPU shares, cpuset, bandwidth control

## Why This Matters for Pyramid Wiki

- Core to [[container-technology]] and [[cloud-native]] deep dives
- Essential for understanding Docker, Kubernetes, and container runtimes
- Relates to [[linux-kernel-mm]] memory management and process scheduling
- Relevant to [[linux-kernel-ipc-core]] IPC mechanisms

## Related Pages
- [[container-technology]] - container technology overview
- [[cloud-native]] - cloud native architecture
- [[linux-kernel-ipc-core]] - IPC mechanisms
- [[linux-kernel-mm-swap]] - memory management
