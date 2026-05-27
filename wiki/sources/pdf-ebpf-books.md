---
type: source
created: 2026-05-22
source-type: pdf
sources: [pdf-ebpf-books]
tags: [ebpf, linux-kernel, books]
title: "eBPF Books (3册)"
author: "浪潮信息/龙蜥社区; 多位贡献者"
date: 2026-05-22
size: medium
path: raw/PDFs/books/eBPF基础.pdf, raw/PDFs/books/eBPF_technical_practice_v2.pdf, raw/PDFs/books/Beginners_guide_to_eBPF_programming_for_networking.pdf
summary: "3册eBPF书籍：龙蜥社区白皮书/基础教程（架构/CO-RE/Verifier/JIT/Maps/6大场景）、技术实践指南（XDP/TC/iproute2/CO-RE）、Liz Rice入门指南（事件驱动/程序类型/网络钩子）"
---

# eBPF Books (3册)

## 核心内容

### 1. eBPF基础（龙蜥社区白皮书）

《eBPF基础》是由浪潮信息、阿里云、东南大学联合编写，龙蜥社区发布的 eBPF 技术白皮书，系统全面。

**架构章节：**
- eBPF 加载过程：字节码读取 → 重定位（map fd替换、BTF CO-RE）→ Verifier 校验 → JIT 编译 → 挂载执行
- Verifier 两阶段安全检查：DAG 验证 + 逐条字节码分析（寄存器/内存/指针类型）
- JIT 编译：字节码到 native 机器码，即时编译缓存解决解释器性能问题
- Maps 实现：fd 替换机制，内核 map 地址注入 BPF 指令
- Map 性能排名：Array > Percpu Array > Hash > Percpu Hash > LRU Hash > LPM

**程序类型详解：**
- **kprobe/kretprobe**：动态内核探针，追踪函数入口/返回值，可高效采集数据
- **XDP**：eXpress Data Path，NIC 驱动层早期数据包处理，~20Mpps
- **TC (Traffic Control)**：Ingress/Egress 双方向，skb 上下文，可附加到虚拟设备（veth）
- **sock_ops**：TCP socket 操作拦截（15个hook点），动态调整 TCP 参数
- **LSM**：Linux Security Modules，eBPF 动态挂载安全策略

**CO-RE 详解：**
- BTF 类型信息 → 字段重定位（偏移/存在性/大小）
- `bpf_core_field_exists()` / `bpf_core_read()` / `BPF_CORE_READ()` 宏
- `bpf_core_enum_value_exists()` 枚举值重定位
- struct flavors 处理跨内核版本不兼容类型

**应用场景（6大场景）：**
1. 系统诊断 — PingTrace（ICMP 延迟探测定界）
2. 虚拟化 IO 全链路时延监测 — bpftrace 追踪 virtio/blk 路径
3. TCP 监控 — eBPF 采集 TCP RTT/重传/拥塞数据
4. 网络性能优化 — XDP/TC 加速数据包处理
5. 流量镜像 — 无锁 perf ring buffer 高性能采样
6. 网络访问控制 — 基于 eBPF 的防火墙策略

### 2. eBPF技术实践 v2

《eBPF技术实践》侧重工程落地细节。

**XDP 三种模式：**
- `xdpdrv` (native)：驱动层最早 hook，性能最优
- `xdpgeneric`：generic XDP，skb 已分配后 hook，测试用
- `xdpoffload`：SmartNIC offload，Netronome nfp 驱动

**TC 深度：**
- sch_clsact 伪 qdisc（无锁执行，可安全用于虚拟设备）
- Direct-Action 模式：BPF 程序直接返回 verdict，无需外部 action 模块
- offload 支持：hw-tc-offload + clsact + BPF da 模式

**CO-RE 实战：**
- `__builtin_preserve_access_index()` 编译器内置函数
- `bpf_core_field_exists()` / `bpf_core_field_size()`
- struct flavor 机制（`struct thread_struct___v46`）
- 只读全局变量优化（vs Map 查询）

**BPF 编程要点：**
- 512 字节栈限制，per-CPU array 突破
- `#pragma unroll` 处理循环
- BPF-BPF 调用（4.16+）替代 always_inline
- 字节对齐补白：显式 pad 字段 vs `#pragma pack(4)`

### 3. Beginners Guide to eBPF Programming for Networking (Liz Rice)

Liz Rice (Isovalent) 的入门教程，简洁易懂。

**eBPF 事件驱动模型：**
- 系统调用、函数入口/退出、tracepoint、网络事件作为 hook 点
- "Hello World"：`SEC("kprobe/sys_execve")` + `bpf_printk()`
- BPF 程序注册到 hook 后，内核执行到 hook 点时自动触发

**程序类型全览：**
- kprobe/kretprobe：内核函数追踪
- XDP：网卡驱动层数据包处理
- Socket Filter：raw socket 数据过滤（copy to userspace 前）
- TC (Traffic Control)：Ingress/Egress qdisc hook
- Sock_ops：TCP socket 参数动态调整
- LSM：安全策略强制

**网络追踪示例：**
- `tcp_v4_connect()` kprobe 追踪连接建立
- Socket Filter 挂载到 raw socket 观测网络数据
- TC ingress 抓取 ping 包 reply（验证 egress hook 双向性）

## 关键引用

- "eBPF 的诞生是 BPF 技术的一个转折点，使得 BPF 不再仅限于网络栈，而是成为内核的一个顶级子系统" — 《eBPF基础》前言
- "XDP allows packets to be reflected, filtered or redirected without traversing networking stack" — Liz Rice
- "Linux 内核不知道容器或 Kubernetes pod，内核只有 namespace 和 cgroup" — 《eBPF技术实践》

## 相关页面

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-xdp]] — XDP 快速数据路径
- [[entities/linux/ebpf/ebpf-networking]] — TC 与 Cilium
- [[entities/linux/ebpf/ebpf-ecosystem]] — eBPF 开发框架
- [[entities/linux-ebpf-fundamentals]] — eBPF基础教程（80页入门）
- [[entities/linux-ebpf-technical-practice]] — eBPF技术实践白皮书v2（龙蜥社区100页）
- [[kernel-subsystems-index]] — Linux 内核子系统
