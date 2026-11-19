---
type: entity
tags: [llm, inference, kv-cache, disaggregated, moonscake, kv-cache-disaggregation]
created: 2026-05-27
sources: [pdf-mooncake]
---

# Mooncake: KVCache-Centric Disaggregated LLM Inference

## Definition

Mooncake is a disaggregated LLM inference architecture centered on KVCache management, proposed by Ke Yang (Approaching.AI). It separates Prefill and Decode into distinct node clusters, enabling a distributed KVCache pool to maximize GPU utilization during long-context inference.

## Key Concepts

### KVCache Memory Problem

During LLM inference, the Key-Value cache grows quadratically with context length. Traditional systems store KVCache in GPU HBM, creating a **memory wall** where compute utilization drops as memory bandwidth saturates.

### Disaggregated Architecture

```
Prefill Node(s)  ──→  KVCache Pool (multi-tier storage)  ──→  Decode Node(s)
                         HBM | LPDDR | NVMe分层
                         跨节点高速网络
```

**核心设计：以存换算**
- Storage bandwidth >> network bandwidth between nodes
- KVCache在节点间传输，计算节点专注于compute
- 异步预取：在Decode进行时预取下一token的KVCache

### KVCache Pool Tiers

| 层级 | 存储介质 | 带宽 | 延迟 |
|------|----------|------|------|
| GPU HBM | VRAM | ~2TB/s | ~1μs |
| LPDDR | Host RAM | ~100GB/s | ~10μs |
| NVMe | SSD | ~5GB/s | ~100μs |

### Mooncake × LLM Ecosystem

- 与vLLM/TensorRT-LLM API兼容
- 开源地址：github.com/LeptonAI/Mooncake
- 已在趋境科技生产环境部署

## Related Pages

- [[entities/cpp/cpp-llm-inference]] — LLM推理引擎的通用架构模式
- [[entities/cpp/cpp-high-performance]] — C++高性能计算（存储优化相关）
- [[entities/ai-mlir-compilation]] — AI编译基础设施（MLIR/Triton）
- [[entities/linux/kernel/index#memory-management]] — Linux内存管理（存储分层相关）

## Source Details

- [[sources/pdf-mooncake]] — Mooncake: 解耦式架构和以存换算，优化大模型推理