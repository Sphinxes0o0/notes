# AI Agent 安全与 IAM 方案全景调研报告

> **报告时间**：2026 年 6 月
> **研究范围**：AI Agent（LLM Agent / Tool-Use Agent / 多智能体系统）的安全威胁模型、IAM 身份治理、主流开源工具、头部厂商方案、行业共识与标准
> **调研方法**：多源信息检索 + 交叉验证 + 一手资料（论文/官方文档/技术博客）

---

## 0. 摘要（TL;DR）

AI Agent 的"自主决策 + 工具调用 + 持久记忆 + 多 Agent 协作"四大能力，在带来效率革命的同时，**从根本上打破了传统 IAM"主体=人"的假设**。业界已基本形成如下共识：

1. **威胁模型独立化**：传统 Web/云安全威胁（如 OWASP Top 10 2025）已无法覆盖 Agent 场景，需用 **OWASP ASI01–ASI10（Agentic Security Initiative）+ MITRE ATLAS** 重新建模。
2. **IAM 主体扩展**：Agent 成为"非人类身份（NHI）"的一等公民，需独立身份、最小权限、凭证轮换、生命周期管理——业界称为 **"Least Agency"** 原则。
3. **协议标准化**：MCP（Model Context Protocol）成为 Agent ↔ 工具的事实标准，**OIDC-A 1.0**（OpenID Connect for Agents）成为 Agent IAM 的新协议方向。
4. **防御栈分层**：业界普遍放弃"靠 prompt 工程堵住一切"的思路，转向 **6 层防护栈**（Fence / 注入检测 / 工具守卫 / 执行门 / 最小权限 / 红队门禁）。
5. **大厂布局收敛**：Microsoft Entra Agent ID、Google Agent Identity、AWS AgentCore Identity、Okta for AI Agents 形成"四大 Agent IAM 平台"格局；NVIDIA NeMo Guardrails、阿里 Qwen3Guard、OpenAI Agent SDK Guardrails、AWS Bedrock Guardrails 是"四大开源/半开源护栏工具"。

---

## 1. 研究框架：AI Agent 安全问题的"三张面孔"

AI Agent 的安全问题可以从 **威胁、IAM、运行时** 三个维度切入，这三个维度互相依赖，缺一不可：

```
┌──────────────────────────────────────────────────────────┐
│  ① 威胁建模（What can go wrong）                          │
│     OWASP LLM Top 10 / OWASP ASI01-ASI10 / MITRE ATLAS    │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│  ② IAM 身份治理（Who is acting, with what authority）      │
│     Agent Identity / Least Agency / OIDC-A / 生命周期     │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│  ③ 运行时防护（How do we constrain execution）             │
│     Guardrails / 沙箱 / 工具守卫 / 6 层防护栈 / 红队      │
└──────────────────────────────────────────────────────────┘
```

下面按这三条主线展开。

---

## 2. 主流共识：标准与威胁框架

### 2.1 OWASP：两套互补的 Top 10

| 标准 | 适用场景 | 核心风险条目（部分） |
|---|---|---|
| **OWASP Top 10 for LLM Applications（2025 版）** | LLM 应用整体 | LLM01 Prompt Injection、LLM02 Sensitive Information Disclosure、LLM03 Supply Chain、LLM06 Excessive Agency（过度代理）、LLM07 System Prompt Leakage、LLM10 Model Theft |
| **OWASP GenAI Security Project — ASI01–ASI10** | AI Agent / Agentic 系统 | ASI01 Agent Goal Hijack、ASI02 Tool Misuse、ASI03 Identity & Privilege Abuse、ASI04 Agentic Supply Chain、ASI05 Unexpected Code Execution、ASI06 Memory & Context Poisoning、ASI08 Cascading Failures、ASI09 Rogue Agents、ASI10 Human-Agent Trust Exploitation |

