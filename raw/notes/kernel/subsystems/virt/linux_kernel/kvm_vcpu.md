# Linux 内核 KVM vCPU 管理机制分析

## 1. 概述

KVM (Kernel-based Virtual Machine) 是 Linux 内核中最主流的虚拟化解决方案,基于硬件虚拟化技术(如 Intel VT-x 和 AMD-V)实现。vCPU (虚拟 CPU) 是 KVM 虚拟机的核心执行单元,每个 vCPU 对应一个宿主机的线程。

本文档分析 KVM vCPU 的完整生命周期管理,包括创建与销毁、寄存器状态管理、VM-Exit 处理、VM-Entry 流程和任务调度。

**源码位置:**
- 通用 vCPU 代码: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c`
- x86 vCPU 实现: `/Users/sphinx/github/linux/arch/x86/kvm/x86.c`
- VMX vCPU 实现: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c`
- 头文件: `/Users/sphinx/github/linux/include/linux/kvm_host.h`, `/Users/sphinx/github/linux/arch/x86/include/asm/kvm_host.h`

---

## 2. vCPU 数据结构

### 2.1 通用 vCPU 结构 (kvm_vcpu)

定义于 `/Users/sphinx/github/linux/include/linux/kvm_host.h` 第 324-400 行:

```c
struct kvm_vcpu {
    struct kvm *kvm;              // 所属虚拟机
    int cpu;                      // 当前运行的物理 CPU
    int vcpu_id;                  // 用户空间指定的 vCPU ID
    int vcpu_idx;                 // vCPU 在 kvm->vcpu_array 中的索引
    int mode;                     // vCPU 模式: OUTSIDE_GUEST_MODE, IN_GUEST_MODE, EXITING_GUEST_MODE
    u64 requests;                 // 待处理请求位图
    struct mutex mutex;            // 保护 vCPU 状态的互斥锁
    struct kvm_run *run;          // 与用户空间共享的运行信息
    struct rcuwait wait;          // vCPU 阻塞等待队列
    struct pid *pid;               // vCPU 线程的 PID
    rwlock_t pid_lock;            // 保护 pid 的读写锁
    unsigned int halt_poll_ns;     // 暂停轮询时间
    bool valid_wakeup;            // 唤醒是否有效
    struct kvm_vcpu_arch arch;    // 架构相关状态
    struct kvm_vcpu_stat stat;    // vCPU 统计信息
    struct kvm_dirty_ring dirty_ring;  // 脏页环形缓冲区
};
```

### 2.2 x86 vCPU 架构状态 (kvm_vcpu_arch)

定义于 `/Users/sphinx/github/linux/arch/x86/include/asm/kvm_host.h` 第 796-989 行:

```c
struct kvm_vcpu_arch {
    // 通用寄存器
    unsigned long regs[NR_VCPU_REGS];  // RAX, RBX, RCX, RDX, RSI, RDI, RSP, RBP, R8-R15
    u32 regs_avail;                   // 可用寄存器位图
    u32 regs_dirty;                    // 已修改寄存器位图

    // 控制寄存器
    unsigned long cr0, cr2, cr3, cr4, cr8;
    u64 efer;                         // EFER MSR

    // APIC (高级可编程中断控制器)
    struct kvm_lapic *apic;           // 内核 APIC 上下文
    u64 apic_base;                     // APIC 基址寄存器

    // FPU 状态
    struct fpu_guest guest_fpu;       // 客户机 FPU 上下文

    // MMU 状态
    struct kvm_mmu *mmu;              // 当前使用的 MMU 上下文
    struct kvm_mmu root_mmu;          // L1 根 MMU
    struct kvm_mmu guest_mmu;         // L1 客户机 MMU
    struct kvm_mmu nested_mmu;        // L2 嵌套 MMU (用于 NPT)

    // 异常和中断
    struct kvm_queued_exception exception;      // 待注入异常
    struct kvm_queued_interrupt interrupt;      // 待注入中断

    // TSC (时间戳计数器)
    u64 tsc_offset;                   // 当前 TSC 偏移
    u64 l1_tsc_offset;               // L1 TSC 偏移

    // 性能监控
    u64 microcode_version;            // 微码版本
    u64 arch_capabilities;            // 架构能力
    u64 perf_capabilities;            // 性能能力

    // 状态标志
    int mp_state;                     // 多处理器状态
    bool preempted_in_kernel;         // 是否在内核中被抢占
};
```

### 2.3 vCPU 模式定义

```c
enum {
    OUTSIDE_GUEST_MODE,    // 不在客户机模式
    IN_GUEST_MODE,        // 正在运行客户机代码
    EXITING_GUEST_MODE,   // 正在退出客户机模式
    READING_SHADOW_PAGE_TABLES,  // 正在读取影子页表
};
```

---

## 3. vCPU 创建与销毁

### 3.1 创建流程概览

```
用户空间 ioctl(KVM_CREATE_VCPU)
    |
    v
kvm_vm_ioctl_create_vcpu()  [kvm_main.c:4158]
    |
    +-> kvm_arch_vcpu_precreate()     架构相关预处理
    +-> kmem_cache_zalloc()           分配 vCPU 结构
    +-> alloc_page()                  分配 kvm_run 页面
    +-> kvm_vcpu_init()               初始化 vCPU 基本状态
    +-> kvm_arch_vcpu_create()        架构相关创建
    +-> kvm_dirty_ring_alloc()        分配脏页环
    +-> xa_insert()                   加入 vcpu_array
    +-> create_vcpu_fd()              创建文件描述符
    +-> kvm_arch_vcpu_postcreate()    创建后处理
```

### 3.2 核心创建函数

