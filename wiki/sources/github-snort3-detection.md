---
type: source
source-type: github
title: "snort3/src/detection — Detection Engine Source"
author: "Cisco / Sourcefire"
date: 2026-05-27
path: /Users/sphinx.shi/workspace/github/snort3/src/detection/
summary: "Snort3 IDS/IPS 入侵检测引擎核心源代码，涵盖规则评估流水线、快速模式匹配、事件队列、检测选项树"
---

# Snort3 Detection Engine Source

## 仓库信息

- **仓库**: `snort3` (official Cisco Snort 3)
- **路径**: `src/detection/`
- **许可**: GNU General Public License v2
- **版权**: Cisco and/or its affiliates, 2014-2025; Sourcefire Inc., 2002-2013

## 源代码文件清单

### 核心引擎

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `detection_engine.cc` | `snort::DetectionEngine` | 检测上下文管理、主检测入口 |
| `detection_engine.h` | 同上 | 头文件 |
| `fp_detect.cc` | `fpLogEvent`, `fpEvalPacket`, `fpFinalSelectEvent` | 快速模式后评估、事件选择 |
| `fp_detect.h` | `MatchInfo`, `OtnxMatchData` | 匹配数据结构 |
| `detection_options.cc` | `detection_option_node_evaluate`, `DetectionOptionHash` | 选项树评估、哈希去重 |
| `detection_options.h` | `dot_node_state_t`, `detection_option_tree_node_t` | 选项树节点结构 |
| `ips_context.cc` | `snort::IpsContext` | 单包检测状态容器 |
| `ips_context.h` | 同上 | 上下文状态机 |
| `ips_context_chain.cc` | `IpsContextChain` | 上下文链表管理 |
| `ips_context_chain.h` | 同上 | |
| `ips_context_data.cc` | `IpsContextData` | 上下文数据基类 |
| `ips_context_data.h` | 同上 | |

### 快速模式

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `fp_create.cc` | `fpCreateFastPacketDetection`, `PMX`, `NCListNode` | 规则组编译、MPSE 创建 |
| `fp_create.h` | 同上 | |
| `fp_config.cc` | `FastPatternConfig` | 快速模式配置 |
| `fp_config.h` | 同上 | |
| `fp_utils.cc` | `fp_single_pattern_match` | 模式匹配工具 |
| `fp_utils.h` | 同上 | |

### 规则结构

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `rules.cc` | `RuleStateMap`, `RuleListNode` | 规则列表管理、规则状态映射 |
| `rules.h` | `RuleTreeNode`, `ListHead` | RTN、规则列表头 |
| `treenodes.cc` | `OptTreeNode`, `RuleTreeNode` | OTN/RTN 实现 |
| `treenodes.h` | `OptFpList`, `OtnState` | 选项函数列表、统计 |
| `signature.cc` | `OtnLookup*`, `SigInfo` | OTN 查找、签名信息 |
| `signature.h` | `SigInfo`, `ClassType`, `ReferenceNode` | 签名元数据结构 |
| `rule_option_types.h` | `option_type_t` | 选项类型枚举 |

### 规则过滤

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `tag.cc` | `SetTags`, `CheckTagList` | tag 规则选项（日志后续包） |
| `tag.h` | `TagData` | tag 数据结构 |

### 端口规则映射

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `pcrm.cc` | `prmFindRuleGroupTcp/Udp/Ip/Icmp` | 端口规则映射查询 |
| `pcrm.h` | `PORT_RULE_MAP` | 规则组索引结构 |
| `service_map.cc` | `ServiceMap` | 基于服务的规则组索引 |
| `service_map.h` | 同上 | |

### 异步 Offload

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `regex_offload.cc` | `RegexOffload` | 大 PDU 正则 offload |
| `regex_offload.h` | 同上 | |
| `sfrim.cc` | `RegexOffload` 实现 | offload 队列管理 |
| `sfrim.h` | 同上 | |

### 追踪与日志

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `detect_trace.cc` | `debug_log*`, `fp_print_fplist` | 调试追踪 |
| `detect_trace.h` | 同上 | |
| `event_trace.cc` | `EventTrace_Log` | 事件追踪到 PacketTracer |
| `event_trace.h` | 同上 | |
| `context_switcher.cc` | `ContextSwitcher` | 上下文切换器 |
| `context_switcher.h` | 同上 | |

