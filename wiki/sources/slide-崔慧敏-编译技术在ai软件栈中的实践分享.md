---
type: source
source-type: slide
title: "崔慧敏_编译技术在AI软件栈中的实践分享"
path: slides/崔慧敏_编译技术在AI软件栈中的实践分享.pdf
size: 14286 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 崔慧敏_编译技术在AI软件栈中的实践分享

> Ingested from `slides/崔慧敏_编译技术在AI软件栈中的实践分享.pdf` via `lit parse` on 2026-06-04.
> Source file: 13.95 MB.

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

编译技术在AI软件栈中的实践分享

主讲人： 崔慧敏

## Page 7

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 8

 AI基础设施投资持续增长，           国产化势不可挡
                     AI投资保持战略重点
                     IDC预测，2025年全球2000强企业会将超过40%的IT预算投入到人工智能项目中； 2025年全球企业生成式人工智能支出预计将达到691亿
                     美元，2028年超过2,022亿美元
RAG    《2025年中国人工智能计算力发展评估报告》
     生成式推荐                             算力需求持续高速增长
                     自动驾驶              全球AI芯片算力呈现爆发式增长态势，预计到2025 年全球计算设备算力总规模将超过3ZFlops，至
                                       2030年将超过 20 Zflops
                                       中国信通院《中国算力发展指数白皮书(2023年)》
                         AI                   国产芯片增速领跑
                         agent                国产AI芯片销售额从去年的60亿美元增长至160亿美元，市场份额从29%提升至42%，
                                              增速达到112%，约国外芯片的三倍
                                       具      伯恩斯坦《2025中国芯片行业大报告》
                                       身 私有化需求稳固
                                       智
                                         能               全球 2023 年公有云收入占整体云基础设施支出约 73%（私有云约占 27% ）
HBM                                                      Gartner《Forecast Analysis: Public Cloud Services》
 TensorCore    ……                                        2025年至2027年，一体机需求量将从15万台增长至72万台，对应市场空间预
                                                         计从1236亿元增长至5208亿元，增速达321%
     硬件层                          大模型&AI应用               浙商证券研报

## Page 9

模型与硬件飞速演进，软件优化释放算力潜力

                                     AI基础设施软件：大模型生态的“软底座”
                                  •   支撑大模型训练与推理
                                  •   决定性能天花板
RAG 生成式推荐                                 承上启下：连接应用与算力，屏蔽硬件差异
                       自动驾驶                             •  对上理解丰富的业务需求
                                                        •  对下适配多元化的算力
                                      AI agent                优化挑战
                                          具                •   硬件多样性：AI硬件多样，架构差异大，但都高度依赖软件
                   BLAS                   身                    进行优化
                                          智
                   DNN                    能                •   编程复杂性：硬件“偷懒”，编程难度NPU > GPU > CPU；架
    Runtime                                                    构迭代快，工具链成熟度相对较低
HBM                Driver                                  •   系统复杂性：从多核 → 多卡 → 多机，需处理通信、同步、
TensorCore  ……     运行时系统     算子库     AI推训框架 模型层   应用层          负载均衡等问题，通信/计算重叠、显存管理、算子融合、张
    硬件层                                                        量切分等需深度协同优化

## Page 10

    私有化部署需求大幅提速
•   推理算力市场规模、私有化需求齐头并进：据弗若斯特沙利文《中国推理算力市场追踪报告，2025年H1》预测，中国推理市场算力将于未来3年
    完成超6倍增幅；随着AI从训练为重走向推理为主，私有化环境及边缘的部署需求迎来爆发，推理平台及应用部署偏好数据预测显示，私有云占
    比将由2023年的13%提升至26%（2027年）。

•   信创迎来 100% 替代冲刺：根据国资委79号文要求，2027年前央企国企核心系统需实现100%信创替代。这一举措将涵盖芯片、操作系统、数据库
    等全产业链，推动信创技术在关键领域的广泛应用。

