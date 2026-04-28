# IPv4 UDP 实现

## 1. 模块架构

### 1.1 功能概述

UDP 是无连接的不可靠传输协议，提供简单的数据包传输服务。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv4/udp.c` | UDP 实现 (约 4000 行) |
| `include/linux/udp.h` | UDP Socket 定义 |
| `include/net/udp.h` | 核心 UDP 定义 |

## 2. UDP 头结构

### 2.1 struct udphdr

```c
// include/uapi/linux/udp.h:8
struct udphdr {
    __be16  source;         // 源端口
    __be16  dest;           // 目的端口
    __be16  len;            // UDP 长度
    __sum16 check;          // 校验和 (0 表示禁用)
};
```

## 3. UDP Socket 结构

### 3.1 struct udp_sock

```c
// include/linux/udp.h:53
struct udp_sock {
    struct inet_sock inet;  // 基类 (必须第一)

    /* 端口哈希 */
    __u16  udp_port_hash;   // 本地端口
    __u16  udp_portaddr_hash;  // 本地地址哈希

    unsigned long  udp_flags;     // UDP 标志
    int          pending;         // 待发送帧

    __u8  encap_type;       // 封装类型

    /* UDP 4 元组哈希 */
    __u16  udp_lrpa_hash;

    __u16  len;            // 待发送帧总长度
    __u16  gso_size;       // GSO 大小

    /* UDP-Lite */
    __u16  pcslen;         // 校验和覆盖长度
    __u16  pcrlen;         // 校验和要求长度

    /* 封装回调 */
    int  (*encap_rcv)(struct sock *sk, struct sk_buff *skb);
    void (*encap_err_rcv)(struct sock *sk, struct sk_buff *skb, ...);
    int  (*encap_err_lookup)(struct sock *sk, struct sk_buff *skb);
    void (*encap_destroy)(struct sock *sk);

    /* GRO 回调 */
    struct sk_buff *(*gro_receive)(struct sock *sk, struct list_head *head,
                                   struct sk_buff *skb);
    int  (*gro_complete)(struct sock *sk, struct sk_buff *skb, int nhoff);

    /* 接收队列 */
    struct udp_prod_queue *udp_prod_queue;
    struct sk_buff_head    reader_queue;
    int                   forward_deficit;
    int                   forward_threshold;
};
```

## 4. 端口哈希表

### 4.1 UDP 哈希表结构

```c
// include/net/udp.h:60
struct udp_hslot {
    union {
        struct hlist_head head;
        struct hlist_nulls_head nulls_head;  // RCU 安全
    };
    int    count;          // 槽中 socket 数量
    spinlock_t lock;       // 保护修改
};

struct udp_hslot_main {
    struct udp_hslot hslot;
    u32 hash4_cnt;       // hash4 中的 socket 数量
};

