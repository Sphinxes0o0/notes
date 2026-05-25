---
type: entity
tags: [machine-code, assembly, x86-64, instruction-set, low-level]
created: 2026-05-25
sources: [pdf-computer-systems-programmers-perspective, pdf-the-linux-programming-interface]
---

# Machine Code: A Programmer's Perspective

## 定义

机器码是 CPU 直接执行的二进制指令格式，汇编语言是其人类可读的文本表示。理解机器码使程序员能够编写更高效、更安全的代码，并理解编译器优化行为。

## 关键要点

### x86-64 寄存器架构

**通用寄存器 (64-bit)：**
```
rax — 返回值 / 累加器        r8-r15 — 新增 64 位寄存器
rbx — 基址（callee-saved）   r9  — 第 5 参数 (System V ABI)
rcx — 第 4 参数              r10 — 第 6 参数
rdx — 第 3 参数 / I/O        r11
rsi — 第 2 参数              r12 — callee-saved
rdi — 第 1 参数              r13 — callee-saved
rbp — 帧指针（callee-saved） r14
rsp — 栈指针                 r15
```

**特殊寄存器：**
- RIP：指令指针（Program Counter）
- EFLAGS：条件标志（ZF/SF/CF/OF/AF/PF）
- RSP：栈指针（指向当前栈帧顶部）
- RBP：帧指针（可选，现代编译器用 RBX + 栈帧）

**XMM 寄存器（浮点/SIMD）：**
- XMM0–XMM7：参数传递（System V ABI）、返回值（浮点）
- XMM8–XMM15：额外参数
- YMM/ZMM：AVX/AVX-512 扩展（256/512-bit）

### 数据移动指令

```asm
movq src, dst      ; 移动 64 位值（movl = 32 位，movw = 16 位，movb = 8 位）
movzbl src, dst    ; 移动并零扩展（z = zero-extend）
movsbl src, dst    ; 移动并符号扩展（s = sign-extend）
lea src, dst       ; Load Effective Address（计算地址但不访问内存）
pushq src          ; rsp -= 8; *rsp = src
popq dst          ; dst = *rsp; rsp += 8
```

### 算术与逻辑指令

```asm
addq src, dst      ; dst += src
subq src, dst      ; dst -= src
imulq src, dst     ; 有符号乘法（rdx:rax = rax * src）
mulq src           ; 无符号乘法
incq dst           ; dst++
decq dst           ; dst--
negq dst           ; dst = -dst
andq src, dst      ; dst &= src
orq src, dst       ; dst |= src
xorq src, dst      ; dst ^= src
notq dst           ; dst = ~dst
salq src, dst      ; 左移（算术/逻辑同义）
sarq src, dst      ; 算术右移（保留符号位）
shrq src, dst      ; 逻辑右移（高位补 0）
```

### 控制流：条件跳转

```asm
cmpq src2, src1    ; 设置 EFLAGS（计算 src1 - src2，不存储结果）
testq src2, src1   ; 设置 EFLAGS（计算 src1 & src2，不存储结果）

je/jz  label       ; ZF=1 时跳转（相等/为零）
jne/jnz label      ; ZF=0 时跳转（不相等/非零）
jg/jnle label      ; SF=OF 且 ZF=0（有符号 >）
jge/jnl label      ; SF=OF（有符号 >=）
jl/jnge label      ; SF≠OF（有符号 <）
jle/jng label      ; SF≠OF 或 ZF=1（有符号 <=）
ja/jnbe label      ; CF=0 且 ZF=0（无符号 >）
jb/jnae label      ; CF=1（无符号 <）
```

**条件传送（避免分支预测失败）：**
```asm
cmove src, dst     ; ZF=1 时执行 mov（条件传送）
cmovne src, dst    ; ZF=0 时执行 mov
```

### 函数调用约定 (System V AMD64 ABI)

**参数传递顺序：** rdi, rsi, rdx, rcx, r8, r9, 然后栈（从右到左压栈）
**返回值：** rax（整数/指针），rdx:rax（128-bit），xmm0（浮点）
**Callee-saved（被调用者保存）：** rbx, rbp, r12, r13, r14, r15, rsp
**Caller-saved（调用者保存）：** rax, rcx, rdx, rsi, rdi, r8-r11

**栈帧布局：**
```
 rsp+0x00  ← 当前 rsp
           ← 函数 prologue: pushq %rbp; movq %rsp, %rbp
           ← 本地变量
           ← 保存的 callee-saved 寄存器
           ← 函数参数（大于 6 个时）
 rsp-0x08  ← 返回地址（call 自动 push）
 rbp        ← 保存的 rbp（call 自动 push）
```

### CISC 特性：复杂寻址模式

```asm
movq (%rdi, %rsi, 4), %rax   ; rax = *(rdi + rsi*4)  [数组下标]
lea 0x10(%rdi), %rax         ; rax = rdi + 0x10       [地址计算]
```

### 循环与数组

```asm
; sum = 0; for (i=0; i<n; i++) sum += a[i];
    xorq %rax, %rax           ; sum = 0（用 rax 存 sum）
    xorl %ecx, %ecx           ; i = 0（用 rcx 存 i）
.Lloop:
    cmpq %rsi, %rcx           ; 比较 i 和 n
    jge .Lend                 ; if (i >= n) goto .Lend
    addq (%rdi,%rcx,8), %rax  ; sum += a[i]（8字节元素）
    incq %rcx                 ; i++
    jmp .Lloop
.Lend:
```

### 浮点编程

```asm
vaddsd %xmm1, %xmm0, %xmm2   ; 标量双精度加法（scalar double）
vmulss %xmm1, %xmm0, %xmm2   ; 标量单精度乘法（scalar single）
vmovsd 8(%rsp), %xmm0         ; 从内存加载 double 到 xmm0
vcvttsd2sil %xmm0, %eax      ; double → int（截断）
```

### 栈帧与函数 prologue/epilogue

**典型函数 prologue：**
```asm
pushq %rbp
movq %rsp, %rbp
subq $0x20, %rsp    ; 分配本地变量空间（栈对齐到 16 字节）
```

**典型函数 epilogue：**
```asm
leave                ; movq %rbp, %rsp; popq %rbp
ret
```

### 安全相关的机器码知识

**返回导向编程 (ROP)：**
- 攻击者利用程序中的 gadget（ret 结尾的短序列）拼接攻击链
- 防御：ASLR（地址空间布局随机化）、栈金丝雀（stack canary，-fstack-protector）

**Spectre/Meltdown：**
- 投机执行（speculative execution）导致缓存侧信道
- 防御：IBRS、STIBP、Speculative Store Bypass Disable

## 相关概念

- [[sys-prog-index]] — 系统编程
- [[os-index]] — 操作系统基础
- Memory Hierarchy — 内存层级与缓存
- [[entities/linux/process-management-model]] — 进程管理
- [[sources/notes-os]] — Linux 内核（VFS/调度器/SLUB）
- [[qemu-index]] — QEMU 模拟（可动态观察机器码执行）

## 来源详情

- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP Ch3 机器码表示，Ch5 性能优化
- [[sources/pdf-the-linux-programming-interface]] — TLPI Appendix A 系统调用追踪
