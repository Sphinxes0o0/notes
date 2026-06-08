---
type: source
source-type: pdf
title: "黄石柱-Deepseek推理性能优化"
path: slides/黄石柱-Deepseek推理性能优化.pdf
size: 9703 KB
category: slide
ingested: 2026-06-08
tool: liteparse
liteparse-version: 2.0.5
source-md5: d5aef80aab41d49142244c853dda585e
ocr-applied: true
---

# 黄石柱-Deepseek推理性能优化

> Ingested from `/private/tmp/lfs_pdfs/slides/黄石柱-Deepseek推理性能优化.pdf` via `lit parse` on 2026-06-08.
> Source file: 9.48 MB.

## Page 1

        CPP-Summit 2025

SEK 系统办 技术 大 会
       C++ 及 y | 人 人 用 ya
C++ and System Software Summit


    方/Organizers:    CSDN
        主办
合作伙伴/ Partners: # incrzDIBUILD PARASOFT. UX iA 2 sh Witt Broadview

## Page 2

                                        CPP-Summit 2025
 Intelligence Research Institute        SEK C++ 及 系统软件技术 大 会
 ngularity 曾 能研究     CSDN

     木    大                            预
     2026                           as活动
                                     会
                                    al  AFA






 Machine Learning Summit            C++ and System Software Summit



 GOSIM                              4
                                    Al 构建世界
                                    _     —
                                        =

 :
</>

## Page 3

媒体    服务          一     形态     媒体  矩阵
l  Ak         —     多     3

       ime.       起     en
                        ore        F |          a             <<
              (Fe)      22                      《万有

                                                              tro               ge
   采访             报道                                          2.           ~
              *        +                              La
                                                              =-                 tie
                  a                         ere       ——      =      is a  2      Se
                  (AGI 技术 50 A)                           GEE)             《开源 英雄 》
              出版
   权威

   (inte? A)        |     A                         《中 国 开 发者调查 报告 》    mo          on
   MR             先 |     Rien                          ee       ae             >.
   先锋       从   前 沿     技术 到 行业                     者 调查报告       已成             7023
       ,                                                        ,目前
            您     来                     2   AA
      ,为 带 全 方位 的深刻      到                           为 完整 准确 了 解 中国             7
                 解读
   见 和 专业             ，        可   中  | s   joa     开发 者 市 场  的重要 参
                                                              a



                                                                                eee eee)

## Page 4

企业    CSDN
| 技术 咨询 一 ou 信赖 的 策略 伙伴


                                         涵盖人工智能、架
   依托 雄厚 的 专家 团队 和 丰富 的行业 经 验     通过 12 大 技术 咨询 板块,提供                  构设计、产 品管理
                             ,                                               等全栈
   技术 咨询解决方案 帮助
,                       企业在数字化      化,万 物 互联 的变革 中 打造 关键创新 能 力, 加速 技术和 产品 迭代 升级。
   技术 领域
   核心
   咨询

|  Wy  a                                 wo      a4      SS,     rN
   “a     =                          ——     |
                                     Al  软件技术栈        软件
       02                                   系统        03 企业 开源     设计 与 治理


   4 Gd                              a
}  软件                                能  一 S|        . aa 战略  落地
                                        与
04   架构 设计 与 重 构  05                 系统 软件 性 工程 优化 06 智能 化   转型 与



                                     mes aa

## Page 5

球C++ 及 系统软件 技术 大 会
全




腾讯 云 智能 资深 专家 与研友 架构师


          从 Al 应  用 到 底层 Al Infra都有 着 丰富 的 实战 经 验 ，  化 与 建设 腾讯多个 大 中 型 项
          目   。主  导TencentOS、 语 音 助 手 、 对话机 器 人 技术 研发     ，支持腾讯多个 产品 线 落
ai  te                营销                                   平 系统
          地Al 技术   ; 深度优化     与加 固 企 点 客服、企 点     云、TI   台  架构;
                0到1， 化 与 建设 腾讯 云 智能 体平台 并 深度 赋 能 行业 伙伴             ，2024
 gel      从                                                       年曾在上海电
  be      机 工程 学 会学术 年 会上进行 Al 技术 的 专场 分     享;     深度 支持腾讯 云大模型多 个 技术 方
          案 的       与优化，2025     通过                         业务 成
              设计      年     Deepseek 推 理性 能 优化 帮助            大 幅 降 低 本 。

          演讲 主题      :
                      推理:     性 能 优化 的 核心 方法 与 实践
          高 性 价 比DeepSeek

## Page 6

fh  By
vt  |
1  :å
|  a
(a   i   Nit
een|  at Lue  it
|  ä¸  |  }  i i
|  it  AAT  i
|  i
[å¯  i   TATRRL  AHN

å¸  AN
j  |  ad  UPN
 jal  |   Wi
|ata  Mi  |
â  iH}
|  all
oe  ai
|  |  TUL:
|  |  ahs  =
Ny  |
Wi
æ  adh
ae
Wi
7  ay  itl   |  Te  iy
yaa  eee
ES  rT  ata  il  a  iy
:  itt  ii
1  i
â  |  |  at i
ae  |
ââe  |  TA
å¯  |  HH i
A  |  |  1
â
1
=  niin
äº

