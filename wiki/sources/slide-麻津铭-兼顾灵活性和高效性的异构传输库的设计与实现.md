---
type: source
source-type: slide
title: "麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现"
path: slides/麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现.pdf
source-md5: 0d703deb100d12bc5685a49a895e904a
size: 8548 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现

> Ingested from `slides/麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现.pdf` via `lit parse` on 2026-06-04.
> Source file: 8.35 MB.

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

    DLSlime: 兼具灵活与高效的点对点
    RDMA 传输工具
        JimyMa
        2025.12.12
        上海人工智能实验室





DeepLink-org/DLSlime

## Page 7

目 录 CONTENTS
    01:背景介绍
    AI 场景与集群下的通信困境
    场景一：异构三维并行

    场景二：分离式推理服务

    场景三：异构参数服务器
    RDMA 及其在异构通信中的优势

## Page 8

背景介绍

## Page 9

    AI Infra 范式转移：负载特征与通信挑战
        任务异构需求：针对分离式架构的灵活拓扑

    传统并行范式 (单程序多数据，SPMD)




    数据流向复杂，传统集合通信难以适配
    ● 高并发小消息带来高昂控制面开销
      设备异构需求：统一互联协议


    1. 任务同构：计算模式单一
    2. 设备同构：计算架构单一

芯片混布需求日益增长
● 互联协议不同，生态割裂

## Page 10

异构算力之困：负载特征与通信墙

核心场景一 – 异构三维并行        生态现状 – 通信孤岛

    异构芯片通信通而不畅
                  ●   生态割裂 (Fragmentation)：不同厂商（NVIDIA, Huawei, Moore
                      Threads 等）拥有私有通信库（NCCL, HCCL, MCCL），彼此协
                  ●   议不兼容。
                      资源孤岛 (Resource Silos)：单一集群内无法混合部署不同类型的
                  ●   卡，导致算力池化困难，资源利用率低。
                      开发成本 (High Cost)：上层框架需要针对不同硬件分别适配，维
                      护成本极高。




场景对通信系统的苛刻要求
●   需屏蔽硬件差异：作为统一的异构通信中间件，向下屏蔽硬件差异，
    向上提供标准接口。
●   需微秒级延迟：极低开销，保证流水线间微秒级延迟。
    通信可以和计算异步并发：计算和通信重叠，快慢节点自适应。

## Page 11

分离式推理：海量搬运与高频交互

核心场景二 – 异构分离式推理        xCCL 痛点 – 高昂控制面开销

    传统通信库难以应对高并发小消息
                   ●   低吞吐率 (Low Throughput)：传统集合通信库（NCCL/HCCL）为
                       大包同步设计，在海量小消息（Small Messages）时显存交互开
                       销占比高，有效带宽下降。
                   ●   缺乏单边语义 (One-Sided Semantics)：双边通信强依赖接收端
                       CPU 参与，打断 Prefill 节点的计算流水线。








场景对通信系统的苛刻要求
    计算与显存解耦：Prefill, Decode 分离，提升利用率，服务质量。
    海量数据搬运：Cache 要在不同集群间实时迁移，带宽要求极高。
●   控制流挑战：除了大块 Cache 数据，还伴随着大量的小控制信令
    （Requests/Meta），对延迟极度敏感。

## Page 12

异构参数服务器：多点并发与非对称通信

核心场景三 – 异构参数服务器       xCCL痛点：CPU瓶颈与语义缺失
    传统方案导致 Server 端 CPU 严重过载
                   ●   CPU 过载 (CPU Overload)：使用 TCP/IP 或传统消息队列时，
                       Server 端 CPU 需要耗费大量算力处理网络包（内核中断、内存拷
                   ●   贝），严重拖慢模型更新速度。
                       语义不匹配 (Semantic Mismatch)：传统集合通信库（xCCL）主
                       要针对 AllReduce 设计，缺乏高效的 Client-Server 原语支持。







场景对通信系统的苛刻要求
●   跨架构互联 (Cross-Architecture)：Worker 与 Server 架构不同，
●   通信协议需兼容。
    非对称流量 (Asymmetric Traffic)：存在多对一 和一对多流量特
    征，极易造成 Server 端网络拥塞。
