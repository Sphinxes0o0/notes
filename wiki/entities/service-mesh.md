---
type: entity
tags: [服务网格, Service Mesh, Envoy, Istio, 边车代理]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# 服务网格 (Service Mesh)

## 定义

边车代理模式在微服务架构中的大规模应用，实现请求路由、负载均衡、可观测、安全等功能的透明治理。

## 关键要点

### 核心特征
- **数据平面**: 边车代理(Envoy/Linkerd)拦截所有进出流量
- **控制平面**: xDS API下发配置，管理代理行为
- **透明代理**: 应用无感知，无需修改代码

### 边车代理模式

```
服务A → [Envoy Sidecar] ← 服务B
              ↓
         控制平面
```

- 与主容器共享Network/UTS/IPC命名空间
- 拦截所有出站/入站请求
- 功能: 负载均衡/熔断/重试/超时/安全/可观测

### 演进路径

1. **客户端内嵌SDK** (Finagle/Eureka/Ribbon)
   - 缺点: 多语言实现困难，版本依赖
2. **边车代理模式** (服务网格)
   - 优点: 语言无关，应用透明，单独升级
   - 代表: Envoy/Linkerd/Istio

### 数据平面

#### Envoy核心功能
- **L3/L4过滤器**: TCP代理/UDP代理
- **L7过滤器**: HTTP/REST/gRPC
- **健康检查**: 主动/被动
- **熔断器**: Circuit Breaker模式
- **负载均衡**: RR/Least-Connection/一致性哈希
- **重试/超时**: 故障处理
- **速率限制**: 局部限流

#### xDS协议
- **Listener**: 监听套接字配置
- **Route**: HTTP路由规则
- **Cluster**: 后端服务集群
- **Endpoint**: 具体后端实例
- **Secret**: TLS证书

### 控制平面

#### Istio架构
- **Pilot**: 抽象配置→xDS分发
- **Mixer**: 策略检查+遥测收集
- **Citadel**: 证书管理，mTLS
- **Galley**: 配置验证

### vs 传统负载均衡
| 方面 | 服务网格 | 传统负载均衡 |
|------|----------|--------------|
| 部署位置 | 应用旁 | 网络边界 |
| 配置方式 | API动态 | 配置变更 |
| 粒度 | 请求级 | 连接级 |
| 治理范围 | 东西向+南北向 | 主要南北向 |

## 相关概念
- [[load-balancing]] — 负载均衡（服务网格的底层技术）
- [[cloud-native]] — 云原生（服务网格是云原生核心技术）
- [[kubernetes-orchestration]] — Kubernetes（服务网格运行平台）
- [[container-technology]] — 容器技术（边车是特殊容器）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
