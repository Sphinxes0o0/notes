---
type: entity
tags: [snort3, ids-ips, detection-options, content-matching]
created: 2026-05-27
sources: [github-snort3-flow-ips]
---

# Snort3 IPS Options

## 定义

IPS options 是 Snort3 检测规则中的匹配选项，在数据包的 payload、header 或 flow 状态上执行匹配操作。选项通过插件架构注册，支持 content、pcre、byte_test、flow 等多种类型，按树形结构求值。

## 关键要点

### 选项类型分类

#### Content Matching（内容匹配）

| 选项 | 文件 | 说明 |
|------|------|------|
| `content` | `ips_content.cc` | Boyer-Moore 快速模式匹配 |
| `pcre` | `ips_pcre.cc` | PCRE2 正则表达式 |
| `regex` | `ips_regex.cc` | Hyperscan regex（可用时） |
| `sd_pattern` | `ips_sd_pattern.cc` | Hyperscan 模式匹配 |

#### Byte Operations（字节操作）

| 选项 | 文件 | 说明 |
|------|------|------|
| `byte_test` | `ips_byte_test.cc` | 提取字节并与值比较 |
| `byte_jump` | `ips_byte_jump.cc` | 提取字节并跳转游标位置 |
| `byte_extract` | `ips_byte_extract.cc` | 提取字节存入变量 |
| `byte_math` | `ips_byte_math.cc` | 对提取的字节执行算术运算 |

#### Flow/State（流/状态）

| 选项 | 文件 | 说明 |
|------|------|------|
| `flow` | `ips_flow.cc` | 检查会话属性（established、stateless 等） |
| `flowbits` | `ips_flowbits.cc` | 在会话上设置/检查布尔标志 |
| `detection_filter` | `ips_detection_filter.cc` | 告警前限速 |

#### Payload Data（载荷数据）

| 选项 | 文件 | 说明 |
|------|------|------|
| `file_data` | `ips_file_data.cc` | 设置游标到文件数据缓冲区 |
| `raw_data` | `ips_raw_data.cc` | 设置游标到原始数据包数据 |
| `pkt_data` | `ips_pkt_data.cc` | 设置游标到规范化数据包数据 |
| `base64_decode` | `ips_base64.cc` | Base64 解码 |

#### Other

| 选项 | 文件 | 说明 |
|------|------|------|
| `dsize` | `ips_dsize.cc` | 检查 payload 大小 |
| `isdataat` | `ips_isdataat.cc` | 检查指定偏移是否有数据 |
| `so` | `ips_so.cc` | 调用自定义 SO eval 函数 |
| `replace` | `ips_replace.cc` | 替换 payload 数据 |
| `tag` | `ips_tag.cc` | 记录额外数据包 |

### IpsOption 基类

```cpp
class IpsOption
{
    virtual ~IpsOption() = default;
    virtual uint32_t hash() const;
    virtual bool operator==(const IpsOption&) const;

    // packet threads
    virtual bool is_relative() { return false; }
    virtual bool retry(Cursor&) { return false; }
    virtual void action(Packet*) { }

    enum EvalStatus { NO_MATCH, MATCH, NO_ALERT, FAILED_BIT };
    virtual EvalStatus eval(Cursor&, Packet*) { return MATCH; }

    virtual CursorActionType get_cursor_type() const;
    virtual PatternMatchData* get_pattern(SnortProtocolId, RuleDirection);
    // ...
};
```

**返回类型**：
- `MATCH` — 匹配成功，继续求值子节点
- `NO_MATCH` — 匹配失败，立即返回
- `NO_ALERT` — 匹配成功但不生成告警（用于 flowbits:noalert）
- `FAILED_BIT` — flowbit 检查失败，需重求值

**CursorActionType**：`CAT_NONE`、`CAT_READ`、`CAT_ADJUST`、`CAT_SET_OTHER`、`CAT_SET_RAW`、`CAT_SET_FAST_PATTERN`、`CAT_SET_SUB_SECTION`

