# IPv6 NDisc 邻居发现

## 1. 模块架构

### 1.1 功能概述

NDisc (Neighbor Discovery Protocol) 是 IPv6 的核心协议，实现了地址解析、路由器发现、重复地址检测等功能。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv6/ndisc.c` | NDisc 实现 (约 2000 行) |
| `include/net/ndisc.h` | NDisc 定义 |
| `include/net/addrconf.h` | 地址配置 |

## 2. NDisc 消息类型

### 2.1 ICMPv6 类型

| 类型 | 名称 | 用途 |
|-----|------|-----|
| 133 | Router Solicitation (RS) | 主机请求路由器配置 |
| 134 | Router Advertisement (RA) | 路由器通告前缀/路由 |
| 135 | Neighbor Solicitation (NS) | 地址解析 + DAD |
| 136 | Neighbor Advertisement (NA) | 地址解析回复 + DAD |
| 137 | Redirect | 更好的第一跳通知 |

### 2.2 NDisc 消息结构

```c
// include/net/ndisc.h
struct nd_msg {
    struct icmp6hdr icmph;
    struct in6_addr target;    // NS/NA 的目标地址
    __u8        opt[];       // 选项
};

struct ra_msg {
    struct icmp6hdr icmph;
    __be32        reachable_time;  // 可达时间
    __be32        retrans_timer;   // 重传定时器
};

struct rs_msg {
    struct icmp6hdr icmph;
    __u8        opt[];
};
```

### 2.3 NDisc 选项

```c
// include/net/ndisc.h
struct nd_opt_hdr {
    __u8    nd_opt_type;   // 选项类型
    __u8    nd_opt_len;    // 长度 (8字节单位)
};

#define ND_OPT_SOURCE_LL_ADDR      1   // 源链路层地址
#define ND_OPT_TARGET_LL_ADDR     2   // 目标链路层地址
#define ND_OPT_PREFIX_INFO         3   // 前缀信息
#define ND_OPT_MTU                5   // MTU
#define ND_OPT_NONCE              14  // DAD 随机数
#define ND_OPT_ROUTE_INFO         24  // 路由信息
#define ND_OPT_RDNSS              25  // 递归 DNS
#define ND_OPT_DNSSL              31  // DNS 搜索列表
```

## 3. 邻居请求 (NS)

### 3.1 ndisc_send_ns()

```c
// net/ipv6/ndisc.c:653
void ndisc_send_ns(struct net_device *dev, const struct in6_addr *solicit,
                  const struct in6_addr *daddr, const struct in6_addr *saddr,
                  u64 nonce)
{
    struct sk_buff *skb;

    // 创建 NS 包
    skb = ndisc_ns_create(dev, solicit, saddr, nonce);
    if (skb)
        ndisc_send_skb(skb, daddr, saddr);
}

// ns 创建
static struct sk_buff *ndisc_ns_create(struct net_device *dev, ...)
{
    struct nd_msg *msg;

    skb = alloc_skb(LL_ALLOCATED_SPACE(dev) + sizeof(*msg), GFP_ATOMIC);
    if (!skb) return NULL;

    // 添加 Eth + IPv6 头
    skb_reserve(skb, LL_RESERVED_SPACE(dev));
    eth_hdr(skb)->h_proto = htons(ETH_P_IPV6);

    // 添加 ICMPv6 头
    msg = skb_put(skb, sizeof(*msg));
    msg->icmph.icmp6_type = NDISC_NEIGHBOUR_SOLICITATION;
    msg->target = *target;

    // 添加选项 (源链路层地址)
    if (saddr)
        ndisc_fill_addr_option(skb, ND_OPT_SOURCE_LL_ADDR, dev->dev_addr);

    return skb;
}
```

### 3.2 ndisc_recv_ns()

```c
// net/ipv6/ndisc.c:787
static void ndisc_recv_ns(struct sk_buff *skb)
{
    struct nd_msg *msg = (struct nd_msg *)skb->data;
    struct inet6_ifaddr *ifp;
    bool dad = ipv6_addr_any(saddr);  // DAD 检测

    // DAD: 目标是试探性地址
    if (dad) {
        // 检查 DAD
        if (ipv6_addr_is_solict_mult(daddr)) {
            // 必须是 solicitation-node 多播
            if (nonce && ifp->dad_nonce == nonce) {
                // 环路检测，忽略
                goto out;
            }
            // 地址冲突
            addrconf_dad_failure(skb, ifp);
        }
    } else {
        // 地址解析：查找邻居
        neigh = __neigh_lookup(&nd_tbl, &msg->target, dev);
        if (neigh) {
            // 更新邻居
            neigh_update(neigh, lladdr);
            // 发送 NA
            ndisc_send_na(dev, saddr, &msg->target, ...);
        }
    }
}
```

## 4. 邻居通告 (NA)

### 4.1 ndisc_send_na()

```c
// net/ipv6/ndisc.c:524
void ndisc_send_na(struct net_device *dev, const struct in6_addr *daddr,
                  const struct in6_addr *solicited_addr,
                  bool router, bool solicited, bool override, bool inc_opt)
{
    struct sk_buff *skb;
    struct nd_msg *msg;

    skb = ndisc_na_create(dev, solicited_addr, inc_opt, router,
                         solicited, override);
    if (!skb) return;

    ndisc_send_skb(skb, daddr, solicited_addr ? solicited_addr : dev->dev_addr);
}

