# 车载 IAM + LLM Guard 综合白皮书

> **版本**: v1.0
> **日期**: 2026-07-21
> **状态**: 评审稿
> **整合自**: 7 份 research 文档 + 1 份 Framework v2.0 整合 spec

---

## 整合源

| 文档 | 路径 | 核心贡献 |
|------|------|----------|
| AI Agent IAM 调研 | `../ai-agent-security-iam/report.md` | 6 层防护栈 / NHI / Least Agency / 4 大 IAM 平台 |
| 车载端侧 AI 安全 | `../vehicle-edge-ai-security/report.md` | 车规三层标准 / 物理安全 / 传感器对抗 |
| LLM 应用安全架构 | `../llm-app-security-architecture/report.md` | 三层平面 / 5 层信任域 / 7 个控制点 |
| OWASP LLM Top 10 防御 | `../owasp-llm-top10-defenses/report.md` | LLM01-10 详细防御 + 30 开源工具 |
| MITRE ATLAS 101 | `../atlas-ai-security-101/AI-Security-101-CN.md` | ATLAS 基础概念 |
| 委托链标准调研 | `../llm-agent-delegation-research-2026/README.md` | OIDC-A / SPIFFE / JWT-SVID |
| ASG 车规形态 | `../nio-asg-design/architecture.md` | 单进程 + 2 Gate 实现 |
| Framework v2.0 | `../nio-vehicle-ai-agent-security-framework-design-v1/framework-design-v2-integrated.md` | 完整 spec |

---

## 白皮书目录

```
第 1 章 — 知识地图与整合逻辑
第 2 章 — 基础威胁模型（OWASP / ATLAS / 车规）
第 3 章 — 车端 IAM 体系
第 4 章 — LLM Guard 体系
第 5 章 — 三域差异化（座舱 / 智驾 / 车控）
第 6 章 — ASG 实现形态
第 7 章 — 协议与接口
第 8 章 — 关键流程
第 9 章 — 实施路线图
第 10 章 — 风险与缓解
附录 — 术语表 / 工具清单 / 参考资料
```

完整内容见 `whitepaper.md`。
