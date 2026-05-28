---
type: entity
tags: [memory-hierarchy, cache, TLB, storage, von-neumann]
created: 2026-05-28
sources: [bookmark-archbase]
---

# Memory Hierarchy

## 定义

存储层次是从CPU寄存器到外部存储的多个速度/容量/成本不同层次的组合，利用程序局部性原理（时间局部性+空间局部性）在成本可控的前提下提供接近最快层的访问速度。

## 关键要点

### 存储层次
| 层次 | 典型容量 | 访问延迟 | 带宽 | 介质 |
|------|---------|---------|------|------|
| 寄存器 | <1KB | 0 cycle | ~1TB/s | SRAM |
| L1 Cache | 32-64KB/core | 1-2 cycle | ~1TB/s | SRAM |
| L2 Cache | 256KB-1MB/core | ~10 cycle | ~500GB/s | SRAM |
| L3 Cache | 8-32MB/shared | ~40 cycle | ~100GB/s | SRAM |
| DRAM | 8-64GB | ~100ns | ~50GB/s | DDR |
| SSD/NVMe | 256GB-2TB | ~10μs | ~5GB/s | NAND Flash |
| HDD | TB级 | ~10ms | ~100MB/s | 磁盘 |

### Cache 映射方式
- **直接映射**：每地址只能出现在一个固定Cache行，简单但冲突多
- **N路组相联**：每地址可在N行中选择，平衡效率和命中率
- **全相联**：任意位置，最灵活但查找成本高，适用于TLB小容量场景

### Cache 写策略
- **Write-Through (WT)**：同时写Cache和主存，一致性好但写延迟高
- **Write-Back (WB)**：仅写Cache，替换时写回，开销小但需要额外脏位
- **Write-Allocate / No-Write-Allocate**：写缺失时是否将块调入Cache

### TLB（Translation Lookaside Buffer）
- 虚拟地址到物理地址转换的旁路缓存
- 查找过程：虚拟页号→TLB tag比较→物理页号+页内偏移
- TLB Shootdown：多核修改页表时通知其他核失效TLB，开销大
- 软件管理TLB（LoongArch）vs 硬件自动填充（x86）

### 一致性协议
- **MESI**：Modified（脏）/ Exclusive（独占干净）/ Shared（共享干净）/ Invalid（无效）
- **MOESI**：AMD扩展，Owned状态支持脏数据直接转移
- **Snooping**：总线广播监听，适用于小规模多核
- **Directory**：目录协议，适用于大规模多核

### 存储层次与冯·诺依曼瓶颈
- 经典冯·诺依曼结构：以运算器为中心，存储器带宽成为瓶颈
- 改进方向：以存储器为中心、存储与计算融合、Near-Memory Computing

## 相关概念

- [[cache-memory-design]] — Cache架构设计的更多细节（3C缺失/伪共享/预取）
- [[cpu-architecture]] — CPU微架构与Cache的协同设计
- [[os/os-virtual-memory]] — 虚拟内存与物理内存的页表管理
- [[linux/kernel/mm/linux-kernel-mm-page-fault]] — 页错误处理（Cache未命中的类似机制）
- [[qemu-memory]] — QEMU的内存模拟与虚拟化

## 来源详情

- [[sources/bookmark-archbase]] — 计算机体系结构基础（龙芯第3版）：存储层次/总线章节
- [[sources/pdf-cache-memory-architectural-design]] — Cache Memory 架构设计（111页中文原创）
