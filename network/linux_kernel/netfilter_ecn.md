# Netfilter xt_HL/ipt_ECN

## 1. 模块架构

### 1.1 功能概述

ECN (Explicit Congestion Notification) 和 HL (Hop Limit) 是两个相关的 Netfilter 目标模块。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/netfilter/xt_HL.c` | Hop Limit 目标 |
| `net/netfilter/ip_tables.c` | ECN 支持 |
| `include/uapi/linux/netfilter/xt_HL.h` | 用户空间接口 |
| `include/uapi/linux/netfilter_ipv4/ipt_ECN.h` | ECN 定义 |

## 2. xt_HL (Hop Limit)

### 2.1 struct xt_HL_info

```c
// include/uapi/linux/netfilter/xt_HL.h:15
struct xt_HL_info {
    __u32 hl;            // Hop Limit 值
    __u32 mode;          // 操作模式
};

#define XT_HL_SET     0x01   // 设置
#define XT_HL_INC     0x02   // 增加
#define XT_HL_DEC     0x04   // 减少
```

### 2.2 xt_hl_target()

```c
// net/netfilter/xt_HL.c:60
static unsigned int xt_hl_target(struct sk_buff *skb,
                                 const struct xt_action_param *par)
{
    const struct xt_HL_info *info = par->targinfo;
    struct ipv6hdr *ip6h;
    struct iphdr *iph;

    if (skb->protocol == htons(ETH_P_IPV6)) {
        ip6h = ipv6_hdr(skb);

        switch (info->mode) {
        case XT_HL_SET:
            ip6h->hop_limit = info->hl;
            break;
        case XT_HL_INC:
            ip6h->hop_limit += info->hl;
            break;
        case XT_HL_DEC:
            ip6h->hop_limit -= info->hl;
            break;
        }
    }

    return XT_CONTINUE;
}
```

### 2.3 使用示例

```bash
# 设置 IPv6 Hop Limit
ip6tables -t mangle -A OUTPUT -j HL --set-hl 64

# 增加 Hop Limit
ip6tables -t mangle -A POSTROUTING -j HL --hl-inc 1

# 减少 Hop Limit
ip6tables -t mangle -A PREROUTING -j HL --hl-dec 1
```

## 3. ipt_ECN

### 3.1 struct ipt_ECN_info

```c
// include/uapi/linux/netfilter_ipv4/ipt_ECN.h:15
struct ipt_ECN_info {
    __u8 operation;      // 操作类型
    __u8 invert;         // 反转
    union {
        struct {
            __u8 ip_ect;   // IP ECT bit
        } ip;
        struct {
            __u8 tcpflgs;  // TCP 标志
            __u8 ect;      // ECT bit
            __u8 ce;       // CE bit
        } tcp;
    } proto;
};
```

### 3.2 操作类型

```c
// ipt_ECN.h
#define IPT_ECN_OP_SET      0x01   // 设置 ECT/CE
#define IPT_ECN_OP_MASK     0x02   // 掩码
#define IPT_ECN_OP_AND      0x03   // AND 操作
```

### 3.3 ECN 原理

```
ECN 使用 IP 头 TOS 字段的低 2 位:
- 00: 非 ECT (Not ECN-Capable Transport)
- 01: ECT(1) (ECN-Capable Transport)
- 10: ECT(0) (ECN-Capable Transport)
- 11: CE (Congestion Experienced)

TCP 中使用 ECE 和 CWR 标志:
- ECE (ECN-Echo): 通知接收到的 CE
- CWR (Congestion Window Reduced): 通知已降低窗口
```

## 4. ECN 在 Netfilter 中的支持

### 4.1 检查 ECN

```c
// net/ipv4/netfilter/ipt_ECN.c:100
static bool ecn_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct ipt_ECN_info *info = par->matchinfo;
    struct iphdr *iph;

    if (skb->protocol == htons(ETH_P_IP)) {
        iph = ip_hdr(skb);

        // 检查 IP ECT 位
        if (info->operation & IPT_ECN_OP_SET) {
            __u8 ect = iph->tos & IPTOS_ECN_MASK;
            if (ect != info->proto.ip.ip_ect)
                return false;
        }
    }

    return true;
}
```

### 4.2 设置 ECN

```c
// net/ipv4/netfilter/ipt_ECN.c:150
static int ecn_tg(struct sk_buff *skb, const struct xt_action_param *par)
{
    const struct ipt_ECN_info *info = par->targinfo;
    struct iphdr *iph;

    iph = ip_hdr(skb);

    switch (info->operation) {
    case IPT_ECN_OP_SET:
        iph->tos &= ~IPTOS_ECN_MASK;
        iph->tos |= info->proto.ip.ip_ect;
        break;
    case IPT_ECN_OP_MASK:
        iph->tos &= ~IPTOS_ECN_MASK;
        break;
    }

    ip_send_check(iph);
    return XT_CONTINUE;
}
```

## 5. 使用示例

### 5.1 ipt_ECN

```bash
# 设置 IP ECT 位
iptables -t mangle -A FORWARD -p tcp --dport 80 -j ECN --set-ip-ect 1

# 标记 CE (拥塞指示)
iptables -t mangle -A OUTPUT -p tcp -j ECN --set-ce

# 清除 ECT 位
iptables -t mangle -A PREROUTING -j ECN --mask
```

### 5.2 完整 ECN 流程

```bash
# 启用 ECN
echo 1 > /proc/sys/net/ipv4/tcp_ecn

# 允许 ECN 流量
iptables -A INPUT -p tcp -m ecn --ect 1 -j ACCEPT
```

## 6. ECN 与 TCP

```
正常拥塞控制:
1. 路由器检测到拥塞 → 设置 IP CE 位
2. 接收方收到 CE 包 → 设置 TCP ECE 标志
3. 发送方收到 ECE → 降低窗口，发送 CWR

ECN 拥塞控制:
1. 路由器支持 ECN → 用 CE 替代丢包
2. 接收方收到 CE 包 → 设置 TCP ECE
3. 发送方收到 ECE → 降低窗口，发送 CWR
```
