# Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks

> arXiv: 2601.04603  
> 作者: Hoagy Cunningham, Jerry Wei (Anthropic, equal contribution, 通讯)  
> 提交: 2026-01-08  
> 全文来源: ar5iv 转换版 + arXiv abstract  
> 一手材料路径: `/tmp/p2601-abs.html` (50K) + `/tmp/p2601-ar5iv.html` (181K → 67K 文本)  
> **注意**: 论文 PDF 90s 超时未下,改用 ar5iv.labs.arxiv.org HTML 转换(完整正文 1754 行,所有章节齐全);Table 1 / Figure 2 / Figure 3 数字已从文字描述中提取

---

## 一句话定位

Anthropic **第二代 Constitutional Classifiers** 防御系统,从 2025 Sharma et al. 的版本升级,核心是**三层叠加**:
1. **Exchange classifier**(把 input classifier + output classifier 合并,看 input-output 对)
2. **Two-stage cascade**(轻量 first-stage 筛全部,贵的 second-stage 只筛可疑)
3. **Linear probe ensemble**(在已算好的 model activations 上加 logistic,几乎零成本)

**核心成就**: 在**显著降低 40× 计算开销**和**降低生产流量误拒率到 0.05%**(前代 0.38%)的同时,**1700+ 小时红队**没找到任何能让模型对 8 个 CBRN 目标 query 全部答出 "comparable in detail to undefended model" 的 universal jailbreak。

---

## 1. 背景:上一代 Constitutional Classifiers 的两个失效

论文来自 Anthropic 自身对 2025 Sharma et al. "Constitutional Classifiers" 的**对抗性测试**,找到两类新攻击能绕过:

**(a) Reconstruction attacks**(重组攻击)
- 把 harmful query 拆成多段藏进大 context,然后让模型重组
- 示例: codebase 里的函数 `a()="How"`、`b()="to"`、`c()="synthesize"`、`d()="dangerous"`、`e()="substances"`,用户让模型把 `a+b+c+d+e` 重组并回答

**(b) Output obfuscation attacks**(输出混淆)
- 让模型把回答写成"谜语"或不可直读形式,绕过只看 output 的 classifier
- 示例: 让模型用"winter's breath"=CO₂、"sun's fire"=heat、"sea's gift"=salt 之类的隐喻表达

论文原话:
> "These attacks tend to harm model capabilities, but they can still elicit detailed harmful responses."

→ 关键观察: **last-gen 系统 input classifier 和 output classifier 各看各的**,不看"配对" → 重组攻击有机可乘。

---

## 2. Section 3: Exchange Classifier(解决攻击 #1)

**核心改动**: 用 **一个 classifier** 看 **input + 正在生成的 output** 的配对,而不是 input-only + output-only 两个分开。

具体机制:
- 收到 prompt 后先独立评估 input(像 input classifier 一样)
- 然后在 generation 过程中**按 token batch 连续评估 output 在 input context 下的 harmful 程度**
- 边生成边拦,不用等生成完

**Why it works**(论文自述):
- "Reconstruction attacks 往往在 model 开始 response 后变得可检测,因为 fragments 一旦按 prompt 重组,和原始 harmful query 在 embeddings 上就 align 了"
- "Output obfuscation 也因为 classifier 看到 input 后对'答非所问/绕弯子'模式更敏感而更容易识别"

**实现细节**:
- 直接 fine-tune **Claude Haiku 3.5** 作为 exchange classifier
- 训练数据 = Sharma et al. 同一套 synthetic CBRN 数据
- 阈值 calibrate 到 WildChat **0.1% refusal rate**
- **代价**: 比 last-gen(input + output-only 两个)贵 **50%**(一个 Haiku 跑全 exchange vs 两个小 classifier 分工)

**Robustness 数据**:
- Last-gen: 695K red-team queries 找到 13 个 high-risk vulnerabilities → **0.01871 / 1000 queries**
- Exchange: 数字未在本段直接给出但 Table 1 写 **0.00885 / 1000 queries**(降到 ~52%)
- **Limitation**: expert red-teamers 在 bounty program **外** 还是能发现 universal jailbreaks,虽然需要 substantial effort + automated tools

---

