---
title: "Snort3 网络层检查器 (Network Inspectors)"
description: "网络层检查器是Snort3中处理链路层到网络层协议分析的核心组件,负责数据包的初步解码、协议验证和异常检测。"
---
# Snort3 网络层检查器 (Network Inspectors)

网络层检查器是Snort3中处理链路层到网络层协议分析的核心组件,负责数据包的初步解码、协议验证和异常检测。

## 1. 概述

**代码规模**: 约 90,694 行代码

**子模块列表**:
| 模块 | 描述 |
|------|------|
| `arp_spoof` | ARP欺骗检测 |
| `binder` | 流量绑定与服务识别 |
| `extractor` | 元数据提取 |
| `normalize` | 数据包规范化 |
| `packet_capture` | 数据包捕获 |
| `perf_monitor` | 性能监控 |
| `port_scan` | 端口扫描检测 |
| `reputation` | IP信誉评估 |
| `rna` | 响应网络分析 |
| `snort_ml` | 机器学习检测 |
| `appid` | 应用识别 |

## 2. 类层次结构

### 2.1 基类: Inspector

所有网络检查器继承自 `snort::Inspector` 基类(`framework/inspector.h`):

```cpp
class SO_PUBLIC Inspector
{
public:
    virtual ~Inspector();
    virtual bool configure(SnortConfig*) { return true; }
    virtual void tear_down(SnortConfig*, bool) { }
    virtual bool disable(SnortConfig*) { return false; }
    virtual void show(const SnortConfig*) const { }
    virtual void tinit() { }      // 线程初始化
    virtual void tterm() { }      // 线程终止
    virtual void eval(Packet*) = 0; // 数据包处理
    virtual bool ready_to_process(Packet* p);
};
```

### 2.2 PerfMonitor 类

```cpp
class PerfMonitor : public snort::Inspector
{
public:
    PerfMonitor(PerfConfig*);
    bool configure(snort::SnortConfig*) override;
    void show(const snort::SnortConfig*) const override;
    void eval(snort::Packet*) override;
    bool ready_to_process(snort::Packet* p);
    void tinit() override;
    void tterm() override;
    void update_trackers();
    void rotate();
    void swap_constraints(PerfConstraints*);
    PerfConstraints* get_original_constraints();
    void enable_profiling(PerfConstraints*);
    void disable_profiling(PerfConstraints*);
    FlowIPTracker* get_flow_ip();

private:
    PerfConfig* const config;
    void disable_tracker(size_t);
};
```

### 2.3 Binder 类

Binder负责将流量绑定到正确的服务检查器:

```cpp
class Binder
{
public:
    Binder(BindModule*);
    ~Binder();

    void tinit();
    void tterm();
    void eval(Packet*);

private:
    void check_policy(Packet*, Flow*, BindWhen&, BindUse&);
    void configure_services(Packet*, Flow*, Binding*, bool);
    Inspector* get_gadget(const SnortProtocolId protocol_id);

    BindModule* module;
    std::vector<Binding*> bindings[2];
    // ...
};
```

### 2.4 PortScan 类

```cpp
class PortScanLogger
{
public:
    virtual void log(PS_EVENT_TYPE, uint32_t, uint8_t, uint32_t,
        uint32_t, uint8_t, time_t) = 0;
    // ...
};

class PortScan
{
public:
    PortScan(PortScanModule*);
    void tinit();
    void tterm();
    void eval(Packet*);

private:
    void update(PS大同小异, Packet*);
    void process(PS_EVENT_TYPE, Packet*);

    PortScanConfig* config;
    PortScanLogger* logger;
    // ...
};
```

## 3. 核心数据结构

### 3.1 规范化标志 (Normalize)

`normalize/normalize.h` 定义了数据包规范化选项:

