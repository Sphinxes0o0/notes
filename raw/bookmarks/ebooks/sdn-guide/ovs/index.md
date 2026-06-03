# Open vSwitch

## 概述

本章介绍Open vSwitch在CentOS系统上的安装、配置和管理。

## OVS安装 (CentOS)

- 使用`yum`通过centos-release-openstack-newton安装
- 从COPR仓库安装替代主版本

## 常用OVS命令参考

- 使用`ovs-vsctl`管理网桥和端口
- OVS端口的IP配置
- 流量镜像配置
- QoS设置（出口队列和入口限制）
- sFlow监控设置
- 使用`ovs-ofctl`管理流表规则
- VXLAN/GRE隧道配置
- 使用`ovs-appctl fdb/show`查看MAC地址学习
- 控制器配置

## 流表管理

- 流规则组成：基本字段、匹配字段和动作字段
- 常见OpenFlow字段（in_port, dl_vlan, dl_src/dst, dl_type, nw_src/dst等）
- 支持的动作（output, mod_vlan_vid, strip_vlan, mod_dl_src/dst, mod_nw_src/dst, resubmit, load）
- 使用`ovs-appctl ofproto/trace`进行数据包跟踪

## 数据包注入 (Packet Out)

使用Scapy和`ovs-ofctl packet-out`进行数据包注入。

## OVS文档链接

- Open vSwitch官方网站
- Scott Lowe的博客
- Russell Bryant的博客
