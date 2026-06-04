---
type: source
source-type: slide
title: "Pete_软件工程进阶金字塔"
path: slides/Pete_软件工程进阶金字塔.pdf
source-md5: e2f9088863f55b8b212778e5818a9675
size: 3058 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# Pete_软件工程进阶金字塔

> Ingested from `slides/Pete_软件工程进阶金字塔.pdf` via `lit parse` on 2026-06-04.
> Source file: 2.99 MB.

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

The Pyramid of Software Engineering
Mastery
软件工程进阶金字塔
Pete Muldoon : Bloomberg

## Page 7

The Pyramid of Software Engineering Mastery
软件工程进阶金字塔
Maturity in your career
职业发展成熟度
Cpp-Summit
Dec 12th, 2025
Peter Muldoon
Senior Engineering Lead, Ticker Plant

© 2025 Bloomberg Finance L.P. All rights reserved.

## Page 8

Who Am I 我是谁     •   Starting using C++ professionally in 1991自
                     1991年起开始专业使用C++
                 •   Professional Career职业生涯
                         Systems Analyst & Architect 系统分析与架构师
                     •   21 years as a consultant 担任顾问21年
                         Bloomberg Ticker Plant Engineering Lead 彭博行情
                         系统（Ticker Plant）工程主管
                •    Conference talks focused on practical
                     Software Engineering技术大会演讲聚焦于软件工
                     程实践
                         Based in the real world 源于实际场景
                     •   Take something away or change
                         perspective 获得启发或转变视角
                    Bloomberg        8

## Page 9

Why is that?
为何有此一问？
Not!
可能没有

Bloomberg    9

## Page 10

What does “Done”
mean?
“完成”意味着什么？

Bloomberg       10

## Page 11

Why bother? 为何要多此一举？
The benefits of establishing a definition of “Done” include creating a shared
understanding and unified language for software delivery, ensuring that new
employees have access to tribal knowledge and process expectations
确立“完成”标准的价值在于：它能为软件交付建立共同认知与统一语言，确保新成员能够快速理解
团队既有经验和流程规范。
A proper definition of “Done” across an organization acknowledges the shared
responsibility and helps a software organization maintain alignment on
projects/deliverables
一个贯穿组织的、恰当的“完成”定义，既体现了责任的共同担当，也有助于整个软件团队在项目与
交付物的推进中形成合力、保持同频共振。



    Bloomberg    11

## Page 12

Basic Terminology 基本术语
What is the Business Value of Software Engineering?软件工程的商业价值是什么？
Delivering desired product outcomes in incremental steps以渐进式步骤(迭代)交付期望的
产品成果
Why incremental steps?为什么采用渐进式步骤？
    Shorter time horizons 更短的时间周期
    More predictable 更容易预测
    Lower risk 更低风险
•   Better feedback from customers/stakeholders来自客户/利益相关者的更好的反馈



    Bloomberg    12

## Page 13

Basic Terminology 基本术语

Where is the Business Value in Software Engineering?软件工程的商业价值体现在哪里？
Software Value is actualized when it’s
软件价值的实现，取决于其是否满足以下核心条件：
    Available 可用
    Usable 易用
•   Reliable 可靠
Software Value (future proofing) 软件价值（面向未来）
•   Configurable 可配置 /safely 安全
    Flexible 灵活
    Fix issues quickly 快速修复问题
•   Evolve quickly/safely 安全高效的演进
        Bloomberg        13

## Page 14

Software Engineering Pyramid
软件工程能力金字塔










Bloomberg    14

## Page 15

Development 开发环节
Have the changes been verified and applied? 变更是否已通过验证并
应用？
•   Met the change Acceptance Criteria?是否满足变更验收标准？
   q Fully vs partially 完全满足还是部分满足        DONE?
•   Passed all testing driven by the validation system?是否通过了验证系统
    驱动的所有测试？
   q Unit tests/integration all passed单元测试/集成测试是否全部通过
   q Added tests for a new feature/bug fix 是否为新功能/缺陷修复添加了测试
