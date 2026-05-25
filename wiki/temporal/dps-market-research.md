---
type: journal
tags: [idps, nids, security, market-research]
created: 2026-05-25
---

# IDPS 市场调研报告

调研日期: 2026/05/25
调研对象: Snort 3, Suricata, Zeek, Palo Alto NDR, Fortinet FortiGate

---

## 一、检测能力对比

### 1.1 协议解析

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **HTTP** | HTTP/1.1, HTTP/2 | HTTP/1.1, HTTP/2 | HTTP/1.1, HTTP/2 | HTTP/1.1, HTTP/2, HTTP/3 | HTTP/1.1, HTTP/2, HTTP/3 |
| **DNS** | DNS | DNS, DoT, DoH | DNS | DNS, DoT, DoH | DNS, DoT, DoH |
| **TLS/SSL** | TLS 1.0-1.3 | TLS 1.0-1.3 | TLS 1.0-1.3 | TLS 1.0-1.3 | TLS 1.0-1.3 |
| **SSH** | Yes | Yes | Yes | Yes | Yes |
| **SMB** | SMB1/2/3 | SMB1/2/3 | SMB1/2/3 | SMB1/2/3 | SMB1/2/3 |
| **FTP** | Yes | Yes | Yes | Yes | Yes |
| **SMTP** | Yes | Yes | Yes | Yes | Yes |
| **工业协议** | Modbus, DNP3, IEC 104 | Modbus, DNP3, ENIP | DNP3, Modbus, BACnet | Modbus, DNP3 | Modbus, DNP3, IEC 104, MMS |
| **数据库** | DCE/RPC | MySQL, MSSQL, PostgreSQL | No | Oracle, MySQL, MSSQL | Oracle, MySQL, MSSQL, PostgreSQL |
| **VoIP** | SIP | SIP | No | SIP, SCCP, H.323 | SIP, H.323, MGCP, SCCP |
| **P2P** | No | BitTorrent | BitTorrent | BitTorrent | BitTorrent, eDonkey |
| **深度解析** | Protocol Aware Flushing (PAF) | HTTP_inspect (decompression, normalization) | Event-driven analyzers | App-ID + Content-ID | Full proxy-based inspection |

### 1.2 规则引擎

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **规则语言** | Snort 3 enhanced + Lua | Snort兼容 + Lua | Zeek脚本(Turing-complete) | App-ID/Signature | Fortinet Signature |
| **规则选项数** | 70+ | 70+ | N/A (脚本) | 10000+ | 15000+ |
| **正则表达式** | PCRE | PCRE | 内置/PCRE | PCRE | PCRE |
| **多模匹配** | AC, Hyperscan | AC, Hyperscan | AC (plugin) | 硬件加速 | CP9/CP10 ASIC |
| **Lua脚本** | Yes (LuaJIT) | Yes | Yes | Yes | Yes |
| **Fast Pattern** | Yes | Yes | No | Yes | Yes |
| **规则分类** | gid/sid/rev | sid/rev | 事件脚本 | Signature/CVE | Severity/CVE |
| **Snort规则兼容** | 原生 | 95%+ 兼容 | 需转换 | 需转换 | 需转换 |

### 1.3 异常检测

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **统计异常检测** | Port Scan检测 | Protocol Anomaly | 内置统计框架 | 是 | 是 |
| **机器学习** | HTTP参数分类(libml) | 无 | 需外部集成 | Cortex XDR AI | FortiGuard AI |
| **行为分析** | 无 | 无 | 脚本框架 | 是 | 是 |
| **速率检测** | Rate Filter | threshold/rate_filter | 阈值脚本 | 是 | 是 |
| **协议异常** | Yes | Yes | Yes | 是 | 是 |
| **DoS检测** | 是 | 是 | 是 | 是 | 是 |

### 1.4 文件检测

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **文件提取** | SHA256 + 存储 | Yes + magic识别 | Yes + 多种hash | Yes (WildFire) | Yes |
| **文件类型** | PE, ELF, PDF等 | 多种 | 多种 | 多种 | 多种 |
| **PE分析** | No | No | Yes | Yes | Yes |
| **沙箱** | 无(外部) | 无(外部) | 外部集成 | WildFire(原生) | FortiSandbox(原生) |
| **文件大小限制** | 可配置 | 可配置 | 可配置 | 可配置 | 可配置 |
| **元数据日志** | file_id | fileinfo | files.log | 是 | 是 |

