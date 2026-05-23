---
type: entity
tags: [linux, ebpf, security, containers, audit, kubernetes, lsm]
created: 2026-05-23
sources: [pdf-ebpf-papers]
---

# saBPF - Secure Container Audit with eBPF

## 定义

saBPF (secure audit BPF) 是 eBPF 框架的安全审计扩展，在 Linux Security Modules (LSM) hook 点附加 eBPF 程序，基于 cgroup namespace 实现容器粒度的内核审计。每个容器可独立定义审计策略和机制。

## 核心架构

### Reference Monitor + Namespace 交集

saBPF 修改内核以支持在 cgroup 层级附加 eBPF 程序：

- **根 cgroup** — 主机级审计策略（所有容器可见）
- **子 cgroup** — 容器/ Pod 级策略，叠加在父策略之上
- **独立隔离** — 同一主机的不同容器可运行不同的审计程序

### 高保真审计 (High-Fidelity Audit)

- **完整性** — LSM hooks 捕获所有内核对象间的有意义的交互
- **忠实性** — LSM 的 reference-monitor 设计确保触发 hook 时内核状态不可变
- **无并发漏洞** — 避免系统调用拦截的 TOCTTOU 攻击（time-of-check-to-time-of-use）

## Kubernetes 集成

### Sidecar 模式

1. **saBPF sidecar 容器** — 附加到每个 Pod，配置基于微服务特性的 eBPF 审计程序
2. **审计日志捕获** — 记录进程执行、文件访问、网络连接等系统活动
3. **可疑事件关联** — 各 Pod sidecar 发送事件到远程关联分析系统
4. **Cyber Kill-Chain 检测** — 跨多个微服务的攻击步骤关联

### 安全应用

- **入侵检测系统 (IDS)** — 基于容器行为模式的异常检测
- **轻量级访问控制** — 容器级 MAC 策略强制
- **取证分析** — 完整的容器活动审计线索

## 与传统方案的对比

| 特性 | Linux Audit Framework | saBPF |
|------|----------------------|-------|
| 记录完整度 | 不完整（丢失记录） | 高保真（LSM hooks 全覆盖） |
| 容器感知 | 无（主机级） | 容器级（cgroup 绑定） |
| 自定义策略 | 系统级策略 | 每个容器独立策略 |
| 部署复杂度 | 无需修改内核 | 需 saBPF 内核补丁 |
| 性能开销 | 低 | 与内核集成方案相当 |

## 相关概念

- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控与 Rootkit 防御
- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-ecosystem]] — eBPF 生态库对比
- [[kernel-subsystems-index]] — Linux 安全子系统

## 来源详情

- [[sources/pdf-ebpf-papers]] — Secure Namespaced Kernel Audit for Containers (SoCC 2021)
