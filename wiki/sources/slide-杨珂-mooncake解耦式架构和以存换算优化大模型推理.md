---
type: source
source-type: slide
title: "杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理"
path: slides/杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理.pdf
source-md5: cba28171993bef953e07adbb80c4bd84
size: 12722 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理

> Ingested from `slides/杨珂_Mooncake：解耦式架构和以存换算，优化大模型推理.pdf` via `lit parse` on 2026-06-04.
> Source file: 12.42 MB.

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

Mooncake：
解耦式架构和以存换算，优化大模型推理

杨珂 趋境科技技术专家 | Mooncake 核心贡献者
Ke Yang, Approaching.AI Tech Expert | Mooncake Core Contributor

## Page 7

目 录 CONTENTS

  Background:LLM Inference in Long-context Era
  Mooncake:A KVCache-centric Disaggregated Architecture
  Mooncake × LLM Ecosystem Collaboration

## Page 8

Current Paradigm:
Data + Algorithm + Hardware = Intelligence

                                 Algorithm - Transformer is
                                 all we need?
Data – Big Data is Everywhere        Intelligence – AI Become Everywhere Too







Hardware – Huang’s
Law Take Over

## Page 9

The Old Scaling Law is Slowing down



 Larger
 Model

                                  BUT, who use it?
 Growing         More
 Computing       Data     •   Performance gains from adding more parameters are
 Power                        increasingly limited.
                          •   It is becoming difficult to gather enough high-quality data to
 The Old     Scaling Law      feed ultra-large models.

## Page 10

Everyone is Talking about Scaling Law But the Real Question
is What to Scale?










https://www.reuters.com/technology/artificial-
intelligence/openai-rivals-seek-new-path-smarter-ai-
current-methods-hit-limitations-2024-11-11/

## Page 11

More Data + Larger Model + Longer Context =  Higher Intelligence

Long input - Kimi        Long output – DeepSeek R1






In March 2024, Kimi became one of the leading     In January 2025, DeepSeek R1 quickly rose to
large model services thanks to its strong long-
context (long-input) processing capability.       become one of the most renowned large model
                                                  services for its strong reasoning (long-output)
                                                  capability.

## Page 12

More Data + Larger Model + Longer Context =  Higher Intelligence


Chain-of-Thought

## Page 13

More Data + Larger Model + Longer Context =  Higher Intelligence
AI applications are evolving from simple chat to complex agent-based systems.









Single-turn, short inputs/outputs    Multi-turn, complex execution
    topologies, long inputs/outputs.

## Page 14

    More Data + Larger Model + Longer Context =  heavier workload



Lack of Computing and Higer Inference Cost  Longer Response Time
  Memory Resources
        •     Inference costs are skyrocketing
                      •   Amazon reports that over 90% of costs come
                          from inference rather than training
                      •   DeepSeek R1’s training cost is only $6M, but
                          its projected annual inference cost far
                          exceeds $32M.

    One of the key bottlenecks in the long-context era:

## Page 15

Value Engineering

 Value      =    Function
     Cost


 solution: KVCache reuse + P/D disaggregation

## Page 16

Introduction to LLM Inference

       Token: In large-model inference, a token is the smallest unit of text (such as a word or
       subword) that the model processes and generates step by step.





    KV: Each token produces a Key tensor and a Value tensor.
    Prefill stage: Processes all input tokens in parallel to generate their KV tensors.
    Decode stage: Generates new tokens one by one, each time needing to access all previous
    tokens’ KV tensors.
    KV cache: Stores computed KV tensors to avoid redundant computation.

## Page 17

    Introduction to LLM Inference

    Prefill        Decode
      LLM            LLM    LLM                    LLM
  iteration 1    iteration 2    iteration 3    iteration 4

What day is it        KV     Today KV    is    KV Friday  END
    today?        Cache        Cache        Cache


    Process all inputs in parallel,    Generate one output at a time,
    compute-intensive        bandwidth-intensive

## Page 18

Introduction to P/D Disaggregation
Prefill and decode have different computational characteristics and SLO
                                  Prefill    Decode

Metrics          TTFT                    TBT
         (Time To First Token)  (Time Between Tokens)

           High :100ms ~ 10s    Low: Less than 100ms
Value        (Depending on       (Aligns with human
             input length)         reading speed)
               Parallel,           Auto-Regressive
Computation  Compute-bound        (token by token),
                                    Memory-bound

## Page 19

Introduction to P/D Disaggregation

