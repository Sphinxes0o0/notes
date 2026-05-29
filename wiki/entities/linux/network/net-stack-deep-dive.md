---
type: entity
tags: [linux-kernel, networking, tcp, udp, ip, skbuff, netfilter, routing, socket, architecture]
created: 2026-05-22
sources: [notes-net-deep]
---

# Network Stack Deep Dive — 网络栈全路径深度分析

## 定义

Linux 网络栈从应用层 socket API 到物理层 NIC DMA 的全路径分析，涵盖 Socket 层架构、TCP/UDP 协议实现、IP 路由与分片重组、Netfilter 钩子框架、sk_buff 数据操作以及拥塞控制算法，形成对内核网络数据路径的完整理解。

## 关键要点

### 全路径架构

```
应用层: socket() / send() / recv()
    ↓
VFS 层: struct socket
    ├─ file 关联 → fd
    ├─ proto_ops (inet_stream_ops / inet_dgram_ops)
    └─ sock → struct sock/ inet_sock / tcp_sock
    ↓
协议层: tcp_sendmsg() / udp_sendmsg()
    ├─ 分段/合并 (Nagle, copybreak)
    ├─ SKB 分配 (alloc_skb)
    └─ 协议头构建 (skb_push TCP/IP/MAC)
    ↓
IP 层: ip_output() / ip_local_deliver()
    ├─ 路由查找 (fib_lookup → Trie LPM)
    ├─ 分片/重组 (ip_fragment / ip_defrag)
    └─ Netfilter LOCAL_OUT / PRE_ROUTING
    ↓
Netfilter 钩子: nf_hook_slow()
    ├─ iptables (filter/nat/mangle/raw 四表)
    ├─ nftables (字节码虚拟机 nft_do_chain)
    ├─ conntrack (连接跟踪, NEW/ESTABLISHED/RELATED)
    └─ NAT (dnat/snat: nf_nat_packet)
    ↓
邻居子系统: neigh_resolve_output()
    ├─ ARP 查找 (neigh_lookup → nud_state)
    └─ L2 地址解析
    ↓
设备层: dev_queue_xmit()
    ├─ Qdisc (tc 流量控制)
    └─ ndo_start_xmit() → NIC DMA
```

### Socket 层（net/socket.c）

**创建流程**：`socket()` → `__sys_socket()` → `__sock_create()` → `sock_alloc()` + `pf->create()` (inet_create)

**核心结构继承链**：
```
struct socket                  (VFS 层, 面向用户)
  └─ struct sock               (协议无关层)
       └─ struct inet_sock     (IPv4 层)
            └─ struct inet_connection_sock  (面向连接)
                 └─ struct tcp_sock  (TCP 专用, 按 cacheline 优化)
```

**关键方法表**：
- `struct proto_ops` (socket 层): `bind`, `connect`, `accept`, `sendmsg`, `recvmsg`
- `struct proto` (sock 层): `sendmsg`, `recvmsg`, `backlog_rcv`, `hash`/`unhash`

### TCP 发送路径

`tcp_sendmsg()` → `tcp_sendmsg_locked()`：
1. 检查发送窗口和拥塞窗口（cwnd）
2. `skb_stream_alloc_skb()` 分配 SKB
3. `skb_add_data_nocache()` 从用户空间拷贝数据
4. Nagle 算法决策（延迟发送 vs 立即发送）
5. `tcp_push_one()` → `tcp_write_xmit()` → `tcp_transmit_skb()`

### TCP 接收快速路径

`tcp_rcv_established()` 使用**头部预测（Header Prediction）**：
- `pred_flags` 预计算期望的标志位组合
- 若收到的 TCP 标志与预测一致，跳过完整状态检查，直接排队
- 预测失败回退到慢路径 `tcp_rcv_state_process()`

### TCP 拥塞控制

状态机分为慢启动和拥塞避免两阶段：

| 阶段 | 条件 | cwnd 增长 |
|------|------|-----------|
| 慢启动 | cwnd < ssthresh | 每 ACK: cwnd += MSS |
| 拥塞避免 | cwnd >= ssthresh | 每 RTT: cwnd += MSS |

**丢包反应**：
- **Tahoe**：ssthresh = cwnd/2，cwnd = MSS（回到慢启动）
- **Reno**：ssthresh = cwnd/2，cwnd = cwnd/2（快速恢复）

