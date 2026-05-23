---
type: source
created: 2026-05-23
source-type: pdf
sources: [pdf-cpp-compiler-toolchain]
tags: [cpp, compiler, toolchain]
title: "Compiler & Toolchain Slides (2025)"
author: "Various (CAS, PKU, BAAI, Tsinghua, Qiyuan Lab)"
date: 2025-12-13
size: large
path: raw/PDFs/slides/
summary: "6 slides covering MLIR fuzzing, RISC-V AI compilers, multi-chip operator libraries, compilation in AI software stack, and unified heterogeneous computing architecture"
---

# Compiler & Toolchain — C++ Slides Collection

> Group source page for compiler infrastructure, AI compiler, and toolchain slides.

---

## 崔慧敏 — 编译技术在AI软件栈中的实践分享

**Speaker:** 崔慧敏
**File:** `崔慧敏_编译技术在AI软件栈中的实践分享.pdf` (50 pages, 13.4K chars)

Comprehensive talk on compilation techniques in the AI software stack, covering inference engines, CUDA compatibility, and AI for compilers.

**Key takeaways:**
- **AI infrastructure trends:** China's AI chip market share grew 112% to $16B (42% share); private deployment demand booming (15M→720M units, $124B→$521B market)
- **Hardware diversity challenge:** NPU > GPU > CPU programming difficulty; architecture iterations fast; toolchain immaturity
- **SigInfer:** Compilation-centric high-performance AI inference engine:
  - Custom operator fusion, memory optimization, tensor partitioning
  - Multi-level IR optimization pipeline
- **CUDA compatibility for domestic chips:** Translation layer between CUDA kernel code and domestic NPU instruction sets; binary translation + source-to-source compilation
- **AI for Compiler:** Using AI/ML to automate compiler pass generation, heuristic search for optimization sequences
- **Future directions:** AI-native compilers, automatic differentiation compilation, domain-specific IR design

---

## 赵英全 — MLIR编译器基础设施模糊测试

**Speaker:** 赵英全
**File:** `赵英全_MLIR编译器基础设施模糊测试.pdf` (34 pages, 11.5K chars)

MLIR (Multi-Level IR) compiler infrastructure fuzzing — generating valid MLIR programs to find compiler bugs.

**Key takeaways:**
- **MLIR background:** Multi-Level IR designed for domain-specific compilation; dialects define operations, attributes, and types; passes transform between dialects
  - Common dialects: `tosa`, `scf`, `memref`, `linalg`, `llvm`
  - Example pipeline: `tosa-to-linalg-named` → `linalg-generalize-named-ops` → `one-shot-bufferize` → `convert-linalg-to-loops` → `canonicalize`
- **Compiler testing challenge:** Traditional test program generation (e.g., Csmith) generates C/C++ programs, then translates through LLVM-IR to MLIR — poor test diversity and effectiveness
- **MLIRSmith (ASE'23):** Direct MLIR test program generation:
  - Uses program templates with parameterized operations, attributes, and types
  - Ensures both syntactic and semantic validity
  - Generates diverse dialect combinations for better test coverage
- **Key techniques:** Dialect operation diversity, type/attribute constraint solving, template instantiation with valid operand chains

---

## 张洪滨 — 面向RISC-V大模型推理AI编译器设计与实现

**Speaker:** 张洪滨 (Chinese Academy of Sciences, Institute of Software)
**File:** `张洪滨_面向RISC-V大模型推理AI编译器设计与实现.pdf` (72 pages, 24.8K chars)

AI compiler design and implementation for LLM inference on RISC-V architecture.

**Key takeaways:**
- **AI compiler techniques for RISC-V:**
  - Graph-level operator fusion, compute load partitioning, vectorization optimization, dead code elimination, constant folding
  - Multi-level compilation: front-end (model graph) → middle-end (MLIR dialects) → back-end (RISC-V ISA)
- **RISC-V-specific optimizations:**
  - RISC-V Vector Extension (RVV) for SIMD-like parallel computation
  - Custom instruction extensions for AI workloads (matrix multiply, attention)
  - Memory hierarchy-aware tiling and prefetching
- **Hardware-software co-design:** AI system design involves compilation optimization, accelerator design, interface design, and resource co-tuning
- Challenges: RISC-V AI ecosystem immaturity, limited optimized kernels, toolchain fragmentation

---

## 谢涛 — 从开放指令集到开源算子和编译器：RISC-V+AI的全栈软件生态突破路径

**Speaker:** 谢涛 (Peking University Professor, Dean of Fudan Advanced Computing Systems)
**File:** `谢涛_从开放指令集到开源算子和编译器：RISC-V+AI的全栈软件生态突破路径.pdf` (21 pages, 5.9K chars)

Strategic perspective on RISC-V + AI full-stack software ecosystem breakthroughs.

**Key takeaways:**
- **RISC-V strategic importance:** Open ISA immune to geopolitical risks; China holds half of global RISC-V ecosystem; RISC-V AI chip market projected at $291B by 2027
- **Current fragmentation:** 40+ domestic AI chip vendors, each with separate software stacks; <10% combined market share
- **RISC-V core advantages:** Open standard (RVI maintained), modularity + extensibility (base ISA + optional extensions)
- **Era shift:** PC era (Wintel/x86) → Mobile era (AA/ARM) → AI era (Open Software + RISC-V alliance)
- Breakthrough path: unified operator library + unified compiler infrastructure + open ISA

---

## 郑杨 — 面向多元AI芯片的算子库和编译器建设实践与思考

**Speaker:** 郑杨 (BAAI / 智源研究院)
**File:** `郑杨_面向多元AI芯片的算子库和编译器.pdf` (25 pages, 10.5K chars)

FlagOS ecosystem: operator libraries (FlagGems) and compilers (FlagTree) for diverse AI chips.

**Key takeaways:**
- **FlagOS v1.5:** Supports GPGPU, DSA/NPU, RISC-V AI, ARM; 10+ chip vendors, 20+ chip models
- **FlagGems:** Universal operator library for large model inference and training — abstracted from specific hardware backends
- **FlagTree:** Unified compiler with multi-level IR:
  - Frontend: model-specific optimizations
  - Middle: hardware-agnostic transformations (fusion, memory planning)
  - Backend: target-specific code generation
- **Coverage:** Language models (DeepSeek, Qwen, Llama), multimodal (EMU, Qwen-VL), embodied AI (RoboBrain)
- Auto-migration and release tools (FlagRelease) reduce cross-chip porting effort

---

## 王豪杰 — 面向异构计算的统一智能计算架构及开源生态

**Speaker:** 王豪杰 (Qiyuan Lab / Tsinghua University)
**File:** `王豪杰_面向异构计算的统一智能计算架构及开源生态.pdf` (51 pages, 11.8K chars)

"九源" unified intelligent computing architecture for heterogeneous computing — addressing China's domestic AI chip ecosystem fragmentation.

**Key takeaways:**
- **Domestic chip dilemma:** Hardware approaching international levels, but software ecosystem immature → large-scale idle capacity
- **九源 architecture:** Unified training/inference framework that:
  - Shields underlying chip differences
  - Supports different chip types (GPU, NPU, GPGPU)
  - Provides consistent developer experience
- **Ecosystem building:** Courses, competitions, incentive mechanisms, community building, employment guidance
- Key feature: automatic workload distribution across heterogeneous devices

---

## Related Pages

- [[sources/pdf-cpp-ai-inference]] — AI/ML inference slides
- [[entities/cpp/cpp-perf-optimization]] — Performance optimization at the CPU/cache level
- [[entities/cpp/cpp-llm-inference]] — C++ for LLM inference frameworks
