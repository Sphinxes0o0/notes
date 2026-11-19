---
type: entity
tags: [负载均衡, Load Balancing, L4/L7, Envoy, Nginx]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# 负载均衡 (Load Balancing)

## 定义

将传入的网络流量高效分配到多个后端服务器的架构模式，实现弹性、可扩展和高可用的系统。

## 关键要点

### OSI分层视角
- **四层负载均衡**: L2(修改MAC)/L3(修改IP)/L4(修改端口+NAT)
  - 维持传输层连接特性，不关心应用层内容
  - NAT/DR/TUN/FULLNAT模式
- **七层负载均衡**: 应用层代理，新建TCP连接到后端
  - 基于HTTP头部/URL/Host进行路由
  - 支持内容缓存/TLS卸载/高级路由

### 核心功能
- **服务发现**: 静态配置/DNS/服务注册中心(Zookeeper/etcd/Consul)/xDS
- **健康检查**: 主动(探测)/被动(监控请求)
- **负载均衡算法**: Round-Robin/最小连接/一致性哈希/加权
- **粘性会话**: Cookie/IP哈希
- **TLS卸载**: 证书集中管理，硬件加速

### 部署拓扑
1. **中间代理型**: Nginx/HAProxy/Envoy/F5，配置简单但单点
2. **边缘代理型**: CDN边缘节点，DDoS防护+缓存
3. **客户端内嵌**: Finagle/Eureka/Ribbon SDK，无单点但多语言负担
4. **边车代理型**: Envoy/Linkerd，透明治理→[[service-mesh]]

### 阻抗不匹配问题
- 四层负载均衡下，同一TCP连接的所有请求路由到同一后端
- 导致负载不均（HTTP/2多路复用场景）
- 解决：四层+七层两级分发

### 调度算法详解
| 算法 | 原理 | 适用场景 |
|------|------|----------|
| Round-Robin | 依次循环 | 服务器能力均等 |
| Least-Connection | 最少活跃连接 | 请求处理时间差异大 |
| Consistent Hash | 特征值→节点 | 会话保持 |
| Weighted | 权重分配 | 服务器能力不均 |

## 相关概念
- [[cloud-native]] — 云原生（负载均衡是微服务基础设施）
- [[service-mesh]] — 服务网格（边车代理型负载均衡）
- [[kubernetes-orchestration]] — Kubernetes Service（K8s内置负载均衡）
- [[linux-net-stack-overview]] — Linux网络协议栈

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
