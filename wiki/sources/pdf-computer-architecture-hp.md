---
type: source
source-type: pdf
title: 计算机体系结构：量化研究方法（第五版）
author: John L. Hennessy, David A. Patterson
date: 2017
size: large
path: raw/PDFs/books/计算机体系结构：量化研究方法（第五版）（中文版）.pdf
summary: "CS:APP Architecture（Hennessy & Patterson）第五版：612页计算机体系结构权威教材量化研究方法经典"
tags: [computer-architecture, cpu, gpu, performance, quantitative, books]
created: 2017
---
# 计算机体系结构：量化研究方法（第五版）

## 核心内容

**Authors:** John L. Hennessy & David A. Patterson | 2017 | 第五版 | 612页

### 地位

被誉为"计算机体系结构圣经"，与《计算机系统程序员视角》(CS:APP) 并列为体系结构领域两大经典。

**经典语录**：
> "Architecture = Organization + Hardware"

### 核心内容

- **量化研究方法**：用测量和实验方法评估计算机系统
- **指令集体系结构**：RISC vs CISC，x86/ARM/RISC-V
- **流水线**：五级流水线/超标量/乱序执行
- **内存层次**：Cache (L1/L2/L3) + 主存 + 辅存
- **并行性**：ILP/TLP/DLP/MLP
- **多核处理器**：片上多核架构
- **领域专用体系结构**：DSA，GPU，TPU

### 关键概念

| 概念 | 说明 |
|------|------|
| Roofline Model | 计算密度与带宽的权衡分析 |
| Amdahl定律 | 并行化收益的上限 |
| CPI/IPC | 每指令周期数/每周期指令数 |
| SPEC CPU | 标准化性能基准测试 |

### 与CS:APP的关系

| 维度 | CS:APP | H&P Architecture |
|------|--------|-------------------|
| 定位 | 程序员视角 | 体系结构设计视角 |
| 重点 | 系统编程/性能 | ISA/流水线/并行 |
| 受众 | 软件工程师 | 硬件/系统架构师 |

## 相关页面
- [[entities/arm/computer-architecture]] — 计算机体系结构
- [[entities/cpp/cpp-perf-optimization]] — C++性能优化（涉及CPU）
- [[os-index]] — 操作系统
- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP