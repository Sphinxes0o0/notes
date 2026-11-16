---
type: entity
tags: [cpp, compiler, ai, inference, siginfer, roofline-model]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# Compiler Techniques in AI Software Stack — SigInfer & AI Compiler

## 定义
崔慧敏的演讲分享编译技术在AI软件栈中的实践：私有化部署需求、推理引擎SigInfer、Roofline Model性能优化、国产卡CUDA兼容、AI for Compiler。

## 关键要点

### 私有化部署驱动因素
- **推理算力爆发**：中国推理市场未来3年超6倍增幅
- **信创100%替代**：国资委79号文要求2027年前央企国企核心系统全信创替代
- **一体机需求**：2025-2027年从15万台增至72万台，市场空间1236→5208亿元

### AI基础设施挑战
- **硬件多样性**：GPU/CPU/NPU架构差异大，编程复杂性NPU > GPU > CPU
- **软硬件协同低**：国产芯片适配性和软件生态完备度不足
- **优化门槛高**：需针对不同硬件特性进行针对性优化

### SigInfer推理引擎
- **以编译为核心的高性能AI推理引擎**
- 支持国产卡兼容CUDA生态
- 多模部署场景（手机/一体机/企业智算/大规模智算）

### Roofline Model性能分析
- **Memory bound区间**：算力有空余，增大batch有利于吞吐量
- **Compute bound区间**：增大batch不再增加吞吐量
- **Prefill特征**：计算密集
- **Decode特征**：访存密集（计算不饱和）
- 混合阶段（Prefill+Decode同卡）出现"双瓶颈交替"

### AI for Compiler
- 基于AI的编译器自动生成
- 自动化算子优化和代码生成

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — 容器与张量
- [[entities/cpp/cpp-perf-optimization]] — 性能优化工具

## 来源详情
- [[sources/pdf-cpp-slides]] — 崔慧敏, 编译技术在AI软件栈中的实践分享