#### kvm_vm_ioctl_create_vcpu() - 主入口

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:4158-4276`

```c
static int kvm_vm_ioctl_create_vcpu(struct kvm *kvm, unsigned long id)
{
    int r;
    struct kvm_vcpu *vcpu;
    struct page *page;

    // 1. 验证 vCPU ID 不超过最大限制
    if (id >= KVM_MAX_VCPU_IDS)
        return -EINVAL;

    mutex_lock(&kvm->lock);

    // 2. 检查是否已达到最大 vCPU 数量
    if (kvm->created_vcpus >= kvm->max_vcpus) {
        mutex_unlock(&kvm->lock);
        return -EINVAL;
    }

    // 3. 架构相关预处理
    r = kvm_arch_vcpu_precreate(kvm, id);
    if (r) {
        mutex_unlock(&kvm->lock);
        return r;
    }

    kvm->created_vcpus++;
    mutex_unlock(&kvm->lock);

    // 4. 分配 vCPU 结构 (slab 缓存)
    vcpu = kmem_cache_zalloc(kvm_vcpu_cache, GFP_KERNEL_ACCOUNT);

    // 5. 分配 kvm_run 页面用于用户空间通信
    page = alloc_page(GFP_KERNEL_ACCOUNT | __GFP_ZERO);
    vcpu->run = page_address(page);

    // 6. 初始化 vCPU 基本状态
    kvm_vcpu_init(vcpu, kvm, id);

    // 7. 架构相关创建 (x86: 创建 LAPIC, MMU, FPU, emulate context 等)
    r = kvm_arch_vcpu_create(vcpu);
    if (r)
        goto vcpu_free_run_page;

    // 8. 分配脏页环 (可选)
    if (kvm->dirty_ring_size) {
        r = kvm_dirty_ring_alloc(kvm, &vcpu->dirty_ring, id, kvm->dirty_ring_size);
        if (r)
            goto arch_vcpu_destroy;
    }

    // 9. 加入 vCPU 数组
    mutex_lock(&kvm->lock);
    vcpu->vcpu_idx = atomic_read(&kvm->online_vcpus);
    xa_insert(&kvm->vcpu_array, vcpu->vcpu_idx, vcpu, GFP_KERNEL_ACCOUNT);

    // 10. 创建文件描述符供用户空间访问
    r = create_vcpu_fd(vcpu);

    // 11. 增加在线 vCPU 计数
    smp_wmb();
    atomic_inc(&kvm->online_vcpus);

    kvm_arch_vcpu_postcreate(vcpu);
    kvm_create_vcpu_debugfs(vcpu);
    return r;
}
```

#### kvm_vcpu_init() - 基本初始化

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:442-465`

```c
static void kvm_vcpu_init(struct kvm_vcpu *vcpu, struct kvm *kvm, unsigned id)
{
    mutex_init(&vcpu->mutex);
    vcpu->cpu = -1;
    vcpu->kvm = kvm;
    vcpu->vcpu_id = id;
    vcpu->pid = NULL;
    rwlock_init(&vcpu->pid_lock);
    rcuwait_init(&vcpu->wait);
    kvm_async_pf_vcpu_init(vcpu);

    kvm_vcpu_set_in_spin_loop(vcpu, false);
    kvm_vcpu_set_dy_eligible(vcpu, false);
    vcpu->preempted = false;
    vcpu->ready = false;
    preempt_notifier_init(&vcpu->preempt_notifier, &kvm_preempt_ops);
    vcpu->last_used_slot = NULL;

    snprintf(vcpu->stats_id, sizeof(vcpu->stats_id), "kvm-%d/vcpu-%d",
             task_pid_nr(current), id);
}
```

#### kvm_arch_vcpu_create() - x86 架构创建

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:12736-12814`

```c
int kvm_arch_vcpu_create(struct kvm_vcpu *vcpu)
{
    struct page *page;
    int r;

    vcpu->arch.last_vmentry_cpu = -1;
    vcpu->arch.regs_avail = ~0;
    vcpu->arch.regs_dirty = ~0;

    kvm_gpc_init(&vcpu->arch.pv_time, vcpu->kvm);

    // 设置初始多处理器状态
    if (!irqchip_in_kernel(vcpu->kvm) || kvm_vcpu_is_reset_bsp(vcpu))
        kvm_set_mp_state(vcpu, KVM_MP_STATE_RUNNABLE);
    else
        kvm_set_mp_state(vcpu, KVM_MP_STATE_UNINITIALIZED);

    // 创建 MMU 结构
    r = kvm_mmu_create(vcpu);
    if (r < 0)
        return r;

    // 创建 LAPIC (本地 APIC)
    r = kvm_create_lapic(vcpu);
    if (r < 0)
        goto fail_mmu_destroy;

    // 分配 PIO 数据缓冲区
    page = alloc_page(GFP_KERNEL_ACCOUNT | __GFP_ZERO);
    if (!page)
        goto fail_free_lapic;
    vcpu->arch.pio_data = page_address(page);

    // 分配 MCE (机器检查异常) 银行
    vcpu->arch.mce_banks = kcalloc(KVM_MAX_MCE_BANKS * 4, sizeof(u64), GFP_KERNEL_ACCOUNT);
    vcpu->arch.mcg_cap = KVM_MAX_MCE_BANKS;

    // 分配 WBINVD 脏掩码
    if (!zalloc_cpumask_var(&vcpu->arch.wbinvd_dirty_mask, GFP_KERNEL_ACCOUNT))
        goto fail_free_mce_banks;

    // 创建仿真上下文
    if (!alloc_emulate_ctxt(vcpu))
        goto free_wbinvd_dirty_mask;

    // 分配 guest FPU 状态
    if (!fpu_alloc_guest_fpstate(&vcpu->arch.guest_fpu)) {
        pr_err("failed to allocate vcpu's fpu\n");
        goto free_emulate_ctxt;
    }

    // 初始化异步页错误哈希表
    kvm_async_pf_hash_reset(vcpu);

    // 初始化 PMU (性能监控单元)
    kvm_pmu_init(vcpu);

    // 架构特定初始化 (VMX/SVM)
    r = kvm_x86_call(vcpu_create)(vcpu);
    if (r)
        goto free_guest_fpu;

    // Xen vCPU 初始化
    kvm_xen_init_vcpu(vcpu);

    // 加载 vCPU 到当前物理 CPU
    vcpu_load(vcpu);

    // 根据 CPUID 设置 vCPU 状态
    kvm_vcpu_after_set_cpuid(vcpu);

    // 设置 TSC 频率
    kvm_set_tsc_khz(vcpu, vcpu->kvm->arch.default_tsc_khz);

    // 重置 vCPU 状态
    kvm_vcpu_reset(vcpu, false);

    // 初始化 MMU
    kvm_init_mmu(vcpu);

    vcpu_put(vcpu);
    return 0;

// 错误处理路径 (省略部分)
}
```

### 3.3 销毁流程

#### kvm_vcpu_destroy() - 主入口

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:467-481`

