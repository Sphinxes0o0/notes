---
type: source
source-type: slide
title: "熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进"
path: slides/熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进.pdf
size: 9771 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进

> Ingested from `slides/熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进.pdf` via `lit parse` on 2026-06-04.
> Source file: 9.54 MB.

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

统一算力，  FlagScale在
FlagOS生态中的演进
    北京智源人工智能研究院
    敖玉龙

## Page 7

目 录 CONTENTS
    1. FlagScale大模型训推框架介绍
    2. 通过自动化技术实现跨芯片迁移
    3. 通过FlagCX统一通信库实现跨芯片协同
    4. FlagOS统一生态应用示例

## Page 8

    FlagOS：    面向多种AI芯片的统一、开源的系统软件栈
            AI大模型                      已支持大模型
    (语言大模型，多模态大模型，MoE架构等)             语言模型      多模态模型      具身智能模型
                                 DeepSeek，Qwen，     智源EMU，面壁CPM，     智源RoboBrain
           深度学习框架               Seed-oss，GPT-oss，      Qwen-VL系列，ERNIE4.5,        Pai-0
（PyTorch, PaddlePaddle, etc）    Step, Grok，Llama等        Llava系列

        众智FlagOS ：面向多种AI芯片的系统软件栈                                       各种大模型
        开源核心库             开源工具         各种深度学习框架
                     Triton-Copilot
FlagGEMs:  FlagScale:   算子自动生成工具
通用大模型算子库    训练推理并行框架   FlagRelease        统一自主软件栈：统一支持
                        自动迁移和发版工具        各种AI芯片
FlagTree:    FlagCX:    FlagPerf
  统一编译器       统一通信库      多芯片评测工具        各种的智算集群
      后端编译 底层通信    后端编译   底层通信    后端编译   底层通信      • 芯片企业：超过10家芯片企业，20多款不同芯片
   器 A      库 A     器 B    库 B     器 C    库 C        数据中心               机器人        边缘
      芯片 A        芯片 B             芯片 C        (train & Inference)  (cloud-edge    (inference)
                                                                   cooperation)

    已支持的硬件架构: Nvidia, NPU, GPGPU, DSA, RISC-V AI, ARM

## Page 9

    AI加速框架面临的三大关键碎片化挑战

•   挑战一: LLM 全生命周期的端到端支持碎片化
      DeepSpeed 和 Megatron-LM 等框架主要聚焦训练，虽已支持推理，但缺乏全生命周期集成。
   o  NeMo-Megatron 尝试提供从预训练到部署的全周期支持，但与 NVIDIA 生态深度绑定，限制了通用性。
•   挑战二: 框架能力重叠且专业化导致的碎片化
   o vLLM 和 SGLang 等框架在不同场景中各有优势，选择难度大。
   o  llama.cpp 等更多选项进一步分化生态，增加了框架选择和集成的复杂度。
 •  挑战三: AI 硬件碎片化与缺乏标准化
   o GPU、NPU 和定制加速器等 AI 硬件种类日益增多，用户需在性能、兼容性和成本间权衡。
   o 每个硬件平台通常需要专属工具链和优化策略，跨平台开发部署需大量工程投入。

## Page 10

    FlagScale：支持“多芯片+多后端”的元框架



    统一启动器      自动调优         自动容错   自动预估                  统一检查点      统一命令行               • 通过自动化技术实现跨芯片的自适应计算

        训练              压缩        推理                         服务                         • 通过多种可扩展的执行引擎后端支持大
FlagScale-  Megatron-   FlagScale- llm-  FlagScale-      vllm/SGLa
   Train      LM/…      Compress   compresso Inference   ng/llama.c  FlagScale-   Ray-  模型的全生命周期
                            r/…                          pp…            Serve    Serve/…


    算子库                                                  通信库                            • 通过统一底层库实现不同芯片间计算
    FlashAttn/Transformer
    FlagGems            Engine/xformers/…    FlagCX          NCCL/GLOO/…                与通信兼容

## Page 11

目 录 CONTENTS
    1. FlagScale大模型训推框架介绍
    2. 通过自动化技术实现跨芯片迁移
    3. 通过FlagCX统一通信库实现跨芯片协同
    4. FlagOS统一生态应用示例