●   零干扰更新 (Zero-Interference)：Server 端 CPU 需专注优化器计
    算，通信过程不能抢占 CPU 资源。

## Page 13

 节点间 RDMA 进程通信基座：IBVerbs 原语
 RDMA 协议栈        IBVerbs 通信原语










   RDMA 相比 TCP 的优势
   零拷贝 (Zero-Copy)        ● IBVerbs 通信流程
   内核旁路（Kernel Bypass）            ○ Step 0：注册内存区域
   低 CPU 占用（Low CPU Overhead）     ○ Step 1：提交请求到发送队列（DoorBell，数据传输）
●  高带宽与低延迟                        ○ Step 2：从完成队列中获取发送完成信号

## Page 14

目 录 CONTENTS
    02:DLSlime 设计简述
    01: 总体架构
    02: 编程范式
    03: 传输引擎
    04: 流同步
    05: 链路复用

## Page 15

DLSlime 设计简述

## Page 16

DLSlime 2.0 传输层整体架构图
                    ●  应用层（Interface）
                         兼容 torch.dist，兼容软件生态
                      ○  原生接口灵活建链，无需预分配通信组

                    ●  代理层（Execution）
                         RDMAWorker 作为无锁时间循环
                      ○  接管任务提交并收集完成事件

                    ●  逻辑层：
                         轻量级逻辑连接句柄
                      ○  维护 QP 和流控逻辑，按需建链。

                    ●  流管理：
                      ○  利用 Host / Device Signal 构建双向信
                         令
                      ○  确保计算流与通信流的严格保序。
                    ●  资源层：
                         共享保护域和完成队列，最大化利用率
                      ○  共享内存池缓存实现数据零拷贝传输

## Page 17

  DLSlime 编程范式：多模驱动的灵活抽象

 面向兼容 (Compatibility)：消息传递 面向并发 (High Concurrency)：单边通信 面向定制 (Customization)：共享内存










   兼容现有软件生态 (torch.distributed) CPU 旁路：单边语义，旁路远端 CPU     全局视野：Device 抽象成共享内存
   存量 PyTorch 模型无需修改即可运行     支持超大 Batch 请求聚合提交        ●  灵活读写：非连续内存的精确读写拼
●  适用场景：异构三维并行训练     ●     适用场景：分离式推理，参数服务器              接
                                                      ●  适用场景：自定义算子，复杂拓扑通
                                                         信

## Page 18

面向高并发：单边通信机制实现

端点连接        RDMA READ / WRITE










1. 基于事件驱动的异步完成处理 (Event-Driven Async Completion)     2. 智能流量整形与背压机制 (Traffic Shaping & Software Backpressure)
●     中断唤醒机制： ibv_get_cq_event 中断通知机制。              ●     实时水位监控：软件层实时追踪硬件队列深度。
●     极致 CPU 能效：将 CPU 资源让渡给核心计算任务。                  ●     鲁棒性保障：突发流量导致硬件 QP 溢出或连接断开风险避免

3. 大消息分片与负载均衡 (Segmentation & QP Aggregation)        4. 双工线程分离结构 (Full-Duplex Thread Separation)
●     透明大包切分：自动将大内存请求切分，上层业务无感。                     ●     收发物理隔离：独立部署WQ Dispatch与 CQ Polling 线程池。
●     多队列聚合：通过将数据切片分发至所有QP，充分压榨网卡带宽。                ●     消除队头阻塞：避免慢速 IO 阻塞后续请求，提升并发流水效率。

## Page 19

面向兼容：消息传递机制实现










1. 架构模式：无锁流水线设计 (Lock-Free Pipeline Architecture)     2. 关键优化：批处理与零内存分配 (Batching & Zero-Malloc)
●     解耦应用与传输：移除 std::mutex 锁竞争，提交与传输解耦。             ●     批量流水线：摊薄 MMIO和队列出入队开销。
●     全异步驱动：采用代理线程)模式，发送与接收独立运转                      ●     零动态分配：对象均初始化阶段预分消除内存碎片与分配延迟
3. 信号机制：基于计分板的极速同步 (Scoreboard-based Synchronize)     4. 硬件交互：元数据与数据分离 (Decoupled Meta/Data Path)
●     原子计分板：计分板”替代传统条件等待。                            ●     双流分离：小包元数据先行，大包数据紧随其后，零拷贝通知。
●     忙轮询机制：利用 用户态轮询替代内核态挂起。。                        ●     直接硬件轮询：代理线程直接持有 CQ 轮询，第一时间捕获处理。