•   AI平权推动一体机市场近三年 增幅度超三倍：DeepSeek技术创新带来部署成本及API/token价格的断崖式下降，推理市场爆发增长，浙商证券研
    报数据，2025年至2027年，一体机需求量将从15万台增长至72万台，对应市场空间预计从1236亿元增长至5208亿元，增幅超三倍。

   中国推理算力市场规模，2024年-2028E     模型训练与推理的算力需求及工程化难度对比表        2025-2027E 一体机需求量及市场空间

                                                       80                           6000

                                                       70                           5000
                                                       60
                                                       50                           4000

                                                       40                           3000

                                                       30                           2000
                                                       20
                                                       10                           1000

                                                        0                           0
                                                           2025年  2026年  2027年

                                                           一体机需求台数（万台）   一体机市场空间（亿元）



    数据来源：沙利文、头豹研究院                                     数据来源：浙商证券研报

## Page 11

   推理私有化部署场景，开启新一轮智能化进程
   大规模算力部署场景：城市、企业大型智算中心    中小规模算力部署场景：企业中小型智算中心








   一体机部署场景：小规模用户量本地大模型应用    端侧部署场景：手机、平板、AIPC等移动端AI应用


  场 景
“ 飞 轮 ”

                                基 础 设 施
   海内外主流开源大模型、闭源大模型、行 模 型       “ 引 擎 ” 算 力
   业大模型、传统模型等        “ 大 脑 ” “ 基 座 ” 海外及国产AI芯片

## Page 12

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 13

私有化部署面临的挑战


    硬件繁多                                          需求多元                        多模部署

•   硬件特性参差：大 模 型 推 理 涉 及 多                •   丰富的业务需求：不 同 业 务 场 景                  • 兼容性要求：不同模型往往针对不同硬
    种计算设备，包括 G P U、C P U、N P U等。              对使用场景提出不同需求，且迅速迭代，              件进行优化，可能依赖不同框架或版本，私
    不 同 硬 件 架 构 的 算 力 特 性 差 异 巨 大 （ 如         如上下文长度、多摸态等                     有化部署方案需要具备良好的兼容性
    C P U侧的x 8 6、鲲鹏）同品牌不同型号的              •   场景对性能需求的差异：不 同                        • 算力资源利用率较低：多模型混合部
    特性亦有较大区别（如昇腾910B1-B4）                     场景对于吞吐、时延等需求不同，单一               署时，不同任务对硬件需求不同，大量算力
•   优化门槛高：大 模 型 的 计 算 模 式 对                   版本难以满足不同场景对应用体验的需               可能因调度不佳或内存带宽瓶颈被浪费
    硬 件 要 求 极 高 ， 厂 商 需 针 对 不 同 硬 件 特     •   要                              • 监控和维护复杂：多 模 型 部 署 需 要 对
    性 进 行 针 对 性 优 化 ， 否 则 会 导 致 性 能 严         S L O 要 求 ： 系 统 对 服 务 等 级 目 标   模型性能监控、资源使用率监控、动态扩缩
    重下降或兼容性问题                                 （SLO，Service-Level-Objective）   容、故障定位等提出更高的要求
•   软硬件协同程度低：复杂的异构硬                           的约束，用户对系统在可用性和平均响                     • 数据安全与隐私要求：私有化部署，
    件 场 景 带 来 迁 移 困 难 ， 国 产 芯 片 适 配 性         应时间方面提出更高的要求                    尤其在多模型共享硬件时，对数据隔离、模
    和软件生态的完备度有待提升                                                             型安全等提出更高要求

## Page 14

算力性能释放的瓶颈
算力固定，但负载并不均衡                                    DeepSeek 推理服务波动情况
•   时间维度：有波峰有波谷
•   空间维度：序列长短不一，“空洞”
Roofline 天花板：计算特征决定“理论上限”
•   Prefill计算特征：计算密集
•   Decode计算特征：访存密集（计算不饱和）
•   混合阶段（Prefill+Decode 同卡）出现“双瓶颈交替”，任一阶段触顶即
    宣告整体上限                                      The Roofline Model
