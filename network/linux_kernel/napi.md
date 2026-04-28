# NAPI - 轮询机制

## 1. 模块架构

### 1.1 功能概述

NAPI (New API) 是 Linux 网络设备驱动的轮询接口，用于高效处理高频网络中断。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/dev.c` | NAPI 实现 |
| `include/linux/netdevice.h` | NAPI 定义 |

## 2. 核心数据结构

### 2.1 struct napi_struct

```c
// include/linux/netdevice.h:950
struct napi_struct {
    struct list_head    dev_list;      // 设备链表
    struct hlist_node   napi_hash;     // NAPI 哈希表
    struct gro_list     gro_list;      // GRO 列表
    int                 (*poll)(struct napi_struct *, int);
    unsigned int        state;
    unsigned int        weight;        // 权重 (默认 64)
    unsigned long       gro_bitmask;   // GRO 掩码

    struct net_device   *dev;         // 关联设备
    struct list_head    poll_list;     // 轮询链表
    unsigned int        poll_owner;    // 轮询所有者

    unsigned int        gro_count;     // GRO 计数
    int                 (*complete)(struct sk_buff *skb);
};
```

## 3. NAPI 状态

```c
// include/linux/netdevice.h
enum {
    NAPI_STATE_SCHED,      // 等待轮询
    NAPI_STATE_DISABLE,    // 已禁用
    NAPI_STATE_NPSVC,      // 非每秒向量
    NAPI_STATE_HASHED,     // 已加入哈希表
};
```

## 4. NAPI 轮询流程

### 4.1 net_rx_action()

```c
// net/core/dev.c:5300
static int net_rx_action(struct softirq_action *h)
{
    struct list_head *process_list = &__get_cpu_var(softnet_data.poll_list);
    struct napi_struct *napi;
    unsigned long time_limit = jiffies + 2;
    int budget = weight_p;

    list_for_each_entry(napi, process_list, poll_list) {
        // 调用设备驱动的 poll 函数
        work = napi->poll(napi, budget);

        // 更新统计
        if (work > budget)
            napi->weight = work;
    }

    return budget - work;
}
```

### 4.2 napi_disable()

```c
// net/core/dev.c:5400
void napi_disable(struct napi_struct *napi)
{
    set_bit(NAPI_STATE_DISABLE, &napi->state);
    wait_var_event(&napi->state, !test_bit(NAPI_STATE_SCHED, &napi->state));
}
```

### 4.3 napi_enable()

```c
// net/core/dev.c:5390
void napi_enable(struct napi_struct *napi)
{
    clear_bit(NAPI_STATE_DISABLE, &napi->state);
    synchronize_rcu();
}
```

## 5. NAPI 注册

### 5.1 netif_napi_add()

```c
// net/core/dev.c:5420
void netif_napi_add(struct net_device *dev, struct napi_struct *napi,
                   int (*poll)(struct napi_struct *, int), int weight)
{
    INIT_LIST_HEAD(&napi->poll_list);
    napi->poll = poll;
    napi->weight = weight;
    napi->dev = dev;
    list_add_rcu(&napi->dev_list, &dev->napi_list);
}
```

### 5.2 netif_napi_del()

```c
// net/core/dev.c:5440
void netif_napi_del(struct napi_struct *napi)
{
    list_del_rcu(&napi->dev_list);
    napi_free_frags(napi);
}
```

## 6. 混合模式 (NAPI vs 中断)

### 6.1 中断处理

```c
// 设备中断处理
irqreturn_t xxx_interrupt(int irq, void *dev_id)
{
    struct net_device *dev = dev_id;

    if (likely(netif_running(dev) && netif_carrier_ok(dev))) {
        // 立即关闭中断，启用 NAPI
        disable_irq_nosync(irq);
        __netif_rx_schedule(dev);
    }

    return IRQ_HANDLED;
}
```

### 6.2 __netif_rx_schedule()

```c
// net/core/dev.c:5150
void __netif_rx_schedule(struct net_device *dev)
{
    struct softnet_data *sd = &__get_cpu_var(softnet_data);

    // 添加到 per-CPU 轮询链表
    list_add_tail(&dev->napi->poll_list, &sd->poll_list);
    __raise_softirq_irqoff(NET_RX_SOFTIRQ);
}
```

## 7. GRO 与 NAPI

```c
// net/core/dev.c:5170
static int process_backlog(struct napi_struct *napi, int quota)
{
    struct softnet_data *sd = container_of(napi, struct softnet_data, backlog);

    while ((skb = __skb_dequeue(&sd->process_queue)) && quota--) {
        // 调用 GRO 接收
        napi_gro_receive(napi, skb);
    }

    if (!skb_queue_empty(&sd->process_queue)) {
        // 还有更多数据，调度自己
        __list_add(&napi->poll_list, ...);
        return quota;
    }

    return 0;
}
```

## 8. 权重调度

### 8.1 权重计算

```c
// net/core/dev.c:5270
static int dev_weight_thresh(struct net_device *dev)
{
    // 根据 MTU 和带宽计算权重
    return max(dev->mtu, 64) * (dev->num_tx_queues ?: 1);
}
```

### 8.2 budget 分配

```c
// 每个 NAPI 实例获得的 budget:
// budget = weight_p * num_napi / num_online_cpus
// 默认 weight_p = 64
```
