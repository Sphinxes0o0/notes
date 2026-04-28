# IPv6 TCP/UDP 实现

## 1. 模块架构

### 1.1 功能概述

IPv6 下的 TCP 和 UDP 实现与 IPv4 基本相同，主要区别在于地址处理和伪头部校验和计算。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv6/tcpv6.c` | IPv6 TCP |
| `net/ipv6/udp.c` | IPv6 UDP |
| `net/ipv6/inet6_connection.c` | IPv6 连接处理 |

## 2. IPv6 TCP

### 2.1 tcp_v6_connect()

```c
// net/ipv6/tcpv6.c:280
int tcp_v6_connect(struct sock *sk, struct sockaddr *uaddr, int addr_len)
{
    struct sockaddr_in6 *usin = (struct sockaddr_in6 *)uaddr;
    struct inet_sock *inet = inet_sk(sk);
    struct inet6_sock *inet6 = inet6_sk(sk);

    // 1. 设置地址
    inet->inet_rcv_saddr = inet->inet_saddr = 0;
    inet6->pinet6->saddr = 0;

    // 2. 设置端口
    inet->inet_dport = usin->sin6_port;
    inet->inet_daddr = usin->sin6_addr;

    // 3. 路由查找
    sk->sk_state = TCP_SYN_SENT;
    err = ip6_route_connect(usk, fl6, addr_len, O_RDWR);

    // 4. 设置本地地址
    if (!sk->sk_rcv_saddr)
        sk->sk_rcv_saddr = fl6->saddr;
}

// net/ipv6/tcpv6.c:200
static struct sock *tcp_v6_syn_recv_sock(...)
{
    struct sock *sk;

    // 创建新的 child socket
    sk = tcp_create_openreq_child(sk, req, skb);
    if (sk) {
        inet6_sk(sk)->pinet6->saddr = fl6->saddr;
        inet6_sk(sk)->rcv_saddr = fl6->daddr;
    }
    return sk;
}
```

### 2.2 IPv6 TCP 伪头部

```c
// IPv6 TCP 伪头部
struct ipv6_pseudohdr {
    struct in6_addr saddr;
    struct in6_addr daddr;
    __be32         length;
    __u8          next_hdr;
};

tcp_v6_check(struct tcphdr *th, int len, struct in6_addr *saddr,
             struct in6_addr *daddr)
{
    // 计算校验和
    return csum_ipv6_magic(saddr, daddr, len, IPPROTO_TCP, 0);
}
```

## 3. IPv6 UDP

### 3.1 udp_v6_sendmsg()

```c
// net/ipv6/udp.c:850
int udp_v6_sendmsg(struct sock *sk, struct msghdr *msg, size_t len)
{
    struct in6_addr *addr = &np->saddr;
    struct flowi6 fl6;

    // 1. 设置源/目的地址
    fl6.flowi6_proto = IPPROTO_UDP;
    fl6.fl6_sport = inet->inet_sport;
    fl6.fl6_dport = inet->inet_dport;

    // 2. 路由查找
    ip6_route_output(sock_net(sk), sk, &fl6);

    // 3. 发送
    return ip6_push_pending_frames(sk);
}
```

### 3.2 udp_v6_recvmsg()

```c
// net/ipv6/udp.c:600
int udp_v6_recvmsg(struct sock *sk, struct msghdr *msg, size_t len,
                   int noblock, int flags, int *addr_len)
{
    struct sk_buff *skb;
    unsigned int ulen;

    // 1. 接收数据
    skb = skb_recv_datagram(sk, flags, noblock, &err);

    // 2. 获取地址
    if (use_udp6_rx_csum) {
        // UDPv6 校验和验证
    }

    // 3. 复制数据
    err = skb_copy_datagram_msg(skb, offset, msg, len);

    // 4. 获取源地址
    ipv6_addr_copy(&sin6->sin6_addr, &ipv6_hdr(skb)->saddr);

    return len;
}
```

### 3.3 IPv6 UDP 校验和

```c
// net/ipv6/udp.c:100
void udp6_set_csum(bool csum, struct sk_buff *skb,
                    struct in6_addr *saddr, struct in6_addr *daddr)
{
    struct udphdr *uh = udp_hdr(skb);

    if (csum) {
        uh->check = ~csum_ipv6_magic(saddr, daddr, skb->len,
                                     IPPROTO_UDP, 0);
    } else {
        uh->check = 0;
    }
}
```

## 4. IPv6 特殊处理

### 4.1 碎片头处理

```c
// IPv6 发送时处理分片
// net/ipv6/ip6_output.c:1200
int ip6_fragment(struct sk_buff *skb, int (*output)(struct sk_buff *))
{
    struct frag_hdr *fh;
    unsigned int mtu;
    unsigned int hlen;
    unsigned int fragoff;
    unsigned int len;

    // 计算 MTU
    mtu = ip6_skb_dst_mtu(skb);

    // 如果不需要分片，直接发送
    if (skb->len <= mtu)
        return output(skb);

    // 分片
    // ... fragment code
}
```

### 4.2 扩展头处理

```c
// IPv6 扩展头遍历
// net/ipv6/exthdrs.c
int ipv6_skip_exthdr(struct sk_buff *skb, int start, u8 *nexthdrp)
{
    u8 nexthdr = *nexthdrp;

    while (ipv6_ext_hdr(nexthdr)) {
        struct ipv6_opt_hdr *hdr;

        // 跳过扩展头
        hdr = (void *)(skb->data + start);
        start += ipv6_optlen(hdr);
        nexthdr = hdr->nexthdr;
    }

    *nexthdrp = nexthdr;
    return start;
}
```

## 5. 连接跟踪

### 5.1 ipv6_conntrack()

```c
// net/ipv6/netfilter/nf_conntrack_l3proto_ipv6.c
static int ipv6_help(struct sk_buff *skb, unsigned int xtnum)
{
    enum ip_conntrack_info ctinfo;
    struct nf_conn *ct;

    // 查连接跟踪表
    ct = nf_ct_get(skb, &ctinfo);
    if (!ct)
        return NF_ACCEPT;

    // 更新连接状态
    return nf_conntrack_in(skb, PF_INET6, &ctinfo);
}
```

## 6. Socket 选项

### 6.1 IPv6_ONLY

```c
// net/ipv6/sockopts.c:150
int ipv6_only_sock(struct sock *sk)
{
    return inet_sk(sk)->inet_ipv6only;
}
```

### 6.2 IPV6_V6ONLY

```c
// 防止 IPv4 映射地址绑定到 IPv6 socket
// 仅接受真正的 IPv6 连接
```