=|

## Page 7

        1.    Bink
        C.    1 FUR
EGR     3.        AE
        4.

        5.

## Page 8

o  Me

## Page 9

Bl                 架构
      Deepseek R1 型核心



                                        参          6716B，   激
    651 层 Transformer， 前 3 层 密层+   后                     活37B
                                    58  层 oFE   层       总

    D_model=7168,                       ik           A

        d_head=128,                 (d_c=512)         11.4B

  3层) ”中间 层 维度18432 (2.57xD_model)  ，     稀 激活       264.4
  【前

        激活                              数K=9，         层    38
        专家 专 家 中间 层 维度                  单
        ，                                             =11


  专家               Wg_u:7168*4096, Wd: 2048*7168    单个专家: 44M

  671 = 0.93*2 +   114 + 2.64 + 11.3*58

                                  MoE

## Page 10

BB)                                推理
       Deepseek R7 模 型 核心           流程
                                                                    层[并行计算)               KV
                                    >     Rid     ”Transformer                          ~   缓存生成   ”
 Prefill BiFe       [ 处 理 完BE输入序列)        |        _                ; Self-Attention >  Add > Norm > MoE-FFN > Add
          核心 任务     :一 次性 计算输入  序列 203260 token) 的 隐藏 状态 ，初
 ©                                  始
      化 KV缓 存
                    ;批量 长 序列    计 算        ,     7B                 | 首ftoken    | «—
 。    关键 特征  处理         ，           密集

                              的KV     向量)     + 最 后 一 个token
 。                  【 存 所 有  token                         的                            |
       藏     状态
                                                                |    {rom 1         |
                                                                                       |
                                                                et |
                            生成)                                 |                   |
 Decode 阶段 ( 逐 token
 。                                 BFKVA
      token                                                                            |
 。    关键     :      单   串行计算，          感
              特征      token 通 信 敏                                   |
      KilFE)   ，      KV 缓 存 复月                                 |    LUm Head          |
                                                                    二
                                                                                           一一一
 。    输出，     新 ioken + 更新 后 的 KV缓 存                            一
                                                                    |
                                                                              条件?
                                                                    |          停止

## Page 11

  BD)
   Prefil



                 注意                                   总                                     ”激活 25.6B
               非           力     部 分   太LDOPs#nttn= 2 参数 数)b5     [公式一)    166912           参数
      Prefill              力
注意 部 分                                                het                                   11.4B
 [MHA]                                                _      [公式 一)        26569        13.7% 3XB5'=3260/2

                                                                           193481       100%

               非注意      力 部 分                                              51.2         44%     token
   Decode                 注意 力 部 分                ~ Mayer *2.8 *1N-4hc!                     5=1 token
                                              as        *10-*bs's          65.1         56%

       小 计      每       token                                              116.3        100%

           FLOPS        pis  =    站                 5 (Ast=)               FLOPS     mia
                                      力头
                                                  数)
   *   b=batch size =1            pees a         [注意
   .       二                          layer=
                             7        7 512
                                      ( 解   的    维度)
                             -                  ROPE
                                                                    长度) ,比如
                             。        缓 存 长度 [上下文                 取3260+550

## Page 12

  分析一
BD)    显存
      资源

      的占用变小，但 高batch
  模型 权重 占 比 较 大、采 用  之 后 ，KV Cache  长 入情况 下、显 存 也 容易 成 为瓶颈


                DB                              节                                            模型
                                     6718 字                        -671                          权重 按照   加   8 精度 测算

                模型权重                            BF                                           权重      所、
  (attention    fp8/MoE w4a8)      14+657/2                        342.5                         w4a8，       以657e

                                                                                                 下的数据 ，32650 长 度
      KV Cache    (MLA)                                            0.213                     Tbatch

                                            公开                                               1batch 下        单层            数
      mista                                 参考                                                                        平均 的激活
                                            AN       二一    ~       0.000%                    据 ， 8精度                       段
                                                                                                                     ，decode

                                                                                             1batch 下 平均 单层的 激活 数
                (MHA)                       4x                     ~ 1.13                    ，
                                                                                             据 儿8精度 ，prefill
                                 通信 缓冲 、系 统 预 、内 存 池 管                                          大
                其 他              、     区    运行
                                 理 框 架 与        时 开销留                10                      每

  公 丈 五    :        MeMsct= MEM                 MEM                      =1 ( batch size]                    *d.=512    Lig在 维度)
                                                                     “5=3260 [A KEE]                             =      128  [注意
      六 【公式                                                                                                  “Mheads
  公式            五的展开                 del        吕 + bnheads5dc+                              维度      力    。  =     9         最
  公式   六            laact                       +     Dnnead             7168 [隐藏                                                力头数]
                                                                         ，，=                     注意          .K [ 单 卡         大 激活 专家
                五的展开)   :                                            KH)                                     数)
  Axtt 【公式
                    Q、K、V、5core@v、0                                  dm     = 18432                          “权重 精度=    加    8

