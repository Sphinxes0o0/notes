---
title: "Snort 3 · Codec、TCP 重组与流管理"
description: "附录LX：Codec模块详细分析 — 附录ML：Flow管理详细分析"
---

# Snort 3 · Codec、TCP 重组与流管理

[返回总目录](../snort3_architecture_analysis)

## 附录LX：Codec模块详细分析 {#附录lx-codec模块详细分析}

### LX.1 Codec概述 {#lx-1-codec概述}

Codec负责将原始网络字节流解析为协议数据结构，是数据包处理的第一环。Snort 3共有**39个Codec模块**。

### LX.2 IP协议族Codec (`codecs/ip/`) {#lx-2-ip协议族codec-codecs-ip}

| Codec | 文件 | 协议 | 关键功能 |
|-------|------|------|----------|
| `Ipv4Codec` | cd_ipv4.cc | IPv4 | 头部解析、选项处理、校验和验证、分片检测 |
| `Ipv6Codec` | cd_ipv6.cc | IPv6 | 扩展头处理、Teredo隧道检测、多播范围验证 |
| `TcpCodec` | cd_tcp.cc | TCP | 序列号验证、选项解析、标志检测 |
| `UdpCodec` | cd_udp.cc | UDP | 端口检测(GTP/VXLAN/Geneve)、校验和验证 |
| `Icmp4Codec` | cd_icmp4.cc | ICMPv4 | Echo检测、目标不可达处理、嵌入IP解析 |
| `Icmp6Codec` | cd_icmp6.cc | ICMPv6 | NDP选项验证、邻居发现 |
| `IgmpCodec` | cd_igmp.cc | IGMP | 选项DoS检测 |
| `EspCodec` | cd_esp.cc | ESP | 跳过IV和序列号、仅支持NULL加密 |
| `GreCodec` | cd_gre.cc | GRE | 版本0(RFC2784)和版本1(PPTP) |
| `Ipv6FragCodec` | cd_frag.cc | IPv6分片 | 分片偏移、M标志提取 |
| `Ipv6HopOptsCodec` | cd_hop_opts.cc | IPv6逐跳选项 | 扩展头解析 |
| `Ipv6DSTOptsCodec` | cd_dst_opts.cc | IPv6目标选项 | 目的选项头解析 |
| `Ipv6RoutingCodec` | cd_routing.cc | IPv6路由扩展 | 路由类型验证、Type 0警告(RFC5095) |
| `MobilityCodec` | cd_mobility.cc | IPv6移动性 | 移动头部解析(RFC6275) |
| `Ipv6NoNextCodec` | cd_no_next.cc | IPv6无下一头部 | 头部链结束标记(协议59) |
| `AuthCodec` | cd_auth.cc | IP认证头(AH) | ICV计算、头部长度验证 |
| `BadProtocalCodec` | cd_bad_proto.cc | 未知协议 | SWIPE/SUN_ND通用处理 |
| `PgmCodec` | cd_pgm.cc | PGM | NAK结构验证、溢出检测 |

### LX.3 链路层Codec (`codecs/link/`) {#lx-3-链路层codec-codecs-link}

| Codec | 文件 | 协议 | 关键功能 |
|-------|------|------|----------|
| `EthCodec` | cd_eth.cc | Ethernet II/802.3 | EtherType解析、FabricPath处理 |
| `VlanCodec` | cd_vlan.cc | IEEE 802.1Q | VID/PCP/CFI提取、QinQ支持 |
| `ArpCodec` | cd_arp.cc | ARP | 地址解析协议 |
| `MplsCodec` | cd_mpls.cc | MPLS | 标签栈遍历、净荷类型自动检测 |
| `PPPoEDiscCodec` | cd_pppoe.cc | PPPoE发现 | 发现阶段处理 |
| `PPPoESessCodec` | cd_pppoe.cc | PPPoE会话 | 会话建立、下一协议为PPP |
| `PppEncapCodec` | cd_ppp_encap.cc | PPP | 协议压缩(1字节vs2字节) |
| `LlcCodec` | cd_llc.cc | IEEE 802.2 LLC | DSAP/SSAP/Ctrl解析 |
| `TransbridgeCodec` | cd_trans_bridge.cc | 透明桥接 | 嵌套以太网处理 |
| `Erspan2Codec` | cd_erspan2.cc | ERSPAN Type II | 版本验证、下一协议以太网 |
| `Erspan3Codec` | cd_erspan3.cc | ERSPAN Type III | 时间戳和pad处理 |
| `FabricPathCodec` | cd_fabricpath.cc | Cisco FabricPath | 16字节头处理 |
| `CiscoMetaDataCodec` | cd_ciscometadata.cc | Cisco元数据 | SGT标签验证 |

