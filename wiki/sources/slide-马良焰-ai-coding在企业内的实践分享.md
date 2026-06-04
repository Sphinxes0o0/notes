---
type: source
source-type: slide
title: "马良焰_AI Coding在企业内的实践分享"
path: slides/马良焰_AI Coding在企业内的实践分享.pdf
size: 5367 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 马良焰_AI Coding在企业内的实践分享

> Ingested from `slides/马良焰_AI Coding在企业内的实践分享.pdf` via `lit parse` on 2026-06-04.
> Source file: 5.24 MB.

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

美团 AI Coding 实践
演进人： 马良焰
美团/研发质量与效率部

## Page 7

目 录 CONTENTS
    01:  AI Coding 行业发展趋势

    02:  美团 AI Coding 建设情况

    03:  研发范式重塑

    04:  未来展望

## Page 8

_(no text content on this page)_

## Page 9

AI Coding 演进趋势










100%







GitHub Copilot    Cursor


AI 生成的代码占比

## Page 10

AI 代码占比持续提升








    微软                       谷歌                             Meta                          Anthropic

Satya Nadella 在 2025.4 的     Sundar Pichai 在 2025 Q1 财报     Mark Zuckerberg 预测：2026 年     Dario Amodei 2025.3 做出激进预
LlamaCon 活动上表示：“在微软          电话会议上表示：“Google 超过             AI 将承担 50% 的编程工作，并成           测：“3-6 个月内达到 AI 编写
的代码仓库中，目前有 20%–30%           30% 的新增代码由 AI 生成，6 个           为主力开发，未来开发者的角色将               90% 代码的状态，12 个月内我们
的代码由 AI 编写”，且占比仍在            月提升了 5%”                       发生根本性变化                       可能处于 AI 编写所有代码的世
持续提高                                                                                      界”。2025.12 Anthropic 内部称
                                                                                          约“90% 的代码都被 AI touch
                                                                                          （触达）过—也就是参与生成、改
                                                                                          写、review 等环节”

## Page 11

_(no text content on this page)_

## Page 12

    美团 AI Coding 建设情况










    MCopilot 插件         MCopilot 插件升级为 CatPaw 品牌
代码补全、单测生成、Chat 知识问答  产品覆盖 IDE、JetBrains 插件、Xcode 插件
                       Code Agent、Next Edit、上下文工程

## Page 13

产品矩阵










CatPaw 是美团推出的 AI IDE，面向专业程序员，
以 Agent & 人协作为核心，通过 Agent 智能驱
动编程，辅以代码补全、项目预览调试等功能，
结合美团 LongCat 模型，让编码过程更专注，
项目交付更高效。

## Page 14

美团 AI 代码占比已超过 50%

## Page 15

NoCode 使用数据

       3000+     50w+
       持续使用作品    作品月 PV



 30000+  10000+    20+
 创作者     创作者月 UV    覆盖 20+ 岗位序列

## Page 16

Why  do we need NoCode ？

Why  not IDE？

## Page 17

    AI 功能模块


• Next Edit：编码场景，生成补全，下一步预测
• Code Agent：通过对话生成代码
• Review Agent：负责在提交前审查生成后的代码
• Bugfix Agent：根据 Review Agent 生成结果修改代码
• Deploy Agent：负责将代码发布至线下/泳道环境

## Page 18

Next Edit - Tab Tab Tab

    预测下意一图个识编别辑，点多行编辑










LongCat-7B-catpaw-next-edit

## Page 19

Code Agent 设计


 用户交互层  用户发出的指令：Prompt


 上下文层   AI 的眼睛和耳朵：负责收集信息


 决策层    AI 的大脑：进行推理和生成的核心模型


 执行层    AI 的手：负责执行和使用工具


 反馈层    Tool Result、Lint Error、Runtime Error、Browser Result

## Page 20

Agent 架构

客户端                        Web 端 - NoCode

CatPaw IDE    交互渲染     工具拓展        省略 …

JetBrains 插   交互渲染     工具拓展
件
                           Sandbox

                           CatPaw Agent SDK    CatPaw Agent SDK


执行层    工具执行      MCP 调用  Hooks

