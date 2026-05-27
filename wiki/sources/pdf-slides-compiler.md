---
type: source
source-type: slides
title: "C++ Compiler Infrastructure (Slides)"
date: 2024
size: medium
path: raw/PDFs/slides/
summary: "5个编译器相关演讲：MLIR fuzzing/AI软件栈/多元AI算子库/RISC-V AI编译器/RISC-V全栈生态"
tags: [compiler, mlir, risc-v, llvm, ai-compiler, cpp-slides]
---

# C++ Compiler Infrastructure (Slides)

> 5个编译器与AI编译栈演讲，来自C++大会/技术峰会。

## 演讲列表

| # | Speaker | Title | Topic |
|---|---------|-------|-------|
| 1 | 赵英全 | MLIR编译器基础设施模糊测试 | 覆盖率引导fuzzing/pass间bug |
| 2 | 崔慧敏 | 编译技术在AI软件栈中的实践分享 | SigInfer/国产卡CUDA兼容 |
| 3 | 郑杨 | 面向多元AI芯片的算子库和编译器 | 算子库/跨芯片生态 |
| 4 | 张洪滨 | 面向RISC-V大模型推理AI编译器 | 软硬件协同/V扩展/代价模型 |
| 5 | 谢涛 | RISC-V+AI全栈软件生态突破路径 | 开放指令集/开源算子/编译器 |

## 主题分类

| 分类 | 演讲 |
|------|------|
| MLIR/LLVM | 1, 2 |
| RISC-V | 4, 5 |
| 异构AI芯片 | 2, 3 |

## 核心要点

### MLIR Fuzzing (赵英全)
- 覆盖率引导fuzzing：libFuzzer + 输入语料库
- 自动生成valid MLIR dialect操作
- 发现pass内/pass间/dialect边界的bug
- 交叉验证不同lowering路径语义等价性

### AI Compiler Stack (崔慧敏)
- SigInfer推理引擎
- 国产AI芯片的CUDA兼容层
- AI编译器自动生成算子

### 多元AI芯片 (郑杨)
- 跨多元AI芯片的算子库统一抽象
- 编译器层面的跨芯片支持
- 生态建设策略

### RISC-V AI Compiler (张洪滨)
- RISC-V V扩展(Vector Extension)
- 软硬件协同设计
- 代价模型与自动调优
- 大模型推理在RISC-V上的AI编译器支持

### RISC-V全栈生态 (谢涛)
- 开放指令集RISC-V
- 开源算子和编译器
- RISC-V + AI完整软件栈
- 突破路径与生态建设

## 相关页面
- [[sources/pdf-mlir-fuzzing]] — MLIR fuzzing专题
- [[sources/pdf-ai-compiler-stack]] — AI编译器软件栈
- [[sources/pdf-riscv-ai-compiler]] — RISC-V AI编译器专题
- [[cpp-index]] — Modern C++ 模块索引