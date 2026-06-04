---
type: source
source-type: slide
title: "易慧民_RecIS：C++ 驱动的高性能推荐训练框架优化实践"
path: slides/易慧民_RecIS：C++ 驱动的高性能推荐训练框架优化实践.pdf
size: 5447 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 易慧民_RecIS：C++ 驱动的高性能推荐训练框架优化实践

> Ingested from `slides/易慧民_RecIS：C++ 驱动的高性能推荐训练框架优化实践.pdf` via `lit parse` on 2026-06-04.
> Source file: 5.32 MB.

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

RecIS：C++ 驱动的高性能推荐系统训
 练优化实践


 阿里巴巴-平台技术
 易慧民(须焰)

## Page 7

目 录 CONTENTS
    背景：计算演进和衡量指标
    分析：推荐系统的性能挑战
    优化：RecIS C++工程实践
    总结和展望

## Page 8

背景：计算演进和衡量指标

## Page 9

"The Free Lunch Is Over"

## Page 10

"The Free Lunch Is Over"

                        • 免费午餐时代
                        • ~2005
                        • 单核
                        • 摩尔定律
                        • 午餐终结与 CPU 的困境
                        • ~2015
                        • 主频撞墙
                        • 多核
                        • GPU 的暴力美学
                        • ~now
                        • 深度学习计算
                        • 海量并行和专用电路

## Page 11

GPU VS. CPU

     • CPU
           • 片上面积50%以上是控
             制单元
           • 流水线、分支预测、乱
             序执行
           • 低延迟
     • GPU
           • 片上面积几乎全是计算
           单元
           • 海量的可并行计算，能
           够以计算掩盖延迟
           • 高吞吐

## Page 12

GPU计算优化-Compute Wall-高并发&DSA










• H100为例
• SM 132个        • Peak FP16/BF16: 134 TFLOPS
• ALU(Cuda Core)    • Peak FP16/BF16 TensorCore: 989T FLOPS
• 32*4*132 = 16896

## Page 13

GPU计算优化-Memory Wall

                   • 访存总比计算慢
                   • 容量与速度的矛盾
                   • 距离
                   • 移动数据比计算数据更
                   费电
                   • Roofline
                   • 只有计算密度(算存比)足
                   够大，才有机会打满峰
                   值算力

## Page 14

GPU计算优化-Memory Wall-Memory Hierarchy










矩阵乘法通过分块计算，把重复访存从Global Memory
转移到Shared Memory和寄存器。

## Page 15

GAP 大语言模型 VS. 推荐模型
• 大语言模型 ~ 50%     • 推荐模型 ~ 10%

## Page 16

分析：推荐系统的性能挑战

## Page 17

       推荐模型VS. 大模型

Ops                    LLM       RecModel     BottleNeck     • IO密集
Input tokens/Batch     ~10k      ~1B          CPU            • 分列计算
Input Columns          ~1        ~1000        Python         • 巨大的Embedding table
                                                             • 算子数量/种类多
Emb Tables             1         ~1000        Python         • 计算密度相对低

Table Rows             ~100k     ~100B        Mem,CPU

Ops Count              ~500      ~50000       Python


Ops Type               Gemm 70%     Concat/Split/Reduce/bn Compute,Mem
                                    70%

## Page 18

推荐模型的4重性能墙

• Comput Wall（最普遍问题）        • CPU Wall（历史问题）
• 稠密部分的计算效率        • CPU的样本流水线
• 大模型结合        • CPU的Embedding Table

• Python Wall（Pytorch带来的问题）    • Memory Wall（最核心问题）
• 人工特征工程导致的千列特征        • 稀疏部分都是访存密集型
• 每列都对应着特征处理和Embedding查询、    • 算子的访存效率
计算、更新                        • 原子操作的低效
• 数万次python构图操作

## Page 19

优化：RecIS C++工程实践

## Page 20

RecIS

## Page 21

Python Wall – Modeling
                      • Python
                      • Frontend
                      • Control Flow
                      • Model Building
                      • C++
                      • Backend
                      • Data Flow
                      • Tensor Computation

## Page 22

Python Wall - DataIO
    • Dataset + DataLoader
                    • Pythonic with GIL
                    • Row-wise Reading
                    • CPU Processing
                    • Copy to GPU
                    • Multi-Processing
            • DataIO
                    • C++
                    • Columnar Reading
                    • To GPU First
                    • GPU Processing
                    • Multi-Threading

## Page 23

CPU Wall-硬件趋势 – 访存效率

                    2020~2025
                    • CPU Memory
                    • DDR4 * 6 Channels
                    • DDR5 * 8 Channels
                    • Cap: 0.5 - 1TB
                    • BW: 200 – 400 GBps
                    • GPU Memory
                    • HBM2 * 3 die
                    • HBM3e * 8 die
                    • Cap: 32-192 GB
                    • BW: 1-8 TBps
                    • GPU/CPU BW
                    • ~10 - ~100+

## Page 24

CPU Wall – GPU HashTable

                        • GPU HashTable
                        • Open Addressing
                        • Tile-based Probing
                        • Atomic CAS
                        • Warp Intrinsics
                        • GPU Slabs
                        • Logically Contiguous
                        • Merge & Split
                        • Logical Fusion
                        • Full-Hash Sharding
                        • Functions
                        • Auto Scaling
                        • Eviction Policy

## Page 25

Memory Wall – Sparse Fusion

                           • Vertical Fusion
                           • Hash+Bucketize
                           • Unique + Partition w/o
                           stitch
                           • Tile + Reduce
                           • Horizontal Fusion
                           • All Columns with same
                           ops

## Page 26

Memory Wall – Vectorized Access










• Coalesced Access    • Vectorized Access
                      • LDG.64
                      • LDG.128

## Page 27

Memory Wall – Atomic Optimizatioin










• Warp Shuffle • Block Shared Memory  • Global Memory

## Page 28

总结和展望

## Page 29

优化成果

• 从TensorFlow全面转向Pytorch生态
• 比优化前提升2~3倍
• 超过TensorFlow性能(30%~150%)

## Page 30

总结和展望

• 推荐模型和大语言模型有显著的不同             • C++→python
• Python/CPU/访存/计算 维度有不同瓶颈     • 访存→算力
• 需要依赖C++贴合硬件特性充分优化，才能         • 系统→算法
 逼近算力极限

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/易慧民_RecIS：C++ 驱动的高性能推荐训练框架优化实践.pdf]]`
