---
type: source
source-type: slide
title: "汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站"
path: slides/汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站.pdf
source-md5: eb3f2ad4b61338ec559f96ca5c2fd924
size: 5256 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站

> Ingested from `slides/汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站.pdf` via `lit parse` on 2026-06-04.
> Source file: 5.13 MB.

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

C++在无图形终端时代的下一站
CodeBuddy 产品负责人

汪晟杰 腾讯资深技术产品专家

## Page 7

目 录 CONTENTS
 01: 终端的回归与 CLI 新范式的价值主张
 02: 上下文工程的核心概念与 CodeBuddy CLI 的解决方案

 03: Agent 内核统一设计与扩展性架构
 （Command、Subagent、MCP、Hook、Skills）

 04: Spec-Coding实战场景在CLI中的应用与企业级落地

## Page 8

终端的回归与 CLI 新范式的价值主张

## Page 9

深夜两点的故障
 IDE 为什么不够用
 当线上故障爆发，开发者真正稳定可依赖的入口只有一个： SSH + Shell 。

     远程环境 本地IDE 多集群场景
  网络抖动导致Web IDE卡顿 无法还原线上依赖与数据 图形界面成额外负担
        结论：终端不是备胎，而是 生产一线 。

## Page 10

为何是 CLI，而不是又一个新 IDE？
CLI 的工程价值在于其无可替代的工程优势，而非情怀复古。
 工作流连续性 终端本就承载构建、测试、Git，让AI进驻意味着零上下文切换
 可组合性 AI可直接编排现有工具链（编译器、脚本、CI），成为智能壳层，而非推倒重来
 跨环境一致性 无论是本地、容器还是CI Runner，终端形态天然可用，这是GUI难以企及的
       真正的生产力，不是多一个界面，而是 少一次 Alt-Tab 。

## Page 11

  从补丁到主角：AI 为何要先住进终端？
AI 编程工具正从“IDE插件”进化为“终端常驻Agent ”，这是一次角色的升级。
   CodeBuddy CLI                     Claude Code
   Agentic Coding: 理解整库代码，执行命令，      持续执行: 连续数小时进行重构、修复和Git操
   编辑文件。                             作。
   Background Agent 模式: 在后台长期、异步     Agent能力: 自主拆分任务列表，按步骤推
   地推进复杂需求。                          进。

## Page 12

C++开发者+AI Coding 的GAP
终端成C++主战场                      远程与容器场景
                               Vim/Neovim、tmux、gdb、CMake/Ninja构成硬核日常，
在Linux服务器、Docker/K8s Pod、交     却面临构建慢、调试长、依赖深的三重阻碍。
叉编译链中，图形IDE无法渗透，C++工           传统AI辅助失效
程师只能依赖 SSH+Shell 。             传统Copilot式补全因脱离真实构建环境而失效，开发者呼
                               唤能在 仓库现场 解决问题的智能工具。

## Page 13

   大型项目 构建、调试、依赖三重门


   构建慢    调试长       依赖深
百万级工程构建耗时数十分钟，头 手动重复“cmake .. && ninja && 横跨apt、vcpkg、conan等，版本
文件与模板展开让增量编译举步维 gdb”长链，出错信息被稀释，定 冲突隐蔽，IDE静态索引常基于错误
   艰。    位成本飙升。    宏定义。
  开发者被迫在编辑器、终端、浏览器间来回切换，形成认知断档。AI必须住进现场环境，与构建、调
        试、依赖同频呼吸。

## Page 14

上下文工程的核心概念与 CodeBuddy CLI
的解决方案

## Page 15

   为何C++项目需要上下文工程？
  C++项目规模庞大，结构复杂，
  化提取与持久化存储，将分布式知识浓缩为可装载的项目记忆，赋予AI全局视野，避免
  “只见树木不见森林”的陷阱。
项目规模与复杂性           构建系统与依赖             AI理解的局限性
  数十万行代码、深层头文件、模   CMake/Bazel、第三方库和编译选
  板与宏展开，使项目结构极为复
  杂。               项本身就是核心上下文，直接影      缺乏全局视野导致AI建议片面，
                   响代码含义。              甚至可能引发连锁缺陷，无法有
                                       效进行诊断或重构。

## Page 16

   CLI 形态为何天然适合上下文治理？
        天然优势
    CLI 环境              信息集中: 无需复杂协议即可结构化
拥有 IDE 无法直接触达的 额外信息     抽取信息。
 入口 ：仓库、日志、命令输出等，       命令驱动: 借助脚本或钩子，在命令级别完成扫描、
 这些信息原本就“住在终端附近”。       过滤与封装。
                        高信噪比: 为模型提供精准素材， 显著降低幻觉
                        与迭代成本 。

