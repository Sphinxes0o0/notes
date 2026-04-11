# MASSCAN 代码架构深度分析

## 1. 项目概述

### 1.1 定位

Masscan 是一个**互联网规模的端口扫描器**，能够在单台机器上以每秒 1000 万数据包的速度扫描整个互联网（under 5 minutes）。它的设计目标与 nmap 类似，但在处理大规模扫描时更加高效。

### 1.2 核心功能

- **TCP SYN 扫描**：发送 SYN 包检测端口开放状态
- **Banner 抓取**：完成 TCP 握手后获取服务标识信息
- **UDP 扫描**：支持 UDP 协议扫描
- **SCTP 扫描**：支持 SCTP 协议扫描
- **ICMP/ARP 扫描**：支持网络层探测
- **无状态扫描架构**：无需为每个连接维护状态
- **多协议解析**：HTTP、SSH、SSL、SMB、FTP、SMTP 等

### 1.3 技术选型

| 技术选型 | 说明 |
|---------|------|
| **语言** | C 语言，无外部依赖 |
| **并发模型** | 异步发送/接收线程对 |
| **TCP/IP 栈** | 自定义用户态协议栈（绕过内核） |
| **随机化** | BlackRock Feistel 网络 + SipHash24 |
| **速率限制** | Token Bucket 算法（256 桶） |
| **进程间通信** | DPDK FreeBSD bufring 锁无关 Ring Buffer |
| **跨平台** | Linux/Windows/macOS/FreeBSD |

## 2. 目录结构

```
/Users/sphinx/github/masscan/
├── src/                    # 主源代码目录
│   ├── main.c              # 主程序，发送/接收线程入口
│   ├── main-conf.c         # 配置解析（命令行/配置文件）
│   ├── main-throttle.c     # 速率限制（Token Bucket）
│   ├── main-dedup.c        # 重复响应去重
│   ├── main-status.c       # 状态显示
│   ├── syn-cookie.c/h      # SYN Cookie 实现
│   ├── crypto-blackrock.c/h # BlackRock 随机化算法
│   ├── crypto-siphash24.c/h # SipHash24 哈希
│   ├── templ-pkt.c/h       # 数据包模板
│   ├── stack-tcp-core.c/h  # 用户态 TCP 协议栈核心
│   ├── stack-tcp-app.c/h   # TCP 应用层状态机
│   ├── proto-banner1.c/h    # Banner 抓取解析器
│   ├── proto-*.c/h         # 各协议解析器（ssl, http, ssh...）
│   ├── massip-*.c/h        # IP 地址范围处理
│   ├── output.c/h          # 输出模块
│   ├── rawsock.c/h         # 原始套接字封装
│   ├── rte-ring.c/h         # 锁无关 Ring Buffer
│   └── pixie-*.c/h         # 跨平台工具函数
├── data/                   # nmap-payloads 等数据文件
└── doc/                    # 文档
```

## 3. 核心模块深度分析

### 3.1 main.c: 发送/接收线程架构

#### 3.1.1 整体架构

```
main()
  │
  ▼
main_scan()
  │
  ├─► 为每个 NIC 创建 ThreadPair
  │     ├─► transmit_thread()  发送探测包
  │     └─► receive_thread()   接收响应包
  │
  └─► 主线程循环（状态显示 + Ctrl-C 处理）
```

#### 3.1.2 ThreadPair 结构

```c
struct ThreadPair {
    const struct Masscan *masscan;    // 配置（只读）
    struct Adapter *adapter;           // 网络适配器
    struct stack_t *stack;            // 用户态 TCP 栈
    unsigned nic_index;               // NIC 索引
    volatile uint64_t my_index;       // 当前位置
    struct TemplateSet tmplset[1];    // 数据包模板
    struct Throttler throttler[1];   // 速率限制器
};
```

#### 3.1.3 发送线程主循环

```c
for (i=start; i<end; ) {
    batch_size = throttler_next_batch(throttler, packets_sent);
    stack_flush_packets(parms->stack, adapter, &packets_sent, &batch_size);

    while (batch_size && i < end) {
        xXx = blackrock_shuffle(&blackrock, i + (r--)*rate);
        ip_them = rangelist_pick(&targets.ipv4, xXx % count);
        port_them = rangelist_pick(&targets.ports, xXx / count);
        cookie = syn_cookie_ipv4(ip_them, port_them, ip_me, port_me, entropy);
        rawsock_send_probe_ipv4(adapter, ip_them, port_them, ip_me, port_me, cookie, ...);
    }
}
```

