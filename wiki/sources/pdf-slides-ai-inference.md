---
type: source
source-type: slides
title: "AI Inference & LLM Optimization (Slides)"
date: 2024
size: medium
path: raw/PDFs/slides/
summary: "9个LLM推理优化演讲：Mooncake(RTP-LLM/LazyLLM/xLLM/DeepSeek/FlagScale/RecIS/端侧存储/AI成熟度/AI Spec Coding)"
tags: [llm, inference, ai, mooncake, rtp-llm, xllm, deepseek, flagscale, recsys, edge-ai]
---

# AI Inference & LLM Optimization (Slides)

> 9个AI推理与LLM优化演讲，来自C++大会/技术峰会。

## 演讲列表

| # | Speaker | Title | Topic |
|---|---------|-------|-------|
| 1 | 石新飞 | RTP-LLM：阿里大模型推理引擎 | MoE专家模型/投机采样/分布式架构 |
| 2 | 刘童旋 | 基于C++构建大模型推理优化框架xLLM实践 | PD分离/电商场景/DAG调度/KVCache |
| 3 | 杨珂 | Mooncake：解耦式架构和以存换算 | KVCache Pool/以存换算/vLLM兼容 |
| 4 | 黄石柱 | Deepseek推理性能优化 | DeepSeek SGLang优化 |
| 5 | 王志宏 | LazyLLM三阶段架构演化实践 | 原型→生产架构演进 |
| 6 | 熬玉龙 | FlagScale在FlagOS生态中的演进 | 统一算力/跨AI芯片生态 |
| 7 | 易慧民 | RecIS：C++驱动的高性能推荐训练框架 | 推荐训练/C++/GPU HashTable |
| 8 | 王骁 | 端侧大模型部署：存储系统面临的挑战 | AIOS/分层KVCache/计算存储融合 |
| 9 | 李建忠 | AI原生软件研发成熟度模型与演进 | AI-Native研发成熟度评估 |

## 主题分类

| 分类 | 演讲 |
|------|------|
| 推理引擎架构 | 1, 2, 3, 4, 5 |
| 分布式/异构 | 3, 6 |
| 推荐系统 | 7 |
| 端侧部署 | 8 |
| AI工程方法 | 9 |

## 核心要点

### Mooncake 架构 (杨珂)
- KVCache-centric disaggregated architecture
- 以存换算：存储成本 << 计算成本
- KVCache Pool分层存储：GPU HBM + CPU内存 + NVMe
- 与vLLM/TensorRT-LLM兼容

### xLLM (刘童旋)
- C++实现的大模型推理框架
- Prefill/Decode分离调度
- 电商场景：DAG调度优化
- KVCache优化策略

### RTP-LLM (石新飞)
- 阿里自研推理引擎
- MoE专家模型支持
- 投机采样(speculative decoding)
- 分布式推理架构

### RecIS (易慧民)
- C++驱动的高性能推荐训练框架
- Four Walls约束：Python/CPU/Memory/Compute
- GPU HashTable设计
- Sparse Fusion优化

### 端侧部署 (王骁)
- AIOS架构
- 存储挑战：KVCache太大
- 分层KVCache策略
- 计算存储融合

## 相关页面
- [[sources/pdf-mooncake]] — Mooncake专题
- [[sources/pdf-rtp-llm]] — RTP-LLM专题
- [[sources/pdf-xllm-inference]] — xLLM专题
- [[cpp-index]] — Modern C++ 模块索引