### LX.4 隧道/封装Codec (`codecs/misc/`) {#lx-4-隧道-封装codec-codecs-misc}

| Codec | 文件 | 协议 | 关键功能 |
|-------|------|------|----------|
| `VxlanCodec` | cd_vxlan.cc | VXLAN | VNI提取、隧道旁路支持 |
| `GtpCodec` | cd_gtp.cc | GTP | v0/v1支持、扩展头处理 |
| `GeneveCodec` | cd_geneve.cc | GENEVE | 选项验证、版本检查(RFC8926) |
| `TeredoCodec` | cd_teredo.cc | Teredo | IPv6签名验证、隧道检测 |
| `UserCodec` | cd_user.cc | 用户/DAQ | DAQ ioctl PCI信息提取 |
| `Icmp4IpCodec` | cd_icmp4_ip.cc | 嵌入IPv4 | ICMP内嵌IP解析(RFC1812) |
| `Icmp6IpCodec` | cd_icmp6_ip.cc | 嵌入IPv6 | ICMPv6内嵌IPv6解析 |

### LX.5 Codec API结构 {#lx-5-codec-api结构}

```cpp
// 所有Codec遵循的插件模式
class Codec {
    virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;
    virtual bool encode(const uint8_t* raw_in, const uint16_t raw_len,
                       EncState&, Buffer&, Flow*) = 0;
    virtual void update(const ip::IpApi&, EncodeFlags, uint8_t* raw_pkt,
                       uint16_t lyr_len, uint32_t& updated_len);
    virtual void log(TextLog* const, const uint8_t* raw_pkt, 
                     const uint16_t lyr_len);
};
```

### LX.6 协议解码流程 {#lx-6-协议解码流程}

```
原始数据包字节
     │
     ▼
┌──────────────────┐
│   Ethernet Codec │
│  (DLT_EN10MB)   │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    VLAN Codec    │  (optional)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    MPLS Codec    │  (optional)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│   IPv4/IPv6 Codec │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│  IPv6 Ext Codecs │  (optional)
│  (Frag/Hop/Dst/  │
│   Routing/Mobility)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    TCP/UDP Codec  │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│   Application    │
│   Protocol Codec │
│ (HTTP, DNS, ...) │
└──────────────────┘
```

---

## 附录LY：TCP重组详细分析 {#附录ly-tcp重组详细分析}

### LY.1 TCP重组器架构 {#ly-1-tcp重组器架构}

```
TcpReassembler (抽象基类)
├── TcpReassemblerIgnore - 忽略重组 (STREAM_FLPOLICY_IGNORE)
└── TcpReassemblerBase (抽象)
    ├── TcpReassemblerIds - 基于ACK刷新 (STREAM_FLPOLICY_ON_ACK)
    └── TcpReassemblerIps - 基于数据刷新 (STREAM_FLPOLICY_ON_DATA)
```

### LY.2 关键数据结构 {#ly-2-关键数据结构}

**TcpSegmentNode** (tcp_segment_node.h):
```cpp
class TcpSegmentNode {
    TcpSegmentNode* prev;     // 前一segment
    TcpSegmentNode* next;     // 后一segment
    struct timeval tv;        // 时间戳
    uint32_t ts;              // TCP时间戳选项
    uint32_t seq;             // 起始序列号
    uint16_t length;         // 相对偏移的工作长度
    uint16_t offset;          // 工作起始偏移
    uint16_t cursor;          // 扫描位置
    uint16_t size;            // 分配的净荷大小
    uint8_t data[1];         // 变长数据
};
```

**TcpReassemblySegments** (tcp_reassembly_segments.h):
```cpp
class TcpReassemblySegments {
    TcpSegmentNode* head = nullptr;        // 链表头
    TcpSegmentNode* tail = nullptr;        // 链表尾
    TcpSegmentNode* cur_rseg = nullptr;   // 当前读segment
    TcpSegmentNode* cur_sseg = nullptr;   // 当前扫描segment
    uint32_t seglist_base_seq = 0;        // 首个segment序列号
    uint32_t seg_count = 0;                // 队列segment数
    uint32_t seg_bytes_total = 0;          // 队列总字节
    uint32_t seg_bytes_logical = 0;        // 逻辑字节(去重)
    uint32_t overlap_count = 0;            // 重叠计数
};
```

