# net/xfrm - IPsec 框架

## 1. 模块架构

### 1.1 功能概述

xfrm 是 Linux 内核的 IPsec 实现框架，支持 ESP、AH 和 IPcomp 协议。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/xfrm/xfrm_state.c` | SA 管理 |
| `net/xfrm/xfrm_policy.c` | 策略管理 |
| `net/xfrm/xfrm_input.c` | 输入处理 |
| `net/xfrm/xfrm_output.c` | 输出处理 |
| `include/net/xfrm.h` | xfrm 定义 |

## 2. 核心数据结构

### 2.1 struct xfrm_state

```c
// include/net/xfrm.h:180
struct xfrm_state {
    struct hlist_node byspi;          // 按 SPI 哈希
    struct hlist_node bydst;         // 按目的地址哈希

    struct xfrm_src {
        __be32 saddr;
        __be32 daddr;
    } id;

    struct xfrm_spi {
        __be32 spi;
        __be32 seq;
    } key;

    struct xfrm_algo *algo;         // 算法
    struct xfrm_algo_auth *aalgo;  // 认证算法
    struct xfrm_encap_tmpl *encap; // 封装模板

    __u32 props;                     // 属性
    __u32 mode;                     // 模式 (传输/隧道)

    unsigned long curlft.bytes;      // 当前流量统计
    unsigned long curlft.packets;

    struct timer_list timer;         // 生命周期定时器
    atomic_t refcnt;                // 引用计数
    struct rcu_head rcu;
};
```

### 2.2 struct xfrm_policy

```c
// include/net/xfrm.h:250
struct xfrm_policy {
    struct hlist_node bydst;         // 按目的地址哈希
    struct hlist_node byidx;         // 按索引哈希

    struct xfrm_selector {
        __be32 saddr;
        __be32 daddr;
        __be16 sport;
        __be16 dport;
        __u8 proto;
        __u8 family;
    } selector;

    __u8 dir;                        // 方向 (in/out)
    __u8 action;                     // 动作 (allow/block)

    struct xfrm_lifetime_cfg {
        unsigned long add_time;
        unsigned long use_time;
        unsigned long expire;
    } lft;

