---
type: entity
tags: [snort3, intrusion-detection, codec, network-parsing, linux]
created: 2026-05-27
sources: [github-snort3-codecs]
---

# Snort3 Codecs

## 定义

Snort3 的 **codec**（编解码器）是协议解析的核心插件，负责从链路层到传输层的每层协议头的解码与验证。codec 不做业务处理，只做基础的逐层解析和合法性检查。

## 架构概览

### 目录结构

| 目录 | 用途 |
|------|------|
| `codecs/root/` | 顶层 codec（DLT 类型驱动：Ethernet、Raw IP） |
| `codecs/link/` | 链路层协议：VLAN、MPLS、ARP、PPPoE、LLC、ERSPAN |
| `codecs/ip/` | IP 层协议：IPv4/IPv6、TCP、UDP、ICMP、IGMP、GRE、ESP、IPv6 扩展头 |
| `codecs/misc/` | 隧道协议：GTP、VXLAN、GENEVE、Teredo、ICMP 嵌入 IP |

### Codec 基类

所有 codec 继承 `Codec` 基类（`framework/codec.h`），核心接口：

```cpp
class Codec {
    virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;
    virtual bool encode(const uint8_t*, uint16_t, EncState&, Buffer&, Flow*) = 0;
    virtual void update(const IpApi&, EncodeFlags, uint8_t*, uint16_t, uint32_t&) { }
};
```

`CodecData` 携带协议间状态：
- `next_prot_id` — 下一层协议 ID
- `lyr_len` — 当前层有效长度
- `codec_flags` — 标志位（如 `CODEC_ETHER_NEXT`、`CODEC_TEREDO_SEEN`）
- `tunnel_bypass` — 隧道旁路标记

## 协议解码树

### 以太网帧 → IP → TCP/UDP/ICMP（主流路径）

```
Ethernet (DLT_EN10MB, ethertype)
│
├── 0x8100 / 0x9200/0x9100 → VLAN (802.1Q/802.1AD)
│       └── 若 proto <= 1518 → LLC; 否则 → 内层协议
│
├── 0x8847 / 0x8848 → MPLS (单播/组播)
│       └── Label 0 → IPv4; Label 2 → IPv6; 否则 auto → nibble 检测
│
├── 0x0800 → IPv4
│       ├── protocol=1  → ICMPv4
│       ├── protocol=2  → IGMP
│       ├── protocol=6  → TCP
│       ├── protocol=17 → UDP
│       ├── protocol=41 → IPv6 (IP-in-IP)
│       ├── protocol=43 → IPv6 Routing Header
│       ├── protocol=44 → IPv6 Fragment
│       ├── protocol=46 → GRE
│       ├── protocol=50 → ESP
│       ├── protocol=51 → Authentication Header
│       ├── protocol=58 → ICMPv6
│       ├── protocol=59 → IPv6 No Next Header
│       ├── protocol=60 → Hop-by-Hop Options
│       └── protocol=63 → IPv6 Mobility
│
├── 0x86DD → IPv6
│       └── next_header 同上 IP protocol 字段
│
├── 0x0806 → ARP (终端)
├── 0x8864 → PPPoE Session
│       └── 0x0021 → IPv4; 0x0057 → IPv6; 0x002F → VJ-Uncompressed
└── 0x8863 → PPPoE Discovery (终端)
```

### UDP 隧道检测（端口驱动）

```
UDP
├── port 2152 / 3386 → GTP → IPv4/IPv6
├── port 4789       → VXLAN → Ethernet (递归回 ethertype)
├── port 6081       → GENEVE → Ethernet 或 proto 指定
└── port 3544       → Teredo → IPv6
```

### ICMP/ICMPv6 嵌入 IP

```
ICMPv4 / ICMPv6 (error messages)
└── 嵌入 IP 头 → icmp4_ip / icmp6_ip → 重新解码内层 IP
```

### 完整层叠顺序（典型包）

```
Ethernet → [VLAN×N] → [MPLS×N] → IPv4/IPv6
         → [IPv6 扩展头: HopOpts → DstOpts → Routing → Fragment]
         → TCP/UDP/ICMP4/ICMPv6/GRE/ESP...
             → [UDP 隧道: GTP/VXLAN/GENEVE/Teredo → 递归回对应层]
```

## Ethertype 映射表

