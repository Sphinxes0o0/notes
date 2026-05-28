---
type: source
source-type: github
title: "snort3/src/codecs — Protocol Decoder Tree"
author: "Cisco / Snort Team"
date: 2024-2025
path: ~/workspace/github/snort3/src/codecs/
summary: "Snort3 网络协议解码器 codec 框架：Ethernet→IP→TCP/UDP/ICMP 完整协议树、codec 注册机制、层叠解析顺序"
---

# snort3/src/codecs

## 核心定位

`codecs/` 是 Snort3 的**协议解析核心**，从原始帧中逐层提取和验证协议头。所有 codec 遵循 `framework/codec.h` 定义的 API，不做业务处理，只做逐层解码和合法性检查。

## 目录布局

```
codecs/
├── codec_api.cc/h        # load_codecs() — 插件注册入口
├── codec_module.cc/h      # decode 规则模块（GID_DECODE = 116）
├── dev_notes.txt          # 开发者注释
│
├── root/                  # 第一层：DLT 类型分发
│   ├── cd_eth.cc          # Ethernet (DLT_EN10MB)
│   └── cd_raw.cc          # Raw IP (DLT_RAW)
│
├── link/                  # 链路层
│   ├── cd_vlan.cc         # 802.1Q / 802.1AD
│   ├── cd_mpls.cc         # MPLS 单播/组播
│   ├── cd_arp.cc          # ARP / RARP
│   ├── cd_pppoe.cc        # PPPoE Discovery / Session
│   ├── cd_ppp_encap.cc    # PPP 封装
│   ├── cd_llc.cc          # Logical Link Control
│   ├── cd_trans_bridge.cc # 透明桥接
│   ├── cd_fabricpath.cc   # Cisco FabricPath
│   ├── cd_ciscometadata.cc# Cisco Metadata
│   ├── cd_erspan2.cc      # ERSPAN Type 2
│   └── cd_erspan3.cc      # ERSPAN Type 3
│
├── ip/                    # IP 层及其上层协议
│   ├── cd_ipv4.cc         # IPv4
│   ├── cd_ipv6.cc         # IPv6
│   ├── cd_tcp.cc          # TCP
│   ├── cd_udp.cc          # UDP（含隧道端口检测）
│   ├── cd_icmp4.cc        # ICMPv4
│   ├── cd_icmp6.cc        # ICMPv6
│   ├── cd_igmp.cc         # IGMP
│   ├── cd_gre.cc          # GRE (v0/v1)
│   ├── cd_esp.cc          # ESP
│   ├── cd_frag.cc         # IPv6 Fragment
│   ├── cd_hop_opts.cc     # IPv6 Hop-by-Hop Options
│   ├── cd_dst_opts.cc     # IPv6 Destination Options
│   ├── cd_routing.cc      # IPv6 Routing Header
│   ├── cd_auth.cc         # IP Authentication Header
│   ├── cd_mobility.cc     # IPv6 Mobility Header
│   ├── cd_no_next.cc      # IPv6 No Next Header (sentinel)
│   ├── cd_bad_proto.cc    # 不支持协议（SWIPE/SUN_ND）告警
│   ├── cd_pgm.cc          # PGM (Pragmatic General Multicast)
│   └── checksum.h         # 校验和计算辅助
│
└── misc/                  # 隧道与特殊协议
    ├── cd_gtp.cc           # GPRS Tunneling Protocol
    ├── cd_vxlan.cc         # VXLAN
    ├── cd_geneve.cc        # GENEVE
    ├── cd_teredo.cc        # Teredo隧道
    ├── cd_icmp4_ip.cc      # ICMPv4 嵌入 IP
    ├── cd_icmp6_ip.cc      # ICMPv6 嵌入 IP
    ├── cd_llc.cc           # LLC（重复）
    └── cd_default.cc       # Unknown Protocol sentinel
```

## 协议栈解析流程

### 1. 入口：Root Codec（DLT 分发）

`cd_eth.cc` 处理 `DLT_EN10MB`（以太网）和 `DLT_PPP_ETHER`，根据 **ethertype** 分发到 link 层 codec。

`cd_raw.cc` 处理 `DLT_RAW`，根据首 nibble 判断：`0x4*` → IPv4，`0x6*` → IPv6。

### 2. Link 层

- **VLAN** (`cd_vlan.cc`)：解析 802.1Q/802.1AD VID，支持 QinQ 配置（`extra_tpid_ether_types`）。若内层 proto ≤ 1518 继续走 LLC，否则按 ethertype 分发。
- **MPLS** (`cd_mpls.cc`)：标签 0 → IPv4，标签 2 → IPv6，否则 nibble 自检测（4=IPv4, 6=IPv6）。验证保留标签（0-15）和栈深度（`max_stack_depth`）。
- **ERSPAN** (`cd_erspan2/3.cc`)：版本校验后递交给透明桥接 codec，最终递归回 Ethernet。
- **Transparent Bridge** (`cd_trans_bridge.cc`)：提取内部 Ethernet 头的 ethertype，递归回 `cd_eth`。

