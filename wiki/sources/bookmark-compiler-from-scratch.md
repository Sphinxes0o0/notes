---
type: source
source-type: bookmark
title: "Build a Compiler from Scratch"
author: "Geoffrey Copin (Sylver)"
date: 2025-06-26
summary: "Rust实现从头构建编译器：Pylite语言→x86汇编，涵盖lexer/parser/语义分析/IR/优化/代码生成"
---

# Build a Compiler from Scratch

## 核心内容

**编译器架构（Pipeline）**
```
PARSER → SEMANTIC ANALYZER → IR GENERATOR → OPTIMIZER → CODE GENERATOR
```

- **Parser**：源代码→Parse Tree（语法树）
- **Semantic Analyzer**：类型检查、名字解析
- **IR Generator**：Parse Tree→中间表示（IR）
- **Optimizer**：IR层面优化
- **Code Generator**：IR→x86汇编

**前端 vs 后端**
- 前端（分析）：Parser + Semantic Analyzer + IR Generator
- 后端（综合）：Optimizer + Code Generator

**目标语言**
- 源语言：Pylite（Python子集）
- 目标：x86-64汇编（AT&T语法）

**系列内容**
- Part 0: Introduction（本篇）
- Part 1.1: Hello World of sorts
- Part 1.2: IR and Code Generation
- 更多内容持续更新中

## 来源详情

- 路径：`raw/bookmarks/ebooks/compiler-from-scratch.md`
- 博客：https://blog.sylver.dev/build-a-compiler-from-scratch-part-0-introduction
- 标签：#rust #compiler #tutorial
