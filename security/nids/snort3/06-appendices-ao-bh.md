---
title: "Snort 3 · 附录 AO–BH"
description: "附录AO：PerfMonitor性能监控 — 附录BH：Protocol IDs协议ID"
---

# Snort 3 · 附录 AO–BH

[返回总目录](../snort3_architecture_analysis)

## 附录AO：PerfMonitor性能监控 {#附录ao-perfmonitor性能监控}

### AO.1 性能监控配置 {#ao-1-性能监控配置}

```cpp
// network_inspectors/perf_monitor/perf_monitor.h

class PerfMonitor : public snort::Inspector {
public:
    PerfMonitor(PerfConfig*);
    ~PerfMonitor() override;
    
    void eval(snort::Packet*) override;
    
    // 流量跟踪器
    FlowTracker* get_flow_tracker();
    
    // 流IP跟踪器
    FlowIPTracker* get_flow_ip();
    
    // 更新跟踪器
    void update_trackers();
    
    // 轮换统计
    void rotate();
};
```

### AO.2 性能统计类型 {#ao-2-性能统计类型}

```cpp
// base_tracker.h

class BaseTracker {
public:
    // 获取格式化的输出
    virtual void print_interval(FILE*) = 0;
    
    // 获取统计
    virtual void get_stats() = 0;
};

// FlowTracker - 流统计
// FlowIPTracker - IP级别统计
// CpuTracker - CPU统计
```

---

## 附录AP：Stream UDP处理 {#附录ap-stream-udp处理}

### AP.1 UDP会话 {#ap-1-udp会话}

```cpp
// stream/stream_udp.h

class UdpSession : public Session {
public:
    UdpSession(Flow*);
    ~UdpSession() override;
    
    bool setup(Packet*) override;
    void clear() override;
    int process(Packet*) override;
    
    void update_flow(Flow*);
};
```

### AP.2 UDP重组 {#ap-2-udp重组}

```cpp
class UdpReassembler {
public:
    // 添加数据
    void add_data(const uint8_t* data, unsigned len);
    
    // 刷新数据
    void flush(uint8_t** data, unsigned* len);
};
```

---

## 附录AQ：Normalizer规范化器 {#附录aq-normalizer规范化器}

### AQ.1 TCP规范化 {#aq-1-tcp规范化}

```cpp
// network_inspectors/normalize/normalize.h

class Normalizer : public Inspector {
public:
    // 规范化选项
    enum NormalizerOption {
        NORM_OPT_NONE,
        NORM_OPT_IP4_ID,
        NORM_OPT_IP4_TTL,
        NORM_OPT_IP6_HH,
        NORM_OPT_TCP_ECN,
        NORM_OPT_TCP_NS,
        NORM_OPT_TCP_TRIM,
        NORM_OPT_TCP_URP,
        NORM_OPT_TCP_WSS,
        NORM_OPT_TCP_TS,
        NORM_OPT_TCP_REQ,
        NORM_OPT_TCP_PAD,
        NORM_OPT_TCP_LOSS,
        NORM_OPT_TCP燕,
        NORM_OPT_TCP_OPTS,
        NORM_OPT_TCP_PORTS,
    };
};
```

### AQ.2 规范化操作 {#aq-2-规范化操作}

```cpp
// 去除冗余数据
void normalize_tcp_trim(Packet* p);

// 规范化IP ID
void normalize_ip4_id(Packet* p);

// 规范化TTL
void normalize_ip4_ttl(Packet* p);

// 规范化TCP选项
void normalize_tcp_opts(Packet* p);
```

---

## 附录AR：Service Map和Classifier {#附录ar-service-map和classifier}

### AR.1 ServiceMap {#ar-1-servicemap}

```cpp
// detection/service_map.h

class ServiceMap {
public:
    // 添加服务
    void add(const char* service, SnortProtocolId id);
    
    // 查找服务
    SnortProtocolId find(const char* service);
    
    // 获取所有服务
    std::vector<std::string> get_all_services();
};
```

### AR.2 Classifier {#ar-2-classifier}

```cpp
// detection/classification.h

struct Classifier {
    const char* name;         // 分类名称
    int priority;              // 优先级
    const char* classification; // 分类描述
    const char* reference;    // 参考信息
};
```

---

