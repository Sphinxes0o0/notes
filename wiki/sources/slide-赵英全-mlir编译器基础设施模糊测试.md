---
type: source
source-type: slide
title: "赵英全_MLIR编译器基础设施模糊测试"
path: slides/赵英全_MLIR编译器基础设施模糊测试.pdf
size: 7690 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 赵英全_MLIR编译器基础设施模糊测试

> Ingested from `slides/赵英全_MLIR编译器基础设施模糊测试.pdf` via `lit parse` on 2026-06-04.
> Source file: 7.51 MB.

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

MLIR编译器基础设施模糊测试
赵英全

## Page 7

MLIR编译器                                     1      Dialect(方言)：定义操作、属性和类型
        …                                              如：用于表示计算图的 tosa dialect
LLVM IR  ByteCode  SIL IR  … XLA HLO        2      Pass(转换)：遍历程序并执行转换和优化
        …                                              如：tosa 方言的Lowering Pass
1   基础设施成本高昂且容易出错                           level 1    tosa
2   （例如，循环展开优化）                             level 2    scf  memref  ...
        MLIR                                    ...
    Multi-Level IR (Compiler Infrastructure)

## Page 8

  多级中间表示    （Multi-Level IR）
  %2 = tosa.transpose %1, %0 : (tensor<1x2x3xi32>, tensor<3xi32>)
  -> tensor<2x3x1xi32>  1

  %0 = memref.get_global @__constant_1x2x3xi32 :
  memref<1x2x3xi32>
  %alloc = memref.alloc() {alignment = 64 : i64} :
  memref<2x3x1xi32>
  scf.for %arg0 = %c0 to %c2 step %c1 {
   scf.for %arg1 = %c0 to %c3 step %c1 {
    %1 = memref.load %0[%c0, %arg0, %arg1] : memref<1x2x3xi32>
    memref.store %1, %alloc[%arg0, %arg1, %c0] :        MLIR powered tools
  memref<2x3x1xi32>
   }
  }

    （例如 llvm 方言）来执行        MLIR
        MLIR的质量保证（测试）
        非常重要！



1: applied passes: -pass-pipeline="builtin.module(func.func(tosa-to-linalg-named,linalg-generalize-named-ops))" and -one-shot-buf erize -func-buf erize -convert-linalg-to-loops -canonicalize

## Page 9

  编译器测试-测试程序生成
  1 传统编译器测试流程
    51%       7%

  2 MLIR测试程序生成    25 %
    …        间接   MLIR    测试多样性有限
       测试程序      MLIR测试程序    测试效果差

1. A Survey of Compiler Testing. Junjie Chen, Jibesh Patra, Michael Pradel, Yingfei Xiong, Dan Hao, Lu Zhang. ACM Computing Surveys (CSUR) 2020

## Page 10

MLIRSmith (ASE 23)
MLIR测试程序生成
多样性 (Dialect中的操作)    有效性 (保障语法和语义的正确性)
                     attribute: [ op = memref.alloc, key = alignment ][[C1]] =>
                     operand: [ visible_vals = {%alloc, ...}, op = memref. store,
                     attrs={}, types ={f32} ][[V6]] => %alloc
MLIR 语法              实例化规则


测试程序模版               测试程序模版实例化

## Page 11

程序模板构建
语法正确性
                  func.func @parallel_store(%cst: f32, %lb: index,
                  %rb: index, %step: index) {
                  %alloc = memref.alloc [[V1]] {alignment = [[C1]]} :
                  memref<?xf32>
                  scf.parallel (%iv) = [[V2]] to [[V3]] step [[V4]] {
                   memref.store [[V5]], [[V6]] [[[V7]]]
                   scf.yield
    type body     }
                  return
                 }
MLIR 程序模板的语法规则         程序模版示例
    [[V]] 和 [[C]] 分别是操作数和属性的占位符

## Page 12

程序模板实例化
语法有效性: 属性、操作数类型、操作数可见性
上下文感知的生成规则 → 12…
q attribute: [ op = memref.alloc, key = alignment ][[C1]] =>
N
q operand: [ visible_vals = {%alloc, ...}, op = memref.store, attrs={}, types = {f32} ][[V6]]
     => %alloc

   func.func @parallel_store(%cst: f32, %lb: index, %rb: index, %step: index) {
    8
    %alloc = memref.alloc(%rb) {alignment =[[C1]]} : memref<?xf32>
    scf.parallel (%iv) = (%lb) to (%rb) step (%step) {
     %alloc   %iv  : memref<?xf32>
  scf.yield
 }
 return
}

## Page 13

