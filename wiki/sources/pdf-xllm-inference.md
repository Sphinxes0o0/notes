---
type: source
source-type: pdf
title: 基于C++构建大模型推理优化框架xLLM实践
author: 刘童旋
date: 2024
size: small
path: raw/PDFs/slides/刘童旋_基于C++构建大模型推理优化框架xLLM实践.pdf
summary: 刘童旋：xLLM大模型推理引擎C++实现，电商场景多模型推理优化，DAG调度
tags: [llm, inference, cpp, xllm, optimization, ai, cpp-slides]
created: 2024
---
# 基于C++构建大模型推理优化框架xLLM实践

## 核心内容

**Author:** 刘童旋 | 2024

### 电商场景 AI 需求

- **生成式AI**：商品图/短视频/AI营销内容/AI数字人
- **Agentic AI**：AI客服、售后管理、经营托管、仓配优化
- **具身智能**：自动分拣机器人、智能空间、自动驾驶

### AI 推理的挑战

1. **多模型异构**：大模型+多模态+文生图+视频+生成式推荐
2. **推理框架碎片化**：各框架无法协同
3. **硬件异构**：输入多样性，优先级调度
4. **效率平衡**：模型规模、效果、效率的权衡

### xLLM 架构

- **全栈C++实现**：高性能推理引擎
- **DAG任务调度**：多模型依赖图调度
- **异构资源管理**：GPU/CPU/NPU统一抽象
- **KVCache优化**：PagedAttention式显存管理
- **投机采样**：Speculative Decoding加速

### 为什么选择 C++

- 内存控制精确（LLM显存管理critical）
- 无GC停顿（实时推理不可接受延迟波动）
- 硬件直接控制（SIMD/GPU编程）
- 跨平台部署（云/端/嵌入式）

## 相关页面
- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理优化
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[cpp-index]] — Modern C++ 模块索引
- [[entities/ai-mlir-compilation]] — AI编译器基础设施