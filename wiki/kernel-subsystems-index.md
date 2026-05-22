---
type: index
tags: [linux-kernel, crypto, locking, ipc, rcu, time, sound]
created: 2026-05-22
---

# Linux Kernel — Core Subsystems

> Crypto, locking, IPC, RCU, time management, and sound

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/crypto/linux-kernel-crypto-core]] | Crypto subsystem: crypto_alg registration, skcipher, aead, template mechanism | linux-kernel, crypto |
| [[entities/linux/kernel/locking/linux-kernel-locking-core]] | Locking: spinlock, mutex, rwsem, percpu, lockdep | linux-kernel, locking |
| [[entities/linux/kernel/ipc/linux-kernel-ipc-core]] | IPC: msg, sem, shm, mqueue, pipelined send | linux-kernel, ipc |
| [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] | RCU: Read-Copy-Update, lock-free reads, grace period, srcu | linux-kernel, rcu |
| [[entities/linux/kernel/time/linux-kernel-time-core]] | Time: tick, hrtimer, timekeeping, NTP, posix-timers | linux-kernel, time |
| [[entities/linux/kernel/sound/linux-kernel-sound-core]] | Sound: ALSA, PCM, ASoC, DAPM widget, DAI | linux-kernel, sound |

## Cross-References

- [[kernel-sched-index]] — All these subsystems interact with the scheduler; RCU is scheduler-dependent
- [[os-index]] — IPC and locking are core OS concepts; os-process-thread covers process memory model
- [[kernel-net-index]] — Crypto subsystem used for TLS/IPsec in the network stack