上下文      代码      Rules    Skills    服务端
                                    业务层    OpenAPI  会话管理 上下文管理

控制层    Loop      会话管理     API       数据层    Blade    Redis    S3

数据层    SqlLite   配置文件     KV

                              MaaS

                              模型注册     模型路由     模型调用     模型配置  向量服务

## Page 21

用户交互层





文本输入区域

    设计稿、图片

指定上下文

## Page 22

上下文管理



•   Codebase 索引 + DeepWiki：让 AI
    具备“全局上下文”能力




•   Docs 文档：给 AI 补充项目知识（SDK
    文档、API 文档等）

## Page 23

上下文管理


 •   Memory：记录对话过程中产生的重要信
     息






 •   Rules 文档：规则、规范和约束

## Page 24

    决策模型

        LongCat-Flash-CatPaw-Coder








    LongCat  +  CatPaw

基于美团自研大模型 LongCat 打造的编码场景专用模型
 LongCat-Flash-CatPaw-Coder

## Page 25

Agent 执行层



• Search 工具：Agent 通过工具主动收集上下文
• Edit 工具：负责处理文件修改
• Run 工具：运行命令、部署代码等
• MCP 工具：接入第三方 MCP 工具

## Page 26

预览调试





• 模拟用户操作，验证功能实现
• 截图查看 UI 实现效果
• 获取运行时报错，修复问题
• 指定页面元素精确修改

## Page 27

_(no text content on this page)_

## Page 28

ChatGPT 问世，之后美团专业通道合并



•  2022 年及之前
   美团专业通道：前端开发、后端开发、系统开发、数据开发......

•  2022.11
   ChatGPT 问世

•  2023.5
   美团技术角色改革，上述通道全部合并为“软件开发”

## Page 29

AI 时代，技术门槛降低，全栈能力成为核心优势


AI 出现前      AI 赋能后
        产品思维
        100
         90
         80
         70
         60
         50
         40
运维能力     30       设计审美
         20
         10
        0










后端能力    前端能力

## Page 30

沟通成本大幅降低


旧范式：一个需求 3-6 人参与    新范式：一人兼任多个角色，协作链路简化


前端    LLM


设计 设计稿    上下文                              设计文档
   接口文档   成品                描述需求    监督、审查
                                           后端代码
业务  MRD  产品  PRD    测试    用户        Agent

                            敏捷迭代    自测验收   前端代码
    后端


成品

## Page 31

重新定义全栈能力






 全栈（旧）= 前端能力 + 后端能力 + 运维能力 …



 全栈（新）= 工具调用能力 + 判断力 + 品味

## Page 32

_(no text content on this page)_

## Page 33

   CatPaw Engineer


基于对业界发展趋势以及公司当前实践现状的分析，我们认为 AI
Coding 将逐步演化为 AI for Software Engineering，并呈现以
下特征：
1）在能力范围上，AI 将由点及面。从单点代码生成，扩展至文
档编写、测试、代码评审、运维等环节，AI 将成为全链路研发效
率与质量的核心支撑。
2）在协作方式上，AI 将从辅助演进到共建。AI 不再只是个人工
具，而是在软件工程中嵌入到团队协作与工程流程，逐步承担局
部决策，实现人机共建。
3）在工作形态上，AI 将从工具走向自治。AI 将以 Agent 形态
具备执行端到端任务，具备自诊断、自优化和自进化能力，推动
软件工程走向自治化与普适化。

## Page 34

探索中的项目



 ☁   Cloud Agent               并行开发

 •   基于云端沙箱环境，且具备长程任务的     •   基于 Git WorkTree 的多工作区机制
     执行能力                  •   在同一任务目标下，由主 Agent 同时
 •   可以更好的与公司的基础设施集成，打         启动多个执行 Agent，并行实现不同方
     通软件工程的全流程                 案或子任务
 •   可随时随地通过聊天窗口发起任务       •   在每一步通过对结果进行评估、对比与
                               筛选，选择最优路径推进下一步操作，
                               提升 Agent 的完成效率、结果质量

## Page 35

产品体验







 https://catpaw.meituan.com
 内测激活码：CSDN25        在线体验

## Page 36

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/马良焰_AI Coding在企业内的实践分享.pdf]]`