•   Passed code review and been committed into the repository?是否通
    过代码审查并已提交至代码库？
   q Executed in a structured sane manner是否以结构化的合理方式执行
•   Merged into a package for Production release?是否已合并至用于生产发
    布的软件包中？
   q Ready for deployment是否已准备就绪，可部署

        Bloomberg        15

## Page 16

Development 开发环节
Are the changes deployed everywhere?
变更是否已在所有环境中部署？
•   What is the pace of deployment through Production stages
    在生产各阶段部署的节奏如何？        DONE?
•   When is the code finished being deployed Everywhere
•   代码何时能完成全环境部署？
    Any staggered dependencies needing tracking
•   是否存在需要追踪的分批依赖项？
    Any code freezes imminent
    是否有临时代码冻结安排？



    Bloomberg    16

## Page 17

   Feature Flags 功能开关

   What is a Feature Flag?什么是功能开关？
   Feature flags are a software development tool that allow you, at runtime, to
   enable or disable a change without modifying the source code or requiring
   a rollback/redeploy 功能开关是一种软件开发工具，它允许您在运行时启用或禁用某项变更，
   而无需修改源代码，也无需进行回滚或重新部署。
   Safety based if-statements are placed in the code base that act as circuit
   breakers for “untested”1 code 基于安全性的条件判断被置于代码库中，充当"未经充分测
   试"代码的断路器。
   Disables a single change which obviates the need for system rollbacks which
   would affect multiple unrelated changes 其作用是：可针对单一变更进行禁用，从而避
   免了因系统整体回滚而影响多个不相关变更的问题。
1: Untested in production Bloomberg 17

## Page 18

Feature Flag Enablement 功能开关启用管理
Deployed code that’s not being utilized is not useful (yet)
功能开关启用管理已部署但未启用的代码（目前）尚未产
生实际价值。
Are Feature flags enabled Everywhere in Production?      DONE?
功能开关是否已在生产环境全量启用？
    What is the pace of enablement?启用的推进节奏如何？
    When is enablement complete?何时能完成全量启用？
•   *When is the feature flag being removed?功能开关计划何时
    被移除？

* Dealt with in later section
        Bloomberg        18

## Page 19

    Software Engineering Pyramid
    软件工程能力金字塔










Commit Code  Tests Passing  Code packaged  Changes Deployed  Feature Flags enabled
   提交代码          测试通过           代码已打包            变更已部署       功能开关已开启

        Bloomberg                                                19

## Page 20

Survival Achieved
已经存活

Congratulations, you’re a competent hacker
恭喜，你已成为一名合格的黑客




Bloomberg    20

## Page 21

Rationale!核心理由！
Why is survival not enough? 为何仅满足“存活”远远不够？
Any system where engineering is invested completely in feature
change/bug fixing, that system will devolve, over time, into a
complex brittle codebase.在任何一个工程资源完全倾注于功
能开发与缺陷修复的系统中，随着时间推移，该系统将不
可避免地退化为复杂而脆弱的代码库。
Efforts are needed to stabilize/reverse the entropy in the code
base.必须投入持续努力，才能稳定乃至逆转代码库中的熵
增趋势。



    Bloomberg    21

## Page 22

Code Health Basics代码健康基础
What is software decommissioning? 什么是软件退役
Decommissioning is the strategic process of retiring outdated software and related
infrastructure, to streamline and enhance overall maintainability/efficiency. 软件退役
是指有计划地淘汰过时软件及相关基础设施的战略性流程，旨在提升整体可维护性与运行效率。
Two categories两大类别
• Code that is structurally never abled to be accessed 结构上永远无法被访问的代码
    q Actual functionality that is never called实际功能从未被调用
    q Find with static analysis tools – Coverity, cppcheck, xunused, IDE 可通过静态分析工具发现（如
      Coverity、Cppcheck、xunused、IDE 工具）
