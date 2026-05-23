---
type: source
source-type: pdf
title: "Concurrency & Parallel Programming (2 books)"
author: "Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau; Paul E. McKenney"
date: 2026-05-23
size: medium
path: raw/PDFs/books/threads-locks.pdf, raw/PDFs/books/perfbook-e2-rc11.pdf
summary: "2册并发与并行编程经典：Arpaci-Dusseau OSTEP Concurrency章（线程/锁/条件变量/信号量/死锁）、Paul McKenney perfbook（RCU/无锁同步/内存屏障/并行性能）"
---

# Concurrency & Parallel Programming (2 books)

## Core Content

### 1. Threads & Locks (from OSTEP, Arpaci-Dusseau, 22 pages)

The concurrency chapter from OSTEP's virtual machine section — a concise yet thorough treatment of the fundamental concurrency primitives and patterns.

**Threads Overview (Chapter 26):**
- Thread creation and join: pthread_create, pthread_join
- Shared data and race conditions: why concurrency is hard
- Atomic operations and critical sections
- Thread control flow: running on single/multiple CPUs, context switching

**Interlude: Thread API (Chapter 27):**
- pthread_create: thread attributes, argument passing
- pthread_join: collecting results
- pthread_mutex: initialization, locking, error handling
- pthread_cond_wait/signal: condition variable patterns (Mesa vs Hoare semantics)
- Common pitfalls: unnecessary locking, incorrect lock ordering, signal vs broadcast

**Locks (Chapter 28):**
- Lock basics: lock/unlock semantics, mutual exclusion
- Evaluating locks: mutual exclusion, fairness, performance
- Interrupt-based spin locks (on single CPU)
- Test-and-set (TAS) spin locks: basic hardware support for locking
- Compare-and-swap (CAS): lock-free operation basis
- Load-linked/store-conditional (LL/SC): MIPS/ARM/PowerPC alternatives
- Ticket locks: fair spin locks with ticket counters
- Yield-based approach: yield() to avoid busy-waiting
- Queue-based locks: parking/unparking to avoid wasted CPU cycles
- Two-phase locks: spin-then-sleep hybrid approach

**Condition Variables (Chapter 29):**
- Producer/consumer problem: signaling patterns, Mesa semantics
- Covering conditions: pthread_cond_broadcast usage

**Semaphores (Chapter 31):**
- Dijkstra's semaphore: P()/V() operations, binary vs counting semaphores
- Thread join, producer/consumer, reader-writer lock implementations
- Dining philosophers problem: deadlock, starvation, solution patterns

**Concurrency Bugs (Chapter 32):**
- Non-deadlock bugs: atomicity violation, order violation
- Deadlock bugs: circular wait, mutex lock ordering, prevention strategies

**Event-Based Concurrency (Chapter 33):**
- select()/poll() event loops, callback-based programming
- Single-threaded event handling, blocking system calls problem

### 2. Is Parallel Programming Hard, And, If So, What Can You Do About It? (perfbook, Paul E. McKenney, 2nd Ed RC11, 601 pages)

The definitive guide to parallel programming for Linux kernel developers and performance engineers, with deep coverage of RCU, lock-free data structures, and memory models.

**Introduction (Ch 1-2):**
- Historic difficulties in parallel programming
- Performance vs productivity vs generality tradeoffs
- Work partitioning and parallel access control strategies
- Hardware interaction: cache coherence, memory ordering, false sharing

**Hardware & Its Habits (Ch 3-4):**
- CPU cache hierarchy: L1/L2/L3, cache lines, cache coherence protocols (MESI/MOESI)
- Memory barriers: load-load, load-store, store-load, store-store; DMB/DMB/DSB (ARM), mfence/lfence/sfence (x86)
- Hardware atomic operations: CAS, LL/SC, fetch-and-add, atomic RMW

**Locking (Ch 5-6):**
- Spinlocks: ticket locks, MCS locks, qspinlock, qrwlock
- Locking overhead: contention, cacheline bouncing, lock hold time
- Lock profiling: lock_stat, lockdep, perf lock
- Read-copy-update (RCU) preliminary view

**Deferred Processing (Ch 7-8):**
- RCU fundamentals: grace periods, quiescent states, synchronization (synchronize_rcu/call_rcu)
- RCU API: rcu_read_lock/unlock, rcu_assign_pointer, rcu_dereference, RCU list/hlist/tree
- RCU variants: Tree RCU, Tiny RCU, SRCU, Tasks RCU
- Hazard pointers vs RCU comparison

**Data Structures (Ch 9-11):**
- Concurrent linked lists: RCU-protected, lock-based, lock-free variants
- Concurrent hash tables: resizing, RCU-based lock-free reader
- Concurrent queues: MPMC, SPSC, M&S queue, RCU-based queue
- Concurrent trees: RCU-protected radix tree, rbtree

**Memory Ordering (Ch 12-14):**
- Formal memory models: Sequential Consistency (SC), Total Store Order (TSO), Relaxed Memory Model (RMO)
- Alpha, x86, ARM, PowerPC memory models comparison
- Linux kernel memory barriers: smp_mb, smp_rmb, smp_wmb, READ_ONCE, WRITE_ONCE
- C11/C++11 memory model: memory_order_relaxed/consume/acquire/release/acq_rel/seq_cst

**Validation & Tools (Ch 15-17):**
- Formal verification: Promela/SPIN model checking
- Linux kernel locking validation: lockdep, sparse, KCSAN (Linux kernel concurrency sanitizer)
- Performance measurement: perf, ftrace, eBPF-based profiling

## Key Quotes

- "Locks are one of the fundamental building blocks of concurrent programming, providing mutual exclusion to critical sections" — Arpaci-Dusseau
- "Parallel programming is hard because of the need to manage the interactions between concurrent activities" — Paul E. McKenney

## Related Pages

- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — Kernel locking mechanisms
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU subsystem
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — CPU scheduling
- [[kernel-subsystems-index]] — Kernel subsystems
- [[entities/cpp/concurrency]] — C++ concurrency
- [[entities/cpp/cpp-perf-optimization]] — C++ performance optimization
- [[entities/os/os-process-thread]] — Process and thread model
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — Memory allocators
- [[sys-prog-index]] — System programming
- [[cpp-index]] — Modern C++
