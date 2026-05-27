# Linux Kernel skbuff 内存管理分析

## 1. skbuff 核心结构体

### 1.1 struct sk_buff 定义

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 885-1103 行)

```c
struct sk_buff {
    union {
        struct {
            /* These two members must be first to match sk_buff_head. */
            struct sk_buff      *next;
            struct sk_buff      *prev;
            union {
                struct net_device *dev;
                unsigned long      dev_scratch;
            };
        };
        struct rb_node  rbnode;
        struct list_head list;
        struct llist_node ll_node;
    };

    struct sock     *sk;
    union {
        ktime_t     tstamp;
        u64         skb_mstamp_ns;
    };
    char            cb[48] __aligned(8);   // 控制缓冲区,各层私有

    union {
        struct {
            unsigned long _skb_refdst;
            void         (*destructor)(struct sk_buff *skb);  // 析构函数
        };
        struct list_head tcp_tsorted_anchor;
    };

    unsigned int    len,               // 总长度
                    data_len;          // 数据长度(非线性部分)
    __u16           mac_len,
                    hdr_len;

    __u16           queue_mapping;

    /* cloned 标志位 */
    __u8            __cloned_offset[0];
    __u8            cloned:1,
                    nohdr:1,
                    fclone:2,
                    peeked:1,
                    head_frag:1,
                    pfmemalloc:1,
                    pp_recycle:1;

    /* headers group - 通过单个 memcpy 复制 */
    struct_group(headers,
        __u8        __pkt_type_offset[0];
        __u8        pkt_type:3;
        __u8        ignore_df:1;
        __u8        dst_pending_confirm:1;
        __u8        ip_summed:2;
        __u8        ooo_okay:1;
        // ... 更多字段
        __u16       tc_index;
    );

    /* 关键指针 - 必须在末尾 */
    sk_buff_data_t  tail;              // 尾部指针
    sk_buff_data_t  end;               // end 指针
    unsigned char   *head,              // 头指针
                   *data;               // 数据指针
    unsigned int    truesize;           // 真实大小
    refcount_t      users;              // 引用计数

#ifdef CONFIG_SKB_EXTENSIONS
    struct skb_ext  *extensions;
#endif
};
```

### 1.2 struct skb_shared_info 定义

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 593-629 行)

```c
struct skb_shared_info {
    __u8        flags;
    __u8        meta_len;
    __u8        nr_frags;              // 片段数量
    __u8        tx_flags;
    unsigned short gso_size;            // GSO 大小
    unsigned short gso_segs;            // GSO 段数
    struct sk_buff *frag_list;          // 片段列表(用于 fraglist GSO)
    union {
        struct skb_shared_hwtstamps hwtstamps;
        struct xsk_tx_metadata_compl xsk_meta;
    };
    unsigned int gso_type;
    u32         tskey;

    atomic_t    dataref;                // 数据引用计数

    union {
        struct {
            u32 xdp_frags_size;
            u32 xdp_frags_truesize;
        };
        void    *destructor_arg;         // 析构函数参数
    };

    /* must be last field, see pskb_expand_head() */
    skb_frag_t  frags[MAX_SKB_FRAGS];   // 片段数组
};
```

### 1.3 skb_frag_t (片段结构)

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 361-365 行)

```c
typedef struct skb_frag {
    netmem_ref netmem;                  // 网络内存引用(page 或 net_iov)
    unsigned int len;                   // 片段长度
    unsigned int offset;                // 偏移量
} skb_frag_t;
```

### 1.4 struct sk_buff_fclones (快速克隆)

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 1394-1400 行)

```c
struct sk_buff_fclones {
    struct sk_buff skb1;                // 原始 skb
    struct sk_buff skb2;                // 克隆 skb
    refcount_t    fclone_ref;           // 克隆引用计数
};
```

---

## 2. skbuff 内存布局 (Layout)

### 2.1 指针关系图

