# Netfilter 核心框架

## 1. 模块架构

### 1.1 功能概述

Netfilter 是 Linux 内核的包过滤框架，提供了在网络协议栈的关键位置拦截和处理数据包的能力。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/netfilter/core.c` | Netfilter 核心 |
| `net/netfilter/nf_hook.c` | 钩子实现 |
| `include/linux/netfilter.h` | Netfilter 定义 |
| `include/linux/netfilter_ipv4.h` | IPv4 特定定义 |

## 2. 钩子点

### 2.1 IPv4 钩子点

```c
// include/linux/netfilter_ipv4.h
enum nf_inet_hooks {
    NF_INET_PRE_ROUTING,   // 路由前 - 接收包
    NF_INET_LOCAL_IN,     // 本地输入 - 目的为本地
    NF_INET_FORWARD,      // 转发 - 目的为其他主机
    NF_INET_LOCAL_OUT,    // 本地输出 - 本地生成
    NF_INET_POST_ROUTING, // 路由后 - 发送包
    NF_INET_NUMHOOKS
};
```

### 2.2 IPv6 钩子点

```c
// include/linux/netfilter_ipv6.h
enum nf_inet_hooks {
    NF_INET_PRE_ROUTING,
    NF_INET_LOCAL_IN,
    NF_INET_FORWARD,
    NF_INET_LOCAL_OUT,
    NF_INET_POST_ROUTING,
    NF_INET_NUMHOOKS
};
```

## 3. 钩子结构

### 3.1 struct nf_hook_ops

```c
// include/linux/netfilter.h:62
struct nf_hook_ops {
    struct list_head list;    // 链表

    // 钩子回调
    nf_hookfn *hook;          // 回调函数
    struct net_device *dev;    // 设备 (NULL 表示全部)
    void *priv;               // 私有数据

    u_int8_t pf;             // 协议族 (NFPROTO_*)
    unsigned int hooknum;     // 钩子编号
    int priority;             // 优先级 (越小越先)
};
```

### 3.2 回调函数

```c
// include/linux/netfilter.h:46
typedef unsigned int nf_hookfn(void *priv,
                               struct sk_buff *skb,
                               const struct nf_hook_state *state);

struct nf_hook_state {
    unsigned int hook;
    u_int8_t pf;
    struct net_device *in;
    struct net_device *out;
    struct sock *sk;
    struct net *net;
};
```

## 4. 钩子注册

### 4.1 nf_register_net_hook()

```c
// net/netfilter/core.c:258
int nf_register_net_hook(struct net *net, const struct nf_hook_ops *ops)
{
    // 1. 分配 nf_hook_entries
    // 2. 添加到钩子链表
    // 3. 返回
}
```

### 4.2 nf_unregister_net_hook()

```c
// net/netfilter/core.c:276
void nf_unregister_net_hook(struct net *net, const struct nf_hook_ops *ops)
{
    // 从链表移除
    // 同步等待
}
```

## 5. 钩子调用

### 5.1 nf_hook_slow()

```c
// net/netfilter/nf_hook.c:96
int nf_hook_slow(struct sk_buff *skb, struct nf_hook_state *state)
{
    struct nf_hook_entries *entries;
    unsigned int verdict;
    int i;

    // 获取钩子条目
    entries = rcu_dereference(state->net->nf.hooks_entries[state->pf][state->hook]);

    // 遍历所有钩子
    for (i = 0; i < entries->num_hook_entries; i++) {
        verdict = entries->hooks[i].hook(entries->hooks[i].priv, skb, state);

        if (verdict != NF_ACCEPT) {
            if (verdict != NF_REPEAT)
                return verdict;
            i--;
        }
    }

    return NF_ACCEPT;
}
```

## 6. x_tables 框架

### 6.1 表结构

```c
// net/netfilter/x_tables.c
struct xt_table {
    struct list_head list;          // 表链表
    unsigned int valid_hooks;       // 有效钩子掩码
    struct xt_table_info *private;  // 表信息
    const struct xt_table_ops *ops;
    u_int8_t af;                   // 地址族 (AF_INET/AF_INET6)
    struct module *me;
};
```

### 6.2 规则结构

```c
// include/uapi/linux/netfilter/x_tables.h
struct xt_entry_match {
    __u16 match_size;           // 匹配大小
    char name[XT_FUNCTION_MAXNAMELEN];  // 匹配名称
    __u8 revision;              // 修订版
    __u8 private[0];            // 匹配数据
};