### 1.5 TLS/加密流量

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **JA3指纹** | 无(需Lua) | 原生支持 | 原生支持 | 原生支持 | 原生支持 |
| **JA4指纹** | 无 | Suricata 7.x+ | 原生支持 | 是 | 是 |
| **证书链解析** | Yes | Yes | Yes | 是 | 是 |
| **SNI提取** | Yes | Yes | Yes | 是 | 是 |
| **TLS解密** | 私钥配置 | 私钥配置 | 私钥配置 | 透明代理 | 深度SSL检查 |
| **TLS 1.3** | Yes | Yes | Yes | 是 | 是 |
| **ECH支持** | No | Yes | Yes | 是 | 是 |
| **加密流量检测** | 证书/JA3 | JA3/JA4 | JA3/JA4 | JA3/JA4 | JA3/JA4 |

---

## 二、架构对比

### 2.1 线程模型

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **模型** | 多线程 | 多线程(AutoFP/Workers) | 事件驱动+cluster | 多核SMP | SMP + NPU offload |
| **默认线程** | 1 (可配置) | Auto (CPU核心) | 单进程 | 多核 | 多核 |
| **流分布** | DAQ batch | cluster_flow (5-tuple) | 事件分发 | 硬件分布 | NP会话分发 |
| **无锁设计** | Partial | Yes (AF_PACKET) | Partial | Yes | Yes |
| **内存池** | Packet pool | Packet pool | Flow table | 硬件表 | CP表 |

### 2.2 硬件加速

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **DPDK** | Roadmap | Yes | No | 是 | No |
| **AF_XDP** | Roadmap | Yes | No | 是 | No |
| **PF_RING** | Yes | Yes | pf_ring | 是 | No |
| **NETMAP** | Yes | Yes | No | 是 | No |
| **SmartNIC** | No | No | No | 是 | 是(NP7/8) |
| **硬件加速** | Hyperscan | Hyperscan | No | 专用ASIC | CP9/10 ASIC |
| **零拷贝** | Partial (DAQ) | AF_PACKET tpacket-v3 | No | Yes | Yes |

### 2.3 集群/HA

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **HA模式** | Active-Passive | 外部实现 | Manager/Worker/Proxy | Active-Active, A-P | FGCP |
| **状态同步** | SideChannel | Redis/Kafka | 实时同步 | 会话同步 | 会话同步 |
| **水平扩展** | 无原生 | 外部负载均衡 | 原生cluster | 是 | 是 |
| **最大节点** | 2 | 外部决定 | 100+ | 多节点 | 多节点 |
| **故障切换** | <1s | 外部决定 | <1s | Sub-second | Sub-second |
| **集群协议** | HA Module | N/A | Zeek Cluster | 专有 | FGCP |

---

## 三、运维对比

### 3.1 日志/告警格式

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **主格式** | Unified2/JSON | EVE JSON | ASCII/JSON | Syslog/JSON | Syslog/JSON |
| **JSON输出** | alert_json | EVE (原生) | JSON | 是 | 是 |
| **CSV输出** | alert_csv | No | TSV | 是 | 是 |
| **Syslog** | alert_syslog | 是 | 是 | 是 | 是 |
| **PCAP** | log_pcap | file-store | No | 是 | 是 |
| **Barnyard2** | Yes | Yes (unified2) | No | No | No |
| **告警字段** | sid, gid, rev, msg | signature_id, msg | notice | threatID | attackid |
| **统一格式** | Unified2 | EVE | 多种log | FGT格式 | FGT格式 |

### 3.2 管理界面

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **Web GUI** | 无 | 无 | 无(第三方) | Panorama/Strata | FortiGate GUI |
| **REST API** | 无 | 无 | 无 | 是 | 是 |
| **CLI** | Yes | Yes | zeekctl | Yes | Yes |
| **集中管理** | Cisco FMC | 外部(SecurityOnion) | 外部 | Panorama | FortiManager |
| **配置语言** | Lua | YAML | Zeek脚本 | JSON | CLI/YAML |
| **实时配置** | --lua选项 | SIGUSR1 reload | zeekctl | 是 | 是 |
| **第三方集成** | Sguil, Snorby | ELK, Splunk | Splunk, ELK | Splunk | FortiSIEM |

