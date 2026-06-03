# OVS DPDK

## 主要内容

OVS DPDK - Open vSwitch加速版，使用DPDK (Data Plane Development Kit)

## 1. OVS架构概述

OVS由用户空间和内核空间组件组成。用户空间处理数据交换、OpenFlow表功能和管理工具。内核组件（openvswitch.ko）提供流表查找的快速路径。

## 2. 核心模块

- **ofproto**: 实现OpenFlow交换机
- **dpif**: 抽象单个转发路径
- **netdev**: 抽象网络接口（物理/虚拟）

## 3. DPDK集成

DPDK加速替代内核数据路径处理。数据包直接从DPDK PMD驱动到用户空间ovs-vswitchd，无需内核介入。

## 4. DPDK网络接口类型

- dpdk physical ports: 使用高性能向量化DPDK PMD驱动
- dpdkvhostuser/vhostcuse: 支持用于快速VM通信的vhost优化接口
- dpdkr: DPDK环接口，使用librte_ring与IVSHMEM VM实现零拷贝通信

## 5. 数据包流程

1. ovs-vswitchd从网络端口接收数据包
2. 检查精确匹配和通配符流表
3. 如果miss，通过OpenFlow通知SDN控制器
4. 控制器安装新流表条目用于后续数据包

## 6. 网络存储优化

讨论与OVS DPDK集成的存储优化技术。

## 图片

![OVS核心组件图](../images/14782304758427.jpg)
![OVS datapath内部模块图](../images/14782304382703.jpg)
![DPDK加速概念图](images/14889834607297.jpg)
![OVS with DPDK架构图](images/14889835917214.jpg)
![DPDK组件详情图](../images/14782305819331.jpg)
![数据包流程图](images/14889841929411.jpg)
![网络存储优化图](../images/14782307838073.jpg)
