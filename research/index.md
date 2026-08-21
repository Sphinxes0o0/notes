---
title: Research
---

# 研究合集

> 个人研究 / 项目分析 / 研报综述的汇总入口。
> 这些内容主题相关但**不是工具或教程**，故放在 `research/` 而非 `ccpp/` / `network/` 等。

## 主题分类

| 子目录 | 性质 | 核心问题 |
|---|---|---|
| [`agent-safetybench-singuard-eval/`](./agent-safetybench-singuard-eval/) | 实测评估 | SingGuard 在 Agent-SafetyBench 上的实测结果 |
| [`agentgateway-analysis/`](./agentgateway-analysis/) | 项目分析 | Agentgateway 项目深度分析（含 IAM 认证 / AgentTeams） |
| [`nio-vehicle-ai-agent-security/`](./nio-vehicle-ai-agent-security/) | 内部研究 | NIO 车端 AI Agent 安全：IAM 设计 / 框架 spec / 边缘 AI 报告 |
| [`uber-adr-analysis/`](./uber-adr-analysis/) | 案例分析 | Uber ADR（架构决策记录）深度分析 |

## 与 security/ 的边界

| 内容类型 | 在哪 | 说明 |
|---|---|---|
| **通用 LLM Agent 安全研报**（OWASP / 三实验室 / METR）| [`/security/llm-agent-security-reports/`](../security/llm-agent-security-reports/) | 与 `security/network-traffic-analysis/`（论文集）同性质，外部资料综述 |
| **LLM Agent 防御方案**（分层防御 / IAM 架构 / A2A 协议）| [`/security/llm_agent_defense/`](../security/llm_agent_defense/) | 通用工程防御方案，可独立实施 |
| **NIO 车端 AI Agent 安全** | `./nio-vehicle-ai-agent-security/` | 内部研究 / 框架 spec / 行业特定（车规）|
| **项目 / 案例分析** | `./agentgateway-analysis/`、`./uber-adr-analysis/` | 项目深度拆解 |

## 阅读建议

- **想了解通用威胁模型**：先看 `security/llm_agent_defense/layered_defense`
- **想了解 OWASP Top 10 防御**：`security/llm-agent-security-reports/owasp-llm-top10-defenses`
- **在做车端 AI Agent 项目**：从 `nio-vehicle-ai-agent-security/` 的 `index.md` 开始