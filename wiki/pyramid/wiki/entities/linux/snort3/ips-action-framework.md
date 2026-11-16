---
type: entity
tags: [snort3, ips, ips-action, action-framework, ids]
created:2026-06-08
sources: [github-snort3-actions-connectors]
---

# Snort3 IPS Action Framework (ips_action)

## 定义

Snort3 IPS Action Framework 是规则触发后的响应动作抽象，定义了 `IpsAction` 基类接口，每个 action 实现 `exec(Packet*)` 执行特定行为（alert/drop/reject/log/pass/sdrop 等）。Action 通过 `ActionManager` 注册并按 action_priority排序输出，logger负责把 action 结果写入统一的事件流。

##关键要点

- **`IpsAction` 基类**：`exec(Packet*)`、`get_action_type()`、`get_priority()`
- **ActionManager**：单例管理所有 IpsAction插件
- **Action 类型**：`alert`、`log`、`pass`、`drop`、`reject`、`sdrop`
- **优先级**：`ACTION_LOG_PRIORITY` 等决定多 action 并存时的输出顺序
- **Active vs Passive**：drop/reject/sdrop 需要 inline（active）模式
- **Module 配置**：每个 action 通常有 Module（如 `reject` 控制 TCP reset vs ICMP unreachable）

##核心概念

- **`exec(Packet*)` 返回值**：ACTION_HANDLE 或 ACTION_NONE
- **`alert`动作**：默认 logger 输出 +事件队列
- **`drop`动作**：通过 DAQ丢弃包（inline）
- **`reject`动作**：TCP reset 或 ICMP unreachable
- **`sdrop`动作**：静默丢弃（不告警）
- **`log`动作**：写入日志但不影响转发
- **`pass`动作**：规则匹配后停止本包检测

## 相关页面

- [[entities/linux/snort3/snort3-actions]] — Action总览
- [[entities/linux/snort3/snort3-framework]] —框架
- [[entities/linux/snort3/snort3-detection-engine]] —检测引擎
- [[entities/linux/snort3/snort3-runtime]] —运行时
