---
type: source
source-type: pdf
title: Mooncake：解耦式架构和以存换算，优化大模型推理
author: 杨珂 (趋境科技)
date: 2024
size: medium
path: raw/PDFs/slides/杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理.pdf
summary: 杨珂：Mooncake解耦式大模型推理架构，KVCache为中心的 disaggregated/prefetch 架构
tags: [llm, inference, mooncake, kv-cache, disaggregated, ai-slides]
created: 2024
---
# Mooncake：解耦式架构和以存换算，优化大模型推理

## 核心内容

**Author:** 杨珂（趋境科技技术专家/Mooncake核心贡献者）| 2024

### 背景：LLM Inference in Long-context Era

**现状范式**：Data + Algorithm + Hardware = Intelligence
- Algorithm：Transformer为核心
- Data：大数据无处不在
- Hardware：Huang's Law算力持续增长

### 长上下文推理的KVCache问题

- **显存瓶颈**：KVCache随上下文长度二次增长
- **PagedAttention**：Meta提出，但仍是单卡内部分页
- **跨请求共享**：多请求间KVCache无法共享
- **Preemptible KVCache**：冷热分层

### Mooncake 核心架构

**KVCache-centric Disaggregated Architecture：**

```
Prefill节点集群 ──→ KVCache Pool (分布式) ──→ Decode节点集群
                        ↑
                    GPU显存 + CPU内存 + NVMe分层存储
```

### 核心设计思想：以存换算

- **存储成本 << 计算成本**：HBM带宽是网络带宽的10-100x
- **跨节点KVCache**：Prefill和Decode节点物理分离
- **异步预取**：在Decode进行时预取下一个token的KVCache
- **弹性扩展**：KVCache节点可独立扩缩容

### Mooncake × LLM Ecosystem

- 与vLLM/TensorRT-LLM兼容
- 开源：github.com/LeptonAI/Mooncake
- 已在趋境科技生产环境部署

## 相关页面
- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理优化
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[cpp-index]] — Modern C++ 模块索引
- [[entities/ai-mlir-compilation]] — AI编译器基础设施