```
head                    data                            tail                end
  |                       |                               |                   |
  v                       v                               v                   v
  +-----------------------+-------------------------------+-------------------+
  |      headroom         |        data area              |    tailroom      |
  |   (预留空间)           |    (实际网络数据)              |   (预留空间)      |
  +-----------------------+-------------------------------+-------------------+
                          |<- len ->|<- data_len ->|
                          |<----------- truesize ------------>|
                                                         
  |<------------ skb_shared_info (在 end 位置) --------->|
```

### 2.2 关键宏和函数

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h`

**skb_end_pointer** (第 1722-1725 行):
```c
static inline unsigned char *skb_end_pointer(const struct sk_buff *skb)
{
    return skb->head + skb->end;
}
```

**skb_shinfo** (第 1783 行):
```c
#define skb_shinfo(SKB) ((struct skb_shared_info *)(skb_end_pointer(SKB)))
```

**skb_tail_pointer** (第 2702-2705 行):
```c
static inline unsigned char *skb_tail_pointer(const struct sk_buff *skb)
{
    return skb->head + skb->tail;
}
```

**skb_headlen** (第 2531-2534 行):
```c
static inline unsigned int skb_headlen(const struct sk_buff *skb)
{
    return skb->len - skb->data_len;  // 线性数据长度
}
```

**skb_pagelen** (第 2545-2548 行):
```c
static inline unsigned int skb_pagelen(const struct sk_buff *skb)
{
    return skb_headlen(skb) + __skb_pagelen(skb);  // 全部数据长度
}
```

---

## 3. 内存分配函数

### 3.1 __alloc_skb()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 672-743 行)

```c
struct sk_buff *__alloc_skb(unsigned int size, gfp_t gfp_mask,
                            int flags, int node)
{
    struct sk_buff *skb = NULL;
    struct kmem_cache *cache;
    u8 *data;

    if (sk_memalloc_socks() && (flags & SKB_ALLOC_RX))
        gfp_mask |= __GFP_MEMALLOC;

    if (flags & SKB_ALLOC_FCLONE) {
        cache = net_hotdata.skbuff_fclone_cache;
        goto fallback;
    }
    cache = net_hotdata.skbuff_cache;
    
    // 尝试从 per-CPU cache 获取
    if (flags & SKB_ALLOC_NAPI) {
        skb = napi_skb_cache_get(true);
        if (unlikely(!skb))
            return NULL;
    } else if (!in_hardirq() && !irqs_disabled()) {
        local_bh_disable();
        skb = napi_skb_cache_get(false);
        local_bh_enable();
    }

    if (!skb) {
fallback:
        skb = kmem_cache_alloc_node(cache, gfp_mask & ~GFP_DMA, node);
        if (unlikely(!skb))
            return NULL;
    }
    skbuff_clear(skb);

    // 分配数据缓冲区
    data = kmalloc_reserve(&size, gfp_mask, node, skb);
    if (unlikely(!data))
        goto nodata;

    __finalize_skb_around(skb, data, size);

    // 如果是 fclone, 设置 fclone 标志
    if (flags & SKB_ALLOC_FCLONE) {
        struct sk_buff_fclones *fclones;
        fclones = container_of(skb, struct sk_buff_fclones, skb1);
        skb->fclone |= SKB_FCLONE_ORIG;
        refcount_set(&fclones->fclone_ref, 1);
    }

    return skb;

nodata:
    kmem_cache_free(cache, skb);
    return NULL;
}
```

### 3.2 __netdev_alloc_skb()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 759-820 行)

```c
struct sk_buff *__netdev_alloc_skb(struct net_device *dev, unsigned int len,
                                   gfp_t gfp_mask)
{
    struct page_frag_cache *nc;
    struct sk_buff *skb;
    bool pfmemalloc;
    void *data;

    len += NET_SKB_PAD;  // 添加接收.pad

    // 小包或大包使用 kmalloc
    if (len <= SKB_WITH_OVERHEAD(SKB_SMALL_HEAD_CACHE_SIZE) ||
        len > SKB_WITH_OVERHEAD(PAGE_SIZE) ||
        (gfp_mask & (__GFP_DIRECT_RECLAIM | GFP_DMA))) {
        skb = __alloc_skb(len, gfp_mask, SKB_ALLOC_RX, NUMA_NO_NODE);
        if (!skb)
            goto skb_fail;
        goto skb_success;
    }

    // 使用 page_frag_cache 分配
    len = SKB_HEAD_ALIGN(len);

    if (in_hardirq() || irqs_disabled()) {
        nc = this_cpu_ptr(&netdev_alloc_cache);
        data = page_frag_alloc(nc, len, gfp_mask);
        pfmemalloc = page_frag_cache_is_pfmemalloc(nc);
    } else {
        local_bh_disable();
        nc = this_cpu_ptr(&napi_alloc_cache.page);
        data = page_frag_alloc(nc, len, gfp_mask);
        pfmemalloc = page_frag_cache_is_pfmemalloc(nc);
        local_bh_enable();
    }

    if (unlikely(!data))
        return NULL;

    skb = __build_skb(data, len);
    if (unlikely(!skb)) {
        skb_free_frag(data);
        return NULL;
    }

    if (pfmemalloc)
        skb->pfmemalloc = 1;
    skb->head_frag = 1;

skb_success:
    skb_reserve(skb, NET_SKB_PAD);
    skb->dev = dev;

skb_fail:
    return skb;
}
```

---

## 4. 克隆和复制函数

### 4.1 skb_clone()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 2098-2125 行)

```c
struct sk_buff *skb_clone(struct sk_buff *skb, gfp_t gfp_mask)
{
    struct sk_buff_fclones *fclones = container_of(skb,
                           struct sk_buff_fclones, skb1);
    struct sk_buff *n;

