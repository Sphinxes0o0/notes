# 流量控制 (Traffic Control)

流量控制（Traffic Control， tc）是Linux内核提供的流量限速、整形和策略控制机制。它以`qdisc-class-filter`的树形结构来实现对流量的分层控制。

## 基本组成

tc由qdisc、filter和class三部分组成：
- qdisc通过队列将数据包缓存，用来控制网络收发的速度
- class用来表示控制策略
- filter用来将数据包划分到具体的控制策略中

## qdisc类型

- 无分类qdisc：pfifo_fast、red、sfq、tbf等
- 有分类qdisc：cbq、htb、prio等

ingress qdisc有诸多限制，通常借助ifb内核模块进行ingress方向流量控制。

## 图片

![tc示例1](images/tc1.jpeg)
![tc示例2](images/tc2.jpeg)
![htb-class](images/htb-class.png)
![ifb示例](images/ifb.jpeg)

## htb示例

代码示例展示如何添加qdisc、class和filter来控制特定IP（如192.168.0.9）的流量，限制为3mbit。

## ifb示例

代码示例展示如何使用ifb设备重定向ingress流量并进行整形控制。

## 参考文档

- Linux Traffic Control HOWTO
- ifb wiki
- Linux TC框架原理解析
