---
title: "Snort3 IPS检测选项 (ips_options/)"
description: "IPS检测选项是规则体中的具体检测谓词，每个选项实现 `IpsOption` 基类，通过 `eval()` 方法对数据包执行检测。"
---
# Snort3 IPS检测选项 (ips_options/)

IPS检测选项是规则体中的具体检测谓词，每个选项实现 `IpsOption` 基类，通过 `eval()` 方法对数据包执行检测。

## 文件清单 (共70个文件)

### 核心选项 (重点分析)

| 文件 | 行数 | 功能描述 |
|------|------|----------|
| ips_content.cc/h | ~400 | **content** - 字符串模式匹配 |
| ips_pcre.cc/h | ~600 | **pcre** - Perl兼容正则表达式 |
| ips_byte_test.cc | ~400 | **byte_test** - 字节比较测试 |
| ips_byte_jump.cc | ~400 | **byte_jump** - 字节跳转(移动光标) |
| ips_byte_extract.cc | ~300 | **byte_extract** - 提取字节值到变量 |
| ips_byte_math.cc | ~300 | **byte_math** - 字节数学运算 |
| ips_flow.cc/h | ~300 | **flow** - 流状态检查 |
| ips_flowbits.cc/h | ~300 | **flowbits** - 流标志位管理 |
| ips_flags.cc | ~300 | **flags** - TCP标志位检查 |
| ips_dsize.cc | ~200 | **dsize** - 数据包载荷大小 |

### 其他选项 (列表概述)

| 选项名 | 文件 | 功能描述 |
|--------|------|----------|
| ack | ips_ack.cc | TCP ACK值检查 |
| base64_decode | ips_base64.cc | Base64解码 |
| ber_data | ips_ber_data.cc | BER编码数据 |
| ber_skip | ips_ber_skip.cc | BER跳过 |
| bufferlen | ips_bufferlen.cc | 缓冲区长度 |
| classtype | ips_classtype.cc | 规则分类(元数据) |
| cvs | ips_cvs.cc | CVS协议检测 |
| detection_filter | ips_detection_filter.cc | 检测率过滤 |
| enable | ips_enable.cc | 规则启用控制 |
| file_data | ips_file_data.cc | 文件数据缓冲 |
| file_meta | ips_file_meta.cc | 文件元数据 |
| file_type | ips_file_type.cc | 文件类型检测 |
| fragbits | ips_fragbits.cc | IP分片标志位 |
| fragoffset | ips_fragoffset.cc | IP分片偏移 |
| gid | ips_gid.cc | 规则组ID |
| hash | ips_hash.cc | 哈希计算 |
| icmp_id | ips_icmp_id.cc | ICMP标识符 |
| icmp_seq | ips_icmp_seq.cc | ICMP序列号 |
| icode | ips_icode.cc | ICMP代码 |
| id | ips_id.cc | IP标识符 |
| ip_proto | ips_ip_proto.cc | IP协议号 |
| ipopts | ips_ipopts.cc | IP选项 |
| isdataat | ips_isdataat.cc | 数据存在性检查 |
| itype | ips_itype.cc | ICMP类型 |
| js_data | ips_js_data.cc | JavaScript数据 |
| luajit | ips_luajit.cc | Lua脚本执行 |
| metadata | ips_metadata.cc | 元数据(服务/规则追踪) |
| msg | ips_msg.cc | 告警消息(元数据) |
| pkt_data | ips_pkt_data.cc | 数据包数据指针 |
| priority | ips_priority.cc | 优先级(元数据) |
| raw_data | ips_raw_data.cc | 原始数据缓冲 |
| reference | ips_reference.cc | 外部参考链接 |
| regex | ips_regex.cc | 正则表达式选项 |
| rem | ips_rem.cc | 备注(注释) |
| replace | ips_replace.cc | 数据包替换 |
| rev | ips_rev.cc | 规则版本号(元数据) |
| rpc | ips_rpc.cc | RPC映射 |
| sd_pattern | ips_sd_pattern.cc | 敏感数据模式 |
| seq | ips_seq.cc | TCP序列号 |
| service | ips_service.cc | 服务识别 |
| sid | ips_sid.cc | 签名ID(元数据) |
| so | ips_so.cc | 共享对象规则 |
| soid | ips_soid.cc | 签名对象ID |
| tag | ips_tag.cc | 事件标记 |
| target | ips_target.cc | 攻击目标 |
| tos | ips_tos.cc | IP TOS字段 |
| ttl | ips_ttl.cc | IP TTL字段 |
| vba_data | ips_vba_data.cc | VBA宏数据 |
| window | ips_window.cc | TCP窗口大小 |
| ips_options.cc | ~200 | 选项注册 |
| ips_vba_data.h | ~69 | VBA数据辅助 |
| sd_credit_card.h | ~29 | 信用卡检测辅助 |