```cpp
enum NormFlags
{
    NORM_IP4_BASE        = 0x00000001,  // 基础IP4规范化
    NORM_IP4_DF          = 0x00000004,  // 清除DF标志
    NORM_IP4_RF          = 0x00000008,  // 清除RF标志
    NORM_IP4_TTL         = 0x00000010,  // 确保最小TTL
    NORM_IP4_TOS         = 0x00000020,  // 清除TOS
    NORM_IP4_TRIM        = 0x00000040,  // 强制最小帧长度

    NORM_IP6_BASE        = 0x00000100,
    NORM_IP6_TTL         = 0x00000200,

    NORM_TCP_ECN_PKT     = 0x00001000,  // 清除ECE和CWR
    NORM_TCP_URP         = 0x00004000,  // 根据dsize修剪URP
    NORM_TCP_OPT         = 0x00008000,  // NOP覆盖非必要选项
    NORM_TCP_IPS         = 0x00010000,  // 启用流规范化/预确认刷新

    NORM_ALL             = 0xFFFFFFFF,
};
```

### 3.2 绑定条件 (Binding)

`binder/binding.h` 定义了流量绑定规则:

```cpp
class BindWhen
{
public:
    enum class Role { BR_CLIENT, BR_SERVER };

    enum class Criteria
    {
        BWC_IPS_ID,      // IPS策略ID
        BWC_VLANS,       // VLAN ID
        BWC_SRC_IP,      // 源IP
        BWC_DST_IP,      // 目标IP
        BWC_SRC_PORT,    // 源端口
        BWC_DST_PORT,    // 目标端口
        BWC_PROTOCOL,    // 协议
        BWC_GID,         // 规则组ID
        BWC_SID,         // 规则签名ID
        BWC_CLASS,       // 类别
        BWC_PRIORITY,    // 优先级
    };

    Role role;
    uint32_t ips_id_user;
    std::bitset<4096> vlans;
    sfip_var_t* src_ip = nullptr;
    sfip_var_t* dst_ip = nullptr;
    // ...
};

class BindUse
{
public:
    enum class Action { BA_RESET, BA_BLOCK, BA_ALLOW };
    Action action;
    Inspector* svc = nullptr;
    // ...
};
```

### 3.3 主机属性 (HostAttributes)

`target_based/host_attributes.h`:

```cpp
class HostAttributesDescriptor
{
public:
    bool update_service(uint16_t port, uint16_t protocol,
        SnortProtocolId, bool& updated, bool is_appid_service = false);
    void clear_appid_services();
    void get_host_attributes(uint16_t protocol, uint16_t port, HostAttriInfo*) const;
};

struct HostAttributeStats
{
    PegCount total_hosts = 0;
    PegCount hosts_pruned = 0;
    PegCount dynamic_host_adds = 0;
    PegCount dynamic_service_adds = 0;
    PegCount dynamic_service_updates = 0;
    PegCount service_list_overflows = 0;
};
```

## 4. 核心函数

### 4.1 Binder::eval()

```cpp
void Binder::eval(Packet* p)
{
    THREAD_LOCAL ProfileStats bindPerfStats;
    Profile profile(bindPerfStats);

    if ( !p->flow || p->is_frag() )
        return;

    Flow* flow = p->flow;
    Binding* binding = match(flow, p);

    if ( binding->when.role == BindWhen::BR_CLIENT )
        configure_services(p, flow, binding, false);
    else if ( binding->when.role == BindWhen::BR_SERVER )
        configure_services(p, flow, binding, true);

    check_policy(p, flow, binding->when, binding->use);
}
```

### 4.2 PortScan::update()

```cpp
void PortScan::update(PS_MEMORY_TYPE* ps, Packet* p)
{
    switch (ps->type)
    {
    case PS_TYPE_IP:
        UpdateIpScanner(&ps->ps_ip, p);
        UpdateIpProbes(&ps->ps_ip, p);
        break;
    case PS_TYPE_TCP:
        UpdateTcpScanner(&ps->ps_tcp, p);
        UpdateTcpProbes(&ps->ps_tcp, p);
        break;
    case PS_TYPE_UDP:
        UpdateUdpScanner(&ps->ps_udp, p);
        UpdateUdpProbes(&ps->ps_udp, p);
        break;
    case PS_TYPE_ICMP:
        UpdateIcmpScanner(&ps->ps_icmp, p);
        UpdateIcmpProbes(&ps->ps_icmp, p);
        break;
    }
}
```

### 4.3 ARP Spoof 检测

