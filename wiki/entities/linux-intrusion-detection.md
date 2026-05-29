---
type: entity
tags: [security, ids, ips, linux, intrusion-detection]
created: 2026-05-29
sources: [github-snort3-detection]
---

# Linux Intrusion Detection Systems

## Definition

Linux intrusion detection systems (IDS/IPS) monitor network traffic or system calls for malicious activity, policy violations, or anomalous behavior — running as user-space daemons (Snort, Suricata) or kernel-space agents (eBPF-based).

## Categories

### Network-based IDS (NIDS)
- **Snort** — Rule-based signature detection
- **Suricata** — Multi-threaded, IDS/IPS/DPI
- **Zeek (Bro)** — Traffic analysis and logging

### Host-based IDS (HIDS)
- **OSSEC** — Log analysis, file integrity, rootkit detection
- **AIDE** — File integrity checker
- **rkhunter** — Rootkit detection

### eBPF-based Security Tools
- **Falco** — Runtime security, container behavior monitoring
- **eBPF + LSM** — Kernel-level policy enforcement

## Related Concepts

- [[intrusion-detection-system]] — General IDS entity
- [[snort3-deep-architecture]] — Snort3 NIDS architecture
- [[linux-ebpf-security]] — eBPF for security observability

## Sources
- [[github-snort3-detection]]
