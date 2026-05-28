# Linux Kernel KVM (Kernel Virtual Machine) 核心架构分析

## 1. 概述

KVM (Kernel-based Virtual Machine) 是 Linux 内核级的硬件虚拟化解决方案，将 Linux 内核转变为 Hypervisor。KVM 需要硬件虚拟化支持 (Intel VT-x 或 AMD-V)，通过 `/dev/kvm` 字符设备与用户空间交互。

### 1.1 源码位置

| 组件 | 路径 |
|------|------|
| 核心代码 | `/Users/sphinx/github/linux/virt/kvm/kvm_main.c` |
| 通用头文件 | `/Users/sphinx/github/linux/include/linux/kvm_host.h` |
| 架构相关头文件 | `/Users/sphinx/github/linux/arch/x86/include/asm/kvm_host.h` |
| 用户空间 API | `/Users/sphinx/github/linux/include/uapi/linux/kvm.h` |
| VMX 实现 | `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` |
| SVM 实现 | `/Users/sphinx/github/linux/arch/x86/kvm/svm/sev.c` |

### 1.2 KVM 核心数据结构关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         struct kvm (虚拟机实例)                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ 主要字段:                                                        │ │
│  │   - mm: 用户空间进程 mm_struct                                    │ │
│  │   - memslots[]: 内存槽数组 (KVM_MAX_NR_ADDRESS_SPACES)          │ │
│  │   - vcpu_array: vCPU xarray                                      │ │
│  │   - buses[]: IO 总线数组 (KVM_NR_BUSES)                          │ │
│  │   - arch: 架构特定数据 (kvm_arch)                                │ │
│  │   - lock: 虚拟机锁                                               │ │
│  │   - slots_lock: 内存槽锁                                         │ │
│  │   - srcu: SRCU 结构 (用于内存槽迭代)                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│          ┌───────────────────┼───────────────────┐                   │
│          │                   │                   │                   │
│          ▼                   ▼                   ▼                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│  │ struct kvm_vcpu│  │ struct kvm_vcpu│  │ struct kvm_vcpu│            │
│  │    (vcpu 0)    │  │    (vcpu 1)    │  │    (vcpu N)    │            │
│  │  ┌───────────┐ │  │  ┌───────────┐ │  │  ┌───────────┐ │            │
│  │  │ arch     │ │  │  │ arch     │ │  │  │ arch     │ │            │
│  │  │ run      │ │  │  │ run      │ │  │  │ run      │ │            │
│  │  │ requests │ │  │  │ requests │ │  │  │ requests │ │            │
│  │  │ mutex    │ │  │  │ mutex    │ │  │  │ mutex    │ │            │
│  │  └───────────┘ │  │  └───────────┘ │  │  └───────────┘ │            │
│  └───────────────┘  └───────────────┘  └───────────────┘            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                 struct kvm_memory_slot (内存槽)                   │ │
│  │   - base_gfn: 起始 Guest Frame Number                           │ │
│  │   - npages: 页数量                                              │ │
│  │   - dirty_bitmap: 脏页位图                                       │ │
│  │   - userspace_addr: 用户空间虚拟地址                             │ │
│  │   - flags: 槽标志 (KVM_MEM_READONLY, KVM_MEM_GUEST_MEMFD 等)   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心数据结构

### 2.1 struct kvm (虚拟机实例)

**定义位置**: `/Users/sphinx/github/linux/include/linux/kvm_host.h:769-878`

```c
struct kvm {
    // MMU 管理锁 (根据架构选择 spinlock 或 rwlock)
#ifdef KVM_HAVE_MMU_RWLOCK
    rwlock_t mmu_lock;
#else
    spinlock_t mmu_lock;
#endif

    struct mutex slots_lock;           // 内存槽操作锁
    struct mutex slots_arch_lock;      // 架构相关内存槽锁
    struct mm_struct *mm;              // 关联的用户空间进程

    // 内存槽管理
    unsigned long nr_memslot_pages;
    struct kvm_memslots __memslots[KVM_MAX_NR_ADDRESS_SPACES][2];  // 双缓冲槽集
    struct kvm_memslots __rcu *memslots[KVM_MAX_NR_ADDRESS_SPACES];  // 当前活动槽

    // vCPU 管理
    struct xarray vcpu_array;          // xarray 存储 vCPU 指针
    atomic_t online_vcpus;             // 在线 vCPU 数量
    int max_vcpus;                     // 最大 vCPU 数量
    int created_vcpus;                 // 已创建 vCPU 数量

    // 虚拟机链表 (全局 vm_list)
    struct list_head vm_list;
    struct mutex lock;                  // 虚拟机全局锁

    // IO 总线
    struct kvm_io_bus __rcu *buses[KVM_NR_BUSES];  // MMIO, PIO, VirtIO 等

    // 中断管理
#ifdef CONFIG_HAVE_KVM_IRQCHIP
    struct {
        spinlock_t lock;
        struct list_head items;
        struct list_head resampler_list;
        struct mutex resampler_lock;
    } irqfds;
#endif

    // 统计信息
    struct kvm_vm_stat stat;

    // 架构特定数据 (x86: VMX/SVM 状态, 页表等)
    struct kvm_arch arch;

    // 引用计数
    refcount_t users_count;

    // 脏页环
    u32 dirty_ring_size;
    bool dirty_ring_with_bitmap;

    // 调试相关
    struct dentry *debugfs_dentry;
    struct srcu_struct srcu;           // 用于安全迭代内存槽
    struct srcu_struct irq_srcu;
};
```

