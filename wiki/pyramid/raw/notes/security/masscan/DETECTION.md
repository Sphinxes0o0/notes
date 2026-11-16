# MASSCAN 检测方法与实时检测引擎设计

## 1. 检测概述

### 1.1 检测挑战

MASSCAN 作为高速互联网端口扫描器，其检测面临以下挑战：

- **高速扫描**：可在数秒内完成目标网络扫描
- **早期发现要求**：必须在造成实质影响前检测
- **低误报要求**：避免将正常流量误判为扫描
- **实时性要求**：检测延迟需低于 100ms

### 1.2 MASSCAN 核心特征回顾

| 特征维度 | MASSCAN 表现 | 正常主机表现 |
|---------|-------------|-------------|
| 源端口 | 完全随机高位端口 | 连续低位端口，有连接复用 |
| 扫描顺序 | BlackRock 加密随机 | 子网/端口连续性 |
| 发包速率 | 固定精确速率 | 自然抖动分布 |
| SYN Cookie | SipHash24 生成 | 随机或时序相关 |
| TCP 指纹 | 固定 Window=1024/16384 | 多样化 |
| IP ID | 连续递增 | 随机或系统特征 |

## 2. 报文层检测（Packet-level）

### 2.1 TCP 指纹匹配

MASSCAN 的 TCP 握手特征高度确定，可作为精确指纹：

```
┌─────────────────────────────────────────────────────────────┐
│  MASSCAN TCP SYN 报文                                      │
├─────────────────────────────────────────────────────────────┤
│  Window Size: 1024 或 16384 (Windows 风格)                 │
│  TTL: 64 (默认)                                            │
│  MSS: 1460                                                 │
│  Window Scale: 7                                           │
│  Options: MSS→NOP→WS→NOP→NOP→SACK (固定顺序)              │
└─────────────────────────────────────────────────────────────┘
```

#### TCP 选项顺序检测

```c
enum tcp_option_kind {
    TCP_OPT_EOL = 0,
    TCP_OPT_NOP = 1,
    TCP_OPT_MSS = 2,
    TCP_OPT_WS = 3,
    TCP_OPT_SACKPERM = 4,
    TCP_OPT_TIMESTAMP = 8
};

// MASSCAN 指纹
static const uint8_t MASSCAN_OPTIONS_ORDER[] = {
    TCP_OPT_MSS, TCP_OPT_NOP, TCP_OPT_WS, TCP_OPT_NOP, TCP_OPT_NOP, TCP_OPT_SACKPERM
};

// 指纹匹配评分
int match_tcp_fingerprint(const struct tcphdr *tcp) {
    int score = 0;
    
    // Window Size 检测 (30分)
    uint16_t window = ntohs(tcp->window);
    if (window == 1024 || window == 16384)
        score += 30;
    
    // MSS 检测 (20分)
    if (mss == 1460)
        score += 20;
    
    // Window Scale 检测 (25分)
    if (window_scale == 7)
        score += 25;
    
    // Options 顺序检测 (25分)
    if (options_order_matches(MASSCAN_OPTIONS_ORDER))
        score += 25;
    
    return score;  // >= 60 分认为匹配
}
```

### 2.2 SYN Cookie 熵检测

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

**检测原理**：
- 正常主机序列号：时序相关，有明显模式
- MASSCAN Cookie：基于 SipHash24，熵值极高，均匀分布

```c
// 检测序列号均匀分布程度
int detect_syn_cookie_entropy(struct syn_sample *samples, int n) {
    if (n < 50) return 0;
    
    // 计算自相关性
    double autocorr = calculate_autocorrelation(samples, n);
    
    // MASSCAN: 自相关 < 0.1 (极低)
    // 正常主机: 自相关 > 0.3 (有时序关系)
    if (autocorr < 0.1)
        return DETECT_MASCAN;
    
    return 0;
}
```

### 2.3 IP ID 序列检测

```c
// 检测 IP ID 递增模式
int detect_ipid_pattern(const uint16_t *ipids, int n) {
    int increments = 0;
    for (int i = 1; i < n; i++) {
        if (ipids[i] > ipids[i-1])
            increments++;
    }
    
    double inc_ratio = (double)increments / n;
    
    // MASSCAN: 增量 > 95%
    // 正常: 增量 < 80%
    if (inc_ratio > 0.95)
        return DETECT_MASCAN_IPID;
    
    return 0;
}
```

## 3. 流层检测（Flow-level）

### 3.1 源端口分布异常

```python
def detect_src_port_anomaly(flows: List[Flow]) -> bool:
    """
    MASSCAN: 源端口完全随机，几乎无重复
    正常客户端: 源端口会复用（连接复用）
    """
    src_ports = [f.src_port for f in flows]
    
    # 重复率检测
    unique_ratio = len(set(src_ports)) / len(src_ports)
    
    # MASSCAN: unique_ratio ≈ 1.0
    # 正常: unique_ratio < 0.5
    if unique_ratio > 0.95:
        return True
    
    # 熵值检测
    port_entropy = calculate_entropy(src_ports)
    if port_entropy > 14:
        return True
    
    return False
```

