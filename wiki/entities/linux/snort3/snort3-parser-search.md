---
type: entity
tags: [snort, intrusion-detection, parser, search-engine, aho-corasick, hyperscan]
created: 2026-05-27
sources: [github-snort3-parser-search]
---

# Snort3 Parser + Search Engine Architecture

## 定义

Snort3 的规则解析与多模式搜索子系统，负责将文本规则转换为内部数据结构，并驱动数据包检测。是 IDS/IPS 检测流水线的前两环：**规则解析** → **规则树构建** → **模式搜索匹配**。

## 核心组件

### 1. Parser 层（规则文本 → 内存结构）

**入口文件：** `parser/parser.cc` + `parser/parse_rule.cc`

```
Snort.conf / rules file
    │
    ▼
parse_stream()          [parse_stream.cc]
    │  FSM tokenization (action,proto,src_ip,src_port,dst_ip,dst_port,options)
    ▼
parse_rule_type()       [parse_rule.cc:771]  — 解析 action (alert/pass/drop/...)
    ▼
parse_rule_proto()      [parse_rule.cc:819]  — 解析协议 (tcp/udp/icmp/ip)
    ▼
parse_rule_nets()       [parse_rule.cc:854]  — 解析 src/dst IP (支持变量 $HOME_NET)
    ▼
parse_rule_ports()      [parse_rule.cc:873]  — 解析 src/dst 端口 (支持 PortVar)
    ▼
parse_rule_dir()        [parse_rule.cc:896]  — 解析方向 (-> / <>)
    ▼
parse_rule_open()       [parse_rule.cc:1052] — 创建 OptTreeNode (OTN)
    │
    ▼  options loop
parse_rule_opt_begin() [parse_rule.cc:956]  — IpsManager::option_begin()
parse_rule_opt_set()   [parse_rule.cc:970]  — IpsManager::option_set()
parse_rule_opt_end()    [parse_rule.cc:1006] — IpsManager::option_end()
    │
    ▼
parse_rule_close()      [parse_rule.cc:1120] — 创建 RuleTreeNode (RTN)，加入 OTN
    ▼
addRtnToOtn()          [parse_rule.cc:811]  — RTN-OTN 绑定（支持多 policy）
```

#### 关键数据结构

| 结构 | 文件 | 作用 |
|------|------|------|
| `RuleTreeNode` | `detection/rules.h` | 规则头（action、IP、端口、方向） |
| `OptTreeNode` | `detection/treenodes.h` | 规则体（检测选项链 FastPattern + IpsOption） |
| `RulePortTables` | `ports/rule_port_tables.h` | 按协议/端口分组的规则索引表 |
| `PortObject` | `ports/port_object.h` | 端口列表抽象（支持范围、变量、否定） |

#### FSM 解析状态机

`parse_stream.cc:404` 定义了 25 个状态 + 16 种动作：

```
FSM_ACT → FSM_PRO → FSM_SIP → FSM_SP/FSPX → FSM_DIR → FSM_DIP → FSM_DP/DPX
                                                              ↓
                                                         FSM_SOB/FSM_STB → FSM_KEY → FSM_OPT → FSM_VAL
                                                              ↓
                                                         FSM_EOB (rule end)
```

关键路径：`(action) (proto) (src_net) (src_port) (dir) (dst_net) (dst_port) (options...)`

#### 变量展开

- `vars.{c,h}` — 规则变量（$HOME_NET、$HTTP_PORTS 等）
- `var_dependency.{c,h}` — 变量依赖解析（支持交叉引用）
- `sf_vartable` — IP 变量表（支持网络范围、否定、变量别名）
- `parse_ip.{c,h}` — IP 地址解析（支持 CIDR、范围、变量）
- `parse_ports.{c,h}` — 端口解析（支持 `80:90,!82`、PortVar）

#### RTN 合并与 Reduction

`parse_rule.cc:524` — `reduce_rtns()`：将具有相同 header 的多条规则合并，减少 RTN 数量，提升检测效率。

---

### 2. Search Engine 层（MPSE — Multi-Pattern Search Engine）

**入口文件：** `framework/mpse.h` + `search_engines/search_tool.{cc,h}`

#### MPSE 抽象接口

```cpp
// framework/mpse.h
class Mpse {
    virtual int add_pattern(pat, len, desc, user) = 0;
    virtual int prep_patterns(SnortConfig*) = 0;
    virtual int search(T, n, match_cb, context, state) = 0;
    virtual int search_all(T, n, match_cb, context, state);  // 返回所有匹配
};
```

#### 三种搜索引擎