**RTT 估计（Jacobson 算法）**：
```
srtt   = (1 - α) × srtt + α × RTT_sample    (α = 0.125)
mdev   = (1 - β) × mdev + β × |srtt - RTT|  (β = 0.25)
rttvar = mdev
RTO    = srtt + 4 × rttvar
```

### IP 路由与分片

**输出路由**：`ip_route_output_key_hash()` → `fib_lookup()` → `fib_table_lookup()`（LC-trie 最长前缀匹配）

**三层 FIB Trie 算法**：
1. **Travel**：从根节点按 key bits 向叶子遍历
2. **Backtrack**：未匹配则回溯查找更短前缀
3. **Process Leaf**：在叶子链表 `fib_alias` 中选最佳条目（TOS/DSCP/scope 匹配）

**IP 分片**：`ip_fragment()` 当 skb→len > MTU 时，拆分为多个 SKB，设置 `frag_off` 偏移和 MF（More Fragments）标志。

### Netfilter 钩子

五个标准钩子点覆盖全路径：
- `NF_INET_PRE_ROUTING`（接收后路由前）：DNAT、conntrack
- `NF_INET_LOCAL_IN`（本地交付）：INPUT 防火墙
- `NF_INET_FORWARD`（转发）：FORWARD 防火墙
- `NF_INET_LOCAL_OUT`（本机发出）：OUTPUT 防火墙
- `NF_INET_POST_ROUTING`（发送前）：SNAT、MASQUERADE

四表（iptables）：filter、nat、mangle、raw，各有不同的 hook 注册组合。

### SKB 数据操作

在协议栈各层穿越时通过 `skb_push/skb_pull` 操作协议头：

```
应用数据准备:
  alloc_skb → skb_reserve(headroom) → skb_put(载荷)

协议头添加 (自上而下):
  TCP:  skb_push(tcp_hdr) → 填充端口/序列号
  IP:   skb_push(ip_hdr)  → 填充地址/协议号
  MAC:  skb_push(eth_hdr) → 填充 MAC/EtherType

接收解析 (自下而上):
  MAC:  skb_pull(eth_hdr) → 获取 EtherType
  IP:   skb_pull(ip_hdr)  → 获取协议号/地址
  TCP:  skb_pull(tcp_hdr) → 获取端口
```

## 源码关键位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `net/socket.c` | 1534 | `__sock_create()` |
| `net/socket.c` | 632 | `sock_alloc()` |
| `net/ipv4/af_inet.c` | 350 | `inet_create()` |
| `net/ipv4/tcp.c` | 1460 | `tcp_sendmsg()` |
| `net/ipv4/tcp_input.c` | 6519 | `tcp_rcv_established()` (快速路径) |
| `net/ipv4/udp.c` | `udp_sendmsg()` / `udp_recvmsg()` |
| `net/ipv4/route.c` | 2691 | `ip_route_output_key_hash()` |
| `net/ipv4/fib_trie.c` | 1420 | `fib_table_lookup()` (LPM) |
| `net/ipv4/ip_output.c` | `ip_fragment()` / `ip_output()` |
| `net/netfilter/core.c` | 616 | `nf_hook_slow()` |
| `net/core/dev.c` | 4760 | `__dev_queue_xmit()` |

## 相关概念

- [[entities/linux/kernel/net]] — 网络子系统整体架构
- [[entities/linux/kernel/net/skbuff-deep-dive]] — SKB 内存管理与 Clone/Copy 详解
- [[entities/linux/kernel/netfilter]] — Netfilter/iptables/nftables/conntrack
- [[entities/linux/network/linux-network-protocols]] — TCP/UDP/IPv4/IPv6 协议实现细节
- [[entities/linux/network/osi-physical-layer]] — 底部 PHY/MAC 层与驱动接口

## 来源详情

- [[sources/notes-net-deep]] — network_stack_deep_dive.md + net_deep_dive_r1.md + 相关 core/ 文档
- [[sources/achieved-linux-packet-flow]] — plantegg: 网络包流转详解
- [[sources/achieved-arp-table-aging]] — Linux ARP表老化机制
- [[sources/achieved-bluepuni-blog]] — Caturra's Blog: packetdrill TCP分析
