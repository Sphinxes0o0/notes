# page_pool - 内存页池

## 1. 模块架构

### 1.1 功能概述

page_pool 是一种高效的内存页管理机制，为网络设备提供可回收的内存页，减少内存分配开销。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/page_pool.c` | page_pool 实现 |
| `include/linux/page_pool.h` | page_pool 定义 |

## 2. 核心数据结构

### 2.1 struct page_pool

```c
// include/linux/page_pool.h:40
struct page_pool {
    struct list_head list;           // 空闲页链表
    unsigned int pool_size;          // 池大小
    unsigned int pages_state_hold_cnt;

    // 内存页属性
    unsigned int alloc.cache_size;    // 缓存大小
    struct page *(*alloc_pages)(struct page_pool *pool, gfp_t gfp);

    // 缓存
    void **cache;

    // 统计
    atomic_t avail;                  // 可用页数
    atomic_t total;                 // 总页数
};
```

### 2.2 struct page_pool_params

```c
// include/linux/page_pool.h:100
struct page_pool_params {
    unsigned int flags;
    unsigned int order;              // 页阶数 (0=4KB, 1=8KB)
    unsigned int pool_size;          // 池大小
    int nid;                         // NUMA 节点
    gfp_t gfp;                       // 分配标志

    struct net_device *dev;          // 关联设备
};
```

## 3. 分配与释放

### 3.1 page_pool_alloc()

```c
// net/core/page_pool.c:180
struct page *page_pool_alloc(struct page_pool *pool)
{
    struct page *page;

    // 先从缓存获取
    if (pool->cache) {
        page = pool->cache[--pool->alloc.cache_size];
        if (page)
            return page;
    }

    // 从页池分配
    page = pool->alloc_pages(pool, GFP_ATOMIC);
    if (page)
        atomic_dec(&pool->avail);

    return page;
}
```

### 3.2 page_pool_release()

```c
// net/core/page_pool.c:240
void page_pool_release(struct page_pool *pool, struct page *page)
{
    // 放回缓存或空闲链表
    if (pool->cache_size < pool->pool_size) {
        pool->cache[pool->cache_size++] = page;
        return;
    }

    // 真正的释放
    put_page(page);
}
```

## 4. DMA 映射

### 4.1 page_pool_set_fp()

```c
// net/core/page_pool.c:300
static void page_pool_set_fp(struct page *page, dma_addr_t dma)
{
    page->dma_addr = dma;
    set_bit(PAGE_FLAGS_MAPPED, &page->flags);
}
```

### 4.2 page_pool_get_dma()

```c
// net/core/page_pool.c:320
static dma_addr_t page_pool_get_dma(struct page *page)
{
    return page->dma_addr;
}
```

## 5. 使用场景

### 5.1 驱动集成

```c
// 在驱动中使用 page_pool
struct xxx_priv {
    struct page_pool *page_pool;
};

xxx_init(struct net_device *dev)
{
    priv->page_pool = page_pool_create(&params);
}

xxx_rx(struct net_device *dev, struct page *page)
{
    // 使用 page_pool 管理页
}
```