```c
static void kvm_vcpu_destroy(struct kvm_vcpu *vcpu)
{
    // 架构相关销毁
    kvm_arch_vcpu_destroy(vcpu);

    // 释放脏页环
    kvm_dirty_ring_free(&vcpu->dirty_ring);

    // 释放 PID 引用
    put_pid(vcpu->pid);

    // 释放 kvm_run 页面
    free_page((unsigned long)vcpu->run);

    // 释放 vCPU slab 对象
    kmem_cache_free(kvm_vcpu_cache, vcpu);
}
```

#### kvm_arch_vcpu_destroy() - x86 架构销毁

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:12847-12876`

```c
void kvm_arch_vcpu_destroy(struct kvm_vcpu *vcpu)
{
    int idx, cpu;

    // 清除异步页错误完成队列
    kvm_clear_async_pf_completion_queue(vcpu);

    // 卸载 MMU
    kvm_mmu_unload(vcpu);

    // 重置时钟
    kvmclock_reset(vcpu);

    // 清除 per-CPU vCPU 指针
    for_each_possible_cpu(cpu)
        cmpxchg(per_cpu_ptr(&last_vcpu, cpu), vcpu, NULL);

    // 架构特定销毁 (VMX/SVM)
    kvm_x86_call(vcpu_free)(vcpu);

    // 释放仿真上下文
    kmem_cache_free(x86_emulator_cache, vcpu->arch.emulate_ctxt);

    // 释放 WBINVD 掩码
    free_cpumask_var(vcpu->arch.wbinvd_dirty_mask);

    // 释放 FPU 状态
    fpu_free_guest_fpstate(&vcpu->arch.guest_fpu);

    // Xen 和 Hyper-V 清理
    kvm_xen_destroy_vcpu(vcpu);
    kvm_hv_vcpu_uninit(vcpu);

    // 销毁 PMU
    kvm_pmu_destroy(vcpu);

    // 释放 MCE 银行
    kfree(vcpu->arch.mce_banks);
    kfree(vcpu->arch.mci_ctl2_banks);

    // 释放 LAPIC
    kvm_free_lapic(vcpu);

    // 销毁 MMU
    idx = srcu_read_lock(&vcpu->kvm->srcu);
    kvm_mmu_destroy(vcpu);
    srcu_read_unlock(&vcpu->kvm->srcu, idx);

    // 释放 PIO 数据和 CPUID 条目
    free_page((unsigned long)vcpu->arch.pio_data);
    kvfree(vcpu->arch.cpuid_entries);
}
```

### 3.4 vCPU 生命周期流程图

```
                                    用户空间
                                      |
                    ioctl(KVM_CREATE_VCPU) |
                                      v
                            +---------------------+
                            | kvm_vm_ioctl_create |
                            |       _vcpu()      |
                            +---------------------+
                                      |
            +-------------+-----------+----------+------------+
            |             |                        |            |
            v             v                        v            v
    +------------+  +-------------+  +------------------+  +--------+
    | kvm_arch_  |  | kvm_vcpu_  |  | kvm_arch_vcpu_  |  | 创建   |
    | vcpu_pre   |  | init()     |  | create()        |  | debugfs|
    | create()   |  |            |  | (分配LAPIC,MMU, |  |        |
    +------------+  +-------------+  | FPU,emulate_ctxt)  +--------+
                                    +------------------+          |
                                      |                         |
                                      v                         v
                            +---------------------+
                            | kvm_arch_vcpu_     |
                            | postcreate()        |
                            +---------------------+
                                      |
                                      v
                            ====================
                            =   vCPU 运行状态  =
                            ====================

                ioctl(KVM_RUN) 循环...
                                      |
                                      v
                            +---------------------+
                            | kvm_arch_vcpu_     |
                            | ioctl_run()        |
                            +---------------------+
                                      |
            +-------------+-----------+----------+------------+
            |             |                        |            |
            v             v                        v            v
    +------------+  +-------------+  +------------------+  +--------+
    | vcpu_load()|  | 加载 FPU   |  | vcpu_enter_guest()|  | VMX/   |
    |            |  | 激活信号   |  |                  |  | SVM    |
    +------------+  +-------------+  +------------------+  | vcpu_  |
                                    |                  |  | run()  |
                                    +------------------+  +--------+
                                                      |
                                                      v
                                            +------------------+
                                            |   VM-Exit 处理   |
                                            +------------------+
                                                      |
                                                      v
                                            ===================
                                            =   返回用户空间  =
                                            ===================

ioctl(KVM_DESTROY_VCPU) 或 VM 关闭
                                      |
                                      v
                            +---------------------+
                            | kvm_vcpu_destroy() |
                            +---------------------+
                                      |
            +-------------------------+-------------+
            |                           |             |
            v                           v             v
    +------------+  +------------------+  +------------------+
    | kvm_arch_  |  | kvm_dirty_ring_ |  | kmem_cache_free()|
    | vcpu_destroy|  | free()          |  | (释放 vCPU 结构) |
    +------------+  +------------------+  +------------------+
