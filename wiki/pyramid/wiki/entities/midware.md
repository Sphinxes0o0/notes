---
type: entity
tags: [中间件, 汽车电子, DoIP, SOME/IP]
created: 2026-05-20
sources: [notes-ccpp]
---

# 中间件（Middleware）

中间件是分布式系统中连接应用层与底层通信协议的桥梁，在汽车电子领域尤为重要。

## 定义

中间件是为应用提供通用能力和通信抽象的软件层，使应用无需关心底层网络传输细节。在车载网络领域，DoIP 和 SOME/IP 是两种核心的诊断/服务通信协议。

## 关键要点

### DoIP（Diagnostic over IP）

**ISO 13400** — 将 IP 技术应用于车载网络，满足车规需求。

**DoIP 位置**：七层模型中第 3/4 层（网络层/传输层），基于 TCP/IP 和 UDP 协议。

**通信流程**：
1. **物理连接**：外部诊断设备通过 IP 接口连接车身边缘节点（DoIP Edge Node），需激活线激活
2. **车辆声明**：车辆以广播形式发送三次声明（VIN, EID, GID），诊断设备也可主动请求
3. **通信建立**：通过 Payload Type（0005/0006）激活 Socket
4. **诊断通信**：Socket 激活后进行诊断通信，Tester 发送诊断请求，网关转发至 ECU

**响应机制**：Tester 收到两个响应 — Diagnostic Message Acknowledgement（网关确认）+ Diagnostic Message Response（ECU 响应）

**安全性**：2020 版新增 TLS 支持

### SOME/IP（Scalable Service-Oriented Middleware over IP）

**汽车服务导向通信协议**，用于车内服务发现与服务调用。

**vSOMEIP**：GENIVI 项目的开源实现（MPL v2.0，BMW 贡献）。

**架构**：
- 每个 vSOMEIP 应用通过 Routing Manager 与其他设备通信
- 一个设备上的多个应用共用一个 Routing Manager
- 默认第一个启动的应用负责启动 Routing Manager
- 基于 boost.asio 异步 IO 库实现

**核心模块**：
- **runtime**：创建和管理 application、message、payload
- **application**：最核心模块，管理客户端生命周期和通讯
- **endpoint**：TCP/UDP/Unix Domain Socket 客户端/服务端点
- **service_discovery**：服务注册、查询、健康检查（SD）
- **routing**：路由管理，每个系统只能有一个 Routing Manager
- **configuration**：JSON 配置文件（unicast, diagnosis, logging 等）

**服务发现机制**：
- **自主注册模式**：服务自己维护注册，定时发送心跳
- **第三方注册模式**：第三方健康检查确认服务可用性

**Endpoint 类型**（6 大类）：
- local-client, udp-client, tcp-client
- local-server, udp-server, tcp-server

**Banner 抓取**：支持 SSH、HTTP、SSL、SMB、FTP、SMTP 等多协议解析

## 相关概念

- [[entities/sys]] — TCP/IP 协议栈基础
- [[entities/cpp]] — C++ 在车载软件中的应用

## 来源详情

- github-notes-midware — 中间件笔记（DoIP 协议、vSOMEIP 架构分析）
