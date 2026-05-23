---
type: source
created: 2026-05-23
source-type: pdf
title: "Performance Engineering Slides (2025)"
author: "Various (IIT Bombay, Alibaba, Incredibuild, Shanghai AI Lab)"
date: 2025-12-13
size: medium
path: raw/PDFs/slides/
summary: "5 slides covering kernel bypass for network packet processing, Linux kernel block cache Btree indexing, distributed caching/build acceleration, heterogeneous RDMA transfer, and AI-powered kernel crash diagnosis"
---

# Performance Engineering — C++ Slides Collection

> Group source page for performance engineering slides spanning networking, storage, distributed builds, and system diagnosis.

---

## CS744 — Kernel-Bypass Techniques for High-Speed Network Packet Processing

**Speaker:** Rinku Shah, Priyanka Naik (IIT Bombay, CS744 course)
**File:** `CS744_kernel-bypass_theory_slides.pdf` (34 pages, 12.8K chars)

Academic survey of kernel-bypass techniques for high-speed packet processing.

**Key takeaways:**
- **Standard Linux network stack overhead:** Each packet traverses NIC → Driver → Data Link (L2) → Network (L3) → Transport (L4) → Application — significant CPU overhead and context switches
- **Need for kernel bypass:** 10G/40G/100G line rates overwhelm kernel processing; per-packet overhead becomes the bottleneck
- **Three kernel-bypass approaches:**
  1. **User-space packet processing:**
     - **DPDK (Data Plane Development Kit):** Poll-mode drivers (PMD), hugepages, NUMA-aware, lockless rings — bypasses kernel entirely
     - **Netmap:** Memory-mapped NIC buffers, zero-copy, lightweight — faster but less featureful than DPDK
  2. **User-space network stack (e.g., mTCP):** Full TCP/IP stack in user space; combines kernel bypass with protocol processing
  3. **XDP/eBPF:** In-kernel packet processing at driver level (not strictly bypass, but avoids full stack traversal)
- **Performance comparison:** DPDK achieves 10-80 Mpps (million packets per second) vs Linux kernel's ~1 Mpps on similar hardware
- **Trending topics:** SmartNICs, programmable switches (P4), RDMA (InfiniBand/RoCE/iWARP)

---

## 李勇 — Linux内核块设备缓存的高性能Btree索引设计与实现

**Speaker:** Coly Li (colyli@fnnas.com, Bcache subsystem maintainer, Fnnas kernel architect)
**File:** `李勇_内核块设备缓存的高性能Btree索引设计与实现5.pdf` (21 pages, 5.6K chars)

Bcache's high-performance Btree index for Linux kernel block device caching.

**Key takeaways:**
- **Bcache:** Linux kernel block device cache system — hot data on SSD, cold data on HDD
  - Cache modes: writeback, writethrough, write-around, no cache
- **Key design challenge:** Need to determine if data is cached using an index — LSM-tree-based Btree provides the best performance in Linux kernel
- **Bcache's LSM-tree improvements:**
  - Single node can hold 10,000+ index keys (optimized for IO efficiency)
  - Cacheline-aware data layout for CPU cache efficiency
  - **`struct bkey`:** 3× __u64 (high, low, ptr[]) — stored directly in cache device metadata buckets; loaded into Btree nodes for indexing
  - Uses LBA (Logical Block Address) from read IO requests to search `bkey->low` for cache hit detection
  - **Not** traditional linear search or binary search (cache-unfriendly jumps); instead uses a novel Btree design that is CPU-cache friendly
- Challenges: key insertion, stale key invalidation, building balanced binary trees isn't always feasible

---

## 范颂颂 — 超越并行化：缓存与分布式计算如何重新定义算力加速

**Speaker:** 范颂颂
**File:** `范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速.pdf` (14 pages, 2.7K chars)

Using caching and distributed computing to accelerate AOSP (Android Open Source Project) build times.

**Key takeaways:**
- **Challenge:** Large codebase builds take 40+ minutes; 3000+ builds/week for CI; resource utilization is spiky
- **Combined approach: Parallelization + Caching:**
  - **Incredibuild platform:** Hybrid development acceleration with distribution (to network hosts) + caching (reuse historical results)
  - **BuildCache:** MD5 hash-based build artifact caching:
    - Hash includes: source file contents, compiler version, environment variables, compilation flags
    - Reuses .obj files across identical compilation units
- **Insight:** Increasing cores from 16→64 reduces compile time significantly (2h→50min), but beyond 64 cores there's diminishing returns
- Solution: Virtualization + containerization ensures consistent build environments; resource sharing across developers' workstations

---

## 麻津铭 — DLSlime: 兼顾灵活与高效的点对点RDMA传输工具

**Speaker:** JimyMa (上海人工智能实验室)
**File:** `麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现.pdf` (35 pages, 7.2K chars)

DLSlime: a flexible and efficient point-to-point RDMA transfer library for heterogeneous AI infrastructure.

**Key takeaways:**
- **AI Infra paradigm shift:** Traditional SPMD (single program, multiple data) → Task-heterogeneous (disaggregated architecture) + Device-heterogeneous (unified interconnect)
- **Three core scenarios:**
  1. **Heterogeneous 3D parallelism:** Different chip vendors (NVIDIA, Huawei, Moore Threads) have private communication libraries (NCCL, HCCL, MCCL) — incompatible protocols, resource silos
  2. **Disaggregated inference:** Massive small-message transfers; traditional collective communication libraries designed for large-bulk synchronous communication — low throughput for small messages; lack of one-sided semantics
  3. **Heterogeneous parameter servers:** CPU-GPU communication with high concurrency
- **DLSlime features:**
  - Microsecond-level latency; computation-communication overlap
  - One-sided RDMA semantics (no CPU involvement at receiver)
  - Unified abstraction layer over different RDMA transports (InfiniBand, RoCE)
  - Open source: DeepLink-org/DLSlime

---

## 邹涛 — CRASH_NG：基于AI和内核调试的自动化Linux系统宕机诊断工具

**Speaker:** 邹涛 (Alibaba Cloud Kernel Technical Expert)
**File:** `邹涛_CRASH_NG：基于AI和内核调试的自动化Linux系统宕机诊断工具.pdf` (15 pages, 4.9K chars)

AI-powered automated Linux kernel crash diagnosis tool.

**Key takeaways:**
- **Traditional crash analysis pain points:**
  1. Insufficient log information
  2. VMCORE analysis requires deep kernel expertise
  3. Time-consuming manual root cause analysis
- **CRASH_NG approach:** AI-assisted analysis of kernel crash dumps:
  - Uses LLM to analyze vmcore and dmesg
  - Automates memory state inspection, call trace analysis, and root cause identification
  - Covers: use-after-free, double-free, buffer overflow, driver bugs, race conditions
- **Types of kernel crashes detected:**
  - Hardware: RAM ECC errors, CPU register faults, PCIe bus errors
  - Software: use-after-free, double-free, out-of-bounds, driver logic bugs, race conditions
- Future: integration with eBPF for proactive anomaly detection before crashes occur

---

## Related Pages

- [[entities/cpp/cpp-perf-optimization]] — CPU cache, SIMD, profiling tools
- [[entities/cpp/cpp-llm-inference]] — LLM inference performance (PD disaggregation involves RDMA)
- [[sources/pdf-cpp-slides]] — Previously ingested slides (includes 阿里云 perf talk)
- [[sources/pdf-cpp-compiler-toolchain]] — Compiler/toolchain slides