实验评估-研究问题
   研究问题1: MLIRSmith能否检测出MLIR编译器中以前未知的错误？
   转换为 MLIR 程序进行模糊测试）？ （将高级源代码程序
     q 对比方法: NNSmith (IREE) and NNSmith (ONNX-MLIR)
     q 评价指标: 检测到的错误数量、覆盖的行数、Dialect Pairs和Operation Pairs

## Page 14

   研究问题1: 未知缺陷检测
   MLIRSmith 检测到53个此前未知的漏洞，其中49/38个漏洞已被开发人员确认/修复
   缺陷根因分析
       Incorrect Rewrite Logic (13)    Incorrect Pattern (9)
   Incomplete Verifier (7)    Unregistered Dialect (5) Incorrect Assertion (4)

 Match     Verifier     Rewriter     Registered
Pattern        Dialects

Source        Opertions        Opertions        Target
Program        Program

       Assertion

## Page 15

    研究问题2: 与间接模糊测试对比
    检测到的错误数量、覆盖的行数、Dialect Pairs和Operation Pairs (24小时)
MLIRSmith    MLIRSmith    MLIRSmith
  (23)       (47220)      (34770)
   15        24918        19639







    MLIRSmith可以覆盖比间接模糊测试更多的特征！

## Page 16

MLIRSmith的局限性
 MLIRSmith 的整体工作流程
            随机    scf.parallel (%iv) = [[V2]] to [[V3]] 随机 scf.parallel (%iv) = %lb to %rb
                  step [[V4]] {        step %step {
                      Body;        Body;
                  }        }
 MLIR 语法              程序模版        实例化MLIR程序
 局限性        随机策略限制了对庞大的 MLIR 特征空间探索的能力
            随机策略限制了生成的测试程序未知缺陷检测的能力
                对生成过程进行引导是有必要的！

## Page 17

MLIRod (ISSTA 24)
  观察   q 如，buffer-loop-hoisting 优化需要控制分配操作和循环操作之间的依赖关系来触发.
  覆盖   q 比收集编译器代码覆盖率所需要的时间更少.
  变异  q 基于操作依赖的指导，生成更多样的测试程序.
           覆盖更多样的操作依赖模式，从而发现新的错误

## Page 18

MLIRod的整体流程图                      基于变异的MLIR测试程序生成
 1 种子程序池初始化(MLIRSmith)        2
 3 基于 MLIR-Pass 的模糊测试         4   基于OD-Coverage的种子程序池维护
          选择     基于ODG变异

   种子程序池      种子程序                变异后程序
                                  Pass    crash
       有新覆盖                           测试报告
   丢弃  无新覆盖    OD Coverage        转换后程序

## Page 19

操作依赖图(Operation Dependency Graph, ODG)
操作数类型、结果类型）                           1 func.func @onePlusOne() {
                                      2 %one = arith.constant 1 : i64
1 (arith.addi, (i64, i64), (i64))     3 %res = arith.addi %one, %one : i64
                                      4 return
控制依赖（边）：一个节点的执行受另一个节点的                5 }
执行支配
1 func.func @onePlusOne() {        01: func.func    02: arith.constant
2 %one = arith.constant 1 : i64
5 }

另一个节点使用了该值        02: arith.constant        03: arith.addi
2 %one = arith.constant 1 : i64
3 %res = arith.addi %one, %one : i64
操作依赖图（ODG）：        01: func.func          04: return
    （节点，边）
    02: arith.constant                    03: arith.addi

## Page 20

操作依赖覆盖(Operation Dependency Coverage)
D-step可达性：在D-step中是否存在从一个节
点到另一个节点的路径                        01: func.func    04: return
01:func.func  1
1        2     x        02: arith.constant        03: arith.addi
02:arith.constant    03:arith.addi
    ：
到目标节点的节点构成的子图     由所有 d 步可达       操作依赖覆盖率（OD覆盖率）：OD模式数的
                                  比率
01:func.func                          测试集T
1        2
02:arith.constant    03:arith.addi
                                    所有可能的测试程序

## Page 21

    变异规则: 节点变异
    节点添加: 向ODG中添加一个随机节点.        节点删除：从 ODG 中删除一个随机节点.
    1 func.func @onePlusOne() {        1 func.func @onePlusOne() {
    2    %true = index.bool.constant true                 2    %true = index.bool.constant true
    3    %two = arith.constant 2 : i64                    3    %two = arith.constant 2 : i64
    4    scf.if %true {                                   4    scf.if %true {
    5         %one = arith.constant 1 : i64               -     %one = arith.constant 1 : i64
    6         %res = arith.addi %one, %one : i64          ~                  %one, %one
    +         %newOp = math.absi %res : i64               7    }
    7    }                                                8    return
    8    return              9 }
    9 }
                         1:func.func      8:return                           1:func.func     8:return

