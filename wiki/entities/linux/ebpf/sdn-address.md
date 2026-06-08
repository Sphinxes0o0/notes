---
type: entity
tags: [ebpf, sdn, networking, addressing, observability]
created:2026-06-08
sources: [bookmark-sdn-guide]
---

# SDN Addressing with eBPF

## 定义

SDN（Software-Defined Networking，软件定义网络）中的地址寻址是指在控制面与数据面分离后，通过控制器统一管理网络地址分配、路由、流表下发。eBPF作为现代 Linux 内核的可编程数据面，提供 XDP/TC钩子实现 SDN转发面，在 Cilium、Katran、CalicoeBPF data plane 等生产系统中广泛部署。

##关键要点

- **控制面/数据面分离**：OpenFlow/Ryu/ONOS 控制面 + eBPF/XDP 数据面
- **地址寻址**：L2 (MAC) + L3 (IP) + L4 (port) + 五元组流标识
- **eBPF map**：内核态 hash map存储 LPM trie路由、MAC/IP 表
- **Cilium**：eBPF-based CNI，替代 kube-proxy 实现 service 地址+负载均衡
- **可观测性**：eBPF 程序可导出连接跟踪、metric 到 Prometheus

##核心概念

- **LPM trie map**：最长前缀匹配，用于 IP路由查找
- **hash map**：MAC/IP → interface/endpoint映射
- **XDP_REDIRECT**：跨网卡/namespace 重定向（Cilium kube-proxy替代）
- **service 地址 (ClusterIP)**：iptables/IPVS → eBPF sockmap/sockhash
- **CT（Connection Tracking）**：eBPF 实现 conntrack + NAT
- **policy map**：CIDR-based流量策略

## 相关页面

- [[entities/linux/ebpf/ebpf-sdn-guide]] — eBPF SDN 综合指南
- [[entities/linux/ebpf/ebpf-networking]] — eBPF 网络编程
- [[entities/linux/ebpf/xdp-sdn-guide]] — XDP 在 SDN 的应用
- [[entities/sdn/sdn-architecture]] — SDN架构
- [[sources/bookmark-sdn-guide]] — SDN 学习资源
