---
type: source
source-type: github
title: snort3/src/parser + search_engines
author: Cisco/OASIS
date: 2026-05-27
size: large
path: /Users/sphinx.shi/workspace/github/snort3/src/parser
summary: Snort3 规则解析器（26 文件）+ 多模式搜索引掣（20 文件）。覆盖规则文本 → FSM 解析 → RTN/OTN 构建 → AC/Hyperscan 模式搜索完整流水线。
created: 2026-05-27
tags: []
---
# Source: Snort3 Parser + Search Engines

**仓库：** `sphinx shi / snort3`（OASIS-LPP/Openlntrusion/Snort3 fork）
**路径：** `src/parser/`（26 文件）+ `src/search_engines/`（20 文件）
**协议：** GPL-2.0

## 核心文件索引

### Parser 层（`src/parser/`）

| 文件 | 职责 |
|------|------|
| `parser.cc` | 入口：初始化、配置解析、OTN map 管理 |
| `parse_rule.cc` | 规则 FSM 解析（action → proto → nets → ports → dir → options） |
| `parse_stream.cc` | 行/列 tokenizer + FSM 状态机执行器 |
| `parse_conf.cc` | 配置文件解析（include、variable） |
| `parse_ip.cc` | IP 地址解析（CIDR、范围、变量） |
| `parse_ports.cc` | 端口解析（范围、否定、PortVar） |
| `parse_utils.cc` | 工具：byte_code、int 解析 |
| `parse_so_rule.cc` | Shared Object 规则解析 |
| `cmd_line.cc` | 命令行参数解析 |
| `config_file.cc` | Lua 配置文件读取 |
| `var_dependency.cc` | 变量依赖解析 |
| `vars.cc` | 规则变量表管理 |

### Search Engine 层（`src/search_engines/`）

| 文件 | 职责 |
|------|------|
| `mpse.h` | MPSE 抽象接口定义 |
| `ac_full.cc` | Aho-Corasick Full 引擎（最高性能） |
| `acsmx2.cc` | AC 核心实现（Trie→NFA→DFA→FullMatrix） |
| `acsmx2.h` | AC 数据结构定义 |
| `hyperscan.cc` | Intel Hyperscan 引擎（支持正则） |
| `search_tool.cc` | SearchTool 封装（normal + offload MPSE） |
| `search_common.h` | MpseAgent / MpseMatch 接口定义 |
| `bnfa_search.h` | BNFA NFA 搜索引擎（低内存备选） |
| `search_engines.cc` | 引擎加载器 |

## 关键算法

### AC Full 状态机构建（acsmx2.cc:119-176）

```
1. acsmNew2()           创建空 AC 状态机
2. acsmAddPattern2()    逐模式插入 Trie
3. acsmCompile2()        BFS 计算 fail 状态 + 构建 DFA
4. acsmSearchDfaFull()  Full Matrix 搜索（每字节 O(1) 状态转移）
```

**存储格式演进：** List → NFA (List) → DFA (List) → Full Matrix

**关键数据结构：**
```cpp
struct ACSM_PATTERN2 {
    uint8_t* patrn;         // 原始模式
    uint8_t* casepatrn;      // 大写版本
    void* udata;             // 用户数据（规则 ID）
    void* rule_option_tree;  // 检测选项树
    void* neg_list;          // 否定模式列表
};

struct ACSM_STRUCT2 {
    acstate_t* acsmFailState;      // fail 函数
    ACSM_PATTERN2** acsmMatchList; // 每状态匹配列表
    acstate_t** acsmNextState;     // Full DFA 矩阵
    const MpseAgent* agent;
    int acsmNumStates;
};
```

### Hyperscan 编译流程（hyperscan.cc:348-414）

```cpp
1. escape(pat, n, literal)  // 非打印字符转义，正则元字符处理
2. std::sort(pvector)        // 保证序列化一致性
3. hs_compile_multi()        // 批量编译为 Hyperscan 数据库
4. hs_alloc_scratch()        // 分配全局 scratch
5. user_ctor(sc)             // 为每个模式构建 detection option tree
```

**flags：** `HS_FLAG_CASELESS`、`HS_FLAG_SINGLEMATCH`（非 multi-match）

### 规则解析 FSM（parse_stream.cc:404-471）