2:index.bool.              4:scf.if    3:arith.constant    2:index.bool.     4:scf.if      3:arith.constant
  constant                   constant
    5:arith.constant     6:arith.addi      +:math.absi  5:arith.constant     6:arith.addi

## Page 22

    变异规则: 依赖变异        情况下修改控制依赖关系
    情况下修改数据依赖关系
    1 func.func @onePlusOne() {        01 func.func @onePlusOne() {
    2      %true = index.bool.constant true      02    %true = index.bool.constant true
    3      %two = arith.constant 2 : i64         03 %two = arith.constant 2 : i64
    4      scf.if %true {                           %one = arith.constant 1 : i64
    5      %one = arith.constant 1 : i64         ++    %res = arith.addi %one, %one : i64
               %one
    ~      %res = arith.addi %one, %two : i64    06    scf.if %true {
    7      }        %one = arith.constant 1 : i64
    8      return                                --    %res = arith.addi %one, %one : i64
    9 }                                          09    }
               1:func.func        8:return       10    return
               11 }        1:func.func      10:return
2:index.bool.      4:scf.if     3:arith.constant
  constant                          2:index.bool.        4:scf.if    3:arith.constant
    5:arith.constant  6:arith.addi    constant
               5:arith.constant     6:arith.addi

## Page 23

实验评估-研究问题
 研究问题1: MLIRod能否检测出MLIR编译器中的未知缺陷？
 研究问题2: 相比于MLIRSmith，MLIRod的缺陷检测效果如何？
 研究问题3: MLIRod 中各个组件的贡献如何？
 实验设置:
 q 可达参数  设置为 2.
 q 初始种子： 50 个由 MLIRSmith 生成的 MLIR 程序.
 q Pass序列长度设置为10.

## Page 24

研究问题1: 未知缺陷检测
    MLIRod共检测到68个此前未知的缺陷，其中48/38个缺陷已被开发人员确认/修复
    缺陷根因分析 Incorrect Pattern (20) Incorrect Rewrite Logic (9)
        Incomplete Verifier (7) Unregistered Dialect (1) Incorrect Assertion (1)





    生成的揭错模式！

## Page 25

    研究问题2: 与MLIRSmith对比
    与 MLIRSmith 相比，MLIRod 在漏洞检测方面表现如何？

21 10 4

MLIRod MLIRSmith

      发现
    1 在 24 小时模糊测试中，MLIRod共检测到31个漏洞，而MLIRSmith仅检测到14个漏洞
    2 MLIRod可以检测到21个独特的缺陷，而MLIRSmith仅检测到4个独特的缺陷

## Page 26

研究问题3: 消融实验
MLIRod 中各个组件的贡献如何？
q 变异规则变体:  1     ,        2 ,    3 ,    4 .
q OD-Coverage引导变体:        ,        .
组件      变体名称                               描述
                      1                 移除节点添加变异规则(R1).
变异规则                  2
                      3                 移除节点删除变异规则(R2).
                      4                 移除数据依赖修改变异规则(R3).
                                        移除控制依赖修改变异规则(R4).
引导                                      将程序随机放回种子程序池中.
                          将OD coverage替换为Edge coverage.

## Page 27

研究问题3: 消融实验
组件  方法       缺陷数量
         1     26     发现1
         2     25     每条变异规则都对MLIRod有所贡献。
变异规则     3     16     最有效的变异规则是数据依赖性修改。
         4     26     发现2
引导             20     OD Coverage可以比边覆盖(Edge Coverage)
               3      提供更好的引导。
---            31

## Page 28

MLIRod 和 MLIRSmith的局限性
 MLIRSmith及MLIRod



 现有MLIR模糊测试方法的局限性：检测静默缺陷（Silent Bugs）的能力有限!

## Page 29

静默缺陷检测的挑战（DESIL的理念）
 UB 消除 q 方案: 未定义行为消除 (Undefined Behavior Elimination)
 Lowering q 方案: 下降路径优化 (Lowering Path Optimization)
 缺陷检测     q 方案: 差分测试 (Differential Testing)

     静默缺陷检测

## Page 30

DESIL的整体流程图(OOPSLA 25)
  1 未定义行为消除           2 下降路径优化
  3 差分测试              4 缺陷检测

## Page 31

未定义行为消除
消除给定 MLIR测试程序中的未定义行为：
易触发UB操作收集                       1       %v = affine.vector_load %m[%idx9] : memref<14xi32>, vector<6xi32>
                                2       %p = vector.extract %v[5] : i32 from vector<6xi32>