## 3. Section 4: Two-Stage Cascade(降本)

**核心改动**: exchange classifier 贵 50%,加一层 lightweight first-stage 预筛。

机制:
- **Stage 1**: 一个 **~1/3 大小/成本** 的模型筛所有 exchanges
- **Stage 2**: 当 Stage 1 flag(不是 refuse,只是 escalate)时,才调 exchange classifier
- **关键**: flag ≠ refuse。flagged exchange 仍要过 Stage 2 才最终决定

→ 这给 Stage 1 的"高 false positive 率"留了 buffer — Stage 1 宁可多 flag,Stage 2 严判

**实现**:
- Stage 1: 内部小模型,~1/3 size/cost of Stage 2
- Stage 2: fine-tuned Claude **Haiku 4.5** (升级到 4.5)
- 保护: Claude **Opus 4**
- 阈值: Stage 2 calibrate 到 0.1% WildChat refusal
- 第一阶段 flag 流量约 10% 进入 Stage 2

**Robustness 数据**:
- 569K queries 找到 5 个 high-risk → **0.00878 / 1000 queries**(几乎和单独 exchange classifier 一样强)
- **计算开销下降**:
  - 比单 exchange classifier 降 **5.4×**(pipeline 优化 + 模型升级)
  - 仅升级 Stage 2 (Haiku 3.5 → 4.5) 单独贡献 **3×**
  - 相对 last-gen: 27.8% compute(在 Table 1 数字)

**Limitation**(论文承认):
- "Expert-level red-teamers **outside our bounty program** were nonetheless able to discover universal jailbreaks for this system, though this required substantial effort and automated tools."
- 内部 bounty 受控环境 vs 真实外部专家仍存在 gap

---

## 4. Section 5: Linear Probe Classifier(更进一步降本)

**核心思想**: **复用主模型 generation 时的 activations**,加一个 logistic-style linear probe,**几乎零额外算力**就能实时分类。

> "Linear probes offer substantial computational advantages over external classifiers."
> "Such a probe requires 2Ld ≈ 377K FLOPs per token. By contrast, a single forward pass for one token through Gemma 3 4B requires approximately 2N ≈ 8B FLOPs... The probe is thus several orders of magnitude cheaper than a small external classifier, rendering its marginal cost for per-token prediction effectively zero."

### 4.1 关键训练技巧(两个 ablation 都重要)

**(a) Sliding Window Mean (SWiM) Logit Smoothing**
- 训练时对 logit 做 **M token sliding window 平均**:
  - $\bar{z}_t = \frac{1}{M}\sum_{k=0}^{M-1}[W^\top \psi_{t-k}(x_{1:t-k}) + b]$
- 推理时换成 **EMA**(Exponential Moving Average,只存一个标量状态,streaming 友好)
- **作用**: 避免"单个 token 偶然高激活"误判整个 sequence

**(b) Softmax-Weighted Loss**
- 损失函数:
  - $\mathcal{L} = \sum_{t=M}^{T_i} w_t \cdot \mathcal{L}_{BCE}(y, \sigma(\bar{z}_t))$
  - $w_t = \frac{\exp(\bar{z}_t/\tau)}{\sum_{t'} \exp(\bar{z}_{t'}/\tau)}$
- $\tau \to 0$: loss 集中在"最 confident harmful"的 token 位置
- $\tau \to \infty$: 所有位置等权
- **不对称性论证**(论文讲得最细的): 对**无害 prefix 后接有害内容**这种情况:
  - 标准 BCE 会被无害 prefix 的 token 拉低(harm 概率 ~0.5)
  - softmax weighting 给**负 logit(预测无害)的 token 几乎零权重**,只聚焦正 logit
  - 论文:"any confident harmful prediction in a harmless sequence would receive high weight, reflecting how a single flag blocks all subsequent content for streaming classification" — false positive 严惩符合 streaming 部署实际

### 4.2 Ablation 结果(Figure 2)

| 配置 | Attack Success Rate(越低越好) |
|------|------|
| 既不 smooth 也不 softmax weight | 最差 |
| 仅 softmax weight 或仅 smoothing | 各自有提升 |
| **两者结合** | **最好** |