## Page 20

零拷贝机制加速小消息传输

内存区缓存实现运行时零系统开销
               ● 逻辑视图 —— 回合制交互
                    Step 1：Recv 元信息发送
                    Step 2：Sender 发送大包
                 ○  Step 3：完成信号处理

               ● 物理视图 —— 静态内存池
                    Meta MR Pool：小块（常驻内存）
                 ○  Data Pool：大块，常驻内存，循环复用

               ● 关键动作：
                    Init 阶段：一次性 ibv_reg_mr。
                 ○  Run 阶段：直接使用 LKey / Rkey，零
                    系统调用

## Page 21

面向定制化：共享内存抽象
DLSlime共享内存抽象    灵活地定制通信算子










●  通过DLSlime共享内存打破物理边界，支持通过其进行跨 ● 当标准算子无法满足需求时，DLSlime共享内存提供了极
   设备内存访问 大的自由度，可以定制灵活的通信算子(已支持All2All、
●  在处理不同节点间数据流向时，共享内存提供了最直接的 AllGather)
   数据交互通道
●  直接读取跨设备远端内存，进行灵活地非连续内存读写拼
   接

## Page 22

引擎内核：多流范式流控与一致性保障机制

## Page 23

极致解耦：基于双信号量的全异步流式同步

极低开销保序信号量同步
    ●     零驱动开销
                   Proxy Zero-Systemcall，纯内存读写
    ○              减少用户内核切换， ns级同步


    ●     硬件级流保序
                   流 Write / Wait 原语实现 GPU 端同步
    ○              CPU线程与设备流互不影响，无间断流
                   水


    ●     双向安全闭环
                   Ready 信号 (Device->Host)：杜绝脏读
    ○              Done 信号 (Host->Device)：放置踩踏

## Page 24

    大批量高并发单边传输










  零拷贝：消除 MemCpy 开销 ● MMIO：仅单次调用实现 CPU Bypass：全程无感
  批处理：单次Doorbell批量发 多批次打包传输 ● 传输与异构计算任务重叠，
● 背压机制：本地水位熔断，保证硬件 ● DMA 直接抓取离散数据， 掩盖传输延迟
  队列不溢出 跑满极限带宽

## Page 25

零拷贝机制加速小消息传输

内存区缓存实现运行时零系统开销
               ● 逻辑视图 —— 回合制交互
                    Step 1：Recv 元信息发送
                    Step 2：Sender 发送大包
                 ○  Step 3：完成信号处理

               ● 物理视图 —— 静态内存池
                    Meta MR Pool：小块（常驻内存）
                 ○  Data Pool：大块，常驻内存，循环复用

               ● 关键动作：
                    Init 阶段：一次性 ibv_reg_mr。
                 ○  Run 阶段：直接使用 LKey / Rkey，零
                    系统调用

## Page 26

Reactor 模式实现多链路复用

                             ●  痛点分析
Polling 线程和 Dispatch 线程复用       ○  One-Thread-Per-Connection 模型 OS
                                   调度开销大，缓存失效，延迟不可控

                             ●  解法
○                                  多路复用。Shared CQ 聚合硬件信号，
                                   逻辑上利用 Reactor 模式聚合处理流

                             ●  架构优势
                                   独占 CPU 核心，消除 OS 调度抖动
                                   高缓存命中率
                                ○  线程数不在随连接数线性增长，扩展性强

                             ●  关键技术点
                                   全局共享 CQ，关联所有 QP
                                   wr_id 存储 Context 指针，O(1) 分发
                                ○  Non-blocking Handling：逻辑层
                                   Handler 非阻塞（只做更新或入队）

## Page 27

目 录 CONTENTS
    02: 性能分析
    01: 点对点通信性能
    02: Send/Recv 通信性能

## Page 28

DLSlime 性能分析

## Page 29

OneSide Read/Write Benchmark

## Page 30

Send/Recv Benchmark

## Page 31