### LY.3 重叠解决策略 {#ly-3-重叠解决策略}

**OverlapResolver策略** (tcp_overlap_resolver.cc):

| 策略 | 左重叠动作 | 右重叠动作 | 完全重叠动作 |
|------|-----------|-----------|-------------|
| FIRST | 保留旧 | 截断新 | 保留新 |
| LAST | 保留新 | 截断旧 | 删除旧 |
| OS_LINUX | 保留旧 | 截断旧 | 保留旧 |
| OS_BSD | 保留旧 | 截断旧 | 保留旧 |
| OS_WINDOWS | 保留旧 | 截断旧 | 保留旧 |
| OS_VISTA | 保留旧 | 截断新 | 保留新 |
| OS_OLD_LINUX | 保留旧 | 截断旧 | 删除旧 |
| OS_SOLARIS | 截断旧 | 截断新 | 保留新 |
| OS_HPUX11 | 截断旧 | 截断新 | 保留新 |

### LY.4 PAF (Protocol Aware Flushing) {#ly-4-paf-protocol-aware-flushing}

**状态机**:
```
START → SEARCH → FLUSH → LIMIT → LIMITED
         ↓
       SKIP → (gap处理)
         ↓
       ABORT
         ↓
       STOP
```

**Flush类型**:
```cpp
enum FlushType {
    FT_NOP,   // 无flush
    FT_SFP,   // 终止PAF
    FT_PAF,   // 到PAF点flush
    FT_LIMIT, // 到PAF点flush，不更新flags
    FT_MAX    // 达到最大长度flush
};
```

### LY.5 TCP状态机 {#ly-5-tcp状态机}

```cpp
enum TcpState {
    TCP_LISTEN,        // 等待连接
    TCP_SYN_SENT,      // 已发送SYN
    TCP_SYN_RECV,      // 收到SYN
    TCP_ESTABLISHED,   // 连接已建立
    TCP_MID_STREAM_SENT,   // 中途开始
    TCP_MID_STREAM_RECV,   // 中途接收
    TCP_FIN_WAIT1,     // FIN等待1
    TCP_FIN_WAIT2,     // FIN等待2
    TCP_CLOSE_WAIT,     // 关闭等待
    TCP_CLOSING,       // 关闭中
    TCP_LAST_ACK,      // 最后ACK
    TCP_TIME_WAIT,     // 时间等待
    TCP_CLOSED,        // 已关闭
    TCP_STATE_NONE,
    TCP_MAX_STATES
};
```

### LY.6 乱序和重传处理 {#ly-6-乱序和重传处理}

**乱序检测**:
```cpp
void TcpReassemblySegments::skip_holes() {
    // 检测列表开头空洞
    // 遍历列表检测间隙
    // 清除间隙左侧segment
}
```

**重传检测** (tcp_overlap_resolver.cc):
```cpp
bool TcpOverlapResolver::is_segment_retransmit(...) {
    // 必须有相同序列号和净荷
    if (!SEQ_EQ(seq, rseq))
        return false;
    // 比较未扫描部分
    if (orig_dsize == unscanned()) {
        if (!memcmp(data, rdata, cmp_len))
            return true;
    }
}
```

### LY.7 Normalizer集成 {#ly-7-normalizer集成}

```cpp
// tcp_session.cc
int rc = listener->normalizer.apply_normalizations(tsd, ...);
switch (rc) {
    case NORM_OK:
        // 继续处理
        listener->seglist.queue_reassembly_segment(tsd);
        break;
    case NORM_TRIMMED:
        // 数据被裁剪
        break;
    case NORM_BAD_SEQ:
        return;  // 丢弃
}
```

---

## 附录LZ：模式匹配算法详细分析 {#附录lz-模式匹配算法详细分析}

### LZ.1 搜索引擎概览 {#lz-1-搜索引擎概览}

