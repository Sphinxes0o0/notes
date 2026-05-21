---
type: entity
tags: [QEMU, 块设备, QCOW2, 存储]
created: 2026-05-20
sources: [notes-qemu]
---

# QEMU 块设备层

## 定义

QEMU 块设备层通过 BlockDriverState (BDS) 图结构管理存储，支持 QCOW2、RAW 等多种格式，协程实现异步 I/O。

## 关键要点

- **BDS 图结构**: 每个 BDS 有 `children`（子节点链表）和 `parents`（父节点链表），通过 `BdrvChild` 连接
- **BdrvChildRole**: `BDRV_CHILD_COW`（写时复制）、`BDRV_CHILD_DATA`（数据）、`BDRV_CHILD_FILTERED`（过滤）、`BDRV_CHILD_METADATA`（元数据）
- **权限模型**: `perm` + `shared_perm` 实现安全的共享访问，`BLK_PERM_READ/WRITE/RESIZE/GRAPH_MOD`
- **冻结链接**: 热迁移期间 `frozen=true` 防止子图结构修改
- **COW (Copy-On-Read)**: 读取未分配区域时从后备文件复制数据
- **bdrv_open_child 流程**: `bdrv_open_child()` → `bdrv_open_child_common()` → `bdrv_attach_child()` → 添加到 parents/children 列表

## 设计模式

1. **图结构**: BDS 通过 BdrvChild 形成有向无环图（DAG）
2. **协程模式**: 块 I/O 使用协程避免线程阻塞
3. **权限模型**: 多消费者并发访问的读写权限控制

## 相关概念

- [[entities/linux/qemu/qemu-memory]] — 块设备涉及内存映射
- [[entities/linux/qemu/qemu-migration]] — 冻结链接用于迁移期间的一致性

## 来源详情

- [[sources/github-notes-qemu]]
