# MASSCAN 报文特征与识别

## 1. 概述

MASSCAN 是一个高速互联网端口扫描器，其报文具有独特的特征模式。理解这些特征对于：

- **安全运营**：检测潜在的恶意扫描活动
- **网络安全**：构建 IDS/IPS 检测规则
- **隐蔽性评估**：了解 MASSCAN 的可检测性

## 2. MASSCAN 报文特征

### 2.1 TCP SYN 扫描（默认）

MASSCAN 默认使用 SYN 扫描，其 TCP 报文结构如下：

```
┌─────────────────────────────────────────────────────────────┐
│                      Ethernet Header                        │
│  Dst MAC: <gateway_mac>     Src MAC: <adapter_mac>         │
│  Type: 0x0800 (IPv4)                                         │
├─────────────────────────────────────────────────────────────┤
│                        IP Header                            │
│  Version: 4  IHL: 5    TOS: 0    Total Length: 44          │
│  Identification: <递增>  Flags: DF(1)  Fragment: 0          │
│  TTL: 64 (默认, 可修改)                                      │
│  Protocol: 6 (TCP)                                          │
│  Header Checksum: <计算>                                     │
│  Src IP: <source_ip>   Dst IP: <target_ip>                 │
├─────────────────────────────────────────────────────────────┤
│                        TCP Header                           │
│  Src Port: <高位随机端口>   Dst Port: <target_port>        │
│  Seq: <syn_cookie>      Ack: 0                              │
│  Offset: 7  Flags: SYN                                     │
│  Window: 1024 or 16384  Checksum: <计算>  Urgent: 0        │
│  Options:                                                   │
│    - Kind 2 (MSS): 1460 或自定义                            │
│    - Kind 1 (NOP)                                          │
│    - Kind 3 (Window Scale): 7                               │
│    - Kind 1 (NOP)                                          │
│    - Kind 1 (NOP)                                          │
│    - Kind 4 (SACK Permitted): 1                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 关键特征详解

#### 源端口特征

| 特征 | 正常客户端 | MASSCAN |
|------|----------|---------|
| 端口范围 | 连续低位端口 (32768-60999 Linux) | 高位随机端口 |
| 端口复用 | 短时间内重复使用 | 每次扫描随机分配 |
| 模式 | 自然分布 | 完全随机 |

MASSCAN 默认源端口范围：
- Linux: `32768-60999`
- 可通过 `--source-port` 自定义

#### 序列号 (SYN Cookie)

```c
// syn-cookie.c 实现
uint64_t syn_cookie_ipv4(
    unsigned ip_them, unsigned port_them,
    unsigned ip_me, unsigned port_me,
    uint64_t entropy)
{
    unsigned data[4];
    uint64_t x[2] = {entropy, entropy};
    data[0] = ip_them; data[1] = port_them;
    data[2] = ip_me;   data[3] = port_me;
    return siphash24(data, sizeof(data), x);
}
```

**特征**：
- 使用 SipHash24 生成，而非随机生成
- 基于 5 元组 (src_ip, dst_ip, src_port, dst_port, entropy)
- entropy 默认基于时间戳，可通过 `--seed` 固定

#### TCP Window 大小

- 默认值：**1024** 或 **16384**（Windows 风格）
- 正常扫描器通常使用：
  - nmap: 1024
  - 其他工具: 65535

#### IP ID 递增

MASSCAN 为每个 IP 包分配递增的 Identification：

```c
// templ-pkt.c
pkt->ipv4.ip_id = template->ip_id++;  // 递增分配
```

| 系统 | IP ID 特征 |
|------|-----------|
| Windows | 0x4000 起始 |
| iOS | 0x3AAA 起始 |
| Linux | 0x0000 起始 |
| MASSCAN | 连续递增（可被检测）|

#### TTL 特征

- 默认值：**64**
- 可通过 `--ttl` 修改
- 不同 OS 默认值：
  - Linux: 64
  - Windows: 128
  - macOS: 64

#### TCP Options 顺序

MASSCAN 的 TCP Options 顺序是固定的：

```
MSS → NOP → Window Scale → NOP → NOP → SACK Permitted
```

这与其他扫描器不同，可用于指纹识别。

### 2.3 扫描行为特征

#### 完全随机化扫描顺序

MASSCAN 使用 BlackRock 加密算法对扫描索引进行随机化：

```
index:  0    1    2    3    4    5    6    7    8    9   ...
        ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓
target: 192  45   123  67   10   201  89   156  34   178 ...
```

正常扫描器通常是：
- 顺序扫描（连续 IP）
- 伪随机但基于子网

#### 固定速率发包

正常网络流量：
- 发包间隔自然分布
- 突发流量模式

MASSCAN：
- `--rate 1000000` = 每秒精确发送 100 万包
- 固定间隔：1/1,000,000 秒 = 1 微秒

### 2.4 IPv6 特征

MASSCAN 同时支持 IPv6：

```
Src IP: <local_ipv6>   Dst IP: <target_ipv6>
Next Header: 6 (TCP)
```

IPv6 相关特征：
- 使用 IPv6 的 MSS: 1440
- Hop Limit: 64（默认）
- 没有 IP ID（IPv6 使用 Flow Label）

## 3. 识别方法

### 3.1 基于 Snort/Suricata 规则

```snort
# 检测 MASSCAN 典型特征组合
alert tcp any any -> any any (
    msg:"MASSCAN Detection: SYN with high random source port";
    flags:S,12;
    seq:0;
    window:1024;
    threshold:type threshold, track by_src, count 10, seconds 1;
    sid:1000001;
    rev:1;
)

