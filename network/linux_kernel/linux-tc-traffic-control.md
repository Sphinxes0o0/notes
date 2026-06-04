# Linux TC流量控制

**Source:** https://www.ilikejobs.com/posts/what-is-tc/
**NIDS Relevance:** ★★★★☆ (NIDS流量仿真/测试的核心工具)

## 核心内容

### Queuing Disciplines (qdisc)
| qdisc | 用途 |
|-------|------|
| `pfifo_fast` | 默认FIFO队列 |
| `netem` | 网络仿真（延迟、丢包、重排、损坏、复制） |
| `tbf` | Token Bucket Filter（带宽限速） |
| `htb` | Hierarchical Token Bucket（复杂带宽分配） |
| `cbq` | Class-Based Queue |
| `prio` | Priority Queue |
| `fq_codel` | Fair Queueing CoDel（减少bufferbloat） |
| `cake` | 高级队列管理 |

### Filters & Classifiers
- **u32**: 基于协议/IP/端口分类
- **fw**: 基于firewall mark分类

### 流量控制操作
- 带宽限速: `rate 1mbit`, `200kbit`
- 延迟仿真: `fixed 2ms`, `variable 100ms±10ms`
- 丢包: `1%`, `0.1%`, `correlated`
- 重排: `25% reorder`
- 复制/损坏
- 基于优先级QoS

### NIDS Relevance
1. **网络损伤仿真**: 用`netem`模拟丢包、延迟、重排测试NIDS检测准确性
2. **限速压测**: `tbf`限速压测NIDS在高负载下的检测能力
3. **流量分类**: u32/fw隔离suspicious flows独立分析
4. **协议重构验证**: 延迟/重排测试NIDS的TCP协议重组能力
5. **QoS隔离**: 为检测流量保障带宽，避免被合法大流量淹没

## 关联概念
- [[linux-advanced-routing-tc]] — lartc.org HOWTO更全面
-  — TC eBPF direct-action mode
- NIDS架构: tc netem → 流量仿真 → Snort3测试