## Page 13

    分
    资源 析 一 显存 带宽

        Fit SHEN SULA


    _    显存 读 写 大小 RFit Sith    :



  *  23B æ´»  çå¤¯ oF:
  æ¿æ´»å¼  ä»¥  â
  æé+KV Cache+
1 batch Prefill  14/8+23/2+ 0.213 + 1.13*61*2  =
   [tp8+ep8j  ä¸­  152.3  0.038  ~ 0.08  0.47  æ¯3260  é¿åº¦ç  KV
  23/2  ã0.2136
  +  å¶
  ã  113 æ¥  èª  ä¸  ä¸ é¡µ ç ä¼°ç®  å¤§å°

  Cache+
  Tbatch  æé+KV  æ¿æ´»å¼
  Decode  âÂ«-14+23/2+0.213+0.0004*61*2  25.76  0.0064 ~  å¨  16.7  æ¯3260é¿åº¦çKV
  ã  0.2136
   (tp1+ep8)  ä¸­  ç¬¬  å  Cache
  23/2
  ã  å¶  å¤§å°
  0.0004
  ã  æ¥èªä¸ä¸é¡µçä¼°ç®
   32 batch  æé  +KV  æ¿æ´»  0.012  32 batch;
  Cache+  ~  *
  Decode  =  33.88  0.0085 0.000383*32,  iz  0.71  0.2136
  *  æ¯3260é¿ åº¦ç KV
   (tp1+ep8)  å¶ ä¸­ 23/2  ä¸º oF æ ä¸ åè¡¡ ç æåµ  Er  Cache
  *ã  å¤§å°

  -b=1  (  batch size]  âChm   = 18432  IS  ä¸:
  åº¦  é¿  æ¨å¯¼ 26.6/8  +  166.9/8
  )  *k=9 [ å å¡  æ   å¤§ æ¿æ´» ä¸å®¶ æ°)
  .5=  3260 [åºå
  âws  1batch  å¥æ¡  ä¸ï¼
  å¹³å  åº¦  )  å  å¸¦å®½  3260 ä»¶  Tbatch
  â5! ï¼ =  ç¼ å­ é¿  /ä¸ä¸æ é¿ åº¦  å32650+550  w4a8  mmoe å
  (BARE  ,  attention é¨ å çè®¡ç® é/8ï¼  é¨åçè®¡ç®é/8ï¼  ä½
  è
  .  å­  4TB/s  ç¬¬   å­é¡µ
  .d 7168  AEE)  *TPS>=20 Tokens/s  åä½ Ttopsï¼ å

## Page 14

 分析一
BD) 资源了 取  1 通信
     一


 a—\ 一 us mASta,
     一      a   .



                                               量 (GB)                                       AAT 5                           备注
                                      据        通信      5
             阶段                    估算 依                                                     it
       Prefill.                (EP)        Axtn        ~ 0.045                  ~       0.16 ¢5- 在 第 十 七 页   0.28  Attention TP=1
                                                                                                                      MoE EP=8

       Prefill     40.39G      (EP)                                                                                Attention TP=8
              ，     4.876      (TP)        axy        45.2    _ 0.05            _                            0.617       eee

                                                                                                                   Attention TP=1

     Decode         0.012 (EP)                 ~0.012      ~  0.000013                                       0.034

                                                                                                                        5=1     (decode 1 token)

 计算 条 件    :

 ASI: Trafficrota        =    Trafficep+ Trafficyp                        *b=1       [    batch size]            *TPS>=20 Tokens/s
                                                                                                      长度)               机 内 不间通信: IOOBG/s
                         |                                                *5 =  3260 [序列                             *
                                                                                        = 7168    【隐藏层维度 注意 力 头 数)   *  帮oOE 量 化， w4a8
 aN        ，             Hi                                               “dm   =       7168*3                          (BF16)
                    ~          *                                          *k=9 [ 单 卡 最      大    激活 专家 数)        “auemoe=58
                                                                          “权重             8  度
 Axtt:              =                       modet*Esize*[TP-1)/TP+
           (reduce-scatter+all agther,      ArLX*2)   前 三层 FFm

## Page 15

    加速的核心
    推理 问题

        ，    由
1.  资 源 不均衡  导 致 FU

    1 如 TTFT
例子      果    要小于25，Pre 单 大约 可以 让 4.5 个 请 求同时 进来 ，KV Cache 的显存 占用 大 约 0.9806显 存 ，


    2:       TFSAA73IG/K,
例子
3.7Tflops,





2. RAE

             (fp8) ，  此 时 如 果 不
进行 资源 优化 ，很  难 做 到 高QP TTFT 兼 顾。

