---
type: entity
tags: [cpp, ai, software-engineering, technical-debt]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# David Sankel — Beyond the Hype: Mitigating Real Risks of AI-Generated Code

## 定义
Adobe首席科学家David Sankel分析AI生成代码的真实风险：幻觉陷阱、战略稳定性、技术债与"人力债"，并提供安全集成检查清单。

## 关键要点

### 承诺 vs 现实
- **宣传**："AI会为你写所有代码，你会快10倍"
- **现实**：正面临"Day 2"困境 — 更多时间花在配置工具上，持续上下文切换破坏工作流

### 问题#1：演讲已过时
- 新模型几乎每周发布（Claude/GPT/Gemini/Copilot）
- 新IDE集成每天出现
- 陷阱：更多时间配置工具而非使用工具

### 规避措施#1：战略稳定性
- **试点项目**：指定小型"探索"团队测试新工具
- **经验法则**：测试周期按"月"算而非"天"
- **坚持学习**：选定工具集，长期掌握其特性
- **知识共享**：创建内部空间分享"我学到了什么"

### 问题#2：幻觉陷阱
- AI优化合理性（plausibility）而非正确性（correctness）
- 代码看起来地道，变量名有意义，但调用不存在的函数
- 个人经历：花数小时调试AI"幻想"出来的环境变量

### 技术债与人力债
- **技术债**：AI生成代码的维护成本随时间累积
- **人力债**：团队知识被AI稀释，集体理解能力下降
- **稳定性问题**：AI生成代码的行为可能随模型版本变化

### 安全集成检查清单
- 代码审查不可省略
- 理解AI生成代码的假设和限制
- 保持团队核心工程能力

## 相关概念
- [[entities/cpp/smart-pointers]] — AI代码中常见的内存管理问题
- [[entities/cpp/cpp-safety]] — David Sankel纵深防御（[[entities/cpp/cpp-safety]]）

## 来源详情
- [[sources/pdf-cpp-slides]] — David Sankel, 规避AI生成代码的真实风险, Adobe 2025