目 录 CONTENTS
    03:DLSlime 场景适配
    异构三维并行

    分离式推理服务

    异构参数服务器

    异构序列并行

## Page 32

DLSlime 场景适配

## Page 33

DLSlime 赋能分离式部署
控制面数据面分离       DLSlime 加速 引擎/运行时 通信










●   Push 模式主动传输：Prefill 节点主动推送，彻         计算通信自动重叠：推理与传输异步并行，最小化对 GPU 计算的干扰。
    底消除 Pull 模式的轮询开销 (Zero-Polling)。 ●   硬件级资源隔离：利用多网卡与 RDMA Zero-Copy 技术，突破通信带
●   控制数据解耦：调度指令与大数据块传输路径                 宽瓶颈。
    分离，大幅降低系统抖动。

## Page 34

    实战收益：异构参数服务器通信性能跃升
    异构参数服务器 （9000+ Tensor 共 200G 数据传输）   DLSlime 加速参数服务器数据传输

                                            集群环境：异构算力集群
                                            链路：Worker (山东) — Server (上海)
                                         ●  对比方案：ZMQ (TCP / IP) vs DLSlime










                                   ●        CPU Offload 消除长距离抖动
                                            ○ CPU 旁路，减少 CPU 中断开销
PS 方案将大集群拆分成更小的相对独立的标准训练任务组件，大大降   ●        多链路聚合实现 100B 参数秒级传输
   低了集群软硬件故障，时延和通信带宽对于模型训练的影响               ○ 批量传输充分填充链路，避免带宽浪费

## Page 35

          赋能国产 3D 并行
    弥合硬件鸿沟，

          针对生态壁垒                      向下屏蔽硬件差异，向上对接主流软件生态
                                   ●  国产异构芯片“零成本”接入主流 AI 生态

          异构流水线适配                     利用 DLSlime 灵活性，支持非均匀切分
                                   ●  显存大多存，算力强多算，实现 1 + 1 > 2

          通信算子融合                      算子融合与多链路聚合，充分利用网络拓扑
                                   ●  提升通信效率，掩盖物理链路高延迟

      单卡种无法满足训推需求，强依赖多卡互联 低精度传输       支持 FP8 / BF16 在线压缩传输
      节点内互联带宽，拓扑差异大                ●  在有限的物理带宽下，倍增通信吞吐量
   ●  均一化的并行策略失效，需“定制化”通信

H2: Towards Efficient Large-Scale LLM Training on Hyper-Heterogeneous Cluster over 1,000 Chips

## Page 36

   极致点对点性能
   (a) 芯片 A -> 芯片 B    (b) 芯片 B -> 芯片 C (e) 异构 PP 倍增模型训练效率





   (c) 芯片 C -> 芯片 D    (d) 芯片 D -> 芯片 A  (f) 千公里 PP 混训等效算力





H2: Towards Efficient Large-Scale LLM Training on Hyper-Heterogeneous Cluster over 1,000 Chips

## Page 37

总结

## Page 38

DLSlime: 灵活高效的点对点异构 RDMA 传输工具

## Page 39

THANKS

## Page 40

动态序列并行：突破小力度非规则通信瓶颈

核心场景四 – 动态序列并行       MoE/Attention 对通信的苛刻要求

    传统通信库难以应对高并发小消息
                  ●   元数据开销过大 (High Overhead)：NCCL/HCCL 针对 MB/GB 级
                      大包设计。在传输 KB 级小消息时，Kernel 启动和 Ring 协商的耗
                  ●   时远超数据传输本身。
                      显存碎片化：处理非连续内存（由 Mask 产生）需要额外的
                      Pack/Unpack 操作，增加显存读写压力。





动态负载下的通信 “既要有要”
●   负载不可预测 (Unpredictable Payload)：在线推理 (Serving) 场
●   景下，Batch 内请求长短不一，且随时间动态变化。
    静态图约束 (Static Graph Constraint)：CUDA Graph 强依赖静
●   态显存布局。
    低延迟：Decode阶段对于TPOT的要求极其严格(<50ms)，需要确
    保引入的通信延迟不会过高。

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/麻津铭_兼顾灵活性和高效性的异构传输库的设计与实现.pdf]]`