来源：[OWASP LLM Top 10 解读 (ChaMD5)](https://www.cnblogs.com/) / [OWASP GenAI Security Project](https://genai.owasp.org/)

**业界共识**：LLM06"过度代理"是 Agent 场景的**最大新型风险**，它直接催生了 **"Least Agency"** 这个 Agent 安全的核心原则。

### 2.2 MITRE ATLAS（AI 专用威胁框架）

- **定位**：MITRE ATT&CK 的 AI 扩展，2024 年起持续更新
- **规模**：16 个战术（Tactics）× 84 个技术（Techniques）
- **覆盖**：训练数据投毒、对抗样本、提示注入、模型窃取、成员推断、梯度泄露、提示泄露、Agent 工具滥用等
- **与传统 ATT&CK 的关系**：传统 IT 入侵仍需 ATT&CK，AI 特定攻击面用 ATLAS，**两者联合使用**

来源：[MITRE ATLAS 官方](https://atlas.mitre.org/) / [CSDN - AI Security 03](https://blog.csdn.net/)

### 2.3 NIST AI RMF（风险管理框架）

- **AI Risk Management Framework**（2023 年发布）+ **AI Agent Profile 草案（2025）**
- 三大功能：**Map / Measure / Manage / Govern**
- **AI Agent Profile 新增要求**：
  - 身份认证（Identity）
  - 权限管控（Authorization）
  - 行为审计（Audit）—— **"可解释性日志"**：不仅记录"调了什么 API"，还要记录"基于什么推理步骤"
  - AI Agent 像人类员工一样被管理

来源：[NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

### 2.4 关键学术协议草案

| 草案 | 来源 | 核心贡献 |
|---|---|---|
| **OIDC-A 1.0**（OpenID Connect for Agents） | arXiv:2509.25974 | OAuth 2.0 生态内的 Agent 身份/委托链/属性授权标准扩展 |
| **Identity Management for Agentic AI** | arXiv:2510.25819 | 多机构联合白皮书，定义 Agent IAM 概念框架 |
| **Enterprise-Grade Security for MCP** | arXiv:2504.08623 | MCP 协议的企业级安全加固方案 |
| **MCP Safety Audit** | arXiv:2504.03767 | 实证研究 MCP 协议的安全漏洞谱 |
| **CausalArmor**（Google） | arXiv:2602.07918v1 | 因果归因法检测间接 Prompt Injection |

---

## 3. IAM for AI Agent：从 NHI 到"Agent Identity 一等公民"

### 3.1 为什么传统 IAM 不够？

传统 IAM 的隐含假设：**主体是人**。Agent 出现后这些假设全部失效：

| 传统假设 | Agent 场景的现实 |
|---|---|
| 主体是人，需要 MFA | Agent 7×24 运行，无法使用 MFA |
| 凭据长期稳定 | Agent 生命周期短，需自动轮换 |
| 权限按"角色"静态分配 | 权限按"任务"动态申请 |
| 一个用户 ≈ 一个身份 | 一个业务可能调用几百个 Agent |
| 出问题可重置密码 | Agent 出问题需"终止开关" |

### 3.2 Agent IAM 的六大核心能力（业界共识）

1. **独立身份**：Agent 不是"借用人的权限"，而是**一等公民**（first-class identity）
2. **身份绑定（Identity Binding）**：Agent 与用户/委托人/模型/代码做密码学绑定（数字签名、证书）
3. **最小代理权限（Least Agency）**：每次任务按需申请最小权限，**用完即废**
4. **生命周期管理**：创建 → 授权 → 轮换 → 回收，全链路可审计
5. **终止开关（Kill Switch）**：异常时**通用注销**（global revocation），立即撤销所有 token
6. **可审计性**：每次工具调用都关联到"哪个 Agent → 谁授权 → 哪段输入 → 为什么这么做"

### 3.3 协议方向：OIDC-A 1.0

**OIDC-A（OpenID Connect for Agents）1.0** 是 arXiv 2509.25974 提出的标准草案，目的是：

- 在 OAuth 2.0 生态内表示 Agent 身份（区别于人和机器账户）
- 支持**委托链**（Delegation Chain）：用户 → 主 Agent → 子 Agent
- 基于 Agent 属性做**细粒度授权**（attestation-based authorization）
- 与现有 IdP（Okta、Entra、Auth0）兼容

来源：[OpenID Connect for Agents (OIDC-A) 1.0](https://arxiv.org/abs/2509.25974)

---

## 4. 主流开源方案全景

按"运行时护栏 / 沙箱 / 身份治理 / 协议"四大类划分：

### 4.1 护栏（Guardrails）类

| 项目 | 厂商 | 类型 | 核心能力 |
|---|---|---|---|
| **NVIDIA NeMo Guardrails** | NVIDIA | 开源 | 5 类护栏：输入 / 对话 / 检索 / 执行 / 主题；用 Colang 语言编程；3.5 万标注样本的 Aegis 数据集；GPU 加速 |
| **OpenAI Agents SDK — Guardrails** | OpenAI | 开源 | Input Guardrail + Output Guardrail + Tool Guardrail；以可抛异常实现"绊线"（tripwire） |
| **AWS Bedrock Guardrails** | AWS | 商业（但 API 标准化） | 内容过滤 + 主题控制 + PII 脱敏 + Prompt Attack 检测；多模态准确率 88% |
| **阿里 Qwen3Guard** | 阿里 | 开源（HuggingFace / ModelScope） | Qwen3Guard-Gen（离线标注）+ Qwen3Guard-Stream（流式检测）；0.6B / 4B / 8B 三种规模；119 种语言 |
| **Google Model Armor** | Google | 商业 | 与 Agent Gateway 集成；防御间接 prompt injection |
| **Lakera Guard** | Lakera | 商业 SaaS | 专注 prompt injection 防御；含 Gandalf benchmark |
| **Microsoft Defender for Cloud AI Security Posture** | Microsoft | 商业 | 检测 15+ 种 AI 威胁，包括越狱、配置错误、敏感数据泄露 |
| **Microsoft Purview SDK** | Microsoft | 商业 | 对 AI 数据流执行策略保护 |

### 4.2 沙箱（Sandbox）类

| 项目 | 厂商 | 隔离强度 | 启动速度 | 资源效率 |
|---|---|---|---|---|
| **腾讯 CubeSandbox** | 腾讯云 | KVM 硬件虚拟化（独立 Guest OS 内核） | <60 ms 冷启动 | <5 MB / 实例，单机 2000+ 沙箱 |
| **E2B Code Interpreter** | E2B | Firecracker microVM | ~150 ms | 中等 |
| **Docker** | 开源 | OS 级共享内核 | 3 s | <5% 性能损耗 |
| **OpenAI Agents SDK Sandbox** | OpenAI | 多厂商（Blaxel/Cloudflare/Daytona 等 7 家） | 厂商相关 | 中等 |

腾讯 CubeSandbox 的关键创新：
- eBPF 内核态虚拟交换机 **CubeVS** 实现网络隔离
- "运行时快照 + 资源预创建池化" 把冷启动压到 60 ms
- 原生兼容 E2B 接口，零成本迁移

来源：[腾讯云 CubeSandbox 介绍](https://blog.csdn.net/)

### 4.3 协议与框架

| 项目 | 说明 |
|---|---|
| **MCP（Model Context Protocol）** | Anthropic 2024 年 11 月开源，已成 Agent ↔ 工具事实标准；微软 / OpenAI / 谷歌均支持 |
| **A2A（Agent-to-Agent）** | Google 主导的 Agent 间通信协议 |
| **Anthropic MCP Inspector** | MCP 调试工具（曾有 CVE-2025-49596 RCE 漏洞） |
| **LangChain / LangGraph Guardrails** | 通用 Agent 框架 + 集成护栏 |
| **阿里 AgentScope 1.0** | 三层架构：核心框架 + Runtime（沙箱）+ Studio（可视化） |

### 4.4 其他值得关注的开源/学术项目

- **CyberArk 蜜罐动作（Honeypot Actions）**：在工具集中植入"诱捕工具"，检测异常行为
- **历史感知校验（History-Aware Validation）**：把多轮对话历史整体提交给"裁判模型"检测"历史投毒"
- **Garak**（NVIDIA）：开源 LLM 漏洞扫描工具

---

## 5. 大厂方案对比：四大云厂 + 中国三强 + 模型厂

### 5.1 Microsoft：Entra + Defender + Purview 三件套

**核心产品**：
- **Microsoft Entra Agent ID**（2026 年 3 月推出，业内首个）
  - **Agent ID Administrator** 内置目录角色（模板 ID: db506228-d27e-4b7d-95e5-295956d6615f）
  - **Agent Blueprint**（Agent 蓝图）：预定义的身份模板，含权限范围、凭证策略、条件访问
  - **业务赞助人（Sponsor）机制**：区别于传统 Owner，要求部门经理对 Agent 合规负责
- **Microsoft Defender for Cloud** for AI Workloads：检测 15+ 种 AI 威胁
- **Microsoft Purview SDK**：对自定义 AI 应用的数据流执行策略保护
- **Security Copilot Agents**：安全运营侧的 Agent

**合作伙伴**：ServiceNow、Workday（非人类身份治理集成）

来源：[Microsoft Entra Agent ID 文档](https://learn.microsoft.com/en-us/entra/) / [Microsoft Security](https://www.microsoft.com/security)

### 5.2 Google：Gemini Enterprise Agent Platform

**核心产品**：
- **Agent Identity**：为每个 Agent 分配**唯一密码学身份**，配置明确授权策略
- **Agent Gateway**：执行 MCP / A2A 等协议的安全策略，防范 prompt injection、tool poisoning、数据泄露
- **Agent Runtime**：亚秒级冷启动，支持长期运行 Agent
- **Model Armor**：针对模型和 Agent 交互的运行时防护
- **Agent Evaluation / Observability**：上线前仿真压力测试 + 上线后实时监控
- **Memory Bank**：跨会话持久长期记忆
- **CausalArmor**（研究项目）：因果归因法检测间接 Prompt Injection

来源：[Google Cloud Next 2026](https://cloud.google.com/blog)

### 5.3 AWS：Bedrock AgentCore + Bedrock Guardrails

**AgentCore 七大模块**：
| 模块 | 功能 |
|---|---|
| Runtime | 无服务器、低延迟、多模态执行环境 |
| Memory | 短期 + 长期记忆 |
| **Identity** | 基于 OAuth 的身份管理，Agent 代表用户操作 |
| Gateway | MCP 协议工具网关 |
| Browser | 无头浏览器 |
| Code Interpreter | 安全代码执行环境 |
| Observability | OpenTelemetry/LangSmith/Datadog 集成 |

**Bedrock Guardrails**：配置即用的内容过滤 + 主题控制 + PII 脱敏 + Prompt Attack 检测（多模态准确率 88%）

来源：[AWS Bedrock AgentCore](https://aws.amazon.com/cn/bedrock/)

### 5.4 OpenAI：AgentKit + Agents SDK Guardrails

**核心组件**：
- **Agent SDK / Agents SDK**（2025 初开源，GitHub 15k+ stars）
- **Guardrails 机制**：
  - Input Guardrail
  - Output Guardrail
  - Tool Guardrail（输入 / 输出两个方向）
- **Handoffs**：多 Agent 协作的"切换"被建模成"调一个特殊工具"
- **沙箱执行环境**：2025 年新增，支持 7 家厂商（Blaxel、Cloudflare、Daytona 等）
- **Manifest 抽象**：跨供应商环境可移植性
- **AgentKit**（2025 10 月发布）：从原型到生产的完整工具包

来源：[OpenAI Agent SDK](https://github.com/openai/openai-agents-python)

### 5.5 Anthropic：Constitutional AI + MCP

- **Constitutional AI**：用预设"宪法原则"指导模型自我修正，而非纯 RLHF
- **Claude 4 系列**（2025 年 5 月）：内置多层级安全过滤
- **MCP 协议**：开源贡献者，定义了 Agent ↔ 工具的标准
- **CVE-2025-49596**（MCP Inspector RCE 漏洞）：暴露 MCP 生态的安全成熟度问题
- **Red Team**：定期发布模型安全评估报告

### 5.6 阿里：Qwen3Guard + AgentScope + Agent 安全中心

- **Qwen3Guard**：开源护栏模型（Gen 版 + Stream 版），3 种规模，119 种语言
- **AgentScope 1.0**：三层架构（核心框架 / Runtime / Studio），支持 Agentic RL 训练
- **Agent 安全中心**：IDC 2026 中国智能体威胁检测评估总分第一
  - **Agent 资产地图**：识别 190+ AI 组件，自动生成关系图谱
  - **Agent-SPM**：从镜像构建到运行的全链路合规
  - **Agent ID Guard**：机器身份细粒度访问控制
  - **AI Red Teaming**：基于 Qwen 的攻击 Agent
- **百炼平台**：模型 + 智能体 + AI 安全护栏 API
- **Qwen3Guard 开源**：[HuggingFace](https://huggingface.co/Qwen/qwen3guard)

来源：[阿里云 AI 安全护栏](https://www.aliyun.com/product/content-moderation/guardrail) / [IDC 2026 评估](https://news.qq.com/)

### 5.7 腾讯云：SAFE-AI + Least Agency + CubeSandbox

**"Least Agency" 原则**：赋予 Agent 身份，确保 Agent 永远是**最小代理权限**，强制引入运行时安全机制。

**安全框架（SAFE-AI）**：
- **S - Secure Data Pipeline**：数据全链路安全，零信任 + AES-256 + TLS 1.3
- **A - 分层隔离架构**：沙箱到特权层多级环境，最小权限
- **F - 形式化安全模型**：定义特权层和能力边界
- **E - Enterprise Controls**：企业级治理
- **AI - 全栈防护**：纵深防御 L0–L4

**核心产品**：
- **AI Agent 安全网关**：token 限流 / 提示词防护 / 敏感数据脱敏 / 身份凭据认证
- **CubeSandbox**：见 4.2
- **Agent Runtime**：Serverless 弹性 + Cube 沙箱
- **iOA + Agent 安全中心联动**：桌面端 Agent 保护
- **RCE 全栈风控引擎**：95% 黑产识别，90% Token 成本降低

**12 项最佳实践**：按鉴权类别对 Skill/MCP 分类、巧用共享凭据与动态授权...

来源：[腾讯云 - Least Agency 框架](https://cloud.tencent.com/)

### 5.8 字节跳动：扣子 Coze（已开源）

- **Coze Studio + Coze Loop**：2025 年 7 月 Apache 2.0 开源
- **Coze 3.0**：支持一人 + 多 Agent、多人 + 多 Agent、跨端同步
- **接入 Claude Code、Codex CLI、OpenClaw** 等本地 Agent
- 系统要求极低：2 核 CPU + 4GB 内存即可部署

来源：[Coze Studio GitHub](https://github.com/coze-dev/coze-studio)

### 5.9 Okta & Auth0：第三方 IAM 龙头

- **Okta for AI Agents**（2025 年 4 月发布）：三大核心能力
  - 定位智能体（Agent Discovery）
  - 监控活动状态（Activity Monitoring）
  - 必要时关闭（Kill Switch / Global Revocation）
- **安全代理型企业蓝图（Secure Agentic Enterprise Blueprint）**：
  - Universal Directory 扩展支持 NHI 注册
  - 8000+ 集成的 Okta Integration Network
  - 与 Boomi、DataRobot 等 Agent 平台对接
- **Auth for GenAI**（Auth0 Developer Preview）：
  - 内置认证 + 细粒度授权
  - 异步工作流
  - 安全 API 访问

> **关键数据**：91% 的企业已使用 AI Agent，但只有 **10%** 有管理 NHI 的策略 — Okta 数据

来源：[Okta](https://www.okta.com/)

---

## 6. 6 层防护栈（业界共识的运行时防御模型）

针对 prompt injection，单点防御必然失效。业界共识是**按成本/收益分层组合**，并把"红队攻击成功率"作为发布门禁指标。

| 层级 | 目标 | 典型手段 | 成本 | 拦截能力 | 误伤 |
|---|---|---|---|---|---|
| **L1 Fence** | 降低模型"把数据当指令"概率 | 不可信内容显式分区/标记（`<<UNTRUSTED>>...<</UNTRUSTED>>`） | 低 | 中 | 低 |
| **L2 注入检测** | 过滤明显恶意输入 | 规则 + 模型分类器 | 中 | 中 | 中 |
| **L3 工具守卫** | 阻断越权工具调用 | 工具白名单 + 参数 schema + 审计 | 中 | 高 | 低 |
| **L4 执行门** | 防止"输出驱动执行" | 结构化输出 plan + 校验门 | 中 | 高 | 低 |
| **L5 最小权限** | 外部内容权限降到最小 | 按来源 ABAC 鉴权 | 高 | 高 | 低 |
| **L6 红队门禁** | 风险可度量 | 固定样本库 + CI 阻断 | 中-高 | 系统级 | 低 |

**推荐默认配置**：
- 低权限助手（只总结）：L1 + L2 + L6
- 带工具但低风险：L1 + L3 + L4 + L6
- **高权限企业 Copilot：必须 L1–L6 全开**

来源：[EchoLeak 论文（arXiv:2509.10540）](https://arxiv.org/abs/2509.10540) / [CyberArk 蜜罐动作方法](https://www.infoq.com/news/2026/01/cyberark-agents-defenses/)

### 6.1 真实事故：EchoLeak（CVE-2025-32711）

Microsoft 365 Copilot 在 2025 年被发现的**零点击 prompt injection**：
- 攻击者只需发一封邮件
- 绕过 XPIA 分类器 → 用 reference-style Markdown 绕过链接脱敏 → 利用自动图片拉取 → 滥用 Teams 代理（CSP 允许）外泄数据
- **用户零操作**即被攻陷

**工程教训**：
1. 单点防御被链式绕过
2. 跨信任边界是核心危险点（外部输入 → 内部数据 → 外部回传）
3. 工具守卫（L3）ROI 高于注入检测（L2）

---

## 7. 关键协议与生态：MCP 的崛起与挑战

### 7.1 MCP（Model Context Protocol）

- **2024 年 11 月** 由 Anthropic 开源
- **架构**：Host（Claude Desktop / IDE）↔ Client ↔ Server（GitHub / Slack / DB）
- **2025 年 3 月** 规范版本成为业界主流
- **微软 / OpenAI / 谷歌** 均已支持

### 7.2 MCP 的安全挑战

| 风险 | 案例 |
|---|---|
| 命令注入 | 43% 公开 MCP 服务器存在命令注入缺陷 |
| RCE | CVE-2025-49596（MCP Inspector，CVSS 9.4） |
| 描述投毒（Description Poisoning） | MCP 工具描述被篡改，诱导 LLM 调用 |
| 过度授权 | MCP 服务器权限过大 |
| 横向移动 | 通过信任链从弱权限服务器攻陷强权限服务器 |

来源：[Enterprise-Grade Security for MCP（arXiv:2504.08623）](https://arxiv.org/abs/2504.08623)

### 7.3 MCP 安全机制（推荐实践）

- 远程连接必须 **OAuth 2.0 鉴权**（MCP 2025 路线图）
- 服务发现（Service Discovery）标准化
- 包管理（标准化 MCP Server 打包格式）
- 会话令牌 + Origin 头检查（修复 CVE-2025-49596）

---

## 8. 监管与合规：政策环境

| 地区/机构 | 政策 | 关键点 |
|---|---|---|
| **中国** | 《人工智能安全治理框架 2.0》（2025 年 9 月） | 首次明确"智能体演进"趋势，提出"熔断机制"和"一键管控" |
| **欧盟** | EU AI Act | 高风险 AI 系统（含 Agent）需 CE 认证、人工监督、可追溯 |
| **美国** | NIST AI RMF + AI Agent Profile（草案） | 标准化"身份认证-权限管控-行为审计"全链 |
| **行业自律** | Microsoft Responsible AI、Google AI Principles、Anthropic Constitutional AI | 公平性 / 可靠性 / 隐私 / 包容性 / 透明度 / 问责制 6 大原则 |

---

## 9. 行业现状数据（用于校准认知）

- **91%** 企业已使用 AI Agent（Okta 2025）
- 仅 **10%** 企业有 NHI 管理策略（Okta）
- **68%** 企业 AI 安全事件源于 Agent 身份权限管理不当（Microsoft MSRC 2026 Q1）
- **84.30%** 是基于 LLM 的 Agent 最高平均攻击成功率（学界研究）
- **GPT-4 Agent** 可自主利用 **87%** 的测试漏洞（学界研究）
- **3.73%** 应用受 OWASP Top 10 #1 访问控制失效影响
- 微软 Entra CVE-2025-55241（CVSS 10.0）暴露 IAM 系统对 Agent 信任传递的脆弱性
- 国内某上市零售企业因 AI 导购 Agent 漏洞被网信办罚 **280 万元**

---

## 10. 实践建议：企业落地的"先做哪些"

按 ROI 和紧迫性排序：

### 第一优先级（必做）
1. **建立 Agent 资产清单**：哪些 Agent 在跑？谁拥有？访问什么数据？
2. **为每个 Agent 分配独立身份**：禁止"借用用户权限"
3. **实施最小代理权限（Least Agency）**：默认拒绝，按需授权
4. **关键操作设置终止开关**：Global Revocation 能力

### 第二优先级（建议）
5. **L3 工具守卫**：所有 Agent 调用工具走白名单 + schema 校验
6. **L4 执行门**：高风险操作必须人类审批
7. **凭证自动轮换**：避免长期有效 token

### 第三优先级（成熟阶段）
8. **L6 红队门禁**：固定样本库 + CI 阻断
9. **MCP 协议加固**：服务鉴权 + 描述完整性校验
10. **跨 Agent 委托链审计**：可追溯的 Sponsor 机制

---

## 11. 信息缺口与待验证

研究过程中识别出以下信息需要在企业落地时进一步验证：

- ⚠️ **AI Agent 在中国市场的实际部署规模**：缺乏权威统计
- ⚠️ **OIDC-A 1.0 标准的最终落地时间**：目前仅是 arXiv 草案
- ⚠️ **不同 Guardrails 工具的横向对比数据**：缺乏统一基准
- ⚠️ **国内大厂 Agent IAM 的具体落地案例**：公开信息有限
- ⚠️ **CausalArmor 在生产环境的实际效果**：仅有论文数据

---

## 12. 参考来源汇总

| 类别 | 来源 | 链接 |
|---|---|---|
| 标准 | OWASP LLM Top 10 2025 | owasp.org |
| 标准 | OWASP GenAI Security Project (ASI01-ASI10) | genai.owasp.org |
| 标准 | MITRE ATLAS | atlas.mitre.org |
| 标准 | NIST AI RMF | nist.gov/itl/ai-risk-management-framework |
| 协议 | OIDC-A 1.0（arXiv:2509.25974） | arxiv.org/abs/2509.25974 |
| 协议 | MCP | modelcontextprotocol.io |
| 协议 | MCP Safety Audit（arXiv:2504.03767） | arxiv.org/abs/2504.03767 |
| 协议 | Enterprise-Grade Security for MCP（arXiv:2504.08623） | arxiv.org/abs/2504.08623 |
| 学术 | EchoLeak（arXiv:2509.10540） | arxiv.org/abs/2509.10540 |
| 学术 | CausalArmor（arXiv:2602.07918v1） | arxiv.org/abs/2602.07918v1 |
| 学术 | Identity Management for Agentic AI（arXiv:2510.25819） | arxiv.org/abs/2510.25819 |
| 开源 | NVIDIA NeMo Guardrails | github.com/NVIDIA/NeMo-Guardrails |
| 开源 | OpenAI Agents SDK | github.com/openai/openai-agents-python |
| 开源 | 阿里 Qwen3Guard | huggingface.co/Qwen/qwen3guard |
| 开源 | 字节 Coze Studio | github.com/coze-dev/coze-studio |
| 开源 | 阿里 AgentScope | github.com/modelscope/agentscope |
| 商业 | Microsoft Entra Agent ID | learn.microsoft.com/en-us/entra |
| 商业 | AWS Bedrock AgentCore | aws.amazon.com/cn/bedrock |
| 商业 | Google Gemini Enterprise Agent Platform | cloud.google.com |
| 商业 | 腾讯云 AI Agent 安全网关 | cloud.tencent.com |
| 商业 | 阿里云 Agent 安全中心 | aliyun.com |
| 商业 | Okta for AI Agents | okta.com |
| 商业 | Auth0 Auth for GenAI | auth0.com |
| 漏洞 | CVE-2025-49596（MCP Inspector RCE） | nvd.nist.gov |
| 漏洞 | CVE-2025-55241（Microsoft Entra 10.0） | nvd.nist.gov |
| 漏洞 | CVE-2025-32711（EchoLeak） | microsoft.com/security |

---

**报告完成时间**：2026-06-26
**下次更新建议**：每季度更新（OWASP、NIST、主要厂商季度更新较快）