## Page 12

   跨芯片自动调优框架

 不同模型                          搜索空间:       多维剪枝:
(不同大小)                         • 并行策略      • 联合优化剪枝
 Qwen                          • 优化策略      • 基于历史剪枝
   …                           • …         • …
   DeepSeek     模型信息
   …                1              2           3
   Llama            搜索             剪枝          生成

不同规模集群          集群信息
 1K 设备                         在线反馈            可执行配置
   …                                       性能结果
   10K 设备           4 6
                                   5
 不同芯片      M x N x K     执行        记录          预估
  芯片A
   …
  芯片B                              最优策略       实际执行  代价模型
   …
  芯片C                                          与厂商合作

## Page 13

    更大的搜索空间和更完善的内存建模
•  扩展搜索空间，更好支持MoE模型和其他新模型
Types                 Items
Parallelism           DP, TP, SP, VPP, CP, PP, EP, ETP, Uneven-PP
Optimization          Distributed-Optimizer, Re-computation, Gradient Accumulation
Models                Dense Model (Llama3, Qwen3, …), Sparse Model (DeepSeek-V3, Qwen3-MoE, …)
Search Strategy       Pruned by history performance and model memory utilization rate

•  更精确的内存模型                                                                              DeepSeekV3-16B-A3B
Item             Params     Activation                                                   per-layer param(B)  num layers  params(B)
                            (Peak Mem with Parallelism)                              Embedding     0.3111     1             0.3111
GQA/MLA                                                                              MLA           0.0138     27            0.3726
QKV Proj         ✓          ✓                                                        MoE           0.5711     26           14.8486
                                                                                     MLP           0.0692                   0.0692
GQA/MLA          -          ✓                                                        Output        0.3111     1             0.3111
Core Attn                                                                            Total                                 15.9126
Out Proj         ✓          ✓
FFN Up&Down      ✓          ✓
Experts          ✓          ✓
Shared Experts   ✓          ✓
Layernorms       ✓          ✓
MTP Module       ✓          ✓

## Page 14

         训练自动调优的最新结果
                     不同芯片上训练自动调优结果
        50%                                     Pruned by
                 Chip-1                      GPU Utilization
        40%      Chip-2        36.43%36.88%    [0.5, 0.9]              Qwen3-32B
                 Chip-3
        30%          26.52%      28.95%        Pruned by
                     23.96%        Historical Performance

        20%
             13.33%     14.88% 14.52%
                 11.92%
        10%                                                        Base

             0%  Qwen3-32B     Qwen3-30B-A3B DeepSeekV3-16B-A3B        0 0.2 0.4 0.6 0.8  1
   •     在不同模型规模、模型架构和芯片上均实现了加速效果。      •                          通过历史性能分析和内存模型估算，将搜索空间压
         观测到的最大加速比达到约36.88%（去年为23.08%），平均提升幅                       缩了76%。
         度约为23%（去年为11.3%）。










加速比

## Page 15

    多种推理加速引擎自动调优
  Base                自动支持和优化选择多种推理加速引擎
AutoTuner

    AutoTuner         Training    Inference                             vllm
                  AutoTuner       AutoTuner                         Backend
                                              FlagScale             Agnostic
    Training          Training    Inference    Plugin                   SGLang
                                               System
                                                  &
    Megatron-     Megatron-                     Tools               Backend
   LM                 LM        vllm                                Specific    llama.cpp

        面向具体任务的AutoTuners                      AutoTuner  支持同一种任务的不同后端加速引擎

 Backend
                                               Dispatcher

    …     Megatron-LM      DeepSpeed           vllm       SGLang        llama.cpp     …

                      面向多种加速引擎的通用AutoTuner

## Page 16

       多种推理加速引擎自动调优结果
           同一模型推理在多种芯片的自动调优对比                                 同一模型推理在不同后端引擎的自动调优对比
  3        ChipA  ChipB  ChipC  ChipD  ChipE              3.5    Throughput    E2E Latency    Time To First Token
2.5                                                         3
  2                                                       2.5
1.5                                                         2
                                                          1.5
  1                                                         1
