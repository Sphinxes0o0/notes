# Linux Kernel Swap Subsystem Analysis

## Table of Contents

1. [swap_info_struct Structure](#1-swap_info_struct-structure)
2. [Swap Cluster Mechanism](#2-swap-cluster-mechanism)
3. [swapon/swapoff System Calls](#3-swapon-swapoff-system-calls)
4. [swapin_readahead Page Swap-in](#4-swapin_readahead-page-swap-in)
5. [swap_readpage/swap_writepage I/O Operations](#5-swap_readpageswap_writepage-io-operations)
6. [Swap Cache Structure (XA Tree)](#6-swap-cache-structure-xa-tree)
7. [swp_entry_t Definition and PTE Conversion](#7-swp_entry_t-definition-and-pte-conversion)
8. [add_to_swap / free_swap_and_cache](#8-add_to_swap--free_swap_and_cache)

---

## 1. swap_info_struct Structure

**Location:** `include/linux/swap.h` lines 261-303

```c
struct swap_info_struct {
    struct percpu_ref users;          /* indicate and keep swap device valid */
    unsigned long flags;             /* SWP_USED etc: see below */
    signed short prio;               /* swap priority of this type */
    struct plist_node list;          /* entry in swap_active_head */
    signed char type;                /* strange name for an index */
    unsigned int max;                /* extent of the swap_map */
    unsigned char *swap_map;         /* vmalloc'ed array of usage counts */
    unsigned long *zeromap;           /* kvmalloc'ed bitmap to track zero pages */
    struct swap_cluster_info *cluster_info; /* cluster info. Only for SSD */
    struct list_head free_clusters;   /* free clusters list */
    struct list_head full_clusters;   /* full clusters list */
    struct list_head nonfull_clusters[SWAP_NR_ORDERS];
    struct list_head frag_clusters[SWAP_NR_ORDERS];
    unsigned int pages;               /* total of usable pages of swap */
    atomic_long_t inuse_pages;        /* number of those currently in use */
    struct swap_sequential_cluster *global_cluster;
    spinlock_t global_cluster_lock;
    struct rb_root swap_extent_root;  /* root of the swap extent rbtree */
    struct block_device *bdev;        /* swap device or bdev of swap file */
    struct file *swap_file;           /* seldom referenced */
    struct completion comp;           /* seldom referenced */
    spinlock_t lock;                  /* protect map scan related fields */
    spinlock_t cont_lock;             /* protect swap count continuation page list */
    struct work_struct discard_work;  /* discard worker */
    struct work_struct reclaim_work;  /* reclaim worker */
    struct list_head discard_clusters; /* discard clusters list */
    struct plist_node avail_list;     /* entry in swap_avail_head */
};
```

### Flags (enum)

| Flag | Value | Description |
|------|-------|-------------|
| SWP_USED | 0x01 | slot in swap_info[] used |
| SWP_WRITEOK | 0x02 | ok to write to this swap |
| SWP_DISCARDABLE | 0x04 | blkdev support discard |
| SWP_DISCARDING | 0x08 | now discarding a free cluster |
| SWP_SOLIDSTATE | 0x10 | blkdev seeks are cheap |
| SWP_CONTINUED | 0x20 | swap_map has count continuation |
| SWP_BLKDEV | 0x40 | its a block device |
| SWP_ACTIVATED | 0x80 | set after swap_activate success |
| SWP_FS_OPS | 0x100 | swapfile operations go through fs |
| SWP_AREA_DISCARD | 0x200 | single-time swap area discards |
| SWP_PAGE_DISCARD | 0x400 | freed swap page-cluster discards |
| SWP_STABLE_WRITES | 0x800 | no overwrite PG_writeback pages |
| SWP_SYNCHRONOUS_IO | 0x1000 | synchronous IO is efficient |

### Key Limits

- **MAX_SWAPFILES_SHIFT:** 5 (maximum 32 swap files)
- **MAX_SWAPFILES:** `(1 << 5) - SWP_DEVICE_NUM - SWP_MIGRATION_NUM - SWP_HWPOISON_NUM - SWP_PTE_MARKER_NUM`
- **SWAP_CLUSTER_MAX:** 32
- **SWAPFILE_CLUSTER:** 256 (or HPAGE_PMD_NR for THP)

---

## 2. Swap Cluster Mechanism

**Location:** `mm/swap.h` lines 11-54, `mm/swapfile.c` lines 863-963

### Cluster Structure

```c
struct swap_cluster_info {
    spinlock_t lock;
    u16 count;
    u8 flags;
    u8 order;
    atomic_long_t __rcu *table;  /* Swap table entries */
    struct list_head list;
};

enum swap_cluster_flags {
    CLUSTER_FLAG_NONE = 0,
    CLUSTER_FLAG_FREE,
    CLUSTER_FLAG_NONFULL,
    CLUSTER_FLAG_FRAG,
    CLUSTER_FLAG_USABLE = CLUSTER_FLAG_FRAG,
    CLUSTER_FLAG_FULL,
    CLUSTER_FLAG_DISCARD,
    CLUSTER_FLAG_MAX,
};
```

### Cluster Allocation

Clusters are managed through lists:
- `free_clusters` - completely free clusters
- `full_clusters` - completely full clusters
- `nonfull_clusters[]` - clusters with some free slots (per order)
- `frag_clusters[]` - fragmented or contended clusters

**Allocation flow (alloc_swap_scan_cluster):**
1. Scan the cluster for available slots via `cluster_scan_range()`
2. If slot found and empty, call `cluster_alloc_range()`
3. If cluster becomes full, move to `full_clusters`
4. For SSD (SWP_SOLIDSTATE), use per-CPU offset cache

### Cluster Size

- **SWAPFILE_CLUSTER:** 256 pages (normal) or HPAGE_PMD_NR (THP enabled)
- **SWAP_CLUSTER_MAX:** 32 pages

---

## 3. swapon/swapoff System Calls

### swapon()

**Location:** `mm/swapfile.c` lines 3328-3569

```c
SYSCALL_DEFINE2(swapon, const char __user *, specialfile, int, swap_flags)
```

**流程:**

1. **权限检查** - `CAP_SYS_ADMIN` required
2. **分配 swap_info** - `alloc_swap_info()`
3. **打开 swap 文件** - `file_open_name()`
4. **声明 swap file** - `claim_swap_file()`
5. **读取 swap header** - `read_mapping_folio()` and `read_swap_header()`
6. **设置 swap extents** - `setup_swap_extents()` -> `add_swap_extent()` or `generic_swapfile_activate()`
7. **分配 swap_map** - `valloc(maxpages)`
8. **初始化 cgroup** - `swap_cgroup_swapon()`
9. **设置 zeromap** - `kvmalloc_array()`
10. **设置 cluster_info** - `setup_clusters()`
11. **处理 discard** - if SWAP_FLAG_DISCARD set
12. **启用 swap** - `enable_swap_info()`
13. **设置 S_SWAPFILE** - mark inode

### swapoff()

**Location:** `mm/swapfile.c` lines 2769-2907

```c
SYSCALL_DEFINE1(swapoff, const char __user *, specialfile)
```

**流程:**

1. **权限检查** - `CAP_SYS_ADMIN` required
2. **查找 swap_info** - iterate `swap_active_head`
3. **检查内存** - `security_vm_enough_memory_mm()`
4. **移除活动列表** - `plist_del()` and `del_from_avail_list()`
5. **等待分配完成** - `wait_for_allocation()`
6. **清除所有 PTE** - `try_to_unuse(type)` - 遍历所有 mm_struct
7. **杀死 percpu_ref** - `percpu_ref_kill()` and `synchronize_rcu()`
8. **刷新 worker** - `flush_work()`
9. **销毁 extents** - `destroy_swap_extents()`
10. **释放资源** - `vfree(swap_map)`, `kvfree(zeromap)`, `free_cluster_info()`
11. **清理 cgroup** - `swap_cgroup_swapoff()`
12. **清除 S_SWAPFILE** - clear inode flag

---

## 4. swapin_readahead Page Swap-in

**Location:** `mm/swap_state.c` lines 913-927

### swapin_readahead()

```c
struct folio *swapin_readahead(swp_entry_t entry, gfp_t gfp_mask,
                               struct vm_fault *vmf)
{
    struct mempolicy *mpol;
    pgoff_t ilx;
    struct folio *folio;

    mpol = get_vma_policy(vmf->vma, vmf->address, 0, &ilx);
    folio = swap_use_vma_readahead() ?
        swap_vma_readahead(entry, gfp_mask, mpol, ilx, vmf) :
        swap_cluster_readahead(entry, gfp_mask, mpol, ilx);
    mpol_cond_put(mpol);

    return folio;
}
```

### Two Readahead Modes

#### 1. Cluster-based Readahead (`swap_cluster_readahead`)

**Location:** `mm/swap_state.c` lines 720-772

- Reads `1 << page_cluster` entries around the target offset
- Uses `swapin_nr_pages()` to calculate window size based on hit rate
- Reads aligned block of swap device pages

```c
mask = swapin_nr_pages(offset) - 1;
start_offset = offset & ~mask;
end_offset = offset | mask;
```

#### 2. VMA-based Readahead (`swap_vma_readahead`)

**Location:** `mm/swap_state.c` lines 828-899

- Uses fault address and VMA for readahead decision
- Reads pages whose virtual addresses are around the fault address
- Dynamic window size based on `swap_vma_ra_win()`

### Readahead Window Calculation

**Location:** `mm/swap_state.c` lines 641-700

```c
static unsigned int __swapin_nr_pages(unsigned long prev_offset,
                                      unsigned long offset,
                                      int hits, int max_pages, int prev_win)
{
    pages = hits + 2;  // heuristic: hits + 2
    if (pages == 2) {
        // adjacent offset check
        if (offset != prev_offset + 1 && offset != prev_offset - 1)
            pages = 1;
    }
    // roundup to power of 2
    pages = roundup_pow_of_two(pages);
    // limit by max_pages and don't shrink too fast
}
```

---

## 5. swap_readpage/swap_writepage I/O Operations

**Location:** `mm/page_io.c`

### swap_read_folio()

**Location:** `mm/page_io.c` lines 609-657

```c
void swap_read_folio(struct folio *folio, struct swap_iocb **plug)
```

**流程:**

1. 检查 zeromap - `swap_read_folio_zeromap()` - 如果是零页直接返回
2. 检查 zswap - `zswap_load()` - 如果 zswap 有数据直接返回
3. 增加 zswap 保护 - `zswap_folio_swapin()`
4. 根据设备类型选择 I/O 方式:
   - **SWP_FS_OPS:** `swap_read_folio_fs()` - 通过文件系统
   - **SWP_SYNCHRONOUS_IO:** `swap_read_folio_bdev_sync()` - 同步块设备
   - **其他:** `swap_read_folio_bdev_async()` - 异步块设备

### swap_writepage()

**Location:** `mm/page_io.c` lines 240-289

```c
int swap_writeout(struct folio *folio, struct swap_iocb **swap_plug)
```

**流程:**

1. 检查是否可以跳过写回 - `folio_free_swap()`
2. 架构准备 - `arch_prepare_to_swap()`
3. 检查零页 - `is_folio_zero_filled()` - 设置 zeromap 位
4. 尝试 zswap - `zswap_store()`
5. 调用 `__swap_writepage()`

### __swap_writepage()

**Location:** `mm/page_io.c` lines 447-468

根据 `sis->flags` 选择:
- **SWP_FS_OPS:** `swap_writepage_fs()` - 通过文件系统
- **SWP_SYNCHRONOUS_IO:** `swap_writepage_bdev_sync()` - 同步
- **其他:** `swap_writepage_bdev_async()` - 异步

### I/O Structures

```c
struct swap_iocb {
    struct kiocb iocb;
    struct bio_vec bvec[SWAP_CLUSTER_MAX];
    int pages;
    int len;
};
```

### Bio End Handlers

- `end_swap_bio_read()` - lines 72-76
- `end_swap_bio_write()` - lines 52-56
- `sio_read_complete()` - lines 482-506
- `sio_write_complete()` - lines 344-372

---

## 6. Swap Cache Structure (XA Tree)

**Location:** `mm/swap_table.h`, `mm/swap_state.c`

### Swap Table Entry

Each swap slot in a cluster has an entry in the swap table:

```c
struct swap_table {
    atomic_long_t entries[SWAPFILE_CLUSTER];  // 256 entries per cluster
};
```

### Entry Types

| Type | Check | Description |
|------|-------|-------------|
| NULL | `swp_tb_is_null()` | Slot is empty |
| Folio | `swp_tb_is_folio()` | Swap cache folio |
| Shadow | `swp_tb_is_shadow()` | XA_VALUE for reclaim |

### Helper Functions

**Location:** `mm/swap_table.h` lines 28-129

```c
// Casting
unsigned long null_to_swp_tb(void)
unsigned long folio_to_swp_tb(struct folio *folio)
unsigned long shadow_swp_to_tb(void *shadow)

// Type checking
bool swp_tb_is_null(unsigned long swp_tb)
bool swp_tb_is_folio(unsigned long swp_tb)
bool swp_tb_is_shadow(unsigned long swp_tb)

// Access
struct folio *swp_tb_to_folio(unsigned long swp_tb)
void *swp_tb_to_shadow(unsigned long swp_tb)

// Atomic operations (require cluster lock)
void __swap_table_set(struct swap_cluster_info *ci, unsigned int off, unsigned long swp_tb)
unsigned long __swap_table_xchg(struct swap_cluster_info *ci, unsigned int off, unsigned long swp_tb)
unsigned long __swap_table_get(struct swap_cluster_info *ci, unsigned int off)
unsigned long swap_table_get(struct swap_cluster_info *ci, unsigned int off)  // RCU protected
```

### Swap Cache Address Space

**Location:** `mm/swap_state.c` lines 33-42

```c
static const struct address_space_operations swap_aops = {
    .dirty_folio    = noop_dirty_folio,
#ifdef CONFIG_MIGRATION
    .migrate_folio  = migrate_folio,
#endif
};

struct address_space swap_space __read_mostly = {
    .a_ops = &swap_aops,
};
```

### Key Cache Operations

| Function | Location | Description |
|----------|----------|-------------|
| `swap_cache_get_folio()` | swap_state.c:87-103 | Lookup folio in cache |
| `swap_cache_has_folio()` | swap_state.c:112-119 | Check if slot has cache |
| `__swap_cache_add_folio()` | swap_state.c:140-166 | Add folio to cache |
| `__swap_cache_del_folio()` | swap_state.c:237-282 | Remove folio from cache |
| `swap_cache_del_folio()` | swap_state.c:294-304 | Remove folio (with lock) |
| `__swap_cache_replace_folio()` | swap_state.c:320-352 | Replace folio in cache |
| `__swap_cache_clear_shadow()` | swap_state.c:362-373 | Clear shadow entries |
| `read_swap_cache_async()` | swap_state.c:615-639 | Async read into cache |

---

## 7. swp_entry_t Definition and PTE Conversion

**Location:** `include/linux/swapops.h`

### swp_entry_t Structure

```c
typedef struct {
    unsigned long val;
} swp_entry_t;
```

### Encoding Format

```
|----------+--------------------|
| swp_type | swp_offset         |
| (5 bits) | (remaining bits)   |
|----------+--------------------|
```

- **SWP_TYPE_SHIFT:** `BITS_PER_XA_VALUE - MAX_SWAPFILES_SHIFT` (typically 59 - 5 = 54)
- **SWP_OFFSET_MASK:** `(1UL << SWP_TYPE_SHIFT) - 1`

### Key Functions

```c
// Create swp_entry from type and offset
static inline swp_entry_t swp_entry(unsigned long type, pgoff_t offset)
{
    ret.val = (type << SWP_TYPE_SHIFT) | (offset & SWP_OFFSET_MASK);
    return ret;
}

// Extract type from swp_entry
static inline unsigned swp_type(swp_entry_t entry)
{
    return (entry.val >> SWP_TYPE_SHIFT);
}

// Extract offset from swp_entry
static inline pgoff_t swp_offset(swp_entry_t entry)
{
    return entry.val & SWP_OFFSET_MASK;
}

// Convert to arch-dependent PTE
static inline pte_t swp_entry_to_pte(swp_entry_t entry)
{
    arch_entry = __swp_entry(swp_type(entry), swp_offset(entry));
    return __swp_entry_to_pte(arch_entry);
}
```

### Special Swap Entries

| Type | Macro | Purpose |
|------|-------|---------|
| SWP_HWPOISON | `make_hwpoison_entry()` | Hardware poisoned pages |
| SWP_MIGRATION_READ | `make_readable_migration_entry()` | Migration source |
| SWP_MIGRATION_WRITE | `make_writable_migration_entry()` | Migration target |
| SWP_DEVICE_READ | `make_readable_device_private_entry()` | Device memory |
| SWP_DEVICE_WRITE | `make_writable_device_private_entry()` | Device memory |
| SWP_PTE_MARKER | `make_pte_marker_entry()` | PTE markers (uffd-wp, poison, guard) |

### Conversion with Radix Tree

```c
// Radix tree <-> swp_entry
static inline swp_entry_t radix_to_swp_entry(void *arg)
{
    entry.val = xa_to_value(arg);
    return entry;
}

static inline void *swp_to_radix_entry(swp_entry_t entry)
{
    return xa_mk_value(entry.val);
}
```

---

## 8. add_to_swap / free_swap_and_cache

### folio_alloc_swap() (formerly add_to_swap)

**Location:** `mm/swapfile.c` lines 1484-1538

```c
int folio_alloc_swap(struct folio *folio)
{
    unsigned int order = folio_order(folio);
    unsigned int size = 1 << order;

    VM_BUG_ON_FOLIO(!folio_test_locked(folio), folio);
    VM_BUG_ON_FOLIO(!folio_test_uptodate(folio), folio);

    if (order) {
        if (!IS_ENABLED(CONFIG_THP_SWAP))
            return -EAGAIN;
        if (size > SWAPFILE_CLUSTER)
            return -EINVAL;
    }

again:
    local_lock(&percpu_swap_cluster.lock);
    if (!swap_alloc_fast(folio))
        swap_alloc_slow(folio);
    local_unlock(&percpu_swap_cluster.lock);

    if (!order && unlikely(!folio_test_swapcache(folio))) {
        if (swap_sync_discard())
            goto again;
    }

    if (unlikely(mem_cgroup_try_charge_swap(folio, folio->swap)))
        swap_cache_del_folio(folio);

    if (unlikely(!folio_test_swapcache(folio)))
        return -ENOMEM;

    return 0;
}
```

**流程:**

1. 验证 folio 已锁定且最新
2. 尝试快速分配 - `swap_alloc_fast()` - 使用 per-CPU 缓存
3. 慢速分配 - `swap_alloc_slow()` - 扫描 cluster 列表
4. 如果 order=0 且未加入 cache，同步 discard
5. memcg 计费 - `mem_cgroup_try_charge_swap()`
6. 检查是否成功加入 swap cache

### folio_dup_swap() - Increase Swap Count

**Location:** `mm/swapfile.c` lines 1555-1573

Called when folio is unmapped and swap entry takes its place.

```c
int folio_dup_swap(struct folio *folio, struct page *subpage)
{
    swp_entry_t entry = folio->swap;
    unsigned long nr_pages = folio_nr_pages(folio);

    if (subpage) {
        entry.val += folio_page_idx(folio, subpage);
        nr_pages = 1;
    }

    while (!err && __swap_duplicate(entry, 1, nr_pages) == -ENOMEM)
        err = add_swap_count_continuation(entry, GFP_ATOMIC);

    return err;
}
```

### folio_put_swap() - Decrease Swap Count

**Location:** `mm/swapfile.c` lines 1577+

Decreases swap count and frees entries if count reaches zero.

### folio_free_swap() - Free Swap Slot

**Location:** `mm/swapfile.c` lines 1876-1886

```c
bool folio_free_swap(struct folio *folio)
{
    if (!folio_swapcache_freeable(folio))
        return false;
    if (folio_swapped(folio))
        return false;

    swap_cache_del_folio(folio);
    folio_set_dirty(folio);
    return true;
}
```

**条件:**
- folio 必须在 swap cache 中 (`folio_swapcache_freeable`)
- folio 不能被其他 PTE 引用 (`folio_swapped`)

### free_folio_and_swap_cache()

**Location:** `mm/swap_state.c` lines 396-401

```c
void free_folio_and_swap_cache(struct folio *folio)
{
    free_swap_cache(folio);
    if (!is_huge_zero_folio(folio))
        folio_put(folio);
}
```

### free_swap_cache()

**Location:** `mm/swap_state.c` lines 383-390

```c
void free_swap_cache(struct folio *folio)
{
    if (folio_test_swapcache(folio) && !folio_mapped(folio) &&
        folio_trylock(folio)) {
        folio_free_swap(folio);
        folio_unlock(folio);
    }
}
```

---

## Complete Swap Workflow

### Swap-out Workflow

```
1. Page reclaim selects an anon page
   └─> vmscan.c: shrink_folio_list()

2. Add page to swap cache
   └─> folio_alloc_swap() [swapfile.c:1493]
       ├─> swap_alloc_fast/slow() - allocate cluster slot
       ├─> mem_cgroup_try_charge_swap() - charge to memcg
       └─> __swap_cache_add_folio() - add to swap cache

3. Write page to swap device
   └─> swap_writeout() [page_io.c:240]
       ├─> arch_prepare_to_swap()
       ├─> is_folio_zero_filled() - check for zeromap
       ├─> zswap_store() - try zswap first
       └─> __swap_writepage() [page_io.c:447]
           └─> swap_writepage_fs/bdev_sync/bdev_async()

4. Update PTE to swap entry
   └─> do_swap_page() [memory.c]
       └─> set_pte_at() with swp_entry_to_pte()
```

### Swap-in Workflow

```
1. Page fault encounters swap entry
   └─> do_swap_page() [memory.c:4047]

2. Check swap cache first
   └─> swap_cache_get_folio() [swap_state.c:87]
       └─> If found, skip to step 5

3. Allocate new folio
   └─> swap_cache_alloc_folio() [swap_state.c:551]
         └─> folio_alloc() + __swap_cache_prepare_and_add()

4. Readahead (optional)
   └─> swapin_readahead() [swap_state.c:913]
       ├─> swap_cluster_readahead() - disk-based
       └─> swap_vma_readahead() - vma-based

5. Read page from swap
   └─> swap_read_folio() [page_io.c:609]
       ├─> swap_read_folio_zeromap() - check zeromap
       ├─> zswap_load() - try zswap first
       └─> swap_read_folio_fs/bdev_sync/bdev_async()

6. Insert into page table
   └─> do_swap_page() continues
       └─> set_pte_at() with pte_mkuffd_wp(), etc.
```

### Swap-off Workflow

```
1. syscall: swapoff()
   └─> mm/swapfile.c:2769

2. Remove from active list
   └─> plist_del() and del_from_avail_list()

3. Wait for ongoing I/O
   └─> wait_for_allocation()

4. Clear all PTEs using this swap
   └─> try_to_unuse() [swapfile.c:2399]
       ├─> shmem_unuse() - for shmem files
       ├─> unuse_mm() - for each mm_struct
       └─> folio_free_swap() for remaining entries

5. Kill swap device reference
   └─> percpu_ref_kill() and synchronize_rcu()

6. Free all resources
   └─> destroy_swap_extents()
   └─> vfree(swap_map)
   └─> kvfree(zeromap)
   └─> free_cluster_info()
   └─> swap_cgroup_swapoff()
```

---

## Key Source Files Summary

| File | Purpose |
|------|---------|
| `include/linux/swap.h` | Core swap definitions, swap_info_struct |
| `include/linux/swapops.h` | swp_entry_t operations, PTE conversion |
| `mm/swap.h` | Swap cluster definitions, internal headers |
| `mm/swap_table.h` | Swap table (XA tree) helpers |
| `mm/swapfile.c` | swapon/swapoff, swap allocation, cluster management |
| `mm/swap_state.c` | Swap cache operations, readahead |
| `mm/page_io.c` | swap_readpage/swap_writepage I/O |

---

## Key Data Structures Summary

```
swap_info[]           - Array of swap devices (MAX_SWAPFILES)
  └─> swap_info_struct - Per-swap device info
       ├─> swap_map    - Usage count per slot (unsigned char)
       ├─> zeromap    - Bitmap for zero-filled pages
       ├─> cluster_info - Per-cluster info array
       │    └─> swap_cluster_info
       │         ├─> table  - Array of folio/shadow pointers (256 entries)
       │         ├─> count  - Used slots in cluster
       │         └─> flags  - Cluster state
       └─> swap_extent_root - RB tree of disk extents

swap_space            - Global address_space for swap cache
  └─> Uses XArray internally for entry->folio mapping

swp_entry_t           - Software PTE encoding
  └─> val = (type << SWP_TYPE_SHIFT) | offset
```
