---
title: tcpdump 使用指南
---

# tcpdump

tcpdump 是一个功能强大的命令行网络抓包工具, 广泛应用于网络故障诊断、安全审计和协议分析等场景。它基于 libpcap 库实现, 能够捕获和分析网络流量, 是网络工程师和安全研究人员必备的工具之一。

## 基础用法

### 抓包命令格式

tcpdump 的基本命令格式如下:

```bash
tcpdump [选项] [表达式]
```

### 常用选项

- `-i interface`: 指定监听的网络接口, 如 `-i eth0`, 使用 `-i any` 监听所有接口
- `-n`: 不进行 DNS 解析, 直接显示 IP 地址, 避免 DNS 查询带来的延迟
- `-nn`: 不解析主机名和端口名, 显示数字形式的地址和端口
- `-v`: 输出更详细的信息, 包括 TTL、 TOS 等
- `-vv`: 更详细的输出
- `-c count`: 捕获指定数量的数据包后退出
- `-w file`: 将抓取的包保存为 pcap 格式文件, 供后续分析
- `-r file`: 从 pcap 文件读取数据包进行离线分析
- `-e`: 显示数据链路层 (MAC) 头部信息
- `-x`: 以十六进制格式显示数据包内容
- `-xx`: 以十六进制格式显示数据包内容, 包括链路层头部
- `-X`: 同时以十六进制和 ASCII 格式显示数据包内容
- `-XX`: 同时以十六进制和 ASCII 格式显示数据包内容, 包括链路层头部

常用选项示例:

```bash
# 监听 eth0 接口, 不解析 DNS
tcpdump -i eth0 -n

# 监听所有接口, 显示详细输出
tcpdump -i any -vv

# 捕获 100 个数据包后退出
tcpdump -i eth0 -c 100

# 保存为 pcap 文件
tcpdump -i eth0 -w capture.pcap

# 读取 pcap 文件
tcpdump -r capture.pcap
```

### 基本表达式

tcpdump 使用 BPF (Berkeley Packet Filter) 语法, 表达式用于过滤特定的数据包。表达式可以是协议类型、主机地址、端口号等。

```bash
# 抓取 TCP 包
tcpdump -i eth0 tcp

# 抓取 UDP 包
tcpdump -i eth0 udp

# 抓取 ICMP 包
tcpdump -i eth0 icmp

# 抓取特定主机的数据包
tcpdump -i eth0 host 192.168.1.100

# 抓取来源或目标是特定主机的数据包
tcpdump -i eth0 host 192.168.1.100
```

## 过滤器表达式

tcpdump 的过滤器表达式是其核心功能之一, 通过组合不同的过滤条件, 可以精准地捕获所需的网络流量。

### 协议过滤

通过协议类型进行过滤:

```bash
# 只抓 TCP 包
tcpdump -i eth0 tcp

# 只抓 UDP 包
tcpdump -i eth0 udp

# 只抓 ICMP 包
tcpdump -i eth0 icmp

# 只抓 ARP 包
tcpdump -i eth0 arp

# 只抓 IP 包
tcpdump -i eth0 ip
```

### 主机过滤

通过 IP 地址进行过滤:

```bash
# 抓取与特定主机相关的所有数据包
tcpdump -i eth0 host 192.168.1.100

# 抓取来自特定主机的数据包 (src)
tcpdump -i eth0 src host 192.168.1.100

# 抓取发往特定主机的数据包 (dst)
tcpdump -i eth0 dst host 192.168.1.100

# 抓取来自特定网段的数据包
tcpdump -i eth0 src net 192.168.1.0/24

# 抓取发往特定网段的数据包
tcpdump -i eth0 dst net 192.168.1.0/24
```

### 端口过滤

通过端口号进行过滤:

```bash
# 抓取特定端口的数据包
tcpdump -i eth0 port 80

# 抓取来源或目的端口为 80 的数据包
tcpdump -i eth0 port 80

# 抓取来源端口为 80 的数据包
tcpdump -i eth0 src port 80

# 抓取目的端口为 80 的数据包
tcpdump -i eth0 dst port 80

# 抓取端口范围内的数据包
tcpdump -i eth0 portrange 8000-9000
```