    if (skb_orphan_frags(skb, gfp_mask))
        return NULL;

    // 尝试使用 fclone cache
    if (skb->fclone == SKB_FCLONE_ORIG &&
        refcount_read(&fclones->fclone_ref) == 1) {
        n = &fclones->skb2;           // 使用已分配的克隆
        refcount_set(&fclones->fclone_ref, 2);
        n->fclone = SKB_FCLONE_CLONE;
    } else {
        if (skb_pfmemalloc(skb))
            gfp_mask |= __GFP_MEMALLOC;

        n = kmem_cache_alloc(net_hotdata.skbuff_cache, gfp_mask);
        if (!n)
            return NULL;

        n->fclone = SKB_FCLONE_UNAVAILABLE;
    }

    return __skb_clone(n, skb);
}
```

### 4.2 __skb_clone() - 内部克隆实现

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1608-1639 行)

```c
static struct sk_buff *__skb_clone(struct sk_buff *n, struct sk_buff *skb)
{
#define C(x) n->x = skb->x

    n->next = n->prev = NULL;
    n->sk = NULL;
    __copy_skb_header(n, skb);

    C(len);
    C(data_len);
    C(mac_len);
    n->hdr_len = skb->nohdr ? skb_headroom(skb) : skb->hdr_len;
    n->cloned = 1;                     // 设置克隆标志
    n->nohdr = 0;
    n->peeked = 0;
    C(pfmemalloc);
    C(pp_recycle);
    n->destructor = NULL;
    C(tail);
    C(end);
    C(head);
    C(head_frag);
    C(data);
    C(truesize);
    refcount_set(&n->users, 1);

    atomic_inc(&(skb_shinfo(skb)->dataref));  // 增加数据引用
    skb->cloned = 1;

    return n;
#undef C
}
```

### 4.3 skb_copy() - 完全复制

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 2178-2206 行)

```c
struct sk_buff *skb_copy(const struct sk_buff *skb, gfp_t gfp_mask)
{
    struct sk_buff *n;
    unsigned int size;
    int headerlen;

    if (!skb_frags_readable(skb))
        return NULL;

    if (WARN_ON_ONCE(skb_shinfo(skb)->gso_type & SKB_GSO_FRAGLIST))
        return NULL;

    headerlen = skb_headroom(skb);
    size = skb_end_offset(skb) + skb->data_len;
    n = __alloc_skb(size, gfp_mask,
            skb_alloc_rx_flag(skb), NUMA_NO_NODE);
    if (!n)
        return NULL;

    skb_reserve(n, headerlen);
    skb_put(n, skb->len);

    BUG_ON(skb_copy_bits(skb, -headerlen, n->head, headerlen + skb->len));

