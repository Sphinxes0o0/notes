# IPv6 addrconf 地址管理

## 1. 模块架构

### 1.1 功能概述

`addrconf` 负责 IPv6 地址的自动配置，包括 SLAAC (无状态地址自动配置)、DAD (重复地址检测) 和路由器发现。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv6/addrconf.c` | 地址配置 (约 7600 行) |
| `net/ipv6/ndisc.c` | 邻居发现 |
| `include/net/addrconf.h` | addrconf 定义 |
| `include/net/if_inet6.h` | inet6_dev 定义 |

## 2. 核心数据结构

### 2.1 struct inet6_ifaddr

```c
// include/net/if_inet6.h:33
struct inet6_ifaddr {
    struct in6_addr     addr;           // IPv6 地址
    __u32               prefix_len;      // 前缀长度
    __u32               rt_priority;     // 路由优先级
    __u32               valid_lft;       // 有效生命周期
    __u32               prefered_lft;    // 首选生命周期

    refcount_t          refcnt;          // 引用计数
    spinlock_t          lock;
    int                 state;           // DAD 状态

    __u8                dad_probes;       // DAD 探测次数
    unsigned char       flags;           // IFA_F_* 标志

    __u16               scope;            // 地址范围
    __u64               dad_nonce;        // DAD 随机数

    struct delayed_work dad_work;         // DAD 工作队列
    struct inet6_dev   *idev;           // 所属 inet6_dev
    struct fib6_info    *rt;             // 关联的路由

    struct hlist_node   addr_lst;        // 地址哈希表节点
    struct list_head    if_list;         // 接口地址列表
    struct list_head    tmp_list;        // 临时地址列表
    struct inet6_ifaddr *ifpub;         // 公开地址 (临时地址)
    int                 regen_count;     // 再生计数
};
```

### 2.2 struct inet6_dev

```c
// include/net/if_inet6.h:167
struct inet6_dev {
    struct net_device   *dev;            // 网络设备
    struct list_head    addr_list;        // 单播地址列表

    struct ifmcaddr6    __rcu *mc_list; // 多播地址列表
    struct ifmcaddr6    __rcu *mc_tomb;

    unsigned char       mc_qrv;           // 多播查询健壮性变量
    unsigned char       mc_gq_running;   // 多播查询运行中
    unsigned char       mc_ifc_count;    // 多播接口计数

    struct delayed_work mc_gq_work;      // MLD 查询
    struct delayed_work mc_ifc_work;      // 接口变化
    struct delayed_work mc_dad_work;      // DAD 完成

    rwlock_t            lock;
    refcount_t          refcnt;
    __u32              if_flags;          // IF_RA_* 标志

    u32                desync_factor;     // 去同步因子
    struct list_head   tempaddr_list;    // 临时地址列表

    struct in6_addr     token;            // 接口标识符
    struct neigh_parms *nd_parms;        // 邻居发现参数

    struct ipv6_devconf cnf;             // 配置
    struct ipv6_devstat stats;          // 统计

    struct timer_list   rs_timer;        // 路由器 solicitation 定时器
    __s32              rs_interval;       // RS 间隔
};
```

## 3. 地址状态

### 3.1 DAD 状态

```c
// include/net/if_inet6.h:95
enum {
    INET6_IFADDR_STATE_DAD,       // DAD 进行中
    INET6_IFADDR_STATE_POSTDAD,   // DAD 完成
    INET6_IFADDR_STATE_ERRDAD,    // DAD 失败
    INET6_IFADDR_STATE_DEAD,       // 正在删除
};
```

### 3.2 地址标志

```c
// include/net/if_inet6.h:100
#define IFA_F_PERMANENT       0x01  // 永久地址
#define IFA_F_TENTATIVE        0x02  // 试探性 (DAD 中)
#define IFA_F_OPTIMISTIC       0x04  // 乐观 DAD
#define IFA_F_DADFAILED       0x08  // DAD 失败
#define IFA_F_DEPRECATED       0x10  // 已废弃
#define IFA_F_TEMPORARY        0x20  // 临时地址
#define IFA_F_NODAD           0x40  // 跳过 DAD
#define IFA_F_MANAGETEMPADDR   0x80  // 管理临时地址
```

## 4. SLAAC 流程

### 4.1 链路本地地址

```c
// net/ipv6/addrconf.c:376
static int ipv6_add_dev(struct net_device *dev)
{
    // 1. 创建 inet6_dev
    idev = ipv6_add_dev(dev);
    if (IS_ERR(idev)) return PTR_ERR(idev);

    // 2. 生成链路本地地址
    addr.s6_addr32[0] = htonl(0xfe800000);
    ipv6_generate_eui64(addr.s6_addr32 + 8, dev);

    // 3. 添加地址
    ipv6_add_addr(idev, &addr, 64, IFA_F_PERMANENT | IFA_F_NODAD);
}
```

### 4.2 路由器 Solicitation

```c
// net/ipv6/addrconf.c:4018
static void addrconf_rs_timer(unsigned long data)
{
    struct inet6_ifaddr *ifp = (void *)data;

    if (ifp->idev->cnf.forwarding)
        return;  // 是路由器，不发送 RS

    // 发送 RS 到 ff02::2
    ndisc_send_rs(dev, &in6addr_linklocal_allrouters, NULL);

    // 指数退避重试
    if (ifp->idev->rs_probes < rad->rs_max_probes)
        addrconf_mod_rs_timer(ifp, ifp->idev->cnf.rtr_solicit_interval);
}
```

### 4.3 路由器 Advertisement 处理

```c
// net/ipv6/ndisc.c:1232
static void ndisc_router_discovery(struct sk_buff *skb)
{
    // 1. 验证 RA (源地址是链路本地)
    if (!ipv6_addr_is_lladdr(&ipv6_hdr(skb)->saddr))
        return;

    // 2. 更新默认路由
    if (ra_msg->icmph.icmp6_router)
        rt6_add_dflt_router(ra_msg->icmph.icmp6_router, skb->dev);

    // 3. 处理前缀信息
    for (each option) {
        if (option->nd_opt_type == ND_OPT_PREFIX_INFORMATION)
            addrconf_prefix_rcv(skb->dev, option);
    }

    // 4. 更新设备标志
    if (ra_msg->icmph.icmp6_flags & ND_RA_FLAG_MANAGED)
        idev->if_flags |= IF_RA_MANAGED;
}
```

## 5. DAD (重复地址检测)

### 5.1 DAD 状态机

```
PREDAD -> DAD -> POSTDAD (成功)
              \-> ERRDAD (失败)
