---
type: entity
tags: [webrtc, media, getusermedia, mediastream, codec, srtp]
created: 2026-05-29
sources: [bookmark-webrtc]
---

# WebRTC Media Handling

## 定义

WebRTC 媒体处理涵盖从本地设备采集（getUserMedia）、媒体轨道管理（MediaStream）到端到端加密传输（SRTP）的完整链路，涉及编解码协商、流量控制和质量监控。

## 关键要点

- **getUserMedia()**: 请求用户授权访问摄像头/麦克风，返回 `MediaStream`
  - 媒体约束（宽高、帧率、分辨率）可配置
  - `stop()` 撤销访问权限
- **MediaStream**: 音频/视频轨道的抽象容器
  - `getAudioTracks()` / `getVideoTracks()` 获取轨道列表
  - `addTrack()` / `removeTrack()` 动态增删轨道
  - 可跨 PeerConnection 共享（同一本地流发送给多个远端）
- **编解码器**:
  - 音频: Opus（强制要求，IP 语音优化）、G.711（老式电话系统兼容）
  - 视频: H.264、VP8、VP9、AV1（标准未统一）
- **SRTP (Secure RTP)**: 加密媒体流
  - DTLS 握手期间派生 SRTP 密钥
  - RTCP 控制信息伴随媒体流（报告质量、报告接收状态）
- **RTP 会话**: 每种媒体通常在独立 RTP 会话中传输（独立 RTCP）
- **多路复用**: IETF 正在标准化同一端口复用多媒体（减少 NAT 打孔数量）

## 媒体流路径

```
本地摄像头/麦克风 → getUserMedia() → MediaStream
                                        ↓
                              addTrack() → RTCPeerConnection
                                        ↓
                              SRTP 加密 → UDP 传输 → 远端
```

## 相关概念

- [[webrtc-peer-connection]] — MediaStream 通过 PeerConnection 添加到连接
- [[webrtc-signaling]] — 编解码器能力在 SDP offer/answer 中协商
- [[webrtc-protocol-stack]] — SRTP 是协议栈最底层的媒体加密传输
- [[tcp-congestion-control]] — WebRTC 媒体流基于 UDP，拥塞控制算法（GCC）决定发送速率