| 算法 | 类型 | 内存 | 性能 | 支持模式 |
|------|------|------|------|----------|
| **AC_FULL** | 多模式DFA | 高 | 最优 | 任意 |
| **AC_BNFA** | 多模式NFA | 低 | 较低 | 任意 |
| **Hyperscan** | 多模式DFA/NFA | 中 | 最优(Intel) | 正则+字面 |
| **Boyer-Moore** | 单模式 | 极低 | 单模式优 | 单模式 |

### LZ.2 AC_FULL (Aho-Corasick全DFA) {#lz-2-ac-full-aho-corasick全dfa}

**数据结构** (acsmx2.h):
```cpp
struct ACSM_STRUCT2 {
    ACSM_PATTERN2* acsmPatterns;      // 模式列表
    acstate_t* acsmFailState;         // 失败函数
    ACSM_PATTERN2** acsmMatchList;    // 每状态匹配列表
    trans_node_t** acsmTransTable;    // NFA转换表
    acstate_t** acsmNextState;       // DFA完整矩阵
    int acsmMaxStates;                // 最大状态数
    int acsmNumStates;                // 当前状态数
    int numPatterns;                  // 模式数
};
```

**构建流程**:
1. `acsmNew2()` - 创建状态机
2. `acsmAddPattern2()` - 添加模式
3. `acsmCompile2()`:
   - 统计状态数
   - 构建关键词trie
   - BFS构建NFA和失败链接
   - 转换NFA到DFA
   - 转换为完整矩阵

**搜索流程**:
```cpp
for each byte in text:
    state = NextState[state][byte + 2];  // +2跳过匹配标志
    if (match flag set):
        invoke match callback
```

**内存估算**: `states * 256 * sizeof(state)`
- 10K状态 * 256 * 4字节 ≈ 10MB

### LZ.3 AC_BNFA (二进制NFA) {#lz-3-ac-bnfa-二进制nfa}

**特点**:
- 低内存占用
- 稀疏存储格式
- 使用二分查找(>6转换)或线性查找(≤6转换)
- 状态0使用完整256条目数组

**构建流程**:
1. `bnfaNew()` - 创建结构
2. `bnfaAddPattern()` - 添加模式
3. `bnfaCompile()`:
   - 构建关键词trie
   - 构建带失败状态的NFA
   - 转换为稀疏格式

### LZ.4 Boyer-Moore (单模式) {#lz-4-boyer-moore-单模式}

**位置**: `/src/helpers/boyer_moore.cc`

**数据结构**:
```cpp
class BoyerMoore {
    const uint8_t* pattern;
    unsigned pattern_len;
    unsigned last;
    unsigned skip[256];    // 坏字符跳转表
};
```

**搜索流程**:
```cpp
while (buffer_len >= pattern_len) {
    for (pos = last; buffer[pos] == pattern[pos]; pos--)
        if (pos == 0) return buffer - start;
    buffer_len -= skip[buffer[last]];
    buffer += skip[buffer[last]];
}
```

**使用场景**:
- 文件处理(zip解压)
- 单模式字面匹配
- 工厂模式: `LiteralSearch::instantiate()` 优先使用Hyperscan

### LZ.5 Hyperscan (Intel) {#lz-5-hyperscan-intel}

**特点**:
- Intel优化，支持硬件加速
- 支持正则表达式
- `hs_scan()` 返回所有匹配

**构建流程**:
1. `add_pattern()` - 收集模式
2. `prep_patterns()`:
   - `hs_compile_multi()` - 编译数据库
   - `hs_alloc_scratch()` - 分配临时空间

### LZ.6 快速模式提取 {#lz-6-快速模式提取}

```cpp
bool PatternMatchData::can_be_fp() const {
    // 必须是肯定的（非否定）
    // 不能是相对的
    // 不能有offset/depth限制
    if (flags & NO_FP) return false;
    if (is_relative()) return false;
    if (is_negated()) return false;
    return true;
}
```

---

## 附录MA：Port Scan检测模块详细分析 {#附录ma-port-scan检测模块详细分析}

### MA.1 核心类结构 {#ma-1-核心类结构}

```cpp
class PortScan : public snort::Inspector {
    // 关键方法
    void eval(snort::Packet*) override;           // 主包处理
    bool ps_ignore_ip(...);                       // 检查忽略列表
    int ps_detect(PS_PKT*);                       // 主检测入口
    void ps_tracker_update_tcp(...);               // TCP更新
    void ps_tracker_update_udp(...);               // UDP更新
    void ps_tracker_update_icmp(...);              // ICMP更新
    void ps_alert_ip(...);                         // IP告警
    void ps_alert_tcp(...);                        // TCP告警
};
```