**关键特性**:
- 双缓冲内存槽设计: `__memslots[as_id][2]` 允许原子切换活跃/非活跃槽
- xarray 存储 vCPU: 支持高效索引和迭代
- SRCU (Sleepable RCU): 允许在内存槽迭代时睡眠

### 2.2 struct kvm_vcpu (虚拟 CPU)

**定义位置**: `/Users/sphinx/github/linux/include/linux/kvm_host.h:324-400`

```c
struct kvm_vcpu {
    struct kvm *kvm;                   // 所属虚拟机

    // 调度相关
    int cpu;                           // 当前运行的物理 CPU
    int vcpu_id;                       // 用户空间指定的 vCPU ID
    int vcpu_idx;                      // 在 vcpu_array 中的索引
    int mode;                          // vCPU 模式 (OUTSIDE_GUEST_MODE, IN_GUEST_MODE, etc.)
    u64 requests;                      // 待处理请求位图

    // 运行状态
    struct mutex mutex;                // vCPU 互斥锁
    struct kvm_run *run;               // 运行状态结构 (用户空间映射)

    // 信号处理
    struct pid *pid;                   // 关联的进程 PID
    rwlock_t pid_lock;
    int sigset_active;
    sigset_t sigset;

    // Halt polling (暂停轮询优化)
    unsigned int halt_poll_ns;
    bool valid_wakeup;

    // MMIO 处理
#ifdef CONFIG_HAS_IOMEM
    int mmio_needed;
    int mmio_read_completed;
    int mmio_is_write;
    int mmio_cur_fragment;
    int mmio_nr_fragments;
    struct kvm_mmio_fragment mmio_fragments[KVM_MAX_MMIO_FRAGMENTS];
#endif

    // 异步页错误 (用于 PV EPT)
#ifdef CONFIG_KVM_ASYNC_PF
    struct {
        u32 queued;
        struct list_head queue;
        struct list_head done;
        spinlock_t lock;
    } async_pf;
#endif

    // Spinloop 优化
#ifdef CONFIG_HAVE_KVM_CPU_RELAX_INTERCEPT
    struct {
        bool in_spin_loop;             // 是否在自旋循环中
        bool dy_eligible;              // 是否符合定向让出条件
    } spin_loop;
#endif

    bool wants_to_run;                 // 是否希望运行
    bool preempted;                    // 是否被抢占
    bool ready;                       // 是否就绪

    // 架构特定数据
    struct kvm_vcpu_arch arch;

    // 统计信息
    struct kvm_vcpu_stat stat;

    // 脏页环
    struct kvm_dirty_ring dirty_ring;

    // 最后使用的内存槽缓存
    struct kvm_memory_slot *last_used_slot;
    u64 last_used_slot_gen;
};
```

**vCPU 模式状态机**:
```c
enum {
    OUTSIDE_GUEST_MODE,      // vCPU 不在客户机模式
    IN_GUEST_MODE,           // vCPU 正在客户机模式运行
    EXITING_GUEST_MODE,      // vCPU 正在退出客户机模式
    READING_SHADOW_PAGE_TABLES, // vCPU 正在读取影子页表
};
```

### 2.3 struct kvm_run (vCPU 运行状态)

**定义位置**: `/Users/sphinx/github/linux/include/uapi/linux/kvm.h:223-490`

```c
struct kvm_run {
    /* in - 输入参数 */
    __u8 request_interrupt_window;    // 请求中断窗口
    __u8 immediate_exit;               // 立即退出标志

    /* out - 输出参数 */
    __u32 exit_reason;                // 退出原因 (关键字段!)
    __u8 ready_for_interrupt_injection;
    __u8 if_flag;                     // 中断标志
    __u16 flags;                       // 架构特定标志

    /* in (pre_kvm_run), out (post_kvm_run) */
    __u64 cr8;                        // CR8 寄存器 (TPR)
    __u64 apic_base;                  // APIC 基址

    /* union - 根据 exit_reason 不同而不同 */
    union {
        /* KVM_EXIT_UNKNOWN */
        struct {
            __u64 hardware_exit_reason;
        } hw;

        /* KVM_EXIT_IO - 端口 I/O */
        struct {
            __u8 direction;           // KVM_EXIT_IO_IN 或 KVM_EXIT_IO_OUT
            __u8 size;               // 字节数
            __u16 port;              // I/O 端口
            __u32 count;             // 重复次数
            __u64 data_offset;       // 数据在 kvm_run 中的偏移
        } io;

        /* KVM_EXIT_MMIO - 内存映射 I/O */
        struct {
            __u64 phys_addr;         // 物理地址
            __u8 data[8];            // 数据 (最多 8 字节)
            __u32 len;               // 长度
            __u8 is_write;           // 是否写操作
        } mmio;

        /* KVM_EXIT_HYPERCALL - 超级调用 */
        struct {
            __u64 nr;                // 调用号
            __u64 args[6];           // 参数
            __u64 ret;               // 返回值
        } hypercall;

        /* KVM_EXIT_DEBUG - 调试异常 */
        struct {
            struct kvm_debug_exit_arch arch;
        } debug;

        /* KVM_EXIT_HLT - CPU 停止 */
        /* ... 其他退出类型 ... */
    };
};
```

