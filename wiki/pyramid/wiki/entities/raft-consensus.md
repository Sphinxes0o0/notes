---
type: entity
tags: [Raft, 分布式共识, Leader Election, Log Replication]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# Raft 共识算法

## 定义

Diego Ongaro和John Ousterhout于2014年提出的可理解的共识算法，是Multi-Paxos的工程化变体，成为etcd、Consul等分布式系统的实现基础。

## 关键要点

### 三种角色
- **Leader (领导者)**: 处理所有客户端请求，将日志复制到Follower
- **Follower (跟随者)**: 接收Leader消息，心跳超时后成为Candidate
- **Candidate (候选人)**: 过渡角色，发起选举

### 领导者选举

#### 任期 (Term)
- 递增的数字，贯穿选举、日志复制全过程
- 保证领导者唯一性
- 冲突检测：节点通过任期号判断是否落后

#### 选举过程
1. Follower心跳超时(150-300ms随机)，转为Candidate
2. 任期号+1，广播RequestVote RPC
3. 其他节点：日志至少与投票者一样新+本任期未投票→投票
4. 获得多数票→成为Leader
5. 发送心跳维持Leader地位

### 日志复制

#### 日志条目结构
```json
{
  "index": 9,        // 单调递增索引
  "term": 5,         // 创建时的任期
  "command": "set x=4"  // 客户端请求
}
```

#### AppendEntries RPC
- Leader广播日志复制请求
- Follower验证任期+日志连续性( prevLogIndex/prevLogTerm )
- 冲突时：删除冲突条目之后的所有条目
- Leader等待多数节点确认后提交

### 成员变更 (ConfChange)
- 单节点变更（避免脑裂）
- joint consensus两阶段方案
- 新节点先追上日志再参与投票

### vs Paxos

| 方面 | Raft | Paxos |
|------|------|-------|
| 可理解性 | 强 | 弱 |
| 领导者 | 强制选主 | 可多Proposer |
| 日志复制 | 明确 | 需要Multi-Paxos |
| 工程实现 | 详细 | 缺实现细节 |

## 相关概念
- [[paxos-consensus]] — Paxos（Raft的理论基础）
- [[raft-leader-election]] — 领导者选举详解
- [[raft-log-replication]] — 日志复制详解
- [[kubernetes-orchestration]] — Kubernetes（etcd基于Raft）
- [[cloud-native]] — 云原生（分布式协调是基础设施）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