### 3.2 扫描序列随机性检测

```python
def detect_scan_randomness(flows: List[Flow]) -> bool:
    """
    MASSCAN: BlackRock 加密导致完全随机
    正常扫描: 有子网/端口连续性
    """
    targets = [(f.dst_ip, f.dst_port) for f in flows]
    
    # 检测 IP 字节分布熵
    ip_bytes = [ip.to_bytes() for ip, _ in targets]
    byte_entropies = [calculate_entropy([b[i] for b in ip_bytes]) 
                      for i in range(4)]
    
    # MASSCAN: 所有字节熵 > 7.5 (接近 8)
    if all(e > 7.5 for e in byte_entropies):
        return True
    
    return False
```

### 3.3 流特征统计向量

```python
class FlowFeatures:
    def __init__(self, flows: List[Flow]):
        self.src_port_unique_ratio = len(set(f.src_port for f in flows)) / len(flows)
        self.src_port_entropy = calculate_entropy([f.src_port for f in flows])
        self.dst_ip_entropy = calculate_entropy([f.dst_ip for f in flows])
        self.dst_port_entropy = calculate_entropy([f.dst_port for f in flows])
        self.inter_arrival_mean = mean([f.timestamp for f in flows])
        self.inter_arrival_std = std([f.timestamp for f in flows])
        self.syn_count = count_flags(flows, 'SYN')
        self.rst_count = count_flags(flows, 'RST')

# 检测判决
def detect(flows):
    features = FlowFeatures(flows)
    
    # 规则快速过滤
    if features.src_port_entropy < 10:
        return NO_DETECTION
    if features.dst_ip_entropy < 12:
        return NO_DETECTION
    
    # ML 模型二次验证
    prob = model.predict_proba([features])[0]
    if prob > 0.9:
        return DetectionResult(tool='MASSCAN', confidence=prob)
```

## 4. 行为层检测（Behavioral）

### 4.1 扫描行为模式

```python
def detect_scan_pattern(flows: List[Flow]) -> bool:
    """
    检测典型扫描行为
    单一源 → 大量目标 → 目标分布均匀
    """
    src_counts = Counter(f.src_ip for f in flows)
    
    for src, count in src_counts.items():
        if count > 1000:
            targets = [f for f in flows if f.src_ip == src]
            unique_targets = set(f.dst_ip for f in targets)
            
            if len(unique_targets) > 500:
                ports = [f.dst_port for f in targets]
                port_entropy = calculate_entropy(ports)
                
                # MASSCAN: 端口熵接近最大值
                if port_entropy > 13:
                    return True
    
    return False
```

### 4.2 时间间隔异常

```python
def detect_timing_anomaly(flows: List[Flow]) -> bool:
    """
    MASSCAN: 固定速率，时间间隔标准差极小
    正常流量: 时间间隔有自然抖动
    """
    timestamps = sorted([f.timestamp for f in flows])
    intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    
    # 变异系数 CV = std / mean
    cv = std(intervals) / mean(intervals)
    
    # MASSCAN: CV < 0.01 (几乎固定)
    # 正常流量: CV > 0.1
    if cv < 0.05:
        return True
    
    return False
```

## 5. 实时检测引擎设计

### 5.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    实时检测引擎                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  报文层检测  │  │   流层检测   │  │  行为层检测  │        │
│  │   (<1ms)    │  │   (<100ms)  │  │   (>1s)    │        │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤        │
│  │ TCP指纹     │  │ 端口分布熵   │  │ 扫描行为模式 │        │
│  │ SYN Cookie │  │ IP分布熵    │  │ 时间序列异常 │        │
│  │ IP ID序列  │  │ 流特征向量   │  │ 机器学习    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │   结果融合层     │                        │
│                  │   加权投票       │                        │
│                  └────────┬────────┘                        │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │   告警输出      │                        │
│                  │  JSON/Syslog   │                        │
│                  └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 滑动窗口统计

```c
#define SLIDING_WINDOW_SIZE 1024
#define MAX_SAMPLES 10000

typedef struct {
    uint64_t timestamps[MAX_SAMPLES];
    uint32_t indices[MAX_SAMPLES];
    uint32_t head;
    uint32_t count;
} sliding_window_t;

// 滑动窗口添加
static inline void sliding_window_add(sliding_window_t *w, uint64_t ts, uint32_t idx) {
    uint32_t pos = (w->head + w->count) % MAX_SAMPLES;
    w->timestamps[pos] = ts;
    w->indices[pos] = idx;
    if (w->count < MAX_SAMPLES)
        w->count++;
    else
        w->head = (w->head + 1) % MAX_SAMPLES;
}

// 清理过期数据
static inline void sliding_window_cleanup(sliding_window_t *w, uint64_t now, uint64_t window_ms) {
    while (w->count > 0) {
        uint32_t pos = w->head;
        if (now - w->timestamps[pos] > window_ms * 1000)
            w->head = (w->head + 1) % MAX_SAMPLES, w->count--;
        else
            break;
    }
}
```

