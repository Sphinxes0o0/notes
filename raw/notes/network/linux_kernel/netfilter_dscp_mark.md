# Netfilter xt_DSCP/xt_MARK

## 1. 模块架构

### 1.1 功能概述

DSCP 和 MARK 是 Netfilter 中用于分组标记的两个目标模块，分别设置 TOS 字段和 fwmark。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/netfilter/xt_DSCP.c` | DSCP 目标 |
| `net/netfilter/xt_MARK.c` | MARK 目标 |
| `include/uapi/linux/netfilter/xt_DSCP.h` | 用户空间接口 |
| `include/uapi/linux/netfilter/xt_MARK.h` | 用户空间接口 |

## 2. xt_DSCP

### 2.1 struct xt_DSCP_info

```c
// include/uapi/linux/netfilter/xt_DSCP.h:15
struct xt_DSCP_info {
    __u8 dscp;          // DSCP 值 (0-63)
    __u8 set_dscp;     // 要设置的 DSCP 值
};
```

### 2.2 xt_dscp_target()

```c
// net/netfilter/xt_DSCP.c:80
static unsigned int xt_dscp_target(struct sk_buff *skb,
                                   const struct xt_action_param *par)
{
    const struct xt_DSCP_info *info = par->targinfo;
    struct iphdr *iph;

    // 只处理 IPv4
    if (skb->protocol == htons(ETH_P_IP)) {
        iph = ip_hdr(skb);

        // 设置 DSCP (TOS 高 6 位)
        iph->tos &= ~IPTOS_TOS_MASK;
        iph->tos |= info->dscp << IPTOS_PREC_SHIFT;

        // 重新计算校验和
        ip_send_check(iph);
    }

    return XT_CONTINUE;
}
```

### 2.3 使用示例

```bash
# 设置 DSCP 为 EF (46)
iptables -t mangle -A FORWARD -p tcp --dport 80 -j DSCP --set-dscp 46

# 设置 DSCP 为 AF41 (34)
iptables -t mangle -A OUTPUT -p udp -j DSCP --set-dscp 34
```

## 3. xt_MARK

### 3.1 struct xt_mark_tginfo

```c
// include/uapi/linux/netfilter/xt_MARK.h:15
struct xt_mark_tginfo {
    __u32 mark;
    __u32 mask;          // 掩码 (与 mark 进行 AND 操作)
};

struct xt_mark_tginfo2 {
    __u32 mark;
    __u32 mask;
};
```

### 3.2 xt_mark_target()

```c
// net/netfilter/xt_MARK.c:60
static unsigned int xt_mark_target(struct sk_buff *skb,
                                    const struct xt_action_param *par)
{
    const struct xt_mark_tginfo *info = par->targinfo;

    // 设置 fwmark
    skb->mark &= ~info->mask;
    skb->mark |= info->mark & ~info->mask;

    return XT_CONTINUE;
}
```

### 3.3 使用示例

```bash
# 标记所有 HTTP 流量
iptables -t mangle -A PREROUTING -p tcp --dport 80 -j MARK --set-mark 1

# 标记并设置掩码
iptables -t mangle -A PREROUTING -p tcp -j MARK --set-mark 0x10/0xF0

# 查看标记
iptables -t mangle -L -v -n
```

## 4. DSCP 值

### 4.1 PHB (Per-Hop Behavior)

| DSCP | 名称 | 用法 |
|-----|------|-----|
| 0 | BE | Best Effort (默认) |
| 46 | EF | Expedited Forwarding (Voice) |
| 34 | AF41 | High Priority |
| 26 | AF31 | Medium High |
| 18 | AF21 | Medium Low |
| 10 | CS1 | Low Priority |

### 4. TOS 到 DSCP 映射

```c
// TOS 字段结构
// +---+-------+
// |IP |  DSCP |
// |Pre| (6bit)|
// +---+-------+
```

## 5. 与 TC 交互

### 5.1 fwmark 作为 TC 匹配

```bash
# 在 mangle 表标记
iptables -t mangle -A POSTROUTING -o eth0 -j MARK --set-mark 0x1

# 在 TC 中使用 fwmark 进行过滤
tc filter add dev eth0 parent 1: protocol ip handle 0x1 fw flowid 1:10
```

### 5.2 skb->mark 传播

```c
// mark 在发送时可能被清除
// 使用 -j CONNMARK 保存 mark 到连接
iptables -t mangle -A PREROUTING -j CONNMARK --save-mark
iptables -t mangle -A OUTPUT -j CONNMARK --restore-mark
```
