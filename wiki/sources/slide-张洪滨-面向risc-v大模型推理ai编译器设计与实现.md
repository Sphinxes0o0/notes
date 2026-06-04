---
type: source
source-type: slide
title: "张洪滨_面向RISC-V大模型推理AI编译器设计与实现"
path: slides/张洪滨_面向RISC-V大模型推理AI编译器设计与实现.pdf
source-md5: 49fd9635ce9a0412f1c788ea1f1f9704
size: 23373 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 张洪滨_面向RISC-V大模型推理AI编译器设计与实现

> Ingested from `slides/张洪滨_面向RISC-V大模型推理AI编译器设计与实现.pdf` via `lit parse` on 2026-06-04.
> Source file: 22.83 MB.

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

面向 RISC-V 大模型推理的
AI 编译器设计与实现
报告人： 张洪滨
中国科学院软件研究所
智能软件研究中心

## Page 7

_(no text content on this page)_

## Page 8

    AI 软硬件和编译技术




                  . . .                     （ 手动调优 / 自动调优 ）

DNN 与 BLAS 高性能算子库      深度学习编译器与基础设施         - 约束设计   - 性能仿真
                                            - 搜索策略制定 - 代价模型设计
    . . .     OpenBLAS        . . .

                  /
                  . . .                         Verilog. . .

              CPU /GPU /FPGA /CGRA /ASIC        . . .
                  . . .        EDA              . . .


 AI 系统的软硬件协同设计涉及多项关键技术，主要包括 AI 计算负载的编译优化、硬件加速器设计、软硬件接口设计以及资源联合调优。
一个典型的协同设计流程涵盖需求分析与系统规划、软硬件接口确定、编译工具链开发、硬件设计与仿真，以及协同验证与调优等环节。

        8

## Page 9

    AI 软硬件和编译技术


   AI 编译器
   采用多级编译技术进行优化：        . . .                        （ 手动调优 / 自动调优 ）
   图级别算子融合、计算负载分
   块、向量化优化、死代码消除、  DNN 与 BLAS 高性能算子库  深度学习编译器与基础设施   - 约束设计    - 性能仿真
   常量折叠等。                                            - 搜索策略制定  - 代价模型设计
        . . .       OpenBLAS        . . .                               硬件编译器
                        /                                               在硬件设计领域，多级编译技
                        . . .                            Verilog. . .   术通过提供更高层次的抽象和
                                                                        统一支持，有效解决了硬件设
                    CPU /GPU /FPGA /CGRA /ASIC           . . .          计中的语言和抽象问题。多级
                                                                        编译技术已经应用到了HLS、
                        . . .        EDA                 . . .          硬件编程语言、硬件编译基础
                                                                        设施上。

    AI 系统的软硬件协同设计涉及多项关键技术，主要包括 AI 计算负载的编译优化、硬件加速器设计、软硬件接口设计以及资源联合调优。
    一个典型的协同设计流程涵盖需求分析与系统规划、软硬件接口确定、编译工具链开发、硬件设计与仿真，以及协同验证与调优等环节。

9

## Page 10

    AI 软硬件和编译技术




                  . . .                     （ 手动调优 / 自动调优 ）

DNN 与 BLAS 高性能算子库      深度学习编译器与基础设施         - 约束设计   - 性能仿真
                                            - 搜索策略制定 - 代价模型设计
    . . .     OpenBLAS        . . .

                  /
                  . . .                         Verilog. . .

              CPU /GPU /FPGA /CGRA /ASIC        . . .
                  . . .        EDA              . . .


 AI 系统的软硬件协同设计涉及多项关键技术，主要包括 AI 计算负载的编译优化、硬件加速器设计、软硬件接口设计以及资源联合调优。
一个典型的协同设计流程涵盖需求分析与系统规划、软硬件接口确定、编译工具链开发、硬件设计与仿真，以及协同验证与调优等环节。

        10

