# Linux 网络子系统 (Net/) 文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [net_socket_core.md](net_socket_core.md) | Socket 核心: socket.c, sock.c | net/socket.c, net/core/sock.c |
| [net_tcp_ip.md](net_tcp_ip.md) | TCP/IP 协议栈 | net/ipv4/tcp.c, tcp_input.c, tcp_output.c |
| [net_netfilter.md](net_netfilter.md) | Netfilter/iptables | net/netfilter/, net/ipv4/netfilter/ |
| [net_routing.md](net_routing.md) | 路由子系统 | net/ipv4/route.c, fib_frontend.c, fib_rules.c |
| [net_skbuff.md](net_skbuff.md) | skbuff 内存管理 | net/core/skbuff.c |

---

## 1. Socket 核心 (net_socket_core.md)

### 关键内容
- `socket()` 系统调用: `__sys_socket()` → `__sock_create()` → `sock_alloc()`
- `sock_map_fd()`: fd 分配 + file 结构关联
- `struct socket` vs `struct sock`: VFS 层与协议层数据结构
- `inet_stream_ops` / `inet_dgram_ops`: TCP/UDP 操作函数表
- `sock_sendmsg()` / `sock_recvmsg()`: 消息发送/接收
- 内存分配路径: `sk_alloc()` → `sk_prot_alloc()` → kmalloc/slab

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| __sys_socket | net/socket.c:1742 |
| __sock_create | net/socket.c:1534 |
| sock_alloc | net/socket.c:632 |
| sock_map_fd | net/socket.c:504 |
| sock_sendmsg | net/socket.c:753 |
| sock_recvmsg | net/socket.c:1096 |
| sk_alloc | net/core/sock.c:2296 |

---

## 2. TCP/IP 协议栈 (net_tcp_ip.md)

### 关键内容
- `struct tcp_sock`: 按缓存行优化的字段分组
- `tcp_sendmsg_locked()`: Nagle 算法、SKB 合并、copybreak
- `tcp_recvmsg_locked()`: 接收队列管理、urg data 处理
- `tcp_v4_connect()` → `tcp_connect()` → 三次握手
- TCP 状态机: TCP_SYN_SENT → TCP_ESTABLISHED → TCP_CLOSE
- `tcp_rcv_established()`: 快速路径（头部预测）
- `tcp_ack()`: ACK 处理、窗口更新、SACK
- 定时器: ICSK_TIME_RETRANS, ICSK_TIME_DACK, tcp_retransmit_timer()

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| tcp_sock | include/linux/tcp.h:197 |
| tcp_sendmsg | net/ipv4/tcp.c:1460 |
| tcp_recvmsg | net/ipv4/tcp.c:2965 |
| tcp_v4_connect | net/ipv4/tcp_ipv4.c:222 |
| tcp_connect | net/ipv4/tcp_output.c:4296 |
| tcp_rcv_established | net/ipv4/tcp_input.c:6519 |
| tcp_ack | net/ipv4/tcp_input.c:4246 |
| tcp_set_state | net/ipv4/tcp.c:2997 |

---

## 3. Netfilter (net_netfilter.md)

### 关键内容
- `struct nf_hook_ops`: 钩子函数结构
- `nf_register_net_hook()` / `nf_unregister_net_hook()`: 钩子注册
- `nf_hook_slow()`: 遍历执行所有注册的钩子
- `ipt_do_table()`: iptables 规则遍历（IP 头匹配 → matches → target）
- `struct ipt_entry`: 单条规则结构
- `struct ipt_replace`: 规则表替换结构
- NAT: `nf_nat_packet()` → `nf_nat_manip_pkt()`
- nftables: `nft_do_chain()` 表达式求值

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| nf_hook_ops | include/linux/netfilter.h:98 |
| nf_register_net_hook | net/netfilter/core.c:554 |
| __nf_register_net_hook | net/netfilter/core.c:393 |
| nf_hook_slow | net/netfilter/core.c:616 |
| ipt_do_table | net/ipv4/netfilter/ip_tables.c:222 |
| nft_do_chain | net/netfilter/nf_tables_core.c:249 |
| nf_nat_packet | net/netfilter/nf_nat_core.c:866 |

---

## 4. 路由子系统 (net_routing.md)

