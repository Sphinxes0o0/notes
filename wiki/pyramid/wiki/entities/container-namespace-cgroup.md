---
type: entity
tags: [container, linux-kernel, namespace, cgroup, isolation]
created: 2026-05-29
sources: [bookmark-linux-namespace-cgroup]
---

# Container Isolation (Namespace + Cgroup)

## 定义

Linux 容器依赖两大内核机制：**Namespace** 实现资源隔离（每个进程看到独立的系统视图），**Cgroup** 实现资源限制（控制 CPU/内存/IO 等资源使用）。

## 关键要点

### Namespace 类型

| Namespace | Flag | 隔离内容 |
|-----------|------|----------|
| UTS | CLONE_NEWUTS | 主机名、域名 |
| IPC | CLONE_NEWIPC | System V IPC、POSIX 消息队列 |
| Mount | CLONE_NEWNS | 文件系统挂载点 |
| PID | CLONE_NEWPID | 进程 ID 空间 |
| Network | CLONE_NEWNET | 网络接口、路由表、iptables |
| User | CLONE_NEWUSER | UID/GID 映射 |

### Cgroup 资源控制

| 子系统 | 控制内容 |
|--------|----------|
| memory | 内存上限、swap、OOM 配置 |
| cpu | CPU shares、cpuset、bandwidth |
| pids | 进程/线程数量上限 |
| blkio | 块设备 IO 权重和上限 |
| cpuset | CPU 核心绑定 |

### 容器 = Namespace + Cgroup

- **Namespace**: 隔离（进程看到什么）
- **Cgroup**: 限制（进程能用多少）
- Docker/LXC/runc 在这两层之上提供镜像和工具

### 与 VM 的区别

容器共享宿主机内核，无独立硬件模拟，因此比 VM 轻量（秒级启动 vs 分钟级），但隔离性较弱。

## 相关概念

- [[container-technology]] — 容器技术总览
- [[cloud-native]] — 云原生应用架构
- [[linux-kernel-ipc-core]] — IPC 机制（与 Namespace IPC 相关）
- [[linux-kernel-mm-swap]] — 内存管理（Cgroup memory 子系统）

## 来源详情

- [[bookmark-linux-namespace-cgroup]] — SegmentFault Linux Namespace and Cgroup 系列
