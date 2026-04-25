# Linux 网络协议栈深度源码分析 (第二轮)

## 深入 Connection Tracking 机制

### 1.1 连接跟踪哈希表结构

```c
/*
 * nf_conntrack_hash - 连接跟踪的哈希表
 *
 * 设计考量：
 * 1. 使用 RCU (Read-Copy-Update) 实现无锁读取
 * 2. 双向链表处理哈希冲突
 * 3. 支持连接跟踪垃圾回收
 */
struct nf_conntrack_hash {
    struct hlist_nulls_head *hash;    // 哈希桶数组
    unsigned int hash_size;              // 哈希表大小
    unsigned int hash_count;            // 连接计数
};

/*
 * 连接跟踪条目
 *
 * 生命周期：
 * 1. NEW - 新建立的连接
 * 2. ESTABLISHED - 双向通信
 * 3. RELATED - 关联的连接 (如 FTP data)
 * 4. INVALID - 无效的包
 * 5. SNAT/DNAT - NAT 状态
 */
struct nf_conn {
    /* 引用计数 */
    refcount_t use;

    /* 连接跟踪状态 */
    unsigned int status;

    /* 方向 */
    struct nf_conntrack_tuple_hash tuplehash[IP_CT_DIR_MAX];

    /* 时间戳 */
    struct nf_conntrack_timestamp *timestamp;

    /* 预期连接 (对于 RELATED) */
    struct hlist_node expect_node;

    /* Master 连接 (对于 RELATED) */
    struct nf_conn *master;

    /* 扩展数据 */
    struct nf_ct_ext *ext;

    /* 网络命名空间 */
    possible_net_t ct_net;

    /* 回调函数 */
    struct nf_conntrack_l4proto *proto;

    /* 辅助数据 */
    union nf_conntrack_proto_data {
        struct nf_conntrack_tcp_reply_data tcp;
        /* 其他协议数据 */
    } proto;
};
```

### 1.2 Tuple 哈希计算

```c
/*
 * 连接跟踪的核心数据结构 - Tuple
 *
 * Tuple 是连接的端点描述符，包括：
 * - 源 IP / 目的 IP
 * - 源端口 / 目的端口
 * - 协议类型
 */
struct nf_conntrack_tuple {
    union nf_conntrack_lookups {
        struct {
            __be32 src_ip;           // 源 IP
            __be32 dst_ip;           // 目的 IP
            union {
                __be16 all;         // 所有端口
                struct {
                    __be16 src;     // 源端口
                    __be16 dst;     // 目的端口
                };
            };
        };
    } src;

    union nf_conntrack_lookups {
        struct {
            __be32 src_ip;
            __be32 dst_ip;
            union {
                __be16 all;
                struct {
                    __be16 src;
                    __be16 dst;
                };
            };
        };
        struct {
            __be16 protonum;         // 协议号
            __be16 dir;             // 方向
        };
    } dst;

    struct nf_conntrack_l3proto *l3proto;  // L3 协议
    struct nf_conntrack_l4proto *l4proto;  // L4 协议
};

/*
 * Tuple 哈希计算 - SipHash
 *
 * 使用 SipHash 而不是 Jenkins Hash 的原因：
 * 1. SipHash 对小输入优化
 * 2. 抵抗哈希洪水攻击
 * 3. 更快
 */
u32 nf_conntrack_hash(const struct nf_conntrack_tuple *tuple)
{
    u32 hash;

    /* 初始化 SipHash 状态 */
    struct {
        __le64 k0, k1;
    } key;

    /* 获取 per-netns 的哈希密钥 */
    get_random_bytes(&key, sizeof(key));

    /* SipHash 计算 */
    hash = siphash(&tuple, sizeof(*tuple), &key);

    /* 混合方向位 */
    hash ^= tuple->dst.dir;

    return hash;
}
```

### 1.3 连接建立流程

