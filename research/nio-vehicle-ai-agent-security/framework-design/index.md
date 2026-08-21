---
title: Framework Design
---

# NIO Vehicle AI Agent Security Framework — 正式设计文档

> **版本**: v2.0 (整合版)
> **日期**: 2026-07-21
> **状态**: 评审稿
> **主交付物**: [`framework-design-v2-integrated.md`](./framework-design-v2-integrated.md) — **整合 spec v2.0（Framework + ASG）**
>
> **历史版本**: v1.1 设计 spec 见 git history（已合并入 v2.0）
>
> **v2.0 增量**:
> - 整合 Framework v1.1 + ASG v0.1 两份设计稿
> - 给出 8 个模块的详细设计（IAM / INPUT / OUTPUT / Guard / 审计 / Sub-Agent / 跨域 / 凭证）
> - 完整接口定义（ASG 8 个 C API + gRPC proto + 数据结构 + 错误码）
> - 6 个关键流程的时序细节（启动 / 工具调用 / Sub-Agent / 跨域 / OTA / Kill Switch）
> - 三域差异化的完整资源预算

## 文件说明

| 文件 | 用途 | 受众 | 大小 |
|------|------|------|------|
| `framework-design-v2-integrated.md` | **整合 spec v2.0**（Framework + ASG 详细设计 + 接口定义）| Coding Agent v2 / 实施工程师 | 33 KB |
| `index.md` | 本文件，目录说明 | 任意编辑器 | - |

## 设计文档结构

```
框架设计文档 v1.0
├─ 0. 文档信息
├─ 1. 背景与目标
├─ 2. 整体架构（全景图 + 凭证流）
├─ 3. 基础设施层（KMSS / TEE / NTS）
├─ 4. 身份层（Blueprint / Registry / 状态机）
├─ 5. 认证层（Attestation 三层栈）
├─ 6. 凭证层（L1 / L2 / L3 JWT-SVID）
├─ 7. 授权层（OpenFGA + Conditional Access）
├─ 8. 通信层（gRPC + SPIFFE Federation）
├─ 9. Sub-Agent 层（线程 / 裸进程双模）
├─ 10. 审计层（TEE 加密 + 异步上传）
├─ 11. 威胁模型（T-01..T-10）
├─ 12. 三域差异化（座舱 / 智驾 / 车控）
├─ 13. 决策汇总表
├─ 14. 实施 Roadmap
├─ 15. 风险与缓解
├─ 附录 A: 术语表
├─ 附录 B: 参考资料
├─ 附录 C: 修订历史
```

## 配套文档

- `../nio-asg-design/architecture.md` — 配套的 **AgentSec Gateway（ASG）** 网关层设计（lib + daemon）
- `../llm-agent-delegation-research-2026/README.md` — 本设计的**调研依据**（四梯队资料 + 决策对齐表）

## 评审建议

1. **第 1 轮（架构层）**: 重点看 §2 整体架构 + §13 决策汇总
2. **第 2 轮（模块层）**: 按 §3-§10 顺序 review 各模块
3. **第 3 轮（威胁 / 落地）**: §11 威胁模型 + §14 Roadmap
4. **第 4 轮（合规）**: §15 风险与缓解 + 跟 KMSS / 认证团队对齐

## 反馈

请直接在 Confluence 评审页面或对应 GitLab MR 上留言，标注"FD v1.0"前缀。
