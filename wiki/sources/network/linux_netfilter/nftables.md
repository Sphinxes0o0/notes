# nftables

nftables 是 Linux 上新一代的包过滤框架，它虽然是 Netfilter 的“继任者”，但并不是完全独立的系统——它是基于 Netfilter 核心架构之上重新设计的规则引擎与用户空间接口。

## 整体架构概览
nftables 底层依然依附于 Netfilter 内核框架，但重构了规则存储和执行逻辑
```
┌───────────────────────────────┐
│        用户空间 (user space)  │
│  nft 命令行工具 / libnftables │
└──────────────┬────────────────┘
               │ Netlink (NFNETLINK)
┌──────────────┴────────────────┐
│         内核空间 (kernel)     │
│ ┌───────────────────────────┐ │
│ │ nftables 内核子系统      │ │
│ │  ├─ nft_core             │ │
│ │  ├─ nft_rule_set (规则树)│ │
│ │  ├─ nft_expr (表达式集)  │ │
│ │  ├─ nft_chain (链)       │ │
│ │  ├─ nft_table (表)       │ │
│ │  └─ nft_hooks (Netfilter)│ │
│ └───────────────────────────┘ │
│     ↑             ↑           │
│ Netfilter 框架钩子   conntrack│
└────────────────────────────────┘
```
关键区别于旧版 iptables：

| 特性   | iptables           | nftables                 |
| ---- | ------------------ | ------------------------ |
| 数据结构 | 每条规则独立链表           | 规则集编译成表达式树               |
| 执行方式 | 线性匹配遍历             | 字节码解释执行（VM）              |
| 用户接口 | 专用命令+内核接口          | 通用 Netlink + libnftables |
| 扩展方式 | 内核模块（match/target） | 表达式（expr）和链式扩展           |
| 性能   | 多规则时线性变慢           | 优化结构，可编译字节码              |


## 核心底层技术组件

### Netlink 通信 (nfnetlink)

用户空间的命令 (nft) 与内核空间通信依赖 Netlink 协议族：
- 专用子协议：NFNETLINK_SUBSYS_NFTABLES
- 用户空间通过 libnftables 或 libmnl 构建 netlink 消息；
- 内核模块 nf_tables.ko 解析消息并更新规则集。

这使得：
- 规则更易批量原子更新（transaction-based）
- 用户态与内核态解耦，不需为每种 match/target 写 ioctl。

👉 内核接口：nf_tables_netlink.c

### nftables 虚拟机（nft_expr bytecode engine）
nftables 内核通过一个轻量虚拟机执行规则表达式。
- 每条规则在加载时被“编译”为一组 nft_expr 字节码（表达式链）；
- 每个表达式是一个结构体:

```c
struct nft_expr {
    const struct nft_expr_ops *ops;
    unsigned char data[];
};
```
ops 定义了执行逻辑，如 compare、counter、meta、payload、bitwise 等。

- 运行时遍历这些表达式执行逻辑判断；
- 当匹配成功可调用动作表达式（如 verdict、counter、log、nat 等）。

### Netfilter Hook 集成

底层仍依赖 Netfilter 钩子：

- 对 IPv4/IPv6/ARP/Bridge/Inet 协议族注册：
  - NF_INET_PRE_ROUTING
  - NF_INET_LOCAL_IN
  - NF_INET_FORWARD
  - NF_INET_LOCAL_OUT
  - NF_INET_POST_ROUTING
- 每当包经过这些点，nftables 会调用相应链表的规则集（chain）。

代码位置：net/netfilter/nf_tables_api.c, nf_tables_core.c。

### nft_set 与查找加速机制
nftables 支持高效的集合匹配（set / map）：
- 内核中通过 rhashtable / rbtree / hash 实现。
- 提供高效匹配和关联映射（如 IP → 动作）。

这比 iptables 的线性规则匹配快得多，尤其在大规则集（成千上万条 IP）场景。

### conntrack（连接跟踪）集成

nftables 内部复用 Netfilter conntrack 框架：

提供连接状态（NEW, ESTABLISHED, RELATED...）

用于状态匹配、NAT、反欺骗等。

内核模块：nf_conntrack.ko、nf_nat.ko
对应 nftables 表达式：ct state, ct mark, ct zone。

### 事务（Atomic Transactions）
nftables 通过 事务模型（transaction model）支持原子更新规则集：
- 所有规则修改（add/delete/replace）被放入事务；
- 一次性提交，内核切换新规则集；
- 避免中间状态造成安全空窗。

