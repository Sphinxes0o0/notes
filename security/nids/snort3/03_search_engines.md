---
title: "Snort3 模式匹配引擎 (search_engines/)"
description: "模式匹配引擎(MPSE - Multi-Pattern Search Engine)负责在数据包载荷中快速搜索多个模式,是Snort检测性能的关键。"
---
# Snort3 模式匹配引擎 (search_engines/)

模式匹配引擎(MPSE - Multi-Pattern Search Engine)负责在数据包载荷中快速搜索多个模式,是Snort检测性能的关键。

## 文件清单与行数统计

| 文件 | 行数 | 功能描述 |
|------|------|----------|
| search_engines.h | 30 | 模块接口 |
| search_engines.cc | ~200 | 引擎加载器 |
| search_tool.h | 71 | 搜索工具基类 |
| search_tool.cc | ~200 | 搜索工具实现 |
| ac_bnfa.cc | ~400 | **AC_BNFA** - Aho-Corasick Binary NFA |
| ac_full.cc | ~800 | **ACF** - Aho-Corasick Full |
| acsmx2.cc | ~1500 | **ACSMX2** - Aho-Corasick Sparse |
| acsmx2.h | 300+ | ACSMX2 API |
| acsmx2_api.cc | ~300 | ACSMX2 封装 |
| bnfa_search.h | ~200 | BNFA搜索接口 |
| bnfa_search.cc | ~600 | BNFA搜索实现 |
| hyperscan.cc | ~600 | **Hyperscan** - Intel正则引擎 |
| search_common.h | 42 | 公共类型定义 |
| pat_stats.h | 44 | 模式统计 |

**总计**: 约 5,000+ 行代码

---

## 类层次结构

```cpp
Mpse (framework/mpse.h - MPSE抽象基类)
├── enum MpseType { MPSE_TYPE_NORMAL, MPSE_TYPE_OFFLOAD }
├── virtual int add_pattern(pat, len, descriptor, user) = 0
├── virtual int prep_patterns(SnortConfig*) = 0
├── virtual int search(T, n, MpseMatch, context, current_state) = 0
├── virtual void search(MpseBatch&, MpseType)
└── static MpseRespType poll_responses(MpseBatch*&, MpseType)

AcBnfaMpse (ac_bnfa.cc)
├── bnfa_struct_t* obj
└── 实现 Mpse 接口

HyperscanMpse (hyperscan.cc)
├── hs_database* database
├── hs_scratch* scratch
├── std::vector<Pattern> patterns
└── 实现 Mpse 接口

bnfa_struct_t (bnfa_search.h)
├── bnfa_nfa_state_t* nfa
├── bnfa_nfa_state_t** nfa_list
├── int nstates
├── int format
└── MpseAgent* agent
```

---

## 核心算法

### 1. AC_BNFA (Aho-Corasick Binary NFA)

低内存占用的AC变体,适用于规则数量较少的场景。

```cpp
// ac_bnfa.cc:40-44
#define MOD_NAME "ac_bnfa"
#define MOD_HELP "Aho-Corasick Binary NFA (low memory, low performance) MPSE"

class AcBnfaMpse : public Mpse {
private:
    bnfa_struct_t* obj;  // BNFA状态机

public:
    AcBnfaMpse(const MpseAgent* agent) : Mpse("ac_bnfa") {
        obj = bnfaNew(agent);
        if (obj) obj->bnfaMethod = 1;
    }

    int add_pattern(...) override;
    int prep_patterns(...) override;
    int search(...) override;
};
```

**BNFA搜索接口**:
```cpp
// bnfa_search.h
bnfa_struct_t* bnfaNew(const MpseAgent* agent);
void bnfaFree(bnfa_struct_t*);
int bnfaAddPattern(bnfa_struct_t*, const uint8_t* pat, unsigned len, void* user, unsigned flags);
int bnfaCompile(bnfa_struct_t*);
int bnfaSearch(bnfa_struct_t*, const uint8_t* T, int n, MpseMatch, void* context);
```

### 2. Hyperscan (Intel HyperScan)

Intel提供的正则表达式匹配库,支持硬件加速,高性能。

```cpp
// hyperscan.cc:47-48
static const char* s_name = "hyperscan";
static const char* s_help = "intel hyperscan-based MPSE with regex support";

class HyperscanMpse : public Mpse {
private:
    hs_database* database;    // 编译后的数据库
    hs_scratch* scratch;      // 工作区(每线程)
    std::vector<Pattern> patterns;

public:
    // 支持正则表达式模式
    int add_pattern(...) override {
        // 1. escape非打印字符
        // 2. 构建Hyperscan模式
        Pattern p(pat, len, desc, user);
        patterns.push_back(p);
    }

    int prep_patterns(...) override {
        // 编译所有模式为HS数据库
        hs_compile_multi(patterns.data(), ..., &database);
        // 分配scratch
        hs_alloc_scratch(database, &scratch);
    }

    int search(...) override {
        // 执行搜索
        hs_scan(database, T, n, scratch, match_cb, context);
    }
};
```