## Page 17

   CodeBuddy CLI 一键初始化机制
    通过 `/init` 命令，自动扫描仓库，生成包含模块、依赖和构建信息的项目记忆，为AI
                            提供精准的项目蓝图。
         扫描仓库        解析依赖        生成记忆
识别CMakeLists、conanfile等    提取目标、源文件、包含路径    输出markdown格式的项目记
         构建入口                  和第三方库            忆文件，供AI引用
                   项目记忆包含: 模块层级 | 接口依赖图 | 关键宏列表

## Page 18

   上下文压缩

        原始上下文                 压缩后上下文
包含完整日志、历史代码片段、重复错误信息，
        体积庞大。                 确保精准高效。
  分层摘要:                   重复信息归一:
  保留最近编译失败片段、关键调用链；历史成功构建降
  级为统计摘要。                 对重复第三方头文件错误，仅保留首次位置与统一修复
                          方案。

## Page 19

 把编码准则写进上下文规范
        持久化规则文件 CODEBUDDY.md / AGENTS.md
    CODEBUDDY.md 记录 领域约束 与 决策背景 ，帮助AI理解“为什么”，避免团队重复踩坑，实现知识可审计、
        可回溯。
  记录决策背景 固化安全规则 实现知识回溯
解释为何选用自研线程池而非std::thread， 明确禁用存在已知漏洞的Boost子模块，并 通过版本控制追踪规则变更，确保决策过程
记录技术选型的权衡与理由。 关联对应的CVE编号与修复策略。 透明，新成员能快速理解历史演进。

## Page 20

   融合构建日志定位链式错误

   构建日志 CodeBuddy 解析 项目记忆 AI 诊断    精准定位
CMake/Ninja输出、编译错误行列号    头文件依赖图、宏定义、模板实例化栈 还原宏展开路径，定位ODR违规，
       还原模板错误到用户源码
       实现从 构建日志 到 源码缺陷 的闭环诊断

## Page 21

   性能剖析上下文驱动优化

perf hotspots, heap profiler    容器类型, 算法选择, 调    智能优化建议
             分配栈                     用关系     避免拷贝, 减少虚调用, 更
                                                   换容器
                   通过融合性能数据与源码语义，AI的优化建议兼顾可维护性与性能收益，避免纯数值
                                 驱动导致的代码恶化。

## Page 22

Agent 内核统一设计与扩展性架构
（Command、Subagent、MCP、Hook）

## Page 23

纯自研 Nodejs 内核：极速跨平台

高性能
内置并发调度器，保证高并发场景下终端交互依旧流畅。
企业级
提供静态链接选项，方便企业内网一键分发，满足严苛的可
审计、可管控要求。

## Page 24

Agent 内核：统一可扩展框架
CodeBuddy Code 中所有交互被抽象为 Prompt、Tool、Hook 三类事件，四层解耦，15 分钟即可
       定义自然语言的可执行指令 上线新能力。 Skills (技能包)
        AI 如何实现的专用的技能指导书
        按领域加载专用提示词与工具集，实现上下文隔离
        统一入口，协调各层
集成企业私有API、数据库、IoT设备 在关键节点插入自定义逻辑，如审计、通知

## Page 25

   上下文工程：让 AI 拥有项目记忆
 CodeBuddy 将会话、文件、Git 历史等信息抽象为统一的 Context Object，实现“换终端不换脑
        子”的无损连续协作。

    记忆具像化     会话压缩        断点恢复
关键内容自动落盘，敏感字  通过算法在超限前进行语义压缩。
    段脱敏。        /compact    /clear 一键清理
        自动压缩               /resume 随时续写。

## Page 26

  自定义指令：    一句话封装复杂流程

通过 YAML 描述文件，将任意 Shell、API、脚本组合成自然语
言指令，让“写脚本”变成“写描述”。
  name: fast-commit
  description: “快速提交并推送代码”
  command: |
  git add .
  git commit -m"{{MSG}}"
  git push
项目级、用户级、系统级 三级配置 ，保证个人便捷与企业规范并存。   $ codebuddy /fast-commit "fix: 修复登录bug"

## Page 27

子代理：让智能体更专业
子代理是面向特定领域或任务而设计的智能体，它在主代
理的调度下独立运行，拥有专属的提示词、知识库与工具
集。通过把复杂需求拆解为多个子代理，系统可实现更高
的专业度与可维护性，也降低单点故障风险。

 核心概念
 面向特定领域，独立运行，拥有专属资源。
 与主代理关系
 在主代理调度下工作，协同完成复杂任务。

## Page 28

   子代理的三大核心价值

    上下文隔离        领域知识增强          权限控制