## Page 11

RISC-V 近期事件









https://riscv.org/blog/risc-v-jtc1-pas-submitter/








https://riscv.org/blog/risc-v-jtc1-pas-submitter/
    11

## Page 12

RISC-V 近期事件










12

## Page 13

AI 软硬件和编译技术










13

## Page 14

_(no text content on this page)_

## Page 15

    什么是 MLIR

        不是Machine Learning，但为Machine Learning而生

    MLIR (Multi-Level Intermediate Representation)

    The MLIR project is a novel approach to building reusable and extensible compiler
    infrastructure. MLIR aims to address software fragmentation, improve compilation for
    heterogeneous hardware, significantly reduce the cost of building domain specific
    compilers, and aid in connecting existing compilers together.
                 •   处理软件的碎片化
    一个可重用、可扩展的   •   为面向异构硬件的编译提供支持
开源编译基础框架         •   为领域专用编译器的开发减少开销
                 •   连接已有的各种编译器
                         15

## Page 16

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     16

## Page 17

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     17

## Page 18

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     18

## Page 19

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     19

## Page 20

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     20

## Page 21

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     21

## Page 22

 MLIR 简介

MLIR Overview
The MLIR project is a novel approach to building
reusable and extensible compiler infrastructure.

MLIR Ecosystem
- Language: Mojo
- Compilers for AI Framework:
 Torch-MLIR, MHLO-MLIR, ONNX-MLIR
- Execution Environment: IREE
- End-to-End Compiler：Buddy Compiler
- Hardware Compiler：CIRCT
- Compilers for Specific Hardware：Triton，TPU-MLIR  MLIR：多层中间表示编译基础设施[1]
- Compiler Frontend：Polygeist        [1] Codegen Dialect Overview,
     https://discourse.llvm.org/t/codegen-dialect-overview/2723
     22

## Page 23

MLIR 多级编译路径



func.func @matmul(%a : memref<?x?xf32>,
                   %b : memref<?x?xf32>,
   linalg.matmul   %c : memref<?x?xf32>) {
  ins(%a, %b: memref<?x?xf32>, memref<?x?xf32>)
  outs(%c:memref<?x?xf32>)
}  return






   -convert-linalg-to-loops









                   23

## Page 24

MLIR 多级编译路径




func.func @matmul(%a : memref<?x?xf32>,
                   %b : memref<?x?xf32>,
   linalg.matmul   %c : memref<?x?xf32>) {
  ins(%a, %b: memref<?x?xf32>, memref<?x?xf32>)
  outs(%c:memref<?x?xf32>)
}  return






-convert-linalg-to-loops
-convert-scf-to-cf







                   24

## Page 25

MLIR 多级编译路径



func.func @matmul(%a : memref<?x?xf32>,
                   %b : memref<?x?xf32>,
   linalg.matmul   %c : memref<?x?xf32>) {
  ins(%a, %b: memref<?x?xf32>, memref<?x?xf32>)
  outs(%c:memref<?x?xf32>)
}  return






-convert-linalg-to-loops
-convert-scf-to-cf
-finalize-memref-to-llvm







                   2525

## Page 26

MLIR 多级编译路径



func.func @matmul(%a : memref<?x?xf32>,
                   %b : memref<?x?xf32>,
   linalg.matmul   %c : memref<?x?xf32>) {
  ins(%a, %b: memref<?x?xf32>, memref<?x?xf32>)
  outs(%c:memref<?x?xf32>)
}  return






-convert-linalg-to-loops
-convert-scf-to-cf
-finalize-memref-to-llvm
-convert-arith-to-llvm






                   26

## Page 27

MLIR 多级编译路径



func.func @matmul(%a : memref<?x?xf32>,
                   %b : memref<?x?xf32>,
   linalg.matmul   %c : memref<?x?xf32>) {
  ins(%a, %b: memref<?x?xf32>, memref<?x?xf32>)
  outs(%c:memref<?x?xf32>)
}  return