```c
/*
 * nf_conntrack_in - 连接跟踪入口
 *
 * 在 Netfilter PREROUTING 钩子调用
 */
unsigned int nf_conntrack_in(struct net *net, u_int8_t pf,
                            unsigned int hooknum, struct sk_buff *skb)
{
    struct nf_conntrack_tuple tuple;
    struct nf_conn *ct;

    /* 1. 创建/查找 tuple */
    if (!nf_ct_get_tuple(skb, skb_network_offset(skb),
                        &tuple, l3proto, l4proto)) {
        NF_CT_STAT_INC_ATOMIC(net, invalid);
        return NF_DROP;
    }

    /* 2. 查找现有连接 */
    ct = nf_conntrack_find_get(net, &tuple);
    if (ct) {
        /* 已存在连接 */
        NF_CT_STAT_INC_ATOMIC(net, found);
        return nf_conntrack_handle_packet(ct, skb);
    }

    /* 3. 新连接，建立跟踪条目 */
    if (!nf_conntrack_alloc(net, &tuple, &ct)) {
        NF_CT_STAT_INC_ATOMIC(net, new);
        return nf_conntrack_new(ct, skb);
    }

    return NF_DROP;
}

/*
 * 创建新的连接跟踪条目
 */
static unsigned int nf_conntrack_new(struct nf_conn *ct, struct sk_buff *skb)
{
    /* 1. 初始化状态 */
    ct->status = IPS_EXPECTING;

    /* 2. 设置超时 */
    ct->timeout = proto->new_timeout(ct);

    /* 3. 加入哈希表 */
    nf_conntrack_hash_insert(ct);

    /* 4. 触发期望连接检查 (对于 RELATED) */
    nf_ct_expect_find_get(&ct->tuplehash[IP_CT_DIR_REPLY].tuple);

    return NF_ACCEPT;
}
```

### 1.4 TCP 状态机与连接跟踪

```c
/*
 * TCP 连接跟踪状态
 *
 * 与 TCP 协议状态机的关系：
 * - TCP 状态：CLOSED, LISTEN, SYN_SENT, SYN_RECV, ESTABLISHED, ...
 * - 连接跟踪状态：NEW, ESTABLISHED, RELATED, etc.
 */
enum ip_conntrack_status {
    IPS_EXPECTED        = (1 << IP_CT_EXPECTED),        // 期望的连接
    IPS_SEEN_REPLY     = (1 << IP_CT_SEEN_REPLY),     // 看到回复
    IPS_ASSURED        = (1 << IP_CT_ESTABLISHED),    // 确认的连接
    IPS_CONFIRMED      = (1 << IP_CT_DEFAULT),         // 已确认
    IPS_SNAT           = (1 << IPS_SRC_NAT),          // SNAT 状态
    IPS_DNAT           = (1 << IPS_DST_NAT),          // DNAT 状态
    IPS_DYING          = (1 << IP_CT_DYING),          // 正在销毁
    IPS_TEMPLATE       = (1 << IP_CT_TEMPLATE),        // 模板
};

/*
 * TCP 协议连接跟踪
 */
static bool tcp_new(struct nf_conn *ct, const struct sk_buff *skb,
                   unsigned int dataoff)
{
    struct tcphdr *tcph = (struct tcphdr *)(skb->data + dataoff);

    /* TCP SYN - 新的连接 */
    if (tcph->syn && !tcph->ack) {
        ct->proto.tcp.state = TCP_CONNTRACK_SYN_SENT;
        set_bit(IPS_EXPECTED_BIT, &ct->status);
    }
    return true;
}

/*
 * TCP 状态转换处理
 */
static bool tcp_packet(struct nf_conn *ct, const struct sk_buff *skb,
                      unsigned int dataoff, enum tcp_conntrack state)
{
    struct tcphdr *tcph = (struct tcphdr *)(skb->data + dataoff);

    switch (ct->proto.tcp.state) {
    case TCP_CONNTRACK_SYN_SENT:
        if (tcph->syn && tcph->ack) {
            /* SYN+ACK - 进入 SYN_RECV */
            ct->proto.tcp.state = TCP_CONNTRACK_SYN_RECV;
            set_bit(IPS_SEEN_REPLY_BIT, &ct->status);
        } else if (tcph->syn) {
            /*  simultaneous open */
            ct->proto.tcp.state = TCP_CONNTRACK_SYN_SENT2;
        }
        break;

    case TCP_CONNTRACK_SYN_RECV:
        if (tcph->ack) {
            /* ACK - 连接建立 */
            ct->proto.tcp.state = TCP_CONNTRACK_ESTABLISHED;
            set_bit(IPS_ASSURED_BIT, &ct->status);
        }
        break;

    case TCP_CONNTRACK_ESTABLISHED:
        if (tcph->fin) {
            /* FIN - 开始关闭 */
            ct->proto.tcp.state = TCP_CONNTRACK_FIN_WAIT;
        }
        if (tcph->rst) {
            /* RST - 异常关闭 */
            ct->proto.tcp.state = TCP_CONNTRACK_CLOSE_WAIT;
        }
        break;

    case TCP_CONNTRACK_FIN_WAIT:
        if (tcph->fin && tcph->ack) {
            /* FIN+ACK - TIME_WAIT */
            ct->proto.tcp.state = TCP_CONNTRACK_TIME_WAIT;
        }
        break;
    }

    return true;
}
```

