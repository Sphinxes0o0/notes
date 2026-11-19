---
type: entity
tags: [snort3, tcp, stream-reassembly, ids-ips]
created: 2026-05-27
sources: [github-snort3-stream]
---

# Snort3 Stream TCP Reassembly

## 定义

Snort3 的 TCP stream 模块负责追踪 TCP 会话状态、执行分段重组、管理重叠数据、处理 PAWS 时间戳验证，并在检测前将字节流重新组装为逻辑 PDU。

## 关键要点

### TCP Stream Tracker

每个 TCP flow 有两个 `TcpStreamTracker` 实例（client 和 server），各维护：

| 字段 | 含义 |
|------|------|
| `rcv_nxt` / `rcv_wnd` | RCV.NXT（接收下一序号）、RCV.WND（接收窗口） |
| `snd_una` / `snd_nxt` / `snd_wnd` | SND.UNA（未确认）、SND.NXT（发送下一）、SND.WND（发送窗口） |
| `irs` / `iss` | IRS（初始接收序号）、ISS（初始发送序号） |
| `ts_last` | 最近一次时间戳（PAWS 用） |
| `fin_seq_status` | FIN 序号状态：FIN_NOT_SEEN / FIN_WITH_SEQ_SEEN / FIN_WITH_SEQ_ACKED |
| `seglist` | `TcpReassemblySegments` — 重组分段链表 |
| `reassembler` | `TcpReassembler*` — PAF 刷新策略执行器 |

### TCP 状态机

14 个状态（RFC 793 + 中间流接收）：

```
TCP_LISTEN → TCP_SYN_SENT → TCP_SYN_RECV → TCP_ESTABLISHED
                                          ↘ TCP_MID_STREAM_RECV
TCP_SYN_SENT → TCP_MID_STREAM_SENT
TCP_ESTABLISHED → TCP_FIN_WAIT1 → TCP_FIN_WAIT2
               ↘ TCP_CLOSE_WAIT → TCP_CLOSING → TCP_LAST_ACK
                                    ↘ TCP_TIME_WAIT → TCP_CLOSED
               ↘ TCP_CLOSED（RST）
```

- `TcpStateMachine::eval()` 调度 talker 和 listener 的状态转换
- 每个状态有专属 `TcpStateHandler` 子类（如 `TcpStateEstablished`），处理 SYN/ACK/DATA/FIN/RST 事件
- pre/post SM packet actions 用于更新 tracker、触发刷新、记录事件

### Segment Reassembly（分段重组）

**核心结构 `TcpReassemblySegments`**：

```
seglist_base_seq     // 链表首个分段的基准序号
head / tail          // 双向链表指针
cur_rseg / cur_sseg  // 当前读/扫描分段
seg_count            // 当前排队分段数
seg_bytes_total      // 总字节（含头部开销）
seg_bytes_logical    // 逻辑字节（去重后）
total_bytes_queued   // 累计排字节（会话生命周期）
overlap_count        // 重叠分段计数
```

**Segment Node（`TcpSegmentNode`）**：
```cpp
seq, length, offset, cursor  // seq=初始序号；length=工作长度；offset=有效数据偏移；cursor=扫描位置
data[size]                    // 变长数据（struct hack 单次分配）
```

**添加分段流程**：
1. `queue_reassembly_segment()` — 落入窗口则直接插入
2. `insert_segment_in_seglist()` — 快路径（SEQ_EQ 紧随其后，无规范化）
3. 否则调用 `TcpOverlapResolver` 处理重叠

### Flush Policies（刷新策略）

三种策略（`FlushPolicy` 枚举）：

| 策略 | 类 | 触发条件 | 说明 |
|------|-----|---------|------|
| `STREAM_FLPOLICY_IGNORE` | `TcpReassemblerIgnore` | — | 不重组 |
| `STREAM_FLPOLICY_ON_ACK` | `TcpReassemblerIds` | ACK 到达 | IDS 模式：等数据被确认后再刷新 |
| `STREAM_FLPOLICY_ON_DATA` | `TcpReassemblerIps` | 数据到达 | IPS 模式：数据到达即刷新（减少延迟） |

