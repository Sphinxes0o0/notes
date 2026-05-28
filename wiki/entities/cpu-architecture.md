---
type: entity
tags: [computer-architecture, CPU, ISA, pipeline, RISC, CISC]
created: 2026-05-28
sources: [bookmark-archbase]
---

# CPU Architecture

## 定义

CPU架构涵盖指令集体系结构（ISA）和微架构两个层面：ISA定义软件与硬件的接口规范（指令格式、寄存器、内存模型、特权级别）；微架构是ISA的具体硬件实现（流水线深度、发射宽度、Cache配置）。

## 关键要点

### ISA 设计原则
- **兼容性**：x86保持30年向后兼容，是市场成功的关键
- **通用性**：覆盖运算/访存/转移/特殊指令四类
- **高效性**：便于硬件流水线、多发射、乱序执行
- **安全性**：保护模式、特权级、地址空间隔离

### ISA 类型
- **CISC**（复杂指令系统）：x86、x64，指令长度可变，微码翻译为类RISC内部操作
- **RISC**（精简指令系统）：ARM、MIPS、RISC-V、LoongArch，固定长度，仅load/store访存
- **VLIW**（超长指令字）：编译器静态指定并行，无硬件冒险判断

### 微架构：流水线
- **五级流水线**：取指(IF)→译码(ID)→执行(EX)→访存(MEM)→写回(WB)
- **流水线冒险**：结构冒险（硬件冲突）、数据冒险（RAW/WAR/WAW）、控制冒险（分支预测）
- **超标量**：多发射，同一时刻多条指令在不同流水级
- **乱序执行**：寄存器重命名+ROB，违背程序顺序但保证结果正确

### 微架构：分支预测
- 动态分支预测：两位饱和计数器、BHT（分支历史表）、BTB（分支目标缓冲器）
- 分支历史移位寄存器（GHR）：记录最近N次分支方向
- 返回地址栈（RAS）：函数返回地址预测

### 关键概念
- **IPC**（Instructions Per Cycle）：衡量CPU效率的核心指标
- **流水线停顿**：数据依赖导致的stall cycles
- **流水线深度**：越深主频越高，但冒泡代价越大
- **指令发射宽度**：每周期发射的指令数

## 相关概念

- [[cache-memory-design]] — Cache是CPU与DRAM之间的速度桥梁，影响IPC
- [[arm/armv8-architecture]] — ARMv8-A是RISC ISA的典型代表
- [[arm/arm-cortex-a9]] — Cortex-A9微架构：超标量+乱序执行
- [[computer-architecture]] — 体系结构基础（已有综合页）
- [[qemu-cpu]] — QEMU如何模拟CPU执行

## 来源详情

- [[sources/bookmark-archbase]] — 计算机体系结构基础（龙芯第3版）
- 章节覆盖：ISA设计/流水线/运算器/多核/存储层次
