# codecs 模块 — 协议解码器

## 概述

`codecs` 模块负责网络协议的解析与编码，将原始字节流解码为分层协议结构(IPv4/IPv6/TCP/UDP/ICMP等)。

## 文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| codec_api.h | 25 | 动态加载接口 |
| codec_module.h | ~71 | Snort Module |
| ip/checksum.h | 334 | 校验和计算 |

### IPv4 解码器 (ip/)

| 文件 | 行数 | 功能 |
|------|------|------|
| cd_tcp.cc | 836 | TCP解码 |
| cd_udp.cc | 657 | UDP解码 |
| cd_icmp4.cc | 645 | ICMPv4解码 |
| cd_icmp6.cc | 515 | ICMPv6解码 |
| cd_ipv6.cc | 730 | IPv6解码 |
| cd_frag.cc | 190 | IP分片解码 |
| cd_gre.cc | 358 | GRE隧道解码 |
| cd_auth.cc | 172 | IPSec AH解码 |
| cd_esp.cc | 227 | IPSec ESP解码 |
| cd_igmp.cc | 138 | IGMP解码 |
| cd_hop_opts.cc | 143 | IPv6逐跳选项 |
| cd_dst_opts.cc | 134 | IPv6目的选项 |
| cd_routing.cc | 163 | IPv6路由选项 |
| cd_mobility.cc | 143 | IPv6移动性选项 |
| cd_pgm.cc | 212 | PGM可靠传输 |
| cd_bad_proto.cc | 98 | 未知协议 |

**codecs总计: 约11479行**

## 类层次

```
Codec (基类 - framework/codec.h)
│
├─── Codec 体系 (插件式)
│    ├── EthernetCodec
│    ├── IPv4Codec / IPv6Codec
│    ├── TCPCodec / UDPCodec
│    ├── ICMPv4Codec / ICMPv6Codec
│    ├── GRECodec
│    ├── EspCodec / AhCodec
│    └── ... (其他协议)
│
└─── 辅助类
     ├── StreamSplitter (流分割器)
     │    ├── AtomSplitter (定长分割)
     │    ├── LogSplitter (变长记录分割)
     │    └── StopAndWaitSplitter (停等分割)
     │
     └── PAF_State (协议感知Flush状态)
```

## 核心类: Codec

```cpp
class SO_PUBLIC Codec
{
public:
    virtual ~Codec() = default;

    // 解码: raw -> Packet结构
    virtual bool decode(
        RawData&,          // 原始数据
        CodecData&,        // 解码状态
        const CodecFlags,  // 标志
        snort::Packet*     // 输出Packet
    ) = 0;

    // 编码: Packet -> 原始字节
    virtual void encode(
        snort::Packet*,
        EncState&,
        Buffer&
    ) = 0;

    // 格式检查
    virtual void check(
        snort::Packet*
    ) const;

    // 获取协议名称/ID
    const char* get_name() const;
    ProtocolId get_protocol_id() const;

    // 日志/追踪
    void log_protocol_detail(
        TextLog&, snort::Packet*
    ) const;
};
```

## 核心函数

### 解码流程
```cpp
// PacketManager 调用链
bool PacketManager::process() {
    // 1. 获取原始数据
    RawData rd(daq_msg, data, len);

    // 2. 调用根codec解码
    Codec* root = get_root_codec(dlt);
    root->decode(rd, codec_data, flags, p);

    // 3. 循环解析下一层
    while (next_prot_id != ProtocolId::NONE) {
        Codec* next = get_codec(next_prot_id);
        next->decode(rd, codec_data, flags, p);
    }
}
```

### 协议标识
```cpp
// CodecFlags 定义
constexpr uint16_t CODEC_DF = 0x0001;        // 不分片标志
constexpr uint16_t CODEC_UNSURE_ENCAP = 0x0002; // 封装层不确定
constexpr uint16_t CODEC_ENCAP_LAYER = 0x0004;  // 回退封装层
constexpr uint16_t CODEC_STREAM_REBUILT = 0x0100; // 流重组包
constexpr uint16_t CODEC_LAYERS_EXCEEDED = 0x400; // 层级超限
```

### TCP解码关键逻辑
```cpp
// cd_tcp.cc
class TcpModule : public BaseCodecModule {
    bool decode(RawData& rd, CodecData& cd, const CodecFlags&,
        snort::Packet* p) override {
        // 1. 检查TCP头部长度
        // 2. 解析TCP选项
        // 3. 校验校验和
        // 4. 更新Session状态
        // 5. 设置下一层协议
    }
};
```

## 模块交互

```
packet_io
    │
    ▼
PacketManager::process()
    │
    ├──► root_codec (Ethernet/Loopback/...)
    │     │
    │     ▼
    │    IPv4Codec / IPv6Codec
    │     │
    │     ▼
    │    TCPCodec / UDPCodec / ICMPv4/6Codec
    │     │
    │     ▼
    │    应用层协议 (待检测模块处理)
    │
    └──► detection (规则匹配)
```

## IP分片重组

```cpp
// ip_defrag.h
class Defrag {
    void process(snort::Packet*, FragTracker*);
    int insert(snort::Packet*, FragTracker*, FragEngine*);
    int add_frag_node(FragTracker*, FragEngine*,
        const uint8_t* fragStart, int16_t fragLength,
        char lastfrag, int16_t len, uint16_t slide,
        uint16_t trunc, uint16_t frag_offset,
        Fragment* left, Fragment** retFrag);
};
```

## 校验和计算

```cpp
// ip/checksum.h
namespace ip {
uint16_t checksum(const uint16_t* buf, size_t len);
uint16_t ipv6_checksum(const ip::IpApi&, uint8_t, const uint8_t*,
    uint16_t len);
bool validate_checksum(const snort::Packet*);
}
```

## 协议映射

```
DLT            → Root Codec
─────────────────────────────
Ethernet       → EthernetCodec
Linux Cooked  → CookedCodec
Raw IP         → IPv4Codec / IPv6Codec
...
```

| ProtocolId | Codec |
|-----------|-------|
| IP4 | IPv4Codec |
| IP6 | IPv6Codec |
| TCP | TCPCodec |
| UDP | UDPCodec |
| ICMP4 | ICMPv4Codec |
| ICMP6 | ICMPv6Codec |
| GRE | GRECodec |
| ESP | EspCodec |
| AH | AhCodec |
