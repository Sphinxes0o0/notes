---
type: source
source-type: pdf
title: "RTP-LLM：阿里大模型推理引擎"
author: "石新飞"
date: 2024
size: small
path: raw/PDFs/slides/石新飞_RTP-LLM：阿里大模型推理引擎.pdf
summary: "石新飞：RTP-LLM阿里巴巴大模型推理引擎，MOE专家模型、投机采样、分布式架构"
tags: [llm, inference, moe, speculative-decoding, distributed, ai-slides]
---

# RTP-LLM：阿里大模型推理引擎

## 核心内容

**Author:** 石新飞 | 2024

### 目录结构

01. 大模型推理介绍
02. 推理优化
03. MOE专家模型
04. MTP投机采样
05. 分布式架构
06. 未来展望

### 大模型推理挑战

- **KVCache显存瓶颈**：长上下文显存爆炸
- **Decoding延迟**：自回归生成逐token输出的串行性
- **MOE负载均衡**：专家模型间请求分布不均
- **Prefill-Decode分离**：不同阶段计算特征差异

### RTP-LLM 核心优化

**1. MOE（Mixture of Experts）：**
- Top-K专家激活，每个token路由到K个专家
- All-to-All通信模式
- 动态专家负载均衡

**2. MTP（Mountain Turbulence Parallelism / 投机采样）：**
- 小模型生成候选token序列
- 大模型并行验证
- 加速比 ~2-3x

**3. 分布式架构：**
- Tensor Parallelism：张量切分到多卡
- Pipeline Parallelism：按层切分
- 分片策略：静态 + 动态混合

## 相关页面
- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理优化
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[entities/ai-mlir-compilation]] — AI编译器基础设施
- [[cpp-index]] — Modern C++ 模块索引