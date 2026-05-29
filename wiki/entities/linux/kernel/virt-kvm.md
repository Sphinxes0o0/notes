---
type: entity
tags: [linux-kernel, virtualization, kvm]
created: 2026-05-20
sources: [github-notes-virt-kvm-core, github-notes-virt-kvm-vcpu, github-notes-virt-kvm-mmu, github-notes-virt-kvm-memory, github-notes-virt-kvm-interrupt]
---

# Linux Kernel KVM Virtualization

KVM (Kernel-based Virtual Machine) 是 Linux 内核的完整硬件虚拟化解决方案，将内核转变为 hypervisor。

## 定义

KVM 是 Linux 内核内置的 Type-1 虚拟化平台，通过硬件虚拟化扩展（Intel VT-x / AMD-V）实现高性能虚拟机监控。

## 关键要点

### 核心架构

- **struct kvm**: VM 实例结构，管理所有 vCPU 和内存槽
- **struct kvm_vcpu**: 虚拟 CPU，每个 vCPU 是独立调度实体
- **struct kvm_run**: 与用户空间共享的运行状态（通过 ioctl 访问）
- VM-Exit / VM-Entry: vCPU 在 guest 和 host 模式间的切换
- mmu_notifier: KVM 注册的页表失效回调，监听宿主内存变化

### vCPU 管理

- vCPU 创建: `kvm_arch_vcpu_create()` → 分配 LAPIC、设置初始状态
- vCPU 运行: `vcpu_enter_guest()` → VMX/SVM 指令进入 guest
- 退出处理: `handle_exit()` → 查表分发到具体处理函数
- 模式状态机: OUTSIDE_GUEST → IN_GUEST → EXITING_GUEST

### 内存虚拟化

- **EPT/NPT**: 嵌套页表，guest 虚拟地址 → guest 物理地址 → host 物理地址的两级转换
- **TDP MMU**: Top-Down Level Page Table，KVM 自己的页表遍历实现
- **Dirty Ring**: 替代 dirty_bitmap，批量追踪脏页，避免全量扫描
- **guest_memfd**: 虚拟机私有内存文件描述符，支持大页和 folio 管理

### 中断虚拟化

- IRQ Chip 模拟: `kvm_set_irq()` 注入外部中断
- Local APIC: `kvm_apic_send_ipi()` 处理处理器间中断
- IOAPIC: 中断路由到 vCPU
- Eventfd (IRQFD): 绕过内核直接注入中断

### 关键源码文件

| 文件 | 作用 |
|------|------|
| `virt/kvm/kvm_main.c` | KVM 核心：VM 创建、ioctl 入口 |
| `arch/x86/kvm/x86.c` | x86 架构：vcpu_run、MSR 模拟 |
| `arch/x86/kvm/vmx.c` | Intel VT-x：VMX 指令实现 |
| `virt/kvm/mmu/tdp_mmu.c` | TDP MMU 页表映射 |
| `virt/kvm/dirty_ring.c` | Dirty Ring 脏页追踪 |
| `virt/kvm/guest_memfd.c` | Guest 私有内存管理 |

## 相关概念

- [[entities/linux/kernel/virt-virtio]]: Virtio 设备模拟
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]]: 页错误处理（KVM EPT Violation 类似机制）
- [[entities/linux/kernel/sched/linux-kernel-sched-core]]: vCPU 调度（vCPU 作为调度实体）
- [[entities/linux/kernel/block/linux-kernel-block-mq]]: 虚拟机块设备后端

## 来源详情

- `raw/github/notes/virt/linux_kernel/kvm_core.md`
- `raw/github/notes/virt/linux_kernel/kvm_vcpu.md`
- `raw/github/notes/virt/linux_kernel/kvm_mmu.md`
- `raw/github/notes/virt/linux_kernel/kvm_memory.md`
- `raw/github/notes/virt/linux_kernel/kvm_interrupt.md`
- `raw/github/notes/virt/linux_kernel/virt_deep_dive_r1.md`
- `raw/github/notes/virt/linux_kernel/virt_deep_dive_r2.md`
