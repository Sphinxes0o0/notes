---
type: entity
tags: [game-engine, ecs, rust, architecture-pattern]
created: 2026-05-29
sources: [bookmark-bevy-engine-guide]
---

# ECS Architecture (Entity Component System)

## 定义

ECS (Entity Component System) 是一种游戏引擎架构模式，用 **组合替代继承**：Entities 是 ID，Components 是数据，Systems 是行为逻辑。广泛应用于 Unity、Bevy、Flecs 等现代游戏引擎。

## 关键要点

### Core Pattern

```
Entity   — 只是一个 ID，无状态
Component — 数据（仅字段，无逻辑）
System   — 纯函数，处理特定 Component 组合的 Entities
```

### 对比传统 OOP

| 方面 | OOP Game Engine | ECS |
|------|----------------|-----|
| 继承 | Actor/GameObject 树 | 组合，自由度高 |
| 数据 | 分散在对象内 | Components 连续内存，缓存友好 |
| 行为 | 方法绑定对象 | Systems 独立，可并行 |
| 扩展 | 需改类层次 | 新增 Component/System 即可 |

### Bevy ECS 特性

- **World**: 所有 Entities/Components/Systems 的容器
- **Schedule**: DAG 驱动的并行调度（无数据竞争的 Systems 可并行）
- **Query**: 缓存友好的 ECS 专用查询
- **Change Detection**: Component 变更追踪，精确刷新 System 状态

### 并行执行原理

Systems 之间通过 DAG 描述依赖，只有不访问同一 Components 的 Systems 才能并行执行 — 本质是 **无锁并行**。

## 相关概念

- [[concurrency]] — 并发控制模式
- [[rust-language]] — Rust ownership 使 ECS 内存安全
- [[cloud-native]] — 类似的解耦/组合思想（微服务）

## 来源详情

- [[bookmark-bevy-engine-guide]] — Bevy Engine Guide 系统讲解 ECS 架构
