---
type: source
source-type: bookmark
title: "并行编程导论 — HPC Wiki Parallel Programming Introduction"
author: "HPC Wiki"
date: 2026-05-29
size: medium
path: https://hpcwiki.io/parallel-programming/parallel-programming-intro/
summary: "HPC Wiki introduction to parallel programming covering CPU power wall, shared memory (Pthreads/OpenMP) vs message passing (MPI), and Foster's design methodology."
---

# Parallel Programming Introduction

## Core Content

HPC Wiki introduction to parallel computing paradigms and methodology.

### Key Topics
- **CPU Power Wall (2003)**: End of Dennard scaling, shift to multi-core
- **Processes vs Threads**: Execution units, address space models
- **Shared Memory**: Pthreads, OpenMP — threads share address space
- **Message Passing**: MPI — distributed memory model
- **Foster's Design Methodology**:
  1. Partitioning — divide work into subtasks
  2. Communication — exchange data between units
  3. Agglomeration — merge subtasks to reduce overhead
  4. Mapping — assign tasks to processors for load balancing
- **Learning Path**: MPI, OpenMP, CUDA — Pi computation, matrix multiply

### Communication Overhead
Emphasizes minimizing communication between processing units as key to parallel performance.

## Why This Matters for Pyramid Wiki

- Relevant to [[concurrency]] patterns and parallel computing
- Covers [[computer-architecture]] memory models and multi-core considerations
- Related to [[load-balancing]] and distributed task scheduling
- Links to GPU architecture (CUDA) — [[memory-hierarchy]] considerations

## Related Pages
- [[concurrency]] - concurrency patterns
- [[computer-architecture]] - CPU/memory architecture
- [[memory-hierarchy]] - cache hierarchies
- [[load-balancing]] - load distribution
