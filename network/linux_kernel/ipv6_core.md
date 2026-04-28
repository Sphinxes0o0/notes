# IPv6 协议栈核心

## 1. 模块架构

### 1.1 功能概述

IPv6 是下一代互联网协议，提供更大的地址空间、简化的头部和内置安全支持。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv6/ipv6_sockglue.c` | IPv6 socket 选项 |
| `net/ipv6/addrconf.c` | 地址配置 (SLAAC, DAD) |
| `net/ipv6/ndisc.c` | 邻居发现 |
| `net/ipv6/route.c` | IPv6 路由 |
| `net/ipv6/ip6_offload.c` | IPv6 分片/重组 |

## 2. IPv6 头结构

### 2.1 struct ipv6hdr

```c
// include/uapi/linux/ipv6.h:12
struct ipv6hdr {
    __u8    priority:4,       // 流量类别
            version:4;         // 版本 (6)
    __u8    flow_lbl[3];     // 流标签
    __be16  payload_len;     // 负载长度
    __u8    nexthdr;         // 下一头部
    __u8    hop_limit;       // 跳数限制 (TTL)
    struct in6_addr  saddr;  // 源地址
    struct in6_addr  daddr;  // 目的地址
};
```

## 3. IPv6 扩展头

### 3.1 扩展头类型

| 值 | 类型 |
|---|------|
| 0 | Hop-by-Hop Options |
| 6 | TCP |
| 17 | UDP |
| 43 | Routing |
| 44 | Fragment |
| 50 | ESP |
| 51 | AH |
| 59 | No Next Header |
| 60 | Destination Options |

### 3.2 跳过扩展头

```c
// net/ipv6/exthdrs.c:398
int ipv6_skip_exthdr(const struct sk_buff *skb, int start, __be16 *nexthdrp,
                      struct ipv6_opt_hdr **opthdr)
{
    while (likely(proto)) {
        switch (proto) {
        case NEXTHDR_HOP:
            // 处理 Hop-by-Hop 选项
            break;
        case NEXTHDR_ROUTING:
            // 处理路由头
            break;
        case NEXTHDR_FRAGMENT:
            // 处理分片头
            break;
        default:
            // 返回下一个头和位置
            return -1;
        }
    }
    return -1;
}
```

## 4. IPv6 地址类型

### 4.1 地址分类

```c
// include/net/addrconf.h:350
enum {
    IPV6_ADDR_ANY           = 0x0000U,
    IPV6_ADDR_UNICAST       = 0x0001U,
    IPV6_ADDR_MULTICAST      = 0x0002U,
    IPV6_ADDR_ANYCAST        = 0x0004U,
    IPV6_ADDR_LOOPBACK       = 0x0010U,
    IPV6_ADDR_LINKLOCAL     = 0x0020U,
    IPV6_ADDR_SITELOCAL     = 0x0040U,
    IPV6_ADDR_COMPATv4      = 0x0080U,
    IPV6_ADDR_SCOPE_MASK    = 0x00f0U,
    IPV6_ADDR_MAPPED        = 0x1000U,  // ::ffff:x.x.x.x
    IPV6_ADDR_RESERVED      = 0x2000U,
};
```

### 4.2 地址检测

```c
// include/net/addrconf.h:484
static inline bool ipv6_addr_type(const struct in6_addr *addr)
{
    __be32 st;

    st = addr->s6_addr32[0];

    // 多播
    if ((st & htonl(0xff000000)) == htonl(0xff000000))
        return IPV6_ADDR_MULTICAST;

    // 循环地址
    if (st == 0 && addr->s6_addr32[1] == 0 &&
        addr->s6_addr32[2] == 0 && addr->s6_addr32[3] == htonl(1))
        return IPV6_ADDR_LOOPBACK;

    // 映射地址
    if (st == 0 && addr->s6_addr32[1] == 0 &&
        addr->s6_addr32[2] == htonl(0xffff))
        return IPV6_ADDR_MAPPED | IPV6_ADDR_UNICAST;

    // 链路本地
    if ((st & htonl(0xffc00000)) == htonl(0xfe800000))
        return IPV6_ADDR_LINKLOCAL | IPV6_ADDR_UNICAST;

    // 站点本地
    if ((st & htonl(0xffc00000)) == htonl(0xfec00000))
        return IPV6_ADDR_SITELOCAL | IPV6_ADDR_UNICAST;

    return IPV6_ADDR_UNICAST;
}
```

## 5. IPv6 接收流程

### 5.1 ipv6_rcv()

```c
// net/ipv6/ip6_input.c:126
int ipv6_rcv(struct sk_buff *skb, struct net_device *dev, struct packet_type *pt,
             struct net_device *orig_dev)
{
    const struct ipv6hdr *hdr;
    struct net *net = dev_net(dev);
    u extends;

    // 1. 验证版本
    if (ipv6_hdr(skb)->version != 6)
        goto drop;

    // 2. 验证头长度
    if (!pskb_may_pull(skb, sizeof(*hdr)))
        goto drop;

    hdr = ipv6_hdr(skb);

    // 3. 验证 hop limit
    if (hdr->hop_limit == 0)
        goto drop;