-convert-linalg-to-loops
-convert-scf-to-cf
-finalize-memref-to-llvm
-convert-arith-to-llvm
-convert-func-to-llvm






                   27

## Page 28

RISC-V Vector 扩展
RVV Overview                                                 Library
The RISC-V Vector extension adds support for                     …
high-performance vector operations that allow for the            OpenBLAS
efficient processing of large amounts of data.               Toolchain
RVV Features
- Dynamic vector length at runtime, smaller code size.
- Vector length agnostic (VLA), better code portability.     Hardware
- Functional unit pipelining, larger data-level parallelism.

RVV Ecosystem
- Library: OpenCV, OpenBLAS, etc.                                …
- Compiler: GCC, LLVM
- Emulator: QEMU
- Hardware: Intelligence X280, XuanTie C906, etc.
                                                                 28

## Page 29

    RISC-V Vector 扩展
   RVV Vector Register Configuration
                                         VLA （Vector Length Agnostic）
    V31 ... ...                          VLEN is bound to the processor implementation, not to the instruction set.
    V0                                   RVV code adapts to the machine's vector register length at runtime.

                  VLEN
（ The Length of Hardware Vector Register）










                                         29

## Page 30

    RISC-V Vector 扩展
   RVV Vector Register Configuration
                                           VLA （Vector Length Agnostic）
    V31 ... ...                            VLEN is bound to the processor implementation, not to the instruction set.
    V0                                     RVV code adapts to the machine's vector register length at runtime.

                  VLEN                      Runtime Vector Configuration
（ The Length of Hardware Vector Register）   LMUL = 2
                                            ( Vector Register Group Multiplier )


                                            VLEN x LMUL









                                            30

## Page 31

    RISC-V Vector 扩展
   RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )


                                              VLEN x LMUL









                                              31

## Page 32

    RISC-V Vector 扩展
    RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )


                                              VLEN x LMUL

                                              AVL （The Application Vector Length）
                                              The application specifies the total number of elements to be processed.






                                              32

## Page 33

    RISC-V Vector 扩展
    RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )


                                              VLEN x LMUL

                                              AVL （The Application Vector Length）
                                              The application specifies the total number of elements to be processed.

                                              Configuration-Setting Instructions ( vsetvli / vsetivli / vsetvl )



                                              33

## Page 34

    RISC-V Vector 扩展
    RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )


                                              VLEN x LMUL

                                              AVL （The Application Vector Length）
    vsetvli a3, a0, e16, m4                   The application specifies the total number of elements to be processed.
                                              Configuration-Setting Instructions ( vsetvli / vsetivli / vsetvl )



                                              34

## Page 35

    RISC-V Vector 扩展
   RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )

        SEW = 16
        AVL        LMUL = 4                       VLEN x LMUL
                                              AVL （The Application Vector Length）
    vsetvli a3, a0, e16, m4                   The application specifies the total number of elements to be processed.
                                              Configuration-Setting Instructions ( vsetvli / vsetivli / vsetvl )



                                              35

## Page 36

    RISC-V Vector 扩展
   RVV Vector Register Configuration
                                             VLA （Vector Length Agnostic）
    V31 ... ...                              VLEN is bound to the processor implementation, not to the instruction set.
    V0                                       RVV code adapts to the machine's vector register length at runtime.

                  VLEN                        Runtime Vector Configuration
（ The Length of Hardware Vector Register）     LMUL = 2        SEW ( Selected Element Width )
                                              ( Vector Register Group Multiplier )

        SEW = 16
        AVL        LMUL = 4                       VLEN x LMUL
                                              AVL （The Application Vector Length）
    vsetvli a3, a0, e16, m4                   The application specifies the total number of elements to be processed.
                                              Configuration-Setting Instructions ( vsetvli / vsetivli / vsetvl )

               VL
( Dynamic Runtime Vector Length)

                                                  36