### 逻辑运算符

使用逻辑运算符组合多个过滤条件:

```bash
# and (或者使用 &&): 两个条件同时满足
tcpdump -i eth0 host 192.168.1.100 and port 80
tcpdump -i eth0 'host 192.168.1.100 && port 80'

# or (或者使用 ||): 任意一个条件满足
tcpdump -i eth0 tcp or udp
tcpdump -i eth0 'host 192.168.1.100 or host 192.168.1.200'

# not (或者使用 !): 条件取反
tcpdump -i eth0 not port 22
tcpdump -i eth0 '! port 22'

# 组合使用
tcpdump -i eth0 'host 192.168.1.100 and (port 80 or port 443)'

# 复杂组合
tcpdump -i eth0 'tcp and ((host 192.168.1.100 and port 80) or (host 192.168.1.200 and port 443))'
```

## 常用抓包场景

### 抓取 HTTP 流量

```bash
# 抓取 HTTP 流量 (80 端口)
tcpdump -i eth0 port 80

# 抓取 HTTP 请求头信息
tcpdump -i eth0 -nn -tttt port 80

# 抓取特定主机的 HTTP 流量
tcpdump -i eth0 -nn host 192.168.1.100 and port 80

# 抓取 HTTP 请求和响应
tcpdump -i eth0 -A 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
```

### 抓取 TCP SYN/FIN/RST 包

使用 tcpflags 过滤器抓取特殊的 TCP 控制报文:

```bash
# 抓取 SYN 包 (连接建立)
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# 抓取 FIN 包 (连接关闭)
tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'

# 抓取 RST 包 (连接重置)
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'

# 抓取 SYN-ACK 包
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-ack) != 0'

# 抓取所有 TCP 控制报文 (排除 ACK)
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-fin|tcp-rst) != 0'
```

### 抓取特定端口数据

```bash
# 抓取 SSH 连接 (22 端口)
tcpdump -i eth0 port 22

# 抓取 DNS 查询 (53 端口)
tcpdump -i eth0 port 53

# 抓取 FTP 数据 (21 端口控制, 20 端口数据)
tcpdump -i eth0 port 21

# 抓取 SMTP 邮件 (25 端口)
tcpdump -i eth0 port 25

# 抓取 MySQL 数据库 (3306 端口)
tcpdump -i eth0 port 3306

# 抓取 Redis (6379 端口)
tcpdump -i eth0 port 6379
```

### 保存和读取 pcap 文件

```bash
# 保存抓包结果到文件
tcpdump -i eth0 -w capture.pcap

# 保存特定条件的抓包结果
tcpdump -i eth0 -w capture.pcap host 192.168.1.100 and port 80

# 读取 pcap 文件
tcpdump -r capture.pcap

# 读取并显示详细信息
tcpdump -r capture.pcap -vv

# 读取并应用过滤器
tcpdump -r capture.pcap 'tcp port 80'

# 保存多个文件, 每个文件 100MB
tcpdump -i eth0 -W 10 -C 100 -w capture.pcap

# 按包数量轮转文件
tcpdump -i eth0 -W 5 -C 100 -w capture.pcap
```

## 输出格式解析

tcpdump 的输出包含丰富的信息, 理解这些信息对于分析网络问题至关重要。

### 包头信息

典型的 tcpdump 输出格式:

```
12:34:56.789012 IP 192.168.1.100.443 > 192.168.1.200.52345: Flags [P.], seq 1:100, ack 1, win 502, length 99
```

各字段含义:
- `12:34:56.789012`: 时间戳 (小时:分钟:秒.微秒)
- `IP`: 网络层协议
- `192.168.1.100.443`: 源 IP 和端口
- `>`: 数据流向符号
- `192.168.1.200.52345`: 目标 IP 和端口
- `Flags [P.]`: TCP 标志位
- `seq 1:100`: TCP 序列号
- `ack 1`: 确认号
- `win 502`: 窗口大小
- `length 99`: 数据载荷长度

### TCP 标志位说明

