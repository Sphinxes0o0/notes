---
type: entity
tags: [cpp, ai, standardization, tensors, mdspan]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# Michael Wong — C++ AI Stack: Full-Stack Standardization for the Agent Era

## 定义
Michael Wong 2025年演讲，阐述面向AI智能体时代的全栈C++标准化路线图：C++ AI Stack三层架构（数据科学层→核心数据结构层→执行层）。

## 关键要点

### Three-Layer C++ AI Stack

**Layer 1 — Foundation（数据科学）**
- `std::data_frame`：异构列导向容器，目标是直接移植Pandas脚本到C++
- 状态：Experimental/Future
- 底层：ranges、statistics算法

**Layer 2 — Core Data Structures（核心数据结构）**
- `mdspan`：多维视图（非拥有型），C++23引入
- **Tensors（张量）**：多维数组，AI计算核心数据结构
- **Graphs（图）**：神经网络/知识图谱表示

**Layer 3 — Execution（执行层）**
- 性能与并行性
- SIMD向量化、多线程、GPU/NPU加速

### 为什么现在？AI软件栈的分裂
- 2025年AI软件栈碎片化：不同硬件（CUDA/ROCm/国产NPU）、不同框架、不同优化路径
- C++需要成为AI的"通用语"，实现跨平台AI应用的标准化

### 演讲者背景
- **Michael Wong**，Yetiware AI CTO
- C++标准委员会机器学习组主席
- 加拿大ISO编程语言、功能安全、AI/ML委员会主席
- Boost Foundation Director

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — mdspan、容器
- [[entities/cpp/lambda-expressions]] — AI中的Lambda
- [[entities/cpp/cpp20-features]] — C++23 mdspan

## 来源详情
- [[sources/pdf-cpp-slides]] — Michael Wong, AI使命：C++全栈标准化