## Page 37

MLIR 的 RISC-V Vector 动态特性支持
RISC-V Vector Extension Vectorization

A[0] A[1] ... ... A[??] A[??] + B[0] B[1] ... ... B[??] B[??]

    C[0] C[1]     ... ...     C[??] C[??]










37

## Page 38

     MLIR 的 RISC-V Vector 动态特性支持
RISC-V Vector Extension Vectorization

 A[0] A[1] ... ...   A[??] A[??] + B[0] B[1] ... ... B[??] B[??]

     C[0] C[1]     ... ...     C[??] C[??]

     Get the application vector length (d) at runtime
 Mask-Based Approach        Strip-Mining Approach

Tail = getTail(d)        AVL = d
Loop:        While(AVL > 0):
 if (not Tail)        do:
 vector load        vl = setvl AVL，LMUL，SEW
 vector add        vector load vl
 vector store        vector add vl
 else        vector store vl
 calculate mask        AVL = AVL - vl
 masked load        End
 masked add
 masked store
 end if
 End loop
     38

## Page 39

     MLIR 的 RISC-V Vector 动态特性支持
RISC-V Vector Extension Vectorization
     ... ...        +    ... ...                              AVL = d
 A[0] A[1]        A[??] A[??]    B[0] B[1]    B[??] B[??]     While(AVL > 0):
                                                                  do:
                                                                   vl = setvl AVL，LMUL，SEW
     C[0] C[1]      ... ...      C[??] C[??]                       vector load vl
                                                                   vector add vl
     Get the application vector length (d) at runtime              vector store vl
 Mask-Based Approach        Strip-Mining Approach             End  AVL = AVL - vl
Tail = getTail(d)        AVL = d                              Strip-Mining Approach
Loop:        While(AVL > 0):
 if (not Tail)        do:                                     -     Initialize the AVL
 vector load        vl = setvl AVL，LMUL，SEW
 vector add        vector load vl                             -     For each iteration:
 vector store        vector add vl
 else        vector store vl                                       -     Set the dynamic vector length
 calculate mask        AVL = AVL - vl
 masked load        End                                            -     Perform vector operation with the dynamic VL
 masked add
 masked store                                                      -     Update the AVL
 end if
 End loop                                                     -     Until all elements have been processed
                                                                             39

## Page 40

     MLIR 的 RISC-V Vector 动态特性支持
RISC-V Vector Extension Vectorization                         Information Required at Compile Time：
     ... ...        ... ...                                   -  Dynamic VL Configuration
 A[0] A[1]        A[??] A[??]  +  B[0] B[1]    B[??] B[??]       -     AVL Configuration
                                                                 -     LMUL Configuration
     C[0] C[1]      ... ...      C[??] C[??]                     -     SEW Configuration
                                                                 AVL = Application Vector Length
                                                                 SEW = Selected Element Width
     Get the application vector length (d) at runtime            LMUL = Vector Register Group Multiplier
 Mask-Based Approach        Strip-Mining Approach             -  Operations Dynamic VL Operand

Tail = getTail(d)        AVL = d
Loop:        While(AVL > 0):
 if (not Tail)        do:
 vector load      Set Dynamic VL     vl = setvl AVL，LMUL，SEW
 vector add        vector load vl
 vector store     Ops Accept Dynamic VL     vector add vl
 else        vector store vl
 calculate mask        AVL = AVL - vl
 masked load        End
 masked add
 masked store
 end if
 End loop
                                                                           40

## Page 41

     MLIR 的 RISC-V Vector 动态特性支持
