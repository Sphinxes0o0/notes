# Netfilter xt_TCPMSS

## 1. 模块架构

### 1.1 功能概述

xt_TCPMSS 用于修改 TCP 最大段大小 (MSS)，主要在 PPTP、IPsec 和其他隧道场景中使用。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/netfilter/xt_TCPMSS.c` | TCPMSS 实现 |
| `include/uapi/linux/netfilter/xt_TCPMSS.h` | 用户空间接口 |

## 2. 核心数据结构

### 2.1 struct xt_tcpmss_info

```c
// include/uapi/linux/netfilter/xt_TCPMSS.h:15
struct xt_tcpmss_info {
    __u16 mss;           // MSS 值
    __u8  minmss;        // 最小 MSS (syn flood)
};
```

## 3. 实现

### 3.1 xt_tcpmss_target()

```c
// net/netfilter/xt_TCPMSS.c:120
static unsigned int xt_tcpmss_target(struct sk_buff *skb,
                                     const struct xt_action_param *par)
{
    const struct xt_tcpmss_info *info = par->targinfo;
    struct tcphdr *tcph;
    int tcphoff;
    __be16 newtotlen, newmss;

    // 获取 TCP 头
    tcph = skb_header_pointer(skb, par->thoff, sizeof(*tcph), buff);
    if (!tcph)
        return NF_DROP;

    // 计算 MSS 选项
    newmss = htons(info->mss);
    tcphoff = par->thoff;

    // 修改 MSS 选项
    return nf_mangle_tcp(skb, par->hooknum, tcphoff,
                         tcph, sizeof(*tcph),
                         &newmss, sizeof(newmss));
}
```

### 3.2 nf_mangle_tcp()

```c
// net/netfilter/nf_conntrack_netlink.c (类似函数)
// 用于修改 TCP 选项
static int nf_mangle_tcp(struct sk_buff *skb, int hooknum,
                         unsigned int dataoff,
                         struct tcphdr *tcph,
                         int tcphoff,
                         const __u8 *newopts,
                         int optlen)
{
    // 1. 调整 skb
    if (!skb_make_writable(skb, dataoff + tcphoff + tcph->doff * 4))
        return 0;

    // 2. 复制并修改
    tcph = (struct tcphdr *)(skb->data + tcphoff);
    memcpy((char *)tcph + sizeof(*tcph), newopts, optlen);

    // 3. 更新 TCP 头
    tcph->doff = (sizeof(*tcph) + optlen) / 4;

    // 4. 重新计算校验和
    inet_proto_csum_replace4(&tcph->check, skb,
                            oldmss, newmss, 1);

    return 1;
}
```

## 4. 使用示例

### 4.1 基本用法

```bash
# 设置 MSS 为 1400
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1400

# 设置 MSS 为 PMTU
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
```

### 4.2 与 PPtP 配合

```bash
# GRE 隧道
iptables -t mangle -A FORWARD -p 47 -j TCPMSS --set-mss 1400
```

### 4.3 与 IPsec 配合

```bash
# IPsec 封装后 MTU 减小
iptables -t mangle -A POSTROUTING -o ipsec+ -j TCPMSS --clamp-mss-to-pmtu
```

## 5. clamp-mss-to-pmtu

### 5.1 PMTU 发现

```c
// 自动根据路径 MTU 调整 MSS
// 使用 --clamp-mss-to-pmtu 时:
// 1. 计算出口设备的 MTU
// 2. 减去 IP 头 (20) + TCP 头 (20) = MSS 上限
// 3. 如果 MSS 大于该值，使用该值
```

### 5.3 MSS 范围

```c
// 典型 MSS 值:
// Ethernet: 1500 - 40 (IP+TCP) = 1460
// VPN:     1400 - 40 = 1360
// PPPoE:   1492 - 40 = 1452
```

## 6. 典型问题

### 6.1 大文件传输失败

```
原因: MSS 设置过小但 PMTU 未发现
解决: 使用 --clamp-mss-to-pmtu 或设置合理的 MSS
```

### 6.2 SYN 包 MSS 修改

```
注意: 只有 SYN 和 SYN/ACK 包可以修改 MSS
因为 MSS 选项只在 TCP 握手时协商
```