#### 3.1.4 接收线程主循环

```c
while (!is_rx_done) {
    rawsock_recv_packet(adapter, &length, &secs, &usecs, &px);
    x = preprocess_frame(px, length, data_link, &parsed);
    cookie = syn_cookie(...) & 0xFFFFFFFF;

    switch (parsed.found) {
        case FOUND_TCP:    handle_tcp();    break;
        case FOUND_UDP:    handle_udp();    break;
        case FOUND_ICMP:   handle_icmp();   break;
        case FOUND_ARP:    handle_arp();    break;
    }
}
```

### 3.2 syn-cookie: 无状态扫描的 Cookie 机制

**核心原理**：发送时不记录发出的包，接收时通过 Cookie 验证响应是否匹配。

```c
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

**工作流程**：
1. 发送 SYN 时，序列号 = syn_cookie(目标IP, 端口, 源IP, 源端口, entropy)
2. 收到 SYN-ACK 时，从 ACKNO-1 获取 cookie 并验证

### 3.3 crypto-blackrock: BlackRock 随机化算法

**设计目标**：将单调递增索引 [0, N) 映射为均匀随机的一一对应排列，且可逆。

**Feistel 网络结构**：
```
输入 m → 分割 L=m%a, R=m/a → r轮迭代 → 输出 c
```

**特点**：
- 可逆：可以用相同密钥解密
- 确定性：相同种子产生相同序列（可重现）
- 高效：适合 10Mpps 的高速扫描

### 3.4 main-throttle: 速率限制算法

**Token Bucket（256 桶）算法**：

```c
uint64_t throttler_next_batch(struct Throttler *throttler, uint64_t packet_count) {
    current_rate = (packet_count - old_packet_count) /
                  ((timestamp - old_timestamp) / 1000000.0);

    if (current_rate > max_rate) {
        waittime = (current_rate - max_rate) / max_rate;
        throttler->batch_size *= 0.999;
        pixie_usleep(waittime * 1000000);
    } else {
        throttler->batch_size *= 1.005;  // 增大批次
    }
    return (uint64_t)throttler->batch_size;
}
```

### 3.5 templ-pkt: 数据包模板

```c
enum TemplateProtocol {
    Proto_TCP, Proto_UDP, Proto_SCTP,
    Proto_ICMP_ping, Proto_ICMP_timestamp,
    Proto_ARP, Proto_Oproto, Proto_VulnCheck
};

struct TemplateSet {
    unsigned count;
    struct TemplatePacket pkts[Proto_Count];  // 每种协议一个模板
};
```

### 3.6 stack-tcp: 用户态 TCP 协议栈

#### TCP 控制块 (TCB)

```c
struct TCP_Control_Block {
    ipaddress ip_me, ip_them;
    unsigned short port_me, port_them;
    uint32_t seqno_me, seqno_them;
    uint32_t ackno_me, ackno_them;
    unsigned char ttl, syns_sent;
    unsigned short mss;
    unsigned tcpstate:4;
    struct BannerOutput banout;  // Banner 输出缓冲
};
```

#### TCP 状态机

```
CLOSED → SYN_SENT → ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
                   ↓
              CLOSE_WAIT → LAST_ACK → CLOSED
```

### 3.7 proto-banner: Banner 抓取

**支持协议**：SSH1/2, HTTP, FTP, SSL3, SMB, SMTP, POP3, IMAP4, VNC, RDP, MEMCACHED, NTP, SNMP 等。

**解析流程**：
1. Aho-Corasick 模式匹配识别协议
2. 调用对应协议的解析器
3. 输出到 banout

## 4. 关键数据结构

```c
struct Masscan {
    enum Operation op;
    struct {
        char ifname[256];
        struct Adapter *adapter;
        macaddress_t source_mac;
        macaddress_t router_mac_ipv4;
    } nic[8];
    unsigned nic_count;
    struct MassIP targets;      // 目标 IP 范围
    struct MassIP exclude;      // 排除 IP 范围
    double max_rate;             // 最大速率 (pps)
    unsigned retries;
    uint64_t seed;
    struct OutputStuff output;
    struct NmapPayloads payloads;
};

