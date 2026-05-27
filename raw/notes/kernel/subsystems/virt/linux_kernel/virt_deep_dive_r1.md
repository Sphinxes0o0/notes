# Linux Virt/KVM 子系统深度分析 R1

## 目录
1. [KVM Core: struct kvm 与虚拟机生命周期管理](#1-kvm-core-struct-kvm-与虚拟机生命周期管理)
2. [vCPU: struct kvm_vcpu 与虚拟处理器](#2-vcpu-struct-kvm_vcpu-与虚拟处理器)
3. [MMU/EPT: 内存虚拟化与页表管理](#3-mmuept-内存虚拟化与页表管理)
4. [KVM_RUN: vCPU 运行循环与退出处理](#4-kvm_run-vcpu-运行循环与退出处理)
5. [Dirty Ring: 脏页追踪机制](#5-dirty-ring-脏页追踪机制)
6. [guest_memfd: 私有内存管理](#6-guest_memfd-私有内存管理)
7. [知识点关联表](#7-知识点关联表)

---

## 1. KVM Core: struct kvm 与虚拟机生命周期管理

### 1.1 核心数据结构 struct kvm

**源码位置**: `/Users/sphinx/github/linux/include/linux/kvm_host.h` 第769-878行

```c
struct kvm {
    // MMU锁 - 保护影子页表
#ifdef KVM_HAVE_MMU_RWLOCK
    rwlock_t mmu_lock;        // 读写锁，支持并发读
#else
    spinlock_t mmu_lock;      // 某些架构使用自旋锁
#endif

    // 内存槽锁
    struct mutex slots_lock;
    struct mutex slots_arch_lock;
    
    // 关联的用户空间进程
    struct mm_struct *mm;     // 用户空间绑定
    unsigned long nr_memslot_pages;
    
    // 内存槽 - 双缓冲设计
    struct kvm_memslots __memslots[KVM_MAX_NR_ADDRESS_SPACES][2];
    struct kvm_memslots __rcu *memslots[KVM_MAX_NR_ADDRESS_SPACES];
    
    // vCPU数组
    struct xarray vcpu_array;  // 高效的vCPU存储
    atomic_t online_vcpus;
    int max_vcpus;
    int created_vcpus;
    
    // MMU notifier - 宿主机关页表变更通知
    struct mmu_notifier mmu_notifier;        // 第850行
    unsigned long mmu_invalidate_seq;
    long mmu_invalidate_in_progress;
    gfn_t mmu_invalidate_range_start;
    gfn_t mmu_invalidate_range_end;
    
    // 脏环相关
    u32 dirty_ring_size;
    bool dirty_ring_with_bitmap;
    
    // 统计与调试
    struct kvm_vm_stat stat;
    struct kvm_arch arch;
    struct dentry *debugfs_dentry;
    
    // 源RCU锁 - 用于内存槽迭代
    struct srcu_struct srcu;
    struct srcu_struct irq_srcu;
};
```

### 1.2 kvm_create_vm() 虚拟机创建流程

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c` 第1105-1214行

```c
static struct kvm *kvm_create_vm(unsigned long type, const char *fdname)
{
    // 1. 分配KVM结构
    struct kvm *kvm = kvm_arch_alloc_vm();  // 第1107行
    
    // 2. 初始化多层次锁
    KVM_MMU_LOCK_INIT(kvm);
    mutex_init(&kvm->lock);
    mutex_init(&kvm->slots_lock);
    spin_lock_init(&kvm->mn_invalidate_lock);  // MMU notifier锁
    
    // 3. 初始化数据结构
    xa_init(&kvm->vcpu_array);
    xa_init(&kvm->mem_attr_array);  // 内存属性
    
    // 4. 初始化源RCU结构
    init_srcu_struct(&kvm->srcu);      // 第1147行
    init_srcu_struct(&kvm->irq_srcu);  // 第1149行
    
    // 5. 初始化内存槽双缓冲
    for (i = 0; i < kvm_arch_nr_memslot_as_ids(kvm); i++) {
        for (j = 0; j < 2; j++) {
            slots = &kvm->__memslots[i][j];
            slots->hva_tree = RB_ROOT_CACHED;
            slots->gfn_tree = RB_ROOT;
            hash_init(slots->id_hash);
        }
    }
    
    // 6. 注册MMU notifier (第850行关联)
    // mmu_notifier.ops = &kvm_mmu_notifier_ops;
    
    // 7. 创建debugfs条目
    kvm_create_vm_debugfs(kvm, fdname);  // 第1203行
    
    // 8. 加入全局虚拟机链表
    list_add(&kvm->vm_list, &vm_list);  // 第1208行
    
    return kvm;
}
```

### 1.3 kvm_destroy_vm() 虚拟机销毁流程

**关键步骤**:
1. 从全局链表移除: `list_del(&kvm->vm_list)`
2. 注销MMU notifier: `mmu_notifier_unregister(&kvm->mmu_notifier, mm)`
3. 销毁所有vCPU: `kvm_destroy_vcpus(kvm)`
4. 刷新所有影子页表: `kvm_arch_flush_shadow_all(kvm)`
5. 释放内存槽: `kvm_free_irq_routing(kvm)`
6. 清理debugfs

### 1.4 mmu_notifier 机制

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c` 第505-895行

```c
// MMU notifier到kvm的转换 (第505行)
static inline struct kvm *mmu_notifier_to_kvm(struct mmu_notifier *mn)
{
    return container_of(mn, struct kvm, mmu_notifier);
}

// notifier操作集 (第888-895行)
static const struct mmu_notifier_ops kvm_mmu_notifier_ops = {
    .invalidate_range_start  = kvm_mmu_notifier_invalidate_range_start, // 第726行
    .invalidate_range_end    = kvm_mmu_notifier_invalidate_range_end,   // 第802行
    .clear_flush_young       = kvm_mmu_notifier_clear_flush_young,      // 第833行
    .clear_young            = kvm_mmu_notifier_clear_young,            // 第844行
    .test_young             = kvm_mmu_notifier_test_young,              // 第867行
    .release                = kvm_mmu_notifier_release,                 // 第877行
};
```

---

## 2. vCPU: struct kvm_vcpu 与虚拟处理器

### 2.1 核心数据结构 struct kvm_vcpu

**源码位置**: `/Users/sphinx/github/linux/include/linux/kvm_host.h` 第324-400行

```c
struct kvm_vcpu {
    struct kvm *kvm;                    // 所属虚拟机
    
    // vCPU标识
    int cpu;                            // 当前运行的物理CPU
    int vcpu_id;                       // 用户空间分配的ID
    int vcpu_idx;                      // 在vcpu_array中的索引
    
    // 运行模式状态机
    int mode;                          // OUTSIDE_GUEST_MODE/IN_GUEST_MODE/EXITING_GUEST_MODE
    u64 requests;                       // 待处理请求位掩码
    
    // 执行上下文
    struct mutex mutex;
    struct kvm_run *run;               // 与用户空间共享的运行状态
    
    // 暂停相关
    unsigned int halt_poll_ns;         // 暂停轮询超时
    bool valid_wakeup;
    bool wants_to_run;
    bool preempted;
    
    // 架构特定数据
    struct kvm_vcpu_arch arch;         // x86: MSR, CR, APIC等
    struct kvm_vcpu_stat stat;         // 统计信息
    
    // 脏环
    struct kvm_dirty_ring dirty_ring;   // 第390行
    
    // 最近使用的内存槽缓存
    struct kvm_memory_slot *last_used_slot;
    u64 last_used_slot_gen;
};
```

**模式状态机**:
```
                    ┌──────────────────┐
                    │ OUTSIDE_GUEST_MODE│
                    └────────┬─────────┘
                             │ vcpu_load()
                             ▼
┌──────────────────┐   ┌─────────────┐   ┌─────────────────────┐
│READING_SHADOW_PT │◄──│IN_GUEST_MODE│──►│EXITING_GUEST_MODE   │
└──────────────────┘   └──────┬──────┘   └─────────────────────┘
                              │ VM-Exit
                              ▼
                    ┌──────────────────┐
                    │ handle_exit()   │
                    └──────────────────┘
```

### 2.2 vCPU创建 kvm_vcpu_create()

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c` (间接通过kvm_arch_vcpu_create)

**x86实现** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 第12736-12780行:

```c
int kvm_arch_vcpu_create(struct kvm_vcpu *vcpu)
{
    // 1. 初始化vCPU状态
    vcpu->arch.last_vmentry_cpu = -1;
    vcpu->arch.regs_avail = ~0;
    vcpu->arch.regs_dirty = ~0;
    
    // 2. 初始化 pv_time gfn_to_pfn_cache
    kvm_gpc_init(&vcpu->arch.pv_time, vcpu->kvm);  // 第12745行
    
    // 3. 设置初始MP状态
    if (!irqchip_in_kernel(vcpu->kvm) || kvm_vcpu_is_reset_bsp(vcpu))
        kvm_set_mp_state(vcpu, KVM_MP_STATE_RUNNABLE);
    else
        kvm_set_mp_state(vcpu, KVM_MP_STATE_UNINITIALIZED);
    
    // 4. 创建MMU结构
    kvm_mmu_create(vcpu);  // 第12752行
    
    // 5. 创建本地APIC
    kvm_create_lapic(vcpu);  // 第12756行
    
    // 6. 分配PIO数据页
    page = alloc_page(GFP_KERNEL_ACCOUNT | __GFP_ZERO);
    vcpu->arch.pio_data = page_address(page);  // 第12765行
    
    // 7. 分配MCE银行
    vcpu->arch.mce_banks = kcalloc(KVM_MAX_MCE_BANKS * 4, sizeof(u64), ...);
    
    // 8. 分配脏环
    if (kvm->dirty_ring_size)
        kvm_dirty_ring_alloc(kvm, &vcpu->dirty_ring, ...);
}
```

### 2.3 kvm_vcpu_run() vCPU运行循环

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 第11533-11710行 (vcpu_run函数)

**核心循环结构**:
```c
// vcpu_run 伪代码
for (;;) {
    // 检查阻塞
    if (!kvm_arch_vcpu_runnable(vcpu)) {
        // 切换到软件定时器
        if (kvm_lapic_hv_timer_in_use(vcpu))
            kvm_lapic_switch_to_sw_timer(vcpu);
        
        // 阻塞vCPU
        if (vcpu->arch.mp_state == KVM_MP_STATE_HALTED)
            kvm_vcpu_halt(vcpu);
        else
            kvm_vcpu_block(vcpu);
        
        // 唤醒后检查事件
        if (!kvm_arch_vcpu_runnable(vcpu))
            continue;
    }
    
    // 进入客户机模式
    if (kvm_vcpu_running(vcpu)) {
        r = vcpu_enter_guest(vcpu);  // 第11677行 - VM-Entry
    } else {
        r = vcpu_block(vcpu);       // 处理阻塞
    }
    
    if (r <= 0) break;
    
    // 处理退出事件
    if (kvm_check_request(KVM_REQ_UNBLOCK, vcpu)) ...
    if (kvm_xen_has_pending_events(vcpu)) ...
    if (kvm_cpu_has_pending_timer(vcpu)) ...
    if (dm_request_for_irq_injection(vcpu)) {
        vcpu->run->exit_reason = KVM_EXIT_IRQ_WINDOW_OPEN;
        break;
    }
}
```

### 2.4 kvm_skip_emulated_instruction()

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 第9243-9265行

```c
int kvm_skip_emulated_instruction(struct kvm_vcpu *vcpu)
{
    unsigned long rflags = kvm_x86_call(get_rflags)(vcpu);
    int r;
    
    // 调用架构特定的跳过指令函数
    r = kvm_x86_call(skip_emulated_instruction)(vcpu);
    if (unlikely(!r))
        return 0;
    
    // 更新PMU指令计数
    kvm_pmu_instruction_retired(vcpu);
    
    // 处理单步调试
    if (unlikely(rflags & X86_EFLAGS_TF))
        r = kvm_vcpu_do_singlestep(vcpu);
    return r;
}
```

---

## 3. MMU/EPT: 内存虚拟化与页表管理

### 3.1 核心数据结构

**struct kvm_mmu_page** `/Users/sphinx/github/linux/arch/x86/kvm/mmu/mmu_internal.h` 第44-141行:

```c
struct kvm_mmu_page {
    struct list_head link;              // 全局页表链表
    struct hlist_node hash_link;       // 哈希链表
    
    bool tdp_mmu_page;                 // 是否为TDP MMU页
    bool unsync;                       // 是否未同步到CPU
    
    union kvm_mmu_page_role role;      // 页表角色 (级别,模式等)
    gfn_t gfn;                         // 关联的客户机帧号
    
    u64 *spt;                          // 影子页表页 (Shadow Page Table)
    
    // 用于TDP MMU的引用计数
    union {
        int root_count;
        refcount_t tdp_mmu_root_count;
    };
    
    union {
        struct {
            unsigned int unsync_children;
            atomic_t write_flooding_count;
        };
        void *external_spt;            // TDX外部页表
    };
    
    // 父页表指针链表
    struct kvm_rmap_head parent_ptes;
    DECLARE_BITMAP(unsync_child_bitmap, 512);
};
```

**struct tdp_iter** `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_iter.h` 第76-117行:

```c
struct tdp_iter {
    gfn_t next_last_level_gfn;        // 下一个最后级别GFN
    gfn_t yielded_gfn;                // 上次让出时的GPN
    
    // 页表遍历路径
    tdp_ptep_t pt_path[PT64_ROOT_MAX_LEVEL];  // 各级页表指针
    tdp_ptep_t sptep;                 // 当前SPTE指针
    
    gfn_t gfn;                        // 当前GPN
    gfn_t gfn_bits;                  // GPN掩码位
    
    int root_level;                   // 根级别
    int min_level;                    // 最小遍历级别
    int level;                        // 当前级别
    int as_id;                        // 地址空间ID
    
    u64 old_spte;                     // 修改前的SPTE值
    
    bool valid;                       // 迭代器是否有效
    bool yielded;                     // 是否在遍历中让出过CPU
};
```

### 3.2 ept_set_spte() / TDP页表设置

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_mmu.c` 第650-700行:

```c
// 原子设置SPTE (第650行)
static inline int __must_check __tdp_mmu_set_spte_atomic(struct kvm *kvm,
                                                         struct tdp_iter *iter,
                                                         u64 new_spte)
{
    WARN_ON_ONCE(iter->yielded || is_frozen_spte(iter->old_spte));
    
    // 对mirror页表进行处理
    if (is_mirror_sptep(iter->sptep) && !is_frozen_spte(new_spte)) {
        // mirror页表用于TDX
        ...
    }
    
    // 使用原子cmpxchg设置SPTE
    return cmpxchg64(iter->sptep, iter->old_spte, new_spte) != iter->old_spte;
}

// 批量设置SPTE (第772行)
static inline void tdp_mmu_iter_set_spte(struct kvm *kvm, struct tdp_iter *iter,
                                         u64 new_spte)
{
    WARN_ON_ONCE(iter->yielded);
    iter->old_spte = tdp_mmu_set_spte(kvm, iter->as_id, iter->sptep,
                                       iter->old_spte, new_spte,
                                       iter->gfn, iter->level);
}
```

### 3.3 kvm_mmu_unload() MMU卸载

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/mmu.c` 第6083-6092行:

```c
void kvm_mmu_unload(struct kvm_vcpu *vcpu)
{
    struct kvm *kvm = vcpu->kvm;
    
    // 释放root_mmu的所有根页
    kvm_mmu_free_roots(kvm, &vcpu->arch.root_mmu, KVM_MMU_ROOTS_ALL);
    WARN_ON_ONCE(VALID_PAGE(vcpu->arch.root_mmu.root.hpa));
    
    // 释放guest_mmu的所有根页
    kvm_mmu_free_roots(kvm, &vcpu->arch.guest_mmu, KVM_MMU_ROOTS_ALL);
    WARN_ON_ONCE(VALID_PAGE(vcpu->arch.guest_mmu.root.hpa));
    
    // 清除MMIO信息
    vcpu_clear_mmio_info(vcpu, MMIO_GVA_ANY);
}
```

### 3.4 TDP (Top-Down Level) 页表遍历

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_mmu.c` 第1168-1223行:

```c
// TDP MMU映射处理 (第1168行)
static int tdp_mmu_map_handle_target_level(struct kvm_vcpu *vcpu,
                                           struct kvm_page_fault *fault,
                                           struct tdp_iter *iter)
{
    struct kvm_mmu_page *sp = sptep_to_sp(rcu_dereference(iter->sptep));
    u64 new_spte;
    int ret = RET_PF_FIXED;
    bool wrprot = false;
    
    // 级别不匹配则重试
    if (WARN_ON_ONCE(sp->role.level != fault->goal_level))
        return RET_PF_RETRY;
    
    // 检查是否可以使用大页
    if (is_shadow_present_pte(iter->old_spte) &&
        (fault->prefetch || is_access_allowed(fault, iter->old_spte)) &&
        is_last_spte(iter->old_spte, iter->level)) {
        return RET_PF_SPURIOUS;
    }
    
    // 生成新的SPTE
    if (unlikely(!fault->slot))
        new_spte = make_mmio_spte(vcpu, iter->gfn, ACC_ALL);
    else
        wrprot = make_spte(vcpu, sp, fault->slot, ACC_ALL, iter->gfn,
                           fault->pfn, iter->old_spte, fault->prefetch,
                           false, fault->map_writable, &new_spte);
    
    // 原子设置SPTE
    if (tdp_mmu_set_spte_atomic(vcpu->kvm, iter, new_spte))
        return RET_PF_RETRY;
    
    // 处理TLB刷新
    if (is_shadow_present_pte(iter->old_spte) &&
        (!is_last_spte(iter->old_spte, iter->level) ||
         WARN_ON_ONCE(leaf_spte_change_needs_tlb_flush(iter->old_spte, new_spte))))
        kvm_flush_remote_tlbs_gfn(vcpu->kvm, iter->gfn, iter->level);
    
    // 写保护处理
    if (wrprot && fault->write)
        ret = RET_PF_WRITE_PROTECTED;
    
    // MMIO SPTE处理
    if (unlikely(is_mmio_spte(vcpu->kvm, new_spte))) {
        vcpu->stat.pf_mmio_spte_created++;
        ret = RET_PF_EMULATE;
    }
    
    return ret;
}
```

---

## 4. KVM_RUN: vCPU运行循环与退出处理

### 4.1 vcpu_enter_guest() 客户机进入

**源码位置**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 第11079-11150行:

```c
static int vcpu_enter_guest(struct kvm_vcpu *vcpu)
{
    int r;
    fastpath_t exit_fastpath;
    
    // 处理待处理请求
    if (kvm_request_pending(vcpu)) {
        // VM死亡检查
        if (kvm_check_request(KVM_REQ_VM_DEAD, vcpu)) {
            r = -EIO;
            goto out;
        }
        
        // 脏环软满检查
        if (kvm_dirty_ring_check_request(vcpu)) {
            r = 0;
            goto out;
        }
        
        // MMU相关请求
        if (kvm_check_request(KVM_REQ_MMU_FREE_OBSOLETE_ROOTS, vcpu))
            kvm_mmu_free_obsolete_roots(vcpu);
        if (kvm_check_request(KVM_REQ_MMU_SYNC, vcpu))
            kvm_mmu_sync_roots(vcpu);
        if (kvm_check_request(KVM_REQ_LOAD_MMU_PGD, vcpu))
            kvm_mmu_load_pgd(vcpu);
        
        // TLB刷新请求
        if (kvm_check_request(KVM_REQ_TLB_FLUSH, vcpu))
            kvm_vcpu_flush_tlb_all(vcpu);
        
        // 事件注入
        if (kvm_check_request(KVM_REQ_EVENT, vcpu))
            kvm_x86_ops.inject_irq(vcpu);
        
        // 异常注入
        if (kvm_check_request(KVM_REQ_TRIPLE_FAULT, vcpu)) {
            vcpu->run->exit_reason = KVM_EXIT_SHUTDOWN;
            r = 0;
            goto out;
        }
    }
    
    // 调用VMX/VTX VM-Entry
    exit_fastpath = kvm_x86_call(run)(vcpu);
    
    // VM-Exit后处理
    r = kvm_x86_call(handle_exit)(vcpu, exit_fastpath);
    
    return r;
}
```

### 4.2 handle_exit() 退出处理

**VMX实现** `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` 第6781-6953行:

```c
// 主入口 (第6937行)
int vmx_handle_exit(struct kvm_vcpu *vcpu, fastpath_t exit_fastpath)
{
    int ret = __vmx_handle_exit(vcpu, exit_fastpath);
    
    // 总线锁检测
    if (vmx_get_exit_reason(vcpu).bus_lock_detected) {
        if (ret > 0)
            vcpu->run->exit_reason = KVM_EXIT_X86_BUS_LOCK;
        vcpu->run->flags |= KVM_RUN_X86_BUS_LOCK;
        return 0;
    }
    return ret;
}

// 实际处理 (第6781行)
static int __vmx_handle_exit(struct kvm_vcpu *vcpu, fastpath_t exit_fastpath)
{
    union vmx_exit_reason exit_reason = vmx_get_exit_reason(vcpu);
    
    // PML缓冲区刷新
    if (enable_pml && !is_guest_mode(vcpu))
        vmx_flush_pml_buffer(vcpu);
    
    // 嵌套VMX处理
    if (is_guest_mode(vcpu)) {
        if (vmx->vt.emulation_required) {
            nested_vmx_vmexit(vcpu, EXIT_REASON_TRIPLE_FAULT, 0, 0);
            return 1;
        }
        if (nested_vmx_reflect_vmexit(vcpu))
            return 1;
    }
    
    // 模拟要求检查
    if (vmx->vt.emulation_required)
        return handle_invalid_guest_state(vcpu);
    
    // 失败VM-Entry处理
    if (exit_reason.failed_vmentry) {
        vcpu->run->exit_reason = KVM_EXIT_FAIL_ENTRY;
        return 0;
    }
    
    // 调用具体退出处理程序
    exit_handler_index = array_index_nospec(
        exit_reason.basic, ARRAY_SIZE(kvm_vmx_exit_handlers));
    return kvm_vmx_exit_handlers[exit_handler_index](vcpu);
}
```

**退出处理程序表** `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` 第6402-6450行:

```c
static int (*kvm_vmx_exit_handlers[])(struct kvm_vcpu *vcpu) = {
    [EXIT_REASON_EXCEPTION_NMI]         = handle_exception_nmi,
    [EXIT_REASON_EXTERNAL_INTERRUPT]    = handle_external_interrupt,
    [EXIT_REASON_TRIPLE_FAULT]          = handle_triple_fault,
    [EXIT_REASON_NMI_WINDOW]            = handle_nmi_window,
    [EXIT_REASON_IO_INSTRUCTION]        = handle_io,
    [EXIT_REASON_CR_ACCESS]             = handle_cr,
    [EXIT_REASON_DR_ACCESS]             = handle_dr,
    [EXIT_REASON_CPUID]                 = kvm_emulate_cpuid,
    [EXIT_REASON_MSR_READ]              = kvm_emulate_rdmsr,
    [EXIT_REASON_MSR_WRITE]             = kvm_emulate_wrmsr,
    [EXIT_REASON_INTERRUPT_WINDOW]      = handle_interrupt_window,
    [EXIT_REASON_HLT]                   = kvm_emulate_halt,
    [EXIT_REASON_INVD]                  = kvm_emulate_invd,
    [EXIT_REASON_INVLPG]                = handle_invlpg,
    [EXIT_REASON_RDPMC]                 = kvm_emulate_rdpmc,
    [EXIT_REASON_VMCALL]                = kvm_emulate_hypercall,
    [EXIT_REASON_VMCLEAR]               = handle_vmx_instruction,
    // ... 更多处理器
};
```

---

## 5. Dirty Ring: 脏页追踪机制

### 5.1 核心数据结构 struct kvm_dirty_ring

**源码位置**: `/Users/sphinx/github/linux/include/linux/kvm_dirty_ring.h` 第21-28行:

```c
struct kvm_dirty_ring {
    u32 dirty_index;           // 下一个脏页应写入的位置
    u32 reset_index;           // 下一个需要重置的位置
    u32 size;                  // 环的总大小
    u32 soft_limit;            // 软限制 (触发用户空间回收)
    struct kvm_dirty_gfn *dirty_gfns;  // 脏页数组
    int index;                 // 环的索引
};
```

**kvm_dirty_gfn结构** (内核API):
```c
struct kvm_dirty_gfn {
    __u32 slot;    // 内存槽ID
    __u64 offset;  // 槽内偏移 (GFN)
    __u32 flags;  // 标志 (KVM_DIRTY_GFN_F_DIRTY等)
};
```

### 5.2 kvm_dirty_ring_get() / 脏环操作

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/dirty_ring.c`:

```c
// 脏环已用数量 (第38行)
static u32 kvm_dirty_ring_used(struct kvm_dirty_ring *ring)
{
    return READ_ONCE(ring->dirty_index) - READ_ONCE(ring->reset_index);
}

// 脏环是否满 (第48行)
static bool kvm_dirty_ring_full(struct kvm_dirty_ring *ring)
{
    return kvm_dirty_ring_used(ring) >= ring->size;
}

// 脏环是否软满 (第43行)
static bool kvm_dirty_ring_soft_full(struct kvm_dirty_ring *ring)
{
    return kvm_dirty_ring_used(ring) >= ring->soft_limit;
}

// 脏环分配 (第74行)
int kvm_dirty_ring_alloc(struct kvm *kvm, struct kvm_dirty_ring *ring,
                         int index, u32 size)
{
    ring->dirty_gfns = vzalloc(size);
    if (!ring->dirty_gfns)
        return -ENOMEM;
    
    ring->size = size / sizeof(struct kvm_dirty_gfn);
    ring->soft_limit = ring->size - kvm_dirty_ring_get_rsvd_entries(kvm);
    ring->dirty_index = 0;
    ring->reset_index = 0;
    ring->index = index;
    
    return 0;
}
```

### 5.3 kvm_dirty_ring_push() 脏页推送

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/dirty_ring.c` 第218-241行:

```c
void kvm_dirty_ring_push(struct kvm_vcpu *vcpu, u32 slot, u64 offset)
{
    struct kvm_dirty_ring *ring = &vcpu->dirty_ring;
    struct kvm_dirty_gfn *entry;
    
    // 环不应满
    WARN_ON_ONCE(kvm_dirty_ring_full(ring));
    
    // 计算入口位置 (环形缓冲)
    entry = &ring->dirty_gfns[ring->dirty_index & (ring->size - 1)];
    
    entry->slot = slot;
    entry->offset = offset;
    
    // 确保数据写入完成后再发布
    smp_wmb();
    kvm_dirty_gfn_set_dirtied(entry);
    
    ring->dirty_index++;
    trace_kvm_dirty_ring_push(ring, slot, offset);
    
    // 软满时设置请求
    if (kvm_dirty_ring_soft_full(ring))
        kvm_make_request(KVM_REQ_DIRTY_RING_SOFT_FULL, vcpu);
}
```

### 5.4 dirty_ring_full() 满环检测

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/dirty_ring.c` 第243-260行:

```c
bool kvm_dirty_ring_check_request(struct kvm_vcpu *vcpu)
{
    // 检查软满请求
    if (kvm_check_request(KVM_REQ_DIRTY_RING_SOFT_FULL, vcpu) &&
        kvm_dirty_ring_soft_full(&vcpu->dirty_ring)) {
        kvm_make_request(KVM_REQ_DIRTY_RING_SOFT_FULL, vcpu);
        vcpu->run->exit_reason = KVM_EXIT_DIRTY_RING_FULL;
        trace_kvm_dirty_ring_exit(vcpu);
        return true;
    }
    return false;
}
```

**脏环流程图**:
```
Guest写入 → EPT Violation → kvm_dirty_ring_push()
    → dirty_index++ → soft_limit触发
    → KVM_REQ_DIRTY_RING_SOFT_FULL
    → VM-Exit → 用户空间回收脏页
    → KVM_RESET_DIRTY_RINGS → reset_index++
```

---

## 6. guest_memfd: 私有内存管理

### 6.1 KVM_MEMORY_FLAG_GUEST_MEMFD

**源码位置**: `/Users/sphinx/github/linux/include/uapi/linux/kvm.h` 第57行:

```c
#define KVM_MEM_GUEST_MEMFD    (1UL << 2)
```

### 6.2 guest_memfd 数据结构

**源码位置**: `/Users/sphinx/github/linux/virt/kvm/guest_memfd.c`:

```c
// guest_memfd文件 (第24行)
struct gmem_file {
    struct kvm *kvm;
    struct xarray bindings;      // 槽绑定
    struct list_head entry;
};

// guest_memfd inode信息 (第30行)
struct gmem_inode {
    struct shared_policy policy;
    struct inode vfs_inode;
    u64 flags;                  // GUEST_MEMFD_FLAG_MMAP等
};
```

### 6.3 guest_memfd_create() 内存创建

**核心流程**:

1. **folio分配** `/Users/sphinx/github/linux/virt/kvm/guest_memfd.c` 第62-77行:
```c
static int __kvm_gmem_prepare_folio(struct kvm *kvm, struct kvm_memory_slot *slot,
                                    pgoff_t index, struct folio *folio)
{
    kvm_pfn_t pfn = folio_file_pfn(folio, index);
    gfn_t gfn = slot->base_gfn + index - slot->gmem.pgoff;
    
    int rc = kvm_arch_gmem_prepare(kvm, gfn, pfn, folio_order(folio));
    if (rc) {
        pr_warn_ratelimited("gmem: Failed to prepare folio...\n");
        return rc;
    }
    return 0;
}
```

2. **folio获取** 第119-150行:
```c
static struct folio *kvm_gmem_get_folio(struct inode *inode, pgoff_t index)
{
    // 快速路径: 检查folio是否已在mapping中
    folio = __filemap_get_folio(inode->i_mapping, index,
                                FGP_LOCK | FGP_ACCESSED, 0);
    if (!IS_ERR(folio))
        return folio;
    
    // 创建新folio
    policy = mpol_shared_policy_lookup(&GMEM_I(inode)->policy, index);
    folio = __filemap_get_folio_mpol(...);
    mpol_cond_put(policy);
    
    return folio;
}
```

### 6.4 gmem folio管理

**关键特性**:

1. **锁folio** (folio锁定):
   - folio在映射到客户机前必须被锁定
   - 确保folio在客户机使用期间不被回收

2. **大页支持**:
   ```c
   // 第103行 - folio_order对齐检查
   WARN_ON(!IS_ALIGNED(slot->gmem.pgoff, folio_nr_pages(folio)));
   index = kvm_gmem_get_index(slot, gfn);
   index = ALIGN_DOWN(index, folio_nr_pages(folio));
   ```

3. **失效处理** `/Users/sphinx/github/linux/virt/kvm/guest_memfd.c` 第160-195行:
```c
static void __kvm_gmem_invalidate_begin(struct gmem_file *f, pgoff_t start,
                                        pgoff_t end, enum kvm_gfn_range_filter attr_filter)
{
    bool flush = false, found_memslot = false;
    struct kvm_memory_slot *slot;
    
    xa_for_each_range(&f->bindings, index, slot, start, end - 1) {
        struct kvm_gfn_range gfn_range = {
            .start = slot->base_gfn + max(pgoff, start) - pgoff,
            .end = slot->base_gfn + min(pgoff + slot->npages, end) - pgoff,
            .slot = slot,
            .may_block = true,
            .attr_filter = attr_filter,
        };
        
        KVM_MMU_LOCK(kvm);
        kvm_mmu_invalidate_begin(kvm);
        flush |= kvm_mmu_unmap_gfn_range(kvm, &gfn_range);
    }
    
    if (flush)
        kvm_flush_remote_tlbs(kvm);
    
    KVM_MMU_UNLOCK(kvm);
}
```

---

## 7. 知识点关联表

| 模块 | 核心结构 | 关键函数 | 源码位置 | 功能描述 |
|------|----------|----------|----------|----------|
| **KVM Core** | `struct kvm` | `kvm_create_vm()` | `kvm_main.c:1105` | 创建虚拟机实例,初始化所有子系统 |
| | | `kvm_destroy_vm()` | `kvm_main.c:1203` | 销毁虚拟机,释放所有资源 |
| | | `mmu_notifier` ops | `kvm_main.c:888` | 监听宿主页表变更 |
| **vCPU** | `struct kvm_vcpu` | `kvm_arch_vcpu_create()` | `x86.c:12736` | 创建vCPU,初始化MSR/LAPIC |
| | | `vcpu_run()` | `x86.c:11676` | vCPU主运行循环 |
| | | `kvm_skip_emulated_instruction()` | `x86.c:9243` | 跳过已模拟指令 |
| **MMU/EPT** | `struct kvm_mmu_page` | `tdp_mmu_map_handle_target_level()` | `tdp_mmu.c:1168` | TDP页表映射处理 |
| | `struct tdp_iter` | `__tdp_mmu_set_spte_atomic()` | `tdp_mmu.c:650` | 原子设置SPTE |
| | | `kvm_mmu_unload()` | `mmu.c:6083` | 卸载MMU上下文 |
| **KVM_RUN** | - | `vcpu_enter_guest()` | `x86.c:11079` | VM-Entry前的请求处理 |
| | | `vmx_handle_exit()` | `vmx.c:6937` | VMX退出处理分发 |
| | | `__vmx_handle_exit()` | `vmx.c:6781` | VMX退出实际处理 |
| **Dirty Ring** | `struct kvm_dirty_ring` | `kvm_dirty_ring_push()` | `dirty_ring.c:218` | 推送脏页到环 |
| | | `kvm_dirty_ring_reset()` | `dirty_ring.c:105` | 重置脏环 |
| | | `kvm_dirty_ring_check_request()` | `dirty_ring.c:243` | 检查软满状态 |
| **guest_memfd** | `struct gmem_file` | `kvm_gmem_get_folio()` | `guest_memfd.c:119` | 获取/创建gmem folio |
| | | `__kvm_gmem_invalidate_begin()` | `guest_memfd.c:160` | gmem失效处理 |
| | `struct kvm_memory_slot.gmem` | `kvm_gmem_get_file()` | `guest_memfd.c:373` | 获取活跃gmem文件 |

---

## 附录: 关键锁与同步机制

| 锁 | 类型 | 用途 | 持有路径 |
|----|------|------|----------|
| `kvm->mmu_lock` | rwlock/spinlock | 保护影子页表 | MMU操作,页表映射 |
| `kvm->slots_lock` | mutex | 保护内存槽 | memslot修改 |
| `kvm->mn_invalidate_lock` | spinlock | MMU notifier同步 | invalidate计数 |
| `vcpu->mutex` | mutex | vCPU状态修改 | vCPU创建/销毁 |
| `kvm->lock` | mutex | VM全局操作 | vCPU创建/列表修改 |

---

**文档版本**: R1  
**分析源码版本**: Linux Kernel (latest)  
**生成时间**: 2026-04-26
