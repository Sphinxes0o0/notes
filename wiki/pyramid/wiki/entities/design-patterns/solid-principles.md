---
type: entity
tags: [设计模式, 设计原则, SOLID]
created: 2026-05-20
sources: [notes-overview-design-patterns]
---

# SOLID 设计原则 (SOLID Principles)

## 定义

SOLID 是五个面向对象设计原则的首字母缩写，帮助编写可维护、可扩展、可理解的代码。

## 五大原则

### 1. 单一职责原则 (SRP)
一个类只负责一件事，一个模块只有一个变化的原因。
- **实现**：里氏替换、接口隔离、开闭原则的基础

### 2. 开闭原则 (OCP)
软件实体应对扩展开放，对修改关闭。
- **实现**：通过继承、抽象来扩展而非修改原有代码
- **最终目标**：修改代码容易引入 Bug，扩展相对安全

### 3. 里氏替换原则 (LSP)
子类必须能够替换其基类，不破坏程序正确性。
- **核心**：继承关系的正确使用

### 4. 接口隔离原则 (ISP)
客户端不应依赖它不需要的接口，类之间的依赖应建立在最小接口上。
- **实现**：大接口拆分为小接口

### 5. 依赖倒置原则 (DIP)
高层组件不应依赖低层组件，两者都应依赖抽象。
- **核心**：抽象不应依赖实现，实现应依赖抽象
- **实现**：面向接口编程，如 JDBC

## 原则间的关系

```
SRP（基础） ──┬──→ LSP
              ├──→ ISP
              └──→ OCP
              
DIP（指导） ──┬──→ OCP
              ├──→ LSP
              └──→ ISP
```

- **SRP 是基础**：职责单一的模块更容易被组合、替换和修改
- **OCP 是最终目标**：修改代码容易引入 Bug，扩展相对安全
- **DIP 是指导原则**：在更高层次、更广范围内分离和替换代码

## 核心启示

> 设计模式的底层逻辑：**找到变化，封装变化**

## 相关概念

- [[entities/design-patterns/design-principles-advanced]] — DIP、SoC 等进阶原则
- [[entities/design-patterns/creational-patterns]] — 创建型模式
- [[entities/design-patterns/structural-patterns]] — 结构型模式
- [[entities/design-patterns/behavioral-patterns]] — 行为型模式

## 来源详情

- github-sphinxes0o0-notes-design-patterns — SOLID 五大设计原则
- github-sphinxes0o0-notes-design-patterns — `solid-principles-relation.md`
