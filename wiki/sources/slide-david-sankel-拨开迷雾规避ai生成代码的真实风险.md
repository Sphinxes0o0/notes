---
type: source
source-type: slide
title: "David Sankel_拨开迷雾：规避AI生成代码的真实风险"
path: slides/David Sankel_拨开迷雾：规避AI生成代码的真实风险.pdf
size: 2004 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# David Sankel_拨开迷雾：规避AI生成代码的真实风险

> Ingested from `slides/David Sankel_拨开迷雾：规避AI生成代码的真实风险.pdf` via `lit parse` on 2026-06-04.
> Source file: 1.96 MB.

## Page 1

© 2025 Adobe. All Rights Reserved.

## Page 2

© 2025 Adobe. All Rights Reserved.

## Page 3

© 2025 Adobe. All Rights Reserved.

## Page 4

© 2025 Adobe. All Rights Reserved.

## Page 5

© 2025 Adobe. All Rights Reserved.

## Page 6

Beyond the
Hype
拨开迷雾
Mitigating the Real
Risks of AI-Generated
Code
规避AI生成代码的真实风险
David Sankel | Principal Scientist

      Im
      a
      ge
      generated
      with
      A
      d
      o
      be
      Firefly

## Page 7

Who am I?
自我介绍
§ Principal Scientist at Adobe/Adobe
首席科学家
§ Leading the Tech Foundations Group
管理一个技术基础团队
§ Also lead Software Technology Lab
以及一个软件技术实验室




为std::variant、std::input_vector、反射和语言的
§ Director, Boost Foundation/Boost
许多其他方面做出了贡献

基金会负责人
    © 2024 Adobe. All Rights Reserved. Adobe Confidential.    © 2025 Adobe. All Rights Reserved.

## Page 8

The promise vs. the reality/承诺与现实
鼓吹:
现实: 我们正面临“Day 2”困境（相对于“Day 1”的理想化， “Day 2”的混乱现实）.
§ The Goal of this Talk
本次演讲的目的
超越“工具犯错”的简单论断
§ Address stability, technical debt, and human debt.
§ Provide a checklist for safe integration.
提供安全性集成检查单

    © 2025 Adobe. All Rights Reserved.     8

## Page 9

Problem #1: This talk is already out of date
问题 #1: 这个演讲已经过时了
§ The landscape
全景
主要的几个大模型几乎每周都会发布更新 (Claude, Chat-GPT, Gemini, Copilot)
每天都有新的 IDE 集成工具
§ The trap
困境
§ Spending more time configuring tools than using them.
更多的时间花在工具配置上，而不是使用这些工具
持续的上下文切换破坏工作流（的连续性）

    © 2025 Adobe. All Rights Reserved.     9

## Page 10

Mitigation #1: Strategic stability
规避措施 #1: 战略稳定
§ Pilot programs
试点项目
§ Don’t roll out every update to the whole organization immediately.
指定一个小型“探索”团队来测试新工具
不要把每一次更新都立即推送给整个组织
经验法则：测试周期应按“月”来算，而不是“天”
§ Stick & learn:
坚持并持续学习
§ Knowledge sharing
选定一个工具集，持续使用足够长的时间，以真正掌握它的各种特性和小毛病

知识共享
创建内部空间（Slack 频道、Wiki），用于分享“我学到了什么”，而不仅仅是“看看这个很酷的演示”
    © 2025 Adobe. All Rights Reserved.     10

## Page 11

Problem #2: The hallucination
trap
问题 #2: 幻觉陷阱

      而不是正确性
 § Code looks idiomatic
 § Variable names make sense
  代码看起来很地
  变量名也很有达意
  但是却调用了一个不存在的函数

  我曾经花了几个小时调试一个“幻想”出来的环境变量，AI 坚持这个东西存
 在

 斯坦福学者 (Perry 等人):使用人工智能助手的开发人员编写的代码不太安
 全，却对它更有信心
      © 2024 Adobe. All Rights Reserved. Adobe Confidential.
      11        © 2025 Adobe. All Rights Reserved.

## Page 12

