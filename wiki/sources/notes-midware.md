---
type: source
source-type: github
path: raw/github/notes/midware/
created: 2026-05-22
---

# 中间件笔记

## Overview

中间件技术学习笔记，重点涵盖 DoIP（Diagnostic over IP）车载诊断协议。内容涉及 DoIP 在 ISO 13400 标准下的物理连接、车辆声明、通信建立、诊断通信全流程，以及 SOME/IP 服务导向通信协议的基本概念。

## Key Topics

- **DoIP（ISO 13400）**：基于 IP 的车载诊断协议，位于七层模型第 3/4 层
  - 物理连接：外部诊断设备通过 IP 接口连接边缘节点（需激活线）
  - 车辆声明：VIN/EID/GID 广播或主动请求
  - 通信建立：Socket 激活（Payload Type 0005/0006）
  - 诊断通信：Tester → 网关 → ECU 双响应机制（ACK + Response）
  - 2020 版新增 TLS 安全机制
- **SOME/IP**：汽车服务导向通信协议，vSOME/IP 开源实现
- **技术栈**：DoIP、SOME/IP、vSOME/IP

## Related Entities

- [[entities/midware]] — 中间件概念页（DoIP、SOME/IP 协议详解）
- [[entities/sys]] — TCP/IP 协议栈基础（Socket 通信）
