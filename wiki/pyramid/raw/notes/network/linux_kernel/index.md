# Linux 内核网络子系统深度分析

## 概述

本文档是 Linux 内核网络子系统的全面深度分析，涵盖从物理设备驱动到应用层 socket API 的完整协议栈。

## 目录结构

### 核心框架
- [sk_buff - 套接字缓冲区管理](./sk_buff.md)
- [net_device - 网络设备抽象层](./net_device.md)
- [Socket 层 - 通用套接字层](./socket.md)
- [Socket 系统调用](./socket_syscall.md)

### 数据路径
- [NAPI 轮询机制](./napi.md)
- [GRO - 通用接收卸载](./gro.md)
- [Netpoll - 网络轮询接口](./netpoll.md)
- [page_pool - 内存页池](./page_pool.md)

### 协议栈核心
- [IPv4 协议栈核心](./ipv4_core.md)
- [IPv4 UDP 实现](./ipv4_udp.md)
- [IPv4 TCP 实现](./ipv4_tcp.md)
- [IPv4 路由子系统](./ipv4_routing.md)
- [IPv4 FIB 路由结构](./ipv4_fib.md)

### IPv6
- [IPv6 协议栈核心](./ipv6_core.md)
- [IPv6 路由子系统](./ipv6_routing.md)
- [IPv6 addrconf 地址管理](./ipv6_addrconf.md)
- [IPv6 NDisc 邻居发现](./ipv6_ndisc.md)
- [IPv6 TCP/UDP 实现](./ipv6_tcp_udp.md)

### Netfilter
- [Netfilter 核心框架](./netfilter.md)
- [xt_DSCP/xt_MARK - 分组标记](./netfilter_dscp_mark.md)
- [xt_HL/ipt_ECN - 生存时间](./netfilter_ecn.md)
- [xt_TCPMSS - TCP MSS 修正](./netfilter_tcpmss.md)
- [xt_RATEEST - 速率估计](./netfilter_rateest.md)

### BPF/XDP
- [BPF 过滤器核心](./bpf_filter.md)
- [BPF/XDP 钩子](./bpf_xdp.md)
- [XDP 传输层](./xdp.md)

### 传输协议
- [Unix Domain Socket](./unix_socket.md)
- [AF_PACKET 套接字](./af_packet.md)
- [net/sctp - SCTP 传输协议](./sctp.md)
- [net/rxrpc - RxRPC 远程调用](./rxrpc.md)
- [net/tipc - TIPC 传输服务](./tipc.md)

### 路由与邻居
- [dst_entry 和路由缓存](./dst_entry.md)
- [neighbour - 邻居子系统](./neighbour.md)
- [rtnetlink - 路由 netlink 接口](./rtnetlink.md)
- [flow_dissector - 报文解析](./flow_dissector.md)

### 交换与虚拟化
- [net/bridge - 网桥实现](./bridge.md)
- [net/openvswitch - Open vSwitch](./openvswitch.md)
- [net/dsa - 分布式交换机架构](./dsa.md)

### 其他组件
- [net/mac80211 - IEEE 802.11 协议栈](./mac80211.md)
- [net/xfrm - IPsec 框架](./xfrm.md)
- [net/sched - QoS 调度框架](./qos_sched.md)
- [net/bluetooth - 蓝牙协议栈](./bluetooth.md)

## 分析方法论

本分析采用以下方法论：

1. **源代码优先** - 直接阅读内核源码而非仅依赖文档
2. **结构化分解** - 将大型子系统拆分为可管理的分析单元
3. **关键数据结构** - 带文件位置和行号的结构定义
4. **函数实现** - 关键函数的签名、位置和实现要点
5. **协议流程** - 状态机和数据流分析

## 任务统计

| 类别 | 数量 |
|-----|-----|
| 核心框架 | 4 |
| 数据路径 | 5 |
| IPv4/IPv6 | 10 |
| Netfilter | 5 |
| BPF/XDP | 3 |
| 传输协议 | 4 |
| 路由与邻居 | 5 |
| 交换与虚拟化 | 3 |
| 其他组件 | 4 |
| **总计** | **43** |

## 来源

本分析基于 Linux 内核源码，任务编号 #1-42。
