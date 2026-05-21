---
type: entity
tags: [设计模式, 设计原则, DIP, SoC, 关注点分离]
created: 2026-05-20
sources: [notes-overview-design-patterns]
---

# 进阶设计原则 (Advanced Design Principles)

## 定义

超越 SOLID 的进阶设计原则，包括依赖倒置、关注点分离、契约设计等核心理念。

## 关键要点

### 依赖倒置原则 (DIP)

**核心思想**：统一代码交互的标准

- 高级组件不应依赖于低级组件，两者都应依赖抽象
- 抽象不应依赖实现，实现应依赖抽象

**DIP vs IoC vs DI**：
- **IoC (控制反转)**：设计原则，反转控制权（不用自己开车，打车）
- **DI (依赖注入)**：实现 IoC 的设计模式，通过构造函数/属性/方法注入
- **IoC 容器**：自动依赖注入的框架（如 Spring）
- **DIP**：设计原则，认为高层应定义抽象，让低层依赖

### 关注点分离 (SoC)

将复杂问题拆分为小问题的方法论。

**两个视角**：
1. **架构设计视角**：层与层、模块与模块、服务与服务分离
2. **编码实现视角**：类与类、方法与方法的职责分离

**两个技巧**：
- **架构上**：策略和机制分离（标准化，如 HTTP 协议）
- **编码上**：使用和创建分离（用工厂模式，如 CaseFilterFactory）

### 惯例原则

提升编程中的沟通效率，减少代码间的相互影响。

### 契约原则 (Design by Contract)

通过明确的接口契约来定义组件间的交互规范。

## 设计原则与设计模式的关系

- 设计原则是**指导思想**（为什么要这样做）
- 设计模式是**最佳实践**（具体怎么实现）
- 模式是对原则的具体应用

## 相关概念

- [[entities/design-patterns/solid-principles]] — SOLID 基础原则
- [[entities/design-patterns/creational-patterns]] — 工厂模式（使用与创建分离的典型）
- [[entities/design-patterns/structural-patterns]] — 适配器模式（接口转换）
- [[entities/design-patterns/behavioral-patterns]] — 策略模式（算法的封装）

## 来源详情

- github-sphinxes0o0-notes-design-patterns — `13-反转原则如何减少代码间的相互影响`, `14-惯例原则如何提升编程中的沟通效率`, `15-分离原则如何将复杂问题拆分成小问题`, `16-契约原则如何做好-API-接口设计`
