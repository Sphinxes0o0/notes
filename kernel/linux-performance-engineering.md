# Linux性能优化实战

**Source:** https://learn.lianglianglee.com/专栏/Linux性能优化实战
**NIDS Relevance:** ★★★★☆ (系统性能问题排查工具和方法论)

## 核心内容 (基于目录结构推断)

### 性能优化维度
- **CPU性能**: 热点分析、调度优化、上下文切换
- **内存性能**: 缓存命中率、OOM分析、SLUB/SLAB
- **磁盘IO**: IOPS、吞吐量、blk-mq
- **网络性能**: TCP参数、拥塞控制、软中断

### 核心工具链
| 工具 | 用途 |
|------|------|
| `perf` | CPU profiling,热点分析 |
| `bpftrace` | 动态内核追踪 |
| `top/htop` | 进程/线程监控 |
| `vmstat` | 虚拟内存统计 |
| `iostat` | 磁盘IO统计 |
| `sar` | 系统活动报告 |
| `tcpdump` | 网络包抓取 |
| `ss` | Socket统计 |
| `bcc/tools` | eBPF性能分析工具 |

### 典型问题场景
- CPU利用率100%但吞吐低 → 锁竞争/IO阻塞
- 内存泄漏 → 堆外内存泄漏排查
- 网络延迟高 → TCP参数/拥塞控制问题
- 软中断不均衡 → RSS/RPS配置

### NIDS Relevance
1. **性能瓶颈定位**: NIDS丢包通常因CPU/内存/网络瓶颈，用perf/bpftrace定位
2. **软中断优化**: 网络包处理依赖softirq，优化RX/TX平衡
3. **TCP参数调优**: net.core.somaxconn、net.ipv4.tcp_max_syn_backlog等影响NIDS连接处理
4. **eBPF观测**: bpftrace/bcc工具可实时观测NIDS数据包处理路径
5. **缓存优化**: NIDS flow table缓存命中率影响检测性能

## 关联概念
- [[wiki/sources/arthurchiao-linux-net-stack]] — Linux网络栈概览
- [[wiki/sources/arthurchiao-linux-irq-softirq]] — IRQ/softirq机制
