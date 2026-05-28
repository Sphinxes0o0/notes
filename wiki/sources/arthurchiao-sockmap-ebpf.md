---
type: source
source-type: web
title: "Socket Acceleration with eBPF Sockmap/Redirection"
author: "Arthur Chiao (translation of Cyral.com)"
date: 2021
url: https://arthurchiao.art/blog/socket-acceleration-with-ebpf-zh/
summary: "eBPF sockmap/sockhash: BPF sockops program captures TCP events and stores sockets; sk_msg program intercepts sendmsg and redirects data directly to peer socket queues, bypassing TCP/IP stack."
tags: [linux, ebpf, networking, sockmap, sockhash, socket, acceleration]
created: 2026-05-28
---

# Socket Acceleration with eBPF Sockmap/Redirection

## Core Concept
For applications where source and destination are on the same machine, eBPF sockmap **bypasses the entire TCP/IP stack**, sending data directly to the socket peer queue.

## Architecture

### Two BPF Programs Working Together

**Program 1 (sockops):**
- Monitors TCP connection events (establishment, termination)
- Extracts socket metadata (IP, port, protocol)
- Stores socket reference in sockhash map

**Program 2 (sk_msg):**
- Intercepts `sendmsg()` syscalls
- Extracts key from message metadata
- Calls `msg_redirect_hash()` to bypass TCP/IP stack
- Routes data directly to peer's socket queue

### Map Definition
```c
struct bpf_map_def sock_ops_map = {
    .type = BPF_MAP_TYPE_SOCKHASH,
    .key_size = sizeof(struct sock_key),
    .value_size = sizeof(int),
    .max_entries = 65535,
};
```

## Key Insight
> "This requires no Cilium — can be implemented with vanilla eBPF."

## Prerequisites
- BPF development environment (LLVM Clang)
- bpftool utility
- cgroupv2 support
- Linux kernel 5.3+ (tested on 5.8)

## Compilation & Loading
```bash
# Compile
clang -O2 -g -target bpf -c bpf_sockops.c -o bpf_sockops.o
clang -O2 -g -target bpf -c bpf_redir.c -o bpf_redir.o

# Load sockops, attach to cgroup
bpftool prog load bpf_sockops.o /sys/fs/bpf/bpf_sockops type sockops
bpftool cgroup attach /sys/fs/cgroup/unified/ sock_ops pinned /sys/fs/bpf/bpf_sockops

# Load sk_msg, attach to sockmap
bpftool prog load bpf_redir.o /sys/fs/bpf/bpf_redir map name sock_ops_map pinned /sys/fs/bpf/sock_ops_map
bpftool prog attach pinned /sys/fs/bpf/bpf_redir msg_verdict pinned /sys/fs/bpf/sock_ops_map
```

## Related Pages
- [[entities/linux/ebpf/ebpf-networking]] — eBPF networking context
- [[entities/linux/ebpf/sockmap-sockhash]] — Entity page
- [[entities/linux/network/net-stack-implementation-rx]] — Where socket events originate
