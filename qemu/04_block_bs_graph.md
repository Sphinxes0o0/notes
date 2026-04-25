---
title: BlockDriverState 图结构
---

# BlockDriverState 图结构分析

## BdrvChild 结构

```c
struct BdrvChild {
    BlockDriverState *bs;              // 指向的块设备
    char *name;                         // 子节点名称
    const BdrvChildClass *klass;       // 子节点类
    BdrvChildRole role;                 // 角色类型
    void *opaque;                       // 私有数据
    uint64_t perm;                      // 授予的权限
    uint64_t shared_perm;               // 可共享的权限
    bool frozen;                        // 链接冻结标志
    bool quiesced_parent;               // 父节点排空状态
    QLIST_ENTRY(BdrvChild) next;        // 在 bs->children 列表中
    QLIST_ENTRY(BdrvChild) next_parent; // 在 bs->parents 列表中
};
```

## 父子关系

- 每个 BDS 有 `QLIST_HEAD(, BdrvChild) children` - 子节点列表
- 每个 BDS 有 `QLIST_HEAD(, BdrvChild) parents` - 父节点列表

### BdrvChildRole 角色类型

```c
enum BdrvChildRole {
    BDRV_CHILD_COW,         // 写时复制后备存储
    BDRV_CHILD_DATA,        // 数据子节点
    BDRV_CHILD_FILTERED,    // 过滤子节点
    BDRV_CHILD_METADATA,    // 元数据子节点
};
```

## bdrv_open_child 流程

```c
bdrv_open_child()
  → bdrv_open_child_common()
    → bdrv_open_child_bs()
      → bdrv_open_inherit()
    → bdrv_attach_child()
      → 添加到 parents 列表
      → 添加到 children 列表
```

## COW (Copy-On-Read)

```c
// block/io.c
bdrv_co_do_copy_on_readv()
{
    // 读取未分配区域时从后备文件复制数据
    if (!bs->backing) {
        return;
    }

    // 使用弹跳缓冲区安全复制
    bounce_buffer = qemu_blockalign(bs, len);
    copy_from_backing_file(bounce_buffer, offset, len);
}
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `block.c` | BDS 图管理, bdrv_open_child |
| `block_int-common.h` | BdrvChild, BlockDriverState 结构 |
| `io.c` | COW 实现 |
