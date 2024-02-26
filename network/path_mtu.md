# Path MTU

> The Path MTU Discovery mechanism is specified in RFC 1191.

PMTU，Path MTU，以路由为单位，作为路由表的属性信息缓存于路由表。

PMTU发现机制，若网络设备收到超MTU IP报文且该IP报文不允许分片，则返回一个ICMP type 3 code 4报文;
将网络设备支持的MTU大小附在ICMP报文中，返回给报文源主机，由报文源主机调整该路径的PMTU。
该机制利用IP头部flags中的Don't fragment位，为1时表示不允许分片。

### IP报文不允许分片

#### 对于TCP报文
- 将通过PMTU发现机制，调整主机PMTU
- 通过快速重传机制，迅速恢复
- 主机调整TCP报文大小，以适应PMTU

#### 对于UDP报文
- 将通过PMTU发现机制，调整主机PMTU
- 丢弃该报文
- 后续传输时，对超过PMTU的报文，在主机处主动进行分片。
- 若有需要，超时重传、调整报文大小的机制由UDP的上层协议支持。

#### 对于其他IP报文（以ping报文为例）
- 将通过PMTU发现机制，调整主机PMTU
- 丢弃该报文
- 后续传输时，在主机处主动分片（以Linux为例）

### IP报文允许分片
- 主机已经调整PMTU，则分片在主机进行，业务可正常运行。
- 主机未调整PMTU，则分片在旁挂设备进行，将导致业务中断。

### 规避手段

规避目标：将分片的行为转移至主机上，不允许旁挂设备上进行任何分片行为。
方案：对所有超IP MTU送旁挂设备CPU的报文，皆返回ICMP type 3 code 4。需验证此规避对允许分片IP报文的影响。


#### Linux

- PMTU发现机制默认为IP_PMTUDISC_WANT，如果报文不超过PMTU，默认开启PMTU发现机制，如果报文超过PMTU，则主动在终端进行分片处理。
（will fragment a datagram if needed according to the path MTU, or will set the don’t-fragment flag otherwise.）

#### Windows

- TCP报文，默认不允许分片
- 其他报文，默认允许分片
- 对允许分片的报文，如果报文长度超过PMTU，则主动在终端处进行分片

不能假定网络上的所有的TCP报文都不允许分片（如新浪网，默认TCP报文允许分片）
