---
type: entity
tags: [snort3, packet-processing, pipeline, daq, codec]
created:2026-06-08
sources: [github-snort3-runtime, github-snort3-codecs]
---

# Snort3 Packet Processing Pipeline

## 定义

Snort3 包处理流水线（Packet Processing Pipeline）是从 DAQ（Data Acquisition）抓包 →Codec 解码 →Inspector链评估 →Detection 检测 →Action触发 →Logger输出的完整数据通路。Snort3 采用多线程 PigPen 模型 +共享 FlowCache +上下文切换（ContextSwitcher）支持流重组的多 PDU场景。

##关键要点

- **DAQ抓包**：跨平台抽象（pcap/afpacket/nfqueue/dpdk）
- **Codec 解码**：按协议层级链式解码（Ethernet → IP → TCP → payload）
- **Inspector链**：binder → network → service → detect
- **Flow 流表**：跨包跨线程状态共享
- **ContextSwitcher**：流重建时切换检测上下文（PDU边界）
- **offload**：大 PDU 可走 Hyperscan/AC异步匹配
- **action → log**：触发告警/阻断动作后输出到 logger

##核心概念

- **DAQ 模块**：`daq_module_t`抽象，`pcap` / `afpacket` / `nfq` / `dpdk`
- **Packet 数据结构**：`Packet` 含 data指针、layers、flow、context
- **Decode链**：CodecManager 按顺序遍历（Ethernet → IPv4 → TCP → HTTP）
- **PigPen线程**：单包处理线程，循环 `idle()`
- **ContextSwitcher**：`enter_context/exit_context`支持流 PDU切换
- **Offload**：Hyperscan异步模式匹配 + callback
- **MPTransport**：多进程传输（shared memory）

## 相关页面

- [[entities/linux/snort3/snort3-runtime]] —运行时
- [[entities/linux/snort3/snort3-codecs]] — Codec
- [[entities/linux/snort3/snort3-inspectors]] — Inspector框架
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-flow]] — Flow 流表