    skb_copy_header(n, skb);
    return n;
}
```

### 4.4 __pskb_copy_fclone()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 2226-2247 行)

```c
struct sk_buff *__pskb_copy_fclone(struct sk_buff *skb, int headroom,
                   gfp_t gfp_mask, bool fclone)
{
    unsigned int size = skb_headlen(skb) + headroom;
    int flags = skb_alloc_rx_flag(skb) | (fclone ? SKB_ALLOC_FCLONE : 0);
    struct sk_buff *n = __alloc_skb(size, gfp_mask, flags, NUMA_NO_NODE);

    if (!n)
        goto out;

    skb_reserve(n, headroom);
    skb_put(n, skb_headlen(skb));
    skb_copy_from_linear_data(skb, n->data, n->len);

    n->truesize += skb->data_len;
    n->data_len  = skb->data_len;
    n->len       = skb->len;

    // 片段数据仍然共享
    if (skb_shinfo(skb)->nr_frags) {
        // ... 处理 frags
    }
    // ...
out:
    return n;
}
```

---

## 5. 内存释放函数

### 5.1 kfree_skb() 释放链

```
kfree_skb()
  └── sk_skb_reason_drop()
        └── __sk_skb_reason_drop()
              └── __kfree_skb()
                    ├── skb_release_all()
                    │     ├── skb_release_head_state()  // 释放 dst, destructor, nf, ext
                    │     └── skb_release_data()
                    │           ├── skb_data_unref()    // 检查 dataref
                    │           ├── skb_zcopy_clear()    // 释放零拷贝
                    │           ├── __skb_frag_unref()  // 释放片段引用
                    │           ├── kfree_skb_list_reason() // 释放 frag_list
                    │           └── skb_free_head()      // 释放线性数据
                    └── kfree_skbmem()
                          ├── SKB_FCLONE_UNAVAILABLE → kmem_cache_free()
                          ├── SKB_FCLONE_ORIG → 检查 fclone_ref
                          └── SKB_FCLONE_CLONE → 检查 fclone_ref
```

### 5.2 __kfree_skb()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1212-1217 行)

```c
void __kfree_skb(struct sk_buff *skb)
{
    skb_release_all(skb, SKB_DROP_REASON_NOT_SPECIFIED);
    kfree_skbmem(skb);
}
```

### 5.3 skb_release_all()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1196-1201 行)

```c
static void skb_release_all(struct sk_buff *skb, enum skb_drop_reason reason)
{
    skb_release_head_state(skb);
    if (likely(skb->head))
        skb_release_data(skb, reason);
}
```

### 5.4 skb_release_data()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1102-1137 行)

```c
static void skb_release_data(struct sk_buff *skb, enum skb_drop_reason reason)
{
    struct skb_shared_info *shinfo = skb_shinfo(skb);
    int i;

    if (!skb_data_unref(skb, shinfo))   // 检查引用计数
        goto exit;

    if (skb_zcopy(skb)) {
        bool skip_unref = shinfo->flags & SKBFL_MANAGED_FRAG_REFS;
        skb_zcopy_clear(skb, true);
        if (skip_unref)
            goto free_head;
    }

    // 释放所有片段引用
    for (i = 0; i < shinfo->nr_frags; i++)
        __skb_frag_unref(&shinfo->frags[i], skb->pp_recycle);

free_head:
    // 释放 frag_list
    if (shinfo->frag_list)
        kfree_skb_list_reason(shinfo->frag_list, reason);

    skb_free_head(skb);
exit:
    // 禁用 pp_recycle 以避免竞争
    skb->pp_recycle = 0;
}
```

### 5.5 kfree_skbmem()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1142-1170 行)

```c
static void kfree_skbmem(struct sk_buff *skb)
{
    struct sk_buff_fclones *fclones;

    switch (skb->fclone) {
    case SKB_FCLONE_UNAVAILABLE:
        kmem_cache_free(net_hotdata.skbuff_cache, skb);
        return;

    case SKB_FCLONE_ORIG:
        fclones = container_of(skb, struct sk_buff_fclones, skb1);
        // 通常 TX 完成时先释放 clone
        if (refcount_read(&fclones->fclone_ref) == 1)
            goto fastpath;
        break;

    default: /* SKB_FCLONE_CLONE */
        fclones = container_of(skb, struct sk_buff_fclones, skb2);
        break;
    }
    if (!refcount_dec_and_test(&fclones->fclone_ref))
        return;
fastpath:
    kmem_cache_free(net_hotdata.skbuff_fclone_cache, fclones);
}
```

### 5.6 consume_skb()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1441-1449 行)

```c
void consume_skb(struct sk_buff *skb)
{
    if (!skb_unref(skb))
        return;

    trace_consume_skb(skb, __builtin_return_address(0));
    __kfree_skb(skb);
}
```

### 5.7 __skb_frag_unref() - 片段引用释放

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff_ref.h` (第 54-57 行)

