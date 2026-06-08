---
type: entity
tags: [linux, networking, namespace, kernel, container, isolation]
created:2026-06-08
sources: [bookmark-linux-namespace-cgroup]
---

# Linux Network Namespace

## 定义

Linux network namespace（netns）是内核对网络栈进行虚拟化的核心机制，将网络设备、协议栈、路由表、conntrack 表、iptables规则等完整隔离在独立的命名空间中。network namespace 是容器网络（Docker、Kubernetes CNI）、VLAN隔离、Open vSwitch虚拟化的底层基石。

##关键要点

- **完全隔离**：每个 netns 有独立的 loopback、路由表、`/proc/net`、socket、iptables规则
- **生命周期**：`ip netns add NAME` 创建；`unshare -n` 创建临时 namespace
- **veth pair**：跨 netns通信的标准机制（一端在 ns1，另一端在 ns2）
- **与容器**：Docker 默认每个容器一个 netns（可 `--network=host`共享）
- **Kubernetes**：CNI插件（calico/flannel/cilium）创建 per-pod netns + veth桥接

##核心概念

- `ip netns list` —列出所有 netns
- **veth pair**：成对虚拟网卡，一进一出
- **bridge/vxlan**：跨 netns/host 二层互联
- **物理设备迁移**：`ip link set DEV netns PID` 把物理网卡移入 ns
- **netns file**：绑定挂载（`/run/netns/<name>`）保留 netns生命周期
- **unshare**：clone 新进程到新 netns

## 相关页面

- [[entities/container-namespace-cgroup]] — namespace整体隔离机制
- [[entities/container-technology]] —容器技术总览
- [[entities/linux/network/net-stack-overview]] — Linux 网络栈
- [[entities/linux/network/netfilter-hooks]] — 每个 netns独立 netfilter