```
状态机：25 states × 16 actions
关键状态转换：
  (action) → FSM_ACT
  (proto) → FSM_PRO
  [src_ip] → FSM_SIP
  [src_port] → FSM_SP
  (->/<>) → FSM_DIR
  [dst_ip] → FSM_DIP
  [dst_port] → FSM_DP
  (options...) → FSM_KEY → FSM_OPT → FSM_VAL
  (;) → FSM_END
  ()) → FSM_EOB
```

---

## 代码片段

### Rule Header 解析（parse_rule.cc:771-817）

```cpp
void parse_rule_type(SnortConfig* sc, const char* s, RuleTreeNode& rtn) {
    s_type = s;
    rtn = RuleTreeNode();
    rtn.action = IpsAction::get_type(s);
    rtn.listhead = get_rule_list(sc, s);
    if ( sc->get_default_rule_state() )
        rtn.set_enabled();
}
```

### OTN-RTN 绑定（parse_rule.cc:811-852）

```cpp
int addRtnToOtn(SnortConfig* sc, OptTreeNode* otn, RuleTreeNode* rtn, PolicyId policyId) {
    // 扩展 proto_nodes 数组
    if (otn->proto_node_num <= policyId) {
        RuleTreeNode** tmp = (RuleTreeNode**)snort_calloc(policyId + 1, sizeof(RuleTreeNode*));
        if (otn->proto_nodes) { memcpy(tmp, otn->proto_nodes, sizeof(RuleTreeNode*) * otn->proto_node_num); }
        otn->proto_nodes = tmp;
    }
    // 插入 RTN 到哈希表（用于 RTN reduction）
    if (!sc->rtn_hash_table)
        sc->rtn_hash_table = new RuleTreeCache(10000, sizeof(RuleTreeNodeKey));
    RuleTreeNodeKey key = { rtn, policyId };
    sc->rtn_hash_table->insert(&key, rtn);
    return 0;
}
```

### AC Search 调用（ac_full.cc:109-119）

```cpp
int AcfMpse::search(const uint8_t* T, int n, MpseMatch match, void* context, int* current_state) {
    Profile profile(full_stats);
    full_counts.searches++;
    full_counts.bytes += n;
    int found = acsm_search_dfa_full(obj, T, n, match, context, current_state);
    full_counts.matches += found;
    return found;
}
```

### Hyperscan Search（hyperscan.cc:475-494）

```cpp
int HyperscanMpse::search(const uint8_t* buf, int n, MpseMatch mf, void* pv, int* current_state) {
    *current_state = 0;
    ScanContext scan(this, mf, pv);
    hs_scratch_t* ss = (hs_scratch_t*)SnortConfig::get_conf()->state[get_instance_id()][scratch_index];
    hyper_counts.searches++;
    hyper_counts.bytes += n;
    hs_scan(hs_db, (const char*)buf, n, 0, ss, HyperscanMpse::match, &scan);
    return scan.nfound;
}
```

---

## 架构要点

### Port Group 分组策略

`parse_rule_finish_ports()` 将规则按 `(protocol, src_port, dst_port)` 分配到 port groups：
- `any-any` → 加入 `port_tables->{proto}.any`
- `src-specific, dst-generic` → 加入 `port_tables->{proto}.src`
- `src-generic, dst-specific` → 加入 `port_tables->{proto}.dst`
- 双向规则同时加入 src 和 dst 表

### SearchTool Offload

```cpp
// search_tool.cc:find()
if (fp->get_offload_search_api() && (len >= sc->offload_limit) &&
    (mpsegrp->get_offload_mpse() != mpsegrp->get_normal_mpse())) {
    num = mpsegrp->get_offload_mpse()->search(...);  // offload 实例
    if (num < 0)
        num = mpsegrp->get_normal_mpse()->search(...);  // fallback
} else {
    num = mpsegrp->get_normal_mpse()->search(...);
}
```

### 关键约束（代码注释）

1. **Hyperscan 每个 fast pattern 视为独立 match state**，无法共享检测选项树 → 检测树退化为单链
2. **AC BNFA 和 Hyperscan 不实现 `search_all()`**，只有 AC Full 支持全量匹配
3. **RTN Hash Table** 用于 rule reduction，但仅在 `strict_rtn_reduction` 启用时比较端口对象
4. **Scratch 克隆**：Hyperscan 使用 `hs_clone_scratch()` 而非 per-call 分配，避免线程竞争

---

## 相关页面

- [[snort3-parser-search]] — 实体页面（架构分析与交叉引用）
- [[snort3]] — Snort3 整体文档
- [[linux-intrusion-detection]] — Linux IDS/IPS 生态
- [[hyperscan]] — Intel RE 模式匹配库