struct udp_table {
    struct udp_hslot      *hash;    // 主哈希: (local port)
    struct udp_hslot_main *hash2;   // 次哈希: (local port, local addr)
    struct udp_hslot      *hash4;   // 4 元组哈希: (local port, local addr, remote port, remote addr)
    unsigned int          mask;      // 槽数 - 1
    unsigned int          log;      // log2(槽数)
};
```

### 4.2 哈希表初始化

```c
// net/ipv4/udp.c:3811
void __init udp_table_init(struct udp_table *table, const char *name)
{
    unsigned int slot_size = sizeof(struct udp_hslot) +
                            sizeof(struct udp_hslot_main) +
                            udp_hash4_slot_size();

    // 分配哈希表
    table->hash = alloc_large_system_hash(name, slot_size,
                                          uhash_entries, 21, 0,
                                          &table->log, &table->mask,
                                          UDP_HTABLE_SIZE_MIN,
                                          UDP_HTABLE_SIZE_MAX);

    // 初始化每个槽
    for (i = 0; i <= table->mask; i++) {
        INIT_HLIST_HEAD(&table->hash[i].head);
        spin_lock_init(&table->hash[i].lock);
    }
}
```

## 5. UDP 接收

### 5.1 udp_rcv()

```c
// net/ipv4/udp.c:2934
int udp_rcv(struct sk_buff *skb)
{
    return __udp4_lib_rcv(skb, dev_net(skb->dev)->ipv4.udp_table, IPPROTO_UDP);
}
```

### 5.2 __udp4_lib_rcv()

```c
// net/ipv4/udp.c:2692
int __udp4_lib_rcv(struct sk_buff *skb, struct udp_table *udptable, int proto)
{
    struct udphdr *uh;
    struct sock *sk;
    unsigned short ulen;
    __be32 saddr, daddr;
    struct rtable *rt;

    // 1. 验证 IP 头
    if (!pskb_may_pull(skb, sizeof(struct udphdr)))
        goto drop;

    // 2. 获取 UDP 头
    uh = udp_hdr(skb);
    ulen = ntohs(uh->len);

    // 3. 验证长度
    if (ulen > skb->len || ulen < sizeof(*uh))
        goto drop;

    // 4. 移除 UDP 头
    skb_pull(skb, sizeof(struct udphdr));

    // 5. 提取地址
    saddr = ip_hdr(skb)->saddr;
    daddr = ip_hdr(skb)->daddr;

    // 6. 查找 socket
    sk = __udp4_lib_lookup_skb(skb, uh->source, uh->dest, udptable);

    if (sk) {
        // 7. 发送到 socket
        raw_rcv(sk, skb);
        sock_put(sk);
        return 0;
    }

    // 8. 无 socket，发送 ICMP
    icmp_send(skb, ICMP_DEST_UNREACH, ICMP_PORT_UNREACH, 0);

drop:
    kfree_skb(skb);
    return 0;
}
```

### 5.3 Socket 查找

```c
// net/ipv4/udp.c:677
struct sock *__udp4_lib_lookup_skb(struct sk_buff *skb, __be16 sport, __be16 dport,
                                   struct udp_table *udptable)
{
    return __udp4_lib_lookup(dev_net(skb->dev), sport, dport,
                             &ip_hdr(skb)->saddr, &ip_hdr(skb)->daddr,
                             skb->dev->ifindex, udptable);
}

// net/ipv4/udp.c:677
struct sock *__udp4_lib_lookup(struct net *net, __be16 sport, __be16 dport,
                               __be32 saddr, __be32 daddr, int dif, int sdif,
                               struct udp_table *udptable)
{
    // 1. 计算哈希
    u32 hash2 = ipv4_portaddr_hash(net, htonl(INADDR_ANY), sport);
    u32 slot = hash2 & udptable->mask;

    // 2. 在 hash2 中查找
    sk = udp4_lib_lookup2(net, daddr, dport, saddr, sport, dif, sdif, udptable);

    if (sk)
        return sk;

    // 3. 在 hash 中查找 (仅端口)
    hash2 = udp_hashfn(net, sport, udptable->mask);
    slot = hash2 & udptable->mask;

    return udp_hash_lookup(udptable, sport);
}