### 多协议支持（families）
nftables 支持多协议族：
- inet：IPv4 + IPv6 混合
- ip：仅 IPv4
- ip6：仅 IPv6
- arp：ARP 层
- bridge：二层桥接
- netdev：直接挂在网络设备层

## nftables 内核模块结构（源码层）
源码路径：
```
net/netfilter/
 ├─ nf_tables_api.c      → Netlink 接口 & 表/链/规则管理
 ├─ nf_tables_core.c     → 表达式执行引擎（nft_vm）
 ├─ nf_tables_expr.c     → 各种表达式实现（payload, cmp, log, verdict 等）
 ├─ nf_tables_set.c      → set/map 实现（hash, rbtree 等）
 ├─ nf_tables_trace.c    → 调试与 trace 框架
 └─ nf_tables_inet.c     → inet family 集成
```

## 执行流程简化
以一个 IPv4 包为例：
1️⃣ 内核在 NF_INET_LOCAL_IN 调用 nftables hook
2️⃣ 查找对应 table & chain
3️⃣ 执行 chain 中的表达式序列（nft_expr 数组）
4️⃣ 每个 expr 读取 packet 元数据（IP, TCP, mark...）→ 计算判断
5️⃣ 若匹配成功 → 执行动作表达式（例如 verdict = DROP / ACCEPT / JUMP / COUNTER）
6️⃣ 执行完毕 → 返回 verdict 给 Netfilter 框架

## 技术优势与设计理念

| 目标   | 技术实现                         |
| ---- | ---------------------------- |
| 性能   | 字节码解释器 + 高效集合查找 (rhashtable) |
| 可扩展性 | 动态表达式插件机制 (nft_expr_ops)     |
| 一致性  | 单一 Netlink 接口统一多协议           |
| 原子性  | 事务模型                         |
| 易维护  | 用户空间 libnftables 封装          |
| 安全性  | 无需多模块编译、减少用户态与内核态耦合          |


## 用户态开发
| 层次                    | 主要库                                                                          | 作用 / 场景                          |
| --------------------- | ---------------------------------------------------------------------------- | -------------------------------- |
| 🔹 **通用 Netlink 通信层** | **libmnl**                                                                   | 与内核的 Netlink 通信（底层基础库）           |
| 🔹 **nftables 配置接口层** | **libnftnl**, **libnftables**                                                | 构建、解析、序列化 nftables 规则、表、链        |
| 🔹 **数据包捕获 / 队列层**    | **libnetfilter_queue**                                                       | 用户空间接收 NFQUEUE 包，执行自定义处理后再决定是否放行 |
| 🔹 **连接跟踪层**          | **libnetfilter_conntrack**                                                   | 获取、监控、修改 conntrack 状态表           |
| 🔹 **日志接口层**          | **libnetfilter_log**                                                         | 从内核接收 NFLOG 输出的数据包日志             |
| 🔹 **状态同步层**          | **libnetfilter_cttimeout**, **libnetfilter_cthelper**, **libnetfilter_acct** | 管理连接跟踪的超时、helper、计数等高级功能         |


### 库的功能详解
1️⃣ libmnl（Minimal Netlink Library）

📍 作用：
这是所有 Netfilter 用户态库的通信基础。
- 提供简洁的 API 封装 Linux Netlink 套接字；
- 用于构造、发送、解析 Netlink 消息；
- 比传统 libnl 更轻量、无依赖。

📦 用途：
- 开发自定义 Netlink 客户端；
- 自己实现 nftables、conntrack、queue 的高性能控制接口；
- 嵌入式 / 安全代理中常用。

💡 例子：
```
struct mnl_socket *nl = mnl_socket_open(NETLINK_NETFILTER);
mnl_socket_sendto(nl, msg, len);
mnl_socket_recvfrom(nl, buf, sizeof(buf));
```

2️⃣ libnftnl（nftables Netlink API 库）

📍 作用：
- 提供创建、解析、序列化 nftables 对象（table、chain、rule、set、expr 等） 的接口；
- 基于 Netlink 消息构建完整对象描述；
- 是 nft 命令行工具的底层实现依赖。

📦 用途：
- 自己编写程序动态生成 nftables 规则；
- 在控制平面中实现动态防火墙或安全策略下发；
- 替代手工调用 system("nft add rule ...")。

📘 API 示例：
```
struct nftnl_rule *r = nftnl_rule_alloc();
nftnl_rule_set_str(r, NFTNL_RULE_TABLE, "filter");
nftnl_rule_set_str(r, NFTNL_RULE_CHAIN, "input");
nftnl_rule_add_expr(r, expr_payload);
nftnl_rule_add_expr(r, expr_cmp);
nftnl_rule_add_expr(r, expr_verdict);
```

