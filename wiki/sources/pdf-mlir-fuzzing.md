---
type: source
source-type: pdf
title: "MLIR编译器基础设施模糊测试"
author: "赵英全"
date: 2024
size: small
path: raw/PDFs/slides/赵英全_MLIR编译器基础设施模糊测试.pdf
summary: "赵英全：MLIR编译器模糊测试实践，基于覆盖率引导的fuzzing发现编译器bug"
tags: [mlir, compiler, fuzzing, llvm, testing, ai, cpp-slides]
---

# MLIR编译器基础设施模糊测试

## 核心内容

**Author:** 赵英全 | 2024 C++大会

### MLIR 架构

```
Multi-Level IR (Compiler Infrastructure)
LLVM IR ByteCode  SIL IR  XLA HLO
Dialect(方言)：定义操作、属性和类型
如：tosa dialect（用于DNN计算图）
scf  memref ...  tosa
Pass(转换)：遍历程序并执行转换和优化
```

### 关键概念

- **Dialect（方言）**：独立的IR表示，如 tosa（LoweR TeNSor）、scf（structured control flow）、memref
- **Lowering Pass**：tosa → linalg → arith → llvm 的多级 lowering 流水线
- **One-Shot Bufferize**：自动张量→内存转换

### 模糊测试方法

1. **覆盖率引导Fuzzing**：libFuzzer + 输入语料库
2. **MLIR Dialect 操作随机生成**：基于 op definitions 自动生成 valid IR
3. **Pass 流水线组合测试**：随机 pass 组合，发现 pass 间不兼容
4. **交叉验证**：比较不同 lowering 路径的语义等价性

### 发现的问题类型

- Pass内：无效的canonicalization导致UB
- Pass间：one-shot-bufferize与convert-linalg-to-loops的顺序依赖
- Dialect边界：跨 dialect type 转换不完整

## 相关页面
- [[entities/ai-mlir-compilation]] — MLIR编译基础设施
- [[entities/cpp/mlir-fuzzing]] — MLIR模糊测试
- [[entities/cpp/compiler-ai-software-stack]] — AI编译器软件栈
- [[cpp-index]] — Modern C++ 模块索引