```

---

## 4. vCPU 寄存器状态管理

### 4.1 寄存器结构

x86 vCPU 寄存器定义于 `kvm_vcpu_arch` 结构中的 `regs[]` 数组,包括:

```c
// 定义于 /Users/sphinx/github/linux/arch/x86/include/asm/kvm_host.h
enum {
    VCPU_REGS_RAX = 0,
    VCPU_REGS_RCX = 1,
    VCPU_REGS_RDX = 2,
    VCPU_REGS_RBX = 3,
    VCPU_REGS_RSP = 4,
    VCPU_REGS_RBP = 5,
    VCPU_REGS_RSI = 6,
    VCPU_REGS_RDI = 7,
#ifdef CONFIG_X86_64
    VCPU_REGS_R8  = 8,
    VCPU_REGS_R9  = 9,
    VCPU_REGS_R10 = 10,
    VCPU_REGS_R11 = 11,
    VCPU_REGS_R12 = 12,
    VCPU_REGS_R13 = 13,
    VCPU_REGS_R14 = 14,
    VCPU_REGS_R15 = 15,
#endif
    NR_VCPU_REGS,  // 16 (x86-64) 或 8 (x86)
};
```

### 4.2 寄存器读写接口

#### 寄存器读取

```c
// 位置: /Users/sphinx/github/linux/arch/x86/kvm/x86.c:12052-12073
static void __get_regs(struct kvm_vcpu *vcpu, struct kvm_regs *regs)
{
    // 处理仿真上下文字符串寄存器同步
    if (vcpu->arch.emulate_regs_need_sync_to_vcpu) {
        emulator_writeback_register_cache(vcpu->arch.emulate_ctxt);
        vcpu->arch.emulate_regs_need_sync_to_vcpu = false;
    }
    regs->rax = kvm_rax_read(vcpu);
    regs->rbx = kvm_rbx_read(vcpu);
    regs->rcx = kvm_rcx_read(vcpu);
    regs->rdx = kvm_rdx_read(vcpu);
    regs->rsi = kvm_rsi_read(vcpu);
    regs->rdi = kvm_rdi_read(vcpu);
    regs->rsp = kvm_rsp_read(vcpu);
    regs->rbp = kvm_rbp_read(vcpu);
    // ... R8-R15 ...
    regs->rip = kvm_rip_read(vcpu);
    regs->rflags = kvm_get_rflags(vcpu);
}
```

#### 寄存器写入

```c
// 位置: /Users/sphinx/github/linux/arch/x86/kvm/x86.c:12087-12109
static void __set_regs(struct kvm_vcpu *vcpu, struct kvm_regs *regs)
{
    vcpu->arch.emulate_regs_need_sync_from_vcpu = true;
    vcpu->arch.emulate_regs_need_sync_to_vcpu = false;

    kvm_rax_write(vcpu, regs->rax);
    kvm_rbx_write(vcpu, regs->rbx);
    // ... 其他寄存器 ...
}
```

### 4.3 GDT (全局描述符表) 访问

```c
// 位置: /Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c:3860-3870
void vmx_get_gdt(struct kvm_vcpu *vcpu, struct desc_ptr *dt)
{
    dt->size = vmcs_read32(GUEST_GDTR_LIMIT);   // 读取 GDT 限长
    dt->address = vmcs_readl(GUEST_GDTR_BASE);   // 读取 GDT 基址
}

void vmx_set_gdt(struct kvm_vcpu *vcpu, struct desc_ptr *dt)
{
    vmcs_write32(GUEST_GDTR_LIMIT, dt->size);
    vmcs_writel(GUEST_GDTR_BASE, dt->address);
}
```

### 4.4 MSR (Model Specific Register) 访问

#### MSR 读取

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:1967-2033`

```c
static int __kvm_get_msr(struct kvm_vcpu *vcpu, u32 index, u64 *data, bool host_initiated)
{
    struct msr_data msr_info;

    msr_info.index = index;
    msr_info.host_initiated = host_initiated;

    if (kvm_x86_call(get_msr)(vcpu, &msr_info)) {
        // 尝试通用 MSR 处理
        if (!kvm_get_msr_common(vcpu, &msr_info)) {
            *data = msr_info.data;
            return 0;
        }
        return 1;  // MSR 不存在
    }
    *data = msr_info.data;
    return 0;
}

// 导出给用户空间的接口
int kvm_get_msr(struct kvm_vcpu *vcpu, u32 index, u64 *data)
{
    return __kvm_get_msr(vcpu, index, data, false);
}
```

#### MSR 写入

```c
static int __kvm_set_msr(struct kvm_vcpu *vcpu, u32 index, u64 data, bool host_initiated)
{
    struct msr_data msr_info;

    msr_info.index = index;
    msr_info.data = data;
    msr_info.host_initiated = host_initiated;

    // 优先尝试架构特定处理
    if (kvm_x86_call(set_msr)(vcpu, &msr_info))
        return 0;  // 成功

    // 回退到通用 MSR 处理
    return kvm_set_msr_common(vcpu, &msr_info);
}
```

#### 常见 MSR

| MSR | 功能 | 说明 |
|-----|------|-----|
| MSR_IA32_TSC | 时间戳计数器 | vCPU 的 TSC 值 |
| MSR_IA32_APICBASE | APIC 基址 | 本地 APIC 基址 |
| EFER | 扩展功能启用寄存器 | SCE, LME, LMA, NXE 等位 |
| CR0, CR4 | 控制寄存器 | PG, PE, WP 等标志 |
| MSR_KVM_POLL_CONTROL | 暂停轮询控制 | 控制 vCPU 暂停时的轮询行为 |

---

## 5. VM-Exit 处理

### 5.1 VM-Exit 概念

当客户机执行特权指令或发生外部事件时,硬件自动退出到 VMM (虚拟机监控器) 运行。这个过程称为 VM-Exit。

### 5.2 VM-Exit 原因码

**Intel VMX 退出原因** (部分):

| 原因码 | 名称 | 说明 |
|--------|------|------|
| 0 | EXIT_REASON_EXCEPTION_NMI | 异常或 NMI |
| 1 | EXIT_REASON_EXTERNAL_INTERRUPT | 外部中断 |
| 10 | EXIT_REASON_CPUID | 执行 CPUID 指令 |
| 12 | EXIT_REASON_HLT | 执行 HLT 指令 |
| 14 | EXIT_REASON_INVD | 执行 INVD 指令 |
| 15 | EXIT_REASON_INVLPG | 执行 INVLPG 指令 |
| 18 | EXIT_REASON_MSR_READ | 读取 MSR |
| 19 | EXIT_REASON_MSR_WRITE | 写入 MSR |
| 24 | EXIT_REASON_PAUSE | 执行 PAUSE 指令 |
| 30 | EXIT_REASON_EPT_VIOLATION | EPT 违规 |
| 33 | EXIT_REASON_EPT_MISCONFIG | EPT 错误配置 |
| 36 | EXIT_REASON_PREEMPTION_TIMER | 抢占计时器到期 |
| 48 | EXIT_REASON_VMCALL | 执行 VMCALL |
| 54 | EXIT_REASON_VMCLEAR | 执行 VMCLEAR |
| 55 | EXIT_REASON_VMLAUNCH | 执行 VMLAUNCH |
| 56 | EXIT_REASON_VMPTRLD | 执行 VMPTRLD |
| 57 | EXIT_REASON_VMPTRST | 执行 VMPTRST |
| 58 | EXIT_REASON_VMREAD | 执行 VMREAD |
| 59 | EXIT_REASON_VMWRITE | 执行 VMWRITE |
| 60 | EXIT_REASON_VMRESUME | 执行 VMRESUME |
| 61 | EXIT_REASON_VMXOFF | 执行 VMXOFF |
| 62 | EXIT_REASON_VMXON | 执行 VMXON |
| 63 | EXIT_REASON_CR_ACCESS | 控制寄存器访问 |
| 64 | EXIT_REASON_DR_ACCESS | 调试寄存器访问 |
| 66 | EXIT_REASON_IO_INSTRUCTION | I/O 指令 |

