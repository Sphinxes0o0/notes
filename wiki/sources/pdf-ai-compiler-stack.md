---
type: source
source-type: pdf
title: "编译技术在AI软件栈中的实践分享"
author: "崔慧敏"
date: 2024
size: medium
path: raw/PDFs/slides/崔慧敏_编译技术在AI软件栈中的实践分享.pdf
summary: "崔慧敏：AI基础设施挑战、SigInfer编译推理引擎、国产卡CUDA兼容、AI编译器自动生成"
tags: [ai, compiler, inference, mlir, tvm, xla, cuda, cpp-slides]
---

# 编译技术在AI软件栈中的实践分享

## 核心内容

**Author:** 崔慧敏 | 2024

### 目录

01. 私有化部署的需求
02. AI基础设施的挑战和现状
03. SigInfer：以编译为核心的高性能AI推理引擎
04. 国产卡兼容CUDA生态的探索与实践
05. AI for Compiler：基于AI的编译器自动生成
06. AI软件栈未来若干发展方向

### AI基础设施投资趋势

- IDC预测2025年全球2000强企业将超过40% IT预算投入AI
- 2025年全球生成式AI支出预计达691亿美元，2028年超过2022亿美元
- 全球AI芯片算力爆发：2025年预计超过3ZFlops，2030年超过20Zflops

### AI编译器技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 模型格式 | ONNX/TFLite/MicroTVM | 前端模型表示 |
| 中间表示 | MLIR/TFLite Dialect | 多级IR |
| 算子优化 | Tosa/Linalg/SCF Dialects | 张量→循环 |
| 代码生成 | LLVM/NVVM/ROCM | 目标代码 |

### SigInfer架构

- 基于MLIR的端到端AI推理编译器
- 支持多后端（CPU/GPU/NPU）
- 自动算子融合、内存规划、量化

### 国产卡 CUDA 兼容

- 工具链兼容层：PTX/SASS 二进制翻译
- 算子库兼容层：cuBLAS → 自研
- 编译期兼容：nvcc flag 兼容

## 相关页面
- [[entities/ai-mlir-compilation]] — MLIR编译基础设施
- [[entities/cpp/compiler-ai-software-stack]] — AI编译器软件栈
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[cpp-index]] — Modern C++ 模块索引