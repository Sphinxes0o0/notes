# Linux Netfilter 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [netfilter_subsystem.md](netfilter_subsystem.md) | 网络过滤: iptables, nftables, conntrack | net/netfilter/ |
| [netfilter_deep_dive_r1.md](netfilter_deep_dive_r1.md) | 深度分析 R1: conntrack, NAT, PIPAPO, xtables | net/netfilter/ |
| [netfilter_deep_dive_r2.md](netfilter_deep_dive_r2.md) | 深度分析 R2: nf_tables, nft_chain_hook, nft_rule_lookup, nft_set_pipapo | net/netfilter/ |

---

## 主要内容

### 1. Netfilter Hook 点
- PREROUTING, INPUT, FORWARD, OUTPUT, POSTROUTING
- Ingress

### 2. Hook 机制
- struct nf_hook_ops
- nf_hook_entries_grow()
- nf_hook_slow()

### 3. Connection Tracking
- NEW, ESTABLISHED, RELATED, INVALID
- Conntrack 哈希表

### 4. iptables
- ipt_do_table()
- filter, nat, mangle, raw 表
- match 和 target

### 5. nftables
- nft_do_chain()
- Table → Chain → Rule → Expression
- NFT_CONTINUE, NFT_BREAK, NFT_JUMP

### 6. Xtables
- xt_register_table()
- xt_entry_match / xt_entry_target

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| 核心 | net/netfilter/ |
| IPv4 | net/ipv4/netfilter/ |
| IPv6 | net/ipv6/netfilter/ |
| xtables | net/netfilter/ |