static struct sk_buff *ndisc_na_create(struct net_device *dev, ...)
{
    msg->icmph.icmp6_router = router;       // 是否为路由器
    msg->icmph.icmp6_solicited = solicited;  // 是否为 NS 响应
    msg->icmph.icmp6_override = override;    // 是否覆盖缓存
}
```

### 4.2 ndisc_recv_na()

```c
// net/ipv6/ndisc.c:988
static void ndisc_recv_na(struct sk_buff *skb)
{
    struct nd_msg *msg = (struct nd_msg *)skb->data;
    struct neighbour *neigh;

    // 查找邻居条目
    neigh = __neigh_lookup(&nd_tbl, &msg->target, dev);
    if (!neigh) {
        // 创建新条目
        neigh = neigh_add(&nd_tbl, &msg->target, dev);
    }

    // 更新邻居
    if (solicited) {
        // NS 响应 -> REACHABLE
        neigh->nud_state = NUD_REACHABLE;
        neigh_update(neigh, lladdr);
    } else {
        // 非请求 NA -> STALE
        neigh->nud_state = NUD_STALE;
    }
}
```

## 5. 路由器发现

### 5.1 RS 发送

```c
// net/ipv6/ndisc.c:550
void ndisc_send_rs(struct net_device *dev, const struct in6_addr *saddr,
                  const struct in6_addr *daddr)
{
    struct sk_buff *skb;
    struct rs_msg *msg;

    skb = ndisc_rs_create(dev, saddr, daddr);
    if (!skb) return;

    ndisc_send_skb(skb, daddr, saddr);
}
```

### 5.2 RA 处理

```c
// net/ipv6/ndisc.c:1232
static void ndisc_router_discovery(struct sk_buff *skb)
{
    struct ra_msg *msg = (struct ra_msg *)skb->data;

    // 1. 验证源地址是链路本地
    if (!ipv6_addr_is_lladdr(&ipv6_hdr(skb)->saddr))
        return;

    // 2. 更新默认路由
    if (msg->icmph.icmp6_router)
        rt6_add_dflt_router(skb->dev, &ipv6_hdr(skb)->saddr);

    // 3. 更新设备标志
    if (msg->icmph.icmp6_flags & ND_RA_FLAG_MANAGED)
        idev->if_flags |= IF_RA_MANAGED;
    if (msg->icmph.icmp6_flags & ND_RA_FLAG_OTHER)
        idev->if_flags |= IF_RA_OTHERCONF;

    // 4. 更新定时器参数
    idev->nd_parms->reachable_time = ntohl(msg->reachable_time);
    idev->nd_parms->retrans_time = ntohl(msg->retrans_timer);

    // 5. 处理前缀选项
    for (each option) {
        if (option->nd_opt_type == ND_OPT_PREFIX_INFORMATION)
            addrconf_prefix_rcv(dev, option);
    }
}
```

## 6. Solicited-Node 多播地址

### 6.1 计算公式

```
ff02::1:ffXX:XXXX
  ││      │ └────┘└────┘
  ││      │    │      └─ 后 24 位 = 目标地址的后 24 位
  ││      └─── 固定: ffXX:XXXX
  │└──────────── 固定前缀
  └────────────── 链路本地多播组 (ff02::1)
```

### 6.2 生成函数

```c
// include/net/addrconf.h:484
static inline void addrconf_addr_solict_mult(const struct in6_addr *addr,
                                            struct in6_addr *solicited)
{
    ipv6_addr_set(solicited,
              htonl(0xFF020000), 0,
              htonl(0x1),
              htonl(0xFF000000) | addr->s6_addr32[3]);
}
```

## 7. 安全性

### 7.1 Hop Limit 验证

所有 NDisc 消息必须在本地链路发送，Hop Limit 必须为 255：

```c
// ndisc.c:1804
int ndisc_rcv(struct sk_buff *skb)
{
    // 1. 验证 hop limit = 255
    if (ipv6_hdr(skb)->hop_limit != 255)
        return;

    // 2. 验证 ICMPv6 code = 0
    if (msg->icmph.icmp6_code != 0)
        return;

    // 3. 分发到处理函数
    switch (msg->icmph.icmp6_type) {
    case NDISC_NEIGHBOUR_SOLICITATION:
        ndisc_recv_ns(skb);
        break;
    // ...
    }
}
```

### 7.2 DAD 随机数 (RFC 7527)

```c
// 用于防止多接口场景下的 DAD 误判
// 随机数在 NS 中携带
// 收到匹配的 NA 时比较随机数
```

## 8. 与 IPv4 ARP 对比

| 特性 | IPv6 NDisc | IPv4 ARP |
|-----|-----------|---------|
| 协议 | ICMPv6 (IP 协议 58) | 独立 Ethernet 类型 |
| 消息 | RS/RA/NS/NA/Redirect | ARP Request/Reply |
| 多播组 | Solicited-node | 广播 (ff:ff:ff:ff:ff:ff) |
| DAD | 内置 NS/NA 交换 | 无 |
| 路由器发现 | RS/RA | Proxy ARP 或 DHCP |
| 扩展性 | TLV 选项 | 固定格式 |
| 安全 | SEND (RFC 3971) | 无标准安全 |
