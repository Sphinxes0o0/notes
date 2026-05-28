---
type: entity
tags: [linux, kernel, networking, skbuff, net-stack]
created: 2026-05-28
sources: [arthurchiao-linux-net-stack]
---

# skbuff Deep Dive

## 定义

skbuff（socket buffer）是 Linux 内核网络栈中用于管理网络数据包的核心数据结构。它包含数据包的实际数据以及元信息，用于在各网络层之间传递数据。

## 关键结构

```c
struct sk_buff {
    struct sk_buff *next;
    struct sk_buff *prev;
    ktime_t     tstamp;        // 数据包时间戳
    struct sock *sk;            // 所属 socket
    struct net_device *dev;     // 接收/发送设备
    char         cb[48];        // 控制缓冲区
    unsigned int len, data_len;  // 长度信息
    __u8        *head;         // 缓冲区和数据指针
    __u8        *data;
    __u8        *tail;
    __u8        *end;
    // ... more fields
};
```

## 相关概念

- [[entities/linux/network/net-stack-deep-dive]] — Linux 网络栈深入分析
- [[entities/linux/network/net-stack-overview]] — 网络栈概览
- [[entities/linux/kernel/netfilter-hooks]] — Netfilter 钩子与 skbuff 交互