### 3. IP 层

- **IPv4** (`cd_ipv4.cc`)：验证头部校验和、IP 选项、源/目的地址（广播/多播/保留地址）、TTL（≥64）、分片偏移与 DF 位冲突。
- **IPv6** (`cd_ipv6.cc`)：验证版本、跳数限制（≥64）、源/目的地址（零地址/多播作用域）、ISATAP 欺骗检测。扩展头顺序由 `CheckIPv6ExtensionOrder()` 强制校验（HopOpts → DstOpts → Routing → Fragment）。

### 4. Transport 层

- **TCP** (`cd_tcp.cc`)：最小 20 字节头，校验和，选项（长度/类型/WScale），标志异常（XMAS、SYN-FIN、SYN-RST、无 ACK）、NAPTHA 漏洞检测。
- **UDP** (`cd_udp.cc`)：最小 8 字节头，端口检测隧道类型（GTP 2152/3386、VXLAN 4789、GENEVE 6081、Teredo 3544）。
- **ICMPv4/ICMPv6** (`cd_icmp4/6.cc`)：类型/代码校验，嵌入式 IP 头验证，ICMPv6 的 NDP 选项和 MTU（≥1280）校验。

### 5. 隧道协议

- **GTP** (`cd_gtp.cc`)：v0（20 字节头）和 v1（12 字节 + 扩展）双重支持，递交给 IPv4/IPv6。
- **VXLAN** (`cd_vxlan.cc`)：标志 0x08 校验，递交给 Ethernet（递归回 ethertype）。
- **GENEVE** (`cd_geneve.cc`)：版本 0 校验，可变选项长度，关键标志一致性检查。
- **Teredo** (`cd_teredo.cc`)：认证/源指示标志检测，设置 `CODEC_TEREDO_SEEN`，递交给 IPv6。

## Codec 注册机制

```cpp
// codec_api.cc
void load_codecs() {
    // 动态链接 codec（始终加载）
    PluginManager::load_plugins(cd_ipv4);
    PluginManager::load_plugins(cd_ipv6);
    PluginManager::load_plugins(cd_tcp);
    PluginManager::load_plugins(cd_hopopts);

#ifdef STATIC_CODECS
    // 静态编译 codec（~30 个）
    PluginManager::load_plugins(cd_eth);
    PluginManager::load_plugins(cd_vlan);
    // ...
#endif
}
```

每个 codec 暴露 `BaseApi*` 指针数组：

```cpp
#ifdef BUILDING_SO
SO_PUBLIC const BaseApi* snort_plugins[] = ...
#else
const BaseApi* cd_<name>[] = ...
#endif
{
    &codec_api.base,
    nullptr
};
```

`PluginManager::load_plugins()` 将这些 API 注册到全局插件表。

## 核心数据结构

### CodecData（协议间状态）

```cpp
struct CodecData {
    ProtocolId next_prot_id;   // 下一层协议 ID
    uint16_t lyr_len;          // 当前层有效长度
    uint16_t invalid_bytes;    // 当前层无效字节数
    uint32_t proto_bits;       // 协议位图（传播到 Packet）
    uint16_t codec_flags;      // 标志位
    uint8_t ip_layer_cnt;      // IP 层计数（检测封装循环）
    bool tunnel_bypass;        // 隧道旁路标记
};
```

### 协议 ID 枚举

- **Ethertype**：以太网类型（`ETHERTYPE_IPV4 = 0x0800` 等）
- **IpProtocol**：IP 协议号（`TCP=6`, `UDP=17`, `GRE=47` 等）
- **ProtocolId**：全局协议 ID（含 `IP_EMBEDDED_IN_ICMP4`、`VXLAN`、`GTP` 等）

## 验证规则体系

所有 decoder 告警使用 `GID_DECODE = 116`，规则定义在 `codec_module.cc`：

- SID 1-6：IPv4 头部错误
- SID 45-63：TCP 选项和标志异常
- SID 95-98：UDP 长度错误
- SID 105-134：ICMP/ICMPv6 错误
- SID 150-176：MPLS、VLAN 错误
- SID 250-296：IPv6 扩展头错误
- SID 400-476：各类协议异常（XMAS 扫描、smurf、fragment 等）

## 设计特点

1. **插件化**：每种协议独立 codec，可独立加载/替换
2. **递归解析**：Transparent Bridge、ERSPAN 等协议递归回 Ethernet，形成树形解析
3. **扩展头有序**：IPv6 扩展头必须在 RFC 8200 规定的顺序内
4. **IP 层计数**：防止 4in4、6in6 等嵌套隧道无限递归（`ip_layer_cnt`）
5. **隧道旁路**：可配置跳过 GTP/VXLAN/GENEVE/Teredo 内层检测
6. **CODEC_ENCAP_LAYER 回退**：当某层解码失败时，自动回退到上一层继续尝试

## 相关页面

- [[entities/linux/snort3/snort3-codecs]] — 概念实体页
- [[snort3]] — Snort3 概览