📚 依赖： libmnl

3️⃣ libnftables（高层封装）

📍 作用：
- 比 libnftnl 更高一层；
- 内置一个 nftables 解释器，能解析文本规则语法；
- 可以直接加载 .nft 规则文件、脚本；
- 自动管理事务、错误报告。

📦 用途：
- 若你不想直接构造 Netlink 消息，可用这个库；
- 可直接集成 “nftables CLI 语法”；
- 适合防火墙管理工具、配置守护进程（如 firewalld）。

💡 示例：
```
#include <libnftables.h>

struct nft_ctx *ctx = nft_ctx_new(NFT_CTX_DEFAULT);
nft_ctx_buffer_output(ctx);
nft_run_cmd_from_buffer(ctx, "add table inet myfilter");
printf("%s\n", nft_ctx_get_output(ctx));
nft_ctx_free(ctx);
```
4️⃣ libnetfilter_queue（NFQUEUE 队列接口）

📍 作用：
- 接收从内核通过 NFQUEUE 发送上来的数据包；
- 允许用户空间程序分析、修改、放行或丢弃；
- 常用于 入侵检测/防御系统 (IDS/IPS)、DPI（深度包检测）、流量审计。

📦 用途：
- 防火墙扩展：编写用户空间逻辑（如基于AI或规则的判断）；
- 实现流量镜像、过滤、负载均衡等；
- 与 Python 绑定（nfqueue-bindings）配合使用。

💡 例子：
```
#include <libnetfilter_queue/libnetfilter_queue.h>

static int cb(struct nfq_q_handle *qh, struct nfgenmsg *nfmsg,
              struct nfq_data *nfa, void *data) {
    struct nfqnl_msg_packet_hdr *ph = nfq_get_msg_packet_hdr(nfa);
    printf("Packet id=%u\n", ntohl(ph->packet_id));
    return nfq_set_verdict(qh, ntohl(ph->packet_id), NF_ACCEPT, 0, NULL);
}

int main() {
    struct nfq_handle *h = nfq_open();
    struct nfq_q_handle *qh = nfq_create_queue(h, 0, &cb, NULL);
    nfq_handle_packet(h, buf, len);
}
```
5️⃣ libnetfilter_conntrack

📍 作用：
- 提供对连接跟踪表（conntrack table）的管理；
- 可枚举、添加、删除、修改、过滤连接；
- 还可注册事件监听（新建/销毁连接）。

📦 用途：
- 网络状态监控；
- 实现会话级流量控制；
- 防火墙状态同步。

💡 示例：
```
struct nfct_handle *h = nfct_open(CONNTRACK, 0);
nfct_query(h, NFCT_Q_GET, &ct);
nfct_callback_register(h, NFCT_T_ALL, cb, NULL);
```

6️⃣ libnetfilter_log

📍 作用：
- 用于从内核 NFLOG 接口接收日志包；
- 比内核 printk 或 syslog 更高效；
- 可实现自定义日志分析系统。

📦 用途：
- 安全审计；
- 包级别日志系统；
- 与 ELK / SIEM 集成。

7️⃣ 其他辅助库
| 库名                         | 作用                                   |
| -------------------------- | ------------------------------------ |
| **libnetfilter_cthelper**  | 管理 conntrack helper（例如 FTP、SIP 协议辅助） |
| **libnetfilter_cttimeout** | 管理 conntrack 超时策略                    |
| **libnetfilter_acct**      | 连接跟踪的流量计数管理                          |

### 常见组合方案（应用场景）
| 场景                         | 推荐库组合                                          |
| -------------------------- | ---------------------------------------------- |
| 🔥 动态防火墙控制面                | libnftables + libmnl                           |
| 📡 用户态包处理（DPI / IDS / IPS） | libnetfilter_queue + libmnl                    |
| 📈 流量监控 / 可视化              | libnetfilter_conntrack + libnetfilter_log      |
| 🧰 自定义安全策略引擎               | libnftnl + libnftables                         |
| 🕹️ NFLOG 收集系统             | libnetfilter_log + libmnl                      |
| 🧩 协议辅助开发                  | libnetfilter_cthelper + libnetfilter_cttimeout |