0.5                                                       0.5
  0        Config 6                                         0
   Config 1
       Config 2
           Config 3
           Config 4
           Config 5      Config 7      Predefined Config  vL M-config 1
                                                              vL M-config 2
                                                              SGLang-config 1
                                                              SGLang-config 2
                                                              SGLang-config 3
                                                              l ama.cp -config 1
                                                              l ama.cp -config 2
•      针对不同芯片架构需要自动调优：同一种配置在不同芯片上的性能差异可以达到3倍，同一种芯片在不同配置下的性能差异
       也超过3倍。
•      对大多数的缺省预设配置，使用AutoTuner，可以获得2%–20%的吞吐量提升。
•      不同加速引擎分别在吞吐量、端到端时延、第一token响应上表现出不同的性能优势

## Page 17

 推理部署的多模型自动编排和自动扩缩容功能










•   自动编排：通过配置模型依赖，FlagScale能自动编排多模型流水线，并完成服务部署。
•   自动扩缩容：通过配置资源需求，服务实时根据承载和资源总量自动扩缩容。

## Page 18

目 录 CONTENTS
    1. FlagScale大模型训推框架介绍
    2. 通过自动化技术实现跨芯片迁移
    3. 通过FlagCX统一通信库实现跨芯片协同
    4. FlagOS统一生态应用示例

## Page 19

    支持可产业应用的异构混训技术



       关键技术1: 设计与实现支持多款芯片    单一训练任务
       的通用异构并行策略，实现负载均衡任
   端   务划分，发挥不同类型芯片的算力潜能。
   到   FlagScale
   端
   方   FlagCX        子任务 A   子任务 B  子任务 C
   案   关键技术2: 基于标准协议和兼容厂商
       通信库，实现多款不同芯片之间高效通
       信，打破算力障碍。


       芯片 A 芯片 B  芯片 C
       同构芯片Collective通信 异构芯片跨节点P2P通信










层 1


层 2


层 3


层 4


层 5


层 6










层 1


层 2


层 3


层 4


层 5


层 6

## Page 20

    多种灵活异构并行策略，显著提升异构训练效率

    批大小=1       批大小=2     批大小=3      类型 A    类型 B    类型 C
    类型 A      类型 B      类型 C
          层 1       层 1     层 1
          层 3       层 3     层 3
          层 6       层 6     层 6
                                流水线并行阶段1     流水线并行阶段2 流水线并行阶段3
    数据并行实例1     数据并行实例2   数据并行实例3        流水线并行异构
                数据并行异构          类型 A        类型 B      类型 C
    类型 A      类型 B
                            类型 C




                            流水线并行阶段1 流水线并行阶段2
   流水线并行阶段1 流水线并行阶段2  流水线并行阶段3        流水线并行阶段3

            模型并行异构（减小）          模型并行异构（增大）










                    批大小=1










                    批大小=1










层 1




层 2

层 3




层 4

层 5

层 6







 Layer 1




 Layer 2

 Layer 3




 Layer 4

 Layer 5

 Layer 6










          批大小=1










层 1




层 2

层 3




层 4

层 5

层 6

## Page 21

 统一通用多维异构并行策略

 DP: 数据并行          TP: 张量并行                  PP: 流水线并行  EP: 专家并行               •   支持包含两种以上芯片类型的异构
DP0/EP0 PP0                                      DP2/EP2                           环境
                   PP1                           PP2                           •   支持高度灵活且可定制的芯片比例
                   DP1/EP1                                                         配置
 TP0    ProcessMesh     TP1   ProcessMesh        ProcessMesh                   •   支持全场景异构混训
     A             B                             TP2        C

                                                                                   Models  GDR-based      CPU-based
                                                                                         Communication  Communication
               …                             …                           …      Dense
                                                                                   (Llama,   ✅          ✅
                                                                             Qwen etc.)
               …                             …                           …       MoE
               …                             …                           …    (DeepSeek      ✅          ✅
     … … …         …    Cross-chip               Cross-chip                     etc.)
               …     Communication    … … …  …    … Communication … … …  …    …
     TP0 × DP0 × PP0        TP1 × DP1 × PP1        TP2 × DP2 × PP2

## Page 22

