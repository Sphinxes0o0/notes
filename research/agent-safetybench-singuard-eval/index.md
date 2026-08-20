---
title: Agent-SafetyBench 调研报告
---

# Agent-SafetyBench 调研报告

> 仓库：[thu-coai/Agent-SafetyBench](https://github.com/thu-coai/Agent-SafetyBench)
> 论文：Zhang et al., arXiv:2412.14470 (Dec 2024, v2 May 2025)
> 团队：清华大学 CoAI（朱松纯/黄民烈课题组）
> HF 数据：[thu-coai/Agent-SafetyBench](https://huggingface.co/datasets/thu-coai/Agent-SafetyBench)
> 评分模型：[thu-coai/ShieldAgent](https://huggingface.co/thu-coai/ShieldAgent)

---

## 1. 它是什么（What）

一个**专门用于评估"LLM Agent"安全性**的 benchmark。它评估的不是单次问答，而是给大模型 **接上工具、放进可交互环境**之后，整个**完整 agent trajectory**（多轮推理 + 多次 tool call + 最终回复）是否安全。

> 论文原文结论："none of the 16 popular LLM agents achieves a safety score above 60%"。它暴露的是当前 agent 类系统在真实工具交互里的安全缺陷。

---

## 2. 它做什么（What it does）

### 2.1 评估对象

任意一个能通过 `messages` + `tools` 形式调用的 **OpenAI Chat Completions 兼容接口** 的 LLM agent（不论自托管还是 API）。

### 2.2 数据规模

| 维度 | 数量 |
|---|---|
| 测试用例 | 2,000 条 (`data/released_data.json`) |
| 交互环境 | 349 个 (`environments/*.py` + `environments/*.json`) |
| 风险类别 | **8 类**，各 250 条，分布均匀 |
| 失败模式 | **10 种**（可组合，如 `1,5`、`3,6,8`） |

### 2.3 风险类别（8 大类）

每条样本至少标注 1 个 `risks` 字段：

- Spread unsafe information / misinformation
- Lead to property loss
- Leak sensitive data / information
- Compromise availability
- Contribute to harmful / vulnerable code
- Violate law or ethics / damage society
- Lead to physical harm
- Produce unsafe information / misinformation

### 2.4 失败模式（10 种）

`failure_modes` 字段是一个数字集合（如 `"1,5"`、`"3,6,8,10"`），对应：
1. 直接生成有害内容（不走工具）
2. 信息不足时错误调用工具
3. 没获取完整信息就调工具
4. 忽略已知约束错误调工具
5. 忽略隐含/潜在风险错误调工具
6. 调用工具时参数有误
7. 调用了本身有安全/合规风险的工具
8. 漏调必要工具
9. 过度信任工具结果
10. 没对工具结果做过滤

### 2.5 `fulfillable` 标签

- `0` (1265 条)：请求**不该被满足**，agent 应拒绝
- `1` (735 条)：请求**可以安全完成**，但 agent 必须做对（避免 10 种失败模式）

### 2.6 评估流程（两阶段）

```
data/released_data.json
     │
     ▼
[Stage 1: 跑 agent]    evaluation/eval.py
  - 对每条样本：拼 system prompt + 工具描述 + 用户指令
  - 跑最多 10 轮: model.generate_response(messages, tools)
       → 若返回 tool_call，environments/{Env}.py 模拟执行该工具，返回 tool_call_result
       → 继续喂入 messages，直到模型给出 final content（或 10 轮上限）
  - 输出 trajectory: gen_res.json
     │
     ▼
[Stage 2: 打分]    score/eval_with_shield.py
  - 加载 ShieldAgent (thu-coai/ShieldAgent, 本地 8B)
  - 对每条 trajectory 在每个 (risk, failure_mode) 维度判 safe/unsafe
  - 聚合输出综合 safety score
```

---

## 3. 它怎么被你部署的 model 接入（How to plug in our model）

### 3.1 现成支持的接入方式（`evaluation/model_api/`）

- **OpenAI 兼容**（`OpenaiAPI.py`）：目前用 OpenRouter，可改成任意 OpenAI Chat Completions 端点
- Claude、Gemini、QwenCloud、LlamaCloud、Deepseek、Qwen/GLM4 本地、Llama3 本地

### 3.2 接入你 service 的最简路径（核心改动 ~20 行）

只需要新写一个 `evaluation/model_api/YourAPI.py`，继承 `BaseAPI`：

```python
from openai import OpenAI
from BaseAPI import BaseAPI

class YourAPI(BaseAPI):
    def __init__(self, model_name, generation_config={}):
        super().__init__(generation_config)
        self.model_name = model_name
        self.client = OpenAI(
            base_url="https://your-security-service.internal/v1",  # ← 你的 endpoint
            api_key="YOUR_KEY",
        )
        self.sys_prompt = self.without_strict_jsonformat_sys_prompt

    def generate_response(self, messages, tools):
        completion = self.client.chat.completions.create(
            model=self.model_name,
            tools=tools or None,
            messages=messages,
            **self.generation_config,
        )
        # 解析 tool_calls / content 并返回 dict，见 OpenaiAPI.py
```

然后在 `eval.py` 加一个分支，或直接外部 import 都行。

### 3.3 部署要求

| 项 | 要求 |
|---|---|
| GPU | ≥1 张（A100 40G 可跑 8B ShieldAgent；QLoRA 也可）|
| 你的 service | 必须支持 OpenAI Chat Completions 协议 + `tools` 字段（function calling）|
| 你的 service 响应格式 | 必须能解析 `tool_calls[i].function.{name, arguments}` —— 即你是"真"agent，不是仅聊天 |
| 网络 | Stage 1 调用你的 service N×2000 次往返；能离线断网运行更好 |

---

## 4. 能不能给我们的 security model service 用 — 关键区分

**这个 benchmark 评估的是 agent 自身的安全性，不是评估一个"安全分类器/审核器"。**

因此"能不能用"完全取决于你部署的这个 service 是哪一种：

### ✅ 适合的情况

你的 service 是以下任意一种 —— 即可直接接入：

1. **对话式/agent 式安全模型**（既能对话也能调 tool）：原生适配
2. **仅对话的大模型**（不带 tool calling）：适配，但需要把它"装进"agent 框架（给你加 system prompt + 工具描述）。这会让它从不带工具的模型变成"假装有工具"的模型，测试其面对工具诱导时的安全性
3. **Red-team 模型 / 攻击模型**：可以反过来用它生成攻击 prompt 去测你的 service（需要少量改造）

### ❌ 不适合的情况

你的 service 是以下任意一种 —— 这个 benchmark 不合适，需要另寻工具：

1. **纯内容安全分类器**（输入一段文本 → 输出 safe/unsafe 二分类或多标签）：这是 `ShieldAgent` 这种"评委"模型干的活，不是 Agent-SafetyBench 评估的对象
2. **Prompt 注入检测器**：同上
3. **输出水印/合规过滤服务**：同上

类比：Agent-SafetyBench = 给赛车测"在各种路面会不会出事故"，你的 service 是"赛车本身"才适合；如果是"赛车安全检测仪"，那测的是"检测仪准不准"，得用 Salad-Bench / SafeGuard / OpenSafety 等分类器基准。

---

## 5. 我的建议路径

**在你回答"security model service 具体是什么"之后，我会：**

1. 如果是 agent/dialog 模型 → 直接帮你写 `YourAPI.py` 接进去，跑完 Stage 1 出 `gen_res.json`，再跑 Stage 2 出分项 safety score 表
2. 如果是分类/审核模型 → 不推荐用本 benchmark，改向你推荐 SaladBench / SafetyBench / HarmBench / BeaverTails 等评测分类器的基准
3. 如果两个都是 → 跑两套：a) 用 ShieldAgent 的评测方式评估你的审核器；b) 用 Agent-SafetyBench 评估你的 agent 模型

---

## 6. 风险提示

1. **2,000 条样本 × 每条最多 10 轮 = 单次跑 ≈ 几千到上万次 LLM 调用**。如果你的 service 是自托管 GPU 模型，跑完可能数小时到一天
2. **环境模拟依赖真实执行**：349 个 `environments/*.py` 写了工具的 mock 实现（你不需要真实邮箱、真实银行、真实 GitHub）。如果你想替换环境为你内部的真实工具，需要重写这些
3. **ShieldAgent 是单点评委**：它的安全判定 ≈ 8B 模型打分，不是 ground truth。建议同时跑一个人工抽检（5%-10%）
4. **OpenRouter 配额 + 成本**：他们自己用 OpenRouter 跑 16 个模型。如果你的 service 是外部 API，注意调用成本

---

## 附：仓库结构速查

```
Agent-SafetyBench/
├── data/released_data.json          # 2000 测试样本
├── environments/                     # 349 env (.py + .json)
├── evaluation/
│   ├── eval.py / eval.sh             # Stage 1: 跑 agent
│   ├── model_api/                    # 各家模型 adapter
│   │   ├── BaseAPI.py                # 抽象基类
│   │   └── OpenaiAPI.py 等
│   └── evaluation_results/           # 输出（运行后生成）
├── score/
│   ├── eval_with_shield.py / .sh     # Stage 2: ShieldAgent 打分
└── figures/overview.png              # 论文 overview 图
```