并行损耗：“大模型”切成“小碎片”的损耗
•   张量并行：AllReduce通信开销
•   流水并行：Pipeline Bubble难以完全克服
•   专家并行：门控负载不均，出现专家“围观”现象
实现效率
•   并行效率
•   通信效率        单点效率 × 协同效率
•   算子效率                                    •   Memory bound区间：算力有空余，增大batch有利于增大系统吞吐量
•   ...     系统效率：                           •   Compute bound区间：增大batch不会再增加系统吞吐量

## Page 15

    AI软件栈构建现状

    烟囱式的软件生态加剧了大模型推理私有化部署在国内 AI 生态的落地困难

    NVIDIA生态                                       国内算力技术生态

                   第三方公司        AI应用方                第三方公司+芯片企业
Runway, Midjourney, Microsoft, Character.ai    互联网厂商，行业ISV，芯片厂商A，芯片厂商B

              第三方公司（模型+算子）                模型研发方      第三方公司+芯片企业
OpenAI, Google, Stability.AI, Mistral AI       互联网厂商，大模型厂商，芯片厂商A，芯片厂商B

                以第三方公司为主                  框架研发方        芯片企业为主
       Meta, Google, Microsoft, ….             芯片厂商A，芯片厂商B，芯片厂商C，芯片厂商D

                 Nvidia        算子提供方                   芯片企业为主
              400万+CUDA开发者                     芯片厂商A，芯片厂商B，芯片厂商C，芯片厂商D

    基于Nvidia CUDA的统一生态                                硬件异构下的烟囱式隔离型软件生态

## Page 16

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 17

高性能大模型推理引擎SigInfer

    高效支持主流大模型行，广泛适配国产算力

API Server                    异步推理框架        异构抽象层
                          请求调度、缓存管理和推理阶段调度
                                                                         数据类型
Serving      [Request]        Scheduler
Engine      [Output]      Batch Manager      Batch Cache Infer-Stage     运行时库    异构硬件平台
                          Cache Manager
Web Server                    Prefill
                          Model Executor
    [OpenAI API]          Sample & Decode    Decoding                    算子库
User

## Page 18

高性能大模型推理引擎SigInfer
 算力性能释放的瓶颈                   SigInfer的应对机制

            算力固定，但负载并不均衡     ① 面向长上下文的优化

 Roofline 天花板：计算特征决定“理论上     ② 大模型PD最优配比；多模态大模型EPD分离
                      限”

并行损耗：“大模型”切成“小碎片”的损耗         ③ Prefill/Decode阶段低损耗并行模式定制

 实现效率                        ④ 深融合高效算子实现

## Page 19

  ① 面向长下文优化：极致显存利用

显 存  算子工作空间  激活    权重  KV Cache
=

       ∝ 上下文长度        如何最大化？

## Page 20

   ① 面向长下文优化：极致显存利用

显 存  算子工作空间  激活    权重  KV Cache
=

     独立的算子工作空间     全图复用的算子工作空间

     算子A  算子B  算子C  算子D    算子A  算子B  算子C  算子D

     中间张量 中间张量 中间张量 中间张量    中间张量 中间张量 中间张量 中间张量

       复用

## Page 21

    ① 面向长下文优化：极致显存利用
 显 存 =  算子工作空间            激活    权重               KV Cache
 上下文长度 ↑  激活所占显存 ↑                           根据roofline拐点
        MLA计算访存比 ↑                           确定上下文Chunksize
                              计算访存比          最大化激活显存的性能转化
                                             <架构相关>
                      •   拐点左侧：激活多占空间可换来吞吐提升
                      •   拐点右侧：激活多占空间无法继续提升吞吐










吞吐

## Page 22

   ① 面向长下文优化：极致显存利用

显 存  =  算子工作空间  激活    权重  KV Cache


                                                   KVCache    KVCache
                Shard     Shard                     (R0)       (R2)
       TP <其他算子>      DP：权重冗余 0+1 0+1              KVCache    KVCache
   TP2DP                                            (R1)       (R3)
            DP <Attention>
   DP2TP        Shard 0                            KVCache    KVCache
                                                    (R0)       (R0)
            TP <MLP>      TP：KV Cache冗余    Shard 1 KVCache    KVCache
                                                    (R1)       (R1)

   用通信换取显存占用的降低        GPU0      GPU1              GPU0          GPU1

