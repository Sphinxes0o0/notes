---
type: source
source-type: bookmark
title: "You Are The BIOS Now: Building A Hypervisor In Rust With KVM"
author: "Julian Goldstein"
date: 2025-07-29
summary: "用Rust+KVM从用户态构建Type-II hypervisor：VCPU管理、guest内存映射、x86实模式到长模式、I/O端口虚拟化、VMExit处理"
---

# You Are The BIOS Now: Building A Hypervisor In Rust With KVM

## 核心内容

**Type-II Hypervisor 架构**
- KVM（Kernel-based Virtual Machine）：Linux内置虚拟化层，无需内核模块
- 用户空间程序通过ioctl与/dev/kvm交互
- VCPU：虚拟CPU，每个VCPU是独立调度实体
- Guest内存通过mmap_anonymous分配，通过kvm_userspace_memory_region注册

**VCPU 管理**
- `Kvm::new()` 打开 `/dev/kvm`
- `vm.create_vcpu(0)` 创建虚拟CPU
- `vcpu.run()` 进入guest执行
- `vcpu.get_sregs()` / `vcpu.set_sregs()` 读写特殊寄存器
- `vcpu.get_regs()` / `vcpu.set_regs()` 读写通用寄存器

**Guest 内存映射**
- `mmap_anonymous`：分配guest物理内存
- `kvm_userspace_memory_region`：将用户空间地址映射为guest物理地址
- PML4→PDPT→PD→Page四级页表，identity map首1GB
- CR3指向PML4，2MB大页映射

**x86 模式切换**
- 实模式（16-bit）：1MB地址空间，段寄存器×16
- 保护模式（32-bit）：GDT描述符，特权级
- 长模式（64-bit）：GDT + EFER.LME + CR0.PG + CR4.PAE
- Guest无BIOS，启动时需要手动初始化所有状态

**GDT（全局描述符表）**
- 三个描述符：Null、Code Segment（64-bit）、Data Segment
- CS: present/dpl=0/type=11(Code)/L=1(Long mode)
- DS/ES/FS/GS/SS：type=3(Data)/DPL=0

**I/O 虚拟化**
- I/O端口：x86古董，每条in/out指令触发VMExit
- Guest通过outb向端口0x10写字符，主机拦截后打印
- "tin can phone"隐喻：两端靠信任和ioctl连接

**VMExit 处理**
- `VcpuExit::IoOut(port, data)`：Guest执行out指令
- Hypervisor实现io_handler回调处理I/O
- 可用BPF观测VMExit频率

## 来源详情

- 路径：`raw/bookmarks/ebooks/hypervisor-rust.md`
- 博客：https://yeet.cx/blog/you-are-the-bios-now
- 标签：#rust #hypervisor #kvm #x86