---

## 深入 Netfilter NAT 实现

### 2.1 NAT 转换原理

```c
/*
 * NAT (Network Address Translation) 类型
 *
 * SNAT: 源地址转换 (内网 → 外网)
 * DNAT: 目的地址转换 (外网 → 内网)
 */

/*
 * NAT 钩子函数
 */
static unsigned int
nf_nat_manip_pkt(struct sk_buff *skb, struct nf_conn *ct,
                 enum ip_nat_manip_type mtype)
{
    struct nf_conntrack_tuple *target;

    /* 获取需要转换的 tuple */
    if (mtype == IP_NAT_MANIP_SRC)
        target = &ct->tuplehash[IP_CT_DIR_REPLY].tuple;
    else
        target = &ct->tuplehash[IP_CT_DIR_ORIGINAL].tuple;

    /* L3 转换 */
    if (nf_nat_l3proto_module_put(ct))
        return NF_ACCEPT;

    return nf_nat_manip_pkt(skb, target, mtype);
}

/*
 * SNAT 实现 - 修改源地址和源端口
 */
static unsigned int nf_nat_out(struct sk_buff *skb, unsigned int hooknum,
                              struct nf_conn *ct)
{
    /* 检查是否需要 SNAT */
    if (ct->status & IPS_NAT_MASK) {
        /* 执行 SNAT */
        return ip_nat_setup(ct, skb, hooknum);
    }
    return NF_ACCEPT;
}

/*
 * 连接跟踪的 NAT 辅助
 */
struct nf_nat_hooks {
    unsigned int (*manip_pkt)(struct sk_buff *skb,
                              struct nf_conn *ct,
                              enum ip_nat_manip_type mtype);
    bool (*chunk_pkt)(struct sk_buff *skb,
                      struct nf_conntrack_l4proto *proto,
                      unsigned int dataoff,
                      unsigned int *matchoff,
                      unsigned int *matchlen);
};
```

---

## 深入 TCP 协议实现

### 3.1 TCP 首部处理

```c
/*
 * TCP 首部结构
 *
 * 固定首部 20 字节，可选部分最长 40 字节
 */
struct tcphdr {
    __be16  source;         // 源端口 (16-bit)
    __be16  dest;           // 目的端口 (16-bit)
    __be32  seq;            // 序列号 (32-bit)
    __be32  ack_seq;        // 确认号 (32-bit)

    /* 偏移量 + 控制标志 */
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u8    doff:4,        // 数据偏移 (4-bit)
            res1:4;        // 保留 (4-bit)
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u8    res1:4,
            doff:4;
#else
#error "Adjust your <asm/byteorder.h> defines"
#endif

    __u8    flags;          // 控制标志

    __be16  window;         // 窗口大小
    __sum16 check;         // 校验和
    __be16  urgent_ptr;    // 紧急指针
};

/* TCP 控制标志 */
#define TCP_FIN  0x01      // 结束
#define TCP_SYN  0x02      // 同步序列号
#define TCP_RST  0x04      // 重置连接
#define TCP_PSH  0x08      // 推送数据
#define TCP_ACK  0x10      // 确认
#define TCP_URG  0x20      // 紧急
#define TCP_ECE  0x40      // ECN 回应
#define TCP_CWR  0x80      // 拥塞窗口减小
```