### 5.3 VM-Exit 处理流程

```
VM-Exit 发生
     |
     v
+-------------------------+
| __vmx_handle_exit()     |  [vmx.c:6781]
| 1. 获取退出原因          |
| 2. 处理 PML 缓冲区       |
| 3. 检查嵌套 VM-Exit      |
| 4. 处理状态无效情况      |
| 5. 处理向量化中断        |
+-------------------------+
     |
     v
+-------------------------+
| exit_fastpath 检查      |
| 如果是快速路径,直接返回 |
+-------------------------+
     |
     v
+-------------------------+
| 查找退出处理函数        |
| kvm_vmx_exit_handlers[] |
+-------------------------+
     |
     +----+------------+----+----+----+----+----+
     |         |         |    |    |    |    |    |
     v         v         v    v    v    v    v    v
  CPUID   EXCEPTION  MSR   HLT  EPT  I/O  ...
```

### 5.4 __vmx_handle_exit() 实现

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c:6781-6929`

```c
static int __vmx_handle_exit(struct kvm_vcpu *vcpu, fastpath_t exit_fastpath)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);
    union vmx_exit_reason exit_reason = vmx_get_exit_reason(vcpu);
    u32 vectoring_info = vmx->idt_vectoring_info;
    u16 exit_handler_index;

    // 1. 刷新 PML 缓冲区
    if (enable_pml && !is_guest_mode(vcpu))
        vm x_flush_pml_buffer(vcpu);

    // 2. 检查嵌套 VM-Exit
    if (is_guest_mode(vcpu)) {
        if (exit_reason.basic == EXIT_REASON_PML_FULL)
            goto unexpected_vmexit;

        // 标记 VMCS12 页为脏
        nested_vmx_mark_all_vmcs12_pages_dirty(vcpu);

        // 如果需要仿真是 L2 状态,生成三重故障
        if (vmx->vt.emulation_required) {
            nested_vmx_vmexit(vcpu, EXIT_REASON_TRIPLE_FAULT, 0, 0);
            return 1;
        }

        // 处理嵌套 VM-Exit
        if (nested_vmx_reflect_vmexit(vcpu))
            return 1;
    }

    // 3. 如果客户机状态无效,开始仿真
    if (vmx->vt.emulation_required)
        return handle_invalid_guest_state(vcpu);

    // 4. 处理 VM-Entry 失败
    if (exit_reason.failed_vmentry) {
        vcpu->run->exit_reason = KVM_EXIT_FAIL_ENTRY;
        vcpu->run->fail_entry.hardware_entry_failure_reason = exit_reason.full;
        return 0;
    }

    // 5. 处理 VM-Entry 失败标志
    if (unlikely(vmx->fail)) {
        vcpu->run->exit_reason = KVM_EXIT_FAIL_ENTRY;
        vcpu->run->fail_entry.hardware_entry_failure_reason =
            vmcs_read32(VM_INSTRUCTION_ERROR);
        return 0;
    }

    // 6. 处理向量化信息
    if ((vectoring_info & VECTORING_INFO_VALID_MASK) &&
        (exit_reason.basic != EXIT_REASON_EXCEPTION_NMI &&
         exit_reason.basic != EXIT_REASON_EPT_VIOLATION &&
         // ... 其他异常类型 ... ))
    {
        kvm_prepare_event_vectoring_exit(vcpu, INVALID_GPA);
        return 0;
    }

    // 7. 快速路径退出
    if (exit_fastpath != EXIT_FASTPATH_NONE)
        return 1;

    // 8. 查找并调用退出处理函数
    if (exit_reason.basic >= kvm_vmx_max_exit_handlers)
        goto unexpected_vmexit;

    exit_handler_index = array_index_nospec((u16)exit_reason.basic,
                                            kvm_vmx_max_exit_handlers);
    if (!kvm_vmx_exit_handlers[exit_handler_index])
        goto unexpected_vmexit;

    return kvm_vmx_exit_handlers[exit_handler_index](vcpu);
}
```

### 5.5 常见退出处理函数

| 处理函数 | 对应退出 | 位置 |
|----------|----------|------|
| handle_exception_nmi | EXIT_REASON_EXCEPTION_NMI | vmx.c |
| handle_external_interrupt | EXIT_REASON_EXTERNAL_INTERRUPT | vmx.c |
| handle_cpuid | EXIT_REASON_CPUID | vmx.c |
| kvm_emulate_halt | EXIT_REASON_HLT | x86.c |
| kvm_emulate_wrmsr | EXIT_REASON_MSR_WRITE | x86.c |
| handle_ept_misconfig | EXIT_REASON_EPT_MISCONFIG | vmx.c |
| handle_preemption_timer | EXIT_REASON_PREEMPTION_TIMER | vmx.c |

---

## 6. VM-Entry 流程

### 6.1 VM-Entry 概览

```
用户空间 KVM_RUN ioctl
         |
         v
kvm_arch_vcpu_ioctl_run()  [x86.c:11919]
         |
         +-> vcpu_load()           加载 vCPU 到当前物理 CPU
         +-> kvm_sigset_activate() 激活信号掩码
         +-> kvm_load_guest_fpu() 加载客户机 FPU
         +-> vcpu_run()            运行循环
         |         |
         |         v
         |  +---------------------+
         |  | vcpu_enter_guest() |  [x86.c:11079]
         |  +---------------------+
         |         |
         |         +-> 处理请求 (TLB flush, 时钟更新等)
         |         +-> 注入待处理事件
         |         +-> 加载 VMCS 状态
         |         +-> 禁用中断
         |         +-> 设置 IN_GUEST_MODE
         |         +-> kvm_x86_call(vcpu_run)  // VMX: vmx_vcpu_run()
         |                      |
         |                      v
         |              +----------------+
         |              | VM-Entry 发生   |
         |              +----------------+
         |                      |
         |                      v
         |              +----------------+
         |              | VM-Exit 返回   |
         |              +----------------+
         |                      |
         +<- - - - - - - - - - -+
         |
         +-> kvm_put_guest_fpu() 保存客户机 FPU
         +-> store_regs()       保存寄存器
         +-> vcpu_put()         释放 vCPU
```

### 6.2 vcpu_enter_guest() 实现

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:11079-11470`

```c
static int vcpu_enter_guest(struct kvm_vcpu *vcpu)
{
    int r;
    bool req_int_win;
    fastpath_t exit_fastpath;
    u64 run_flags, debug_ctl;
    bool req_immediate_exit = false;

    // 1. 处理待处理请求
    if (kvm_request_pending(vcpu)) {
        if (kvm_check_request(KVM_REQ_VM_DEAD, vcpu)) {
            r = -EIO;
            goto out;
        }

        // 脏页环检查
        if (kvm_dirty_ring_check_request(vcpu)) {
            r = 0;
            goto out;
        }

        // MMU 相关请求
        if (kvm_check_request(KVM_REQ_MMU_FREE_OBSOLETE_ROOTS, vcpu))
            kvm_mmu_free_obsolete_roots(vcpu);

        // 计时器迁移
        if (kvm_check_request(KVM_REQ_MIGRATE_TIMER, vcpu))
            __kvm_migrate_timers(vcpu);

        // 时钟更新
        if (kvm_check_request(KVM_REQ_CLOCK_UPDATE, vcpu)) {
            r = kvm_guest_time_update(vcpu);
            if (unlikely(r))
                goto out;
        }

        // TLB 刷新
        if (kvm_check_request(KVM_REQ_TLB_FLUSH, vcpu))
            kvm_vcpu_flush_tlb_all(vcpu);

        // NMI 处理
        if (kvm_check_request(KVM_REQ_NMI, vcpu))
            process_nmi(vcpu);

        // 等等...
    }

    // 2. 处理事件注入
    if (kvm_check_request(KVM_REQ_EVENT, vcpu) || req_int_win) {
        ++vcpu->stat.req_event;
        r = kvm_apic_accept_events(vcpu);
        if (r < 0) {
            r = 0;
            goto out;
        }
        if (vcpu->arch.mp_state == KVM_MP_STATE_INIT_RECEIVED) {
            r = 1;
            goto out;
        }

        r = kvm_check_and_inject_events(vcpu, &req_immediate_exit);
        // ...
    }

    // 3. 重新加载 MMU
    r = kvm_mmu_reload(vcpu);
    if (unlikely(r))
        goto cancel_injection;

    preempt_disable();

    // 4. 准备切换到客户机
    kvm_x86_call(prepare_switch_to_guest)(vcpu);

    // 5. 禁用中断
    local_irq_disable();

    // 6. 设置 IN_GUEST_MODE
    smp_store_release(&vcpu->mode, IN_GUEST_MODE);

    // 7. 释放 SRCU 锁
    kvm_vcpu_srcu_read_unlock(vcpu);
    smp_mb__after_srcu_read_unlock();

    // 8. 同步 Posted Interrupt
    if (kvm_lapic_enabled(vcpu))
        kvm_x86_call(sync_pir_to_irr)(vcpu);

    // 9. 检查退出请求
    if (kvm_vcpu_exit_request(vcpu)) {
        vcpu->mode = OUTSIDE_GUEST_MODE;
        smp_wmb();
        local_irq_enable();
        preempt_enable();
        kvm_vcpu_srcu_read_lock(vcpu);
        r = 1;
        goto cancel_injection;
    }

    // 10. 运行标志
    run_flags = 0;
    if (req_immediate_exit)
        run_flags |= KVM_RUN_FORCE_IMMEDIATE_EXIT;

    // 11. 加载调试寄存器
    // ...

    // 12. 加载客户机 FPU/PKRU
    fpregs_assert_state_consistent();
    kvm_load_guest_pkru(vcpu);

    // 13. 执行 VM-Entry (核心!)
    for (;;) {
        exit_fastpath = kvm_x86_call(vcpu_run)(vcpu, run_flags);
        if (likely(exit_fastpath != EXIT_FASTPATH_REENTER_GUEST))
            break;

        // 同步 Posted Interrupt
        if (kvm_lapic_enabled(vcpu))
            kvm_x86_call(sync_pir_to_irr)(vcpu);

        // 检查退出请求
        if (unlikely(kvm_vcpu_exit_request(vcpu))) {
            exit_fastpath = EXIT_FASTPATH_EXIT_HANDLED;
            break;
        }

        run_flags = 0;
        ++vcpu->stat.exits;
    }

    // 14. 保存客户机 PKRU
    kvm_load_host_pkru(vcpu);

    // 15. 处理 VM-Exit
    // ...

out:
    // 处理取消注入等
    return r;
}
```

### 6.3 vmx_vcpu_run() 实现

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c:7580-7610`

```c
fastpath_t vmx_vcpu_run(struct kvm_vcpu *vcpu, u64 run_flags)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);

    // 1. 加载 guest 寄存器
    vmx_vcpu_load(vcpu, cpu);

    // 2. 加载 VMCS
    vmx_load_vmcs(vmx);

    // 3. 加载 guest 状态区域
    vmcs_writel(GUEST_RSP, vcpu->arch.regs[VCPU_REGS_RSP]);
    vmcs_writel(GUEST_RIP, vcpu->arch.regs[VCPU_REGS_RIP]);

    // 4. 加载 MSR
    vmx_load_msrs(vcpu);

    // 5. 刷新 EPTP (如果需要)
    // ...

    // 6. 执行 VM-Entry
    __vmx_vcpu_run(vmx, (unsigned long *)&vcpu->arch.regs);

    // 7. VM-Exit 发生!保存状态
    vcpu->arch.regs[VCPU_REGS_RSP] = vmcs_readl(GUEST_RSP);
    vcpu->arch.regs[VCPU_REGS_RIP] = vmcs_readl(GUEST_RIP);

    // 8. 保存 MSR
    vmx_save_msrs(vcpu);

    // 9. 更新 VM-Exit 信息
    vmx->fail = vmcs_read32(VM_INSTRUCTION_ERROR);
    vmx->exit_reason = vmcs_read32(VM_EXIT_REASON);

    // 10. 返回快速路径类型
    return exit_fastpath;
}
```

---

## 7. vCPU 任务调度

### 7.1 vCPU 与宿主机调度器交互

KVM vCPU 以线程形式运行在宿主机上,参与宿主机的调度。当 vCPU 线程被调度时,它执行客户机代码;当被抢占时,客户机暂停。

**关键机制:**

1. **preempt_notifier**: vCPU 实现 `preempt_notifier` 接口,在宿主机调度器进行抢占时收到通知
2. **vcpu_load/vcpu_put**: 在 vCPU 切换到不同物理 CPU 时调用,用于保存/恢复物理 CPU 相关状态
3. **kvm_vcpu_block/kvm_vcpu_kick**: vCPU 阻塞和唤醒机制

### 7.2 vCPU 加载到物理 CPU

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:165-173`

