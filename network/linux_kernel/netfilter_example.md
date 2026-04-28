---
title: Netfilter 内核模块示例
---

# Netfilter 内核模块示例

## 1. Netfilter Hook 框架简介

Netfilter 是 Linux 内核提供的包过滤框架，允许内核模块在网络协议栈的关键位置拦截、检查和修改网络数据包。

### 1.1 nf_hook_ops 结构体

```c
// include/linux/netfilter.h
struct nf_hook_ops {
    struct list_head list;    // 链表节点，用于插入钩子链表

    // 钩子回调函数
    nf_hookfn *hook;

    // 网络设备，NULL 表示匹配所有设备
    struct net_device *dev;

    // 私有数据，会传递给 hook 函数
    void *priv;

    // 协议族：NFPROTO_IPV4, NFPROTO_IPV6, NFPROTO_ARP 等
    u_int8_t pf;

    // 钩子点编号
    unsigned int hooknum;

    // 优先级，越小越先执行
    int priority;
};
```

### 1.2 注册与注销 Hook

```c
// 注册钩子
int nf_register_net_hook(struct net *net, const struct nf_hook_ops *ops);

// 注销钩子
void nf_unregister_net_hook(struct net *net, const struct nf_hook_ops *ops);

// 老版本内核接口（全局，非命名空间）
int nf_register_hook(struct nf_hook_ops *ops);
void nf_unregister_hook(struct nf_hook_ops *ops);
```

## 2. 完整内核模块示例

以下是一个完整的 Netfilter 内核模块示例，实现基本的包过滤功能：

```c
// netfilter_example.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/skbuff.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/icmp.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Example");
MODULE_DESCRIPTION("Netfilter Hook Example");

// 私有数据结构
struct nf_priv {
    unsigned int drop_tcp;
    unsigned int drop_udp;
    unsigned int drop_icmp;
    unsigned int accept_all;
};

// Hook 函数
static unsigned int hook_func(void *priv,
                             struct sk_buff *skb,
                             const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct tcphdr *tcph;
    struct udphdr *udph;
    struct nf_priv *pinfo = priv;

    // 检查 sk_buff 有效性
    if (!skb)
        return NF_ACCEPT;

    // 获取 IP 头
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;

    // 仅处理 IPv4
    if (iph->version != 4)
        return NF_ACCEPT;

    // 根据协议类型处理
    switch (iph->protocol) {
    case IPPROTO_TCP:
        // 获取 TCP 头
        tcph = tcp_hdr(skb);
        if (!tcph)
            return NF_ACCEPT;

        printk(KERN_INFO "TCP: %pI4:%d -> %pI4:%d\n",
               &iph->saddr, ntohs(tcph->source),
               &iph->daddr, ntohs(tcph->dest));

        // 根据配置丢弃 TCP 包
        if (pinfo->drop_tcp) {
            printk(KERN_INFO "Dropping TCP packet\n");
            return NF_DROP;
        }
        break;

    case IPPROTO_UDP:
        // 获取 UDP 头
        udph = udp_hdr(skb);
        if (!udph)
            return NF_ACCEPT;

        printk(KERN_INFO "UDP: %pI4:%d -> %pI4:%d\n",
               &iph->saddr, ntohs(udph->source),
               &iph->daddr, ntohs(udph->dest));

        // 根据配置丢弃 UDP 包
        if (pinfo->drop_udp) {
            printk(KERN_INFO "Dropping UDP packet\n");
            return NF_DROP;
        }
        break;

    case IPPROTO_ICMP:
        printk(KERN_INFO "ICMP: %pI4 -> %pI4, type=%d\n",
               &iph->saddr, &iph->daddr,
               ((struct icmphdr *)(iph + 1))->type);

        // 根据配置丢弃 ICMP 包
        if (pinfo->drop_icmp) {
            printk(KERN_INFO "Dropping ICMP packet\n");
            return NF_DROP;
        }
        break;

    default:
        printk(KERN_INFO "Other protocol: %d\n", iph->protocol);
        break;
    }

    return NF_ACCEPT;
}

// 定义 Hook 操作结构
static struct nf_hook_ops nf_hook_ops = {
    .hook     = hook_func,
    .pf       = NFPROTO_IPV4,
    .hooknum  = NF_INET_PRE_ROUTING,
    .priority = NF_IP_PRI_FIRST,
};

// 模块初始化
static int __init nf_example_init(void)
{
    static struct nf_priv priv_data = {
        .drop_tcp = 0,
        .drop_udp = 0,
        .drop_icmp = 0,
        .accept_all = 1,
    };

    printk(KERN_INFO "Netfilter example module loaded\n");

    // 设置私有数据
    nf_hook_ops.priv = &priv_data;

    // 注册 Hook
    return nf_register_hook(&nf_hook_ops);
}

// 模块退出
static void __exit nf_example_exit(void)
{
    // 注销 Hook
    nf_unregister_hook(&nf_hook_ops);
    printk(KERN_INFO "Netfilter example module unloaded\n");
}

module_init(nf_example_init);
module_exit(nf_example_exit);
```

