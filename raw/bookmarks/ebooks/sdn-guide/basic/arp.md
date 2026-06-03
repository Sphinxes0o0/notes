# ARP

## ARP概述

ARP (Address Resolution Protocol) 将32位IP地址映射到48位以太网硬件地址。RARP执行反向映射，通常用于无盘系统。

## ARP缓存

每个主机维护ARP缓存，条目通常保留20分钟，未完成的条目3分钟后过期。`arp -a`命令显示当前缓存条目。

管理ARP缓存的命令：
- `arp` - 显示当前ARP缓存
- `arp -s ip mac` - 添加静态ARP记录
- `arp -f` - 从/etc/ethers应用静态ARP记录

## ARP包格式

- 帧类型: 0x0806
- 硬件类型: 1 (以太网)
- 协议类型: 0x800 (IP)
- 硬件地址长度: 6
- 协议地址长度: 4
- 操作码: 1=ARP请求, 2=ARP应答, 3=RARP请求, 4=RARP应答

## ARP代理

两个网络之间的路由器响应不同网络的ARP请求，实现通信同时隐藏物理网络细节。

## 免费ARP (Gratuitous ARP)

主机发送自己IP地址的ARP请求，用于检测冲突和MAC地址更改时更新缓存。

## RARP

用于无盘系统使用硬件地址获取IP地址。使用链路层广播，路由器不转发。

## 示例 (tcpdump输出)

```
21:08:10.329163 00:16:3e:01:79:43 > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806), length 42: Request who-has 192.168.14.23 tell 192.168.13.43
21:08:10.329626 00:16:3e:01:7b:17 > 00:16:3e:01:79:43, ethertype ARP (0x0806), length 60: Reply 192.168.14.23 is-at 00:16:3e:01:7b:17
```

## 图片

![ARP包格式图](images/201210212059568914.jpg)