```c
void vcpu_load(struct kvm_vcpu *vcpu)
{
    int cpu = get_cpu();

    // 记录当前运行的 vCPU (per-CPU 变量)
    __this_cpu_write(kvm_running_vcpu, vcpu);

    // 注册抢占通知器
    preempt_notifier_register(&vcpu->preempt_notifier);

    // 架构相关加载 (x86: 加载 FPU, MSR 等)
    kvm_arch_vcpu_load(vcpu, cpu);

    put_cpu();
}
```

### 7.3 vCPU 阻塞 (kvm_vcpu_block)

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:3649-3679`

```c
bool kvm_vcpu_block(struct kvm_vcpu *vcpu)
{
    struct rcuwait *wait = kvm_arch_vcpu_get_wait(vcpu);
    bool waited = false;

    vcpu->stat.generic.blocking = 1;

    preempt_disable();
    kvm_arch_vcpu_blocking(vcpu);
    prepare_to_rcuwait(wait);
    preempt_enable();

    for (;;) {
        set_current_state(TASK_INTERRUPTIBLE);

        // 检查 vCPU 是否可运行
        if (kvm_vcpu_check_block(vcpu) < 0)
            break;

        waited = true;
        schedule();  // 调度出去,让出物理 CPU
    }

    preempt_disable();
    finish_rcuwait(wait);
    kvm_arch_vcpu_unblocking(vcpu);
    preempt_enable();

    vcpu->stat.generic.blocking = 0;

    return waited;
}
```

### 7.4 x86 架构的 vCPU 阻塞处理

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:11594-11645`