## Page 23

① 面向长下文优化：极致显存利用

      140    128K                                    1000000
      120                                                 799488    最高提升 640%
      100    96K                                      800000
支
持
的
上
下
文
长
度（K
B）        有
          效
          K
          V
          C
          a
          c
          h
          e
          容
          量 （#
          o
          f
          T
          o
          k
          e
       80    64K    64K    ns）                        600000        540416
       60        48K                                  400000
       40    32K
       20                                             200000    124928    131872

        0                                                  0
          910B4 32G*32  910B1 64G*16  910B1 64G*32        H20 96G*8       910B1 64G*8

          优化前（K）     优化后（K）                               优化前（K）     优化后（K）

## Page 24

 ① 面向长下文优化：极致显存利用
SigInfer具备更好的性能扩展性
     Ascend910B1 Qwen3-32B模型 2卡推理性能









 Ascend910B1 DeepSeek-671B-INT8模型 16卡推理性能

## Page 25

  ② 大模型PD配比分析
• 科学问题 —— 给定P+D的总吞吐，PD配比受什么因素影响？
• 观察：P节点计算密集，单机吞吐不随batch增加而增加；D节点访存密集，单机吞吐随batch增加而增加
• 思路：以P+D总吞吐为约束，考虑P单机吞吐变化时，PD配比、D单机吞吐如何变化
  ：RPS（每秒完成请求数）需求  ：P每机RPS  :1  ：D每机RPS
• 结论：     ≥ ⇒ =    −， = −       P单机吞吐为
                                P+D总吞吐的2x时，
                                PD配比1:1
          且对D单机吞吐要求更高（优化成本高）

## Page 26

② 多模态场景EPD分离
多模态模型通用架构：               E的特点①：资源需求
Vision Encoder + LLM     与D存在互补性
(E)    Qwen2-VL-7B 各组件对 Streaming Multiprocessor (SM)
                         分配的时延敏感性分析

                        E的特点②：最佳并行
                        策略存在动态性





最优并行策略在低分辨率范围内为单 GPU，
而在高分辨率范围内转变为 4-GPU 张量并行

## Page 27

② 多模态场景EPD分离
EPD分离：Encoder，Prefill，Decode解耦架构

            •   即时并行(JIT-P)：动态选择 Encoder 的最佳并行策略，优化TTFT
               •   Performance Atlas: 离线构建性能模型
               •   PRISM Scheduler: 运行时动态规划选择最佳 DP/TP 组合

            •   即时空间分区(JIS-P)：动态分配 Encoder和 Decoder 的计算资源，优化 TPOT
               • LASER Allocator: 同一GPU 上同时运行Encoder和Decoder








                   不同请求速率下 相比 vLLM 显著降低延迟（3.3 - 29.7x）

Zhicheng Li, Shuoming Zhang, Jiacheng Zhao, etc. SpaceServe: Spatial Multiplexing of Complementary Encoders and Decoders for Multimodal LLMs. (NeurIPS 2025)

## Page 28

    ③ 低损耗并行模式的国产化实践
    TP的损耗：KV Cache重复存放        Prefill：Chunked Prefill Pipeline Parallelism(CPPP)
    DP的损耗：Weight复制带来的开销 & 无TTFT收益  Decode：DP + EP
    PP的损耗：请求TTFT成倍增长

                               DeepSeek测试：增大EP size，每机吞吐提升
                           7000
                           6000
                           5000
                           4000
                           3000
                           2000
                           1000
                              0    32    64
                               EP size










TPS per node

## Page 29

   ④ 深融合高效算子实现
    破除“优化墙”：通过深融合扩大优化空间至全模型+跨模型



     从 LLVM-IR 上发掘 Kernel 层的全程序优化




     从张量表达式上发掘亚算子级优化




  计算图上进行算子融合时   从微算子间发掘组合优化机会
能看到算子内部的指令效果更好

## Page 30

  ④ 深融合高效算子实现

 从 LLVM-IR 上发掘 Kernel 层的全程序优化  从张量表达式上发掘亚算子级优化  从微算子间发掘组合优化机会

