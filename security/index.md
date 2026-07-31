---
title: Security Notes
---

# 安全工具

本节收录网络安全监控、入侵检测、漏洞扫描等安全工具的架构分析笔记。

## 内容分类

### 网络扫描
- [Masscan](/security/masscan/ARCHITECTURE) - 高速端口扫描器

### 安全监控
- [Falco](/security/falco/ARCHITECTURE) - Kubernetes 安全监控

### 入侵检测
- [Snort 3](/security/nids/snort3_architecture_analysis) - 网络入侵检测系统架构分析

### LLM Agent 安全防御
- [Agent IAM 认证架构](/security/llm_agent_defense/iam_auth_architecture) - 4 层 Token 模型、KMSS、委托链、凭据管理
- [分层防御方案](/security/llm_agent_defense/layered_defense) - Guard 模型 + 规则层 + 沙箱 + 高通 SA8155 部署
- [详细架构](/security/llm_agent_defense/detailed_architecture) - 启动序列、状态机、故障演练
- [A2A 协议与车端 IAM 集成](/security/llm_agent_defense/a2a/) - Agent-to-Agent 协议在车端的应用 (7 篇系列)
