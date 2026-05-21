---
type: entity
tags: [linux-kernel, virtualization, virtio, para-virtualization]
created: 2026-05-20
sources: [github-notes-virt-virtio-framework, github-notes-virt-virtio-ring, github-notes-virt-virtio-transport, github-notes-virt-virtio-drivers]
---

# Linux Kernel Virtio Framework

Virtio 是 Linux 内核的半虚拟化 I/O 框架，定义 guest 与 host 之间的标准设备通信协议。

## 定义

Virtio 是一个开放标准，通过共享内存的 virtqueue 环形队列实现 guest 与 hypervisor 之间的高效通信，比纯模拟方案性能显著提升。

## 关键要点

### 核心数据结构

- **struct virtio_device**: 设备实例，持有特征位、virtqueue 链表、配置接口
- **struct virtqueue**: 虚拟队列，描述符环 + 可用环 + 已用环
- **struct virtio_driver**: 驱动描述符，定义支持的设备 ID 和回调
- **struct virtio_config_ops**: 配置操作接口（读写配置、协商特性）

### 设备状态机

```
ACKNOWLEDGE → DRIVER → DRIVER_OK
                      ↓
              FEATURES_OK (特性协商)
                      ↓
              DRIVER_OK (驱动就绪)
```

### Virtio Ring 实现

**Split Ring (传统)**:
- `struct vring_desc`: 描述符，16字节，指向 DMA 缓冲
- `struct vring_avail`: Guest 写入可用描述符索引
- `struct vring_used`: Host 写入已用描述符信息

**Packed Ring (现代 v1.0+)**:
- 压缩格式，无需分离的 avail/used 环
- 通过 wrap_counter 和 flags 区分可用/已用状态
- 支持描述符重置（`VIRTIO_F_RING_RESET`）

### 描述符链

- `VRING_DESC_F_NEXT`: 缓冲区链式连接
- `VRING_DESC_F_WRITE`: 写缓冲（由 device 填充）
- `VRING_DESC_F_INDIRECT`: 间接描述符，指向外部描述符数组

### 传输层

- **PCI**: 现代 PCI 配置空间 + MSI/MSI-X 中断
- **MMIO**: 早期 virtio-blk 使用的寄存器映射接口
- **vDPA**: vhost Data Path Acceleration，SR-IOV 虚拟函数直接 DMA

### 设备类型

| 设备 ID | 类型 | 驱动 |
|---------|------|------|
| 1 | virtio-net | `drivers/net/virtio_net.c` |
| 2 | virtio-blk | `drivers/block/virtio_blk.c` |
| 3 | virtio-console | `drivers/char/virtio_console.c` |
| 5 | virtio-balloon | `virt/virtio/virtio_balloon.c` |
| 8 | virtio-scsi | `drivers/scsi/virtio_scsi.c` |
| 16 | virtio-gpu | `drivers/gpu/drm/virtio/` |
| 24 | virtio-mem | `virt/virtio/virtio_mem.c` (内存热插拔) |

### 关键源码文件

| 文件 | 作用 |
|------|------|
| `drivers/virtio/virtio.c` | 核心框架：设备注册、探测、状态机 |
| `drivers/virtio/virtio_ring.c` | Virtqueue Ring 实现 |
| `drivers/virtio/virtio_pci_common.c` | PCI 传输公共代码 |
| `drivers/virtio/virtio_mmio.c` | MMIO 传输 |
| `drivers/net/virtio_net.c` | 网络设备驱动 |
| `drivers/block/virtio_blk.c` | 块设备驱动 |

## 相关概念

- [[entities/linux/kernel/virt/linux-kernel-virt-kvm]]: KVM 虚拟机监控器（通常作为 Virtio 的 host 端）
- [[entities/linux/kernel/block/linux-kernel-block-core]]: 块设备层（virtio-blk 的后端）
- [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core]]: io_uring（现代异步 I/O，可与 Virtio 协同）

## 来源详情

- `raw/github/notes/virt/linux_kernel/virtio_framework.md`
- `raw/github/notes/virt/linux_kernel/virtio_ring.md`
- `raw/github/notes/virt/linux_kernel/virtio_transport.md`
- `raw/github/notes/virt/linux_kernel/virtio_drivers.md`
- `raw/github/notes/virt/linux_kernel/virtio_device_drivers.md`
## Related Concepts

- [[entities/linux/kernel/sound/linux-kernel-sound-core]] — Virtio音频设备驱动
