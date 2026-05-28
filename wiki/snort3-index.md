---
type: index
tags: [snort3, ids, ips, intrusion-detection, network-security]
created: 2026-05-27
---

# Snort3 Module Index

> Snort3 入侵检测/防御系统（IDS/IPS）源码分析，共 10 个 entity 页面。

## Entity 索引

| Entity | Domain | Key Concepts |
|--------|--------|--------------|
| [[entities/linux/snort3/snort3-framework]] | 核心框架 | 插件架构（Codec/Inspector/IpsOption/Action/Logger/Connector/Mpse）、Module 生命周期、pig 线程封装、Lua Shell、DataBus 事件系统 |
| [[entities/linux/snort3/snort3-detection-engine]] | 检测引擎 | Fast Pattern、MPSE 批量搜索、Detection Option Tree、IpsContext、Port Rule Map、Regex Offload |
| [[entities/linux/snort3/snort3-ips-options]] | IPS 选项 | content/pcre/byte_test/flowbits/detection_filter、选项树求值、Cursor 系统、变量提取 |
| [[entities/linux/snort3/snort3-actions]] | 动作系统 | alert/log/pass/drop/block/reject/react/rewrite、优先级链、IpsAction 基类、Active 动作执行 |
| [[entities/linux/snort3/snort3-events-filters]] | 事件与过滤 | SF_EVENTQ 环形队列、HostTracker（LRU 分段缓存）、Detection/Rate/Event 三层过滤器 |
| [[entities/linux/snort3/snort3-flow]] | Flow 追踪 | FlowCache ZHash 表、FlowKey 超时淘汰、角色追踪、Session 抽象、流状态机 |
| [[entities/linux/snort3/snort3-connectors]] | 连接器 | file/tcp/unixdomain/std connector、双工通信、异步接收、Ring buffer、HA 数据导出 |
| [[entities/linux/snort3/snort3-infrastructure]] | 基础设施 | XHash/ZHash/GHash、File API 三阶段管道、PDF/SWF/ZIP/OLE 解压、JS Normalization、MemCapAllocator |
| [[entities/linux/snort3/snort3-codecs]] | 协议编解码 | Ethernet/VLAN/MPLS/IPv4/IPv6/TCP/UDP/ICMP/GTP/VXLAN/GENEVE 解码树、隧道旁路 |
| [[snort3-control-startup]] | 控制与启动 | Lua Shell + ControlConn 双层架构、pig 状态机（NEW→INITIALIZED→STARTED→RUNNING）、零宕机配置重载、epoll/poll 事件驱动 |

## Cross-Reference Map

```
snort3-framework
├── snort3-detection-engine
├── snort3-ips-options
├── snort3-codecs
├── snort3-infrastructure
├── snort3-control-startup
└── snort3-actions

snort3-detection-engine
├── snort3-actions
├── snort3-ips-options
├── snort3-events-filters
├── snort3-flow
├── snort3-connectors
└── snort3-infrastructure

snort3-actions
├── snort3-connectors
├── snort3-detection-engine
├── snort3-framework
└── snort3-events-filters

snort3-events-filters
├── snort3-framework
├── snort3-actions
├── snort3-flow
└── snort3-ips-options

snort3-flow
├── snort3-ips-options
└── snort3-framework

snort3-connectors
├── snort3-actions
├── snort3-detection-engine
└── snort3-framework

snort3-infrastructure
├── snort3-actions
├── snort3-connectors
├── snort3-events-filters
├── snort3-flow
├── snort3-ips-options
├── snort3-framework
└── snort3-control-startup

snort3-codecs
├── snort3-infrastructure
└── snort3-detection-engine

snort3-ips-options
├── snort3-flow
└── snort3-framework

snort3-control-startup
├── snort3-framework
├── snort3-actions
├── snort3-connectors
├── snort3-events-filters
├── snort3-flow
└── snort3-ips-options
```

## Sources

| Source | 文件数 | 描述 |
|--------|--------|------|
| [[github-snort3-framework]] | ~30 | framework/ 目录：codec.h、module.h、connector.h、 pig、shell |
| [[github-snort3-detection]] | ~25 | detection/ 目录：fp_detect、detection_options、ips_context、pcrm |
| [[github-snort3-flow-ips]] | ~15 | flow/ 和 ips_options/ 目录：flow_cache、flow、ips_content、ips_pcre |
| [[github-snort3-actions-connectors]] | ~20 | actions/ 和 connectors/ 目录：alert/drop/pass/reject、file/tcp_connector |
| [[github-snort3-events-filters]] | ~26 | events/、host_tracker/、filters/ 目录：sfeventq、host_cache、rate_filter |
| [[github-snort3-infrastructure]] | ~80 | helpers/hash/file_api/decompress/js_norm/ 目录 |
| [[github-snort3-codecs]] | ~25 | codecs/ 目录：root/link/ip/misc 各层 codec |
| [[github-snort3-control-startup]] | ~15 | main/ 和 control/ 目录：snort.cc、main.cc、control_mgmt |