## 3. 代码分析

### 3.1 Hook 函数签名

```c
typedef unsigned int nf_hookfn(void *priv,
                               struct sk_buff *skb,
                               const struct nf_hook_state *state);
```

参数说明：

| 参数 | 类型 | 说明 |
|-----|------|-----|
| priv | void * | 私有数据，注册时设置 |
| skb | struct sk_buff * | 待处理的 socket 缓冲区 |
| state | struct nf_hook_state * | 钩子状态信息 |

nf_hook_state 结构：

```c
struct nf_hook_state {
    unsigned int hook;        // 钩子点编号
    u_int8_t pf;              // 协议族
    struct net_device *in;    // 入站设备
    struct net_device *out;   // 出站设备
    struct sock *sk;          // 关联的 sock
    struct net *net;          // 网络命名空间
};
```

### 3.2 struct sk_buff 操作

sk_buff 是 Linux 内核中表示网络数据包的核心数据结构：

```c
// 获取 IP 头
struct iphdr *iph = ip_hdr(skb);

// 获取 TCP 头（注意：iph 必须已验证不为 NULL）
struct tcphdr *tcph = tcp_hdr(skb);

// 获取 UDP 头
struct udphdr *udph = udp_hdr(skb);

// 获取数据指针和长度
unsigned char *data = skb->data;
unsigned int len = skb->len;

// 检查层信息
struct dst_entry *dst = skb_dst(skb);
```

### 3.3 协议头访问

获取各层协议头的辅助函数（定义于 `include/linux/skbuff.h`）：

```c
static inline struct iphdr *ip_hdr(const struct sk_buff *skb);
static inline struct ipv6hdr *ipv6_hdr(const struct sk_buff *skb);
static inline struct tcphdr *tcp_hdr(const struct sk_buff *skb);
static inline struct udphdr *udp_hdr(const struct sk_buff *skb);
static inline struct icmphdr *icmp_hdr(const struct sk_buff *skb);
```

### 3.4 返回值

| 返回值 | 说明 |
|-------|------|
| NF_ACCEPT | 接受数据包，继续正常处理 |
| NF_DROP | 丢弃数据包 |
| NF_STOLEN | 数据包被"窃取"，不继续处理 |
| NF_QUEUE | 排队到用户空间处理 |
| NF_REPEAT | 重新调用当前钩子 |
| NF_STOP | 停止处理（NF_STOLEN 的新名称） |

## 4. 编译与加载

### 4.1 Makefile 示例

```makefile
obj-m := netfilter_example.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

.PHONY: all clean
```

### 4.2 编译与加载

```bash
# 编译模块
make

# 加载模块
sudo insmod netfilter_example.ko

# 查看模块信息
lsmod | grep netfilter_example
dmesg | tail

# 卸载模块
sudo rmmod netfilter_example

# 查看内核日志
dmesg | grep Netfilter
```

### 4.3 完整 Makefile（支持交叉编译）

```makefile
obj-m := netfilter_example.o

# 内核源码路径
KDIR := /lib/modules/$(shell uname -r)/build

# 交叉编译器（注释掉使用默认）
# CC := aarch64-linux-gnu-gcc
# CROSS_COMPILE := aarch64-linux-gnu-

PWD := $(shell pwd)

EXTRA_CFLAGS := -DDEBUG

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

help:
	$(MAKE) -C $(KDIR) M=$(PWD) help
```

## 5. 注意事项

### 5.1 内核版本差异

不同内核版本间 Netfilter API 有显著变化：

| 特性 | 旧版本 (< 3.13) | 新版本 (>= 3.13) |
|------|-----------------|------------------|
| 注册接口 | `nf_register_hook()` | `nf_register_net_hook()` |
| 命名空间 | 不支持 | 支持 `struct net *` 参数 |
| Hook 链表 | 双向链表 | nf_hook_entries 结构 |
| xt_match | `match()` | `match()` + `checkentry()` |

兼容性处理示例：

