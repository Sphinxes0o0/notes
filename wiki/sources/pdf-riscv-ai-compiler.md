---
type: source
source-type: pdf
title: 面向RISC-V大模型推理AI编译器设计与实现
author: 张洪滨 (中国科学院软件研究所)
date: 2024
size: medium
path: raw/PDFs/slides/张洪滨_面向RISC-V大模型推理AI编译器设计与实现.pdf
summary: 张洪滨：RISC-V AI编译器设计，软硬件协同优化，DNN算子库，代价模型，自动调优
tags: [risc-v, ai, compiler, riscv64, optimization, ai-slides]
created: 2024
---
# 面向RISC-V大模型推理AI编译器设计与实现

## 核心内容

**Author:** 张洪滨（中国科学院软件研究所智能软件研究中心）| 2024

### AI软硬件协同设计关键技术

```
DNN 与 BLAS 高性能算子库    深度学习编译器与基础设施
        OpenBLAS / 手动调优                MLIR / TVM
              ↓                                  ↓
        性能仿真 · 代价模型设计 · 约束设计 · 搜索策略制定
                                   ↓
                   EDA 工具链 → Verilog → 硬件加速器
                   (CPU/GPU/FPGA/CGRA/ASIC)
```

### 编译优化技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 算子优化 | 循环 tiling/vectorization/unrolling | 通用优化 |
| 内存优化 | 数据布局转换、融合 | 减少搬移 |
| RISC-V特性 | V扩展(Vector)、Zicsr | SIMD并行 |
| 自动调优 | AutoTVM/AutoSch | 搜索最优参数 |

### RISC-V向量扩展 (V Extension)

- **VLEN**：向量寄存器位宽（可配置）
- **LMUL**：向量长度因子，多元素打包
- **SEW**：选定元素宽度
- **Vsetvli**：动态向量长度指令，RISC-V独有特性

### 代价模型

- Roofline Model：计算密度 vs 内存带宽
- Latency Model：算子执行时间预测
- 搜索空间：tiling factor、向量长度、分块大小

## 相关页面
- [[entities/ai-mlir-compilation]] — MLIR编译基础设施
- [[entities/cpp/compiler-ai-software-stack]] — AI编译器软件栈
- [[cpp-index]] — Modern C++ 模块索引
- [[entities/arm/armv8-architecture]] — ARM/RISC-V架构对比