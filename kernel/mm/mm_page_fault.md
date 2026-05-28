# Linux Kernel 缺页中断(Page Fault)处理机制

## 目录

1. [概述](#概述)
2. [缺页中断入口 do_page_fault](#1-缺页中断入口-do_page_fault)
3. [handle_mm_fault](#2-handle_mm_fault)
4. [handle_pte_fault - PTE层缺页处理](#3-handle_pte_fault---pte层缺页处理)
5. [do_anonymous_page - 匿名页面缺页](#4-do_anonymous_page---匿名页面缺页)
6. [do_fault - 文件映射缺页](#5-do_fault---文件映射缺页)
7. [do_swap_page - 交换空间缺页](#6-do_swap_page---交换空间缺页)
8. [do_wp_page - COW机制](#7-do_wp_page---cow机制)
9. [vm_fault结构体和fault_flag](#8-vm_fault结构体和fault_flag)
10. [vm_operations_struct 回调](#9-vm_operations_struct-回调)
11. [完整缺页中断流程图](#完整缺页中断流程图)

---

## 概述

缺页中断(Page Fault)是Linux内核处理内存访问的核心机制。当CPU访问的虚拟地址在页表中没有对应的物理页帧(PFN)或权限不足时，会触发缺页中断。

**缺页中断分类：**

| 类型 | 说明 |
|------|------|
| Minor Fault | 页表项不存在，但页面已在内存中（如匿名页面未映射、文件缓存未映射） |
| Major Fault | 页面不在内存中，需要从磁盘读取（如swap in、文件读取） |
| Protection Fault | 权限不足（如写只读页面、COW等） |

---

## 1. 缺页中断入口 do_page_fault

**源码位置：** `arch/x86/mm/fault.c`

### 1.1 入口点：exc_page_fault

```c
// arch/x86/mm/fault.c:1483
DEFINE_IDTENTRY_RAW_ERRORCODE(exc_page_fault)
{
    irqentry_state_t state;
    unsigned long address;

    address = cpu_feature_enabled(X86_FEATURE_FRED) ? fred_event_data(regs) : read_cr2();

    // KVM异步页面故障处理
    if (kvm_handle_async_pf(regs, (u32)address))
        return;

    state = irqentry_enter(regs);
    instrumentation_begin();
    handle_page_fault(regs, error_code, address);
    instrumentation_end();
    irqentry_exit(regs, state);
}
```

### 1.2 页面故障分发：handle_page_fault

```c
// arch/x86/mm/fault.c:1461-1481
static __always_inline void
handle_page_fault(struct pt_regs *regs, unsigned long error_code,
                  unsigned long address)
{
    trace_page_fault_entries(regs, error_code, address);

    if (unlikely(kmmio_fault(regs, address)))
        return;

    /* 判断是内核空间还是用户空间地址 */
    if (unlikely(fault_in_kernel_space(address))) {
        do_kern_addr_fault(regs, error_code, address);
    } else {
        do_user_addr_fault(regs, error_code, address);
    }
    local_irq_disable();
}
```

### 1.3 用户空间缺页处理：do_user_addr_fault

```c
// arch/x86/mm/fault.c:1206-1448
static inline void do_user_addr_fault(struct pt_regs *regs,
            unsigned long error_code, unsigned long address)
{
    struct vm_area_struct *vma;
    struct task_struct *tsk;
    struct mm_struct *mm;
    vm_fault_t fault;
    unsigned int flags = FAULT_FLAG_DEFAULT;

    tsk = current;
    mm = tsk->mm;

    // 内核代码尝试执行用户空间内存
    if (unlikely((error_code & (X86_PF_USER | X86_PF_INSTR)) == X86_PF_INSTR)) {
        if (is_errata93(regs, address))
            return;
        page_fault_oops(regs, error_code, address);
        return;
    }

    // 保留位检查
    if (unlikely(error_code & X86_PF_RSVD))
        pgtable_bad(regs, error_code, address);

    // SMAP检查
    if (unlikely(cpu_feature_enabled(X86_FEATURE_SMAP) && ...))
        page_fault_oops(regs, error_code, address);

    // pagefault禁用检查
    if (unlikely(faulthandler_disabled() || !mm)) {
        bad_area_nosemaphore(regs, error_code, address);
        return;
    }

    local_irq_enable();
    perf_sw_event(PERF_COUNT_SW_PAGE_FAULTS, 1, regs, address);

    // 设置fault flags
    if (error_code & X86_PF_SHSTK)
        flags |= FAULT_FLAG_WRITE;
    if (error_code & X86_PF_WRITE)
        flags |= FAULT_FLAG_WRITE;
    if (error_code & X86_PF_INSTR)
        flags |= FAULT_FLAG_INSTRUCTION;
    if (user_mode(regs))
        flags |= FAULT_FLAG_USER;

    // vsyscall页面模拟
    if (is_vsyscall_vaddr(address)) {
        if (emulate_vsyscall(error_code, regs, address))
            return;
    }

    // 查找VMA并调用handle_mm_fault
    vma = lock_vma_under_rcu(mm, address);
    if (!vma)
        goto lock_mmap;

    if (unlikely(access_error(error_code, vma))) {
        bad_area_access_error(regs, error_code, address, NULL, vma);
        return;
    }
    fault = handle_mm_fault(vma, address, flags | FAULT_FLAG_VMA_LOCK, regs);
    // ... 错误处理和重试逻辑
}
```

### 1.4 x86错误码定义

| 错误码 | 名称 | 说明 |
|--------|------|------|
| X86_PF_PROT | bit 0 | 1=权限错误, 0=页面不存在 |
| X86_PF_WRITE | bit 1 | 1=写访问, 0=读访问 |
| X86_PF_USER | bit 2 | 1=用户态, 0=内核态 |
| X86_PF_RSVD | bit 3 | 保留位违规 |
| X86_PF_INSTR | bit 4 | 指令获取 |
| X86_PF_PK | bit 5 | Protection Key违规 |
| X86_PF_SGX | bit 15 | SGX违规 |

---

## 2. handle_mm_fault

**源码位置：** `mm/memory.c:6589`

### 2.1 函数签名

```c
vm_fault_t handle_mm_fault(struct vm_area_struct *vma, unsigned long address,
               unsigned int flags, struct pt_regs *regs)
```

### 2.2 核心实现

```c
// mm/memory.c:6589-6654
vm_fault_t handle_mm_fault(struct vm_area_struct *vma, unsigned long address,
               unsigned int flags, struct pt_regs *regs)
{
    struct mm_struct *mm = vma->vm_mm;
    vm_fault_t ret;
    bool is_droppable;

    __set_current_state(TASK_RUNNING);

    // 验证flags合法性
    ret = sanitize_fault_flags(vma, &flags);
    if (ret)
        goto out;

    // 架构级权限检查
    if (!arch_vma_access_permitted(vma, flags & FAULT_FLAG_WRITE,
                        flags & FAULT_FLAG_INSTRUCTION,
                        flags & FAULT_FLAG_REMOTE)) {
        ret = VM_FAULT_SIGSEGV;
        goto out;
    }

    is_droppable = !!(vma->vm_flags & VM_DROPPABLE);

    // 用户fault启用memcg OOM处理
    if (flags & FAULT_FLAG_USER)
        mem_cgroup_enter_user_fault();

    lru_gen_enter_fault(vma);

    // hugeTLB页面处理
    if (unlikely(is_vm_hugetlb_page(vma)))
        ret = hugetlb_fault(vma->vm_mm, vma, address, flags);
    else
        ret = __handle_mm_fault(vma, address, flags);

    lru_gen_exit_fault();

    // droppable VMA的OOM不致命
    if (is_droppable)
        ret &= ~VM_FAULT_OOM;

    if (flags & FAULT_FLAG_USER) {
        mem_cgroup_exit_user_fault();
        if (task_in_memcg_oom(current) && !(ret & VM_FAULT_OOM))
            mem_cgroup_oom_synchronize(false);
    }
out:
    mm_account_fault(mm, regs, address, flags, ret);
    return ret;
}
```

### 2.3 __handle_mm_fault - 页表级处理

```c
// mm/memory.c:6355-6456
static vm_fault_t __handle_mm_fault(struct vm_area_struct *vma,
        unsigned long address, unsigned int flags)
{
    struct vm_fault vmf = {
        .vma = vma,
        .address = address & PAGE_MASK,
        .real_address = address,
        .flags = flags,
        .pgoff = linear_page_index(vma, address),
        .gfp_mask = __get_fault_gfp_mask(vma),
    };
    struct mm_struct *mm = vma->vm_mm;
    pgd_t *pgd;
    p4d_t *p4d;
    vm_fault_t ret;

    // PGD级别
    pgd = pgd_offset(mm, address);
    p4d = p4d_alloc(mm, pgd, address);
    if (!p4d)
        return VM_FAULT_OOM;

    // PUD级别 - 尝试创建huge page
    vmf.pud = pud_alloc(mm, p4d, address);
    if (!vmf.pud)
        return VM_FAULT_OOM;
retry_pud:
    if (pud_none(*vmf.pud) &&
        thp_vma_allowable_order(vma, vm_flags, TVA_PAGEFAULT, PUD_ORDER)) {
        ret = create_huge_pud(&vmf);
        if (!(ret & VM_FAULT_FALLBACK))
            return ret;
    } else if (pud_trans_huge(orig_pud)) {
        if ((flags & FAULT_FLAG_WRITE) && !pud_write(orig_pud)) {
            ret = wp_huge_pud(&vmf, orig_pud);
            if (!(ret & VM_FAULT_FALLBACK))
                return ret;
        } else {
            huge_pud_set_accessed(&vmf, orig_pud);
            return 0;
        }
    }

    // PMD级别 - 尝试创建huge page
    vmf.pmd = pmd_alloc(mm, vmf.pud, address);
    if (!vmf.pmd)
        return VM_FAULT_OOM;

    if (pmd_none(*vmf.pmd) &&
        thp_vma_allowable_order(vma, vm_flags, TVA_PAGEFAULT, PMD_ORDER)) {
        ret = create_huge_pmd(&vmf);
        if (ret & VM_FAULT_FALLBACK)
            goto fallback;
        else
            return ret;
    }

    // ...

fallback:
    return handle_pte_fault(&vmf);
}
```

---

## 3. handle_pte_fault - PTE层缺页处理

**源码位置：** `mm/memory.c:6273`

### 3.1 核心逻辑

```c
// mm/memory.c:6273-6347
static vm_fault_t handle_pte_fault(struct vm_fault *vmf)
{
    pte_t entry;

    if (unlikely(pmd_none(*vmf->pmd))) {
        // PMD为空，延迟分配页表
        vmf->pte = NULL;
        vmf->flags &= ~FAULT_FLAG_ORIG_PTE_VALID;
    } else {
        // 获取PTE并加锁
        vmf->pte = pte_offset_map_rw_nolock(vmf->vma->vm_mm, vmf->pmd,
                            vmf->address, &dummy_pmdval, &vmf->ptl);
        if (unlikely(!vmf->pte))
            return 0;
        vmf->orig_pte = ptep_get_lockless(vmf->pte);
        vmf->flags |= FAULT_FLAG_ORIG_PTE_VALID;

        if (pte_none(vmf->orig_pte)) {
            pte_unmap(vmf->pte);
            vmf->pte = NULL;
        }
    }

    if (!vmf->pte)
        return do_pte_missing(vmf);    // 页面不存在

    if (!pte_present(vmf->orig_pte))
        return do_swap_page(vmf);      // 页面被swap out

    if (pte_protnone(vmf->orig_pte) && vma_is_accessible(vmf->vma))
        return do_numa_page(vmf);      // NUMA迁移

    spin_lock(vmf->ptl);
    entry = vmf->orig_pte;

    // PTE在并发中被修改
    if (unlikely(!pte_same(ptep_get(vmf->pte), entry))) {
        update_mmu_tlb(vmf->vma, vmf->address, vmf->pte);
        goto unlock;
    }

    // 写访问或unshare请求但页面只读
    if (vmf->flags & (FAULT_FLAG_WRITE | FAULT_FLAG_UNSHARE)) {
        if (!pte_write(entry))
            return do_wp_page(vmf);     // COW处理
        else if (likely(vmf->flags & FAULT_FLAG_WRITE))
            entry = pte_mkdirty(entry);
    }

    entry = pte_mkyoung(entry);

    // 更新PTE的access bit
    if (ptep_set_access_flags(vmf->vma, vmf->address, vmf->pte, entry,
                vmf->flags & FAULT_FLAG_WRITE))
        update_mmu_cache_range(vmf, vmf->vma, vmf->address, vmf->pte, 1);
    else
        fix_spurious_fault(vmf, PGTABLE_LEVEL_PTE);
unlock:
    pte_unmap_unlock(vmf->pte, vmf->ptl);
    return 0;
}
```

### 3.2 PTE缺失处理：do_pte_missing

```c
// mm/memory.c:4472-4478
static vm_fault_t do_pte_missing(struct vm_fault *vmf)
{
    if (vma_is_anonymous(vmf->vma))
        return do_anonymous_page(vmf);  // 匿名页面
    else
        return do_fault(vmf);          // 文件映射
}
```

---

## 4. do_anonymous_page - 匿名页面缺页

**源码位置：** `mm/memory.c:5217`

### 4.1 核心实现

```c
// mm/memory.c:5217-5330
static vm_fault_t do_anonymous_page(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    unsigned long addr = vmf->address;
    struct folio *folio;
    vm_fault_t ret = 0;
    int nr_pages = 1;
    pte_t entry;

    // 共享映射不能使用匿名页面
    if (vma->vm_flags & VM_SHARED)
        return VM_FAULT_SIGBUS;

    // 分配PMD页表
    if (pte_alloc(vma->vm_mm, vmf->pmd))
        return VM_FAULT_OOM;

    /* 读访问：使用零页(zero page) */
    if (!(vmf->flags & FAULT_FLAG_WRITE) &&
            !mm_forbids_zeropage(vma->vm_mm)) {
        entry = pte_mkspecial(pfn_pte(my_zero_pfn(vmf->address),
                        vma->vm_page_prot));
        vmf->pte = pte_offset_map_lock(vma->vm_mm, vmf->pmd,
                vmf->address, &vmf->ptl);
        if (!vmf->pte)
            goto unlock;
        if (vmf_pte_changed(vmf)) {
            update_mmu_tlb(vma, vmf->address, vmf->pte);
            goto unlock;
        }
        ret = check_stable_address_space(vma->vm_mm);
        if (ret)
            goto unlock;
        /* userfaultfd缺失处理 */
        if (userfaultfd_missing(vma)) {
            pte_unmap_unlock(vmf->pte, vmf->ptl);
            return handle_userfault(vmf, VM_UFFD_MISSING);
        }
        goto setpte;
    }

    /* 写访问：分配新的匿名页面 */
    ret = vmf_anon_prepare(vmf);
    if (ret)
        return ret;

    folio = alloc_anon_folio(vmf);
    if (IS_ERR(folio))
        return 0;
    if (!folio)
        goto oom;

    nr_pages = folio_nr_pages(folio);
    addr = ALIGN_DOWN(vmf->address, nr_pages * PAGE_SIZE);

    __folio_mark_uptodate(folio);

    entry = folio_mk_pte(folio, vma->vm_page_prot);
    entry = pte_sw_mkyoung(entry);
    if (vma->vm_flags & VM_WRITE)
        entry = pte_mkwrite(pte_mkdirty(entry), vma);

    vmf->pte = pte_offset_map_lock(vma->vm_mm, vmf->pmd, addr, &vmf->ptl);
    // ... 检查PTE变化

    folio_ref_add(folio, nr_pages - 1);
    add_mm_counter(vma->vm_mm, MM_ANONPAGES, nr_pages);
    folio_add_new_anon_rmap(folio, vma, addr, RMAP_EXCLUSIVE);
    folio_add_lru_vma(folio, vma);
setpte:
    if (vmf_orig_pte_uffd_wp(vmf))
        entry = pte_mkuffd_wp(entry);
    set_ptes(vma->vm_mm, addr, vmf->pte, entry, nr_pages);
    update_mmu_cache_range(vmf, vma, addr, vmf->pte, nr_pages);
unlock:
    if (vmf->pte)
        pte_unmap_unlock(vmf->pte, vmf->ptl);
    return ret;
oom:
    return VM_FAULT_OOM;
}
```

### 4.2 匿名页面分配：alloc_anon_folio

```c
// mm/memory.c:5127 附近
static struct folio *alloc_anon_folio(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct folio *folio;
    struct mem_cgroup *memcg;
    gfp_t gfp = vma_thp_gfp_mask(vma);

    // 尝试分配THP (Transparent Huge Page)
    if (thp_vma_allowable_orders(vma, vma->vm_flags, TVA_PAGEFAULT,
                     BIT(PMD_ORDER))) {
        folio = vma_alloc_folio(gfp, order, vma, vmf->address);
        if (folio)
            return folio;
    }

    // 回退到order-0页面
    return vma_alloc_folio(gfp, 0, vma, vmf->address);
}
```

---

## 5. do_fault - 文件映射缺页

**源码位置：** `mm/memory.c:5903`

### 5.1 核心分发

```c
// mm/memory.c:5903-5945
static vm_fault_t do_fault(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct mm_struct *vm_mm = vma->vm_mm;
    vm_fault_t ret;

    /* VMA没有fault回调且页表不存在 */
    if (!vma->vm_ops->fault) {
        vmf->pte = pte_offset_map_lock(vmf->vma->vm_mm, vmf->pmd,
                           vmf->address, &vmf->ptl);
        if (unlikely(!vmf->pte))
            ret = VM_FAULT_SIGBUS;
        else {
            if (unlikely(pte_none(ptep_get(vmf->pte))))
                ret = VM_FAULT_SIGBUS;
            else
                ret = VM_FAULT_NOPAGE;
            pte_unmap_unlock(vmf->pte, vmf->ptl);
        }
    } else if (!(vmf->flags & FAULT_FLAG_WRITE))
        ret = do_read_fault(vmf);      // 读错误
    else if (!(vma->vm_flags & VM_SHARED))
        ret = do_cow_fault(vmf);       // COW错误
    else
        ret = do_shared_fault(vmf);    // 共享映射错误

    if (vmf->prealloc_pte) {
        pte_free(vm_mm, vmf->prealloc_pte);
        vmf->prealloc_pte = NULL;
    }
    return ret;
}
```

### 5.2 do_read_fault - 读文件映射

```c
// mm/memory.c:5779-5809
static vm_fault_t do_read_fault(struct vm_fault *vmf)
{
    vm_fault_t ret = 0;
    struct folio *folio;

    /* 尝试fault-around优化 */
    if (should_fault_around(vmf)) {
        ret = do_fault_around(vmf);
        if (ret)
            return ret;
    }

    ret = vmf_can_call_fault(vmf);
    if (ret)
        return ret;

    ret = __do_fault(vmf);  // 调用vm_ops->fault
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY)))
        return ret;

    ret |= finish_fault(vmf);
    folio = page_folio(vmf->page);
    folio_unlock(folio);
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY)))
        folio_put(folio);
    return ret;
}
```

### 5.3 __do_fault - 调用文件系统的fault处理

```c
// mm/memory.c:5337-5391
static vm_fault_t __do_fault(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct folio *folio;
    vm_fault_t ret;

    // 预分配PTE页表（避免在持有锁时分配）
    if (pmd_none(*vmf->pmd) && !vmf->prealloc_pte) {
        vmf->prealloc_pte = pte_alloc_one(vma->vm_mm);
        if (!vmf->prealloc_pte)
            return VM_FAULT_OOM;
    }

    // 调用文件系统的fault处理
    ret = vma->vm_ops->fault(vmf);
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY |
                VM_FAULT_DONE_COW)))
        return ret;

    folio = page_folio(vmf->page);
    if (unlikely(PageHWPoison(vmf->page))) {
        // HWPoison处理...
    }

    if (unlikely(!(ret & VM_FAULT_LOCKED)))
        folio_lock(folio);
    else
        VM_BUG_ON_PAGE(!folio_test_locked(folio), vmf->page);

    return ret;
}
```

### 5.4 do_cow_fault - COW文件映射

```c
// mm/memory.c:5811-5851
static vm_fault_t do_cow_fault(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct folio *folio;
    vm_fault_t ret;

    ret = vmf_can_call_fault(vmf);
    if (!ret)
        ret = vmf_anon_prepare(vmf);
    if (ret)
        return ret;

    folio = folio_prealloc(vma->vm_mm, vma, vmf->address, false);
    if (!folio)
        return VM_FAULT_OOM;

    vmf->cow_page = &folio->page;

    ret = __do_fault(vmf);
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY)))
        goto uncharge_out;
    if (ret & VM_FAULT_DONE_COW)
        return ret;

    // 复制原页面内容到新页面
    if (copy_mc_user_highpage(vmf->cow_page, vmf->page, vmf->address, vma)) {
        ret = VM_FAULT_HWPOISON;
        goto unlock;
    }
    __folio_mark_uptodate(folio);

    ret |= finish_fault(vmf);
unlock:
    unlock_page(vmf->page);
    put_page(vmf->page);
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY)))
        goto uncharge_out;
    return ret;
uncharge_out:
    folio_put(folio);
    return ret;
}
```

### 5.5 do_shared_fault - 共享映射写错误

```c
// mm/memory.c:5853-5901
static vm_fault_t do_shared_fault(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    vm_fault_t ret, tmp;
    struct folio *folio;

    ret = vmf_can_call_fault(vmf);
    if (ret)
        return ret;

    ret = __do_fault(vmf);
    if (unlikely(ret & (VM_FAULT_ERROR | VM_FAULT_NOPAGE | VM_FAULT_RETRY)))
        return ret;

    folio = page_folio(vmf->page);

    // 通知文件系统页面即将变为可写
    if (vma->vm_ops->page_mkwrite) {
        folio_unlock(folio);
        tmp = do_page_mkwrite(vmf, folio);
        if (unlikely(!tmp || (tmp & (VM_FAULT_ERROR | VM_FAULT_NOPAGE)))) {
            folio_put(folio);
            return tmp;
        }
    }

    // 文件系统特定处理
    ret |= fault_dirty_shared_page(vmf);
    folio_unlock(folio);
    return ret;
}
```

---

## 6. do_swap_page - 交换空间缺页

**源码位置：** `mm/memory.c:4706`

### 6.1 核心实现

```c
// mm/memory.c:4706-4980
vm_fault_t do_swap_page(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct folio *swapcache = NULL, *folio;
    struct page *page;
    struct swap_info_struct *si = NULL;
    rmapi_t rmap_flags = RMAP_NONE;
    bool exclusive = false;
    softleaf_t entry;
    pte_t pte;
    vm_fault_t ret = 0;

    if (!pte_unmap_same(vmf))
        goto out;

    entry = softleaf_from_pte(vmf->orig_pte);

    // 处理特殊的PTE条目类型
    if (unlikely(!softleaf_is_swap(entry))) {
        if (softleaf_is_migration(entry)) {
            migration_entry_wait(vma->vm_mm, vmf->pmd, vmf->address);
        } else if (softleaf_is_device_exclusive(entry)) {
            vmf->page = softleaf_to_page(entry);
            ret = remove_device_exclusive_entry(vmf);
        } else if (softleaf_is_device_private(entry)) {
            // device private memory处理...
        } else if (softleaf_is_hwpoison(entry)) {
            ret = VM_FAULT_HWPOISON;
        } else if (softleaf_is_marker(entry)) {
            ret = handle_pte_marker(vmf);
        } else {
            print_bad_pte(vma, vmf->address, vmf->orig_pte, NULL);
            ret = VM_FAULT_SIGBUS;
        }
        goto out;
    }

    // 获取swap设备
    si = get_swap_device(entry);
    if (unlikely(!si))
        goto out;

    // 查找swap缓存
    folio = swap_cache_get_folio(entry);
    if (folio)
        swap_update_readahead(folio, vma, vmf->address);

    // 页面不在swap缓存中，需要读取
    if (!folio) {
        if (data_race(si->flags & SWP_SYNCHRONOUS_IO)) {
            // 同步IO：直接分配并读取
            folio = alloc_swap_folio(vmf);
            if (folio) {
                swapcache = swapin_folio(entry, folio);
                if (swapcache != folio)
                    folio_put(folio);
                folio = swapcache;
            }
        } else {
            // 异步IO：swapin并预读
            folio = swapin_readahead(entry, GFP_HIGHUSER_MOVABLE, vmf);
        }

        if (!folio) {
            vmf->pte = pte_offset_map_lock(vma->vm_mm, vmf->pmd,
                    vmf->address, &vmf->ptl);
            if (likely(vmf->pte && pte_same(ptep_get(vmf->pte), vmf->orig_pte)))
                ret = VM_FAULT_OOM;
            goto unlock;
        }

        // Major fault：页面需要从磁盘读取
        ret = VM_FAULT_MAJOR;
        count_vm_event(PGMAJFAULT);
    }

    swapcache = folio;
    ret |= folio_lock_or_retry(folio, vmf);
    if (ret & VM_FAULT_RETRY)
        goto out_release;

    page = folio_file_page(folio, swp_offset(entry));

    // KSM检查
    folio = ksm_might_need_to_copy(folio, vma, vmf->address);
    if (unlikely(!folio)) {
        ret = VM_FAULT_OOM;
        folio = swapcache;
        goto out_page;
    }

    // 加回swap PTE锁
    vmf->pte = pte_offset_map_lock(vma->vm_mm, vmf->pmd, vmf->address, &vmf->ptl);
    if (unlikely(!vmf->pte || !pte_same(ptep_get(vmf->pte), vmf->orig_pte)))
        goto out_nomap;

    // 设置PTE，将页面映射到虚拟地址
    // ... (省略大页面和exclusive检查)

    // 交换计费
    if ((vmf->flags & FAULT_FLAG_WRITE) &&
        !folio_test_ksm(folio) && !folio_test_lru(folio))
        lru_add_drain();

    folio_throttle_swaprate(folio, GFP_KERNEL);

    // 创建新的PTE
    swap_free(entry);
    if (folio_test_anon(folio) && !folio_test_swapcache(folio)) {
        folio_add_new_anon_rmap(folio, vma, vmf->address, RMAP_EXCLUSIVE);
        folio_add_lru_vma(folio, vma);
    } else {
        folio_add_file_rmap(folio, vma);
    }

    set_pte_at(vma->vm_mm, vmf->address, vmf->pte, mk_pte(page, vma->vm_page_prot));
    update_mmu_cache(vmf, vmf->address, vmf->pte);
    // ...
}
```

---

## 7. do_wp_page - COW机制

**源码位置：** `mm/memory.c:4149`

### 7.1 COW机制概述

Copy-On-Write (COW) 是一种延迟复制技术。当多个进程共享同一个页面时，内核不会立即复制页面，而是将页面标记为只读。当某个进程试图写入共享页面时，才会触发COW，创建一个新的页面副本。

### 7.2 核心实现

```c
// mm/memory.c:4149-4242
static vm_fault_t do_wp_page(struct vm_fault *vmf)
    __releases(vmf->ptl)
{
    const bool unshare = vmf->flags & FAULT_FLAG_UNSHARE;
    struct vm_area_struct *vma = vmf->vma;
    struct folio *folio = NULL;
    pte_t pte;

    // userfaultfd写保护处理
    if (likely(!unshare)) {
        if (userfaultfd_pte_wp(vma, ptep_get(vmf->pte))) {
            if (!userfaultfd_wp_async(vma)) {
                pte_unmap_unlock(vmf->pte, vmf->ptl);
                return handle_userfault(vmf, VM_UFFD_WP);
            }
            pte = pte_clear_uffd_wp(ptep_get(vmf->pte));
            set_pte_at(vma->vm_mm, vmf->address, vmf->pte, pte);
            vmf->orig_pte = pte;
        }
    }

    vmf->page = vm_normal_page(vma, vmf->address, vmf->orig_pte);
    if (vmf->page)
        folio = page_folio(vmf->page);

    /* ========== 共享映射处理 ========== */
    if (vma->vm_flags & (VM_SHARED | VM_MAYSHARE)) {
        // 混合映射或FS DAX：标记为可写
        if (!vmf->page || is_fsdax_page(vmf->page)) {
            vmf->page = NULL;
            return wp_pfn_shared(vmf);
        }
        return wp_page_shared(vmf, folio);
    }

    /* ========== 私有映射处理 ========== */
    // 检查页面是否可以复用（匿名页面且exclusive）
    if (folio && folio_test_anon(folio) &&
        (PageAnonExclusive(vmf->page) || wp_can_reuse_anon_folio(folio, vma))) {
        if (!PageAnonExclusive(vmf->page))
            SetPageAnonExclusive(vmf->page);
        if (unlikely(unshare)) {
            pte_unmap_unlock(vmf->pte, vmf->ptl);
            return 0;
        }
        wp_page_reuse(vmf, folio);  // 复用现有页面
        return 0;
    }

    /* ========== 需要复制页面 ========== */
    if (folio)
        folio_get(folio);

    pte_unmap_unlock(vmf->pte, vmf->ptl);
#ifdef CONFIG_KSM
    if (folio && folio_test_ksm(folio))
        count_vm_event(COW_KSM);
#endif
    return wp_page_copy(vmf);  // 执行页面复制
}
```

### 7.3 wp_page_reuse - 页面复用

```c
// mm/memory.c:3664-3698
static inline void wp_page_reuse(struct vm_fault *vmf, struct folio *folio)
{
    struct vm_area_struct *vma = vmf->vma;

    VM_BUG_ON(!(vmf->flags & FAULT_FLAG_WRITE));

    // 标记页面为脏和年轻
    entry = pte_mkdirty(pte_mkyoung(vmf->orig_pte));
    // 如果VMA允许，设置PTE为可写
    if (vma->vm_flags & VM_WRITE)
        entry = pte_mkwrite(entry);

    // 更新PTE
    ptep_set_access_flags(vma, vmf->address, vmf->pte, entry,
                  vmf->flags & FAULT_FLAG_WRITE);
    update_mmu_cache(vmf, vmf->address, vmf->pte);
}
```

### 7.4 wp_page_copy - 页面复制

```c
// mm/memory.c:3758-3924
static vm_fault_t wp_page_copy(struct vm_fault *vmf)
{
    const bool unshare = vmf->flags & FAULT_FLAG_UNSHARE;
    struct vm_area_struct *vma = vmf->vma;
    struct folio *folio = NULL;
    struct folio *new_folio = NULL;
    pte_t entry;
    vm_fault_t ret;

    // 分配新的匿名页面
    if (likely(!unshare)) {
        ret = vmf_anon_prepare(vmf);
        if (ret)
            return ret;

        new_folio = alloc_anon_folio(vmf);
        if (IS_ERR(new_folio))
            return 0;
        if (!new_folio)
            return VM_FAULT_OOM;
    }

    // 获取原页面
    folio = page_folio(vmf->page);

    // 复制页面内容
    if (copy_mc_user_highpage(&new_folio->page, vmf->page, vmf->address, vma)) {
        ret = VM_FAULT_HWPOISON;
        goto release;
    }
    __folio_mark_uptodate(new_folio);

    // 获取PTE锁并更新
    vmf->pte = pte_offset_map_lock(vma->vm_mm, vmf->pmd, vmf->address, &vmf->ptl);
    if (unlikely(!vmf->pte || !pte_same(ptep_get(vmf->pte), vmf->orig_pte)))
        goto release;

    // 标记新页面为exclusive
    SetPageAnonExclusive(&new_folio->page);

    // 更新进程页表
    entry = mk_pte(&new_folio->page, vma->vm_page_prot);
    entry = pte_mkyoung(entry);
    if (vma->vm_flags & VM_WRITE)
        entry = pte_mkwrite(pte_mkdirty(entry));

    folio_add_new_anon_rmap(new_folio, vma, vmf->address, RMAP_EXCLUSIVE);
    folio_add_lru_vma(new_folio, vma);

    set_pte_at(vma->vm_mm, vmf->address, vmf->pte, entry);
    update_mmu_cache(vmf, vmf->address, vmf->pte);

    // 释放原页面引用
    if (folio)
        folio_put(folio);

release:
    if (new_folio)
        folio_put(new_folio);
    if (vmf->pte)
        pte_unmap_unlock(vmf->pte, vmf->ptl);
    return ret;
}
```

---

## 8. vm_fault结构体和fault_flag

### 8.1 vm_fault结构体

**源码位置：** `include/linux/mm.h:698`

```c
struct vm_fault {
    const struct {
        struct vm_area_struct *vma;    /* 目标VMA */
        gfp_t gfp_mask;                /* 分配内存的gfp掩码 */
        pgoff_t pgoff;                /* 基于vma的逻辑页面偏移 */
        unsigned long address;         /* 故障虚拟地址 - 已掩码 */
        unsigned long real_address;    /* 故障虚拟地址 - 未掩码 */
    };
    enum fault_flag flags;            /* FAULT_FLAG_xxx 标志 */

    pmd_t *pmd;                       /* 指向匹配address的PMD条目 */
    pud_t *pud;                       /* 指向匹配address的PUD条目 */

    union {
        pte_t orig_pte;               /* 故障时刻PTE的值 */
        pmd_t orig_pmd;               /* 故障时刻PMD的值（仅PMD故障使用） */
    };

    struct page *cow_page;            /* COW错误使用的页面 */
    struct page *page;                /* ->fault处理程序应返回的页面 */

    /* 以下条目在持有ptl锁时有效 */
    pte_t *pte;                       /* 指向匹配address的PTE条目 */
    spinlock_t *ptl;                  /* 页表锁 */
    pgtable_t prealloc_pte;           /* 预分配的PTE页表 */
};
```

### 8.2 fault_flag枚举

**源码位置：** `include/linux/mm_types.h:1735`

```c
enum fault_flag {
    FAULT_FLAG_WRITE =         1 << 0,   /* 写访问错误 */
    FAULT_FLAG_MKWRITE =       1 << 1,   /* 对现有PTE的mkwrite */
    FAULT_FLAG_ALLOW_RETRY =   1 << 2,   /* 允许重试 */
    FAULT_FLAG_RETRY_NOWAIT =  1 << 3,   /* 重试时不等待 */
    FAULT_FLAG_KILLABLE =      1 << 4,   /* 任务处于SIGKILL可杀死区域 */
    FAULT_FLAG_TRIED =         1 << 5,   /* 已尝试过一次 */
    FAULT_FLAG_USER =          1 << 6,   /* 源自用户空间 */
    FAULT_FLAG_REMOTE =        1 << 7,   /* 非当前任务/mm的错误 */
    FAULT_FLAG_INSTRUCTION =   1 << 8,   /* 指令获取期间的错误 */
    FAULT_FLAG_INTERRUPTIBLE = 1 << 9,   /* 可被非致命信号中断 */
    FAULT_FLAG_UNSHARE =       1 << 10,  /* COW映射中解除共享请求 */
    FAULT_FLAG_ORIG_PTE_VALID = 1 << 11, /* orig_pte是否有效 */
    FAULT_FLAG_VMA_LOCK =      1 << 12,  /* 在VMA锁下处理 */
};
```

### 8.3 vm_fault_t返回值

```c
typedef unsigned int vm_fault_t;

/* 成功 */
#define VM_FAULT_OK         0x0000
#define VM_FAULT_DONE_COW   0x0010  /* COW完成 */
#define VM_FAULT_MAJOR      0x0020  /* Major fault */

/* 重试（需要释放锁后重试）*/
#define VM_FAULT_RETRY      0x4000
#define VM_FAULT_COMPLETED  0x8000  /* 错误处理完成 */

/* 错误 */
#define VM_FAULT_NOPAGE     0x0001  /* 页面已存在，不需映射 */
#define VM_FAULT_LOCKED     0x0002  /* 页面已锁定 */
#define VM_FAULT_OOM        0x0004  /* 内存不足 */
#define VM_FAULT_SIGSEGV    0x0008  /* SIGSEGV */
#define VM_FAULT_SIGBUS     0x0010  /* SIGBUS */
#define VM_FAULT_HWPOISON   0x0100  /* 硬件内存错误 */
#define VM_FAULT_HWPOISON_LARGE 0x0200  /* 大页硬件错误 */
#define VM_FAULT_ERROR      (VM_FAULT_OOM | VM_FAULT_SIGSEGV | \
                             VM_FAULT_SIGBUS | VM_FAULT_HWPOISON | \
                             VM_FAULT_HWPOISON_LARGE)
```

---

## 9. vm_operations_struct 回调

**源码位置：** `include/linux/mm.h:749`

### 9.1 结构体定义

```c
struct vm_operations_struct {
    void (*open)(struct vm_area_struct *area);
    void (*close)(struct vm_area_struct *area);
    int (*may_split)(struct vm_area_struct *area, unsigned long addr);
    int (*mremap)(struct vm_area_struct *area);

    int (*mprotect)(struct vm_area_struct *vma, unsigned long start,
            unsigned long end, unsigned long newflags);

    /* 页面错误处理 */
    vm_fault_t (*fault)(struct vm_fault *vmf);
    vm_fault_t (*huge_fault)(struct vm_fault *vmf, unsigned int order);

    /* 预读优化 */
    vm_fault_t (*map_pages)(struct vm_fault *vmf,
            pgoff_t start_pgoff, pgoff_t end_pgoff);

    unsigned long (*pagesize)(struct vm_area_struct *area);

    /* 页面即将变为可写时的通知 */
    vm_fault_t (*page_mkwrite)(struct vm_fault *vmf);

    /* VM_PFNMAP|VM_MIXEDMAP的page_mkwrite等效 */
    vm_fault_t (*pfn_mkwrite)(struct vm_fault *vmf);

    int (*access)(struct vm_area_struct *vma, unsigned long addr,
              void *buf, int len, int write);

    const char *(*name)(struct vm_area_struct *vma);
};
```

### 9.2 核心回调详解

#### 9.2.1 fault - 主页面错误处理

```c
// 典型实现：filemap_fault (mm/filemap.c)
vm_fault_t filemap_fault(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct file *file = vma->vm_file;
    struct address_space *mapping = file->f_mapping;
    struct inode *inode = mapping->host;
    struct page *page;
    vm_fault_t ret;

    // 查找页面是否已在页面缓存中
    page = find_get_page(mapping, vmf->pgoff);
    if (likely(page && !PageError(page))) {
        // 页面已缓存，锁定并返回
        folio_lock(page_folio(page));
        ret = VM_FAULT_LOCKED;
    } else {
        // 页面不在缓存，需要读取
        page = NULL;
        ret = filemap_create_folio(vmf);
        if (!page)
            return VM_FAULT_SIGBUS;
    }

    vmf->page = page;
    return ret | VM_FAULT_MAJOR;
}
```

#### 9.2.2 page_mkwrite - 页面即将可写

```c
// 典型实现：ext4_page_mkwrite (fs/ext4/inode.c)
vm_fault_t ext4_page_mkwrite(struct vm_fault *vmf)
{
    struct vm_area_struct *vma = vmf->vma;
    struct inode *inode = file_inode(vma->vm_file);

    // 确保ext4日志准备好
    lock_page(vmf->page);
    ret = ext4_bh_state_try(inode, vmf->page);
    if (ret)
        return ret;

    // 等待页面正在进行的IO完成
    wait_on_page_writeback(vmf->page);
    return VM_FAULT_LOCKED;
}
```

#### 9.2.3 map_pages - 预读优化

```c
// 典型实现：filemap_map_pages (mm/filemap.c)
vm_fault_t filemap_map_pages(struct vm_fault *vmf,
        pgoff_t start_pgoff, pgoff_t end_pgoff)
{
    // 批量映射页面到页表，减少major fault次数
    // 实现fault-around优化
}
```

---

## 完整缺页中断流程图

```
+-----------------+
| CPU执行指令     |
| 访问虚拟地址    |
+--------+--------+
         |
         v
+-----------------+
| MMU查找页表    |
| 页面不存在/权限 |
| 不足?           |
+--------+--------+
         |
         | Yes
         v
+------------------+
| #PF 异常触发     |
| (exc_page_fault) |
| arch/x86/mm/     |
| fault.c:1483     |
+---------+--------+
          |
          v
+-------------------+
| handle_page_      |
| fault()           |
| fault.c:1461      |
+---------+---------+
          |
          v
+----------+-------------------------+
| address in kernel space?          |
+---------+-------------------------+
          |                    |
          | Yes                 | No
          v                     v
+-------------------+    +-------------------+
| do_kern_addr_    |    | do_user_addr_    |
| fault()          |    | fault()          |
| fault.c:1134     |    | fault.c:1206     |
+---------+--------+    +---------+---------+
          |                     |
          |                     v
          |            +-------------------+
          |            | 检查error_code    |
          |            | access_error()    |
          |            | fault.c:1048      |
          |            +---------+---------+
          |                      |
          |                      v
          |            +-------------------+
          |            | handle_mm_fault() |
          |            | mm/memory.c:6589  |
          |            +---------+---------+
          |                      |
          v                      v
+-------------------+    +-------------------+
| 处理内核空间     |    | __handle_mm_fault |
| 地址错误          |    | mm/memory.c:6355 |
+---------+--------+    +---------+---------+
          |                      |
          |                      v
          |            +-------------------+
          |            | handle_pte_fault()|
          |            | mm/memory.c:6273  |
          |            +---------+---------+
          |                      |
          v                      v
+-------------------+    +-------------------+
| vmalloc_fault()   |    | pmd_none?         |
| 同步vmalloc映射   |    +---------+---------+
+---------+--------+          |            |
          |            No    | Yes        |
          |                  v            v
          |         +---------+-------+  +-------------------+
          |         | pte_present?     |  | do_pte_missing() |
          |         +---------+-------+  | mm/memory.c:4472 |
          |                  |            +---------+---------+
          |                  |                      |
    +-----+------+   +-------+------+        +-------+-------+
    |No swap entry|  | Has swap entry|      |vma_is_anon?   |
    |(页面在内存) |  | (页面被swap)  |      +-------+-------+
    +-----+------+   +-------+------+              |       |
          |                  |              Yes   |       | No
          v                  v                    v       v
+-------------------+ +------------------+ +---------+ +--------+
| do_wp_page()      | | do_swap_page()   | |do_anon_ | |do_fault|
| COW处理           | | 交换空间换入     | |page()   | |文件映射|
| memory.c:4149     | | memory.c:4706    | |5217     | |5903    |
+---------+---------+ +---------+---------+----+----+ +----+----+
          |                   |                   |         |
          +---------+---------+                   +-----+---+
                    |                                 |
                    v                                 v
          +---------------------+        +-----------------------+
          | finish_fault()      |        | __do_fault()           |
          | 完成PTE设置        |        | 调用vm_ops->fault()    |
          | memory.c:5556      |        | memory.c:5337          |
          +---------+----------+        +---------+-------------+
                    |                               |
                    v                               v
          +---------------------+        +-----------------------+
          | update_mmu_cache()  |        | finish_fault()         |
          | 更新TLB             |        | 完成PTE设置             |
          +---------------------+        +---------+-------------+
                                          |
                                          v
                                +---------------------+
                                | 返回vm_fault_t      |
                                | 错误处理/重试      |
                                +---------------------+
```

### 详细错误流程

```
handle_pte_fault()
    |
    +-- pmd_none(*pmd) --> do_pte_missing()
    |                         |
    |                         +-- vma_is_anonymous() --> do_anonymous_page()
    |                         |                                      |
    |                         |                                      +-- 读访问 --> zero page
    |                         |                                      +-- 写访问 --> alloc_anon_folio()
    |                         |
    |                         +-- !vma_is_anonymous() --> do_fault()
    |                                                                |
    |                                                                +-- !vm_ops->fault --> SIGBUS
    |                                                                +--读访问 --> do_read_fault()
    |                                                                |           __do_fault() --> vm_ops->fault()
    |                                                                +--写COW --> do_cow_fault()
    |                                                                |           alloc folio, copy page
    |                                                                +--写共享 --> do_shared_fault()
    |
    +-- !pte_present(orig_pte) --> do_swap_page()
    |                         |
    |                         +-- softleaf_is_swap() --> swapin from disk
    |                         +-- softleaf_is_migration() --> migration_entry_wait()
    |                         +-- softleaf_is_device_* --> device specific
    |
    +-- pte_protnone() --> do_numa_page() [NUMA迁移]
    |
    +-- FAULT_FLAG_WRITE && !pte_write() --> do_wp_page()
                                            |
                                            +-- 共享映射 --> wp_page_shared()
                                            |                    |
                                            |                    +-- vm_ops->page_mkwrite()
                                            |
                                            +-- 私有映射可复用 --> wp_page_reuse()
                                            |
                                            +-- 私有映射需复制 --> wp_page_copy()
                                                             |
                                                             +-- alloc_anon_folio()
                                                             +-- copy_mc_user_highpage()
                                                             +-- set_pte_at()
```

---

## 关键源码位置索引

| 函数 | 文件 | 行号 |
|------|------|------|
| exc_page_fault | arch/x86/mm/fault.c | 1483 |
| handle_page_fault | arch/x86/mm/fault.c | 1461 |
| do_kern_addr_fault | arch/x86/mm/fault.c | 1134 |
| do_user_addr_fault | arch/x86/mm/fault.c | 1206 |
| access_error | arch/x86/mm/fault.c | 1048 |
| handle_mm_fault | mm/memory.c | 6589 |
| __handle_mm_fault | mm/memory.c | 6355 |
| handle_pte_fault | mm/memory.c | 6273 |
| do_pte_missing | mm/memory.c | 4472 |
| do_anonymous_page | mm/memory.c | 5217 |
| do_fault | mm/memory.c | 5903 |
| do_read_fault | mm/memory.c | 5779 |
| do_cow_fault | mm/memory.c | 5811 |
| do_shared_fault | mm/memory.c | 5853 |
| __do_fault | mm/memory.c | 5337 |
| finish_fault | mm/memory.c | 5556 |
| do_swap_page | mm/memory.c | 4706 |
| do_wp_page | mm/memory.c | 4149 |
| wp_page_reuse | mm/memory.c | 3664 |
| wp_page_copy | mm/memory.c | 3758 |
| alloc_anon_folio | mm/memory.c | 5127 |
| struct vm_fault | include/linux/mm.h | 698 |
| enum fault_flag | include/linux/mm_types.h | 1735 |
| struct vm_operations_struct | include/linux/mm.h | 749 |
| filemap_fault | mm/filemap.c | (约3927) |

---

## 参考文档

- `arch/x86/mm/fault.c` - x86页面错误处理
- `mm/memory.c` - 通用页面错误处理
- `include/linux/mm.h` - 内存管理核心数据结构
- `include/linux/mm_types.h` - 页错误标志定义
- `Documentation/vm/page_migration.rst` - 页面迁移
- `Documentation/admin-guide/mm/userfaultfd.rst` - userfaultfd机制