### 3.2 TCP 序列号与滑动窗口

```c
/*
 * TCP 滑动窗口算法
 *
 * 核心概念：
 * 1. 序列号：每个字节都有序列号
 * 2. 确认号：期望接收的下一个序列号
 * 3. 窗口大小：接收方允许发送的数据量
 */

/*
 * TCP 接收窗口管理
 */
struct tcp_sock {
    /* 接收窗口 */
    u32     rcv_wnd;           // 接收窗口大小
    u32     rcv_wl1;          // 上次窗口更新时的序列号
    u32     rcv_wl2;          // 上次窗口更新时的确认号
    u32     rcv_nxt;           // 期望接收的下一个序列号

    /* 发送窗口 */
    u32     snd_wnd;           // 对方接收窗口大小
    u32     snd_nxt;          // 下一个要发送的序列号
    u32     snd_una;          // 最早未确认的序列号

    /* 拥塞控制 */
    u32     snd_cwnd;         // 拥塞窗口
    u32     snd_ssthresh;     // 慢启动阈值
};

/*
 * 检查序列号是否在窗口内
 */
static inline bool tcp_sequence(struct tcp_sock *tp, u32 seq, u32 end)
{
    return !before(end, tp->rcv_nxt) &&
           !after(seq, tp->rcv_nxt + tp->rcv_wnd);
}

/*
 * TCP 选项
 */
struct tcp_options_received {
    u16 mss_clamp;         // 最大分段大小
    u8  saw_tstamp;       // 看到时间戳
    u8  snd_wscale;        // 发送方窗口扩展
    u8  rcv_wscale;       // 接收方窗口扩展
    u8  cookie;           // Cookie
};
```

### 3.3 TCP 慢启动与拥塞控制

```c
/*
 * TCP 拥塞控制算法
 *
 * 慢启动 (Slow Start):
 * - cwnd 从 1 MSS 开始
 * - 每收到一个 ACK，cwnd += 1 MSS
 * - 直到 cwnd >= ssthresh 或丢包
 *
 * 拥塞避免 (Congestion Avoidance):
 * - cwnd 线性增长
 * - 每收到一个 ACK，cwnd += MSS*MSS/cwnd
 */

/*
 * 慢启动实现
 */
static void tcp_slow_start(struct tcp_sack *skb)
{
    struct tcp_sock *tp = tcp_sk(skb->sk);

    /* cwnd 每次增加一个 MSS */
    while (tp->snd_cwnd < tp->snd_ssthresh &&
           tp->snd_cwnd_cnt >= tp->snd_cwnd_clamp) {
        tp->snd_cwnd += min(tp->snd_cwnd_clamp, tp->mss_cache);
        tp->snd_cwnd_cnt = 0;
    }
}

/*
 * 拥塞避免实现
 */
static void tcp_cong_avoid(struct tcp_sack *skb)
{
    struct tcp_sock *tp = tcp_sk(skb->sk);

    if (tp->snd_cwnd < tp->snd_ssthresh) {
        /* 慢启动 */
        tcp_slow_start(skb);
    } else {
        /* 拥塞避免 - 线性增长 */
        tcp_reno_ai(tp);
    }
}

/*
 * 快速重传与快速恢复
 */
static void tcp_enter_loss(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);

    /* 1. ssthresh 减半 */
    tp->snd_ssthresh = tcp_fackets_before(tp->snd_una) >> 1;

    /* 2. cwnd 重置为 1 */
    tp->snd_cwnd = 1;
    tp->snd_cwnd_cnt = 0;

    /* 3. 进入恢复状态 */
    tcp_set_ca_state(sk, TCP_CA_Loss);
}

/*
 * 快速重传触发
 *
 * 当收到 3 个重复 ACK 时触发
 */
static void tcp_fastretrans_alert(struct sock *sk, u32 ack)
{
    struct tcp_sock *tp = tcp_sk(sk);

    switch (tp->ca_state) {
    case TCP_CA_Open:
        /* 可能丢包，进入快速恢复 */
        if (!tcp_fastretransmit(sk))
            return;
        fallthrough;
    case TCP_CA_Recovery:
        /* 快速恢复 */
        if (tcp_ack(sk, ack) == 0)
            return;
        tcp_moderate_cwnd(tp);
        break;
    }
}
```

