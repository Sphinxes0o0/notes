# Linux Kernel KVM 中断与设备模拟机制分析

## 目录

1. [IRQ Chip 模拟](#1-irq-chip-模拟)
2. [Local APIC (LAPIC)](#2-local-apic-lapic)
3. [IOAPIC](#3-ioapic)
4. [Eventfd 集成](#4-eventfd-集成)
5. [VFIO 集成](#5-vfio-集成)
6. [中断流程图](#6-中断流程图)

---

## 1. IRQ Chip 模拟

### 1.1 核心数据结构

#### `struct kvm_kernel_irq_routing_entry` (include/linux/kvm_host.h:666)

```c
struct kvm_kernel_irq_routing_entry {
    u32 gsi;                    // Global System Interrupt number
    u32 type;                   // 路由类型
    int (*set)(...);            // IRQ 设置回调函数
    union {
        struct {
            unsigned irqchip;   // IRQ 控制器编号
            unsigned pin;       // 引脚编号
        } irqchip;
        struct {
            u32 address_lo;
            u32 address_hi;
            u32 data;
            u32 flags;
            u32 devid;
        } msi;                  // MSI 消息
        struct kvm_hv_sint hv_sint;
        struct kvm_xen_evtchn xen_evtchn;
    };
    struct hlist_node link;
};
```

#### `struct kvm_irq_routing_table` (include/linux/kvm_host.h:692)

```c
struct kvm_irq_routing_table {
    int chip[KVM_NR_IRQCHIPS][KVM_IRQCHIP_NUM_PINS];  // chip[irqchip][pin] -> GSI 映射
    u32 nr_rt_entries;                                 // 路由条目数量
    struct hlist_head map[] __counted_by(nr_rt_entries); // GSI -> 路由条目列表
};
```

### 1.2 `kvm_set_irq()` - IRQ 设置函数

**位置**: virt/kvm/irqchip.c:70-97

```c
/*
 * 返回值:
 *  < 0   中断被忽略 (被屏蔽或其他原因未投递)
 *  = 0   中断被合并 (上一个 IRQ 仍挂起)
 *  > 0   中断投递到的 CPU 数量
 */
int kvm_set_irq(struct kvm *kvm, int irq_source_id, u32 irq, int level,
                bool line_status)
{
    struct kvm_kernel_irq_routing_entry irq_set[KVM_NR_IRQCHIPS];
    int ret = -1, i, idx;

    trace_kvm_set_irq(irq, level, irq_source_id);

    // 同时设置 PIC 和 IOAPIC, 客户机将忽略未使用的那个
    idx = srcu_read_lock(&kvm->irq_srcu);
    i = kvm_irq_map_gsi(kvm, irq_set, irq);  // 查找 GSI 对应的路由条目
    srcu_read_unlock(&kvm->irq_srcu, idx);

    while (i--) {
        int r;
        // 调用具体的 set 回调 (kvm_pic_set_irq 或 kvm_ioapic_set_irq)
        r = irq_set[i].set(&irq_set[i], kvm, irq_source_id, level, line_status);
        if (r < 0)
            continue;
        ret = r + ((ret < 0) ? 0 : ret);
    }
    return ret;
}
```

### 1.3 `kvm_irq_map_gsi()` - GSI 映射查找

**位置**: virt/kvm/irqchip.c:21-38

```c
int kvm_irq_map_gsi(struct kvm *kvm,
                    struct kvm_kernel_irq_routing_entry *entries, int gsi)
{
    struct kvm_irq_routing_table *irq_rt;
    struct kvm_kernel_irq_routing_entry *e;
    int n = 0;

    irq_rt = srcu_dereference_check(kvm->irq_routing, &kvm->irq_srcu,
                                    lockdep_is_held(&kvm->irq_lock));
    if (irq_rt && gsi < irq_rt->nr_rt_entries) {
        hlist_for_each_entry(e, &irq_rt->map[gsi], link) {
            entries[n] = *e;
            ++n;
        }
    }
    return n;
}
```

### 1.4 `kvm_set_msi()` - MSI 中断设置

**位置**: arch/x86/kvm/irq.c:225-239

```c
int kvm_set_msi(struct kvm_kernel_irq_routing_entry *e,
                struct kvm *kvm, int irq_source_id, int level, bool line_status)
{
    struct kvm_lapic_irq irq;

    if (kvm_msi_route_invalid(kvm, e))
        return -EINVAL;

    if (!level)
        return -1;

    kvm_msi_to_lapic_irq(kvm, e, &irq);  // 将 MSI 消息转换为 LAPIC IRQ

    return kvm_irq_delivery_to_apic(kvm, NULL, &irq);
}
```

---

## 2. Local APIC (LAPIC)

### 2.1 `struct kvm_lapic` 结构

**位置**: arch/x86/kvm/lapic.h:62-89

```c
struct kvm_lapic {
    unsigned long base_address;       // LAPIC 基地址
    struct kvm_io_device dev;          // I/O 设备接口
    struct kvm_timer lapic_timer;     // LAPIC 定时器
    u32 divide_count;                 // 时钟分频系数
    struct kvm_vcpu *vcpu;             // 关联的 vCPU
    bool apicv_active;                // APICv 激活状态
    bool sw_enabled;                  // 软件使能
    bool irr_pending;                 // IRR 挂起标志
    bool lvt0_in_nmi_mode;
    bool guest_apic_protected;
    s16 isr_count;                    // ISR 中置位的位数
    int highest_isr_cache;             // ISR 最高向量缓存
    void *regs;                        // APIC 寄存器页 (MMIO 访问)
    gpa_t vapic_addr;
    struct gfn_to_hva_cache vapic_cache;
    unsigned long pending_events;
    unsigned int sipi_vector;
    int nr_lvt_entries;
};
```

### 2.2 `lapic_set_affinity()` - 设置亲和性

LAPIC 亲和性设置通过修改 LDR (Logical Destination Register) 和 DFR (Destination Format Register) 实现。

**关键路径** (arch/x86/kvm/lapic.c:327-391):

```c
static void kvm_recalculate_logical_map(struct kvm_apic_map *new,
                                        struct kvm_vcpu *vcpu)
{
    struct kvm_lapic *apic = vcpu->arch.apic;
    enum kvm_apic_logical_mode logical_mode;
    struct kvm_lapic **cluster;
    u16 mask;
    u32 ldr;

    if (new->logical_mode == KVM_APIC_MODE_MAP_DISABLED)
        return;

    if (!kvm_apic_sw_enabled(apic))
        return;

    ldr = kvm_lapic_get_reg(apic, APIC_LDR);
    if (!ldr)
        return;

    // 根据模式设置 logical_mode
    if (apic_x2apic_mode(apic)) {
        logical_mode = KVM_APIC_MODE_X2APIC;
    } else {
        ldr = GET_APIC_LOGICAL_ID(ldr);
        if (kvm_lapic_get_reg(apic, APIC_DFR) == APIC_DFR_FLAT)
            logical_mode = KVM_APIC_MODE_XAPIC_FLAT;
        else
            logical_mode = KVM_APIC_MODE_XAPIC_CLUSTER;
    }
    // ...
}
```

### 2.3 `kvm_apic_send_ipi()` - 发送 IPI

**位置**: arch/x86/kvm/lapic.c:1645-1651

```c
void kvm_apic_send_ipi(struct kvm_lapic *apic, u32 icr_low, u32 icr_high)
{
    struct kvm_lapic_irq irq;

    kvm_icr_to_lapic_irq(apic, icr_low, icr_high, &irq);

    trace_kvm_apic_ipi(icr_low, irq.dest_id);

    kvm_irq_delivery_to_apic(apic->vcpu->kvm, apic, &irq);
}
```

### 2.4 定时器中断

**定时器注入** (arch/x86/kvm/lapic.c:3144-3152):

```c
void kvm_inject_apic_timer_irqs(struct kvm_vcpu *vcpu)
{
    struct kvm_lapic *apic = vcpu->arch.apic;

    if (atomic_read(&apic->lapic_timer.pending) > 0) {
        kvm_apic_inject_pending_timer_irqs(apic);
        atomic_set(&apic->lapic_timer.pending, 0);
    }
}
```

**定时器启动** (arch/x86/kvm/lapic.c:2291-2306):

```c
static void start_sw_timer(struct kvm_lapic *apic)
{
    struct kvm_timer *ktimer = &apic->lapic_timer;

    WARN_ON(preemptible());
    if (apic->lapic_timer.hv_timer_in_use)
        cancel_hv_timer(apic);
    if (!apic_lvtt_period(apic) && atomic_read(&ktimer->pending))
        return;

    if (apic_lvtt_period(apic) || apic_lvtt_oneshot(apic))
        start_sw_period(apic);
    else if (apic_lvtt_tscdeadline(apic))
        start_sw_tscdeadline(apic);
    trace_kvm_hv_timer_state(apic->vcpu->vcpu_id, false);
}
```

### 2.5 `kvm_irq_delivery_to_apic()` - IRQ 投递到 LAPIC

**位置**: arch/x86/kvm/lapic.h:125-129 和 lapic.c:1334-1391

```c
// lapic.h 中的内联包装
static inline int kvm_irq_delivery_to_apic(struct kvm *kvm,
                                           struct kvm_lapic *src,
                                           struct kvm_lapic_irq *irq)
{
    return __kvm_irq_delivery_to_apic(kvm, src, irq, NULL);
}

// lapic.c 中的实际实现
int __kvm_irq_delivery_to_apic(struct kvm *kvm, struct kvm_lapic *src,
                               struct kvm_lapic_irq *irq,
                               struct rtc_status *rtc_status)
{
    int r = -1;
    struct kvm_vcpu *vcpu, *lowest = NULL;
    unsigned long i, dest_vcpu_bitmap[BITS_TO_LONGS(KVM_MAX_VCPUS)];
    unsigned int dest_vcpus = 0;

    // 首先尝试快速投递路径
    if (__kvm_irq_delivery_to_apic_fast(kvm, src, irq, &r, rtc_status))
        return r;

    // 遍历所有 vCPU, 查找匹配的目标
    kvm_for_each_vcpu(i, vcpu, kvm) {
        if (!kvm_apic_present(vcpu))
            continue;

        if (!kvm_apic_match_dest(vcpu, src, irq->shorthand,
                                 irq->dest_id, irq->dest_mode))
            continue;

        if (!kvm_lowest_prio_delivery(irq)) {
            // 固定优先级投递
            if (r < 0)
                r = 0;
            r += kvm_apic_set_irq(vcpu, irq, rtc_status);
        } else if (kvm_apic_sw_enabled(vcpu->arch.apic)) {
            // 最低优先级投递 - 找优先级最高的 CPU
            if (!lowest)
                lowest = vcpu;
            else if (kvm_apic_compare_prio(vcpu, lowest) < 0)
                lowest = vcpu;
            // ...
        }
    }
    // ...
}
```

---

## 3. IOAPIC

### 3.1 `struct kvm_ioapic` 结构

**位置**: arch/x86/kvm/ioapic.h:71-89

```c
struct kvm_ioapic {
    u64 base_address;                      // IOAPIC 基地址 (默认 0xFEC00000)
    u32 ioregsel;                          // I/O 寄存器选择器
    u32 id;                                // IOAPIC ID
    u32 irr;                               // 中断请求寄存器 (Interrupt Request Register)
    u32 pad;
    union kvm_ioapic_redirect_entry redirtbl[IOAPIC_NUM_PINS];  // 重定向表
    unsigned long irq_states[IOAPIC_NUM_PINS];                   // 每个引脚的状态
    struct kvm_io_device dev;              // I/O 设备接口
    struct kvm *kvm;
    spinlock_t lock;
    struct rtc_status rtc_status;
    struct delayed_work eoi_inject;         // EOI 延迟注入工作队列
    u32 irq_eoi[IOAPIC_NUM_PINS];          // EOI 计数
    u32 irr_delivered;                     // 已投递的 IRR

    /* reads protected by irq_srcu, writes by irq_lock */
    struct hlist_head mask_notifier_list;
};
```

### 3.2 `ioapic_set_irq()` - IOAPIC 中断设置

**位置**: arch/x86/kvm/ioapic.c:187-245

```c
static int ioapic_set_irq(struct kvm_ioapic *ioapic, unsigned int irq,
                           int irq_level, bool line_status)
{
    union kvm_ioapic_redirect_entry entry;
    u32 mask = 1 << irq;
    u32 old_irr;
    int edge, ret;

    entry = ioapic->redirtbl[irq];
    edge = (entry.fields.trig_mode == IOAPIC_EDGE_TRIG);  // 判断边沿/电平触发

    if (!irq_level) {
        ioapic->irr &= ~mask;  // 清除 IRR
        ret = 1;
        goto out;
    }

    // 边沿触发且 AVIC 激活时的特殊处理
    if (edge && kvm_apicv_activated(ioapic->kvm))
        ioapic_lazy_update_eoi(ioapic, irq);

    // RTC 特殊处理 - 跟踪 EOI
    if (irq == RTC_GSI && line_status && rtc_irq_check_coalesced(ioapic)) {
        ret = 0;  // 被合并
        goto out;
    }

    old_irr = ioapic->irr;
    ioapic->irr |= mask;  // 设置 IRR
    if (edge) {
        ioapic->irr_delivered &= ~mask;
        if (old_irr == ioapic->irr) {
            ret = 0;  // 中断被合并
            goto out;
        }
    }

    ret = ioapic_service(ioapic, irq, line_status);  // 实际投递中断

out:
    trace_kvm_ioapic_set_irq(entry.bits, irq, ret == 0);
    return ret;
}
```

### 3.3 边沿触发 vs 电平触发

**边沿触发 (Edge-triggered)**:
- 当检测到电压/电平变化时触发中断
- `irr_delivered` 标志用于追踪已投递的边沿中断
- 相同向量不会重复投递

**电平触发 (Level-triggered)**:
- 只要电平保持高/低就一直触发
- `remote_irr` 字段追踪远程 CPU 是否在等待 EOI
- EOI 后若电平仍 assert, 需要重新注入

### 3.4 `ioapic_service()` - 中断服务

**位置**: arch/x86/kvm/ioapic.c:457-498

```c
static int ioapic_service(struct kvm_ioapic *ioapic, int irq, bool line_status)
{
    union kvm_ioapic_redirect_entry *entry = &ioapic->redirtbl[irq];
    struct kvm_lapic_irq irqe;
    int ret;

    // 检查是否被屏蔽或远程 IRR 置位
    if (entry->fields.mask ||
        (entry->fields.trig_mode == IOAPIC_LEVEL_TRIG &&
         entry->fields.remote_irr))
        return -1;

    // 构造 LAPIC IRQ
    irqe.dest_id = entry->fields.dest_id;
    irqe.vector = entry->fields.vector;
    irqe.dest_mode = kvm_lapic_irq_dest_mode(!!entry->fields.dest_mode);
    irqe.trig_mode = entry->fields.trig_mode;
    irqe.delivery_mode = entry->fields.delivery_mode << 8;
    irqe.level = 1;
    irqe.shorthand = APIC_DEST_NOSHORT;
    irqe.msi_redir_hint = false;

    // 边沿触发的特殊处理
    if (irqe.trig_mode == IOAPIC_EDGE_TRIG)
        ioapic->irr_delivered |= 1 << irq;

    // 投递到 LAPIC
    if (irq == RTC_GSI && line_status)
        ret = __kvm_irq_delivery_to_apic(ioapic->kvm, NULL, &irqe,
                                         &ioapic->rtc_status);
    else
        ret = kvm_irq_delivery_to_apic(ioapic->kvm, NULL, &irqe);

    // 电平触发中断设置 remote_irr
    if (ret && irqe.trig_mode == IOAPIC_LEVEL_TRIG)
        entry->fields.remote_irr = 1;

    return ret;
}
```

---

## 4. Eventfd 集成

### 4.1 `struct kvm_kernel_irqfd` 结构

**位置**: include/linux/kvm_host.h (前向声明在 2402, 实现分布在 eventfd.c)

```c
struct kvm_kernel_irqfd {
    struct list_head list;              // 链接到 kvm->irqfds.items
    struct eventfd_ctx *eventfd;        // 关联的 eventfd
    struct eventfd_ctx *resamplefd;      // resample 模式的 resamplefd
    struct work_struct inject;           // 注入工作队列
    struct work_struct shutdown;         // 关闭工作队列
    wait_queue_entry_t wait;             // 等待队列条目
    struct kvm *kvm;
    u32 gsi;                             // 全局系统中断号
    struct seqcount_spinlock irq_entry_sc;  // 路由条目的序列计数器
    struct kvm_kernel_irq_routing_entry irq_entry;  // 当前路由条目
    struct kvm_kernel_irqfd_resampler *resampler;  // resampler 引用
    struct irq_bypass_consumer consumer;  // IRQ bypass 消费者
    struct irq_bypass_producer *producer; // IRQ bypass 生产者
    struct kvm_vcpu *irq_bypass_vcpu;    // bypass 目标 vCPU
};
```

### 4.2 `kvm_irqfd()` - IRQFD 机制

**位置**: virt/kvm/eventfd.c:369-520

```c
static int kvm_irqfd_assign(struct kvm *kvm, struct kvm_irqfd *args)
{
    struct kvm_kernel_irqfd *irqfd;
    struct eventfd_ctx *eventfd = NULL, *resamplefd = NULL;
    // ...

    irqfd = kzalloc_obj(*irqfd, GFP_KERNEL_ACCOUNT);
    // ...

    // 获取 eventfd 上下文
    eventfd = eventfd_ctx_fileget(fd_file(f));
    irqfd->eventfd = eventfd;

    // 处理 RESAMPLE 模式
    if (args->flags & KVM_IRQFD_FLAG_RESAMPLE) {
        resamplefd = eventfd_ctx_fdget(args->resamplefd);
        irqfd->resamplefd = resamplefd;
        // 创建或加入现有的 resampler
        // ...
    }

    // 注册到 eventfd 的等待队列
    idx = srcu_read_lock(&kvm->irq_srcu);
    irqfd_pt.irqfd = irqfd;
    irqfd_pt.kvm = kvm;
    init_poll_funcptr(&irqfd_pt.pt, kvm_irqfd_register);
    events = vfs_poll(fd_file(f), &irqfd_pt.pt);

    if (events & EPOLLIN)  // eventfd 已有信号, 立即注入
        schedule_work(&irqfd->inject);

    // 注册 IRQ bypass 消费者
    if (kvm_arch_has_irq_bypass()) {
        irqfd->consumer.add_producer = kvm_arch_irq_bypass_add_producer;
        irqfd->consumer.del_producer = kvm_arch_irq_bypass_del_producer;
        irq_bypass_register_consumer(&irqfd->consumer, irqfd->eventfd);
    }
    // ...
}
```

### 4.3 `irqfd_wakeup()` - 事件唤醒处理

**位置**: virt/kvm/eventfd.c:201-270

```c
static int irqfd_wakeup(wait_queue_entry_t *wait, unsigned mode, int sync, void *key)
{
    struct kvm_kernel_irqfd *irqfd = container_of(wait, struct kvm_kernel_irqfd, wait);
    __poll_t flags = key_to_poll(key);
    struct kvm_kernel_irq_routing_entry irq;
    // ...

    if (flags & EPOLLIN) {
        eventfd_ctx_do_read(irqfd->eventfd, &cnt);  // 消费 eventfd 信号

        idx = srcu_read_lock(&kvm->irq_srcu);
        do {
            seq = read_seqcount_begin(&irqfd->irq_entry_sc);
            irq = irqfd->irq_entry;
        } while (read_seqcount_retry(&irqfd->irq_entry_sc, seq));

        // 注入中断
        if (unlikely(!irqfd_is_active(irqfd)) ||
            kvm_arch_set_irq_inatomic(&irq, kvm,
                                      KVM_USERSPACE_IRQ_SOURCE_ID, 1,
                                      false) == -EWOULDBLOCK)
            schedule_work(&irqfd->inject);
        srcu_read_unlock(&kvm->irq_srcu, idx);
        ret = 1;
    }

    if (flags & EPOLLHUP) {
        // eventfd 关闭, 从 KVM 分离
        spin_lock_irqsave(&kvm->irqfds.lock, iflags);
        if (irqfd_is_active(irqfd))
            irqfd_deactivate(irqfd);
        spin_unlock_irqrestore(&kvm->irqfds.lock, iflags);
    }
    return ret;
}
```

### 4.4 Resampler 机制

**位置**: virt/kvm/eventfd.c:58-116

Resampler 用于电平触发中断的重新采样, 当 Guest 发送 EOI 时重新触发中断。

```c
// EOI 确认回调
static void irqfd_resampler_ack(struct kvm_irq_ack_notifier *kian)
{
    struct kvm_kernel_irqfd_resampler *resampler;
    struct kvm *kvm;
    int idx;

    resampler = container_of(kian, struct kvm_kernel_irqfd_resampler, notifier);
    kvm = resampler->kvm;

    // 解除中断断言
    kvm_set_irq(kvm, KVM_IRQFD_RESAMPLE_IRQ_SOURCE_ID,
                resampler->notifier.gsi, 0, false);

    idx = srcu_read_lock(&kvm->irq_srcu);
    // 通知所有 resampler 上的 irqfd 重新采样
    irqfd_resampler_notify(resampler);
    srcu_read_unlock(&kvm->irq_srcu, idx);
}
```

---

## 5. VFIO 集成

### 5.1 `struct kvm_vfio` 结构

**位置**: virt/kvm/vfio.c:24-36

```c
struct kvm_vfio_file {
    struct list_head node;
    struct file *file;
#ifdef CONFIG_SPAPR_TCE_IOMMU
    struct iommu_group *iommu_group;
#endif
};

struct kvm_vfio {
    struct list_head file_list;    // VFIO 文件列表
    struct mutex lock;
    bool noncoherent;               // 非一致性 DMA 标志
};
```

### 5.2 `kvm_vfio_ops` - VFIO 操作接口

**位置**: virt/kvm/vfio.c:347-353

```c
static const struct kvm_device_ops kvm_vfio_ops = {
    .name = "kvm-vfio",
    .create = kvm_vfio_create,
    .release = kvm_vfio_release,
    .set_attr = kvm_vfio_set_attr,
    .has_attr = kvm_vfio_has_attr,
};
```

### 5.3 `kvm_vfio_file_add()` - 添加设备组

**位置**: virt/kvm/vfio.c:143-186

```c
static int kvm_vfio_file_add(struct kvm_device *dev, unsigned int fd)
{
    struct kvm_vfio *kv = dev->private;
    struct kvm_vfio_file *kvf;
    struct file *filp;
    int ret = 0;

    filp = fget(fd);
    if (!filp)
        return -EBADF;

    // 验证是 VFIO FD
    if (!kvm_vfio_file_is_valid(filp)) {
        ret = -EINVAL;
        goto out_fput;
    }

    mutex_lock(&kv->lock);

    // 检查是否已存在
    list_for_each_entry(kvf, &kv->file_list, node) {
        if (kvf->file == filp) {
            ret = -EEXIST;
            goto out_unlock;
        }
    }

    kvf = kzalloc_obj(*kvf, GFP_KERNEL_ACCOUNT);
    kvf->file = get_file(filp);
    list_add_tail(&kvf->node, &kv->file_list);

    // 设置 KVM 关联
    kvm_vfio_file_set_kvm(kvf->file, dev->kvm);
    kvm_vfio_update_coherency(dev);

out_unlock:
    mutex_unlock(&kv->lock);
out_fput:
    fput(filp);
    return ret;
}
```

### 5.4 Passthrough 设备访问

VFIO 集成允许将物理设备直接传递给 Guest, 主要功能包括:

1. **设备组管理**: 通过 `iommu_group` 跟踪共享 IOMMU 域的设备
2. **DMA 一致性处理**: `kvm_vfio_update_coherency()` 检查所有设备的一致性
3. **用户空间中断**: 通过 eventfd 机制将设备中断注入 Guest

---

## 6. 中断流程图

### 6.1 外部中断注入流程

```
物理设备 IRQ
    │
    ▼
irqfd_wakeup() / kvm_set_irq()
    │
    ▼
kvm_irq_map_gsi() ──查找 GSI 路由──▶ kvm_kernel_irq_routing_entry
    │
    ▼
e->set() 回调 (kvm_ioapic_set_irq / kvm_pic_set_irq / kvm_set_msi)
    │
    ├─▶ ioapic_set_irq()
    │       │
    │       ▼
    │       ioapic_service()
    │           │
    │           ▼
    │           kvm_irq_delivery_to_apic()
    │               │
    │               ▼
    │           kvm_apic_set_irq()
    │               │
    │               ▼
    │           __apic_accept_irq()
    │               │
    │               ▼
    │           apic_set_isr() + 注入到 vCPU
    │
    └─▶ kvm_set_msi() ──▶ kvm_msi_to_lapic_irq() ──▶ kvm_irq_delivery_to_apic()
```

### 6.2 LAPIC IPI 发送流程

```
Guest 写 ICR (Interrupt Command Register)
    │
    ▼
kvm_x2apic_icr_write() / __kvm_x2apic_icr_write()
    │
    ▼
kvm_icr_to_lapic_irq() ──构造 kvm_lapic_irq 结构
    │
    ▼
kvm_apic_send_ipi()
    │
    ▼
kvm_irq_delivery_to_apic()
    │
    ▼
__kvm_irq_delivery_to_apic()
    │
    ├─▶ __kvm_irq_delivery_to_apic_fast() (使用 apic_map 优化)
    │
    └─▶ 遍历所有 vCPU 匹配目标
            │
            ▼
        kvm_apic_set_irq() ──▶ __apic_accept_irq()
```

### 6.3 Eventfd (IRQFD) 流程

```
用户空间 eventfd_signal()
    │
    ▼
eventfd 等待队列唤醒
    │
    ▼
irqfd_wakeup()
    │
    ├─ EPOLLIN:
    │       │
    │       ▼
    │       kvm_arch_set_irq_inatomic() 或 schedule_work(&irqfd->inject)
    │               │
    │               ▼
    │       kvm_set_irq() ──▶ 中断注入流程
    │
    └─ EPOLLHUP:
            │
            ▼
        irqfd_deactivate()
            │
            ▼
        irqfd_shutdown() (延迟执行, 等待中的工作完成)
```

### 6.4 EOI 与 Resampler 流程

```
Guest 执行 EOI 写操作
    │
    ▼
kvm_apic_update_eoi()
    │
    ▼
kvm_ioapic_update_eoi_one()
    │
    ▼
kvm_notify_acked_irq() ──通知 ACK ──▶ irqfd_resampler_ack()
    │                                               │
    │                                               ▼
    │                                           eventfd_signal(resamplefd)
    │                                               │
    │                                               ▼
    │                                           重新注入中断
    │
    ▼
entry->fields.remote_irr = 0 (电平触发)
    │
    ▼
ioapic_service() (如果 IRR 仍挂起则重新投递)
```

---

## 关键常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `KVM_NR_IRQCHIPS` | 3 | IRQ 控制器数量 (PIC master, PIC slave, IOAPIC) |
| `KVM_IRQCHIP_NUM_PINS` | 24 | 每个控制器的引脚数 |
| `KVM_MAX_IRQ_ROUTES` | 256 | 最大 IRQ 路由数 |
| `IOAPIC_NUM_PINS` | 24 | IOAPIC 引脚数 |
| `LAPIC_MMIO_LENGTH` | 0x1000 | LAPIC MMIO 空间大小 |

---

## 参考文件

| 文件路径 | 说明 |
|----------|------|
| virt/kvm/irqchip.c | IRQ 路由核心实现 |
| virt/kvm/eventfd.c | IRQFD 和 ioeventfd 实现 |
| virt/kvm/vfio.c | VFIO 集成实现 |
| arch/x86/kvm/irq.c | x86 架构 IRQ 处理 |
| arch/x86/kvm/lapic.c | Local APIC 实现 |
| arch/x86/kvm/ioapic.c | IOAPIC 实现 |
| include/linux/kvm_host.h | KVM 核心数据结构 |
| arch/x86/kvm/lapic.h | LAPIC 头文件 |
| arch/x86/kvm/ioapic.h | IOAPIC 头文件 |