struct MassIP {
    struct RangeList ipv4;       // IPv4 范围
    struct Range6List ipv6;    // IPv6 范围
    struct RangeList ports;      // 端口范围
};
```

## 5. 完整代码流程

### 5.1 启动流程

```
main()
  ├─► 初始化配置 (memset masscan to 0)
  ├─► 读取 /etc/masscan/masscan.conf
  ├─► 解析命令行 (masscan_command_line)
  ├─► 采集熵源 (get_entropy)
  ├─► 加载数据库文件 (nmap-payloads, nmap-service-probes)
  └─► 调用 op 对应处理函数
        └─► Operation_Scan: main_scan()
```

### 5.2 main_scan() 扫描主流程

```
main_scan()
  ├─► 验证目标地址和端口有效性
  ├─► 优化目标选择 (massip_optimize)
  ├─► 初始化每个 NIC 的 ThreadPair
  ├─► 启动发送/接收线程对
  ├─► 主线程循环（状态显示）
  └─► 保存恢复状态 + 输出统计
```

### 5.3 发送线程流程

```
transmit_thread()
  ├─► 初始化 BlackRock 随机化器
  ├─► 计算扫描范围 [start, end)
  └─► 主循环
        ├─► throttler_next_batch() 获取批次大小
        ├─► stack_flush_packets() 处理 Banner 发送
        └─► 批量发送 SYN 包
              ├─► BlackRock 随机化索引
              ├─► 选择目标 IP:Port
              ├─► 计算 SYN Cookie
              └─► rawsock_send_probe_ipv4()
```

### 5.4 接收线程流程

```
receive_thread()
  ├─► 创建 ResetFilter、Output、Dedup、TCP 连接表
  └─► 主循环
        ├─► rawsock_recv_packet() 接收
        ├─► preprocess_frame() 解析帧
        ├─► 重新计算 SYN Cookie 验证
        ├─► 协议分发
        │     ├─► FOUND_TCP: TCP_IS_SYNACK → 创建 TCB → output_report_status(OPEN)
        │     ├─► FOUND_UDP: handle_udp() → output_report_banner()
        │     └─► FOUND_ICMP: handle_icmp() → output_report_status()
        └─► 发送 RST
```

## 6. 模块间依赖关系

```
main.c
  ├── main-throttle.c
  ├── syn-cookie.c
  │     └── crypto-siphash24.c
  ├── crypto-blackrock.c
  ├── rawsock.c
  │     └── pixie-sockets.c
  ├── output.c
  ├── stack-tcp-core.c
  │     ├── syn-cookie.c
  │     ├── proto-banner1.c
  │     │     ├── proto-ssl.c, proto-http.c, proto-ssh.c...
  │     │     └── smack.c (Aho-Corasick)
  │     └── rte-ring.c
  └── templ-pkt.c
```

## 7. 性能优化

### 7.1 批量发送优化
- 低速率 (<100Kpps): batch_size = 1
- 高速率: batch_size 动态增长（最大 10000）

### 7.2 BlackRock 随机化查找优化
- massip_optimize() 预处理 + 二分查找 + picker 数组
- O(log n) 查找复杂度

### 7.3 锁无关 Ring Buffer
- DPDK FreeBSD bufring 实现
- CAS 操作保证无锁

### 7.4 SYN Cookie 避免状态维护
- 发送时不记录，接收时逆向计算验证
- 极致的无状态设计

## 8. 代码亮点和设计模式

### 8.1 自定义用户态 TCP/IP 栈
完全绕过内核网络栈，实现极致性能。

### 8.2 格式保留加密 (BlackRock)
输入 [0, N) → 输出 [0, N)，一一映射可逆。

### 8.3 插件化输出系统
```c
struct OutputType {
    const char *file_extension;
    void *(*create)(struct Output *out);
    void (*status)(...);
    void (*banner)(...);
};
```
支持 text/xml/json/binary/grepable/redis 等格式。

### 8.4 协议解析器状态机链
同一端口支持多协议尝试（如 443 端口可能是 SSL 或 HTTP）。

### 8.5 跨平台抽象层
```c
#ifdef WIN32
    #define pixie_locked_add_u32 _InterlockedExchangeAdd
#else
    #define pixie_locked_add_u32 __sync_add_and_fetch
#endif
```

---

**文档版本**: 1.0
**生成日期**: 2026-04-11