**总计**: 约 6,000+ 行代码

---

## 核心类层次结构

```cpp
IpsOption (检测选项基类 - framework/ips_option.h)
├── std::string name
├── option_type_t type
├── virtual uint32_t hash() const
├── virtual bool operator==(const IpsOption&) const
├── virtual EvalStatus eval(Cursor&, Packet*) = 0
└── static IpsOption* dup() const

ContentData (content选项数据)
├── PatternMatchData pmd
├── LiteralSearch* searcher
├── int8_t offset_var, depth_var
├── unsigned match_delta
└── uint8_t char_width, bool little_endian

PcreData (pcre选项数据)
├── pcre2_code* re
├── pcre2_match_context* match_context
├── std::vector<pcre2_match_data*> match_data_store
├── int options
└── char* expression

FlowCheckData (flow选项数据)
├── uint8_t from_server
├── uint8_t from_client
├── uint8_t ignore_reassembled
├── uint8_t only_reassembled
├── uint8_t stateless
├── uint8_t established
└── uint8_t unestablished

TcpFlagCheckData (flags选项数据)
├── uint8_t mode        // M_NORMAL/M_ALL/M_ANY/M_NOT
├── uint8_t tcp_flags  // 要检查的标志
└── uint8_t tcp_mask   // 掩码
```

---

## 核心选项详解

### 1. content - 字符串模式匹配

```cpp
// ips_content.cc:42-76
class ContentData {
    PatternMatchData pmd = {};    // 模式数据
    LiteralSearch* searcher;      // Boyer-Moore搜索器

    int8_t offset_var;           // 变量索引(偏移)
    int8_t depth_var;            // 变量索引(深度)
    unsigned match_delta;        // 最大跳转距离
    uint8_t char_width;          // 字符宽度(1/2/4字节)
    bool little_endian;
};
```

**检测逻辑**:
```cpp
// ips_content.cc:48 (伪代码)
IpsOption::EvalStatus CheckANDPatternMatch(ContentData* cd, Cursor& c) {
    // 1. 获取检测缓冲和偏移
    const uint8_t* buf = get_detection_buffer();
    unsigned len = get_detection_buffer_len();

    // 2. 计算起始位置(offset)
    int start = calculate_offset(cd, c);

    // 3. Boyer-Moore搜索
    if (cd->searcher->search(buf + start, len - start, cd->pmd.pattern, ...)) {
        c.set_pos(match_pos + cd->pmd.pattern_len);
        return MATCH;
    }
    return NO_MATCH;
}
```

### 2. pcre - Perl兼容正则表达式

```cpp
// ips_options.h:63-73
struct PcreData {
    pcre2_code* re;                           // 编译后的正则
    pcre2_match_context* match_context;      // 匹配上下文
    std::vector<pcre2_match_data*> match_data_store;  // 每线程match数据
    int options;                              // SNORT_PCRE_RELATIVE/INVERT/ANCHORED
    char* expression;
};
```

**PCRE选项标志**:
```cpp
#define SNORT_PCRE_RELATIVE         0x00010  // 相对上次匹配
#define SNORT_PCRE_INVERT           0x00020  // 反转检测
#define SNORT_PCRE_ANCHORED         0x00040  // 锚定开始
#define SNORT_OVERRIDE_MATCH_LIMIT  0x00080  // 覆盖匹配限制
```

### 3. byte_test - 字节比较测试

```cpp
// ips_byte_test.cc (伪代码)
EvalStatus byte_test_eval(void* option_data, Cursor& c, Packet* p) {
    ByteTestData* btd = (ByteTestData*)option_data;

    // 1. 提取字节
    uint64_t value = extract_bytes(c, btd->bytes, btd->flags);

    // 2. 应用掩码
    if (btd->mask)
        value &= btd->mask;

    // 3. 执行比较
    switch (btd->op) {
        case '=': return (value == btd->value) ? MATCH : NO_MATCH;
        case '>': return (value >  btd->value) ? MATCH : NO_MATCH;
        case '<': return (value <  btd->value) ? MATCH : NO_MATCH;
        case '!': return (value != btd->value) ? MATCH : NO_MATCH;
        case '&': return (value &  btd->value) ? MATCH : NO_MATCH;
    }
}
```

### 4. byte_jump - 字节跳转

