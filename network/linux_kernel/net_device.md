# net_device - 网络设备抽象层

## 1. 模块架构

### 1.1 功能概述

`net_device` 是 Linux 内核中表示网络设备的核心数据结构。它提供了对网络设备（包括物理网卡、虚拟设备、隧道等）的统一抽象。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `include/linux/netdevice.h` | net_device 定义 |
| `net/core/dev.c` | 设备操作实现 |
| `net/core/net-sysfs.c` | sysfs 接口 |

## 2. 关键数据结构

### 2.1 struct net_device

```c
// include/linux/netdevice.h:1088
struct net_device {
    char                    name[IFNAMSIZ];     // 设备名 (e.g., "eth0")
    char                    *ifalias;            // 别名
    unsigned long           mem_end;             // 内存结束
    unsigned long          mem_start;           // 内存开始
    unsigned long          base_addr;           // I/O 基地址
    unsigned int           irq;                 // 中断号

    // 设备状态
    unsigned long          state;
#define NETREG_UNINITIALIZED     0x00
#define NETREG_REGISTERED        0x01
#define NETREG_UNREGISTERING     0x02
#define NETREG_UNREGISTERED      0x03
#define NETREG_DUMMY             0x04

    // 引用计数
    atomic_t               carrier_changes;       // 载波变化计数
    refcount_t            dev_refcnt;          // 设备引用

    // 功能标志
    netdevice_features_t   features;           // 设备功能
    netdevice_hw_features_t hw_features;       // 硬件功能
    netdevice_vlan_features_t vlan_features; // VLAN 功能

    // MTU
    unsigned int           mtu;                 // 最大传输单元
    unsigned short        needed_headroom;     // 需要的 headroom
    unsigned short        needed_tailroom;     // 需要的 tailroom

    // 设备操作
    const struct net_device_ops *ops;          // 设备操作函数集

    // 头操作
    const struct header_ops *header_ops;      // 头操作函数集

    // 地址信息
    unsigned char           addr_len;           // 地址长度
    unsigned short         flags;               // IFF_* 标志
    unsigned short         priv_flags;          // 私有标志
    unsigned char          perm_addr[MAX_ADDR_LEN]; // 永久地址
    unsigned char           addr_assign_type;   // 地址分配类型
    unsigned char           type;               // 设备类型 (ARPHRD_*)

    // 硬件地址
    unsigned char           dev_addr[MAX_ADDR_LEN]; // 当前地址
    struct netdev_hw_addr_list uc;            // 单播地址列表
    struct netdev_hw_addr_list mc;            // 多播地址列表
    struct netdev_hw_addr_list dev_addrs;     // 设备地址列表

    // 队列
    unsigned int           num_tx_queues;       // TX 队列数
    unsigned int           real_num_tx_queues; // 实际 TX 队列数
    struct netdev_tc_to_tc tc_to_txq[];      // TC 到 TXQ 映射

    // RX 队列
    unsigned int           num_rx_queues;      // RX 队列数
    unsigned int           real_num_rx_queues; // 实际 RX 队列数

    // GRO
    struct gro_normal_batch *gro_normal_batch;
    unsigned int           gro_max_size;
    unsigned int           gro_flush_time;

    // RX 统计
    struct net_device_stats stats;             // 设备统计
    struct pcpu_sw_netstats *__percpu *tstats; // per-CPU 统计

    // 设备列表
    struct device           dev;                // 嵌入的 struct device
    struct net            *nd_net;             // 所属网络命名空间

    // 链表
    struct list_head        dev_list;          // 全局设备列表
    struct list_head        napi_list;        // NAPI 列表
    struct list_head        unreg_list;        // 注销中列表
    struct list_head        close_list;        // 关闭中列表

    // NAPI
    structgro_stats *gro_stats;
    struct napi_struct __rcu *napi_list;

    // 分片页池
    struct page_pool __rcu *pp;

    // XDP
    struct bpf_prog __rcu *xdp_prog;
    struct netdev_dev *_xdp;

    // 隧道
    struct ip_tunnel_parm     ip_tunnel_parm;

    // 链表节点
    struct netdev_adjacent    *adj_list;
    struct netdev_phys_port_id phys_port_id;
};
```

### 2.2 struct net_device_ops