P/D Disaggregation: Decouple prefill    Two implementation methods
and decode into different nodes








Intermediate results
    Picture: https://zhuanlan.zhihu.com/p/1906741007606878764
KVCache

## Page 20

  Advantage of P/D Disaggregation

                       Advantage  : Mapping prefill and
                       decode to the most suitable hardware

       H800                H20
Hardwar
       80GB VRAM，3.3 TBps
   e        ~ 1 PFLOPS   96GB VRAM，4 TBps
    Spec                   ~ 200 TFLOPS
       For Prefill!        For Decode!
    Best    Allround,        Bandwidth/$
   for     especially for TFLOPS/$
                           !!! The price numbers are not accurate, just a demonstration!

## Page 21

    Advantage of P/D Disaggregation

    Advantage : Decouple scheduling and parallelization
    strategies to improve model FLOP utilization (MFU).

        Prefill-first
                                                       •     Chunked Prefill can increase MFU by inlining prefill
                                                             requests into the decode batch.
    Chunked Prefill[1]                                 •     However, physical P/D separation provides more
                                                             effective control over TBT and other SLO metrics.
                                                       •     In scenarios with strict SLO requirements, physical
        P/D Disaggregation                                   P/D separation delivers higher throughput

    Decode-first
        MFU










TBT










    Worse








    Better

## Page 22

  Reuse KV Cache between Requests

“What day is it today”         “What day is it tomorrow”

  Prefill for Request I        Prefill for Request II

  What        What             What                What              The KV cache of
  day        day               Reuse KV Cache  day     day           the shared prefix
  is                       is                  is                    can be reused to
                                                       is            avoid redundant
  it                       it                  it      it            computation.
  today        today                          tomor    tomorrow
                                               row
      (5 tokens computed)                          (1 token computed)

## Page 23

     Reuse KV Cache between Requests
   • Example: using LLM to assist in reading research papers

        System Prompt: you are a helpful assistant，…

Reusable
  long
 context




  Short    User Question 1:    User Question 2:    User Question 3:
questions  Summarize this paper  What is Mooncake Store  List related research works

## Page 24