• Code that is never accessed with current user input 在当前用户输入下从未被访问的代码
    q Monitor usage in production over a “length of time”需在生产环境中长期监控使用情况
    q Feature flag removal通过功能开关移除进行验证

        Bloomberg 22

## Page 23

Decommissioning退役管理
Any decommissioning needed? 是否有需要退役的内容？

•   If replacing something, have we planned for the
    removal/decommissioning of the older functionality?
•   若进行功能替换，是否已规划对旧功能的移除/下线？
    Feature flag removal? 功能开关是否已清理？
    q Eliminate dead branching of code 是否已清除代码中的无效分
    支？






    Bloomberg    23

## Page 24

Code Health Basics代码健康基础
What is software refactoring?什么是软件重构？

Refactoring is the disciplined process of changing a system’s software in such a way that it does not
alter the function of the code yet improves its internal structure and/or efficiency.重构是一个有纪
律的软件修改过程，它在不改变代码外部功能的前提下，优化其内部结构和/或效率。
Why is refactoring needed?为何需要重构？
   Tactical战术性修补=> Strategic change/implementation战略性变更/实现
•  Rushed / Sloppy code changes仓促/粗糙的代码改动
   q Time challenges时间压力
   q Refactoring time not budgeted未预留重构时间
   q Inadequate time to research调研时间不足
   q Poor code reviews代码审查不充分
   q Inexperience经验不足
Note: No refactoring, over time, will lead inevitably to a system rewrite
注：长期不进行重构，系统将不可避免地走向彻底重写
       Bloomberg        24

## Page 25

Refactoring 重构需求评估
Any Refactoring needed due to:是否需要因以下情况启动重构：
    Recurring / Duplicated Patterns in code 重复的代码模式
•   Low readability/maintainability code低可读性/可维护性代码
   q Code smells代码异味
   q Overly complicated / redundant logic过度复杂/冗余的逻辑
   q Not using standard components未使用标准组件
    Paradigm changes编程范式变更
•   Technical depreciation技术栈折旧
   q Code ages代码年久失修
   q Technological advancements技术进步推动
   q Language evolution语言特性演进
   q More efficient alternatives出现更高效的替代方案


    Bloomberg    25

## Page 26

Code Health Basics代码健康基础
What is Technical Debt?什么是技术债？
Technical Debt: Cost of reworking/fixing code in the future due to limited quick solutions
Technical Debt: Unnecessary Complexity in the codebase
技术债：代码库中不必要的复杂度     技术债：指因当前采用有限快速的解决方案（捷径）而导致的、

Fomented by主要滋生原因
    Deadlines期限压力
    Firefighting应急救火式开发
    Cleverness / premature optimization过度“炫技”/过早优化
•   Lack of skills / seasoning / poor culture技能不足/经验缺乏/不良工程文化
    Lack of standards / poor code reviews缺乏标准/代码审查不严
    Organic growth无序自然增长
    Poor documentation文档缺失
•   Aging技术老化
* Over a span of time注：技术债通常随时间推移而累积恶化。
        Bloomberg        26

## Page 27

Tech Debt Basics技术债基础
“There is nothing so permanent as a temporary decision” “没有什么比‘临时方案’更持久的了。”
- Knapton 克纳普顿
Categories of Technical Debt:技术债的两大类别：
•   Intentional有意技术债
    q Taken on consciously for strategic reasons主动承担，通常出于战略考量（如缩短上市时
    间）。
•   q Items placed on backlog to mitigate/remove明确记录在待办清单中，并计划后续缓解/清除。
    Unintentional无意技术债
    q The non-strategic result of doing a poor/sloppy job非战略性结果，源于草率、低质的工作。
    q No plan to mitigate通常无缓解计划，随时间积累为“隐形负债”。
“A project isn’t done until you go back and adjust whatever it was you took on as
technical debt; and everybody agrees this is how we define ‘done’” “一个项目只有在
回过头去清理所有技术债之后才算真正完成；这是团队对‘完成’定义的共识。”
- Knapton

        Bloomberg        27

## Page 28

