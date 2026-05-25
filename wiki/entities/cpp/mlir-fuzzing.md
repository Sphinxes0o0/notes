---
type: entity
tags: [cpp, compiler, mlir, fuzzing, testing]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# MLIR Fuzzing — MLIR Compiler Infrastructure Fuzz Testing

## 定义
赵英全的演讲介绍MLIR编译器基础设施模糊测试：MLIRSmith系统通过程序模板实例化生成多样化、语法语义正确的MLIR测试程序。

## 关键要点

### MLIR多级中间表示
- **Dialect（方言）**：定义操作、属性和类型，如`tosa dialect`用于计算图表示
- **Pass（转换）**：遍历程序并执行转换和优化
- 不同编译系统涉及许多共同代码优化（如循环展开）

### 传统编译器测试问题
- 测试程序生成：间接测试，多样性有限（仅51%）
- MLIR测试效果差

### MLIRSmith方案（ASE 23）
**目标**：多样性（Dialect中的操作）+ 有效性（语法和语义正确性）

**程序模板实例化：**
- 属性占位符 `C`：如`memref.alloc`的`alignment`属性
- 操作数占位符 `V`：如`memref.store`的操作数

**语法规则**：
- 程序模板示例：`func.func @parallel_store(%cst: f32, %lb: index, %rb: index, %step: index)`
- 包含`scf.parallel`、`memref.alloc`、`memref.store`的正确MLIR程序结构

**实例化过程**：通过规则将占位符替换为具体值，生成有效的MLIR程序

## 相关概念
- [[entities/cpp/cpp-reflection]] — 编译期代码生成
- [[entities/cpp/cpp-templates]] — 模板元编程

## 来源详情
- [[sources/pdf-cpp-slides]] — 赵英全, MLIR编译器基础设施模糊测试