**主要退出原因 (exit_reason)**:
| 常量 | 值 | 说明 |
|------|-----|------|
| KVM_EXIT_UNKNOWN | 0 | 未知原因退出 |
| KVM_EXIT_EXCEPTION | 1 | 客户机异常 |
| KVM_EXIT_IO | 2 | 端口 I/O 操作 |
| KVM_EXIT_HYPERCALL | 3 | 超级调用 (如 KVM Hyper-V call) |
| KVM_EXIT_DEBUG | 4 | 调试事件 |
| KVM_EXIT_HLT | 5 | CPU halt (等待中断) |
| KVM_EXIT_MMIO | 6 | 内存映射 I/O |
| KVM_EXIT_IRQ_WINDOW_OPEN | 7 | IRQ 窗口打开 |
| KVM_EXIT_SHUTDOWN | 8 | 关机请求 |
| KVM_EXIT_FAIL_ENTRY | 9 | VM-Entry 失败 |
| KVM_EXIT_INTR | 10 | 外部中断 |
| KVM_EXIT_TPR_ACCESS | 12 | TPR 访问 |
| KVM_EXIT_INTERNAL_ERROR | 17 | 内部错误 |
| KVM_EXIT_MEMORY_FAULT | 39 | 内存错误 (TDX) |

### 2.4 struct kvm_memory_slot (内存槽)

**定义位置**: `/Users/sphinx/github/linux/include/linux/kvm_host.h:592-616`

```c
struct kvm_memory_slot {
    // 索引节点 (用于 id_hash 哈希表)
    struct hlist_node id_node[2];

    // HVA 区间树节点 (用于快速查找)
    struct interval_tree_node hva_node[2];

    // GFN 红黑树节点 (用于 GFN 映射)
    struct rb_node gfn_node[2];

    gfn_t base_gfn;                    // 起始 Guest Frame Number
    unsigned long npages;              // 页数量

    // 脏页追踪
    unsigned long *dirty_bitmap;       // 脏页位图

    // 架构特定数据
    struct kvm_arch_memory_slot arch;

    // 用户空间地址
    unsigned long userspace_addr;       // mmap 返回的地址

    // 槽标志
    u32 flags;

    // 槽 ID
    short id;
    u16 as_id;                        // 地址空间 ID

#ifdef CONFIG_KVM_GUEST_MEMFD
    // guest_memfd 支持
    struct {
        struct file *file;            // guest_memfd 文件
        pgoff_t pgoff;                // 页偏移
    } gmem;
#endif
};
```

**内存槽标志**:
```c
#define KVM_MEMSLOT_INVALID     (1UL << 16)  // 槽无效
#define KVM_MEMSLOT_GMEM_ONLY  (1UL << 17)  // 仅 guest_memfd
```

---

## 3. KVM 核心 API

### 3.1 kvm_init() - KVM 模块初始化

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:6487-6550+`

```c
int kvm_init(unsigned vcpu_size, unsigned vcpu_align, struct module *module)
{
    int r;
    int cpu;

    // 1. 创建 vCPU 内存缓存 (kmem_cache)
    //    用于高效分配/释放 vCPU 结构，支持对齐要求
    kvm_vcpu_cache = kmem_cache_create_usercopy("kvm_vcpu", vcpu_size, vcpu_align,
                        SLAB_ACCOUNT,
                        offsetof(struct kvm_vcpu, arch),
                        offsetofend(struct kvm_vcpu, stats_id)
                              - offsetof(struct kvm_vcpu, arch),
                        NULL);

    // 2. 为每个 CPU 分配 kick mask
    for_each_possible_cpu(cpu) {
        alloc_cpumask_var_node(&per_cpu(cpu_kick_mask, cpu), ...);
    }

    // 3. 初始化 irqfd (中断事件文件描述符)
    r = kvm_irqfd_init();

    // 4. 初始化异步页错误机制
    r = kvm_async_pf_init();

    // 5. 设置文件操作 owner
    kvm_chardev_ops.owner = module;
    kvm_vm_fops.owner = module;
    kvm_vcpu_fops.owner = module;
    kvm_device_fops.owner = module;

    // 6. 注册抢占回调 (用于 vCPU 调度)
    kvm_preempt_ops.sched_in = kvm_sched_in;
    kvm_preempt_ops.sched_out = kvm_sched_out;

    // 7. 初始化调试
    kvm_init_debug();

    // 8. 初始化 VFIO 支持
    r = kvm_vfio_ops_init();

    // 9. 初始化 guest_memfd
    r = kvm_gmem_init(module);

    // 10. 初始化虚拟化 (启用硬件虚拟化 VT-x/SVM)
    r = kvm_init_virtualization();

    // 11. 注册 /dev/kvm miscdevice
    r = misc_register(&kvm_dev);

    return r;
}
```

**初始化流程图**:
```
kvm_init()
    │
    ├── kmem_cache_create()        创建 vCPU 内存缓存
    │
    ├── alloc_cpumask_var_node()  分配 CPU kick masks
    │
    ├── kvm_irqfd_init()          初始化 irqfd 机制
    │
    ├── kvm_async_pf_init()       初始化异步页错误
    │
    ├── kvm_init_debug()          初始化调试支持
    │
    ├── kvm_vfio_ops_init()       初始化 VFIO 支持
    │
    ├── kvm_gmem_init()           初始化 guest_memfd
    │
    ├── kvm_init_virtualization() 启用 CPU 虚拟化 (VMX/SVM)
    │
    └── misc_register(&kvm_dev)  注册 /dev/kvm 设备
