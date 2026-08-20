---
title: "eBPF深入理解 — How eBPF Work"
description: "**Source:** https://www.ilikejobs.com/posts/how-ebpf-work/"
---
# eBPF深入理解 — How eBPF Work

**Source:** https://www.ilikejobs.com/posts/how-ebpf-work/
**NIDS Relevance:** ★★★★★ (核心 — XDP/TC是NIDS的主要架构)

## 核心内容

### eBPF架构
- **BPF Verifier**: 10000+行代码，执行静态分析确保安全
- **JIT编译器**: bytecode → native machine code，2-4x性能提升
- **11个64位寄存器** (r0-r9, r10=sp)，RISC-like指令集
- **8字节指令格式**: `opcode(8) | dst_reg:4 | src_reg:4 | off:16 | imm:32`

### Hook点性能排名
Network: **XDP > TC > Socket Filter > Netfilter**
Tracing: **Tracepoint > Fentry/Fexit > Kprobe > Uprobe**

### 程序类型 (Network相关)
| 类型 | 性能 | 用途 |
|------|------|------|
| `BPF_PROG_TYPE_XDP` | ~10-20M pps | 最早可处理点，NIC驱动层 |
| `BPF_PROG_TYPE_SCHED_CLS` | 1-5M pps | TC classifier |
| `BPF_PROG_TYPE_SCHED_ACT` | 1-5M pps | TC action |
| `BPF_PROG_TYPE_SOCKET_FILTER` | ~1M pps | socket层过滤 |
| `BPF_PROG_TYPE_SOCK_OPS` | - | TCP状态监控 |

### Maps类型
- `BPF_MAP_TYPE_HASH` — 通用kv
- `BPF_MAP_TYPE_ARRAY` — 定长数组
- `BPF_MAP_TYPE_LRU_HASH` — 自动eviction缓存
- `BPF_MAP_TYPE_RINGBUF` (Linux 5.8+) — 无锁高性能事件传递
- `BPF_MAP_TYPE_PROG_ARRAY` — tail call跳转链

### Tail Call
最多32层，通过`BPF_MAP_TYPE_PROG_ARRAY`链接多个eBPF程序。

### XDP Relevance
- 运行在网络驱动层，`sk_buff`分配之前
- 支持DDoS防护、负载均衡、包过滤、AF_XDP零拷贝
- **NIDS用例**: 在XDP层做快速预过滤，只把可疑流量送往上层检测引擎

## 关键引用
> "XDP operates at the network driver layer, enabling ~10-20 million packets per second processing"

## 关联概念
-  — 已有entity，复用
-  — XDP是in-kernel bypass
- NIDS架构: XDP预过滤 → TC完整检测 →用户态Snort3