### 3.3 规则更新

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **更新频率** | 手动/订阅 | 手动/订阅 | 无(社区ID) | 5分钟 | 5分钟 |
| **官方规则** | Talos | ET Open/PRO | 社区ID | Palo Alto签名 | FortiGuard |
| **免费规则** | 社区规则 | ET Open | 社区ID | 基础 | IPS基础 |
| **自动更新** | 无 | suricata-update | 无 | 原生 | 原生 |
| **CVE映射** | Yes | Yes | 部分 | 是 | 是 |
| **规则数量** | 50000+ | 35000+(ET Open) | N/A | 3000+ | 15000+ |
| **自定义规则** | SO规则 | 是 | Zeek脚本 | 是 | 是 |

---

## 四、性能对比

### 4.1 吞吐量参考

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **10Gbps** | Yes | Yes | Yes | Yes | Yes |
| **40Gbps** | Yes (多线程) | Yes (DPDK) | Yes (pf_ring) | Yes | Yes |
| **100Gbps** | 需优化 | Yes (DPDK) | Yes (专用) | 是 | 是 |
| **包处理** | DAQ batch | 批处理 | 事件批处理 | 硬件 | NP+CP |
| **延迟控制** | Per-packet latency | 是 | 是 | 是 | 是 |
| **性能调优** | --max-packet-threads | threading配置 | cluster配置 | 自动 | 自动 |

### 4.2 零拷贝/批处理

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **零拷贝** | DAQ batch | AF_PACKET tpacket-v3 | No | Yes | Yes |
| **批处理** | Yes (DAQ batch 64) | Yes | Yes | Yes | Yes |
| **mmap** | Partial | Yes | No | Yes | Yes |
| **内存池** | Packet pool | Packet pool | Flow table | 硬件 | CP表 |
| **锁优化** | Thread-local | Per-thread | Per-node | 硬件 | NP offload |

---

## 五、云原生对比

### 5.1 K8s集成

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **Helm Chart** | 无 | 社区 | 官方 | 是 | 官方 |
| **DaemonSet** | 可部署 | 可部署 | 可部署 | 是 | 是 |
| **Sidecar** | 无 | 无 | 无 | 无 | 无 |
| **CNI集成** | 无 | 无 | 无 | 是 | CNI插件 |
| **服务发现** | 无 | 无 | 无 | K8s API | K8s API |
| **自动扩缩容** | 无 | 无 | 无 | 是 | AWS/GCP/Azure |
| **零信任** | 无 | 无 | 无 | Prisma | Security Fabric |

### 5.2 东西向流量检测

| 能力 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **方案** | 需镜像 | 需镜像 | 需镜像 | 需镜像 | 需镜像 |
| **vTap** | 无 | 无 | 无 | 是 | 是 |
| **CNI镜像** | 无 | 无 | 无 | 是 | 是 |
| **Service Mesh** | 无 | 无 | 无 | Istio | Istio |
| **主机探针** | 无 | 无 | 无 | 是 | 是 |
| **云VPC镜像** | 需手动 | 需手动 | 需手动 | 是 | 是 |

---

## 六、总结对比表

| 维度 | Snort 3 | Suricata | Zeek | Palo Alto | FortiGate |
|------|---------|----------|------|-----------|-----------|
| **开源** | Yes (GPLv2) | Yes (GPLv2) | Yes (BSD) | No | No |
| **厂商** | Cisco | OISF | Corelight | Palo Alto | Fortinet |
| **定位** | IDS/IPS | IDS/IPS | NSM | NGFW | NGFW |
| **学习曲线** | 中 | 中 | 高 | 低 | 低 |
| **规则生态** | Talos | ET/Open | 社区 | 官方 | FortiGuard |
| **加密检测** | 基础 | 强 | 强 | 强 | 强 |
| **沙箱** | 无 | 无 | 无 | WildFire | FortiSandbox |
| **AI/ML** | HTTP参数 | 无 | 外部 | Cortex XDR | FortiGuard AI |
| **HA集群** | 基础 | 外部 | 原生 | 原生 | 原生 |
| **云原生** | 手动 | 手动 | 手动 | 好 | 好 |
| **性能** | 高 | 高 | 中 | 高 | 高 |

---

## 七、差距矩阵: NIDS vs 竞品缺失功能

### 7.1 NIDS vs Snort 3