## Page 31

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 32

国产卡兼容CUDA生态的探索与实践

•    CUDA语言兼容
   • 基于2D向量化的CUDA-NPU编译器（昇腾、寒武纪）
•    CUDA工具兼容
   • 面向海光DCU的CUTLASS编译优化

## Page 33

CUDA-NPU的技术挑战：SIMT 到 2D SIMD








CUDA语言：SIMT并行范式




GPU：SIMT CPU：1D SIMD NPU：2D SIMD

## Page 34

   1D SIMD与2D SIMD
• 1D向量化:                                                                 index:       tx     tx        tx     tx
   • 最内层或最外层1个loop nest                    tx:                                        1      2         3      4
• 2D向量化:                   combine to                                    Index_x:     tx     tx        tx     tx
                           2-D                                                        1      2         3      4
   • 建模CUDA的隐式多维并行语义       vectorization   bx:                           index:       bx1                       bx2   符合NPU
   • 分析各并行维度向量化潜力                                                        Index_x:                                     align要
   • 选择2个维度，组合进行2-D向量化                                                       bx1, bx2, ...                            求
                                                                         index:       ty1              ty2      ty3   不符合NPU
                                           tx:                           Index_x:                34                   align要求
                                                                                      bx1, bx2, ...
kernel of Rodinia bench backprop case, gridDim: (1, 4096); blockDim: (16,
16)

## Page 35

T2T - Threads to Tiles via 2D Vectorization

核心思想  基于统一并行抽象的2-D向量化

Unified Parallelism Abstraction (UPA)      2-D向量化与优化
l 完整捕获CUDA程序的多维并行(7-D)        l 访存、控制流、warp-level function

① 建模CUDA并行语义

② 分析并组合进行2-D向量化

③ 控制流掩码操作优化

④ shuffle, vote等原语向量化

⑤ NPU IR及平台相关优化

## Page 36

 UPA – 完全捕获CUDA的隐式并行
• UPA Function        • UPA Unit
 • 对应一个CUDA __global__ function       • Outmost perfect nest of loops（Parallel Regions）
 • 包含多层Parallel Regions 和UPA Units    • 向量化处理与优化的最小单位
     • 初始UPA Function只包含一个UPA Unit，经过loop
                                fission，变为多个UPA Units

                                        Loop
                                              fission










                                        36

## Page 37

2D向量化 - Analysis
• Parallel Region Vectorizability Analysis:
• 分析访存指令对包含其的每层UPA Parallel Region的向量化属性，由此综合
    得到每层PR的向量化属性
• Transparent（Trans, 可与其他属性进行组合）
   • 其所有循环迭代访问同一个内存位置。                                  offset 如何随 loop iterator 变化
•   1D-continuous-vectorizable（1D-C, 可与1D-S组合实现2-D向量化）
   • 每次循环迭代访问一个长度恒定、占据连续len字节的内存区域，且相邻两次循环迭             Trans
       代访问的两个内存区域也是相邻的，同时总的内存占用len * tc满足NPU对齐约束。
•   1D-strided-vectorizable（1D-S, 可与1D-C组合实现2-D向量化）     1D-C    t1     t2    t3 t4
   •   如果每次循环迭代访问一个数据元素，且相邻两次循环迭代访问的元素之间的
       stride在所有迭代中保持不变，且该 stride 满足NPU对齐约束。            1D-S    t1              t2
• 2D-tile-vectorizable（2D）
   •   如果其所有循环迭代可以被均匀划分为若干区间，并满足：                       2D      t1     t2       t3    t4
   • 每个区间中的所有循环迭代访问同一个连续的内存区域，且该区域长度len在所有区
       间中保持不变，且 len 满足 NPU对齐约束；
   • 相邻两区间访问的内存区域之间的stride在所有区间中保持不变，且 stride 满足        Non            Others
       NPU对齐约束。
• Non-vectorizable：不满足上述条件的情况。

## Page 38

2D向量化 – Plan generation
                                                     • PR  fusion：对相邻且符合要求的PRs进行fusion，可实现对更
