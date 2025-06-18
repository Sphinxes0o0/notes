# Linux 的流量控制子系统（Traffic Control, TC）

## 核心概念：

- queueing discipline (qdisc)：排队规则，根据某种算法完成限速、整形等功能
- class：用户定义的流量类别
- classifier (也称为 filter)：分类器，分类规则
- action：要对包执行什么动作

组合以上概念，下面是对某个网络设备上的流量进行分类和限速时，所需完成的大致步骤：

1. 为网络设备创建一个 qdisc。
- qdisc 是一个整流器/整形器（shaper），可以包含多个 class，不同 class 可以应用不同的策略。
- qdisc 需要附着（attach）到某个网络接口（network interface），及流量方向（ingress or egress）。

2. 创建流量类别（class），并 attach 到 qdisc。
- 例如，根据带宽分类，创建高、中、低三个类别。

3. 创建 filter（classifier），并 attach 到 qdisc。

filters 用于对网络设备上的流量进行分类，并将包分发（dispatch）到前面定义的不同 class。

filter 会对每个包进行过滤，返回下列值之一：

- 0：表示 mismatch。如果后面还有其他 filters，则继续对这个包应用下一个 filter。
- -1：表示这个 filter 上配置的默认 classid。
- 其他值：表示一个 classid。系统接下来应该将包送往这个指定的 class。可以看到，通过这种方式可以实现非线性分类（non-linear classification）。

4. 可以给 filter 添加 action。例如，将选中的包丢弃（drop），或者将流量镜像到另一个网络设备等等。

5. 除此之外，qdisc 和 class 还可以循环嵌套，即： class 里加入新 qdisc，然后新 qdisc 里又可以继续添加新 class， 最终形成的是一个以 root qdisc 为根的树。

### 队列（Queues）和排队规则（Queueing Disciplines）

通过对数据包进行排队（queuing），可以决定数据的发送方式。

这里非常重要的一点是：`只能对发送数据（transmit）进行整形（shape the data）`。TCP/IP 无法提前知道两台主机之间的网络带宽，因此开始时它会以越来越快的速度发送数据（慢启 动），直到开始出现丢包，这时它知道已经没有可用空间来存储这些待发送的包了，因此就会 降低发送速度。

如果内网有一台路由器，希望限制某几台主机的下载速度，那首先应该找到主机直连的路由器接口，然后在这些接口上做出向流量整形（traffic shaping，整流）。 
此外，还要确保链路瓶颈（bottleneck of the link）也在你的控制范围内。例如， 如果网卡是 100Mbps，但路由器的链路带宽是 256Kbps，那首先应该确保不要发送过多数据 给路由器，因为它扛不住。否则，链路控制和带宽整形的决定权就不在主机侧而到路由器侧了。 
要达到限速目的，需要对“发送队列”有完全的把控， 这里的“发送队列”也就是整条链路上最慢的一段（slowest link in the chain）。 

### Simple, classless qdisc（简单、不分类排队规则）
如前所述，排队规则（queueing disciplines）改变了数据的发送方式。

不分类（或称无类别）排队规则（classless queueing disciplines）可以对某个网络 接口（interface）上的所有流量进行无差别整形。包括对数据进行：

- 重新调度（reschedule）
- 增加延迟（delay）
- 丢弃（drop）

与 classless qdisc 对应的是 classful qdisc，即有类别（或称分类别）排队规则，后者是一个排队规则中又包含其他 排队规则（qdisc-containing-qdiscs）！

目前最常用的 classless qdisc 是 pfifo_fast，这也是很多系统上的 默认排队规则。
> 这些高级功能本质上来说，它们 不过是“另一个队列”而已（nothing more than ‘just another queue’）。