```c
// include/linux/netdevice.h:1032
struct net_device_ops {
    int                     (*ndo_init)(struct net_device *dev);
    void                    (*ndo_uninit)(struct net_device *dev);
    void                    (*ndo_open)(struct net_device *dev);
    int                     (*ndo_stop)(struct net_device *dev);
    netdev_tx_t             (*ndo_start_xmit)(struct sk_buff *skb,
                                              struct net_device *dev);
    u16                     (*ndo_select_queue)(struct net_device *dev,
                                                 struct sk_buff *skb,
                                                 struct net_device *sb_dev);
    void                    (*ndo_set_rx_mode)(struct net_device *dev);
    int                     (*ndo_set_mac_address)(struct net_device *dev,
                                                   void *addr);
    int                     (*ndo_validate_addr)(struct net_device *dev);
    int                     (*ndo_do_ioctl)(struct net_device *dev,
                                            struct ifreq *ifreq, int cmd);
    int                     (*ndo_set_config)(struct net_device *dev,
                                                struct ifmap *map);
    int                     (*ndo_change_mtu)(struct net_device *dev, int new_mtu);
    int                     (*ndo_neigh_setup)(struct net_device *dev,
                                                struct neigh_parms *parms);
    void                    (*ndo_tx_timeout)(struct net_device *dev, u32 queue);
    struct rtnl_link_stats64* (*ndo_get_stats64)(struct net_device *dev,
                                                    struct rtnl_link_stats64 *stats);
    void                    (*ndo_vlan_rx_add_vid)(struct net_device *dev,
                                                     __be16 proto, u16 vid);
    void                    (*ndo_vlan_rx_kill_vid)(struct net_device *dev,
                                                      __be16 proto, u16 vid);
    // ... 更多操作
};
```

## 3. NAPI 轮询机制

### 3.1 struct napi_struct

```c
// include/linux/netdevice.h:962
struct napi_struct {
    struct list_head        poll_list;         // 轮询列表
    unsigned long           state;              // NAPI_STATE_*
    int                     weight;             // 每次轮询的配额
    unsigned int            gro_count;          // GRO 计数
    int                     (*poll)(struct napi_struct *, int);
    struct net_device       *dev;              // 关联的设备
    struct gro_list        gro_hash[NAPI_GRO_HASH_BUCKETS];
    struct sk_buff          *skb;
};
```

### 3.2 NAPI 状态

```c
enum {
    NAPI_STATE_SCHED,          // 等待轮询
    NAPI_STATE_MISSED,        // 未轮询
    NAPI_STATE_DISABLE,        // 已禁用
    NAPI_STATE_NPSVC,          // 网络平面服务
    NAPI_STATE_LISTENING,      // 监听中
    NAPI_STATE_NO_DISABLE,     // 不能禁用
};
```

### 3.3 NAPI 轮询流程

```c
// 软中断处理
static void net_rx_action(struct softirq_action *h)
{
    struct list_head *list = &softirq_vec[NET_RX_SOFTIRQ].actions;

    while (!list_empty(list)) {
        napi = list_first_entry(list, struct napi_struct, poll_list);
        budget -= napi->poll(napi, budget);
        if (!budget) break;
    }
}

// NAPI 轮询函数
static int eth_poll(struct napi_struct *napi, int budget)
{
    int work_done = 0;

    // 处理接收
    while (work_done < budget) {
        struct sk_buff *skb = netif_receive_skb(skb);
        if (!skb) break;
        work_done++;
    }

    // 如果工作完成，重新启用中断
    if (work_done < budget) {
        napi_complete(napi);
        enable_irq(dev->irq);
    }

    return work_done;
}
```

## 4. 数据包接收

### 4.1 netif_receive_skb

```c
// net/core/dev.c:5069
static int netif_receive_skb_core(struct sk_buff **pskb, int budget)
{
    struct sk_buff *skb = *pskb;
    struct net_device *orig_dev = skb->dev;

    // 1. VLAN 处理
    skb = vlan_hwaccel_rcv(skb);

    // 2. GRO 处理
    struct gro_list gro_list;
    skb = napi_gro_receive(napi, skb);

    // 3. 协议处理
    deliver_skb(skb, pt_prev, orig_dev);

    // 4. 更新统计
    return NET_RX_SUCCESS;
}
```

