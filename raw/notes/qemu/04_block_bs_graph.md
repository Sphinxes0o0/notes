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

## 权限模型

BdrvChild 使用perm和shared_perm实现安全的共享访问：

```c
// block.c
bdrv_check_perm()
{
    // 检查所有子节点的权限请求
    QLIST_FOREACH(child, &bs->parents, next_parent) {
        required = child->perm;
        shared = child->shared_perm;
        // 验证权限兼容性
    }
}

// 权限标志
#define BLK_PERM_VALID (BLK_PERM_READ | BLK_PERM_WRITE | \
                        BLK_PERM_RESIZE | BLK_PERM_GRAPH_MOD)
```

## 冻结链接 (Frozen Links)

冻结机制防止在热迁移期间子图结构被修改：

```c
// block.c
bdrv_freeze_child_link()
{
    child->frozen = true;
    // 冻结后，任何尝试修改连接的操作都会失败
}

bdrv_unfreeze_child_link()
{
    child->frozen = false;
}
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

## 子节点替换

在事务中安全替换子节点：

```c
// block.c
bdrv_replace_child_noperm()
{
    // 从旧父节点移除
    qlist_remove(&child->next_parent);
    // 添加到新父节点
    qlist_insert(&new_bs->parents, &child->next_parent, ...);
    // 更新指向
    child->bs = new_bs;
}
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `block.c` | BDS 图管理, bdrv_open_child, bdrv_replace_child |
| `block_int-common.h` | BdrvChild, BlockDriverState 结构定义 |
| `io.c` | COW 实现, bdrv_co_do_copy_on_readv |
| `backup.c` | 备份任务的 COW 处理 |
