---
type: entity
tags: [Paxos, 分布式共识, 一致性, Leslie Lamport]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# Paxos 共识算法

## 定义

Leslie Lamport于1990年提出的基于消息传递、具备高度容错特性的共识算法，是分布式系统最重要的理论基础。

> "世界上只有一种共识算法，就是Paxos，其他所有的共识算法都是Paxos的退化版本。"

## 关键要点

### 三种角色
- **Proposer (提议者)**: 发起提案(Proposal)，包含编号N和值V
- **Acceptor (决策者)**: 接受或拒绝提案，超过半数接受则共识达成
- **Learner (记录者)**: 学习被批准的提案，不参与决策

### 两阶段提交

#### Phase 1: Prepare (准备阶段)
1. Proposer选择提案编号N，广播`Prepare(N)`请求
2. Acceptor：
   - 若已承诺≥N的提案：拒绝
   - 若未承诺：承诺不再接受<N的提案，返回已承诺的提案(若有)

#### Phase 2: Accept (批准阶段)
1. Proposer获得多数Promise后，选择提案值(返回的编号最高者，或自己值)
2. 广播`Accept(N,V)`请求
3. Acceptor：若编号N≥已承诺最大编号，则批准
4. 获得多数批准后，广播决议给Learner

### 正确性保证
- **多数派裁决**: 任何两个多数派必有交集，保证不会被两个值都批准
- **提案编号递增**: 乐观锁机制，防止提案冲突
- **值选择规则**: 必须选择已批准的值，保证一致性

### 活锁 (Livelock)
- 多Proposer并发发起提案，互相抢占
- 解决：随机化退让时间

### 工程局限
- 只能处理单个提案
- 至少两次网络往返
- 高并发可能活锁
- Multi-Paxos引入选主优化

## 相关概念
- [[raft-consensus]] — Raft（Multi-Paxos工程化变体，etcd/Consul基础）
- [[raft-leader-election]] — Raft领导者选举
- [[raft-log-replication]] — Raft日志复制
- [[cloud-native]] — 云原生（etcd是K8s一致性存储，基于Raft）
- [[kubernetes-orchestration]] — Kubernetes（依赖etcd）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