### MA.2 关键数据结构 {#ma-2-关键数据结构}

**PS_TRACKER** - 追踪扫描器/被扫描者关系:
```cpp
struct PS_TRACKER {
    int priority_node;      // 优先级告警标记
    int protocol;          // 协议类型
    PS_PROTO proto;        // 协议特定数据
};
```

**PS_PROTO** - 按协议跟踪:
```cpp
struct PS_PROTO {
    int connection_count;      // 连接尝试总数
    int priority_count;       // 负响应数(RST/ICMP不可达)
    int u_ip_count;          // 唯一源IP数
    int u_port_count;         // 唯一端口数
    unsigned short high_p;    // 最高端口
    unsigned short low_p;     // 最低端口
    snort::SfIp high_ip;     // 最高IP
    snort::SfIp low_ip;      // 最低IP
    unsigned short open_ports[PS_OPEN_PORTS];  // 检测到的开放端口
    unsigned char open_ports_cnt;
    unsigned char alerts;     // 告警类型
    time_t window;            // 滑动窗口过期时间
};
```

### MA.3 检测类型和告警分类 {#ma-3-检测类型和告警分类}

| 告警类型 | GID:SID | 说明 |
|---------|---------|------|
| TCP portscan | 122:1 | 单点对单点 |
| TCP decoy | 122:2 | 混淆源扫描 |
| TCP portsweep | 122:3 | 单点对多点 |
| TCP distributed | 122:4 | 分布式 |
| TCP filtered | 122:5-8 | 过滤变体 |
| IP protocol scan | 122:9-16 | IP协议扫描 |
| UDP portscan | 122:17-24 | UDP扫描 |
| ICMP sweep | 122:25-26 | ICMP扫描 |
| Open port | 122:27 | 开放端口 |

### MA.4 滑动窗口和阈值 {#ma-4-滑动窗口和阈值}

**窗口更新**:
```cpp
void PortScan::ps_proto_update_window(unsigned interval, PS_PROTO* proto, time_t pkt_time) {
    if (pkt_time > proto->window) {
        *proto = {};  // 重置结构
        proto->window = pkt_time + interval;
    }
}
```

**阈值检测**:
```cpp
static bool ps_alert_one_to_one(
    const PS_ALERT_CONF& conf, PS_PROTO* scanner, PS_PROTO* scanned) {
    // 条件1: priority_count >= 配置优先级
    // 条件2: u_ip_count < 配置IP数(源IP少)
    // 条件3: u_port_count >= 配置端口数(目标端口多)
}
```

### MA.5 关键配置参数 {#ma-5-关键配置参数}

```lua
port_scan = {
    -- 协议开关
    protos = "all",           -- tcp|udp|icmp|ip|all
    scan_types = "all",       -- portscan|portsweep|decoy|distributed|all
    
    -- 内存限制
    memcap = 10485760,        -- 10MB
    
    -- TCP参数
    tcp_ports = { scans=100, rejects=15, nets=25, ports=25 },
    tcp_window = 0,           -- 0=无限窗口
    
    -- 过滤
    watch_ip = "",             -- 监控IP列表
    ignore_scanners = "",       -- 忽略作为扫描者
    ignore_scanned = "",        -- 忽略作为被扫描者
    
    -- 告警模式
    alert_all = false,         -- false=首次告警, true=所有事件
}
```

### MA.6 检测流程 {#ma-6-检测流程}

```
ps_detect(PS_PKT* ps_pkt)
    │
    ├── ps_filter_ignore()     [过滤忽略的包]
    │     - 检查协议是否启用
    │     - 检查ignore_scanners/ignore_scanned列表
    │     - 检查watch_ip列表
    │
    ├── ps_tracker_lookup()    [查找/创建tracker]
    │     - 从(scanner, scanned, protocol)创建hash键
    │
    ├── ps_tracker_update()    [更新tracker]
    │     - 更新连接/优先级计数
    │     - 更新唯一IP/端口统计
    │     - 调用协议特定更新
    │
    └── ps_tracker_alert()     [评估告警]
          - 对比告警配置阈值
          - 设置告警类型
```