多种芯片上的异构端到端混训案例










“4台英伟达+4台天数”loss对比图    每100B进行效果评测，相比同构训练效果差异在-2.05%-+0.04%









“4台英伟达+4台寒武纪”loss对比图    每100B进行效果评测，相比同构训练效果差异在-1.18%-+1.27%

## Page 23

   通信库行业生态痛点
痛点1：通信实现与优化不具备通用性和自适应性      痛点2：无法实现跨不同芯片高效互联
   o 训练模型结构、规模及超参会变化，而且训练任务     o 数据中心建设存在周期，在多元算力时代有不同的选择，
   可能迁移到不同芯片类型、不同规模机器。          多芯混合集群越来越普遍。
   o 当前通信优化往往针对特定模型结构和集群配置，     o 不同芯片通信库缺乏统一接口和协议，导致跨芯高速互
   依赖专家经验，很难快速适应任务变化。           联开发和优化难度大，很难实现高效混合通信。

   厂  迁移                        深度学习框架
   商
   A

      迁移  迁移  迁移                NCCL APIs    Other APIs

   厂
   商      迁移                    厂商A  厂商B     厂商C  厂商D
   B

      千卡集群      万卡集群                不通或CPU中转

## Page 24

    FlagCX：    通用灵活的层次化创新架构

                   各类分布式应用与框架
                                   用户接口层                                       • 提供统一接口，既提供功能调用接
        不同插件                    通信功能调用接口             通信编程语言接口                  口，又提供通信编程接口
                   通信运行时层                                                      • 高层运行时提供通信编排和自适通
  服务组件                 高层通信函数（Function）
  Proxy        Routines    Scheduler        Optimizer                          信路径优化能力
Topology       Collective  中层通信操作（Operation）     Communicator                  • 中层运行时提供通信操作和通信域
    Simulator  Ops     P2P Ops     Fused Ops     Management                    管理能力
 Monitor           底层通信原语（Primitive）
       …       Host-side Primitives     Device-side      Third-party Primitives
                   Primitives                                                  • 底层运行时提供基础host和device
                   可移植抽象层                                                      高效原语
     CCL    Device     Net      P2P    Tuner             ...                   • 支持不同通信库、不同芯片和不同
 Adaptor    Adaptor  Adaptor  Adaptor                Adaptor
  GPGP      硬件类型        …                            互联协议     …                互联协议
    U     ASIC SuperPod        PCIe     NVLink           IB/RoCE

## Page 25

FlagCX当前厂商适配情况


厂商              英伟达     天数智芯     寒武纪     沐曦      昆仑芯     海光      华为      摩尔线程     AMD     清微智能
模式              Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero Homo/Hetero
send            ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
recv            ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
broadcast       ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
gather          ✓/✓     ✓/✓      ✓/✓     ✓/✓     ☓/☓     ✓/☓     ✓/☓     ✓/☓      ✓/✓     ✓/✓
scatter         ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/☓     ✓✓       ✓/✓     ✓/✓
reduce          ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
allreduce       ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
allgather       ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
reducescatter   ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
alltoall        ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
alltoallv       ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓
group ops       ✓/✓     ✓/✓      ✓/✓     ✓/✓     ✓/✓     ✓/☓     ✓/☓     ✓/✓      ✓/✓     ✓/✓

## Page 26

    统一集合通信C2C算法
    Homo-chip Collective (via FlagCX Adaptor)  Cluster 2
    Hetero-chip P2P (via FlagCX Core)
                  Cluster 1        N4     Chip B     N5    Cluster 3
              N0     N1          Cluster-to-Cluster (C2C)     N6        N7
        Chip A
              N2     N3                                       N8        N9
                                                                  Chip C

    Unified Adaptor Interface        GPU0                                   GPU1
                                 data                                       data
                                                             On-device Data Path
    aCCL  bCCL      cCCL     …     xCCL        Buffer                       Buffer

                                                             NIC             NIC
                             …        proxy                                 proxy
                                 CPU CPU Control Path                       CPU
Homo-chip Collective                                             Hetero-chip P2P
       厂商原生通信库                          FlagCX统一实现

