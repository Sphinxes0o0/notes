---
type: source
source-type: pdf
title: "Computer Systems: A Programmer's Perspective"
author: "Randal E. Bryant, David R. O'Hallaron"
date: 2015
size: large
path: raw/PDFs/books/computer_systems_a_programmers_perspective.pdf
summary: "CMU 15-213 教材，1078页，计算机系统百科：数据表示/机器码/处理器/优化/内存层级/链接/异常控制流/虚拟内存/并发，Bryant & O'Hallaron 经典著作"
tags: [computer-systems, computer-architecture, memory-hierarchy, machine-code, books]
created: 2026-05-25
sources: []
---

# Computer Systems: A Programmer's Perspective (CS:APP)

## Core Content

### Overview

Carnegie Mellon University 15-213 "Intro to Computer Systems" 教材，Bryant & O'Hallaron 著（2017 ACM Turing Award 合著）。从程序员视角理解计算机系统，强调性能优化和系统级思考。

**统计：**
- 1078 页
- 12 章
- Part I: 程序表示与执行
- Part II: 在系统上运行程序
- Part III: 程序间交互与通信

---

### Chapter 1: A Tour of Computer Systems

引导章节，通过 `hello world` 程序的生命周期介绍全书主题：

- 源代码 → 预处理器 → 编译器 → 汇编器 → 链接器 → 可执行文件
- CPU 的指令执行模型：PC 寄存器、指令读取、解码、执行
- 存储层次：寄存器 → L1/L2/L3 Cache → 主存 → 磁盘
- 操作系统抽象：进程（虚拟地址空间）、文件（I/O 设备抽象）、虚拟机
- 并发与并行：线程级并行、数据级并行、指令级并行

---

### Chapter 2: Representing and Manipulating Information

**Data Representations:**
- 字节序：little-endian（x86）vs big-endian（网络字节序），字节序转换
- 有符号数：二补码（two's complement）编码，符号扩展，截断
- 整数运算：溢出、乘法（移位实现）、除法（向零舍入）
- 浮点数：IEEE 754 单精度/双精度，规格化/非规格化数，NaN/无穷

**Bit-Level Operations:**
- 位运算符：&, |, ^, ~，掩码技术
- 逻辑运算：&&, ||, !（注意短路求值）
- 移位运算：左移、无符号右移（逻辑）、有符号右移（算术）

---

### Chapter 3: Machine-Level Representation of Programs

**x86-64 Architecture:**
- 寄存器：rax/rcx/rdx/rbx/rbp/rsp/rsi/rdi + r8–r15，64位扩展
- 指令格式：REX 前缀 + opcode + ModR/M + SIB + displacement + immediate
- 数据移动：mov/movz/movs，地址计算 lea
- 算术逻辑：add/sub/imul/and/or/xor/shift/lea

**Control Flow:**
- 条件码：CF/ZF/SF/OF，cmp/test 指令
- 跳转：jmp/je/jne/jg/jl 等，PC-relative 跳转目标
- 条件移动：cmove/cmovne，替代分支预测失败的分支

**Procedures:**
- 栈帧：rsp/rbp，call/ret，push/pop
- 参数传递：rdi/rsi/rdx/rcx/r8/r9（System V AMD64 ABI）
- 寄存器保存：caller-saved vs callee-saved

**Arrays & Structures:**
- 连续内存布局，结构体字节对齐
- 浮点寄存器：XMM0-XMM15，YMM/ZMM 扩展

---

### Chapter 4: Processor Architecture

**Y86-64 ISA:**
- 简化教学指令集：rrmovl, irmovl, rmmovl, mrmovl, addl, subl, etc.
- 程序员可见状态：PC、条件码、寄存器、内存

**Single-Cycle Datapath:**
- 组合逻辑 + 时序存储（寄存器/内存）
- 每条指令一个时钟周期
- 状态寄存器更新

**Pipelining:**
- 五级流水线：Fetch → Decode → Execute → Memory → Writeback
- 数据冒险：转发（forwarding）vs 停顿（stalling）
- 加载/使用数据冒险：流水线停顿一个周期
- 控制冒险：分支预测（BTB），PC-relative

**Pipeline Hazards:**
- 结构冒险（structure hazards）、数据冒险（data hazards）、控制冒险（control hazards）
- 气泡（bubble）插入

---

### Chapter 5: Optimizing Program Performance