```

### 3.2 kvm_create_vm() - 创建虚拟机

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:1105-1238`

```c
static struct kvm *kvm_create_vm(unsigned long type, const char *fdname)
{
    struct kvm *kvm;
    struct kvm_memslots *slots;
    int r, i, j;

    // 1. 分配 kvm 结构 (架构相关)
    kvm = kvm_arch_alloc_vm();

    // 2. 初始化引用计数
    mmgrab(current->mm);
    kvm->mm = current->mm;

    // 3. 初始化各种锁
    KVM_MMU_LOCK_INIT(kvm);
    mutex_init(&kvm->lock);
    mutex_init(&kvm->irq_lock);
    mutex_init(&kvm->slots_lock);
    mutex_init(&kvm->slots_arch_lock);

    // 4. 初始化 SRCU 结构
    init_srcu_struct(&kvm->srcu);
    init_srcu_struct(&kvm->irq_srcu);

    // 5. 初始化中断路由
    r = kvm_init_irq_routing(kvm);

    // 6. 初始化内存槽 (双缓冲)
    for (i = 0; i < kvm_arch_nr_memslot_as_ids(kvm); i++) {
        for (j = 0; j < 2; j++) {
            slots = &kvm->__memslots[i][j];
            atomic_long_set(&slots->last_used_slot, 0);
            slots->hva_tree = RB_ROOT_CACHED;
            slots->gfn_tree = RB_ROOT;
            hash_init(slots->id_hash);
            slots->node_idx = j;
            slots->generation = i;
        }
        rcu_assign_pointer(kvm->memslots[i], &kvm->__memslots[i][0]);
    }

    // 7. 初始化 IO 总线
    for (i = 0; i < KVM_NR_BUSES; i++) {
        kvm->buses[i] = kzalloc_obj(struct kvm_io_bus, GFP_KERNEL_ACCOUNT);
    }

    // 8. 架构特定初始化 (VMX/SVM 特定设置)
    r = kvm_arch_init_vm(kvm, type);

    // 9. 启用虚拟化
    r = kvm_enable_virtualization();

    // 10. 初始化 MMU notifier (用于 KSM 等)
    r = kvm_init_mmu_notifier(kvm);

    // 11. 初始化合并 MMIO
    r = kvm_coalesced_mmio_init(kvm);

    // 12. 创建调试目录
    r = kvm_create_vm_debugfs(kvm, fdname);

    // 13. 加入全局虚拟机链表
    mutex_lock(&kvm_lock);
    list_add(&kvm->vm_list, &vm_list);
    mutex_unlock(&kvm_lock);

    return kvm;
}
```

### 3.3 kvm_vm_ioctl_create_vcpu() - 创建 vCPU

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:4158-4276`

```c
static int kvm_vm_ioctl_create_vcpu(struct kvm *kvm, unsigned long id)
{
    int r;
    struct kvm_vcpu *vcpu;
    struct page *page;

    // 1. 检查 ID 合法性
    if (id >= KVM_MAX_VCPU_IDS)
        return -EINVAL;

    // 2. 检查 vCPU 数量限制
    mutex_lock(&kvm->lock);
    if (kvm->created_vcpus >= kvm->max_vcpus) {
        mutex_unlock(&kvm->lock);
        return -EINVAL;
    }

    // 3. 架构预创建检查
    r = kvm_arch_vcpu_precreate(kvm, id);
    if (r) goto out;

    kvm->created_vcpus++;
    mutex_unlock(&kvm->lock);

    // 4. 分配 vCPU 结构 (从 kmem_cache)
    vcpu = kmem_cache_zalloc(kvm_vcpu_cache, GFP_KERNEL_ACCOUNT);

    // 5. 分配 kvm_run 页
    BUILD_BUG_ON(sizeof(struct kvm_run) > PAGE_SIZE);
    page = alloc_page(GFP_KERNEL_ACCOUNT | __GFP_ZERO);
    vcpu->run = page_address(page);

    // 6. 初始化 vCPU
    kvm_vcpu_init(vcpu, kvm, id);

    // 7. 架构特定创建 (VMX init, SVM init 等)
    r = kvm_arch_vcpu_create(vcpu);
    if (r) goto out_free_run_page;

    // 8. 分配脏页环
    if (kvm->dirty_ring_size) {
        r = kvm_dirty_ring_alloc(kvm, &vcpu->dirty_ring, id, kvm->dirty_ring_size);
        if (r) goto arch_vcpu_destroy;
    }

    // 9. 加入 xarray
    mutex_lock(&kvm->lock);
    r = xa_insert(&kvm->vcpu_array, vcpu->vcpu_idx, vcpu, GFP_KERNEL_ACCOUNT);

    // 10. 创建 vCPU 文件描述符
    fd = create_vcpu_fd(vcpu);

    // 11. 创建调试文件
    kvm_create_vcpu_debugfs(vcpu);

    return fd;

arch_vcpu_destroy:
    kvm_arch_vcpu_destroy(vcpu);
out_free_run_page:
    free_page((unsigned long)vcpu->run);
out:
    kmem_cache_free(kvm_vcpu_cache, vcpu);
    mutex_lock(&kvm->lock);
    kvm->created_vcpus--;
    mutex_unlock(&kvm->lock);
    return r;
}
```

### 3.4 kvm_vm_ioctl() - VM IOCTL 接口

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c`

