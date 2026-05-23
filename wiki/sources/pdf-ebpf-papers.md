---
type: source
created: 2026-05-22
source-type: pdf
title: "eBPF Papers (9篇)"
author: "Thomas Graf, Pat Hogan, Brendan Jackman, Eric Sage & Melissa Kilby, Kyle Quest, Marcos A. M. Vieira, Soo Yee Lim, Jed Salazar & Natalia Reka Ivanko"
date: 2026-05-22
updated: 2026-05-23
size: medium
path: raw/PDFs/papers/bpf-rethinkingthelinuxkernel-200303183208.pdf, raw/PDFs/papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf, raw/PDFs/papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf, raw/PDFs/papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf, raw/PDFs/papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf, raw/PDFs/papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf, raw/PDFs/papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf, raw/PDFs/papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf, raw/PDFs/papers/isovalent_security_observability.pdf
tags: [ebpf, linux-kernel, papers]
---

# eBPF Papers (9篇)

## 核心内容

### 1. Rethinking the Linux Kernel (Thomas Graf, 2020)

Cilium 创始人 Thomas Graf 的里程碑演讲，提出 eBPF 将 Linux 内核转变为"微内核 + 可组合服务层"的愿景。

**核心论点：**
- Linux 内核的分层抽象（TCP/IP/VFS/Netdevice）让每层都付出上下层开销，难以绕过
- 20 年历史的 iptables/seccomp/tc/ovsctl 等独立 API 造成碎片化
- 内核不知道容器/Pod/API 调用关系——只知道 namespace/cgroup

**eBPF 作为解决方案：**
- 沙盒虚拟机 + Verifier 安全性 + JIT 性能 = 内核可编程性
- 100% 模块化和可组合，新增功能可快速迭代（无需等待内核上游）
- Cilium 让 Linux 内核感知 Kubernetes Pod 和服务身份

**eBPF Map 类型一览：** Hash、Array、LRU、Ring Buffer、Stack Trace、LPM

**生态项目：** Katran (Facebook L4 LB)、bcc/bpftrace (追踪)、Falco (安全)、Cilium (K8s网络)

### 2. BPF: Turning Linux into a Microservices-aware OS (Thomas Graf)

同一主题的扩展版，增加 Cilium 深度解析。

**Hubble 可观测性：** 基于 eBPF 的 Kubernetes 网络可视化
```bash
hubble observe --since 1m -t l7 -j \
  | jq 'select(.l7.dns.rcode==3) | .destination.namespace + "/" + .destination.pod_name'
```

**Cilium 功能矩阵：**
- 容器网络：CN I/路由/Overlay/IPv6/NAT46/多集群
- Service LB：L3-L4，可扩展kube-proxy
- 安全：Identity-based L3-L4 + API-aware (HTTP/gRPC/Kafka)
- Servicemesh加速：Envoy sidecar vs BPF~3.5x

### 3. Creating and Countering the Next Generation of Linux Rootkits using eBPF (Pat Hogan, Black Hat)

eBPF 双刃剑的攻防分析。

**Rootkit 攻击向量：**
- 网络欺骗：防火墙前读写包、篡改IP/Port、克隆流量
- 数据篡改：`bpf_probe_write_user` 覆写用户态内存、`fmod_ret` 覆盖 syscall 返回值
- 进程隐藏：`execve`/`openat` hook 隐藏文件和进程
- Uprobe Hook OpenSSL：读写 TLS 加密流量

**防御检测手段：**
- 文件特征：`__bio_bpf_desc` 等 ELF section（LibBPF 编译产物）
- bpftool 检查已加载程序
- 内核告警：`bpf_probe_write_user` 使用时内核会发出警告

### 4. Fast-Packet-Processing using eBPF and XDP (Marcos A. M. Vieira, UFMG)

XDP 高速数据包处理的技术细节。

**BPF 指令格式：**
- 7 类指令：LD/LDX/ST/STX/ALU/ALU64/JMP
- 64-bit 2-operand 格式：opcode(8) + dst_reg:4 + src_reg:4 + off:16 + imm:32
- 11 个 64-bit 寄存器：R0=返回值，R1-R5=参数，R6-R9=callee-saved，R10=栈指针

**XDP 性能数据：**
- XDP ~20 Mpps vs TC ~5 Mpps vs Netfilter ~1 Mpps
- 云厂商案例：Cloudflare 用 XDP 处理 3Mpps+ DDoS（iptables 仅 1Mpps）

**XDP 完整示例：** C代码 → Clang编译 → BPF字节码 → `ip link set dev eth0 xdp obj prog.o`

### 5. Stories from BPF Security Auditing at Google (Brendan Jackman)

Google 内部 BPF 安全审计经验。

**KRSI (Kernel Runtime Security Instrumentation)：**
- 背景：Audit 日志不灵活，内核模块难维护
- 方案：BPF LSM，在 LSM hook 点附加 BPF 程序获取语义化安全信息

**BPF Atomics：**
- 问题：BPF 程序并发执行时如何生成全局唯一整数？
- 解决方案：`BPF_STX | BPF_ATOMIC | BPF_DW` + `BPF_XOR | BPF_FETCH` 等原子操作码