**Layer 选择**(Figure 2c):
- 用**所有层**(all-layer) ≈ 1.4% ASR — 最低
- 用更少层 → 性能单调下降

### 4.3 Probe vs External Classifier

- Probe(基于 Sonnet 4 的全层 activations): ASR **优于 extra-small classifier,几乎匹配 Haiku 4.5 small classifier**
- **Limitation**: probe 在 benign 学术请求上 false positive 率**更高**(论文原话: "we found the flag rate on benign scientific requests was higher for the probe") — 这就是为什么 probe 适合做**第一阶段**,把可疑流量 escalate 给更准的 external classifier

### 4.4 Probe + External Classifier Ensemble(Figure 3)

- 加权: $z_{ensemble} = \alpha z_1 + (1-\alpha) z_2$,$\alpha$ 在测试集上优化
- **关键发现**(Figure 3a): probe + small classifier 的 ensemble **ASR 最低**,**比两个 external classifier ensemble 还好**
- Figure 3b 解释: probe 和 small external classifier 之间的 **Spearman rank correlation 较低**(错误更独立,ensemble 更有价值)
- **equal weighting ($\alpha=0.5$) 接近最优**

### 4.5 Probe-Classifier Cascade(Figure 3c)

- Stage 1: probe(连续跑)
- Stage 2: 仅在 probe flag 时调 small classifier
- **比 single exchange classifier 100× compute reduction,同时 robustness 超 small classifier 单独**

---

## 5. Section 6: Production-Grade 完整系统

**架构**:
- **Stage 1**: linear probe on **Claude Sonnet 4.5** activations(连续,所有 exchange)
- **Stage 2**: fine-tuned Constitutional Classifier on Claude **Haiku 4.5**
- **Ensemble weight**:**0.55 probe + 0.45 classifier**(从测试集优化得到,**不等于** Section 5 里 equal weighting 最优 — 部署版略偏 probe 一点,可能因 probe 在真实流量 false positive 略高)
- 保护对象: **Claude Sonnet 4.5**

**Shadow deployment 数据**(2025-12-01 到 2026-01-01,Sonnet 4.5):
- **Flag rate = 0.05%**(生产流量,比 Sharma 2025 的 0.38% 降 **7.6×**)
- **Stage 1 → Stage 2 escalate 率 ≈ 5.5%**
- **Compute overhead**: 相对 Section 4 two-stage 降 **8×**,相对 Section 3 single exchange classifier 降 **40×**

**Robustness red-team**:
- **198K attempts,~1736 cumulative hours**(5-minute buckets 估计)
- 只发现 **1 个 high-risk vulnerability** → **0.00505 / 1000 queries**
- 论文强调: "**no attack on this system successfully elicited responses to all eight target queries comparable in detail to an undefended model**"

---

## 6. Table 1: 系统总览(全文最关键的对比表)

| 系统 | 相对 Compute Overhead (%) | High-Risk Vulnerability Rate (per 1000 queries) | Production Refusal Rate (%) |
|------|------|------|------|
| **Last Generation** (Sharma 2025) | 100.0% | 0.01871 | 0.073 |
| **Exchange Classifier** (Section 3) | 150.0% | 0.00885 | 0.038 |
| **Two-Stage Cascade** (Section 4) | 27.8% | 0.00878 | 0.036 |
| **Production Grade** (Section 6) | ~3.5% (8× from 27.8) | **0.00505** | 0.050 |

注: production grade 的相对 compute 数字 Table 1 没直接给百分比,但论文说"约 8× 比 two-stage 降",所以 = 27.8/8 ≈ 3.5%,也对应"比 single exchange 40× 降" = 150/40 ≈ 3.75% — 一致。

**关键 takeaway**:
- Robustness(vulnerability rate)从 0.01871 → 0.00505,**降 3.7×**
- Compute 从 100% → ~3.5%,**降 ~28×**(论文 headline 说 40× 是比 single exchange)
- Production refusal rate 从 0.073% → 0.050%,**降 ~30%**(注: 这个比 Sharma 2025 paper 报的 0.38% 低很多是因为 Sharma paper 是 older 报告期)

---

## 7. Related Work(论文里有意义的对比)