## Page 27

    统一集合通信C2C算法流水线并行优化

    主要瓶颈：pre/inter/post阶段串行处理，存在overlap空间 优化方法：流水线并行

    preHomoFunc    heteroFunc    homoInterFunc    postHomoFunc

    Stage 0        Stage 1        Stage 2
        Stream



    Pipelined           Pipelined        Pipeline Speedup
Pre/Inter Step(s)  Inter/Post Step(s)
        Stage 0        Stage 2                                    Homo
                                                                  Stream

        Stage 1                                                   Hetero
                                                                  Stream
    Sequential     Sequential        Sequential  通过Pipeline优化节省的时间
    Pre Step(s)    Inter Step(s)    Post Step(s)

## Page 28

统一集合通信C2C算法流水线并行优化效果










•   Chip A 2机，Hetero w/ pipeline性能相比w/o     •   Chip A 2机，Hetero w/ pipeline性能在大Message Size上
    pipeline平均提升1.7x。                           （>=128M）相比w/o pipeline平均提升1.3x。
•   Chip A 2机，Hetero w/ pipeline性能相比w/o     •   Chip A 2机，Hetero w/ pipeline性能相比w/o pipeline最大
    pipeline最大提升2.0x。                           提升1.3x。

## Page 29

统一集合通信C2C算法Zero-Copy优化










应用程序的User-buffer和预注册     通过直接注册User-buffer，避免实际通
Devic-buffer的数据传输        信过程中的D2D拷贝调用

## Page 30

    统一集合通信C2C算法Zero-Copy优化效果










• 在小通信量场景下（<=128KB），零拷贝Device-buffer RDMA相比原生实现可以达到大约3.0x的加速比；
• 在[128KB, 128MB]的通信量区间内，零拷贝Device-buffer RDMA相比原生实现的加速效果随着通信量增大而不断降低，
  逐渐和原生实现性能持平；
• 在大通信量场景下（>=128MB），零拷贝Device-buffer RDMA和原生实现性能持平；
• 与业界其他通信库对比表明FlagCX的零拷贝Device-buffer RDMA性能已达到业界领先水平。

## Page 31

芯片解耦集合通信技术



                                           Runner类型       适用场景  测试案例        核心技术

                                           homoRunner     同构    ChipA+B     -

                                           hostRunner     全场景   ChipA+A/B   Host-stage Ops

                                           hybridRunner   异构    ChipA+B     C2C Algorithms

                                           uniRunner      全场景   ChipA+A/B   Kernel-free Ops

uniRunner：基于 Kernel-free Non-reduce 集合     uniRunner : 在同构场景下，一些通信原语能持平厂商原生优
通信技术，并依托 FlagOS 社区自研的 Device-              化后的通信库（homoRunner），在异构场景能达到之前实现
buffer IPC/RDMA 能力，不依赖厂商原生通信库，             （HybridRunner）的4.57倍。
有助于新芯片快速获得完整通信能力。

## Page 32

目 录 CONTENTS
    1. FlagScale大模型训推框架介绍
    2. 通过自动化技术实现跨芯片迁移
    3. 通过FlagCX统一通信库实现跨芯片协同
    4. FlagOS统一生态应用示例

## Page 33

    支持大规模参数高效微调训练功能


        LoRA                          transform
                                (linear->LoRALinear)    TERowParallelLinear
        apply_transform                                       (h’, r)
Pretrain                              transform  TERowParallelLinear   x (s/tp, r)
  Model     freeze_model   DoRA (linear->DoRALinear)   (h’, h)
                                                                       TELinear
        load_state_dict    QLoRA      transform      (r, h) x (s/tp, h) LoRALinear
                                (linear->QLoRALinear)                  x (s/tp, h)

        Finetune Framework  Transform to LoRA Linear        add

        x (s/tp, h)
        LoRA Linear Execution
    • 简单易用，只需在 YAML 中配置相关参数即可一键启动微调。
    • 复用预训练已有功能，通过匹配自动替换模型中的线性层，无需修改核心模型结构，保持并行策略兼容性。
    • 通过PEFT 基类抽象，自动实现模型转换、参数冻结，可扩展到 LoRA、DoRA、QLoRA 等多种微调算法。
    • 高效分布式训练，适配多种并行策略，如 Tensor Parallel / Sequence Parallel等。

