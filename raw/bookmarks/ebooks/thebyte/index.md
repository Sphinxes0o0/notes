# 深入高可用系统原理与设计 — The Byte

> https://www.thebyte.com.cn/ | 85 pages | 199 images

---

## 前言 & 术语

- [[intro]] — 前言
- [[noun]] — 术语缩写释义

---

## Chapter 1: Cloud Native Technology Overview

- [[architecture/history]] — 1.1 Cloud Computing Evolution
- [[architecture/background]] — 1.2 Cloud Native Background
- [[architecture/define-cloud-native]] — 1.3 Cloud Native Definition
- [[architecture/target]] — 1.4 Cloud Native Goals
- [[architecture/container]] — 1.5.1 Container Tech
- [[architecture/MicroService]] — 1.5.2 Microservices
- [[architecture/ServiceMesh]] — 1.5.3 Service Mesh
- [[architecture/Immutable]] — 1.5.4 Immutable Infrastructure
- [[architecture/declarative-api]] — 1.5.5 Declarative Design
- [[architecture/devops]] — 1.5.6 DevOps
- [[architecture/arc]] — 1.6 Architecture Evolution
- [[architecture/architect]] — 1.7 Tech Stack

---

## Chapter 2: Building "Fast Enough" Network Services

- [[http/latency]] — 2.1 Latency Metrics
- [[http/https-latency]] — 2.2 HTTPS Optimization
- [[http/dns]] — 2.3 DNS Principles
  - [[http/dns-ha]] — 2.3.3 Facebook Outage Analysis
  - [[http/http-dns]] — 2.3.4 HTTPDNS
- [[http/compress]] — 2.4 Brotli Compression
- [[http/https-summary]] — 2.5 HTTPS Encryption
- [[http/congestion-control]] — 2.6 Congestion Control
- [[http/Edge-Acceleration]] — 2.7 Dynamic Acceleration
- [[http/quic]] — 2.8 QUIC Protocol

---

## Chapter 3: Linux Kernel Networking

- [[network/network-layer]] — 3.1 OSI Model
- [[network/networking]] — 3.2 Packet Receiving
- [[network/linux-kernel-networking]] — 3.3 Kernel Framework
  - [[network/netfilter]] — 3.3.1 Netfilter Hooks
  - [[network/iptables]] — 3.3.2 iptables
  - [[network/conntrack]] — 3.3.3 Conntrack
- [[network/kernel-bypass]] — 3.4 Kernel Bypass
  - [[network/DPDK]] — 3.4.1 DPDK
  - [[network/XDP]] — 3.4.2 eBPF/XDP
  - [[network/RDMA]] — 3.4.3 RDMA
- [[network/linux-virtual-net]] — 3.5 Network Virtualization
  - [[network/network-namespace]] — 3.5.1 Network Namespaces
  - [[network/tuntap]] — 3.5.2 TUN/TAP
  - [[network/virtual-nic]] — 3.5.3 Veth
  - [[network/linux-bridge]] — 3.5.4 Linux Bridge
  - [[network/vxlan]] — 3.5.5 VXLAN

---

## Chapter 4: Load Balancing & Proxy

- [[balance/balance]] — 4.1 LB & Proxy
- [[balance/balance-features]] — 4.2 Features
- [[balance/balance-topology]] — 4.3 Topologies
- [[balance/balance4]] — 4.4 Layer 4 LB
- [[balance/balance7]] — 4.5 Layer 7 to Gateway
- [[balance/global-load-balancer]] — 4.6 Global LB

---

## Chapter 5: Data Consistency & Distributed Transactions

- [[distributed-transaction/ACID]] — 5.1 Data Consistency
- [[distributed-transaction/CAP]] — 5.2 CAP Tradeoffs
- [[distributed-transaction/transaction]] — 5.3 Transaction Models
  - [[distributed-transaction/BASE]] — 5.3.1 Reliable Events
  - [[distributed-transaction/TCC]] — 5.3.2 TCC
  - [[distributed-transaction/Saga]] — 5.3.3 Saga
- [[distributed-transaction/idempotent]] — 5.4 Idempotency

---

## Chapter 6: Distributed Consensus & Algorithms

- [[consensus/consensus]] — 6.1 Consensus
- [[consensus/Replicated-State-Machine]] — 6.2 State Machine
- [[consensus/Paxos]] — 6.3 Paxos
  - [[consensus/Paxos-history]] — 6.3.1 History
  - [[consensus/Basic-Paxos]] — 6.3.2 Basic Paxos
- [[consensus/Raft]] — 6.4 Raft
  - [[consensus/raft-leader-election]] — 6.4.1 Leader Election
  - [[consensus/raft-log-replication]] — 6.4.2 Log Replication
  - [[consensus/raft-ConfChange]] — 6.4.3 Membership Changes

---

## Chapter 7: Container Orchestration

- [[container/borg-omega-k8s]] — 7.1 Evolution (Borg/Omega/K8s)
- [[container/orchestration]] — 7.2 Container Principles
- [[container/image]] — 7.3 Container Images
- [[container/CRI]] — 7.4 CRI
- [[container/storage]] — 7.5 Persistent Storage
- [[container/container-network]] — 7.6 Container Networking
- [[container/Resource-scheduling]] — 7.7 Scheduling
  - [[container/resource]] — 7.7.1 Resources
  - [[container/Extended-Resource]] — 7.7.2 Device Plugins
  - [[container/kube-scheduler]] — 7.7.3 Scheduler
- [[container/auto-scaling]] — 7.8 Auto-scaling

---

## Chapter 8: Service Mesh

- [[ServiceMesh/What-is-ServiceMesh]] — 8.1 What is Service Mesh
- [[ServiceMesh/MicroService-history]] — 8.2 Evolution
- [[ServiceMesh/data-plane]] — 8.3 Data Plane
- [[ServiceMesh/control-plane]] — 8.4 Control Plane
- [[ServiceMesh/overview]] — 8.5 Products/Ecosystem
- [[ServiceMesh/The-future-of-ServiceMesh]] — 8.6 Future

---

## Chapter 9: System Observability

- [[observability/What-is-Observability]] — 9.1 What is Observability
- [[observability/Observability-vs-Monitoring]] — 9.2 vs Monitoring
- [[observability/metrics]] — 9.3.1 Metrics
- [[observability/logging]] — 9.3.2 Logging
- [[observability/tracing]] — 9.3.3 Tracing
- [[observability/profiles]] — 9.3.4 Profiling
- [[observability/dumps]] — 9.3.5 Core Dumps
- [[observability/OpenTelemetry]] — 9.4 OpenTelemetry

---

## Chapter 10: Application Packaging & Delivery

- [[application-centric/application-centric]] — 10.1 Application-Centric
- [[application-centric/Controller]] — 10.2 Declarative Management
- [[application-centric/Kustomize]] — 10.3.1 Kustomize
- [[application-centric/Helm]] — 10.3.2 Helm
- [[application-centric/Operator]] — 10.3.3 Operator
- [[application-centric/OAM]] — 10.3.4 OAM/KubeVela

---

## Images

- `images/` — 199 downloaded images (max 8 per chapter page)
