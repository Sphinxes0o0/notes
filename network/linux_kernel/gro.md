# GRO - 通用接收卸载

## 1. 模块架构

### 1.1 功能概述

GRO (Generic Receive Offload) 是一种软件层面的 packet coalescing 技术，将多个相关的数据包合并为一个大的数据包，减少协议栈的处理开销。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/dev.c` | GRO 接收实现 |
| `net/ipv4/tcp_offload.c` | TCP GRO |
| `net/ipv6/ip6_offload.c` | IPv6 GRO |
| `include/linux/netdevice.h` | GRO 定义 |

## 2. GRO 结构

### 2.1 struct napi_gro_cb

```c
// include/linux/netdevice.h:970
struct napi_gro_cb {
    struct sk_buff *parent;        // GRO 组中的第一个 skb
    unsigned long age;            // 进入 GRO 的时间
    int           count;          // GRO 中的 skb 数量
    unsigned int  recurse_cnt;   // 递归计数
    __u32         flush:1;       // 强制刷新
    __u32         free:1;        // 释放 GRO 组
    __u32         encap_mark:1;  // 隧道封装标记
    structgro_result *ret;       // 合并结果
    struct sk_buff *last;        // 组中最后一个 skb
};
```

### 2.2 struct gro_list

```c
// net/core/dev.c:460
struct gro_list {
    struct list_head list;    // GRO 项链表
    int count;               // 项数量
};
```

## 3. GRO 接收流程

### 3.1 netif_receive_skb()

```c
// net/core/dev.c:5069
static int netif_receive_skb_core(struct sk_buff **pskb, int budget)
{
    struct sk_buff *skb = *pskb;
    struct packet_offload *ptype;
    __be16 type = skb->protocol;
    int ret;

    // 1. 处理 VLAN
    skb = vlan_hwaccel_rcv(skb);

    // 2. GRO 处理
    list_for_each_entry_rcu(ptype, &ptype_all, list) {
        if (ptype->type == type && ptype->callbacks.gro_receive)
            skb = ptype->callbacks.gro_receive(skb);
    }

    // 3. 协议分发
    ret = deliver_skb(skb, pt_prev, orig_dev);

    return ret;
}
```

### 3.2 napi_gro_receive()

```c
// net/core/dev.c:5160
gro_result napi_gro_receive(struct napi_struct *napi, struct sk_buff *skb)
{
    gro_result ret;

    // 1. 检查是否需要强制刷新
    if (skb_shinfo(skb)->gso_segs)
        goto normal;

    // 2. 查找匹配的 GRO 流
    pp = gro_find_receive(napi, skb);
    if (pp) {
        // 3. 合并到现有流
        skb = gro_list_receive(skb, pp);
        ret = pp->ret;
    } else {
        // 4. 创建新 GRO 流
        pp = gro_find_expand(napi, skb);
        if (!pp) {
            ret = GRO_DROP;
            goto out;
        }
        skb = gro_new_flow(skb, pp);
    }

out:
    return ret;

normal:
    // 不进行 GRO，直接处理
    return GRO_NORMAL;
}
```

## 4. TCP GRO

### 4.1 tcp_gro_receive()

```c
// net/ipv4/tcp_offload.c:220
struct sk_buff *tcp_gro_receive(struct list_head *head, struct sk_buff *skb)
{
    struct tcphdr *th = tcp_hdr(skb);
    struct sk_buff *pp;
    struct tcphdr *tp;
    int flush = 0;

    // 检查 TCP 头
    list_for_each_entry(pp, head, list) {
        tp = tcp_hdr(pp);

        // 检查是否匹配 (same 4-tuple, seq, flags)
        if (tcp_gro_check(tp, th)) {
            // 可以合并
            if (pp->len + skb->len > GRO_LEGACY_MAX_LEN)
                flush = 1;
            break;
        }
    }

    if (flush)
        goto out;

    // 合并
    if (pp) {
        // 将 skb 合并到 pp
        skb_gro_receive(pp, skb);
    } else {
        // 创建新流
        pp = skb;
        skb_gro_header_hard(skb, tcp_hdrlen(skb));
    }

out:
    return pp;
}
```

### 4.2 tcp_gro_complete()

```c
// net/ipv4/tcp_offload.c:250
int tcp_gro_complete(struct sk_buff *skb)
{
    struct tcphdr *th = tcp_hdr(skb);

    skb->mac_len = eth_hdr_len(skb);
    skb->inner_mac_len = skb->mac_len;
    skb->encapsulation = 0;

    // 更新 TCP 头信息
    th->window = htons(min(skb->len, th->window));

    // 计算校验和
    __tcp_hdrlen(skb);

    return 0;
}
```

## 5. GRO 刷新

### 5.1 gro_flush()

```c
// net/core/dev.c:5120
static void gro_flush(struct napi_gro_entries *entries, int flush)
{
    struct gro_list *gro_list = entries->gro_list;

    if (list_empty(gro_list))
        return;

    // 将所有 GRO 项移动到处理队列
    list_splice_init(gro_list, &entries->process_queue);

    // 标记需要处理
    entries->flush = 1;
}
```

### 5.2 强制刷新条件

```c
// 强制刷新 GRO 缓冲的条件:
// 1. 收到 TCP FIN 或 RST
// 2. GRO 缓冲达到最大数量 (GRO_MAX_SKBS)
// 3. 超过 GRO 最大时间 (GRO_TIMEOUT)
// 4. 包长度超过 GRO_LEGACY_MAX_LEN
// 5. 用户调用系统调用请求刷新
```

## 6. ETH GRO

### 6.1 napi_gro_frags()

```c
// net/core/dev.c:5240
gro_result napi_gro_frags(struct napi_struct *napi)
{
    struct sk_buff *skb;

    // GRO 用于分片包的重组
    // 直接传递给协议处理
    return GRO_NORMAL;
}
```

## 7. GRO 与 TSO

| 特性 | GRO | TSO (Transmit Segmentation Offload) |
|-----|-----|-------------------------------------|
| 方向 | 接收 | 发送 |
| 作用 | 合并小包为大包 | 分割大包为小包 |
| 位置 | 网络栈入口 | 网络栈出口 |
| 目的 | 减少处理开销 | 减少 CPU 开销 |

## 8. 使用示例

### 8.1 查看 GRO 状态

```bash
ethtool -k eth0 | grep generic-receive-offload
```

### 8.2 启用/禁用 GRO

```bash
ethtool -K eth0 gro on
ethtool -K eth0 gro off
```
