# 内核VRF

## Virtual Routing and Forwarding (VRF)

Linux内核的Virtual Routing and Forwarding (VRF)是由路由表和一组网络设备组成的路由实例。

## VRF安装

Ubuntu默认不包括vrf内核模块，需要额外安装：

```bash
apt-get install linux-headers-4.10.0-14-generic linux-image-extra-4.10.0-14-generic
reboot
apt-get install linux-image-extra-$(uname -r)
modprobe vrf
```

## VRF示例

```bash
# create vrf device
ip link add vrf-blue type vrf table 10
ip link set dev vrf-blue up

# An l3mdev FIB rule directs lookups to the table associated with the device.
ip ru add oif vrf-blue table 10
ip ru add iif vrf-blue table 10

# Set the default route for the table
ip route add table 10 unreachable default

# Enslave L3 interfaces to a VRF device
ip link set dev eth1 master vrf-blue

# IPv6 sysctl option
sysctl -w net.ipv6.conf.all.keep_addr_on_down=1

# Additional VRF routes
ip route add table 10 ...
```

## 进程绑定VRF

进程可通过`SO_BINDTODEVICE`套接字选项绑定VRF：

```c
setsockopt(sd, SOL_SOCKET, SO_BINDTODEVICE, dev, strlen(dev)+1);
```

默认VRF上下文的服务可通过以下sysctl选项跨所有VRF域工作：

```bash
sysctl -w net.ipv4.tcp_l3mdev_accept=1
sysctl -w net.ipv4.udp_l3mdev_accept=1
```

## VRF操作

**创建VRF:**
```bash
ip link add dev NAME type vrf table ID
```

**查询VRF列表:**
```bash
ip -d link show type vrf
```

**添加网卡到VRF:**
```bash
ip link set dev eth0 master vrf-blue
```

**查询VRF邻接表和路由:**
```bash
ip neigh show vrf vrf-blue
ip addr show vrf vrf-blue
ip -br addr show vrf vrf-blue
ip route show vrf vrf-blue
```

**从VRF中删除网卡:**
```bash
ip link set dev eth0 nomaster
```

## 参考文档

[Linux kernel documentation](https://www.kernel.org/doc/Documentation/networking/vrf.txt)