---

## 深入 Socket 缓冲区管理

### 4.1 sk_buff 结构详解

```c
/*
 * sk_buff - Socket Buffer
 *
 * 网络数据包的内核表示
 *
 * 内存布局:
 * +--------+-----------------+------+
 * | head  |      data      | tail |
 * +--------+-----------------+------+
 *          |<- len  ->|
 * |<------- total len -------->|
 *
 * head: 缓冲区的开始 (固定)
 * data: 数据的开始 (可变)
 * tail: 数据的结束 (可变)
 * end:  缓冲区的结束 (固定)
 */
struct sk_buff {
    /* 链接 */
    struct sk_buff        *next;       // 下一个 SKB
    struct sk_buff        *prev;       // 前一个 SKB

    /* Socket 引用 */
    struct sock           *sk;         // 所属 socket

    /* 网络设备 */
    struct net_device     *dev;        // 接收/发送设备

    /* 长度信息 */
    unsigned int          len;         // 数据长度 (含协议头)
    unsigned int          data_len;    // 非线性数据长度
    __u16                 mac_len;     // MAC 头长度
    __u16                 hdr_len;     // 克隆头的长度

    /* 校验和状态 */
    __u8                  ip_sumed:2;  // CHECKSUM_*

    /* 协议类型 */
    __u16                 protocol;     // ETH_P_IP, etc.

    /* 时间戳 */
    struct skb_mstamp     skb_mstamp; // 到达/发送时间

    /* 线性数据区域 */
    unsigned char         *head;       // 缓冲区开始
    unsigned char         *data;       // 数据开始
    unsigned char         *tail;       // 数据结束
    unsigned char         *end;        // 缓冲区结束

    /* 分片管理 */
    struct skb_shared_info *skb_shinfo;

    /* 私有数据 */
    __u32                 options;
};

/*
 * skb_shared_info - 分片信息
 *
 * 用于管理非线性数据 (分散/聚集 IO)
 */
struct skb_shared_info {
    __u8    nr_frags;          // 分片数量
    __u8    gso_type;          // GSO 类型
    __u16    gso_size;          // GSO 分段大小
    struct sk_buff *frag_list;   // 分片链表
    union {
        struct {
            unsigned int tskey;
            __u32 csum_offset;
            __u8  csum_start;
        };
        __u32 gso_segs;
    };
    struct page_pool *pp;
    unsigned short gso_partial_start;
    unsigned long shared_flag;
    atomic_t dataref;
};

/*
 * 添加数据到 SKB
 */
static inline unsigned char *skb_put(struct sk_buff *skb, unsigned int len)
{
    unsigned char *tmp = skb->tail;
    SKB_LINEAR_ASSERT(skb);
    skb->tail += len;
    skb->len += len;
    if (skb->tail > skb->end)
        skb_over_panic(skb, len, __builtin_return_address(0));
    return tmp;
}

/*
 * 移除数据从 SKB
 */
static inline unsigned char *skb_pull(struct sk_buff *skb, unsigned int len)
{
    skb->len -= len;
    if (skb->len < 0)
        skb_under_panic(skb, len, __builtin_return_address(0));
    return skb->data += len;
}
```

### 4.2 GRO (Generic Receive Offload)

