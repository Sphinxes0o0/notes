---
type: source
source-type: slide
title: "刘童旋_基于C++构建大模型推理优化框架xLLM实践"
path: slides/刘童旋_基于C++构建大模型推理优化框架xLLM实践.pdf
source-md5: fdbcec275a27fff7e1d48b03e8a0cb01
size: 5922 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 刘童旋_基于C++构建大模型推理优化框架xLLM实践

> Ingested from `slides/刘童旋_基于C++构建大模型推理优化框架xLLM实践.pdf` via `lit parse` on 2026-06-04.
> Source file: 5.78 MB.

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

基于C++构建大模型推理优化
框架xLLM实践
刘童璇

## Page 7

    电商场景的 AI 需求


    Generative AI          Agentic AI             Physical AI
• AI 生成商品图生成、短视频、AI • AI 生成商品图生成、短视频、AI • AI 生成商品图生成、短视频、AI
    AI 生成商品图、短视频、AI 营销内容   AI 客服与售后管理、AI 经营托管、   自动分拣机器人、智能空间、自动驾
    营销内容生成、AI 数字人          营销内容生成、AI 数字人         营销内容生成、AI 数字人
    生成、AI 数字人              AI 仓配优化 、AI 交互式推荐     驶

## Page 8

   电商场景 AI 推理的挑战


• 大模型、多模态、文生图/视频、生成式推荐等多场景多模型的推理效率的挑战

• 不同模型采用的不同推理框架，带来无法实现多模型间的协同的挑战

• 输入的多样性，硬件异构，用户的优先级，不同 SLO，分布式调度的挑战

• 模型的规模、效果和效率的平衡，性能优化和轻量化的挑战

        为什么选择C++来构建大模型推理引擎？

## Page 9

大模型推理引擎xLLM



大模型  多模态  文生图/视频  生成式推荐     深度解耦的分布式设计，推理从单机走向集群
                            • 动态PD分离、结合大规模专家负载均衡
                            • 混合的EPD分离架构，异构实例协同推理
                            • 全局多级KV Cache，推理内存池化
                            全局智能调度，严格SLO下最大化资源利用率
                            • 在离线任务的统一调度和弹性调度
                            • 多优先级的用户请求调度
                            • 请求快迁移和快恢复的容错机制
                            Runtime运行时，极致性能优化
                            • 全图化、多层流水线的执行引擎
                            • xTensor显存管理优化
                            • 高效融合算子库、异构硬件、通算并行

## Page 10

xLLM - 自适应PD调度-问题和挑战


• 初期 PD 分离架构中 Prefill 和 Decode 节点比例固定
• 实际场景的Input 和 Output 变化显著，PD 资源浪费

## Page 11

xLLM - 自适应PD调度-实现方案


• P和D 可自动切换身份
• PD 间 KV Cache迁移和请求可平滑迁移

## Page 12

xLLM - 自适应PD调度-实验效果



• 在不同模型上，自适应PD调度可以实现吞吐提升  • 自适应PD调度使用的SLO Aware调度策略对比Mini
1.59X-2.2X        Load和Round Robin具有显著的效果优势

## Page 13

xLLM – EPD分离调度-问题和挑战


• Encoder/Prefill/Decode分别不同的计算、访存特点
• 不同阶段的Stage，最优化的Batch Size不同

## Page 14

xLLM – EPD分离调度-实现方案


 • 通过将编码、预填充和解码三个阶段调度到不同的异构推理实例上，在各个阶段之间重新分配资源

## Page 15

xLLM – EPD分离调度-实验效果




• 在不同模型上，EPD分离调度可以实现吞吐提升最  • EPD调度的消融实验，可以看到EPD分离架构和调度
多3.7X的吞吐提升        优化各自独立带来的性能提升

## Page 16

xLLM – 在离线统一调度-问题和挑战


 • 请求波峰波谷的变化显著，尖峰时负载高且抖动剧烈
 • 基于传统潮汐调度的在离线混部调度成本高

## Page 17

xLLM – 在离线统一调度-实现方案



 • 负载低时，可以快速调度，插入离线请求执行推理
 • 负载高时，驱逐离线请求的KV Cache，并保存离线请求

## Page 18

xLLM – 在离线统一调度-实验效果


 • 在离线统一调度策略，可以提供稳定的SLO性能，并带来最多3X的离线吞吐提升

## Page 19

xLLM – 多层流水线执行-问题和挑战

• 调度和模型执行串行执行，导致GPU/NPU利用率低
• 单流交替执行计算、通信，计算/通信资源利用不充分
• 计算和数据搬运串行，无法打满算力






Bubble

## Page 20

xLLM – 多层流水线执行-实现方案


• CPU调度和GPU/NPU计算异步流水线执行
• 不同Layer的GPU/NPU计算和通信异步流水线执行
• 不同计算单元、访存并行流水线执行，如Cube/Vector/MTE等

## Page 21

xLLM – 多层流水线执行-实验效果


• 在不同模型上基于多级流水线的能力，可以带来5%-10%吞吐的提升，并且随着模型尺寸变小，收益更加明显

## Page 22

xLLM – 生成式推荐

问题和挑战       实现方案

• 一次推理产出512-4096个semantic id (beam    • 基于C++实现的xLLM具备巨大的优势，通过实现高
width)，经过固定个step (4次) 产出完整的item id    性能的Scheduler、Filter机制、自定义算子

## Page 23

xLLM – 全局KV Cache







• 通过构建全局KV Cache
实现高效的 Cache共享
• 实现基于KV Cache的负
载均衡策略
• 构建高效的Failover策略

## Page 24

xLLM –EP负载均衡

## Page 25

xLLM – xTensor高效显存管理

## Page 26

xLLM – DP Load Balance

## Page 27

xLLM – 投机推理优化

## Page 28

xLLM性能效果

## Page 29

xLLM性能效果

## Page 30

xLLM性能效果

## Page 31

业务落地效果

可交互导购  商品对比  商品总结  购物建议    商品理解










TP99 下降 50%，资源节省 ～60%，支持业务场景效果     大模型吞吐提升 3X，助力模型推理成本节省 ～ 70%，多模态大
UCVR提升 +5%，活跃用户占比提升 +2%            模型推理吞吐提升 ～ 20X，支持标签的实效性提升 10X 以上

## Page 32

AI 推理下一步思考


  如何做到规模、效率、成本的既要又要还要？


  如何解决集群中多模型、动态流量的最大化效率？


  如何做到模型分布式推理的可解释和可调试？

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/刘童旋_基于C++构建大模型推理优化框架xLLM实践.pdf]]`