q 递归收集测试程序中容易出现未定义                              1 插入运行时检查
行为的操作                                           2 准备安全操作
未定义行为消除规则(45)                                   3 替换触发未定义行为操作
q shape inconsistency           1       %EnoughSpace = index.cmp uge(Volume(%m), %FlattenIdx+Volume(vector<6xi32>))
                                2   1   %m1 = scf.if %EnoughSpace -> (memref<?xi32>) {
q index out-of-bounds           3        %new-m = memref.cast %m : memref<14xi32> to memref<?xi32> Check the volume of %m
                                4        scf.yield % %new-m : memref<?xi32>
q invalid memory references     5       } else {
                                6        %new-m = memref.alloc(%EnoughVolume) : memref<?xi32> New memref with enough
q scalar calculations           7   2    linalg.fill ins(%RandVal : i32) outs(%new-m : memref<14xi32>) volume generation
                                8        scf.yield %new-m : memref<?xi32>
q … …                           9       }
                                 10 3   %v = affine.vector_load %m1[%idx9 mod m1.dim(0)] : memref<?xi32>, vector<6xi32>
                                 11     %p = vector.extract %v[5] : i32 from vector<6xi32> Replace old operand with safe version

## Page 32

下降路径优化
在不引入冗余 Pass 的情况下对 MLIR 程序进行下降（Lowering）：
针对特定操作的下降路径构建
q represented as a tuple <o, P, R>
q o is the collected operation.
q P: all required lowering pass for o.          • <affine.for, {p1, p2, p3}, {p1>p2, p2>p3}>
q R: order of P for lowering o.                 • <scf.if, {p2, p3}, {p2>p3}>
q R is a partial order on P. ((P, R) is a poset)
下降路径拓扑排序                                        • <{affine.for, scf.if}, {p1, p2, p3}, {p1>p2, p2>p3}>
q 聚合MLIR程序中特定操作的下降路径， 并                         • 正确下降路径: p1 -> p2 -> p3
找到聚合偏序集中的最大元素                                   • 冗余下降路径: p2 -> p3 -> p1 -> p2 -> p3

## Page 33

    下降差分测试
    在不同的优化序列下生成多个执行结果进行对比：
    校验和计算(Checksum)       优化及下降Pass推荐
    q 计算生成程序中所有整数的校验和     q 根据MLIR程序中的方言和操作推荐优化
        Pass

Optimization      Lowering  ···
    Pass        Pass        Silent Bugs
Checksummed        Executable
  Program        Crash Bugs

## Page 34

实验评估-研究问题
 研究问题1: DESIL能否检测出MLIR编译器中的未知缺陷？
 研究问题2: 与增强后MLIRSmith和MLIRod相比，DESIL在漏洞检测方面表现如何？
 研究问题3: DESIL中各个组件的贡献如何？
 实验设置:
 q 测试程序生成工具: MLIRSmith (  ℎ) 及 MLIRod (  ).

## Page 35

研究问题1:未知缺陷检测
研究问题1: DESIL能否检测出MLIR编译器中的未知缺陷？
q 研究问题1实验设置：应用DESIL对MLIR编译器的最新版本（从 adbf21 版本到 b6d5fa 版本）
进行了为期四个月的模糊测试
缺陷类型      #Bugs      #Fixed Bugs    #Confirmed Bugs
Crash Bug      19     13            16
Silent Bug     23     13            17

DESIL共检测到42个此前未知的缺陷，其中33/26个缺陷已被开发人员确认/修复

## Page 36

研究问题2:与MLIRSmith和MLIRod对比
研究问题2:与增强后MLIRSmith和MLIRod相比，DESIL在漏洞检测方面表现如何？
对比方法名称 #Inconsist.   #FP Inconsist. #FP Rate #TP Inconsist. #Silent Bugs
Smith ℎ ℎ     4,914   4,783         97.33%   131            14
    ℎ         4,542   4,404         96.96%   138            15
             519     0              0%       519            25
             470     0              0%       470            31


检测到了 31 个和 25 个缺陷，优于两种对比方法。

## Page 37

研究问题3:消融实验
研究问题3: DESIL中各个组件的贡献如何？
q / : 将优化推荐替换为随机策略;M可以是 MLIRsmith 或 MLIRod。
q :将下降路径优化替换为随机策略;M可以是 MLIRsmith 或 MLIRod。


18  18  3    12  16  5
    /        /
/  无法在50次迭代中降低任何MLIR程序，而DESIL平均只需22次迭代即可降低MLIR
程序; 18/12个缺陷只能被DESIL检测到，而3/5个只能被变体方法检测到。

## Page 38

总结与感谢



MLIRSmith(ASE’23)    MLIRod(ASE’24)    DESIL(OOPSLA’25)

模版->实例化        OD Coverage引导        支持静默缺陷检测

## Page 39

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/赵英全_MLIR编译器基础设施模糊测试.pdf]]`