**PAF（Protocol-Aware Flushing）**：
- `ProtocolAwareFlusher` (PAF) 在字节流中定位协议边界（如 HTTP header 结束）
- `paf_check()` 扫描分段数据，返回 flush point 或 -1（继续扫描）
- 状态：`START → SEARCH → FLUSH → STOP / ABORT`

**IDS 刷新（`scan_data_post_ack`）**：
- 按序扫描已 ACK 的字节，更新 PAF 位置
- 遇到 hole → `skip_seglist_hole()`，设置 `paf.state = SKIP`
- hole 导致 PAF splitter 失效时 → `tracker.fallback()` 回退到 AtomSplitter

**IPS 刷新（`scan_data_pre_ack`）**：
- 不等待 ACK，数据到达即扫描
- 依赖 `is_q_sequenced()` 确认数据连续
- hole 时返回 `FINAL_FLUSH_HOLD` 暂停

### Overlap Handling（重叠处理）

**`TcpOverlapResolver` 架构**：
- `eval_left()` / `eval_right()` — 分别处理左/右重叠
- 13 种 OS 策略工厂（Linux/BSD/Windows/Solaris 等）

**重叠类型**：
1. **Left overlap** — 新分段左边界与已存分段重叠
2. **Right overlap** — 新分段右边界与已存分段重叠
3. **Full overlap** — 新分段完全包含已存分段

**OS 策略差异**（核心方法）：

| 策略 | Left | Right | Full Right |
|------|------|-------|------------|
| FIRST/Vista | keep_first | truncate_new | truncate_new |
| LAST | keep_last | truncate_existing | drop_old |
| Linux | keep_first | truncate_existing | drop_old_if_fully_absorbed |
| BSD/MacOS/Windows | keep_first | truncate_existing | drop_old_if_absorbed_before_slide |
| Solaris/HPUX11 | trim_first | truncate_new | first_if_gap_otherwise_drop |
| OLD_LINUX | keep_first | truncate_existing | drop_old |

**Zero-Window Probe (ZWP)**：
- 重叠段长度 == 1 且为 keep-alive probe 时，检查数据内容是否匹配
- 不匹配且为 inline 模式 → 丢弃该段

**PAWS（Protect Against Wrapped Sequences）**：
- `update_paws_timestamps()` 检查 TSval 是否递增或回绕超过 24 天
- `PAWS_WINDOW = 60` 秒，TSecr 必须匹配 `ts_last`
- 不合格的分段可能被归类为 retransmit

### Held Packets（暂存数据包）

用于处理 ACK 驱动的 flush 场景：

```cpp
held_pkt_seq           // 暂存数据包的序号
set_held_packet()      // 暂存数据包
is_retransmit_of_held_packet()  // 检查重传
release_held_packets() // 超时释放
```

### 关键类关系

```
TcpSession
├── client: TcpStreamTracker
│   ├── seglist: TcpReassemblySegments
│   │   ├── head/tail: TcpSegmentNode*（双向链表）
│   │   └── overlap_resolver: TcpOverlapResolver*
│   └── reassembler: TcpReassembler*
│       ├── TcpReassemblerIds（PAF_ON_ACK）
│       └── TcpReassemblerIps（PAF_ON_DATA）
└── server: TcpStreamTracker（同上）

TcpStateMachine
├── tcp_state_handlers[TCP_MAX_STATES]
│   ├── TcpStateEstablished
│   ├── TcpStateSynSent
│   └── ...（14个状态处理器）
└── eval(TcpSegmentDescriptor&) → talker + listener 状态转换

TcpOverlapResolverFactory → 13 种 OS 策略实例
```

## 相关概念

- [[entities/linux/snort3/snort3-flow]] — Flow 追踪与会话管理
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-framework]] — Snort3 框架概览
- [[network-intrusion-detection]] — 入侵检测系统

## 来源详情

- [[github-snort3-stream]]
