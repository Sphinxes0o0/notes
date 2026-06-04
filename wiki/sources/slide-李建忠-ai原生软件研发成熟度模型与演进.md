---
type: source
source-type: slide
title: "李建忠_AI原生软件研发成熟度模型与演进"
path: slides/李建忠_AI原生软件研发成熟度模型与演进.pdf
source-md5: bd53de2987a651f3f1d9308b10464817
size: 6513 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 李建忠_AI原生软件研发成熟度模型与演进

> Ingested from `slides/李建忠_AI原生软件研发成熟度模型与演进.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.36 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

AI原生软件研发成熟度模型与演进

李建忠
奇点智能研究院 / CSDN

## Page 7

软件领域的每一次范式革命，
既改变软件应用形态，
也改变软件开发方式

## Page 8

  AI 为软件带来什么样的改变？

    互联网                 人工智能

  软件应用形态  Web软件         智能体
        （HTML/CSS/JS）  AI Agent

软件开发方式 云原生软件开发 AI原生软件开发
        Cloud Native    AI Native

## Page 9

AI应用形态：智能体

## Page 10

AI时代的应用形态：智能体Agent



  桌面软件  网页  App  Agent

  PC    互联网  移动互联网 智能时代

## Page 11

智能体的能力成熟度阶梯

    行动     Action
    （bit/atom)
    记忆     Memory
    (long memory)
    协作     A2A
工具      MCP (Agent to Agent)
    (Model Context Protocol)
规划  Reasoning
    (Reinforcement learning)

## Page 12

从训练模型到推理模型

训练模型      预训练  后训练

      快思考      慢思考

推理模型      预训练  后训练  推理

      “讲知识”    “讲文明”  “讲道理”

## Page 13

MCP (Model Context Protocol)

MCP是“图灵-冯诺伊曼架构”与
“神经网络计算架构”之间的桥梁

Model Context Protocol (模型上下文协议) 是一种标准化的通信协议，用于在 AI Agent 和模型之间高效
传递上下文信息，实现可靠的工具调用。
MCP 对 AI Agent 的重要性
提升上下文理解能力。准确传递历史对话、用户意图和环境信息。避免信息丢失，提高响应准确性
l  增强工具集成。统一管理外部工具调用（API、数据库等），实现无缝的功能扩展
l  优化决策流程。提供完整的决策依据和约束条件，支持复杂的多步骤任务执行
l  改善用户体验。保持对话连贯性，实现个性化和智能化交互

## Page 14

 智能体平台


      智能体平台 Agent Platform
      数据库  MCP        Agent
Web        Tcp    A2A     A2A
服务        传统软     Agent
  Http  API       件/服务  网络  Agent A2A Agent

## Page 15

上下文工程 Context Engineering
      上下文的核心是：注意力
      Attention Is All You Need

 • 上下文（Context）是 Agent 感知和决策的 “环境要素总和”，包括但
  不限于：用户需求、任务目标、场景信息、历史交互、资源约束、规则边
  界等。

 • 上下文工程：通过结构化、动态化的方式，确保 Agent 在正确的时间、
  以正确的方式获取 “正确的信息”，为 Agent 的自主决策、任务执行和
  交互行为提供精准、全面的支撑框架。

## Page 16

智能体管理哲学

    Context, Not Control
    提供上下文，而非控制

  Context 是神经网络架构（语义向量计算）的核心

  Control 是冯诺伊曼架构（比特数字计算）的核心

## Page 17

上下文与记忆

 •  上下文是智能体当前注意力焦点（工作记忆），记忆是 Agent 对过去经历、
    知识和信息的存储和检索（长期记忆）。

 •  上下文是记忆的一部分，记忆为上下文提供补充。记忆不是越多越好，也
    需要适当丢弃（人类遗忘机制）。

 •  多智能体、 不仅仅是协作。智能体一定有其边界，不同上下文、 不同记
    忆， 不同注意力。

 •  未来智能体会逐步演进将记忆内化为模型一部分，自己决定上下文，甚至
    自己做上下文工程。

## Page 18

智能体的执行时长每7个月翻一番

## Page 19

智能体的执行时长要从“从长计议”


  秒级   分钟级  小时级  天级  月级    年级

检索/对话  日常任务  办公任务  项目任务  工程任务  科研任务

  ⼈类从执⾏者转变为监督者和决策者，专注于战略思考和价
  值判断，⽽把具体的执⾏和优化⼯作交给 Agent。

## Page 20

AI原生软件开发

## Page 21

AI原生软件开发 VS. 氛围编程

    AI原生软件开发 氛围编程

  • 追求软件复用性         • 软件即用即抛
  • 遵循传统软件工程原则      • 不再追求传统软件工程
  • 软件成本昂贵          • 软件生产成本极低
  •    企业级大规模软件     • 小型消费级软件
  •    专业软件开发团队     • 普通大众用户

## Page 22

氛围编程 带来 “可塑软件”

      软件未来应该像文档一样可随时编辑”
        ——Alan Kay 面向对象编程之父

 • 氛围编程（ Vibe Coding）将会改变软件的生产和交付方式。
 • 氛围编程有望创造出“可塑软件（Malleable Software）” 支持
  用户对软件进行二次加工、个性化定制体验/功能。
 • 不要使用传统软件工程的观念来看待氛围编程。

## Page 23

  颠覆式创新的核心特征


   大规模 个性化 低成本
   Massive Personalize Low Cost

• 氛围编程（Vibe Coding）面向大众用户、使用“自然语言编程”
 来实现软件创造的平权时代。
• 就像互联网时代的Web前端编程，氛围编程是增量市场，创造AI时
 代的软件的新范式。

## Page 24

软件工程的本质

Programming is not
Software Engineering
编程不是软件工程

The essence of Software
Engineering：“The
multiperson development of
multiversion programs.”
软件工程的本质：管理多人多
版本的开发活动

## Page 25

 传统软件工程的核心命题

   复杂       动态  协作
   性        性   性

“最小化复杂性”是软 随着时间的推移，软件 软件开发不是一个人的
件工程设计领的“第一 系统会不断变化。如何 工作。软件工程强调团
性原理”，需要一整套 支持软件系统的演进适 队的协作和项目管理。
工程设计能力，来提高 应性，“拥抱变化”是 团队成员需要协作来实
开发效率和软件质量。 软件工程的重要课题。 现软件的目标。

## Page 26

  AI 原生软件开发 如何应对软件工程复杂性

  复杂性 • 推理模型提升复杂问题的分解和抽象思维能力


动态性 • 动态上下文、共生数据提升Agent 的演化适应性


协作型 • 多智能体（A2A）+工具协作（MCP）促进迈向更高智能

## Page 27

奇点智能AI原生软件研发成熟度模型 AISMM

路线         最佳        组织
图          实践        流程

AI原生软件研     提炼奇点智    技术、流程与
发成熟度演进      能团队和业    组织必须共同
的路线图        界最佳实践    演进

## Page 28

奇点智能-AI原生软件研发成熟度模型 AISMM V1.0

## Page 29

AI原生软件研发的核心三原则

    知道 看见 执行

 工程师知道的，Agent都 工程师能看见的， 工程师能执行的，
 应该知道 Agent都应该看见 Agent都应该能够执行
 软件研发知识工程 上下文+记忆 Agentic DevOps

## Page 30

    AI原生软件研发成熟度模型 AISMM 阶段

    Level 1  Level 2    Level 3  Level 4 Level 5

 辅助提效 领域集成 代理协同 自主代理 软件工厂
   AI       Domain     Agent   Autonomous Software
Assisted  Integrated  Synergy    Agents Factory


    引入模型和  引入领域   引入Agent 角   引入Agent 团   引入AI自适应
    辅助工具   知识工程   色/任务能力      队/组织能力      创新与交付

## Page 31

AI原生软件研发成熟度模型 AISMM 的要素建设

 1. 基础设施 AI Infrastructure

 2. 知识工程 Knowledge Engineering

 3. 流程工具 Process & Tools

 4. 组织人才 Organization & Talents

 5. 安全治理 Security & Governance

## Page 32

    AI原生软件研发成熟度模型 AISMM 阶段

    Level 1  Level 2    Level 3  Level 4 Level 5

 辅助提效 领域集成 代理协同 自主代理 软件工厂
   AI       Domain     Agent   Autonomous Software
Assisted  Integrated  Synergy    Agents Factory


    引入模型和  引入领域   引入Agent 角   引入Agent 团   引入AI自适应
    辅助工具   知识工程   色/任务能力      队/组织能力      创新与交付

## Page 33

    Level 3     代理协同
                Agent Synergy

    • 构建企业级 AI 平台,支持模型编排和 Agent协作框架。
1.          •   构建基于Agent角色的云沙箱环境，并支持 Agent 的记
     基础设施       忆、工具调用能力。
AI
Infrastru   •   建立统一的可观测性平台监控 Agent   行为、包括稳定性、
cture           性能监控和优化机制等,持续改进 Agent 能力。
    • 部署RAG 架构、知识图谱等高级 AI 基础设施。
    • 建立分布式训练集群和弹性推理服务,实现算力调度和成本优化。

## Page 34

    Level 3    代理协同
        Agent Synergy


    2.     •   逐步建立数据飞轮机制,AI 使用产生的数据与软件工程师反
  知识工程         馈行为数据反哺模型能力。
Knowled • 实现动态上下文工程增强,确保Agent拥有“环境要素总和”。
   ge
Engineer • 构建多层次知识图谱(架构/业务/技术图谱),支持复杂推理。
    ing    •   实现知识的版本控制和溯源,支持知识演化追踪。
           •   建立多模态融合系统,整合文档/图表/对话等多种知识形式。

## Page 35

Claude Agent 的上下文工程实践

• Prompts：提示词，对话中需求的即时表达
• Skills：操作⼿册，可⻓期复⽤的指令、脚本和资源
• Projects：包含知识库和历史记录的「项⽬空间」
• Subagents：专⻔完成某件垂直任务的助⼿
• MCP ： 将 模型 链接外部⼯具和数据源上的 「 连接 层 」

## Page 36

           Skills     Prompts   Projects   Subagents  MCP
核心价值 流程性知识 实时操作指南 背景知识 任务委派 工具链接

   持久性     跨对话        单次对话      项目内        跨会话        持续链接
   包含      指令+脚本+资源   自然语言      文档+上下文     智能体逻辑      工具定义

   何时加载    按需动态加载     每轮对话      项目中总是加     被调用时       总是可用
                                载
   包含代码    可以         不可以       不可以        可以         可以

   最佳场景    专业化技能      快速请求      中心化上下文     专有任务       工具/数据访问

核心价值 流程性知识 实时操作指南 背景知识 任务委派 工具链接

## Page 37

        Level 3    代理协同
               Agent Synergy

        • 研发流程重构为 Agent与工程师 协同完成开发任务。
        • 建设基于角色的多Agent：需求分析 Agent、架构设计
    3.     Agent、  代码生成 Agent、测试 Agent。
流程工具 • 建立Agent和工具调用合约(Tool Use/MCP) 和工作流引擎。
Process • 打通Agent与人协作、与工具协作的堵点，所有需求和流程要能够
& Tools
        变成可被 Agent消费和执行的Spec规约。
        • 人的角色转变为监督者和决策者,处理 Agent无法解决的问题。

## Page 38

AI原生软件开发生命周期中的创新工具










From
A16Z

## Page 39

AI原生软件开发工具生态










From
A16Z

## Page 40

        Level 3        代理协同
                     Agent Synergy

        • 重组为 Agent 协作型组织,围绕人机协作模式重构。
    4.       •   设立 Agent Designer、Agent Orchestrator 等新岗位,
  组织人才           负责 Agent 的设计和编排。
Organiza • 开发人员转型为 Agent监督者和调优师,重点提升
   tion &        Agent 管理能力。
   Talents   •   建立跨职能的AI赋能团队,包括领域专家、AI 工程师、流程设
        计师等。
        • 绩效考核关注人机协作效率和 Agent产出质量。

## Page 41

    组织重构：智能体协同的AI原生软件研发组织
  需求分析     系统设计
  Agent    Agent

   LLM      LLM系统
 Master     工程师
  推动模型
   应用       模型开发
 Prompt     微调RAG
 和Agent     /运维
  部署运维     模型数据工程师    编码开发
  Agent               Agent
收集/清洗/训练
           数据和上下文

  质量测试
  Agent

## Page 42

智能体 Agent 康威定律


  康威定律  智能体康威定律

组织的协作沟通架构  Agent的协作沟通架
 决定系统设计架构  构决定系统设计架构

## Page 43

    Level 3    代理协同
        Agent Synergy


        • 建立完整的 AI 治理体系,覆盖整个 Agent 生命周期。
   5. • 实施细粒度的权限管理,Agent 的操作权限与任务范围严格匹配。
治理安全 • 建立 Agent 行为监控系统,实时检测异常行为和潜在风险。
Governa • 实施自动化合规检查,确保 Agent 输出符合法规和标准。
 nce & • 实施红队测试,主动发现和修复 Agent 安全漏洞。建立多层级
Security 的人工介入机制。

## Page 44

大模型在工程应用中的三大主张

  智能的核 而不是结构化数据/视觉等，语言蕴含推
  心是语言 理，而其他数据则不是

  智能需要 没有一步到位的智能，智能需要在不确定
  迭代收敛 性中，快速迭代、收敛至确定性。

  智能需要 除了强大的预训练知识 和 强化学习推理，
  上下文 智能需要上下文、才能发挥作用。

## Page 45

奇点智能
由CSDN、Boolan联合多家机构发起成立，专注于人工智能前沿技术
和产业落地的创新研究、咨询与智库机构。

愿景与使命
成为人工智能产业的“范式孵化器”，推动 AI 成为普惠性的生产力工具。

研究方向
围绕人工智能带来的三大范式转换：计算范式、开发范式、交互范式展开。

## Page 46

奇点智能六大核心研究领域






智能软件工程与研发效能  AI系统软件技术栈  企业开源软件设计与治理






智能化战略转型与落地  系统软件性能工程与优化  软件架构设计与重构

## Page 47

     谢谢大家！
     欢迎关注公众号，
     共同探索AGI时代的创新机会！
李建忠研思

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/李建忠_AI原生软件研发成熟度模型与演进.pdf]]`
