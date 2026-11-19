---
type: entity
tags: [snort3, linux, security, nids, architecture]
created: 2026-06-21
sources: [github-snort3-service-inspectors]
---

# Snort3 Deep Architecture

> **状态**: 🚧 占位 stub — 此总览页已被 `snort3-service-inspectors.md` 与 `linux-intrusion-detection.md` 引用,
> 作为 snort3 子树的"整体架构"入口。整合完成后请删除此状态标记。

## 定义

Snort3 (Snort++ ) 的**整体架构综合视图**: 从数据包入口, 经DAQ → packet processing → inspector 链 →
detection engine → action framework → output, 把分散在 `entities/linux/snort3/` 下的 29 个细节实体
串成一条可线性阅读的主干。对应 [[linux-intrusion-detection]] 的 NIDS 架构章节。

## 架构主干 (待填充详图)

> 数据流: `DAQ capture → packet-thread → ports/inspectors chain → detection → actions → log/alert`

| 层 | 实体 | 说明 |
|----|------|------|
| 抓包 | [[snort3-packet-processing]] / [[packet-capture]] | DAQ 与 packet thread 模型 |
| 解码 | [[snort3-codecs]] | 协议解码器 |
| Stream | [[snort3-stream]] / [[stream-reassembly]] | 流跟踪与重组 |
| Inspector | [[snort3-inspectors]] / [[snort3-service-inspectors]] / [[snort3-net-inspectors]] | 检查器链 |
| Flow | [[snort3-flow]] | 流状态机 |
| 检测 | [[snort3-detection-engine]] / [[snort-rule-language]] | 规则匹配 |
| 动作 | [[snort3-actions]] / [[snort3-events-filters]] / [[ips-action-framework]] | 命中后动作 |
| 框架/运行时 | [[snort3-framework]] / [[snort3-infrastructure]] / [[snort3-runtime]] / [[snort3-control-startup]] | 控制平面 |
| 内存/日志 | [[snort3-mempool]] / [[snort3-pubsub-log]] / [[snort3-parser-search]] | 辅助子系统 |

## 主要发现

> 待填充: 各子系统的耦合点、关键数据结构、性能瓶颈、与 Snort2 的架构差异。

## 相关页面

- [[snort3]] — snort3 主题入口
- [[linux-intrusion-detection]] — 上层 IDS/IPS 语境
- [[snort3-framework-analysis]] — 框架级深度分析