```c
static long kvm_vm_ioctl(struct file *filp, unsigned int ioctl, unsigned long arg)
{
    struct kvm *kvm = filp->private_data;
    int r;

    if (kvm->mm != current->mm || kvm->vm_dead)
        return -EIO;

    switch (ioctl) {
    case KVM_CREATE_VCPU:
        r = kvm_vm_ioctl_create_vcpu(kvm, arg);
        break;

    case KVM_SET_USER_MEMORY_REGION:
        r = kvm_vm_ioctl_set_memory_region(kvm, arg);
        break;

    case KVM_GET_DIRTY_LOG:
        r = kvm_vm_ioctl_get_dirty_log(kvm, arg);
        break;

    case KVM_IRQFD:
        r = kvm_irqfd(kvm, arg);
        break;

    case KVM_CREATE_DEVICE:
        r = kvm_ioctl_create_device(kvm, arg);
        break;

    case KVM_ENABLE_CAP:
        r = kvm_vm_ioctl_enable_cap(kvm, arg);
        break;

    default:
        r = kvm_arch_vm_ioctl(filp, ioctl, arg);
    }
    return r;
}
```

### 3.5 kvm_vcpu_ioctl() - vCPU IOCTL 接口

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:4412-4510+`

```c
static long kvm_vcpu_ioctl(struct file *filp, unsigned int ioctl, unsigned long arg)
{
    struct kvm_vcpu *vcpu = filp->private_data;

    // 等待 vCPU 上线
    r = kvm_wait_for_vcpu_online(vcpu);

    // 先尝试架构特定处理 (不解锁)
    r = kvm_arch_vcpu_unlocked_ioctl(filp, ioctl, arg);
    if (r != -ENOIOCTLCMD)
        return r;

    mutex_lock_killable(&vcpu->mutex);

    switch (ioctl) {
    case KVM_RUN:
        // 核心运行逻辑
        r = -EINVAL;
        if (arg) goto out;

        // 检查 PID 变化
        oldpid = vcpu->pid;
        if (unlikely(oldpid != task_pid(current))) {
            r = kvm_arch_vcpu_run_pid_change(vcpu);
            if (r) break;
            // 更新 PID
        }

        vcpu->wants_to_run = !READ_ONCE(vcpu->run->immediate_exit__unsafe);
        r = kvm_arch_vcpu_ioctl_run(vcpu);  // <-- 核心调用
        vcpu->wants_to_run = false;
        break;

    case KVM_GET_REGS:
        r = kvm_arch_vcpu_ioctl_get_regs(vcpu, &regs);
        break;

    case KVM_SET_REGS:
        r = kvm_arch_vcpu_ioctl_set_regs(vcpu, &regs);
        break;

    case KVM_GET_SREGS:
        r = kvm_arch_vcpu_ioctl_get_sregs(vcpu, &sregs);
        break;

    case KVM_SET_SREGS:
        r = kvm_arch_vcpu_ioctl_set_sregs(vcpu, &sregs);
        break;

    case KVM_GET_MSRS:
        r = kvm_vcpu_ioctl_get_msrs(vcpu, argp);
        break;

    case KVM_SET_MSRS:
        r = kvm_vcpu_ioctl_set_msrs(vcpu, argp);
        break;

    case KVM_SET_CPUID:
        r = kvm_vcpu_ioctl_set_cpuid(vcpu, argp);
        break;

    case KVM_GET_LAPIC:
        r = kvm_vcpu_ioctl_get_lapic(vcpu, argp);
        break;

    case KVM_SET_LAPIC:
        r = kvm_vcpu_ioctl_set_lapic(vcpu, argp);
        break;

    case KVM_SET_SIGNAL_MASK:
        r = kvm_vcpu_ioctl_set_sigmask(vcpu, argp);
        break;

    default:
        r = -EINVAL;
    }
out:
    mutex_unlock(&vcpu->mutex);
    return r;
}
```

---

## 4. VMX/SVM 切换机制

### 4.1 VMX 架构概述

Intel VT-x 引入了 VMX (Virtual Machine Extensions)，包括:
- **VMX root operation**: Hypervisor 运行模式
- **VMX non-root operation**: Guest 运行模式
- **VM-Entry**: 从 root 切换到 non-root (运行 guest)
- **VM-Exit**: 从 non-root 切换到 root (返回 hypervisor)

### 4.2 VM-Entry 流程 (进入 Guest)

**关键函数**: `vmx_vcpu_enter_exit()` 和 `vmx_vcpu_run()`

**定义位置**: `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c:7566-7740+`

```c
// 路径: kvm_vcpu_ioctl(KVM_RUN)
//     -> kvm_arch_vcpu_ioctl_run()
//     -> vmx_vcpu_run()

