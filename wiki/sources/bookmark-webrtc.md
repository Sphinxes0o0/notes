---
type: source
source-type: bookmark
title: "WebRTC 实时通信"
subtitle: "Real-Time Communication with WebRTC"
author: "Salvatore J. Prescod, Justin Uberti"
translator: "a-wing"
date: 2024-01-01
url: https://a-wing.github.io/webrtc-book-cn/
github: https://github.com/a-wing/webrtc-book-cn/
original-url: https://www.oreilly.com/library/view/real-time-communication-with/9781449371869/
license: CC BY-NC 4.0
summary: "中文翻译版 WebRTC 实时通信技术书籍，涵盖 WebRTC 架构、API、信令、媒体处理等核心概念"
tags: [webrtc, real-time-communication, browser-api, p2p, voip]
---

# WebRTC 实时通信 (Real-Time Communication with WebRTC)

## 核心内容

- **WebRTC 架构**: 浏览器 P2P 实时通信模型（RTC 梯形/三角形），打破传统 client-server 范式
- **三大核心 API**: `MediaStream`（媒体获取）、`PeerConnection`（连接管理）、`DataChannel`（双向数据通道）
- **协议栈**: ICE/STUN/TURN（NAT 穿透）、SDP/JSEP（会话描述）、DTLS+SRTP（加密传输）、SCTP over DTLS over UDP
- **信令通道**: 应用层负责，SIP/Jingle 等协议可选，WebSocket/HTTP 传输
- **媒体处理**: getUserMedia 采集、Opus/G.711 音频编解码、SRTP 媒体面传输

## 章节结构

| # | 章节 | 核心概念 |
|---|------|----------|
| 1 | 简介 | WebRTC 架构、RTC 梯形图、PeerConnection 概述 |
| 2 | 处理浏览器中的媒体 | getUserMedia、MediaStream、媒体约束 |
| 3 | 构建浏览器 RTC 梯形图 | RTCPeerConnection、DataChannel、SCTP |
| 4 | 需要信令通道 | 信令通道、SDP offer/answer、ICE candidate 交换 |
| 5 | 放在一起 | 完整 WebRTC 系统实现 |
| 6 | 高级功能 | 网络会议、身份认证、DTMF |

## 关键协议

- **ICE** (Interactive Connectivity Establishment): 协调 STUN/TURN 找到最优通信路径，穿越 NAT/防火墙
- **STUN** (Session Traversal Utilities for NAT): 发现 NAT 公网 IP:端口
- **TURN** (Traversal Using Relays around NAT): 中继服务器解决对称 NAT 问题
- **SDP** (Session Description Protocol): 会话描述（媒体类型、编码格式、传输地址）
- **JSEP** (JavaScript Session Establishment Protocol): 应用层控制信令状态机
- **DTLS**: 密钥派生和证书管理
- **SRTP**: 加密实时媒体传输
- **SCTP**: DataChannel 多流可靠/部分可靠传输

## 相关页面

- [[webrtc-protocol-stack]] — ICE/STUN/TURN、SDP、实时传输协议栈
- [[webrtc-peer-connection]] — RTCPeerConnection、DataChannel、SCTP
- [[webrtc-signaling]] — 信令通道、SDP 协商、JSEP
- [[webrtc-media-handling]] — getUserMedia、MediaStream、编解码
- [[tcp-congestion-control]] — WebRTC 拥塞控制参考 TCP 拥塞控制
- [[load-balancing]] — TURN 中继服务器负载均衡
