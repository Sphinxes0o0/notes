---
type: entity
tags: [linux-kernel, networking, socket, skbuff, netdevice, tcp, udp, routing, ipv4, ipv6]
created: 2026-05-20
sources: [github-notes-net]
---

# Linux Kernel Net Subsystem (网络子系统)

## 定义

Linux 内核网络子系统是负责网络数据包在协议栈各层处理和传输的核心框架，涵盖从物理设备驱动到应用层 socket API 的完整路径。

## 关键要点

### 核心数据结构

| 结构体 | 位置 | 用途 |
|--------|------|------|
| `struct socket` | `include/linux/net.h:116` | VFS 层套接字抽象 |
| `struct sock` | `include/net/sock.h:360` | 协议层套接字状态 |
| `struct sk_buff` | `include/linux/skbuff.h:885` | 数据包缓冲区 |
| `struct net_device` | `include/linux/netdevice.h:2109` | 网络设备抽象 |

### Socket 层 (net/socket.c)

- `socket()` → `__sys_socket()` → `__sock_create()` → `sock_alloc()`
- `struct socket` 通过 inode 嵌入到 VFS，文件描述符关联到 `struct file`
- `sock_map_fd()` 分配 fd 并建立 socket ↔ file 双向映射
- `inet_stream_ops` (TCP) / `inet_dgram_ops` (UDP) 提供协议操作函数表

### sk_buff (套接字缓冲区)

- **head/data/tail/end 指针布局**：head=缓冲起始，tail=数据结束
- **skb_put/skb_push/skb_pull**：在缓冲区头部/尾部操作数据
- **克隆 vs 复制**：`skb_clone()` 共享数据（原子 refcnt），`skb_copy()` 完全复制
- **分散/聚集 I/O**：通过 `frags[]` 和 `frag_list` 支持线性化

### Netdevice (网络设备)

- `struct net_device`：统一抽象物理网卡、虚拟设备、隧道
- **发送**：`dev_queue_xmit()` → `__dev_queue_xmit()` → `sch_handle_egress()` → `ndo_start_xmit()`
- **接收**：NAPI 轮询机制替代传统中断驱动，GRO 批量合并
- **XDP**：在 skb 分配前（DMA 环形缓冲区阶段）即可处理数据包

### 路由子系统 (net/ipv4/route.c)

- `struct rtable` = dst_entry 包装 + 路由表条目
- `fib_lookup()` → `fib_table_lookup()`：Trie 最长前缀匹配（LPM）
- 现代内核移除路由缓存，使用 dst_entry 缓存

### TCP 实现 (net/ipv4/tcp.c)

- `struct tcp_sock` 按缓存行分组优化：TX 热路径、RX 热路径分立
- `tcp_sendmsg_locked()`：Nagle 算法、SKB 合并、copybreak 优化
- `tcp_rcv_established()`：快速路径头部预测
- 三次握手：`tcp_v4_connect()` → `tcp_connect()` → SYN_SENT → ESTABLISHED
- 定时器：ICSK_TIME_RETRANS（重传）、ICSK_TIME_DACK（延迟ACK）、TLP

### 数据路径总结

```
socket() / connect() / send()
    ↓
struct socket (VFS层) → sock->sk (struct sock/inet_sock/tcp_sock)
    ↓
tcp_sendmsg() / udp_sendmsg()
    ↓
alloc_skb() → skb_put() → skb_push(协议头)
    ↓
Netfilter Hooks (nf_hook_slow → ipt_do_table / nft_do_chain)
    ↓
fib_lookup() / ip_route_output()
    ↓
dev_queue_xmit() → netdev_start_xmit() → NIC DMA
```

## 源码关键位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `net/socket.c` | 1742 | `__sys_socket()` |
| `net/socket.c` | 1534 | `__sock_create()` |
| `net/socket.c` | 632 | `sock_alloc()` |
| `net/core/sock.c` | 2296 | `sk_alloc()` |
| `net/core/skbuff.c` | 885 | `struct sk_buff` |
| `net/core/dev.c` | 4760 | `__dev_queue_xmit()` |
| `net/ipv4/tcp.c` | 1460 | `tcp_sendmsg()` |
| `net/ipv4/tcp_ipv4.c` | 222 | `tcp_v4_connect()` |
| `net/ipv4/fib_frontend.c` | 280 | `fib_lookup()` |

## 相关概念

- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] — Netfilter 钩子框架
- [[entities/linux/network/linux-network-protocols]] — 协议层实现（TCP/UDP/IPv4/IPv6）
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] — 调度与网络 softirq 抢占

## 来源详情

- [[sources/github-notes-net]] — Linux Net 子系统深度分析 R1
- [[sources/github-notes-network]] — 网络笔记索引
## Related Concepts

- [[entities/linux/kernel/crypto/linux-kernel-crypto-core]] — 网络协议栈依赖内核加密API实现TLS/IPsec
