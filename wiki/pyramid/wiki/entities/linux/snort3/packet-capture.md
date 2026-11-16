---
type: "entity"
tags: [snort3, networking, packet-capture, libpcap]
created: "2026-06-08"
sources: [sources/github-snort3-detection]
---
# Packet Capture

## 定义
Packet capture 是在数据链路层或网络层捕获网络数据包的过程, 通常
通过 libpcap (Linux) / Npcap (Windows) / BPF (BSD) API 暴露. Snort3
依赖 libpcap 或 AF_PACKET socket 进行抓包.

## 关键要点
- libpcap API: pcap_open_live, pcap_next, pcap_loop, pcap_dispatch
- AF_PACKET socket (Linux): tpacket v1/v2/v3 (零拷贝)
- BPF (Berkeley Packet Filter) 字节码 in-kernel 过滤
- Ring buffer: mmap, TPACKET_V3 (block-based), PACKET_MMAP
- Snort3 DAQ (Data Acquisition) layer: pcap, afpacket, netmap, dpdk

## 相关页面
- [[entities/linux/snort3/snort3-framework-analysis]]
- [[entities/linux/snort3/snort3-codecs]]
- [[entities/linux/snort3/ethernet-frame]]
- [[entities/linux/ebpf/ebpf-networking]]
- [[entities/linux/snort3/snort3]]