```c
static __always_inline void __skb_frag_unref(skb_frag_t *frag, bool recycle)
{
    skb_page_unref(skb_frag_netmem(frag), recycle);
}
```

### 5.8 skb_free_head()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1089-1100 行)

```c
static void skb_free_head(struct sk_buff *skb)
{
    unsigned char *head = skb->head;

    if (skb->head_frag) {
        if (skb_pp_recycle(skb, head))  // 尝试 page_pool 回收
            return;
        skb_free_frag(head);            // 使用 page_frag_cache 释放
    } else {
        skb_kfree_head(head, skb_end_offset(skb));  // kfree 释放
    }
}
```

---

## 6. skb_shared_info 中的 dataref 引用计数

### 6.1 dataref 结构

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 658-659 行)

```c
#define SKB_DATAREF_SHIFT 16
#define SKB_DATAREF_MASK ((1 << SKB_DATAREF_SHIFT) - 1)
```

dataref 被分为两部分:
- **低 16 位**: 总引用数
- **高 16 位**: 仅 payload(无头部)的引用数

### 6.2 skb_data_unref()

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 1298-1314 行)

```c
static inline bool skb_data_unref(const struct sk_buff *skb,
                  struct skb_shared_info *shinfo)
{
    int bias;

    if (!skb->cloned)
        return true;                    // 非克隆,直接释放

    bias = skb->nohdr ? (1 << SKB_DATAREF_SHIFT) + 1 : 1;

    if (atomic_read(&shinfo->dataref) == bias)
        smp_rmb();
    else if (atomic_sub_return(bias, &shinfo->dataref))
        return false;                   // 还有其他引用

    return true;                       // 可以释放
}
```

---

## 7. 分散/聚集 I/O (Scatter-Gather)

### 7.1 片段布局

```
+------------------+     +------------------+     +------------------+
|     skb->head    |     |   skb->frags[0]  |     |   skb->frags[1]  |
|   (线性区域)     |     |  (page/fragment) |     |  (page/fragment) |
+------------------+     +------------------+     +------------------+
      |                       |                       |
      |<--- skb->len -----><-skb->data_len---------->|
```

### 7.2 skb_frag_t 操作

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 371-404 行)

```c
static inline unsigned int skb_frag_size(const skb_frag_t *frag)
{
    return frag->len;
}

static inline void skb_frag_size_set(skb_frag_t *frag, unsigned int size)
{
    frag->len = size;
}

static inline void skb_frag_size_add(skb_frag_t *frag, int delta)
{
    frag->len += delta;
}

static inline void skb_frag_size_sub(skb_frag_t *frag, int delta)
{
    frag->len -= delta;
}
```

### 7.3 片段引用操作

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff_ref.h` (第 18-33 行)

```c
static __always_inline void __skb_frag_ref(skb_frag_t *frag)
{
    get_netmem(skb_frag_netmem(frag));  // 增加 netmem 引用
}

static __always_inline void skb_frag_ref(struct sk_buff *skb, int f)
{
    __skb_frag_ref(&skb_shinfo(skb)->frags[f]);
}

