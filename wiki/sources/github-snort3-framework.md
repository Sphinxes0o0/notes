---
type: source
source-type: github
title: "Snort3 Intrusion Detection System — Framework Module"
author: "Cisco / Snort Team"
date: 2026-04-08
size: medium
path: ~/workspace/github/snort3/src/framework/
summary: "Snort3 核心框架源码分析：插件系统 (Inspector/Codec/IpsOption)、Module 生命周期、数据驱动配置、Packet Thread (pig)、Shell 命令接口、DataBus 事件系统"
---

# Snort3 Framework 源码分析

## 核心文件列表

| 文件 | 关键内容 |
|------|---------|
| `inspector.h/cc` | Inspector 基类，插件主接口 |
| `module.h/cc` | Module 基类，数据驱动配置 |
| `codec.h/cc` | 协议编解码器插件 |
| `ips_option.h/cc` | IPS 规则选项 |
| `ips_action.h/cc` | IPS 规则动作 |
| `pig_pen.h/cc` | Packet thread 统一入口 |
| `data_bus.h/cc` | 进程内事件发布-订阅 |
| `mp_data_bus.h/cc` | 多进程事件同步 |
| `cursor.h/cc` | 规则评估缓冲区指针 |
| `parameter.h/cc` | 配置参数系统 |
| `value.h` | Lua 值类型桥接 |
| `base_api.h` | 所有插件 API 的基类 |
| `plugins.h` | 插件头文件汇总 |

## 架构设计要点

### 插件版本管理

所有插件 API 通过 `BASE_API_VERSION << 16 | plugin_version` 实现版本化，每个插件类型有独立版本号：

```cpp
#define BASE_API_VERSION 22
#define INSAPI_VERSION ((BASE_API_VERSION << 16) | 3)   // Inspector
#define IPSAPI_VERSION ((BASE_API_VERSION << 16) | 3)   // IpsOption
#define CDAPI_VERSION ((BASE_API_VERSION << 16) | 2)    // Codec
```

### BaseApi 结构

所有插件 API 的公共前缀：

```cpp
struct BaseApi
{
    PlugType type;           // PT_INSPECTOR, PT_CODEC, etc.
    uint32_t size;           // sizeof(plugin-api)
    uint32_t api_version;    // 版本号
    uint32_t version;        // 插件版本
    uint64_t reserved;       // 未来扩展
    const char* options;     // API 选项
    const char* name;        // 插件名
    const char* help;        // 帮助文本
    ModNewFunc mod_ctor;     // Module 创建函数
    ModDelFunc mod_dtor;     // Module 销毁函数
};
```

### 数据驱动配置

Module 系统通过 Lua 配置表递归解析：

```
begin() → set() [多次] → end()
```

- `begin(fqn, idx, cfg)` — 表/列表开始时调用
- `set(param, value, cfg)` — 参数赋值
- `end(fqn, idx, cfg)` — 表/列表结束时调用

### 统计系统

PegInfo 定义三类计数：

```cpp
enum CountType { SUM, NOW, MAX };
// SUM: 累计总数 (e.g., packets)
// NOW: 当前快照 (e.g., current sessions)
// MAX: 历史峰值 (e.g., max sessions)
```

### InspectionBuffer 类型

规则选项使用的缓冲区类型：

```cpp
enum Type {
    IBT_VBA, IBT_JS_DATA,  // 通用规则选项
    IBT_KEY, IBT_HEADER, IBT_BODY  // 已废弃
};
```

## 相关页面

- [[entities/linux/snort3/snort3-framework]] — 实体页面
- [[intrusion-detection-system]] — IDS 概念
