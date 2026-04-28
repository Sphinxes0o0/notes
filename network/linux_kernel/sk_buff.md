# sk_buff - 套接字缓冲区管理

## 1. 模块架构

### 1.1 功能概述

`sk_buff`（socket buffer）是 Linux 网络栈中用于描述网络数据包的核心数据结构。它贯穿整个协议栈，从设备驱动接收数据开始，经过协议处理，最终传递到用户空间或发送出去。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/skbuff.c` | sk_buff 实现 (约 4500+ 行) |
| `include/linux/skbuff.h` | 核心数据结构定义 |
| `include/net/sock.h` | sock 与 sk_buff 的关联 |

## 2. 关键数据结构

### 2.1 struct sk_buff

```c
// include/linux/skbuff.h:150
struct sk_buff {
    // 链表指针
    struct sk_buff          *next;       // 下一节点
    struct sk_buff          *prev;       // 前一节点

    // 私有存储（被各协议使用）
    __u32                   len;         // 数据长度
    __u32                   data_len;    // 数据分段长度
    __u16                   mac_len;    // MAC 头长度
    __u16                   hdr_len;    // 头长度

    // 缓冲区和指针
    sk_buff_data_t          head;       // 缓冲起始
    sk_buff_data_t          end;        // 缓冲结束
    sk_buff_data_t          data;       // 数据起始
    sk_buff_data_t          tail;       // 数据结束

    // 网络层信息
    struct sock             *sk;         // 关联的 sock
    struct net_device       *dev;        // 关联的 net_device
    struct sec_path         *spath;      // 安全路径 (IPsec)

    // 校验和
    __sum16                 csum;        // 校验和
    __sum16                 csum_start;  // csum 起始位置
    __wsum                  csum_offset; // csum 偏移

    // 头信息
    unsigned long           _skb_refdst; // 路由目的
    unsigned short         protocol;     // 协议类型
    unsigned short         tstamp;       // 时间戳
    unsigned char           priority;    // 优先级

    // 选项
    unsigned char           local_df:1;  // 本地允许分片
    unsigned char           pfmemalloc:1;
    unsigned char           ip_summed:2; // CHECKSUM_*

    // 通用对象追踪
    void                    (*destructor)(struct sk_buff *);
    union {
        void                *私密数据;
        struct {
            struct sk_buff      *next_skb;
            atomic_t            *dtor_ref;
        };
    };

    // 时间戳
    ktime_t                tstamp;
    ktime_t                skb_mstamp_ns;

    // 队列映射
    u16                     queue_mapping;
};
```

### 2.2 布局图

```
sk_buff 内存布局:

┌─────────────────────────────────────────────────────────────┐
│  head (缓冲起始)                                            │
├─────────────────────────────────────────────────────────────┤
│  transport_header (传输层头)                                 │
├─────────────────────────────────────────────────────────────┤
│  network_header (网络层头)                                  │
├─────────────────────────────────────────────────────────────┤
│  mac_header (MAC 层头)                                      │
├─────────────────────────────────────────────────────────────┤
│  data ──────► payload (数据)                               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  tail (数据结束)                                            │
└─────────────────────────────────────────────────────────────┘
│  end (缓冲结束)                                             │
```

## 3. 分配与释放

### 3.1 分配函数

| 函数 | 位置 | 用途 |
|-----|------|-----|
| `alloc_skb()` | skbuff.c | 分配 sk_buff + 私有数据 |
| `__netdev_alloc_skb()` | skbuff.c | 分配用于设备收包 |
| `netdev_alloc_skb()` | skbuff.c | 分配并预留 headroom |
| `dev_alloc_skb()` | skbuff.c | 分配用于中断处理 |

```c
// skbuff.c:4234
struct sk_buff *alloc_skb(gfp_t priority, unsigned int size)
{
    // 1. 分配 struct sk_buff + size 字节的私有数据
    // 2. 初始化 head/end/data/tail 指针
    // 3. 设置 destructor = NULL
    // 4. 设置 refcnt = 1
}

// skbuff.c:4298
struct sk_buff *__netdev_alloc_skb(struct net_device *dev,
                                    unsigned int length, gfp_t gfp)
{
    // 1. 调用 alloc_skb
    // 2. 预留 NET_SKB_PAD 字节用于对齐和可选项
    // 3. 设置 dev = dev
}
```

### 3.2 释放函数

| 函数 | 用途 |
|-----|-----|
| `kfree_skb()` | 释放 sk_buff (用于接收) |
| `consume_skb()` | 释放 sk_buff (用于发送, 不计为错误) |

```c
// skbuff.c:939
void kfree_skb(struct sk_buff *skb)
{
    // 1. 调用 destructor (如果有)
    // 2. 减少 refcnt
    // 3. refcnt==0 时释放内存
}

void consume_skb(struct sk_buff *skb)
{
    // 与 kfree_skb 类似，但增加 sk_wmem_alloc 计数器
}
```

## 4. 克隆与复制

### 4.1 克隆 (共享数据)

```c
// skbuff.c:2327
struct sk_buff *skb_clone(struct sk_buff *skb, gfp_t priority)
{
    // 1. 分配新的 sk_buff 结构
    // 2. 复制共享的 skb_shared_info
    // 3. refcnt 原子递增
    // 4. 不复制数据，只共享数据指针
}
```

### 4.2 复制 (独立数据)

```c
// skbuff.c:2491
struct sk_buff *pskb_copy(struct sk_buff *skb, gfp_t gfp)
{
    // 1. 分配新的 sk_buff 和新的私有数据缓冲
    // 2. 复制所有头指针和数据
    // 3. 数据独立，可修改
}

