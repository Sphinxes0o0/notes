---
type: entity
tags: [linux, ebpf, security, observability, cilium, kubernetes, isovalent]
created: 2026-05-23
sources: [pdf-ebpf-papers]
---

# eBPF Security Observability

## 定义

基于 eBPF 的安全可观测性是指利用 eBPF 在内核中的 hook 点，以零侵入方式捕获进程执行、网络连接、文件访问和应用层身份等安全事件，实现对云原生环境（尤其是 Kubernetes）的实时安全态势感知。

## Four Golden Signals (四金信号)

由 Isovalent/Cilium 定义的安全可观测性四大信号：

### 1. Process Execution (进程执行)

- 监控容器内进程创建 (`execve`、`fork`)
- 检测反弹 Shell、权限提升、异常二进制执行
- 提供进程名、参数、UID/GID、Capabilities 等上下文

### 2. Network Sockets (网络连接)

- 监控 socket 创建、连接建立 (`connect`、`accept`)
- 捕获 pre-NAT pod IP，保留容器级身份标识
- 检测横向移动、C2 通信、端口扫描

### 3. File Access (文件访问)

- 监控文件打开/读取/写入事件
- 检测敏感文件访问、配置文件篡改、恶意文件创建
- 关联进程上下文识别异常文件操作

### 4. Layer 7 Network Identity (应用层身份)

- 解析 HTTP/gRPC/DNS 请求中的应用层数据
- 识别 API 端点访问、DNS 查询目标
- 检测应用层攻击（SQL 注入、SSRF）

## eBPF 的技术优势

| 对比维度 | 传统工具 | eBPF 安全可观测性 |
|---------|---------|------------------|
| 容器感知 | 不支持 namespace | 原生理解 K8s labels/pod name |
| IP 追溯 | 只有节点 IP | pre-NAT pod IP |
| 事件保真度 | 日志聚合级 | 进程级 (PID/args/caps) |
| 应用修改 | 需 sidecar 注入 | 零侵入，无需修改 |
| 内核兼容 | 版本锁定 | CO-RE 跨版本兼容 |

## 实践模式

### 最小权限配置

1. 部署 eBPF 安全监控观察容器实际使用的 capabilities
2. 基于观察结果精确配置 SecurityContext（只允许需要的 capabilities）
3. 持续监控异常 capabilities 使用

### 攻击检测场景

- **权限提升** — 进程执行 + capabilities 突变组合
- **横向移动** — 异常网络连接 + 非预期端口
- **凭据滥用** — S3 凭证被非预期工作负载使用
- **容器逃逸** — 异常的 namespace 切换、文件系统挂载

## 相关概念

- [[entities/linux/ebpf/ebpf-security]] — eBPF 安全监控与 Rootkit
- [[entities/linux/ebpf/ebpf-container-audit]] — saBPF 容器审计
- [[entities/linux/ebpf/ebpf-networking]] — TC 与 Cilium 网络层
- [[entities/security/commercial-cryptography]] — 国密算法 (SM2/SM3/SM4) 在云原生安全中的应用
- [[ebpf-index]] — eBPF 模块导航

## 来源详情

- [[sources/pdf-ebpf-papers]] — Security Observability with eBPF (O'Reilly 2022)