fastpath_t vmx_vcpu_run(struct kvm_vcpu *vcpu, u64 run_flags)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);

    // 1. 刷新 L1D cache (缓解 L1TF)
    vmx_l1d_flush(vcpu);

    // 2. 保存 host 状态
    vmx_disable_fb_clear(vmx);

    // 3. 恢复 guest CR2
    if (vcpu->arch.cr2 != native_read_cr2())
        native_write_cr2(vcpu->arch.cr2);

    // 4. **VM-Entry**: 执行 guest 代码
    //    __vmx_vcpu_run() 是内联汇编，实际执行 VMLAUNCH 或 VMRESUME
    vmx->fail = __vmx_vcpu_run(vmx,
                                (unsigned long *)&vcpu->arch.regs,
                                flags);

    // 5. 保存 guest CR2
    vcpu->arch.cr2 = native_read_cr2();

    // 6. 恢复 host 状态
    vmx_enable_fb_clear(vmx);

    // 7. 读取 VM-Exit 信息
    vmx->vt.exit_reason.full = vmcs_read32(VM_EXIT_REASON);
    if (!vmx_get_exit_reason(vcpu).failed_vmentry)
        vmx->idt_vectoring_info = vmcs_read32(IDT_VECTORING_INFO_FIELD);

    // 8. 处理 NMI
    vmx_handle_nmi(vcpu);

    // 9. 性能追踪
    pt_guest_exit(vmx);

    // 10. 处理嵌套 VMX
    if (is_guest_mode(vcpu)) {
        if (vmx->nested.nested_run_pending && !vmx_get_exit_reason(vcpu).failed_vmentry)
            ++vcpu->stat.nested_run;
        vmx->nested.nested_run_pending = 0;
    }

    return fastpath;
}
```

### 4.3 VM-Exit 处理流程

**VM-Exit 发生在 guest 执行以下操作时**:
- I/O 端口访问
- 访问敏感 MSR
- 页面错误
- 中断/异常
- CPUID, HLT, PAUSE 等指令

**VM-Exit 原因读取**:
```c
// VM-Exit 原因寄存器
vmx->vt.exit_reason.full = vmcs_read32(VM_EXIT_REASON);

// 常见 VM-Exit 原因 (VMX)
#define EXIT_REASON_HLT                    12
#define EXIT_REASON_MSR_READ               31
#define EXIT_REASON_MSR_WRITE              32
#define EXIT_REASON_CPUID                  10
#define EXIT_REASON_INTR_WINDOW            7
#define EXIT_REASON_PENDING_INTR           7
#define EXIT_REASON_EPT_VIOLATION          48
#define EXIT_REASON_EPT_MISCONFIG          49
```

**VM-Exit 处理流程**:
```
VM-Exit 发生
    │
    ├── vmx_vcpu_enter_exit() 恢复 host 状态
    │
    ├── vmx_handle_exit()      处理退出原因
    │       │
    │       ├── handle_halt()        处理 HLT
    │       ├── handle_rdmsr()       处理 MSR 读
    │       ├── handle_wrmsr()       处理 MSR 写
    │       ├── handle_cpuid()       处理 CPUID
    │       ├── handle_ept_violation() 处理 EPT 违规
    │       └── ... 其他处理函数
    │
    ├── vcpu_enter_guest()     重新进入 guest
    │
    └── 重复运行循环
```

### 4.4 MSR 切换机制

**MSR (Model Specific Register)**: 特殊寄存器，需要在 VM-Entry/VM-Exit 时保存/恢复。

**Host/Guest MSR 切换**:

```c
// VM-Entry 前: 加载 guest MSR
static void vmx_load_guest_msrs(struct kvm_vcpu *vcpu)
{
    struct vcpu_vmx *vmx = to_vmx(vcpu);
    int i;

    for (i = 0; i < vmx->msr_count; i++) {
        wrmsrl(vmx->guest_msrs[i].index,
               vmx->guest_msrs[i].value);
    }
}

// VM-Exit 后: 保存 guest MSR, 恢复 host MSR
static void vmx_save_guest_msrs(struct kvm_vcpu *vcpu)
{
    // 保存 guest MSR 到 vmcs
}

static void vmx_load_host_msrs(struct kvm_vcpu *vcpu)
{
    // 从 vmcs 恢复 host MSR
}
```

**关键 MSR**:
| MSR | 用途 |
|-----|------|
| IA32_SPEC_CTRL | Speculative control |
| IA32_PRED_CMD | Prediction command |
| IA32_CORE_CAPABILITY | Core capability |
| IA32_FLUSH_CMD | L1D flush |

---

## 5. 用户空间交互

### 5.1 /dev/kvm 设备

**设备注册**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:5570-5574`

