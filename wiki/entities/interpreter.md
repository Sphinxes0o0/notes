---
type: entity
tags: [interpreter, bytecode, runtime, language-vm]
created: 2026-05-29
sources: [handson-rust-interpreters, handson-language-vm]
---

# Interpreter

## 定义

解释器是按需读取源代码或字节码并立即执行的程序。与编译器将代码提前翻译成机器码不同，解释器在运行时逐句执行。

## 关键要点

### 解释器 vs 编译器

| 方面 | 解释器 | 编译器 |
|------|--------|--------|
| 翻译时机 | 运行时 | 编译时 |
| 输出 | 直接执行 | 机器码/字节码 |
| 启动开销 | 小 | 大 |
| 运行开销 | 大（每次都要解释） | 小（原生执行） |
| 跨平台 | 源码级或字节码级 | 需多平台后端 |

### 两大实现路线

**AST 解释器**（递归下降）
- 源码 → Parser → AST → 递归求值
- 结构直观，适合教学和原型
- 性能较差（大量虚函数调用）

**字节码解释器**（VM）
- 源码 → Compiler → Bytecode → VM 执行
- 性能更好，执行模型统一
- 主流语言选择（Python, Ruby, JVM）

### 核心组件

```
Source Code
    ↓
Lexer (Tokenizer)  → Tokens
    ↓
Parser  → AST (Abstract Syntax Tree)
    ↓
Semantic Analyzer (Type Check, Name Resolution)
    ↓
Interpreter / Compiler
    ↓
Runtime (VM / Native)
```

### 内存管理
- **手动管理**（C/C++风格）：malloc/free，程序员负责
- **GC 主流**：Tracing GC（mark-sweep, generation），参考 [[handson-rust-interpreters]] 的 Sticky Immix
- **Arena Allocation**：解释器预分配大块内存，按需分配（常见于 AST 解释器）

### Rust 实现解释器的特殊挑战
- **Safe vs Unsafe 边界**：解释器需大量 unsafe 操作（原始指针、内存布局）
- **Custom Allocator**：解释器独占堆，减少 GC 延迟
- **Tagged Pointer**：低开销的多态对象表示

## 相关概念

- [[virtual-machine]] — 字节码解释器运行在 VM 之上
- [[compiler-from-scratch]] — 编译器是解释器的上游，生成字节码或机器码
- [[memory-hierarchy]] — 解释器的堆分配和 GC 是内存层次的应用

## 来源详情

- [[handson-rust-interpreters]] — Rust 解释器全栈：自定义分配器 + 编译器 + VM + GC
- [[handson-language-vm]] — C 语言构建 VM：Part 00-33+ 覆盖从硬件到字节码
