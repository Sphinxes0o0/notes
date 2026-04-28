# net/bridge - 网桥实现

## 1. 模块架构

### 1.1 功能概述

Linux 网桥是二层交换机软件实现，在同一个广播域中连接多个网络接口，支持生成树协议(STP)。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/bridge/br_private.h` | 内部定义 |
| `net/bridge/br_device.c` | 设备实现 |
| `net/bridge/br_forward.c` | 转发逻辑 |
| `net/bridge/br_input.c` | 输入处理 |
| `net/bridge/br_stp.c` | 生成树协议 |
| `net/bridge/br_fdb.c` | FDB (转发表) |

## 2. 核心数据结构

### 2.1 struct net_bridge

```c
// net/bridge/br_private.h:287
struct net_bridge {
    struct net_device       *dev;              // 网桥设备
    struct list_head       port_list;         // 端口列表
    struct net_bridge_port __rcu *default_port;  // 默认端口
    struct list_head       head_list;         // 接口头

    // 功能
    unsigned long           feature_mask;       // 功能掩码
    bool                  STP_ENABLED;        // STP 启用

    // 配置
    unsigned char         bridge_id;          // 网桥 ID
    unsigned char         root_id[8];         // 根桥 ID
    unsigned short        root_port;          // 根端口
    unsigned long         root_path_cost;     // 根路径成本
    unsigned long         bridge_max_age;     // 最大年龄
    unsigned long         bridge_hello_time;  // Hello 时间
    unsigned long         forward_delay;      // 转发延迟
    unsigned long         max_age;
    unsigned long         hello_timer;        // Hello 定时器
    unsigned long         tcn_timer;         // TCN 定时器
    unsigned long         topology_change_timer;

    // FDB
    spinlock_t            hash_lock;
    struct hlist_head     hash[BR_HASH_SIZE];  // FDB 哈希表
    struct list_head       age_list;          // 老化列表

    // VLAN
    struct bridge_vlan_options *vlan_info;
};
```

### 2.2 struct net_bridge_port

```c
// net/bridge/br_private.h:186
struct net_bridge_port {
    struct net_bridge      *br;              // 所属网桥
    struct net_device      *dev;             // 底层设备
    struct list_head        list;            // 网桥端口列表

    // STP
    unsigned char           port_id;          // 端口 ID
    unsigned char           state;            // 端口状态
    unsigned long           designated_root;   // 指定根
    unsigned long           designated_bridge; // 指定桥
    unsigned short          designated_port;   // 指定端口
    unsigned long           path_cost;       // 路径成本
    unsigned long           port_hello_time; // Hello 时间
    unsigned long           designated_cost;  // 指定成本

    // 定时器
    unsigned long           message_age_timer;
    unsigned long           forward_delay_timer;
    unsigned long           hold_timer;

    // FDB
    struct hlist_node       hash_node;
    struct rcu_head         rcu;

    unsigned long           flags;
#define BR_HAIRPIN_MODE     0x01
#define BR_BPDU_ENABLED     0x02
#define BR_ROOT_PORT        0x04
#define BR_MULTICAST_FLOOD  0x08
};
```

## 3. FDB (转发表)

### 3.1 struct net_bridge_fdb_entry

```c
// net/bridge/br_private.h:117
struct net_bridge_fdb_entry {
    struct hlist_node       hash_node;        // 哈希链表
    struct rcu_head        rcu;
    __u8                   addr[ETH_ALEN];   // MAC 地址
    __u16                  vlan_id;          // VLAN ID
    unsigned long           updated;
    unsigned long           used;

    struct net_bridge_port __rcu *dst;      // 输出端口

