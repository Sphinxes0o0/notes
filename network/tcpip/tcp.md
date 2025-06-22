# TCP 协议详解

## 目录
- [TCP 概述](#tcp-概述)
- [TCP 报文格式](#tcp-报文格式)
- [连接管理](#连接管理)
  - [三次握手](#三次握手)
  - [四次挥手](#四次挥手)
  - [连接状态转换](#连接状态转换)
- [流量控制与拥塞控制](#流量控制与拥塞控制)
  - [滑动窗口](#滑动窗口)
  - [拥塞控制算法](#拥塞控制算法)
- [可靠性保证](#可靠性保证)
- [性能优化](#性能优化)
- [常见问题与故障排查](#常见问题与故障排查)

## TCP 概述

**传输控制协议（Transmission Control Protocol，TCP）** 是一种面向连接的、可靠的、基于字节流的传输层通信协议。

### TCP 特点

- **面向连接**：通信前需要建立连接，通信结束后释放连接
- **可靠传输**：通过序号、确认、重传机制保证数据可靠传输
- **流量控制**：通过滑动窗口机制防止发送方发送数据过快
- **拥塞控制**：根据网络状况动态调整发送速率
- **全双工通信**：连接建立后，双方可以同时发送和接收数据
- **面向字节流**：TCP把应用层传下来的数据看成无结构的字节流

## TCP 报文格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             data                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 主要字段说明

- **源端口/目的端口**：标识发送方和接收方的应用进程
- **序号（Sequence Number）**：本报文段数据的第一个字节在整个字节流中的序号
- **确认号（Acknowledgment Number）**：期望收到对方下一个报文段的第一个字节的序号
- **数据偏移**：TCP报文段的数据起始处距离TCP报文段的起始处有多远
- **控制位**：
  - **URG**：紧急指针有效
  - **ACK**：确认号有效
  - **PSH**：推送功能
  - **RST**：连接重置
  - **SYN**：同步序号，用于建立连接
  - **FIN**：发送端完成发送任务
- **窗口**：接收窗口大小，用于流量控制
- **校验和**：检验TCP报文段的完整性
- **紧急指针**：指出紧急数据的末尾在报文段中的位置

## 连接管理

### 三次握手
* 第一次握手：
client首先向server的TCP发送一个连接请求报文，这个特殊的报文不含应用层数据，其首部中同步位SYN被设置为1；
另外，会随机产生一个起始序号seq=x(连接请求报文不携带数据，但要消耗一个序号).

* 第二次握手：
server的收到TCP连接请求报文后，如果同意建立连接，就向client发回确认，并为该TCP连接分配TCP缓存和变量；
在回复报文中，SYN和ACK位都被设置为1，确认号字段值为ack=x+1,并且server随机产生起始序号seq=y. 确认包同样不包含应用层数据。

* 第三次握手：
当client收到确认报文后，向server给出确认，同时在自己的系统上为该连接分配缓存和变量；
这个报文的确认为ACK被设置为1，序号段被设置为seq=x+1,确认号字段ack=y+1. 该报文可以携带数据，如果不携带数据则不消耗序号。 
理想状态下，TCP连接一旦建立，在通信双方中的任何一方主动关闭连接之前，TCP 连接都将被一直保持下去。
因为TCP提供全双工通信，因此双方任何时候都可以发送数据。

### 四次挥手

* 第一次挥手：
client准备关闭连接，就向其TCP发送一个连接释放报文，并停止再发送数据，主动关闭TCP连接。
该报文的FIN标志位被设置为1，seq=u,它等于前面已经发送过的数据的最后一个字节的序号加1。

* 第二次挥手：
server收到连接释放报文后即发出确认，确认号是ack=u+1,序号为v,等于它前面已经发送过的数据的最后一个字节序号加1.
此时client到server这个方向的连接就释放了，TCP处于半关闭状态。ACK=1，seq=v,ack=u+1

* 第三次挥手：
若server已经没有要向client发送的数据，就通知TCP释放连接，此时发出FIN=1，确认号ack= u+1,序号seq =w,已经发送过的数据最后一个字节加1。
确认为ACK=1. (FIN = 1, ACK=1,seq = w, ack =u+1) 第四次挥手：client收到连接释放报文后，必须发出确认。
在确认报文中，确认位ACK=1，序号seq=u+1,确认号ack=w+1. 此时连接还没有释放掉，必须经过实践等待计时器设置的时间2MSL(Max Segment Lifetime)后，
client才进入连接关闭状态。

### 连接状态转换

TCP连接在其生命周期中会经历多个状态，主要状态包括：

#### 客户端状态转换
1. **CLOSED** → **SYN_SENT**：发送SYN报文
2. **SYN_SENT** → **ESTABLISHED**：收到SYN+ACK，发送ACK
3. **ESTABLISHED** → **FIN_WAIT_1**：发送FIN报文
4. **FIN_WAIT_1** → **FIN_WAIT_2**：收到ACK
5. **FIN_WAIT_2** → **TIME_WAIT**：收到FIN，发送ACK
6. **TIME_WAIT** → **CLOSED**：等待2MSL后关闭

#### 服务端状态转换
1. **CLOSED** → **LISTEN**：开始监听
2. **LISTEN** → **SYN_RCVD**：收到SYN，发送SYN+ACK
3. **SYN_RCVD** → **ESTABLISHED**：收到ACK
4. **ESTABLISHED** → **CLOSE_WAIT**：收到FIN，发送ACK
5. **CLOSE_WAIT** → **LAST_ACK**：发送FIN
6. **LAST_ACK** → **CLOSED**：收到ACK

```bash
# 查看TCP连接状态
netstat -an | grep tcp
ss -tuln  # 使用ss命令（推荐）
```

### 连接管理常见问题

#### 为什么需要三次握手，二次握手可以吗？

采用三次握手是为了防止失效的连接请求报文再次传到server，可能因此产生错误。

当网络波动时，假设客户端发送的连接请求正常到达服务方，服务方建立连接的应答未能到达客户端：
则客户方要重新发送连接请求，若采用二次握手，服务方收到客户端重传的请求连接后，会以为是新的请求，就会发送同意连接报文，并新开进程提供服务，这样会造成服务方资源的无谓浪费。

如果只采用一次的话，客户端不知道服务端是否已经收到自己发送的数据，则会不断地发送数据。

**三次握手的必要性**：
- 为了保证服务端能接收到客户端的信息并能做出正确的应答而进行前两次(第一次和第二次)握手
- 为了保证客户端能够接收到服务端的信息并能做出正确的应答而进行后两次(第二次和第三次)握手

#### 为什么主动方要等待2MSL后才关闭连接？

保证TCP协议的全双工连接能够可靠关闭。

主要为了确保对方能收到ACK，如果client直接CLOSED了，那么由于IP协议的不可靠性或其它网络原因，导致server没有收到client最后回复的ACK。

server在超时之后继续发送FIN，此时由于client已经CLOSED了，就找不到与重发的FIN对应的连接，server此时就会收到RST（而不是期待的ACK），系统会认为是连接错误把问题报告给上层。

所以，client不能直接进入CLOSED，而是保持2MSL的状态，如果这个时间内又收到了server的关闭请求时则马上重传，否则说明server已经收到确认包则可以关闭。

**2MSL等待的作用**：
- 确保最后一个ACK能够到达对方
- 防止"已失效的连接请求报文段"出现在本连接中

## 流量控制与拥塞控制

### 滑动窗口

TCP使用滑动窗口机制进行流量控制，确保发送方不会因为发送数据过快而超过接收方的处理能力。

**工作原理**：
- 接收方在TCP报文段中通告自己的接收窗口大小
- 发送方维护一个发送窗口，窗口大小不能超过接收方通告的接收窗口
- 随着数据的发送和确认，发送窗口在数据流上滑动
- 当接收方处理了缓冲区中的数据后，会在后续的确认报文中通告更大的窗口

**拥塞控制与流量控制的关系**：
- 流量控制解决的是发送方和接收方之间的速度匹配问题
- 拥塞控制解决的是发送方和网络之间的速度匹配问题  
- 实际的发送窗口 = min(拥塞窗口, 接收窗口)

### 拥塞控制算法

TCP使用多种拥塞控制策略来避免拥塞。具体来讲，TCP为每条连接维护一个"拥塞窗口"来限制可能在端对端间传输的未确认分组的总数量。在一个连接初始化或超时后使用一种"慢启动"机制来增加拥塞窗口的大小。

> "慢启动"，指的是初始值虽然比较低，但其增长极快：当每个分段得到确认时，拥塞窗口会增加一个MSS（Maximum segment size），使得在每次往返时间（Round-trip time，RTT）内拥塞窗口能高效地双倍增长。

许多年来，不同的流量控制算法已经在各种TCP堆栈中实现和使用。例如Cubic、Tahoe、Vegas、Reno、Westwood，以及最近流行的BBR等。
这些都是TCP中使用的不同拥塞控制算法。这些算法的作用是决定发送方应该以多快的速度发送数据，并同时适应网络的变化。

#### 传统算法对比

| 算法 | 特点 | 优势 | 劣势 |
|------|------|------|------|
| **Tahoe** | 慢启动 + 拥塞避免 | 简单稳定 | 恢复慢 |
| **Reno** | 快重传 + 快恢复 | 改进丢包恢复 | 多丢包性能差 |
| **Vegas** | 基于RTT变化 | 主动避免拥塞 | 与其他算法共存困难 |
| **Cubic** | 三次函数增长 | 高带宽网络友好 | 短流性能一般 |
| **BBR** | 基于带宽和RTT | 高吞吐低延迟 | 公平性待验证 |

#### Linux 上的拥塞控制算法

在Linux 下检查当前可用的拥塞算法可以使用如下命令：
```bash
$ sysctl net.ipv4.tcp_available_congestion_control
net.ipv4.tcp_available_congestion_control = reno cubic
```

了解当前使用了哪一种拥塞算法可以使用以下命令：
```bash
$ sysctl net.ipv4.tcp_congestion_control
net.ipv4.tcp_congestion_control = cubic
```

Cubic 是一种较为温和的拥塞算法，它使用三次函数作为其拥塞窗口的算法，并且使用函数拐点作为拥塞窗口的设置值。

> Linux内核在2.6.19后使用该算法作为默认TCP拥塞算法。今天所使用的绝大多数Linux 分发版本，例如Ubuntu、Amazon Linux 等均将Cubic作为缺省的 TCP流量控制的拥塞算法。

#### BBR 算法

TCP的BBR（Bottleneck Bandwidth and Round-trip propagation time，BBR）是谷歌在2016年开发的一种新型的TCP 拥塞控制算法。
在此以前，互联网主要使用基于丢包的拥塞控制策略，只依靠丢失数据包的迹象作为减缓发送速率的信号。

![BBR](https://s3.cn-north-1.amazonaws.com.cn/awschinablog/talking-about-network-optimization-from-the-flow1.gif)

**BBR 优点**：

可以获得显著的网络吞吐量的提升和延迟的降低。

- **吞吐量改善**：在远距离路径上尤为明显，比如跨太平洋的文件或者大数据的传输，尤其是在有轻微丢包的网络条件下
- **延迟改善**：主要体现在最后一公里的路径上，而这一路径经常受到缓冲膨胀（Bufferbloat）的影响

> 所谓"缓冲膨胀"指的网络设备或者系统不必要地设计了过大的缓冲区。当网络链路拥塞时，就会发生缓冲膨胀，从而导致数据包在这些超大缓冲区中长时间排队。
> 在先进先出队列系统中，过大的缓冲区会导致更长的队列和更高的延迟，并且不会提高网络吞吐量。由于BBR并不会试图填满缓冲区，所以在避免缓冲区膨胀方面往往会有更好的表现。
> 
> 验证参考： https://toonk.io/tcp-bbr-exploring-tcp-congestion-control/index.html

**BBR 实现**：项目地址：https://github.com/google/bbr/tree/master

#### 拥塞控制参数调优

```bash
# 查看当前拥塞控制算法
sysctl net.ipv4.tcp_congestion_control

# 修改拥塞控制算法
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

# 查看可用算法
sysctl net.ipv4.tcp_available_congestion_control

# 永久修改（添加到 /etc/sysctl.conf）
echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf
```

## 可靠性保证

### 可靠性机制

TCP通过以下机制保证数据传输的可靠性：

#### 1. 序号和确认机制
- **序号**：为每个字节分配序号，确保数据按序到达
- **确认**：接收方通过ACK确认已收到的数据
- **累积确认**：确认号表示期望收到的下一个字节序号

#### 2. 重传机制
- **超时重传**：发送方设置重传定时器，超时未收到ACK则重传
- **快速重传**：收到3个重复ACK时立即重传
- **选择性重传（SACK）**：只重传丢失的数据段

#### 3. 流量控制
- **接收窗口**：接收方通告可接收的数据量
- **零窗口探测**：接收窗口为0时的处理机制

#### 4. 连接管理
- **三次握手**：确保连接建立的可靠性
- **四次挥手**：确保连接释放的可靠性

### 重传超时（RTO）计算

TCP使用自适应重传超时机制：

```
SRTT = (1-α) × SRTT + α × RTT
RTTVAR = (1-β) × RTTVAR + β × |RTT - SRTT|
RTO = SRTT + 4 × RTTVAR
```

其中：
- **SRTT**：平滑往返时间
- **RTTVAR**：往返时间变化
- **α = 1/8，β = 1/4**

### TCP与UDP对比

在TCP的连接中，数据流必须以正确的顺序送达对方。TCP的可靠性是通过顺序编号和确认（ACK）来实现的。TCP在开始传送一个段时，为准备重传而首先将该段插入到发送队列之中，同时启动时钟。

其后，如果收到了接收端对该段的ACK信息，就将该段从队列中删去。如果在时钟规定的时间内，ACK未返回，那么就从发送队列中再次送出这个段。

**TCP在协议中就对数据可靠传输做了保障**：
- 握手与断开都需要通讯双方确认
- 数据传输也需要双方确认成功
- 在协议中还规定了：分包、重组、重传等规则

**而UDP主要是面向不可靠连接的**，不能保证数据正确到达目的地。

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接性 | 面向连接 | 无连接 |
| 可靠性 | 可靠传输 | 不可靠传输 |
| 效率 | 开销大，速度慢 | 开销小，速度快 |
| 数据边界 | 面向字节流 | 面向报文 |
| 适用场景 | 要求可靠性的应用 | 要求效率的应用 |

## 性能优化

### 系统参数优化

#### 内核参数调优

```bash
# TCP缓冲区大小
net.core.rmem_max = 16777216          # 最大接收缓冲区
net.core.wmem_max = 16777216          # 最大发送缓冲区
net.ipv4.tcp_rmem = 4096 65536 16777216   # TCP接收缓冲区
net.ipv4.tcp_wmem = 4096 65536 16777216   # TCP发送缓冲区

# TCP连接参数
net.ipv4.tcp_fin_timeout = 30        # FIN_WAIT_2状态超时时间
net.ipv4.tcp_keepalive_time = 1200   # keepalive探测间隔
net.ipv4.tcp_max_syn_backlog = 8192  # SYN队列长度

# TCP优化选项
net.ipv4.tcp_window_scaling = 1      # 启用窗口缩放
net.ipv4.tcp_timestamps = 1          # 启用时间戳
net.ipv4.tcp_sack = 1               # 启用选择性确认
```

#### 应用层优化

```bash
# 启用TCP Fast Open
net.ipv4.tcp_fastopen = 3

# 调整TCP拥塞控制
net.ipv4.tcp_congestion_control = bbr

# 优化TIME_WAIT状态
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 0  # 注意：新版本内核已移除
```

### 编程优化建议

#### Socket选项设置

```c
// 启用Nagle算法控制
int flag = 1;
setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

// 设置接收缓冲区大小
int rcvbuf = 65536;
setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

// 设置发送缓冲区大小
int sndbuf = 65536;
setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));

// 启用地址重用
int reuse = 1;
setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
```

## 常见问题与故障排查

### 连接问题

#### 1. 连接超时
**现象**：连接建立缓慢或失败
**原因**：
- 网络延迟过高
- 防火墙阻拦
- 服务端负载过高

**排查方法**：
```bash
# 测试连接性
telnet target_host target_port
nc -zv target_host target_port

# 查看路由和延迟
traceroute target_host
ping target_host

# 检查防火墙
iptables -L -n
firewall-cmd --list-all
```

#### 2. 连接重置（Connection Reset）
**现象**：收到RST包，连接被重置
**原因**：
- 服务端程序崩溃
- 防火墙策略
- 连接队列满

**排查方法**：
```bash
# 监控RST包
tcpdump -i any 'tcp[tcpflags] & tcp-rst != 0'

# 查看连接状态统计
ss -s
netstat -s | grep -i reset
```

### 性能问题

#### 1. 吞吐量低
**可能原因**：
- 窗口大小限制
- 拥塞控制算法不适合
- 网络带宽限制

**优化方案**：
```bash
# 检查窗口缩放
sysctl net.ipv4.tcp_window_scaling

# 调整拥塞控制算法
sysctl -w net.ipv4.tcp_congestion_control=bbr

# 增大缓冲区
sysctl -w net.core.rmem_max=16777216
```

#### 2. 延迟高
**可能原因**：
- Nagle算法延迟
- 缓冲膨胀
- 网络拥塞

**优化方案**：
```bash
# 禁用Nagle算法（应用层）
setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

# 使用BBR算法减少缓冲膨胀
sysctl -w net.ipv4.tcp_congestion_control=bbr
```

### 监控和调试工具

#### 网络抓包分析
```bash
# 抓取TCP包
tcpdump -i eth0 -w tcp_capture.pcap 'tcp port 80'

# 使用Wireshark分析
wireshark tcp_capture.pcap

# 实时监控连接
watch -n 1 'ss -tuln'
```

#### 系统监控
```bash
# 查看TCP统计信息
cat /proc/net/tcp
ss -i  # 显示详细信息

# 监控网络流量
iftop
nload
```

#### 应用层调试
```bash
# 启用TCP调试日志
echo 1 > /proc/sys/net/ipv4/tcp_debug

# 查看socket信息
lsof -i tcp:port
```

### 常用排查命令总结

```bash
# 连接状态查看
ss -tuln                    # 查看监听端口
ss -tulpn                   # 显示进程信息
netstat -an | grep tcp      # 传统方式

# 网络测试
ping host                   # 测试连通性
telnet host port           # 测试端口
nc -zv host port           # 端口扫描

# 流量监控
iftop                      # 实时流量
nload                      # 网络负载
tcpdump                    # 包捕获

# 系统参数
sysctl -a | grep tcp       # TCP相关参数
cat /proc/net/tcp          # TCP连接信息
```

---

## 参考资料

- [RFC 793 - Transmission Control Protocol](https://tools.ietf.org/html/rfc793)
- [RFC 5681 - TCP Congestion Control](https://tools.ietf.org/html/rfc5681)
- [TCP BBR 项目](https://github.com/google/bbr)
- [Linux TCP 性能调优](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt)

