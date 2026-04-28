# flow_dissector - 报文解析

## 1. 模块架构

### 1.1 功能概述

flow_dissector 用于从网络报文中提取流信息，用于分类和 QoS。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/flow_dissector.c` | flow_dissector 实现 |
| `include/net/flow_dissector.h` | 定义 |
| `net/ipv4/fib_frontend.c` | IPv4 解析 |

## 2. 核心数据结构

### 2.1 struct flow_keys

```c
// include/net/flow_dissector.h:80
struct flow_keys {
    struct flow_dissector_key_data {
        __u32     control;           // 控制 flags
        __u32     src;               // 源地址
        __u32     dst;               // 目的地址
        __u32     src_port;          // 源端口
        __u32     dst_port;          // 目的端口
        __u16     ip_proto;          // IP 协议
        __u16     thoff;             // TCP 头偏移
        __u16     nw_proto;          // 网络层协议
        u8        icmp_type;         // ICMP 类型
        u8        icmp_code;         // ICMP 代码
        __u32     key_control;       // key control
    } key;
};
```

### 2.2 struct flow_dissector

```c
// include/net/flow_dissector.h:40
struct flow_dissector {
    unsigned int used_keys;           // 使用的 key 掩码
    unsigned int nav_keys;            // nav key 掩码

    int (*get_key)(struct flow_dissector *fcd,
                   struct sk_buff *skb,
                   void *data);

    void *target_mask;
    void *target_used;
};
```

## 3. 解析函数

### 3.1 skb_flow_dissector()

```c
// net/core/flow_dissector.c:200
void skb_flow_dissector(struct flow_dissector *fcd,
                         struct sk_buff *skb,
                         void *data)
{
    struct flow_keys *keys = data;

    // 重置
    memset(keys, 0, sizeof(*keys));

    // 解析 Ethernet 头
    keys->key.nw_proto = parse_ethhdr(skb, &keys->data);

    // 解析 IP 头
    if (keys->key.nw_proto == htons(ETH_P_IP)) {
        parse_ip4hdr(skb, keys);
    } else if (keys->key.nw_proto == htons(ETH_P_IPV6)) {
        parse_ip6hdr(skb, keys);
    }

    // 解析传输层
    switch (keys->key.ip_proto) {
    case IPPROTO_TCP:
        parse_tcphdr(skb, keys);
        break;
    case IPPROTO_UDP:
        parse_udphdr(skb, keys);
        break;
    }
}
```

### 3.2 parse_ethhdr()

```c
// net/core/flow_dissector.c:100
static __u16 parse_ethhdr(struct sk_buff *skb, struct flow_keys *keys)
{
    struct ethhdr *eth = eth_hdr(skb);

    // 获取协议
    __u16 proto = eth->h_proto;

    // VLAN 处理
    if (proto == htons(ETH_P_8021Q)) {
        struct vlan_hdr *vlan = (void *)(eth + 1);
        proto = vlan->h_vlan_encapsulated_proto;
    }

    return proto;
}
```

## 4. IPv4 解析

### 4.1 parse_ip4hdr()

```c
// net/core/flow_dissector.c:150
static void parse_ip4hdr(struct sk_buff *skb, struct flow_keys *keys)
{
    struct iphdr *iph = ip_hdr(skb);

    keys->key.src = iph->saddr;
    keys->key.dst = iph->daddr;
    keys->key.ip_proto = iph->protocol;
    keys->key.tos = iph->tos;
}
```

## 5. IPv6 解析

### 5.1 parse_ip6hdr()

```c
// net/core/flow_dissector.c:180
static void parse_ip6hdr(struct sk_buff *skb, struct flow_keys *keys)
{
    struct ipv6hdr *iph = ipv6_hdr(skb);

    keys->key.src = iph->saddr;
    keys->key.dst = iph->daddr;
    keys->key.ip_proto = iph->nexthdr;
    keys->key.tclass = iph->priority;
}
```

## 6. 使用场景

### 6.1 RPS (Receive Packet Steering)

```c
// net/core/dev.c
unsigned int get_rps_cpu(struct net_device *dev, struct sk_buff *skb)
{
    struct flow_keys keys;

    // 解析流
    skb_flow_dissector(&fcd, skb, &keys);

    // 计算 CPU
    return hash_33_to_cpu(hash, dev->num_rx_queues);
}
```

### 6.2 流量分类

```c
// net/sched/cls_flower.c
static int flow_classify(struct sk_buff *skb,
                         struct tcf_proto *tp,
                         struct tcf_result *res)
{
    struct flow_keys keys;

    skb_flow_dissector(&fcd, skb, &keys);

    // 匹配规则
    if (keys.key.dst == filter->dst)
        return TC_MATCH_OK;
}
```

## 7. 扩展

### 7.1 自定义解析器

```c
// 注册自定义解析器
static struct flow_dissector flow_dissector_my = {
    .get_key = my_key_func,
    .used_keys = (1 << FLOW_KEY_SRC_PORT) | (1 << FLOW_KEY_DST_PORT),
};

// 使用
skb_flow_dissector(&flow_dissector_my, skb, &keys);
```

### 7.2 skb_get_flow_keys()

```c
// 获取流的 keys
struct flow_keys *skb_get_flow_keys(struct sk_buff *skb)
{
    static struct flow_keys keys;

    skb_flow_dissector(&flow_dissector, skb, &keys);
    return &keys;
}
```
