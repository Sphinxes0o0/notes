# iptables/netfilter

## netfilter

netfilter是Linux内核的数据包过滤框架，提供钩子供其他模块控制数据包流：
- NF_IP_PRE_ROUTING：数据包刚经过数据链路层解封装进入网络层之后
- NF_IP_LOCAL_IN：经过路由查找后，确定是本地生成的数据包
- NF_IP_FORWARD：转发的数据包（非本地生成，也非本地目的地）
- NF_IP_LOCAL_OUT：本地生成的外发数据包
- NF_IP_POST_ROUTING：即将离开机器的数据包

![netfilter架构图](images/netfilter.png)

## iptables

iptables使用表和链组织数据包过滤规则。默认表包括：
- **raw**: 数据包状态跟踪，PREROUTING和OUTPUT链
- **filter**: 过滤，INPUT/FORWARD/OUTPUT链
- **nat**: 网络地址转换，PREROUTING/INPUT/OUTPUT/POSTROUTING链
- **mangle**: 数据包修改，五个链
- **security**: 安全策略，INPUT/FORWARD/OUTPUT链

每条规则有匹配条件（端口、IP、数据包类型、conntrack等模块）和动作（-j ACCEPT, DROP, RETURN, SNAT, DNAT）。

![iptables流程图](images/iptables.png)

流程：PREROUTING → 路由决策 → INPUT（本地）或FORWARD → POSTROUTING

## iptables示例

```
iptables -nvL
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -s 192.168.0.4 -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -t nat -I POSTROUTING -s 10.0.0.30/32 -j MASQUERADE
```

NAT和端口映射示例也有提供。

## nftables

3.13+内核的新数据包过滤框架，用nft命令替代iptables。支持可配置表（ip, arp, ip6, bridge, inet, netdev）并包括集合/映射支持。

## 参考文档

- A Deep Dive into Iptables and Netfilter Architecture (DigitalOcean)
- netfilter.org
- iptables wiki (Arch Linux)
- nftables wiki