### 关键内容
- `struct fib_result`: FIB 查找结果
- `struct fib_info`: 路由信息（下一跳、接口、度量值）
- `struct rtable`: 路由表条目（dst_entry 包装）
- `fib_lookup()`: 通用 FIB 查找接口
- `fib_table_lookup()`: Trie 最长前缀匹配算法
- `ip_route_output_key_hash()`: 输出路由查找
- `ip_route_input_noref()`: 输入路由查找
- `fib_validate_source()`: 源地址验证
- `fib_rules_lookup()`: 路由策略规则
- 现代内核移除路由缓存，使用 dst_entry 缓存

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| fib_result | include/net/ip_fib.h:173 |
| fib_info | include/net/ip_fib.h:136 |
| fib_lookup | include/net/ip_fib.h:316 |
| fib_table_lookup | net/ipv4/fib_trie.c:1420 |
| ip_route_output_key_hash | net/ipv4/route.c:2691 |
| ip_route_input_noref | net/ipv4/route.c:2546 |
| fib_validate_source | net/ipv4/fib_frontend.c:429 |
| fib_rules_lookup | net/core/fib_rules.c:313 |

---

## 5. skbuff 内存管理 (net_skbuff.md)

### 关键内容
- `struct sk_buff`: 网络数据包缓冲区
  - head/data/tail/end 指针布局
  - frags 分散/聚集 I/O
  - skb_shared_info: 片段信息、引用计数
- `__alloc_skb()`: SKB 分配
- `__netdev_alloc_skb()`: 设备专用分配
- `skb_clone()`: 快速克隆（共享数据）
- `skb_copy()`: 完全复制
- `kfree_skb()` / `consume_skb()`: 释放路径
- SKB destructor 机制: sock_wfree, tcp_wfree
- dataref 引用计数（16位分割）
- `__pskb_pull_tail()`: linearize 过程

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| struct sk_buff | net/core/skbuff.c:885 |
| skb_shared_info | net/core/skbuff.c:593 |
| __alloc_skb | net/core/skbuff.c:672 |
| __netdev_alloc_skb | net/core/skbuff.c:759 |
| skb_clone | net/core/skbuff.c:2098 |
| __skb_clone | net/core/skbuff.c:1608 |
| skb_copy | net/core/skbuff.c:2178 |
| kfree_skb | (skb_free wrapper) |
| skb_release_data | net/core/skbuff.c:1089 |
| __pskb_pull_tail | net/core/skbuff.c:2866 |

---

## 架构总览

```
用户空间
    │
    │ socket() / connect() / send() / recv()
    ▼
┌─────────────────────────────────────────────────────────────┐
│ VFS 层: struct socket                                       │
│   └─> net/socket.c: socket_file_ops                       │
│       ├─> sock_read_iter / sock_write_iter                 │
│       ├─> sock_poll                                        │
│       └─> sock_close                                        │
└─────────────────────────────────────────────────────────────┘
    │
    │ sock->sk
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 协议层: struct sock / struct tcp_sock                       │
│   ├─> net/core/sock.c: sock_sendmsg / sock_recvmsg         │
│   └─> net/ipv4/tcp.c: tcp_sendmsg / tcp_recvmsg           │
│       ├─> tcp_connect / tcp_rcv_established               │
│       └─> tcp_ack / tcp_retransmit_timer                   │
└─────────────────────────────────────────────────────────────┘
    │
    │ skb = alloc_skb()
    ▼
┌─────────────────────────────────────────────────────────────┐
│ skbuff 层: struct sk_buff                                  │
│   ├─> net/core/skbuff.c: __alloc_skb / skb_clone          │
│   └─> frags (分散/聚集 I/O)                                │
└─────────────────────────────────────────────────────────────┘
    │
    │ dst_output()
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Netfilter 钩子                                               │
│   ├─> net/netfilter/core.c: nf_hook_slow                   │
│   └─> net/ipv4/netfilter/ip_tables.c: ipt_do_table        │
└─────────────────────────────────────────────────────────────┘
    │
    │ fib_lookup() / ip_route_output()
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 路由层                                                       │
│   ├─> net/ipv4/route.c: ip_route_output_key_hash          │
│   └─> net/ipv4/fib_trie.c: fib_table_lookup (Trie LPM)     │
└─────────────────────────────────────────────────────────────┘
    │
    │ dev_queue_xmit()
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 设备层                                                       │
│   └─> net/core/dev.c: dev_queue_xmit / netdev_start_xmit   │
└─────────────────────────────────────────────────────────────┘
```
