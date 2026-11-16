---
type: entity
tags: [Kubernetes, K8s, 容器编排, Borg, Omega]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# Kubernetes 容器编排

## 定义

Google第三套容器管理系统，2014年开源，吸收Borg/Omega设计，是容器编排的事实标准。

## 关键要点

### 演进背景
- **Borg**: Google第一代容器管理，Master+Borglet架构，prod/non-prod优先级，cgroups支撑
- **Omega**: Borg进化，拆分BorgMaster为多组件，基于Paxos的分布式Store，乐观绑定调度
- **Kubernetes**: 2014年DockerCon开源，Borg经验+CNCF生态

### 核心架构
- **Master**: API Server/Scheduler/Controller Manager/Cloud Controller Manager
- **Node**: kubelet/kube-proxy/containerd
- **Etcd**: Raft共识的分布式KV存储

### 设计哲学
- **以应用为中心**: 标准化API(Pod/Service/Ingress/PV)，跨云厂商一致
- **CRD扩展**: 自定义资源定义，扩展到数据库/消息队列等
- **声明式配置**: Desired State，控制器模式

### 核心资源
| 资源 | 作用 |
|------|------|
| Pod | 最小调度单元， Infra Container共享UTS/Network/IPC |
| Deployment | 无状态应用滚动更新 |
| StatefulSet | 有状态应用，持久标识 |
| DaemonSet | 每节点一个Pod |
| Service | 稳定网络入口，负载均衡 |
| Ingress | HTTP路由 |
| PV/PVC | 持久化存储 |

### Pod核心概念
- **Infra Container**: pause容器(~300KB)，申请共享命名空间
- **超亲密容器**: Pod内容器共享Network/UTS/IPC，通过setns加入
- **Sidecar模式**: 日志/监控/安全边车容器

### 资源模型与调度
- **资源请求/限制**: CPU/内存申请
- **调度器**: Predicates/Priorities过滤和排序
- **亲和性/反亲和**: Pod间部署约束
- **污点和容忍**: 节点隔离

## 相关概念
- [[container-technology]] — 容器技术原理（namespace/cgroups）
- [[service-mesh]] — 服务网格（K8s+Envoy边车）
- [[raft-consensus]] — Raft（etcd一致性基础）
- [[load-balancing]] — 负载均衡（K8s Service）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
