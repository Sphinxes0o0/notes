---
type: source
source-type: github
title: snort3 flow + ips_options source code
author: Cisco Talos (Snort Team)
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/flow/ ~/workspace/github/snort3/src/ips_options/
summary: Snort3 源码分析：flow 模块（flow tracking、hash table、timeout、direction、state machine）和 ips_options 模块（content/pcre/byte_test 等检测选项、选项评估树、插件架构）
created: 2026-05-27
tags: []
---
# GitHub Snort3 — flow + ips_options 源码分析

## 核心内容

### Flow 模块（`src/flow/`）

#### Flow Hash Table
- **FlowCache**：ZHash + per-protocol LRU + allowlist LRU
- **FlowKey**：IP 对、端口对、MPLS/tenant/vlan + 协议号/pkt_type/version
- **哈希算法**：32-bit mix，15 个 uint32_t 字段，三轮混合
- **Key 规范化**：较小 IP → ip_l，相等时较小端口 → port_l

#### Flow Timeout
- `FlowCache::timeout()`：遍历 LRU，淘汰 idle_timeout 到期流
- `prune_idle()`：容量满时每轮清理 1 条；`prune_excess()`：超容时淘汰
- `allowlist_on_excess()`：可移入 allowlist 而非删除
- PruneReason：EXCESS/UNI/MEMCAP/HA/STALE/IDLE_MAX_FLOWS/IDLE_PROTOCOL_TIMEOUT/STREAM_CLOSED/END_OF_FLOW

#### Flow Direction
- TCP 角色：`init_roles_tcp()` — SYN→client，SYN-ACK→server（dst），其他→高端口是 client
- UDP：`init_roles_udp()` — src=client，dst=server
- IP：`init_roles_ip()` — src=client，dst=server
- `swap_roles()`：交换所有 client/server 字段并翻转 client_initiated

#### Flow State Machine
- 状态：SETUP → INSPECT → BLOCK/RESET/ALLOW
- `FlowState::SETUP`：新流初始化
- `FlowState::INSPECT`：正常检测中
- `FlowState::ALLOW`：放行，`DetectionEngine::disable_all()`
- `FlowState::BLOCK`/`RESET`：`Stream::drop_traffic()`

#### Key Classes
- `FlowControl`：顶层协调器
- `Flow`：核心会话数据（client_ip/server_ip、session、inspector）
- `FlowCache`：哈希表 + LRU 管理
- `Session`：协议特定会话抽象基类
- `FlowDataStore`：inspector 状态存储
- `FlowStash`：通用 KV 存储
- `ExpectCache`：预期流追踪
- `DeferredTrust`：延迟信任决策

---

### IPS Options 模块（`src/ips_options/`）

#### Option Types
- **Content**：`content`、`pcre`（PCRE2）、`regex`（Hyperscan）、`sd_pattern`
- **Byte Ops**：`byte_test`（比较）、`byte_jump`（跳转）、`byte_extract`（存变量）、`byte_math`（算术）
- **Flow/State**：`flow`、`flowbits`、`detection_filter`
- **Payload**：`file_data`、`raw_data`、`pkt_data`、`base64_decode`
- **Other**：`dsize`、`isdataat`、`so`、`replace`、`tag`

#### IpsOption Base Class
- `eval(Cursor&, Packet*)` → `MATCH/NO_MATCH/NO_ALERT/FAILED_BIT`
- `is_relative()`：是否依赖前序匹配
- `retry(Cursor&)`：是否在另一偏移重试
- `get_cursor_type()`：`CAT_NONE/READ/ADJUST/SET_OTHER/SET_RAW/SET_FAST_PATTERN/SET_SUB_SECTION`
- `hash()`/`operator==()`：用于检测树去重

#### Plugin Architecture
- `IpsApi`：pinit/pterm（解析时）、tinit/tterm（线程时）、ctor/dtor
- `load_ips_options()`：通过 PluginManager 加载所有检测插件

#### Detection Tree Evaluation
- `detection_option_tree_node_t`：evaluate 函数指针 + option_data + state
- 求值流程：was_evaluated 缓存 → RTN 匹配 → eval → 处理结果码 → 递归子节点
- **AND 语义**：所有子节点匹配才算成功
- `NO_ALERT`：匹配但不生成告警（flowbits:noalert）
- `FAILED_BIT`：flowbit 未设置，允许重求值

#### Cursor
- 追踪当前 buffer 位置：`buffer()`、`size()`、`get_pos()`、`set_pos()`、`add_pos()`、`get_delta()`

#### Variable Extraction
- `byte_extract` → `SetVarValueByIndex()` → `byte_test`/`byte_jump`/`byte_math` 引用
- 最多 2 个变量槽位

---

## 关键文件索引

| 文件 | 作用 |
|------|------|
| `flow/flow_cache.h/cc` | 哈希表 + LRU + 淘汰策略 |
| `flow/flow_key.h/cc` | FlowKey 定义 + 哈希函数 |
| `flow/flow.h/cc` | Flow 类定义 + 生命周期 |
| `flow/flow_control.h/cc` | 包处理协调 + 角色初始化 |
| `flow/flow_data.h/cc` | inspector 状态存储 |
| `flow/flow_stash.h/cc` | 通用 KV 存储 |
| `flow/session.h` | Session 抽象基类 |
| `flow/expect_cache.h/cc` | 预期流追踪 |
| `flow/ha.h/cc` | 高可用状态 |
| `ips_options/ips_content.cc` | content 选项 |
| `ips_options/ips_pcre.cc` | pcre 选项 |
| `ips_options/ips_byte_test.cc` | byte_test 选项 |
| `ips_options/ips_byte_jump.cc` | byte_jump 选项 |
| `ips_options/ips_byte_extract.cc` | byte_extract 选项 |
| `ips_options/ips_byte_math.cc` | byte_math 选项 |
| `ips_options/ips_flow.cc` | flow/flowbits 选项 |
| `ips_options/ips_detection_filter.cc` | detection_filter 选项 |
| `framework/ips_option.h` | IpsOption 基类 |
| `framework/cursor.h` | Cursor 类 |
| `detection_options.h/cc` | 检测树求值逻辑 |

## 相关页面

- [[entities/linux/snort3/snort3-flow]] — Flow 追踪实体页
- [[entities/linux/snort3/snort3-ips-options]] — IPS 选项实体页
- [[entities/linux/snort3/snort3-framework]] — Snort3 框架概览
