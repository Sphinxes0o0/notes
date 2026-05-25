---
type: entity
tags: [cpp, ai, testing, iso26262, parasoft, functional-safety]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# 李彦博 — From Automation to Intelligence: AI Reshaping C++ Software Testing

## 定义
Parasoft工程师李彦博的演讲，阐述AI技术如何重塑C++软件测试：Parasoft C/C++test的自动化单元测试、静态分析、代码覆盖，以及ISO 26262功能安全认证支持。

## 关键要点

### AI技术的发展阶段
- **大模型定义**：具有庞大参数规模和复杂计算结构的机器学习模型
- **当前状态**：近乎达到强人工智能水平，未来将发展为超强人工智能

### 传统软件测试的瓶颈
- 缺陷定位慢
- 用例设计难
- 复杂场景不足
- 维护成本高
- 功能安全挑战

### Parasoft C/C++test 核心功能
- **静态分析**（1994年以来行业领导者）：数据流/控制流分析，40+代码度量，一键式应用安全关键性行业最佳实践
- **单元测试**（1997年以来行业领导者）：自动生成高覆盖率的健壮性测试套件，灵活生成和优化测试用例
- **代码覆盖率**：九种覆盖率指标（代码行/语句/代码块/路径/判定/MCDC）
- **运行时错误检测**：内存/资源类缺陷，轻量级测试适用于嵌入式
- **需求双向追溯**：无缝集成Polarion/CodeBeamer/Jira/TeamForge

### 功能安全标准支持
- **航空**：DO-178C, DO-326A
- **汽车**：ISO 26262, AUTOSAR, pCWE
- **工业**：IEC 62304, IEC 61508, EN 50128
- **安全**：IEC 81001-5-1, UL 2900

### ISO 26262软件级产品开发验证过程
- Part 6-5：软件产品开发总则
- Part 6-8：软件单元设计与实现 → 静态分析、数据流/控制流分析、度量指标分析
- Part 6-9：软件单元验证 → 自动化单元测试、需求测试双向追溯
- Part 6-10：软件集成和验证 → 自动化集成测试、代码覆盖率
- Part 6-11：嵌入式软件测试 → 目标设备/仿真器/在环测试

## 相关概念
- [[entities/cpp/smart-pointers]] — 测试中的内存泄漏检测
- [[entities/cpp/cpp-stl-algorithms]] — 测试用例生成中的算法应用

## 来源详情
- [[sources/pdf-cpp-slides]] — 李彦博, AI重塑C++软件测试未来, Parasoft 2025