- `[S]`: SYN - 连接建立请求
- `[S.]`: SYN-ACK - SYN 响应
- `[P.]`: PUSH - 数据推送
- `[F]`: FIN - 连接关闭请求
- `[R]`: RST - 连接重置
- `[.]`: ACK - 确认
- `[P.] [.]`: PSH-ACK 组合

### 时间戳含义

```bash
# 默认时间戳格式
tcpdump -i eth0 port 80
# 输出: 12:34:56.789012 IP 192.168.1.100.80 > 192.168.1.200.52345: ...

# 人类可读时间戳 (-tttt)
tcpdump -i eth0 -tttt port 80
# 输出: 2024-01-15 12:34:56.789012 IP 192.168.1.100.80 > 192.168.1.200.52345: ...

# Unix 时间戳 (-t)
tcpdump -i eth0 -t port 80
# 输出: 1705312496 IP 192.168.1.100.80 > 192.168.1.200.52345: ...

# 不显示时间戳 (-t)
tcpdump -i eth0 -tt port 80
# 输出: IP 192.168.1.100.80 > 192.168.1.200.52345: ...
```

## 高级用法

### 表达式组合

```bash
# 抓取特定主机和端口组合
tcpdump -i eth0 'host 192.168.1.100 and port 80 and tcp'

# 排除特定端口
tcpdump -i eth0 'tcp and not port 22'

# 抓取特定网段但排除特定主机
tcpdump -i eth0 'net 192.168.1.0/24 and not host 192.168.1.50'

# 抓取长度大于特定值的包
tcpdump -i eth0 'ip[2:2] > 1000'

# 抓取 TCP 特定端口范围
tcpdump -i eth0 'tcp and (port 80 or port 443 or port 8080)'

# 抓取 ICMP 特定类型 (ping 请求/响应)
tcpdump -i eth0 'icmp and (icmp[0] = 8 or icmp[0] = 0)'
```

### 抓取特定标志位

tcpdump 支持通过 `tcpflags` 关键字和偏移量来抓取 TCP 标志位:

```bash
# TCP 头结构偏移量
# - tcp[0] & 0x12 提取标志位
# - 0x02 = SYN, 0x10 = ACK, 0x01 = FIN, 0x04 = RST

# 抓取 SYN 包
tcpdump -i eth0 'tcp[0] & 0x02 != 0'

# 抓取 RST 包
tcpdump -i eth0 'tcp[0] & 0x04 != 0'

# 抓取 SYN-ACK 包
tcpdump -i eth0 'tcp[0] = 0x12'

# 抓取只有 SYN 标志的包 (不含 ACK)
tcpdump -i eth0 'tcp[13] = 2'

# 抓取包含 RST 标志的包
tcpdump -i eth0 'tcp[13] & 4 != 0'

# tcpflags 关键字方式 (更易读)
tcpdump -i eth0 'tcpflags tcp-syn'
tcpdump -i eth0 'tcpflags tcp-rst'
tcpdump -i eth0 'tcpflags tcp-fin'
```

### 十六进制输出

```bash
# 十六进制输出 (-x)
tcpdump -i eth0 -x port 80
# 输出:
#     0x0000:  4500 0054 0011 4000 4006 1234 0a00 000f
#     0x0010:  0a00 000a c1a8 0050 8c9a 7b5a 1f8e a9cc

# 十六进制输出包含链路层 (-xx)
tcpdump -i eth0 -xx port 80

# 十六进制+ASCII 输出 (-X)
tcpdump -i eth0 -X port 80
# 输出:
#     0x0000:  4500 0054 0011 4000 4006 1234 0a00 000f  E..T..@.@.......
#     0x0010:  0a00 000a c1a8 0050 8c9a 7b5a 1f8e a9cc  .......P..{[....

# 十六进制+ASCII 输出包含链路层 (-XX)
tcpdump -i eth0 -XX port 80

# 完整十六进制输出查看包内容
tcpdump -i eth0 -nn -XX 'tcp port 80 and tcp[32:4] = 0x47455420'
# 0x47455420 = "GET " ASCII
```

### 其他高级选项

