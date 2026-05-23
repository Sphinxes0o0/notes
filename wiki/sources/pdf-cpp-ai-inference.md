---
type: source
created: 2026-05-23
source-type: pdf
title: "AI/ML Inference Slides (2025)"
author: "Various (Alibaba, Approaching.AI, SenseTime, BAAI, vivo)"
date: 2025-12-13
size: large
path: raw/PDFs/slides/
summary: "7 C++ conference slides covering LLM inference engines, disaggregated architectures, on-device deployment, and unified training/inference frameworks"
---

# AI/ML Inference — C++ Slides Collection

> Group source page for AI/ML inference-related slides from the 2025 C++ conference.

---

## 杨珂 — Mooncake: 解耦式架构和以存换算，优化大模型推理

**Speaker:** 杨珂 (Approaching.AI Tech Expert, Mooncake Core Contributor)
**File:** `杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理.pdf` (45 pages, 14.6K chars)

Mooncake is a **KVCache-centric disaggregated architecture** for LLM inference in the long-context era.

**Key takeaways:**
- Inference costs dominate (Amazon: >90% of costs; DeepSeek R1: $6M training vs $32M+ annual inference)
- **P/D Disaggregation** — Prefill (compute-bound) and Decode (memory-bound) separated onto different nodes; each node optimized for its specific workload
- **KVCache reuse** — shared across requests with the same prefix; enables "value engineering" (Function/Cost ratio)
- **Design approach:** "以存换算" — trading storage (KV Cache) for computation; reduces redundant prefill
- Mooncake integrates with vLLM ecosystem; supports RDMA-based KV Cache transfer between nodes
- Long-context era drivers: Kimi (long input), DeepSeek R1 (long output/chain-of-thought), Agent-based systems (multi-turn complex execution)

---

## 石新飞 — RTP-LLM：阿里大模型推理引擎

**Speaker:** 石新飞 (Alibaba Senior Technical Expert)
**File:** `石新飞_RTP-LLM：阿里大模型推理引擎.pdf` (24 pages, 2.2K chars)

RTP-LLM is Alibaba's production LLM inference engine.

**Key takeaways:**
- **Continuous Batching → PD Separation:** Continuous batching causes TPOT (Time Per Output Token) instability because decode is interrupted by prefill. PD separation provides stable TPOT.
- **PD Separation with RDMA:** KV Cache transfer between machines via RDMA; layered transfer hides transfer costs with computation
- **Distributed CacheStore:** Shared KV Cache across nodes
- **MoE (Mixture of Experts):** Deployed with Qwen Coder; Router selects experts, reducing per-token cost while scaling model size
- **MTP (Multi-Token Prediction) Speculative Decoding:** Predict multiple tokens at once to increase throughput
- **Asymmetric Tensor Parallelism:** Different TP configurations for prefill vs decode

---

## 黄石柱 — DeepSeek 推理性能优化

**Speaker:** 黄石柱
**File:** `黄石柱-Deepseek推理性能优化.pdf` (image-only, 0 text chars)

> Note: This PDF contains only slide images with no extractable text. Content could not be captured programmatically. Based on title, covers DeepSeek LLM inference performance optimization techniques.

---

## 王志宏 — 从原型到生产：LazyLLM的三阶段架构演化实践

**Speaker:** 王志宏 (SenseTime, R&D Director)
**File:** `王志宏_从原型到生产：LazyLLM的三阶段架构演化实践.pdf` (42 pages, 18.9K chars)

LazyLLM is an LLM application framework that evolved from prototype to production through three architectural phases.

**Key takeaways:**
- **Phase 1 — Function First:** Modular component library for building AI Agents (RAG, knowledge base, ChatBI, smart QA, document generation)
- **Phase 2 — Usability First:** Architecture abstraction improving developer experience; prompt management, tool invocation, model orchestration
- **Phase 3 — Performance Wins:** Python → C++ hybrid programming;
  - Python for model definition and orchestration
  - C++ for hot paths: pipeline execution, data marshaling, scheduler
  - Result: dramatic latency reduction for production workloads
