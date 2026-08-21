---
title: LLM / AI Agent 安全研究报告合集
---

# LLM / AI Agent 安全研究报告合集

> 围绕 **LLM 应用 + AI Agent 安全** 的通用调研报告合集（无特定行业场景）。
> 适合作为架构师 / 安全工程师 / 后端 / Agent 工程师的入门与速查手册。

## 文件清单

| 文件 | 体裁 | 适合谁 | 读完时间 |
|---|---|---|---|
| [`ai-agent-security-iam.md`](./ai-agent-security-iam.md) | 全景调研 | 想了解 AI Agent 安全威胁模型 + IAM 身份治理 + 主流工具 + 厂商方案的从业者 | 60-90 分钟 |
| [`llm-app-security-architecture.md`](./llm-app-security-architecture.md) | 系统架构 | 想从"信任域划分 / 数据流 / 控制点 / 身份管理"角度设计 LLM 应用的架构师 | 60 分钟 |
| [`llm-app-security-architecture.html`](./llm-app-security-architecture.html) | 系统架构（带可视化） | 同上，浏览器阅读含图表 | — |
| [`owasp-llm-top10-defenses.md`](./owasp-llm-top10-defenses.md) | 防御手册 | 想知道 OWASP LLM Top 10 (2025) 每条具体怎么防的工程师 | 30 分钟 |

## 阅读路径建议

### 新人入门

```
owasp-llm-top10-defenses.md          ← 30 分钟掌握 10 类核心威胁与对应防御
    ↓
llm-app-security-architecture.md     ← 把防御落到系统架构：信任域 / 控制点 / 身份
    ↓
ai-agent-security-iam.md             ← 横向铺开：工具、厂商、标准
```

### 直接做防御落地

```
owasp-llm-top10-defenses.md   ← 速查：每条 Top 10 配防御方案
```

### 直接做架构设计

```
llm-app-security-architecture.md
ai-agent-security-iam.md      ← 当 IAM / 鉴权部分参考
```

## 关联项目（同级目录）

- [`../../research/nio-vehicle-ai-agent-security/`](../../research/nio-vehicle-ai-agent-security/) — 车端 AI Agent 安全的**特定行业**研究线
- [`../../research/agent-safetybench-singuard-eval/`](../../research/agent-safetybench-singuard-eval/) — SingGuard 护栏模型在 Agent-SafetyBench 上的实测
- [`../../research/uber-adr-analysis/`](../../research/uber-adr-analysis/) — Uber 企业级 Agent 检测与响应
- [`../../research/agentgateway-analysis/`](../../research/agentgateway-analysis/) — Agent 网关 + 多 Agent 编排深度分析