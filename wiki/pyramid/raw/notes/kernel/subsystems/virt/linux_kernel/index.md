# Linux 虚拟化子系统 (virt/) 文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [kvm_core.md](kvm_core.md) | KVM 核心架构: struct kvm, VMX/SVM, 用户空间交互 | virt/kvm/kvm_main.c |
| [kvm_vcpu.md](kvm_vcpu.md) | KVM vCPU 管理: 创建/销毁, VM-Exit/Entry, 任务调度 | arch/x86/kvm/x86.c |
| [kvm_mmu.md](kvm_mmu.md) | KVM MMU 虚拟化: EPT/NPT, TDP MMU, 影子页表, 脏页追踪 | virt/kvm/mmu/, arch/x86/kvm/mmu/ |
| [kvm_memory.md](kvm_memory.md) | KVM 内存管理: Dirty Ring, PFN Cache, Guest Memfd, Memory Slot | virt/kvm/guest_memfd.c, pfncache.c |
| [kvm_interrupt.md](kvm_interrupt.md) | KVM 中断模拟: IRQ Chip, LAPIC, IOAPIC, Eventfd, VFIO | virt/kvm/irqchip.c, arch/x86/kvm/lapic.c |
| [virtio_framework.md](virtio_framework.md) | Virtio 框架: virtio_device, virtqueue, 设备状态机, 特征位 | virt/virtio/virtio.c |
| [virtio_ring.md](virtio_ring.md) | Virtio Ring: Split Ring, Packed Ring, DMA, 内存屏障 | drivers/virtio/virtio_ring.c |
| [virtio_transport.md](virtio_transport.md) | Virtio 传输层: PCI, MMIO, MSI/MSI-X, 配置空间 | drivers/virtio/virtio_pci*.c |
| [virtio_drivers.md](virtio_drivers.md) | Virtio 设备驱动: Balloon, Mem, Input, vDPA | virt/virtio/virtio_*.c |
| [virtio_device_drivers.md](virtio_device_drivers.md) | Virtio 设备驱动详细: Block, Net, Console, SCSI, GPU | drivers/block/virtio_blk.c, net/virtio_net.c |

---

## 1. KVM 核心架构 (kvm_core.md)

### 关键内容
- `struct kvm`: VM 实例结构
- `struct kvm_vcpu`: vCPU 结构
- `struct kvm_run`: vCPU 运行状态
- `kvm_init()`: 模块初始化
- `kvm_create_vm()`: 创建虚拟机
- `kvm_vm_ioctl()`: VM IOCTL 接口

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| kvm_init | virt/kvm/kvm_main.c:6487 |
| kvm_create_vm | virt/kvm/kvm_main.c:1105 |
| kvm_vm_ioctl_create_vcpu | virt/kvm/kvm_main.c:4158 |

---

## 2. KVM vCPU 管理 (kvm_vcpu.md)

### 关键内容
- vCPU 创建/销毁流程
- VM-Exit/VM-Entry 切换
- 寄存器状态管理 (MSR, GDT)
- vCPU 任务调度 (block, kick)

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| kvm_arch_vcpu_create | arch/x86/kvm/x86.c:12736 |
| vcpu_enter_guest | arch/x86/kvm/x86.c:11079 |
| vmx_vcpu_run | arch/x86/kvm/vmx.c:7580 |

---

## 3. KVM MMU 虚拟化 (kvm_mmu.md)

### 关键内容
- EPT/NPT 嵌套页表
- TDP MMU (Two-Dimensional Paging)
- 影子页表机制
- 脏页追踪 (dirty_bitmap vs dirty_ring)

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| kvm_tdp_mmu_map | virt/kvm/mmu/tdp_mmu.c:1263 |
| kvm_tdp_mmu_alloc_root | virt/kvm/mmu/tdp_mmu.c:253 |

---

## 4. KVM 内存管理 (kvm_memory.md)

### 关键内容
- Dirty Ring 脏页环机制
- PFN Cache (gfn_to_pfn_cache)
- Guest Memfd
- Memory Slot 管理

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| kvm_dirty_ring_alloc | virt/kvm/dirty_ring.c:74 |
| kvm_gmem_create | virt/kvm/guest_memfd.c:628 |
| kvm_set_memory_region | virt/kvm/kvm_main.c:2001 |

---

## 5. KVM 中断模拟 (kvm_interrupt.md)

### 关键内容
- IRQ Chip 模拟
- Local APIC (LAPIC)
- IOAPIC 中断路由
- Eventfd (IRQFD) 集成
- VFIO passthrough

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| kvm_set_irq | virt/kvm/irqchip.c:70 |
| kvm_apic_send_ipi | arch/x86/kvm/lapic.c:1645 |