```c
// 兼容处理
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 13, 0)
    nf_register_hook(&nf_hook_ops);
#else
    nf_register_net_hook(&init_net, &nf_hook_ops);
#endif

// 卸载时同样处理
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 13, 0)
    nf_unregister_hook(&nf_hook_ops);
#else
    nf_unregister_net_hook(&init_net, &nf_hook_ops);
#endif
```

### 5.2 网络命名空间

在命名空间环境中使用时，需要特别注意：

```c
// 获取当前网络命名空间
struct net *net = &init_net;  // 初始命名空间

// 或从 skb 获取
struct net *net = dev_net(skb->dev);

// 注册到特定命名空间
nf_register_net_hook(net, &nf_hook_ops);

// 确保在正确的命名空间中操作
if (!net_eq(net, current->nsproxy->net_ns))
    return NF_ACCEPT;
```

### 5.3 错误处理

```c
static unsigned int hook_func(void *priv,
                             struct sk_buff *skb,
                             const struct nf_hook_state *state)
{
    struct iphdr *iph;

    // 1. 检查 skb 是否有效
    if (!skb)
        return NF_ACCEPT;

    // 2. 检查 skb 长度
    if (skb->len < sizeof(struct iphdr))
        return NF_ACCEPT;

    // 3. 使用 pskb_may_pull 确保线性数据区包含 IP 头
    if (!pskb_may_pull(skb, sizeof(struct iphdr)))
        return NF_ACCEPT;

    // 4. 获取 IP 头
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;

    // 5. 检查 IP 头长度
    if (iph->ihl < 5)
        return NF_DROP;

    // 6. 确保完整 IP 头在线性区
    if (!pskb_may_pull(skb, iph->ihl * 4))
        return NF_ACCEPT;

    // 7. 重新获取 IP 头（可能重新分配）
    iph = ip_hdr(skb);

    return NF_ACCEPT;
}
```

### 5.4 RCU 同步

Hook 函数在 RCU 临界区中执行，需要注意：

```c
// Hook 函数中不允许使用 sleeping 分配
void *private_data;  // 预分配，不在 hook 中分配

// 不允许在 hook 中使用锁
// 如果需要原子操作，使用 atomic_t

// 读取 skb 数据时保持 rcu_read_lock() 已持有的语义
// 内核已在调用 hook 前获取锁
```

### 5.5 调试技巧

```c
// 使用 netif_msg_* 打印调试信息
if (netif_msg_timer(skb))
    printk(KERN_DEBUG "debug info\n");

// 使用 tracepoint
#include <trace/events/skb.h>
trace_skb_copy(skb);

// 查看注册的所有 hooks
cat /proc/net/netfilter/nf_conntrack

// 使用 iptables 配合调试
iptables -A INPUT -j LOG --log-prefix "INPUT: "
```

## 6. 扩展功能

### 6.1 修改数据包内容

```c
static unsigned int modify_packet(void *priv,
                                  struct sk_buff *skb,
                                  const struct nf_hook_state *state)
{
    struct iphdr *iph;

    if (!pskb_may_pull(skb, sizeof(struct iphdr)))
        return NF_ACCEPT;

    iph = ip_hdr(skb);

    // 修改 TTL
    iph->ttl = 64;

    // 重新计算校验和
    ip_send_check(iph);

    // 标记 skb 为已修改
    skb->ip_summed = CHECKSUM_NONE;

    return NF_ACCEPT;
}
```

### 6.2 使用连接跟踪

```c
#include <net/netfilter/nf_conntrack.h>
#include <net/netfilter/nf_conntrack_l4proto.h>

static unsigned int conntrack_hook(void *priv,
                                  struct sk_buff *skb,
                                  const struct nf_hook_state *state)
{
    enum ip_conntrack_info ctinfo;
    struct nf_conn *ct;

    // 尝试获取连接跟踪条目
    ct = nf_ct_get(skb, &ctinfo);

    if (ct) {
        // 已建立连接
        printk(KERN_INFO "Connection tracked: %p\n", ct);
    } else {
        // 新连接
        printk(KERN_INFO "New connection\n");
    }

    return NF_ACCEPT;
}
```

## 7. 参考资料

- `include/linux/netfilter.h` - Netfilter 核心定义
- `include/linux/netfilter_ipv4.h` - IPv4 特定定义
- `net/netfilter/core.c` - Netfilter 核心实现
- `net/netfilter/nf_hook.c` - Hook 调用实现
- Linux Kernel Documentation - Networking/netfilter
