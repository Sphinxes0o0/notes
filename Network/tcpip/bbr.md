# TCP 拥塞控制

TCP使用多种拥塞控制策略来避免拥塞。具体来讲，TCP为每条连接维护一个“拥塞窗口”来限制可能在端对端间传输的未确认分组的总数量。在一个连接初始化或超时后使用一种“慢启动”机制来增加拥塞窗口的大小。
> “慢启动”，指的是初始值虽然比较低，但其增长极快：当每个分段得到确认时，拥塞窗口会增加一个MSS（Maximum segment size），使得在每次往返时间（Round-trip time，RTT）内拥塞窗口能高效地双倍增长。


许多年来，不同的流量控制算法已经在各种TCP堆栈中实现和使用。例如Cubic、Tahoe、Vegas、Reno、Westwood，以及最近流行的BBR等。
这些都是TCP中使用的不同拥塞控制算法。这些算法的作用是决定发送方应该以多快的速度发送数据，并同时适应网络的变化。

## Linux 上的情况
在Linux 下检查当前可用的拥塞算法可以使用如下命令：
```
$ sysctl net.ipv4.tcp_available_congestion_control
net.ipv4.tcp_available_congestion_control = reno cubic
```
了解当前使用了哪一种拥塞算法可以使用以下命令：
```
$ sysctl net.ipv4.tcp_congestion_control
net.ipv4.tcp_congestion_control = cubic
```

Cubic 是一种较为温和的拥塞算法，它使用三次函数作为其拥塞窗口的算法，并且使用函数拐点作为拥塞窗口的设置值。
> Linux内核在2.6.19后使用该算法作为默认TCP拥塞算法。今天所使用的绝大多数Linux 分发版本，例如Ubuntu、Amazon Linux 等均将Cubic作为缺省的 TCP流量控制的拥塞算法。

## BBR 
TCP的BBR（Bottleneck Bandwidth and Round-trip propagation time，BBR）是谷歌在2016年开发的一种新型的TCP 拥塞控制算法。
在此以前，互联网主要使用基于丢包的拥塞控制策略，只依靠丢失数据包的迹象作为减缓发送速率的信号。

![BBR](https://s3.cn-north-1.amazonaws.com.cn/awschinablog/talking-about-network-optimization-from-the-flow1.gif)

### BBR 优点
可以获得显著的网络吞吐量的提升和延迟的降低。
吞吐量的改善在远距离路径上尤为明显，比如跨太平洋的文件或者大数据的传输，尤其是在有轻微丢包的网络条件下。
延迟的改善主要体现在最后一公里的路径上，而这一路径经常受到缓冲膨胀（Bufferbloat）的影响。
> 所谓“缓冲膨胀”指的网络设备或者系统不必要地设计了过大的缓冲区。当网络链路拥塞时，就会发生缓冲膨胀，从而导致数据包在这些超大缓冲区中长时间排队。
> 在先进先出队列系统中，过大的缓冲区会导致更长的队列和更高的延迟，并且不会提高网络吞吐量。由于BBR并不会试图填满缓冲区，所以在避免缓冲区膨胀方面往往会有更好的表现。
> 验证： https://toonk.io/tcp-bbr-exploring-tcp-congestion-control/index.html

### 实现

https://github.com/google/bbr/tree/master