Mitigation #2: A new review mindset
规避措施 #2: 新的审查心态
§ Read the docs
阅读文档
当看到一个不认识的函数，首先检查文档，而不是假设这是 AI 知道的某个秘密 API
§ The knowledge rule
知识规则
§ Never accept code if you don’t possess the knowledge to write it yourself.
如果掌握的知识不足以让你能自己编写代码，就不要接受生成的代码
如果 AI 使用了一个你不知道的模式，先学习它，然后再接受
§ Test audit
测试审查
§ Do not just run tests. Read the tests. Ensure they actually test the logic, not just the syntax.
不要简单运行测试，而是阅读测试代码，确保它们逻辑正确，而不是语法正确
    © 2025 Adobe. All Rights Reserved.     12

## Page 13

Problem #3: The bloat crisis
问题 #3: 膨胀危机
§ Code is a liability, not an asset
代码是一种负债，不是资产
代码行 = 故障多 = 更难维护
AI 更愿意添加新代码，而不是重构旧代码
§ The data
数据

我们正在构建一座 “write-only” 代码山
    © 2024 Adobe. All Rights Reserved. Adobe Confidential.
    13        © 2025 Adobe. All Rights Reserved.

## Page 14

Mitigation #3: The senior engineer untervention
规避措施 #3: 资深工程师介入
§ The role of the senior engineer
资深工程师角色
§ Start checking for Architecture
§ The checklist
开始检查架构

检查单

这 50 行 AI 生成的函数是否可以用 std::algorithm 替换?
    © 2025 Adobe. All Rights Reserved.     14

## Page 15

Problem #4: Architectural drift
问题 #4: 架构偏离
§ The issue
问题                                                             .
§ It lacks the historical context of your specific architecture.
§ Symptoms
缺少关于你的特定架构的历史上下文
症状

不一致: 一个函数可以工作，但看起来像是从其他项目粘贴的
    © 2025 Adobe. All Rights Reserved.     15

## Page 16

Mitigation #4: The “Spec Check”
规避措施 #4: “规格检查(Spec Check)”
§ Shift left
管控前置
§ Don’t review the code first. Review the plan.
§ The workflow
§

工作流

§ The critical prompt: "Before you write code, list the existing classes and patterns you intend to use. "
§

§ The benefit
§ 关键提示：“在编写代码之前，列出您打算使用的现有类和模式。”

收益

  代码写完再修改这样的错误需要 30 分钟        © 2025 Adobe. All Rights Reserved.      16

## Page 17

Problem #5: The death spiral
问题 #5: 死亡螺旋
§ The scenario
 场景

 它回答有点轻微错误

 它又破坏了一些之前正确的东西（按下葫芦浮起瓢）
§ The result
 后果
 一个 15 分钟的任务花费你 1 个小时时间

     © 2025 Adobe. All Rights Reserved. 17

## Page 18

Mitigation #5: Know when to fold
规避措施 #5:要知道什么时候该弃牌（及时止损）
§ The stop loss
 止损
 § Delete the code. Write it yourself.
§ Reality check
 删除这些代码，自己写

 面对现实
 § Don’t be afraid to code. That’s still your job.
 不要害怕写代码，这是你的工作

     © 2025 Adobe. All Rights Reserved.     18

## Page 19

Problem #6: The erosion of expertise
问题 #6: 侵蚀专业知识
编程的两个输出:
1.
1. 知识 (开发者的神经网络).
§ The risk
风险
§ The struggle is where learning happens.
   而正是在那些努力挣扎中，学习才发生
§ Without learning, you cannot architect complex systems or debug production outages.
   没有这些学习，你无法设计复杂系统，也无法排查生产事故
    © 2025 Adobe. All Rights Reserved.     19

## Page 20

Mitigation #6: Intentional friction
规避措施 #6: 人为引入阻力
§ The framework
原则
核心基础设施 / 长期逻辑? → 把 AI 当作助手，而不是驾驶员
§ My experience
我的经验
如果当初让 AI 生成这些配置，出了问题我就无法自己修复
§ Recommendation
建议
决定你真正想学什么，保护好努力（ struggle ）的过程
    © 2025 Adobe. All Rights Reserved. 20

## Page 21

Conclusion: The safe path forward
结论:稳妥前行之道
§ The checklist
清单


保护学习: 不要把你的专业能力外包给 AI
§ Final thoughts
最后的想法
§ You are the craftsman.
§ Don’t let the tool decide what you build.
你才是那个手艺人
不要让工具替你决定要建造什么
    © 2025 Adobe. All Rights Reserved.     21

## Page 22

Q & A





© 2025 Adobe. All Rights Reserved. 22

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/David Sankel_拨开迷雾：规避AI生成代码的真实风险.pdf]]`