- Key design principles: demand-driven, clear layering, open architecture, moderate design
- Addresses the "Demo to Production" gap: fast response, accurate recall, stable operation, large-scale concurrency

---

## 王骁 — 端侧大模型部署：存储系统面临的挑战和优化实践

**Speaker:** 王骁 (vivo, Storage System Expert)
**File:** `王骁_端侧大模型部署：存储系统面临的挑战和优化实践.pdf` (32 pages, 4.7K chars)

On-device LLM deployment for vivo's Blue LM (蓝心大模型) and AIOS framework.

**Key takeaways:**
- **Challenge:** Model loading time is a critical bottleneck — a 3B model (~2GB file) takes ~10s to load
- **Solution:** dmabuf-based zero-copy model loading; dma-buf A for input/output buffers; optimized file I/O pipeline
- **vivo AIOS architecture:** Blue LM personal AI framework with:
  - Agent framework (intent understanding, task planning, memory management)
  - Model engine (efficient inference, model management, edge-cloud synergy)
  - Storage system (UFS/ZUFS, Block IO)
  - Kernel layer (file system, resource scheduling, memory management)
- End-side LLM features: smart naming, writing assistant, voice dialog, offline processing
- Storage challenges: large model file sizes (1.5-4GB for 3B-7B models), slow file I/O, memory pressure

---

## 熬玉龙 — 统一算力，释放智能：FlagScale在FlagOS生态中的演进

**Speaker:** 敖玉龙 (Beijing Academy of Artificial Intelligence / BAAI)
**File:** `熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进.pdf` (36 pages, 12.0K chars)

FlagScale is BAAI's unified training and inference framework within the FlagOS ecosystem.

**Key takeaways:**
- **FlagOS:** Unified, open-source system software stack for diverse AI chips (10+ chip vendors, 20+ chip types)
  - Supported hardware: GPGPU, DSA/NPU, RISC-V AI, ARM
  - Deployment targets: datacenter (train + inference), edge (inference), robotics (cloud-edge)
- **Three fragmentation challenges:**
  1. LLM lifecycle fragmentation — DeepSpeed/Megatron focus on training, vLLM/SGLang focus on inference
  2. Framework fragmentation — different frameworks excel in different scenarios
  3. Hardware fragmentation — GPU, NPU, custom accelerators each need unique toolchains
- **FlagScale components:**
  - FlagGems: universal operator library for large models
  - FlagTree: unified compiler
  - FlagCX: unified communication library
  - FlagPerf: multi-chip evaluation toolkit
  - Triton-Copilot: auto-generate operators
- **Automated cross-chip migration:** Reduces engineering effort for model porting between hardware platforms

---

## 易慧民 — RecIS：C++驱动的高性能推荐训练框架优化实践

**Speaker:** 易慧民 (Alibaba, Platform Technology)
**File:** `易慧民_RecIS：C++驱动的高性能推荐训练框架优化实践.pdf` (25 pages, 3.2K chars)

RecIS is Alibaba's C++-driven recommendation system training optimization framework.

**Key takeaways:**
- Background: "The Free Lunch Is Over" — CPU frequency wall → multi-core → GPU parallel computing
- **Performance challenges in recommendation training:**
  - CPU vs GPU characteristics: CPU (50%+ control logic, low latency) vs GPU (nearly all compute units, high throughput)
  - GPU memory hierarchy: H100 SM (132 SMs) vs ALU (Cuda Core)
  - Memory bandwidth is the primary bottleneck for recommendation model training
- **C++ engineering optimizations:** Custom memory allocators, SIMD vectorization, cache-aware data layouts, NUMA-aware scheduling
- Compared to LLM training, recommendation training has different workload patterns: sparse features, embedding tables, dynamic shapes

---

## Related Pages

- [[entities/cpp/cpp-llm-inference]] — C++ for LLM inference frameworks (xLLM, PD/EPD separation)
- [[entities/cpp/cpp-perf-optimization]] — Performance optimization techniques
- [[sources/pdf-cpp-slides]] — Previously ingested C++ slides batch
- [[sources/pdf-cpp-compiler-toolchain]] — Compiler/toolchain slides