// 计算分数
static int compute_score(struct sock *sk, struct net *net,
                         __be32 saddr, __be16 sport,
                         __be32 daddr, unsigned short hnum, int dif)
{
    int score = -1;

    if (!net_eq(net, sock_net(sk)))      return -1;
    if (udp_sk(sk)->udp_port_hash != hnum) return -1;
    if (sk->sk_rcv_saddr != daddr)       return -1;

    score = (sk->sk_family == PF_INET) ? 2 : 1;

    if (inet->inet_daddr) {
        if (inet->inet_daddr != saddr) return -1;
        score += 4;
    }

    return score;
}
```

## 6. UDP 发送

### 6.1 udp_sendmsg()

```c
// net/ipv4/udp.c:1270
int udp_sendmsg(struct sock *sk, struct msghdr *msg, size_t len)
{
    struct inet_sock *inet = inet_sk(sk);
    struct udp_sock *up = udp_sk(sk);
    struct flowi4 fl4;
    struct dst_entry *dst;
    int connected = 0;
    __be32 daddr, faddr;
    __be16 dport;
    u8 tos;
    int err;
    int cork_req = up->corkflag || (msg->msg_flags & MSG_MORE);

    // 1. 获取目标地址
    if (msg->msg_name) {
        struct sockaddr_in *usin = (struct sockaddr_in *)msg->msg_name;
        daddr = usin->sin_addr.s_addr;
        dport = usin->sin_port;
        connected = 1;
    }

    // 2. 获取路由
    if (!connected) {
        dst = udp选题_destination(sk, daddr, dport, &fl4);
        if (IS_ERR(dst)) return PTR_ERR(dst);
    }

    // 3. 处理 UDP_CORK
    if (up->corkflag || (msg->msg_flags & MSG_CORK)) {
        up->pending |= MSG_MORE;
        up->len += len;
        return 0;
    }

    // 4. 发送
    return udp_send_skb(sk, &fl4, msg, len);

out:
    release_sock(sk);
    return err;
}
```

### 6.2 udp_send_skb()

```c
// net/ipv4/udp.c:1117
static int udp_send_skb(struct sock *sk, struct flowi4 *fl4,
                         struct msghdr *msg, size_t len)
{
    struct udp_sock *up = udp_sk(sk);
    struct sk_buff *skb;
    struct udphdr *uh;
    int err;

    // 1. 分配 skb
    skb = sock_wmalloc(sk, len + sizeof(*uh), 0, GFP_KERNEL);
    if (!skb) return -ENOMEM;

    // 2. 设置 UDP 头
    uh = udp_hdr(skb);
    uh->source = inet->inet_sport;
    uh->dest = fl4->fl4_dport;
    uh->len = htons(len + sizeof(*uh));

    // 3. 计算校验和
    if (uh->check) {
        // 计算 UDP 伪头校验和
        uh->check = ~csum_tcpudp_magic(fl4->saddr, fl4->daddr,
                                        len + sizeof(*uh), IPPROTO_UDP, 0);
        if (uh->check == 0) uh->check = CSUM_MANGLED_0;
    }

    // 4. 发送
    err = ip_send_skb(dev_net(skb->dev), skb);
    if (err) return err;

    out:
    return err;
}
```

## 7. UDP-Lite

### 7.1 UDP-Lite 头

UDP-Lite 使用与 UDP 相同的头，但 `len` 字段表示"校验和覆盖长度"而非总长度。

### 7.2 校验和覆盖

```c
// net/ipv4/udplite.c
static int udplite_csum(struct sk_buff *skb)
{
    // UDP-Lite 可以部分校验覆盖
    // RFC 3828
    return 0;
}
```

## 8. GRO 支持

### 8.1 UDP GRO 接收

```c
// net/ipv4/udp_offload.c
static struct sk_buff *udp4_gro_receive(struct sock *sk, struct list_head *head,
                                        struct sk_buff *skb)
{
    // UDP 支持 GRO (Generic Receive Offload)
    // 可以合并相同 4 元组的 UDP 包
    return udp_lib_gro_receive(sk, head, skb);
}
```

## 9. 封装支持

### 9.1 封装类型

```c
#define UDP_ENCAP_UDPINUDP     2  // RFC 3948
#define UDP_ENCAP_ESPINUDP    1  // ESP over UDP
#define UDP_ENCAP_ESPINUDP_NON_IKE  2  // ESP over UDP without IKE
```

### 9.2 封装回调

```c
static int udp_v4_encap_rcv(struct sock *sk, struct sk_buff *skb)
{
    struct udp_sock *up = udp_sk(sk);

    // 调用封装类型的处理函数
    return up->encap_rcv(sk, skb);
}
```