**BPF Ringbuf：**
- vs Perf Buffer：全局共享 vs per-CPU，数据重排保证
- promise 系统：部分数据 deferred 输出，避免 ringbuf 满时全丢
- chunking：大数据分固定大小 chunk，避免分配最大可能大小

**跨内核版本兼容性：**
- `bpf_core_field_exists()` 检测字段是否存在
- 线性 fallback：最广泛支持的 prog 版本 → 最完整版本

### 6. Think eBPF for Kernel Security Monitoring (Apple/Falco, eBPF Summit 2021)

Apple 选择 BPF 而非内核模块的核心理由。

**BPF 优势 vs Kernel Module：**
- 有限权限（vs 内核模块全权限）
- 去除外部框架依赖
- bpftool 统一调试工具
- CO-RE 跨内核版本兼容

**高价值 Syscall 监控列表：**
文件：`open/creat/read/write/chmod/rename/unlink`；进程：`execve/ptrace`；网络：`connect/sendto/bind/listen/accept`；权限：`setuid/setns/unshare`

**Apple 生产流水线：** 预构建 Falco probes (`.o`) → libs release → Falco release + 自定义 rules

### 7. eBPF Library Ecosystem Overview in Go Rust Python C and More (Kyle Quest)

生态库全景评测。

**库分类：**

| 语言 | 库 | 定位 |
|------|-----|------|
| C | BCC | 追踪工具箱，最流行 |
| C | libbpf | 官方，低层次，CO-RE |
| Go | iovisor/gobpf | BCC wrapper |
| Go | **cilium/ebpf** | Pure Go，主流 |
| Go | dropbox/goebpf | 纯Go，专注网络 |
| Go | aquasecurity/libbpfgo | libbpf wrapper |
| Python | bcc | BCC wrapper，最广泛 |
| Rust | libbpf-rs / **aya** | Rust生态 |
| Other | Lua/Node.js/Ruby | 脚本语言绑定 |

**Verdict：** BCC（功能优先）vs libbpf（官方/轻量）vs cilium/ebpf（Go生态首选）

### 8. Secure Namespaced Kernel Audit for Containers (saBPF, Soo Yee Lim, SoCC 2021)

saBPF 是 eBPF 框架的安全审计扩展，实现容器粒度的内核审计。

**核心架构：**
- 在 LSM hook 点附加 eBPF 程序，基于 cgroup 实现容器级隔离
- 每个容器可自定义审计策略和机制，同主机不同容器互不影响
- 扩展 Linux 的 eBPF 框架以支持 reference monitor 与 namespace 的交集

**安全保证：**
- 高保真审计数据：完整记录容器触发的系统活动
- 无并发漏洞：LSM 的 reference-monitor 设计确保内核状态不可变
- 无记录缺失：避免传统 audit 工具的 TOCTTOU 攻击漏洞

**Kubernetes 集成：**
- Sidecar 设计模式：每个 pod 配置 saBPF 捕获审计日志
- Sidecar 容器分析日志并发送可疑事件到远程关联系统
- 实现入侵检测系统和轻量级访问控制机制

**性能对比：** saBPF 性能与直接在内核中实现的审计系统相当

### 9. Security Observability with eBPF (Jed Salazar & Natalia Reka Ivanko, O'Reilly 2022)

Isovalent/Cilium 团队撰写的 eBPF 安全可观测性报告。

**核心论点：**
- Kubernetes 不提供默认安全配置，也无内置可观测性
- 传统安全工具不支持 kernel namespace 识别容器化进程
- Pod IP 地址是临时的，基于 IP 的安全日志难以追溯

**安全可观测性的四金信号 (Four Golden Signals)：**
1. **Process Execution** — 进程执行事件（execve、fork）
2. **Network Sockets** — 网络连接事件（connect、accept）
3. **File Access** — 文件访问事件（open、read、write）
4. **Layer 7 Network Identity** — 应用层身份（HTTP/gRPC/DNS 请求）

**eBPF 优势：**
- 原生理解容器属性（K8s labels、namespace、pod name）
- 捕获 pre-NAT pod IP，保留容器级身份
- 进程级可观测性：包括调用进程、参数、capabilities
- 无需更改应用程序代码

**最佳实践：**
- 最小权限原则：通过 eBPF 观察容器实际需要的 capabilities
- 检测权限提升、横向移动、凭据滥用等攻击模式

## 关键引用

- "eBPF is a highly efficient sandboxed virtual machine in the Linux kernel making the Linux kernel programmable at native execution speed" — Thomas Graf
- "The kernel does not know about containers or Kubernetes pods — there is no container ID in the kernel" — Thomas Graf
- "XDP allows packets to be reflected, filtered or redirected without traversing the networking stack" — Vieira, UFMG

## 相关页面

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-security]] — 安全监控与 Rootkit
- [[entities/linux/ebpf/ebpf-xdp]] — XDP 数据面
- [[entities/linux/ebpf/ebpf-ecosystem]] — 生态库对比
- [[entities/linux/ebpf/ebpf-container-audit]] — saBPF 容器审计
- [[entities/linux/ebpf/ebpf-security-observability]] — eBPF 安全可观测性
- [[kernel-net-index]] — Linux 网络子系统