```c
/*
 * GRO - 批量合并接收的数据包
 *
 * 原理：将多个相同流的 SKB 合并成一个大的 SKB
 * 减少协议栈处理开销和缓存未命中
 */

/*
 * GRO 缓冲
 */
struct gro_list {
    struct list_head list;       // SKB 链表
    struct napi_struct *napi;   // 关联的 NAPI
    unsigned int count;          // SKB 数量
    unsigned int aged;          // 是否过期
};

/*
 * GRO 重组检查
 *
 * 判断一个 SKB 是否可以与现有流合并
 */
static inline bool gro_ok(struct sk_buff *skb, unsigned int frag)
{
    return skb->ip_sumed == CHECKSUM_UNNECESSARY &&
           (skb->encapsulation ||
            (skb->ip_sumed == CHECKSUM_UNNECESSARY &&
             skb->csum_level < 4)) &&
           (!frag || skb_headlen(skb));
}

/*
 * tcp_gro_receive - TCP GRO 合并
 *
 * 合并条件：
 * 1. 相同的源/目的 IP
 * 2. 相同的源/目的端口
 * 3. 连续的序列号
 * 4. 相同的 TCP 选项
 */
static struct sk_buff *tcp_gro_receive(struct sk_buff *skb, struct list_head *head)
{
    struct sk_buff *p, *skb1;
    struct tcphdr *th, *th1;

    /* 检查是否可以合并 */
    for (p = list_first_entry(head, struct sk_buff, list)) {
        th1 = tcp_hdr(p);

        if (th1->source != th->source ||
            th1->dest != th->dest ||
            th1->seq != th->seq) {
            break;
        }

        /* 可以合并 */
        skb1 = p;
        goto merge;
    }

    /* 不能合并，添加到链表头 */
    list_add(&skb->list, head);
    return NULL;

merge:
    /* 合并到 skb1 */
    skb_shinfo(skb)->frags[0] = skb_shinfo(skb)->frags[0];
    skb->data_len = skb->len - skb_headlen(skb);
    skb->len = skb_headlen(skb1) + skb->len - skb_headlen(skb);

    /* 更新序列号 */
    th1->seq += skb1->len - skb_headlen(skb1);

    return p;
}
```

---

## 深入路由子系统

### 5.1 路由查找流程

```c
/*
 * 路由缓存结构
 *
 * Linux 使用转发信息库 (FIB) 而非传统路由缓存
 */
struct fib_table {
    unsigned int        tb_id;        // 路由表 ID
    unsigned int        tb_stamp;
    struct fib_trie     tb_prefix;     // 前缀树
};

/*
 * 路由查找入口
 *
 * 最长前缀匹配 (Longest Prefix Match)
 */
int fib_lookup(struct net *net, const struct flowi4 *flp,
              struct fib_result *res)
{
    struct fib_table *table;

    /* 获取路由表 */
    table = fib_get_table(net, RT_TABLE_MAIN);
    if (!table)
        return -ENETUNREACH;

    /* 执行前缀树查找 */
    return fib_table_lookup(table, flp, res, FIB_LOOKUP_NOREF);
}

/*
 * fib_table_lookup - 前缀树查找
 *
 * 查找过程：
 * 1. 从根节点开始
 * 2. 根据目的 IP 的每一位选择分支
 * 3. 记录最后一个匹配的叶子
 * 4. 返回该叶子对应的路由信息
 */
static int fib_table_lookup(struct fib_table *tb,
                          const struct flowi4 *flp,
                          struct fib_result *res,
                          unsigned int flags)
{
    struct trie *t = (struct trie *)tb->tb_prefix;
    struct key_prefix *k;
    struct fib_alias *fa;
    t_key key;

    /* 获取目的地址的关键字 */
    key = ntohl(flp->daddr);

    /* 遍历前缀树 */
    k = trie_search(&t->trie, key);
    if (!k)
        return -ENETUNREACH;

    /* 获取最佳匹配的前缀 */
    fa = find_default_prefix(k);
    if (fa) {
        res->prefix = fa->fa_info->fib_prefix;
        res->fib_nh = fa->fa_info->fib_nh;
        res->type = fa->fa_type;
        res->scope = fa->fa_scope;
    }

    return 0;
}
```

### 5.2 邻居表与 ARP