保证不同领域数据不交叉污染，
 提升安全与合规性。例如，财   通过专属提示词与模型微调，   按最小可用原则分配工具与数
 务数据与用户隐私信息由不同   使回答更精准权威。例如，医   据访问权，降低误操作风险。
 子代理处理，杜绝信息泄露风   疗咨询子代理能提供更专业的   例如，客服子代理无权访问核
      险。         诊断建议。           心数据库。

## Page 29

    MCP + Hook：连接万物最后一公里
    让 CodeBuddy 不再是孤立工具，而是能融入企业现有平台的“可观测、可治理”节点。


       MCP 插件 深度集成 Hook 机制
封装私有 API、数据库、IoT 设备为标准 在关键点插入逻辑，如通知、审计、流
        Tool 腾讯云服务、Superbase、Figma等 水线

## Page 30

   Skills
  Skills 是 CodeBuddy Code 推出的 模块化能力包 ，以文件夹形式存放，内含     即插即用的
  指令、脚本与参考文档，让模型在需要时自动调用，完成代码审查、数据分                   专家模块
  析等重复性任务。
  Skills 像即插即用的专家模块，使通用大模型秒变领域专家。                     一键安装的插件包
为开发者提供可移植、可组合、可版本化
                                                      的 AI 工作流支撑。

## Page 31

    Skills 核心构建文件

    一个 Skill 就是一个文件夹，其内部结构清晰，支持项目级、个人级和插件级三种管理方式。

    SKILL.md     scripts/    references/
核心定义，包含YAML头、指令和 存放可执行的Python或Shell脚本。  存储API文档、代码规范等知识。
       示例。
    支持项目级(.codebuddy/skills)、个人级(~/.codebuddy/skills)和插件级(marketplace)管理
        支持业界所有的技能包的导入，兼容Claude发布的官方技能

## Page 32

     十分钟编写你的第一个 Skill

                                               #
                                               naSmKILL.md 示例
                                               e: code-security-scan
                                               description扫: 描代码中的常见安全漏洞
1                                              ## Instructions
                                               1. 接收用户提供的代码文件路径。
      在项目 `.codebuddy/skills` 目录新建文件夹，创建       2. 使用 `bandit` 工具扫描该路径下的Python文件。
      `SKILL.md`。                              3. 解析扫描结果，生成结构化的安全报告。
2     用YAML头写下名称与描述，正文按Instructions、      支持业界所有的技能文件导入
3     Examples编写指令与示例。
      将Python等脚本放入 `scripts` 目录，并在Instructions中
      明示调用方式。

## Page 33

_(no text content on this page)_

## Page 34

基于Git Worktree 实现多 Agent 并行开发

## Page 35

    CLI 实践指南

        命令行优先与脚本集成                   结合 Git， AI 驱动的 Pull Request
                                         描述                       拆任务步骤，强化需求计划
    将CodeBuddy Code融入你的Unix工作流，     自然语言完成终端操作，对Git项目，自然语         描述问题要尽量清晰，容易让大模型拆解的
    管道能力叠加buff，玩法多样                 言提交发布，解决冲突。                   需求清单

智能项目配置管理，灵活使用长期记                                录入基础规则与惯例，减少环境上下  明确需求，巧用文件和贴图，
        忆    文“口述”成本                                              让 AI 只改"该改的地方"
    CodeBuddy.md结构，用好分层结构。灵活        # Memory 机制，随代码变更，动态追加或       @ file，截图，各种方式让AI理解需求。明确
    使用 /init 命令，为你的仓库生成工程的长         修改                            哪些可以放心交给 CodeBuddy 的任务
    期记忆的起始点

 合理控制操作权限，重要操作要谨                     明确优先级/禁止项，阻断常见                   规约编码
        慎                                失误
    Shift + Tab 切换Yolo/Solo模式（Auto   当有二义性的定义，Say No，定义好禁止规       团队/项目统一开发规约（如目录结构、提交规
    Edit 和 Auto Run）                 则，然后 Say 请撤回改动，重做            范、命名约定等）

## Page 36

 异步编程新范式：Spec 驱动开发

开发者只需撰写一份 Specification，AI 通过 AskUser 工具主动
澄清需求，随后自主执行，实现“从想法到 Demo”的异步委
派。
 1 开发者用自然语言撰写 Spec
 2 AI 主动澄清需求， 异步执行
 3 交付可运行 Demo， 显著缩短原型周期

## Page 37

    自定义斜杠命令 + Skills 让发版流程自动化且可靠