Tech Debt Basics技术债基础
Tracking Tech Debt技术债追踪：
•   Be intentional主动管理
    q Add to list when suboptimal solutions used在使用非最优解决方
    案时，即时记录至技术债清单
    Highlight business risks明确业务风险
•   Time to market权衡时间价值
Tech Debt prevention技术债预防:
    Proper timeline planning合理的时间规划
    Design reviews/ADRs设计评审/架构决策记录
•   Code review guidelines/ Coding standards代码审查规范
    /编码标准
•   Tracking持续追踪
    q Champion its demise推动债务清除

        Bloomberg        28

## Page 29

Testing Basics?测试基础

All Testing Pillars accounted for是否涵盖所有测试支柱:
    Unit单元测试
    Integration 集成测试
•   System end-to-end (QA) 系统端到端测试(QA)
Test coverage: 测试覆盖范围
    Identified corner cases 已识别边界情况
    Test happy/unhappy paths测试正常路径与异常路径
•   Create tests based on past production problems (for next time)
    基于过往生产问题创建测试（防复发）
•   Automation of testing with alarms测试自动化与告警设置
Maintain quality through testing
        Bloomberg        29

## Page 30

Rationale!核心理由
Why is survival not enough?为什么“能运行”远远不够？
Any system where engineering is invested completely in feature
change/bug fixing will devolve, over time, into a complex brittle
codebase.任何一个将工程资源完全投入到功能变更和缺陷
修复中的系统，随着时间的推移，都必将退化为复杂而脆
弱的代码库。
Efforts are needed to stabilize/reverse the entropy in the code
base.我们需要投入持续的努力，才能稳定乃至逆转代码库
中的熵增趋势。



    Bloomberg    30

## Page 31

    Software Engineering Pyramid
    软件工程能力金字塔







Decommission                Tech Debt  Refactor    Testing
  Old Code                  reduction    Code      Automation
    废弃代码         减少技术债          重构代码      测试自动化
Commit Code  Tests Passing  Code packaged     Changes Deployed Feature Flags enabled
   提交代码          测试通过       代码已打包     变更已部署     功能开关已开启     Coder
                                程序员

                            Bloomberg        31

## Page 32

Sustainability Achieved
达成可持续性
Congratulations, you’re a competent engineer
恭喜，你已成为一名合格的工程师




Bloomberg    32

## Page 33

    Software Engineering Pyramid
    软件工程能力金字塔







Decommission                Tech Debt  Refactor    Testing
  Old Code                  reduction    Code      Automation    Engineer
    废弃代码         减少技术债          重构代码      测试自动化      工程师
Commit Code  Tests Passing  Code packaged     Changes Deployed Feature Flags enabled
   提交代码          测试通过       代码已打包     变更已部署     功能开关已开启     Coder
                                程序员

                            Bloomberg        33

## Page 34

Change of Emphasis重点改变


 Probably not!
 d
 很可能并非如此


 Bloomberg    34

## Page 35

Rationale!核心理由

Why is sustainability not enough?为什么“可持续性”仍显不足？
Sustainability means to maintain the current state of the code. The
Code (development) itself does not live in a vacuum but lives in an ecosystem.
“可持续性”仅意味着维持代码的当前状态。然而，代码（开发工作）并非
存在于真空中，而是处于一个动态的生态系统之中。
Efforts are needed in the areas of manual toil reduction, capacity planning and
general observability within the system.我们必须持续投入精力，致力于减
少人工重复劳动、进行容量规划，并全面提升系统可观测性。



    Bloomberg    35

## Page 36

System Reliability 系统可靠性& Resiliency 系统弹性
What is system reliability?什么是系统可靠性？
System performs its intended function correctly with no
failures or downtime 系统能够正确执行其预期功能，且不出现故障或停
机。
What is system resiliency?什么是系统弹性？
The ability of the system to degrade gracefully in times of
stress as opposed to cease to function altogether系统在压力
下能够优雅降级，而非完全停止运行的能力




