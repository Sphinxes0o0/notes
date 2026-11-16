---
type: entity
tags: [linux, ebpf, networking, sockmap, sockhash, socket, acceleration]
created: 2026-05-28
sources: [arthurchiao-sockmap-ebpf]
---

# eBPF Sockmap and Socket Redirection

## Definition

eBPF sockmap/sockhash enables socket-level traffic acceleration by bypassing the TCP/IP stack for same-host communication. BPF sockops programs capture TCP events and store sockets; sk_msg programs intercept sendmsg and redirect data directly to peer socket queues.

## Architecture

### Two BPF Programs

**Program 1 (sockops):**
- Monitors TCP connection events (establishment, termination)
- Extracts socket metadata (IP, port, protocol)
- Stores socket reference in sockhash/sockmap map

**Program 2 (sk_msg):**
- Intercepts `sendmsg()` syscalls
- Extracts key from message metadata
- Calls `msg_redirect_hash()` to bypass TCP/IP stack
- Routes data directly to peer's socket queue

## Key Insight
> "This requires no Cilium — can be implemented with vanilla eBPF."

## Prerequisites
- LLVM Clang for BPF compilation
- bpftool utility
- cgroupv2 support
- Linux kernel 5.3+

## Related Pages

- [[entities/linux/ebpf/ebpf-networking]] — eBPF networking context
- [[entities/linux/network/net-stack-implementation-rx]] — Where socket events originate
- [[entities/linux/ebpf/ebpf-xdp]] — XDP comparison (different hook points)
