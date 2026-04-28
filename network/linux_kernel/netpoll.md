# Netpoll - 网络轮询接口

## 1. 模块架构

### 1.1 功能概述

Netpoll 提供了一种在中断禁用的情况下发送和接收网络包的能力，主要用于网络引导和内核调试。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/netpoll.c` | Netpoll 实现 |
| `include/linux/netpoll.h` | Netpoll 定义 |

## 2. 核心数据结构

### 2.1 struct netpoll

```c
// include/linux/netpoll.h:20
struct netpoll {
    struct net_device *dev;           // 网络设备
    char name[IFNAMSIZ];              // 名称
    void (*rx_hook)(struct sk_buff *skb);  // 接收钩子

    __be32 local_ip, remote_ip;       // IP 地址
    __be16 local_port, remote_port;   // 端口
    unsigned char local_mac[ETH_ALEN];
    unsigned char remote_mac[ETH_ALEN];
};
```

### 2.2 struct netpoll_info

```c
// include/linux/netpoll.h:50
struct netpoll_info {
    struct netpoll *npinfo;
    atomic_t refcnt;                  // 引用计数
    struct delayed_work rx_work;      // 接收工作

    struct sk_buff_head txq;          // 发送队列
    spinlock_t rx_lock;               // 接收锁
};
```

## 3. 发送

### 3.1 netpoll_send_skb()

```c
// net/core/netpoll.c:280
void netpoll_send_skb(struct netpoll *np, struct sk_buff *skb)
{
    struct netpoll_info *npinfo = np->dev->npinfo;

    // 如果没有锁竞争，直接发送
    if (!spin_trylock(&npinfo->tx_lock)) {
        // 加入队列，稍后发送
        skb_queue_tail(&npinfo->txq, skb);
        return;
    }

    // 发送
    netpoll_send_skb(npinfo, skb);
    spin_unlock(&npinfo->tx_lock);
}
```

### 3.2 poll_two_as()

```c
// net/core/netpoll.c:200
static void poll_two_as(struct netpoll *np)
{
    struct netpoll *old = np;
    struct hlist_node *p;

    // 遍历所有 netpoll
    hlist_for_each_entry(np, p, &netpoll_chain, np_list) {
        if (np == old)
            continue;
        if (np->dev->flags & IFF_UP &&
            netif_carrier_ok(np->dev))
            netpoll_poll(np);
    }
}
```

## 4. 接收

### 4.1 netpoll_rx_enable()

```c
// net/core/netpoll.c:400
void netpoll_rx_enable(struct netpoll *np)
{
    struct netpoll_info *npinfo;

    npinfo = np->dev->npinfo;
    if (!npinfo)
        return;

    atomic_inc(&npinfo->refcnt);
    schedule_delayed_work(&npinfo->rx_work, 0);
}
```

### 4.2 netpoll_rx()

```c
// net/core/netpoll.c:340
void netpoll_poll(struct netpoll *np)
{
    struct netpoll_info *npinfo = np->dev->npinfo;

    // 禁用设备 IRQ
    np->dev->irq_disable;

    // 轮询设备
    np->dev->netdev_ops->ndo_poll_controller(np->dev);

    // 重新启用 IRQ
    np->dev->irq_enable;
}
```

## 5. 应用场景

### 5.1 网络引导 (netconsole)

```c
// 初始化 netconsole
static int __init netconsole_init(void)
{
    // 创建 netpoll
    // 注册到 netpoll_chain
}
```

### 5.2 KGDB over NET

```c
// kgdb 内核调试
// 使用 netpoll 进行网络通信
```