### MA.7 调优策略 {#ma-7-调优策略}

**高灵敏度(捕获更多扫描)**:
```lua
port_scan = {
    tcp_ports = { scans=50, rejects=10, nets=15, ports=15 },
    tcp_window = 300,  -- 5分钟
}
```

**低假阳性(减少误报)**:
```lua
port_scan = {
    tcp_ports = { scans=200, rejects=30, nets=50, ports=50 },
    tcp_window = 1800,  -- 30分钟
}
```

---

## 附录MB：资源管理与性能优化 {#附录mb-资源管理与性能优化}

### MB.1 Memory Cap配置 {#mb-1-memory-cap配置}

```lua
memory = {
    cap = 0,                    -- 0=禁用, 否则为字节数
    interval = 50,               -- 检查间隔(ms), 0=禁用
    prune_target = 1048576,     -- 每次回收目标字节
    threshold = 100,             -- 堆开销缩放(1-100)
}
```

### MB.2 Flow Cache配置 {#mb-2-flow-cache配置}

```lua
stream = {
    -- 流数量限制
    max_flows = 476288,         -- 最大并发流
    prune_flows = 10,           -- 每次回收数量
    pruning_timeout = 30,       -- 空闲超时(秒)
    
    -- 协议超时
    tcp_cache = { idle_timeout = 3600 },   -- 1小时
    udp_cache = { idle_timeout = 180 },    -- 3分钟
    icmp_cache = { idle_timeout = 180 },
    ip_cache = { idle_timeout = 180 },
}
```

### MB.3 延迟监控配置 {#mb-3-延迟监控配置}

```lua
latency = {
    packet = {
        max_time = 500,         -- 微秒阈值
        fastpath = false,        -- 快速跳过昂贵包
    },
    rule = {
        max_time = 500,         -- 微秒阈值
        suspend = false,         -- 挂起昂贵规则
        suspend_threshold = 5,  -- 超时次数阈值
        max_suspend_time = 30000, -- 最大挂起时间(ms)
    }
}
```

### MB.4 速率限制 {#mb-4-速率限制}

**Rate Filter** (`filters/rate_filter.cc`):
```lua
-- 规则示例
rate_filter:
    gen_id 1, sig_id 2001,
    track by_src,
    count 100, seconds 60,
    timeout 10,
    new_action alert
```

**Detection Filter** (`filters/detection_filter.cc`):
```lua
-- 规则示例
detection_filter:
    gen_id 1, sig_id 2001,
    track by_src,
    count 100, seconds 60
```

### MB.5 CPU亲和性配置 {#mb-5-cpu亲和性配置}

```lua
-- CPU核心绑定
thread_affinity = "0-3"        -- packet线程绑定到核心0-3
named_thread_affinity = {
    main = "0",
    packet = "1-4"
}
```

### MB.6 降低资源占用配置 {#mb-6-降低资源占用配置}

**低资源占用配置**:
```lua
-- 内存
memory.cap = 1073741824       -- 1GB
memory.prune_target = 262144  -- 256KB

-- 流
stream.max_flows = 100000     -- 10万流
stream.prune_flows = 20
stream.tcp_cache.idle_timeout = 300

-- 延迟
latency.packet.max_time = 1000
latency.packet.fastpath = true

-- DAQ
daq = { batch_size = 32 }    -- 默认64
```

**积极检测配置**:
```lua
stream.tcp_cache.idle_timeout = 60
stream.udp_cache.idle_timeout = 30

latency.packet.max_time = 200
latency.packet.fastpath = true
latency.rule.max_time = 200
latency.rule.suspend = true
latency.rule.suspend_threshold = 5
latency.rule.max_suspend_time = 15000
```

### MB.7 Profiler配置 {#mb-7-profiler配置}

```lua
profiler = {
    modules = {
        show = true,           -- 显示模块时间统计
        count = 0,             -- 0=无限制
        sort = "total_time",  -- total_time|checks|avg_check
        max_depth = -1         -- -1=无限制
    },
    rules = {
        show = true,           -- 显示规则时间统计
        count = 0,             -- 0=全部
        sort = "total_time"
    },
    memory = {
        show = true,
        sort = "total_used",
        dump_file_size = 1073741824  -- 1GB
    }
}
```

---

## 附录MC：附录索引 {#附录mc-附录索引}

### MC.1 主题索引 {#mc-1-主题索引}

