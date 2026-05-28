# Linux 内核 KVM 内存管理机制分析

本文档详细分析 Linux Kernel KVM (Kernel-based Virtual Machine) 的内存管理机制，包括 Dirty Ring、PFN Cache、Guest Memfd、Memory Slot 等核心组件。

## 目录

1. [Dirty Ring 机制](#1-dirty-ring-机制)
2. [PFN Cache](#2-pfn-cache)
3. [Guest Memfd](#3-guest-memfd)
4. [Memory Slot](#4-memory-slot)
5. [内存分配流程](#5-内存分配流程)
6. [架构图](#6-架构图)

## 源码位置

| 文件 | 说明 |
|------|------|
| `virt/kvm/kvm_main.c` | KVM 核心实现，VM 创建/销毁，memory slot 管理 |
| `virt/kvm/dirty_ring.c` | Dirty ring 实现，脏页追踪 |
| `virt/kvm/pfncache.c` | GFN-to-PFN cache 实现 |
| `virt/kvm/guest_memfd.c` | Guest memfd 文件系统实现 |
| `include/linux/kvm_host.h` | KVM 主机端结构体定义 |
| `include/linux/kvm_dirty_ring.h` | Dirty ring 接口定义 |
| `include/linux/kvm_types.h` | KVM 类型定义 |

---

## 1. Dirty Ring 机制

### 1.1 概述

Dirty Ring 是 KVM 中用于追踪虚拟机脏页的新一代机制，相比传统的 dirty bitmap 方式具有更好的可扩展性和更低的锁竞争。

**源码位置**: `virt/kvm/dirty_ring.c`, `include/linux/kvm_dirty_ring.h`

### 1.2 结构定义

#### struct kvm_dirty_ring

```c
// include/linux/kvm_dirty_ring.h:21-28
struct kvm_dirty_ring {
    u32 dirty_index;    // 下一个可用的脏页槽位（生产者指针）
    u32 reset_index;     // 下一个待重置的槽位（消费者指针）
    u32 size;            // ring 大小（条目数量）
    u32 soft_limit;      // 软限制，达到此值时 VCPU 退出到用户空间
    struct kvm_dirty_gfn *dirty_gfns;  // 脏页数组
    int index;           // ring 索引
};
```

**关键字段说明**:
- `dirty_index` 和 `reset_index` 形成生产者-消费者模式
- `size` 表示 ring 容量，通常为 CPU 相关的值
- `soft_limit` 用于触发 VCPU 退出，让用户空间有机会收集脏页
- `dirty_gfns` 数组存储脏页的 GFN 信息

#### struct kvm_dirty_gfn

```c
// include/linux/kvm.h (用户空间可见)
struct kvm_dirty_gfn {
    __u32 slot;    // 内存槽 ID
    __u32 flags;   // 标志位
    __u64 offset;  // GFN 相对于 slot 起始地址的偏移
};
```

### 1.3 kvm_dirty_ring_alloc()

**位置**: `virt/kvm/dirty_ring.c:74-88`

```c
int kvm_dirty_ring_alloc(struct kvm *kvm, struct kvm_dirty_ring *ring,
                         int index, u32 size)
{
    ring->dirty_gfns = vzalloc(size);  // 使用 vzalloc 分配内存
    if (!ring->dirty_gfns)
        return -ENOMEM;

    ring->size = size / sizeof(struct kvm_dirty_gfn);  // 计算条目数量
    ring->soft_limit = ring->size - kvm_dirty_ring_get_rsvd_entries(kvm);
    ring->dirty_index = 0;
    ring->reset_index = 0;
    ring->index = index;

    return 0;
}
```

**功能说明**:
- 使用 `vzalloc()` 分配零初始化的内存
- `soft_limit` 预留 `KVM_DIRTY_RING_RSVD_ENTRIES` 个条目作为保护
- `kvm_dirty_ring_get_rsvd_entries()` 计算预留 entries (dirty_ring.c:19-22)

### 1.4 kvm_dirty_ring_push()

**位置**: `virt/kvm/dirty_ring.c:218-241`

```c
void kvm_dirty_ring_push(struct kvm_vcpu *vcpu, u32 slot, u64 offset)
{
    struct kvm_dirty_ring *ring = &vcpu->dirty_ring;
    struct kvm_dirty_gfn *entry;

    /* 环不应该满 */
    WARN_ON_ONCE(kvm_dirty_ring_full(ring));

    // 计算当前条目位置（使用掩码实现环形缓冲）
    entry = &ring->dirty_gfns[ring->dirty_index & (ring->size - 1)];

    entry->slot = slot;
    entry->offset = offset;
    /*
     * 确保数据先填充完成，再发布到用户空间
     */
    smp_wmb();
    kvm_dirty_gfn_set_dirtied(entry);  // 设置 KVM_DIRTY_GFN_F_DIRTY 标志
    ring->dirty_index++;
    trace_kvm_dirty_ring_push(ring, slot, offset);

    // 达到软限制时触发 VCPU 请求
    if (kvm_dirty_ring_soft_full(ring))
        kvm_make_request(KVM_REQ_DIRTY_RING_SOFT_FULL, vcpu);
}
```

**关键点**:
- 使用 `smp_wmb()` 保证内存顺序
- 达到 `soft_limit` 时发送 `KVM_REQ_DIRTY_RING_SOFT_FULL` 请求
- `kvm_dirty_gfn_set_dirtied()` 设置 `flags = KVM_DIRTY_GFN_F_DIRTY` (dirty_ring.c:95-98)

### 1.5 kvm_dirty_ring_reset()

**位置**: `virt/kvm/dirty_ring.c:105-216`

```c
int kvm_dirty_ring_reset(struct kvm *kvm, struct kvm_dirty_ring *ring,
                         int *nr_entries_reset)
{
    u32 cur_slot, next_slot;
    u64 cur_offset, next_offset;
    unsigned long mask = 0;
    struct kvm_dirty_gfn *entry;

    // ... 批处理重置逻辑

    while (likely((*nr_entries_reset) < INT_MAX)) {
        if (signal_pending(current))
            return -EINTR;

        entry = &ring->dirty_gfns[ring->reset_index & (ring->size - 1)];

        if (!kvm_dirty_gfn_harvested(entry))  // 检查 KVM_DIRTY_GFN_F_RESET
            break;

        next_slot = READ_ONCE(entry->slot);
        next_offset = READ_ONCE(entry->offset);

        /* 更新标志位 */
        kvm_dirty_gfn_set_invalid(entry);  // smp_store_release(&gfn->flags, 0)

        ring->reset_index++;
        (*nr_entries_reset)++;

        // 批处理优化：合并同一 slot 连续范围的 GFNs
        if (mask) {
            cond_resched();
            if (next_slot == cur_slot) {
                s64 delta = next_offset - cur_offset;
                if (delta >= 0 && delta < BITS_PER_LONG) {
                    mask |= 1ull << delta;
                    continue;
                }
                // 处理反向情况...
            }
            kvm_reset_dirty_gfn(kvm, cur_slot, cur_offset, mask);
        }
        // ...
    }
    // ...
}
```

**核心优化**:
- 批量处理相邻 GFN 的重置操作
- 使用位掩码一次性重置多个连续页面
- 调用 `cond_resched()` 避免锁竞争
- `kvm_dirty_gfn_harvested()` 检查 `flags & KVM_DIRTY_GFN_F_RESET` (dirty_ring.c:100-103)

### 1.6 Dirty Ring vs Dirty Bitmap

| 特性 | Dirty Ring | Dirty Bitmap |
|------|------------|--------------|
| 内存占用 | O(n) n=VCPU数 | O(2*pages_per_slot) |
| 锁竞争 | 低（每 VCPU 独立 ring） | 高（全局 bitmap） |
| 扩展性 | 好 | 差 |
| 实现复杂度 | 中等 | 简单 |
| 用户空间交互 | 轮询/事件驱动 | ioctl 同步 |

---

## 2. PFN Cache

### 2.1 概述

PFN Cache（Page Frame Number Cache）是 KVM 中用于缓存 GFN 到 PFN 转换结果的机制，减少重复的页表查找开销。

**源码位置**: `virt/kvm/pfncache.c`

### 2.2 结构定义

#### struct gfn_to_pfn_cache

PFN 缓存结构维护 GFN 到 PFN 的映射关系，核心字段包括：

```c
// include/linux/kvm_types.h:84-97
struct gfn_to_pfn_cache {
    u64 generation;           // memslot generation 号
    gpa_t gpa;               // Guest Physical Address
    unsigned long uhva;      // Userspace HVA (用户空间虚拟地址)
    struct kvm_memory_slot *memslot;  // 关联的 memory slot
    struct kvm *kvm;         // KVM 实例
    struct list_head list;    // 链接到 kvm->gpc_list
    rwlock_t lock;           // 读写锁保护
    struct mutex refresh_lock;  // 刷新时的互斥锁
    void *khva;              // Kernel HVA (内核虚拟地址)
    kvm_pfn_t pfn;           // 缓存的 PFN
    bool active;              // 是否激活
    bool valid;               // 缓存是否有效
};
```

### 2.3 pfncache_init()

**位置**: `virt/kvm/pfncache.c:385-395`

```c
void kvm_gpc_init(struct gfn_to_pfn_cache *gpc, struct kvm *kvm)
{
    rwlock_init(&gpc->lock);
    mutex_init(&gpc->refresh_lock);

    gpc->kvm = kvm;
    gpc->pfn = KVM_PFN_ERR_FAULT;    // 初始化为错误 PFN
    gpc->gpa = INVALID_GPA;
    gpc->uhva = KVM_HVA_ERR_BAD;
    gpc->active = gpc->valid = false;
}
```

### 2.4 kvm_pfncache_invalidate()

**位置**: `virt/kvm/pfncache.c:25-58`

```c
void gfn_to_pfn_cache_invalidate_start(struct kvm *kvm, unsigned long start,
                                       unsigned long end)
{
    struct gfn_to_pfn_cache *gpc;

    spin_lock(&kvm->gpc_lock);
    list_for_each_entry(gpc, &kvm->gpc_list, list) {
        read_lock_irq(&gpc->lock);

        /* 只检查单页，长度检查由调用者负责 */
        if (gpc->valid && !is_error_noslot_pfn(gpc->pfn) &&
            gpc->uhva >= start && gpc->uhva < end) {
            read_unlock_irq(&gpc->lock);

            /*
             * 刷新过程中可能有修改，需重新检查
             */
            write_lock_irq(&gpc->lock);
            if (gpc->valid && !is_error_noslot_pfn(gpc->pfn) &&
                gpc->uhva >= start && gpc->uhva < end)
                gpc->valid = false;  // 标记为无效
            write_unlock_irq(&gpc->lock);
            continue;
        }

        read_unlock_irq(&gpc->lock);
    }
    spin_unlock(&kvm->gpc_lock);
}
```

**功能说明**:
- 作为 MMU notifier 的回调函数
- 当发生页面回收或迁移时，使相关缓存失效
- 使用两阶段锁（读锁→写锁）减少锁竞争

### 2.5 kvm_gpc_refresh()

**位置**: `virt/kvm/pfncache.c:366-383`

```c
int kvm_gpc_refresh(struct gfn_to_pfn_cache *gpc, unsigned long len)
{
    unsigned long uhva;

    guard(mutex)(&gpc->refresh_lock);

    if (!kvm_gpc_is_valid_len(gpc->gpa, gpc->uhva, len))
        return -EINVAL;

    /* 如果 GPA 有效则忽略 HVA */
    uhva = kvm_is_error_gpa(gpc->gpa) ? gpc->uhva : KVM_HVA_ERR_BAD;

    return __kvm_gpc_refresh(gpc, gpc->gpa, uhva);
}
```

### 2.6 GUP 机制

GUP（Get User Pages）是 Linux 内核中用于获取用户空间页面引用的机制，在 KVM 中用于：

```c
// pfncache.c 中的 hva_to_pfn 流程
new_pfn = hva_to_pfn(&kfp);
if (is_error_noslot_pfn(new_pfn))
    goto out_error;

// 获取内核映射
if (new_pfn == gpc->pfn)
    new_khva = old_khva;  // 复用已有映射
else
    new_khva = gpc_map(new_pfn);  // 创建新映射
```

**关键点**:
- 使用 FOLL_WRITE 标志获取写权限
- 支持直接映射和高内存映射
- 错误处理包括 KVM_PFN_ERR_FAULT 等

---

## 3. Guest Memfd

### 3.1 概述

Guest Memfd 是 KVM 实现基于 memfd 的 guest 内存管理机制，允许虚拟机使用匿名内存作为后端存储。

**源码位置**: `virt/kvm/guest_memfd.c`

### 3.2 核心结构

#### struct gmem_file

```c
// virt/kvm/guest_memfd.c:24-28
struct gmem_file {
    struct kvm *kvm;              // 关联的 KVM 实例
    struct xarray bindings;       // slot => gmem 绑定关系 (xa_for_each 遍历)
    struct list_head entry;       // 链接到 inode 的 i_private_list
};
```

#### struct gmem_inode

```c
// virt/kvm/guest_memfd.c:30-35
struct gmem_inode {
    struct shared_policy policy;  // NUMA 内存策略
    struct inode vfs_inode;       // 底层文件系统 inode

    u64 flags;                    // GUEST_MEMFD_FLAG_* 标志
};
```

**关键宏** (guest_memfd.c:37-43):

```c
#define GMEM_I(inode) \
    container_of(inode, struct gmem_inode, vfs_inode)

#define kvm_gmem_for_each_file(f, mapping) \
    list_for_each_entry(f, &(mapping)->i_private_list, entry)
```

### 3.3 kvm_gmem_create()

**位置**: `virt/kvm/guest_memfd.c:628-640`

```c
int kvm_gmem_create(struct kvm *kvm, struct kvm_create_guest_memfd *args)
{
    loff_t size = args->size;
    u64 flags = args->flags;

    if (flags & ~kvm_gmem_get_supported_flags(kvm))
        return -EINVAL;

    if (size <= 0 || !PAGE_ALIGNED(size))
        return -EINVAL;

    return __kvm_gmem_create(kvm, size, flags);
}
```

**内部实现** `__kvm_gmem_create()` (guest_memfd.c:559-626):

```c
static int __kvm_gmem_create(struct kvm *kvm, loff_t size, u64 flags)
{
    // 1. 获取未使用的 fd
    fd = get_unused_fd_flags(0);
    if (fd < 0)
        return fd;

    // 2. 分配 gmem_file 结构
    f = kzalloc_obj(*f);
    if (!f) {
        err = -ENOMEM;
        goto err_fd;
    }

    // 3. 创建匿名 inode
    inode = anon_inode_make_secure_inode(kvm_gmem_mnt->mnt_sb, name, NULL);
    if (IS_ERR(inode)) {
        err = PTR_ERR(inode);
        goto err_fops;
    }

    // 4. 初始化 inode
    inode->i_op = &kvm_gmem_iops;
    inode->i_mapping->a_ops = &kvm_gmem_aops;
    inode->i_size = size;
    mapping_set_gfp_mask(inode->i_mapping, GFP_HIGHUSER);
    mapping_set_inaccessible(inode->i_mapping);

    GMEM_I(inode)->flags = flags;

    // 5. 创建文件描述符
    file = alloc_file_pseudo(inode, kvm_gmem_mnt, name, O_RDWR, &kvm_gmem_fops);
    file->f_flags |= O_LARGEFILE;
    file->private_data = f;

    kvm_get_kvm(kvm);
    f->kvm = kvm;
    xa_init(&f->bindings);
    list_add(&f->entry, &inode->i_mapping->i_private_list);

    fd_install(fd, file);
    return fd;
}
```

### 3.4 kvm_gmem_bind()

**位置**: `virt/kvm/guest_memfd.c:642-704`

```c
int kvm_gmem_bind(struct kvm *kvm, struct kvm_memory_slot *slot,
                  unsigned int fd, loff_t offset)
{
    loff_t size = slot->npages << PAGE_SHIFT;
    unsigned long start, end;
    struct gmem_file *f;
    struct inode *inode;
    struct file *file;
    int r = -EINVAL;

    file = fget(fd);
    if (!file)
        return -EBADF;

    if (file->f_op != &kvm_gmem_fops)
        goto err;

    f = file->private_data;
    if (f->kvm != kvm)
        goto err;

    inode = file_inode(file);

    // 验证偏移和大小
    if (offset < 0 || !PAGE_ALIGNED(offset) ||
        offset + size > i_size_read(inode))
        goto err;

    filemap_invalidate_lock(inode->i_mapping);

    start = offset >> PAGE_SHIFT;
    end = start + slot->npages;

    // 检查绑定冲突
    if (!xa_empty(&f->bindings) &&
        xa_find(&f->bindings, &start, end - 1, XA_PRESENT)) {
        filemap_invalidate_unlock(inode->i_mapping);
        goto err;
    }

    // 执行绑定
    WRITE_ONCE(slot->gmem.file, file);
    slot->gmem.pgoff = start;
    if (kvm_gmem_supports_mmap(inode))
        slot->flags |= KVM_MEMSLOT_GMEM_ONLY;

    xa_store_range(&f->bindings, start, end - 1, slot, GFP_KERNEL);
    filemap_invalidate_unlock(inode->i_mapping);

    r = 0;
err:
    fput(file);
    return r;
}
```

### 3.5 kvm_gmem_get_pfn()

**位置**: `virt/kvm/guest_memfd.c:788-819`

```c
int kvm_gmem_get_pfn(struct kvm *kvm, struct kvm_memory_slot *slot,
                     gfn_t gfn, kvm_pfn_t *pfn, struct page **page,
                     int *max_order)
{
    pgoff_t index = kvm_gmem_get_index(slot, gfn);
    struct folio *folio;
    int r = 0;

    CLASS(gmem_get_file, file)(slot);
    if (!file)
        return -EFAULT;

    folio = __kvm_gmem_get_pfn(file, slot, index, pfn, max_order);
    if (IS_ERR(folio))
        return PTR_ERR(folio);

    if (!folio_test_uptodate(folio)) {
        clear_highpage(folio_page(folio, 0));
        folio_mark_uptodate(folio);
    }

    r = kvm_gmem_prepare_folio(kvm, slot, gfn, folio);

    folio_unlock(folio);

    if (!r)
        *page = folio_file_page(folio, index);
    else
        folio_put(folio);

    return r;
}
```

### 3.6 Notifier 机制

**位置**: `guest_memfd.c:160-228`

```c
static void __kvm_gmem_invalidate_begin(struct gmem_file *f, pgoff_t start,
                                        pgoff_t end,
                                        enum kvm_gfn_range_filter attr_filter)
{
    bool flush = false, found_memslot = false;
    struct kvm_memory_slot *slot;
    struct kvm *kvm = f->kvm;
    unsigned long index;

    xa_for_each_range(&f->bindings, index, slot, start, end - 1) {
        pgoff_t pgoff = slot->gmem.pgoff;

        struct kvm_gfn_range gfn_range = {
            .start = slot->base_gfn + max(pgoff, start) - pgoff,
            .end = slot->base_gfn + min(pgoff + slot->npages, end) - pgoff,
            .slot = slot,
            .may_block = true,
            .attr_filter = attr_filter,
        };

        if (!found_memslot) {
            found_memslot = true;
            KVM_MMU_LOCK(kvm);
            kvm_mmu_invalidate_begin(kvm);
        }

        flush |= kvm_mmu_unmap_gfn_range(kvm, &gfn_range);
    }

    if (flush)
        kvm_flush_remote_tlbs(kvm);

    if (found_memslot)
        KVM_MMU_UNLOCK(kvm);
}
```

---

## 4. Memory Slot

### 4.1 概述

Memory Slot 是 KVM 管理虚拟机物理内存的核心数据结构，每个 slot 代表一段连续的 GPA 空间。

**源码位置**: `virt/kvm/kvm_main.c`, `include/linux/kvm_host.h`

### 4.2 结构定义

#### struct kvm_memory_slot

```c
// include/linux/kvm_host.h:592-616
struct kvm_memory_slot {
    struct hlist_node id_node[2];         // 用于 id_hash 链表 (双链表用于 RCU)
    struct interval_tree_node hva_node[2];  // 用于 HVA 区间树
    struct rb_node gfn_node[2];           // 用于 GFN 红黑树 (双链表用于 RCU)
    gfn_t base_gfn;                      // 起始 GFN (Guest Frame Number)
    unsigned long npages;                // 页数
    unsigned long *dirty_bitmap;         // 脏页位图 (双位图结构)
    struct kvm_arch_memory_slot arch;    // 架构特定数据
    unsigned long userspace_addr;         // 用户空间 HVA (Host Virtual Address)
    u32 flags;                           // KVM_MEM_* 标志 (如 KVM_MEM_LOG_DIRTY_PAGES)
    short id;                            // slot ID
    u16 as_id;                           // 地址空间 ID

#ifdef CONFIG_KVM_GUEST_MEMFD
    struct {
        /*
         * 由 kvm->slots_lock 保护
         */
        struct file *file;               // guest_memfd 文件
        pgoff_t pgoff;                  // 在文件中的页偏移
    } gmem;
#endif
};
```

**主要字段说明**:
- `id_node`: 用于通过 slot ID 快速查找 (id_hash 哈希表)
- `hva_node`: 用于通过用户空间虚拟地址区间查找 (interval_tree)
- `gfn_node`: 用于通过 GFN 区间查找 (rb_tree，红黑树)
- `dirty_bitmap`: 传统 dirty logging 使用的位图 (双位图用于手动保护模式)
- `gmem`: guest_memfd 绑定信息

**辅助函数** (kvm_host.h:618-638):

```c
static inline bool kvm_slot_has_gmem(const struct kvm_memory_slot *slot)
{
    return slot && (slot->flags & KVM_MEM_GUEST_MEMFD);
}

static inline bool kvm_slot_dirty_track_enabled(const struct kvm_memory_slot *slot)
{
    return slot->flags & KVM_MEM_LOG_DIRTY_PAGES;
}

static inline unsigned long kvm_dirty_bitmap_bytes(struct kvm_memory_slot *memslot)
{
    return ALIGN(memslot->npages, BITS_PER_LONG) / 8;
}
```

### 4.3 struct kvm (VM 主结构)

```c
// include/linux/kvm_host.h:769-878
struct kvm {
    // MMU 锁
#ifdef KVM_HAVE_MMU_RWLOCK
    rwlock_t mmu_lock;
#else
    spinlock_t mmu_lock;
#endif

    struct mutex slots_lock;         // 内存槽操作锁
    struct mutex slots_arch_lock;    // 架构特定槽锁
    struct mm_struct *mm;            // 用户空间 mm_struct
    unsigned long nr_memslot_pages;  // 所有 slot 的总页数

    /* 两个 memslot 集合 - 活跃和非活跃（每个地址空间）*/
    struct kvm_memslots __memslots[KVM_MAX_NR_ADDRESS_SPACES][2];
    struct kvm_memslots __rcu *memslots[KVM_MAX_NR_ADDRESS_SPACES];

    struct xarray vcpu_array;       // vCPU 数组
    atomic_t nr_memslots_dirty_logging;  // 正在 dirty logging 的 slot 数

    /* MMU notifier 相关 */
    spinlock_t mn_invalidate_lock;
    unsigned long mn_active_invalidate_count;
    struct rcuwait mn_memslots_update_rcuwait;

    /* PFN cache 管理 */
    spinlock_t gpc_lock;
    struct list_head gpc_list;

    /* ... 其他字段 ... */
    u32 dirty_ring_size;             // dirty ring 大小
    bool dirty_ring_with_bitmap;     // 是否同时使用 ring 和 bitmap
};
```

### 4.4 kvm_set_memory_region()

**位置**: `virt/kvm/kvm_main.c:2001-2132`

```c
static int kvm_set_memory_region(struct kvm *kvm,
                                 const struct kvm_userspace_memory_region2 *mem)
{
    struct kvm_memory_slot *old, *new;
    struct kvm_memslots *slots;
    enum kvm_mr_change change;
    unsigned long npages;
    gfn_t base_gfn;
    int as_id, id;
    int r;

    lockdep_assert_held(&kvm->slots_lock);

    r = check_memory_region_flags(kvm, mem);
    if (r)
        return r;

    as_id = mem->slot >> 16;       // 高16位是地址空间ID
    id = (u16)mem->slot;            // 低16位是slot ID

    // 基本合法性检查
    if ((mem->memory_size & (PAGE_SIZE - 1)) ||
        (mem->memory_size != (unsigned long)mem->memory_size))
        return -EINVAL;
    if (mem->guest_phys_addr & (PAGE_SIZE - 1))
        return -EINVAL;
    if ((mem->userspace_addr & (PAGE_SIZE - 1)) ||
        (mem->userspace_addr != untagged_addr(mem->userspace_addr)) ||
        !access_ok((void __user *)(unsigned long)mem->userspace_addr,
            mem->memory_size))
        return -EINVAL;

    // guest_memfd 相关检查
    if (mem->flags & KVM_MEM_GUEST_MEMFD &&
        (mem->guest_memfd_offset & (PAGE_SIZE - 1) ||
         mem->guest_memfd_offset + mem->memory_size < mem->guest_memfd_offset))
        return -EINVAL;

    slots = __kvm_memslots(kvm, as_id);
    old = id_to_memslot(slots, id);

    if (!mem->memory_size) {
        // 删除 slot
        if (!old || !old->npages)
            return -EINVAL;
        return kvm_set_memslot(kvm, old, NULL, KVM_MR_DELETE);
    }

    base_gfn = (mem->guest_phys_addr >> PAGE_SHIFT);
    npages = (mem->memory_size >> PAGE_SHIFT);

    if (!old || !old->npages) {
        change = KVM_MR_CREATE;
    } else {
        // 修改现有 slot
        if (mem->flags & KVM_MEM_GUEST_MEMFD)
            return -EINVAL;  // private memslot 不可修改
        if ((mem->userspace_addr != old->userspace_addr) ||
            (npages != old->npages) ||
            ((mem->flags ^ old->flags) & (KVM_MEM_READONLY | KVM_MEM_GUEST_MEMFD)))
            return -EINVAL;

        if (base_gfn != old->base_gfn)
            change = KVM_MR_MOVE;
        else if (mem->flags != old->flags)
            change = KVM_MR_FLAGS_ONLY;
        else
            return 0;  // 无变化
    }

    // 检查与其他 slot 的重叠
    if ((change == KVM_MR_CREATE || change == KVM_MR_MOVE) &&
        kvm_check_memslot_overlap(slots, id, base_gfn, base_gfn + npages))
        return -EEXIST;

    // 分配新的 slot 结构
    new = kzalloc_obj(*new, GFP_KERNEL_ACCOUNT);
    if (!new)
        return -ENOMEM;

    new->as_id = as_id;
    new->id = id;
    new->base_gfn = base_gfn;
    new->npages = npages;
    new->flags = mem->flags;
    new->userspace_addr = mem->userspace_addr;

    // 如果是 guest_memfd，绑定到文件
    if (mem->flags & KVM_MEM_GUEST_MEMFD) {
        r = kvm_gmem_bind(kvm, new, mem->guest_memfd, mem->guest_memfd_offset);
        if (r)
            goto out;
    }

    r = kvm_set_memslot(kvm, old, new, change);
    if (r)
        goto out_unbind;

    return 0;

out_unbind:
    if (mem->flags & KVM_MEM_GUEST_MEMFD)
        kvm_gmem_unbind(new);
out:
    kfree(new);
    return r;
}
```

### 4.5 gfn_to_memslot()

**位置**: `virt/kvm/kvm_main.c:2635-2638`

```c
struct kvm_memory_slot *gfn_to_memslot(struct kvm *kvm, gfn_t gfn)
{
    return __gfn_to_memslot(kvm_memslots(kvm), gfn);
}
```

这是一个关键的性能优化点，使用路径：
1. 从当前活跃的 memslots 中查找
2. 使用 `__gfn_to_memslot` 通过 GFN 红黑树进行 O(log n) 查找
3. vCPU 有缓存 (`last_used_slot`) 进一步优化热点访问

### 4.6 kvm_alloc_dirty_bitmap()

**位置**: `virt/kvm/kvm_main.c:1428-1437`

```c
static int kvm_alloc_dirty_bitmap(struct kvm_memory_slot *memslot)
{
    unsigned long dirty_bytes = kvm_dirty_bitmap_bytes(memslot);

    /* 大小是实际位图的两倍，用于支持手动保护模式 */
    memslot->dirty_bitmap = __vcalloc(2, dirty_bytes, GFP_KERNEL_ACCOUNT);
    if (!memslot->dirty_bitmap)
        return -ENOMEM;

    return 0;
}
```

---

## 5. 内存分配流程

### 5.1 kvm_create_vm() - VM 创建

**位置**: `virt/kvm/kvm_main.c:1105-1238`

```c
static struct kvm *kvm_create_vm(unsigned long type, const char *fdname)
{
    struct kvm *kvm = kvm_arch_alloc_vm();  // 分配 VM 结构
    struct kvm_memslots *slots;
    int r, i, j;

    if (!kvm)
        return ERR_PTR(-ENOMEM);

    /* 初始化锁 */
    KVM_MMU_LOCK_INIT(kvm);
    mmgrab(current->mm);
    kvm->mm = current->mm;
    kvm_eventfd_init(kvm);
    mutex_init(&kvm->lock);
    mutex_init(&kvm->irq_lock);
    mutex_init(&kvm->slots_lock);
    mutex_init(&kvm->slots_arch_lock);
    spin_lock_init(&kvm->mn_invalidate_lock);
    rcuwait_init(&kvm->mn_memslots_update_rcuwait);
    xa_init(&kvm->vcpu_array);

#ifdef CONFIG_KVM_GENERIC_MEMORY_ATTRIBUTES
    xa_init(&kvm->mem_attr_array);
#endif

    /* 初始化 PFN cache 列表 (gfn_to_pfn_cache) */
    INIT_LIST_HEAD(&kvm->gpc_list);
    spin_lock_init(&kvm->gpc_lock);

    /* 初始化设备链表 */
    INIT_LIST_HEAD(&kvm->devices);
    kvm->max_vcpus = KVM_MAX_VCPUS;

    /* 初始化 memslots (双重缓冲 - 活跃/非活跃) */
    for (i = 0; i < kvm_arch_nr_memslot_as_ids(kvm); i++) {
        for (j = 0; j < 2; j++) {
            slots = &kvm->__memslots[i][j];

            atomic_long_set(&slots->last_used_slot, (unsigned long)NULL);
            slots->hva_tree = RB_ROOT_CACHED;    // HVA 区间树
            slots->gfn_tree = RB_ROOT;            // GFN 红黑树
            hash_init(slots->id_hash);            // ID 哈希表
            slots->node_idx = j;
            slots->generation = i;  // 每个地址空间 generation 不同
        }
        rcu_assign_pointer(kvm->memslots[i], &kvm->__memslots[i][0]);
    }

    /* 分配 IO 总线 (PCI, IO, MMIO) */
    for (i = 0; i < KVM_NR_BUSES; i++) {
        rcu_assign_pointer(kvm->buses[i],
            kzalloc_obj(struct kvm_io_bus, GFP_KERNEL_ACCOUNT));
        if (!kvm->buses[i])
            goto out_err_no_arch_destroy_vm;
    }

    /* 架构特定初始化 (x86, ARM, RISC-V 等) */
    r = kvm_arch_init_vm(kvm, type);
    if (r)
        goto out_err_no_arch_destroy_vm;

    r = kvm_enable_virtualization();  // 启用虚拟化 (VMX/SVM)
    if (r)
        goto out_err_no_disable;

#ifdef CONFIG_HAVE_KVM_IRQCHIP
    INIT_HLIST_HEAD(&kvm->irq_ack_notifier_list);
#endif

    /* 初始化 MMU notifier (页面回收/迁移通知) */
    r = kvm_init_mmu_notifier(kvm);
    if (r)
        goto out_err_no_mmu_notifier;

    /* 初始化合并 MMIO ring */
    r = kvm_coalesced_mmio_init(kvm);
    if (r < 0)
        goto out_no_coalesced_mmio;

    /* 创建 debugfs 目录 */
    r = kvm_create_vm_debugfs(kvm, fdname);
    if (r)
        goto out_err_no_debugfs;

    /* 添加到全局 VM 列表 */
    mutex_lock(&kvm_lock);
    list_add(&kvm->vm_list, &vm_list);
    mutex_unlock(&kvm_lock);

    preempt_notifier_inc();
    kvm_init_pm_notifier(kvm);

    return kvm;

// 错误处理路径 (跳转到对应 out_xxx 标签)...
}
```

**VM 创建流程图**:

```
kvm_create_vm()
    │
    ├── kvm_arch_alloc_vm()              # 分配架构特定 VM 结构
    │
    ├── 初始化基本结构
    │   ├── KVM_MMU_LOCK_INIT(kvm)
    │   ├── kvm->mm = current->mm
    │   ├── mutex_init(&kvm->slots_lock)
    │   └── xa_init(&kvm->vcpu_array)
    │
    ├── 初始化 PFN cache 列表
    │   ├── INIT_LIST_HEAD(&kvm->gpc_list)
    │   └── spin_lock_init(&kvm->gpc_lock)
    │
    ├── 初始化 memslots (双重缓冲)
    │   └── for each address_space:
    │       ├── __memslots[i][0] (active)
    │       └── __memslots[i][1] (inactive)
    │
    ├── 分配 IO buses (KVM_NR_BUSES=3)
    │
    ├── kvm_arch_init_vm()                # 架构特定 VM 初始化
    │
    ├── kvm_enable_virtualization()      # 启用虚拟化 (VMX/SVM/SME)
    │
    ├── kvm_init_mmu_notifier()          # 初始化 MMU notifier
    │
    ├── kvm_coalesced_mmio_init()        # 初始化合并 MMIO
    │
    ├── kvm_create_vm_debugfs()          # 创建 debugfs 条目
    │
    └── list_add(&kvm->vm_list)          # 添加到全局 VM 列表
```

### 5.2 kvm_destroy_vm() - VM 销毁

**位置**: `virt/kvm/kvm_main.c:1261-1317`

```c
static void kvm_destroy_vm(struct kvm *kvm)
{
    int i;
    struct mm_struct *mm = kvm->mm;

    kvm_destroy_pm_notifier(kvm);
    kvm_uevent_notify_change(KVM_EVENT_DESTROY_VM, kvm);
    kvm_destroy_vm_debugfs(kvm);

    /* 从全局列表移除 */
    mutex_lock(&kvm_lock);
    list_del(&kvm->vm_list);
    mutex_unlock(&kvm_lock);

    kvm_arch_pre_destroy_vm(kvm);

    /* 释放中断路由 */
    kvm_free_irq_routing(kvm);

    /* 释放 IO buses */
    for (i = 0; i < KVM_NR_BUSES; i++) {
        struct kvm_io_bus *bus = kvm_get_bus_for_destruction(kvm, i);
        if (bus)
            kvm_io_bus_destroy(bus);
        kvm->buses[i] = NULL;
    }

    kvm_coalesced_mmio_free(kvm);

    /* 注销 MMU notifier */
    mmu_notifier_unregister(&kvm->mmu_notifier, kvm->mm);

    /*
     * 处理 pending invalidation:
     * - mn_active_invalidate_count 非零表示有待处理的 invalidation
     * - 如果为零但 mmu_invalidate_in_progress 非零则发出警告
     */
    WARN_ON(rcuwait_active(&kvm->mn_memslots_update_rcuwait));
    if (kvm->mn_active_invalidate_count)
        kvm->mn_active_invalidate_count = 0;
    else
        WARN_ON(kvm->mmu_invalidate_in_progress);

    /* 架构特定销毁 */
    kvm_arch_destroy_vm(kvm);

    /* 销毁设备 */
    kvm_destroy_devices(kvm);

    /* 释放所有 memslots (活跃和非活跃集合) */
    for (i = 0; i < kvm_arch_nr_memslot_as_ids(kvm); i++) {
        kvm_free_memslots(kvm, &kvm->__memslots[i][0]);
        kvm_free_memslots(kvm, &kvm->__memslots[i][1]);
    }

    /* 清理 SRCU */
    cleanup_srcu_struct(&kvm->irq_srcu);
    srcu_barrier(&kvm->srcu);
    cleanup_srcu_struct(&kvm->srcu);

    /* 释放属性数组 */
#ifdef CONFIG_KVM_GENERIC_MEMORY_ATTRIBUTES
    xa_destroy(&kvm->mem_attr_array);
#endif

    kvm_arch_free_vm(kvm);
    preempt_notifier_dec();
    kvm_disable_virtualization();
    mmdrop(mm);
}
```

### 5.3 kvm_free_memslot()

**位置**: `virt/kvm/kvm_main.c:945-955`

```c
static void kvm_free_memslot(struct kvm *kvm, struct kvm_memory_slot *slot)
{
    /* 如果是 guest_memfd，先解除绑定 */
    if (slot->flags & KVM_MEM_GUEST_MEMFD)
        kvm_gmem_unbind(slot);

    /* 释放 dirty bitmap */
    kvm_destroy_dirty_bitmap(slot);

    /* 释放架构特定数据 */
    kvm_arch_free_memslot(kvm, slot);

    kfree(slot);
}

/* 释放 dirty bitmap (kvm_main.c:935-942) */
static void kvm_destroy_dirty_bitmap(struct kvm_memory_slot *memslot)
{
    if (!memslot->dirty_bitmap)
        return;

    vfree(memslot->dirty_bitmap);
    memslot->dirty_bitmap = NULL;
}
```

### 5.4 kvm_alloc_dirty_bitmap()

**位置**: `virt/kvm/kvm_main.c:1428-1437`

```c
static int kvm_alloc_dirty_bitmap(struct kvm_memory_slot *memslot)
{
    unsigned long dirty_bytes = kvm_dirty_bitmap_bytes(memslot);

    /* 大小是实际位图的两倍，用于支持手动保护模式 */
    memslot->dirty_bitmap = __vcalloc(2, dirty_bytes, GFP_KERNEL_ACCOUNT);
    if (!memslot->dirty_bitmap)
        return -ENOMEM;

    return 0;
}
```

---

## 6. 架构图

### 6.1 KVM 内存管理整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户空间 (Userspace)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   QEMU / CRIU   │  │   脏页采集线程   │  │  内存管理工具   │    │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
└───────────┼───────────────────┼───────────────────┼───────────────┘
            │                   │                   │
            │ ioctl/KVM_SET_    │ KVM_GET_DIRTY_    │ KVM_CREATE_
            │   MEMORY_REGION   │   RING            │   GUEST_MEMFD
            ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         KVM 内核模块                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    kvm_main.c                                │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐     │   │
│  │  │ kvm_create_vm│  │kvm_set_memory │  │ gfn_to_memslot│     │   │
│  │  │ kvm_destroy_vm│ │_region        │  │               │     │   │
│  │  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘     │   │
│  │          │                  │                  │             │   │
│  │  ┌───────┴──────────────────┴──────────────────┴───────┐     │   │
│  │  │              struct kvm_memory_slot                 │     │   │
│  │  │  base_gfn, npages, dirty_bitmap, gmem.file, ...     │     │   │
│  │  └─────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  dirty_ring.c   │  │  pfncache.c     │  │  guest_memfd.c  │   │
│  │                 │  │                 │  │                 │   │
│  │ kvm_dirty_ring  │  │ gfn_to_pfn_cache│  │ kvm_guest_memfd │   │
│  │  .dirty_index   │  │  .generation   │  │  .gmem_file     │   │
│  │  .reset_index   │  │  .pfn, .khva   │  │  .bindings     │   │
│  │  .dirty_gfns[]  │  │  .active,valid │  │                 │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │
└───────────┼─────────────────────┼───────────────────┼────────────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      底层内核机制                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   MMU Notifier  │  │   get_user_pages │  │   匿名 inode    │   │
│  │                 │  │   _fast (GUP)    │  │   (anon_inode)  │   │
│  │ invalidate_     │  │                 │  │                 │   │
│  │  range_start/   │  │ hva_to_pfn()    │  │ kvm_gmem_mnt    │   │
│  │  end            │  │                 │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        物理内存层                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   主机物理内存   │  │   Page Frame    │  │   Memfd 存储    │   │
│  │   (RAM)         │  │   Number (PFN)  │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Dirty Ring 工作流程

```
VCPU 执行 guest 写入                          用户空间采集
       │                                            │
       ▼                                            │
┌──────────────────┐                                │
│ 写入 guest 物理  │                                │
│     内存         │                                │
└────────┬─────────┘                                │
         │                                         │
         ▼                                         │
┌──────────────────┐     触发                 ┌──────────────────┐
│ KVM MMU 追踪     │──────────────────────────▶│ 检测 soft_limit  │
│ (标记 dirty)     │     KVM_REQ_              │ 达到，软限制触发  │
└────────┬─────────┘     DIRTY_RING_            └────────┬─────────┘
         │              SOFT_FULL                      │
         ▼                                             ▼
┌──────────────────┐                          ┌──────────────────┐
│ kvm_dirty_ring   │     VCPU 退出            │ VCPU 返回用户空间 │
│ _push()          │─────────────────────────▶│                  │
│                  │                          └────────┬─────────┘
│ [slot, offset]   │                                   │
│ 写入 dirty_gfns  │                                   │
└────────┬─────────┘                                   │
         │                                             │
         │◀──────────────────────────────────────────┘
         │            kvm_dirty_ring_reset()
         │                    │
         ▼                    ▼
┌──────────────────┐   ┌──────────────────┐
│ reset_index++    │   │ kvm_reset_dirty_ │
│                  │   │ gfn() 批量重置    │
│ bitmap[offset]   │   │ MMU 重新追踪      │
│ = 0              │   │                   │
└──────────────────┘   └──────────────────┘
```

### 6.3 Guest Memfd 架构

```
用户空间 (QEMU)                        KVM 内核                          物理层
   │                                  │                               │
   │ KVM_CREATE_GUEST_MEMFD         │                               │
   │ ─────────────────────────────────▶                               │
   │                                  │ anon_inode_make_secure_inode()│
   │                                  │ ─────────────────────────────▶│
   │                                  │        创建伪文件系统 inode    │
   │◀─────────────────────────────────│                               │
   │   返回 fd                        │                               │
   │                                  │                               │
   │ KVM_SET_MEMORY_REGION            │                               │
   │ (KVM_MEM_GUEST_MEMFD)           │                               │
   │ ─────────────────────────────────▶                               │
   │                                  │ kvm_gmem_bind()               │
   │                                  │  - 验证 fd                    │
   │                                  │  - xa_store(bindings)         │
   │                                  │  - 设置 slot->gmem.file       │
   │                                  │                               │
   │                                  │                               │
   │ VCPU 访问 guest 内存              │                               │
   │ ─────────────────────────────────▶                               │
   │                                  │ kvm_mmu_fault()               │
   │                                  │  │                            │
   │                                  │  ▼                            │
   │                                  │ kvm_gmem_get_pfn()            │
   │                                  │  │                            │
   │                                  │  ▼                            │
   │                                  │ folio = kvm_gmem_get_folio()  │
   │                                  │  │                            │
   │                                  │  ▼                            │
   │                                  │ __filemap_get_folio()         │
   │                                  │  │                            │
   │                                  │  ▼                            │
   │                                  │      (如果需要) 分配 folio     │
   │                                  │◀──────────────────────────────│
   │                                  │                               │
   │                                  │ pfn = folio_file_pfn()       │
```

### 6.4 PFN Cache 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    GFN to PFN Cache 生命周期                    │
└─────────────────────────────────────────────────────────────────┘

1. 初始化                     2. 激活                       3. 首次使用
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ kvm_gpc_init()   │───▶│ kvm_gpc_activate │───▶│ kvm_gpc_refresh │
│                  │    │                  │    │                  │
│ - 初始化锁        │    │ - 添加到 gpc_list│    │ - 查找 memslot  │
│ - 设置初始值     │    │ - 设置 active    │    │ - 调用 hva_to_  │
│                  │    │                  │    │   pfn_retry()   │
└──────────────────┘    └──────────────────┘    │ - 获取 PFN      │
                                                └────────┬─────────┘
                                                         │
                                                         ▼
4. 缓存命中                  5. MMU Notifier            6. 再次刷新
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ kvm_gpc_check()  │    │ invalidate_start │───▶│ kvm_gpc_refresh │
│                  │    │                  │    │                  │
│ - 检查 generation│    │ - 设置 valid=flase│    │ - 重新查找 PFN  │
│ - 检查 valid     │    │ - 清除缓存       │    │ - 更新 khva/pfn │
│ - 返回 pfn       │◀───┤                  │    │ - 设置 valid=1  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### 6.5 Memory Slot 查找优化

```
gfn_to_memslot(gfn)
      │
      ▼
┌──────────────────┐
│ 检查 vCPU 本地缓存│
│ last_used_slot   │
└────────┬─────────┘
         │ 命中
         ▼
┌──────────────────┐
│ try_get_memslot()│
│ 返回缓存的 slot  │
└────────┬─────────┘
         │ 未命中
         ▼
┌──────────────────┐
│ search_memslots()│
│ (O(log n) 红黑树)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 更新 last_used_slot│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 返回 slot        │
└──────────────────┘
```

### 6.6 双 Mem slot 集合 (RCU 优化)

```
┌──────────────────────────────────────────────────────────────┐
│                    Mem slot 双重缓冲                          │
└──────────────────────────────────────────────────────────────┘

kvm->memslots[i] ──────▶  ┌─────────────────┐    ┌─────────────────┐
       (RCU 指针)         │  __memslots[i][0]│    │  __memslots[i][1]│
                         │    (active)      │    │   (inactive)     │
                         └────────┬─────────┘    └────────┬─────────┘
                                  │                       │
                                  │                       │
                           ┌──────┴───────┐        ┌──────┴───────┐
                           │ hva_tree      │        │ hva_tree      │
                           │ gfn_tree      │        │ gfn_tree      │
                           │ id_hash       │        │ id_hash       │
                           └───────────────┘        └───────────────┘

用户空间修改时:
1. 修改 __memslots[i][1] (inactive)
2. 调用 kvm_set_memslot() 完成修改
3. rcu_assign_pointer() 切换指针
4. 调用 rcu_barrier() 等待旧引用释放
5. 交换 active/inactive 角色
```

---

## 总结

KVM 的内存管理是一个复杂而精密的系统，包含以下核心组件：

1. **Dirty Ring**: 高效的脏页追踪机制，通过环形缓冲区和批处理优化减少锁竞争
2. **PFN Cache**: GFN 到 PFN 转换结果的缓存，减少重复页表查找
3. **Guest Memfd**: 基于匿名内存的 guest 内存管理，支持 NUMA 策略和 mmap
4. **Memory Slot**: 虚拟机物理内存的核心抽象，支持多种后端类型
5. **MMU Notifier**: 与 Linux 内存管理子系统交互的桥梁，处理页面迁移和回收

这些组件协同工作，为 KVM 虚拟机提供了高效、可靠的内存管理能力。

### 关键设计模式

| 设计模式 | 应用场景 | 优势 |
|----------|---------|------|
| Per-VCPU Ring | Dirty Ring | 减少锁竞争 |
| 双重缓冲 | Memory Slots | RCU 无锁切换 |
| 缓存 | PFN Cache | 减少页表查找 |
| 批处理 | Dirty Ring Reset | 合并操作，减少 MMU lock |
| 区间树 | Slot HVA 查找 | O(log n) 查找 |

### 安全性考虑

- **MMU Notifier**: 确保页面回收/迁移时缓存失效
- **slots_lock**: 保护 memslot 操作
- **refcount**: KVM 引用计数管理生命周期
- **gmem bindings**: xarray 确保原子性绑定

---

**文档信息**

- 分析版本: Linux Kernel (基于 master 分支)
- 分析日期: 2026-04-26
- 源码路径: `/Users/sphinx/github/linux/virt/kvm/`
