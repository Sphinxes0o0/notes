# net/openvswitch - Open vSwitch

## 1. 模块架构

### 1.1 功能概述

Open vSwitch (OvS) 是一种多层虚拟交换机，支持 OpenFlow 协议，用于 SDN 环境。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `datapath/datapath.c` | OVS 数据路径 |
| `datapath/vport.c` | 端口管理 |
| `datapath/flow.c` | 流表 |
| `datapath/actions.c` | 动作执行 |
| `include/openvswitch/datapath.h` | 数据路径定义 |

## 2. 核心数据结构

### 2.1 struct sw_flow

```c
// datapath/flow.h:50
struct sw_flow {
    struct rcu_head rcu;
    struct hlist_node hash_node[2];
    u32 hash;

    struct ovs_key_ipv4 key;          // 流键
    struct ovs_key_ipv4 mask;          // 掩码
    unsigned long *stats;              // 统计

    struct sw_flow_actions *sf_acts;  // 动作
    unsigned long used;                // 最后使用时间
    unsigned long tcp_flags;           // TCP 标志
};
```

### 2.2 struct ovs_action_set

```c
// include/openvswitch/actions.h:40
struct ovs_action_set {
    __be16 ethertype;
    struct ethhdr eth;
    struct {
        __be32 src;
        __be32 dst;
    } ipv4;
    __be16 src_port;
    __be16 dst_port;
    __u8 ipv4_frag;
    __u8 ipv4_frag_max;
};
```

### 2.3 struct datapath

```c
// include/openvswitch/datapath.h:50
struct datapath {
    struct rcu_head rcu;
    u32 dp_ifindex;

    struct list_head ports;            // 端口列表
    struct hlist_head *flow_table;    // 流表
    struct list_head pending_list;    // 待处理列表

    struct per_cpu *stats;
};
```

## 3. 数据路径

### 3.1 ovs_dp_process_packet()

```c
// datapath/datapath.c:400
int ovs_dp_process_packet(struct sk_buff *skb, struct datapath *dp)
{
    struct sw_flow *flow;
    struct sw_flow_key key;
    struct ovs_actions *acts;

    // 提取流键
    ovs_flow_extract(skb, &key);

    // 查找流
    flow = ovsl_lookup_flow(dp, &key);
    if (!flow) {
        // 发送 upcall 到用户空间
        ovs_dp_upcall(dp, skb, &key);
        return -ENOENT;
    }

    // 获取动作
    acts = get_flow_actions(flow);

    // 执行动作
    ovs_execute_actions(dp, skb, acts);

    return 0;
}
```

### 3.2 ovs_execute_actions()

```c
// datapath/actions.c:200
static int ovs_execute_actions(struct datapath *dp, struct sk_buff *skb,
                               struct ovs_actions *acts)
{
    for each action in acts {
        switch (action->type) {
        case OVS_ACTION_ATTR_OUTPUT:
            // 输出到端口
            ovs_vport_output(dp, skb, action->port);
            break;
        case OVS_ACTION_ATTR_PUSH_VLAN:
            // 推送 VLAN 头
            __vlan_push(skb, action->vlan);
            break;
        case OVS_ACTION_ATTR_SET:
            // 修改字段
            ovs_set_action(skb, action->set);
            break;
        }
    }
}
```

## 4. 流表

### 4.1 流表查找

```c
// datapath/flow.c:300
struct sw_flow *ovsl_lookup_flow(struct datapath *dp,
                                  struct sw_flow_key *key)
{
    struct hlist_head *head;
    struct sw_flow *flow;

    // 计算哈希
    u32 hash = flow_hash(key);

    // 查找
    head = &dp->flow_table[hash & (dp->flow_table_size - 1)];
    hlist_for_each_entry_rcu(flow, head, hash_node) {
        if (flow->hash == hash && flow_match(flow, key))
            return flow;
    }

    return NULL;
}
```

### 4.2 流表过期

```c
// datapath/flow.c:500
void ovs_flow_free(struct rcu_head *rcu)
{
    struct sw_flow *flow = container_of(rcu, struct sw_flow, rcu);

    // 释放动作
    if (flow->sf_acts)
        release_flow_acts(flow->sf_acts);

    // 释放流
    kfree(flow);
}
```

## 5. Upcall

### 5.1 upcall 到用户空间

```c
// datapath/datapath.c:600
int ovs_dp_upcall(struct datapath *dp, struct sk_buff *skb,
                 struct sw_flow_key *key)
{
    struct vport *vport;
    int err;

    // 获取输入端口
    vport = ovs_vport_rcu(dp, key->in_port);
    if (!vport)
        return -ENOENT;

    // 添加到 pending 列表
    queue_gso_packets(dp->dp, skb, vport);

    return 0;
}
```

### 5.2 处理用户空间响应

```c
// datapath/datapath.c:700
static int ovs_dp_notify(struct datapath *dp, struct sk_buff *skb)
{
    struct ip_vs_mh_msg *msg = (void *)skb->data;

    switch (msg->type) {
    case OVS_PACKET_CMD_FLOW:
        // 添加/修改流
        ovs_flow_install(dp, &msg->key, msg->actions);
        break;
    case OVS_PACKET_CMD_EXECUTE:
        // 直接执行动作
        ovs_execute_actions(dp, skb, msg->actions);
        break;
    }
}
```

## 6. 端口

### 6.1 struct vport

```c
// include/openvswitch/vport.h:40
struct vport {
    struct list_head dp_node;
    struct datapath *dp;

    char name[IFNAMSIZ];
    u32 port_id;

    const struct vport_ops *ops;

    struct net_device *dev;
    struct pcpu_tstats __percpu *stats;
};
```

### 6.2 vport 操作

```c
// include/openvswitch/vport.h:60
struct vport_ops {
    enum ovs_vport_type type;
    struct vport *(*create)(const struct vport_parms *);
    int (*recv)(struct vport *, struct sk_buff *);
    void (*send)(struct vport *, struct sk_buff *);
};
```

## 7. OpenFlow 支持

### 7.1 消息类型

```c
// 支持的 OpenFlow 消息:
// - OFPT_FLOW_MOD: 流表修改
// - OFPT_PACKET_IN: 数据包到达
// - OFPT_PACKET_OUT: 数据包输出
// - OFPT_STATS_REQUEST/REPLY: 统计信息
```

### 7.2 匹配字段

```c
// 支持的匹配字段:
// - in_port: 输入端口
// - eth_src/dst: MAC 地址
// - vlan_vid: VLAN ID
// - eth_type: 以太网类型
// - ip_src/dst: IP 地址
// - tcp/udp src/dst_port: 端口
```