### 5.3 熵计算

```c
// 香农熵计算
static double calculate_port_entropy(uint16_t *ports, uint32_t n) {
    if (n < 2) return 0;
    
    uint32_t counts[65536] = {0};
    for (uint32_t i = 0; i < n; i++)
        counts[ports[i]]++;
    
    double entropy = 0.0;
    for (uint32_t i = 0; i < 65536; i++) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / n;
            entropy -= p * log2(p);
        }
    }
    
    return entropy;
}

// 快速近似熵（使用直方图）
static double fast_entropy(uint16_t *ports, uint32_t n) {
    uint32_t buckets[1024] = {0};
    for (uint32_t i = 0; i < n; i++)
        buckets[ports[i] >> 6]++;
    
    double entropy = 0.0;
    for (int i = 0; i < 1024; i++) {
        if (buckets[i] > 0) {
            double p = (double)buckets[i] / n;
            entropy -= p * log2(p);
        }
    }
    
    return entropy * (10.0 / log2(1024));  // 归一化
}
```

### 5.4 速率变异系数

```c
// 计算发包间隔的变异系数
static double calculate_rate_variance(sliding_window_t *w, uint64_t now, uint64_t window_ms) {
    sliding_window_cleanup(w, now, window_ms);
    if (w->count < 10) return -1.0;
    
    double intervals[SLIDING_WINDOW_SIZE];
    uint32_t n = 0;
    
    for (uint32_t i = 1; i < w->count; i++) {
        uint32_t pos = (w->head + i) % MAX_SAMPLES;
        uint32_t prev_pos = (w->head + i - 1) % MAX_SAMPLES;
        
        uint64_t interval_us = w->timestamps[pos] - w->timestamps[prev_pos];
        if (interval_us > 0 && interval_us < 1000000)
            intervals[n++] = (double)interval_us;
    }
    
    if (n < 5) return -1.0;
    
    double mean = 0;
    for (uint32_t i = 0; i < n; i++) mean += intervals[i];
    mean /= n;
    
    double variance = 0;
    for (uint32_t i = 0; i < n; i++) {
        double diff = intervals[i] - mean;
        variance += diff * diff;
    }
    variance /= n;
    
    double cv = sqrt(variance) / mean;
    return cv;
    // MASSCAN: CV < 0.01
    // 正常流量: CV > 0.1
}
```

### 5.5 源 IP 状态跟踪

```c
typedef struct {
    uint32_t src_ip;
    uint64_t first_syn_time;
    uint64_t syn_count;
    uint64_t last_syn_time;
    
    // 特征统计
    uint16_t last_ports[256];
    uint32_t port_count;
    double port_entropy;
    double rate_cv;
    
    // TCP 指纹投票
    uint32_t fingerprint_score_sum;
    uint32_t fingerprint_count;
    
    // 检测结果
    uint8_t detected : 1;
    uint8_t confidence;
} src_ip_state_t;
```

### 5.6 核心处理逻辑

```c
static void process_syn_packet(detector_context_t *ctx,
                               uint64_t now,
                               uint32_t src_ip,
                               uint16_t src_port,
                               const struct tcphdr *tcp) {
    
    // 1. 查找/创建源 IP 状态
    src_ip_state_t *state = hash_lookup_or_create(ctx->src_ip_table, src_ip);
    
    // 2. 更新统计
    state->syn_count++;
    state->last_syn_time = now;
    state->last_ports[state->port_count++ & 0xFF] = src_port;
    
    // TCP 指纹
    int fp_score = match_tcp_fingerprint(tcp);
    if (fp_score > 0) {
        state->fingerprint_score_sum += fp_score;
        state->fingerprint_count++;
    }
    
    // 3. 滑动窗口记录
    sliding_window_add(&ctx->syn_times, now, src_ip);
    
    // 4. 达到阈值后检测
    if (state->syn_count >= ctx->syn_count_threshold && !state->detected) {
        
        state->port_entropy = calculate_port_entropy(state->last_ports, state->port_count);
        state->rate_cv = calculate_rate_variance(&ctx->syn_times, now, ctx->time_window_ms);
        
        uint32_t score = 0;
        uint32_t features = 0;
        
        // 特征 1: 源端口高熵 (+30)
        if (state->port_entropy > ctx->entropy_threshold) {
            score += 30;
            features |= (1 << 0);
        }
        
        // 特征 2: 固定速率 (+30)
        if (state->rate_cv > 0 && state->rate_cv < ctx->rate_cv_threshold) {
            score += 30;
            features |= (1 << 1);
        }
        
        // 特征 3: TCP 指纹匹配 (+40)
        if (state->fingerprint_count > 0) {
            uint32_t avg_fp = state->fingerprint_score_sum / state->fingerprint_count;
            if (avg_fp >= ctx->fingerprint_threshold) {
                score += 40;
                features |= (1 << 2);
            }
        }
        
        // 5. 触发检测
        if (score >= 60) {
            state->detected = 1;
            state->confidence = score;
            send_alert(ctx, state, features);
        }
    }
}
```