#### pfifo_fast（先入先出队列）
![alt text](https://arthurchiao.art/assets/img/lartc-qdisc/pfifo_fast-qdisc.png)

pfifo_fast 有三个所谓的 “band”（可理解为三个队列），编号分别为 0、1、2：

- 每个 band 上分别执行 FIFO 规则。
- 如果 band 0 有数据，就不会处理 band 1；同理，band 1 有数据时，不会去处理 band 2。
- 内核会检查数据包的 TOS 字段，将“最小延迟”的包放到 band 0。

不要将 pfifo_fast qdisc 与后面介绍的 PRIO qdisc 混淆，后者是 classful 的！ 虽然二者行为类似，但 pfifo_fast 是无类别的，这意味无法用 tc 命令向 pfifo_fast 内添加另一个 qdisc。

#### 参数与用法
pfifo_fast qdisc 默认配置是写死的（the hardwired default），因此无法更改。

下面介绍这份写死的配置是什么样的。

- priomap

priomap 决定了如何将内核设置的 packet priority 映射到 band。priority 位于包的 TOS 字段：
```
     0     1     2     3     4     5     6     7
  +-----+-----+-----+-----+-----+-----+-----+-----+
  |                 |                       |     |
  |   PRECEDENCE    |          TOS          | MBZ |
  |                 |                       |     |
  +-----+-----+-----+-----+-----+-----+-----+-----+
```
TOS 字段占用 4 个比特，各 bit 含义如下：
```
  Binary Decimcal  Meaning
  -----------------------------------------
  1000   8         Minimize delay (md)
  0100   4         Maximize throughput (mt)
  0010   2         Maximize reliability (mr)
  0001   1         Minimize monetary cost (mmc)
  0000   0         Normal Service
```

tcpdump -vv 会打印包的 TOS 字段，其中的 TOS 值对应下面的第一列：
```
  TOS     Bits  Means                    Linux Priority    Band
  ------------------------------------------------------------
  0x0     0     Normal Service           0 Best Effort     1
  0x2     1     Minimize Monetary Cost   1 Filler          2
  0x4     2     Maximize Reliability     0 Best Effort     1
  0x6     3     mmc+mr                   0 Best Effort     1
  0x8     4     Maximize Throughput      2 Bulk            2
  0xa     5     mmc+mt                   2 Bulk            2
  0xc     6     mr+mt                    2 Bulk            2
  0xe     7     mmc+mr+mt                2 Bulk            2
  0x10    8     Minimize Delay           6 Interactive     0
  0x12    9     mmc+md                   6 Interactive     0
  0x14    10    mr+md                    6 Interactive     0
  0x16    11    mmc+mr+md                6 Interactive     0
  0x18    12    mt+md                    4 Int. Bulk       1
  0x1a    13    mmc+mt+md                4 Int. Bulk       1
  0x1c    14    mr+mt+md                 4 Int. Bulk       1
  0x1e    15    mmc+mr+mt+md             4 Int. Bulk       1
```
第二列是对应的十进制表示，第三列是对应的含义。例如，15 表示这个包期望 Minimal Monetary Cost + Maximum Reliability + Maximum Throughput + Minimum Delay。第四列是对应到 Linux 内核的优先级；最后一列是映射到的 band， 从命令行输出看，形式为：
```
  1, 2, 2, 2, 1, 2, 0, 0 , 1, 1, 1, 1, 1, 1, 1, 1
```

例如，priority 4 会映射到 band 1。priomap 还能列出 priority > 7 的那些 不是由 TOS 映射、而是由其他方式设置的优先级。例如，下表列出了应 用（application）是如何设置它们的 TOS 字段的，来自 RFC 1349（更多信息可阅 读全文），
```
  TELNET                   1000           (minimize delay)
  FTP     Control          1000           (minimize delay)
          Data             0100           (maximize throughput)

  TFTP                     1000           (minimize delay)

  SMTP    Command phase    1000           (minimize delay)
          DATA phase       0100           (maximize throughput)

  DNS     UDP Query        1000           (minimize delay)
          TCP Query        0000
          Zone Transfer    0100           (maximize throughput)

  NNTP                     0001           (minimize monetary cost)

  ICMP    Errors           0000
          Requests         0000 (mostly)
          Responses        <same as request> (mostly)
```

- txqueuelen

发送队列长度，是一个网络接口（interface）参数，可以用 ifconfig 命令设置。例 如，ifconfig eth0 txqueuelen 10。

tc 命令无法修改这个值。