Bloomberg    36

## Page 37

System Reliability & Resiliency系统可靠性和弹性
Why do we care?为何关注系统可靠性与弹性？
Impacts on:因其直接影响：
    User trust用户信任
    Business continuity业务连续性
•   Brand reputation品牌声誉







    Bloomberg    37

## Page 38

System Reliability & Resiliency 系统可靠性和弹性
How healthy is your system?你的系统健康状况如何？
Are changes impacting your systems’ ( aggregate ) health?变更是否
正在影响系统的（整体）健康度？
Can you catch problems before your clients notice?您能否在客户察
觉之前发现问题？
Post-Incident investigation practices事件后调查实践是否健全？





    Bloomberg    38

## Page 39

System Reliability & Resiliency系统可靠性与弹性
Do you have System health monitoring?您是否具备系统健康度监控？
Operational Metrics运营指标
• Latency – Time taken to service a request (response time)延迟：处理请求所需时间（响
• 应时间）
   Traffic/Throughput - How much stress is the system taking, at a given time, from users
   or transactions processing through the service流量/吞吐量：系统在特定时刻承受的用
   户或事务处理压力
   q e.g., How is latency affected by throughput (requests per minute)例如：延迟如何受
      每分钟请求量的影响
• Saturation – overall capacity/utilization of the service (%CPU/RAM/disk net free,
   queue depths)饱和度：服务的整体容量/利用率（可用CPU/RAM/磁盘空间百分比、队列
• 深度等）
   Errors – Rate of failing requests to total requests – assuming requests are well-formed
   错误率：失败请求数占总请求数的比例（假设请求格式正确）
Any other metrics tailored for your system是否针对您的系统定制了其他关键指标？
        Bloomberg 39

## Page 40

System Reliability & Resiliency系统可靠性与弹性
Using System health monitoring运用系统健康监控:
•   Automatic alarms自动告警
    q Avoid “eyes on glass” 避免人工盯屏
•   q Imminent outages 预判潜在故障
    Monitoring Trends over spans of time长期趋势监控
    q Capacity planning容量规划支撑






    Bloomberg    40

## Page 41

Improvement Planning 改进规划
Improvement planning: Identifying areas of risk that need fixing or
optimization 改进规划：识别需要修复或优化的风险领域。
Broad scale functionality changes require大规模功能变更需要:
•   Multiple stages / iterations needed多阶段/多轮迭代
   q Complicated problems 复杂问题
   q Mitigate risk to current production降低对当前生产环境的风险
•   What are predicted timelines/effort for this?预计此项工作的时间线与
    投入如何？
   q Mid level time horizons so less certainty中长期规划存在不确定性
   q Non-trivial releases will need fixes/features added重要的版本发布往往
    需要伴随额外的修复或功能补充。
•   Many external dependencies众多外部依赖
   q Co-ordination and communication become critical and time consuming
    协调与沟通成为关键且耗时的环节

        Bloomberg        41

## Page 42

Architectural Design架构设计
Strategic local re-engineering: The targeted modification or
redevelopment of key parts of a system to achieve long-term
strategic goals 战略性局部重构：为实现长期战略目标，对
系统关键部分进行有针对性修改或重新开发。
•   Broad complex changes in system architecture 系统架构的广
•   泛复杂变更
    Vision for managing future performance 面向未来性能管理的
•   远景规划
    Where to target the system for most benefit确定系统优化的最
•   大效益点
    Leveraging existing technologies or introducing new ones利
    用现有技术或引入新技术


    Bloomberg    42

## Page 43

Strategic Vision战略愿景
Strategic vision: Long-term guiding objectives that defines where a software
system or organization aims to be and how its technology strategy will
evolve to that state.战略愿景：定义软件系统或组织长期发展目标，以及
技术战略如何演进至该状态的指导性原则。
Decisions that are long-term and influence future direction and are usually
beyond just the technical details.此类决策具有长期性，影响未来方向，
且通常超越纯技术细节范畴。
Forward looking and dealing with 其着眼于应对：
    Business shifts业务模式变迁
    Technology shifts技术格局演进
