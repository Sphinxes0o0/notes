---
type: entity
tags: [C++异步框架, 自定义协议, TLV]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow TLV Message

## 定义
TLV（Type-Length-Value）是一种简单通用的消息格式，适合自定义协议。框架内置 TLV 消息支持。

## 消息结构
- **Type**：4 字节（网络序）
- **Length**：4 字节（网络序）
- **Value**：最多 32GB

## 关键要点
- **接口**：`set_type()` / `get_type()`，`set_value()` / `get_value()`
- **派生**：建议派生 TLVMessage 实现更丰富的接口
- **应用**：简单二进制协议

## 相关概念
- [[entities/cpp/workflow/workflow-user-defined-protocol]] — 自定义协议