RISC-V Vector Extension Vectorization                         Information Required at Compile Time：
     ... ...        ... ...                                   -      Dynamic VL Configuration
 A[0] A[1]        A[??] A[??]  +  B[0] B[1]    B[??] B[??]                   -     AVL Configuration        No SETVL Operation
                                                                             -     LMUL Configuration       Cannot Set Dynamic VL
     C[0] C[1]      ... ...      C[??] C[??]                                 -     SEW Configuration
                                                                             AVL = Application Vector Length
                                                                             SEW = Selected Element Width
     Get the application vector length (d) at runtime                        LMUL = Vector Register Group Multiplier
 Mask-Based Approach        Strip-Mining Approach             -      Operations Dynamic VL Operand
Tail = getTail(d)        AVL = d                              Vector operations do not accept dynamic VL parameters.
Loop:        While(AVL > 0):                                      %0 = arith.addf %v, %v : vector<8xf32>
 if (not Tail)        do:
 vector load      Set Dynamic VL     vl = setvl AVL，LMUL，SEW
 vector add        vector load vl
 vector store     Ops Accept Dynamic VL     vector add vl     MLIR Limitation
 else        vector store vl
 calculate mask        AVL = AVL - vl
 masked load        End
 masked add
 masked store
 end if
 End loop
                                                                                                                41

## Page 42

 MLIR 的 RISC-V Vector 动态特性支持










                                                                    Vector Dialect    Add abstraction support for dynamic VL.
                                                                    AMX Dialect
                                                                    X86 Vector Dialect
                                                                    Arm Neon Dialect
                                                                    Arm SVE Dialect
MLIR Lowering Paths - https://mlir.llvm.org/docs/Dialects/Vector/   RVV Dialect      Add abstraction support for RVV-specific ops.
                                                                        42

## Page 43

MLIR 的 RISC-V Vector 动态特性支持

1 – RVV-Specific Dialect SetVL Operation: Set dynamic vector length
( RVV SetVL Op -> Low-Level SetVL Intrinsic Op -> LLVM IR -> Assembly Code )
%vl = rvv.setvl %avl, %sew, %lmul : index
AVL = Application Vector Length
SEW = Selected Element Width
LMUL = Vector Register Group Multiplier

2 – Generic Vector Predication Operation
( Predication Op + Inner Op -> VP Intrinsic Op -> LLVM IR -> Assembly Code )
%vec = vector_exp.predication %mask, %vl : vector<[4]xi1>, i32 {
%ele = vector.load %m[%c0, %c0]: memref<8x8xi32>, vector<[4]xi32>
vector.yield %ele : vector<[4]xi32>
} : vector<[4]xi32>




43

## Page 44

MLIR 的 RISC-V Vector 动态特性支持
Vectorization Algorithm for Matrix Multiplication




%vl = rvv.setvl %avl, %sew, %lmul : index










%vec = vector_exp.predication %mask, %vl : vector<[4]xi1>, i32 {
%ele = vector load / vector store / arith operations ...
vector.yield %ele : vector<[4]xi32>
} : vector<[4]xi32>
    44

## Page 45

MLIR 的 RISC-V Vector 动态特性支持

## Page 46

    MLIR 的 RISC-V Vector 动态特性支持










动态 Vector 的表达能力评估主要针对两个方面：（1）支持向量计算的能力；（2）多种硬件平台的兼容性。将向量计算分为八种类型，
包括元素级操作、归约操作、谓词操作、类型转换等。实验在多种硬件架构（如 x86 AVX512、ARM Neon、RISC-V Vector 等）和设
备上进行，设备分布广泛（从嵌入式开发板到服务器）。结果表明，动态 Vector 能够有效支持所有八种向量操作类型，并生成适配多
种硬件平台的高性能代码，充分展示了其向量计算的表达能力和广泛的应用范围。


    46

## Page 47