```bash
# 监听特定 VLAN 的流量
tcpdump -i eth0 vlan 100

# 监听 IPv6 流量
tcpdump -i eth0 ip6

# 显示相对序列号 (相对于 TCP 握手)
tcpdump -i eth0 -S port 80

# 打印包过滤代码
tcpdump -i eth0 -d 'tcp and port 80'

# 打印编译后的 BPF 代码
tcpdump -i eth0 -dd 'tcp and port 80'

# 设置快照长度 (snaplen)
tcpdump -i eth0 -s 100 port 80

# 不截断输出 (完整抓取)
tcpdump -i eth0 -s 0 port 80
```

## 与 Wireshark 配合

tcpdump 和 Wireshark 是网络分析的双剑合璧。tcpdump 负责高效抓包, Wireshark 负责深度分析。

### 工作流程

```bash
# 1. 在服务器或路由器上使用 tcpdump 抓包
# 优点: 资源占用少, 可远程抓包, 保存完整数据

# 抓取特定条件的包并保存
tcpdump -i eth0 -s 0 -w /tmp/capture.pcap 'host 192.168.1.100 and port 80'

# 后台持续抓取, 每小时轮转一次
tcpdump -i eth0 -s 0 -G 3600 -w /tmp/capture_%H.pcap 'tcp'

# 按文件大小轮转 (每个文件 100MB)
tcpdump -i eth0 -s 0 -C 100 -w /tmp/capture.pcap

# 2. 将 pcap 文件传输到分析主机
scp user@remote:/tmp/capture.pcap /tmp/

# 3. 使用 Wireshark 图形界面分析
wireshark /tmp/capture.pcap

# 或者使用 tshark (命令行版 Wireshark) 分析
tshark -r /tmp/capture.pcap -Y 'http' | less

# 提取 HTTP 请求
tshark -r /tmp/capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

### tcpdump 与 tshark 配合

```bash
# 使用 tcpdump 预处理, 再用 tshark 分析
tcpdump -i eth0 -nn -c 1000 'tcp port 80' -w - | tshark -r - -Y 'http'

# 提取特定字段
tcpdump -i eth0 -nn -c 100 'tcp port 80' -w - | tshark -r - -T fields -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport
```

### 常见分析场景

```bash
# 分析 TCP 连接问题
tcpdump -i eth0 -nn -tttt 'tcp port 80' > tcpdump.txt
# 然后在 Wireshark 中:
# 1. 筛选 tcp.flags.syn == 1 查看 SYN 包
# 2. 筛选 tcp.flags.reset == 1 查看 RST 包
# 3. 查看专家信息 (Expert Information)

# 分析 HTTP/HTTPS 问题
tcpdump -i eth0 -nn -A 'tcp port 80 or tcp port 443' > http.txt
# 对于 HTTPS, 需要结合私钥解密
# openssl s_client -connect site:443 -key keyfile -cert certfile
```

## 性能优化

tcpdump 在高流量环境中可能丢包, 以下是一些优化建议:

```bash
# 使用缓冲区
tcpdump -i eth0 -B 4096 port 80

# 选择空闲接口
tcpdump -i eth0 -p  # 不进入混杂模式

# 缩短表达式
tcpdump -i eth0 -nn 'tcp port 80'

# 使用 -c 限制数量
tcpdump -i eth0 -nn -c 10000 'tcp port 80'

# 避免 DNS 解析
tcpdump -i eth0 -nn port 80

# 内核过滤 (早期过滤, 减少用户空间拷贝)
tcpdump -i eth0 -f 'tcp port 80'
```

## 注意事项

1. **权限**: 抓包通常需要 root 权限, 或者使用 `setcap` 授予 tcpdump 特定权限
2. **磁盘空间**: 长时间抓包会生成大文件, 注意监控磁盘使用
3. **性能影响**: 在高流量环境中抓包会影响网络性能
4. **隐私**: 抓包可能包含敏感信息, 确保数据安全
5. **法規**: 在某些场景下抓包可能涉及法律问题, 请确保合规使用

```bash
# 授予 tcpdump 永久抓包权限 (谨慎使用)
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```
