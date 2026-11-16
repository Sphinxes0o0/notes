---
type: index
tags: [tools, networking, security, system-administration]
created: 2026-05-22
---

# Tools — 开发与系统工具

> 网络诊断、端口扫描、系统管理工具实战笔记

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/tools/linux-network-tools]] | tcpdump 网络抓包 + netcat 网络瑞士军刀：BPF 过滤器、TCP 标志位分析、文件传输、远程 Shell | networking, tcpdump, netcat, linux |
| [[entities/tools/port-scanning]] | masscan 高速异步扫描 + nmap 全面服务/漏洞检测：实战组合技、场景速查表 | security, masscan, nmap, port-scanning |

## Cross-References

- [[entities/linux/kernel/index#networking]] — tcpdump 抓包和端口扫描依赖内核网络协议栈（Socket/sk_buff/TCP）
- [[entities/security]] — masscan 架构分析（无状态扫描、BlackRock 随机化、SYN Cookie）在安全领域深度应用
- [[sys-prog-index]] — 安全工具属于系统编程中 security 子域
- [[os-index]] — netcat 的 socket 编程是 OS I/O 模型的核心概念
- [[cpp-index]] — masscan 使用 C 语言实现无状态用户态协议栈

## Sources

| Source | Description | Date |
|--------|-------------|------|
| [[sources/notes-tools]] | 工具使用笔记：tcpdump + netcat + masscan/nmap + 移除 Snap | 2026-05-22 |
