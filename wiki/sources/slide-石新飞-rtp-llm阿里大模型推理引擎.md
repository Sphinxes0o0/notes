---
type: source
source-type: slide
title: "石新飞_RTP-LLM：阿里大模型推理引擎"
path: slides/石新飞_RTP-LLM：阿里大模型推理引擎.pdf
source-md5: 743fe3e6c2adb59a2c3b187c1de38a07
size: 6891 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 石新飞_RTP-LLM：阿里大模型推理引擎

> Ingested from `slides/石新飞_RTP-LLM：阿里大模型推理引擎.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.73 MB.

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

RTP-LLM大模型推理及分布式架构
石新飞
阿里巴巴高级技术专家

## Page 7

目 录 CONTENTS
    01: 大模型推理介绍
    02: 推理优化
    03: MOE专家模型
    04: MTP投机采样
    05: 分布式架构
    06: 未来展望

## Page 8

_(no text content on this page)_

## Page 9

大模型推理介绍

## Page 10

大模型推理介绍

## Page 11

推理阶段

## Page 12

_(no text content on this page)_

## Page 13

Continuous Batching

## Page 14

Continuous Batching 的问题










凑批越大，Decode 被 Prefill 打断的次数越多，TPOT（Time Per Output Token）不稳定

## Page 15

Continuous Batching -> PD分离










• 稳定的 TPOT
• Prefill 和 Decode 根据计算特性异构部署，更好的利用 GPU 资源

## Page 16

PD分离










•   使用 RDMA 进行机器间的 KV Cache 传输
•   分层传输，用计算掩盖大部分传输消耗，减少请求总时间

## Page 17

PD分离






l 多 TP（Tensor Parallelism）
l 不对称 TP
l 多种 Attention 类型

## Page 18

分布式 CacheStore

## Page 19

_(no text content on this page)_

## Page 20

MOE










 通过Router进行专家选择的方式，在增加模型规模的同时，降低单个Token的成本

## Page 21

  MOE：
      Qwen Coder 模型部署形式
      DP Rank 0                         2DP           DP Rank 1

      Input 0                                         Input 1

  Attention    Attn0  Attn1  Attn2  Attn3  4TP        Attn0    Attn1  Attn2  Attn3  4TP

      All reduce                                      All reduce

                    MoE Route                                MoE Route

               H0    H1      H2     H3            a2a    H0    H1     H2     H3

 FFN                                                                             8EP
(MoE)        E0      E1      E2     E3                E4       E5     E6     E7
               H0    H1      H2     H3            a2a    H0    H1     H2     H3

## Page 22

   MOE MicroBatch Overlap
Prefill

Decode

## Page 23

MOE 专家均衡

## Page 24

_(no text content on this page)_

## Page 25

MTP 投机采样


    Normal                                                      投机采样(MTP)

               Main             Step 1(                  ) Step 2 ( ) Step 3 ( )                     Main Model
               Model
                   …                                                     …
Forward k                        Forward k                                        input        8     9    10 11
               inp          8      input         7   8           …
               ut                                                    …            output       9     10 11 12
              outp          9                    9
               ut                 output                    10       11                        9     10 11     accept 9,10
                                                                                  rejection              9     10 11
Forward k+1    inp          9                                                     sample       9     10 11 12
               ut           10    Forward k+1                                     input        11 12 13 14
              outp
               ut                  input         9   10 11       …   …
                                                     8                            output       12 13 14 15
Forward k+2    inp          10    output         12         13       14                        12 13 14     accept 12,13,14
               ut                                                                 rejection              12 13 14 15
              outp          11                                                    sample       12 13 14 15
               ut      …                                                 …

                                单步时延上升，但每步可以生成更多token，总的时延下降

## Page 26

MTP 投机采样实现

## Page 27

MTP 投机采样步数对于性能影响

## Page 28

加载加速





 加载时间 30 min -> 50 s

## Page 29

_(no text content on this page)_

## Page 30

分布式架构

## Page 31

      分布式架构效果

压测条件          指标                   无 Master     有 Master
QPS=225       TTFT Avg             1.08s        479ms（下降 50%）
输入≈7600 左右
输出≈650 左右     TTFT P99             4.29s        742ms
              prefill 排队时间 avg     1.99s        120ms
              prefill 排队时间 p99     3.95s        197ms

## Page 32

_(no text content on this page)_

## Page 33

Py Model

现状：
• 基于C++开发和调试困难，无法形成生态

期望：
• 使用Python为每个模型建立描述（类比Hugging face）
• 使用CUDA Graph 优化CPU开销

好处：
• 更方便的开发和调试，快速适配新模型和功能，和开源社区共建生态

## Page 34

Attention 和 FFN 分离










长序列下，Attention的KV Cache占用量线性增长的问题逐渐凸显

## Page 35

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: ``
