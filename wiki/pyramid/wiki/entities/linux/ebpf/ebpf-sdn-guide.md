---
type: entity
tags: [eBPF, SDN, Linux, 可编程网络, XDP, TC]
created: 2026-05-28
sources: [bookmark-sdn-guide]
---

# eBPF (extended Berkeley Packet Filter)

## 定义

源于BPF，为内核数据包过滤提供支持。Linux 3.15+引入带有内核虚拟机的eBPF，实现内核可编程数据平面。

## 关键要点

### 启用方式
- `SO_ATTACH_FILTER` (cBPF)
- `SO_ATTACH_BPF` (eBPF)

### 主要使用场景
- **XDP**: eXpress Data Path，网卡驱动层可编程
- **TC** (Traffic Control): 流量控制qdisc的classifier/action
- **防火墙**: netfilter hook，替代部分iptables规则
- **网络数据包跟踪**: sk_buff探针
- **内核探针** (kprobe/uprobe): 函数入口/出口插桩
- **cgroups**: 资源控制和限制
- **BCC**: BPF Compiler Collection工具链
- **bpftools**: 内核BPF调试工具

### 内核虚拟机
- 64位寄存器(10个通用寄存器+1个PC)
- 栈空间512字节
- 辅助函数访问内核数据
- Verifier安全验证

### 与SDN关系
- eBPF可作为SDN数据平面的可编程方案(替代P4的一部分场景)
- 在Linux内核中实现灵活的包处理逻辑
- [[linux-ebpf-xdp]] — XDP深度分析
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action模式

## 相关概念
- [[linux-ebpf-overview]] — eBPF基础总览
- [[linux-ebpf-xdp]] — XDP快速数据路径
- [[sdn-address]] — SDN架构（eBPF是数据平面可编程的关键技术）
- [[traffic-control]] — TC流量控制（eBPF的另一个重要应用场景）

## 来源详情
- [[bookmark-sdn-guide]] — SDN网络指南