### 配置

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `detection_module.cc` | `DetectionModule` | `detection` 配置命名空间 |
| `detection_module.h` | 同上 | |

### 工具

| 文件 | 类/结构 | 职责 |
|------|---------|------|
| `extract.cc` | `byte_extract`, `string_extract`, `extract_data` | 字节/字符串提取工具 |
| `extract.h` | 同上 | |
| `detection_buf.h` | `DataBuffer`, `DataPointer` | 检测缓冲区封装 |
| `detection_continuation.h` | `Continuation` | 检测暂停/恢复 |
| `pattern_match_data.h` | `PatternMatchData` | 模式匹配数据结构 |

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    DetectionEngine                          │
│  inspect(Packet*) → detect(Packet*) → finish_inspect()   │
└──────────────────────────┬────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │    IpsContext (per packet) │
            │  packet / searches / stash  │
            │  otnx / equeue / matched_buf│
            └──────────────┬──────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │    PCRM              │   ServiceMap        │
     │  prmFindRuleGroup*   │  sopgTable          │
     └──────────┬───────────┴──────────┬─────────┘
                │                     │
         RuleGroup lookup      RuleGroup lookup
                │                     │
                └──────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              │   fpEvalPacket()        │
              │  (TCP/UDP/ICMP/IP/Svc)  │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │     Fast Pattern        │    MPSE Batch Search
              │   (fp_search)           │ ← rule_tree_queue()
              │   PMT_PKT/PDU/FILE     │
              └────────────┬────────────┘
                           │  MpseStash
              ┌────────────┴────────────┐
              │  rule_tree_match()     │
              │  detection_option_tree_ │
              │    evaluate()          │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │  match_rtn()   │  match_node()   │ match_leaf()
         │  (rule head)   │  (ips option)   │ (fpAddMatch)
         └─────────────────┴─────────────────┘
                           │
              ┌────────────┴────────────┐
              │  OtnxMatchData         │
              │  (per action type)     │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │ fpFinalSelectEvent()    │  Sort & dedup
              │ queue_event()          │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │  fpLogEvent()          │
              │  RateFilter + sfthreshold │
              │  IpsAction::exec()     │
              │  SetTags()             │
              └────────────────────────┘
```

## 关键设计决策

### 1. 快速模式选择器（Fast Pattern Selector）
每条规则可以选择"快速模式"内容，该内容被编译进 MPSE（Aho-Corasick / Hyperscan）进行批量匹配。只有命中快速模式的规则才会进入后续选项树评估。

### 2. PCRM — Port-Rule Map
按 `src_port/dst_port` 双索引规则组，避免对所有规则逐一检查。TCP/UDP 5元组直接索引，ICMP 按类型，IP 按协议。

### 3. Service Map
在 PCRM 基础上，额外按 `SnortProtocolId` 建立服务级索引，用于服务感知检测。

### 4. Detection Option Tree DAG
相同选项的规则共享同一个选项树节点，通过哈希去重减少内存和评估时间。

### 5. MpseStash
MPSE 批量搜索结果先存入 stash，支持流内去重，然后批量处理避免频繁回调开销。

### 6. Context Chain for Stream Rebuilt
TCP 流重建时，同一流有多个 PDU 对应多个 IpsContext，通过 `depends_on`/`next_to_process` 链接。检测可以暂停（在流边界）和恢复。

## 配置参数（DetectionModule）

```
detection:
  allow_missing_so_rules     # SO 规则缺失告警
  global_default_rule_state  # 默认启用规则
  global_rule_state          # 对所有策略应用 rule_state
  hyperscan_literals         # 使用 Hyperscan 做字符串匹配
  offload_limit             # 触发 offload 的最小 PDU 大小
  offload_threads           # offload 线程数
  pcre_enable               # 启用 PCRE
  pcre_match_limit          # PCRE 回溯限制
  pcre_match_limit_recursion # PCRE 递归限制
  pcre_override             # 忽略 /O 修饰符
  enable_address_anomaly_checks
  enable_strict_reduction   # 严格规则去重
  max_continuations_per_flow
  service_extension         # 服务扩展映射
```

## 相关页面

- [[snort3-detection-engine]] — 实体页面（完整分析）
- [[snort-rule-language]] — Snort 规则语言
- [[intrusion-detection-system]] — 入侵检测系统概念