•   Future-proofing未来适应性保障
Usually weighing trade-offs for a number of solutions通常需要在多种解决方案之
间权衡取舍        Bloomberg        43

## Page 44

Rationale!核心逻辑

Why is sustainability not enough?为何“可持续性”仍不足够？
Sustainability means to maintain the current state of the code. The
Code (development) itself does not live in a vacuum but in an ecosystem.
“可持续性”仅指维持代码的现有状态。然而，代码（开发）本身并非存在于真空中，而是处于一
个动态生态系统之中。

Efforts are needed for future planning in the areas of manual toil reduction,
capacity planning and general observability within the system.
必须投入精力进行前瞻性规划，重点关注减少人工重复劳动、容量规划以及提升系统整体可观测
性。

Further efforts are required to construct a roadmap of where do we want to
go in the long term.此外，还需进一步构建长期发展路线图，明确我们未来要抵达的方向。

        Bloomberg 44

## Page 45

    Software Engineering Pyramid
    软件工程能力金字塔



Strategic        Architectural      SRE
 Vision             Design      Metrics
Decommission      Tech Debt  Refactor    Testing        Engineer
  Old Code        reduction    Code      Automation
 Commit    Tests     Code     Changes               Feature      Coder
  Code    Passing  packaged  Deployed               Flags enabled

                    Bloomberg                           45

## Page 46

System Reliability Achieved
达成系统可靠性
Congratulations, you’re a competent Systems Engineer
恭喜，你已经是一名合格的系统工程师




Bloomberg    46

## Page 47

Rationale!核心理由
Why is overall system reliability & resiliency not enough?为何整体系统可靠性与弹
性仍显不足？
Engineering must align with the business’ needs.工程必须与业务需求对齐。
Efforts are needed to communicate clearly and bidirectionally需要投入努力，
确保清晰、双向的沟通：
•   Engineering understands and aligns with the Business needs工程团队
    理解并协同业务需求
•   Business understands Engineering constraints & capabilities业务方理
    解工程约束与能力


    Bloomberg    47

## Page 48

Roadmaps路线图

What is a Roadmap meeting?什么是路线图会议？
A formal meeting where a group assembles to discuss the
current progress and future direction of a product or project
一种正式的会议形式，相关人员齐聚一堂，共同讨论产品或项目的当前进展
与未来方向
This is to ensure everyone is striving collaboratively towards
shared objectives这是为了确保每个人都能朝着共同的目标协同努力。




    Bloomberg    48

## Page 49

Business/Stakeholder involvement业务/利益相关方参与

Roadmap meeting composition (Roles)路线图会议的构成（角色）:
•   Product owner产品负责人
    q Create your roadmap and present all your strategic goals创建并展示路线图，阐述所
•   有战略目标
    Business analyst/proxy业务分析师/代理
•   q Explain user engagement and business goals解释用户参与度与业务目标
    Development representatives from each major area involved各主要领域
    开发代表
    q Explain roadblocks, effort and timelines说明当前障碍、工作量与时间线
•   q Flag risky shortcuts标识高风险捷径
    Executive stakeholder高管利益相关方
•   q When you need approval in your decision-making process需要决策批准时参与
    Product manager / Delivery specialist产品经理/交付专家
    q Long-range timelines负责长期时间线规划
        Bloomberg        49

## Page 50

Business/Stakeholder involvement业务/利益相关方参与

Roadmap meeting formula路线图会议的标准流程:
• Reviewing the Current Landscape审视当前状况
   q Presenting progress since last meeting汇报自上轮会议以来的进展
   q Listing any roadblocks and current status of each列出各项障碍及其当前状态
• Setting Strategic Direction设定战略方向
   q Where we are going?目标是什么？
   q How we are getting there?如何达成？
   q Gaining consensus/buy-in达成共识与获得支持