Trace Analysis: Reusable KV Cache

                                 Traces in our paper
                                 (open-sourced in https://github.com/kvcache-ai/Mooncake )

                                 Conversation: collected from real-world online
                                 conversation requests
                                 Tool&Agent: collected from real-world online
                                 requests that include tool use
                                 Synthetic: synthesized from publicly available
                                 long context datasets


• Around 50% of the tokens’ KVCache in the real-world workloads can be reused

## Page 25

Trace Analysis: is Local Cache Enough?

                                      Traces in our paper
                                      (open-sourced in https://github.com/kvcache-ai/Mooncake )

                                      Conversation: collected from real-world online
                                      conversation requests
                                      Tool&Agent: collected from real-world online
                                      requests that include tool use
                                      Synthetic: synthesized from publicly available
                                      long context datasets

local capacity (~3M tokens)

• Around 50% of the tokens’ KVCache in the real-world workloads can be reused
• However, the cache hit rate will significantly drop if only using the local cache

## Page 26

      ℎ      = 2×     ×                               ×      _      ×
    KV Cache: Huge Challenge to Storage System

    • One token's KV cache size is quite large        •      KV cache linearly increases with the
                                                             sequence length
    One token (Bytes) One token’s KVCache (Tens of KB)
        Hidden Dimension                                            Model: LLaMA3-70B
        Key                                       Num Layer     400        320
                                                                50

        Value                                     Num Layer
                                                             0      1k 16k  128k     1M
                                                                    Sequence Length










KVCache Size (GB)

## Page 27

   KV Cache: Huge Challenge to Storage System
    •  The volume of reusable KVCache is much larger than the
       available storage capacity of a single inference node
               Over 100 billion tokens per day        Reusable
               KVCache
DRAM or Other     (Hundreds
Storage (TB)        of TB ~ PB)
            One Token’s GPU VRAM
              KVCache   (Hundreds of GB)
One Token  (Tens of KB)
 (Bytes)

## Page 28

  Mooncake Solution

                         Mapping prefill, decode and KVCache
                         storage to the most suitable hardware

       H800                  H20  Xeon SPR + 8 * DDR5-4800
Hardwar
       80GB VRAM，3.3 TBps
   e        ~ 1 PFLOPS   96GB VRAM，4 TBps8*64GB DRAM，8*40GB/s
    Spec                     ~ 200 TFLOPS      < 20 TFLOPS
       For Prefill!          For Decode!        For KVCache!
    Best    Allround,        Bandwidth/$        Capacity/$
   for     especially for TFLOPS/$
                             !!! The price numbers are not accurate, just a demonstration!

## Page 29

Mooncake: A KVCache-centric Disaggregated Architecture
     The underlying LLM inference architecture of Kimi
       • KV cache caching & scheduling centered on a large-scale distributed memory pool
       • Designed for good user experience: strict SLO on heavy overload
       • Powering over 80% of Kimi’s traffic
       • Space–time tradeoff: boosts Kimi’s throughput by over 75%







    FAST ’25 Best paper    Moonshot + Tsinghua KVCache.AI team

## Page 30

Mooncake: Open-sourced on GitHub










and more …

## Page 31

Mooncake: Open-sourced on GitHub
 Active community:
 We welcome your use and contributions!

## Page 32

Mooncake Architecture

## Page 33

    Key to Mooncake

                   • End-to-end zero-copy
                   • Mooncake Transfer Engine
⚡Transfer Fast




High-performance distributed
 LLM inference architecture

        Store More                                        ✅Easy to Use
    •   Elastic, Shared, and Multi-layer KV Cache     •   Rich and user-friendly APIs
• Memory Allocator Optimized for LLM Inference • Extensive LLM Ecosystem Collaboration

## Page 34

Transfer Fast: End-to-end zero-copy
•   Workflow
    •   Mooncake client get source and target memory address from LLM inference instance and
        Mooncake master
        Launch RDMA R/W directly between source and target memory
    •   Transfer speed only bound on RDMA network bandwidth

## Page 35

 Transfer Fast: Mooncake Transfer Engine
• Key features
      Multi-NIC pooling
  •   Topology-aware path selection

## Page 36

 Transfer Fast: Mooncake Transfer Engine
• Key features
      Topology-aware path selection
      Multi-NIC pooling
  •   Supports multiple protocols
      and provides unified interfaces.
  •   Multi-language APIs

                                        Lightening fast over RDMA
                                        •   40 GB KVCache (128k tokens, LLaMA3-70B)
                                        •   87 GB/s @ 4×200 Gbps, RoCE
                                        •   190 GB/s @ 8×400 Gbps, RoCE
                                        Transfer Engine NT
                                        •   FAISys 2025
                                        •   Coming soon

## Page 37

   Store More: Elastic Shared Multi-layer KV Cache

•  Key features
   • Distributed KV cache sharing: storing
     one and usable by all

## Page 38

   Store More: Elastic Shared Multi-layer KV Cache

•  Key features

   •     Distributed KV cache sharing: storing
         one and usable by all
   •     Dynamic resource scaling: dynamically
         adding and removing store nodes
         (startup in <80s for 500GB memory and
         8 RDMA NICs)
   •     Multi-layer storage (WIP): offloading     Time cost of registering newly allocated
         cached data from DRAM to 3FS and          memory with 8 mlx5 RDMA NICs
         local SSD

## Page 39

   Store More: Memory Allocator Optimized for LLM Inference
•  Allocation memory space for KV cache
            High memory utilization
      •     Fast allocation
•  LLM inference workload
            Size: from KBs to GBs
            Most objects have identical size
      •     May have various object size: different
            chunk size, TP settings or models
      •     May not known from the start                    Offset Allocator (TLSF)
  •   Mooncake solution: Offset Allocator
      (TLSF)
          •        Fast allocation, few fragmentation, high
            utilization
      GitHub: https://github.com/sebbbi/OffsetAllocator     Masmano, Miguel & Ripoll, Ismael & Crespo, Alfons. (2006). A
                                                            comparison of memory allocators for real-time applications

## Page 40

   Store More: Memory Allocator Optimized for LLM Inference
•  Allocation memory space for KV cache
                High memory utilization                          Memory Utilization (%)
         •      Fast allocation                               100
•  LLM inference workload                                      80
                Size: from KBs to GBs
                Most objects have identical size               60
         •      May have various object size: different        40
                chunk size, TP settings or models              20
         •      May not known from the start                    0
   •     Mooncake solution: Offset Allocator                     8MB  7.2MB  8.8MB      Random
         (TLSF) optimized for LLM inference                      Offset (Original)  Offset (LLM Optimized)
             •     Fast allocation, few fragmentation, high      More details: https://kvcache-ai.github.io
                utilization                                      /Mooncake/performance/allocator-benchmark-result.html
         GitHub: https://github.com/sebbbi/OffsetAllocator

## Page 41

Rich APIs, Easy to Use

Put/Get APIs
•   Put/Get single object
•   Batch Put/Get
•   (Batch) Zero-copy Put/Get: recommended
•   (Batch and zero-copy) Put/Get from/into
    multi-parts
•   Etc.
Configurable KV cache placement
•   Replica number
•   With soft pin
•   Preferred segment

        Hello world example

## Page 42

Mooncake × LLM Ecosystem Collaboration

     NVIDIA Dynamo

## Page 43

  Mooncake with SGLang

• Disaggregated serving
  •     Mooncake Transfer Engine for KV transfer
  •     Support GPUDirect RDMA (GDR) and TCP
• Distributed KV cache
  •     Mooncake Store as HiCache L3
  •     Prefix aware KV cache retrieval
  •     Support RDMA and TCP
• Significant performance gain
  •     Larger capacity, higher hit rate, increased     Experiment settings
        performance                                     •     Hardware: 8 × H800 GPUs
                                                        •     Model: Qwen3-235B-A22B-Instruct-2507
                                                        •     Workload: SGLang multiturn benchmark
                                                        •     KV cache configuration: hicache-ratio set as 2,
                                                              760GB Mooncake global memory

## Page 44

Mooncake with SGLang

                    SGLang + Mooncake: the first open-source stack to
                    fully replicate DeepSeek’s inference architecture.

## Page 45

SGLang + Mooncake + NVL72:
The First Open-source LLM Inference Stack on NVL72









Efficient support for
multi-node NVL,
achieving a 2.7×
throughput gain over
the H-series.

## Page 46

 Mooncake with Dynamo

Mooncake Transfer Engine serves as a      Mooncake Store serves as the
backend of NIXL, offering significant     KVBM backend (WIP)
performance advantages with small
chunks and multi-NIC setups.

## Page 47

    Mooncake with vLLM V0
  1st version
  • Disaggregated serving
       •   Data flow: GPU→CPU—Transfer engine
           → CPU → GPU
       •   1P1D

2nd version
•   Disaggregated serving
    •     Use Mooncake Store as a buffer for KV
          cache data transfer
    •     xPyD

## Page 48

       Mooncake with vLLM V1
    Mooncake ✖ vLLM V1
    •   Disaggregated serving
        • Via LMCache and NIXL connector
    •   Distributed KV cache
        • Via LMCache connector

  vLLM
Connector


 LMCache      NIXL
Connector   Connector

Mooncake    Mooncake
  Store  Transfer Engine
 Backend     Backend

## Page 49

         Mooncake with vLLM: Performance Evaluation
     Mooncake ✖ vLLM V1
     •     Disaggregated serving                         Metric            Cold Start         Cache Hit (Second    Improvement
           •  Via LMCache and NIXL connector                              (First Round)            Round)
     •     Distributed KV cache                          Average TTFT            21,707.62 ms    6,708.39 ms       ↓ 69.1%
           •  Via LMCache connector                      P50 TTFT                22,102.51 ms    7,253.38 ms       ↓ 67.2%
     •     Significant performance gain                  P90 TTFT         38,170.54 ms          11,128.26 ms       ↓ 70.9%
                                                              Average TPOT  368.12 ms             140.17 ms        ↓ 61.9%
Experiment settings                                             P50 TPOT    362.08 ms             132.98 ms        ↓ 63.3%
•         Hardware: 8 × H800 GPUs                               P90 TPOT    632.90 ms             221.93 ms        ↓ 64.9%
•         Model: Qwen2.5-72B-Instruct                      Request Throughput
•         Workload: 50 requests, input = 9728 tokens,            (req/s)          1.11           3.23              ↑ 191.0%
          output = 64 tokens
•         Cache Configuration: LMCache’s local CPU       Output Token Throughput  71.24          202.91            ↑ 184.8%
                                                                 (tok/s)
          cache was disabled to ensure a direct
          assessment of Mooncake Store’s effectiveness.  Total Token Throughput   10,899.84      31,665.01         ↑ 190.5%
                                                                 (tok/s)

              More details: https://kvcache-ai.github.io/Mooncake/getting_started/examples/lmcache-integration.html

## Page 50

Mooncake in Industrial Application


 Mooncake supports various accelerators such as NVIDIA and Ascend,
 and runs on thousands of GPUs across many companies.





 and more …

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: ``
