# io_uring 子系统内存管理与缓冲区机制分析

## 目录

1. [概述](#概述)
2. [环形缓冲区映射 (Ring Buffer Mapping)](#环形缓冲区映射-ring-buffer-mapping)
3. [固定缓冲区 (Fixed Buffers)](#固定缓冲区-fixed-buffers)
4. [缓冲区管理 (kbuf.c)](#缓冲区管理-kbufc)
5. [分配缓存 (alloc_cache.c)](#分配缓存-alloc_cachec)
6. [Scatter-Gather 列表](#scatter-gather-列表)
7. [内存布局图](#内存布局图)
8. [关键数据结构关系图](#关键数据结构关系图)

---

## 概述

io_uring 是 Linux 内核的高性能异步 I/O 子系统，其内存管理机制包含以下几个核心组件：

| 组件 | 文件 | 职责 |
|------|------|------|
| 环形缓冲区映射 | `memmap.c`, `memmap.h` | SQ/CQ 环和 SQEs 的内存映射 |
| 固定缓冲区注册 | `rsrc.c`, `rsrc.h` | 用户缓冲区的注册和管理 |
| 缓冲区管理 | `kbuf.c`, `kbuf.h` | 提供缓冲区(Provided Buffers)的管理 |
| 分配缓存 | `alloc_cache.c`, `alloc_cache.h` | 小对象分配缓存 |

---

## 环形缓冲区映射 (Ring Buffer Mapping)

### 1.1 核心数据结构

**`struct io_mapped_region`** (include/linux/io_uring_types.h:80-85)

```c
struct io_mapped_region {
    struct page      **pages;    // 指向页指针数组的指针
    void              *ptr;      // 内核虚拟地址
    unsigned           nr_pages; // 页数量
    unsigned           flags;     // 区域标志
};
```

区域标志定义 (memmap.c:82-89):

```c
enum {
    IO_REGION_F_VMAP          = 1,  // 内存通过 vmap 映射给内核
    IO_REGION_F_USER_PROVIDED = 2,  // 内存由用户提供,内核固定(pin)
    IO_REGION_F_SINGLE_REF    = 4,  // 仅数组中第一个页面被引用
};
```

### 1.2 io_uring_mmap() 实现

**memmap.c:295-319**

```c
__cold int io_uring_mmap(struct file *file, struct vm_area_struct *vma)
{
    struct io_ring_ctx *ctx = file->private_data;
    size_t sz = vma->vm_end - vma->vm_start;
    long offset = vma->vm_pgoff << PAGE_SHIFT;
    unsigned int page_limit = UINT_MAX;
    struct io_mapped_region *region;
    void *ptr;

    guard(mutex)(&ctx->mmap_lock);

    ptr = io_uring_validate_mmap_request(file, vma->vm_pgoff);
    if (IS_ERR(ptr))
        return PTR_ERR(ptr);

    switch (offset & IORING_OFF_MMAP_MASK) {
    case IORING_OFF_SQ_RING:
    case IORING_OFF_CQ_RING:
        page_limit = (sz + PAGE_SIZE - 1) >> PAGE_SHIFT;
        break;
    }

    region = io_mmap_get_region(ctx, vma->vm_pgoff);
    return io_region_mmap(ctx, region, vma, page_limit);
}
```

### 1.3 mmap 偏移量定义

**include/uapi/linux/io_uring.h:542-548**

```c
#define IORING_OFF_SQ_RING       0ULL        // SQ 环形缓冲区
#define IORING_OFF_CQ_RING       0x8000000ULL // CQ 环形缓冲区
#define IORING_OFF_SQES          0x10000000ULL // SQEs 数组
#define IORING_OFF_PBUF_RING     0x80000000ULL // 提供缓冲区环
#define IORING_OFF_PBUF_SHIFT    16            // bgid 位移
```

### 1.4 区域获取

**memmap.c:233-256**

```c
static struct io_mapped_region *io_mmap_get_region(struct io_ring_ctx *ctx,
                                                   loff_t pgoff)
{
    loff_t offset = pgoff << PAGE_SHIFT;
    unsigned int id;

    switch (offset & IORING_OFF_MMAP_MASK) {
    case IORING_OFF_SQ_RING:
    case IORING_OFF_CQ_RING:
        return &ctx->ring_region;
    case IORING_OFF_SQES:
        return &ctx->sq_region;
    case IORING_OFF_PBUF_RING:
        id = (offset & ~IORING_OFF_MMAP_MASK) >> IORING_OFF_PBUF_SHIFT;
        return io_pbuf_get_region(ctx, id);
    case IORING_MAP_OFF_PARAM_REGION:
        return &ctx->param_region;
    case IORING_MAP_OFF_ZCRX_REGION:
        id = (offset & ~IORING_OFF_MMAP_MASK) >> IORING_OFF_ZCRX_SHIFT;
        return io_zcrx_get_region(ctx, id);
    }
    return NULL;
}
```

### 1.5 页面映射核心函数

**memmap.c:284-293**

```c
static int io_region_mmap(struct io_ring_ctx *ctx,
                          struct io_mapped_region *mr,
                          struct vm_area_struct *vma,
                          unsigned max_pages)
{
    unsigned long nr_pages = min(mr->nr_pages, max_pages);

    vm_flags_set(vma, VM_DONTEXPAND);
    return vm_insert_pages(vma, vma->vm_start, mr->pages, &nr_pages);
}
```

### 1.6 用户/内核共享机制

环形缓冲区通过 mmap 实现用户态和内核态共享：

1. **内核分配页面**: `io_region_allocate_pages()` (memmap.c:152-182)
2. **内核映射到内核地址空间**: `io_region_init_ptr()` (memmap.c:114-132)
3. **用户态 mmap**: `vm_insert_pages()` 将同一批物理页面映射到用户态

---

## 固定缓冲区 (Fixed Buffers)

### 2.1 概述

固定缓冲区通过 `IORING_REGISTER_BUFFERS` 或 `IORING_REGISTER_BUFFERS2` 注册，允许应用预先注册内存区域供 I/O 操作使用，避免每次操作的用户/内核态数据拷贝。

### 2.2 核心数据结构

**`struct io_rsrc_node`** (rsrc.h:15-24)

```c
struct io_rsrc_node {
    unsigned char   type;      // IORING_RSRC_FILE 或 IORING_RSRC_BUFFER
    int             refs;       // 引用计数
    u64             tag;        // 用户提供的标签
    union {
        unsigned long           file_ptr;
        struct io_mapped_ubuf  *buf;  // 仅对缓冲区类型有效
    };
};
```

**`struct io_mapped_ubuf`** (rsrc.h:35-47)

```c
struct io_mapped_ubuf {
    u64             ubuf;         // 用户缓冲区的原始地址
    unsigned int    len;          // 缓冲区长度
    unsigned int    nr_bvecs;     // bio_vec 数组元素数量
    unsigned int    folio_shift;  // folio 大小 (页或大页)
    refcount_t      refs;         // 引用计数
    unsigned long   acct_pages;   // 已记账的页数
    void            (*release)(void *);  // 释放回调
    void            *priv;        // 私有数据
    u8              flags;        // 标志
    u8              dir;          // 方向 (IO_IMU_DEST | IO_IMU_SOURCE)
    struct bio_vec  bvec[] __counted_by(nr_bvecs);  // 页面向量数组
};
```

### 2.3 缓冲区注册流程

**rsrc.c:858-925** - `io_sqe_buffers_register()`

```c
int io_sqe_buffers_register(struct io_ring_ctx *ctx, void __user *arg,
                            unsigned int nr_args, u64 __user *tags)
{
    struct page *last_hpage = NULL;
    struct io_rsrc_data data;
    struct iovec fast_iov, *iov = &fast_iov;
    // ...
    for (i = 0; i < nr_args; i++) {
        node = io_sqe_buffer_register(ctx, iov, &last_hpage);
        if (IS_ERR(node)) {
            ret = PTR_ERR(node);
            break;
        }
        data.nodes[i] = node;
    }
    ctx->buf_table = data;
    // ...
}
```

### 2.4 单个缓冲区注册

**rsrc.c:762-856** - `io_sqe_buffer_register()`

```c
static struct io_rsrc_node *io_sqe_buffer_register(struct io_ring_ctx *ctx,
                                                   struct iovec *iov,
                                                   struct page **last_hpage)
{
    struct io_mapped_ubuf *imu = NULL;
    struct page **pages = NULL;
    struct io_rsrc_node *node;
    // ...
    // 1. 固定用户页面
    pages = io_pin_pages((unsigned long) iov->iov_base, iov->iov_len, &nr_pages);
    if (IS_ERR(pages)) { ... }

    // 2. 检查是否可以合并大页
    if (nr_pages > 1 && io_check_coalesce_buffer(pages, nr_pages, &data)) {
        if (data.nr_pages_mid != 1)
            coalesced = io_coalesce_buffer(&pages, &nr_pages, &data);
    }

    // 3. 分配 imu 结构
    imu = io_alloc_imu(ctx, nr_pages);
    if (!imu) goto done;

    // 4. 填充 imu
    imu->nr_bvecs = nr_pages;
    imu->ubuf = (unsigned long) iov->iov_base;
    imu->len = iov->iov_len;
    imu->folio_shift = PAGE_SHIFT;
    imu->release = io_release_ubuf;
    imu->priv = imu;
    imu->dir = IO_IMU_DEST | IO_IMU_SOURCE;
    refcount_set(&imu->refs, 1);

    // 5. 构建 bio_vec 数组
    for (i = 0; i < nr_pages; i++) {
        size_t vec_len;
        vec_len = min_t(size_t, size, (1UL << imu->folio_shift) - off);
        bvec_set_page(&imu->bvec[i], pages[i], vec_len, off);
        off = 0;
        size -= vec_len;
    }
    // ...
}
```

### 2.5 页面固定

**memmap.c:40-80** - `io_pin_pages()`

```c
struct page **io_pin_pages(unsigned long uaddr, unsigned long len, int *npages)
{
    unsigned long start, end, nr_pages;
    struct page **pages;
    // ...
    nr_pages = (end >> PAGE_SHIFT) - (start >> PAGE_SHIFT);
    pages = kvmalloc_objs(struct page *, nr_pages, GFP_KERNEL_ACCOUNT);

    ret = pin_user_pages_fast(uaddr, nr_pages, FOLL_WRITE | FOLL_LONGTERM, pages);
    if (ret == nr_pages) {
        *npages = nr_pages;
        return pages;
    }
    // 失败处理...
}
```

### 2.6 固定缓冲区 vs 动态分配

| 特性 | 固定缓冲区 | 动态分配 |
|------|-----------|----------|
| 内存固定 | 预注册,使用 pin_user_pages | 每次分配 |
| 零拷贝 | 支持,直接使用注册的 bio_vec | 需要复制 |
| 内存占用 | 长期占用 (受 RLIMIT_MEMLOCK 限制) | 临时分配 |
| 延迟 | 无分配延迟 | 有分配开销 |
| 安全性 | 受限特定地址范围 | 灵活但需验证 |

---

## 缓冲区管理 (kbuf.c)

### 3.1 概述

kbuf.c 管理"提供缓冲区"(Provided Buffers)，这是一种由应用提供、内核使用的缓冲区机制，与固定缓冲区不同，提供缓冲区可以按需从列表中获取。

### 3.2 核心数据结构

**`struct io_buffer_list`** (kbuf.h:15-37)

```c
struct io_buffer_list {
    union {
        struct list_head buf_list;           // 经典缓冲区列表
        struct io_uring_buf_ring *buf_ring; // 环形缓冲区
    };
    int                     nbufs;      // 缓冲区数量
    __u16                   bgid;       // 缓冲区组 ID
    // 以下用于环形缓冲区
    __u16                   nr_entries; // 条目数
    __u16                   head;       // 头指针
    __u16                   mask;       // 掩码
    __u16                   flags;      // 标志
    struct io_mapped_region region;    // 映射区域
};
```

**`struct io_buffer`** (kbuf.h:39-45)

```c
struct io_buffer {
    struct list_head list;
    __u64            addr;   // 缓冲区地址
    __u32            len;    // 缓冲区长度
    __u16            bid;     // 缓冲区 ID
    __u16            bgid;    // 缓冲区组 ID
};
```

**标志定义** (kbuf.h:8-13):

```c
enum {
    IOBL_BUF_RING   = 1,  // 环形缓冲区
    IOBL_INC        = 2,  // 增量消费(部分读取)
};
```

### 3.3 提供缓冲区注册

**kbuf.c:616-696** - `io_register_pbuf_ring()`

```c
int io_register_pbuf_ring(struct io_ring_ctx *ctx, void __user *arg)
{
    struct io_uring_buf_reg reg;
    struct io_buffer_list *bl;
    struct io_uring_buf_ring *br;
    unsigned long ring_size;
    // ...
    // 1. 验证参数
    if (copy_from_user(&reg, arg, sizeof(reg))) return -EFAULT;
    if (!is_power_of_2(reg.ring_entries)) return -EINVAL;
    if (reg.ring_entries >= 65536) return -EINVAL;

    // 2. 分配 buffer_list
    bl = kzalloc_obj(*bl, GFP_KERNEL_ACCOUNT);
    if (!bl) return -ENOMEM;

    // 3. 计算环形缓冲区大小并创建区域
    ring_size = flex_array_size(br, bufs, reg.ring_entries);
    ret = io_create_region(ctx, &bl->region, &rd, mmap_offset);

    // 4. 初始化环形缓冲区
    bl->nr_entries = reg.ring_entries;
    bl->mask = reg.ring_entries - 1;
    bl->flags |= IOBL_BUF_RING;
    bl->buf_ring = br;
    if (reg.flags & IOU_PBUF_RING_INC)
        bl->flags |= IOBL_INC;

    io_buffer_add_list(ctx, bl, reg.bgid);
    // ...
}
```

### 3.4 用户空间缓冲区结构

**include/uapi/linux/io_uring.h:850-871**

```c
struct io_uring_buf {
    __u64   addr;    // 缓冲区地址
    __u32   len;     // 缓冲区长度
    __u16   bid;     // 缓冲区 ID
    __u16   resv;    // 保留
};

struct io_uring_buf_ring {
    union {
        struct {
            __u64   resv1;
            __u32   resv2;
            __u16   resv3;
            __u16   tail;  // 与 io_uring_buf.resv 共用空间
        };
        __DECLARE_FLEX_ARRAY(struct io_uring_buf, bufs);
    };
};
```

### 3.5 缓冲区选择

**kbuf.c:226-244** - `io_buffer_select()`

```c
struct io_br_sel io_buffer_select(struct io_kiocb *req, size_t *len,
                                  unsigned buf_group, unsigned int issue_flags)
{
    struct io_ring_ctx *ctx = req->ctx;
    struct io_br_sel sel = { };
    struct io_buffer_list *bl;

    io_ring_submit_lock(req->ctx, issue_flags);

    bl = io_buffer_get_list(ctx, buf_group);
    if (likely(bl)) {
        if (bl->flags & IOBL_BUF_RING)
            sel = io_ring_buffer_select(req, len, bl, issue_flags);
        else
            sel.addr = io_provided_buffer_select(req, len, bl);
    }
    io_ring_submit_unlock(req->ctx, issue_flags);
    return sel;
}
```

### 3.6 环形缓冲区选择

**kbuf.c:192-224** - `io_ring_buffer_select()`

```c
static struct io_br_sel io_ring_buffer_select(struct io_kiocb *req, size_t *len,
                                               struct io_buffer_list *bl,
                                               unsigned int issue_flags)
{
    struct io_uring_buf_ring *br = bl->buf_ring;
    __u16 tail, head = bl->head;
    struct io_br_sel sel = { };
    struct io_uring_buf *buf;
    // ...
    tail = smp_load_acquire(&br->tail);
    if (unlikely(tail == head))
        return sel;  // 缓冲区为空

    buf = io_ring_head_to_buf(br, head, bl->mask);
    buf_len = READ_ONCE(buf->len);
    if (*len == 0 || *len > buf_len)
        *len = buf_len;
    req->flags |= REQ_F_BUFFER_RING | REQ_F_BUFFERS_COMMIT;
    req->buf_index = READ_ONCE(buf->bid);
    sel.buf_list = bl;
    sel.addr = u64_to_user_ptr(READ_ONCE(buf->addr));
    // ...
}
```

### 3.7 缓冲区回收

**kbuf.c:108-133** - `io_kbuf_recycle_legacy()`

```c
bool io_kbuf_recycle_legacy(struct io_kiocb *req, unsigned issue_flags)
{
    struct io_ring_ctx *ctx = req->ctx;
    struct io_buffer_list *bl;
    struct io_buffer *buf;

    io_ring_submit_lock(ctx, issue_flags);

    buf = req->kbuf;
    bl = io_buffer_get_list(ctx, buf->bgid);
    if (bl && !(bl->flags & IOBL_BUF_RING)) {
        list_add(&buf->list, &bl->buf_list);  // 返回缓冲区到列表
        bl->nbufs++;
    } else {
        kfree(buf);  // 环形缓冲区不回收
    }
    req->flags &= ~REQ_F_BUFFER_SELECTED;
    req->kbuf = NULL;

    io_ring_submit_unlock(ctx, issue_flags);
    return true;
}
```

---

## 分配缓存 (alloc_cache.c)

### 4.1 概述

`io_alloc_cache` 是一个轻量级对象缓存，用于减少小对象的分配/释放开销。最大缓存大小为 128 个对象。

### 4.2 核心数据结构

**`struct io_alloc_cache`** (include/linux/io_uring_types.h:263-269)

```c
struct io_alloc_cache {
    void            **entries;      // 缓存条目数组
    unsigned int    nr_cached;      // 当前缓存数量
    unsigned int    max_cached;     // 最大缓存数量 (IO_ALLOC_CACHE_MAX = 128)
    unsigned int    elem_size;      // 每个元素的大小
    unsigned int    init_clear;     // 分配后需要清零的字节数
};
```

### 4.3 缓存初始化

**alloc_cache.c:21-34**

```c
bool io_alloc_cache_init(struct io_alloc_cache *cache,
                        unsigned max_nr, unsigned int size,
                        unsigned int init_bytes)
{
    cache->entries = kvmalloc_array(max_nr, sizeof(void *), GFP_KERNEL);
    if (!cache->entries)
        return true;  // 初始化失败

    cache->nr_cached = 0;
    cache->max_cached = max_nr;
    cache->elem_size = size;
    cache->init_clear = init_bytes;
    return false;  // 初始化成功
}
```

### 4.4 缓存分配 (io_cache_alloc)

**alloc_cache.h:54-62**

```c
static inline void *io_cache_alloc(struct io_alloc_cache *cache, gfp_t gfp)
{
    void *obj;

    obj = io_alloc_cache_get(cache);
    if (obj)
        return obj;  // 命中缓存
    return io_cache_alloc_new(cache, gfp);  // 缓存未命中,分配新对象
}
```

### 4.5 缓存释放 (io_cache_free)

**alloc_cache.h:64-68**

```c
static inline void io_cache_free(struct io_alloc_cache *cache, void *obj)
{
    if (!io_alloc_cache_put(cache, obj))
        kfree(obj);  // 缓存满,直接释放
}
```

### 4.6 put 操作

**alloc_cache.h:21-31**

```c
static inline bool io_alloc_cache_put(struct io_alloc_cache *cache,
                                      void *entry)
{
    if (cache->nr_cached < cache->max_cached) {
        if (!kasan_mempool_poison_object(entry))
            return false;
        cache->entries[cache->nr_cached++] = entry;
        return true;
    }
    return false;  // 缓存已满
}
```

### 4.7 get 操作

**alloc_cache.h:33-52**

```c
static inline void *io_alloc_cache_get(struct io_alloc_cache *cache)
{
    if (cache->nr_cached) {
        void *entry = cache->entries[--cache->nr_cached];
#if defined(CONFIG_KASAN)
        kasan_mempool_unpoison_object(entry, cache->elem_size);
        if (cache->init_clear)
            memset(entry, 0, cache->init_clear);
#endif
        return entry;
    }
    return NULL;
}
```

### 4.8 缓存使用场景

io_uring 中多个子系统使用分配缓存：

| 缓存 | 用途 | 元素类型 |
|------|------|----------|
| `node_cache` | 资源节点分配 | `io_rsrc_node` |
| `imu_cache` | 用户缓冲区映射 | `io_mapped_ubuf` |
| `apoll_cache` | 异步 poll 对象 | `async_poll` |
| `netmsg_cache` | 网络消息 | - |
| `rw_cache` | 读写请求 | - |
| `cmd_cache` | 命令请求 | - |

---

## Scatter-Gather 列表

### 5.1 iovec 与 bio_vec

io_uring 使用两种向量结构：

```c
// 用户空间 iovec (POSIX)
struct iovec {
    void    *iov_base;  // 缓冲区地址
    size_t  iov_len;    // 缓冲区长度
};

// 内核空间 bio_vec (块层)
struct bio_vec {
    struct page *bv_page;   // 页面
    unsigned int bv_len;    // 长度
    unsigned int bv_offset; // 页内偏移
};
```

### 5.2 iou_vec 结构

**include/linux/io_uring_types.h:131-137**

```c
struct iou_vec {
    union {
        struct iovec  *iovec;   // 用户向量
        struct bio_vec*bvec;    // 内核向量
    };
    unsigned    nr;  // 向量元素数量
};
```

### 5.3 固定缓冲区的向量导入

**rsrc.c:1049-1099** - `io_import_fixed()`

```c
static int io_import_fixed(int ddir, struct iov_iter *iter,
                           struct io_mapped_ubuf *imu,
                           u64 buf_addr, size_t len)
{
    // 1. 验证范围
    ret = validate_fixed_range(buf_addr, len, imu);
    if (unlikely(ret)) return ret;
    if (!(imu->dir & (1 << ddir))) return -EFAULT;

    // 2. 计算偏移和folio信息
    offset = buf_addr - imu->ubuf;
    folio_mask = (1UL << imu->folio_shift) - 1;

    // 3. 处理跨 folio 的情况
    bvec = imu->bvec;
    if (offset >= bvec->bv_len) {
        unsigned long seg_skip;
        offset -= bvec->bv_len;
        seg_skip = 1 + (offset >> imu->folio_shift);
        bvec += seg_skip;
        offset &= folio_mask;
    }

    // 4. 计算需要的段数并设置 iov_iter
    nr_segs = (offset + len + bvec->bv_offset + folio_mask) >> imu->folio_shift;
    iov_iter_bvec(iter, ddir, bvec, nr_segs, len);
    iter->iov_offset = offset;
    return 0;
}
```

### 5.4 多缓冲区向量导入

**rsrc.c:1326-1378** - `io_vec_fill_bvec()`

```c
static int io_vec_fill_bvec(int ddir, struct iov_iter *iter,
                            struct io_mapped_ubuf *imu,
                            struct iovec *iovec, unsigned nr_iovs,
                            struct iou_vec *vec)
{
    unsigned long folio_size = 1 << imu->folio_shift;
    unsigned long folio_mask = folio_size - 1;
    struct bio_vec *res_bvec = vec->bvec;
    size_t total_len = 0;
    unsigned bvec_idx = 0;

    for (iov_idx = 0; iov_idx < nr_iovs; iov_idx++) {
        size_t iov_len = iovec[iov_idx].iov_len;
        u64 buf_addr = (u64)(uintptr_t)iovec[iov_idx].iov_base;

        // 验证每个 iovec 范围
        ret = validate_fixed_range(buf_addr, iov_len, imu);

        offset = buf_addr - imu->ubuf + imu->bvec[0].bv_offset;
        src_bvec = imu->bvec + (offset >> imu->folio_shift);
        offset &= folio_mask;

        // 为 iovec 中的每个段创建 bio_vec
        for (; iov_len; offset = 0, bvec_idx++, src_bvec++) {
            size_t seg_size = min_t(size_t, iov_len, folio_size - offset);
            bvec_set_page(&res_bvec[bvec_idx], src_bvec->bv_page, seg_size, offset);
            iov_len -= seg_size;
        }
    }
    iov_iter_bvec(iter, ddir, res_bvec, bvec_idx, total_len);
    return 0;
}
```

---

## 内存布局图

### 6.1 io_uring 整体内存布局

```
用户空间进程
+----------------------------------------------------------+
|                                                          |
|  +--------------------------------------------------+   |
|  |         SQ Ring (IORING_OFF_SQ_RING)            |   |
|  |  struct io_uring { head, tail }                 |   |
|  |  u32 sq_array[]                                  |   |
|  |  u32 sq_ring_mask, sq_ring_entries              |   |
|  |  atomic_t sq_flags                               |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |         CQ Ring (IORING_OFF_CQ_RING)            |   |
|  |  struct io_uring { head, tail }                 |   |
|  |  struct io_uring_cqe cqes[]                     |   |
|  |  u32 cq_ring_mask, cq_ring_entries              |   |
|  |  u32 cq_overflow                                 |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |         SQEs (IORING_OFF_SQES)                  |   |
|  |  struct io_uring_sqe sq_sqes[]                  |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |         Provided Buffer Ring                     |   |
|  |  struct io_uring_buf_ring { tail, bufs[] }      |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  |         Registered User Buffers                  |   |
|  |  (通过 mmap 固定,不是这里)                       |   |
|  +--------------------------------------------------+   |
|                                                          |
+----------------------------------------------------------+
```

内核空间

```
+----------------------------------------------------------+
|                                                          |
|  struct io_ring_ctx {                                    |
|      struct io_mapped_region ring_region; // SQ/CQ 环    |
|      struct io_mapped_region sq_region;  // SQEs        |
|      struct io_mapped_region param_region;               |
|                                                          |
|      struct io_rings *rings;  -->  用户空间共享          |
|      u32 *sq_array;                                      |
|      struct io_uring_sqe *sq_sqes;                       |
|                                                          |
|      struct xarray io_bl_xa;  // 提供缓冲区组            |
|                                                          |
|      struct io_rsrc_data buf_table; // 固定缓冲区表      |
|      struct io_alloc_cache {                             |
|          node_cache,                                     |
|          imu_cache,                                      |
|          apoll_cache,                                    |
|          ...                                             |
|      }                                                   |
|  }                                                       |
|                                                          |
|  +--------------------------------------------------+   |
|  |  struct io_mapped_region {                       |   |
|  |      struct page **pages;  --> 共享物理页        |   |
|  |      void *ptr;           --> 内核虚拟地址       |   |
|  |      unsigned nr_pages;                          |   |
|  |  }                                               |   |
|  +--------------------------------------------------+   |
|                                                          |
+----------------------------------------------------------+
```

### 6.2 环形缓冲区结构

```
struct io_rings (共享内存)
+------------------------+----------------+
| sq.head (kernel write) | sq.tail (app) |
| sq.array[index]        |                |
+------------------------+----------------+
                        |
                        v
                struct io_uring_sqe
                (sq_array[index])

+------------------------+----------------+
| cq.head (app)          | cq.tail       |
| cqes[0], cqes[1], ...  | (kernel write)|
+------------------------+----------------+
```

### 6.3 Provided Buffer Ring

```
用户空间 mmap 的缓冲区环
+--------------------------------------------------+
|  struct io_uring_buf_ring {                       |
|      __u16 tail;  <-- 用户写入                    |
|  }                                                |
|  +--------------------------------------------+  |
|  |  struct io_uring_buf {                    |  |
|  |      __u64 addr;                          |  |
|  |      __u32 len;                           |  |
|  |      __u16 bid;                           |  |
|  |      __u16 resv;                          |  |
|  |  } bufs[0];                               |  |
|  +--------------------------------------------+  |
|  |  struct io_uring_buf bufs[1];              |  |
|  +--------------------------------------------+  |
|  |       ...                                  |  |
|  +--------------------------------------------+  |
|  |  struct io_uring_buf bufs[n-1];            |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+

内核空间 struct io_buffer_list
+--------------------------------------------------+
|  struct io_buffer_list {                          |
|      bgid: 0                                      |
|      nr_entries: n (例如 256)                    |
|      head: 0      <-- 内核读取                    |
|      mask: n-1                                   |
|      flags: IOBL_BUF_RING                         |
|      buf_ring: --> 映射到用户空间                 |
|      region: io_mapped_region                     |
|  }                                                |
+--------------------------------------------------+
```

---

## 关键数据结构关系图

### 7.1 固定缓冲区关系

```
io_ring_ctx
    |
    +-- buf_table (struct io_rsrc_data)
    |       |
    |       +-- nr: 注册缓冲区数量
    |       +-- nodes[] (struct io_rsrc_node **)
    |               |
    |               +-- [0] --> struct io_rsrc_node {
    |               |           type: IORING_RSRC_BUFFER
    |               |           refs: 1
    |               |           buf: --> struct io_mapped_ubuf {
    |               |                   ubuf: 用户地址
    |               |                   len: 长度
    |               |                   nr_bvecs: 页数
    |               |                   folio_shift: 12 (或更大)
    |               |                   refs: 1
    |               |                   acct_pages: 已记账页数
    |               |                   bvec[] {
    |               |                       [0] { page, len, offset }
    |               |                       [1] { page, len, offset }
    |               |                       ...
    |               |                   }
    |               |           }
    |               +-- [1] --> ...
    |
    +-- imu_cache (struct io_alloc_cache)  // 分配缓存
            entries[] --> 回收的 io_mapped_ubuf 对象
```

### 7.2 提供缓冲区关系

```
io_ring_ctx
    |
    +-- io_bl_xa (struct xarray)
    |       |
    |       +-- bgid=0 --> struct io_buffer_list {
    |       |               flags: IOBL_BUF_RING
    |       |               buf_ring: --> struct io_uring_buf_ring {
    |       |                               tail: 用户写入
    |       |                               bufs[] {
    |       |                                   [0] { addr, len, bid }
    |       |                                   ...
    |       |                               }
    |       |                       }
    |       |               region: io_mapped_region
    |       |               head: 内核读取位置
    |       |               mask: nr_entries-1
    |       +-- bgid=1 --> struct io_buffer_list {
    |                       flags: 0 (经典列表)
    |                       buf_list: struct list_head
    |                           +-- io_buffer {
    |                               |   addr, len, bid
    |                               +-- io_buffer {
    |                                   |   addr, len, bid
    |                                   +-- ...
```

### 7.3 请求缓冲区选择流程

```
io_kiocb {
    flags: REQ_F_BUFFER_SELECT 或 REQ_F_BUFFER_RING
    buf_index: 缓冲区组 ID 或缓冲区索引
    kbuf: struct io_buffer * (经典模式)
}

io_buffer_select(req, len, buf_group)
    |
    +-- io_ring_submit_lock()
    |
    +-- bl = io_buffer_get_list(ctx, buf_group)
    |       |
    |       +-- xa_load(&ctx->io_bl_xa, bgid)
    |
    +-- if (bl->flags & IOBL_BUF_RING)
    |       |
    |       +-- io_ring_buffer_select()
    |               |
    |               +-- 读取 buf_ring->tail
    |               +-- 获取 buf_ring->bufs[head & mask]
    |               +-- 设置 req->flags |= REQ_F_BUFFER_RING
    |               +-- req->buf_index = buf->bid
    |
    +-- else
            |
            +-- io_provided_buffer_select()
                    |
                    +-- 从 buf_list 取第一个 io_buffer
                    +-- 设置 req->flags |= REQ_F_BUFFER_SELECTED
                    +-- req->kbuf = buf
                    +-- req->buf_index = buf->bid
```

---

## 参考代码路径

| 文件 | 行号 | 描述 |
|------|------|------|
| io_uring/memmap.c | 295-319 | `io_uring_mmap()` 内存映射入口 |
| io_uring/memmap.c | 152-182 | `io_region_allocate_pages()` 页分配 |
| io_uring/memmap.c | 114-132 | `io_region_init_ptr()` 内核地址映射 |
| io_uring/kbuf.c | 616-696 | `io_register_pbuf_ring()` 缓冲区环注册 |
| io_uring/kbuf.c | 192-224 | `io_ring_buffer_select()` 环形缓冲区选择 |
| io_uring/kbuf.c | 108-133 | `io_kbuf_recycle_legacy()` 缓冲区回收 |
| io_uring/rsrc.c | 858-925 | `io_sqe_buffers_register()` 固定缓冲区注册 |
| io_uring/rsrc.c | 762-856 | `io_sqe_buffer_register()` 单个缓冲区注册 |
| io_uring/rsrc.c | 645-675 | `io_buffer_account_pin()` 页记账 |
| io_uring/rsrc.c | 1049-1099 | `io_import_fixed()` 固定缓冲区导入 |
| io_uring/alloc_cache.c | 21-34 | `io_alloc_cache_init()` 缓存初始化 |
| io_uring/alloc_cache.c | 5-18 | `io_alloc_cache_free()` 缓存释放 |

---

## 版本信息

- 内核版本: Linux 7.0+ (基于当前源码)
- 文档编写日期: 2026-04-26
- 分析文件版本:
  - io_uring/kbuf.c: 最新
  - io_uring/memmap.c: 最新
  - io_uring/alloc_cache.c: 最新
  - io_uring/rsrc.c: 最新