```cpp
// ips_byte_jump.cc - 移动检测光标
EvalStatus byte_jump_eval(void* option_data, Cursor& c, Packet* p) {
    ByteJumpData* bjd = (ByteJumpData*)option_data;

    // 1. 提取字节值
    uint64_t val = extract_bytes(c, bjd->bytes, bjd->flags);

    // 2. 应用乘数
    val *= bjd->multiplier;

    // 3. 对齐(可选)
    if (bjd->align)
        val = (val + 3) & ~3;

    // 4. 移动光标
    unsigned new_pos = calculate_new_pos(c, val, bjd);
    if (new_pos < c.size())
        c.set_pos(new_pos);

    return MATCH;
}
```

### 5. byte_extract - 提取字节到变量

```cpp
// ips_byte_extract.cc
// 将提取的字节值存储到变量,供后续选项使用
// 变量索引0-3, 可用于offset/depth/distance/within参数
```

### 6. byte_math - 字节数学运算

```cpp
// ips_byte_math.cc
// 对提取的字节执行数学运算,结果可存储到变量
// 支持 +, -, *, /, %, ^, &, |, <<, >>
```

### 7. flow - 流状态检查

```cpp
// ips_flow.cc:44-53
struct FlowCheckData {
    uint8_t from_server;        // C2S方向
    uint8_t from_client;        // S2C方向
    uint8_t ignore_reassembled; // 忽略重组数据
    uint8_t only_reassembled;   // 仅重组数据
    uint8_t stateless;          // 无状态
    uint8_t established;        // 已建立连接
    uint8_t unestablished;     // 未建立连接
};

EvalStatus FlowCheckOption::eval(Cursor&, Packet* p) {
    // 检查Packet->flow状态
    Flow* flow = p->flow;
    if (!flow) return NO_MATCH;

    if (config.established && !flow->established) return NO_MATCH;
    if (config.from_server && !flow->from_server) return NO_MATCH;
    // ...
    return MATCH;
}
```

### 8. flowbits - 流标志位管理

```cpp
// ips_flowbits.cc - 流标志位操作
// set, unset, toggle, is_set, no_set, isset
```

### 9. flags - TCP标志位检查

```cpp
// ips_flags.cc:55-60
struct TcpFlagCheckData {
    uint8_t mode;       // M_NORMAL/M_ALL/M_ANY/M_NOT
    uint8_t tcp_flags;  // 要检查的标志
    uint8_t tcp_mask;   // 掩码
};

// 标志定义
#define R_FIN  0x01
#define R_SYN  0x02
#define R_RST  0x04
#define R_PSH  0x08
#define R_ACK  0x10
#define R_URG  0x20
#define R_ECE  0x40
#define R_CWR  0x80
```

### 10. dsize - 数据包载荷大小

```cpp
// ips_dsize.cc:37-51
class DsizeOption : public IpsOption {
    RangeCheck config;  // 范围检查(min, max)
};

EvalStatus DsizeOption::eval(Cursor&, Packet* p) {
    unsigned dsize = p->dsize;  // 数据包载荷大小
    return config.eval(dsize) ? MATCH : NO_MATCH;
}
```

---

## 选项注册机制

```cpp
// ips_options.cc
void load_ips_options() {
    // 注册所有IPS选项到IpsManager
    IpsManager::register_option("content", new ContentModule());
    IpsManager::register_option("pcre", new PcreModule());
    IpsManager::register_option("byte_test", new ByteTestModule());
    // ...
}
```

每个选项模块继承自 `Module`, 实现:
- `bool begin(const char*, int, SnortConfig*)` - 解析开始
- `bool set(const char*, Value&, SnortConfig*)` - 设置参数
- `bool end(const char*, int, SnortConfig*)` - 解析结束
- `IpsOption* get_instance()` - 创建选项实例

---

## 模块交互

```
┌─────────────────────────────────────────────────────────────┐
│                    DetectionEngine                         │
│  detection_option_tree_evaluate()                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              IpsOption::eval(Cursor&, Packet*)             │
├─────────────────────────────────────────────────────────────┤
│  content ──► LiteralSearch (Boyer-Moore)                   │
│  pcre    ──► pcre2_match()                                 │
│  byte_test ─► extract_bytes() → 比较运算                   │
│  byte_jump ─► extract_bytes() → Cursor::set_pos()         │
│  flow    ──► Packet::flow 状态检查                         │
│  flags   ──► TCP头标志位检查                               │
│  dsize   ──► Packet::dsize 范围检查                        │
│  ...                                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Cursor (检测光标)                              │
│  跟踪当前检测位置,支持相对偏移                              │
└─────────────────────────────────────────────────────────────┘
```
