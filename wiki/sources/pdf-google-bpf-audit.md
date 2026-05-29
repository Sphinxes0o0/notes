---
type: source
source-type: pdf
title: Stories from BPF Security Auditing at Google (Brendan Jackman)
author: Brendan Jackman
date: 2021
size: medium
path: raw/PDFs/papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf
summary: Google Brendan Jackman：KRSI BPF LSM安全遥测、BPF Atomics原子操作、Ringbuf promise机制、跨内核版本CO-RE兼容性
tags: [security, ebpf, google, krsi, lsm, atomics, ringbuf, bpf]
created: 2021
---
# Stories from BPF Security Auditing at Google

## 核心内容

**Author:** Brendan Jackman (Google) | 2021

### 背景：为什么 Google 需要 BPF 安全审计

- **Audit 日志不灵活** — 传统 auditd 输出格式固定，难以自定义字段
- **内核模块难维护** — 每次内核升级需重编，安全风险高
- **eBPF 的出现** — 沙盒 VM + Verifier + LSM hook = 理想安全遥测方案

### KRSI (Kernel Runtime Security Instrumentation)

**Google 的 BPF LSM 安全遥测方案：**

1. **LSM hook 作为安全 API** — Linux 内核的 LSM（Linux Security Module）本为强制访问控制设计，但 hook 点提供了丰富的安全语义信息
2. **BPF 程序附加到 LSM hook** — 获取语义化安全事件（不只是原始 syscall）
3. **遥测数据上报** — Ringbuf 传递事件到用户态处理

**LSM hook 覆盖范围：**
```
security_bprm_check       — 程序加载检查
security_file_open        — 文件打开检查
security_socket_bind     — Socket 绑定检查
security_socket_connect  — Socket 连接检查
security_inode_setattr    — 文件属性设置
security_mmap_file        — 内存映射检查
```

### BPF Atomics（原子操作）

**问题：** BPF 程序并发执行时，如何生成全局唯一整数（如 trace ID）？

**解决方案：** BPF 指令集新增原子操作码：

```
BPF_STX | BPF_ATOMIC | BPF_DW    — 64-bit 原子存储
+ BPF_XOR | BPF_FETCH            — fetch_xor 原子 XOR
+ BPF_ADD | BPF_FETCH            — fetch_add 原子加
```

这些原子操作让 BPF 程序可以安全地在多核间共享计数器/ID 生成器。

### BPF Ringbuf 深入

**vs Perf Buffer：**

| 特性 | Perf Buffer | Ringbuf |
|------|------------|---------|
| 数据结构 | 全局共享 | per-CPU |
| 数据重排 | 需用户态处理 | 内核保证 |
| 内存效率 | 中等 | 高 |
| 满载行为 | 丢失事件 | 丢新保旧 |

**Promise 机制：**
- 避免 ringbuf 满时全部数据丢失
- 部分数据 deferred 输出，优先保证已提交数据

**Chunking：**
- 大数据（堆栈trace、字符串）分块存储
- 避免一次性分配"最大可能大小"导致内存浪费

### CO-RE 跨内核版本兼容性

```c
// 检测字段是否存在
if (bpf_core_field_exists(task->real_parent))
    parent_pid = BPF_CORE_READ(task, real_parent, pid);

// 线性 fallback 策略
// 最广泛支持的 prog 版本 → 功能最完整的版本
```

**bpf_core_read 宏族：**
- `BPF_CORE_READ()` — 安全读取嵌套字段
- `BPF_CORE_READ_INTO()` — 读取到预分配 buffer
- `BPF_PROBE_READ()` — 兼容旧内核的宏

## 关键引用

> "LSM provides a semantic internal API for security information — designed for enforcement, but we use it for audit."

> "BPF atomics enable safe concurrent access to shared counters from multiple BPF programs."

## 相关页面

- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控与 Rootkit
- [[entities/linux/security/linux-security-observability-ebpf]] — eBPF 安全可观测性
- [[entities/linux/kernel/index]] — Linux 内核子系统
- [[sources/pdf-ebpf-papers]] — eBPF 论文集（含本篇）
- [[ebpf-index]] — eBPF 模块索引
