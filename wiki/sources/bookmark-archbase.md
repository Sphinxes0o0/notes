---
type: source
source-type: bookmark
title: "计算机体系结构基础（第3版）"
author: "胡伟武 等（龙芯）"
date: 2024-09-20
summary: "龙芯团队编写的体系结构教材，覆盖ISA设计、CPU流水线、存储层次、多核结构、总线、启动等核心主题"
---

# 计算机体系结构基础（第3版）

## 核心内容

龙芯团队系统性讲解计算机体系结构，围绕"如何造CPU"这一核心问题展开：

**指令系统（ISA）**
- ISA设计原则：兼容性、通用性、高效性、安全性
- CISC vs RISC vs VLIW：x86复杂指令→RISC简化→VLIW编译时并行
- 主流ISA：X86、ARM、MIPS、RISC-V、LoongArch
- 特权级CSR、虚拟内存页表机制、地址空间布局

**计算机组成原理**
- 冯·诺依曼结构五部分：运算器+控制器+存储器+输入+输出
- 哈佛结构（程序/数据分离）vs 冯·诺依曼
- 运算器ALU、FPU、向量运算部件；寄存器堆读写端口是运算单元数量瓶颈
- 以存储器为中心取代以运算器为中心

**指令流水线**
- 单周期→多周期→流水线处理器的演进
- 五级流水线：取指、译码、执行、访存、写回
- 流水线冒险：结构冒险、数据冒险（RAW/WAR/WAW）、控制冒险
- 流水线的时空图分析

**存储层次**
- 寄存器→L1 Cache→L2 Cache→L3 Cache→DRAM→SSD
- Cache映射：直接映射、组相联、全相联
- TLB（Translation Lookaside Buffer）：虚拟地址→物理地址转换缓存

**多核处理结构**
- 多核共享LLC（Last Level Cache）架构
- Snooping vs Directory一致性协议
- NuX interconnect：片上网络拓扑
- 缓存写策略：Write-Through vs Write-Back

**软硬件协同**
- 函数调用约定（x86 fastcall/vectorcall/member function call）
- 地址空间布局：text/rodata/data/bss/heap/stack
- 栈帧结构与寄存器保护
- 编译过程：预处理→编译→汇编→链接

**计算机总线接口**
- AXI/AHB/APB总线协议层次
- Burst传输、突发读写、重叠传输
- 设备配置：BAR寄存器、PCIe配置空间

**特权模式（privileged-ISA）**
- LoongArch CSR寄存器：CRMD、PRMD、EUEN、ECFG、ESTAT
- TLB重填、缓存、异常向量
- 物理地址扩展（PAE）、长模式（Long Mode）切换流程

## 关键引用

- "一以贯之"：应用→系统→结构→逻辑→电路→器件的融会贯通
- ISA是软硬件界面，是软件兼容的关键，是生态建设的终点
- ABI：用户态指令+系统调用，介于API和ISA之间

## 来源详情

- 路径：`raw/bookmarks/ebooks/archbase/`
- 章节：12章（引言/ISA/组成原理/运算器/总线/启动/指令流水线/并行编程/多核/特权ISA/性能评价/总结）
- 图片：70+张（hierarchy、pipeline、cache结构、GDT、页表等）
