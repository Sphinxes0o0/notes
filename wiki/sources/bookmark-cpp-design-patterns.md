---
type: source
source-type: bookmark
title: "C++ 设计模式"
author: "liu-jianhao"
date: 2024
size: medium
path: raw/github/liu-jianhao/Cpp-Design-Patterns
summary: "30个GoF设计模式的C++实现，按「封装变化」分类组织，含SOLID原则、Head-First版本对比，2.6k stars。"
tags: [cpp, design-patterns, GoF, SOLID, OOP]
---

# C++ 设计模式

## Overview

C++ 设计模式的全面实现仓库，按「封装变化」视角分类组织，覆盖 GoF 23 种设计模式 + 7 个额外模式，共 30 个模式，2.6k stars。

## Core Content

### 30 Patterns Organized by "Encapsulating Changes"

**组件协作 (Component Collaboration):**
- [[Template Method]] — 算法骨架
- [[Observer]] / Event — 事件监听
- [[Strategy]] — 算法替换

**单一职责 (Single Responsibility):**
- [[Decorator]] — 动态添加职责
- [[Bridge]] — 抽象与实现分离

**对象创建 (Object Creation):**
- [[Factory Method]] — 子类决定创建
- [[Abstract Factory]] — 产品族创建
- [[Prototype]] — 克隆复制
- [[Builder]] — 分步构建

**对象性能 (Object Performance):**
- [[Singleton]] — 单实例（饿汉/懒汉）
- [[Flyweight]] — 享元（共享细粒度对象）

**接口隔离 (Interface Isolation):**
- [[Facade]] — 简化子系统
- [[Proxy]] — 远程/虚代理
- [[Mediator]] — 中介者解耦
- [[Adapter]] — 接口转换

**状态变化 (State Changes):**
- [[Memento]] — 状态快照
- [[State]] — 状态机

**数据结构 (Data Structures):**
- [[Composite]] — 树形结构
- [[Iterator]] — 遍历抽象
- [[Chain of Responsibility]] — 责任链

**行为变化 (Behavior Changes):**
- [[Command]] — 请求封装
- [[Visitor]] — 操作与结构分离

**领域问题 (Domain Problems):**
- [[Interpreter]] — 语法解析

### 8 SOLID + OOP Principles

1. **DIP** — Dependency Inversion Principle（依赖倒置）
2. **OCP** — Open-Closed Principle（开闭）
3. **SRP** — Single Responsibility Principle（单一职责）
4. **LSP** — Liskov Substitution Principle（里氏替换）
5. **ISP** — Interface Segregation Principle（接口隔离）
6. **CARP** — Composition/Aggregation Reuse Principle（组合优先）
7. **EP** — Encapsulate What Varies（封装变化）
8. **PAI** — Program to an Interface（面向接口）

## 相关页面

### Entity 页面
- [[entities/cpp/large-scale-cpp]] — 大规模 C++ 设计
- [[entities/cpp/raii]] — RAII（单例等模式的基础）

### Source 页面
- [[sources/cpp-modern-skills]] — Modern C++ Skills（含架构相关内容）
