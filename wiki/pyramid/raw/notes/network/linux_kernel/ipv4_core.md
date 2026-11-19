# IPv4 协议栈核心

## 1. 模块架构

### 1.1 功能概述

IPv4 是互联网协议栈的核心，负责寻址和路由。本文档分析 Linux 内核中 IPv4 协议的核心实现。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv4/ip_input.c` | IP 数据包接收 |
| `net/ipv4/ip_output.c` | IP 数据包发送 |
| `net/ipv4/ip_forward.c` | IP 转发 |
| `net/ipv4/ip_fragment.c` | IP 分片/重组 |
| `net/ipv4/ipc_router/ipc_router.c` | IPC 路由 |

## 2. IP 头结构

### 2.1 struct iphdr

```c
// include/uapi/linux/ip.h:55
struct iphdr {
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u8    ihl:4,                // IP 头长度 (5-15)
            version:4;             // 版本 (4)
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u8    version:4,
            ihl:4;
#endif
    __u8    tos;                  // 服务类型
    __be16  tot_len;              // 总长度
    __be16  id;                   // 标识
    __be16  frag_off;             // 分片偏移
    __u8    ttl;                  // 生存时间
    __u8    protocol;             // 上层协议
    __sum16 check;                // 校验和
    __be32  saddr;                // 源地址
    __be32  daddr;                // 目的地址
};
```

### 2.2 IP 选项

```c
// include/uapi/linux/ip.h:76
#define IP_OPTIONS_MAX 40

struct ip_options {
    __be32         faddr;         // 第一个目标
    __be32         router;         // 路由器
    __u32          ptr;           // 选项指针
    __u32          nopts;         // 选项数量
    __u32          ndest;         // 目的数量
    unsigned char  __data[IP_OPTIONS_MAX];
};
```

## 3. IP 接收流程

### 3.1 ip_rcv()

```c
// net/ipv4/ip_input.c:568
int ip_rcv(struct sk_buff *skb, struct net_device *dev, struct packet_type *pt,
           struct net_device *orig_dev)
{
    const struct iphdr *iph;
    struct net *net;
    int len;

    // 1. 验证数据包
    if (!pskb_may_pull(skb, sizeof(struct iphdr)))
        goto drop;

    iph = ip_hdr(skb);

    // 2. 验证版本
    if (iph->version != 4)
        goto drop;

    // 3. 验证头长度
    if (unlikely(ip_fast_csum(iph, iph->ihl)))
        goto drop;

    // 4. 验证总长度
    len = ntohs(iph->tot_len);
    if (skb->len < len)
        goto drop;
    if (len < (iph->ihl << 2))
        goto drop;

    // 5. 移除分片偏移
    if (ip_is_fragment(iph))
        goto ip_defrag;