**Compiler Optimizations:**
- 循环不变代码外提（loop-invariant code motion）
- 减少过程调用（procedure inlining）
- 寄存器分配优化

**现代 CPU 超标量:**
- Issue width：每个周期发射多条指令
- Out-of-order execution：寄存器重命名，重排缓冲区（ROB）
- Retirement：指令完成顺序提交

**Cache Effects:**
- 内存山（memory mountain）：时间局部性 + 空间局部性
- 缓存友好代码：数据布局对齐、遍历顺序
- 分块（blocking/tiling）优化矩阵乘法

**Amdahl's Law:**
- Speedup = 1 / (F + (1-F)/N)
- 并行化收益受串行部分限制

**Performance Measurement:**
- 周期计数：perf counter, gprof
- Roofline 模型：计算密度 vs 内存带宽

---

### Chapter 6: The Memory Hierarchy

**Storage Technologies:**
- SRAM vs DRAM：6T vs 1T1C 单元，访问延迟（SRAM ~1ns, DRAM ~100ns）
- 磁盘：旋转延迟 + 寻道时间 + 传输延迟，磁盘缓存
- SSD：NAND Flash，erase/write cycles，FTL（Flash Translation Layer）

**Locality Principle:**
- 时间局部性（temporal）：最近访问的地址倾向于再次访问
- 空间局部性（spatial）：相邻地址倾向于一起访问

**Cache Memory:**
- 缓存结构：S sets × E lines × B bytes/line
- 直接映射（E=1）、组相联（E>1）、全相联（只有一个 set）
- 缓存查找：Tag/Index/Offset 比较
- 替换策略：LRU、FIFO、随机
- 写策略：write-through vs write-back，write-allocate vs no-write-allocate

**Cache Hierarchy in Modern CPUs:**
- L1 dcache/icache：~32KB，4-cycle latency
- L2 unified cache：~256KB，~12-cycle latency
- L3 cache：~8MB，~30-50 cycle latency

**Virtual Memory:**
- 页表（PTE）、页表缓存（TLB）、多级页表
- 地址翻译：VPN → PTE → PFN → physical address
- 页替换：OPT(optimal), LRU, FIFO, CLOCK（Second Chance）

---

### Chapter 7: Linking

**Static Linking:**
- 链接器任务：符号解析（symbol resolution）、重定位（relocation）
- 对象文件格式：ELF（Executable and Linkable Format）

**Relocatable Object Files:**
- .text（代码）、.data（已初始化全局变量）、.bss（未初始化）
- .symtab（符号表）、.rel.text（代码重定位表）、.rel.data（数据重定位表）
- .strtab（字符串表）

**Symbol Resolution:**
- 全局符号（.text/.bss）：强符号 vs 弱符号
- 多重定义强符号：错误
- 引用弱符号使用全局符号

**Loading Executable Files:**
- ELF 头、程序头、段（segment）
- 加载地址 = 链接时地址 + relocations
- ASLR（Address Space Layout Randomization）

**Shared Libraries / Dynamic Linking:**
- .so（Linux）/ .dylib（macOS）
- 延迟绑定：GOT（Global Offset Table）+ PLT（Procedure Linkage Table）
- 运行时加载：dlopen/dlsym（Linux）

---

### Chapter 8: Exceptional Control Flow (ECF)

**Exceptions:**
- 硬件异常：除零、页Fault、非法指令
- 陷阱（trap）：系统调用（_SYSCALL）、断点
- 故障（fault）：可恢复（页Fault），不可恢复（除零）
- 中止（abort）：不可恢复硬件错误

**Processes:**
- 进程 = 运行中的程序实例
- 上下文切换：内核态切换，用户态到用户态
- 进程控制：fork()/execve()/wait()/exit()

**System Calls and Library Functions:**
- C 标准库封装系统调用：printf → write()，malloc() → brk()/mmap()

**Signals:**
- 软件异常：SIGTERM/SIGCHLD/SIGSEGV 等
- signal handler：异步执行的函数
- pending signal vs blocked signal
- sigprocmask() 阻塞/解除阻塞

**Nonlocal Jumps:**
- setjmp()/longjmp()：跨函数跳转，突破栈 unwind
- C++ 异常实现机制

**Process Control:**
- wait()/waitpid()：回收子进程
- 僵死进程（zombie）
- execve()：替换当前进程映像