### 4.2 数据包类型处理

```c
// struct packet_type - 协议处理函数
struct packet_type {
    __be16                  type;               // 协议类型 (ETH_P_*)
    struct net_device       *dev;              // 设备 (NULL 表示全部)
    int                     (*func)(struct sk_buff *,
                                    struct net_device *,
                                    struct packet_type *,
                                    struct net_device *);
    struct net             *af_packet_net;
    void                    *af_packet_priv;
    struct list_head        list;
};
```

## 5. 数据包发送

### 5.1 dev_queue_xmit

```c
// net/core/dev.c:4230
int dev_queue_xmit(struct sk_buff *skb)
{
    struct net_device *dev = skb->dev;
    struct netdev_queue *txq;

    // 1. 获取发送队列
    txq = netdev_pick_tx(dev, skb);

    // 2. 尝试软件传输
    if (!netdev_txq_maybe_xmit(txq, skb)) {
        // 队列已满，尝试沨入
        if (netif_xmit_frozen_or_stopped(txq))
            goto drop;
    }

    // 3. 硬中断发送
    return dev_hard_start_xmit(skb, dev);
}
```

### 5.2 ndo_start_xmit

```c
// net/core/dev.c:3490
static netdev_tx_t dev_hard_start_xmit(struct sk_buff *skb,
                                        struct net_device *dev)
{
    netdev_tx_t ret;

    // 1. 处理 GSO
    if (skb_shinfo(skb)->gso_size) {
        ret = dev_gso_segment(skb);
        if (ret != NETDEV_TX_OK)
            return ret;
    }

    // 2. 更新统计
    dev->stats.tx_packets++;
    dev->stats.tx_bytes += skb->len;

    // 3. 调用设备驱动
    ret = dev->ops->ndo_start_xmit(skb, dev);

    return ret;
}
```

## 6. 设备注册

### 6.1 注册流程

```c
// net/core/dev.c:8864
int register_netdevice(struct net_device *dev)
{
    struct net *net = dev_net(dev);

    // 1. 初始化设备
    init_device_random(dev);

    // 2. 添加到设备列表
    list_add_tail_rcu(&dev->dev_list, &net->dev_index_head);

    // 3. 注册设备
    device_add(&dev->dev);

    // 4. 注册 sysfs 文件
    netdev_register_sysfs(dev);

    // 5. 注册协议处理
    dev_add_pack(&dev->ptype_specific);

    // 6. 设置状态
    set_bit(NETREG_REGISTERED, &dev->state);

    return 0;
}
```

### 6.2 注销流程

```c
// net/core/dev.c:8932
int unregister_netdevice(struct net_device *dev)
{
    // 1. 停止设备
    dev_close(dev);

    // 2. 清玹队列
    netif_disable_gpio(dev);

    // 3. 移除协议处理
    __dev_remove_pack(dev);

    // 4. 从列表移除
    list_del_rcu(&dev->dev_list);

    // 5. 释放资源
    free_netdev(dev);
}
```

## 7. netdev 通知链

### 7.1 通知事件

```c
enum netdev_event {
    NETDEV_UP,               // 设备启用
    NETDEV_DOWN,             // 设备停用
    NETDEV_REBOOT,           // 设备重启
    NETDEV_CHANGEMTU,        // MTU 改变
    NETDEV_CHANGEADDR,       // 地址改变
    NETDEV_CHANGE,           // 其他改变
    NETDEV_FEAT_CHANGE,      // 功能改变
    NETDEV_BONDING_FAILOVER,// bonding 故障转移
    NETDEV_PRE_UP,           // 启动前
    NETDEV_PRE_TYPE_CHANGE,  // 类型改变前
    NETDEV_POST_TYPE_CHANGE, // 类型改变后
    NETDEV_POST_INIT,       // 初始化后
    NETDEV_UNREGISTER,      // 注销中
    NETDEV_UNREGISTER_FINAL,// 注销完成
    NETDEV_RELEASE,          // 释放
    NETDEV_NOTIFY_PEERS,    // 通知邻居
    NETDEV_JOIN,            // 加入
};
```

### 7.2 注册通知

```c
int register_netdevice_notifier(struct notifier_block *nb);
int unregister_netdevice_notifier(struct notifier_block *nb);
```