2-D Vectorization Plan Generation                   多PRs的向量化，并实现对向量化方案生成的搜索空间的剪枝
• 核心思想：在SPM使用量不超过硬件SPM容量的约束下，                        • PR combination：按照PRs的向量化属性，根据组合规则进行判
最小化其动态2-D指令数。                                       断，哪些PRs可组合成2-D向量化
• PR Fusion + PR Combination + Deferred Decision     • Deferred decision：编译时当前未知信息（如硬件SPM容量、
                                                    gridDim等），推迟决策，等到编译流程后期或运行时进行决策，
                                                    选择性能最好的向量化实现。

                 PR Fusion：Wid + txg fuse -> ty
                 PR Combination: tx + by -> 2-D向量化





                                                     38

## Page 39

    昇腾910B + 寒武纪MLU370实验结果

    Benchmark: AI CUDA Engineer + Rodinia    平台/性能对比        910B           MLU370
                                                        avg   up to    avg   up to
    performance：运行性能与硬件峰值性能的比例：            AI CUDA      51%    74%     34%    56%
                                          Engineer
    • NPU上该比例为a%, GPU上该比例为b%, 我们展示的是a/b    Rodinia      41%    73%     26%    48%
        Ascend 910B                                         Ascend 910B






AI CUDA Rodinia
Engineer MLU370
        MLU370









                                                        39

## Page 40

海光DCU CUTLASS 核心优化点


          03

          指令调度优化
          优化以 DPP 指令为核心的数类规约操作
      02        04

      控制流优化                       BufferLoad 优化
      优化边界检查产生的大量分支    更好地实现边界检查优化和 StaggerK 优化
                                       节约地址计算指令

01        核心        05
混合精度 FMA 指令支持                                    StaggerK 优化
支持硬件内积指令 v_dot2_f32_f16 等    优化点  优化全局内存访问的 channel conflict
添加全流程优化的数据通路

## Page 41

 指令调度优化




良好的指令流水对GPU的性能发挥非常重要
•   数据通路1：GlobalMemory -> SharedMemory    理想的指令流水    time
•   数据通路2：SharedMemory->ALU（乘加运算）
•   流水线机制：设置多块SharedMemory工作区，流水并行



理想的工作方式
•   Load GlobalMemory 的延迟被充足的（不相关的）Load
    SharedMemory 和 Math指令掩盖
•   Load SharedMemory 的延迟被（不相关的）Math指令掩盖
•   Store SharedMemory 的延迟被（不相关的）Math指令掩盖


    GPU与CPU不同，一般不具备很强的动态调度能力，指令的（静态）发射顺序很重要

## Page 42

指令调度优化
    优化机会1：隐藏LDS 访问延迟




优化前：



优化机会2：隐藏Global Load 访问延迟 优化机会3：隐藏 Shared Write 指令延迟（需wait）








优化后：

## Page 43

指令调度优化

      优化机会1：增强别名分析，以提
      高指令依赖分析精确度

      优化机会2：充分考虑store的代价




优化前:    优化后:

## Page 44

BufferLoad 优化

BufferLoad 格式                 •     Tile 块是整个 ThreadBlock 一起移动的（sgpr）
•  128 位的胖指针
•  32 位 uint 的 vgpr offset    •     Tile 块整体移动时，每个读取单元相对于 Tile 块
•  32 位 uint 的 sgpr offset
•  32 位 uint 的 glc_slc              首地址的偏移是恒定的（vgpr）
优势：同时完成 ptr+vgpr+sgpr 地址计算，效果如下

   优化前

    优化后

## Page 45

StaggerK 缓解 Channel Conflict

         优化前：同时访问 0-0/1-0/2-0/3-0
         对Matrix A/B的四个 Block Tile 的访问，在Channel相关的地址位上没有区别，引发冲突

             tep = K * BLOCK_M * sizeof(Type) = 4096 * 128 * 2 = 2 ^ 20
             channel无关地址位        channel 相关地址位
Matrix A
Row Major









Matrix B
Col Major

## Page 46