MLIR 的 RISC-V Vector 动态特性支持

 实验结果表明，动态 Vector 在规则驱动和自动调优两种转换方法下，整体性能均优于其他方案。在具体平台上的表现如下：在 AVX2
 平台上，相比 Google Highway 和 XSIMD 分别提升了 1.09 倍和 1.13 倍；在 AVX512 平台上，相比 Google Highway 和 XSIMD
 分别提升了 1.33 倍和 1.32 倍；在 ARM Neon 平台上，相比 Google Highway 和 XSIMD 分别提升了 1.45 倍和 1.71 倍；在 ARM
 SVE 平台上，相比 Google Highway 和 XSIMD 分别提升了 1.42 倍和 1.43 倍；在 RVV 平台上，相比 Google Highway 和 XSIMD
 分别提升了 1.68 倍和 1.78 倍。这些结果表明，动态 Vector 在多种硬件架构下均具有显著的性能优势。










    47

## Page 48

MLIR 的 RISC-V Gemmini 加速器支持

Gemmini Hardware Architecture[1]    Gemmini Software Stack


C++ Operators

Macro Function

Inline Assembly

RISC-V GNU Toolchain




Gemmini ISA



Spike Simulator

[1] The origin image is from Gemmini GitHub repository - https://github.com/ucb-bar/gemmini

    48

## Page 49

MLIR 的 RISC-V Gemmini 加速器支持
    Deep Learning Models        Buddy Compiler Gemmini Support   Gemmini Software Stack

                                         MLIR Operations          C++ Operators
linalg.matmul      gemmini.tile_matmul
linalg.conv_2d*    gemmini.tile_conv     Gemmini MLIR Dialect     Macro Function
... ...        ... ...
Linalg Dialect        Gemmini Dialect    Gemmini LLVM
                                           Intrinsic              Inline Assembly

                                         RISC-V GNU Toolchain    RISC-V GNU Toolchain
int_riscv_loop_ws_config_bounds
int_riscv_loop_ws_config_addrs_ab
int_riscv_loop_ws_config_addrs_dc
int_riscv_loop_ws_config_strides_ab
int_riscv_loop_ws_config_strides_dc                               Gemmini ISA
... ...
    Gemmini Intrinsic
                                                                 Spike Simulator
    Gemmini ISA

                                                                      49

## Page 50

    MLIR 的 RISC-V Gemmini 加速器支持

                                                                                              数据流分析
                                                                                        （以矩阵乘法和转置计算融合为例）

    对接上层框架  linalg.m atm ulins(% m em 0,% m em 1:m em ref<8x8xi8>,m em ref<8x8xi8>)
                outs(% m em 2:m em ref<8x8xi8>)

                                                                                     矩阵乘法节点  转置计算节点  其他计算节点
    高层中间表示  gem m ini.tile_m atm ul% aloc% aloc_0 % aloc_1% aloc_2
                 :m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi32>  计算节点依赖信息 计算节点尺寸信息
                                                   高层级中间表示      分块策略                      基于规则的编译策略制定方法
转换到低层级中间表示                                                                          编译时根据数据流分析和硬件信息指导指令选择分块策略
                                                                                     脉动阵列尺寸  数据流重用模式 存储器尺寸
            ......
            gem m ini.intr.config_ex% 116,% 117:i64,i64                                      硬件信息收集
            ......
            gem m ini.intr.config_st% 119,% 120 :i64,i64
            ......
            gem m ini.intr.config_ld % 122,% 121:i64,i64    低层中间表示
            ......
            gem m ini.intr.config_ld % 124,% 123 :i64,i64   对接硬件指令
            ......
            gem m ini.intr.config_ld % 126,% 125 :i64,i64
            ......
            gem m ini.intr.loop_w s% 137,% 138 :i64,i64
            ......


Gemmini 方言核心思想：将定制硬件加速器的硬件抽象层构建为双层中间表示。高层中间表示对接上层框架，低层中间表示对接硬件
指令，可以将定制硬件接入人工智能框架，提升开发效率，降低维护开销。通过多级编译技术，将高层级计算负载中间表示映射到低层
级硬件相关的中间表示。这种方法能够根据特定的软硬件信息，在编译阶段动态制定编译策略，提高执行效率。 50