    atomic_t                ahh_entries;      // 引用计数
};
```

### 3.2 FDB 查找

```c
// net/bridge/br_fdb.c:78
static struct net_bridge_fdb_entry *br_fdb_find(struct net_bridge *br,
                                                  const unsigned char *addr,
                                                  __u16 vlan_id)
{
    struct hlist_head *head = &br->hash[br_mac_hash(addr)];

    hlist_for_each_entry_rcu(fdb, head, hash_node) {
        if (ether_addr_equal(fdb->addr, addr) && fdb->vlan_id == vlan_id)
            return fdb;
    }
    return NULL;
}
```

## 4. 接收流程

### 4.1 br_handle_frame()

```c
// net/bridge/br_input.c:108
static rx_handler_result_t br_handle_frame(struct sk_buff **pskb)
{
    struct sk_buff *skb = *pskb;
    const unsigned char *dest = eth_hdr(skb)->h_dest;

    // 丢弃生成树 BPDU (除非启用)
    if (!br->STP_ENABLED && is_bpdu)
        return RX_HANDLER_PASS;

    // 检查是否为本地 MAC
    if (unlikely(is_link_local(dest)))
        return br_pass_frame_up(skb);

    // 查找 FDB
    fdb = br_fdb_find(br, dest, vlan_id);
    if (fdb) {
        // 已知单播，发送到对应端口
        br_forward(fdb->dst->dev, skb);
    } else {
        // 未知单播/广播，洪泛
        br_flood_forward(skb);
    }
}
```

## 5. 转发逻辑

### 5.1 br_forward()

```c
// net/bridge/br_forward.c:63
void br_forward(const struct net_bridge_port *to, struct sk_buff *skb)
{
    // 1. Hairpin 检查
    if (should_deliver(to, skb)) {
        // 2. 发送到端口
        deliver(to, skb);
    }
}

static void deliver(const struct net_bridge_port *to, struct sk_buff *skb)
{
    // 更新统计
    to->br->dev->stats.tx_packets++;
    to->br->dev->stats.tx_bytes += skb->len;

    // 发送到设备
    skb->dev = to->dev;
    dev_queue_xmit(skb);
}
```

### 5.2 br_flood_forward()

```c
// net/bridge/br_forward.c:83
void br_flood_forward(struct sk_buff *skb)
{
    list_for_each_entry(p, &br->port_list, list) {
        if (should_deliver(p, skb))
            __br_forward(p, skb);
    }
}
```

## 6. 生成树协议 (STP)

### 6.1 端口状态

```c
// net/bridge/br_stp.h:12
enum br_port_state {
    BR_STATE_DISABLED = 0,      // 禁用
    BR_STATE_BLOCKING = 1,      // 阻塞
    BR_STATE_LISTENING = 2,     // 监听
    BR_STATE_LEARNING = 3,      // 学习
    BR_STATE_FORWARDING = 4,    // 转发
    BR_STATE_STATE = 5
};
```

### 6.2 BPDU 处理

```c
// net/bridge/br_stp.c:145
void br_stp_handle_bpdu(struct sk_buff *skb)
{
    struct br_config_bpdu bpdu;

    // 解析 BPDU
    br_stp_parse_bpdu(skb, &bpdu);

    switch (bpdu.type) {
    case BPDU_TYPE_CONFIG:
        br_stp_config_bpdu(skbpdu, &bpdu);
        break;
    case BPDU_TYPE_TCN:
        br_stp_tcn_bpdu(skb);
        break;
    }
}
```

## 7. VLAN 支持

### 7.1 VLAN 感知网桥

```c
// net/bridge/br_vlan.c
struct bridge_vlan_options {
    struct rhashtable       vlan_hash;      // VLAN 哈希表
    u16                     pvid;           // 端口 VLAN ID
};

int br_vlan_add(struct net_bridge *br, u16 vid, bool tagged);
int br_vlan_delete(struct net_bridge *br, u16 vid);
```

## 8. netfilter 集成

### 8.1 ebtables

```c
// net/bridge/netfilter/ebtables.c
// 网桥层面的包过滤
// 支持在 INPUT/OUTPUT/FORWARD 链上过滤

struct ebt_entries {
    char name[EBT_IFTABLE_MAXNAMELEN];
    struct ebt_entry *entries;
    unsigned int nentries;
};
```