StaggerK 缓解 Channel Conflict

         优化后：
         通过调整ThreadBlock对Block Tile的访问顺序，使访存地址在channel相关地址位上引入差异，消除冲突
             Step = K * BLOCK_M * sizeof(Type) = 4096 * 128 * 2 = 2 ^ 20
             channel无关地址位    channel相关地址位
Matrix A
Row Major









Matrix B
Col Major

## Page 47

CUTLASS 优化效果



整体优化结果：


FP32: 92.82%


FP16: 108.06%


INT8: 115.71%




FP16：V1：40.29%；Final：108.06%

## Page 48

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 49

传统编译器后端开发流程 V.S. AI辅助的开发流程

 利用AI模型辅助后端开发
  • 挑战：现有模型在后端代码任务上准确率低，缺乏专用数据集进行微调训练
  • 动机：模仿人工开发方法，从已有后端中寻找后端代码的规律

## Page 50

   VEGA：   基于AI的编译器后端生成方法

   模板化：     特征提取与表示：     模型训练：
公共代码和变量代码提 部分出现的语句和特定值映射成为特征向量 利用模板和特征向量微调训练
取









        代码生成：
        用户提供 *.td、*.h中的enum、*.def，自动生成后端，并给出置信区间

VEGA: Automatically Generating Compiler Backends using a Pre-trained Transformer Model, CGO'25

## Page 51

VEGA： 基于AI的编译器后端生成方法
 正确率（无需任何人工修改）
  • 平均正确率(7个模块正确率求平均): 69.9%, 69.3%, 69.1%, 55.6%
  • 整体正确率(正确函数/全部函数): 68.3%, 70.3%, 61.7%, 54.2%
  • 局限性：在较短的函数上正确率较高，在长难函数上正确率低










VEGA: Automatically Generating Compiler Backends using a Pre-trained Transformer Model, CGO'25

## Page 52

         传统编译器  大语言模型编译器

       编译：高级语言到低级语言的翻译和优化

 编译器：源语言(源代码)---目标语言(汇编)
 LLM：自然语言---自然语言
 具有相似性


 数据集: 使用现有编译器将源程序生成汇编，进行语料对齐
 挑战: 编译器直接生成的语言对，不易学习
 编译器生成汇编：面向机器运行，而非面向人类/大模型
l 如何表示数字
l 如何表示控制语句
l 如何表示特定指令/操作
l 如何正确处理语料稀缺的指令/操作

## Page 53

目 录 CONTENTS
    01. 私有化部署的需求
    02. AI基础设施的挑战和现状
    03. SigInfer：以编译为核心的高性能AI推理引擎
    04. 国产卡兼容CUDA生态的探索与实践
    05. AI for Compiler：基于AI的编译器自动生成
    06. AI软件栈未来若干发展方向

## Page 54

 AI软件栈未来若干发展方向
            AI基础设施软件是大模型生态的核心底座
它不仅决定模型能否“跑得快”，更决定能否“跑得稳”“跑得省”，是大模型走向产业化的关键支撑

    01 算力形态：从“集中式”到“泛在异构”                                 02 系统架构：从“单机峰值”到“能效密度”

 •     多极化：中心云  区域池  边缘节点  端侧NPU，形                     •   机柜即计算机：NVL72 NVL144， CM384  Atlas 950
       成云、边、端连续体                                              SuperPoD（8192） Atlas 960 SuperPoD（15488）
 •     异构化：GPU、NPU、DSA架构共存，国产芯片担当大任

    03 AI框架：从“大模型导向”    到“Agent导向”                        04 软件栈：从“框架+库”到  “AI-Native 平台”

    •   多模型部署，多智能体联动                                   •     统一调度 Batch、Streaming、Agent 三类负载，支持 长时
    •   MaaS（Model-as-a-Service）  AaaS（Agent-as-a-          记忆、上下文缓存、多代理编排
        Service）                                       •     编译与并行协同：MLIR+DSL 打通“图-算子-芯片”多级 IR，
                                                             自动并行+自动调优替代手工切分，缩短 50 % 调参时间

## Page 55

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/崔慧敏_编译技术在AI软件栈中的实践分享.pdf]]`
