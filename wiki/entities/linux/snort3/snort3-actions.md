---
type: entity
tags: [snort3, intrusion-prevention, ids-ips]
created: 2026-05-27
sources: [github-snort3-actions-connectors]
---

# Snort3 Actions

## 定义

Snort3 IPS 动作是规则匹配时执行的操作。动作系统基于 [[ips_action.framework]] 基类，所有动作都是插件，通过 `PluginManager::load_plugins()` 动态加载。

## 动作类型

| 动作 | 优先级 | 流量丢弃 | 说明 |
|------|--------|----------|------|
| `alert` | 20 | No | 生成告警并记录匹配的数据包 |
| `log` | 10 | No | 仅记录数据包，不告警 |
| `pass` | 70 | No | 标记数据包为已通过，跳过后续检测 |
| `drop` | 40 | **Yes** | 丢弃数据包并生成告警 |
| `block` | 50 | **Yes** | 阻塞当前及后续同流数据包 |
| `reject` | 60 | **Yes** | 丢弃并发送 TCP Reset 或 ICMP 不可达 |
| `react` | 41 | **Yes** | 发送 HTML 页面后终止会话 |
| `rewrite` | 30 | No | 用 `replace` 选项内容覆盖数据包 |

### 优先级顺序（低→高）

```
OTHER(1) → LOG(10) → ALERT(20) → REWRITE(30) → DROP(40) → REACT(41) → BLOCK(50) → REJECT(60) → PASS(70)
```

## 核心类层次

### IpsAction 基类 (`framework/ips_action.h`)

```cpp
class IpsAction {
public:
    enum IpsActionPriority { IAP_OTHER=1, IAP_LOG=10, IAP_ALERT=20, ... };
    virtual void exec(Packet*, const ActInfo&) = 0;
    virtual bool drops_traffic();  // 默认 false
};
```

### IpsAction 派生类模式

每个动作实现：
- **`exec(Packet*, const ActInfo&)`** — 动作执行逻辑
- **`Module` 类** — 配置和统计（继承自 `snort::Module`）
- **`ActionApi` 结构** — 插件 API 描述
- **`snort_plugins[]`** — 插件入口点

### 聚合模块 (`actions_module.h`)

`ActionsModule` 聚合所有动作的计数器，提供统一的统计接口：
```cpp
static void add_action(std::string module_name, const PegInfo* pegs);
```

## 各动作详解

### alert — 告警

```cpp
class AlertAction : public IpsAction {
    void exec(Packet* p, const ActInfo& ai) override {
        alert(p, ai);           // 调用全局 alert() 函数
        ++alert_stats.alert;    // 更新统计
    }
};
```
- 总是调用 `alert()` 记录事件
- 不丢弃流量
- 无 `ActiveAction` 关联

### log — 日志

```cpp
void LogAction::exec(Packet* p, const ActInfo& ai) {
    if ( log_it(ai) ) {  // 检查是否需要日志
        log(p, ai);
        ++log_stats.log;
    }
}
```
- 仅在 `log_it(ai)` 返回 true 时记录
- 继承 `IpsAction::log()` 函数

### pass — 通过

```cpp
void PassAction::exec(Packet* p, const ActInfo& ai) {
    if ( log_it(ai) ) {
        pass();
        p->packet_flags |= PKT_PASS_RULE;  // 设置跳过标志
        ++pass_stats.pass;
    }
}
```
- 最高优先级动作（70）
- 设置 `PKT_PASS_RULE` 标志跳过后续规则匹配

### drop — 丢弃

```cpp
void DropAction::exec(Packet* p, const ActInfo& ai) {
    p->active->drop_packet(p);   // 主动丢弃
    p->active->set_drop_reason("ips");
    alert(p, ai);
    ++drop_stats.drop;
}
bool DropAction::drops_traffic() override { return true; }
```
- 实现 `drops_traffic()` 返回 true
- 调用 `Active::drop_packet()` 丢弃

### block — 阻塞会话

```cpp
void BlockAction::exec(Packet* p, const ActInfo& ai) {
    p->active->block_session(p);  // 阻塞整个会话
    p->active->set_drop_reason("ips");
    alert(p, ai);
    ++block_stats.block;
}
```
- 调用 `block_session()` 阻塞双向流量
- 比 `drop` 更彻底

### reject — 拒绝 + 重置

```cpp
class RejectAction : public IpsAction {
    RejectAction(uint32_t f = REJ_RST_BOTH);
    void exec(Packet* p, const ActInfo& ai) override;
};

enum { REJ_RST_SRC=0x01, REJ_RST_DST=0x02, REJ_UNR_NET=0x04, REJ_UNR_HOST=0x08, REJ_UNR_PORT=0x10 };
```
- 支持配置：`reset`（none/source/dest/both）和 `control`（none/network/host/port/forward/all）
- 使用 `ActiveAction` 延迟执行 TCP Reset / ICMP 不可达
- 可同时发送 Reset 和 Unreachable

### react — 响应 + 终止

```cpp
void ReactAction::exec(Packet* p, const ActInfo& ai) {
    p->active->drop_packet(p);
    alert(p, ai);
    ++react_stats.react;
}
```
- 发送自定义 HTML 页面后终止会话
- 使用 `PayloadInjector::inject_http_payload()` 注入 HTTP 响应
- 支持 HTTP2 流

### rewrite — 重写

```cpp
void ReplaceAction::exec(Packet* p, const ActInfo& ai) {
    p->active->rewrite_packet(p);
    alert(p, ai);
    ++replace_stats.replace;
}
```
- 调用 `DetectionEngine::get_replacement()` 获取替换数据
- 使用 `Replace_ModifyPacket()` 修改数据包内容
- 设置 `PKT_MODIFIED` 标志

## 插件注册

```cpp
// ips_actions.cc
void load_actions() {
    PluginManager::load_plugins(act_alert);
    PluginManager::load_plugins(act_block);
    PluginManager::load_plugins(act_drop);
    PluginManager::load_plugins(act_file_id);
    PluginManager::load_plugins(act_log);
    PluginManager::load_plugins(act_pass);
    PluginManager::load_plugins(act_react);
    PluginManager::load_plugins(act_reject);
    PluginManager::load_plugins(act_replace);
}
```

## 相关概念

- [[snort3-connectors]] — 动作的数据导出机制
- [[snort3-detection-engine]] — 检测引擎触发动作执行
- [[snort3-framework]] — 插件系统、IpsAction 基类
- [[snort3-events-filters]] — 动作的触发来源（事件队列）
