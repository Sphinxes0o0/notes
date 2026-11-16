---
type: entity
tags: [webrtc, network, real-time, protocol-stack, ice, stun, turn]
created: 2026-05-29
sources: [bookmark-webrtc]
---

# WebRTC Protocol Stack

## 定义

WebRTC 协议栈是一组用于浏览器之间端到端实时通信的协议，涵盖媒体协商（SDP）、连接建立（ICE/STUN/TURN）、加密传输（DTLS/SRTP）和数据通道（SCTP）。

## 关键要点

- **分层架构**: ICE（顶层协调）→ STUN/TURN（NAT 穿透）→ DTLS（密钥交换）→ SRTP/SCTP（媒体/数据面）
- **ICE (Interactive Connectivity Establishment)**: 协调 STUN/TURN 服务器，枚举所有候选路径（host、srflx、relay），选择最优路径
- **STUN**: 查询公网 IP:端口，解决非对称 NAT 问题
- **TURN**: 中继服务器作为最后手段，解决对称 NAT 问题，带宽成本高
- **SDP (Session Description Protocol)**: 文本格式会话描述，包含媒体类型、编解码器、IP/端口、Crypto 等
- **JSEP**: JavaScript API 控制信令状态机，会话描述和 ICE candidate 由应用层透传
- **DTLS**: 基于 UDP 的 TLS 1.3，用于密钥交换和证书管理
- **SRTP (Secure RTP)**: 加密的 RTP 媒体流，防止窃听和篡改
- **SCTP over DTLS**: DataChannel 传输层，支持多流、部分可靠、有序/无序

## 协议交互流程

1. 交换 SDP offer/answer（媒体类型、编解码器、IP/端口）
2. ICE 开始收集 candidates（host → srflx → relay）
3. ICE 连通性检查（STUN binding request/response）
4. DTLS 握手建立安全会话
5. SRTP 传输加密媒体流
6. SCTP 关联建立 DataChannel

## 相关概念

- [[webrtc-peer-connection]] — PeerConnection API 是 ICE/DTLS/SRTP 的上层封装
- [[webrtc-signaling]] — SDP offer/answer 通过信令通道交换
- [[webrtc-media-handling]] — SRTP 传输的媒体内容（Opus/G.711 音频、H.264/VP8 视频）
- [[tcp-congestion-control]] — WebRTC 媒体传输基于 UDP，但拥塞控制参考 TCP 模型
- [[load-balancing]] — TURN 中继服务器本身是负载均衡节点