static __always_inline void skb_frag_unref(struct sk_buff *skb, int f)
{
    struct skb_shared_info *shinfo = skb_shinfo(skb);

    if (!skb_zcopy_managed(skb))
        __skb_frag_unref(&shinfo->frags[f], skb->pp_recycle);
}
```

---

## 8. Linearize 过程 (非线性を线性转换)

### 8.1 skb_linearize()

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 3985-3988 行)

```c
static inline int skb_linearize(struct sk_buff *skb)
{
    return skb_is_nonlinear(skb) ? __skb_linearize(skb) : 0;
}
```

### 8.2 __skb_linearize()

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 3973-3976 行)

```c
static inline int __skb_linearize(struct sk_buff *skb)
{
    return __pskb_pull_tail(skb, skb->data_len) ? 0 : -ENOMEM;
}
```

### 8.3 __pskb_pull_tail() - Linearize 核心实现

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 2866-2992 行)

```c
void *__pskb_pull_tail(struct sk_buff *skb, int delta)
{
    int i, k, eat = (skb->tail + delta) - skb->end;

    if (!skb_frags_readable(skb))
        return NULL;

    // 如果尾部空间不足或 skb 被克隆,则重新分配
    if (eat > 0 || skb_cloned(skb)) {
        if (pskb_expand_head(skb, 0, eat > 0 ? eat + 128 : 0,
                     GFP_ATOMIC))
            return NULL;
    }

    // 复制片段数据到线性区域
    BUG_ON(skb_copy_bits(skb, skb_headlen(skb),
                 skb_tail_pointer(skb), delta));

    // 处理 frag_list
    if (!skb_has_frag_list(skb))
        goto pull_pages;

    // 处理 frag_list,可能需要克隆
    eat = delta;
    for (i = 0; i < skb_shinfo(skb)->nr_frags; i++) {
        int size = skb_frag_size(&skb_shinfo(skb)->frags[i]);
        if (size >= eat)
            goto pull_pages;
        eat -= size;
    }

    // ... 处理 frag_list 的复杂逻辑

pull_pages:
    // 将片段数据合并到线性区域
    eat = delta;
    k = 0;
    for (i = 0; i < skb_shinfo(skb)->nr_frags; i++) {
        int size = skb_frag_size(&skb_shinfo(skb)->frags[i]);

        if (size <= eat) {
            skb_frag_unref(skb, i);    // 释放片段
            eat -= size;
        } else {
            // 部分使用片段
            skb_frag_t *frag = &skb_shinfo(skb)->frags[k];
            *frag = skb_shinfo(skb)->frags[i];
            if (eat) {
                skb_frag_off_add(frag, eat);
                skb_frag_size_sub(frag, eat);
                eat = 0;
            }
            k++;
        }
    }
    skb_shinfo(skb)->nr_frags = k;

    skb->tail += delta;
    skb->data_len -= delta;

    if (!skb->data_len)
        skb_zcopy_clear(skb, false);

    return skb_tail_pointer(skb);
}
```

---

## 9. pskb_expand_head() - 重新分配头部

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 2294-2370 行)

```c
int pskb_expand_head(struct sk_buff *skb, int nhead, int ntail,
             gfp_t gfp_mask)
{
    unsigned int osize = skb_end_offset(skb);
    unsigned int size = osize + nhead + ntail;
    long off;
    u8 *data;
    int i;

    BUG_ON(nhead < 0);
    BUG_ON(skb_shared(skb));           // 必须未被共享

    skb_zcopy_downgrade_managed(skb);

    if (skb_pfmemalloc(skb))
        gfp_mask |= __GFP_MEMALLOC;

    // 分配新的数据缓冲区
    data = kmalloc_reserve(&size, gfp_mask, NUMA_NO_NODE, NULL);
    if (!data)
        goto nodata;
    size = SKB_WITH_OVERHEAD(size);

    // 复制原有数据到新缓冲区
    memcpy(data + nhead, skb->head, skb_tail_pointer(skb) - skb->head);

    // 复制 skb_shared_info
    memcpy((struct skb_shared_info *)(data + size),
           skb_shinfo(skb),
           offsetof(struct skb_shared_info, frags[skb_shinfo(skb)->nr_frags]));

    // 如果是克隆,需要特殊处理
    if (skb_cloned(skb)) {
        if (skb_orphan_frags(skb, gfp_mask))
            goto nofrags;
        if (skb_zcopy(skb))
            refcount_inc(&skb_uarg(skb)->refcnt);
        for (i = 0; i < skb_shinfo(skb)->nr_frags; i++)
            skb_frag_ref(skb, i);

        if (skb_has_frag_list(skb))
            skb_clone_fraglist(skb);

        skb_release_data(skb, SKB_CONSUMED);
    } else {
        skb_free_head(skb);
    }

    off = (data + nhead) - skb->head;

    // 更新指针
    skb->head     = data;
    skb->head_frag = 0;
    skb->data    += off;
    skb_set_end_offset(skb, size);
    skb->tail    += off;
    skb_headers_offset_update(skb, nhead);
    skb->cloned   = 0;
    skb->hdr_len  = 0;
    skb->nohdr    = 0;
    atomic_set(&skb_shinfo(skb)->dataref, 1);

    if (!skb->sk || skb->destructor == sock_edemux)
        skb->truesize += size - osize;

    return 0;

// 错误处理
nofrags:
    skb_kfree_head(data, size);
nodata:
    return -ENOMEM;
}
```

---

## 10. SKB Destructor 机制

### 10.1 skb_release_head_state()

**文件**: `/Users/sphinx/github/linux/net/core/skbuff.c` (第 1172-1193 行)

```c
void skb_release_head_state(struct sk_buff *skb)
{
    skb_dst_drop(skb);                  // 释放 dst entry

    if (skb->destructor) {             // 调用析构函数
        DEBUG_NET_WARN_ON_ONCE(in_hardirq());
#ifdef CONFIG_INET
        INDIRECT_CALL_4(skb->destructor,
                tcp_wfree, __sock_wfree, sock_wfree,
                xsk_destruct_skb,
                skb);
#else
        INDIRECT_CALL_2(skb->destructor,
                sock_wfree, xsk_destruct_skb,
                skb);
#endif
        skb->destructor = NULL;
        skb->sk = NULL;
    }

    nf_reset_ct(skb);                   // 重置 netfilter 状态
    skb_ext_reset(skb);                 // 重置 extensions
}
```

### 10.2 常见的 destructor

- **sock_wfree**: 释放 socket 引用,更新 sk_wmem_alloc
- **__sock_wfree**: socket 写释放
- **tcp_wfree**: TCP 写释放
- **xsk_destruct_skb**: XDP socket 释放

---

## 11. 内存分配标志

**文件**: `/Users/sphinx/github/linux/include/linux/skbuff.h` (第 1131-1133 行)

```c
#define SKB_ALLOC_FCLONE   0x01   // 从 fclone cache 分配
#define SKB_ALLOC_RX       0x02   // 接收路径分配
#define SKB_ALLOC_NAPI     0x04   // NAPI 上下文分配
```

---

## 12. 总结: SKB 生命周期

```
1. 分配
   ├─ __alloc_skb()        → kmalloc/kfree 或 fclone cache
   ├─ __netdev_alloc_skb() → page_frag_cache (大包)
   └─ napi_alloc_skb()     → NAPI per-CPU cache

2. 使用
   ├─ skb_clone()          → 共享数据,仅复制 skb 元数据
   ├─ skb_copy()           → 完全复制(线性化)
   ├─ pskb_expand_head()   → 重新分配头部空间
   └─ skb_linearize()      → 将非线性 skb 转为线性

3. 释放
   ├─ consume_skb()        → 正常消费,无 drop reason
   ├─ kfree_skb()          → 释放并记录 drop reason
   └─ napi_consume_skb()   → NAPI 上下文消费,尝试 defer
```

---

## 13. 参考文件

| 文件路径 | 描述 |
|---------|------|
| `/Users/sphinx/github/linux/include/linux/skbuff.h` | SKB 主要结构体定义 |
| `/Users/sphinx/github/linux/include/linux/skbuff_ref.h` | 片段引用计数操作 |
| `/Users/sphinx/github/linux/include/net/netmem.h` | netmem 网络内存抽象 |
| `/Users/sphinx/github/linux/net/core/skbuff.c` | SKB 核心实现 |
