---
type: entity
tags: [webrtc, signaling, sdp, jsep, ice, sip]
created: 2026-05-29
sources: [bookmark-webrtc]
---

# WebRTC Signaling

## 定义

WebRTC 信令是应用层负责的会话协商过程，用于在两个 PeerConnection 之间交换 SDP（会话描述协议）offer/answer 和 ICE candidates。信令协议本身未被标准化，留给应用选择（SIP、Jingle、WebSocket 等）。

## 关键要点

- **信令未标准化**: W3C/IETF 将信令层留白，不同应用可选不同协议（SIP、XMPP、WebSocket、HTTP Long Poll）
- **SDP Offer/Answer**: 交换媒体能力（编解码器、IP/端口、传输参数）
  - `v=` 版本、`o=` 发起者、`s=` 会话名、`c=` 连接地址
  - `m=` 媒体描述（音频/视频/数据，端口，协议，格式）
  - `a=` 属性行（Crypto、rtpmap、ice-ufrag、ice-pwd、fingerprint）
- **JSEP (JavaScript Session Establishment Protocol)**: 应用层控制信令状态机
  - 调用 `createOffer/createAnswer` 生成 SDP
  - `setLocalDescription/setRemoteDescription` 应用对端能力
  - ICE candidate 由 `onicecandidate` 回调触发，通过信令通道发送
- **ICE Candidate 交换**: candidate 类型（host/srflx/relay）决定网络路径优先级
- **呼叫流程**: Alice 创建 offer → 发送给服务器 → 服务器转发 Bob → Bob 创建 answer → 交换 ICE candidates → 连接建立
- **SIP 梯形 vs WebRTC 三角形**: 传统 VoIP 媒体经过 SIP 代理，WebRTC 媒体直连

## 信令传输方式

| 方式 | 优点 | 缺点 |
|------|------|------|
| WebSocket | 双向、低延迟、可穿透防火墙 | 需要 WebSocket 服务器 |
| HTTP Long Poll | 无需 WebSocket | 延迟高、资源占用大 |
| SIP | 电信级信令 | 复杂度高 |

## 相关概念

- [[webrtc-protocol-stack]] — SDP 是协议栈中会话描述层，ICE 负责连接建立
- [[webrtc-peer-connection]] — PeerConnection API 与信令状态机交互
- [[webrtc-media-handling]] — getUserMedia 获取本地媒体流后才能创建 offer
- [[load-balancing]] — 信令服务器本身可以做负载均衡（如 Janus、FreeSWITCH）
