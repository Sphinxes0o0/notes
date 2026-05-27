---
type: source
created: 2026-05-22
source-type: github
sources: [notes-tools]
tags: [tools, networking, security]
title: "工具使用笔记 (Tools Notes)"
author: "Sphinx"
date: 2025-02-16
size: small
path: raw/notes/tools/
summary: "Linux 网络抓包（tcpdump）、网络工具（netcat）、端口扫描（masscan/nmap）、系统管理（移除 Snap）实用指南"
---

# 工具使用笔记

## 核心内容

本来源包含 5 个工具使用笔记，涵盖以下主题：

| 文件 | 主题 | 概述 |
|------|------|------|
| tcpdump.md | 网络抓包 | BPF 过滤器语法、TCP 标志位分析、pcap 文件操作、Wireshark 配合 |
| netcat.md | 网络工具 | TCP/UDP 连接建立、端口扫描、文件/目录传输、远程 Shell、跳板登录 |
| port_scanner.md | 端口扫描 | masscan 高速异步扫描 + nmap 全面服务/漏洞检测，实战组合技 |
| remove_snap.md | 系统管理 | Ubuntu 22.04 完全移除 Snap：清理包、防止 apt 自动重装、替代方案 |
| index.md | 导航索引 | 工具笔记目录导航 |

### tcpdump

- 基于 libpcap，使用 BPF 过滤器语法
- 支持 TCP 标志位精细过滤（SYN/FIN/RST/SYN-ACK）
- 保存为 pcap 文件供 Wireshark 离线分析
- 性能优化：缓冲区、避免 DNS 解析、内核预过滤

### netcat

- "网络瑞士军刀"：TCP/UDP 连接、端口扫描、聊天、文件传输、远程 Shell
- 管道兼容性强（stdin/stdout），易于脚本化
- 支持 SOCKS4/5 和 HTTPS 代理
- 变种众多：ncat、socat、pnetcat

### masscan & nmap

- masscan：无状态异步扫描，自定义用户态 TCP/IP 栈，速率可达千万 pps
- nmap：功能最全面的扫描器，SYN/TCP/UDP/ACK 多种扫描类型，NSE 脚本引擎
- 最佳实践：masscan 快速发现 → nmap 精细探测

### 移除 Snap

- 完整流程：停止服务 → 移除 snap 包 → apt purge → 清理残留目录
- 防止重装：apt pinning（Pin-Priority: -10）或 apt-mark hold
- 替代方案：Flatpak、AppImage、传统 deb 包

## 相关页面

- [[entities/tools/linux-network-tools]] — tcpdump + netcat 网络诊断工具
- [[entities/tools/port-scanning]] — masscan + nmap 端口扫描
- [[entities/security]] — Masscan 在安全扫描中的角色
- [[kernel-net-index]] — 网络抓包依赖内核网络协议栈
