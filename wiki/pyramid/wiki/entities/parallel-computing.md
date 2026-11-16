---
type: entity
tags: [parallel-computing, hpc, mpi, openmp, cuda, distributed-memory]
created: 2026-05-29
sources: [bookmark-parallel-programming-intro]
---

# Parallel Computing

## 定义

并行计算是利用多个处理单元同时执行计算任务以提升性能的范式。与串行计算相对，核心挑战是 **通信开销** 和 **负载均衡**。

## 关键要点

### CPU Power Wall (2003)

Dennard 缩放失效后，CPU 性能提升从单核转向多核 — 这是并行计算成为主流的背景。

### 两种内存模型

| 模型 | 代表技术 | 特点 |
|------|----------|------|
| Shared Memory | Pthreads, OpenMP | 线程共享地址空间，需要同步 |
| Distributed Memory | MPI | 进程私有内存，通信显式 |

### Foster's Design Methodology

1. **Partitioning**: 将工作划分为子任务
2. **Communication**: 子任务间交换数据
3. **Agglomeration**: 合并子任务减少通信开销
4. **Mapping**: 分配任务到处理器实现负载均衡

### 通信开销

并行计算的核心开销是进程/线程间通信 — 好的并行算法必须 **最小化数据交换**。

### 技术栈

- **MPI**: Message Passing Interface，分布式内存标准
- **OpenMP**: 共享内存并行，编译指令 `#pragma omp parallel`
- **CUDA/OpenCL**: GPU 并行计算
- **MapReduce**: 大数据批处理范式

## 相关概念

- [[concurrency]] — 并发控制（锁、无锁数据结构）
- [[memory-hierarchy]] — 多级缓存对并行性能的影响
- [[computer-architecture]] — 多核架构
- [[load-balancing]] — 负载均衡策略
- [[distributed-systems]] — 分布式计算（节点间通信）

## 来源详情

- [[bookmark-parallel-programming-intro]] — HPC Wiki 并行编程导论
