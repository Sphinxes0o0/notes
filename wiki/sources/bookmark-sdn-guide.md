---
type: source
source-type: bookmark
title: "SDN网络指南"
author: "feiskyer"
date: 2026-05-28
size: small
path: raw/bookmarks/ebooks/sdn-guide/
summary: "feiskyer SDN实践指南，覆盖网络基础(TCP/IP/ARP/DHCP/VLAN)、Linux网络(TC/eBPF/XDP/iptables)、SDN架构(OpenFlow/P4/ONOS)、DPDK/OVS容器网络"
---

# SDN网络指南

## 核心内容

### 网络基础 (basic/)
- TCP/IP五层模型、ARP、ICMP、路由、交换机、UDP、DHCP、DNS、VLAN、Overlay

### Linux网络 (linux/)
- **流量控制 TC/eBPF**: qdisc-class-filter树形结构，HTB/PFIFO/RED等qdisc类型，ifbingress整形
- **负载均衡**: LVS NAT/DR/TUN/FULLNAT模式，Maglev一致性哈希
- **XDP**: eXpress Data Path，网卡驱动层可编程，~20Mpps，无锁批量I/O，DDIO
- **eBPF**: 扩展BPF，Linux 3.15+，内核虚拟机，tc/iptables/XDP/firewall/跟踪/探针
- **iptables/netfilter**: 5个hook点(NF_IP_PRE_ROUTING/LOCAL_IN/FORWARD/LOCAL_OUT/POST_ROUTING)，table-chain-filter
- **SR-IOV**: 虚拟函数VF，IOMMU直通，网卡虚拟化
- **VRF**: 虚拟路由转发，内核级路由隔离

### SDN架构 (sdn/)
- **OpenFlow**: 2008年Nick McKeown提出，流表匹配(输入端口/包头/MAC/IP/TCP/UDP/ICMP)，Meter表速率限制，三种消息类型(controller-to-switch/asynchronous/symmetric)
- **OF-Config**: OpenFlow交换机配置协议
- **NETCONF**: 网络配置协议，XML编码，RPC调用
- **P4**: 可编程数据平面语言，协议无关，靶向网络编程
- **控制器**: NOX/POX、OpenDaylight、ONOS、Floodlight
- **ONOS**: Open Network Operating System，Bell Labs发起，高可用SDN控制器
- **Floodlight**: Java实现的OpenFlow控制器

### DPDK (dpdk/)
- 数据平面开发套件，轮询模式驱动PMD，大页内存，NUMA感知，Ring队列，virtio-user
- **OVS-DPDK**: Open vSwitch结合DPDK用户态转发
- **SPDK**: 存储性能开发套件，NVMe over Fabrics

### 容器网络 (container/)
- **CNI**: Container Network Interface，K8s网络插件标准，ADD/DEL/GET接口
- **CNM**: Docker libnetwork容器网络模型
- **Kubernetes网络**: Pod网络、Service、Ingress、CNI插件(Calico/Flannel/Weave)

### NFV & SD-WAN
- NFV: 网络功能虚拟化，ETSI NFV架构
- SD-WAN: 软件定义广域网，WAN优化

## 关键引用

- GitBook: https://feisky.gitbooks.io/sdn/
- GitHub: https://github.com/feiskyer/sdn-handbook

## 相关页面
- [[linux-ebpf-overview]] — eBPF基础（XDP/tc/BCC/bpftools）
- [[linux-ebpf-xdp]] — XDP深度（Facebook生产实践）
- [[linux-network-tc-ebpf-direct-action]] — TC eBPF Direct Action模式
- [[linux-net-stack-overview]] — Linux网络协议栈总览
- [[sdn-architecture]] — SDN架构
- [[openflow]] — OpenFlow协议详解