## Page 51

    MLIR 的 RISC-V Gemmini 加速器支持

                                                                                              数据流分析
                                                                                        （以矩阵乘法和转置计算融合为例）

    对接上层框架  linalg.m atm ulins(% m em 0,% m em 1:m em ref<8x8xi8>,m em ref<8x8xi8>)
                outs(% m em 2:m em ref<8x8xi8>)

                                                                                     矩阵乘法节点  转置计算节点  其他计算节点
    高层中间表示  gem m ini.tile_m atm ul% aloc% aloc_0 % aloc_1% aloc_2
                 :m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi32>  计算节点依赖信息 计算节点尺寸信息
                                                   高层级中间表示      分块策略                      基于规则的编译策略制定方法
转换到低层级中间表示                                                                          编译时根据数据流分析和硬件信息指导指令选择分块策略
                                                                                     脉动阵列尺寸  数据流重用模式 存储器尺寸
            ......
            gem m ini.intr.config_ex% 116,% 117:i64,i64                                      硬件信息收集
            ......
            gem m ini.intr.config_st% 119,% 120 :i64,i64
            ......
            gem m ini.intr.config_ld % 122,% 121:i64,i64    低层中间表示
            ......
            gem m ini.intr.config_ld % 124,% 123 :i64,i64   对接硬件指令
            ......
            gem m ini.intr.config_ld % 126,% 125 :i64,i64
            ......
            gem m ini.intr.loop_w s% 137,% 138 :i64,i64
            ......


Gemmini 方言核心思想：将定制硬件加速器的硬件抽象层构建为双层中间表示。高层中间表示对接上层框架，低层中间表示对接硬件
指令，可以将定制硬件接入人工智能框架，提升开发效率，降低维护开销。通过多级编译技术，将高层级计算负载中间表示映射到低层
级硬件相关的中间表示。这种方法能够根据特定的软硬件信息，在编译阶段动态制定编译策略，提高执行效率。 51

## Page 52

    MLIR 的 RISC-V Gemmini 加速器支持

                                                                                              数据流分析
                                                                                        （以矩阵乘法和转置计算融合为例）

    对接上层框架  linalg.m atm ulins(% m em 0,% m em 1:m em ref<8x8xi8>,m em ref<8x8xi8>)
                outs(% m em 2:m em ref<8x8xi8>)

                                                                                     矩阵乘法节点  转置计算节点  其他计算节点
    高层中间表示  gem m ini.tile_m atm ul% aloc% aloc_0 % aloc_1% aloc_2
                 :m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi8>m em ref<8x8xi32>  计算节点依赖信息 计算节点尺寸信息
                                                   高层级中间表示      分块策略                      基于规则的编译策略制定方法
转换到低层级中间表示                                                                          编译时根据数据流分析和硬件信息指导指令选择分块策略
                                                                                     脉动阵列尺寸  数据流重用模式 存储器尺寸
            ......
            gem m ini.intr.config_ex% 116,% 117:i64,i64                                      硬件信息收集
            ......
            gem m ini.intr.config_st% 119,% 120 :i64,i64
            ......
            gem m ini.intr.config_ld % 122,% 121:i64,i64    低层中间表示
            ......
            gem m ini.intr.config_ld % 124,% 123 :i64,i64   对接硬件指令
            ......
            gem m ini.intr.config_ld % 126,% 125 :i64,i64
            ......
            gem m ini.intr.loop_w s% 137,% 138 :i64,i64
            ......


Gemmini 方言核心思想：将定制硬件加速器的硬件抽象层构建为双层中间表示。高层中间表示对接上层框架，低层中间表示对接硬件
指令，可以将定制硬件接入人工智能框架，提升开发效率，降低维护开销。通过多级编译技术，将高层级计算负载中间表示映射到低层
级硬件相关的中间表示。这种方法能够根据特定的软硬件信息，在编译阶段动态制定编译策略，提高执行效率。 52

