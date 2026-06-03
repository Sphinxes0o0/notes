# Kubernetes网络

## 网络模型

- **IP-per-Pod**: 每个pod有唯一IP；容器在同一网络命名空间内共享
- **扁平网络**: 所有pod可以直接通过IP通信，无需NAT
- **Service Cluster IP**: 内部使用；外部访问需要NodePort、LoadBalancer或Ingress

## 官方插件

- **kubenet**: 默认基于CNI的桥接插件，具有端口映射、流量整形、SNAT规则和带宽限制
- **CNI**: 标准插件，需要在`/etc/cni/net.d`配置和`/opt/cni/bin`中的二进制文件

## 其他插件

- **Flannel**: 使用UDP封装通过etcd的覆盖网络
- **Weave Net**: 去中心化L2覆盖，有sleeve（用户空间）和fastpath（内核/OVS）模式
- **Calico**: 基于BGP的纯L3解决方案，无覆盖；包括通过iptables的网络策略
- **OVS**: Linux桥接kbr0 + 通过GRE连接的OVS桥接obr0
- **OVN**: 原生OVS虚拟化，提供覆盖和底层模式
- **Contiv**: Cisco的基于策略的多租户网络（VLAN、BGP、VXLAN、ACI）
- **Romana**: 路由聚合减少覆盖开销
- **OpenContrail**: Juniper的vRouter解决方案（内核、DPDK或Agilio模式）
- **Midonet**: 基于Zookeeper+Cassandra的分布式网络
- **Host Network**: 共享主机命名空间；无隔离，高性能

## 其他选项

- **ipvs**: v1.8+中用于负载均衡的Alpha支持
- **Canal**: Flannel + Calico组合
- **kuryr-kubernetes**: OpenStack Neutron集成
- **Cilium**: 基于eBPF/XDP的高性能网络
- **kope**: Layer2、Vxlan或IPsec模式
- **Kube-router**: 具有可选ipvs服务发现的BGP
