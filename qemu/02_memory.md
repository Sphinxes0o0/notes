---
title: 内存管理
---

# QEMU 内存管理架构分析

## 核心概念

### 地址空间 (AddressSpace)

```c
struct AddressSpace {
    MemoryRegion *root;                  // 根内存区域
    FlatView *current_map;              // 当前平面视图
    int ref_count;
    uintptr_t allocated_regions;
    QTAILQ_HEAD(, AddressSpaceListeners) listeners;
    QTAILQ_ENTRY(AddressSpace) address_spaces_link;
};
```

### 内存区域 (MemoryRegion)

```c
struct MemoryRegion {
    Object obj;                         // 继承自 Object
    MemoryRegionOps *ops;               // 操作接口
    MemoryRegion *parent;               // 父区域
    Int128 size;                        // 大小
    hwaddr addr;                        // 地址
    void *opaque;                       // 驱动私有数据
    bool romd_mode;                     // ROMD 模式
    bool ram;                           // 是否 RAM
    bool subpage;                       // 是否子页
    bool readonly;                      // 只读
    bool nonvolatile;                   // 非易失
    bool rom_device;                    // ROM 设备
    bool flush_coalesced;              // 刷新合并
};
```

### 平面视图 (FlatView)

```c
struct FlatView {
    unsigned ref;
    FlatRange *ranges;                  // 平面范围数组
    unsigned nranges;                   // 范围数量
    unsigned notifier_mem_dirty;
    struct FlatView *next_view;
};
```

## 内存区域操作

### 内存区域操作接口

```c
struct MemoryRegionOps {
    bool (*valid.accepts)(void *opaque, hwaddr addr,
                          unsigned size, bool *ret);
    int (*read)(void *opaque, hwaddr addr, uint64_t *value, unsigned size);
    int (*write)(void *opaque, hwaddr addr, uint64_t value, unsigned size);
    MemTxResult (*read_with_attrs)(void *opaque, hwaddr addr,
                                    uint64_t *value, unsigned size, MemTxAttrs attrs);
    MemTxResult (*write_with_attrs)(void *opaque, hwaddr addr,
                                     uint64_t value, unsigned size, MemTxAttrs attrs);
    // ... 更多字段
};
```

### I/O 操作流程

```
address_space_read/write()
  → address_space_dispatch_read/write()
    → memory_region_dispatch_read/write()
      → ops->read/write()
```

## 子系统

### RAMBlock

```c
struct RAMBlock {
    void *host;                         // 主机地址
    void *colocated;                    // 协同定位
    size_t used_length;                // 使用长度
    size_t max_length;                 // 最大长度
    int fd;                            // 内存文件描述符
    void *mr;                          // 关联的 MemoryRegion
};
```

### 脏页跟踪

- `cpu_physical_memory_set_dirty_range()` 设置脏页
- `memory_region_set_dirty()` 标记区域为脏
- `bdrv_get_dirty_count()` 获取脏页数量

## 设计模式

1. **视图模式**: FlatView 提供内存的简化视图
2. **分派模式**: MemoryRegionOps 分派具体操作
3. **监听器模式**: AddressSpaceListeners 通知区域变化
4. **懒评估**: 内存区域按需创建和销毁