| 功能 | 状态 | 说明 |
|------|------|------|
| 规则引擎Lua扩展 | 缺失 | Snort 3支持LuaJIT脚本规则 |
| Hyperscan加速 | 缺失 | Snort 3支持Intel Hyperscan |
| 内置HA | 缺失 | Snort 3只有active-passive HA |
| REST API | 缺失 | Snort 3无原生API |
| 自动规则更新 | 缺失 | 需手动或外部脚本 |
| HTTP参数ML分类 | 缺失 | Snort 3有snort_ml模块 |

### 7.2 NIDS vs Suricata

| 功能 | 状态 | 说明 |
|------|------|------|
| EVE JSON格式 | 缺失 | Suricata原生EVE输出 |
| AF_PACKET零拷贝 | 缺失 | Suricata支持tpacket-v3 |
| DPDK支持 | 缺失 | Suricata支持DPDK |
| PF_RING支持 | 缺失 | Suricata支持PF_RING |
| suricata-update | 缺失 | Suricata有官方规则更新工具 |
| 规则兼容性 | 缺失 | Suricata 95%+兼容Snort规则 |

### 7.3 NIDS vs Zeek

| 功能 | 状态 | 说明 |
|------|------|------|
| 事件驱动架构 | 缺失 | Zeek完整的事件模型 |
| 协议分析器框架 | 缺失 | Zeek 30+内置分析器 |
| Cluster架构 | 缺失 | Zeek原生Manager/Worker/Proxy |
| 威胁情报框架 | 缺失 | Zeek Intel框架支持STIX/OTX |
| 统计异常检测 | 缺失 | Zeek内置统计框架 |
| 文件深度分析 | 缺失 | Zeek PE/hash分析更强 |
| 日志格式多样性 | 缺失 | Zeek支持ASCII/JSON/TSV |
| Splunk/ELK集成 | 缺失 | Zeek有官方TA |

### 7.4 NIDS vs Palo Alto

| 功能 | 状态 | 说明 |
|------|------|------|
| App-ID | 缺失 | Palo Alto应用识别 |
| Content-ID | 缺失 | Palo Alto深度内容检测 |
| WildFire沙箱 | 缺失 | Palo Alto原生沙箱 |
| Cortex XDR | 缺失 | Palo Alto XDR平台 |
| Panorama集中管理 | 缺失 | Palo Alto管理平台 |
| 自动威胁更新 | 缺失 | Palo Alto 5分钟更新 |
| NGFW完整功能 | 缺失 | Palo Alto是完整NGFW |
| SSL深度检查 | 缺失 | Palo Alto透明代理 |
| DNS安全 | 缺失 | Palo Alto DNS防护 |

### 7.5 NIDS vs FortiGate

| 功能 | 状态 | 说明 |
|------|------|------|
| FortiGuard威胁情报 | 缺失 | Fortinet全球威胁情报 |
| FortiSandbox | 缺失 | Fortinet原生沙箱 |
| CP9/CP10加速 | 缺失 | Fortinet专用ASIC |
| FortiManager | 缺失 | Fortinet集中管理 |
| FGCP集群 | 缺失 | Fortinet HA协议 |
| SSL深度检查 | 缺失 | Fortinet透明代理 |
| 安全Fabric | 缺失 | Fortinet生态 |
| 自动更新 | 缺失 | Fortinet 5分钟自动更新 |
| 病毒扫描 | 缺失 | Fortinet AV引擎 |
| 完整UTM | 缺失 | Fortinet完整安全功能 |

---

## 八、建议

### 8.1 短期优先级 (0-6月)

1. **完善规则引擎** - 兼容Snort规则格式，支持快速模式匹配
2. **EVE JSON日志** - 实现标准化的JSON日志输出
3. **TLS指纹** - JA3/JA4支持
4. **协议解析** - 扩展HTTP/2、DNS深度解析

### 8.2 中期目标 (6-12月)

1. **高性能捕获** - AF_PACKET/DPDK支持
2. **集群方案** - 支持水平扩展
3. **文件分析** - 文件提取+hash计算
4. **威胁情报** - 集成STIX/TAXII

### 8.3 长期目标 (12月+)

1. **ML异常检测** - 行为分析能力
2. **沙箱集成** - 文件动态分析
3. **云原生** - K8s深度集成
4. **自动化响应** - SOAR集成

---

*报告生成时间: 2026/05/25*