```c
/*
 * 邻居表条目
 *
 * 维护 IP → MAC 地址映射
 */
struct neighbour {
    struct neighbour        *next;          // 哈希链表
    struct net_device       *dev;           // 网络设备
    unsigned char           *ha;            // 硬件地址
    __u8                   nud_state;       // 状态

    /* 状态机 */
    __u8                    probes;         // 探测计数
    struct timer_list       timer;           // 超时定时器

    /* 操作 */
    const struct neigh_ops  *ops;           // 操作函数集

    /* 引用计数 */
    refcount_t              refcnt;
};

/*
 * NUD (Neighbor Unreachability Detection) 状态
 */
enum {
    NUD_INCOMPLETE,      // 正在解析
    NUD_REACHABLE,       // 可达
    NUD_STALE,           // 陈旧
    NUD_DELAY,           // 延迟探测
    NUD_PROBE,           // 正在探测
    NUD_FAILED,          // 失败
    NUD_NOARP,          // 无 ARP
    NUD_PERMANENT        // 永久
};

/*
 * ARP 解析流程
 */
static void neigh_probe(struct neighbour *neigh)
{
    struct sk_buff *skb;

    /* 创建 ARP 请求 */
    skb = alloc_skb(sizeof(struct arphdr) + 2 * 4 + 2 * 6, GFP_ATOMIC);
    if (!skb)
        return;

    /* 填充 ARP 请求 */
    arp = (struct arphdr *)skb_put(skb, sizeof(struct arphdr));

    /* 发送 */
    dev_queue_xmit(skb);
}
```

---

## 附录：核心数据结构关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Network Packet Flow                                    │
│                                                                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │Eth Head  │───►│ IP Head  │───►│TCP/UDP   │───►│  Data    │   │
│  │(14 bytes)│    │(20 bytes)│   │ Header   │    │          │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│       │                │               │                            │
│       ▼                ▼               ▼                            │
│  skb->mac_len    skb->network_header  skb->transport_header        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                     sk_buff                                 │  │
│  │  head ────────► ┌──────────┬──────────┬──────────┐       │  │
│  │                │  MAC hdr │  IP hdr  │TCP/UDP hdr│ Data │       │  │
│  │  data ──────────────────────►│          │          │       │  │
│  │                             │          │          │       │  │
│  │  tail ──────────────────────────────────────────►│       │  │
│  │                ◄─────────── len ──────────────►│       │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    TCP State Machine                                     │
│                                                                   │
│  CLOSED ────► LISTEN ◄──────┐                                   │
│       │           │           │                                   │
│       │           ▼           │                                   │
│       │      ┌────────┐       │                                   │
│       │      │SYN_   │       │                                   │
│       │      │SENT   │───────┘                                   │
│       │      └───┬────┘                                         │
│       │          │                                              │
│       │          ▼                                              │
│       │      ┌────────┐                                         │
│       │      │SYN_   │                                         │
│       │      │RECV   │                                         │
│       │      └───┬────┘                                         │
│       │          │                                              │
│       │          ▼                                              │
│       └──────►ESTABLISHED◄─────────┐                           │
│                    │                 │                           │
│                    │                 │                           │
│                    ▼                 │                           │
│              ┌──────────┐           │                           │
│              │CLOSE_WAIT│───────────┘                           │
│              └────┬─────┘                                       │
│                   │                                             │
│                   ▼                                             │
│              ┌──────────┐                                      │
│              │CLOSING  │                                      │
│              └────┬─────┘                                      │
│                   │                                             │
│         ┌────────┴────────┐                                    │
│         ▼                 ▼                                    │
│   ┌──────────┐    ┌──────────┐                              │
│   │LAST_ACK  │    │TIME_WAIT  │                              │
│   └─────┬────┘    └──────────┘                              │
│         │                                                     │
│         ▼                                                     │
│   ───► CLOSED                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 参考代码路径

| 文件 | 功能 |
|------|------|
| `net/netfilter/nf_conntrack_core.c` | 连接跟踪核心 |
| `net/netfilter/nf_nat_core.c` | NAT 核心 |
| `net/ipv4/tcp_ipv4.c` | TCP IPv4 实现 |
| `net/ipv4/tcp_input.c` | TCP 输入处理 |
| `net/ipv4/tcp_output.c` | TCP 输出处理 |
| `include/net/tcp.h` | TCP 通用定义 |
| `include/linux/skbuff.h` | SKB 结构 |
| `include/net/neighbour.h` | 邻居表 |
| `net/ipv4/route.c` | 路由查找 |