## 6. 检测阈值矩阵

| 条件 | 置信度 | 告警级别 | 动作 |
|------|--------|---------|------|
| SYN ≥ 10 + 指纹 ≥ 80 + 端口唯一 = 100% | 95% | 严重 | 立即告警 |
| SYN ≥ 50 + 熵 > 13 + CV < 0.05 | 90% | 高 | 告警 |
| SYN ≥ 100 + 熵 > 12 | 75% | 中 | 告警 |
| SYN ≥ 20 + 指纹匹配 + 端口高熵 | 80% | 高 | 告警 |
| SYN ≥ 20 + CV < 0.01 + 熵 > 13 | 85% | 高 | 告警 |
| SYN < 10 | < 30% | 低 | 忽略 |
| 熵 < 10 + CV > 0.1 | < 20% | 低 | 排除 |

## 7. 告警输出格式

```json
{
  "alert_type": "MASSCAN_SCAN",
  "confidence": 92,
  "timestamp": "2026-04-16T10:30:45.123Z",
  "source": {
    "ip": "192.168.1.100",
    "port_range": "32768-60999",
    "asn": "AS12345",
    "geo": "CN"
  },
  "features": {
    "syn_count": 156,
    "port_entropy": 13.8,
    "rate_cv": 0.008,
    "tcp_fingerprint_score": 85,
    "ipid_incremental": true
  },
  "detection_methods": [
    "TCP_FINGERPRINT",
    "PORT_ENTROPY",
    "RATE_FIXED"
  ],
  "recommendation": "block_source_ip"
}
```

## 8. 优化策略

### 8.1 早期检测

```c
// 在只有 10-20 个 SYN 时就开始初步判断
static uint32_t early_detection(src_ip_state_t *state) {
    if (state->syn_count < 10) return 0;
    
    uint32_t score = 0;
    
    // TCP 指纹（立即可检测）
    if (state->fingerprint_count > 0) {
        uint32_t avg = state->fingerprint_score_sum / state->fingerprint_count;
        if (avg >= 60) score += 40;
        else if (avg >= 40) score += 20;
    }
    
    // 源端口唯一性（10 个包全是不同端口 = 强特征）
    if (state->syn_count >= 10) {
        uint32_t unique = count_unique(state->last_ports, state->port_count);
        if (unique >= 10) score += 30;
        else if (unique >= 8) score += 15;
    }
    
    return score;  // >= 50 即可早期预警
}
```

### 8.2 批量处理

```c
// 使用 DPDK/Ring Buffer 批量处理
#define BATCH_SIZE 32

static void process_packet_batch(detector_context_t *ctx, 
                                  struct packet_batch *batch) {
    for (int i = 0; i < batch->count; i++) {
        struct packet *pkt = &batch->pkts[i];
        
        if (pkt->tcp_syn && !pkt->tcp_ack) {
            process_syn_packet(ctx, pkt->timestamp,
                            pkt->src_ip, pkt->src_port, &pkt->tcp_hdr);
        }
    }
}
```

### 8.3 内存优化

```c
// 紧凑结构设计
typedef struct {
    uint32_t src_ip;
    uint64_t last_time;
    uint64_t syn_count;
    uint16_t last_port;
    uint8_t detected : 1;
    uint8_t confidence;
    uint32_t fingerprint_acc;
} compact_state_t;

// 内存占用: ~200 bytes → ~32 bytes
```

## 9. 部署建议

| 检测层次 | 部署位置 | 检测延迟 | 适用场景 |
|---------|---------|---------|---------|
| 报文层 | IDS 探针 | < 1ms | 实时告警 |
| 流层 | NetFlow 收集器 | < 100ms | 统计分析 |
| 行为层 | 离线分析集群 | 分钟级 | 深度分析 |

**建议检测优先级**：
1. **报文层** → 低延迟，捕获明显特征
2. **流层** → 统计异常，捕获隐蔽扫描
3. **行为层** → 离线分析，捕获复杂攻击

---

**文档版本**: 1.0
**生成日期**: 2026-04-16