## 附录AS：EventQueue事件队列 {#附录as-eventqueue事件队列}

### AS.1 SF_EVENTQ结构 {#as-1-sf-eventq结构}

```cpp
// events/sfeventq.h

struct EventNode {
    uint32_t gid;            // 生成器ID
    uint32_t sid;            // 签名ID
    uint32_t priority;       // 优先级
    uint32_t class_id;       // 分类ID
    
    struct timeval timestamp; // 时间戳
    
    EventNode* next;
};

class SF_EVENTQ {
public:
    SF_EVENTQ(unsigned max_events);
    ~SF_EVENTQ();
    
    // 添加事件
    int add_event(uint32_t gid, uint32_t sid, uint32_t priority);
    
    // 获取事件
    EventNode* get_event();
    
    // 清空
    void clear();
};
```

---

## 附录AT：Config Dump配置输出 {#附录at-config-dump配置输出}

### AT.1 配置输出格式 {#at-1-配置输出格式}

```cpp
// dump_config/json_config_output.h

class JsonConfigOutput : public ConfigOutput {
public:
    void init() override;
    void term() override;
    
    // 输出配置
    void dump(const SnortConfig*);
    
    // 输出模块配置
    void dump_module(const Module*);
};
```

### AT.2 文本输出 {#at-2-文本输出}

```cpp
// dump_config/text_config_output.h

class TextConfigOutput : public ConfigOutput {
public:
    void dump(const SnortConfig*);
    void dump_rules(const SnortConfig*);
};
```

---

## 附录AU：Target Based目标基础 {#附录au-target-based目标基础}

### AU.1 HostAttributes {#au-1-hostattributes}

```cpp
// target_based/host_attributes.h

class HostAttributes {
public:
    // 添加主机
    void add_host(const sfip_var_t*, HostAttributeData*);
    
    // 查找主机
    HostAttributeData* find_host(const SfIp*);
    
    // 获取服务
    SnortProtocolId get_service(const SfIp*, uint16_t port, IpProtocol proto);
};

// 主机属性数据
struct HostAttributeData {
    std::string hostname;
    std::vector<ServiceInfo> services;
    std::vector<ClientInfo> clients;
};
```

### AU.2 SnortProtocols {#au-2-snortprotocols}

```cpp
// target_based/snort_protocols.h

class SnortProtocols {
public:
    // 添加协议
    SnortProtocolId add(const char* name);
    
    // 查找协议
    SnortProtocolId find(const char* name);
    
    // 获取协议名称
    const char* get_name(SnortProtocolId);
};
```

---

## 附录AV：PacketManager数据包管理 {#附录av-packetmanager数据包管理}

### AV.1 PacketManager {#av-1-packetmanager}

```cpp
// protocols/packet_manager.h

class PacketManager {
public:
    // 解码数据包
    static void decode(Packet*);
    
    // 清理
    static void clear(Packet*);
    
    // 获取数据链路类型
    static int get_data_link_type();
};
```

### AV.2 解码流程 {#av-2-解码流程}

```cpp
void PacketManager::decode(Packet* p) {
    // 1. 获取链路层codec
    Codec* codec = CodecManager::get_codec(DLT);
    
    // 2. 解码链路层
    codec->decode(raw_data, codec_data, decode_data);
    
    // 3. 循环解码直到无更多协议
    while (codec_data.next_prot_id != ProtocolId::UNKNOWN) {
        Codec* next_codec = CodecManager::get_codec(codec_data.next_prot_id);
        next_codec->decode(raw_data, codec_data, decode_data);
    }
}
```

---

## 附录AW：Prox模块 {#附录aw-prox模块}

### AW.1 DCE/RPC {#aw-1-dce-rpc}

```cpp
// service_inspectors/dce_rpc/dce.h

class DceInspector : public Inspector {
public:
    DceInspector(DceRpcModule*);
    ~DceInspector() override;
    
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    
    // 处理DCE/RPC数据
    void process_dce_rpc(const uint8_t* data, unsigned len);
    
    // 验证连接
    bool validate_connection();
};
```

### AW.2 DCE/RPC操作 {#aw-2-dce-rpc操作}