---

## 6. Virtio 框架 (virtio_framework.md)

### 关键内容
- `struct virtio_device`: 设备结构
- `struct virtqueue`: 虚拟队列
- 设备状态机 (ACKNOWLEDGE → DRIVER → ...)
- 特征位协商

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| register_virtio_driver | virt/virtio/virtio.c:449 |
| virtio_add_device | virt/virtio/virtio.c:517 |

---

## 7. Virtio Ring (virtio_ring.md)

### 关键内容
- Split Ring: 传统实现 (desc/avail/used ring)
- Packed Ring: 现代实现 (压缩描述符)
- DMA 映射和内存屏障
- virtqueue_add/get/kick 操作

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| virtqueue_add_split | drivers/virtio/virtio_ring.c:599 |
| virtqueue_add_packed | drivers/virtio/virtio_ring.c:1615 |
| vring_interrupt | drivers/virtio/virtio_ring.c:3229 |

---

## 8. Virtio 传输层 (virtio_transport.md)

### 关键内容
- PCI 传输: 能力查找, MSI/MSI-X
- MMIO 传输: 寄存器映射
- virtio_config_ops 接口

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| virtio_pci_find_capability | drivers/virtio/virtio_pci_common.c |
| virtio_mmio_probe | drivers/virtio/virtio_mmio.c |

---

## 9. Virtio 设备驱动 (virtio_drivers.md)

### 关键内容
- Virtio Balloon: 内存气球
- Virtio Mem: 内存热插拔
- Virtio Input: 输入设备
- vDPA: vhost Data Path Acceleration

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| fill_balloon | virt/virtio/virtio_balloon.c |
| virtio_mem_add | virt/virtio/virtio_mem.c |

---

## 10. Virtio 设备驱动详细 (virtio_device_drivers.md)

### 关键内容
- Virtio Block: 块设备存储
- Virtio Net: 网络驱动
- Virtio Console: 串口控制台
- Virtio SCSI: SCSI 存储
- Virtio GPU: 虚拟显示

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         QEMU / 用户空间                  │
                    └─────────────────┬───────────────────────┘
                                      │ ioctl / mmap
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         /dev/kvm                        │
                    │    KVM_GET/SET_VCPU_STATE              │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │    KVM VM Instance   │               │    Virtio Device    │
        │    (struct kvm)      │               │  (virtio_device)    │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                      │
                   ▼                                      ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │    KVM vCPU         │               │    Virtqueue        │
        │   (kvm_vcpu)       │               │   (virtqueue)       │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                      │
                   ▼                                      ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │  VM-Exit / VM-Entry │               │    Shared Memory    │
        │  (VMX / SVM)        │               │    (VRing)         │
        └─────────────────────┘               └─────────────────────┘


Virtio 设备类型:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ virtio_blk  │  │ virtio_net  │  │virtio_balloon│  │virtio_input│
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

---

## 源码位置索引

| 组件 | 文件路径 |
|------|----------|
| KVM 核心 | virt/kvm/kvm_main.c |
| KVM MMU | virt/kvm/mmu/, arch/x86/kvm/mmu/ |
| KVM vCPU | arch/x86/kvm/x86.c, arch/x86/kvm/vmx.c |
| KVM 中断 | virt/kvm/irqchip.c, arch/x86/kvm/lapic.c |
| KVM 内存 | virt/kvm/guest_memfd.c, pfncache.c, dirty_ring.c |
| Virtio 核心 | virt/virtio/virtio.c |
| Virtio Ring | drivers/virtio/virtio_ring.c |
| Virtio PCI | drivers/virtio/virtio_pci*.c |
| Virtio MMIO | drivers/virtio/virtio_mmio.c |
| Virtio Block | drivers/block/virtio_blk.c |
| Virtio Net | drivers/net/virtio_net.c |
| Virtio Balloon | virt/virtio/virtio_balloon.c |
| Virtio Mem | virt/virtio/virtio_mem.c |
| Virtio Input | virt/virtio/virtio_input.c |
| Virtio vDPA | virt/virtio/virtio_vdpa.c |

## 深度分析

- [virt_deep_dive_r1.md](virt_deep_dive_r1.md) - 深度分析 R1: KVM Core, vCPU, MMU/EPT, KVM_RUN, Dirty Ring, guest_memfd
- [virt_deep_dive_r2.md](virt_deep_dive_r2.md) - 深度分析 R2: kvm_mmu_map_page, tdp_mmu_iter, ept_sync_root, kvm_x86_emulator, vmx_vcpu_run, nested VMX
