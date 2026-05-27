---
type: source
tags: [someip, autosar, vsomeip, commonapi, franca, automotive, middleware]
source-type: pdf
created: 2026-05-23
sources: [pdf-someip-docs]
title: "SOME/IP & vSOME/IP 技术文档 (6篇)"
author: "AUTOSAR, GENIVI, Charles Chan"
date: 2024
size: medium
path: raw/notes/resources/docs/someip/
summary: "4篇 SOME/IP 技术文档（CommonAPI、Franca IDL、AUTOSAR 错误处理、SOME/IP-SD 头部）+ 2篇网络相关（vSomeIP Endpoints、Netmap 用户态协议栈）"
---

# SOME/IP & vSOME/IP 技术文档

## 1. CommonAPI C++ 使用说明

CommonAPI 是用于分布式应用的标准 C++ API 规范，通过 Franca IDL 描述接口，支持不同 IPC 后端（SOME/IP、D-Bus）透明切换。

**核心架构：**
- CommonAPI Core — 独立于中间件的部分（Runtime API）
- CommonAPI Binding — 特定中间件后端 (someip/d-bus)
- Franca IDL 定义接口 (*.fidl) + 部署参数 (*.fdepl)

## 2. Franca IDL 用户指南

Franca 是接口定义语言 (IDL) 框架，用于定义分布式系统的服务接口。包括 Eclipse 工具链、接口定义、类型系统、代码生成。

## 3. SOME/IP 错误处理 (AUTOSAR 4.2.1)

AUTOSAR 标准中 SOME/IP 序列化协议的错误处理机制。

## 4. SOME/IP-SD 头部格式

SOME/IP Service Discovery 协议头部结构：
- **SOME/IP 头部** (16 bytes): Service ID, Method ID, Length, Client ID, Session ID, Protocol Version, Interface Version, Message Type, Return Code
- **SOME/IP-SD 头部** (12 bytes): Flags (8 bit, bit 7 = Reboot Flag, bits 6-0 reserved) + Reserved (24 bit) + Entries Array + Options Array
- Reboot Flag: 单播模式下重启后置 1，Session-ID（位于 SOME/IP 头部的 Request ID 字段中）递增

## 5. vSomeIP Endpoints 实现分析

vSomeIP 是 GENIVI 的 SOME/IP 开源实现，Endpoints 是通信基础。

**六大 Endpoint 类型：**
- local-client / local-server（本地 IPC）
- udp-client / udp-server（UDP 通信）
- tcp-client / tcp-server（TCP 通信）

**生命周期：** Start() 创建 socket → connect → 接收/发送 → Stop() 断开
**通信机制：** 基于 Boost.Asio 异步 I/O (`async_write`)

## 6. Netmap 接口介绍

Netmap 高性能用户态数据包处理框架（非 SOME/IP 相关内容）。

## 相关页面

- [[entities/midware]] — 中间件概念页（DoIP、SOME/IP）
- [[entities/sys]] — TCP/IP 协议栈基础
- [[entities/cpp/cpp-templates]] — C++ 模板（CommonAPI 使用）
- [[kernel-net-index]] — Linux 网络子系统

## 其他 notes/docs 评估

以下 PDF 属于已有知识覆盖范围的重复：
- **linux_network_stack.pdf** — Linux 内核网络接收路径，已被 [[sources/notes-net-deep]] 覆盖
- **tcp_protocol_rfc_design_implementation.pdf** — TCP 协议 RFC 历史与设计，已被 [[entities/linux/network/net-stack-deep-dive]] 覆盖
- **泛型编程与STL中文版.pdf** — 图像扫描版，与 [[sources/pdf-cpp-effective-stl]] 部分重叠
- **图解密码技术 第三版.pdf** — 图像扫描版，已合并入 [[sources/pdf-crypto-books]]
