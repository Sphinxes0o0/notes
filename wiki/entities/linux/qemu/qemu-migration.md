---
type: entity
tags: [QEMU, 迁移, VMState, 虚拟机]
created: 2026-05-20
sources: [notes-qemu]
---

# QEMU 迁移框架

## 定义

QEMU 迁移框架通过 VMState 声明式描述和 QEMUFile 抽象，实现虚拟机在主机间的状态传输，支持 precopy、postcopy 等多种模式。

## 关键要点

- **VMState 机制**: `VMStateDescription` 描述数据结构版本和字段布局，支持 VMS_STRUCT/VMS_POINTER/VMS_ARRAY 等字段类型
- **SaveVM/LoadVM**: `SaveStateEntry` 保存设备状态，`qemu_savevm_state_complete_precopy()` 完成保存
- **VM 流格式**: `QEMU_VM_SECTION_FULL/START/END/PART/COMMAND/EOF` 段类型
- **迁移状态机**: `MIGRATION_STATUS_NONE` → `SETUP` → `ACTIVE` → `COMPLETED/FAILED/CANCELLING`
- **QEMUFile 抽象**: 封装数据流，支持 socket/file/buffer，基于 QIOChannel
- **脏页同步**: RAM 迁移使用 `cpu_physical_memory_set_dirty_range()` 跟踪脏页
- **Multifd**: 多 fd 并行传输，使用压缩算法（zlib/quicklz/zstd）

## 设计模式

1. **状态机模式**: 迁移状态转换通过 `migrate_set_state()` 原子管理
2. **声明式描述**: VMState 通过结构化描述而非代码序列化
3. **两阶段传输**: 先迭代传输（precopy），再停止传输（postcopy）

## 相关概念

- [[entities/linux/qemu/qemu-memory]] — RAM 迁移依赖脏页跟踪
- [[entities/linux/qemu/qemu-block-layer]] — 块设备迁移涉及 BDS 图的冻结

## 来源详情

- [[sources/github-notes-qemu]]
