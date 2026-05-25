---
type: entity
tags: [security, ebpf, observability, cloud-native, kubernetes, falco, google, krsi, runtime]
created: 2026-05-25
sources: [pdf-security-papers-ebpf, pdf-isovalent-security-observability, pdf-sabpf-container-audit]
---

# eBPF Linux Security Observability

## 定义
使用eBPF（扩展伯克利包过滤器）实现Linux内核级别的安全可观测性，通过LSM钩子、tracepoint、kprobe等机制在不修改内核的情况下收集安全遥测数据。

## 关键要点

### eBPF安全监控优势 vs Kernel模块
- **Safety**: eBPF verifier在加载前验证程序安全性；kernel模块bug可直接crash系统
- **Granularity**: eBPF可按容器/命名空间细分；kernel模块是系统级的
- **No kernel modification**: CO-RE (Compile Once, Run Everywhere) 避免内核版本耦合
- **Performance**: 环形缓冲区(ringbuffer)低延迟内核→用户空间事件传递

### Apple Falco: eBPF for Kernel Security Monitoring
- Apple在eBPF Summit 2021分享Falco使用经验
- **为什么选择BPF**: 易于审计、bug影响受限、不依赖外部框架
- BPF程序可附加到: XDP(网络包过滤)、socket filter、tracepoint、probe
- libbpf + bpftool: 审计BPF程序指令、Map内容、使用统计

### Google KRSI: Kernel Runtime Security Instrumentation
- BPF LSM (Linux Security Module) 接口
- 设计用于强制执行(enforcement)，Google也用于审计(audit)
- 架构: Linux计算机 → BPF程序(attach到LSM钩子) → 安全遥测agent(Google内部)
- BPF Atomics: 原子操作支持
- Ringbuffers: 高效事件传递

### saBPF: Container-granular Audit
- 基于eBPF的容器级审计框架 (UBC/Harvard/Bristol, SoCC 2021)
- 命名空间感知的eBPF程序：理解容器边界(cgroup namespaces)
- 三种演示系统：审计框架、IDS、访问控制
-  provenance追踪：记录每个容器的进程/文件/套接字血缘关系

### Isovalent Four Golden Signals for K8s Security
1. **Latency**: 网络/响应时间异常 (DoS/入侵指标)
2. **Traffic**: 异常网络流 (横向移动检测)
3. **Errors**: 应用错误率 (HTTP 5xx)
4. **Saturation**: 资源耗尽 (CPU/内存/连接)

## 相关概念
- [[entities/linux/ebpf/ebpf-security-observability]] — eBPF安全可观测性（Isovalent）
- [[entities/linux/ebpf/ebpf-container-audit]] — saBPF容器审计
- [[kernel-subsystems-index]] — Linux内核密码学子系统(crypto_alg, skcipher, aead)
- [[ebpf-index]] — eBPF总体索引(XDP/TC/Cilium/Falco/CO-RE)
- [[sources/notes-security]] — 安全工具(Masscan, Falco, Snort)

## 来源
- [[sources/pdf-security-papers-ebpf]] — Rootkit Defense, Falco at Apple, Google BPF Audit
- [[sources/pdf-isovalent-security-observability]] — Isovalent O'Reilly报告
- [[sources/pdf-sabpf-container-audit]] — saBPF SoCC 2021论文