| 主题 | 附录位置 |
|------|----------|
| Codec编解码器 | LX |
| TCP重组 | LY |
| 模式匹配算法 | LZ |
| Port Scan检测 | MA |
| 资源管理 | MB |

### MC.2 源码文件索引 {#mc-2-源码文件索引}

| 功能 | 源文件 |
|------|--------|
| IPv4编解码 | src/codecs/ip/cd_ipv4.cc |
| TCP重组 | src/stream/tcp/tcp_reassembler*.cc |
| AC全匹配 | src/search_engines/acsmx2.cc |
| Boyer-Moore | src/helpers/boyer_moore.cc |
| Port Scan | src/network_inspectors/port_scan/*.cc |
| 内存管理 | src/memory/memory_cap.cc |
| Flow缓存 | src/flow/flow_cache.cc |

---

## 附录MD：文档更新记录 {#附录md-文档更新记录}

### MD.1 更新历史 {#md-1-更新历史}

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-04-10 | 22.0 | 初始版本 |
| 2026-04-11 | 23.0 | 新增Codec详细分析(LX) |
| 2026-04-11 | 23.0 | 新增TCP重组详细分析(LY) |
| 2026-04-11 | 23.0 | 新增模式匹配算法分析(LZ) |
| 2026-04-11 | 23.0 | 新增Port Scan检测分析(MA) |
| 2026-04-11 | 23.0 | 新增资源管理分析(MB) |

---

---

## 附录MK：Stream TCP模块详细分析 {#附录mk-stream-tcp模块详细分析}

### MK.1 TcpStreamInspector类结构 {#mk-1-tcpstreaminspector类结构}

```cpp
class StreamTcp : public Inspector {
    TcpStreamConfig* const config;
    // 实际TCP会话处理由TcpSession类完成
};
```

### MK.2 TCP状态机 {#mk-2-tcp状态机}

**状态** (tcp_stream_tracker.h):
```cpp
enum TcpState {
    TCP_LISTEN,         // 0
    TCP_SYN_SENT,       // 1
    TCP_SYN_RECV,       // 2
    TCP_ESTABLISHED,    // 3
    TCP_MID_STREAM_SENT, // 4 - 中途开始
    TCP_MID_STREAM_RECV, // 5 - 中途接收
    TCP_FIN_WAIT1,      // 6
    TCP_FIN_WAIT2,      // 7
    TCP_CLOSE_WAIT,     // 8
    TCP_CLOSING,        // 9
    TCP_LAST_ACK,       // 10
    TCP_TIME_WAIT,      // 11
    TCP_CLOSED,         // 12
    TCP_MAX_STATES
};
```

**事件**:
```cpp
enum TcpEvent {
    TCP_SYN_SENT_EVENT, TCP_SYN_ACK_SENT_EVENT, TCP_ACK_SENT_EVENT,
    TCP_DATA_SEG_SENT_EVENT, TCP_FIN_SENT_EVENT, TCP_RST_SENT_EVENT,
    TCP_SYN_RECV_EVENT, TCP_SYN_ACK_RECV_EVENT, TCP_ACK_RECV_EVENT,
    TCP_DATA_SEG_RECV_EVENT, TCP_FIN_RECV_EVENT, TCP_RST_RECV_EVENT
};
```

### MK.3 会话管理 (TcpSession) {#mk-3-会话管理-tcpsession}

```cpp
class TcpSession : public Session {
    TcpStreamTracker client;   // 客户端跟踪
    TcpStreamTracker server;   // 服务器端跟踪
    TcpStreamConfig* tcp_config;
    TcpEventLogger tel;
    TcpStateMachine* tsm;
};
```

### MK.4 Normalizer集成 {#mk-4-normalizer集成}

**Normalizer策略** (tcp_defs.h):
```cpp
namespace Normalizer {
    enum Policy { FIRST, LAST, OS_LINUX, OS_OLD_LINUX, OS_BSD, OS_MACOS,
        OS_SOLARIS, OS_IRIX, OS_HPUX11, OS_HPUX10, OS_WINDOWS,
        OS_WINDOWS2K3, OS_VISTA, PROXY, MISSED_3WHS };
}
```

**关键规范化函数**:
- `trim_syn_payload()` - 移除SYN上的数据
- `trim_rst_payload()` - 移除RST上的数据
- `trim_win_payload()` - 裁剪到TCP窗口
- `trim_mss_payload()` - 裁剪到MSS
- `ecn_stripper()` - 移除ECN标志
- `validate_rst()` - 验证RST包

### MK.5 PAF (Protocol Aware Flushing) {#mk-5-paf-protocol-aware-flushing}

```cpp
void TcpStreamTracker::update_flush_policy(snort::StreamSplitter* ss) {
    if (ss->is_paf())
        flush_policy = STREAM_FLPOLICY_ON_ACK;  // IDS模式
    else
        flush_policy = STREAM_FLPOLICY_ON_DATA;  // IPS模式
}
```

### MK.6 关键配置参数 {#mk-6-关键配置参数}

```lua
stream_tcp = {
    flush_factor = 0,
    max_window = 0,
    overlap_limit = 0,
    max_pdu = 16384,
    no_ack = false,
    policy = "bsd",
    max_bytes = 4194304,       -- 4MB
    max_segments = 3072,
    session_timeout = 180,
    embryonic_timeout = 30,
    idle_timeout = 3600,
    track_only = false,
    small_segments = { count=0, size=0 }
}
```

---

## 附录ML：Flow管理详细分析 {#附录ml-flow管理详细分析}

### ML.1 Flow类结构 {#ml-1-flow类结构}

```cpp
class Flow {
    FlowState state = FlowState::SETUP;  // SETUP, INSPECT, BLOCK, RESET, ALLOW
    FlowKey* key;                        // 唯一标识
    Session* session;                    // 协议特定会话
    FlowDataStore* flow_data;           // 检查器状态
    FlowStash* stash;                   // 键值存储
};
```

**会话标志**:
```cpp
SSNFLAG_SEEN_CLIENT = 0x01     // 已见客户端
SSNFLAG_SEEN_SERVER = 0x02     // 已见服务器
SSNFLAG_ESTABLISHED = 0x04     // 会话已建立
SSNFLAG_MIDSTREAM = 0x08       // 中途拾取
SSNFLAG_TIMEDOUT = 0x1000      // 超时
SSNFLAG_PRUNED = 0x2000        // 已清理
SSNFLAG_RESET = 0x4000         // 重置
```

### ML.2 FlowKey - 流向标识 {#ml-2-flowkey-流向标识}

```cpp
struct FlowKey {
    uint32_t ip_l[4], ip_h[4];    // 低/高IP
    uint32_t mplsLabel;            // MPLS标签
    uint32_t addressSpaceId;        // 地址空间ID
    uint32_t tenant_id;             // 租户ID
    uint16_t port_l, port_h;        // 低/高端口
    int16_t group_l, group_h;       // 接口组
    uint16_t vlan_tag;              // VLAN标签
    uint8_t ip_protocol;            // IP协议
    PktType pkt_type;               // 数据包类型
};
```

**流向标准化**: IP和端口始终排序（较低的在`ip_l/port_l`）

### ML.3 FlowCache - 流查找和分配 {#ml-3-flowcache-流查找和分配}

```cpp
class FlowCache {
    ZHash* hash_table;              // Zoned Hash表
    FlowUniList* uni_flows;         // 单向流列表
    FlowUniList* uni_ip_flows;      // IP单向流列表
};
```

**查找流程**:
1. `find()` - 查找现有流，更新LRU
2. `allocate()` - 分配新流，必要时修剪
3. `prune_idle()` - 修剪空闲流
4. `prune_unis()` - 修剪单向流
5. `prune_excess()` - 超容量时修剪

### ML.4 修剪原因 {#ml-4-修剪原因}

```cpp
enum class PruneReason {
    EXCESS,              // 超max_flows
    UNI,                 // 单向流修剪
    MEMCAP,              // 内存上限
    HA,                  // 高可用性同步
    STALE,               // 陈旧
    IDLE_MAX_FLOWS,      // 空闲且达最大
    IDLE_PROTOCOL_TIMEOUT, // 协议超时
    STREAM_CLOSED,       // 流已关闭
    END_OF_FLOW,         // 流正常结束
};
```

### ML.5 关键配置参数 {#ml-5-关键配置参数}

```lua
stream = {
    max_flows = 476288,
    pruning_timeout = 30,
    prune_flows = 10,
    allowlist_cache = false,
    move_to_allowlist_on_excess = false
}
```

---
