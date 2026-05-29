---
type: index
tags: [linux, networking, tcp-ip, udp, webrtc, traffic-control]
created: 2026-05-29
---

# Linux — Networking

> Linux network stack: protocol implementations, traffic control, WebRTC, and load balancing

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/network/webrtc-peer-connection]] | WebRTC PeerConnection: ICE, DTLS, SRTP, peer connection state machine | webrtc, p2p, real-time |
| [[entities/linux/network/webrtc-signaling]] | WebRTC Signaling: SDP offer/answer, signaling server, WebSocket | webrtc, signaling, sdp |
| [[entities/linux/network/webrtc-media-handling]] | WebRTC Media: RTP/RTCP, jitter buffer, NACK, TWCC | webrtc, rtp, media |
| [[entities/linux/network/webrtc-protocol-stack]] | WebRTC Protocol Stack: SRTP, DTLS, ICE, TURN/STUN | webrtc, protocol, security |
| [[entities/linux/network/tcp-congestion-control]] | TCP Congestion Control: CUBIC, BBR, Reno, DCTCP | tcp, congestion, bbr |
| [[entities/linux/network/traffic-control]] | Traffic Control: qdisc, netem, tc-eBPF, packet scheduling | tc, qdisc, networking |
| [[entities/linux/network/load-balancing]] | Load Balancing: L4/L7, NAT, consistent hashing, service discovery | load-balancing, scalability |

## Cross-References

- [[linux-ebpf-xdp]] — XDP provides high-performance packet processing
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action works with XDP pipeline
- [[kernel-net-index]] — Linux kernel network protocol implementation