## Page 16

    加 速 的 核心 优化 思路



                            Ft        FA      在 精度 几乎 无     前提 下 ，减
                           fe
                       。   最大化    利 计算 、显 存 、带 宽 资源     GFF. eK
                       。   算 子 级  利用 率 提升
                                    量化 压缩
                        PDS         fate
             BB                                             命中
          3           Dp 并 行    KV 缓存 Prefix
    消除 “无 效开销 ”       EPF#7T
                                     负载 均衡
                             专家
                        MTP
Kernel Launch 开销 优化    算 子融合
                 优化
    CPU-GPU overlap

## Page 17

ER

## Page 18

                              浪费
            避免
                                       -cpU+GpU     Overlap

 1 项 目 早 期 发 现                       的 问题:                         有
                                                          CPU 大 量 的 空 六
   ~  CUDA HW (0000:ca:00.0   el             a          = |    i        1.   =      ™..
                                  |  ES i       /           加      sh   .    @      @..
      »  0.0% Stream 150                |                 | |                  |  |
 “ere
2                                               BH) kernel launch  bound 问       题  、CPU 端 代码 执行和 计算
vu              Gn                ，     捕获              过程
                                     十 捕获KerneLl Launch
                                                        过 并运行
                                                                  运行时        解决解     决L[aunch 销 太 大 问题
CUDA                       AR     通过                    程，     在   时                    开      。
         CUDHR                方案                   没有     ，        个                                  ，    Batching+，    _、  IL、
开启           Craph 后 Kernel间 空             几 平      ，   但 生成 过        中 每 5tep 还 存在    大 的 空 光    ”ontn045

             ‘won                                                                       负载状态    ，     不 受 CPU 任 务     影响
         otetan                                 TS          SS                  CNT



 分 析 每   个5tep 中间 CPU 的 任务             ，采 用     跟GPU    方案:                 5tep    起              的
                                                CPU Overlap        每     个       结 束 后 先 发 下 一 个5tep
 推理 ， 再 进行 相关 同步 操作 和CPU 处                      理 。 [之 前CPU 处 理 完 在 发   起下  一 个    step)

 -       =                                                         EEE
                              a |               =

## Page 19

 4  A



       些                       ，      规避
 一         例子                         以     快速  浪费
           明 显                    可                   :

                                                                                                             8
                                                                                                           五 由
           选择                          个              所                                3.            Metadatam
       融合                              一                  有
 1. 专 家 4                      :                  kernel 完成    token 的 专家 A选择
                                                                                           Layer                                             只     一
                                                                                           每 个     调 用 获取 不    etadata，     变 为                       次
                                  实现                                                   @                                                             获取
 @  原生PuTorch                          ;
           层                                           归一       化 )      选    择            mF      EE
 线性                                                                                        C     3%
               计算                     、5oftmax            [路 由 权重        、Top-K        ©        ~
  (topk)     .     #S5l#E (gather/scatter/argsort) ....
 e     融合 后                       kernel                                               Before Optimization
 。     HOR:

                                                                                       After Optimization

 2

                                                                     f
 @     显存              ne:        50%                  Quantize      =
                                      Wx               —     Q(W      -  X)                :每     token      分                     ’     MARS全
                       Tiga                                                                                                       编号 K=z2)
 Pre-      t:                                                                          比如 专家 素 引      个    被 配 到 的 Top-K 专 家      [如      ，   形 状 通 常 为
                                                                                       [batch_size,      /的     张量
 进行                  缩放                   寄存                                               5eq_Len
     必要 的 转换 或                     操作 [LWLz/            Row                            路
 器->Tensor core)     。 优 化 前      通常是独立的               BF16              Expand Row        由权重: 对 应     每 个 被 选专家 的 门 控 权重 ，形 状为          seq_len, 的   点张量。
 Kernel                                                =>                Pre-Quant         映射、    通 信 模 式 配置 等   等。
                                                                                       其 他 设备 拓扑

           扩展)           :       指 的 是 在 低 比            FPS                     FPS
 Expand Row (行
量化                             过程中，
 特                     【如 W4AB) 推理     对 答 入
           X    行      准备                         W4A8 GEMM               W4A8 GEMM
 激活 值 进     的     数据     和 对     操作

## Page 20

_(no text content on this page)_

## Page 21

                    利用
                        率    -PD
大                                 分离
                                                                      如
                                                                      下   :
                                   ，  离  面临                  应 对方案
 PD 分 离 可以 缓解 FU 偏                的 问题 但 PD 分 本 身 也 会  不     1 针对 Prefill:
 少 挑战    :                                                        由     存在
                                                                      算力瓶颈，      主             采用
             节点                                              。        于        要            大TP + 小EP 并 行 策略 ，提 升计 算速率
 1                  :                                                 均衡
             算      力瓶颈             ，     致                           分 离 负 载
                                    TTFT     不                        尽可能高
 由 于 存在                 ，以      及 跨 机 通信开销 导   降     下 来                         效传输
                                                             。    KV cache 【计算 通信 重

                    节点:                                      2 针对 Decode:
 2 Decode
                        频       存取，
                    Cache          存 在 明显 的 访 存 站                     于      频
                                                                      繁
 ”       由 于 KV                                                   由             存了        ，      DP     +
                    节点                                       。        KV Cache 存在 明显 的 访 存     颈     主 要 采用 大
 显存                     墙       比较
                                  明显，
         Decode                     算 力 用 不 满                         大
 ”                                                                EP，     尽 可 能 增 batch size,      REN
                                                             。    尽 可 能 充分 利用 显卡 算    力 ，趋 近    compute bound

      架构 示 图  :                                                   pp     ae,
         支持mPnD，        扩展         点                                  了
      1                 自 由       P 节   和      |     (a               _
      2.Prefill:    DP+TP+EP                                       |       7
      3.Decode:     DP+EP                                             <      >
      4.nixl 通 信                    i                                 i’

## Page 22

-Prefill
提升利用 率 -PD 分 离 并 行 策略


    主要 采用 大 TP +        RS     Sit

    算 力        ef                                                                      t

attention TP1  +           MoE EP8    47    0.16    overhead 40.39    0.045   Tbatch,
attention TP8+MoEEP8     9        0.081        overhead 45.2          0.05    Tbatch,  3260%A

    mes                                             可    知:           比      通信
                                                    大 致 测算 相 TP1，TP8      的            耗 时 增加
          1batch 3260MARE        1 batch
attention        位               部分的计算量/8，  位           但 是 推理
                                                                          节约了
             部 分 的计算 量, 单    是    moe 单 是           了 0.0065，             0.085
THLops，     参 考 第 六 页        参 考 第 六 页


推导 三:  51.2  +      65.1

    Tbatch RAF, TP1,    Tbatchn R#F,
decode 段 attention 部 分的计算 量，  decode 阶段moe 部 分 的计算 ，考 虑 最 不
    Cflops，        的     ，     位     量
    单位     参 考 第 六 页               均衡
                                   情况         单
                                        Gflops，  参 考 第 六 页

## Page 23

        率     -负载均衡
    提升利用 -PD 分    离
        ，    般     是      ，      差异             ，  实践  考虑
PD 分 离 后 一 P和D 的 QP 丰 性 能 存在 差异 的 且 性 能 受到 用 户 入 长 度 的 影响 因 此 中 需要 充分 负 衡以 及
      。
分
   策略

    针对 Prefil:
        ，                                     ia
    Chunk 调 度 时 的 请 求 长 度排序 策略 同 一 批 到 达 的
    求，  排序        体                      达        ，
    请 按 长 度     优先 调度 短prompt，      整 TTFT
    到 = 优                                     +
    最     。


    |   GB    requests                                   Decode Node
        EL                                                   |
        CLLR                                  Coordinator

                         一                               Decode Node
        -一
        Chunk 。

                                                  BAB

## Page 24

        肯     利用             -通信                    传
         提升     率 -PD 分 离                       优化 -异步

                                                 及 Metadata 传 给Decode
    Pre   /节点 需要 将计算 得 到 的 KV Cache 以               节点，如 果 采 用 计算->  -> 计算 模式 ，将 导致CPU 利用 率 旗 ，这
                                                    低                                          里
    很 容易 想到 异步传  进行 优化 ，主 要 采用以 下                计 实现 :
    。    ”异步  传 KVCache， 与 当前iteration forward step overlap，  不 影响 吞吐
内完成 ，TPOT
    *    RDMA wR,            step               周期     有保障
             &             GPU Overlap，    适
         调度 层面 ，CPU                             配        PD+
    。                                            投机       采样
                上述方法后，可以 看 到 在 束 iimeline
    采用                                           上，计 算 与 传    能 够 完美overlap，CPU 利 用 率 持 续 保 持高位。

             ~           CUDA HW

                         ,          nee    é        |        at
             ccf ent
                                     ==
                         >  0.2% Memory          i        |    |        4       里        |






         ~ 33421         to                     100%                        Er
                                                    Lf    4  |    i     oon  J
                         —                          =        cm          日 Cee

## Page 25

       利用     -通信
   提升              率 -PD 分 离    优化-Layermwise

如 果 等 到 所 有Layer 算 完 再 进行 发     ，发送的    数据 量 可 能 较     ，占 用 较 多 5 算 ，影响下 轮 次forward step
                           送                       大        力        一    计算 能，    因 此 根据 实际 情况设计
layerwisef$#.
   层 前 向计算
。      与层       KV Cache fe overlap,                   HAR KV Cache fe
   长 15L>8K 时     Layerwise     短文 ISL<8k          WMS, BEABNA,
。  文:      选择        :
       后，主 动 将 数据 推送 到Decode 节点 ，无 额外 协调 开销 ，可         与Layerwise     传     配合 (tH
   分 离 采 用     模式 ，PreL 节点 生成KV Cache
   理 完 一 层 推 一 层) ,

 传     计与实现后，可以 看 到 传     的Lantency 几 平 与                               保持
采用Layerwi5e                                                         在较低水准。



                                                   Layer1 Layer2  as
            —   [Layer                             1|Layer  3
                ,
   —2,  Es  i   PES                                              Bos  和 i |
                                                                  ee




 ISL: Input Sequecne Length

## Page 26

    -PD
提升利用 率 分 离

    传     源和目的 节
NIXLB KVCache 作为 点:GPU[Paged)-->RDMA    GPU[Paged)
的零拷 ， 相 上比 有3 ~ 4% 的 性 能 收益。
真正




定位    通用 并 行 计算 通信 标准          NVIDIA GPU 专用 集合 通信 库   专用 月 /推理异 构 传输 引擎      站 VDIJ 推理 专用 点 对 点 通信 库

                               、 生态性能    集合 通信         为pD设计、     、     能
                                                            、 缓存                、
优点                                                     专 异 构 支 持     功            HER
      mG,_    ROMA.、   RE、     快 易 集成                  完善 与     集成      广     好 支 持  路 由


       非专用设计、    扩 展 、配 置复 ”设计 不 匹配[集合 vspz2P)、 有 额外   能    框架集成、 拷           锁定    可
缺点     、                                                 依赖 可 能非 零   “生态 实 现细节
 全     杂 功 能 单一      差         BRE      贝              、 生 态 较 新     能 不      、   新兴
                                                                              佳    较


性 能 关键           iA             必 有 额外 拷贝 [非 零拷 见 )       可 实现 零 拷贝[依赖实现)     设计 支持 零持

          快速 原型 、 已有   系 、跨平       多GPU环境、      集 合    需  级异构系统、      、       mVIDI      、
适用 场景         统                                     通信          需 灵活 拓扑           全    推 理 平台 需 智能 路
                                   期方案                    需 集 成缓存             由、看 重统一
          BEX                   求 、  初                                                 抽和

## Page 27

       升利用 率 -PD 分 离-Decode 并行 策略
主要 采用 DP + 大 EP 并 行 策 ，旗 低 显存和 访 存 压 ，并 提升
    力  算力惠用率。理 想 情 况                      下 ，EP32 时 显存 和 显存 读 写 比EP8 少。

       写                                  |    |
    资源 (MoE W4AB)    显存 占用计算依据    显存 读 [C)


                                         +KV  激            活+系统预
   Attention DP8/TP1+MoE Ep8                             [Cache+    25.76        am      116
                                         55+0.213+0.0004+10                            Fa        pha

                                         +KV             激活+系统预久
                                     权重                   Cache+    =              =0.383        32 batch
   Attention，    DP6/TPT+MoE EPS         273*32+0,0004*32+10        38am      10.012*32      ane

                                         +KV             激活+系统预久
                                     权重                   Cache+    。        32 batch
Attention，       DP8/TPI+MoE EP32                 374                              =0.383        116*32  decode
                                              全        rg        1

    Ast+—:     BASS (FEMOERIE     MOERIE      不均衡情况)        显存                                       数
        =      +                         【最       +     3260-KEMIMLA KV Cache+ 单 层 激活 占用 *61*2]J*batch


 推导 (14+10.28+0.213+0.0004*61*2)*32      785.34  带入]         ~14 GB
                                       =       【EP32     ”
    10.28=329/32， 粗 估 方 式，先忽略 共享 专家                      ”通信 精度 :BF16

## Page 28

    肯     利用            -DP
     提升            率 -PD 分 离 并 行

DP 并 行 适 配 与 优化                                             人      =
         于          ，     于     节
                        点，
DP 并 行 借鉴     训练 框架    主 要 应 用 Decode       在 满足            onal
                           提升50%以上。
                要 求 ，单 机 throughput                                f=}
         下                                                             <r
1    运行 模式 解                                            |     |= |     和
                                                           =:
                                                                                             ER
因为 在 oF 阶段需要 做 同步      ， 以及CUDR GraphXtinput                                                 Po
         的要求，                               才能确保            -
tensor 5hape        一  般 都 需要 六                                    Elm
                                                            -
Attention                                               cru      一     hidden states 1 |     Jon_stateste
      个DP RanKk 在 每    次 forward   至 少 包 含一 条请 求            ="
。    每              一      step                         ors

                模式下 ，forward 5tep
                                        后需all reduce
*    CUDH Craph                                   对齐                                         一
                                                                       一 二
                        数量
     SDP Rank 待处理   的  reqguest
     mock request                                       os         -}-  ~ |                      i
