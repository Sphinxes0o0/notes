---
type: entity
tags: [snort, ids-ips, framework, architecture, modular]
created:2026-06-08
sources: [github-snort3-framework]
---

# Snort3 Framework Analysis

## 定义

Snort3框架分析聚焦 Snort3架构的模块化设计：插件化 Inspector/IpsAction/Codec/Logger/Connector 系统、Module 配置驱动、Packet Inspection Graph（pig）多线程模型、Managers 单例生命周期管理。框架是 Snort2 → Snort3 重构的核心成果，目标是可扩展性+性能+易维护。

##关键要点

- **模块化**：8+ 种插件类型（Inspector/IpsAction/IpsOption/Codec/Logger/Connector/Mpse/PolicySelector）
- **BaseApi + 版本宏**：每类插件独立 API（`INSAPI_VERSION`、`ACTAPI_VERSION`等）
- **数据驱动配置**：Module 类解析 Lua配置参数（Parameter 系统）
- **Pig (Packet Inspection Graph)**：单包处理线程，调用 inspector链
- **Manager 单例**：PluginManager / InspectorManager / ModuleManager静态表
- **Lua集成**：配置、script rule、动态加载

##核心概念

- **`SnortConfig`**：全局配置对象，多实例支持（reload）
- **configure → start → [reload] → stop**：模块生命周期
- **`PigPen::idle()`**：包处理主循环
- **inspector eval链**：binder → network → service → detect
- **log 输出**：Logger插件（alert_fast/alert_unified/alert_syslog）
- **包捕获 (DAQ)**：跨平台抽象（pcap/afpacket/nfqueue/dpdk）
- **Reload 支持**：inspector 可在运行时替换（reload inspectors）

## 相关页面

- [[entities/linux/snort3/snort3-framework]] —框架总览
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-runtime]] —运行时
- [[entities/linux/snort3/snort3-infrastructure]] —基础设施
- [[sources/github-snort3-framework]] — Snort3框架源码