# 检测大量 SYN + 随机源端口
alert tcp any any -> any any (
    msg:"MASSCAN-like Scan Detected";
    flags:S,12;
    tcp-options:|04 02|MSS;  # 检查非标准 MSS
    threshold:type threshold, track by_src, count 50, seconds 5;
    sid:1000002;
    rev:1;
)
```

### 3.2 TCP 指纹识别

#### p0f 被动指纹

MASSCAN 的 TCP 指纹特征：

| 字段 | 值 | 权重 |
|------|-----|------|
| Window Size | 1024/16384 | 高 |
| TTL | 64 | 中 |
| MSS | 1460 | 低 |
| Window Scale | 7 | 高 |
| Options Order | MSS-NOP-WS-NOP-NOP-SACK | 高 |

### 3.3 SYN Cookie 逆向

如果捕获到足够的 MASSCAN 流量，可以：

1. 提取所有 SYN 包的序列号
2. 收集 5 元组信息
3. 使用 SipHash24 逆向工程 entropy
4. 预测后续扫描目标

```python
# 伪代码：SYN Cookie 逆向
def reverse_syn_cookie(syn_seq, src_ip, dst_ip, src_port, dst_port):
    # 尝试常见 entropy 值
    for entropy in range(0, 0xFFFFFFFF):
        expected = siphash24([src_ip, dst_ip, src_port, dst_port], entropy)
        if expected == syn_seq:
            return entropy
```

### 3.4 行为分析

#### 端口分布检测

正常扫描：
```python
# 大部分工具：连续端口
ports = [80, 81, 82, 83, 84, ...]

# MASSCAN：随机分布
ports = [54321, 1234, 65535, 8080, 4123, ...]
```

#### IP 分布检测

正常扫描：
```python
# 按子网顺序
ips = [10.0.0.1, 10.0.0.2, 10.0.0.3, ...]
# 或随机但基于子网
ips = [10.0.0.1, 10.0.0.5, 10.0.0.3, 10.0.0.9, ...]

# MASSCAN：完全随机（加密索引映射）
ips = [192.168.45.123, 10.255.67.89, 172.16.0.1, ...]
```

### 3.5 检测矩阵

| 特征 | 可检测性 | 误报率 | 说明 |
|------|---------|--------|------|
| 高位随机源端口 | 高 | 中 | 某些代理/VPN 也会使用随机端口 |
| 固定 Window Size | 中 | 中 | 1024 是 nmap 默认值 |
| 递增 IP ID | 中 | 低 | 仅当 IP ID 从 0 开始时可靠 |
| 固定 TTL | 低 | 高 | 64 是 Linux 默认值 |
| TCP Options 顺序 | 高 | 低 | 固定顺序是明显特征 |
| 完全随机扫描顺序 | 高 | 低 | 需要足够样本 |
| 固定发包速率 | 高 | 低 | 精确速率是明显特征 |

## 4. 隐蔽性增强

### 4.1 修改默认特征

```bash
# 修改 TTL 伪装成 Windows
--ttl 128

# 修改源端口范围（低位连续）
--source-port 4000-5000

# 修改 Window 大小
--tcpmss 65535

# 修改 MSS
--tcpmss 1460

# 使用自定义 IP ID
--bad-ip-ip 0x4000

# 添加随机载荷
--data-length 100
```

### 4.2 降低速率

```bash
# 降低到 1000 pps
--rate 1000

# 使用随机延迟
--wait 10
```

### 4.3 使用源 IP 池

```bash
# 使用同网段的多个源 IP
--source-ip 10.0.0.1-10
```

### 4.4 完整隐蔽扫描示例

```bash
masscan 10.0.0.0/24 -p80,443 \
    --source-port 4000-4010 \
    --source-ip 10.0.0.50 \
    --rate 100 \
    --ttl 128 \
    --tcpmss 1460
```

## 5. 检测建议

### 5.1 实时检测

- **NetFlow/sFlow 分析**：检测异常的源端口分布
- ** Zeek 网络监控**：检测 SYN Cookie 模式
- **Snort/Suricata**：部署检测规则

### 5.2 离线分析

- **pcap 分析**：提取 TCP 指纹
- **统计异常检测**：端口分布熵分析
- **机器学习**：基于流量模式的分类

### 5.3 防御措施

1. **限制入站 SYN 速率**：在边界设备配置 SYN Cookie
2. **源端口过滤**：阻止异常源端口范围的连接
3. **威胁情报**：结合已知扫描源 IP 黑名单
4. **行为分析**：部署 UEBA 系统

## 6. 总结

MASSCAN 的报文特征可总结为：

| 层级 | 特征 | 检测难度 |
|------|------|---------|
| 网络 | 高速率、随机源端口 | 易 |
| 传输 | SYN Cookie、固定 Window、递增 IP ID | 中 |
| 应用 | 完全随机扫描顺序 | 难 |

**最佳检测策略**：组合多种特征，而非依赖单一指标。

---

**文档版本**: 1.0
**生成日期**: 2026-04-16
