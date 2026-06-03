# 3.5 Linux 网络虚拟化技术

## 概述

Linux 网络虚拟化技术允许在单一物理机上创建多个隔离的网络环境，每个环境拥有独立的网络资源。

## 主要技术

- **网络命名空间（Network Namespace）**：实现网络资源隔离
- **虚拟网卡（Veth）**：连接不同命名空间
- **Linux Bridge**：虚拟交换机
- **TUN/TAP**：用户空间与内核空间数据传输
- **VXLAN**：Overlay 网络技术

## 相关章节

- [3.5.1 网络命名空间](./network-namespace.html)
- [3.5.2 虚拟网络设备 TUN 和 TAP](./tuntap.html)
- [3.5.3 虚拟网卡 Veth](./virtual-nic.html)
- [3.5.4 虚拟交换机 Linux Bridge](./linux-bridge.html)
- [3.5.5 虚拟网络通信技术 VXLAN](./vxlan.html)
