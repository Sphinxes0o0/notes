---
type: source
source-type: github
title: "计算机网络基础 (Network Fundamentals)"
author: "notes repo"
date: 2026-05-20
size: medium
path: raw/github/notes/network_fundamentals/
summary: "计算机网络课程笔记：TCP/UDP协议、IP协议、Socket编程、HTTP/DNS、网络安全"
tags: [linux-kernel, networking]
created: 2026-05-20
---

# 计算机网络基础 (Network Fundamentals)

## 来源信息

- **路径**: raw/github/notes/network_fundamentals/
- **文件数**: 21个lecture + 5个模块解答
- **类型**: 课程笔记（Markdown格式）

## 核心内容

课程涵盖计算机网络核心概念：
- 网络分层模型：五层TCP/IP模型
- 多路复用：传输层和网络层多路复用
- TCP协议：三次握手/四次挥手、滑动窗口、粘包处理
- UDP协议：无连接、低延迟、适合实时场景
- IP协议：IPv4/IPv6、子网掩码、寻址与路由
- Socket编程：epoll红黑树、BIO/NIO/AIO模型
- HTTP协议：强制缓存/协商缓存
- DNS：记录类型、解析过程
- CDN：回源机制
- 网络安全：对称/非对称加密、TLS/SSL、中间人攻击

## 关键引用

> TCP三次握手确认双方发送和接收能力都正常，四次挥手因全双工需分别关闭。

> epoll在高并发下比select/poll快，因为内核使用红黑树管理fd，线程被动等待事件通知。

## 相关页面
- [[synthesis/topic-network-fundamentals]] — 综合分析
- [[sources/notes-os-fundamentals]]
