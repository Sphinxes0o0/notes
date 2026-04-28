
# Linux Virt/KVM 子系统深度分析 R2

## 目录
1. [kvm_mmu_map_page: SPTE生成流程](#1-kvm_mmu_map_page)
2. [tdp_mmu_iter: 遍历逻辑](#2-tdp_mmu_iter)
3. [ept_sync_root: TLB刷新机制](#3-ept_sync_root)
4. [kvm_x86_emulator: 指令模拟](#4-kvm_x86_emulator)
5. [vmx_vcpu_run: VMEntry/VMExit](#5-vmx_vcpu_run)
6. [nested VMX: 嵌套虚拟化](#6-nested-vmx)
7. [知识点关联表](#7-知识点关联表)

---

## 1. kvm_mmu_map_page: SPTE生成流程

### 1.1 核心入口函数

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/mmu.c`

```c
// 行 4914: kvm_tdp_mmu_map() 是 TDP MMU 的页面映射入口
int kvm_tdp_mmu_map(struct kvm_vcpu *vcpu, struct kvm_page_fault *fault)
{
    struct kvm_mmu_page *root = tdp_mmu_get_root_for_fault(vcpu, fault);
    struct kvm *kvm = vcpu->kvm;
    struct tdp_iter iter;
    struct kvm_mmu_page *sp;
    int ret = RET_PF_RETRY;
    
    // 行 1279: 使用 for_each_tdp_pte 遍历页表
    for_each_tdp_pte(iter, kvm, root, fault->gfn, fault->gfn + 1) {
        // ...
        if (iter.level == fault->goal_level)
            goto map_target_level;
        // ...
    }
map_target_level:
    ret = tdp_mmu_map_handle_target_level(vcpu, fault, &iter);
    // ...
}
```

### 1.2 __direct_map() 影子页表映射

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/mmu.c` 行 3436-3478

```c
static int direct_map(struct kvm_vcpu *vcpu, struct kvm_page_fault *fault)
{
    struct kvm_shadow_walk_iterator it;
    struct kvm_mmu_page *sp;
    int ret;
    gfn_t base_gfn = fault->gfn;

    kvm_mmu_hugepage_adjust(vcpu, fault);

    trace_kvm_mmu_spte_requested(fault);
    // 行 3446: 使用 for_each_shadow_entry 遍历影子页表
    for_each_shadow_entry(vcpu, fault->addr, it) {
        if (fault->nx_huge_page_workaround_enabled)
            disallowed_hugepage_adjust(fault, *it.sptep, it.level);

        base_gfn = gfn_round_for_level(fault->gfn, it.level);
        if (it.level == fault->goal_level)
            break;

        sp = kvm_mmu_get_child_sp(vcpu, it.sptep, base_gfn, true, ACC_ALL);
        if (sp == ERR_PTR(-EEXIST))
            continue;

        link_shadow_page(vcpu, it.sptep, sp);
        // ...
    }

    ret = mmu_set_spte(vcpu, fault->slot, it.sptep, ACC_ALL,
                       base_gfn, fault->pfn, fault);
    // ...
}
```

### 1.3 tdp_mmu_map_handle_target_level() 目标级SPTE安装

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_mmu.c` 行 1168-1223

```c
static int tdp_mmu_map_handle_target_level(struct kvm_vcpu *vcpu,
                      struct kvm_page_fault *fault,
                      struct tdp_iter *iter)
{
    struct kvm_mmu_page *sp = sptep_to_sp(rcu_dereference(iter->sptep));
    u64 new_spte;
    int ret = RET_PF_FIXED;
    bool wrprot = false;

    // 检查是否已经有有效的 SPTE
    if (is_shadow_present_pte(iter->old_spte) &&
        (fault->prefetch || is_access_allowed(fault, iter->old_spte)) &&
        is_last_spte(iter->old_spte, iter->level)) {
        return RET_PF_SPURIOUS;
    }

    // 生成新的 SPTE
    if (unlikely(!fault->slot))
        new_spte = make_mmio_spte(vcpu, iter->gfn, ACC_ALL);
    else
        wrprot = make_spte(vcpu, sp, fault->slot, ACC_ALL, iter->gfn,
                   fault->pfn, iter->old_spte, fault->prefetch,
                   false, fault->map_writable, &new_spte);

    // 原子性地设置 SPTE
    if (tdp_mmu_set_spte_atomic(vcpu->kvm, iter, new_spte))
        return RET_PF_RETRY;
    
    // 如需要则刷新 TLB
    if (is_shadow_present_pte(iter->old_spte) &&
        (!is_last_spte(iter->old_spte, iter->level) ||
         WARN_ON_ONCE(leaf_spte_change_needs_tlb_flush(iter->old_spte, new_spte))))
        kvm_flush_remote_tlbs_gfn(vcpu->kvm, iter->gfn, iter->level);
}
```

### 1.4 SPTE生成流程图

```
kvm_tdp_page_fault()
    │
    ├─► kvm_tdp_mmu_page_fault()  [mmu.c:4923]
    │       │
    │       └─► kvm_tdp_mmu_map()  [tdp_mmu.c:1263]
    │               │
    │               ├─► tdp_iter_start() 初始化迭代器
    │               │
    │               ├─► for_each_tdp_pte() 遍历 GFN [fault->gfn, fault->gfn+1)
    │               │       │
    │               │       ├─► try_step_down() 向下层页表遍历
    │               │       ├─► try_step_side() 横向遍历同级页表项
    │               │       └─► try_step_up() 向上一层
    │               │
    │               └─► tdp_mmu_map_handle_target_level()  [tdp_mmu.c:1168]
    │                       │
    │                       ├─► make_spte() 生成新 SPTE
    │                       ├─► tdp_mmu_set_spte_atomic() 原子写入
    │                       └─► kvm_flush_remote_tlbs_gfn() 刷新 TLB
    │
    └─► direct_page_fault()  [mmu.c:4914]
            │
            └─► direct_map()  [mmu.c:3436]
                    │
                    └─► for_each_shadow_entry() 遍历影子页表
                            │
                            ├─► kvm_mmu_get_child_sp() 获取子页表
                            ├─► link_shadow_page() 链接影子页
                            └─► mmu_set_spte() 设置最终 SPTE
```

---

## 2. tdp_mmu_iter: 遍历逻辑

### 2.1 核心数据结构

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_iter.h` 行 76-117

```c
struct tdp_iter {
    gfn_t next_last_level_gfn;     // 目标 GFN
    gfn_t yielded_gfn;             // 上次让出时的 GFN
    tdp_ptep_t pt_path[PT64_ROOT_MAX_LEVEL];  // 页表路径指针
    tdp_ptep_t sptep;              // 当前 SPTE 指针
    gfn_t gfn;                     // 当前 GFN
    gfn_t gfn_bits;                // GFN 掩码位
    int root_level;                // 根级别
    int min_level;                 // 最低遍历级别
    int level;                     // 当前级别
    int as_id;                     // 地址空间 ID
    u64 old_spte;                  // 当前 SPTE 快照
    bool valid;                    // 迭代器是否有效
    bool yielded;                  // 是否在遍历中让出过 CPU
};
```

### 2.2 tdp_iter_start() 初始化

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_iter.c` 行 39-57

```c
void tdp_iter_start(struct tdp_iter *iter, struct kvm_mmu_page *root,
            int min_level, gfn_t next_last_level_gfn, gfn_t gfn_bits)
{
    if (WARN_ON_ONCE(!root || (root->role.level < 1) ||
             (root->role.level > PT64_ROOT_MAX_LEVEL) ||
             (gfn_bits && next_last_level_gfn >= gfn_bits))) {
        iter->valid = false;
        return;
    }

    iter->next_last_level_gfn = next_last_level_gfn;
    iter->gfn_bits = gfn_bits;
    iter->root_level = root->role.level;
    iter->min_level = min_level;
    // 行 53: 设置根页表的指针
    iter->pt_path[iter->root_level - 1] = (tdp_ptep_t)root->spt;
    iter->as_id = kvm_mmu_page_as_id(root);

    tdp_iter_restart(iter);  // 行 56: 初始化迭代器状态
}
```

### 2.3 tdp_iter_next() 前序遍历核心算法

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_iter.c` 行 163-178

```c
void tdp_iter_next(struct tdp_iter *iter)
{
    if (iter->yielded) {
        tdp_iter_restart(iter);  // 让出过，需要从根重新开始
        return;
    }

    // 优先尝试向下遍历
    if (try_step_down(iter))
        return;

    // 尝试横向遍历
    do {
        if (try_step_side(iter))
            return;
    } while (try_step_up(iter));  // 向上回溯，直到找到可横向移动的节点
    
    iter->valid = false;  // 遍历完成
}
```

### 2.4 遍历算法图解

```
TDP MMU 前序遍历算法:

假设遍历 [GFN 10, GFN 15)，目标级别 PG_LEVEL_4K:

Level 3 (PML3)     Level 2 (PML2)      Level 1 (PML1)     Level 0 (PTE)
    │                   │                    │                  │
    ├──► GFN 0-511     ├──► GFN 0-511      ├──► GFN 10       [SPTE]
    │     ...          │     ...           ├──► GFN 11       [SPTE]
    │                   │                    ├──► GFN 12       [SPTE]
    └──► GFN 10-521    └──► GFN 10-521     ├──► GFN 13       [SPTE]
          (next)             (next)         └──► GFN 14       [SPTE]
              │                   │              │
              ▼                   ▼              ▼
        try_step_down()   try_step_down()  try_step_side()
        
遍历顺序 (前序): 
  1. 先访问节点
  2. 然后递归向下
  3. 最后横向移动

核心函数:
  - try_step_down(): 如果当前 SPTE 指向子页表，则向下移动
  - try_step_side(): 在当前页表中移动到下一个表项
  - try_step_up(): 向上回溯到父页面，准备横向移动
```

### 2.5 关键宏定义

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/mmu/tdp_iter.h` 行 123-134

```c
// 遍历 [start, end) 范围的所有 SPTE
#define for_each_tdp_pte_min_level(iter, kvm, root, min_level, start, end)    \
    for (tdp_iter_start(&iter, root, min_level, start, kvm_gfn_root_bits(kvm, root)); \
         iter.valid && iter.gfn < end;                    \
         tdp_iter_next(&iter))

// 遍历指定级别的 SPTE
#define for_each_tdp_pte_min_level_all(iter, root, min_level)      \
    for (tdp_iter_start(&iter, root, min_level, 0, 0);        \
        iter.valid && iter.gfn < tdp_mmu_max_gfn_exclusive();   \
        tdp_iter_next(&iter))

// 默认遍历到 4K 级别
#define for_each_tdp_pte(iter, kvm, root, start, end)           \
    for_each_tdp_pte_min_level(iter, kvm, root, PG_LEVEL_4K, start, end)
```

---

## 3. ept_sync_root: TLB刷新机制

### 3.1 EPT同步函数

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx_ops.h` 行 358-369

```c
static inline void ept_sync_global(void)
{
    __invept(VMX_EPT_EXTENT_GLOBAL, 0);  // 全局 EPT 无效化
}

static inline void ept_sync_context(u64 eptp)
{
    if (cpu_has_vmx_invept_context())
        __invept(VMX_EPT_EXTENT_CONTEXT, eptp);  // 上下文特定 EPT 无效化
    else
        ept_sync_global();  // 回退到全局无效化
}
```

### 3.2 VMX中的TLB刷新函数

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c`

```c
// 行 3358-3379: 刷新所有 TLB
void vmx_flush_tlb_all(struct kvm_vcpu *vcpu)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);

    if (enable_ept) {
        ept_sync_global();  // EPT 需要全局刷新
    } else if (enable_vpid) {
        if (cpu_has_vmx_invvpid_global())
            vpid_sync_vcpu_global();
        else {
            vpid_sync_vcpu_single(vmx->vpid);
            vpid_sync_vcpu_single(vmx->nested.vpid02);
        }
    }
}

// 行 3412-3420: EPT 根刷新
static void vmx_flush_tlb_ept_root(hpa_t root_hpa)
{
    u64 eptp = construct_eptp(root_hpa);

    if (VALID_PAGE(eptp))
        ept_sync_context(eptp);  // 上下文同步
    else
        ept_sync_global();         // 全局同步
}

// 行 3422-3435: 当前上下文刷新
void vmx_flush_tlb_current(struct kvm_vcpu *vcpu)
{
    struct kvm_mmu *mmu = vcpu->arch.mmu;
    u64 root_hpa = mmu->root.hpa;

    if (!VALID_PAGE(root_hpa))
        return;

    if (enable_ept)
        vmx_flush_tlb_ept_root(root_hpa);
    else
        vpid_sync_context(vmx_get_current_vpid(vcpu));
}
```

### 3.3 INVEPT指令语义

| 指令 | 类型 | 描述 |
|------|------|------|
| `INVEPT rbx, eax` | 单上下文 | 仅无效化指定 EPTP 的 TLB 条目 |
| `INVEPT eax` (rax=0) | 全局 | 无效化所有 EPT TLB 条目 |

**EPTP (EPT Pointer)** 结构:
```
Bits 2:0   - EPTP paging-structure memory type (MBO)
Bits 5:3   - EPT page-walk length (EPTPWL) - 1
Bits 11:6  - Reserved (must be 0)
Bits 47:12 - EPT PML4物理地址 [47:12]
Bits 63:48 - Reserved (must be 0)
```

### 3.4 TLB刷新流程图

```
页面失效/映射变更
      │
      ▼
kvm_flush_remote_tlbs_gfn() / kvm_flush_remote_tlbs()
      │
      ├─► vmx_flush_tlb_ept_root()
      │       │
      │       ├─► construct_eptp(root_hpa)  构建 EPTP
      │       │
      │       └─► ept_sync_context(eptp)  [vmx_ops.h:363]
      │               │
      │               ├─► __invept(VMX_EPT_EXTENT_CONTEXT, eptp)
      │               │       │
      │               │       └─► VM Exit → CPU 执行 INVEPT
      │               │
      │               └─► (fallback) ept_sync_global()
      │                       │
      │                       └─► __invept(VMX_EPT_EXTENT_GLOBAL, 0)
      │
      └─► (非 EPT 模式) vpid_sync_context()
              │
              └─► __invvpid()  VPID 无效化
```

---

## 4. kvm_x86_emulator: 指令模拟

### 4.1 x86_emulate_instruction() 主入口

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 行 9416-9560

```c
int x86_emulate_instruction(struct kvm_vcpu *vcpu, gpa_t cr2_or_gpa,
                int emulation_type, void *insn, int insn_len)
{
    int r;
    struct x86_emulate_ctxt *ctxt = vcpu->arch.emulate_ctxt;
    bool writeback = true;

    // 检查是否允许重试
    if ((emulation_type & EMULTYPE_ALLOW_RETRY_PF) &&
        (WARN_ON_ONCE(is_guest_mode(vcpu)) ||
         WARN_ON_ONCE(!(emulation_type & EMULTYPE_PF))))
        emulation_type &= ~EMULTYPE_ALLOW_RETRY_PF;

    r = kvm_check_emulate_insn(vcpu, emulation_type, insn, insn_len);
    if (r != X86EMUL_CONTINUE) {
        if (r == X86EMUL_RETRY_INSTR || r == X86EMUL_PROPAGATE_FAULT)
            return 1;
        // ...
    }

    if (!(emulation_type & EMULTYPE_NO_DECODE)) {
        kvm_clear_exception_queue(vcpu);
        
        // 指令解码
        r = x86_decode_emulated_instruction(vcpu, emulation_type,
                            insn, insn_len);
        if (r != EMULATION_OK) {
            // 处理解码失败
            if ((emulation_type & EMULTYPE_TRAP_UD) ||
                (emulation_type & EMULTYPE_TRAP_UD_FORCED)) {
                kvm_queue_exception(vcpu, UD_VECTOR);
                return 1;
            }
            // ...
        }
    }

    // 执行模拟指令
    r = x86_emulate_insn(ctxt, is_guest_mode(vcpu) &&
                 !(emulation_type & EMULTYPE_NO_DECODE));

writeback:
    if (writeback)
        emulator_writeback_register_cache(ctxt);
    // ...
}
```

### 4.2 emulator_read_emulated() / emulator_write_emulated()

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 行 8287-8305

```c
static int emulator_read_emulated(struct x86_emulate_ctxt *ctxt,
                  unsigned long addr,
                  void *val,
                  unsigned int bytes,
                  struct x86_exception *exception)
{
    return emulator_read_write(ctxt, addr, val, bytes,
                   exception, &read_emultor);  // 行 8293-8294
}

static int emulator_write_emulated(struct x86_emulate_ctxt *ctxt,
                unsigned long addr,
                const void *val,
                unsigned int bytes,
                struct x86_exception *exception)
{
    return emulator_read_write(ctxt, addr, (void *)val, bytes,
                   exception, &write_emultor);  // 行 8302-8303
}
```

### 4.3 emulator_read_write() 核心读写函数

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c` 行 8233-8266

```c
static int emulator_read_write(struct x86_emulate_ctxt *ctxt,
                   unsigned long addr, void *val, unsigned int bytes,
                   struct x86_exception *exception,
                   read_write_emulator_t *read_write)
{
    // 计算页边界
    unsigned long last_addr = addr + bytes - 1;
    int rc;

    // 跨页处理
    if ((addr & PAGE_MASK) != (last_addr & PAGE_MASK)) {
        // 处理跨页情况
        rc = emulator_read_write_onepage(addr, val, PAGE_SIZE, exception, read_write);
        if (rc != X86EMUL_CONTINUE)
            return rc;
        // 处理第二页
        rc = emulator_read_write_onepage(addr, val, bytes, exception, read_write);
    } else {
        // 单页情况
        rc = emulator_read_write_onepage(addr, val, bytes, exception, read_write);
    }
    return rc;
}
```

### 4.4 模拟器架构图

```
x86_emulate_instruction()
      │
      ├─► kvm_check_emulate_insn()  检查是否需要模拟
      │
      ├─► x86_decode_emulated_instruction()  解码指令
      │       │
      │       ├─► decode_table[]  操作码查找表
      │       ├─► decode_operand()  解码操作数
      │       └─►识别 ModR/M, SIB, 立即数等
      │
      └─► x86_emulate_insn()  执行指令
              │
              ├─► fetch_emulated()  取指令字节
              │
              ├─► read_emulated()  读取内存
              │       │
              │       └─► emulator_read_write()
              │               │
              │               ├─► kvm_mmu_gva_to_gpa_read()
              │               └─► handle_mmio_page_fault()
              │
              ├─► write_emulated()  写入内存
              │
              └─► emulator_writeback_register_cache()  回写寄存器
```

---

## 5. vmx_vcpu_run: VMEntry/VMExit

### 5.1 vmx_vcpu_run() 主函数

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` 行 7605-7756

```c
fastpath_t vmx_vcpu_run(struct kvm_vcpu *vcpu, u64 run_flags)
{
    bool force_immediate_exit = run_flags & KVM_RUN_FORCE_IMMEDIATE_EXIT;
    struct vcpu_vmx *vmx = to_vmx(vcpu);
    unsigned long cr3, cr4;

    // 行 7621-7631: 检查 guest 状态是否有效
    if (unlikely(vmx->vt.emulation_required)) {
        vmx->fail = 0;
        vmx->vt.exit_reason.full = EXIT_REASON_INVALID_STATE;
        vmx->vt.exit_reason.failed_vmentry = 1;
        return EXIT_FASTPATH_NONE;
    }

    trace_kvm_entry(vcpu, force_immediate_exit);

    // 行 7646-7649: 保存 guest 寄存器到 VMCS
    if (kvm_register_is_dirty(vcpu, VCPU_REGS_RSP))
        vmcs_writel(GUEST_RSP, vcpu->arch.regs[VCPU_REGS_RSP]);
    if (kvm_register_is_dirty(vcpu, VCPU_REGS_RIP))
        vmcs_writel(GUEST_RIP, vcpu->arch.regs[VCPU_REGS_RIP]);

    // 行 7665-7675: 刷新 HOST_CR3/CR4
    cr3 = __get_current_cr3_fast();
    if (unlikely(cr3 != vmx->loaded_vmcs->host_state.cr3)) {
        vmcs_writel(HOST_CR3, cr3);
        vmx->loaded_vmcs->host_state.cr3 = cr3;
    }
    cr4 = cr4_read_shadow();
    if (unlikely(cr4 != vmx->loaded_vmcs->host_state.cr4)) {
        vmcs_writel(HOST_CR4, cr4);
        vmx->loaded_vmcs->host_state.cr4 = cr4;
    }

    pt_guest_enter(vmx);  // Performance Timers 进入
    atomic_switch_perf_msrs(vmx);  // 切换 PMU MSR

    kvm_wait_lapic_expire(vcpu);  // 等待 APIC timer

    // 行 7699: 执行 VM-entry
    vmx_vcpu_enter_exit(vcpu, __vmx_vcpu_run_flags(vmx));

    // VM-exit 后的处理
    // ...

    return vmx_exit_handlers_fastpath(vcpu, force_immediate_exit);
}
```

### 5.2 VMEntry/VMExit 状态保存/恢复

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` 行 7573-7603

```c
static void vmx_vcpu_enter_exit(struct kvm_vcpu *vcpu, unsigned long flags)
{
    guest_state_enter_irqoff();  // 关闭本地中断

    vmx_l1d_flush(vcpu);        // 刷新 L1D cache
    vmx_disable_fb_clear(vmx);  // 禁用 TSX 透明 FB clear

    // 恢复 CR2
    if (vcpu->arch.cr2 != native_read_cr2())
        native_write_cr2(vcpu->arch.cr2);

    // 执行 VMENTER (汇编函数)
    vmx->fail = __vmx_vcpu_run(vmx, (unsigned long *)&vcpu->arch.regs, flags);

    // 保存 CR2
    vcpu->arch.cr2 = native_read_cr2();
    vcpu->arch.regs_avail &= ~VMX_REGS_LAZY_LOAD_SET;

    vmx->idt_vectoring_info = 0;
    vmx_enable_fb_clear(vmx);

    if (unlikely(vmx->fail)) {
        vmx->vt.exit_reason.full = 0xdead;
        goto out;
    }

    // 读取 VM-exit 信息
    vmx->vt.exit_reason.full = vmcs_read32(VM_EXIT_REASON);
    if (likely(!vmx_get_exit_reason(vcpu).failed_vmentry))
        vmx->idt_vectoring_info = vmcs_read32(IDT_VECTORING_INFO_FIELD);

    vmx_handle_nmi(vcpu);

out:
    guest_state_exit_irqoff();  // 恢复本地中断
}
```

### 5.3 VMEntry/VMExit 流程图

```
                    VMEntry (VMENTRY)
                          │
                          ▼
    ┌─────────────────────────────────────┐
    │  1. Guest State Loading            │
    │     - GUEST_CR3, CR0, CR4, DR7      │
    │     - GUEST_RIP, RSP, RFLAGS        │
    │     - GDTR, IDTR, LDTR, TR          │
    │     - CS, DS, ES, FS, GS, SS        │
    │     - MSRs (SPEC_CTRL, etc.)        │
    └─────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────┐
    │  2. VMCS Checks                     │
    │     - Control fields validation     │
    │     - Guest state consistency       │
    │     - Resource availability         │
    └─────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────┐
    │  3. __vmx_vcpu_run()               │
    │     - VMENTER 指令执行              │
    └─────────────────────────────────────┘
                          │
                          ▼
                 ┌────────┴────────┐
                 │   Guest Runs    │
                 │   (L1 or L2)    │
                 └────────┬────────┘
                          │
                    VMExit (VMEXIT)
                          │
                          ▼
    ┌─────────────────────────────────────┐
    │  1. VMExit Reason Capture          │
    │     - VM_EXIT_REASON 寄存器        │
    │     - EXIT_QUALIFICATION            │
    │     - IDT_VECTORING_INFO            │
    └─────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────┐
    │  2. Host State Restore             │
    │     - HOST_CR3, CR4                 │
    │     - HOST_RIP, RSP                 │
    │     - HOST_GDTR, IDTR               │
    │     - HOST_CS, DS, ES, FS, GS, SS   │
    │     - HOST MSRs                     │
    └─────────────────────────────────────┘
                          │
                          ▼
              vmx_exit_handlers_fastpath()
                          │
                          ▼
              KVM 退出原因处理
```

### 5.4 关键 VMCS 字段

| 类别 | 字段 | 用途 |
|------|------|------|
| Guest 状态 | GUEST_CR0, CR3, CR4 | Guest 控制寄存器 |
| Guest 状态 | GUEST_RIP, RSP, RFLAGS | Guest 程序计数器 |
| Guest 状态 | GUEST_CS, DS, ES, FS, GS, SS | Guest 段寄存器 |
| Host 状态 | HOST_CR3, CR4 | Host 控制寄存器 |
| Host 状态 | HOST_RIP, RSP | Host 程序计数器 |
| 控制字段 | VM_EXIT_CONTROLS | VMExit 控制 |
| 控制字段 | VM_ENTRY_CONTROLS | VMEntry 控制 |
| 退出信息 | VM_EXIT_REASON | 退出原因 |
| 退出信息 | EXIT_QUALIFICATION | 退出限定符 |

---

## 6. nested VMX: 嵌套虚拟化

### 6.1 nested_vmx_enter_non_root_mode() L2 进入

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/nested.c` 行 3606-3741

```c
enum nvmx_vmentry_status nested_vmx_enter_non_root_mode(struct kvm_vcpu *vcpu,
                             bool from_vmentry)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);
    struct vmcs12 *vmcs12 = get_vmcs12(vcpu);
    enum vm_entry_failure_code entry_failure_code;
    union vmx_exit_reason exit_reason = {
        .basic = EXIT_REASON_INVALID_STATE,
        .failed_vmentry = 1,
    };

    trace_kvm_nested_vmenter(...);  // 行 3618: 跟踪进入

    kvm_service_local_tlb_flush_requests(vcpu);  // 行 3628: 处理本地 TLB 刷新

    // 行 3630-3642: 保存调试和控制状态
    if (!vmx->nested.nested_run_pending ||
        !(vmcs12->vm_entry_controls & VM_ENTRY_LOAD_DEBUG_CONTROLS))
        vmx->nested.pre_vmenter_debugctl = vmx_guest_debugctl_read();

    // 行 3656-3657: 如果 EPT 禁用，覆盖 GUEST_CR3
    if (!enable_ept)
        vmcs_writel(GUEST_CR3, vcpu->arch.cr3);

    // 行 3659: 切换到 vmcs02
    vmx_switch_vmcs(vcpu, &vmx->nested.vmcs02);

    // 行 3661: 早期准备 vmcs02
    prepare_vmcs02_early(vmx, &vmx->vmcs01, vmcs12);

    if (from_vmentry) {
        // 行 3664-3667: 获取 vmcs12 pages
        if (unlikely(!nested_get_vmcs12_pages(vcpu))) {
            vmx_switch_vmcs(vcpu, &vmx->vmcs01);
            return NVMX_VMENTRY_KVM_INTERNAL_ERROR;
        }

        // 行 3669-3672: 检查控制字段
        if (nested_vmx_check_controls_late(vcpu, vmcs12)) {
            vmx_switch_vmcs(vcpu, &vmx->vmcs01);
            return NVMX_VMENTRY_VMFAIL;
        }

        // 行 3674-3679: 检查 guest 状态
        if (nested_vmx_check_guest_state(vcpu, vmcs12,
                         &entry_failure_code)) {
            exit_reason.basic = EXIT_REASON_INVALID_STATE;
            vmcs12->exit_qualification = entry_failure_code;
            goto vmentry_fail_vmexit;
        }
    }

    // 行 3682: 进入 guest 模式
    enter_guest_mode(vcpu);

    // 行 3684-3688: 准备 vmcs02
    if (prepare_vmcs02(vcpu, vmcs12, from_vmentry, &entry_failure_code)) {
        exit_reason.basic = EXIT_REASON_INVALID_STATE;
        vmcs12->exit_qualification = entry_failure_code;
        goto vmentry_fail_vmexit_guest_mode;
    }

    // 行 3690-3698: 加载 MSR
    if (from_vmentry) {
        failed_index = nested_vmx_load_msr(vcpu,
                           vmcs12->vm_entry_msr_load_addr,
                           vmcs12->vm_entry_msr_load_count);
        if (failed_index) {
            exit_reason.basic = EXIT_REASON_MSR_LOAD_FAIL;
            vmcs12->exit_qualification = failed_index;
            goto vmentry_fail_vmexit_guest_mode;
        }
    }

    // 行 3729-3731: 启动抢占计时器
    if (nested_cpu_has_preemption_timer(vmcs12)) {
        u64 timer_value = vmx_calc_preemption_timer_value(vcpu);
        vmx_start_preemption_timer(vcpu, timer_value);
    }

    // 行 3740: 返回成功
    return NVMX_VMENTRY_SUCCESS;
}
```

### 6.2 __nested_vmx_vmexit() L2 退出

**文件**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/nested.c` 行 5048-5183

```c
void __nested_vmx_vmexit(struct kvm_vcpu *vcpu, u32 vm_exit_reason,
             u32 exit_intr_info, unsigned long exit_qualification,
             u32 exit_insn_len)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);
    struct vmcs12 *vmcs12 = get_vmcs12(vcpu);

    // 行 5056: 丢弃待处理的 MTF陷阱
    vmx->nested.mtf_pending = false;

    // 行 5059: 检查 nested_run_pending
    WARN_ON_ONCE(vmx->nested.nested_run_pending);

    // 行 5073-5074: 服务本地 TLB 刷新请求
    kvm_service_local_tlb_flush_requests(vcpu);

    // 行 5081-5082: 加载 PDPTEs (如果需要)
    if (enable_ept && is_pae_paging(vcpu))
        vmx_ept_load_pdptrs(vcpu);

    // 行 5084: 离开 guest 模式
    leave_guest_mode(vcpu);

    // 行 5086-5087: 取消抢占计时器
    if (nested_cpu_has_preemption_timer(vmcs12))
        hrtimer_cancel(&to_vmx(vcpu)->nested.preemption_timer);

    // 行 5089-5093: 恢复 TSC 偏移
    if (nested_cpu_has(vmcs12, CPU_BASED_USE_TSC_OFFSETTING)) {
        vcpu->arch.tsc_offset = vcpu->arch.l1_tsc_offset;
        if (nested_cpu_has2(vmcs12, SECONDARY_EXEC_TSC_SCALING))
            vcpu->arch.tsc_scaling_ratio = vcpu->arch.l1_tsc_scaling_ratio;
    }

    if (likely(!vmx->fail)) {
        // 行 5096: 同步 vmcs02 到 vmcs12
        sync_vmcs02_to_vmcs12(vcpu, vmcs12);

        // 行 5098-5101: 准备 vmcs12
        if (vm_exit_reason != -1)
            prepare_vmcs12(vcpu, vmcs12, vm_exit_reason,
                       exit_intr_info, exit_qualification,
                       exit_insn_len);

        // 行 5112: 刷新 shadow vmcs12 缓存
        nested_flush_cached_shadow_vmcs12(vcpu, vmcs12);
    }

    // 行 5133-5135: 清除事件队列
    vcpu->arch.nmi_injected = false;
    kvm_clear_exception_queue(vcpu);
    kvm_clear_interrupt_queue(vcpu);

    // 行 5137: 切换回 vmcs01
    vmx_switch_vmcs(vcpu, &vmx->vmcs01);

    // 行 5141-5157: 更新 VMCS 字段
    vmcs_write32(VM_EXIT_MSR_STORE_COUNT, vmx->msr_autostore.nr);
    vmcs_write32(VM_EXIT_MSR_LOAD_COUNT, vmx->msr_autoload.host.nr);
    vmcs_write32(VM_ENTRY_MSR_LOAD_COUNT, vmx->msr_autoload.guest.nr);
    vmcs_write64(TSC_OFFSET, vcpu->arch.tsc_offset);

    // 行 5170: 加载 vmcs12 主机状态
    load_vmcs12_host_state(vcpu, vmcs12);

    // 行 5181-5182: 处理待注入事件
    if (kvm_cpu_has_injectable_intr(vcpu) || vcpu->arch.nmi_pending)
        kvm_make_request(KVM_REQ_EVENT, vcpu);
}
```

### 6.3 嵌套 VMX 状态机

```
                    L0 (KVM Hypervisor)
                          │
                          │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌───────┐          ┌───────┐          ┌───────┐
    │ L1    │          │ L1    │          │ L1    │
    │ VMXON │          │VMLAUNCH│          │ VMRESUME │
    └───────┘          └───────┘          └───────┘
        │                  │                  │
        ▼                  ▼                  ▼
    ┌───────┐          ┌───────┐          ┌───────┐
    │ VMCS01│          │ VMCS01│          │ VMCS01│
    │ Root  │          │ Root  │          │ Root  │
    └───────┘          └───────┘          └───────┘
        │                  │                  │
        │                  ▼                  │
        │          nested_vmx_run()          │
        │                  │                  │
        │                  ▼                  │
        │    ┌─────────────────────────┐      │
        │    │nested_vmx_enter_non_root│      │
        │    │      _mode()            │      │
        │    │      (L2 Entry)         │      │
        │    └─────────────────────────┘      │
        │                  │                  │
        │                  ▼                  │
        │             ┌───────┐               │
        │             │ VMCS02│               │
        │             │ Non-  │               │
        │             │ Root  │               │
        │             └───────┘               │
        │                  │                  │
        │    ┌──────────────┼──────────────┐   │
        │    │              │              │   │
        │    ▼              ▼              ▼   │
        │  ┌─────┐      ┌─────┐        ┌─────┐ │
        │  │ L2  │      │ L2  │        │ L2  │ │
        │  │ VMX │      │ VMX │        │ VMX │ │
        │  │exit │      │exit │        │exit │ │
        │  └──┬──┘      └──┬──┘        └──┬──┘ │
        │     │            │              │    │
        │     ▼            ▼              ▼    │
        │  ┌─────────────────────────────────┐│
        └─►│ __nested_vmx_vmexit()           │┘
           │ (L2 Exit to L1)                │
           └─────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ sync_vmcs02_to_vmcs12 │
              │ prepare_vmcs12()      │
              │ load_vmcs12_host_state│
              └───────────────────────┘
```

### 6.4 三层 VMCS 结构

| VMCS | 用途 | 层级 |
|------|------|------|
| VMCS01 | L0 (KVM) 控制结构 | Root (L0) |
| VMCS02 | L1 在 L2 中运行时的控制结构 | Non-root (L1) |
| VMCS12 | L1 的虚拟机控制结构 (由 L0 保存) | Software structure |

---

## 7. 知识点关联表

### 7.1 核心数据结构关联

| 数据结构 | 文件位置 | 用途描述 |
|----------|----------|----------|
| `struct tdp_iter` | `mmu/tdp_iter.h:76` | TDP MMU 遍历迭代器 |
| `struct kvm_mmu_page` | `mmu/mmu_internal.h:44` | MMU 页表页结构 |
| `struct vmcs12` | `vmx/vmcs12.h` | L1 虚拟机控制结构 |
| `struct x86_emulate_ctxt` | `kvm_emulate.h` | x86 指令模拟上下文 |

### 7.2 关键函数调用链

| 起始函数 | 目标函数 | 关联描述 |
|----------|----------|----------|
| `kvm_tdp_page_fault()` | `kvm_tdp_mmu_map()` | TDP 页面错误入口 |
| `kvm_tdp_mmu_map()` | `for_each_tdp_pte()` | 页表遍历 |
| `for_each_tdp_pte()` | `tdp_iter_next()` | 迭代器推进 |
| `kvm_tdp_mmu_map()` | `tdp_mmu_map_handle_target_level()` | SPTE 安装 |
| `vmx_vcpu_run()` | `__vmx_vcpu_run()` | VMEntry |
| `vmx_vcpu_run()` | `vmx_exit_handlers_fastpath()` | VMExit 处理 |
| `nested_vmx_enter_non_root_mode()` | `enter_guest_mode()` | L2 进入 |
| `__nested_vmx_vmexit()` | `leave_guest_mode()` | L2 退出 |
| `x86_emulate_instruction()` | `x86_emulate_insn()` | 指令执行 |

### 7.3 知识点维度关联

```
                    ┌─────────────────────────────────────────────┐
                    │           KVM 虚拟化核心知识点               │
                    └─────────────────────────────────────────────┘
                                          │
        ┌───────────────┬───────────────┬───────────────┬───────┐
        │               │               │               │       │
        ▼               ▼               ▼               ▼       ▼
   ┌─────────┐    ┌──────────┐    ┌───────────┐   ┌─────────┐ ┌─────┐
   │ 内存虚拟化 │   │  指令模拟  │   │ 嵌套虚拟化  │  │ VMEntry │ │ EPT │
   └────┬────┘    └─────┬────┘    └──────┬────┘   └────┬────┘ │     │
        │               │               │              │      │     │
   ┌────┴────┐    ┌─────┴────┐    ┌──────┴─────┐   ┌────┴────┐ │     │
   │ SPTE   │    │ decoder  │    │ VMCS12    │   │ VMCS    │ │     │
   │ 生成   │    │ emulate  │    │ VMCS02    │   │ 状态加载 │ │     │
   │ 流程   │    │          │    │ L2进入/退出│   │         │ │     │
   └─────────┘    └──────────┘    └───────────┘   └─────────┘ └─────┘
        │               │               │              │           
   ┌────┴────┐    ┌─────┴────┐    ┌──────┴─────┐   ┌────┴────┐      
   │ TLB    │    │ MMIO    │    │ 状态机    │   │ 退出    │      
   │ 刷新   │    │ 模拟    │    │ 转换      │   │ 处理    │      
   └─────────┘    └─────────┘    └───────────┘   └─────────┘      
```

### 7.4 关键文件索引

| 源码文件 | 主要内容 | 关键行号 |
|----------|----------|----------|
| `arch/x86/kvm/mmu/mmu.c` | Shadow MMU, direct_map | 3436-3478 |
| `arch/x86/kvm/mmu/tdp_mmu.c` | TDP MMU 实现 | 1263-1350 |
| `arch/x86/kvm/mmu/tdp_iter.c` | TDP 迭代器 | 39-178 |
| `arch/x86/kvm/mmu/tdp_iter.h` | TDP 迭代器结构/宏 | 76-143 |
| `arch/x86/kvm/vmx/vmx.c` | VMX 实现 | 7605-7756 |
| `arch/x86/kvm/vmx/vmx_ops.h` | EPT 同步函数 | 358-369 |
| `arch/x86/kvm/vmx/nested.c` | 嵌套 VMX | 3606-3741, 5048-5183 |
| `arch/x86/kvm/x86.c` | x86 模拟器入口 | 9416-9560 |

### 7.5 性能关键点

| 操作 | 性能关键 | 优化方向 |
|------|----------|----------|
| TLB 刷新 | `INVEPT` 指令开销 | 批量刷新、选择性刷新 |
| SPTE 安装 | 原子操作竞争 | RCU 保护、乐观更新 |
| 页面遍历 | 锁竞争 | 可中断遍历、yield-safe |
| 指令模拟 | 解码开销 | 缓存解码结果、快速路径 |
| VMEntry/Exit | 状态切换 | VMCS 缓存、懒加载 |

---

## 总结

本文档深入分析了 Linux Kernel KVM 虚拟化子系统的六大核心模块:

1. **kvm_mmu_map_page**: 详述了 SPTE 从生成到安装的完整流程,包括 `__direct_map()` 的影子页表机制和 `tdp_mmu_map()` 的 TDP MMU 机制

2. **tdp_mmu_iter**: 解析了前序遍历算法的核心实现,通过 `try_step_down/side/up` 三个函数协同工作实现高效的页表遍历

3. **ept_sync_root**: 阐明了 EPT/NPT 场景下的 TLB 刷新机制,包括 `INVEPT` 指令的上下文和全局无效化语义

4. **kvm_x86_emulator**: 分析了 x86 指令模拟的完整流程,从解码到执行再到寄存器回写

5. **vmx_vcpu_run**: 揭示了 VMEntry/VMExit 的状态保存恢复细节,以及 VMCS 字段的读写管理

6. **nested VMX**: 描述了 L1/L2 嵌套虚拟化的状态机转换,包括 VMCS12/VMCS02 的协作机制