---
type: source
source-type: github
title: Snort3 Network Inspectors & Packet I/O
author: Cisco Talos
date: 2024
size: medium
path: ~/workspace/github/snort3/src/network_inspectors/
summary: Snort3 367个网络inspector源文件 + 25个packet_io源文件，深入分析架构模式、核心inspectors（ARP/IP/ICMP）、DAQ抽象层
created: 2024
tags: []
---
# Snort3 Network Inspectors & Packet I/O 源码分析

## 概述

对 `/Users/sphinx.shi/workspace/github/snort3/src/network_inspectors/`（367文件）和 `src/packet_io/`（25文件）的深度分析。

---

## Network Inspectors 目录结构

```
network_inspectors/
├── network_inspectors.cc      # 插件入口，load_network_inspectors()
├── arp_spoof/                 # ARP 欺骗检测
├── binder/                    # 流量绑定协调器（核心）
├── normalize/                 # 数据包规范化
├── packet_capture/            # PCAP 捕获
├── perf_monitor/             # 性能监控
├── port_scan/                 # 端口扫描检测
├── reputation/               # IP 信誉
├── appid/                     # 应用识别（85文件，最大）
├── extractor/                 # 元数据提取
├── rna/                       # 指纹识别
└── snort_ml/                  # ML 检测
```

---

## 插件注册机制

**入口**: `network_inspectors.cc::load_network_inspectors()`

```cpp
void load_network_inspectors() {
    PluginManager::load_plugins(network_inspectors);
    PluginManager::load_plugins(nin_appid);
    PluginManager::load_plugins(nin_extractor);
    // ...
}
```

每个 inspector 导出 `BaseApi*` 指针数组：

```cpp
const BaseApi* nin_arp_spoof[] = {
    &as_api.base,
    nullptr
};
```

---

## 核心文件清单

### Network Inspectors

| 文件 | 用途 |
|------|------|
| `network_inspectors.cc` | 插件加载入口 |
| `arp_spoof/arp_spoof.cc` | ARP 欺骗检测器 |
| `arp_spoof/arp_module.cc` | ARP 模块配置 |
| `binder/binder.cc` | 流量绑定协调器（最重要的 inspector） |
| `binder/binding.h` | 绑定规则结构体 |
| `normalize/normalize.cc` | 数据包规范化器 |
| `packet_capture/pcap.cc` | PCAP 捕获 |

### Packet I/O

| 文件 | 用途 |
|------|------|
| `sfdaq.h/cc` | DAQ 包装器（主接口） |
| `sfdaq_instance.h/cc` | 每线程 DAQ 实例 |
| `sfdaq_module.h/cc` | DAQ Snort 模块 |
| `sfdaq_config.h/cc` | DAQ 配置结构 |
| `active.h/cc` | 主动响应处理 |
| `active_action.h` | 延迟主动响应基类 |
| `packet_tracer.h/cc` | 包追踪调试 |
| `packet_constraints.h/cc` | 追踪器过滤约束 |
| `trough.h/cc` | 包源发现 |

### Framework（Inspector 基类）

| 文件 | 用途 |
|------|------|
| `framework/inspector.h` | Inspector 基类 |
| `framework/module.h` | Module 基类 |
| `framework/decode_data.h` | 协议位定义 |
| `framework/data_bus.h` | DataBus 发布/订阅 |

---

## 关键实现细节

### ARP Spoof 检测逻辑

```cpp
// arp_spoof.cc 核心检测
if (is_unicast(p, arph)) {
    if (!ethernet_mac_match(p, arph)) {
        DetectionEngine::queue_event(GID_ARP_SPOOF, ARP_SPOOF_SRC_MAC);
    }
}
```

### Binder 绑定规则

```cpp
struct BindWhen {
    PolicyId ips_id;
    unsigned protos;           // PROTO_BIT__TCP 等
    Role role;                // BR_CLIENT, BR_SERVER, BR_EITHER
    std::string svc;          // 服务名
    sfip_var_t* src_nets;
    sfip_var_t* dst_nets;
    PortBitSet src_ports;
    PortBitSet dst_ports;
};

struct BindUse {
    enum Action { BA_RESET, BA_BLOCK, BA_ALLOW, BA_INSPECT };
    std::string svc;
    Action action;
    Inspector* inspector;
};
```

### SFDAQ 批量收包

```cpp
// sfdaq_instance.cc
uint32_t batch_size = cfg->get_batch_size();  // 默认64
DAQ_RecvStatus rstat = instance->receive_messages(max_recv);
while (DAQ_Msg_h msg = instance->next_message()) {
    // 解码和处理
    instance->finalize_message(msg, verdict);
}
```

### Active 响应类型

```cpp
enum ActionType {
    ACT_TRUST, ACT_ALLOW, ACT_HOLD, ACT_RETRY,
    ACT_REWRITE, ACT_DROP, ACT_BLOCK, ACT_RESET
};

void Active::drop_packet(const Packet*, bool force = false);
void Active::reset_session(Packet*, bool force = false);
void Active::send_reset(Packet*, EncodeFlags);
void Active::inject_data(Packet*, EncodeFlags, const uint8_t* buf, uint32_t len);
```

---

## 相关页面

- [[snort3-net-inspectors]] — 架构概念页
- [[snort3]] — Snort3 总览
