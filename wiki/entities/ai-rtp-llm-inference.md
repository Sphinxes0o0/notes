---
type: entity
tags: [llm, inference, moe, speculative-decoding, distributed, rtp-llm, alibaba]
created: 2026-05-27
sources: [pdf-rtp-llm]
---

# RTP-LLM: Alibaba Large-Scale LLM Inference Engine

## Definition

RTP-LLM (Real-Time Practice LLM) is Alibaba's production LLM inference engine, designed for high-throughput serving of large language models (including MoE variants) across distributed GPU clusters. It implements speculative decoding, MoE load balancing, and elastic pipeline parallelism.

## Key Concepts

### MoE (Mixture of Experts)

- **Top-K routing**: each token is routed to K out of N expert models
- **All-to-All communication**: tokens sent to selected experts across the cluster
- **Dynamic load balancing**: prevents expert "starvation" under skewed request distributions
- Trade-off: communication overhead vs. specialization

### MTP (Multi-Token Prediction / Speculative Decoding)

- **Draft model**: smaller, faster model generates a candidate token sequence
- **Verification**: main model validates multiple tokens in parallel
- **Speedup**: 2-3x throughput improvement on typical workloads
- MTP also stands for "Mountain Turbulence Parallelism" in Alibaba internal docs

### Distributed Architecture

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **Tensor Parallelism** | 张量切分到多卡，同步计算 | 超大单层 |
| **Pipeline Parallelism** | 按层切分，异步执行 | 多节点 |
| **Static Sharding** | 固定分片策略 | 负载稳定 |
| **Dynamic Sharding** | 请求级动态调度 | 异构集群 |

### Prefill-Decode Separation

- Prefill阶段：compute-bound，适合批处理
- Decode阶段：memory-bandwidth-bound，适合流式
- 分离部署避免相互干扰，提高整体吞吐

## Related Pages

- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理框架通用架构
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[entities/ai-mlir-compilation]] — AI编译基础设施
- [[entities/ai-moonscake-kvcache-disaggregation]] — Mooncake的KVCache解耦方案对比

## Source Details

- [[sources/pdf-rtp-llm]] — RTP-LLM：阿里大模型推理引擎