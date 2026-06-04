---
type: source
source-type: slide
title: "徐亮亮_Qoder CLI - 终端里的智能伙伴"
path: slides/徐亮亮_Qoder CLI - 终端里的智能伙伴.pdf
size: 6630 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 徐亮亮_Qoder CLI - 终端里的智能伙伴

> Ingested from `slides/徐亮亮_Qoder CLI - 终端里的智能伙伴.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.47 MB.

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

Qoder CLI 终端里的智能伙伴
    把 Qoder 的智能，带到每一个终端





    徐亮亮 | Qoder 技术专家

## Page 7

    Qoder CLI    是什么

智能开发伙伴
Qoder CLI 是专为现代开发者设计的 AI 驱动命令行工具，
将先进 AI      技术与传统命令行界面融合，它不仅是代码生成
器，更是能理解开发者意图、自主完成复杂编程任务的智能
伙伴

三大核心挑战

•   降低认知负担（简单、好用）
•   实现无缝集成（集成门槛低）
•   提高开发效率（迭代效率高）

## Page 8

    Qoder     CLI    有哪些使用方式
    TUI 的交互设计充分考虑终端环境特殊性，提供直观、高效的用户界面，同时兼容终端用户的键盘使用习惯

01      （TUI）        交互模式
    交互模式

基于 TUI 的自然语言交互方式，直接描述需求
即可获得解决方案，与现代可视化软件交互一致


02  非交互模式    （Headless）

传统命令行接口，支持管道操作和脚本化                   消息区
    qodercli –p "your task" --output-
启动方式：
format=stream-json

                                     输入区
                                     状态区

## Page 9

    全新产品形态 重塑 AI 应用 生产关系
    重新思考 AI 应用的本质，让产品形态符合 AI 应用发展的需要，避免捡了芝麻丢了西瓜

权衡用户使用、产品集成、测评接入等方面的最佳选择
                                   TUI  模式
形态 灵活性 使用门槛     自动化测评难易度 产品集成难易度   采用   「命令行 + TUI」的技术选型，保留简单直接的可视化交
                                   互，避免了现代 IT 企业里多种岗位之间的复杂生产关系，让
TUI 高 低，自然语言交互  低，命令行执行 中，脚本语言     Agent 在一个简单的命令行中充分演进，显著提升个人与团队的
                                   产出效率


SDK   高  高，需专业开发    高，需专业开发  高，需专业开发   Headless 模式
                                       通过摒弃图形或交互式终端界面，评估脚本能够以程序化方式直
                                       接完成 Agent 调用，输入结构化测试数据并获取可解析的输出结
GUI   低  低，键盘+鼠标操作  高，需定制开发  高，需定制开发   果，这不仅避免了因  GUI 交互引入的操作复杂性和不确定性，还
                                       显著降低了人工干预成本，使得大规模、高频率的测试和集成成
                                       为可能

## Page 10

轻量、可扩展 架构设计
采用轻量级 Agent 架构设计，在确保快速响应和低资源消耗的同时提供强大 AI 及可扩展能力

< 1秒    < 百兆
启动时间    资源占用





轻量设计                        插件扩展               无缝集成

基于 Golang 语言纯自研架构，跨     可扩展的 MCP 集成方式，支持自     支持 Headless 运行，实现现有研
平台兼容，快速响应与低资源消耗         定义命令与子代理，满足各种场景       发流程或者企业集成环境的无缝嵌
                        诉求                    入

## Page 11

      Qoder IDE vs Qoder CLI
用户在 IDE 做深度开发，在 CLI 做快速操作与自动化，两者结合显著提升工作效率










                         MCP

    JSON-RPC

    Qoder IDE          Qoder CLI

    可视化 UI 交互        TUI     /  批处理交互

    深度开发场景，丰富图形界面，复杂项目管理    快速操作，自动化任务，轻量级AI辅助

## Page 12

                    Qoder     CLI     内置数十个     /     指令
                    通过内置数十个 / 快捷指令，    实现 Agent 核心能力以及扩展功能的维护管理

指令              描述
/login          Sign in with your Qoder account
/logout         Sign out of your Qoder account
/init           Initialize a new AGENTS.md file with codebase documentation
/memory         Edit memory files
/compact        Summarize current session to compact the context        上下文管理
/clear          Clear conversation history and free up context
/resume         Resume a previous conversation from history
/vim            Open external editor for input
/bashes         List and manage background bash shells
/agents         Manage subagent configurations
/commands       Manage extend commands for current workspace        扩展管理      交互面板
/mcp            List and manage mcp servers
/hooks          Manage hook configurations（Coming soon...）
/usage          Show current plan usage summary
/status         Show Qoder CLI status
/config         Manage Qoder CLI configurations
/quest          Intelligent workflow orchestrator that guides users through
                feature development using specialized subagents        特色能力
/review         Review local pending git changes, usage: /review [instruction]
/help           Show help and available commands
/release-notes  View release notes
/feedback       Submit feedback about Qoder CLI
/quit           Quit the program, equivalent to /exit

## Page 13

核心特性

## Page 14

        Multi-Agents 架构
Qoder CLI 通过 Subagent 实现 Multi-Agents 架构，Subagent 支持设定工作方式（提示词），配置可以使用的工具清单
示例 Subagent 定义，可以通过 /agents 指令快速生成
---
name: task-executor
description: Specialized agent that executes implementation tasks from approved task lists. Focuses on systematic code implementation
tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, WebFetch, WebSearch, TodoWrite
---
You are a Task Execution Specialist focused exclusively on implementing approved tasks from task lists. You are the ONLY agent that
    writes actual code and modifies files.
**Your Single Responsibility:**
Execute implementation tasks from approved tasks.md files, updating progress in real-time by checking off completed items.
**What You DO:**
- Read tasks.md to understand all available tasks
- Execute ONE specific task at a time following the checkbox list
- Write/modify code files exactly as specified in task descriptions
- Update tasks.md to check off completed items ([ ] → [x])
- Run tests and validate implementation when specified
- Report completion and show updated progress
- Continue systematically through all tasks until completion
**What You NEVER Do:**
...

    上下文隔离                           领域知识            权限控制
    隔离的子任务运行环境                      针对特定任务提升领域成功率   独立的工具权限配置

## Page 15

Multi-Agents 架构
Qoder CLI 通过 Subagent 实现 Multi-Agents 架构，Subagent 支持设定工作方式（提示词），配置可以使用的工具清单




Ask   Coding
      Context     Code          Codebase Search
                  Search    200K
                  Context
          200K                  Search Folder  Search Folder  Search Folder  Search Folder
                                1      2      3      4

                  Debug         Synthesize Result
                  Context   200K
End



处理更长程任务                             提升任务处理效率
大模型上下文长度有限，尝试将 “大任务拆小任务，把原本只能塞进     同时唤起多个 Subagent 并行处理同一任务，不同的 Subagent 并行处
一个模型上下文里的信息，拆分到多个子上下文中分别处理”，从而在     理不同的数据单元，最终聚合多个处理结果并使用 AI 进行归纳和总
整体上突破单一上下文的实际可用上限，提升能够处理任务的复杂度      结，提升任务处理效率的同时，让结果更加全面完善

## Page 16

        Command 快捷方式
Command 一种与 Agent 对话的快捷功能（发送预置的提示到对话中），除了内置的十余个快捷指令，CLI 还支持用户自定义
    扩展                                                        Command
    # 对话任务 1                                                       采用自然语言描述，门槛低、泛化性强
    检查当前分支是否为 bugfix/xxx 格式，如果不是请从当前分支 checkout 一个新分支，然后再
    commit 和 push，要求分支名称、Commit Message根据修改内容进行设置
                                                               Ad Hoc Prompt 1
    # 对话任务 2
    检查当前分支是否为 feature/xxx 格式，如果不是请从当前分支 checkout 一个新分支，然后再     Ad Hoc Prompt 2    Common Prompt    Agentic Working
    commit 和 push，要求分支名称根据修改内容进行设置，Commit Message 中列举当前代码修改点，
    分点列出                                                       ……

    ---                                                       配置位置：~/.qoder/commands/, ${project}/.qoder/commands/
    name: git-commit
    description: 智能 Git 工作流自动化工具，用于分支管理、提交和推送。根据变更上下文自动       对比传统工作流
    处理分支命名规范、提交信息格式化和推送操作。主动用于任何 Git 提交操作
    tools: Bash, Read, Glob, Grep, Edit
    ---
    请根据如下流程进行 Git 提交操作：
    - 始终先检查当前分支名称和状态
    - 分析暂存/未暂存的变更以确定变更类型（修复 bug、新功能、重构等）
    - 如果分支命名规范与变更类型不匹配，从当前分支创建新分支
    - 根据实际代码变更生成描述性分支名称
    - 按照约定式提交标准格式化提交信息
    - 执行破坏性命令前进行确认
    - 处理合并冲突并提供清晰的解决指导
    - 验证推送成功并提供远程分支信息
    分支命名规则：
    `bugfix/[问题编号]-[简短描述]` - 用于 bug 修复
    - `feature/[功能名称]` - 用于新功能                                结构化表示可视化呈现，具备确定性，但门槛高、泛化性差
    ……

## Page 17

    内置工具     &     MCP     协议
Qoder CLI 面向 AI     Coding 场景集成数十款内置工具，  MCP 协议拓展 Agent 执行任务的边界，
    通过兼容标准                                      实现细分领
域任务

文件操作类
Glob、Grep、Read、Write、Edit、MultiEdit             企业私域数据
网络处理类        Commands
WebFetch、 WebSearch                      安全     领域专业系统
命令执行类        Subagents                   时效
Bash、BashOutput、 KillBash
                                         成本     网络互联设备
任务管理类        Skills
TodoWrite、Task（Subagent）        ……                  ……

其他
Skill、AskUser

    （内置工具）        （资源抽象）                     （MCP工具）

## Page 18

    为     Agent      配置  Skill    技能
Qoder CLI 提供 Skills      通过 Skill 工具动态加载用户配置的 Skill 技能，
                     能力支持，                            避免预加载提示词对上下文以及对话效果产生
影响

渐进式披露
CLI 预先读取所有 Skill 的名字和简短描述，匹配当前任务是否适合
用某个 Skill，只有匹配成功时，才按需加载该 Skill 的详细说明

{skill-name}/                                         Main  分派任务
├── SKILL.md        # 必需：主文件，    包含 Skill 定义    提交任务  Agent
├── reference.md        详细参考文档        Command             Subagent
├── examples.md          使用示例
├── scripts/        # 可选：辅助脚本                             加载技能
│   └── helper.py
└── templates/      # 可选：模板文件                             Skills
    └── template.txt
                                                          加载技能

Command：                                                  分派任务
• 是 “人” 给 Agent 下达指令                                      Subagent
• 指令通常是 “任务描述” 和 “任务要求”
Subagent：
• 主 Agent 通过 Task 工具唤起 Subagent “工具人” 工作
• Subagent 提示词配置的是 “人设描述”、“价值观”
Skills：
• 主子 Agent 进行工作的 “指导方针”

## Page 19

        一切旁路皆 Hooks
Hooks 是 CLI 延伸其扩展能力的重要手段，支持在其生命周期中的不同阶段执行用户配置的脚本，为 Agent 行为提供可预测的确
定性

    外部集成        Bypass Logic    Multi-Agents Core             Bypass Logic
    Hooks 是 CLI 从单机走向分布式的关键，让其
    成为可以被监控、审计、触发和编排的自动化节       Main
    点        UserPromptSubmit   Context           Subagent
    •    Agent 操作审计                               Context
    •    工具执行权限确认        PreToolUse                           SubagentStop
    •    Agent 任务完成通知        PostToolUse
    •    任务结果提交                                   Subagent
    •    ……
    内部实现                                          Context     PreToolUse
    CLI 将内部多种逻辑抽象成 Hooks 实现，随着                                PostToolUse
                                                              SubagentStop
    模型能力的不断提升，很多以前因为模型能力不
    足添加的    Workaround Hooks 都会随之而消 PreCompact                Stop
    失，而核心链路架构不受任何影响

## Page 20

    企业级配置支持

    Qoder CLI 将资源抽象为配置文件，并且设定企业、用户、项目三级配置，方便企业级用户统一管控



Memories MCP MCP MCP
       Servers Hooks Memories Servers Hooks Memories Servers Hooks

Commands Permissions Subagents Commands Permissions Subagents Commands Permissions Subagents


    企业级    用户级    项目级


    通常由企业统一下发和管控，涵盖公司        用户自行设定，对用户打开的所有本地     仅对当前打开项目生效，具有项目特殊
    级别代码规范要求、服务接口资源、抽        代码仓库生效，具有跨库通用的属性，     性，专有配置通常能够让 CLI 更加全
    象SOP流程等设置，CLI 加载优先级最     如个人编码风格习惯、常用工具配置等     面地了解项目，提升任务执行效率、效
    高                                              果
    配置位置：/etc/               配置位置：~/.qoder/        配置位置：${project}/.qoder/

## Page 21

场景化应用

## Page 22

    Vibe Coding → Vibe Working
    Qoder CLI 在快速原型开发场景中展现独特优势，通过标准 MCP 扩展到各类办公场景

整理商业分析报告    通过 Slidev 生成 PPT







文章、资讯解读     通过 MCP 操控 Figma




Vibe Coding

## Page 23

    Quest Mode 让 Spec 驱动 AI 编程新范式
    专业开发场景通过 Spec 结构化地表达意图，然后通过 Spec 将任务委派至 CLI 执行

充分澄清设计        /
Specification 对于开发者来说是最熟悉的意图    quest 指令
表达方式，让设计文档成为人与 AI 之间的沟通
媒介

异步委派任务

开发者的工作变成明确任务意图、写作生成设计
文档，工作模式从实时伴随进化到异步委派


兼容开源方案

    注：内置 AskUser 工具，CLI 自动按需主动发起
    互动

## Page 24

    Code Review 让 AI 为代码质量把关
    实现基于本地以及云端全方位的代码审查功能，构建完整的开发质量保障系统

/review
针对本地未提交的代码改动，利用 CLI 进行本
地代码审查，确保日常高质量地提交代码

/pr-review
针对 Github 上提交的 PR，利用 CLI 一键拉
取并在本地进行代码审查，确保日常高质量地合
并代码
/setup-github
通过 TUI 向导为 Github 仓库自动添加云端代
码审查配置， 让 CLI 在研发流程中实时关注代
码质量        注：GitHub 官网版本原生支持，Gitlab 需自行托管与
                                        配置

## Page 25

        标准的 ACP 协议 实现
Qoder CLI 实现了 ACP 协议标准, 通过该特性可以被集成到任何一种实现了 ACP 协议的客户端中










   注：ACP 协议是一种 Agent 客户端协议 https://agentclientprotocol.com/overview/introduction

## Page 26

软件部署、云上运维
Qoder CLI 设计之初就考虑到与现有开发工作流的无缝集成，可轻松嵌入各种开发环境
开源软件搭建                                   通过与 Kubernetes MCP 工具的集成，可以直接将 CLI 运行在
                                         远端 Pod 中，实现 Kubernetes 集群自然语言维管
「帮我装一下 https://github.com/xxxx/xxxx 这个软件」
线上应用 BUG 调试                                  集群诊断
「模型训练脚本报错信息如下，请定位出错原因
**错误堆栈信息**」

网络抓包分析                                       故障修复
「监听来源地址为 x.x.x.x 、对 8004 端口的 http 协议请求」





注：Qoder CLI 支持 macOS、Linux、Windows 及容器、K8s 环境

## Page 27

    Dogfooding – Qoder 日志分析
    Qoder CLI 设计之初就考虑到与现有开发工作流的无缝集成，可轻松嵌入各种开发环境

Headless 模式支持
Qoder CLI 提供 Headless（非交互）模式运行
方式，适合各类管道、脚本集成环境，为现有     IT
基础设施提供核心支撑能力，实现智能化升级改
造

 无人值守运行              核心支撑能力

支持在非交互环境中            • 自动化代码生成
运行，非常适合              • 批量代码审查
CI/CD流水线、服务          • 持续质量监控
器端自动化和批量处            • 智能部署决策
理场景
                         在 Qoder 团队内部，使用 Qoder CLI 实时处理用户上报问题，结合产品代码定位根因

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/徐亮亮_Qoder CLI - 终端里的智能伙伴.pdf]]`