    // 4. 转发还是本地
    return NF_HOOK(NFPROTO_IPV6, NF_INET_PRE_ROUTING,
                   net, NULL, skb, dev, NULL, ip6_rcv_finish);

drop:
    kfree_skb(skb);
    return NET_RX_DROP;
}
```

### 5.2 ip6_rcv_finish()

```c
// net/ipv6/ip6_input.c:96
static int ip6_rcv_finish(struct sk_buff *skb)
{
    struct net *net = dev_net(skb->dev);
    const struct ipv6hdr *hdr = ipv6_hdr(skb);
    struct rt6_info *rt;

    // 1. 路由查找
    if (!skb_dst(skb)) {
        int err = ip6_route_input(skb);
        if (err)
            goto drop;
    }

    // 2. 本地还是转发
    rt = (struct rt6_info *)skb_dst(skb);
    if (rt->rt6i_flags & RTF_LOCAL) {
        // 本地交付
        return ip6_local_deliver(skb);
    }

    // 3. 转发
    if (rt->rt6i_flags & RTF_GATEWAY) {
        return ip6_forward(skb);
    }

drop:
    kfree_skb(skb);
    return NET_RX_DROP;
}
```

## 6. IPv6 发送流程

### 6.1 ip6_xmit()

```c
// net/ipv6/ip6_output.c:127
int ip6_xmit(struct sock *sk, struct sk_buff *skb, struct flowi6 *fl6,
              __u32 mark, __u32 hop_limit, __u32 tclass, __u32 flowlabel)
{
    struct net *net = sock_net(sk);
    struct ipv6_pinfo *np = inet6_sk(sk);
    struct dst_entry *dst;
    struct ipv6hdr *hdr;

    // 1. 获取路由
    if (!dst)
        dst = ip6_route_output(net, sk, fl6);

    // 2. 设置 IPv6 头
    hdr = ipv6_hdr(skb);
    hdr->version = 6;
    hdr->priority = tclass;
    hdr->flow_lbl[0] = (flowlabel >> 16) & 0xff;
    hdr->flow_lbl[1] = (flowlabel >> 8) & 0xff;
    hdr->flow_lbl[2] = flowlabel & 0xff;
    hdr->payload_len = htons(skb->len - sizeof(*hdr));
    hdr->nexthdr = fl6->flow6_proto;
    hdr->hop_limit = hop_limit ? hop_limit : np->hop_limit;
    hdr->saddr = fl6->saddr;
    hdr->daddr = fl6->daddr;

    // 3. 发送到设备
    return dst_output(net, sk, skb);
}
```

## 7. 分片与重组

### 7.1 IPv6 分片

IPv6 只有源节点进行分片，中间路由器不进行分片。

```c
// net/ipv6/ip6_output.c:892
static int ip6_fragment(struct net *net, struct sock *sk, struct sk_buff *skb,
                         struct dst_entry *dst, bool *failed)
{
    struct ipv6hdr *hdr;
    struct frag_hdr *fh;
    unsigned int mtu, hlen, left, len;
    struct sk_buff *frag;
    __be32 frag_id;

    // 1. 计算 MTU
    mtu = dst_mtu(dst) - sizeof(struct frag_hdr);

    // 2. 分片
    left = skb->len - sizeof(*hdr);
    frag_id = ipv6_select_ident(net, hdr);

    while (left > 0) {
        len = min(left, mtu);

        // 创建分片 skb
        frag = skb_copy(skb, GFP_ATOMIC);
        if (!frag) return -ENOMEM;

        // 设置分片头
        fh = (struct frag_hdr *)skb_push(frag, sizeof(*fh));
        fh->nexthdr = hdr->nexthdr;
        fh->reserved = 0;
        fh->frag_off = htons(offset);
        fh->identification = frag_id;

        // 调整长度
        frag->len = len + sizeof(*hdr) + sizeof(*fh);
        frag->data = skb->data + sizeof(*hdr) + sizeof(*fh);

        // 发送
        ip6_send(frag);

        left -= len;
        offset += len;
    }
}
```

## 8. 协议注册

### 8.1 IPv6 协议表

```c
// net/ipv6/protocol.c
struct inet6_protocol {
    int (*handler)(struct sk_buff *skb);
    int (*err_handler)(struct sk_buff *skb, struct inet6_skb_parm *opt,
                       u8 type, u8 code, int offset, __be32 info);
    int flags;  // INET6_PROTO_NOPOLICY, etc.
};

static const struct inet6_protocol tcpv6_protocol = {
    .handler    = tcp_v6_rcv,
    .err_handler = tcp_v6_err,
    .flags      = INET6_PROTO_NOPOLICY,
};

static const struct inet6_protocol udpv6_protocol = {
    .handler    = udpv6_rcv,
    .err_handler = udpv6_err,
    .flags      = INET6_PROTO_NOPOLICY,
};
```

## 9. IPv6 Socket 选项

### 9.1 IPv6 特有选项

```c
// IPv6 socket 选项
IPV6_CHECKSUM       // 校验和位置
IPV6_NEXTHDR        // 下一个头部
IPV6_HOPLIMIT       // 跳数限制
IPV6_HOPOPTS        // Hop-by-Hop 选项
IPV6_DSTOPTS        // 目的选项
IPV6_RTHDR          // 路由头
IPV6_RTHDRDSTOPTS   // 路由头之前的目的选项
IPV6_MULTICAST_HOPS // 多播跳数
IPV6_MULTICAST_IF   // 多播接口
IPV6_MULTICAST_LOOP // 多播环回
IPV6_RECVHOPLIMIT   // 接收跳数限制
IPV6_RECVPKTINFO    // 接收包信息
IPV6_PKTINFO        // 发送包信息
IPV6_FLOWINFO       // 接收流信息
IPV6_FLOWLABEL      // 流标签
IPV6_JOIN_GROUP      // 加入多播组
IPV6_LEAVE_GROUP     // 离开多播组
IPV6_V6ONLY         // 仅 IPv6
```

### 9.2 flowlabel 管理

```c
// net/ipv6/ip6_flowlabel.c
static int ipv6_flowlabel_opt(struct sock *sk, char __user *optval, int optlen)
{
    // FLOWLABEL 操作:
    // IPV6_FL_A_GET - 获取
    // IPV6_FL_A_PUT - 释放
    // IPV6_FL_A_RENEW - 续订
}
```