• Prioritization and Resource Allocation优先级排序与资源分配
   q In what order are items getting tackled?各项任务将按什么顺序处理？
   q By Whom?由谁负责？
• Action Planning and Collaboration行动计划与协作
   q Actionable items with clear success criteria and dates attached明确可执行任务，附清晰的完成标
     准和时间节点
   q Review long-term timelines审视长期时间表Bloomberg 50

## Page 51

Future planning Done?未来规划完成了吗？
Are you prepared for您是否已为以下情况做好准备：
    Software stability problems?软件稳定性问题？
    Security vulnerabilities?安全漏洞？
•   System scalability issues?系统可扩展性问题？
Are you ready for您是否已准备好应对:
    New technical opportunities?新技术机遇？
    New business opportunities?新商业机会？
    New regulation/restrictions?新法规/限制？
•   Staying competitive?保持竞争力？



    Bloomberg    51

## Page 52

Rationale!核心逻辑

Why is overall system reliability & resiliency not enough?为什么整体系统可
靠性和弹性仍然不够？
Engineering must align with the business’ needs.工程必须与业务需求对齐。
Efforts are needed to communicate clearly and bidirectionally需要努力实现
清晰、双向的沟通
   • Engineering understands and aligns with the Business needs工程团队
     理解并配合业务需求
   • Business understands Engineering constraints & capabilities业务团队
     理解工程的限制与能力
Because Engineering and Business need to collaborate, compromise, and
effectively communicate因为工程和业务需要协作、妥协，并进行有效沟
通 Bloomberg 52

## Page 53

    Software Engineering Pyramid
    软件工程能力金字塔

        needs      goals
Strategic        Architectural      SRE    Systems
 Vision             Design      Metrics    Engineer
Decommission      Tech. Debt  Refactor     Testing        Engineer
  Old Code        reduction     Code       Automation
 Commit    Tests     Code     Changes                 Feature      Coder
  Code    Passing  packaged  Deployed                 Flags enabled

                       Bloomberg                          53

## Page 54

Engineering & Business Alignment Achieved
工程与业务已达成对齐
Congratulations, you’re a Visionary
恭喜，您已成为一位远见者





Bloomberg    54

## Page 55

    Software Engineering Pyramid
    软件工程能力金字塔
        needs      goals      Visionary
Strategic        Architectural      SRE    Systems
 Vision             Design      Metrics    Engineer
Decommission      Tech. Debt  Refactor     Testing        Engineer
  Old Code        reduction     Code       Automation
 Commit    Tests     Code     Changes                 Feature      Coder
  Code    Passing  packaged  Deployed                 Flags enabled

                       Bloomberg                          55

## Page 56

Recap

Software Engineering: What level are you operating at?
    Future direction and market/business competitiveness
    System aggregate health and stability
    Code base health and sustainability
•   Feature Implementation / Bug fix






    Bloomberg    56

## Page 57

Recap

Software Engineering: When are you “Done”?
As a Coder: Features/Fixes tested and delivered everywhere in Production
As a Software Engineer: Maintaining codebase sustainability
As a Systems Engineer: Ensuring System stability/resiliency
As a Visionary: Ensuring Business buy-in and Engineering focus






    Bloomberg    57

## Page 58

Upshot
What have you achieved?
    Happy Customers / Business
    Retained Engineers
    Company poised to meet future challenges
•   Maturity in your Career







    Bloomberg    58

## Page 59

And Finally:

This presentation is well and truly
    Done
    Thank You

    Bloomberg        59

## Page 60

Other Engineering Talks:


Retiring The Singleton Pattern: Concrete Suggestions on What to Use Instead
Redesigning Legacy Systems: Keys to success
Managing External APIs in Enterprise Systems
Exceptions in C++: Better Design Through Analysis of Real-World Usage
Dependency Injection in C++: A Practical Guide
Mastering the Code Review Process: Boosting Code Quality in your Organization

Bloomberg        60

## Page 61

Questions?










Bloomberg    61

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/Pete_软件工程进阶金字塔.pdf]]`