```c
static inline int vcpu_block(struct kvm_vcpu *vcpu)
{
    bool hv_timer;

    if (!kvm_arch_vcpu_runnable(vcpu)) {
        // 将 hypervisor 计时器切换到软件模式
        hv_timer = kvm_lapic_hv_timer_in_use(vcpu);
        if (hv_timer)
            kvm_lapic_switch_to_sw_timer(vcpu);

        kvm_vcpu_srcu_read_unlock(vcpu);

        // 根据状态选择阻塞方式
        if (vcpu->arch.mp_state == KVM_MP_STATE_HALTED)
            kvm_vcpu_halt(vcpu);  // HLT 指令导致
        else
            kvm_vcpu_block(vcpu);  // 等待事件

        kvm_vcpu_srcu_read_lock(vcpu);

        if (hv_timer)
            kvm_lapic_switch_to_hv_timer(vcpu);

        // 如果 vCPU 仍然不可运行,返回 1
        if (!kvm_arch_vcpu_runnable(vcpu))
            return 1;
    }

    // 处理嵌套事件
    if (is_guest_mode(vcpu)) {
        int r = kvm_check_nested_events(vcpu);
        if (r < 0 && r != -EBUSY)
            return 0;
    }

    return 1;
}
```

### 7.5 vCPU 唤醒 (kvm_vcpu_kick)

**位置:** `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:3816-3861`

```c
void __kvm_vcpu_kick(struct kvm_vcpu *vcpu, bool wait)
{
    int me, cpu;

    // 尝试直接唤醒 (如果 vCPU 在阻塞)
    if (kvm_vcpu_wake_up(vcpu))
        return;

    me = get_cpu();

    // 如果当前物理 CPU 正在运行该 vCPU,设置退出标志
    if (vcpu == __this_cpu_read(kvm_running_vcpu)) {
        if (vcpu->mode == IN_GUEST_MODE)
            WRITE_ONCE(vcpu->mode, EXITING_GUEST_MODE);
        goto out;
    }

    // 发送 IPI 强制 vCPU 退出客户机模式
    if (kvm_arch_vcpu_should_kick(vcpu)) {
        cpu = READ_ONCE(vcpu->cpu);
        if (cpu != me && (unsigned int)cpu < nr_cpu_ids && cpu_online(cpu)) {
            if (wait)
                smp_call_function_single(cpu, ack_kick, NULL, wait);
            else
                smp_send_reschedule(cpu);
        }
    }
out:
    put_cpu();
}
```

### 7.6 vCPU 暂停轮询 (halt_poll)

KVM 实现了 "暂停轮询" 优化,避免 vCPU 立即阻塞:

```c
void kvm_vcpu_halt(struct kvm_vcpu *vcpu)
{
    unsigned int max_halt_poll_ns = kvm_vcpu_max_halt_poll_ns(vcpu);
    bool halt_poll_allowed = !kvm_arch_no_poll(vcpu);
    ktime_t start, cur, poll_end;
    bool waited = false;
    bool do_halt_poll;

    // 计算轮询时间
    do_halt_poll = halt_poll_allowed && vcpu->halt_poll_ns;

    start = cur = poll_end = ktime_get();
    if (do_halt_poll) {
        ktime_t stop = ktime_add_ns(start, vcpu->halt_poll_ns);

        // 忙轮询而不是阻塞
        do {
            if (kvm_vcpu_check_block(vcpu) < 0)
                goto out;
            cpu_relax();
            poll_end = cur = ktime_get();
        } while (kvm_vcpu_can_poll(cur, stop));
    }

    // 轮询未成功,进入真正的阻塞
    waited = kvm_vcpu_block(vcpu);
    // ...
}
```

---

## 8. vCPU 运行循环

