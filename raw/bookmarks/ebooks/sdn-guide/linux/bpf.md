# eBPF

## 简介

eBPF (extended Berkeley Packet Filter) 源于BPF，为内核数据包过滤提供支持。两个套接字选项启用过滤：`SO_ATTACH_FILTER` (cBPF) 和 `SO_ATTACH_BPF` (eBPF)。Linux 3.15+引入了带有内核虚拟机eBPF的数据包过滤。

## 使用场景

- XDP
- 流量控制
- 防火墙
- 网络数据包跟踪
- 内核探针
- cgroups
- bcc
- bpftools

## 图片

![eBPF图](ebpf.png)

## 参考文档

- Linux Kernel BPF documentation
- bcc
- "The BSD Packet Filter: A New Architecture for User-level Packet Capture"
- "Notes on BPF & eBPF"