---

### Chapter 9: Virtual Memory

**Physical vs Virtual Addressing:**
- 物理地址（PA）：CPU 直接访问物理内存
- 虚拟地址（VA）：进程的独立地址空间

**VM as a Tool for Memory Management:**
- 每个进程有独立页表，隔离地址空间
- 简化链接：每个进程的虚拟地址布局一致
- 简化分配：malloc() 返回任意地址，页表自动处理映射

**VM as a Tool for Cache:**
- 磁盘作为主存的后备存储（swap space）
- 页缓存命中/缺失 → 磁盘 I/O

**Address Translation:**
- 页表基址寄存器（PTBR）
- TLB 加速翻译
- 多级页表：PTE 只在有效时分配，节省内存

**Linux Virtual Memory System:**
- 虚拟地址区域（VMA）：vm_area_struct
- 进程地址布局：text → rodata → data → bss → heap → shared libraries → stack → kernel
- mmap()/munmap() 系统调用
- 页fault处理：do_page_fault() → VM_FAULT_* 返回值

**Memory Mapping:**
- mmap() 创建匿名映射（用于 malloc）vs 文件映射
- 私有映射 vs 共享映射

---

### Chapter 10: System-Level I/O

**Unix I/O:**
- 所有 I/O 设备建模为文件：open/read/write/close
- 文件描述符（小整数）、stdin/stdout/stderr

**Files:**
- inode：元数据（大小/权限/时间戳）
- 硬链接 vs 符号链接
- 目录操作：opendir/readdir/closedir

**I/O Redirection:**
- dup2() 复制文件描述符
- shell 的 > 和 | 重定向原理

**Standard I/O:**
- FILE* 流，stdio 库（fopen/fread/fprintf）
- 用户态缓冲：全缓冲/行缓冲/无缓冲

**Robust I/O — Rio Package:**
- Rio_readn/Rio_writen：无短读/短写的完整传输
- Rio_readlineb：带缓存的行读取

---

### Chapter 11: Network Programming

**Client-Server Model:**
- 每个网络应用 = 客户端 + 服务器端
- 服务器：listen socket + accept loop

**Networks:**
- TCP/IP 协议栈：应用层 → 传输层（TCP/UDP）→ 网络层（IP）→ 链路层（Ethernet）

**HTTP:**
- GET/POST 请求，状态码（200/404/500）
- 持久连接（Keep-Alive）vs 非持久连接

**Tiny Web Server (code in book):**
- Tiny：单线程迭代服务器，处理静态内容
- CGI 机制：fork() + execve() 生成动态内容

---

### Chapter 12: Concurrent Programming

**Process-Based Concurrency:**
- fork() 创建并发服务器
- 进程间共享：文件描述符、共享内存（需 mmap）

**I/O Multiplexing:**
- select()：监控多个文件描述符的就绪状态
- poll()：类似 select，但接口更一致
- select/poll 的缺点：线性扫描，fd 数量限制

**Thread-Based Concurrency:**
- 线程：共享进程的虚拟地址空间
- 线程创建：pthread_create()
- 线程join：pthread_join()

**Shared Variables and Threads:**
- 线程安全函数 vs 可重入函数
- 竞争条件（race condition）：多个线程并发访问共享变量
- 死锁（deadlock）：循环等待资源

**Semaphores:**
- P()（wait）/ V()（signal）操作
- 互斥锁（binary semaphore）和信号量（counting semaphore）
- 解决生产者-消费者问题、读者-写者问题

**Mutex and Condition Variables:**
- pthread_mutex_lock/unlock
- pthread_cond_wait/signal：Mesa 管语义

**Threaded Echo Server:**
- 线程池并发模型

---

## Key Quotes

- "Our aim is to explain the enduring concepts underlying all computer systems, and to show you the concrete ways that these ideas affect the correctness, performance, and utility of your application programs." — Bryant & O'Hallaron
- "Understanding how compilation systems work is an intellectual achievement that pays off immediately in practical ways." — CS:APP Ch1

## Related Pages

- [[os-index]] — Operating system fundamentals
- Machine Code — Machine code and assembly
- Memory Hierarchy — Memory hierarchy and cache
- Virtual Memory — Virtual memory systems
- [[sys-prog-index]] — System programming navigation
- [[sources/notes-os-fundamentals]] — OS fundamentals synthesis