## Page 53

    MLIR 的 RISC-V Gemmini 加速器支持


                                  1200
                                  1000  Gemmini 原生软件栈        964.79
                                      Gemmini MLIR 方言（本文）        870.11
                                   800

    Gemmini 硬件配置                   600

                                   400
                                   200  114.48 92.76  206.58 176.88  256.18 251.82  66.62 73.43
                                     0 (512, 1536) x (1536, 256) (1504, 512) x (512, 512) (1504, 64) x (64, 1504) (1504, 1504) x (1504, 64) (1504, 2048) x (2048,512)
                                                                                           矩阵乘法测试用例/(I,K) x (K,J)
    Gemmini 原生软件栈的 ONNX 移植开销评估                                                          Gemmini 方言的多级编译方法与原生软件栈的性能对比

    实验结果表明：（1）Gemmini 官方移植的 ONNX 仓库仅关键算子实现就超过 2,000 行代码，并且移植方式导致私有仓库与上游
    社区严重脱节。本文提出的方法直接对接标准的 MLIR 和 PyTorch 接口，避免了仓库分叉问题，降低了长期维护成本。
    （2）Gemmini 方言的多级编译方法相较于原生软件栈实现了 9.8% 至 18.9% 的性能提升。在规模为(1504, 1504) ×(1504, 64)
    的测试案例中，由于分块策略差异。本文方法的分块策略优先考虑累加存储器的使用率，在该尺寸的用例中，存储空间的利用率小
    于Gemmini 原生软件栈的策略，因此在该尺寸下Gemmini 方言编译方法的性能逊色于原生软件栈。
                                      53










时钟周期/104×Cycles

## Page 54

_(no text content on this page)_

## Page 55

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










55

## Page 56

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










56

## Page 57

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










57

## Page 58

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










58

## Page 59

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










59

## Page 60

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










60

## Page 61

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










61

## Page 62

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










62

## Page 63

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










63

## Page 64

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










64

## Page 65

  PyTorch 到 MLIR 的端到端编译通路
  （Ruyi Buddy Compiler）




  AutoConfig 编译优化性能调优机制
  核心思想
      编译优化的多种算法
      优化实现的多种策略






编译时引入分析模型，显著缩小调优空间        将调优的复杂度交给编译器优化的开发者
分析模型的建模方法，确保优化可预测、可解释     1. 编写可配置的代码生成 Rewrite Pattern
可配置的优化实现，达成跨平台的优化效果       2. 针对优化算法构造分析模型进行自动配置     65

## Page 66

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）

## Page 67

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）

## Page 68

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）

## Page 69

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）
= ƛ      + ƛ      +    ƛ
浮点运算开销     访存开销     =1  特殊指令开销

## Page 70

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）
= ƛ      + ƛ      +    =1 ƛ
浮点运算开销     访存开销     特殊指令开销
编译时预测总开销

## Page 71

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）

## Page 72

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）

## Page 73

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）
•   单位加速比所需调优开销 =    总调优开销
        相较于基准性能的加速比
•   与 TVM 的自动调优方式相比，AutoConfig 中的分析模型可以显著缩小调优空间，
    因此能够解决搜索开销大的问题。










    73

## Page 74

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










74

## Page 75

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










75

## Page 76

PyTorch 到 MLIR 的端到端编译通路
（Ruyi Buddy Compiler）










76

## Page 77

 PyTorch 到 MLIR 的端到端编译通路
Text-Modal AI Inference – DeepSeek    Speech-Modal AI Inference – Whisper







 Text-to-Image AI Model Inference
 – Stable Diffusion




 77

## Page 78

Ruyi Buddy Compiler










Homepage: https://buddy-compiler.github.io/
GitHub: https://github.com/buddy-compiler
    78

## Page 79

Ruyi Buddy Compiler










79

## Page 80

Thanks!

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/张洪滨_面向RISC-V大模型推理AI编译器设计与实现.pdf]]`