```c
static struct miscdevice kvm_dev = {
    KVM_MINOR,           // 次设备号
    "kvm",               // 设备名
    &kvm_chardev_ops,    // 文件操作
};

// 字符设备操作
static struct file_operations kvm_chardev_ops = {
    .unlocked_ioctl = kvm_dev_ioctl,
    .llseek         = noop_llseek,
#ifdef CONFIG_KVM_COMPAT
    .compat_ioctl   = kvm_dev_ioctl,
#endif
};
```

**/dev/kvm IOCTL 接口**:

| IOCTL | 说明 |
|-------|------|
| KVM_GET_API_VERSION | 获取 API 版本 (当前: 12) |
| KVM_CREATE_VM | 创建虚拟机, 返回 VM fd |
| KVM_CHECK_EXTENSION | 检查扩展支持 |
| KVM_GET_VCPU_MMAP_SIZE | 获取 mmap 大小 |

### 5.2 VM 文件描述符 IOCTL

**VM 文件操作**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:5473-5478`

```c
static struct file_operations kvm_vm_fops = {
    .release        = kvm_vm_release,
    .unlocked_ioctl = kvm_vm_ioctl,
    .llseek         = noop_llseek,
#ifdef CONFIG_KVM_COMPAT
    .compat_ioctl   = kvm_vm_compat_ioctl,
#endif
};
```

**主要 VM IOCTL**:

| IOCTL | 说明 |
|-------|------|
| KVM_CREATE_VCPU | 创建 vCPU |
| KVM_SET_USER_MEMORY_REGION | 设置内存槽 |
| KVM_GET_DIRTY_LOG | 获取脏页日志 |
| KVM_IRQFD | 注册中断事件fd |
| KVM_CREATE_DEVICE | 创建设备 (如 irqchip) |

### 5.3 vCPU 文件描述符 IOCTL

**vCPU 文件操作**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:4105-4111`

```c
static struct file_operations kvm_vcpu_fops = {
    .release        = kvm_vcpu_release,
    .unlocked_ioctl = kvm_vcpu_ioctl,
    .mmap           = kvm_vcpu_mmap,     // 关键: mmap kvm_run
    .llseek         = noop_llseek,
#ifdef CONFIG_KVM_COMPAT
    .compat_ioctl   = kvm_vcpu_compat_ioctl,
#endif
};
```

**主要 vCPU IOCTL**:

| IOCTL | 说明 |
|-------|------|
| KVM_RUN | 运行 guest (核心) |
| KVM_GET_REGS | 获取通用寄存器 |
| KVM_SET_REGS | 设置通用寄存器 |
| KVM_GET_SREGS | 获取特殊寄存器 |
| KVM_SET_SREGS | 设置特殊寄存器 |
| KVM_GET_MSRS | 获取 MSR 列表 |
| KVM_SET_MSRS | 设置 MSR 列表 |
| KVM_SET_CPUID | 设置 CPUID |
| KVM_SET_LAPIC | 设置本地 APIC |
| KVM_GET_LAPIC | 获取本地 APIC |

### 5.4 内存映射 (mmap)

**vCPU mmap**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c:4083-4095`

```c
static int kvm_vcpu_mmap(struct file *file, struct vm_area_struct *vma)
{
    struct kvm_vcpu *vcpu = file->private_data;
    unsigned long pages = vma_pages(vma);

    // 检查是否是脏页环映射
    if ((kvm_page_in_dirty_ring(vcpu->kvm, vma->vm_pgoff) ||
         kvm_page_in_dirty_ring(vcpu->kvm, vma->vm_pgoff + pages - 1)) &&
        ((vma->vm_flags & VM_EXEC) || !(vma->vm_flags & VM_SHARED)))
        return -EINVAL;

    vma->vm_ops = &kvm_vcpu_vm_ops;
    return 0;
}
```

**mmap 布局**:
```
vCPU fd mmap 区域:
    offset 0:           struct kvm_run (页对齐)
    offset PAGE_SIZE:   PIO 数据页 (x86)
    offset 2*PAGE_SIZE: 合并 MMIO 环页
```

### 5.5 KVM_RUN 执行流程

```
用户空间                    KVM 内核                      硬件
   │                           │                           │
   │  ioctl(KVM_RUN)           │                           │
   │─────────────────────────>│                           │
   │                           │                           │
   │                           │ kvm_arch_vcpu_ioctl_run() │
   │                           │      │                   │
   │                           │      ├── vcpu_enter_guest()
   │                           │      │      │           │
   │                           │      │      ├── 注入事件
   │                           │      │      ├── 检查请求
   │                           │      │      └── vmx_vcpu_run()
   │                           │      │               │   │
   │                           │      │               │ VM-Entry
   │                           │      │               │───────>>
   │                           │      │               │       |
   │                           │      │               │   Guest
   │                           │      │               │       |
   │                           │      │               │ VM-Exit
   │                           │      │               │<<──────
   │                           │      │               │       │
   │                           │      ├── 处理 VM-Exit │       │
   │                           │      │    (handle_exit)       │
   │                           │      │               │       │
   │  return (exit_reason)      │<───────────────────────────│
   │<─────────────────────────│                           │
   │                           │                           │
   │  switch(exit_reason) {     │                           │
   │    case KVM_EXIT_IO:      │                           │
   │      处理 I/O...          │                           │
   │    case KVM_EXIT_MMIO:    │                           │
   │      处理 MMIO...         │                           │
   │    case KVM_EXIT_HLT:     │                           │
   │      休眠等待中断...      │                           │
   │  }                        │                           │