### 8.1 核心运行循环 vcpu_run()

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:11662-11710`

```c
static int vcpu_run(struct kvm_vcpu *vcpu)
{
    int r;

    vcpu->run->exit_reason = KVM_EXIT_UNKNOWN;

    for (;;) {
        // 在指令边界标记
        vcpu->arch.at_instruction_boundary = false;

        if (kvm_vcpu_running(vcpu)) {
            // 进入客户机
            r = vcpu_enter_guest(vcpu);
        } else {
            // 阻塞等待事件
            r = vcpu_block(vcpu);
        }

        if (r <= 0)
            break;

        // 清除解阻塞请求
        kvm_clear_request(KVM_REQ_UNBLOCK, vcpu);

        // 处理 Xen 事件
        if (kvm_xen_has_pending_events(vcpu))
            kvm_xen_inject_pending_events(vcpu);

        // 处理定时器中断
        if (kvm_cpu_has_pending_timer(vcpu))
            kvm_inject_pending_timer_irqs(vcpu);

        // 检查中断窗口
        if (dm_request_for_irq_injection(vcpu) &&
            kvm_vcpu_ready_for_interrupt_injection(vcpu)) {
            r = 0;
            vcpu->run->exit_reason = KVM_EXIT_IRQ_WINDOW_OPEN;
            ++vcpu->stat.request_irq_exits;
            break;
        }

        // 检查需要切换到 guest 模式的 work
        if (__xfer_to_guest_mode_work_pending()) {
            kvm_vcpu_srcu_read_unlock(vcpu);
            r = kvm_xfer_to_guest_mode_handle_work(vcpu);
            kvm_vcpu_srcu_read_lock(vcpu);
            if (r)
                return r;
        }
    }

    return r;
}
```

### 8.2 kvm_arch_vcpu_ioctl_run()

**位置:** `/Users/sphinx/github/linux/arch/x86/kvm/x86.c:11919-12037`

这是用户空间 ioctl(KVM_RUN) 的入口:

```c
int kvm_arch_vcpu_ioctl_run(struct kvm_vcpu *vcpu)
{
    struct kvm_queued_exception *ex = &vcpu->arch.exception;
    struct kvm_run *kvm_run = vcpu->run;
    u64 sync_valid_fields;
    int r;

    // 1. 确保 mmu post init 完成
    r = kvm_mmu_post_init_vm(vcpu->kvm);
    if (r)
        return r;

    // 2. 加载 vCPU
    vcpu_load(vcpu);

    // 3. 激活信号掩码
    kvm_sigset_activate(vcpu);
    kvm_run->flags = 0;

    // 4. 加载 guest FPU
    kvm_load_guest_fpu(vcpu);

    // 5. 获取 SRCU 读锁
    kvm_vcpu_srcu_read_lock(vcpu);

    // 6. 处理未初始化状态
    if (unlikely(vcpu->arch.mp_state == KVM_MP_STATE_UNINITIALIZED)) {
        if (!vcpu->wants_to_run) {
            r = -EINTR;
            goto out;
        }

        // 阻塞等待 INIT 完成
        kvm_vcpu_srcu_read_unlock(vcpu);
        kvm_vcpu_block(vcpu);
        kvm_vcpu_srcu_read_lock(vcpu);

        if (kvm_apic_accept_events(vcpu) < 0) {
            r = 0;
            goto out;
        }
        // ...
    }

    // 7. 同步寄存器
    if (kvm_run->kvm_dirty_regs) {
        r = sync_regs(vcpu);
        if (r != 0)
            goto out;
    }

    // 8. 运行 vCPU
    r = vcpu_run(vcpu);

out:
    // 9. 保存 guest FPU
    kvm_put_guest_fpu(vcpu);

    // 10. 保存寄存器到 run 结构
    if (kvm_run->kvm_valid_regs && likely(!vcpu->arch.guest_state_protected))
        store_regs(vcpu);

    post_kvm_run_save(vcpu);
    kvm_vcpu_srcu_read_unlock(vcpu);

    kvm_sigset_deactivate(vcpu);
    vcpu_put(vcpu);
    return r;
}
```

---

## 9. 退出类型 (kvm_run exit_reason)

| 退出类型 | 说明 | 处理方式 |
|----------|------|----------|
| KVM_EXIT_UNKNOWN | 未知原因 | 用户空间处理 |
| KVM_EXIT_EXCEPTION | 客户机异常 | 用户空间处理 |
| KVM_EXIT_HLT | 执行 HLT 指令 | 通常是客户机空闲 |
| KVM_EXIT_IO | I/O 操作 | 用户空间模拟 |
| KVM_EXIT_CPUID | 执行 CPUID | 用户空间或内核模拟 |
| KVM_EXIT_MSR | MSR 访问 | 用户空间或内核模拟 |
| KVM_EXIT_IRQ_WINDOW_OPEN | 中断窗口打开 | 用户空间注入中断 |
| KVM_EXIT_SHUTDOWN | 关机/三重故障 | 用户空间处理 |
| KVM_EXIT_FAIL_ENTRY | VM-Entry 失败 | 用户空间处理 |
| KVM_EXIT_X86_BUS_LOCK | 总线锁检测 | 用户空间处理 |
| KVM_EXIT_INTR | 被信号中断 | 用户空间处理 |

---

## 10. 总结

KVM vCPU 管理是 Linux 虚拟化的核心机制:

1. **创建/销毁**: 通过 slab 缓存分配 vCPU 结构,架构相关初始化包括 LAPIC、MMU、FPU 等组件

2. **寄存器状态**: 通过 `kvm_vcpu_arch` 结构维护客户机寄存器状态,通过 MSR 接口访问特权寄存器

3. **VM-Exit**: 硬件自动触发,通过退出原因码索引处理函数表,大部分退出由内核直接处理

4. **VM-Entry**: `vcpu_enter_guest()` 完成状态加载和事件注入后,调用 `vmx_vcpu_run()` 执行硬件 VM-Entry

5. **调度**: vCPU 作为宿主机线程参与调度,通过 `preempt_notifier` 与调度器交互,`kvm_vcpu_block/kick` 实现客户机级别的阻塞和唤醒

整体架构设计精巧,兼顾了性能(事件处理、轮询优化)和正确性(状态同步、嵌套虚拟化支持)。