/mr（智能 Merge Request 创建）：开发者在完成日常
     开发提交后调用，自动执行提交流程中的各项检查和
      准备工作，为新的改动创建标准化的 MR。
  /release（智能发版）：在准备发布新版本时调用，自
   动完成版本升级、变更日志汇总以及发布 MR 创建等所
              有步骤。
     覆盖了日常开发提交和正式版本发布的关键链路。通
   过在斜杠命令中编排多个 Skill，我们将以往靠人力和
     零散脚本堆砌的流程变成了清晰、有条理的自动化流
               水线。

## Page 38

 Background Agent 支持接入各类研发管理系统

Background Agent 支持通过沙盒的方式，内置 Codebuddy code 并组成一个包含 模型、工具、环境、指令、智能体 共同协作的专属上下文
环境，用于处理特定的任务，让 Codebuddy code 可以准确的完成研发任务。

• 专属上下文沙箱环境
• 自定义工具、环境、智能体
• 无缝集成到各类研发系统      企业微信  TAPD      CNB/Github  腾讯设计  其他研发系统…

对接研发管理系统：        MCP     WebHook        ACP      Restful API  其他协议
 对接需求管理，实现需求自动拆解             Background Agent
 对接代码仓库，实现任务自动开发
 对接缺陷系统，实现缺陷自动修复 统一接入    Session 管理       Oauth 认证        用户映射
 对接测试系统，自动化测试脚本
                沙箱环境     Codebuddy Code      E2B 沙箱   CloudeStudio 沙箱

对接消息通知系统：        上下文管理   SubAgent      插件/仓库 管理      MCP Tools
 对接企业微信机器人

## Page 39

 Background Agent 支持接入各类研发管理系统

Background Agent 支持通过沙盒的方式，内置 Codebuddy code 并组成一个包含 模型、工具、环境、指令、智能体 共同协作的专属上下文
环境，用于处理特定的任务，让 Codebuddy code 可以准确的完成研发任务。

• 专属上下文沙箱环境
• 自定义工具、环境、智能体
• 无缝集成到各类研发系统      企业微信  TAPD      CNB/Github  腾讯设计  其他研发系统…

对接研发管理系统：        MCP     WebHook        ACP      Restful API  其他协议
 对接需求管理，实现需求自动拆解             Background Agent
 对接代码仓库，实现任务自动开发
 对接缺陷系统，实现缺陷自动修复 统一接入    Session 管理       Oauth 认证        用户映射
 对接测试系统，自动化测试脚本
                沙箱环境     Codebuddy Code      E2B 沙箱   CloudeStudio 沙箱

对接消息通知系统：        上下文管理   SubAgent      插件/仓库 管理      MCP Tools
 对接企业微信机器人

## Page 40

CLI 沙箱隔离确保操作机安全
文件与网络双锁
    文件系统隔离                                          { "sandbox":
    仅开放指定目录，默认屏蔽curl、wget等下载器。                       { “enabled”: true,
                                                    "autoAllowBashIfSandboxed": true,
    网络访问隔离                                          "excludedCommands":
                                                     ["git", "docker"],
    仅放行白名单域名，阻止非授权网络请求。                              "network":
                                                    { "allowUnixSockets":
                                                    ["/var/run/docker.sock"],
    灵活配置                                            "allowLocalBinding": true }
    可配置excludedCommands，如git push、docker等，强制人工确认。   }

## Page 41

 内置多种权限矩阵
默认只读策略 启动，任何修改均需用户显式授权，将“最小权限”写入系统基因，阻断AI误操作与潜在攻击。
 控制对文件和目录的读取访问，可限定特定路径。             控制对文件和目录的写入访问，可限定特定路径。

 控制命令行执行权限，可限定具体命令如npm:test。        控制网络请求权限，可限定特定域名。
     默认命令黑名单                         双层输入清洗
 curl  wget  chmod  sudo  rm -rf     正则清洗: 过滤特殊字符与常见注入模式
     支持项目级自定义增删，高危命令默认阻断。            语义清洗: 分析上下文，拦截异常指令
                                     清洗规则云端动态更新，持续对抗新变种。

## Page 42

 企业级落地：统一管控与全平台适配

通过三级配置与多环境支持，CodeBuddy CLI        Project ($project/.codebuddy/)
可灵活、安全地融入企业现有研发体系。
Enterprise(系统) → User(用户) → Project(项目)，层    User (~/.codebuddy/)
层覆盖，兼顾统一策略与灵活微调。        Enterprise (/etc/) –配置下发
支持 Worktree(隔离分支)、Container(沙箱)、
Kubernetes(远端异步)，满足不同安全与并发需求。        配置优先级 (高 → 低)

## Page 43

 CLI 演示

1.   图片多模态支持
2.   MCP工具和需求详情获取
3.   多轮执行与生成
4.   一键PR

## Page 44

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站.pdf]]`