## Page 34

        支持RWKV-7模型的高效训练

    •   实现RWKV的完整迁移和训练验证
       o 支持Time Mix、Channel Mix等核心模块，在FlagScale中完整支持RWKV-7模型。
       o 支持数据加载、参数保存、与Huggingface参数互转、分布式优化器，可实现高效分布式训练。
       o 在不同模型规模下均实现了加速效果，最大加速比达到34%，平均加速比约为20%。

                        1.6
                        1.4  FlagScale DeepSpeed
                        1.2
                          1
                        0.8
                        0.6
                        0.4
                        0.2
                          0  0.1B  0.4B      1.5B      3B    7B
        RWKV模型结构










Speedup

## Page 35

    支持Diffusion类模型高效灵活推理功能

        DiffusionEngine
    ModelLoader     Transformation
(diffusers/custom)  (TaylorSeer/torch.compil
        e, …)


Model/Pipeline
   Execution


    功能优势           支持模型
        模型和优化解耦        FLUX.1-dev
        非侵入式设计         Qwen-Image
    •   易用易上手      •   Wan2.1-T2V-1.3B-Diffusers

## Page 36

 支持具身VLM+VLA全链路训推

 VLM大脑模型        VLA端到端模型    端云协同





                                FlagScale

 训练挑战          推理挑战         端云挑战      训练优化      推理优化                  端云优化
 •数据处理低效       •云端场景多       •流程复杂       •多类型大规模分布    •提供推理多后端         •共建RoboOS
 •训练性能低        •部署策略多样化     •跨设备高并发通信    式加载            •一键自动调优部署     •定制化端云通信
 •显存容易OOM      •推理延迟敏感      •技能多且不标准    •不均匀细粒度并行       •硬件感知量化压缩     •技能MCP化和检索
                                •有选择重计算
训练吞吐提升154.81%  推理延迟减少22%-23%      输入token减少65%，技能检索token减少29.8%，通信延迟平均<3ms

## Page 37

 支持不同类型的超节点上训推

 浪潮 SD200 超节点支持    海光 Nebula 超节点支持









•   已适配FlagScale，支持预训练、微调、推理等功能，     •   已适配FlagScale训练自动调优，十分钟内搜索出较优配置。
    支持DeepSeek和Qwen模型。               •   在32B+32K序列长度下，实测千卡弱扩展效率超过98%，强
•   经实测，在64卡上的扩展效率近线性。                   扩展效率超过90%。

## Page 38

支持超节点上高效通信

    • 在ChipB 超节点上支持9种通信操作，平均带宽达
          到原生99.8%，具体包括：
          o AllReduce, ReduceScatter, Reduce
          o Broadcast, Scatter, Gather, AllGather
          o AlltoAll, SendReccv
    • 未来将引入P2PAdaptor，通过FlagCX Core原生
          支持超节点通信。

## Page 39

实现统一通信库国家与国际标准“双立项”
推荐性国家标准（GB/T）进展                       ITU国际标准进展
《人工智能 统一通信库接口规范》    《Requirements and Framework of Cross-Platform
                   Unified Communication Libraries for Distributed
                               Multimedia AI Systems》







•   进行4次标准研讨，国标委下发推荐性国家         •  联合10+参编单位
    标准顺利获批（立项计划号 20255428-T-    •  在国际ITU-T SG21 全会立项通过
    469）
•   收集20+单位，200余条意见             •  获得来自美国、德国、英国、俄罗斯、日韩等
•   针对专家意见完成3版修订        多国专家的共识

## Page 40

   支持百度飞桨框架实现多芯片分布式训练和异构混训

飞桨+FlagCX适配情况        FlagCX提交给飞桨的PR列表
    集成百度飞桨3.0正式版本
    支持天数，昆仑芯，英伟达平台上文心一言4.5训练
•   打通英伟达+天数平台文心4.5混训

同构零开销        支持稳定异构混合训练
•   使用flagcx和使用厂商原生通信库训练效率一致    • 基于FlagCX异构通信能力在英伟达和天数平台稳定训练






    注：图中吞吐率已进行归一化处理

## Page 41

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进.pdf]]`
