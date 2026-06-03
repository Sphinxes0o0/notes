# 负载均衡

## 主题

- LVS (Linux Virtual Server)
- HAProxy
- Nginx
- 自研方案 (Google Maglev, UCloud Vortex)

## LVS关键点

- 包括ipvs内核模块和ipvsadm工具
- 角色：Director Server和Real Server
- 工作在netfilter PREROUTING/INPUT链

## 转发模式

- **NAT**: 修改目标IP/端口；需要Director作为网关
- **DR**: 修改目标MAC；需要在Real Server lo上配置VIP
- **TUN**: IP封装；不需要网关
- **FULLNAT**: 阿里巴巴扩展；使用本地IP支持跨vlan

## 图片

![LVS NAT模式](images/lvs-nat.png)
![LVS DR模式](images/lvs-dr.png)
![LVS TUN模式](images/lvs-tun.png)
![LVS FULLNAT模式](images/lvs-fullnat.png)
![Maglev](images/maglev.png)

## 调度算法

- Round-Robin, Weighted Round-Robin
- Least-Connection, Weighted Least-Connection
- Locality-Based Least Connections
- Destination/Source Hashing
- Shortest Expected Delay, Never Queue

## 配置示例

提供安装ipvsadm/keepalived、VRRP配置和ARP抑制VIP设置的命令。

## 自研方案

- **Google Maglev**: 5秒启动，1M req/sec，内核旁路，ECMP，一致性哈希
- **UCloud Vortex**: 类似于Maglev，14M PPS性能使用DPDK
