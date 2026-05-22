---

type: entity
tags: [系统编程, Linux, IPC, ELF]
created: 2026-05-20


sources: [notes-ccpp]---

# 系统编程（System Programming）

系统编程涉及操作系统底层机制的学习与实践，包括进程间通信、文件格式、系统调用等核心概念。

## 定义

系统编程是在操作系统层面上进行软件开发的技术，关注进程管理、内存管理、文件 I/O、网络通信等底层机制，目的是充分利用操作系统提供的能力。

## 关键要点

### ELF 文件格式

ELF（Executable and Linkable Format）是 Linux 下可执行文件、目标代码、共享库的标准格式。

**文件结构**：
- **ELF Header**：文件类型（.o, exec, .so）、机器类型、入口点地址
- **Program Header Table**：运行时所需的内存段信息
- **Section Header Table**：链接和重定位所需的数据

**关键 Sections**：

| Section | 用途 |
|---------|------|
| `.text` | 编译后的机器代码 |
| `.rodata` | 只读数据（常量） |
| `.data` | 已初始化的全局变量 |
| `.bss` | 未初始化的全局变量（不占磁盘空间） |
| `.symtab` | 符号表（函数名、变量名） |
| `.rel.text/.rel.data` | 重定位信息 |
| `.debug` | 调试符号表 |

**编译流程**：源代码 → 预处理(.i) → 汇编(.s) → 目标代码(.o) → 链接 → 可执行文件

**工具链**：readelf（查看 ELF）、objdump（反汇编）、nm（符号表）、strings（字符串）、ldd（库依赖）

### Linux 进程间通信（IPC）

**同一主机**：
- **管道**：匿名管道（亲缘进程）、具名管道/FIFO（无亲缘关系）
- **内存映射（mmap）**：磁盘文件映射到内存，实现进程间通信
- **信号**：异步事件通知机制，5 种默认动作：Term/Ign/Core/Stop/Cont
- **消息队列**：POSIX/System V
- **共享内存**：最高效的 IPC 方式
- **信号量**：进程同步

**网络**：Socket

**管道特点**：
- 字节流，无消息边界
- 单向传递（半双工）
- 读：管道有数据返回实际字节数；无数据且写端关闭返回 0；无数据且写端未关闭则阻塞
- 写：读端全部关闭则收到 SIGPIPE；管道满则阻塞

**mmap 特点**：
- `MAP_SHARED`：修改同步到磁盘，进程间通信必须
- `MAP_PRIVATE`：修改不同步到原文件
- 偏移量必须是 4K 的整数倍
- 文件大小不能为 0
- mmap 后关闭 fd 不影响映射

### 设计模式

**单例模式（Singleton）**：确保类只有一个实例，提供全局访问点。实现方式包括饿汉式、懒汉式（双检锁）、Meyer's Singleton。

## 相关概念

- [[entities/cpp]] — C/C++ 语言基础
- entities/linux — Linux 内核与系统调用
- [[entities/security]] — 安全工具（Masscan 等）

## 来源详情

- github-notes-sys — 系统编程笔记（ELF 格式、Linux IPC、设计模式）
