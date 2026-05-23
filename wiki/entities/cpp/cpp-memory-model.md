---
type: entity
tags: [c, cpp, concurrency, memory-model, atomics, memory-barriers]
created: 2026-05-23
sources: [pdf-concurrency-perf]
---

# C/C++ Memory Model and Atomics

## Definition

The formal specification of how threads interact through shared memory, defining the ordering constraints on memory operations and the semantics of atomic operations. Correct concurrent code depends on understanding the memory model.

## Key Concepts

- **Sequential Consistency (SC)**: The intuitive model where all operations appear in a global total order consistent with program order. The gold standard for correctness but expensive to enforce on modern hardware.
- **Acquire/Release Semantics**: An acquire operation (e.g., lock, atomic load with memory_order_acquire) ensures subsequent reads/writes are not reordered before it. A release operation (e.g., unlock, atomic store with memory_order_release) ensures preceding reads/writes are not reordered after it.
- **C++11 Memory Orderings**: memory_order_relaxed (no ordering constraints), memory_order_consume (data dependency ordering), memory_order_acquire, memory_order_release, memory_order_acq_rel (both), memory_order_seq_cst (strongest, default).
- **Hardware Memory Models**: x86-TSO (Total Store Order, relatively strong: only store-load reordering), ARMv8 (weak: many reorderings possible without barriers), PowerPC (weak), Alpha (weakest: even dependent reads can be reordered).
- **Memory Barriers/Fences**: Compiler barriers (asm volatile("" ::: "memory")), hardware barriers (mfence/lfence/sfence on x86, DMB/DSB/ISB on ARM), Linux kernel barriers (smp_mb/smp_rmb/smp_wmb).

## Common Patterns

- **Lock-Free Programming**: Using CAS (compare-and-swap) or LL/SC for concurrent data structures without locks. Requires ABA problem handling (tagged pointers, hazard pointers, RCU).
- **Double-Checked Locking**: Test without lock, then acquire lock and re-test. Safe only with proper memory ordering (C++11 magic statics make this unnecessary for singletons).
- **Read-Copy-Update (RCU)**: Lock-free readers (rcu_read_lock/unlock provides ordering), grace-period-based reclamation.

## Related Concepts

- [[entities/cpp/concurrency]] — C++ concurrency primitives
- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — Kernel locking mechanisms
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU synchronization
- [[entities/cpp/cpp-perf-optimization]] — Performance optimization
- [[cpp-index]] — Modern C++

## Source Details

- [[sources/pdf-concurrency-perf]] — perfbook: Chapters 12-14 on memory ordering; threads-locks chapter on atomics
