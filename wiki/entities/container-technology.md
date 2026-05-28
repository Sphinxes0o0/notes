---
type: entity
tags: [容器, Container, Linux Namespace, cgroups, Docker]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# 容器技术原理

## 定义

容器是通过Linux namespace实现资源隔离、cgroups实现资源限制、拥有独立rootfs的特殊进程，是"软隔离"而非虚拟机。

## 关键要点

### 技术演进
1. **chroot (1979)**: 改变进程根目录，文件系统隔离
2. **pivot_root**: 更安全的文件隔离（Linux 2.3）
3. **Namespace (Linux 2.6.19+)**: 各项资源隔离
4. **cgroups (Linux 2.6.24)**: 资源限制

### 八类Namespace

| Namespace | 隔离内容 | 内核版本 |
|----------|----------|----------|
| Mount | 文件系统挂载点 | 2.4.19 |
| IPC | 消息队列/共享内存/信号量 | 2.6.19 |
| UTS | Hostname/Domain name | 2.6.19 |
| PID | 进程号 | 2.6.24 |
| Network | 网络设备/协议栈/路由/iptables | 2.6.29 |
| User | 用户/用户组 | 3.8 |
| Cgroup | cgroup控制组 | 4.6 |
| Time | 系统时间 | 5.6 |

### cgroups子系统
- **cpu/cpuacct**: CPU占用率
- **memory**: 内存限制
- **blkio**: 块设备I/O
- **devices**: 设备访问权限
- **freezer**: 暂停/恢复任务
- **net_cls/net_prio**: 网络流量分类

### 容器vs虚拟机

| 方面 | 容器 | 虚拟机 |
|------|------|--------|
| 隔离层级 | 进程级(共享内核) | 硬件级(独立内核) |
| 启动速度 | 秒级 | 分钟级 |
| 资源开销 | 极小 | 较大 |
| 安全性 | 较弱(共享内核) | 较强(完全隔离) |

### 镜像技术
- **UnionFS/OverlayFS**: 联合挂载，分层设计
- **写时复制(CoW)**: 共享只读层，按需复制
- **rootfs**: 包含应用+操作系统文件的自包含环境

### 容器运行时
- **Docker**: 镜像+容器事实标准
- **containerd**: Docker拆分出的容器运行时
- **CRI-O**: K8s专用轻量运行时
- **Kata Containers**: 硬件虚拟化安全容器

## 相关概念
- [[kubernetes-orchestration]] — Kubernetes（容器编排平台）
- [[linux-cgroups]] — cgroups（容器资源隔离的底层支持）
- [[linux-network-namespace]] — Network Namespace（容器网络隔离）
- [[service-mesh]] — 服务网格（边车代理容器）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
