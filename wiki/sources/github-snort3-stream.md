---
type: source
source-type: github
title: snort3 stream/TCP reassembly source code
author: Cisco Talos (Snort Team)
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/stream/tcp/
summary: Snort3 源码分析：TCP stream 追踪（TcpStreamTracker）、分段重组（TcpReassemblySegments）、刷新策略（PAF/IDS/IPS）、重叠处理（13种OS策略）、PAWS时间戳、状态机（14个状态）
created: 2026-05-27
tags: []
---
# GitHub Snort3 — stream/TCP reassembly 源码分析

## 核心内容

### TCP Stream Tracker（`tcp_stream_tracker.h/cc`）

每个 flow 维护两个 tracker（client/server），追踪单方向的 TCP 状态：

- **序列号追踪**：`rcv_nxt/rcv_wnd`、`snd_una/snd_nxt/snd_wnd`、`snd_wl1/snd_wl2`、`irs/iss`
- **选项追踪**：`mss`（MSS）、`wscale`（窗口缩放）、`ts_last`（时间戳）
- **状态标志**：`tf_flags`（TF_WSCALE/TF_TSTAMP/TF_MSS 等）
- **FIN 处理**：`fin_seq_status`（FIN_NOT_SEEN / FIN_WITH_SEQ_SEEN / FIN_WITH_SEQ_ACKED）
- **分段队列**：`TcpReassemblySegments seglist`
- **重组器**：`TcpReassembler* reassembler`

关键方法：
- `init_on_syn_sent/recv()` — 3WHS 初始化
- `update_tracker_ack_recv/sent()` — ACK 处理
- `update_on_fin_recv/sent()` — FIN 处理
- `is_segment_seq_valid()` — 序号合法性验证
- `handle_rst_packet()` — RST 处理

### TCP State Machine（`tcp_state_machine.h/cc` + `tcp_state_*.h`）

14 个 RFC 793 状态 + 中间流接收：

| 状态 | 关键事件 |
|------|---------|
| TCP_LISTEN | SYN recv → SYN_RECV |
| TCP_SYN_SENT | SYN-ACK → SYN_RECV；SYN → MID_STREAM_SENT |
| TCP_SYN_RECV | ACK → ESTABLISHED |
| TCP_ESTABLISHED | FIN → FIN_WAIT1；DATA → 重组 |
| TCP_MID_STREAM_SENT / RECV | 中间流 pickups |
| TCP_FIN_WAIT1 | FIN-ACK → FIN_WAIT2；FIN → CLOSING |
| TCP_FIN_WAIT2 | FIN → TIME_WAIT |
| TCP_CLOSE_WAIT | FIN-ACK → CLOSING |
| TCP_CLOSING | ACK → TIME_WAIT |
| TCP_LAST_ACK | ACK → CLOSED |
| TCP_TIME_WAIT | 2MSL → CLOSED |

`TcpStateMachine::eval()` 执行：
1. talker pre-SM actions
2. talker 状态转换
3. listener 状态转换
4. listener post-SM actions

### Segment Reassembly（`tcp_reassembly_segments.h/cc`）

**双向链表存储分段**：
```cpp
TcpSegmentNode { seq, length, offset, cursor, data[size], prev, next }
```

**队列管理**：
- `queue_reassembly_segment()` — 落窗口则插入
- `insert_segment_in_seglist()` — 快路径或调用 overlap resolver
- `add_reassembly_segment()` — 创建 TcpSegmentNode 并插入
- `advance_rcv_nxt()` — 更新 rcv_nxt 到连续数据末尾
- `skip_holes()` — 检测并跳过 hole，更新 bytes_missing/holes_detected
- `purge_flushed_segments()` — 刷新后清理已扫分段

**hole 处理**：
- `skip_hole_at_beginning()` — 链表头部 hole
- `skip_midstream_pickup_seglist_hole()` — 中间流 pickup 时的 hole
- `purge_segments_left_of_hole()` — 删除 hole 左侧所有分段

### Flush Policies（`tcp_reassembler*.h/cc`）

**TcpReassembler 基类**：
- `flush_stream()` — 执行实际刷新
- `eval_flush_policy_on_ack/data()` — 策略评估入口
- `segment_already_scanned()` — PAF 位置判断

**TcpReassemblerIds（IDS 模式，PAF_ON_ACK）**：
- `scan_data_post_ack()` — 扫描已被对方 ACK 的数据
- hole 时 `skip_seglist_hole()` → 更新 seglist_base_seq
- PAF splitter 失效时 `tracker.fallback()` 回退

**TcpReassemblerIps（IPS 模式，PAF_ON_DATA）**：
- `scan_data_pre_ack()` — 不等 ACK，数据到达即扫描
- 依赖 `is_q_sequenced()` 确认连续性
- hole 时返回 `FINAL_FLUSH_HOLD`

**TcpReassemblerIgnore**：
- 不重组，`perform_partial_flush()` 返回 0

### Protocol-Aware Flushing（PAF）（`paf.h/cc` + `pafng.cc`）

`ProtocolAwareFlusher` 定位协议边界：

```cpp
PAF_State { seq, pos, fpt, tot, paf(状态) }
// seq = stream cursor
// pos = last flush position
// fpt = current flush point
// paf = START/SEARCH/FLUSH/STOP/ABORT/SKIP
```

