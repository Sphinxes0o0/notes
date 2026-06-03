# Mininet

## 概述

Mininet是斯坦福大学Nick研究组开发的网络虚拟化平台，用于测试、验证和研究OpenFlow和SDN网络。它利用Linux网络命名空间创建虚拟节点，每个主机获得自己的网络命名空间，而交换机和控制器运行在根命名空间。

## 安装 (Ubuntu)

```bash
sudo apt-get install -y mininet openvswitch-testcontroller
sudo /usr/bin/ovs-testcontroller /usr/bin/ovs-controller
sudo service openvswitch-switch start
sudo mn --test pingall
```

## mn命令行

**命令:** py, dump, nodes, net, links, link, xterm, dpctl, pingall

**选项:** --topo (拓扑类型), --link (网络参数), --switch (交换机类型), --controller, --nat, --cluster, --mac, --arp

## Python API示例

本章提供了一个完整的Python脚本，使用`Topo`、`Mininet`、`dumpNodeConnections`和`OVSController`类创建连接多个主机的单个交换机。

## 参考链接

- http://mininet.org/
- https://github.com/mininet/mininet
- https://reproducingnetworkresearch.wordpress.com/