    atomic_t refcnt;
};
```

### 2.3 struct xfrm_state_algo

```c
// include/net/xfrm.h:50
struct xfrm_algo {
    char alg_name[64];
    unsigned int alg_key_len;
    unsigned int alg_iv_len;
    unsigned int alg_trunc_len;
    unsigned char alg_key[0];
};
```

## 3. 安全关联 (SA)

### 3.1 xfrm_state_add()

```c
// net/xfrm/xfrm_state.c:300
int xfrm_state_add(struct xfrm_state *x)
{
    struct xfrm_state *old;

    // 查找已存在的 SA
    old = xfrm_state_lookup(&x->id.daddr, x->id.spi, x->id.proto);
    if (old) {
        xfrm_state_put(old);
        return -EEXIST;
    }

    // 添加到哈希表
    hlist_add_head_rcu(&x->bydst, xfrm_state_bydst);
    hlist_add_head_rcu(&x->byspi, xfrm_state_byspi);

    // 启动定时器
    if (x->lft.soft_limit_expires)
        mod_timer(&x->timer, x->lft.soft_limit_expires);

    atomic_inc(&xfrm_state_cnt);
    return 0;
}
```

### 3.2 xfrm_state_lookup()

```c
// net/xfrm/xfrm_state.c:200
struct xfrm_state *xfrm_state_lookup(struct net *net,
                                     const xfrm_address_t *daddr,
                                     __be32 spi, __u8 proto)
{
    unsigned int h = xfrm_spi_hash(net, daddr, spi, proto);
    struct hlist_head *chain = &xfrm_state_byspi[h];

    hlist_for_each_entry_rcu(x, chain, byspi) {
        if (x->id.spi == spi &&
            x->id.daddr.a4 == daddr->a4 &&
            x->id.proto == proto)
            return x;
    }

    return NULL;
}
```

## 4. 策略

### 4.1 xfrm_policy_lookup()

```c
// net/xfrm/xfrm_policy.c:500
struct xfrm_policy *xfrm_policy_lookup(struct net *net,
                                       const xfrm_address_t *daddr,
                                       __be16 dport,
                                       __be16 sport,
                                       u8 proto,
                                       u8 dir)
{
    struct xfrm_policy *pol;
    unsigned int h = xfrm_policy_hash(daddr, dir);
    struct hlist_head *chain = &xfrm_policy_bydst[h];

    hlist_for_each_entry_rcu(pol, chain, bydst) {
        if (xfrm_selector_match(&pol->selector, daddr, dport,
                               sport, proto) &&
            pol->dir == dir)
            return pol;
    }

    return NULL;
}
```

### 4.2 策略匹配

```c
// net/xfrm/xfrm_policy.c:400
static int xfrm_selector_match(struct xfrm_selector *sel,
                                xfrm_address_t *daddr,
                                __be16 dport, __be16 sport,
                                __u8 proto)
{
    if (sel->proto && sel->proto != proto)
        return 0;

    if (xfrm_addr_cmp(&sel->daddr, daddr, sel->family) != 0)
        return 0;

    if (sel->dport && sel->dport != dport)
        return 0;

    return 1;
}
```

## 5. 输入处理

### 5.1 xfrm_input()

```c
// net/xfrm/xfrm_input.c:100
int xfrm_input(struct sk_buff *skb, int nexthdr, __be32 spi, int encap_type)
{
    struct xfrm_state *x;
    int err;

    // 查找 SA
    x = xfrm_state_lookup(&iph->daddr, spi, IPPROTO_ESP);
    if (!x)
        return -EINVAL;

    // 解密/认证
    switch (x->id.proto) {
    case IPPROTO_ESP:
        err = esp_input(x, skb);
        break;
    case IPPROTO_AH:
        err = ah_input(x, skb);
        break;
    case IPPROTO_IPCOMP:
        err = ipcomp_input(x, skb);
        break;
    }

    // 传递给下一个头
    return x->type->input(x, skb);
}
```

### 5.2 ESP 输入

```c
// net/xfrm/esp.c:200
static int esp_input(struct xfrm_state *x, struct sk_buff *skb)
{
    struct esp_data *esp = x->data;
    struct iphdr *iph = ip_hdr(skb);
    struct esp_hdr *esph;

    // 获取 ESP 头
    esph = (void *)(skb->data + iph->ihl * 4);

    // 解密
    err = esp->conf.desc->decrypt(esp, skb, esph);
    if (err)
        return err;

    // 验证
    if (esp->auth) {
        err = esp->auth->verify(esp, skb);
        if (err)
            return err;
    }

    return xfrm_parse_skb(skb);
}
```

## 6. 输出处理

### 6.1 xfrm_output()

```c
// net/xfrm/xfrm_output.c:100
int xfrm_output(struct sk_buff *skb)
{
    struct dst_entry *dst = skb->dst;
    struct xfrm_state *x;

    while (1) {
        x = dst->xfrm;
        if (!x)
            break;

        // 查找策略
        x = xfrm_state_lookup(&x->id.daddr, x->id.spi, x->id.proto);
        if (!x)
            return -EINVAL;

        // 执行转换
        err = x->type->output(x, skb);
        if (err)
            return err;

        // 加密
        err = xfrm_encap(x, skb);
        if (err)
            return err;
    }

    return 0;
}
```

### 6.2 ESP 输出

```c
// net/xfrm/esp.c:300
static int esp_output(struct xfrm_state *x, struct sk_buff *skb)
{
    struct esp_data *esp = x->data;
    struct esp_hdr *esph;
    struct iphdr *iph;

    // 添加 ESP 头
    skb_push(skb, esp->conf.iv_len + sizeof(*esph));

    // 加密
    esp->conf.desc->encrypt(esp, skb);

    // 添加认证
    if (esp->auth) {
        skb_push(skb, esp->auth->icv_full_len);
        esp->auth->verify(esp, skb);
    }

    return dst->xfrm->type->output(x, skb);
}
```

## 7. 模式

### 7.1 传输模式

```
原始 IP 头 | TCP/UDP 头 | 数据
      |
      +-> ESP 头 | 加密数据 | ESP 尾 | 认证
```

### 7.2 隧道模式

```
新 IP 头 | ESP 头 | 原始 IP 头 | TCP/UDP 头 | 数据 | ESP 尾 | 认证
```