| 引擎 | 文件 | 特性 |
|------|------|------|
| **AC Full** | `ac_full.cc` | Aho-Corasick 全表存储，最高内存（~4字节/状态），最优性能 |
| **AC BNFA** | `acsmx2.cc` | Aho-Corasick NFA，紧凑稀疏存储，较低内存 |
| **Hyperscan** | `hyperscan.cc` | Intel Hyperscan，支持正则，高级编译优化，多租户 |

#### Aho-Corasick 实现（AC Full）

**核心文件：** `search_engines/acsmx2.cc`

构建四阶段：
1. **Trie** — 插入所有模式，生成 keyword state table（链表过渡）
2. **NFA** — BFS 计算 fail 函数
3. **DFA** — 将 NFA 转为 DFA（确定性状态转移）
4. **Full Matrix** — 转为 256×N 压缩过渡矩阵（`acsmNextState[state][char]`）

关键搜索函数：
```cpp
acsm_search_dfa_full()   // 单次最长匹配（Snort 主要使用）
acsm_search_dfa_full_all() // 返回所有匹配位置
acsm_search_nfa()        // NFA 模式（已弃用）
```

#### Hyperscan 实现

**核心文件：** `search_engines/hyperscan.cc`

```cpp
class HyperscanMpse : public Mpse {
    PatternVector pvector;    // 模式集合
    hs_database_t* hs_db;     // 编译后的 Hyperscan 数据库

    int prep_patterns(SnortConfig*) override {
        // 1. escape 特殊字符（非打印字符、正则元字符）
        // 2. hs_compile_multi() — 批量编译
        // 3. hs_alloc_scratch() — 分配 per-thread scratch 空间
    }

    int search(buf, n, mf, ctx, state) override {
        // hs_scan(hs_db, buf, n, 0, scratch, match_cb, ctx);
    }
};
```

**关键约束（来自代码注释）：**
- Hyperscan 无法访问内部 FSM 状态，因此每个 fast pattern 被视为独立 match state
- 检测选项树对 Hyperscan 只是单链（single option chains）
- 不支持 `search_all()`（AC BNFA 也不支持）

#### SearchTool 封装

`search_engines/search_tool.cc` — 封装 MPSE，对外提供统一接口：

```cpp
class SearchTool {
    MpseGroup* mpsegrp;  // normal_mpse + offload_mpse

    void add(pat, len, id, no_case, literal);
    void prep();                    // = prep_patterns()
    int find(str, len, mf, state);  // 单次搜索
    int find_all(...);               // 全量搜索
};
```

支持 **offload search**：大缓冲区使用专用 Hyperscan 实例分流（`fp->get_offload_search_api()`）。

---

### 3. MPSE Agent — 规则树绑定

**文件：** `search_engines/search_common.h`

```cpp
struct MpseAgent {
    int (*build_tree)(SnortConfig*, void* id, void** tree);
    int (*negate_list)(void* id, void** list);
    void (*user_free)(void*);
    void (*tree_free)(void**);
    void (*list_free)(void**);
};

typedef int (*MpseMatch)(void* user, void* tree, int index, void* context, void* list);
```

Agent 是 Detection Module（检测选项，如 `content`、`uricontent`）与 MPSE 之间的桥梁：
- 每个模式 ID 关联一个 `user` 指针 → `build_tree()` → 生成检测选项树
- `negate_list()` 处理否定模式（`!pattern`）
- 匹配时 `MpseMatch` 回调在 tree 上执行 IPS 选项检测

---

## 关键设计

### 规则分组策略

Snort3 按 `(protocol, src_port, dst_port)` 分组构建 port groups，每个 group 一个 MPSE 实例。好处：
- 减少每次搜索的模式数
- 同一 group 内的包共享 AC 状态复用

### Fast Pattern

只有标记为 fast pattern 的 content 才加入 MPSE。`detection/fp_config.h` 控制：
- `fast_pattern_id` — 每个 OTN 只能有一个 fast pattern
- `fast_pattern_only` — 仅使用 fast pattern
- `fast_pattern_inspect` — 排序优化

### Scratch 空间管理

Hyperscan 使用 per-thread scratch 克隆：
```cpp
hs_clone_scratch(s_scratch, &sc->state[thread_id][scratch_index]);
```
避免线程竞争，实现无锁搜索。

### 序列化与反序列化

- `Mpse::serialize()` / `deserialize()` — 序列化了规则模式集合
- `HyperscanMpse::get_hash()` — MD5 哈希用于缓存验证
- 支持 snort3 的规则热重载（`--reload`）

---

## 交叉引用

- [[snort3-index]] — 整体架构
- [[linux-intrusion-detection]] — IDS/IPS 生态
- [[ebpf-xdp]] — 网络数据包处理（XDP 旁路架构参考）
- [[hyperscan]] — Intel RE 模式匹配库
