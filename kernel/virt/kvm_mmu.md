# Linux Kernel KVM MMU 虚拟化机制分析文档

## 目录

1. [概述](#1-概述)
2. [嵌套页表 (NPT/EPT)](#2-嵌套页表-nptept)
3. [TDP MMU (Two-Dimensional Paging)](#3-tdp-mmu-two-dimensional-paging)
4. [影子页表](#4-影子页表)
5. [脏页追踪](#5-脏页追踪)
6. [内存Slot管理](#6-内存slot管理)
7. [关键数据结构](#7-关键数据结构)
8. [页表层次结构图](#8-页表层次结构图)

---

## 1. 概述

KVM (Kernel-based Virtual Machine) 是 Linux 内核中的全虚拟化解决方案，其 MMU (Memory Management Unit) 虚拟化机制是核心组件之一。KVM MMU 负责将虚拟机的虚拟地址 (GVA) 转换为物理地址 (GPA)，再转换为宿主机的物理地址 (HPA)。

### 1.1 核心源码位置

| 文件 | 描述 |
|------|------|
| `/arch/x86/kvm/mmu/mmu.c` | MMU 主实现 (~230KB) |
| `/arch/x86/kvm/mmu/tdp_mmu.c` | TDP MMU 实现 (~61KB) |
| `/arch/x86/kvm/mmu/spte.[c,h]` | Shadow PTE 管理和操作 |
| `/arch/x86/kvm/mmu/paging_tmpl.h` | 页表遍历模板 (guest walker) |
| `/arch/x86/kvm/mmu/mmu_internal.h` | MMU 内部结构和函数 |
| `/arch/x86/kvm/mmu/tdp_iter.[c,h]` | TDP 页表迭代器 |

### 1.2 两种虚拟化模式

KVM 支持两种 MMU 虚拟化模式:

1. **传统影子页表 (Shadow Paging)**: KVM 软件模拟完整的页表转换
2. **嵌套页表 (TDP/EPT/NPT)**: 硬件辅助的二维页表转换

---

## 2. 嵌套页表 (NPT/EPT)

### 2.1 基本概念

- **EPT (Extended Page Table)**: Intel 硬件支持
- **NPT (Nested Page Table)**: AMD 硬件支持
- **TDP (Two-Dimensional Paging)**: 通用术语，指两层页表结构

```
传统影子页表:
  GVA → [软件遍历] → GPA → [软件遍历] → HPA

TDP (EPT/NPT):
  GVA → [硬件 L1 页表] → GPA → [硬件 L2 页表 (EPT/NPT)] → HPA
```

### 2.2 页表结构 (x86-64)

```
+-----------------+
|     PML4        |  (Page Map Level 4) - 4KB, 512 entries
+-----------------+
        |
        v
+-----------------+
|     PDPT        |  (Page Directory Pointer Table) - 4KB, 512 entries
+-----------------+
        |
        v
+-----------------+
|      PD         |  (Page Directory) - 4KB, 512 entries
+-----------------+
        |
        v
+-----------------+
|      PT         |  (Page Table) - 4KB, 512 entries
+-----------------+
        |
        v
     4KB Page
```

### 2.3 核心常量定义

**文件**: `/arch/x86/include/asm/kvm_host.h` (行 154-161)

```c
#define KVM_MAX_HUGEPAGE_LEVEL    PG_LEVEL_1G      // 最大大页级别
#define KVM_NR_PAGE_SIZES         (KVM_MAX_HUGEPAGE_LEVEL - PG_LEVEL_4K + 1)
#define KVM_HPAGE_GFN_SHIFT(x)    (((x) - 1) * 9)  // 每级9位索引
#define KVM_HPAGE_SHIFT(x)        (PAGE_SHIFT + KVM_HPAGE_GFN_SHIFT(x))
#define KVM_PAGES_PER_HPAGE(x)    (KVM_HPAGE_SIZE(x) / PAGE_SIZE)
```

**文件**: `/arch/x86/include/asm/pgtable_types.h` (行 544-552)

```c
enum pg_level {
    PG_LEVEL_NONE,
    PG_LEVEL_4K,    // 4KB 页
    PG_LEVEL_2M,    // 2MB 大页
    PG_LEVEL_1G,    // 1GB 大页
    PG_LEVEL_512G,
    PG_LEVEL_256T,
    PG_LEVEL_NUM
};
```

### 2.4 EPT/NPT 页表位定义

**文件**: `/arch/x86/kvm/mmu/spte.h` (行 11-61)

```c
// SPTE (Shadow Page Table Entry) 相关定义
#define SPTE_MMU_PRESENT_MASK     BIT_ULL(11)    // MMU 存在位

// A/D 位跟踪类型 (用于 TDP)
#define SPTE_TDP_AD_SHIFT         52
#define SPTE_TDP_AD_MASK          (3ULL << SPTE_TDP_AD_SHIFT)
#define SPTE_TDP_AD_ENABLED       (0ULL << SPTE_TDP_AD_SHIFT)
#define SPTE_TDP_AD_DISABLED      (1ULL << SPTE_TDP_AD_SHIFT)
#define SPTE_TDP_AD_WRPROT_ONLY   (2ULL << SPTE_TDP_AD_SHIFT)

// EPT 可读/可执行位
#define SPTE_EPT_READABLE_MASK    0x1ull
#define SPTE_EPT_EXECUTABLE_MASK  0x4ull

// SPTE 级别操作
#define SPTE_LEVEL_BITS           9
#define SPTE_ENT_PER_PAGE         512  // 2^9 = 512 entries per page
```

---

## 3. TDP MMU (Two-Dimensional Paging)

### 3.1 TDP MMU 概述

TDP MMU 是 KVM 针对 EPT/NPT 硬件支持的优化实现，相比传统影子页表具有更好的性能和可扩展性。

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.h` (行 1-122)

```c
// TDP MMU 根类型
enum kvm_tdp_mmu_root_types {
    KVM_INVALID_ROOTS = BIT(0),
    KVM_DIRECT_ROOTS  = BIT(1),
    KVM_MIRROR_ROOTS  = BIT(2),   // TDX 使用
    KVM_VALID_ROOTS   = KVM_DIRECT_ROOTS | KVM_MIRROR_ROOTS,
    KVM_ALL_ROOTS     = KVM_VALID_ROOTS | KVM_INVALID_ROOTS,
};
```

### 3.2 初始化与销毁

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.c` (行 14-54)

```c
// 初始化 TDP MMU
void kvm_mmu_init_tdp_mmu(struct kvm *kvm)
{
    INIT_LIST_HEAD(&kvm->arch.tdp_mmu_roots);
    spin_lock_init(&kvm->arch.tdp_mmu_pages_lock);
}

// 卸载 TDP MMU
void kvm_mmu_uninit_tdp_mmu(struct kvm *kvm)
{
    // 使所有根失效并释放
    kvm_tdp_mmu_invalidate_roots(kvm, KVM_VALID_ROOTS);
    kvm_tdp_mmu_zap_invalidated_roots(kvm, false);
    rcu_barrier();  // 等待 RCU 回调完成
}
```

### 3.3 TDP MMU 根页分配

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.c` (行 253-321)

```c
void kvm_tdp_mmu_alloc_root(struct kvm_vcpu *vcpu, bool mirror)
{
    struct kvm_mmu *mmu = vcpu->arch.mmu;
    union kvm_mmu_page_role role = mmu->root_role;
    struct kvm_mmu_page *root;

    if (mirror)
        role.is_mirror = true;

    // 首先检查是否已存在根
    read_lock(&kvm->mmu_lock);
    for_each_valid_tdp_mmu_root_yield_safe(kvm, root, as_id) {
        if (root->role.word == role.word)
            goto out_read_unlock;
    }
    read_unlock(&kvm->mmu_lock);

    // 分配并初始化新根
    root = tdp_mmu_alloc_sp(vcpu);
    tdp_mmu_init_sp(root, NULL, 0, role);

    // 引用计数初始化为 2:
    // 1. vCPU 引用
    // 2. TDP MMU 自身引用 (直到失效才释放)
    refcount_set(&root->tdp_mmu_root_count, 2);
    list_add_rcu(&root->link, &kvm->arch.tdp_mmu_roots);

    if (mirror)
        mmu->mirror_root_hpa = __pa(root->spt);
    else
        mmu->root.hpa = __pa(root->spt);
}
```

### 3.4 TDP MMU 页映射 (核心函数)

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.c` (行 1263-1350)

```c
int kvm_tdp_mmu_map(struct kvm_vcpu *vcpu, struct kvm_page_fault *fault)
{
    struct kvm_mmu_page *root = tdp_mmu_get_root_for_fault(vcpu, fault);
    struct tdp_iter iter;
    struct kvm_mmu_page *sp;
    int ret = RET_PF_RETRY;

    kvm_mmu_hugepage_adjust(vcpu, fault);  // 调整大页目标级别
    trace_kvm_mmu_spte_requested(fault);

    rcu_read_lock();

    for_each_tdp_pte(iter, kvm, root, fault->gfn, fault->gfn + 1) {
        int r;

        // 处理 NX 大页缓解
        if (fault->nx_huge_page_workaround_enabled)
            disallowed_hugepage_adjust(fault, iter.old_spte, iter.level);

        // 如果 SPTE 被冻结,放弃并重试
        if (is_frozen_spte(iter.old_spte))
            goto retry;

        // 到达目标级别
        if (iter.level == fault->goal_level)
            goto map_target_level;

        // 如果存在子页表,继续向下遍历
        if (is_shadow_present_pte(iter.old_spte) && !is_large_pte(iter.old_spte))
            continue;

        // 分配新的子页表
        sp = tdp_mmu_alloc_sp(vcpu);
        tdp_mmu_init_child_sp(sp, &iter);

        if (is_shadow_present_pte(iter.old_spte)) {
            // 需要拆分大页
            r = tdp_mmu_split_huge_page(kvm, &iter, sp, true);
        } else {
            // 链接新页表
            r = tdp_mmu_link_sp(kvm, &iter, sp, true);
        }

        if (r) {
            tdp_mmu_free_sp(sp);
            goto retry;
        }

        // 跟踪可能的 NX 大页
        if (fault->huge_page_disallowed && fault->req_level >= iter.level) {
            spin_lock(&kvm->arch.tdp_mmu_pages_lock);
            if (sp->nx_huge_page_disallowed)
                track_possible_nx_huge_page(kvm, sp, KVM_TDP_MMU);
            spin_unlock(&kvm->arch.tdp_mmu_pages_lock);
        }
    }

map_target_level:
    ret = tdp_mmu_map_handle_target_level(vcpu, fault, &iter);

retry:
    rcu_read_unlock();
    return ret;
}
```

### 3.5 TDP 迭代器

TDP 迭代器用于遍历 TDP 页表结构,实现先序遍历 (pre-order traversal)。

**文件**: `/arch/x86/kvm/mmu/tdp_iter.h` (行 76-143)

```c
struct tdp_iter {
    gfn_t              next_last_level_gfn;  // 下一个最后级 GFN
    gfn_t              yielded_gfn;           // 上次让出时的 GFN
    tdp_ptep_t         pt_path[PT64_ROOT_MAX_LEVEL];  // 页表路径
    tdp_ptep_t         sptep;                 // 当前 SPTE 指针
    gfn_t              gfn;                   // 当前 GFN
    gfn_t              gfn_bits;              // GFN 掩码
    int                root_level;            // 根级别
    int                min_level;             // 最小级别
    int                level;                 // 当前级别
    int                as_id;                 // 地址空间 ID
    u64                old_spte;              // SPTE 快照
    bool               valid;                 // 是否有效
    bool               yielded;               // 是否让出过 CPU
};

// 遍历宏
#define for_each_tdp_pte(iter, kvm, root, start, end)           \
    for_each_tdp_pte_min_level(iter, kvm, root, PG_LEVEL_4K, start, end)
```

### 3.6 大页回收

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.c` (行 1868-1875)

```c
void kvm_tdp_mmu_recover_huge_pages(struct kvm *kvm,
                                    const struct kvm_memory_slot *slot)
{
    struct kvm_mmu_page *root;

    for_each_valid_tdp_mmu_root_yield_safe(kvm, root, slot->as_id)
        recover_huge_pages_range(kvm, root, slot);
}
```

---

## 4. 影子页表

### 4.1 影子页表概述

影子页表是 KVM 在不支持 EPT/NPT 的硬件上使用的软件模拟方案。当 guest 页表发生改变时,KVM 需要同步更新影子页表。

### 4.2 影子页表结构

**文件**: `/arch/x86/kvm/mmu/mmu_internal.h` (行 44-141)

```c
struct kvm_mmu_page {
    struct list_head   link;              // 全局页链表
    struct hlist_node  hash_link;         // 哈希链表

    bool               tdp_mmu_page;      // 是否 TDP MMU 页
    bool               unsync;            // 是否未同步
    u8                 mmu_valid_gen;     // MMU 有效世代号

    bool               nx_huge_page_disallowed;  // NX 大页禁用

    union kvm_mmu_page_role role;        // 页角色
    gfn_t              gfn;              // 关联的 GFN

    u64               *spt;              // 影子页表指针

    u64               *shadowed_translation;  // 被影子化的翻译结果

    union {
        int            root_count;        // 根引用计数 (影子)
        refcount_t     tdp_mmu_root_count;  // TDP MMU 根引用计数
    };

    bool               has_mapped_host_mmio;

    union {
        struct {
            unsigned int  unsync_children;  // 未同步子页数
            atomic_t      write_flooding_count;  // 写洪泛计数
        };
        void           *external_spt;     // 外部页表 (TDX)
    };

    struct kvm_rmap_head parent_ptes;     // 父页表指针
    DECLARE_BITMAP(unsync_child_bitmap, 512);
    struct list_head possible_nx_huge_page_link;
};
```

### 4.3 影子页表分配

**文件**: `/arch/x86/kvm/mmu/mmu.c` (行 2340-2400)

```c
static struct kvm_mmu_page *kvm_mmu_alloc_shadow_page(struct kvm *kvm,
                                                       struct shadow_page_caches *caches,
                                                       gfn_t gfn,
                                                       struct hlist_head *sp_list,
                                                       union kvm_mmu_page_role role)
{
    struct kvm_mmu_page *sp;

    sp = kmem_cache_zalloc(mmu_page_header_cache, GFP_KERNEL_ACCOUNT);
    sp->spt = kvm_mmu_memory_cache_alloc(&caches->sp_cache);
    sp->shadowed_translation = kvm_mmu_memory_cache_alloc(&caches->shadowed_info_cache);

    // 设置页角色
    sp->role = role;
    sp->gfn = gfn;

    // 初始化链表
    INIT_LIST_HEAD(&sp->link);
    INIT_HLIST_NODE(&sp->hash_link);

    // 如果是 TDP 页,标记
    if (sp->tdp_mmu_page)
        set_page_private(virt_to_page(sp->spt), (unsigned long)sp);

    return sp;
}
```

### 4.4 直接映射 (非 TDP)

**文件**: `/arch/x86/kvm/mmu/mmu.c` (行 3436-3478)

```c
static int direct_map(struct kvm_vcpu *vcpu, struct kvm_page_fault *fault)
{
    struct kvm_shadow_walk_iterator it;
    struct kvm_mmu_page *sp;
    int ret;
    gfn_t base_gfn = fault->gfn;

    kvm_mmu_hugepage_adjust(vcpu, fault);
    trace_kvm_mmu_spte_requested(fault);

    for_each_shadow_entry(vcpu, fault->addr, it) {
        // NX 大页工作区调整
        if (fault->nx_huge_page_workaround_enabled)
            disallowed_hugepage_adjust(fault, *it.sptep, it.level);

        base_gfn = gfn_round_for_level(fault->gfn, it.level);
        if (it.level == fault->goal_level)
            break;

        // 获取或创建子页表
        sp = kvm_mmu_get_child_sp(vcpu, it.sptep, base_gfn, true, ACC_ALL);
        if (sp == ERR_PTR(-EEXIST))
            continue;

        // 链接影子页
        link_shadow_page(vcpu, it.sptep, sp);
        if (fault->huge_page_disallowed)
            account_nx_huge_page(vcpu->kvm, sp, fault->req_level >= it.level);
    }

    if (WARN_ON_ONCE(it.level != fault->goal_level))
        return -EFAULT;

    ret = mmu_set_spte(vcpu, fault->slot, it.sptep, ACC_ALL,
                       base_gfn, fault->pfn, fault);

    if (ret == RET_PF_SPURIOUS)
        return ret;

    direct_pte_prefetch(vcpu, it.sptep);
    return ret;
}
```

### 4.5 影子页表同步

**文件**: `/arch/x86/kvm/mmu/mmu.c` (行 4282-4300)

```c
void kvm_mmu_sync_roots(struct kvm_vcpu *vcpu)
{
    int i;
    struct kvm_mmu_page *sp;

    // 遍历所有活跃页表
    list_for_each_entry(sp, &vcpu->kvm->arch.active_mmu_pages, link) {
        if (sp->role.invalid)
            continue;

        // 只同步直接映射的页
        if (sp->role.direct) {
            // 确保未同步标志可见
            smp_rmb();

            // 如果页未同步,则同步之
            if (sp->unsync)
                kvm_sync_page_transuge(sp, &vcpu->arch.mmu->page_header_cache);
        }
    }
}
```

---

## 5. 脏页追踪

### 5.1 脏位图 (Legacy)

**文件**: `/include/linux/kvm_host.h` (行 592-638)

```c
struct kvm_memory_slot {
    struct hlist_node    id_node[2];
    struct interval_tree_node hva_node[2];
    struct rb_node       gfn_node[2];
    gfn_t                base_gfn;          // 起始 GFN
    unsigned long        npages;            // 页数
    unsigned long       *dirty_bitmap;      // 脏位图
    struct kvm_arch_memory_slot arch;
    unsigned long        userspace_addr;     // 用户空间地址
    u32                  flags;             // 标志
    short                id;                // Slot ID
    u16                  as_id;             // 地址空间 ID
};

// 脏位图大小计算
static inline unsigned long kvm_dirty_bitmap_bytes(struct kvm_memory_slot *memslot)
{
    return ALIGN(memslot->npages, BITS_PER_LONG) / 8;
}
```

### 5.2 脏页环 (Dirty Ring) - 新机制

**文件**: `/include/linux/kvm_dirty_ring.h` (行 1-94)

```c
struct kvm_dirty_ring {
    u32 dirty_index;        // 下一个可写位置
    u32 reset_index;       // 下一个待重置位置
    u32 size;               // 环大小
    u32 soft_limit;         // 软限制 (触发 VM exit)
    struct kvm_dirty_gfn *dirty_gfns;  // 脏页数组
    int index;              // 环索引
};
```

### 5.3 写保护与脏页标记

**文件**: `/arch/x86/kvm/mmu/mmu.c` (行 7254-7300)

```c
static bool kvm_mmu_zap_collapsible_spte(struct kvm *kvm,
                                         struct kvm_rmap_head *rmap_head,
                                         const struct kvm_memory_slot *slot)
{
    u64 *sptep;
    struct rmap_iterator iter;
    int need_tlb_flush = 0;
    struct kvm_mmu_page *sp;

restart:
    for_each_rmap_spte(rmap_head, &iter, sptep) {
        sp = sptep_to_sp(sptep);

        // 如果可以创建大页映射但当前是小页,则 zap
        if (sp->role.direct &&
            sp->role.level < kvm_mmu_max_mapping_level(kvm, NULL, slot, sp->gfn)) {
            kvm_zap_one_rmap_spte(kvm, rmap_head, sptep);

            if (kvm_available_flush_remote_tlbs_range())
                kvm_flush_remote_tlbs_sptep(kvm, sptep);
            else
                need_tlb_flush = 1;

            goto restart;
        }
    }
    return need_tlb_flush;
}

// 回收可折叠的大页
void kvm_mmu_recover_huge_pages(struct kvm *kvm,
                                 const struct kvm_memory_slot *slot)
{
    if (kvm_memslots_have_rmaps(kvm)) {
        write_lock(&kvm->mmu_lock);
        kvm_rmap_zap_collapsible_sptes(kvm, slot);
        write_unlock(&kvm->mmu_lock);
    }

    if (tdp_mmu_enabled) {
        read_lock(&kvm->mmu_lock);
        kvm_tdp_mmu_recover_huge_pages(kvm, slot);
        read_unlock(&kvm->mmu_lock);
    }
}
```

### 5.4 Slot 脏位清除

**文件**: `/arch/x86/kvm/mmu/mmu.c` (行 7318-7345)

```c
void kvm_mmu_slot_leaf_clear_dirty(struct kvm *kvm,
                                   const struct kvm_memory_slot *memslot)
{
    // 传统 MMU: 清除 4K SPTEs 的脏位
    if (kvm_memslots_have_rmaps(kvm)) {
        write_lock(&kvm->mmu_lock);
        walk_slot_rmaps_4k(kvm, memslot, __rmap_clear_dirty, false);
        write_unlock(&kvm->mmu_lock);
    }

    // TDP MMU: 使用专用函数
    if (tdp_mmu_enabled) {
        read_lock(&kvm->mmu_lock);
        kvm_tdp_mmu_clear_dirty_slot(kvm, memslot);
        read_unlock(&kvm->mmu_lock);
    }
}
```

---

## 6. 内存Slot管理

### 6.1 Memory Slot 结构

**文件**: `/include/linux/kvm_host.h` (行 592-616)

```c
struct kvm_memory_slot {
    struct hlist_node id_node[2];           // ID 哈希节点
    struct interval_tree_node hva_node[2];  // HVA 区间树节点
    struct rb_node gfn_node[2];            // GFN 红黑树节点
    gfn_t base_gfn;                        // 起始 GFN 号
    unsigned long npages;                  // 总页数
    unsigned long *dirty_bitmap;            // 脏位图指针
    struct kvm_arch_memory_slot arch;       // 架构特定数据
    unsigned long userspace_addr;           // 用户空间映射地址
    u32 flags;                             // KVM_MEM_* 标志
    short id;                              // Slot ID (-1 表示无效)
    u16 as_id;                             // 地址空间 ID

#ifdef CONFIG_KVM_GUEST_MEMFD
    struct {
        struct file *file;                  // guest_memfd 文件
        pgoff_t pgoff;                     // 文件内偏移
    } gmem;
#endif
};
```

### 6.2 Slot 辅助函数

**文件**: `/include/linux/kvm_host.h` (行 618-638)

```c
// 检查是否使用 guest_memfd
static inline bool kvm_slot_has_gmem(const struct kvm_memory_slot *slot)
{
    return slot && (slot->flags & KVM_MEM_GUEST_MEMFD);
}

// 检查脏页追踪是否启用
static inline bool kvm_slot_dirty_track_enabled(const struct kvm_memory_slot *slot)
{
    return slot->flags & KVM_MEM_LOG_DIRTY_PAGES;
}

// 获取第二脏位图 (用于双缓冲)
static inline unsigned long *kvm_second_dirty_bitmap(struct kvm_memory_slot *memslot)
{
    unsigned long len = kvm_dirty_bitmap_bytes(memslot);
    return memslot->dirty_bitmap + len / sizeof(*memslot->dirty_bitmap);
}
```

### 6.3 TDP MMU Slot 操作

**文件**: `/arch/x86/kvm/mmu/tdp_mmu.c` (行 1352-1366)

```c
// 解除映射 GFN 范围 (用于 memslot 更新)
bool kvm_tdp_mmu_unmap_gfn_range(struct kvm *kvm, struct kvm_gfn_range *range,
                                 bool flush)
{
    enum kvm_tdp_mmu_root_types types;
    struct kvm_mmu_page *root;

    types = kvm_gfn_range_filter_to_root_types(kvm, range->attr_filter) | KVM_INVALID_ROOTS;

    __for_each_tdp_mmu_root_yield_safe(kvm, root, range->slot->as_id, types)
        flush = tdp_mmu_zap_leafs(kvm, root, range->start, range->end,
                                  range->may_block, flush);

    return flush;
}

// 写保护 Slot
bool kvm_tdp_mmu_wrprot_slot(struct kvm *kvm,
                             const struct kvm_memory_slot *slot, int min_level)
{
    struct kvm_mmu_page *root;
    bool spte_set = false;

    lockdep_assert_held_read(&kvm->mmu_lock);

    for_each_valid_tdp_mmu_root_yield_safe(kvm, root, slot->as_id)
        spte_set |= wrprot_gfn_range(kvm, root, slot->base_gfn,
                                     slot->base_gfn + slot->npages, min_level);

    return spte_set;
}
```

---

## 7. 关键数据结构

### 7.1 kvm_mmu_page_role

描述影子页表页的角色,用于识别页的类型和属性。

**文件**: `/include/linux/kvm_host.h` (相关定义)

```c
union kvm_mmu_page_role {
    unsigned word;
    struct {
        unsigned level:4;           // 页级别 (PG_LEVEL_*)
        unsigned cr4_pge:1;         // CR4.PGE 标志
        unsigned cr4_pse:1;         // CR4.PSE 标志
        unsigned cr4_pae:1;         // CR4.PAE 标志
        unsigned cr4_smep:1;        // CR4.SMEP 标志
        unsigned cr4_smap:1;        // CR4.SMAP 标志
        unsigned cr4_la57:1;        // CR4.LA57 标志
        unsigned efer_nx:1;         // EFER.NX 标志
        unsigned ad_disabled:1;     // A/D 位禁用
        unsigned guest_mode:1;      // Guest 模式 (嵌套)
        unsigned direct:1;           // 直接映射
        unsigned mmio_value:1;     // MMIO SPTE 值
        unsigned smm:1;             // SMM 模式
        unsigned reserved:1;         // 保留位
        unsigned quadrant:2;        // 4字节 GPTE 的象限
        unsigned invalid:1;          // 无效根
        unsigned is_mirror:1;       // 镜像根 (TDX)
    };
};
```

### 7.2 kvm_page_fault

页面错误处理的核心数据结构。

**文件**: `/arch/x86/kvm/mmu/mmu_internal.h` (行 226-291)

```c
struct kvm_page_fault {
    const gpa_t        addr;              // 错误地址
    const u64          error_code;       // 错误码
    const bool         prefetch;         // 是否预取

    // 从 error_code 派生
    const bool         exec;             // 取指访问
    const bool         write;            // 写访问
    const bool         present;          // 页存在
    const bool         rsvd;             // 保留位违反
    const bool         user;             // 用户态访问

    // 从 MMU 和全局状态派生
    const bool         is_tdp;           // 是否 TDP MMU
    const bool         is_private;       // 是否私有内存
    const bool         nx_huge_page_workaround_enabled;

    bool               huge_page_disallowed;  // 大页是否被禁止
    u8                 max_level;        // 最大可能级别
    u8                 req_level;        // 请求的级别
    u8                 goal_level;       // 目标级别

    gfn_t              gfn;             // 页面帧号
    struct kvm_memory_slot *slot;        // 内存 slot

    // kvm_mmu_faultin_pfn() 输出
    unsigned long       mmu_seq;         // MMU 序列号
    kvm_pfn_t           pfn;             // 物理页帧号
    struct page        *refcounted_page;
    bool                map_writable;     // 是否可写映射

    bool                write_fault_to_shadow_pgtable;  // 写自己页表
};
```

### 7.3 SPTE 位掩码汇总

**文件**: `/arch/x86/kvm/mmu/spte.h` (行 39-96)

```c
// 基本地址掩码
#define SPTE_BASE_ADDR_MASK (((1ULL << 52) - 1) & ~(u64)(PAGE_SIZE-1))

// 权限掩码
#define SPTE_PERM_MASK (PT_PRESENT_MASK | PT_WRITABLE_MASK | shadow_user_mask \
            | shadow_x_mask | shadow_nx_mask | shadow_me_mask)

#define ACC_EXEC_MASK    1
#define ACC_WRITE_MASK   PT_WRITABLE_MASK
#define ACC_USER_MASK    PT_USER_MASK
#define ACC_ALL          (ACC_EXEC_MASK | ACC_WRITE_MASK | ACC_USER_MASK)

// 主机/客户机可写位 (软件位)
#define DEFAULT_SPTE_HOST_WRITABLE  BIT_ULL(9)
#define DEFAULT_SPTE_MMU_WRITABLE   BIT_ULL(10)
#define EPT_SPTE_HOST_WRITABLE      BIT_ULL(57)
#define EPT_SPTE_MMU_WRITABLE       BIT_ULL(58)
```

---

## 8. 页表层次结构图

### 8.1 x86-64 五级页表 (EPT/NPT)

```
                    EPT/NPT 页表结构 (4KB 页)
                    ============================

    GVA (48 bits used)                         HPA (MAXPHYADDR bits)
    +------------------------------------------------+
    |  47:39  |  38:30  |  29:21  |  20:12  |  11:0  |
    +---------+---------+---------+---------+--------+
    |  PML4E  |  PDPTE  |   PDE   |   PTE   | offset |
    +---------+---------+---------+---------+--------+
        |         |        |        |
        v         v        v        v
    +-------+ +-------+ +-------+ +-------+
    | PML4  | |  PDP  | |  PD   | |  PT   |
    | 4KB   | |  4KB  | |  4KB  | |  4KB  |
    | 512   | |  512  | |  512  | |  512  |
    |entry  | | entry | | entry | | entry |
    +-------+ +-------+ +-------+ +-------+
      |
      +---> 指向 PDP

                           PDP
                            |
                            v
                        +-------+
                        |  PD   |  (512 entries)
                        |  4KB  |
                        +-------+
                            |
                            +---> 指向 PD

                           PD
                            |
                            v
                        +-------+
                        |  PT   |  (512 entries)
                        |  4KB  |
                        +-------+
                            |
                            +---> 指向 4KB 页面
```

### 8.2 大页映射

```
    2MB 大页映射 (PDE.PS=1)
    ========================

    GVA
    +---------------------------+
    |  47:30    |    29:21     |  20:0   |
    +-----------+--------------+----------+
    |  PML4E    |    PDE       | offset   |
    +-----------+--------------+----------+
        |            |
        v            v
    +-------+    +--------+
    | PML4  |    | PDE.PS |
    +-------+    +--------+
                    |
                    +---> 2MB 物理页框
```

### 8.3 TDP MMU 与影子页表的关系

```
    TDP 模式 (硬件辅助)
    ===================

    Guest Virtual Address (GVA)
              |
              v
    +---------------------+
    |   L1 Guest Page     |  <-- Guest 软件遍历
    |   Table (SW)        |
    +---------------------+
              |
              v
    Guest Physical Address (GPA)
              |
              v
    +---------------------+
    |   EPT/NPT (HW)      |  <-- 硬件遍历
    +---------------------+
              |
              v
    Host Physical Address (HPA)


    影子页表模式 (传统)
    ===================

    Guest Virtual Address (GVA)
              |
              v
    +---------------------+
    |   L1 Guest Page     |  <-- KVM 遍历 Guest 页表
    |   Table (SW)        |
    +---------------------+
              |
              v
    Guest Physical Address (GPA)
              |
              v
    +---------------------+
    |   Shadow Page       |  <-- KVM 创建影子页表
    |   Table (SW)        |
    +---------------------+
              |
              v
    Host Physical Address (HPA)
```

---

## 附录 A: 关键函数索引

| 函数 | 文件:行 | 描述 |
|------|---------|------|
| `kvm_tdp_mmu_map` | tdp_mmu.c:1263 | TDP MMU 页映射 |
| `kvm_tdp_mmu_alloc_root` | tdp_mmu.c:253 | 分配 TDP MMU 根 |
| `direct_map` | mmu.c:3436 | 非 TDP 直接映射 |
| `kvm_mmu_sync_roots` | mmu.c:4282 | 同步影子页表根 |
| `make_spte` | spte.c:186 | 创建影子 PTE |
| `tdp_iter_start` | tdp_iter.c:39 | 启动 TDP 迭代器 |
| `handle_changed_spte` | tdp_mmu.c:566 | 处理 SPTE 变化 |

---

## 附录 B: 相关配置参数

```bash
# 启用 TDP MMU (默认启用)
echo 1 > /sys/module/kvm/parameters/tdp_mmu

# 启用 MMIO 缓存
echo 1 > /sys/module/kvm/parameters/mmio_caching

# NX 大页恢复比率 (默认 60)
echo 60 > /proc/sys/kernel/nx_huge_pages_recovery_ratio
```

---

*文档生成时间: 2026-04-26*
*内核版本: Linux (based on master branch)*