- `paf_check()` — 调用 splitter 的 `reassemble()` 扫描数据，返回边界位置或 -1
- `paf_jump()` — 快进后重新初始化
- splitter 失效（hole）→ `paf.state = SKIP` 或 `ABORT` → `tracker.fallback()`

### Overlap Handling（`tcp_overlap_resolver.h/cc`）

**13 种 OS 策略工厂**：

| 策略类 | OS 标识 |
|--------|---------|
| TcpOverlapResolverFirst | FIRST (IPS mode default) |
| TcpOverlapResolverLast | LAST |
| TcpOverlapResolverLinux | OS_LINUX |
| TcpOverlapResolverOldLinux | OS_OLD_LINUX |
| TcpOverlapResolverBSD | OS_BSD |
| TcpOverlapResolverMacOS | OS_MACOS |
| TcpOverlapResolverSolaris | OS_SOLARIS |
| TcpOverlapResolverIrix | OS_IRIX |
| TcpOverlapResolverHpux10 | OS_HPUX10 |
| TcpOverlapResolverHpux11 | OS_HPUX11 |
| TcpOverlapResolverWindows | OS_WINDOWS |
| TcpOverlapResolverWindows2K3 | OS_WINDOWS2K3 |
| TcpOverlapResolverVista | OS_VISTA |

**重叠处理算法**：
1. `eval_left()` — 找 left neighbor，调用 `insert_left_overlap()`
2. `eval_right()` — 遍历 right neighbor 链表，调用 `insert_right_overlap()` 或 `insert_full_overlap()`
3. `is_segment_retransmit()` — 检测重传，计为 full_retransmit
4. `zwp_data_mismatch()` — ZWP 数据不匹配检测

**Left overlap**：
- `left_overlap_keep_first()` — 保留已存，trim 新段重叠部分
- `left_overlap_trim_first()` — trim 已存
- `left_overlap_keep_last()` — 保留新段，split 已存

**Right overlap**：
- `right_overlap_truncate_existing()` — trim 已存分段
- `right_overlap_truncate_new()` — trim 新段并归一化（IPS mode）

**Full overlap**：
- `full_right_overlap_truncate_new()` — 截断新段保留已存
- `full_right_overlap_os1()` — BSD/Windows：旧包被新包完全吸收则丢弃旧包
- `full_right_overlap_os2()` — Linux：增加"slideSeq == right.start_seq"条件
- `full_right_overlap_os3()` — Solaris/HPUX11： gap 时保留旧包
- `full_right_overlap_os4()` — OLD_LINUX/LAST：总是丢弃旧包
- `full_right_overlap_os5()` — FIRST/Vista：总是 truncate_new

### PAWS（`tcp_session.cc:511-530`）

```cpp
update_paws_timestamps():
  if (ts_val >= ts_last || packet_ts >= ts_last_packet + PAWS_24DAYS)
      ts_last = ts_val;  // 24 days = 2073600 seconds
```

`PAWS_WINDOW = 60` 秒（默认）。

### Segment Descriptor（`tcp_segment_descriptor.h`）

封装 Packet + TCP header，提供统一访问接口：
- `get_seq() / get_end_seq()` — 序号
- `get_len()` — 数据长度（dsize）
- `get_timestamp()` — TSval
- `get_wnd() / scale_wnd()` — 窗口
- `is_packet_from_client/server()` — 方向
- `slide_segment_in_rcv_window()` — 偏移调整（用于 hole 场景）

---

## 关键文件索引

| 文件 | 作用 |
|------|------|
| `tcp_stream_tracker.h/cc` | TCP 单向 tracker（序列号/窗口/FIN/分段队列） |
| `tcp_session.h/cc` | TcpSession 顶层协调器 |
| `tcp_state_machine.h/cc` | 状态机引擎 |
| `tcp_state_*.h` | 14 个状态处理器（Established/SynSent 等） |
| `tcp_reassembly_segments.h/cc` | 分段双向链表管理 |
| `tcp_segment_node.h/cc` | 单个分段节点（含变长数据） |
| `tcp_segment_descriptor.h/cc` | Packet + TCP header 封装 |
| `tcp_reassembler.h` | 重组器基类（flush 抽象接口） |
| `tcp_reassembler_ids.h/cc` | IDS 模式（PAF_ON_ACK） |
| `tcp_reassembler_ips.h/cc` | IPS 模式（PAF_ON_DATA） |
| `tcp_overlap_resolver.h/cc` | 重叠处理（13 种 OS 策略） |
| `tcp_normalizers.h/cc` | 数据包归一化（trim/pad/drop） |
| `tcp_ha.h/cc` | High Availability 状态同步 |
| `held_packet_queue.h/cc` | 暂存数据包队列 |
| `tcp_event_logger.h/cc` | TCP 事件记录 |
| `tcp_alerts.h/cc` | TCP 告警追踪 |
| `paf.h/cc` | Protocol-Aware Flusher |

---

## 相关页面

- [[snort3-stream]] — Stream TCP 实体页
- [[entities/linux/snort3/snort3-flow]] — Flow 追踪与会话管理
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-framework]] — Snort3 框架概览