```cpp
// DCE/RPC操作类型
enum DceOpNum {
    DCERPC_REQUEST = 0,
    DCERPC_RESPONSE = 2,
    DCERPC_FAULT = 3,
    DCERPC_BIND = 11,
    DCERPC_BINDACK = 12,
    DCERPC_ALTERCONTEXT = 15,
    DCERPC_ALTERCONTEXT_RESP = 16,
    DCERPC_AUTH3 = 17,
    DCERPC_SHUTDOWN = 20,
    DCERPC_CO_CANCEL = 22,
    DCERPC_ORPHANED = 23,
};
```

---

## 附录AX：IP碎片重组 {#附录ax-ip碎片重组}

### AX.1 IP碎片结构 {#ax-1-ip碎片结构}

```cpp
// protocols/frag.h

struct FragEntry {
    uint32_t src_ip;       // 源IP
    uint32_t dst_ip;       // 目标IP
    uint8_t protocol;     // 协议
    
    uint16_t ip_id;       // IP标识
    uint16_t frag_offset;  // 片段偏移
    
    time_t timeout;        // 超时时间
    
    uint8_t* data;        // 碎片数据
    unsigned len;          // 数据长度
    
    FragEntry* next;
};
```

### AX.2 碎片重组流程 {#ax-2-碎片重组流程}

```cpp
class Frag reassembler {
public:
    // 添加碎片
    bool add_frag(const Packet*);
    
    // 检查是否完整
    bool is_complete();
    
    // 获取重组数据
    uint8_t* get_reassembled(unsigned* len);
    
    // 清理过期碎片
    void prune();
};
```

---

## 附录AY：正则表达式PCRE {#附录ay-正则表达式pcre}

### AY.1 PcreData结构 {#ay-1-pcredata结构}

```cpp
// detection/pcre.h

struct PcreData {
    pcre2_code* re;           // 编译的正则
    pcre2_match_data* matches; // 匹配数据
    
    // 正则选项
    uint32_t options;
    
    // 缓冲区选择
    uint8_t buf_select;
    
    // 捕获组
    int capture_dir;   // 1 = forward, -1 = backward
    
    // 匹配偏移
    int match_offset;
    int match_depth;
    
    // 编译标志
    bool compile_anchored;
    bool compile_dot_all;
    bool compile_multi;
    bool compile_dot_not_newline;
    bool compile_ungreedy;
};
```

### AY.2 PCRE匹配流程 {#ay-2-pcre匹配流程}

```cpp
PcreOption::eval(Cursor& c, Packet* p) {
    // 1. 获取缓冲区
    const uint8_t* buf = c.buffer();
    unsigned len = c.length();
    
    // 2. 执行正则匹配
    int rc = pcre2_match(
        data->re,
        buf,
        len,
        0,              // 起始偏移
        PCRE2_ANCHORED, // 选项
        data->matches,
        nullptr
    );
    
    if (rc < 0)
        return NO_MATCH;
        
    // 3. 获取捕获组
    for (int i = 0; i < rc; i++) {
        // 处理捕获组
    }
    
    return MATCH;
}
```

---

## 附录AZ：Sfrt检索表 {#附录az-sfrt检索表}

### AZ.1 SFRT结构 {#az-1-sfrt结构}

```cpp
// sfrt/sfrt.h

class SfrtTable {
public:
    enum flags_t {
        SRC_ANY = 0x01,
        DST_ANY = 0x02,
        BOTH_ANY = 0x03,
        EXCEPT = 0x04
    };
    
    // 添加规则
    void add(unsigned, unsigned, unsigned, void*);
    
    // 查找
    void* lookup(const SfIp* src, const SfIp* dst, uint8_t proto,
                 uint16_t sport, uint16_t dport);
    
    // 编译
    void compile();
};
```

---

## 附录BA：Host Tracker主机追踪 {#附录ba-host-tracker主机追踪}

### BA.1 HostTrackerEntry {#ba-1-hosttrackerentry}