### 典型架构（自定义防火墙系统）
```
┌─────────────────────────────────────┐
│           用户空间自定义程序           │
│ ┌─────────────────────────────────┐ │
│ │ 防火墙控制面（规则下发/管理）        │ │
│ │  → libnftables / libnftnl       │ │
│ │  → 规则表管理（table/chain/rule） │ │
│ ├─────────────────────────────────┤ │
│ │ 数据面（包处理 / 状态分析）         │ │
│ │  → libnetfilter_queue (NFQUEUE)  │ │
│ │  → libnetfilter_conntrack        │ │
│ │  → libnetfilter_log / acct       │ │
│ ├─────────────────────────────────┤ │
│ │ 事件同步 / 状态监控 / 可视化        │ │
│ │  → libmnl 通信 + 自定义协议       │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Linux 内核 (Netfilter 框架)  │
    │  nf_tables, nf_conntrack,  │
    │  nf_nat, nf_queue 等模块    │
    └────────────────────────────┘
```

三种常见防火墙架构模型
1️⃣ 控制面防火墙（规则管理）

使用：
- libnftables 或 libnftnl
- libmnl

功能：
- 创建表、链、规则；
- 动态更新策略；
- 支持事务（规则原子更新）；
- 构建“防火墙守护进程”（类似 firewalld）。

💡 示例项目：

```
#include <libnftables.h>
struct nft_ctx *ctx = nft_ctx_new(NFT_CTX_DEFAULT);
nft_run_cmd_from_buffer(ctx, "add table inet fw");
nft_run_cmd_from_buffer(ctx, "add chain inet fw input { type filter hook input priority 0; }");
nft_run_cmd_from_buffer(ctx, "add rule inet fw input tcp dport 22 accept");
nft_ctx_free(ctx);
```

2️⃣ 数据面防火墙（NFQUEUE 用户空间过滤）

使用：
- libnetfilter_queue
- libmnl（间接依赖）

功能：

从内核队列接收数据包；
- 检查 payload、协议头、应用层特征；
- 决定 DROP / ACCEPT / 修改；
- 适合做 DPI、防病毒、入侵检测、防DDoS。

💡 示例流程：
```
iptables -I FORWARD -j NFQUEUE --queue-num 0
```

```
int cb(struct nfq_q_handle *qh, struct nfgenmsg *nfmsg, struct nfq_data *nfa, void *data) {
    uint32_t id = ntohl(nfq_get_msg_packet_hdr(nfa)->packet_id);
    return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);
}
```

3️⃣ 状态防火墙 / NAT 跟踪系统

使用：
- libnetfilter_conntrack
- 可配合 libnetfilter_cttimeout, libnetfilter_cthelper

功能：
- 枚举连接表；
- 实时监控连接状态；
- 清理、同步状态（主备防火墙）；
- 自定义 NAT 会话规则。

💡 示例：
```
struct nfct_handle *h = nfct_open(CONNTRACK, 0);
nfct_callback_register(h, NFCT_T_NEW, cb_new, NULL);
nfct_callback_register(h, NFCT_T_DESTROY, cb_destroy, NULL);
nfct_catch(h);
```

## Refs

🔗 Netfilter 官方项目页 https://www.netfilter.org/projects/

🔗 libnftables API 文档 https://netfilter.org/projects/libnftables/

🔗 libnetfilter_queue examples https://netfilter.org/projects/libnetfilter_queue/

🔗 libnetfilter_conntrack examples https://netfilter.org/projects/libnetfilter_conntrack/

📘 Linux 内核源码：net/netfilter/ 与 include/uapi/linux/netfilter/


| 库名                         | 功能说明                                        | 常见用途                     |
| -------------------------- | ------------------------------------------- | ------------------------ |
| **libmnl**                 | Minimal Netlink Library；封装 Linux Netlink 通信 | 所有其他 Netfilter 库的基础依赖    |
| **libnftnl**               | 操作 nftables 对象（table、chain、rule、expr）       | 构建防火墙控制面                 |
| **libnftables**            | 高层封装，可直接解析 nft 语法                           | 用于防火墙管理工具（如 `firewalld`） |
| **libnetfilter_queue**     | 处理 NFQUEUE 的数据包                             | 用户空间防火墙、DPI、IDS/IPS      |
| **libnetfilter_conntrack** | 访问和监控连接跟踪表                                  | 状态防火墙、NAT 追踪、流量统计        |
| **libnetfilter_cthelper**  | 管理 conntrack helper（FTP/SIP 等协议辅助）          | 协议识别、防火墙扩展               |
| **libnetfilter_cttimeout** | 管理连接超时配置                                    | 动态调整不同协议的连接生存期           |
| **libnetfilter_acct**      | 访问流量统计数据（Accounting）                        | 流量计数与报表                  |
| **libnetfilter_log**       | 接收内核 NFLOG 输出                               | 实现高性能日志系统                |
