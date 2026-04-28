# Linux Kernel Memory Mapping (mmap) Subsystem Analysis

## Table of Contents

1. [do_mmap 函数和 mmap_region](#1-dommap-函数和-mmap_region)
2. [vm_area_struct 结构详细说明](#2-vm_area_struct-结构详细说明)
3. [vm_flags 标志定义](#3-vm_flags-标志定义)
4. [vm_unmapped_area 地址空间查找](#4-vm_unmapped_area-地址空间查找)
5. [brk/sbrk 系统调用](#5-brksbrk-系统调用)
6. [mlock/munlock 内存锁定](#6-mlockmunlock-内存锁定)
7. [内存布局 (典型进程布局图)](#7-内存布局-典型进程布局图)
8. [Maple Tree VMA 管理](#8-maple-tree-vma-管理)

---

## 1. do_mmap 函数和 mmap_region

### 1.1 do_mmap 函数

**源码位置**: `mm/mmap.c:335-565`

```c
unsigned long do_mmap(struct file *file, unsigned long addr,
                     unsigned long len, unsigned long prot,
                     unsigned long flags, vm_flags_t vm_flags,
                     unsigned long pgoff, unsigned long *populate,
                     struct list_head *uf)
```

**功能**: 执行用户空间内存映射到当前进程的地址空间。

**参数说明**:
- `file`: 文件指针(文件映射时), 匿名映射为 NULL
- `addr`: 期望的映射地址, 如果为 0 则由内核选择
- `len`: 映射长度(页对齐)
- `prot`: 保护位 (PROT_READ, PROT_WRITE, PROT_EXEC)
- `flags`: mmap 标志 (MAP_SHARED, MAP_PRIVATE, MAP_FIXED 等)
- `vm_flags`: VMA 标志
- `pgoff`: 文件内的页偏移
- `populate`: 输出参数, 指示需要填充的页数
- `uf`: userfaultfd 列表头

**主要流程**:

```
do_mmap()
  |
  +-> 1. 验证参数 (len > 0, len 页对齐)
  |
  +-> 2. 处理 PROT_READ -> PROT_EXEC (如果 READ_IMPLIES_EXEC)
  |
  +-> 3. 计算 vm_flags:
  |      - calc_vm_prot_bits(prot, pkey)
  |      - calc_vm_flag_bits(file, flags)
  |      - mm->def_flags
  |      - VM_MAYREAD | VM_MAYWRITE | VM_MAYEXEC
  |
  +-> 4. 获取未映射地址区域:
  |      addr = __get_unmapped_area(file, addr, len, pgoff, flags, vm_flags)
  |
  +-> 5. 检查 MAP_FIXED_NOREPLACE 冲突
  |
  +-> 6. 检查 mlock 限制和权限
  |
  +-> 7. 处理文件映射:
  |      - 检查文件模式 (FMODE_READ/FMODE_WRITE)
  |      - 检查 seals
  |      - 设置 VM_SHARED 等标志
  |
  +-> 8. 处理匿名映射:
  |      - MAP_SHARED / MAP_PRIVATE
  |      - MAP_DROPPABLE
  |
  +-> 9. 处理 MAP_NORESERVE
  |
  +-> 10. 调用 mmap_region() 完成实际映射
  |
  +-> 11. 如果需要, 设置 populate 标志
```

### 1.2 mmap_region 函数

**源码位置**: `mm/vma.c:2818-2860`

```c
unsigned long mmap_region(struct file *file, unsigned long addr,
                         unsigned long len, vm_flags_t vm_flags,
                         unsigned long pgoff, struct list_head *uf)
```

**功能**: 在地址空间中找到合适的位置并创建 VMA。

**返回值**:
- 成功: 映射的实际起始地址
- 失败: 错误码 (负值)

---

## 2. vm_area_struct 结构详细说明

**源码位置**: `include/linux/mm_types.h:913-1056`

```c
struct vm_area_struct {
    /* 第一个缓存行包含 VMA 树遍历的信息 */

    union {
        struct {
            /* VMA 覆盖 [vm_start; vm_end) 地址范围 */
            unsigned long vm_start;
            unsigned long vm_end;
        };
        freeptr_t vm_freeptr; /* SLAB_TYPESAFE_BY_RCU 使用的指针 */
    };

    /* 所属的地址空间 */
    struct mm_struct *vm_mm;

    /* VMA 的访问权限 */
    pgprot_t vm_page_prot;

    /* 标志, 见 vm_flags 定义 */
    union {
        const vm_flags_t vm_flags;
        vma_flags_t flags;
    };

#ifdef CONFIG_PER_VMA_LOCK
    /* VMA 锁序列号 */
    unsigned int vm_lock_seq;
#endif

    /* 匿名 VMA 链表和匿名 VMA 指针 */
    struct list_head anon_vma_chain; /* 通过 mmap_lock 和 page_table_lock 串行化 */
    struct anon_vma *anon_vma;

    /* 操作函数指针 */
    const struct vm_operations_struct *vm_ops;

    /* 备份存储信息 */
    unsigned long vm_pgoff;  /* 文件内的偏移 (PAGE_SIZE 单位) */
    struct file *vm_file;    /* 映射的文件 (可以为 NULL) */
    void *vm_private_data;   /* 私有数据 */

#ifdef CONFIG_SWAP
    atomic_long_t swap_readahead_info;
#endif

#ifndef CONFIG_MMU
    struct vm_region *vm_region;  /* NOMMU 映射区域 */
#endif

#ifdef CONFIG_NUMA
    struct mempolicy *vm_policy;  /* NUMA 策略 */
#endif

#ifdef CONFIG_NUMA_BALANCING
    struct vma_numab_state *numab_state;
#endif

#ifdef CONFIG_PER_VMA_LOCK
    refcount_t vm_refcnt;  /* VMA 引用计数 */
    struct lockdep_map vmlock_dep_map;
#endif

    /* 地址空间 i_mmap 区间树的链接 */
    struct {
        struct rb_node rb;
        unsigned long rb_subtree_last;
    } shared;

#ifdef CONFIG_ANON_VMA_NAME
    struct anon_vma_name *anon_name;  /* 匿名 VMA 名称 */
#endif

    struct vm_userfaultfd_ctx vm_userfaultfd_ctx;

#ifdef __HAVE_PFNMAP_TRACKING
    struct pfnmap_track_ctx *pfnmap_track_ctx;
#endif
} __randomize_layout;
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `vm_start` | unsigned long | VMA 起始地址(包含) |
| `vm_end` | unsigned long | VMA 结束地址(不包含) |
| `vm_mm` | struct mm_struct* | 所属的内存描述符 |
| `vm_page_prot` | pgprot_t | 访问权限的页保护位 |
| `vm_flags` | vm_flags_t | VMA 标志位 |
| `anon_vma_chain` | struct list_head | 匿名 VMA 链表 |
| `anon_vma` | struct anon_vma* | 匿名 VMA 指针 |
| `vm_ops` | const struct vm_operations_struct* | VMA 操作函数集 |
| `vm_pgoff` | unsigned long | 文件内偏移(页单位) |
| `vm_file` | struct file* | 映射的文件 |
| `vm_private_data` | void* | 私有数据指针 |
| `shared` | struct rb_node | 区间树节点(用于 i_mmap) |

---

## 3. vm_flags 标志定义

**源码位置**: `include/linux/mm.h:401-612`

### 3.1 基础访问标志

```c
#define VM_READ       INIT_VM_FLAG(READ)    /* 可读 */
#define VM_WRITE      INIT_VM_FLAG(WRITE)   /* 可写 */
#define VM_EXEC       INIT_VM_FLAG(EXEC)    /* 可执行 */
#define VM_SHARED     INIT_VM_FLAG(SHARED)  /* 共享映射 */
```

### 3.2 权限标志

```c
#define VM_MAYREAD    INIT_VM_FLAG(MAYREAD)    /* 可能设置读权限 */
#define VM_MAYWRITE   INIT_VM_FLAG(MAYWRITE)   /* 可能设置写权限 */
#define VM_MAYEXEC    INIT_VM_FLAG(MAYEXEC)    /* 可能设置执行权限 */
#define VM_MAYSHARE   INIT_VM_FLAG(MAYSHARE)   /* 可能设置共享 */
```

### 3.3 特殊标志

```c
#define VM_GROWSDOWN    INIT_VM_FLAG(GROWSDOWN)    /* 向下扩展(栈) */
#define VM_GROWSUP      INIT_VM_FLAG(GROWSUP)       /* 向上扩展 */
#define VM_PFNMAP       INIT_VM_FLAG(PFNMAP)       /* PFN 映射 */
#define VM_UFFD_WP      INIT_VM_FLAG(UFFD_WP)      /* userfaultfd 写保护 */
#define VM_LOCKED       INIT_VM_FLAG(LOCKED)       /* 已锁定 */
#define VM_IO           INIT_VM_FLAG(IO)           /* I/O 内存 */
#define VM_SEQ_READ     INIT_VM_FLAG(SEQ_READ)    /* 顺序读 */
#define VM_RAND_READ    INIT_VM_FLAG(RAND_READ)    /* 随机读 */
```

### 3.4 行为标志

```c
#define VM_DONTCOPY     INIT_VM_FLAG(DONTCOPY)      /* fork 时不复制 */
#define VM_DONTEXPAND   INIT_VM_FLAG(DONTEXPAND)    /* 不允许 mremap 扩展 */
#define VM_LOCKONFAULT  INIT_VM_FLAG(LOCKONFAULT)  /* 按需锁定 */
#define VM_ACCOUNT      INIT_VM_FLAG(ACCOUNT)       /* 计算内存使用 */
#define VM_NORESERVE    INIT_VM_FLAG(NORESERVE)    /* 不预留内存 */
#define VM_HUGETLB      INIT_VM_FLAG(HUGETLB)      /* 大页映射 */
#define VM_SYNC         INIT_VM_FLAG(SYNC)          /* 同步 I/O */
#define VM_WIPEONFORK   INIT_VM_FLAG(WIPEONFORK)   /* fork 后清空 */
#define VM_DONTDUMP     INIT_VM_FLAG(DONTDUMP)     /* 不转储 */
#define VM_SOFTDIRTY    INIT_VM_FLAG(SOFTDIRTY)    /* 软脏位 */
```

### 3.5 栈相关

```c
#define VM_STACK       INIT_VM_FLAG(STACK)          /* 栈区域 */
#define VM_STACK_EARLY  INIT_VM_FLAG(STACK_EARLY)   /* 栈初始化标志 */
#define VM_SHADOW_STACK INIT_VM_FLAG(SHADOW_STACK)  /* 影子栈 */
```

### 3.6 架构特定标志

```c
#define VM_PKEY_BIT0   INIT_VM_FLAG(PKEY_BIT0)  /* 内存保护键 */
#define VM_PKEY_BIT1   INIT_VM_FLAG(PKEY_BIT1)
#define VM_PKEY_BIT2   INIT_VM_FLAG(PKEY_BIT2)
#define VM_PKEY_BIT3   INIT_VM_FLAG(PKEY_BIT3)
#define VM_PKEY_BIT4   INIT_VM_FLAG(PKEY_BIT4)

#define VM_MTE           INIT_VM_FLAG(MTE)           /* 内存标记扩展 */
#define VM_MTE_ALLOWED   INIT_VM_FLAG(MTE_ALLOWED)
```

### 3.7 其他标志

```c
#define VM_MIXEDMAP     INIT_VM_FLAG(MIXEDMAP)     /* 混合映射 */
#define VM_HUGEPAGE     INIT_VM_FLAG(HUGEPAGE)     /* 可用大页 */
#define VM_NOHUGEPAGE   INIT_VM_FLAG(NOHUGEPAGE)   /* 不用大页 */
#define VM_MERGEABLE    INIT_VM_FLAG(MERGEABLE)   /* KSM 可合并 */
#define VM_DROPPABLE    INIT_VM_FLAG(DROPPABLE)   /* 可丢弃页面 */
#define VM_SEALED       INIT_VM_FLAG(SEALED)       /* 已密封 */
#define VM_UFFD_MINOR   INIT_VM_FLAG(UFFD_MINOR)  /* userfaultfd minor */
```

### 3.8 组合标志

```c
/* 锁相关掩码 */
#define VM_LOCKED_MASK (VM_LOCKED | VM_LOCKONFAULT)

/* 特殊 VMA (不可合并, 不可 mlock) */
#define VM_SPECIAL (VM_IO | VM_DONTEXPAND | VM_PFNMAP | VM_MIXEDMAP)

/* 访问权限位 */
#define VM_ACCESS_FLAGS (VM_READ | VM_WRITE | VM_EXEC)

/* 栈默认标志 */
#define VM_STACK_FLAGS (VM_STACK | VM_STACK_DEFAULT_FLAGS | VM_ACCOUNT)
```

---

## 4. vm_unmapped_area 地址空间查找

### 4.1 vm_unmapped_area_info 结构

**源码位置**: `include/linux/mm.h:3907-3916`

```c
struct vm_unmapped_area_info {
#define VM_UNMAPPED_AREA_TOPDOWN 1
    unsigned long flags;          /* 标志 (如 TOPDOWN) */
    unsigned long length;        /* 所需长度 */
    unsigned long low_limit;     /* 搜索下限 */
    unsigned long high_limit;    /* 搜索上限 */
    unsigned long align_mask;    /* 对齐掩码 */
    unsigned long align_offset;  /* 对齐偏移 */
    unsigned long start_gap;     /* 起始间隙 */
};
```

### 4.2 vm_unmapped_area 函数

**源码位置**: `mm/mmap.c:664-675`

```c
unsigned long vm_unmapped_area(struct vm_unmapped_area_info *info)
{
    unsigned long addr;

    if (info->flags & VM_UNMAPPED_AREA_TOPDOWN)
        addr = unmapped_area_topdown(info);
    else
        addr = unmapped_area(info);

    trace_vm_unmapped_area(addr, info);
    return addr;
}
```

**功能**: 根据 info 中的约束条件搜索未映射的地址区域。

### 4.3 unmapped_area (自底向上搜索)

**源码位置**: `mm/vma.c:2947-2997`

**算法流程**:

```
unmapped_area(info)
  |
  +-> 1. 计算调整后的长度:
  |      length = info->length + info->align_mask + info->start_gap
  |
  +-> 2. 设置搜索边界:
  |      low_limit = max(info->low_limit, mmap_min_addr)
  |      high_limit = info->high_limit
  |
  +-> 3. 使用 Maple Tree 查找空闲区域:
  |      vma_iter_area_lowest(&vmi, low_limit, high_limit, length)
  |      返回包含最大空闲区域的地址
  |
  +-> 4. 计算间隙:
  |      gap = vma_iter_addr(&vmi) + info->start_gap
  |      gap += (info->align_offset - gap) & info->align_mask
  |
  +-> 5. 检查是否与下一个 VMA 冲突
  |
  +-> 6. 检查与前一个 VMA 的间隙
  |
  +-> 7. 返回对齐后的地址
```

### 4.4 unmapped_area_topdown (自顶向下搜索)

**源码位置**: `mm/vma.c:3004-3061`

**算法流程**:

```
unmapped_area_topdown(info)
  |
  +-> 1. 计算调整后的长度
  |
  +-> 2. 设置搜索边界
  |
  +-> 3. 使用 Maple Tree 从高位查找:
  |      vma_iter_area_highest(&vmi, low_limit, high_limit, length)
  |
  +-> 4. 计算间隙:
  |      gap = vma_iter_end(&vmi) - info->length
  |      gap -= (gap - info->align_offset) & info->align_mask
  |
  +-> 5. 检查与下一个 VMA 的冲突
  |
  +-> 6. 如果失败, 回退到自底向上搜索
```

---

## 5. brk/sbrk 系统调用

### 5.1 brk 系统调用

**源码位置**: `mm/mmap.c:116-214`

```c
SYSCALL_DEFINE1(brk, unsigned long, brk)
{
    unsigned long newbrk, oldbrk, origbrk;
    struct mm_struct *mm = current->mm;
    struct vm_area_struct *brkvma, *next = NULL;
    unsigned long min_brk;
    bool populate = false;
    LIST_HEAD(uf);
    struct vma_iterator vmi;

    if (mmap_write_lock_killable(mm))
        return -EINTR;

    origbrk = mm->brk;
    min_brk = mm->start_brk;
    // ...

    if (brk < min_brk)
        goto out;

    // 检查 rlimit(RLIMIT_DATA)
    if (check_data_rlimit(rlimit(RLIMIT_DATA), brk, ...))
        goto out;

    newbrk = PAGE_ALIGN(brk);
    oldbrk = PAGE_ALIGN(mm->brk);

    if (oldbrk == newbrk) {
        mm->brk = brk;
        goto success;
    }

    // 收缩 brk
    if (brk <= mm->brk) {
        // 调用 do_vmi_align_munmap 取消映射
        mm->brk = brk;
        if (do_vmi_align_munmap(&vmi, brkvma, mm, newbrk, oldbrk, &uf, true))
            goto out;
        goto success_unlocked;
    }

    // 扩展 brk
    if (check_brk_limits(oldbrk, newbrk - oldbrk))
        goto out;

    // 检查与下一个 VMA 的 stack_guard_gap
    vma_iter_init(&vmi, mm, oldbrk);
    next = vma_find(&vmi, newbrk + PAGE_SIZE + stack_guard_gap);
    if (next && newbrk + PAGE_SIZE > vm_start_gap(next))
        goto out;

    brkvma = vma_prev_limit(&vmi, mm->start_brk);

    // 调用 do_brk_flags 创建新 VMA
    if (do_brk_flags(&vmi, brkvma, oldbrk, newbrk - oldbrk, 0) < 0)
        goto out;

    mm->brk = brk;
    if (mm->def_flags & VM_LOCKED)
        populate = true;

success:
    mmap_write_unlock(mm);
success_unlocked:
    userfaultfd_unmap_complete(mm, &uf);
    if (populate)
        mm_populate(oldbrk, newbrk - oldbrk);
    return brk;

out:
    mm->brk = origbrk;
    mmap_write_unlock(mm);
    return origbrk;
}
```

### 5.2 do_brk_flags 函数

**源码位置**: `mm/vma.c:2866-2917`

```c
int do_brk_flags(struct vma_iterator *vmi, struct vm_area_struct *vma,
                 unsigned long addr, unsigned long len, vm_flags_t vm_flags)
{
    struct mm_struct *mm = current->mm;

    // 设置默认标志
    vm_flags |= VM_DATA_DEFAULT_FLAGS | VM_ACCOUNT | mm->def_flags;
    vm_flags = ksm_vma_flags(mm, NULL, vm_flags);

    // 检查是否可扩展
    if (!may_expand_vm(mm, vm_flags, len >> PAGE_SHIFT))
        return -ENOMEM;

    // 检查映射数量限制
    if (mm->map_count > sysctl_max_map_count)
        return -ENOMEM;

    // 检查内存是否足够
    if (security_vm_enough_memory_mm(mm, len >> PAGE_SHIFT))
        return -ENOMEM;

    // 尝试与相邻 VMA 合并
    // ...

    // 插入新的 VMA
    // ...
}
```

---

## 6. mlock/munlock 内存锁定

### 6.1 mlock 系统调用

**源码位置**: `mm/mlock.c:659-662`

```c
SYSCALL_DEFINE2(mlock, unsigned long, start, size_t, len)
{
    return do_mlock(start, len, VM_LOCKED);
}
```

### 6.2 do_mlock 函数

**源码位置**: `mm/mlock.c:612-657`

```c
static __must_check int do_mlock(unsigned long start, size_t len, vm_flags_t flags)
{
    unsigned long locked;
    unsigned long lock_limit;
    int error = -ENOMEM;

    start = untagged_addr(start);

    if (!can_do_mlock())
        return -EPERM;

    // 页对齐
    len = PAGE_ALIGN(len + (offset_in_page(start)));
    start &= PAGE_MASK;

    lock_limit = rlimit(RLIMIT_MEMLOCK);
    lock_limit >>= PAGE_SHIFT;
    locked = len >> PAGE_SHIFT;

    if (mmap_write_lock_killable(current->mm))
        return -EINTR;

    locked += current->mm->locked_vm;

    // 检查 RLIMIT_MEMLOCK 限制
    if ((locked > lock_limit) && (!capable(CAP_IPC_LOCK))) {
        locked -= count_mm_mlocked_page_nr(current->mm, start, len);
    }

    if ((locked <= lock_limit) || capable(CAP_IPC_LOCK))
        error = apply_vma_lock_flags(start, len, flags);

    mmap_write_unlock(current->mm);
    if (error)
        return error;

    // 填充页面
    error = __mm_populate(start, len, 0);
    if (error)
        return __mlock_posix_error_return(error);
    return 0;
}
```

### 6.3 mlock2 系统调用

**源码位置**: `mm/mlock.c:664-675`

```c
SYSCALL_DEFINE3(mlock2, unsigned long, start, size_t, len, int, flags)
{
    vm_flags_t vm_flags = VM_LOCKED;

    if (flags & ~MLOCK_ONFAULT)
        return -EINVAL;

    if (flags & MLOCK_ONFAULT)
        vm_flags |= VM_LOCKONFAULT;

    return do_mlock(start, len, vm_flags);
}
```

### 6.4 munlock 系统调用

**源码位置**: `mm/mlock.c:677-692`

```c
SYSCALL_DEFINE2(munlock, unsigned long, start, size_t, len)
{
    int ret;

    start = untagged_addr(start);
    len = PAGE_ALIGN(len + (offset_in_page(start)));
    start &= PAGE_MASK;

    if (mmap_write_lock_killable(current->mm))
        return -EINTR;

    ret = apply_vma_lock_flags(start, len, 0);
    mmap_write_unlock(current->mm);

    return ret;
}
```

### 6.5 mlockall/munlockall 系统调用

**源码位置**: `mm/mlock.c:745-783`

```c
SYSCALL_DEFINE1(mlockall, int, flags)
{
    unsigned long lock_limit;
    int ret;

    if (!flags || (flags & ~(MCL_CURRENT | MCL_FUTURE | MCL_ONFAULT)) ||
        flags == MCL_ONFAULT)
        return -EINVAL;

    if (!can_do_mlock())
        return -EPERM;

    lock_limit = rlimit(RLIMIT_MEMLOCK);
    lock_limit >>= PAGE_SHIFT;

    if (mmap_write_lock_killable(current->mm))
        return -EINTR;

    ret = -ENOMEM;
    if (!(flags & MCL_CURRENT) || (current->mm->total_vm <= lock_limit) ||
        capable(CAP_IPC_LOCK))
        ret = apply_mlockall_flags(flags);

    mmap_write_unlock(current->mm);
    if (!ret && (flags & MCL_CURRENT))
        mm_populate(0, TASK_SIZE);

    return ret;
}

SYSCALL_DEFINE0(munlockall)
{
    int ret;

    if (mmap_write_lock_killable(current->mm))
        return -EINTR;

    ret = apply_mlockall_flags(0);
    mmap_write_unlock(current->mm);
    return ret;
}
```

### 6.6 页面锁定机制

**源码位置**: `mm/mlock.c:61-101`

锁定页面的核心函数:

- `mlock_folio()`: 锁定已存在于 LRU 的页面
- `munlock_folio()`: 解锁页面
- `mlock_new_folio()`: 锁定新分配的页面

**PG_mlocked 标志**:
- 锁定页面设置 `PG_mlocked` 标志
- 页面被标记为不可回收 (unevictable)
- 统计信息: `NR_MLOCK`

---

## 7. 内存布局 (典型进程布局图)

### 7.1 32位进程内存布局

```
+------------------------+ 0xFFFFFFFF (4GB)
|     Kernel Space      | 0xC0000000 - 0xFFFFFFFF (1GB)
+------------------------+ 0xC0000000
|        Stack          | <- 向下增长
|    (gorws down)        |
+------------------------+ 0xBFFFFFFC
|        |               |
|        |  Memory Gap   |
|        |               |
+------------------------+ 0x40000000
|        Heap           | <- 向上增长 (brk)
|                       |
+------------------------+ 0x40000000
|     BSS Segment       |
|    (uninitialized)    |
+------------------------+
|     Data Segment      |
|   (initialized)       |
+------------------------+
|     Text Segment      |
|     (code + rodata)   |
+------------------------+ 0x08048000
|        Reserved       |
+------------------------+ 0x08000000
|     Null Pointer Page | 0x00000000
+------------------------+ 0x00000000
```

### 7.2 64位进程内存布局

```
+----------------------------+ 0xFFFFFFFFFFFFFFFF (128TB)
|       Kernel Space         | (最高 64TB 或 128TB)
+----------------------------+
|        User Space End      |
+----------------------------+ ~0x00007FFFFFFFFFFF
|                           |
|    Stack (gorws down)     |
|                          |
+--------------------------+ ~0x00007FFFFFFFFFFF - stack_size
|                          |
|    Memory Mapping Area   |
|    (mmap, 向上或向下增长) |
|                          |
+--------------------------+ mmap_base
|                          |
|    Heap (brk)            |
|                          |
+--------------------------+ mm->start_brk
|                          |
|    BSS                   |
+--------------------------+ mm->end_data
|                          |
|    Data                  |
+--------------------------+ mm->start_data
|                          |
|    Text                  |
+--------------------------+ 0x400000 (typical)
|    Reserved / ELF Header |
+--------------------------+ 0x0000000000400000
|    Null Pointer Page    | 0x0000000000000000
+--------------------------+ 0x0000000000000000
```

### 7.3 mmap 区域布局 (自顶向下布局)

**源码位置**: `mm/mmap.c` (自底向上/自顶向下选择逻辑)

```
mmap_base (随机化基址)
    |
    |  stack_guard_gap (通常 256KB)
    v
+------------------+
|     Stack       | <- 向低地址增长 (gorwsdown)
+------------------+
|                  |
|   Available      |
|                  |
+------------------+ 假设 mmap_base = 0x7fb9000000
|                  |
|   Heap (brk)     | <- 向高地址增长
+------------------+ mm->start_brk
|    BSS           |
+------------------+ mm->end_data
|    Data          |
+------------------+ mm->start_data
|    Text          |
+------------------+ 0x400000
|   [vsyscall]     |
+------------------+
|   [vdso]         |
+------------------+ 0x0000000000001000
|   [null page]    |
+------------------+ 0x0000000000000000
```

---

## 8. Maple Tree VMA 管理

### 8.1 Maple Tree 简介

Maple Tree 是 Linux 内核中用于替代红黑树管理 VMA 的数据结构。

**源码位置**: `include/linux/maple_tree.h`

**特点**:
- 更快的查找和迭代
- 更好的缓存局部性
- 支持范围查询
- RCU 安全的遍历

### 8.2 mm_struct 中的 Maple Tree

**源码位置**: `include/linux/mm_types.h:1140`

```c
struct mm_struct {
    struct {
        struct maple_tree mm_mt;  /* VMA 树 */
        unsigned long mmap_base;  /* mmap 区域基址 */
        unsigned long mmap_legacy_base;
        // ...
    };
    // ...
};
```

### 8.3 VMA 迭代器

**源码位置**: `include/linux/mm_types.h:1497-1509`

```c
struct vma_iterator {
    struct ma_state mas;
};

#define VMA_ITERATOR(name, __mm, __addr) \
    struct vma_iterator name = {               \
        .mas = {                               \
            .tree = &(__mm)->mm_mt,           \
            .index = __addr,                   \
            .node = NULL,                      \
            .status = ma_start,                \
        },                                     \
    }
```

### 8.4 VMA 树操作函数

**主要函数** (源码位置 `mm/vma.c`):

| 函数 | 功能 |
|------|------|
| `vma_iter_init()` | 初始化 VMA 迭代器 |
| `vma_iter_load()` | 加载当前迭代器位置的 VMA |
| `vma_iter_next()` | 获取下一个 VMA |
| `vma_iter_prev()` | 获取前一个 VMA |
| `vma_iter_store()` | 存储 VMA 到树 |
| `vma_iter_clear()` | 从树中删除 VMA |
| `vma_find()` | 查找包含指定地址的 VMA |
| `vma_find_intersection()` | 查找与范围相交的 VMA |

### 8.5 VMA 查找

**find_vma 函数** (源码位置 `mm/mmap.c:902-908`):

```c
struct vm_area_struct *find_vma(struct mm_struct *mm, unsigned long addr)
{
    unsigned long index = addr;

    mmap_assert_locked(mm);
    return mt_find(&mm->mm_mt, &index, ULONG_MAX);
}
```

**find_vma_intersection 函数** (源码位置 `mm/mmap.c:883-891`):

```c
struct vm_area_struct *find_vma_intersection(struct mm_struct *mm,
                                              unsigned long start_addr,
                                              unsigned long end_addr)
{
    unsigned long index = start_addr;

    mmap_assert_locked(mm);
    return mt_find(&mm->mm_mt, &index, end_addr - 1);
}
```

### 8.6 VMA 合并/分割

**源码位置**: `mm/vma.c`

核心结构:

```c
struct vma_merge_struct {
    struct mm_struct *mm;
    struct vma_iterator *vmi;
    struct vm_area_struct *prev;
    struct vm_area_struct *middle;  /* 要合并的 VMA */
    struct vm_area_struct *next;
    unsigned long start;
    unsigned long end;
    pgoff_t pgoff;
    vm_flags_t vm_flags;
    // ...
    enum vma_merge_state state;
};
```

**合并条件**:
1. 相邻的 VMA
2. 相同的 vm_flags
3. 相同的文件/anon_vma
4. 连续的页偏移

---

## 附录 A: 关键源码文件索引

| 文件 | 功能 |
|------|------|
| `mm/mmap.c` | mmap 系统调用实现, 地址空间查找 |
| `mm/vma.c` | VMA 操作核心函数 |
| `mm/vma.h` | VMA 操作接口定义 |
| `mm/mlock.c` | mlock/munlock 实现 |
| `mm/mremap.c` | mremap 系统调用 |
| `include/linux/mm.h` | mm 子系统头文件, vm_flags 定义 |
| `include/linux/mm_types.h` | mm_struct, vm_area_struct 定义 |
| `include/linux/maple_tree.h` | Maple Tree 数据结构 |

## 附录 B: 系统调用接口

| 系统调用 | 源码位置 |
|---------|----------|
| mmap | `mm/mmap.c:612` (sys_mmap_pgoff) |
| munmap | `mm/mmap.c:1075` |
| mremap | `mm/mremap.c` |
| brk | `mm/mmap.c:116` |
| mlock | `mm/mlock.c:659` |
| mlock2 | `mm/mlock.c:664` |
| munlock | `mm/mlock.c:677` |
| mlockall | `mm/mlock.c:745` |
| munlockall | `mm/mlock.c:774` |
| mprotect | `mm/mprotect.c` |
