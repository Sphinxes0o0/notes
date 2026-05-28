---
type: entity
tags: [virtualization, hypervisor, KVM, VMX, SVM, VMExit]
created: 2026-05-28
sources: [bookmark-hypervisor-rust]
---

# Hypervisor Design

## 定义

Hypervisor（虚拟机监控器）是创建和运行虚拟机的软件，按类型分为：Type-I（裸金属，直接运行在硬件上，如Xen、VMware ESXi）和Type-II（运行在宿主操作系统上，如KVM、VirtualBox）。KVM作为Linux内核模块，属于Type-I但通过用户空间工具（QEMU）提供完整设备模拟。

## 关键要点

### Type-II Hypervisor：KVM架构
- `/dev/kvm`：与内核KVM模块通信的设备文件
- `ioctl`：创建VM、创建VCPU、设置内存、运行guest
- VCPU是独立调度实体，由Linux调度器管理
- 无需内核模块，用户空间即可虚拟化

### 核心数据结构
- **KVM**：VM实例，管理所有VCPU和内存槽
- **VCPU**：虚拟CPU，通过vcpu_fd文件描述符操作
- **KVM_run**：共享数据结构，包含VMExit原因和状态
- **guest_memfd**：虚拟机私有内存

### 内存虚拟化
- `mmap_anonymous`：分配guest物理内存
- `kvm_userspace_memory_region`：将host用户空间地址映射为guest物理地址
- **EPT/NPT**：嵌套页表，两级翻译（gVA→gPA→hPA）
- **TDP MMU**：KVM自己的页表遍历实现

### CPU虚拟化
- **VMX指令**（Intel VT-x）：VMXON/VMLAUNCH/VMRESUME/VMXOFF
- **SVM指令**（AMD-V）：VMRUN/VMMCALL/VMLOAD/VMSAVE
- **VMExit**：guest执行特定指令或事件时切入host
- **VMEntry**：从host切回guest

### x86模式切换
- Guest启动时处于实模式（16-bit，1MB地址空间）
- 必须手动初始化：
  1. 配置GDT（全局描述符表）
  2. 设置CR0/CR4/EFER寄存器
  3. 配置页表（PML4→PDPT→PD）
  4. 加载通用寄存器（RIP/RSP/RBP）
- 长模式（64-bit）：GDT + EFER.LME + CR0.PG + CR4.PAE

### I/O虚拟化
- **I/O端口**：in/out指令访问，触发VMExit
- 常见模式：guest通过outb写特定端口，host拦截处理
- **IRQFD**（Interrupt Event FD）：绕过内核直接注入中断
- **APIC**：Local APIC + IOAPIC中断路由

### 与容器虚拟化的区别
- 容器：共享内核，隔离命名空间（cgroups/namespace）
- Hypervisor：独立内核，硬件级隔离
- 安全边界：Hypervisor远大于容器

## 相关概念

- [[linux/kernel/virt/linux-kernel-virt-kvm]] — Linux内核KVM实现：vcpu_run/VMX/ept_mmu/事件通道
- [[linux/kernel/virt/linux-kernel-virt-virtio]] — Virtio半虚拟化设备，Hypervisor常用后端
- [[cpu-architecture]] — x86体系结构（实模式/保护模式/长模式/GDT/段描述符）
- [[memory-hierarchy]] — TLB和页表机制是虚拟化的核心依赖

## 来源详情

- [[sources/bookmark-hypervisor-rust]] — You Are The BIOS Now: Building A Hypervisor In Rust With KVM