    // 6. 转发还是本地
    return ip_local_deliver(skb);

ip_defrag:
    return ip_defrag(skb);
drop:
    kfree_skb(skb);
    return NET_RX_DROP;
}
```

### 3.2 ip_local_deliver()

```c
// net/ipv4/ip_input.c:484
int ip_local_deliver(struct sk_buff *skb)
{
    struct iphdr *iph = ip_hdr(skb);
    int hash;

    // 处理分片
    if (ip_is_fragment(iph)) {
        if (ip_defrag(skb))
            return 0;
        iph = ip_hdr(skb);
    }

    // 调用协议处理
    hash = iph->protocol;
    return ip_local_deliver_finish(skb, hash);
}
```

### 3.3 ip_local_deliver_finish()

```c
// net/ipv4/ip_input.c:433
static int ip_local_deliver_finish(struct sk_buff *skb, int hash)
{
    struct net *net = dev_net(skb->dev);
    struct net_protocol *ipprot;
    int protocol = ip_hdr(skb)->protocol;

    // 查找协议处理函数
    ipprot = rcu_dereference(net->ipv4.ip_protocols[hash]);

    if (!ipprot) {
        // 未知协议，发送 ICMP
        icmp_send(skb, ICMP_DEST_UNREACH, ICMP_PROT_UNREACH, 0);
        goto drop;
    }

    // 移除 IP 头
    skb_pull(skb, ip_hdrlen(skb));

    // 调用协议处理
    ipprot->handler(skb);

    return 0;

drop:
    kfree_skb(skb);
    return NET_RX_DROP;
}
```

## 4. IP 发送流程

### 4.1 ip_queue_xmit()

```c
// net/ipv4/ip_output.c:453
int ip_queue_xmit(struct sock *sk, struct sk_buff *skb, struct flowi4 *fl4,
                   __u8 tos, __u32 opt, __u32 *generation)
{
    struct iphdr *iph;
    int err;

    // 1. 获取路由
    if (!dst)
        dst = ip_route_output_flow(net, fl4, sk);

    // 2. 设置 IP 头
    iph = ip_hdr(skb);
    iph->version = 4;
    iph->ihl = 5;
    iph->tos = tos;
    iph->tot_len = htons(skb->len);
    iph->id = htons(ip_id_count++);
    iph->frag_off = 0;
    iph->ttl = ip_select_ttl(inet, fl4);
    iph->protocol = sk->sk_protocol;
    iph->saddr = fl4->saddr;
    iph->daddr = fl4->daddr;

    // 3. 计算校验和
    ip_send_check(iph);

    // 4. 发送到设备
    return dst_output(net, sk, skb);
}
```

### 4.2 ip_send_check()

```c
// net/ipv4/ip_output.c:407
void ip_send_check(struct iphdr *iph)
{
    iph->check = 0;
    iph->check = ip_fast_csum(iph, iph->ihl);
}
```

## 5. IP 转发

### 5.1 ip_forward()

```c
// net/ipv4/ip_forward.c:45
int ip_forward(struct sk_buff *skb)
{
    struct iphdr *iph = ip_hdr(skb);
    struct dst_entry *dst = skb_dst(skb);
    struct net_device *dev = dst->dev;

    // 1. 检查 TTL
    if (iph->ttl <= 1)
        goto drop;

    // 2. 发送 ICMP 重定向
    if (IPCB(skb)->flags & IPSKB_DOREDIRECT)
        ip_rt_send_redirect(skb);

    // 3. 减少 TTL
    iph->ttl--;

    // 4. 修改校验和
    ip_dec_total_len(skb);

    // 5. 转发
    return ip_forward_finish(skb);

drop:
    kfree_skb(skb);
    return NET_RX_DROP;
}
```

## 6. 分片与重组

### 6.1 ip_fragment()

```c
// net/ipv4/ip_fragment.c:540
int ip_fragment(struct net *net, struct sock *sk, struct sk_buff *skb,
                 unsigned int mtu)
{
    struct iphdr *iph;
    struct sk_buff *frag;
    int left, len, offset;

    iph = ip_hdr(skb);

    // 分片大小
    frag_size = (mtu - sizeof(struct iphdr)) & ~7;

    // 创建分片
    offset = 0;
    left = skb->len - sizeof(struct iphdr);

    while (left > 0) {
        len = min(left, frag_size);

        // 复制分片
        frag = skb_copy(skb, GFP_ATOMIC);
        if (!frag) return -ENOMEM;

        // 调整分片头
        iph = ip_hdr(frag);
        iph->frag_off = htons(offset >> 3);
        if (left > len)
            iph->frag_off |= htons(IP_MF);

        iph->tot_len = htons(len + sizeof(struct iphdr));
        iph->id = htons(ip_id);

        // 发送分片
        ip_send_check(iph);
        dst_output(net, sk, frag);

        offset += len;
        left -= len;
    }

    return 0;
}
```

### 6.2 ip_defrag()

```c
// net/ipv4/ip_fragment.c:180
struct sk_buff *ip_defrag(struct net *net, struct sk_buff *skb, u32 user)
{
    struct ipq *qp;
    struct sk_buff *head, *prev;
    struct iphdr *iph;
    int err;

    iph = ip_hdr(skb);

    // 查找或创建分片队列
    qp = inet_frag_lookup(net, &ip4_frags, &iph->id, iph->saddr,
                           iph->daddr, iph->protocol);
    if (IS_ERR(qp))
        goto drop;

    // 添加到分片队列
    spin_lock(&qp->q.lock);
    err = ip_frag_queue(qp, skb);
    spin_unlock(&qp->q.lock);

    // 如果完整则重组
    if (err == 0)
        return ip_frag_reasm(net, qp, user);

    return NULL;

drop:
    kfree_skb(skb);
    return NULL;
}
```

## 7. 协议注册

### 7.1 inet_add_protocol()

```c
// net/ipv4/protocol.c:128
int inet_add_protocol(const struct net_protocol *prot, unsigned int num)
{
    if (!prot->init(net))
        return -EBUSY;

    net->ipv4.ip_protocols[num] = prot;
    return 0;
}
```

### 7.2 注册的协议

```c
// net/ipv4/protocol.c:45
static const struct net_protocol tcp_protocol = {
    .handler    = tcp_v4_rcv,
    .err_handler = tcp_v4_err,
    .no_policy  = 1,
};

static const struct net_protocol udp_protocol = {
    .handler    = udp_rcv,
    .err_handler = udp_err,
    .no_policy  = 1,
};

static const struct net_protocol icmp_protocol = {
    .handler    = icmp_rcv,
    .err_handler = NULL,
    .no_policy  = 1,
};
```
