---
type: entity
tags: [snort, ids-ips, rule-language, intrusion-detection, syntax]
created:2026-06-08
sources: [github-snort3-detection]
---

# Snort Rule Language

## 定义

Snort规则语言（Snort Rule Language）是编写 Snort3 IDS/IPS规则的 DSL，单条规则语法为 `action proto src_ip src_port -> dst_ip dst_port (options)`。规则由三部分组成：**Rule Header**（动作+协议+地址+端口+方向）、**Rule Options**（告警信息+检测约束，括号内）、**Rule Action**（触发后行为：alert/log/pass/drop/reject/sdrop）。

##关键要点

- **Rule Header**：`action proto src_addr src_port direction dst_addr dst_port`
- **Rule Options**：检测条件（`msg`、`sid`、`content`、`pcre`、`flow`）+ 元数据（`classtype`、`reference`、`metadata`）
- **Rule Action**：`alert`（告警+记录）、`log`（仅记录）、`pass`（忽略）、`drop`（阻断+记录）、`reject`（阻断+RST）、`sdrop`（静默丢弃）
- **变量定义**：`var HOME_NET [192.168.0.0/16,10.0.0.0/8]`、`portvar HTTP_PORTS [80,8080]`
- **规则链**：Snort3 支持 chained rules（前导规则匹配后才有后续）
- **配置文件**：`snort.lua` 中 `ips.include`路径、规则类别（`category`）

##核心概念

- **检测选项**：`content`（模式）、`pcre`（正则）、`byte_test`/`byte_jump`、`flow`（方向）、`http_*`、`dns_*`（协议专用）
- **元数据选项**：`msg`（告警消息）、`sid`（规则ID，唯一）、`rev`（修订号）、`classtype`、`reference:cve,...`、`metadata`
- **阈值抑制**：`detection_filter:track by_src, count5, seconds60`
- **服务标识**：Snort3 用 `service:` 选项（取代 Snort2 preprocessor）
- **Fast Pattern**：`fast_pattern` 选项指定 fast pattern matcher使用的 pattern
- **规则变量**：`var`、`portvar`、动态引用 `$HOME_NET`

## 相关页面

- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-ips-options]] — IPS选项
- [[entities/linux/snort3/snort3-actions]] —规则动作
- [[entities/linux/snort3/snort3-framework]] — Snort3框架
