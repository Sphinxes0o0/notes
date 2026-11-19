---
type: entity
tags: [snort3, inspector, plugin, packet-processing, framework]
created:2026-06-08
sources: [github-snort3-net-inspectors, github-snort3-service-inspectors]
---

# Snort3 Inspector Framework

## 定义

Snort3 Inspector 是包处理的核心插件抽象，继承自 `Inspector` 基类，每个 inspector负责特定协议层/功能（HTTP、DNS、TCP 流重组、SSL 解密等）。Inspector 通过 `InspectorManager` 实例化，按 InspectorType（GLOBAL/CONTEXT/INSPECT）和 Usage分类索引，形成 inspector链（binder → network → service → detect）。

##关键要点

- **`Inspector` 基类**：实现 `configure/tinit/tterm/eval/likes/disable` 接口
- **InspectorType分类**：IT_NETWORK（binder/network 层）、IT_STREAM（流重组）、IT_SERVICE（HTTP/DNS）、IT_DETECT（检测）
- **Usage维度**：GLOBAL（全局）/CONTEXT（per-packet）/INSPECT（per-inspector）
- **执行链**：`PigPen`协调 binder → network → service → detect顺序
- **数据驱动配置**：Module 参数 + Lua配置
- **动态 reload**：inspector 可运行时替换（不重启进程）

##核心概念

- **`eval(Packet*)`**：包处理入口，返回 Action（PASS/INSPECT）
- **`likes(Packet*)`**：包过滤（决定是否进入 eval）
- **binder inspector**：按 port/protocol选定 service inspector
- **service inspector**：协议级解析（HTTP/DNS/SMB）
- **stream inspector**：TCP 流跟踪、重组
- **network inspector**：网络层操作（frag/route）
- **InspectorType查询**：`PigPen::get_service_inspector(snort_protocol_id)`

## 相关页面

- [[entities/linux/snort3/snort3-framework]] —框架
- [[entities/linux/snort3/snort3-net-inspectors]] — net inspectors
- [[entities/linux/snort3/snort3-service-inspectors]] — service inspectors
- [[entities/linux/snort3/snort3-packet-processing]] — 包处理流程
