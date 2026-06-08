---
type: source
source-type: slide
title: "邢俊威_Coding Agent 重塑软件开发工作"
path: slides/邢俊威_Coding Agent 重塑软件开发工作.pdf
source-md5: dcae15e15b0a1a56071e37ebad008429
size: 6708 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 邢俊威_Coding Agent 重塑软件开发工作

> Ingested from `slides/邢俊威_Coding Agent 重塑软件开发工作.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.55 MB.

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

Coding Agent 重塑软件开发工作
百度工程效能部 邢俊威

## Page 7

目 录 CONTENTS
    AI编码发展历程
    Comate 编码智能体搭建
    Comate 上下文引擎设计
        企业落地实践

## Page 8

_(no text content on this page)_

## Page 9

AI编码产品发展历程

推出Copilot，免费公测

                             ChatGPT正式发布，AI编码助手成为行业关注焦点

                             文心快码百度内全面落地，2023年10月24日正式对外发。
Copilot高歌猛进，与OpenAI各类模型深度整合
Codeium推出，率先支持私有化、VPC多种部署模型                        腾讯云AI助手      通义灵码  Trae

Augment推出，主打大体积代码知识增强                              CodeBuddy    CodeGeeX
Cursor首家构建AI原生IDE            2024

                                                   文心快码3.0在2024年11月正式发布，全系标配智能体。
                     文心快码持续进化中
                         4月：正式发布全自动编码智能体Zulu       2025        Claude Code
                         6月：正式发布AI IDE                 OpenAI Codex
                         7月：推出Zulu CLI
                         8月：自定义智能体、Todo List、Plan模式
                         9月：多智能体协同
                     •   10月：智能体SPEC模式

## Page 10

AI编码产品形态变迁
Copilot、Chat&RAG、Agent

    AI代码生成占比 和 采纳率的变化趋势
    Agent    5% 15%  10% 25%  30+% 35%  50% 80%


Chat       •       理解意图、拆解任务、
           •       调用工具、自动执行、
           •       自我纠错

Completion 项目问答：理解并推理具体代码
    •     通识问答：通用知识


    编辑预测：预测下一步可能修改的位置
    代码改写：一定范围内智能识别、修改
•   代码续写：光标之后进行单行、多行补全 2022 2023 2024 2025

## Page 11

百度落地AI编码效果

 Comate在百度大规模落地，效果显著，推进研发进入人机协同时代

 百度全局提效（2024）        百度内部使用效果（2025）
 12%             85%+
                 工程师使用  52%+       73%+
                     AI代码生成占比      智能体活跃用户
                 90%+              AI代码生成占比
                 用户满意度

## Page 12

   核心能力
Agent工程
                        可控、可执行、多工具协作的任务型智能
                        体体系，实现从“智能回答”到“自动完
                        成任务”。

       上下文工程
  解决企业级编码中的信息理解问题，提供
  准确、结构化、动态的工程上下文供模型                      人机协同方案
  决策。                                     明确的分工机制与流畅的交互方式，实
                                          现智能体与开发者高效协同。

## Page 13

_(no text content on this page)_

## Page 14

文心快码智能体架构
               用户需求

     上下文系统
 用户知识    工程感知  任务规划系统  垂类智能体

                   工具系统
 记忆系统          LLM       读取文件
 当期记忆                    编辑文件
 近期记忆          工具调用      检索代码
 长期记忆                    执行命令
               完成任务        ……

## Page 15

        用户    需要客户端执行的工具：     需要客户端执行的工具：    需要客户端执行的工具：
 客户端 Query    Search、Grep等    Edit、Write等      Run、Debug等
Flow

   Stage 1    Stage 2        Stage 3        Stage 4
      任务分析    代码理解           代码修改      验证测试    组装到
                                            Prompt中的
 服务端                                           工具
Flow

                                                                     Tools
                         工具调用模型    组装prompt        codebase_search  grep_search     list_dir
                                     工具调用链         read_code_block   read_file      run_command
                         文件编辑模型     需要服务端执         write_file        edit_file      delete_file
                                     行的工具
      Code Search Vector                           relate_files     find_by_name    ...

## Page 16

   文心快码智能体能力层级

•   基础能力：核心引擎，感
    知、计划、决策、执行
•   定制能力：定制拓展
•   策略层：多Agent系统隔
    离、共享策略设计
•   企业定制：为企业特定业
    务需求打造的专属智能体
    解决方案

## Page 17

文心快码多Agent系统协作策略
     层级隔离

     变色龙




     记忆解耦，避免记忆污染与占用
     更加专注，注意力更强
 •   不同角度判断，准确度更高

## Page 18

完整效果展示

## Page 19

_(no text content on this page)_

## Page 20

挑战                           解法
•   信息过载：现代代码库规模庞大，远超上下文     •   最优上下文选择：在容量受限的条件下，确保模
    窗口容量，经过精心筛选与裁剪后才能投喂给         型在恰当时刻获取最关键、最有价值的信息。
    模型。                      •   精准语义理解：既能正确解析用户显性指令，也
•   指令模糊：用户常常只会给出不完整的请求，         能把握隐含的需求与期待。
    例如“优化登录逻辑”。              •   预生成知识：主动整理和组织代码相关的核心信
                                 息，使其成为智能体可直接调用的优质上下文。
•   隐性期待：即使用户未明确表达，也期待智能
    体遵循编码规范、保持代码库的风格一致、尽
    可能复用已有逻辑，而不是“推倒重来”。
        生成效果为先，企业场景友好
        只有在真实、复杂的企业环境中证明其价值，AI编码工具才能真正落地

## Page 21

   上下文工程 & 知识工程

知识工程 - 沉淀的成果
•  结构化：索引、摘要、依赖等整理
•  语义映射：术语、约定的统一理解
•  知识沉淀：预生成内容转化为可管理资产


上下文工程 - Agent即时使用
•   语义对齐：把用户需求和代码库内容
    精确匹配
•   动态筛选：限窗高密度表达，动态选
    择最有价值的上下文
•   预生成结合：更快、更准、更智能

## Page 22

上下文引擎系统架构

## Page 23

代码库术语理解

## Page 24

   上下文引擎的代码库理解能力
Query：秒杀是如何实现的？

使用模型生成关键词
•   关键词错误，前几轮检索无有效信息
•   读取文件之后，在第3轮找到方向
•   最终生成答案没有覆盖全部逻辑

使用代码库术语
•   关键词准确，第1轮就识别到主要逻辑
    文件（从控制层到服务层）
•   分析文件内容后不断填充      使用模型生成关键词
•   最终生成答案全面详实
        使用代码库术语

## Page 25

代码库检索工具

## Page 26

 上下文引擎的代码库阅读效率
Query：增加一个功能，
物车。          支持用户把某个已完成历史订单中的所有商品再次加入购
     以简化用户操作，
             提升复购率。

 两次代码库语义检索：
 1. 在哪里处理订单详情查询和购物
  车添加商品的逻辑？
 2. OmsCartItemService是如何实
  现添加商品到购物车的？

## Page 27

    代码库WiKi生成

智能体基于最新、可信的知识工作

•   自然语言友好：提供清晰描述，提升智能
    体理解与生成效率
•   保持一致性：文档与代码实时绑定，避免
    信息滞后
•   系统化资产：覆盖架构、模块、配置、接
    口等文档，形成可持续更新的知识库

## Page 28

    知识体系工程


        知识结构化          知识管理            知识理解      知识应用

知识建模，构建工程化 统计组织与治理知识工程， 让知识具备语义与上下文 赋能工程师与智能体的智
    基础数据：       工具、机制支持知识持续     能力：          能协作：
    •   API     更新：             •   架构理解     •   DeepResearchAgent
    •   调用链     •   版本管理        •   结构识别     •   Sub Agent of
    •   图谱      •   合并/更新       •   模块摘要         CodingAgent
    •   数据流     •   统一组织        •   术语读取

## Page 29

_(no text content on this page)_

## Page 30

    Rules：研发经验传承与进化

        信息类          指令类

•   编程语言、技术栈、关键三方    • 实现任务的确定性步骤
    依赖               • 支持任务实现的重要信息的获取
•   业务名词与代码命名映射关系    方法
•   模块/目录划分，各模块作用    • 相关文件修改的代码示例
•   核心代码、可复用部件的位置    • 全过程的验证点，验证方式

        约束类            索引类

• 按Workflow需要的具体行为   • 统一的读取、激活Rule的行为准
• 不期望进行的执行、调用等行为     则声明
• 受安全等约束禁止访问或修改的     • 每一个Rule包含的内容、激活场
   文件                景、前置条件
• 希望模型扩展任务流程的方式      • 避免Rule重复阅读的约束型要求
                     • 子Rule如果事后激活，强调需要
                     回溯检查

## Page 31

Spec-Driven: Vibe Coding成为可能

在AI主导的情况下，如何让工程师更有效的参与，从而更加务实，可控，白盒化，有效解决实际软件工程
问题，提升研发效果

 需求设计               技术设计             任务拆解
 需求背景               系统架构             涉及文件
 描述需求的来源和业务价值。      展示模块划分与交互关系。     改动涉及的文件/模块/函数
 用户故事               技术选型             目标说明
 描述用户视角的功能需求。       明确技术栈及选型理由。      每步目标与预期结果说明。
 验收标准               实现细节             执行过程
 定义功能完成的量化指标，如性     文件结构、依赖配置等       详细执行过程，而非高层级的抽
 能、兼容性要求。                            象概念

## Page 32

AI Coding组织提效洞察
    衡量组织效率，指引组织落地
    采纳率、AI代码生成占比的实时跟踪

               按照组织、个人查看详细内容

               查看各个语言、功能使用情况

## Page 33

赋能千行百业

## Page 34

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/邢俊威_Coding Agent 重塑软件开发工作.pdf]]`