```cpp
static const IPMacEntry* LookupIPMacEntryByIP(
    const IPMacEntryList& ipmel, uint32_t ipv4_addr)
{
    auto it = std::find_if(ipmel.cbegin(), ipmel.cend(),
        [ipv4_addr](const IPMacEntry& entry)
        { return entry.ipv4_addr == ipv4_addr; });
    return (it != ipmel.cend()) ? &(*it) : nullptr;
}
```

## 5. 关键文件清单

| 文件 | 行数 | 描述 |
|------|------|------|
| `perf_monitor/perf_monitor.cc` | ~2500 | 性能监控主实现 |
| `perf_monitor/perf_monitor.h` | 72 | 性能监控类定义 |
| `binder/binder.cc` | ~1200 | 流量绑定核心 |
| `port_scan/port_scan.cc` | ~1500 | 端口扫描检测 |
| `normalize/normalize.cc` | ~800 | 数据包规范化 |
| `arp_spoof/arp_spoof.cc` | ~600 | ARP欺骗检测 |
| `reputation/reputation.cc` | ~2000 | IP信誉模块 |
| `rna/rna_*` | ~5000 | 响应网络分析 |
| `extractor/extractor.cc` | ~1500 | 元数据提取 |
| `packet_capture/packet_capture.cc` | 695 | 数据包捕获 |
| `snort_ml/snort_ml_*.cc` | ~1000 | ML检测模块 |

## 6. 线程本地变量

每个检查器使用 `THREAD_LOCAL` 存储线程特定数据:

```cpp
THREAD_LOCAL ProfileStats bindPerfStats;
THREAD_LOCAL ProfileStats arpPerfStats;
THREAD_LOCAL ProfileStats portScanPerfStats;
```

## 7. 配置接口

检查器通过模块进行配置,每个检查器对应一个模块:

```cpp
class PerfModule : public snort::Module
{
public:
    PerfModule();
    ~PerfModule() override;

    bool set(const char*, Value&, SnortConfig*) override;
    bool endOfDef(const char*, bool, SnortConfig*) override;

    PerfConfig* get_config();

    ProfileStats* get_stats() const;
    void process_command(const char*, ControlConn*);
};
```

## 8. 使用示例

### 8.1 注册检查器

```cpp
// network_inspectors.cc
void load_network_inspectors()
{
    // 注册Binder
    Binder::bind_module = new BindModule();
    InspectorManager::register_inspector(
        new Binder(Binder::bind_module), "binder");

    // 注册PortScan
    PortScanModule* port_scan_module = new PortScanModule();
    InspectorManager::register_inspector(
        new PortScan(port_scan_module), "port_scan");

    // 注册PerfMonitor
    PerfModule* perf_module = new PerfModule();
    InspectorManager::register_inspector(
        new PerfMonitor(perf_module->get_config()), "perf_monitor");
}
```

### 8.2 匹配绑定

```cpp
Binding* Binder::match(Flow* flow, Packet* p)
{
    for ( auto* binding : bindings[0] )
    {
        if ( match_when(flow, p, binding->when) )
            return binding;
    }
    return default_binding;
}
```

## 9. 与其他模块的关系

```
┌─────────────────────────────────────────────────────────────┐
│                      Packet I/O                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Network Inspectors                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │  Binder  │ │PortScan  │ │ ARP Spoof│ │Normallizer   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │PerfMonitor│ │ RNA     │ │AppId     │ │ Reputation   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Inspectors                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │HTTP Inspect│ │   DNS   │ │   SMTP   │ │     SSH      │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 10. 总结

网络层检查器是Snort3架构中的核心组件,负责:

1. **协议验证** - ARP/IP/TCP等协议的合法性检查
2. **异常检测** - 端口扫描、ARP欺骗等攻击识别
3. **流量绑定** - 将流量正确路由到对应的服务检查器
4. **性能监控** - 跟踪Snort各组件的执行性能
5. **数据包规范化** - 标准化数据包以消除编码差异

这些检查器通过继承 `Inspector` 基类实现统一的接口,使用 `eval()` 方法处理数据包,并通过 `tinit()`/`tterm()` 进行线程生命周期管理。