**Hyperscan特性**:
- 支持PCRE正则表达式
- Intel CPU硬件加速
- 流模式(Stream Mode)支持
- 增量匹配

---

## 搜索公共接口

```cpp
// search_common.h
typedef struct {
    int id;           // 模式ID
    int offset;       // 匹配偏移
    int depth;        // 匹配深度
    void* user;       // 用户数据(指向PMX/PMQ)
} MPSE_MATCH;

// 搜索回调函数类型
typedef void (*MpseMatch)(int id, int offset, int depth, void* context);

// MpseBatch - 批量搜索请求
struct MpseBatch {
    std::vector<MpseBatchEntry> entries;
    MpseType type;
    MpseRespType resp;
};
```

---

## Mpse基类接口

```cpp
// framework/mpse.h:47-100
class Mpse {
public:
    virtual int add_pattern(
        const uint8_t* pat, unsigned len,
        const PatternDescriptor&, void* user) = 0;

    virtual int prep_patterns(SnortConfig*) = 0;

    virtual void reuse_search() { }

    virtual int search(
        const uint8_t* T, int n,
        MpseMatch, void* context,
        int* current_state) = 0;

    virtual int search_all(
        const uint8_t* T, int n,
        MpseMatch, void* context,
        int* current_state);

    virtual void search(MpseBatch&, MpseType);

    virtual MpseRespType receive_responses(MpseBatch&, MpseType)
    { return MPSE_RESP_COMPLETE_SUCCESS; }

    static MpseRespType poll_responses(MpseBatch*&, MpseType);

    struct PatternDescriptor {
        bool no_case;
        bool negated;
        bool literal;
        bool multi_match;
        unsigned flags;
    };
};
```

---

## 搜索流程

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. 规则加载阶段 (prep_patterns)                                  │
│    fpCreateFastPacketDetection()                                │
│    └─► Mpse::add_pattern()      // 添加所有模式                  │
│    └─► Mpse::prep_patterns()    // 编译状态机                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. 数据包检测阶段 (search)                                       │
│    DetectionEngine::detect()                                    │
│    └─► fp_full(packet)                                          │
│        └─► MpseBatch::search()                                  │
│            └─► Mpse::search()          // 批量搜索               │
│                ├─► ac_bnfa search      // 或                      │
│                ├─► hyperscan search    // 或                      │
│                └─► acsmx2 search                              │
│                    └─► MpseMatch(id, offset, depth, context)     │
│                        └─► fpAddMatch()                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. 模式匹配后处理 (option tree evaluation)                       │
│    fp_eval_option()                                             │
│    └─► detection_option_node_evaluate()                         │
│        └─► ips_options::eval()  // content/pcre/...             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 搜索策略选择

```cpp
// search_engines.cc (伪代码)
void load_search_engines() {
    // 注册所有可用搜索引擎
    MpseManager::register_engine("ac_bnfa", new AcBnfaModule());
    MpseManager::register_engine("ac_full", new AcFullModule());
    MpseManager::register_engine("acsmx2", new Acsmx2Module());
    MpseManager::register_engine("hyperscan", new HyperscanModule());

    // 根据配置选择默认引擎
    // hyperscan > acsmx2 > ac_bnfa
}

// Snort配置中指定:
// --search-method=hyperscan
```

---

## 性能比较

| 引擎 | 内存占用 | 搜索性能 | 正则支持 | 适用场景 |
|------|----------|----------|----------|----------|
| AC_BNFA | 低 | 中 | 否 | 资源受限环境 |
| ACSMX2 | 中 | 高 | 否 | 大规模规则集 |
| Hyperscan | 高 | 极高 | 是 | 高性能需求 |

---

## 模式匹配数据结构

```cpp
// detection/fp_create.h:38-49
struct PMX {
    struct PatternMatchData* pmd;
    RULE_NODE rule_node;
};

// detection/pattern_match_data.h
struct PatternMatchData {
    const char* pattern_buf;
    unsigned pattern_len;
    unsigned offset;
    unsigned depth;
    unsigned distance;
    unsigned within;
    unsigned nocase;
    unsigned negative;
    unsigned relative;
    void* user;
};
```
