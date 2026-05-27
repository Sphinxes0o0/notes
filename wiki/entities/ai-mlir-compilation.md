---
type: entity
tags: [compiler, mlir, ai, compilation, deep-learning]
created: 2026-05-23
sources: [pdf-cpp-compiler-toolchain]
---

# AI Compilation & MLIR Infrastructure

## Definition

AI compilation is the use of multi-level intermediate representations (IR) and compiler techniques to optimize deep learning model execution across diverse hardware backends. MLIR (Multi-Level IR) is the dominant infrastructure, enabling domain-specific dialects, progressive lowering, and hardware-agnostic optimization passes.

## Key Concepts

### MLIR Architecture
- **Dialects** — Domain-specific IR definitions (operations, attributes, types). Common dialects include `tosa` (Tensor Operator Set Architecture), `scf` (structured control flow), `memref` (memory references), `linalg` (linear algebra), and `llvm` (LLVM IR target)
- **Passes** — Transformations that convert between dialects or optimize within a dialect. Example pipeline: `tosa-to-linalg-named` → `linalg-generalize-named-ops` → `one-shot-bufferize` → `convert-linalg-to-loops` → `canonicalize`
- **Progressive lowering** — ML programs start at a high-level dialect and are progressively lowered to target-specific code

### AI Compiler Optimizations
- **Graph-level operator fusion** — Combine multiple small ops into a single kernel to reduce memory bandwidth
- **Compute load partitioning** — Split large tensors across compute units for parallelism
- **Vectorization** — Exploit SIMD instructions for data-parallel operations
- **Memory planning** — Optimize buffer allocation, reuse, and tiling
- **Constant folding** — Pre-compute constant expressions at compile time

### MLIR Fuzzing (MLIRSmith)
Traditional compiler testing generates C/C++ programs then translates to MLIR → poor test diversity. MLIRSmith (ASE'23) generates valid MLIR programs directly using program templates with parameterized operations, ensuring both syntactic and semantic validity.

## Compilation-Centric Inference Engines

**SigInfer** is a compilation-centric high-performance AI inference engine that uses multi-level IR optimization pipelines to achieve peak hardware utilization:
- Custom operator fusion passes
- Hardware-agnostic memory optimization
- Tensor partitioning for heterogeneous devices
- CUDA compatibility translation layer for domestic NPU chips

## Related Concepts
- [[entities/risc-v-ai-ecosystem]] — RISC-V AI compilers and operator libraries
- [[entities/cpp/cpp-perf-optimization]] — Low-level CPU/memory optimization complements compiler-level optimization
- [[entities/cpp/cpp-llm-inference]] — LLM inference frameworks that benefit from compiler optimizations
- [[entities/ai-mlir-fuzzing]] — MLIR编译器模糊测试，发现pass间不兼容bug
- [[entities/ai-rtp-llm-inference]] — RTP-LLM推理引擎（AI编译在国产AI芯片的应用）
- [[entities/ai-flagscale-framework]] — FlagScale跨AI芯片训练推理框架
- [[entities/ai-moonscake-kvcache-disaggregation]] — Mooncake解耦式推理架构

## Sources
- [[sources/pdf-cpp-compiler-toolchain]] — MLIR fuzzing, AI compilation, RISC-V AI compiler slides