*                  当Decode请求处理，DP 主 要 应 用  于Decode

## Page 29

肯    利用                          -DP
    提升     率 -PD 分     离               并 行

                                   同      ，PD
由 于 Prefill 和Decode 采 用 不              的 并 行 策略 分 离 需 要 做 相应 适
         两个点:                          CachefFhi.
配 ，主 要考虑                                                                   = ~
1 负载 均衡     (感知丰富 与 精细化 趋势)                                              Js
     round-robin                                                          Pl
。                   调度                 ort
     基于 各ranKk        上 request                                          =
。                            数量                               aK  2       =
。
       KV     Cache             5ize
。    基于                         感知等等                          =<         =
                                                                  aN      =m
                                                              |)  >< >   Wea
                                       为例，  配 置 如下            mK
2 KV Cache Transfer，      TPTD                                           |
。    Prefill: TP=8                                            — Hf
     Decode:  DP=16,     TP=1,     EP=16                                 WE  一
KV cache 传    设计 如 右 图 所 示         :

                                                                         IE
                                                                          —

## Page 30

Bl          -PD                -EP             通信                       =           加            Ea
         提升利用 率                分 离             行     优化        bs, dm     (abs, ir    (abs, i      bs, i
 EPp    并 行情 况 下 因为    Deep5eek 模 型  丰oF 的 稀疏 性 和 激活 分 布 不 均   的 特
        ，会 导致资源利用 率        ，    可以  通过 通信 优化 以  及    负载 均衡优化来  缓                    _—
                                                                                oe
                           低

                                                                    nt!         |   CS  |        a
                                                                    +

  DeepEP 优化 多 机            信                                                                      ==
  FE                                           BLA                      258 pen Top,    AIK, a      a-
  型     ，下 面 是优化 前 后   的   对 比分 析。
         :各        通信
  优化 前      阶段     量 如 右 图 所 示[       图 一  。                        “

         分
         析                     通信     耗        40%+      二)
  采样                                           全
            timeline，  发 现      算 子 时 占比 高 达             [图                                         加
  优化     后:   oF 处 理 前 后 的 数据 维度 变     小   各 ，   段通信 量 情况 参考   图三。
         分
          析                    耗           50%。     四
  采样                                                )               =                      一
            timeline，  通 信 算 子            时 减少     [图




                                                                    256 Experts, Top-8, 32GPUs (EP=32) 输入1k， 输
                                                                                               ，           出1k  四
                                                                                                                图

## Page 31

     提升利用 率 -Ep 并行 负载 均衡
 专家 负载不均衡的情     :                    ‘
                     256      ，      token     其
 DeepSeek V3/R1 包 含     个 路 由 专家 每 一 个     激 活    中 8 个
 SR,           AARANMME,           CRMGKMERRA,        OU  Cee
     分                               如
 采样   析 各 Layer 各 expert    激活 次 数统计 分 布 下 :
 从 右 图 可以 看 到:                       at      iy,
[ayer      热点     ，                  数     热点
 部 分     存 在明显     专家            点 专家 激活 的 次 可 能 是非
     的5倍以
        上
        ，     Ep     存在          ranKk      时     长，
 专家 导 致 并 行     某     个            上 计算 耗       较  其 他
 rank 需 等 待的局 面   。

                                     Load Balancer
 方案 :
    通过        动态                 + 余        [E      ee]     ew)  ee]
 1      EPLB 算 法   ，以 及 负载 均衡 宛      专 家 可以 将 各 rank 上    (|
        均衡     显      ，            度        著
 专家 激活 不     度     著 降 激 活 不 均衡      可 降 至12  ~ 1.5， 显
     计算   和
             通信效率，                   ~
 提升 实 现 oF 线 性 扩展能 力                 。
        Layer     热点        ，        均衡        mn
 2 不 同     的     专家 分 布 不   同    各 Layer 的 负载   可独立 调
 度 管理。

## Page 32

            利用
BB)          率   -     TP优化
      Multi-Token Prediction   是     一    种 通过 对 每一个  位   置 预测 多 个    token 来 ms       PE- =  =
      改进      性      ，               夯                    加速。   TP                         ==
         大 模型 训练 能 的 技术     同 时         TP   可以 用 于推理         由                        [二     =>
            ，Deep5eek              文         做      改进                                 —     ees
      首次 提出     在 ETR论                基础 上 了 进一步            。

                                                                                       —
                                                              META MTP

             只开源   了 一 层    存TP 权    重    ， 参 照EaglLe
                                              模式，         多 层 存 TP 是 反复 调用 相同权重， 最 终 接收
 由 于Deep5eep                                                                     率:
 @    由      接 党 率 为1.7 左                 ，与 数据
                                     右             集相关
             己接受率为2.1左右，                    在 并 发 较 低 时 ， 可 进一步  提升 吞吐
 @       TPnext_n=
 Tips:   为了尽量 减少 存 TP     来 额外      框架    开销 ，将 TP和 主 模 型    实现 在 一 个 图     ， 只生成
                                                              中      一个          Graph.

        率优化:
 接收
 为 了 进一步 提升 Decode 的 接受            ，参 考论文和 开源思想从toKken by      放宽了 draft token   的验证
                               率                                                    条件。
 ©    (RARER:
 ¥           保留 概率 最 高的由 个token
 w”      值过滤: p > p_max    - 6 (6=0.1)

 @           draft_token € candidates;                    token 出 现在 候选    集中 即 可
      MRR: 接受
 ©           率提升10%，                  度 几 乎  无损

## Page 33

_(no text content on this page)_

## Page 34

BD)

量化 优化 略    ;
    度分析:        在 实验 阶段 ，我们 发 现Deep5eeK
                                              模型中，前
  1 敏感                                           三层    scale before quantize
      较为敏感     ，   然 后 凡 -Head本 身 通用 的 形式 就是不 量        -一一
  DenseLauyer
  化 ，并 且 这 些 层 再 束 D5 模 型中占 比非常小 ，所以 这 几 层 不 采取        |
   量化 。        1     average mag.


  策略 使得权重 里 敏感  channeL     进 行 平 ，如 右 图所示，     并且
      的                                        每一层
              的量化方式 ，group-5ize=1T28， 这 样 相比 于per-
  采用per-group
  channeL 能 保持 更 好 的 业  并且         速度 不会明显 的 下
                       ，                     。    W4A8 vs FP8 End2End Throughput Chart

      量化;通过      校准集     校
  3 Fp8 静 态per-tensor      小 批量 的 高 质量     进 行    d | |
                                               量化方
  准 ，针 对 夯 oF 模 块 中所有Linear 都采用 了 静态per-ten5or    _ i
  式 ，并 且 经 过评测 效果 无 损   。        :
  相 较 于 两机FP8 部 署 ，QRP     提升

## Page 35

BD)    减少     量
      需求     -                     力

                           中，      传
长 序列 (32k LAL) Prefill 阶段          统  Attention 计算 复杂 度为  0 [n2?)，
                 上 。
且         序列 增长 占比显著
      注意力算法，            减
通过                 少    每个         与   Token        的计算
                           Query  Key      次数，            可 将 复
杂 度    从 (n*) 降
      D   至   0 (n}—             Query 仅 与     部分Key Token  [如
      个 ，为 超 参) 计算 ，注 意 力  得    分从    简化
100                            刀 x     为N«100,
场景 的计算 速度与 吞吐 量    。


  分析: 通过 分 析Deep5eeK
                           模型的Rttention
 1 HRttention                 的数值                         分 布，    ln


                                                                       Sparse attention End2End Input 19k, Output 1k, TTFT(ms)
 2                                                        nid            —      7
  数 据 即 可 为 每 个Rttention 自 动 化 的 搜索 出 最 佳的  模式 及          超 参。     “     2990.            2043.4
                                                                   4     3407.8           2715.6      1.15x

 3                             Attention
有 动态     性 ， 如 果 使用静态 的    码 迁移 泛化 能 力 很    。内 此 通过 在 线 动 态
      撞 码计算 算     ，基 于  入 实时 计算 Key Token
      子                        重要性，生 成对应 的                    足
    码。
撞

## Page 36

Bl]   减少               -KV
             需求        量   Cache store

             最大的价值是节省     Pre     的 算 力 资 源            (oemeee
 KV Cache store                             。
 e.9. 某 些 场景下20% 的 重复率 可以 减少16% 的 Pre       计算  。

 一  、 方 案 核  心 概述                                      )    [Peny|
 基于 vLLM 集成 LMCache 作为缓存 引擎 ，对 接  远程
 存储   ，支持  本 地  +    远程  湿合缓存 提升  推理   性  能 ;核心架构  为
 vVLL 【推理 引擎    )    +LMCache (KV 存储 层 )  +  远程存储  (FF
    化/分布
 久               式访问)  支
                      ，   持隐式 / 显 式 缓存 模式    ，通 过 多 副本
 +  动态 扩容 实现 容 灾      。

 二  、   关 键 组 件作用
                                                命
 LMCache:  KV 缓存 核心 存储 后     ，    负 责 读   、  中    、         |
                         端      写              判断     一
  性   校验，  支   持PCF5     文件 接口;
 致
 远程   存储:  HIFS #3,        RAS.                        |    | V
                                               【命中        werers  |
 VLLM 集成   :   实现        AH, RA LMCache 逻辑       统
 计  、 缓存开关 控制    )       。

## Page 37

BB) 效果 结 输入 场景
    优化 总 (3.5k /TK 出 )




 TTFT (HEIR)    =3.25    园 <25
 tokens/s 【生成速度 )    =8 token/s    =22 token/s    >20

 单机 吞吐 (QPM)        =120        =212        提升 76.7%

## Page 38

_(no text content on this page)_

## Page 39

    展望未来

    1



CPP. SP

    调度 优化 :
    PPIAERW (Prefill) 、KV cache 调度 优化 (Decode)

    HERR OIL:
存 分离 、 计 算 与 通信 重 优化
    动态

    算 子 优化 :
算子融合 、细 粒度计算 重
    深度



    2， 低 资 源 需 求
           算子深度优化
       化 、通 信人 系列

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[/private/tmp/lfs_pdfs/slides/黄石柱-Deepseek推理性能优化.pdf]]`