```cpp
// host_tracker/host_tracker.h

class HostTrackerEntry {
public:
    // 获取主机IP
    const SfIp* get_ip() const { return &host_ip; }
    
    // 活跃检测
    void set_active() { last_seen = time(nullptr); }
    bool is_active(time_t timeout) const;
    
    // 服务信息
    void add_service(uint16_t port, IpProtocol proto, SnortProtocolId);
    SnortProtocolId get_service(uint16_t port, IpProtocol proto) const;
    
    // 流统计
    FlowStats* get_flow_stats() { return &flow_stats; }
    
private:
    SfIp host_ip;                    // 主机IP
    time_t first_seen;               // 首次发现时间
    time_t last_seen;               // 最后发现时间
    FlowStats flow_stats;           // 流统计
    
    std::map<uint16_t, SnortProtocolId> services; // 端口到服务的映射
};
```

### BA.2 HostTrackerModule {#ba-2-hosttrackermodule}

```cpp
class HostTrackerModule : public snort::Module {
public:
    // 加载主机属性文件
    bool load_host_attributes(const char* file);
    
    // 查找主机
    HostTrackerEntry* find_host(const SfIp* ip);
};
```

---

## 附录BB：PubSub事件详解 {#附录bb-pubsub事件详解}

### BB.1 事件注册 {#bb-1-事件注册}

```cpp
// pub_sub目录下定义事件

// HTTP事件
struct HttpEvent : public DataEvent {
    HttpEvent(Type t) : type(t) { }
    enum Type {
        REQUEST_HEADERS,
        REQUEST_BODY,
        RESPONSE_HEADERS,
        RESPONSE_BODY,
        TRANSACTION
    };
    
    Type type;
    const char* method;
    const char* uri;
    int status_code;
};

// DNS事件
struct DnsEvent : public DataEvent {
    DnsEvent() { }
    uint16_t id;
    uint16_t flags;
    uint8_t num_questions;
    uint8_t num_answers;
    // ...
};
```

### BB.2 事件发布 {#bb-2-事件发布}

```cpp
// 发布事件
DataBus::publish(pub_id, HTTP_REQUEST_HEADERS_EVENT, event, flow);

// 订阅事件
class MyHandler : public DataHandler {
    void handle(DataEvent& e, Flow* f) override {
        if (e.is("http_event")) {
            HttpEvent& he = static_cast<HttpEvent&>(e);
            // 处理HTTP事件
        }
    }
};
```

---

## 附录BC：MpseManager搜索引擎管理 {#附录bc-mpsemanager搜索引擎管理}

### BC.1 MpseManager {#bc-1-mpsemanager}

```cpp
// managers/mpse_manager.h

class MpseManager {
public:
    // 加载搜索引擎
    static void load_search_engines();
    
    // 获取搜索引擎
    static Mpse* get_search_engine(const char* name);
    
    // 创建批量搜索
    static MpseBatch* create_batch();
    
    // 检查能力
    static bool is_async_capable(const MpseApi*);
    static bool is_poll_capable(const MpseApi*);
};
```

### BC.2 批量搜索 {#bc-2-批量搜索}

```cpp
// framework/mpse_batch.h

class MpseBatch {
public:
    // 添加模式
    void add_pattern(const uint8_t* pat, unsigned len, void* user);
    
    // 执行搜索
    void execute(Mpse* engine);
    
    // 获取结果
    std::vector<MpseResult> get_results() const;
};
```

---

## 附录BD：Stream Splitter详解 {#附录bd-stream-splitter详解}

### BD.1 HttpStreamSplitter {#bd-1-httpstreamsplitter}

```cpp
// service_inspectors/http_inspect/http_stream_splitter.h

class HttpStreamSplitter : public HttpStreamSplitterBase {
public:
    HttpStreamSplitter(bool is_client_to_server, HttpInspect* my_inspector);
    
    // PAF扫描
    Status scan(Flow*, const uint8_t* data, uint32_t length,
                uint32_t* flush_offset) override;
    
    // 重组
    const snort::StreamBuffer reassemble(Flow*, unsigned total,
        unsigned, const uint8_t* data, unsigned len,
        uint32_t flags, unsigned& copied) override;
    
    // 是否是PAF
    bool is_paf() override { return true; }
};
```

### BD.2 切割状态机 {#bd-2-切割状态机}

```cpp
// http_cutter.h

class HttpCutter {
public:
    enum State {
        START,
        HEADER,
        BODY,
        DONE
    };
    
    // 处理数据
    CutDirection process(const uint8_t* data, unsigned len,
                        HttpEnums::SectionType& section);
    
    // 获取切割点
    unsigned get_cutoff() const { return cutoff; }
    
private:
    State state = START;
    unsigned cutoff = 0;
    unsigned header_len = 0;
};
```

