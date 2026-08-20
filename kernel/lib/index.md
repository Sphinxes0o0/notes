---
title: "Linux lib 子系统文档索引"
---
# Linux lib 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [lib_subsystem.md](lib_subsystem.md) | 通用库: bitmap, radix-tree, idr | lib/ |
| [lib_deep_dive_r2.md](lib_deep_dive_r2.md) | 深度分析 R2: bitmap算法, radix-tree并发, IDR/IDA, cmdline | lib/ |

---

## 主要内容

### 1. 位图 (bitmap)
- bitmap_alloc()
- bitmap_set/clear
- bitmap_find_next_zero_area

### 2. 基数树 (radix-tree)
- radix_tree_insert/lookup/delete
- 标签机制
- 迭代器

### 3. IDR
- idr_alloc/find/remove
- IDA (ID 分配器)

### 4. 命令行解析
- get_option()
- parse_option_str()

### 5. 其他
- 安全字符串操作
- gcd (最大公约数)

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| bitmap | lib/bitmap.c |
| radix-tree | lib/radix-tree.c |
| idr | lib/idr.c |
| cmdline | lib/cmdline.c |
