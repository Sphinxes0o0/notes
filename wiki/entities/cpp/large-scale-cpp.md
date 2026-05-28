---
type: entity
tags: [cpp, large-scale, software-design, physical-design, components, dependencies, architecture]
created: 2026-05-23
sources: [pdf-cpp-modern-books, pdf-cpp-perf-books]
---

# Large-Scale C++ Software Design

## 定义

大规模 C++ 软件设计是 John Lakos 于 1996 年提出的方法论，聚焦 C++ 项目的**物理设计**（physical design）——即源文件、头文件、库之间的物理依赖关系管理，与传统的逻辑设计（类层次、接口）形成互补。

## 核心概念

### 物理设计 vs 逻辑设计

| 方面 | 物理设计 | 逻辑设计 |
|------|----------|----------|
| 对象 | .h 文件、.cpp 文件、库 | 类、接口、继承体系 |
| 关注点 | 编译依赖、链接顺序 | 抽象层次、职责划分 |
| 工具 | 依赖分析器、构建系统 | UML、设计模式 |

### 组件 (Component)

- 一个 `.h` + 一个 `.cpp` 构成一个基本组件
- 每个组件应封装一个逻辑概念
- 组件间依赖形成有向无环图 (DAG)

### 层级 (Levelization)

- 系统按物理依赖关系分层
- 高层可依赖低层，低层不可依赖高层
- 循环依赖是设计缺陷，必须消除

### 物理设计原则

- **减少编译依赖** — 前向声明代替 `#include`
- **最小化公开接口** — 隐藏实现细节
- **避免循环依赖** — 重构或引入接口层
- **头文件稳定** — 频繁修改的实现应隐藏在 .cpp 中

## 相关概念

- [[entities/cpp/cpp-templates]] — 模板在物理设计中用于策略类和特性类
- [[entities/cpp/cpp-stl-containers]] — 容器的物理依赖管理
- [[entities/cpp/cpp-stl-allocators]] — 自定义分配器与内存层级
- [[entities/cpp/raii]] — RAII 封装资源管理，降低物理耦合
- [[entities/cpp/cpp-perf-optimization]] — 物理设计对编译性能的影响

## 来源详情

- [[sources/bookmark-cpp-design-patterns]] — GoF 设计模式 C++ 实现（SOLID + 30 模式）
- [[sources/pdf-cpp-modern-books]] — Large-Scale C++ 章节
- [[sources/pdf-cpp-perf-books]] — 大规模设计中的性能考量
