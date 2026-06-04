---
type: source
source-type: slide
title: "田文鑫_具身机器人多仓源码构建体系"
path: slides/田文鑫_具身机器人多仓源码构建体系.pdf
size: 8274 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 田文鑫_具身机器人多仓源码构建体系

> Ingested from `slides/田文鑫_具身机器人多仓源码构建体系.pdf` via `lit parse` on 2026-06-04.
> Source file: 8.08 MB.

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

具身机器人多仓源码构建体系
田文鑫@Agibot

## Page 7

目 录 CONTENTS
    智元机器人软件架构
    代码仓库管理方案
    CICD自动化方案
    基于Bazel的源码构建方案
    方案开源计划

## Page 8

_(no text content on this page)_

## Page 9

_(no text content on this page)_

## Page 10

端侧软件架构

## Page 11

端侧软件架构
- 相比电动汽车，具身机器人是把智驾系统和座舱系统，整合到了一起
- 大脑负责交互，作业规划，小脑负责运动，被动安全
- 控制算法相比智驾更复杂，实时性要求更高，大多数的电机都需要500-1000hz的控制频率驱动
- 目前的量产产品还未实现一段式端到端架构，整个系统的模块数量相对较多

## Page 12

_(no text content on this page)_

## Page 13

多仓库如何高效管理

## Page 14

多仓库如何高效管理
- 多仓架构，分集成仓，模块仓，模块仓有相对自主权，信息安全相对可控
- 集成仓负责整合所有模块仓版本，管理公共第三方依赖，实现编译工具链，实现部署流程
- 模块仓负责各软件，算法，嵌入式模块的业务实现，依赖集成仓编译，实现版本对齐
- 集成仓直接关联模块仓git commit，做到全系统源码编译，版本精准对齐
- 基于同名分支的思路，实现多仓联合开发的高效分支管理

## Page 15

分支管理方案

## Page 16

分支管理方案
- 快速基于MR Target分支为Base出版本提测，免去手动更新集成仓source.yaml的麻烦
- 多仓库修改仅需基于任意同名分支mr触发pipeline
- MR 合并时，只要所有同名分支mr符合合并条件，可以通过任意mr触发批量同步合并

## Page 17

_(no text content on this page)_

## Page 18

基于Gitlab的代码管理服务

## Page 19

MR自动化处理过程

## Page 20

_(no text content on this page)_

## Page 21

为什么选择Bazel
- 易读的构建脚本
- 易用的分布式构建方案
- 开箱即用的gitlab和artifactory集成
- 多语言，多平台，易于扩展
- 通过实现bazel cmake rule，可以实现cmake项目的兼容

## Page 22

模块和OTA包构建方案

## Page 23

_(no text content on this page)_

## Page 24

灵渠OS

## Page 25

开源节奏

## Page 26

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/田文鑫_具身机器人多仓源码构建体系.pdf]]`
