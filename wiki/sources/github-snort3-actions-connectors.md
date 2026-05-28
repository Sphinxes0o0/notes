---
type: source
source-type: github
title: snort3 src/actions/ and src/connectors/
author: Cisco / Snort Team
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/actions/ ~/workspace/github/snort3/src/connectors/
summary: Snort3 IPS 动作系统（alert/log/pass/drop/block/reject/react/rewrite）和数据导出 Connector 框架（file/tcp/unix/stdio）
created: 2026-05-27
tags: []
---
# GitHub: snort3 src/actions/ & src/connectors/

## 核心内容

### Actions (`src/actions/`)

9 种 IPS 动作类型，全部实现为插件：

| 文件 | 动作 | 流量丢弃 |
|------|------|----------|
| `act_alert.cc` | alert | No |
| `act_log.cc` | log | No |
| `act_pass.cc` | pass | No |
| `act_drop.cc` | drop | **Yes** |
| `act_block.cc` | block | **Yes** |
| `act_reject.cc` | reject | **Yes** |
| `act_react.cc` | react | **Yes** |
| `act_replace.cc` | rewrite | No |
| `act_file_id.cc` | file_id | No |

**聚合管理**：`ActionsModule`（`actions_module.h`）统一管理所有动作的计数器。

### Connectors (`src/connectors/`)

4 种 Connector 类型：

| 目录 | 类型 | 底层 |
|------|------|------|
| `file_connector/` | file | `std::fstream` |
| `tcp_connector/` | tcp | BSD socket |
| `unixdomain_connector/` | unix | Unix Domain Socket |
| `std_connector/` | stdio | stdout/stdin |

## 关键实现细节

### Action 优先级（`IpsActionPriority`）

```
IAP_OTHER(1) < IAP_LOG(10) < IAP_ALERT(20) < IAP_REWRITE(30) < IAP_DROP(40) < IAP_BLOCK(50) < IAP_REJECT(60) < IAP_PASS(70)
```

### ActiveAction 延迟执行

`reject` 和 `react` 使用 `ActiveAction` 机制延迟执行：
- `RejectActiveAction` → `delayed_exec()` 发送 TCP Reset / ICMP
- `ReactActiveAction` → `delayed_exec()` 发送 HTTP 页面

### Connector 消息格式

所有 connector 使用 3 字节定长头：
```cpp
struct ConnectorMsgHdr {
    uint8_t version;       // 版本号
    uint16_t length;        // 后续数据长度
};
```

### tcp_connector 异步接收

- `poll()` 等待 socket 事件
- 后台线程 + `Ring<ConnectorMsg*>` 无锁队列
- 线程安全的消息传递

### unixdomain_connector 重连

- 连接断开触发 `POLLHUP/POLLERR/POLLNVAL`
- `ReconnectHelper` 管理重试逻辑
- 支持非阻塞 `connect()` + `select()`

## 关键源码文件

### Actions
- `actions/ips_actions.h` — 动作加载接口
- `actions/ips_actions.cc` — `load_actions()` 插件注册
- `actions/actions_module.h` — 聚合计数器管理
- `framework/ips_action.h` — `IpsAction` 基类定义

### Connectors
- `connectors/connectors.h` — `load_connectors()` 接口
- `connectors/connectors.cc` — 插件注册
- `framework/connector.h` — `Connector`/`ConnectorMsg` 基类
- `file_connector/file_connector.cc` — 文件 connector
- `tcp_connector/tcp_connector.cc` — TCP connector（含线程接收）
- `unixdomain_connector/unixdomain_connector.cc` — Unix socket（含重连）
- `std_connector/std_connector.cc` — stdout/stdin connector

## 相关页面

- [[entities/linux/snort3/snort3-actions]] — 动作类型详细分析
- [[entities/linux/snort3/snort3-connectors]] — Connector 框架详细分析
- [[snort3-framework-analysis]] — 整体框架分析
