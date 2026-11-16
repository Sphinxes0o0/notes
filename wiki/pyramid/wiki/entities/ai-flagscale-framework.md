---
type: entity
tags: [llm, training, inference, flagscale, flagcx, unified-stack, cpp-slides]
created: 2026-05-27
sources: [pdf-flagscale]
---

# FlagScale: Unified LLM Training and Inference Framework

## Definition

FlagScale is the core training/inference framework in the FlagOS ecosystem — a unified, open-source software stack that supports multiple AI accelerator chips from different vendors. It includes FlagCX (a unified communication library) for cross-chip coordination.

## Key Concepts

### FlagOS Unified Stack

```
Multiple AI Chips  ←→  FlagOS (unified software)  ←→  Multiple LLMs
                      ↑ PyTorch/PaddlePaddle接口
                      ↑ FlagCX通信层
```

### FlagCX Unified Communication

- **Abstraction**: AllReduce/Broadcast/ReduceScatter/AllGather primitives
- **Backend plugins**: NVIDIA (NCCL), AMD (RCCL), domestic NPU chips
- **Topology awareness**: NUMA-aware, PCIe-aware, NVLink-aware routing
- **NCCL-compatible API**: minimal porting effort for existing CUDA code

### FlagScale Components

| 组件 | 功能 |
|------|------|
| **FlagScale Train/Infer** | 统一训练推理框架 |
| **FlagCX** | 跨芯片通信抽象 |
| **自动化迁移** | 跨芯片模型转换工具链 |
| **跨芯片协同** | 异构芯片联合推理调度 |

### Supported Models

**Language**: DeepSeek, Qwen, Seed-oss, GPT-oss, Step, Grok, Llama
**Multimodal**: 智源EMU, 面壁CPM, Qwen-VL, ERNIE4.5, Llava
**Embodied**: 智源RoboBrain, Pai-0

## Related Pages

- [[entities/cpp/cpp-llm-inference]] — C++推理框架通用模式
- [[entities/ai-mlir-compilation]] — AI编译基础设施
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[entities/ai-rtp-llm-inference]] — 同为国产LLM推理引擎对比

## Source Details

- [[sources/pdf-flagscale]] — 统一算力，释放智能：FlagScale在FlagOS生态中的演进