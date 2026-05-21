---
type: entity
tags: [QEMU, 内存管理, 虚拟化]
created: 2026-05-20
sources: [notes-qemu]
---

# QEMU 内存管理

## 定义

QEMU 通过 AddressSpace、MemoryRegion、FlatView 三层结构实现模拟器的内存虚拟化，支持 MMIO、RAM、ROM 等多种内存区域类型。

## 关键要点

- **AddressSpace**: 全局地址空间容器，包含根 MemoryRegion 和当前 FlatView
- **MemoryRegion**: 可嵌套的内存区域，支持 `ops` 回调定义读写行为
- **FlatView**: 地址空间的扁平化视图，按地址排序的 FlatRange 数组
- **RAMBlock**: 主机端的物理内存块，通过 mmap 文件描述符管理
- **脏页跟踪**: `cpu_physical_memory_set_dirty_range()` 标记脏页，用于迁移
- **I/O 流程**: `address_space_read/write()` → `address_space_dispatch_*()` → `memory_region_dispatch_*()` → `ops->read/write()`

## 设计模式

1. **视图模式**: FlatView 按需重建，提供内存的简化视图
2. **分派模式**: MemoryRegionOps 分派具体操作
3. **监听器模式**: AddressSpaceListeners 通知区域变化
4. **懒评估**: 内存区域按需创建和销毁

## 相关概念

- [[entities/linux/qemu/qemu-qom]] — MemoryRegion 继承自 Object 类型
- [[entities/linux/qemu/qemu-cpu]] — CPU 通过内存管理访问 guest 内存
- [[entities/linux/qemu/qemu-migration]] — 脏页跟踪用于 live migration

## 来源详情

- [[sources/notes-qemu]]