```

### 5.2 DAD 开始

```c
// net/ipv6/addrconf.c:4096
void addrconf_dad_begin(struct inet6_ifaddr *ifp)
{
    // 1. 加入 solicitation-node 多播组
    addrconf_join_solict(ifp->idev->dev, &ifp->addr);

    // 2. 如果不跳过 DAD
    if (!(ifp->flags & IFA_F_NODAD)) {
        // 3. 设置状态为 DAD
        ifp->state = INET6_IFADDR_STATE_DAD;

        // 4. 调度第一次探测
        addrconf_mod_dad_timer(ifp,
            net_random() % max(NEIGH_VAR(ifp->idev->nd_parms, DELAY_FIRST_PROBE_TIME), 1));
    }
}
```

### 5.3 DAD 探测

```c
// net/ipv6/addrconf.c:4284
static void addrconf_dad_timer(unsigned long data)
{
    struct inet6_ifaddr *ifp = (void *)data;

    // 发送 NS 到 solicitation-node 多播组
    ndisc_send_ns(ifp->idev->dev, &ifp->addr, &in6addr_any, ifp->dad_nonce);

    // 增加探测计数
    ifp->dad_probes++;

    // 继续探测直到达到最大次数
    if (ifp->dad_probes < ND_MAX_MULTICAST_SOLICIT)
        addrconf_mod_dad_timer(ifp, ND_RETRANS_TIMER);
}
```

### 5.4 DAD 成功

```c
// net/ipv6/addrconf.c:4311
void addrconf_dad_completed(struct inet6_ifaddr *ifp)
{
    // 1. 标记为非试探性
    ifp->flags &= ~(IFA_F_TENTATIVE | IFA_F_OPTIMISTIC);
    ifp->state = INET6_IFADDR_STATE_POSTDAD;

    // 2. 发送非请求 NA
    ndisc_send_na(ifp->idev->dev, &in6addr_allnodes, &ifp->addr,
                  false, false, true);  // router=0, solicited=0, override=1

    // 3. 如果是链路本地且是唯一默认路由，发送 RS
    if (ipv6_addr_is_lladdr(&ifp->addr))
        addrconf_join_allrouters(ifp->idev->dev);
}
```

## 6. 隐私扩展

### 6.1 临时地址创建

```c
// net/ipv6/addrconf.c:1359
struct inet6_ifaddr *ipv6_create_tempaddr(struct inet6_ifaddr *ifp)
{
    // 1. 复制前缀
    addr = ifp->addr;

    // 2. 生成随机接口 ID
    ipv6_gen_rnd_iid(&addr.s6_addr32[1]);

    // 3. 计算生命周期
    valid_lft = min(ifp->valid_lft, idev->cnf.temp_valid_lft);
    prefered_lft = min(ifp->prefered_lft - desync,
                       idev->cnf.temp_preferred_lft);

    // 4. 创建临时地址
    return ipv6_add_addr(idev, &addr, 64, IFA_F_TEMPORARY, valid_lft, prefered_lft);
}
```

### 6.2 临时地址管理

```c
// net/ipv6/addrconf.c:2592
static void manage_tempaddrs(struct inet6_dev *idev, ...)
{
    // 1. 如果首选生命周期过期，更新为已废弃
    // 2. 如果有效生命周期过期，删除临时地址
    // 3. 如果列表为空且配置启用，创建新的临时地址
}
```

## 7. 地址验证

### 7.1 addrconf_verify()

```c
// net/ipv6/addrconf.c:4743
static void addrconf_verify(struct net *net)
{
    // 1. 调度延迟工作
    mod_delayed_work(addrconf_wq, &net->ipv6.addr_chk_work,
                     ADDR_CHECK_FREQUENCY);

    // 2. 检查所有地址的生命周期
    // 3. 处理临时地址再生
}
```

## 8. 前缀处理

### 8.1 addrconf_prefix_rcv()

```c
// net/ipv6/addrconf.c:2774
void addrconf_prefix_rcv(struct net_device *dev, struct nd_opt_hdr *opt)
{
    struct prefix_info *pinfo = (struct prefix_info *)opt;

    // 1. 验证前缀
    if (pinfo->prefix_len > 64)
        return;

    // 2. 如果 onlink，设置路由
    if (pinfo->onlink) {
        // 添加 onlink 路由
    }

    // 3. 如果是自主地址配置，创建地址
    if (pinfo->autoconf)
        addrconf_prefix_rcv_add_addr(dev, pinfo);
}
```

## 9.Solicited-Node 多播地址

### 9.1 计算

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

格式: `ff02::1:ffXX:XXXX` (后 24 位复制自目标地址)
