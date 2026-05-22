---
type: entity
tags: [cpp, llm, inference, ai, performance, distributed-systems]
created: 2026-05-22
sources: [pdf-cpp-slides]
---

# C++ for LLM Inference Frameworks

## Definition

C++ is the language of choice for **production LLM inference frameworks** due to its combination of low-latency scheduling control, zero-cost abstractions, direct hardware control (GPU/NPU memory management), and the ability to handle high-throughput, low-latency serving that Python-based frameworks cannot match.

## xLLM: A Case Study

xLLM (刘童旋, 2025) is an e-commerce LLM inference framework built in C++ targeting Alibaba's PolarDB and e-commerce AI workloads (product image generation, AI数字人, AI marketing content, AI customer service).

## Architecture: Deeply Decoupled Distributed Design

### PD Separation (Prefill/Decode)
LLM inference has two distinct phases:
- **Prefill**: processes the input prompt; compute-bound; processes all tokens in parallel
- **Decode**: generates output tokens one-by-one; memory-bandwidth-bound; attention over KV cache

In traditional designs, Prefill and Decode run on the same GPU. xLLM **dynamically separates** these onto different nodes:
- PD ratio adapts automatically based on Input/Output ratio
- KV Cache migrates between Prefill and Decode nodes as requests progress
- **Result: 1.59X–2.2X throughput improvement**

### EPD Separation (Encoder/Prefill/Decode)
Going further, xLLM splits into three stages for heterogeneous hardware:
- **Encoder** (multimodal models): processes image/audio inputs
- **Prefill**: KV generation
- **Decode**: token generation

Each stage has different compute/memory characteristics and optimal batch sizes, so EPD schedules them on different heterogeneous instances. **Result: up to 3.7X throughput improvement.**

### Unified Online/Offline Scheduling
E-commerce traffic has dramatic peak valleys:
- Load drops → insert offline batch inference requests
- Load spikes → evict offline KV Cache, migrate offline requests

SLO-aware scheduling ensures latency-critical requests get priority. **Result: 3X offline throughput improvement with stable SLO.**

## Runtime Performance Optimizations

### Multi-Layer Pipeline (Asynchronous Execution)
Key insight: scheduling decisions and GPU computation are **not** independent — they are bottlenecks when serialized.

Solution: **asynchronous pipeline**:
- CPU scheduling and GPU/NPU computation overlap
- Different transformer layers' compute and communication overlap
- Different execution units (Cube/Vector/MTE on NPUs) run in parallel

**Result: 5%–10% throughput improvement**, with greater gains for smaller models.

### xTensor: GPU Memory Management
- Custom memory allocator for KV Cache pooling
- Minimizes GPU memory fragmentation
- Enables global KV Cache sharing across requests

### Speculative Inference
Speculative decoding: use a smaller draft model to propose tokens, verify with the larger model. Reduces decode-step latency.

### High-Performance Scheduler
C++ enables:
- Custom scheduling policies (SLO-aware, priority-based)
- Filter mechanisms for request routing
- Custom operators for model-specific kernels

## Why C++ for LLM Inference?

| Factor | Python | C++ |
|--------|--------|-----|
| Latency control | High GC overhead, interpreter | Predictable, minimal overhead |
| GPU memory | Limited control via PyTorch | Direct CUDA/HIP/Level Zero control |
| Scheduling | GIL, async Python overhead | Direct thread/process control |
| Throughput | Batching inefficiencies | Custom batching with zero-copy |
| Custom operators | ffi overhead | Inlined, optimized kernels |

Python is used for model definition and orchestration; **C++ handles production inference paths**.

## Key Design Patterns

### Global KV Cache Pool
- Shared KV Cache across multiple inference requests
- Enables request coalescing and cache sharing
- Reduces redundant computation for similar prompts

### Elastic Load Balancing
- Per-layer/head load balancing for MoE (Mixture of Experts) models
- Dynamic request routing based on current load

### Fault Tolerance
- Fast KV Cache migration on node failure
- Request checkpointing for long-running generations

## Relationship to Existing Entities

- [[entities/cpp/cpp-perf-optimization]] — LLM inference is the ultimate performance engineering problem: cache-aware attention, SIMD matmuls, NUMA-aware KV Cache, profiling with perf/eBPF
- [[entities/cpp/smart-pointers]] — shared ownership of KV Cache tensors; `unique_ptr` for per-request allocations
- [[entities/cpp/concurrency]] — multi-threaded scheduling, async pipelines, thread pools for request handling
- [[entities/cpp/move-semantics]] — passing large tensors between pipeline stages without copying; move-on-send semantics