// skbuff.c:2600
struct sk_buff *skb_copy(const struct sk_buff *skb, gfp_t gfp)
{
    // 完整复制，包括克隆数据区域
}
```

## 5. 头操作

### 5.1 skb_push - 添加头

```c
// skbuff.c:3725
static inline void *__skb_push(struct sk_buff *skb, unsigned int len)
{
    skb->data -= len;
    skb->len += len;
    return skb->data;
}

// 示例: 添加 ETH 头
eth_hdr = skb_push(skb, sizeof(struct ethhdr));
```

### 5.2 skb_pull - 移除头

```c
// skbuff.c:3744
static inline void *__skb_pull(struct sk_buff *skb, unsigned int len)
{
    skb->len -= len;
    return skb->data += len;
}

// 示例: 移除 IP 头后获取传输层
iph = skb_pull(skb, ip_hdrlen(skb));
trans_hdr = skb->data;
```

### 5.3 skb_put - 添加数据到尾部

```c
// skbuff.c:3759
static inline void *__skb_put(struct sk_buff *skb, unsigned int len)
{
    void *tmp = skb->tail;
    skb->tail += len;
    skb->len += len;
    return tmp;
}
```

### 5.4 skb_reserve - 预留空间

```c
// skbuff.c:3713
static inline void skb_reserve(struct sk_buff *skb, int len)
{
    skb->data += len;
    skb->tail += len;
}
```

## 6. 分片管理

### 6.1 struct skb_shared_info

```c
// include/linux/skbuff.h:876
struct skb_shared_info {
    unsigned char   nr_frags;        // 片段数量
    __u8            tx_flags;        // 发送标志
    unsigned short  gso_size;        // GSO 大小
    unsigned short  gso_segs;        // GSO 段数
    unsigned short  gso_type;        // GSO 类型
    struct sk_buff  *frag_list;     // 分片列表
    struct page     *frags[MAX_SKB_FRAGS];  // 页面片段
    __u32           dataref;
    void            (*destructor)(struct sk_buff *skb);
};
```

### 6.2 分片操作

```c
// 添加分片
skb_fill_page_desc(skb, i, page, offset, size);

// 检查是否有分片
skb_has_frag_list(skb);
```

## 7. 校验和

### 7.1 校验和选项

```c
enum {
    CHECKSUM_NONE           = 0,  // 不校验
    CHECKSUM_UNNECESSARY    = 1,  // 已校验
    CHECKSUM_COMPLETE       = 2,  // 完整校验
    CHECKSUM_PARTIAL        = 3,  // 部分校验 (硬件)
};
```

### 7.2 计算校验和

```c
// 计算 IPv4 校验和
__sum16 ip_fast_csum(const void *iph, unsigned int ihl);

// 计算伪头校验和
__wsum csum_tcpudp_magic(__be32 saddr, __be32 daddr, __u16 len,
                          __u8 proto, __wsum sum);

// 计算完整校验和
__sum16 csum_fold(__wsum sum);
```

## 8. 队列管理

### 8.1 接收队列

```c
// sock 结构中的接收队列
struct sk_buff_head sk_receive_queue;

// 操作函数
skb_queue_head_init(&sk->sk_receive_queue);
skb_queue_tail(&sk->sk_receive_queue, skb);
skb_dequeue(&sk->sk_receive_queue);
```

### 8.2 发送队列

```c
// sock 结构中的发送队列
struct sk_buff_head sk_write_queue;

// 操作函数
skb_queue_tail(&sk->sk_write_queue, skb);
skb_dequeue(&sk->sk_write_queue);
```

## 9. 典型使用流程

### 9.1 接收流程

```
NIC 接收中断
    ↓
netif_rx() / netif_receive_skb()
    ↓
分配 skb (__netdev_alloc_skb)
    ↓
协议处理 (ip_rcv, tcp_v4_rcv)
    ↓
skb_push() 移除各层头
    ↓
skb_queue_tail() 入队到 sock
    ↓
wake_up_interruptible() 唤醒用户进程
    ↓
recvmsg() 从队列取出
    ↓
skb_pull() 移除协议头
    ↓
copy_to_user() 复制到用户空间
    ↓
kfree_skb() 释放
```

### 9.2 发送流程

```
用户 sendmsg()
    ↓
sock_alloc_send_skb() 分配 skb
    ↓
skb_put() 添加数据
    ↓
skb_push() 添加协议头 (TCP/IP)
    ↓
skb_push() 添加 MAC 头
    ↓
dev_queue_xmit() 发送到设备
    ↓
netif_start_queue() / netif_tx()
    ↓
NIC DMA 发送
    ↓
consume_skb() 释放
```

## 10. GRO (Generic Receive Offload)

### 10.1 GRO 缓冲结构

```c
struct napi_gro_cb {
    struct sk_buff *parent;        // gro 组中的第一个 skb
    unsigned long  age;            // 进入 gro 的时间
    int           count;          // gro 中的 skb 数量
    unsigned int  recurse_cnt;   // 递归计数
    __u32         flush:1;        // 强制刷新
    __u32         free:1;         // 释放 gro 组
    __u32         encap_mark:1;   // 隧道封装标记
    structgro_remcatail;         // 尾部数据
};
```

### 10.2 GRO 处理流程

```c
// dev.c 中 napi_gro_receive()
gro_result napi_gro_receive(struct napi_struct *napi, struct sk_buff *skb)
{
    // 1. 调用 gro_counters 统计
    // 2. 遍历 device 的 gro_list
    // 3. 调用 gro_receive() 尝试合并
    // 4. 如果不能合并，调用 gro_complete
    // 5. 返回合并结果
}
```
