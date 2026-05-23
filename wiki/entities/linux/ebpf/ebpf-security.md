---
type: entity
tags: [linux, ebpf, security, falco, auditing, rootkit, lsm]
created: 2026-05-22
sources: [pdf-ebpf-books, pdf-ebpf-papers]
---

# eBPF Security

## 定义

eBPF 在安全领域有两面性：**防御侧** — 通过 Falco、KRSI、LSM 等实现运行时安全监控和策略强制；**攻击侧** — rootkit 可利用 eBPF 实现隐蔽的数据包篡改、系统调用拦截和进程隐藏。eBPF 的安全价值在于以零侵入方式在内核关键路径提供细粒度可观测性。

## 防御侧：安全监控

### Falco (Apple)

Falco 是 CNCF 毕业项目，通过 eBPF probe 监控容器和宿主机的异常行为。

**为什么选择 eBPF（而非内核模块）：**
- 有限的内核访问权限 — 不像内核模块拥有完整内核权限，BPF 程序受限
- 去除对外部框架和大型模块的依赖
- 可通过标准内核工具（bpftool）查看/调试/分析
- CO-RE 支持跨内核版本兼容，减少部署复杂度

**Falco BPF 监控的 Syscall 类别（高价值系统调用）：**
- 文件操作：`open`, `openat`, `creat`, `read`, `write`, `chmod`, `rename`, `unlink`
- 进程操作：`execve`, `ptrace`
- 网络操作：`connect`, `sendto`, `bind`, `listen`, `accept`
- 权限操作：`setuid`, `setns`, `unshare`
- 系统控制：`capset`, `mkdir`, `symlink`

**Falco 告警规则示例：**
- 本地文件包含 (LFI) — `open` 读取敏感文件
- 反向 shell — `execve` + `connect` + `dup` 组合
- 权限提升 — `sudo` 配置错误
- 可疑网络活动 — 系统进程的网络连接

**Apple 内部生产流水线：**
1. 针对所有内部内核预构建 Falco probes (`.o` 文件)，打包发布
2. Falco release 包含 probes + 用户态二进制
3. 自定义 Falco rules 支持内部策略

### Google KRSI (Kernel Runtime Security Instrumentation)

Google 的 KRSI 项目：
- **起因**：Audit 日志不够灵活，内核模块难以维护
- **方案**：BPF LSM — 在 LSM hook 点附加 BPF 程序
- LSM 提供语义化内部 API（安全信息接口），设计用于强制执行，Google 将其用于审计

### BPF LSM

LSM (Linux Security Modules) 在内核安全关键路径预置 hook 点（如 `security_file_open`、`security_bprm_check`），安全模块可自由加载/卸载。

eBPF LSM 优势：
- 无需编写内核模块，动态加载 BPF 程序
- BPF Verifier 保证程序安全性
- 通过 CO-RE 跨内核版本可移植

### BPF Atomics (Google 贡献)

解决 BPF 程序并发场景下生成全局唯一整数的需求：
- `BPF_ATOMIC` 操作码：`BPF_ADD | BPF_FETCH`、`BPF_XOR | BPF_FETCH` 等
- 替代方案：per-CPU arrays、`bpf_spin_lock`

### BPF Ringbuf vs Perf Buffer

| 特性 | Perf Buffer | BPF Ringbuf |
|------|-------------|-------------|
| 内存模型 | 每 CPU 一个 ring | 全局单一 ring（lock-free） |
| 内存效率 | 浅（per-CPU） | 深（全局共享） |
| 数据重排 | 不保证顺序 | 保证顺序（跨 CPU） |
| 大数据 | 每个事件独立 buffer | chunking 机制（固定大小 chunk 拼合成大数据） |

Ringbuf promise 系统：部分数据可 deferred 输出，避免 ringbuf 满时丢失整个事件。

## 攻击侧：eBPF Rootkit

### 威胁模型

eBPF rootkit 利用 eBPF 实现**内核级**攻击，且无需加载内核模块（需 CAP_BPF 或 root 权限）：

**网络欺骗：**
- 在防火墙之前读写/修改/丢弃/重定向数据包
- 篡改源 IP/Port，克隆包创建新流量
- Hook `bpf_skb_store_bytes` 可修改任意用户态 buffer

**数据篡改：**
- `bpf_probe_write_user`：覆写任意用户态内存（如伪造 `pam.d` 文件绕过 MFA）
- `fmod_ret` 程序可覆盖任意系统调用的返回值
- `bpf_send_signal`：向当前线程发送信号（`SIGKILL` 不可阻挡）

**进程隐藏：**
- 文件/进程隐藏（通过 hook `execve`/`openat` 系统调用）
- 隐蔽 C2 通信（正常 netstat/tcpdump 看不到）

### Rootkit 检测

**文件检测：**
- 查找包含 eBPF 程序的 ELF 文件（LLVM+LibBPF 编译特征：`__bio_bpf_desc` 等 section 名）
- bpftool 检查已加载的 BPF 程序和 Maps
- 监控 `/sys/fs/bpf/` 伪文件系统的异常 pinning

**行为检测：**
- `bpf_probe_write_user` 被内核告警（高危操作）
- 异常系统调用 + 网络活动的组合模式

### 防御措施

- `kernel.unprivileged_bpf_disabled=1` — 禁止非 root 用户加载 BPF 程序
- `kernel.bpf.stats_enabled=1` — 启用 BPF 统计（bpftool 可观测）
- seccomp + CAP_BPF 最小权限原则

## 相关概念

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构（Verifier/JIT/Maps）
- [[entities/linux/ebpf/ebpf-xdp]] — XDP 网络处理（数据包层安全）
- [[kernel-subsystems-index]] — Linux 内核安全子系统（crypto/LSM/seccomp）
- [[sources/notes-security]] — 安全工具（Masscan/Falco/Snort）

## 来源详情

- [[sources/pdf-ebpf-papers]] — Think eBPF for Kernel Security Monitoring (Apple Falco, eBPF Summit 2021)
- [[sources/pdf-ebpf-papers]] — Stories from BPF Security Auditing at Google (Brendan Jackman)
- [[sources/pdf-ebpf-papers]] — Creating and Countering the Next Generation of Linux Rootkits using eBPF (Pat Hogan, Black Hat)
- [[sources/pdf-ebpf-papers]] — Secure Namespaced Kernel Audit for Containers (saBPF, SoCC 2021)
- [[sources/pdf-ebpf-papers]] — Security Observability with eBPF (O'Reilly 2022)
- [[sources/pdf-ptp-security]] — PTPsec: PTP Time Delay Attack Detection (INFOCOM 2024)