struct xt_entry_target {
    __u16 target_size;         // 目标大小
    char name[XT_FUNCTION_MAXNAMELEN];  // 目标名称
    __u8 revision;              // 修订版
    __u8 private[0];            // 目标数据
};
```

## 7. iptables 命令

### 7.1 iptables 链

| 链 | 钩子点 | 用途 |
|---|-------|-----|
| PREROUTING | NF_INET_PRE_ROUTING | 路由前处理 |
| INPUT | NF_INET_LOCAL_IN | 本地输入 |
| FORWARD | NF_INET_FORWARD | 转发 |
| OUTPUT | NF_INET_LOCAL_OUT | 本地输出 |
| POSTROUTING | NF_INET_POST_ROUTING | 路由后处理 |

### 7.2 内建目标

```c
// net/netfilter
NF_DROP       // 丢弃包
NF_ACCEPT     // 接受包
NF_STOLEN     // 接管包，不继续处理
NF_QUEUE      // 排队到用户空间
NF_REPEAT     // 重复当前钩子
NF_CONTINUE   // 继续下一个钩子
```

## 8. 连接跟踪

### 8.1 连接跟踪结构

```c
// net/netfilter/nf_conntrack.h
struct nf_conn {
    struct nf_conntrack_tuple_hash __rcu *tuplehash[IP_CT_DIR_MAX];
    atomic_t use;                      // 引用计数
    void *sfe_entry;                  // 状态
    unsigned long status;              // 状态
    struct sk_buff *sfe_skb;         // 相关 skb
    struct nf_conn *master;          // 主连接
    struct timer_list timeout;        // 超时定时器
    ...
};
```

### 8.2 连接状态

```c
// include/uapi/linux/netfilter/nf_conntrack_common.h
enum ip_conntrack_status {
    IPS_EXPECTED,        // 预期连接
    IPS_SEEN_REPLY,     // 已见回复
    IPS_ASSURED,        // 确认连接
    IPS_CONFIRMED,      // 已确认
    IPS_SRC_NAT,        // 源 NAT
    IPS_DST_NAT,        // 目的 NAT
    IPS_SEQ_ADJUST,     // 序列号调整
    IPS_SRC_NAT_DONE,   // 源 NAT 完成
    IPS_DST_NAT_DONE,   // 目的 NAT 完成
    IPS_DYING,          // 正在消失
    IPS_FIXED_TIMEOUT,  // 固定超时
};
```

## 9. NAT

### 9.1 NAT 钩子

```c
// net/ipv4/netfilter/nf_nat_rule.c
static unsigned int
nf_nat_rule_local_out(unsigned int hooknum, struct sk_buff *skb,
                     const struct net_device *out, ...)
{
    return nf_nat_rule_hook(skb, hooknum, out, NULL, AF_INET);
}
```

### 9.2 NAT 转换

```c
// net/netfilter/nf_nat_core.c
static int nf_nat_packet(struct nf_conn *ct, enum ip_conntrack_info ctinfo,
                        unsigned int hooknum, struct sk_buff *skb)
{
    enum nf_nat_manip_type maniptype = HOOK2MANIP(hooknum);

    // 获取源/目的地址和端口
    // 应用 NAT 转换
    // 更新校验和
}
```

## 10. 快速路径

### 10.1 nf_hookfn 快速路径

```c
// net/netfilter/nf_hook.c
static int nf_hook_slow(struct sk_buff *skb, struct nf_hook_state *state)
{
    // 遍历所有注册的钩子
    // 返回最终裁决
}
```

### 10.2 批量处理

```c
// net/netfilter/nfnetlink_hook.c
static int nfnetlink_rcv_msg(struct sk_buff *skb, struct nlmsghdr *nlh)
{
    // 处理来自用户空间的 netlink 消息
    // 添加/删除钩子
}
```
