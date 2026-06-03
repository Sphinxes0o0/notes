# 内核网络参数

## 概述

本章涵盖Linux内核网络参数，组织成几个类别：nf_conntrack（连接跟踪）、bridge-nf（桥接netfilter）、反向路径过滤、TCP参数和ARP相关设置。它为每个参数提供配置建议和优化值。

## nf_conntrack

nf_conntrack处理iptables的连接跟踪，参数包括`nf_conntrack_max`、`nf_conntrack_buckets`和`nf_conntrack_tcp_timeout_established`。建议对于64GB RAM：`net.netfilter.nf_conntrack_max=4194304`、`net.netfilter.nf_conntrack_buckets=1048576`。

## bridge-nf

bridge-nf允许netfilter过滤桥接流量，通过`net.bridge.bridge-nf-call-iptables`和相关设置。

## 反向路径过滤

`rp_filter`有三个模式：
- 0（无验证）
- 1（严格RFC3704）
- 2（宽松RFC3704）

## TCP参数

记录在综合表中，包含窗口大小、keepalive设置、背包队列和各种TCP功能（SACK、时间戳、窗口缩放等）的默认和优化值。

## ARP参数

包括垃圾回收阈值（`gc_thresh1/2/3`）和过滤选项（`arp_filter`、`arp_announce`、`arp_ignore`、`arp_notify`、`arp_accept`）。