```

---

## 6. 数据结构关系总结

### 6.1 KVM 完整层次结构

```
用户空间进程 (QEMU, libvirt)
    │
    ├── /dev/kvm (misccharacter device)
    │       │
    │       └── KVM_CREATE_VM ioctl
    │               │
    │               ▼
    │       ┌───────────────────┐
    │       │   struct kvm      │
    │       │   (VM 实例)        │
    │       │                   │
    │       ├── memslots[]     │ ◄── 内存槽 (guest 物理内存映射)
    │       ├── vcpu_array      │ ◄── vCPU 数组
    │       ├── buses[]        │ ◄── IO 总线 (MMIO, PIO)
    │       ├── arch           │ ◄── 架构数据 (VMX/SVM 状态)
    │       └── irq_routing     │ ◄── 中断路由
    │               │
    │               ├── KVM_CREATE_VCPU ioctl
    │               │       │
    │               │       ▼
    │               │  ┌───────────────────┐
    │               │  │   struct kvm_vcpu  │
    │               │  │   (虚拟 CPU)        │
    │               │  │                   │
    │               │  ├── run             │ ◄── struct kvm_run (mmap)
    │               │  ├── arch            │ ◄── vCPU 架构状态
    │               │  ├── requests       │ ◄── 待处理请求
    │               │  └── dirty_ring      │ ◄── 脏页环
    │               │
    │               └── KVM_SET_USER_MEMORY_REGION
    │                       │
    │                       ▼
    │               ┌───────────────────┐
    │               │ struct kvm_memory_slot │
    │               │ (内存槽)            │
    │               │                   │
    │               ├── base_gfn        │ ◄── Guest PFN 起始
    │               ├── npages          │ ◄── 页数量
    │               ├── userspace_addr  │ ◄── Host HVA
    │               └── dirty_bitmap    │ ◄── 脏页追踪
    │
    └── mmap(vcpu_fd, 0, sizeof(kvm_run))
            │
            ▼
        struct kvm_run * (用户/内核共享内存)
```

### 6.2 关键锁依赖

```
kvm_lock (全局虚拟机链表锁)
    │
    └── vm_list

per-vcpu:
    vcpu->mutex
    │
    └── vcpu->pid_lock

per-vm:
    kvm->lock (VM 全局锁)
    │
    ├── kvm->slots_lock (内存槽操作)
    │       └── kvm->slots_arch_lock
    │
    └── kvm->irq_lock (中断操作)
            └── kvm->irq_routing
```

### 6.3 重要全局变量

**定义位置**: `/Users/sphinx/github/linux/virt/kvm/kvm_main.c`

```c
DEFINE_MUTEX(kvm_lock);           // 保护 vm_list
LIST_HEAD(vm_list);              // 所有 KVM 虚拟机链表

static struct kmem_cache *kvm_vcpu_cache;  // vCPU 内存缓存

static __read_mostly struct preempt_ops kvm_preempt_ops;
static DEFINE_PER_CPU(struct kvm_vcpu *, kvm_running_vcpu);

unsigned int halt_poll_ns = KVM_HALT_POLL_NS_DEFAULT;
unsigned int halt_poll_ns_grow = 2;
unsigned int halt_poll_ns_grow_start = 10000;
unsigned int halt_poll_ns_shrink = 2;
```

---

## 7. 总结

### 7.1 KVM 架构特点

1. **模块化设计**: 核心与架构实现分离 (`kvm_main.c` vs `arch/x86/kvm/`)
2. **高效内存管理**: 双缓冲内存槽 + SRCU 迭代
3. **高性能**: vCPU 零拷贝 mmap, 脏页环, halt-polling 优化
4. **安全隔离**: 完整的 VM-Exit/VM-Entry 机制
5. **可扩展**: 支持 VFIO 设备分配, 嵌套虚拟化, TDX/SEV

### 7.2 关键路径

1. **创建 VM**: `/dev/kvm` ioctl -> `kvm_create_vm()` -> `kvm_arch_init_vm()`
2. **创建 vCPU**: VM ioctl -> `kvm_vm_ioctl_create_vcpu()` -> `kvm_arch_vcpu_create()`
3. **运行 vCPU**: vCPU ioctl(KVM_RUN) -> `kvm_arch_vcpu_ioctl_run()` -> `vmx_vcpu_run()` -> VM-Entry
4. **VM-Exit 处理**: `handle_exit()` -> 具体处理函数 -> `vcpu_enter_guest()`

### 7.3 扩展阅读

- `/Users/sphinx/github/linux/Documentation/virt/kvm/` - KVM 文档
- `/Users/sphinx/github/linux/Documentation/virt/kvm/api.rst` - KVM API 详细文档
- `/Users/sphinx/github/linux/arch/x86/kvm/vmx/vmx.c` - VMX 实现
- `/Users/sphinx/github/linux/arch/x86/kvm/svm/sev.c` - SEV 实现
