---
title: VLAN 和 Hub
---

# VLAN 和 Hub 架构分析

## Hub 架构

```c
// net/hub.c
struct NetHub {
    int id;                          // Hub 标识符
    QLIST_ENTRY(NetHub) next;       // 全局 hubs 列表
    int num_ports;                   // 端口数
    QLIST_HEAD(, NetHubPort) ports; // 连接的端口
};

typedef struct NetHubPort {
    NetClientState nc;               // 嵌入的 net 客户端
    QLIST_ENTRY(NetHubPort) next;   // Hub 的端口列表
    NetHub *hub;                    // 父 Hub
    int id;                         // Hub 内端口号
    bool listed;                     // 在 hub 的端口列表中
} NetHubPort;
```

## Hub 数据包转发

```c
// net/hub.c
static ssize_t net_hub_receive(NetHub *hub, NetHubPort *source_port,
                               const uint8_t *buf, size_t len)
{
    NetHubPort *port;
    QLIST_FOREACH(port, &hub->ports, next) {
        if (port == source_port) {
            continue;               // 不发回源
        }
        qemu_send_packet(&port->nc, buf, len);
    }
    return len;
}
```

### 广播模型

- 传入数据包发送到**所有端口**除了源
- 无 MAC 学习或交换 - 纯广播
- 每个端口可独立连接到 NIC 或后端

## Hub 端口创建

```c
// net/hub.c
NetClientState *net_hub_add_port(int hub_id, const char *name,
                                 NetClientState *hubpeer)
{
    // 查找或创建给定 ID 的 hub
    // 创建新的 NetHubPort
    // 可连接到可选的 netdev
}
```

### 关键特性

- Hub ID 0 是**默认 hub** - 为传统 `-net` 选项隐式创建
- 端口命名为 `hub{N}port{M}`
- Hub ID 0 是传统网络默认

## Hub vs VLAN

| 方面 | QEMU Hub | 传统 VLAN |
|------|----------|----------|
| 隔离 | 广播域 | Layer 2 分段 |
| 转发 | 广播到所有端口 | MAC 学习 + 转发 |
| 标签 | 无 | 802.1Q VLAN 标签 |
| 用例 | 简单隔离 | 生产网络 |

## 多端口交换行为

```c
// 每个 NetHubPort 连接一个网络实体 (NIC 或后端)
// 所有数据包广播到除了源之外的所有端口
// 无生成树或环路检测
// 简单的中心-辐射拓扑
```

## 过滤器集成

```c
// net/net.c
// 过滤器按顺序应用于 TX，反向顺序用于 RX
// 当 hub 端口接收数据包时，该端口上的过滤器在转发前处理
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `net/hub.c` | Hub 实现 |
| `net/net.c` | Hub 集成和网络配置 |
