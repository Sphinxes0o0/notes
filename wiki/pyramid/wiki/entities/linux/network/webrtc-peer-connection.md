---
type: entity
tags: [webrtc, peer-connection, datachannel, sctp, browser-api]
created: 2026-05-29
sources: [bookmark-webrtc]
---

# WebRTC Peer Connection

## 定义

`RTCPeerConnection` 是 WebRTC 的核心 API 对象，封装了 ICE 代理、DTLS 端点、SRTP 会话和 SCTP 关联，为浏览器提供端到端的实时媒体/数据通信抽象。

## 关键要点

- **连接建立流程**: 创建 PeerConnection → 添加 MediaStream/DataChannel → createOffer/createAnswer → 设置本地/远程描述 → ICE 候选交换 → 连接完成
- **DataChannel**: 基于 SCTP over DTLS，支持双向通信，可在媒体流建立前创建
  - 可靠有序（TCP 语义）、部分可靠（重传次数限制）、不可靠无序（UDP 语义）
  - 每个 DataChannel 是一个 SCTP 流，支持独立流量控制
- **媒体传输**: MediaStream 添加轨道（音频/视频），通过 SRTP 加密传输
- **ICE 状态机**: `new` → `connecting` → `connected` → `completed`（失败则 `failed`）
- **DTLS 证书**: 自签名证书，P2P 信任模型，不依赖 PKI
- **编解码协商**: 音频 Opus/G.711，视频 H.264/VP8/AV1（强制要求未标准化）

## 核心 API

```
pc = new RTCPeerConnection(servers)       // 创建连接
pc.addStream(stream)                     // 添加媒体流
dc = pc.createDataChannel('label')        // 创建 DataChannel
offer = await pc.createOffer()           // 生成 SDP offer
await pc.setLocalDescription(offer)      // 设置本地描述
// ... 信令交换 ...
await pc.setRemoteDescription(answer)    // 设置远端描述
```

## 相关概念

- [[webrtc-protocol-stack]] — PeerConnection 内部组合了 ICE、DTLS、SRTP、SCTP 协议栈
- [[webrtc-signaling]] — 信令通道用于交换 SDP offer/answer 和 ICE candidates
- [[webrtc-media-handling]] — MediaStream 媒体轨道通过 PeerConnection 传输
- [[load-balancing]] — P2P 连接失败时 fallback 到 TURN 中继（负载均衡节点）
