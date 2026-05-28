---
type: source
source-type: bookmark
title: "深入高可用系统原理与设计"
author: "isno"
date: 2026-05-28
size: small
path: raw/bookmarks/ebooks/thebyte/
summary: "isno 高可用系统实践指南，覆盖云原生/容器/K8s/负载均衡/一致性算法/Paxos/Raft/Service Mesh，10章系统设计"
---

# 深入高可用系统原理与设计

## 核心内容

### 云计算与云原生 (第1章)
- 云原生定义：容器、微服务、服务网格、不可变基础设施、声明式API、DevOps
- 云原生架构演进：从单体→SOA→微服务→云原生
- CNCF技术栈全景图

### 网络性能优化 (第2-3章)
- 延迟指标、RTT、HTTPS延迟分析
- DNS/HTTPDNS/Brotli压缩/QUIC
- Linux内核网络框架：Netfilter/iptables/conntrack
- 内核旁路：DPDK/XDP/RDMA
- Linux虚拟网络：namespace/veth/bridge/VXLAN

### 负载均衡 (第4章)
- 四层/七层负载均衡
- 部署拓扑：中间代理/边缘代理/客户端内嵌/边车代理
- LVS NAT/DR/TUN/FULLNAT、Maglev一致性哈希
- 全局负载均衡设计
- 服务发现/健康检查/粘性会话/TLS卸载

### 数据一致性与分布式事务 (第5章)
- ACID/BASE/CAP
- TCC/Saga/可靠事件队列
- 服务幂等性设计

### 分布式共识 (第6章)
- **Paxos**: Proposer/Acceptor/Learner角色，两阶段提交(Prepare/Accept)，多数派裁决，活锁问题
- **Raft**: 领导者选举(Log Replication/AppendEntries RPC)，成员变更(ConfChange)，工程化共识
- 复制状态机

### 容器编排 (第7章)
- **Borg/Omega/Kubernetes演进**: Master/Borglet→Store→API Server/Scheduler/Controller
- **容器技术原理**: chroot→namespace(Mount/UTS/PID/Network/IPC/User/Cgroup)→cgroups限制
- **Pod设计**: Infra Container(pause容器)、超亲密容器组、sidecar模式
- **CRI**: containerd/CRI-O/katacontainers/firecracker
- **镜像**: UnionFS/OverlayFS/分层设计/写时复制CoW/Nydus启动加速/Dragonfly下载加速
- **存储**: Volume(PV/PVC)/StorageClass/CSI插件/块存储/文件存储/对象存储

### 服务网格 (第8章)
- 数据平面：Envoy/Linkerd
- 控制平面：Istio/xDS协议
- 边车代理模式

### 可观测性 (第9章)
- 指标/日志/链路追踪/性能剖析
- OpenTelemetry

### 应用封装与交付 (第10章)
- Kustomize/Helm/Operator/OAM/KubeVela

## 关键引用

- GitHub: https://github.com/isno/theByteBook
- 出版书籍: https://item.jd.com/14531549.html

## 相关页面
- [[cloud-native]] — 云原生概念
- [[load-balancing]] — 负载均衡
- [[paxos-consensus]] — Paxos共识算法
- [[raft-consensus]] — Raft共识算法
- [[kubernetes-orchestration]] — Kubernetes容器编排
- [[container-technology]] — 容器技术原理
- [[service-mesh]] — 服务网格
