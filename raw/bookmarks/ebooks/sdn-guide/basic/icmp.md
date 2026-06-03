# ICMP

## ICMP协议格式

ICMP消息在IP数据报内传输：`| IP Header | ICMP Message |`

ICMP消息格式：
- Type – ICMP类型
- Code – 给定类型的子类型
- Checksum – 错误检查数据
- Rest of Header – 四个字节字段

ICMP消息分为两类：查询消息和错误消息。

不生成ICMP错误消息的情况：
1. ICMP错误消息（但ICMP查询消息可能生成ICMP错误消息）
2. 目的地址为广播或多播的IP数据报
3. 链路层广播的数据包
4. 除第一个分片外的IP分片
5. 源地址为零地址、环回地址、广播地址或多播地址

## 地址掩码请求

无盘系统在启动期间获取子网掩码。

示例：
```
icmpush -mask -sp 10.2.3.4 -to 10.0.1.255
```

## 时间戳请求和响应

允许系统查询另一系统的当前时间，返回自午夜UTC以来的毫秒数。

## 端口不可达错误

有15种基于不同代码的ICMP错误消息。ICMP消息在主机之间交换，不像UDP那样使用目标端口号。

ICMP错误消息必须包括导致错误的数据报的IP头和紧随其后的至少前8个字节。

## ping

ping使用ICMP回显请求和回复实现。

示例：
```
ping -i 5 IP
ping 0
ping -c 5 google.com
ping -s 100 localhost
```

## traceroute

traceroute使用ICMP消息和IP头中的TTL字段。发送TTL递增的UDP数据报，从路由器接收ICMP超时消息，从最终目的地接收ICMP端口不可达消息。

## 图片

![ICMP图1](images/201210212111052571.jpg)
![ICMP图2](images/201210212111073278.jpg)
![ICMP图3](images/201210212111078196.jpg)
