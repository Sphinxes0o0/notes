---
type: entity
tags: [vm, bytecode, interpreter, runtime]
created: 2026-05-29
sources: [handson-language-vm]
---

# Virtual Machine

## 定义

虚拟机（VM）是通过软件模拟的计算机，执行字节码而非原生机器码。与物理 CPU 类似，有寄存器/栈/指令集，但通过软件解释执行，实现「write once, run anywhere」。

## 关键要点

### VM vs Physical CPU

| 方面 | 物理 CPU | 虚拟机 |
|------|----------|--------|
| 指令 | x86/ARM 机器码 | Bytecode |
| 执行 | 硬件直接执行 | 软件解释 |
| 跨平台 | 需重新编译 | 同一份字节码 |
| 性能 | 最优 | 有开销（但 JIT 可接近原生） |

### 两大范式

**栈式 VM**（JVM, Python）
```
push a    ; 将 a 压栈
push b    ; 将 b 压栈
add       ; 弹出两值相加，结果压栈
```
- 指令短（隐式操作数），但多次内存访问
- 适合资源受限环境

**寄存器 VM**（Lua 5.0+, Dalvik）
```
add r1, r2, r3    ; r1 = r2 + r3
```
- 指令长（显式寄存器），无栈颠簸
- 更接近物理 CPU，执行效率更高

### 字节码设计
- **固定宽度 vs 可变宽度**：固定宽（如 4 字节）解码简单；可变宽（如 IBM 360）节省空间
- **指令分类**：算术/逻辑/控制流/内存访问/函数调用

### 运行时组件
- **Call Stack**：函数调用栈帧管理
- **Heap**：动态对象分配（配合 GC）
- **Constant Pool**：字符串/字面量集中存储
- **Frame**：每个函数的局部变量 + 操作数栈

### 行业案例
- **JVM**：Java、Groovy、Kotlin、Scala
- **CLR**：C#, F#, VB.NET
- **Python VM**：CPython 字节码
- **BEAM**：Erlang/Elixir（VM 层面并发）

## 相关概念

- [[interpreter]] — 解释器是 VM 的上层封装，读取字节码并执行
- [[compiler-from-scratch]] — 编译器前端生成字节码，后端对接 VM
- [[database-internals]] — SQLite/LevelDB 等数据库内部都有字节码执行引擎（如 SQLite VM）

## 来源详情

- [[handson-language-vm]] — Part 00-33+，用 C 构建完整语言 VM（Iridium）
