# OVS介绍

## 概述

Open vSwitch (OVS) 是一个开源的、多层虚拟交换机，广泛用于SDN环境中。它支持OpenFlow协议，可用于网络虚拟化和隧道协议。

## 组件

- ovs-vswitchd: 主用户空间守护进程
- ovsdb-server: 配置数据库
- openvswitch.ko: 内核模块

## 常用命令

```bash
# 查看版本
ovs-vsctl show

# 创建网桥
ovs-vsctl add-br br0

# 添加端口
ovs-vsctl add-port br0 eth0

# 设置控制器
ovs-vsctl set-controller br0 tcp:192.168.1.1:6633

# 查看流表
ovs-ofctl dump-flows br0
```
