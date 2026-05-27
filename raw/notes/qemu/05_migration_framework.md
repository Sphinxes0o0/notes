---
title: 迁移框架
---

# 迁移框架分析

## VMState 机制

```c
// migration/vmstate.c
struct VMStateDescription {
    const char *name;                // 唯一标识符
    int version_id;                  // 当前版本号
    int minimum_version_id;          // 最小兼容版本
    const VMStateField *fields;     // 数据布局描述
    const VMStateDescription **subsections; // 子描述
    int (*pre_load)(void *opaque); // 加载前钩子
    int (*post_load)(void *opaque, int version_id); // 加载后钩子
    int (*pre_save)(void *opaque); // 保存前钩子
    int (*post_save)(void *opaque); // 保存后钩子
};

// 字段类型
VMS_STRUCT, VMS_VSTRUCT, VMS_POINTER, VMS_ARRAY, VMS_VARRAY_*
```

## SaveVM/LoadVM

```c
// migration/savevm.c
struct SaveStateEntry {
    char *idstr;                     // ID 字符串
    int instance_id;                 // 实例 ID
    int version_id;                  // 版本 ID
    int section_id;                  // 段 ID
    SaveVMHandlers *ops;            // 处理程序
    const VMStateDescription *vmsd; // VM 状态描述
    void *opaque;                   // 私有数据
    QTAILQ_ENTRY(SaveStateEntry) next;
};
```

### VM 流格式

```c
QEMU_VM_SECTION_FULL      // 完整段: 头部 + 数据 + 页脚
QEMU_VM_SECTION_START     // 开始段
QEMU_VM_SECTION_END       // 结束段
QEMU_VM_SECTION_PART     // 部分段
QEMU_VM_COMMAND          // 迁移命令
QEMU_VM_EOF              // 终止标记
```

### 保存流程

```
qemu_savevm_state()
  → 遍历 SaveStateEntry 处理程序
    → 调用 save_live_iterate()
  → 通过 vmstate_save() 发送设备段
    → 带段头
  → qemu_savevm_state_complete_precopy()
```

## 迁移状态机

```c
// migration/migration.c
enum MigrationStatus {
    MIGRATION_STATUS_NONE,
    MIGRATION_STATUS_SETUP,
    MIGRATION_STATUS_ACTIVE,
    MIGRATION_STATUS_COMPLETED,
    MIGRATION_STATUS_FAILED,
    MIGRATION_STATUS_CANCELLING,
    MIGRATION_STATUS_CANCELLED,
    // Postcopy 变体
    MIGRATION_STATUS_POSTCOPY_ADVISE,
    MIGRATION_STATUS_POSTCOPY_LISTEN,
    MIGRATION_STATUS_POSTCOPY_RUN,
    // ...
};

// 状态转换通过 migrate_set_state() 管理，使用原子比较交换
```

## QEMUFile 机制

```c
// migration/qemu-file.h
struct QEMUFile {
    const QEMUFileOps *ops;          // 操作接口
    void *opaque;                   // 私有数据
    int64_t pos;                    // 当前位置
    int64_t len;                   // 长度
    int buf_index;                  // 缓冲区索引
    int buf_size;                   // 缓冲区大小
    unsigned char buf[16384];       // 缓冲区
};

// 基于 QIOChannel (socket, file, buffer)
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `vmstate.c` | VMState 声明式描述 |
| `savevm.c` | 保存/加载实现 |
| `migration.c` | 主迁移框架 |
| `qemu-file.c` | QEMUFile 抽象 |
