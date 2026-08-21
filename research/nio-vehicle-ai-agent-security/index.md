---
title: NIO 车端 AI Agent 安全研究合集
---

# NIO 车端 AI Agent 安全研究合集

> 围绕 **NIO 车端 AI Agent 安全框架** 的一份完整研究线（端云协同 / 多规模 LLM / ASIL-D）。
> 由 2026-06~07 的多轮调研、设计、整合沉淀而成。

## 文件清单（按主题阅读顺序）

### 1. 调研层（Why / What）

| 文件 | 来源 | 内容 |
|---|---|---|
| [`edge-ai-security-report.md`](./edge-ai-security-report.md) | 原 `vehicle-edge-ai-security/report.md` | 车载端侧 AI 模型安全与 IAM 方案深度调研（端到端自动驾驶 / VLM / 智能座舱 LLM Agent） |
| [`iam-llm-guard-whitepaper.md`](./iam-llm-guard-whitepaper.md) | 原 `vehicle-iam-llm-guard-whitepaper/whitepaper.md` | 车载 IAM + LLM Guard 综合白皮书 v1.0（评审稿） |
| [`iam-llm-guard-README.md`](./iam-llm-guard-README.md) | 原 `vehicle-iam-llm-guard-whitepaper/README.md` | 上述白皮书的目录说明 |

### 2. 整合设计层（How）

| 文件 | 来源 | 内容 |
|---|---|---|
| [`vehicle-iam-integrated.md`](./vehicle-iam-integrated.md) | 原根目录 `vehicle-iam-integrated.md` | 车端 AI Agent IAM 综合设计文档 v1.0（2026-07-23）—— 跨车端 / 智驾 / 座舱的统一 IAM 模型 |

### 3. 框架实施层（Spec）

| 文件 | 来源 | 内容 |
|---|---|---|
| [`framework-design/README.md`](./framework-design/README.md) | 原 `nio-vehicle-ai-agent-security-framework-design-v1/README.md` | NIO 车端 AI Agent 安全框架正式设计文档入口 |
| [`framework-design/framework-design-v1.html`](./framework-design/framework-design-v1.html) | — | Framework v1.1 评审稿（含 10 个 mermaid 图） |
| [`framework-design/framework-design-v1.md`](./framework-design/framework-design-v1.md) | — | Framework v1.1 Coding Agent Spec（紧凑 markdown，给 LLM 消费的纯文本视图） |
| [`framework-design/framework-design-v2-integrated.md`](./framework-design/framework-design-v2-integrated.md) | — | Framework v2.0 整合版（合并 ASG v0.1 + 四梯队调研） |

## 阅读路径建议

```
edge-ai-security-report.md      ← 端侧威胁面 & 约束（为什么车端不同）
    ↓
iam-llm-guard-whitepaper.md     ← 车端 IAM + LLM Guard 设计原则
    ↓
vehicle-iam-integrated.md       ← 跨域统一的 IAM 模型
    ↓
framework-design/               ← 把上述抽象落到具体模块、API、字段
```

## 关联项目（同级目录）

- [`../../security/llm-agent-security-reports/`](../../security/llm-agent-security-reports/) — 通用 LLM / AI Agent 安全调研报告（无车端特异性；2026-08 从 research/ 迁移到 security/）
- [`../agent-safetybench-singuard-eval/`](../agent-safetybench-singuard-eval/) — SingGuard 在 Agent-SafetyBench 上的实测
- [`../spiffe-translation/`](../spiffe-translation/) — SPIFFE 身份标准（车端 SPIFFE 化设计的参考）
- [`../agentgateway/`](../agentgateway/) 与 [`../agentgateway-analysis/`](../agentgateway-analysis/) — Agent 网关与多 Agent 编排（车云协同的网关层参考）