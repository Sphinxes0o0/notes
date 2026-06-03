# OVN (Open Virtual Network)

## OVN简介

OVN是OVS提供的原生虚拟化网络方案，旨在解决传统SDN架构的性能问题。主要功能包括：

1. L2/L3虚拟网络以及逻辑交换机
2. L2/L3/L4 ACL
3. IPv4/IPv6分布式L3路由
4. ARP/IPv6 ND suppression for known IP-MAC bindings
5. Native support for NAT and load balancing using OVS connection tracking
6. Native distributed DHCP support
7. Works with any OVS datapath (kernel, DPDK, Hyper-V)
8. Supports L3 gateways (logical to physical)
9. Supports software-based L2 gateways
10. Supports TOR-based L2 gateways (hardware_vtep schema)
11. Provides networking for VMs and containers

## OVN架构

组件：
- **northbound database**: 存储逻辑交换机、路由器、ACL、端口（基于ovsdb-server）
- **ovn-northd**: 集中式控制器，分发数据从northbound到ovn-controllers
- **ovn-controller**: 运行在每台机器上的本地SDN控制器
- **southbound database**: 包含物理网络数据、逻辑网络数据和绑定

## 图片

![OVN架构图](14879288590597.jpg)

## OVN安装

### CentOS:

```
wget -o /etc/yum.repos.d/ovs-master.repo https://copr.fedorainfracloud.org/coprs/leifmadsen/ovs-master/repo/epel-7/leifmadsen-ovs-master-epel-7.repo
yum install openvswitch openvswitch-ovn-*
```

### Ubuntu:

```
apt-get install -y openvswitch-switch ovn-central ovn-common ovn-controller-vtep ovn-docker ovn-host
```

## 启动OVN

**控制节点:**

```
/usr/share/openvswitch/scripts/ovs-ctl start --system-id=random
/usr/share/openvswitch/scripts/ovn-ctl start_northd
export CENTRAL_IP=10.140.0.2
export LOCAL_IP=10.140.0.2
export ENCAP_TYPE=vxlan
ovs-vsctl set Open_vSwitch . external_ids:ovn-remote="tcp:$CENTRAL_IP:6642" external_ids:ovn-nb="tcp:$CENTRAL_IP:6641" external_ids:ovn-encap-ip=$LOCAL_IP external_ids:ovn-encap-type="$ENCAP_TYPE"
```

**计算节点:**

```
/usr/share/openvswitch/scripts/ovs-ctl start --system-id=random
/usr/share/openvswitch/scripts/ovn-ctl start_controller
/usr/share/openvswitch/scripts/ovn-ctl start_controller_vtep
export CENTRAL_IP=10.140.0.2
export LOCAL_IP=10.140.0.2
export ENCAP_TYPE=vxlan
ovs-vsctl set Open_vSwitch . external_ids:ovn-remote="tcp:$CENTRAL_IP:6642" external_ids:ovn-nb="tcp:$CENTRAL_IP:6641" external_ids:ovn-encap-ip=$LOCAL_IP external_ids:ovn-encap-type="$ENCAP_TYPE"
```

## 参考文档

[Open Virtual Network architecture](http://openvswitch.org/support/dist-docs/ovn-architecture.7.html)