| Ethertype (hex) | 下一层 Codec |
|----------------|-------------|
| 0x0800 | ipv4 |
| 0x86DD | ipv6 |
| 0x0806 | arp |
| 0x8100 | vlan |
| 0x9100 / 0x9200 | vlan (QinQ) |
| 0x8847 | mpls (unicast) |
| 0x8848 | mpls (multicast) |
| 0x8864 | pppoe_sess |
| 0x8863 | pppoe_disc |
| 0x8865 | ppp_encap |
| 0x8903 | fabricpath → eth |
| 0x8926 | trans_bridge → eth (递归) |
| 0x9001 | ciscometadata |
| 0x88BE | erspan2 → trans_bridge |
| 0x88BF | erspan3 → trans_bridge |
| ≤ 0x05DC 或 ≤ 1500 | llc |

## IP Protocol 映射表

| IP Protocol | 下一层 Codec |
|------------|-------------|
| 1 | icmp4 |
| 2 | igmp |
| 6 | tcp |
| 17 | udp |
| 41 | ipv6 (IP-in-IP) |
| 43 | routing (IPv6) |
| 44 | frag (IPv6) |
| 46 | gre |
| 47 | gre |
| 50 | esp |
| 51 | auth |
| 58 | icmp6 |
| 59 | no_next |
| 60 | hop_opts |
| 63 | mobility |
| 135 | dstopts |
| 132 | SCTP (未实现 → FINISHED_DECODE) |

## 关键验证机制

### IPv4 验证（GID_DECODE = 116）

| SID | 描述 |
|-----|------|
| 1-6 | IPv4 头部长度、校验和、选项校验 |
| 150-151 | 环回/同源同目标检测 |
| 182 | TTL 检查（最小值 64） |
| 450 | 未知/未分配 IP 协议号 |
| 430 | Don't Fragment 位 + Fragment Offset 冲突 |

### IPv6 验证

| SID | 描述 |
|-----|------|
| 270-273 | TTL/扩展头截断 |
| 276-280 | 源/目的地址校验（零地址、多播作用域） |
| 281-296 | 扩展头顺序、重复检测 |
| 292 | DSTOPTS + ROUTING 同时出现 |

### TCP 验证

| SID | 描述 |
|-----|------|
| 45-47 | TCP 头部长度、最小长度、Offset 异常 |
| 54-63 | TCP 选项校验（长度、类型、WScale） |
| 400-401 | XMAS 扫描检测 |
| 173-176 | SYN-FIN、SYN-RST、无 ACK 等异常标志 |

### UDP 验证

| SID | 描述 |
|-----|------|
| 95-98 | UDP 头部长度、包长异常 |
| 200-201 | 端口零检测 |
| 198 | 大包检测（> 4000 bytes） |

## Codec 标志位

| 标志 | 含义 |
|------|------|
| `CODEC_DF` | IPv4 Don't Fragment 位 |
| `CODEC_ENCAP_LAYER` | 封装层回退标记（解码失败时回退到上一层） |
| `CODEC_TEREDO_SEEN` | 见过 Teredo 隧道 |
| `CODEC_NON_IP_TUNNEL` | 非 IP 隧道 |
| `CODEC_IP6_EXT_OOO` | IPv6 扩展头顺序错乱 |
| `CODEC_ETHER_NEXT` | 以太网帧内有额外封装层 |
| `CODEC_LAYERS_EXCEEDED` | 协议层数超限（最大 8 层） |

## 隧道旁路（Tunnel Bypass）

配置项控制以下隧道类型的检测旁路：
- `geneve_decap` — GENEVE 解封装
- `vxlan_decap` — VXLAN 解封装
- `gtp_decap` — GTP 解封装
- `teredo_decap` — Teredo 解封装

设置 `codec.tunnel_bypass = true` 后，Snort 跳过内层内容检测。

## 插件注册机制

`codec_api.cc` 中 `load_codecs()` 通过 `PluginManager::load_plugins()` 注册所有 codec：

```cpp
// 动态 codec（不锁定）
PluginManager::load_plugins(cd_ipv4);
PluginManager::load_plugins(cd_ipv6);
PluginManager::load_plugins(cd_tcp);
PluginManager::load_plugins(cd_hopopts);

// 静态 codec（#ifdef STATIC_CODECS）
PluginManager::load_plugins(cd_eth);
PluginManager::load_plugins(cd_vlan);
PluginManager::load_plugins(cd_mpls);
// ... 其余 ~30 个 codec
```

## 相关概念

- [[network-packet-decoding]]
- [[ethernet-frame]]
- [[ipv4]]
- [[ipv6]]
- [[tcp]]
- [[udp]]
- [[vlan]]
- [[mpls]]
- [[snort3]]

## 来源详情

- [[github-snort3-codecs]]