---

## 附录BE：Detection模块配置 {#附录be-detection模块配置}

### BE.1 FastPatternConfig {#be-1-fastpatternconfig}

```cpp
// detection/fp_config.h

class FastPatternConfig {
public:
    // 是否启用快速模式
    bool is_fast_pattern_enabled() const { return enabled; }
    
    // 获取搜索引擎
    const MpseApi* get_search_api() const { return search_api; }
    
    // 获取卸载搜索引擎
    const MpseApi* get_offload_search_api() const { return offload_search_api; }
    
    // 最大模式数
    unsigned get_max_pattern_len() const { return max_pattern_len; }
};
```

### BE.2 DetectionModule {#be-2-detectionmodule}

```cpp
// detection/detection_module.h

class DetectionModule : public snort::Module {
public:
    DetectionModule();
    ~DetectionModule() override;
    
    // 配置检测引擎
    bool configure(SnortConfig*) override;
    
    // 获取快速模式配置
    FastPatternConfig* get_fp_config() const;
};
```

---

## 附录BF：Actions模块详解 {#附录bf-actions模块详解}

### BF.1 AlertModule {#bf-1-alertmodule}

```cpp
// loggers/alert_fast/alert_fast.h

class AlertFastModule : public snort::Module {
public:
    AlertFastModule();
    ~AlertFastModule() override;
    
    bool begin(const char*, int, SnortConfig*) override;
    bool set(const char*, snort::Value&, SnortConfig*) override;
    
    Usage get_usage() const override { return GLOBAL; }
};
```

### BF.2 LogModule {#bf-2-logmodule}

```cpp
// loggers/log_pcap/log_pcap.h

class LogPcapModule : public snort::Module {
public:
    LogPcapModule();
    ~LogPcapModule() override;
    
    // 开始新的pcap文件
    void begin_pcap(const char* filename);
    
    // 写入数据包
    void log_packet(const Packet*);
};
```

---

## 附录BG：Inspector类型详解 {#附录bg-inspector类型详解}

### BG.1 InspectorType枚举 {#bg-1-inspectortype枚举}

```cpp
// framework/inspector.h

enum InspectorType {
    IT_PASSIVE,   // 仅配置或数据消费者
    IT_PACKET,    // 仅处理原始包
    IT_STREAM,    // 流跟踪和重组
    IT_NETWORK,   // 处理无服务的包
    IT_SERVICE,   // 提取和分析服务PDU
    IT_CONTROL,   // 检测前处理所有包
    IT_PROBE,     // 检测后处理所有包
    IT_PROBE_FIRST // 检测前处理所有包
};
```

### BG.2 各类型用途 {#bg-2-各类型用途}

| 类型 | 用途 | 示例 |
|-----|------|-----|
| IT_PASSIVE | 配置/数据消费 | binder, file_log |
| IT_PACKET | 原始包处理 | normalize, capture |
| IT_STREAM | 流重组 | stream_tcp, stream_udp |
| IT_NETWORK | 无服务包 | arp, bo |
| IT_SERVICE | 服务检测 | http_inspect, dns |
| IT_CONTROL | 预处理 | appid |
| IT_PROBE | 后处理 | perf_monitor, port_scan |
| IT_PROBE_FIRST | 最早处理 | packet_capture |

---

## 附录BH：Protocol IDs协议ID {#附录bh-protocol-ids协议id}

### BH.1 IpProtocol枚举 {#bh-1-ipprotocol枚举}

```cpp
// protocols/ip.h

namespace IpProtocol {
    enum IpProtocol : uint8_t {
        IP = 0,
        ICMP = 1,
        TCP = 6,
        UDP = 17,
        GRE = 47,
        ESP = 50,
        AH = 51,
        ICMP6 = 58,
        // ...
    };
}
```

### BH.2 PktType数据包类型 {#bh-2-pkttype数据包类型}

```cpp
// framework/decode_data.h

enum class PktType : uint8_t {
    NONE,
    IP,
    TCP,
    UDP,
    ICMP,
    USER,   // 用户级协议
    FILE,   // 文件数据
    PDU,    // 协议数据单元
    MAX
};
```

---
