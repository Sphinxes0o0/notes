---
type: entity
tags: [linux-kernel, networking, tcp, udp, ipv4, ipv6, ipsec, bridging, routing, bpf, xdp]
created: 2026-05-20
sources: [notes-network]
---

# Linux Network Protocols (Linux 网络协议实现)

## 定义

Linux 网络协议实现涵盖 IPv4/IPv6/TCP/UDP/SCTP 等传输层和网络层协议的详细内核实现，以及 BPF/XDP、桥接、路由等高级网络功能。

## 关键要点

### TCP 实现 (net/ipv4/tcp.c, tcp_input.c, tcp_output.c)

**核心结构**：
- `struct tcp_sock`（继承 `inet_connection_sock` → `inet_sock` → `sock`）
- 按缓存行优化分组：TX 热路径、RX 热路径、TXRX 读写热点

**发送路径**：
- `tcp_sendmsg()` → `tcp_sendmsg_locked()`
- Nagle 算法、SKB 合并（`tcp_skb_can_collapse_to()`）
- copybreak 优化：skb 数据直接复用
- `tcp_transmit_skb()` → `tcp_output()` 生成 IP 头

**接收路径**：
- `tcp_rcv_established()`：快速路径头部预测（pred_flags 匹配）
- `tcp_ack()`：ACK 处理、窗口更新、SACK
- `tcp_data_queue()`：接收队列管理、乱序段处理

**连接生命周期**：
- 三次握手：`tcp_v4_connect()` → `tcp_connect()` → SYN_SENT
- 状态机：`TCP_SYN_SENT` → `TCP_SYN_RECV` → `TCP_ESTABLISHED`
- 四次挥手：`FIN_WAIT1` → `FIN_WAIT2` → `TIME_WAIT`

**定时器**（net/ipv4/tcp_timer.c）：
- `ICSK_TIME_RETRANS`：重传定时器
- `ICSK_TIME_DACK`：延迟 ACK 定时器
- `ICSK_TIME_PROBE0`：零窗口探测定时器
- `ICSK_TIME_LOSS_PROBE`：Tail Loss Probe

### UDP 实现 (net/ipv4/udp.c)

- `struct udp_sock`：继承 `sock`，包含 `udp_table` 哈希槽
- `udp_sendmsg()` / `udp_recvmsg()`：无连接，简单发送/接收
- `udp_v4_check()`：伪头校验和计算
- 无状态，不跟踪连接状态

### IPv4 协议栈 (net/ipv4/)

**路由**（net/ipv4/route.c）：
- `ip_route_output_key_hash()`：输出路由查找
- `ip_route_input_noref()`：输入路由查找
- `fib_lookup()` → `fib_table_lookup()`：Trie 最长前缀匹配
- `fib_validate_source()`：源地址验证（anti-spoofing）

**FIB 结构**（include/net/ip_fib.h）：
- `struct fib_result`：查找结果（prefix、fib_info、fib_props）
- `struct fib_info`：路由信息（下一跳、接口、度量值）
- `struct fib_table`：路由表（local/main/default）

### IPv6 协议栈 (net/ipv6/)

- `ipv6_addrconf`：地址配置（autoconf、SLAAC）
- `ipv6_ndisc`：邻居发现协议（NDP）
- `ipv6_route_input()`：IPv6 输入路由查找
- 支持 `struct in6_addr` 128 位地址

### BPF/XDP (net/core/filter.c, kernel/bpf/)

**XDP (Express Data Path)**：
- 在 skb 分配**前**处理数据包（DMA 环形缓冲区阶段）
- 极低延迟：~10 cycles/packet vs 传统 ~60 cycles/packet
- 返回码：`XDP_PASS`/`XDP_DROP`/`XDP_TX`/`XDP_REDIRECT`
- 支持 AF_XDP 零拷贝重定向

**BPF_PROG_TYPE_XDP**：
- `dev_change_xdp_fd()`：附加 XDP 程序到设备
- `bpf_redirect_map()`：重定向到其他设备或 AF_XDP socket
- `struct bpf_dtab`：设备映射表

**BPF 过滤器**：
- `BPF_PROG_TYPE_SOCKET_FILTER`：套接字过滤
- `bpf_prog_run()`：执行 BPF 程序
- `SK_RUN_ARRAY`：基于 `SK_RUN_FILTER` 的快速分发

### 桥接 (net/bridge/)

- `struct net_bridge`：网桥设备
- `br_forward()`：桥接转发
- `br_handle_frame()`：MAC 学习 + 转发决策
- 支持 STP（生成树协议）、VLAN

### Open vSwitch (net/openvswitch/)

- 软件交换机，支持 OpenFlow 控制器
- `ovs_flow_tbl`：流表查找
- `dp_packet`：通用数据包（支持多种封装）

### DSCP/ECN 标记 (netfilter/)

- `xt_DSCP`/`xt_MARK`：DSCP 分组标记
- `ipt_ECN`/`xt_HL`：ECN、TTL 修改
- `xt_TCPMSS`：TCP MSS 修正

### 性能优化机制

**NAPI 轮询**：
- 中断驱动 → 轮询模式切换，减少高负载时中断风暴
- `net_rx_action()` softirq 处理
- `napi_schedule()` / `napi_complete_done()`

**GRO (Generic Receive Offload)**：
- 批量合并相同流的 SKB
- `napi_gro_receive()` → `gro_complete()` 或合并
- 减少协议处理开销

**RPS/RFS (Receive Packet Steering)**：
- 软件层面将包分发到不同 CPU
- 避免单核瓶颈

## 源码关键位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `net/ipv4/tcp.c` | 197 | `struct tcp_sock` |
| `net/ipv4/tcp.c` | 1460 | `tcp_sendmsg()` |
| `net/ipv4/tcp.c` | 2965 | `tcp_recvmsg()` |
| `net/ipv4/tcp_ipv4.c` | 222 | `tcp_v4_connect()` |
| `net/ipv4/tcp_output.c` | 4296 | `tcp_connect()` |
| `net/ipv4/tcp_input.c` | 6519 | `tcp_rcv_established()` |
| `net/ipv4/route.c` | 2691 | `ip_route_output_key_hash()` |
| `net/core/dev.c` | 4760 | `__dev_queue_xmit()` |
| `net/core/filter.c` | XDP | BPF/XDP 实现 |

## 相关概念

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络子系统核心框架
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] — Netfilter 钩子与 iptables/nftables

## 来源详情

- github-notes-network-tcpip-tcp — TCP 协议详解
- github-notes-network-tcpip-ip — IP 协议详解
- github-notes-network-linux-kernel-bpf-xdp — BPF/XDP 钩子
- github-notes-network-linux-kernel-ipv4-tcp — IPv4 TCP 实现
- github-notes-network-linux-kernel-ipv6-core — IPv6 核心实现
