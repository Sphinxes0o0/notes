---
type: source
source-type: slide
title: "郑杨_面向多元AI芯片的算子库和编译器"
path: slides/郑杨_面向多元AI芯片的算子库和编译器.pdf
source-md5: e0b959bf725dd24b616e18dfd4f45d70
size: 6721 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 郑杨_面向多元AI芯片的算子库和编译器

> Ingested from `slides/郑杨_面向多元AI芯片的算子库和编译器.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.56 MB.

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

面向多元AI芯片的算子库&编译器
建设实践与思考

智源研究院 郑杨
2025.12

## Page 7

目 录 CONTENTS
    众智 FlagOS 软硬件统一生态概览
    大模型通用算子库 FlagGems
    多元芯片统一编译器 FlagTree
    众智 FlagOS 发展历程与生态建设

## Page 8

_(no text content on this page)_

## Page 9

    众智 FlagOS：    面向多元 AI 芯片的系统软件栈
            AI大模型                                           已支持大模型
    (语言大模型，多模态大模型，MoE架构等)              语言模型                  多模态模型      具身智能模型
                                  DeepSeek，Qwen，        智源 EMU，面壁 CPM，     智源 RoboBrain
           深度学习框架                Seed-oss，GPT-oss，    Qwen-VL系列，ERNIE4.5,        Pai-0
（PyTorch, PaddlePaddle, etc）    Step, Grok，Llama 等          Llava系列
        众智FlagOS v1.5：面向多种AI芯片的系统软件栈                                   各种大模型
        开源核心库             开源工具         各种深度学习框架
                     Triton-Copilot
FlagGEMs:  FlagScale:   算子自动生成工具
通用大模型算子库    训练推理并行框架   FlagRelease        统一自主软件栈：统一支持
FlagTree:    FlagCX:    自动迁移和发版工具        各种AI芯片
  统一编译器       统一通信库     FlagPerf
                         多芯片评测工具        各种的智算集群
      后端编译 底层通信    后端编译   底层通信    后端编译   底层通信    • 芯片企业：超过10家芯片企业，20多款不同芯片
   器 A      库 A     器 B    库 B     器 C    库 C    数据中心                   机器人        边缘
      芯片 A        芯片 B             芯片 C        (train & Inference)  (cloud-edge    (inference)
                                                                   cooperation)

    已支持的硬件架构: GPGPU, DSA/NPU, RISC-V AI, ARM

## Page 10

_(no text content on this page)_

## Page 11

FlagGems：为多硬件生态构建 AI 通用算子层
https://github.com/flagos-ai/FlagGems
一个使用 Triton 语言实现的大模型通用算子库
• 平均加速比达到130%
• 85%以上的算子性能持平或优于 PyTorch ATen









speedup>1    speedup≈1

## Page 12

FlagGems：为多硬件生态构建 AI 通用算子层

替代CUDA算子库，全球最大、支持芯片种类最多的大模型         Ø 持续优化算子性能
通用算子库：                              部分性能低洼算子，性能超越
ü 实现了超过200个算子，平均性能优于CUDA            CUDA算子30% 以上                   优化技术
ü 支持了16家芯片厂商的25款AI芯片，且覆盖 GPGPU、     hstack/stack/cat            批处理融合，减少kernel 启动次数
DSA/NPU、RISC-V AI 和 ARM 多种架构        slice_scatter/select_       统一内存访问，后维乘积预计算，避免
                                    scatter                     kernel内昂贵的除法/取模运算
                                    full/full_like/fill/fill_   应用@dynamic_pointwise 装饰器，自动代
Ø 提升推理场景覆盖度和性能：重点模型全覆盖，且性能逐渐追平                                  码生成
原生                                  cumsum/cummin               根据输入张量形态，细化设计三种kernel
    模型名称              覆盖度       性能
                           优化前   优化后
Qwen2.5-7B-Instruct  100%  35%   95%
Qwen3_30A_A3B        100%  25%   92%
Qwen3_8B              92%  98%  104%

## Page 13

FlagGems：为多硬件生态构建 AI 通用算子层

Ø 基于 CPP JIT Runtime 的算子封装层
实现了 CPP 的算子封装层替代原有的 Python 算子封装
层。累计 20 个算子升级为 CPP 封装层，单个算子的性
能提升 20% 以上。
Wrapper  libtorch   torch     triton     triton
time     (cpp)      (python)  (python)   (cpp)
add      14.44us    14.44us   61.11us    14.44us
sum_dim  17.78us    18.89us   82.22us    16.67us
Kernel time     torch        triton
add             2.126us      2.097us
sum_dim         8.805us      4.538us

## Page 14

 FlagGems：为多元 AI 芯片提供更好的性能

Ø PreTune 离线搜寻最优内核配置
问题：online AutoTune 造成推理耗时陡增
方案：采用离线搜寻机制，建立Shape与内核参数对应关系，online 直接查表获
取内核参数，避免搜索耗时
① 核心亮点
• 通过预执行自动调优提升效率，彻底消除运行时开销
• 持久化存储使Pretune结果可复用、可共享，并便于分发
• 借助多级缓存加速自动调优——即使缓存部分命中也能节省时间
② 技术实现
• 基于SQL的存储架构赋予Pretune结果多级缓存与离散化键值存储优势——既
 加速查询又简化数据分析
• 智能性能优化通过懒加载实现——仅在缓存未命中时查询，启动时绝不加载整
 个数据库
• SQL驱动的并发能力通过多线程与多进程提升自动调优效率——完美适配现代
 推理框架的工作流程
收益：应用于 Qwen2.5-7B-Instruct，推理性能提升40%

## Page 15

FlagGems：算子库演进路线的思考

 提升开发效率       •    编程语言保持易用性
              •    AI for Operator : Triton-Copilot

 算子库  提升覆盖度   •    领域首发：起步于算法研究阶段
              •    扩充到更多领域：计算机视觉、科学计算

     提升性能 • 基于硬件感知的融合规则，软硬件协同优化
     • 从计算图到 MLIR，再到 LLVM 多级联合优化

## Page 16

_(no text content on this page)_

## Page 17

 FlagTree：愿景与目标
Ø 用户价值：一站式开发体验
  •   上层支持：提供统一的Triton（类似CUDA的高性能计算语言）兼容层，用户无需关心底层硬件差异
  •   工具链整合：将编译、优化、调试等工具集成到同一框架中，避免在不同工具间切换
Ø 技术目标：增强型编译技术
  •   统一中间表示（IR）：设计硬件无关的中间层，支持多芯片后端的代码生成和优化
  •   性能优化：
     ü 一是聚合社区和厂商的优化技术（如自动并行化、内存优化），形成共享技术池
     ü 二是可能引入AI驱动的编译优化（如自动调优、成本模型预测）
  •   可扩展性：允许硬件厂商以插件形式接入新后端，避免重复造轮子
Ø 生态目标：推动协作与创新
  •   研发合力：打破厂商或团队间的技术壁垒，避免重复开发（例如每家芯片公司自研一套编译器）
  •   技术沉淀：通过开源或开放协作，吸引社区贡献，长期培育高性能编译技术
  •   降低行业门槛：中小厂商或学术机构可直接基于统一框架开发，无需从零构建工具链

## Page 18

FlagTree：整体架构
    FlagTree     .

Triton Language    Triton DSL Ext
    hints      op                                                     edsl

Triton IR        TTIR Ext                                                      Unified
    op                                                           attribute    Hardware
    FLIR                                                                       Manager
Structured        Unstructured    Mem Access  Calculation
TritonGPU        Linalg        TTGIR Ext
    Memref        Tensor        Linalg Ext    Math Ext

Hardware-specific Dialect    CodeGen Kernel Language    Plugin    MLIR Ext

LLVM        Hardware-specific Compiler

## Page 19

    FlagTree：生态矩阵
•     单版本多后端，具备跨平台编        common    ops                         ErrorHandler  FlagGems
      译与快速验证能力             Device    Register    ConfLoader      TestWrapper   manager
•     持续集成后端（15）并为各后   heur configs  tune configs backend ops    tl extension  backend
      端搭建 CI/CD 服务保障质量
•     适配更多 ML 框架，
          适配更多         nvidia        Triton Language                 FlagTree
      操作系统，适配云计算中心，       amd                                                   cpu
      壮大生态矩阵           i*****        Triton IR    (180+ ops, 10+ AI chips)      a*****
•     持续建设统一编程接口扩展     k*****                                                   n*****
•     统一中间层表示及转换扩展     m*****        Structured                  Unstructured
•     提升硬件感知和编译指导支持        TritonGPU        Linalg                              t*****
      能力与范围            m*****        backend plugin    Memref    Tensor         s*****
•     高差异度模块插件化能力      t*****
•     版本定期演进           h*****        LLVM IR        CodeGen Kernel Language     c*****

## Page 20

FlagTree：多后端统一方案
FlagTree.                                                FlagTree 编译路径前状
                                                         •     起步阶段，将各后端编译器代码合入，快速达成单仓库
Triton Language                                                多后端编译的能力
                                                         •     确定两条基本的编译路径
Triton IR                                                      •     TritonGPU：各后端有 nvidia/amd 的实现作为参考，
                                                                     但编译器代码在后端目录中自有几乎一整套
    FLIR                                                       •     Linalg：仅确定了基础方言和表示转换方向，实际
Structured        Unstructured                                       扩展与转换实现各后端自有一套，既不利于算子编
TritonGPU        Linalg                                              写模式的统一演进，也不利于性能优化手段的横向
    Memref        Tensor                                             推广
                                                         统一编译器解决方案
Hardware-specific Dialect    CodeGen Kernel Language     •     FlagTree Backend Specialization 后端统一特化（GPGPU、
                                                               DSA/NPU）
LLVM        Hardware-specific Compiler                   •     FLIR 多后端统一编译中间层（DSA/NPU）

## Page 21

FlagTree：后端统一特化

• 基本设计                                         •   mlir 的 td 文件特化
  •   FlagTree 为 C++ 代码的后端特化提供的实现                 •   td 文件整体特化
      方案：使用宏判断在工程编译时选择是否特化。                       •   EncodingAttr 使用特化
      宏定义在后端特化目录 spec 目录下的头文件，                 •   头文件特化
      统一通过 spec/include/flagtree_spec.h 最先被       •   情形一：函数声明修改返回类型或参数类型
      包含，保证同名文件以特化为优先。特化实现                        •   情形二：函数声明添加特化参数
                                               •   cpp 文件特化
      的目标保证最先生成，使得主干链接目标时能                        •   情形一：cpp 文件中添加一段特化逻辑
      正确选择特化实现生成的目标。                              •   情形二：cpp 文件中定义的 static 函数特化
                                                  •   情形三：整个 cpp 文件特化
                                                  •   特化目标链接

## Page 22

    FlagTree：基于硬件感知的编译优化技术

                          on comment                       核心思想
        Triton Language extension based
                                                           • 允许程序员通过注释嵌入硬件优化提示 flagtree_hints ，对程序员
        Triton IR          extension                       使用成本低、生态兼容性好
                           attribute                       • 实现性能提升
                           based on                        • 提升编译器可移植性、多平台统一的能力
        FLIR           Extension passed
                           attribute
    TritonGPU IR        Structured  Unstructured           整体设计
    backend plugin             Linalg            Unified
                           Memref       Tensor  Hardware   • 前端：扩展 Triton 抽象语法树解析，将 flagtree_hints 编码为
                                               Abstractio  MLIR 属性
                                                    n      • 中端：基于 flagtree_hints 属性设计优化过程，以增强优化效果
    LLVM IR                CodeGen Kernel Language         • 后端：使硬件供应商能够基于 flagtree_hints 选择性地注册 pass
GPU Backend Compilation                                    • 管理模块 Unified Hardware：实现硬件特异信息记录，包括架构
                   DSA Backend Compilation                 信息和下降需求等
   Hardware-Specific  Hardware-Specific
     Optimization      backend-specific
                         registration                      生态      性能      编程灵活性

## Page 23

    FlagTree：基于硬件感知的编译优化技术

                           on comment
        Triton Language  extension based               前端语言扩展
                                                        • 语法: #@hints: 后面紧跟着注释指导内容，需要为特定的字
        Triton IR           extension                       符串
                            attribute
                        Extension passed                •   Example:
        FLIR                based on
                            attribute
    TritonGPU IR      Structured Unstructured
    backend plugin          Linalg             Unified
                        Memref        Tensor  Hardware
                                             Abstractio • 注释分为两类：
                                                  n         ü 硬件单元映射有关：指导数据存储、并行分配等，如：共
    LLVM IR             CodeGen Kernel Language             享内存的分配
GPU Backend Compilation DSA Backend Compilation             ü 编译优化有关：帮助编译器选择合适的优化策略、优化参
   Hardware-Specific       Hardware-Specific                数等，如：pipeline阶段数
     Optimization    backend-specific
                       registration

## Page 24

    FlagTree：基于硬件感知的编译优化技术
                           on comment                     • hints识别：解析#@hints注释，建立语法节点与对应提示之间的
        Triton Language  extension based                 AST 解析扩展
        Triton IR           extension                     映射关系
                            attribute              • hints前端验证：
                            based on
        FLIR            Extension passed                  ü 初步进行合法性检查，如：验证hints与目标架构是否匹配
                            attribute                     ü 静默忽略无效提示，以确保编译成功
    TritonGPU IR      Structured Unstructured
    backend plugin          Linalg             Unified    TTIR Attribute 扩展
                        Memref        Tensor  Hardware
                                             Abstractio   • 扩展TTIR Dialect，将hints内容作为attribute带入TTIR，后续
                                                  n       pass将进行对应的优化或继续传递hints attribute
    LLVM IR             CodeGen Kernel Language

GPU Backend Compilation DSA Backend Compilation
   Hardware-Specific       Hardware-Specific
     Optimization    backend-specific
                       registration

## Page 25

    FlagTree：基于硬件感知的编译优化技术

                                 on comment        流程：
        Triton Language        extension based     中端: 实现一系列 hints 驱动的优化pass
        Triton IR                 extension        • 对照已有pass，注册hints有关的对应pass
                                  attribute        • 在每个pass进行优化前，备份原始mod
                              Extension passed     • 根据hints和unified haredware内容进行优化和下降，及时进行合法性检查，
        FLIR                      based on            若遇错误则返回备份的mod
                                  Unstructured
    TritonGPU IR      Structured  attribute
    backend plugin          Linalg             Unified
                        Memref        Tensor  Hardware
                                             Abstractio
                                                  n
    LLVM IR             CodeGen Kernel Language

GPU Backend Compilation DSA Backend Compilation
   Hardware-Specific       Hardware-Specific
     Optimization    backend-specific
                       registration                后端: 在backend组织相关pass+注册Unified Haredware

## Page 26

 FlagTree：基于硬件感知的编译优化技术
• 以生态友好为目的，编译指导采用注释的形式，指导信息分为两类
  •   硬件单元映射有关：指导数据存储、并行分配等，例如共享内存的分配
  •   编译优化有关：帮助编译器选择合适的优化策略、优化参数等，如 pipeline

     类别       功能     语法
              内存分配   tl.load # @hints: shared_memory/UB_buffer

     硬件映射指导   访存通路   tl.load # @hints: dma

              并行映射   for  # @hint: bind_sub_block

     指导 padding tl.load # @hint: dot_pad_only_k
   编译 pass 指导 指导 buffer tl.load # @hint: multibuffer

## Page 27

    FlagTree：辅导芯片后端接入
新后端接入 Triton 生态（算子库层）               common    ops                          ErrorHandler    FlagGems
1.     PyTorch 功能函数接口、Triton        Device    Register    ConfLoader        TestWrapper    manager
       Language 原语接口标准化接入       heur configs  tune configs backend ops    tl extension     backend
2.     ATen 算子注册后端键值                                                          FlagTree
3.     运行设备保护，张量设备指定            nvidia        Triton Language
4.     模块导入时自动检测后端                 amd        (180+ ops, 10+ AI chips)                      cpu
5.     定制自动调参空间、启发式调参、          i*****        Triton IR                                     a*****
       算子特化实现或选禁用               k*****                                                      n*****
                                m*****        Structured                  Unstructured
                                    TritonGPU        Linalg                                 t*****
                                m*****        backend plugin    Memref           Tensor
                                t*****                                                      s*****
                                h*****        LLVM IR           CodeGen Kernel Language     c*****

## Page 28

    FlagTree：辅导芯片后端接入
新后端接入 Triton 生态（编译器层）                                FlagTree 工程构建系统                .
1.   复用插件化的后端发现能力与运         构建入口
     行时机制
2.   实现后端 driver：设备相关方法     多后端构建    后端构建参      三方库下载    安装打包范
     及 Launcher              主控        数                   围
3.   定制后端 compiler stage    自动下载与    下载缓存管
                            离线构建管      理        二进制插件      LLVM                 SDK
4.   前端 python 代码统一管理特化       理
5.   接入后端底层库
6.   中间层统一                  构建差异化     i*****     k*****    m*****    m*****     h*****
7.   编译指导接入                  实现
8.   运行时优化应用                          s*****     a*****    n*****    t*****     c*****
9.   工程构建接入
10. PyTorch 后端扩展

## Page 29

 FlagTree：编译器演进路线的思考
    保持编程易用性，   •   基础层：语法和生态完全成熟，达到或超越现有编程语言（Triton）的易用性水平
     加速算子全覆盖 • 专家层：极其稳定和高效，成为硬件厂商和顶级性能优化专家的首选开发语言
     • 扩展层：指导信息库极大丰富，覆盖绝大多数硬件感知优化场景
     • 全栈协同优化：实现跨层联合优化，如高层 IR 的融合决策会考虑中层IR的循环变换能力和底
统一  多维度性能优化，       层 IR 的硬件指令，做出全局最优选择
编译器 计算性能超越     •   中层 IR：优化策略高度自动化，并能根据目标硬件特性自动选择优化 PASS
     • 底层 IR：代码生成质量达到手写优化代码的水平，甚至在某些场景下超越
     多后端支持， • 硬件抽象层足够完善，支持所有前沿模型架构所需的算子，并能充分表达其性能关键路径
     加速迁移效率 • 双路线融合：探索 TritonGPU 与 Linalg 编译路径的互通与融合，共享优化 PASS

                    生态


                   性能  编程灵活性

## Page 30

_(no text content on this page)_

## Page 31

众智 FlagOS：发展历程

        合作企业11家 合作企业20家 合作企业34家

        2023.10 2024.06 2025.03
        发布支持异构芯片的并行框 发布基于Triton的通用算子 发布统一AI编译器
        架FlagScale 库FlagGems FlagTree



    2022年底    2023.11            2024.12    2025.6
  启动统一编译研究    基于Triton的大模型算子库   发布首个统一通信库   发布首个大模型多芯片自
              FlagAttention发布    FlagCX     动发版平台 FlagRelease
    合作企业6家        合作企业29家        合作企业43家

## Page 32

   生态建设：AI 芯片统一开源软件栈合作型生态
    Triton中国生态Meetup 智源大会-Triton算子开发培训 万卡训练场前沿技术闭门研讨会
智源牵头举办，获得上海人工智能实验室、CSDN、 智源大会增设Triton生态活动专场，现场开展Triton 智源联合浪潮等举办闭门研讨会。就大模型算力基础
中国互联网协会人工智能工作委员会的共同支持。首 通用算子开发培训，与开发者面对面交流，现场气 设施技术趋势和发展，大模型训推框架多元算力适配
次活动线下满员，线上参与5000+人次 氛热烈，互动火爆 发展，AI算力的软硬件生态体系构建等领域展开探讨






 通用算子适配及软硬件协同研讨会 高校AI课程 CSDN-Triton中文社区
智源依托中国人工智能产业发展联盟（AIIA）、中国 智源积极参与北京市属高校人工智能通识课 “前沿 与CSDN深度合作，在CSDN平台建设Triton中文社区门
信通院组织召开面向大模型的通用算子适配及软硬件 拓展”模块课程案例征集，打造《AI模型的算子开 户，同时运营Triton中国社区微信群，开发者交流活跃，
协同闭门研讨会 发入门》课程。 群成员已超过1000+

## Page 33

 生态建设：产业生态与开源社区 双驱动

 产业生态：与众多企业和机构的积极合作 开发者生态：收到越来越多开发者关注和参与
• 上下游生态关联企业：10 多家芯片企业，5 家服务器厂商，     • 通过多次举办技术沙龙、研讨会，进行技术布道，发
 4 家系统软件公司 展社区开发者
• 科研：北京开源芯片研究院、先进编译实验室、北京大学、        • 社区爱好者：17140
 清华大学、中科院计算所、中科院软件所、北京中关村学          • 开发贡献者：164
 院 高校积极参与教学培训
• 智算云：京能数产、中国电信、中国移动、中国联通           • 北京市教委把国产芯片生态软件内容纳入北京市高校人
• 标准规范：中国电子技术标准化研究院、信通院 工智能通识教育、首都高校AI创新社区
                                    • 中科院计算所、中国科学院大学等开展试点授课







 积极对外发声，通过开源开放，形成产业影响力

## Page 34

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: ``