### 插件架构

```cpp
struct IpsApi
{
    BaseApi base;               // 名称、版本、类型
    RuleOptType type;           // OPT_TYPE_LOGGING, OPT_TYPE_DETECTION, OPT_TYPE_META
    int max_per_rule;           // 每规则最大实例数（0=无限）
    unsigned protos;           // PROTO_BIT_* 掩码
    IpsOptFunc pinit, pterm;   // 解析时初始化/终止
    IpsOptFunc tinit, tterm;   // 线程时初始化/终止
    IpsNewFunc ctor;           // 构造器
    IpsDelFunc dtor;           // 析构器
    IpsOptFunc verify;         // 配置验证
};
```

### 选项评估树

`detection_option_tree_node_t` 是树节点：
```cpp
struct detection_option_tree_node_t
{
    eval_func_t evaluate;       // 求值函数指针
    void* option_data;         // IpsOption 派生对象
    dot_node_state_t* state;   // 每线程状态
    int is_relative;
    option_type_t option_type;
};
```

**求值流程**（`detection_option_node_evaluate()`）：
1. 检查是否已求值（`was_evaluated()` 缓存）
2. 匹配 RTN（规则树节点）— 端口/协议检查
3. 调用选项 `eval()` 函数
4. 处理结果码
5. 递归求值子节点（所有子节点都匹配才通过 — AND 语义）
6. 若 `relative_children` 且 `retry()` 返回 true，则循环

### 求值语义

- **ALL（默认）**：所有兄弟选项必须匹配，规则才触发
- **否定**：各选项自行处理 — `content: !"pattern"`、`byte_test: !4`、`pcre: !"/regex/"`
- **NO_ALERT**：`flowbits: noalert` 返回 `NO_ALERT`，设置 `eval_data.flowbit_noalert = 1`，阻止子节点生成告警
- **FAILED_BIT**：flowbit 未设置时触发，允许后续重求值

### Cursor（游标）

```cpp
class Cursor
{
    void set(const char* s, const uint8_t* b, unsigned n, bool ext = false);
    const uint8_t* buffer() const { return buf; }
    unsigned size() const { return buf_size; }
    unsigned get_pos() const { return current_pos; }
    unsigned get_delta() const { return delta; }  // 循环偏移
    bool set_pos(unsigned n);
    bool add_pos(unsigned n);
};
```

### 变量提取系统

`byte_extract` 可将值存入变量供后续选项使用：

```cpp
#define NUM_IPS_OPTIONS_VARS 2
SetVarValueByIndex(value, config.var_number);
GetVarValueByIndex(&val, var_index);
```

### content 选项详解

```cpp
class ContentOption : public IpsOption
{
    EvalStatus eval(Cursor& c, Packet*) override
    { return CheckANDPatternMatch(config, c); }

    bool retry(Cursor&) override;
    PatternMatchData* get_pattern(...) override { return &config->pmd; }
    bool is_relative() override { return pmd.is_relative(); }
};
```

- 使用 Boyer-Moore 搜索
- 支持 `distance`、`within`、`offset`、`depth` 修饰符
- `get_pattern()` 为快速模式匹配器提供数据

### pcre 选项

PCRE2 支持选项：`SNORT_PCRE_RELATIVE`、`SNORT_PCRE_INVERT`、`SNORT_PCRE_ANCHORED`

### byte_test 操作符

`CHECK_EQ、CHECK_LT、CHECK_GT、CHECK_LTE、CHECK_GTE、CHECK_AND、CHECK_XOR`

### flowbits 操作

`SET、UNSET、IS_SET、IS_NOT_SET、NO_ALERT`

## 相关概念

- [[entities/linux/snort3/snort3-flow]] — Flow 追踪机制
- [[entities/linux/snort3/snort3-framework]] — Snort3 框架概览
- [[network-intrusion-detection]] — 入侵检测系统

## 来源详情

- [[github-snort3-flow-ips]]
