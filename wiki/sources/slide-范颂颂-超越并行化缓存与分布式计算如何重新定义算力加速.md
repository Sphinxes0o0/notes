---
type: source
source-type: slide
title: "范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速"
path: slides/范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速.pdf
source-md5: 2d5054d5f7e4537c735fa8dffde94c17
size: 6486 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速

> Ingested from `slides/范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.33 MB.

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

缓存与并行化重新定义算力加速
以解决优化Android （AOSP） 大型工程构建编译时间

## Page 7

目 录 CONTENTS
    AOSP项目构建基本现状
    IB在AOSP构建时间优化方案
    实测案例
    QA

## Page 8

AOSP构建环境现状及挑战
• 构建背景
门禁构建次数多，每周构建超过3000次；
总构建次数较多，每周构建超过2000次，日均构建376次；
个人构建占比多，且选择构建领域多，每周个人构建超过1500次；每周规划出版本10个以上，需要增加工具支撑编译再提效
编译耗时问题
大仓编译耗时：对于大型代码仓库，编译过程往往需要40分钟以上的时间，不仅降低了开发效率，也影响到项目的交付效率。
资源利用不充分：由于编译任务对资源的需求具有瞬时性且周期较短，往往单机编译时CPU被编译任务占满而无法正常开展开发工作，
其余未发起编译的开发人员的工作站同时又有大量空闲资源，造成工作站大部分时间内计算资源未得到充分利用。
可行优化建议
分布式构建系统：分布式构建系统不仅可以有效缩短编译时间，还可以通过将编译任务分配至多个工作站并行处理，解放单机性能且提
高编译效率。
虚拟化技术应用：采用虚拟化技术，可以在不增加物理硬件资源的情况下，动态分配计算能力给需要的应用程序或服务，从而更高效地
利用现有资源。
资源共享机制：建立内部资源共享平台，使团队成员能够在非高峰时段共享彼此的工作站资源进行大规模编译或其他计算密集型任务。
容器化方案：考虑使用容器化解决方案来封装开发环境，这样不仅可以简化环境搭建流程，还能更好地控制资源分配，实现更高效的资
源利用

## Page 9

AOSP构建编译瓶颈
 每一行代表一个CPU core

 构建主机有96个CPUcore

                从2小时到50分钟左右；    比如
                2. 在64core基础上继续增加核数，编译时间几乎没有明显减少

## Page 10

_(no text content on this page)_

## Page 11

    Incredibuild构建编译加速平台

    Hybrid Dev Acceleration Platform
    Caching        Distribution
通过重用历史构建结果，大幅减少        将编译任务分发至网络中其他主机，实
 编译任务数量，提升编译速度        现大规模并行编译，提升编译速度



    Combine parallelization with caching

## Page 12

BuildCache：编译产物共享

                         Index
                         A709873HSCNSC7N
    环境变量                 CD8J73HSJIUHJUYT
                         36OHTKHGHJUOOI

a.cpp  a.h               EYEINBXNIIEU8639

              Hash
    cl.exe    (MD5)          a.obj      b.obj  x.obj    i.obj
                             Cache EndPoint
    编译参数                 编译结果一致性验证项
                       • 编译源文件及依赖文件内容
                       • 编译器版本
                       • 编译环境变量
                       • 编译参数

## Page 13

   Incredibuild分布式编译

       编译主机

   COORDINATOR    INITIATOR
       动态计算资源池
  Dev        计算机”
process

                                      Helper协助机不需要部署任何代码/
   HELPER        HELPER    HELPER     编译构建工具
   笔记本, 云桌面       虚拟机, 容器  实例-instance

## Page 14

基于SharedCache的构建编译时间优化实践
产品代码库 PULL CI服务器 Contribute/write Shared Cache   更新写入Shared Cache； 限定
    COORDINATOR                                  （2）
                                                 务量，显著缩短编译编译等待时间；
开发编译主机     开发编译主机  开发编译主机










PUL










Read

## Page 15

_(no text content on this page)_

## Page 16

基于AOSP15/16 Vanelia构建benchmark

## Page 17

AOSP构建中可缓存及分布式任务列表

## Page 18

某大型OEM AOSP Build Monitor[part 1]










Gradle (Java apps) stuff
total of ~16 minutes
(Accelerated in the next
Incredibuild version)

## Page 19

某大型OEM AOSP Build Monitor[part 2]







Gradle (Java apps) stuff                      Gradle (Java apps) stuff
total of ~16 minutes                          total of ~16 minutes
(Accelerated in the next     Distributed      (Accelerated in the next
Incredibuild version)        appcompat.sh     Incredibuild version)
                             script

## Page 20

Incredibuild Benefit

        Faster Single- Optimized Shared Cache &
        Build Throughput & Distribution.
        Cloud Costs Extendable

      Zero Changes to CI & Developers. Enterprise
      Tools and Scripts Build Agnostic. Support

        Data, Auditing, Compliance and Security

## Page 21

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/范颂颂_超越并行化：缓存与分布式计算如何重新定义算力加速.pdf]]`