- **OpenAI(2025a, 2025b)**: 也是 two-stage,但 **Stage 1 是 topic filter**(检测是否涉及 biology/敏感领域),Stage 2 才做具体 harm classification。论文承认 OpenAI 的 Stage 1 关注"topic"而非"jailbreak" — 路线不同但 spirit 类似
- **Cunningham et al. 2025**(Anthropic 之前的工作): 探索 internals-based classifiers,focus 在 last-N layer networks;本文是**单层 linear probe + weighted loss + logit smoothing** 的简化路线
- **McKenzie et al. 2025**: 也用 softmax-weighted probes + classifier cascade,但**只做 sequence-level 单次预测**;本文是**streaming continuous prediction**
- **HybridLLM / AutoMix / Rabanser 2025**: 都是 cascades / model routers 路线,本文是 "straightforward two-stage" + 用 human red-teaming 验证

---

## 8. 论文自陈的 Future Work

1. **Tighter integration between classifier and LLM**: 把 classifier signal 融进 model sampling 过程(不只是事后拦)
2. **Training models to better resist obfuscation**: 训练阶段就让模型对 obfuscated 表达保持 aligned
3. **More representative production data**: classifier 训练数据更贴近真实流量
4. **Targeted solutions to false positives**: 0.05% 仍有优化空间

---

## 9. 关键 takeaway(给做 agent / 防御的人)

1. **Defense in depth,三层独立工作**:
   - Exchange classifier(input-output 配对看)解决重组 / 混淆攻击
   - Two-stage cascade(轻量预筛 + 贵重判)解决成本
   - Linear probe(基于 model 自身 activations)几乎零成本
2. **Streaming classification 的关键技巧**:
   - Sliding window logit smoothing 防单 token 误判
   - **Softmax-weighted loss** 对 false positive **极严惩**(因 streaming 中 single flag 就 block 后续全部内容)
3. **"Universal jailbreak" 的实际门槛极高**:1700 小时人类红队 + 198K attempts 才 1 个 high-risk;但 "expert outside bounty" 仍能成功(论文承认)— **完全防御不存在**
4. **Probe + External ensemble 比 External + External 强**: 因 error correlation 低(Figure 3b)
5. **production-grade 系统的真实生产数据**: Sonnet 4.5 shadow deployment 一个月,refusal rate 0.05% 是**真生产数据**而非 benchmark 估计
6. **AI R&D 角度**: 这是 Anthropic 公开的 "defense" 论文线;Opus 4.6 system card 的 agentic safety 章节(我之前抓过)对应的是 **prompt injection 防御层**,而 Constitutional Classifiers 对应 **output safety 防御层**。两者不重叠,合起来才形成完整"agent safety"防御

---

## 10. 已知局限(我的)

- **PDF 没下下来**(90s 超时),用 ar5iv 转换版替代。**ar5iv 转换有时会破坏数学公式 layout**(论文里 5 个核心公式我都看到但显示为转义形式如 `\mathcal{D}=\{(x^{(i)},y^{(i)})\}_{i=1}^{N}`,不是 LaTeX rendered)
- **Figure 2 / Figure 3 的图我看不到**,所有数字从文字描述里抠
- **Appendix B/C/D/E/F 内容**没全读(主要 ablation 在 Appendix A,Section 5 已覆盖核心;Appendix B/C/D/E/F 是 datasets、classifier training、red-team 协议等补充,论文主线外的)
- **arXiv id "2601.04603"** 用了未来日期(2026 年 1 月),Anthropic 是 2026-01-08 提交,符合"近期 2026 paper"语境

## 11. 报告方法

- 抓 abstract: `curl https://arxiv.org/abs/2601.04603` → 50K HTML → 提取 abstract
- 抓全文(替代 PDF): `curl https://ar5iv.labs.arxiv.org/html/2601.04603` → 181K HTML → 67K 纯文本(1754 行)
- PDF 直下: `curl https://arxiv.org/pdf/2601.04603` 90s 超时,放弃
- 论文结构由 `ar5iv` 提供,内容主要 Section 1-6,Appendix 没全读
- Table 1 数字从文字描述中精确提取,Figure 2/3 描述引用自 Section 5/6 文字
