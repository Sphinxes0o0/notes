---
type: "entity"
tags: [snort3, networking, tcp, stream-reassembly]
created: "2026-06-08"
sources: [sources/github-snort3-detection]
---
# TCP Stream Reassembly

## 定义
Stream reassembly 是把同一 TCP 连接分片重组为完整 byte stream
的过程. Snort3 的 stream inspector 维护 per-flow TCP state
machine, 把乱序到达的 segments 按序列号排序.

## 关键要点
- TCP state: SYN_SENT, SYN_RECV, ESTABLISHED, FIN_WAIT, CLOSE_WAIT
- Sequence number tracking + sliding window
- Out-of-order segment buffering (per-direction)
- 重组策略: flush on timeout / flush on close / flush on application-layer boundary
- Performance: per-flow hash table, lock-free lookup
- Snort3: src/flow/, src/stream/, src/stream_inspectors/

## 相关页面
- [[entities/linux/snort3/snort3-framework-analysis]]
- [[entities/linux/snort3/snort3-runtime]]
- [[entities/linux/snort3/snort3-stream]]  -- 拼写变体
- [[entities/linux/snort3/packet-capture]]
- [[entities/linux/network/tcp-sack-dsack]]
