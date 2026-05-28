# Linux Advanced Routing & Traffic Control HOWTO

**Source:** https://lartc.org/howto/index.html
**NIDS Relevance:** ★★★★★ (packet filtering/classification/qos深度，Netfilter集成)

## 核心内容

### iproute2套件
`ip`命令操作：links, addresses, routes, ARP, tunnel, maddr

### 路由策略数据库 (Routing Policy Database)
- 源地址策略路由 (source policy routing)
- 多uplink场景负载均衡
- 支持OSPF/BGP动态路由 (via Zebra)

### Traffic Control (tc)

#### Queueing Disciplines (qdisc)
**Classful**: CBQ, HTB, PRIO
**Classless**: TBF (token bucket), SFQ, RED, `netem` (网络仿真)

#### Filters & Classifiers
- `u32`: 基于协议/IP/端口分类
- `fw`: 基于firewall mark分类
- `route`: 基于路由分类
- `hash`: 哈希分类

#### 高级qdisc
- **RED**: Random Early Detection (主动队列管理)
- **DSmark**: Differentiated Services标记
- **Ingress policing**: 入向流量限速
- **ATM emulation**: ATM仿真

### 安全与监控相关
- Netfilter集成: `fwmark`用于packet标记和追踪
- Reverse Path Filtering (反欺骗)
- IPSEC隧道 (manual/自动keying, X.509)
- GRE隧道 (封装流量)

### 实用场景
- 多接口负载均衡
- 限速 (rate limiting/shaping)
- SYN flood防护
- 透明web缓存架构
- 桥接和proxy ARP配置

### NIDS Relevance
1. **Packet Filtering**: u32/fw filter直接在kernel层过滤，可用于快速丢弃已知恶意流量
2. **Traffic Classification**: 隔离suspicious flows，独立监控
3. **QoS for IDS**: 为检测流量保障带宽，避免被大流量淹没
4. **Netfilter Integration**: 连接追踪、NAT都与NIDS流量分析相关
5. **netem**: 模拟网络损伤测试NIDS检测准确性

## 关联概念
- [[linux-ebpf-technical-practice]] — TC eBPF direct-action mode
- NIDS架构: tc filter → packet classification → Snort3
