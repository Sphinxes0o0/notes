# Linux 内核 lib/ 子系统分析文档

## 目录

1. [位图 (Bitmap)](#1-位图-bitmap)
2. [基数树 (Radix-Tree)](#2-基数树-radix-tree)
3. [IDR (ID Radix)](#3-idr-id-radix)
4. [命令行解析 (Command Line)](#4-命令行解析-cmdline)
5. [其他通用库函数](#5-其他通用库函数)

---

## 1. 位图 (Bitmap)

### 1.1 概述

位图(bitmap)是一种紧凑的数据结构,用于表示大量布尔值。Linux内核使用 `unsigned long` 数组来实现位图,每个比特表示一个标志位。

**源码位置**: `/Users/sphinx/github/linux/lib/bitmap.c`, `/Users/sphinx/github/linux/include/linux/bitmap.h`

### 1.2 核心数据结构

```c
// include/linux/bitmap.h
// 位图本质上是 unsigned long 数组
// DECLARE_BITMAP(name, nbits) 在 linux/types.h 中定义
```

### 1.3 关键函数分析

#### 1.3.1 bitmap_alloc() - 位图内存分配

```c
// lib/bitmap.c, 第723-728行
unsigned long *bitmap_alloc(unsigned int nbits, gfp_t flags)
{
    return kmalloc_array(BITS_TO_LONGS(nbits), sizeof(unsigned long),
                         flags);
}
EXPORT_SYMBOL(bitmap_alloc);
```

**功能**: 分配一个位图所需的内存
- 计算所需 `unsigned long` 数量: `BITS_TO_LONGS(nbits)`
- 使用 `kmalloc_array` 分配连续内存
- `flags`: 内存分配标志(如 `GFP_KERNEL`)

**变体**:
- `bitmap_zalloc()`: 分配并初始化为零
- `bitmap_alloc_node()`: 在指定节点分配
- `devm_bitmap_alloc()`: 设备管理内存

#### 1.3.2 bitmap_set() / bitmap_clear() - 位设置/清除

```c
// lib/bitmap.c, 第364-382行 - __bitmap_set 实现
void __bitmap_set(unsigned long *map, unsigned int start, int len)
{
    unsigned long *p = map + BIT_WORD(start);          // 定位到起始字
    const unsigned int size = start + len;
    int bits_to_set = BITS_PER_LONG - (start % BITS_PER_LONG);
    unsigned long mask_to_set = BITMAP_FIRST_WORD_MASK(start);

    while (len - bits_to_set >= 0) {                  // 循环处理完整字
        *p |= mask_to_set;
        len -= bits_to_set;
        bits_to_set = BITS_PER_LONG;
        mask_to_set = ~0UL;                            // 全F掩码
        p++;
    }
    if (len) {                                         // 处理尾部不完整字
        mask_to_set &= BITMAP_LAST_WORD_MASK(size);
        *p |= mask_to_set;
    }
}
```

```c
// lib/bitmap.c, 第385-403行 - __bitmap_clear 实现
void __bitmap_clear(unsigned long *map, unsigned int start, int len)
{
    unsigned long *p = map + BIT_WORD(start);
    const unsigned int size = start + len;
    int bits_to_clear = BITS_PER_LONG - (start % BITS_PER_LONG);
    unsigned long mask_to_clear = BITMAP_FIRST_WORD_MASK(start);

    while (len - bits_to_clear >= 0) {
        *p &= ~mask_to_clear;                          // 清除操作
        len -= bits_to_clear;
        bits_to_clear = BITS_PER_LONG;
        mask_to_clear = ~0UL;
        p++;
    }
    if (len) {
        mask_to_clear &= BITMAP_LAST_WORD_MASK(size);
        *p &= ~mask_to_clear;
    }
}
```

**算法核心**:
```
设 start=5, len=20, BITS_PER_LONG=64

第一次迭代:
  bits_to_set = 64 - (5 % 64) = 59
  mask = 0xFFFFFFFFFFFFFFE0 (第5位开始的掩码)
  59 >= 20, 条件不满足,进入尾部处理

尾部处理:
  mask = 0x000000FFFFFFFFFF & BITMAP_LAST_WORD_MASK(25)
       = 0x000000FFFFFFFFFF & 0x01FFFFFF
       = 0x01FFFFFF (25位全1)
```

#### 1.3.3 bitmap_find_next_zero_area_off() - 查找连续零区域

```c
// lib/bitmap.c, 第419-442行
unsigned long bitmap_find_next_zero_area_off(unsigned long *map,
                         unsigned long size,
                         unsigned long start,
                         unsigned int nr,
                         unsigned long align_mask,
                         unsigned long align_offset)
{
    unsigned long index, end, i;
again:
    index = find_next_zero_bit(map, size, start);      // 找下一个零位

    /* 对齐调整 */
    index = __ALIGN_MASK(index + align_offset, align_mask) - align_offset;

    end = index + nr;                                  // 连续区域末端
    if (end > size)
        return end;                                     // 超出范围
    i = find_next_bit(map, end, index);                // 检查是否全零
    if (i < end) {
        start = i + 1;                                  // 有占用,从头开始
        goto again;
    }
    return index;                                       // 找到合适的连续零区
}
```

**算法流程图**:

```
┌─────────────────────────────────────────────────────┐
│                   开始查找                           │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  find_next_zero_bit(map, size, start) → index       │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  对齐调整: index = ALIGN(index+offset, mask)        │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  end = index + nr (连续区域末端)                     │
└─────────────────────┬───────────────────────────────┘
                      ▼
              ┌───────────────┐
              │ end > size?   │
              └───────┬───────┘
         Yes /         \ No
            ▼            ▼
     ┌──────────┐  ┌─────────────────────────────┐
     │ return end│  │ find_next_bit(map, end, index)│
     │ (失败)    │  └─────────────┬───────────────┘
     └──────────┘                ▼
                      ┌───────────────────────┐
                      │  i < end (有位被占用)? │
                      └───────────┬───────────┘
                     Yes /         \ No
                        ▼            ▼
              ┌───────────────┐  ┌──────────┐
              │ start = i + 1 │  │return idx│
              │ goto again    │  │ (成功)   │
              └───────────────┘  └──────────┘
```

### 1.4 位图操作一览

| 操作 | 函数 | 说明 |
|------|------|------|
| 分配 | `bitmap_alloc()` | 分配位图内存 |
| 释放 | `bitmap_free()` | 释放位图内存 |
| 设置 | `bitmap_set()` | 设置连续位 |
| 清除 | `bitmap_clear()` | 清除连续位 |
| 查找零区 | `bitmap_find_next_zero_area()` | 查找连续零区域 |
| 与运算 | `bitmap_and()` | 位图AND操作 |
| 或运算 | `bitmap_or()` | 位图OR操作 |
| 异或运算 | `bitmap_xor()` | 位图XOR操作 |
| 取反 | `bitmap_complement()` | 位图取反 |
| 权重 | `bitmap_weight()` | 计算置位数 |

---

## 2. 基数树 (Radix-Tree)

### 2.1 概述

基数树是一种空间优化的前缀树,用于高效存储和查找键值对。在Linux内核中,基数树被广泛用于页面缓存、进程地址空间管理等场景。

**源码位置**: `/Users/sphinx/github/linux/lib/radix-tree.c`, `/Users/sphinx/github/linux/include/linux/radix-tree.h`

**注意**: 现代内核中 `radix_tree_root` 实际上是 `xarray` 的别名(见 include/linux/radix-tree.h 第25行)

### 2.2 核心数据结构

```c
// include/linux/radix-tree.h (通过 xarray.h)

// radix_tree_root 实际上是 xarray 的别名
#define radix_tree_root xarray
#define radix_tree_node xa_node

// include/linux/xarray.h 中的 xarray 结构
struct xarray {
    spinlock_t xa_lock;
    /* 最底部bits表示entry类型 */
    void *xa_head;
};

// 内部节点结构 (radix-tree.c 第67-75行)
#define RADIX_TREE_ENTRY_MASK     3UL
#define RADIX_TREE_INTERNAL_NODE  2UL

/* Slot类型判断:
 * 00 - 数据指针
 * 10 - 内部节点
 * x1 - 值条目
 */
```

**节点结构** (实际在 xarray.h 中定义):

```
Radix Tree 节点布局:

        根节点 (xa_node)
              │
    ┌─────────┼─────────┐
    │         │         │
  slot0   slot1   ... slot(MAP_SIZE-1)
    │         │
    ▼         ▼
  叶子A     内部节点B
              │
        ┌─────┼─────┐
        │     │     │
      slot0 slot1 ... slot(MAP_SIZE-1)
        │     │
        ▼     ▼
      数据   数据

MAP_SIZE = 2^RADIX_TREE_MAP_SHIFT = 2^6 = 64 (在64位系统上)
```

### 2.3 关键函数分析

#### 2.3.1 radix_tree_insert() - 插入操作

```c
// lib/radix-tree.c, 第703-730行
int radix_tree_insert(struct radix_tree_root *root, unsigned long index,
            void *item)
{
    struct radix_tree_node *node;
    void __rcu **slot;
    int error;

    BUG_ON(radix_tree_is_internal_node(item));         // 不能插入内部节点

    error = __radix_tree_create(root, index, &node, &slot); // 创建路径
    if (error)
        return error;

    error = insert_entries(node, slot, item);          // 插入条目
    if (error < 0)
        return error;

    // 确保该位置之前没有标签
    if (node) {
        unsigned offset = get_slot_offset(node, slot);
        BUG_ON(tag_get(node, 0, offset));
        BUG_ON(tag_get(node, 1, offset));
        BUG_ON(tag_get(node, 2, offset));
    } else {
        BUG_ON(root_tags_get(root));
    }

    return 0;
}
```

```c
// lib/radix-tree.c, 第598-645行 - __radix_tree_create
static int __radix_tree_create(struct radix_tree_root *root,
        unsigned long index, struct radix_tree_node **nodep,
        void __rcu ***slotp)
{
    struct radix_tree_node *node = NULL, *child;
    void __rcu **slot = (void __rcu **)&root->xa_head;
    unsigned long maxindex;
    unsigned int shift, offset = 0;
    unsigned long max = index;
    gfp_t gfp = root_gfp_mask(root);

    shift = radix_tree_load_root(root, &child, &maxindex);

    /* 确保树足够高 */
    if (max > maxindex) {
        int error = radix_tree_extend(root, gfp, max, shift);
        if (error < 0)
            return error;
        shift = error;
        child = rcu_dereference_raw(root->xa_head);
    }

    while (shift > 0) {
        shift -= RADIX_TREE_MAP_SHIFT;                 // 逐层下降
        if (child == NULL) {
            /* 需要添加子节点 */
            child = radix_tree_node_alloc(gfp, node, root, shift,
                            offset, 0, 0);
            if (!child)
                return -ENOMEM;
            rcu_assign_pointer(*slot, node_to_entry(child));
            if (node)
                node->count++;
        } else if (!radix_tree_is_internal_node(child))
            break;                                      // 遇到值节点

        node = entry_to_node(child);
        offset = radix_tree_descend(node, &child, index);
        slot = &node->slots[offset];
    }

    if (nodep)
        *nodep = node;
    if (slotp)
        *slotp = slot;
    return 0;
}
```

**插入算法流程**:

```
radix_tree_insert(root, index=50, item)

假设 MAP_SHIFT=6, MAP_SIZE=64

步骤1: __radix_tree_create
  index=50 = 0b110010
  level 0: offset = (50 >> 6) & 63 = 0
  level 1: offset = 50 & 63 = 50

步骤2: 创建必要的中间节点

步骤3: insert_entries() 将item放入slot
```

#### 2.3.2 radix_tree_lookup() - 查找操作

```c
// lib/radix-tree.c, 第747-779行
void *__radix_tree_lookup(const struct radix_tree_root *root,
              unsigned long index, struct radix_tree_node **nodep,
              void __rcu ***slotp)
{
    struct radix_tree_node *node, *parent;
    unsigned long maxindex;
    void __rcu **slot;

restart:
    parent = NULL;
    slot = (void __rcu **)&root->xa_head;
    radix_tree_load_root(root, &node, &maxindex);
    if (index > maxindex)
        return NULL;

    while (radix_tree_is_internal_node(node)) {       // 遍历内部节点
        unsigned offset;

        parent = entry_to_node(node);
        offset = radix_tree_descend(parent, &node, index);
        slot = parent->slots + offset;
        if (node == RADIX_TREE_RETRY)
            goto restart;                               // 处理并发修改
        if (parent->shift == 0)
            break;                                      // 到达叶子层
    }

    if (nodep)
        *nodep = parent;
    if (slotp)
        *slotp = slot;
    return node;                                       // 返回数据项
}
```

#### 2.3.3 radix_tree_delete() - 删除操作

```c
// lib/radix-tree.c, 第1413-1448行
void *radix_tree_delete_item(struct radix_tree_root *root,
                 unsigned long index, void *item)
{
    struct radix_tree_node *node = NULL;
    void __rcu **slot = NULL;
    void *entry;

    entry = __radix_tree_lookup(root, index, &node, &slot);
    if (!slot)
        return NULL;
    if (!entry && (!is_idr(root) || node_tag_get(root, node, IDR_FREE,
                    get_slot_offset(node, slot))))
        return NULL;

    if (item && entry != item)                         // 检查item匹配
        return NULL;

    __radix_tree_delete(root, node, slot);

    return entry;
}

static bool __radix_tree_delete(struct radix_tree_root *root,
                struct radix_tree_node *node, void __rcu **slot)
{
    void *old = rcu_dereference_raw(*slot);
    int values = xa_is_value(old) ? -1 : 0;
    unsigned offset = get_slot_offset(node, slot);
    int tag;

    if (is_idr(root))
        node_tag_set(root, node, IDR_FREE, offset);   // IDR标记为空闲
    else
        for (tag = 0; tag < RADIX_TREE_MAX_TAGS; tag++)
            node_tag_clear(root, node, tag, offset);   // 清除标签

    replace_slot(slot, NULL, node, -1, values);        // 删除条目
    return node && delete_node(root, node);           // 可能触发树收缩
}
```

### 2.4 标签机制 (Tagging)

基数树支持为条目打标签,用于快速查找满足特定条件的条目。

```c
// lib/radix-tree.c, 第100-116行
static inline void tag_set(struct radix_tree_node *node, unsigned int tag,
        int offset)
{
    __set_bit(offset, node->tags[tag]);
}

static inline void tag_clear(struct radix_tree_node *node, unsigned int tag,
        int offset)
{
    __clear_bit(offset, node->tags[tag]);
}

static inline int tag_get(const struct radix_tree_node *node, unsigned int tag,
        int offset)
{
    return test_bit(offset, node->tags[tag]);
}
```

**标签操作**:

| 操作 | 函数 | 说明 |
|------|------|------|
| 设置标签 | `radix_tree_tag_set()` | 从根到叶设置标签 |
| 清除标签 | `radix_tree_tag_clear()` | 清除标签,可能触发父节点清除 |
| 获取标签 | `radix_tree_tag_get()` | 获取特定条目标签 |
| 批量查找 | `radix_tree_gang_lookup_tag()` | 查找所有带特定标签的条目 |

**标签传播规则**:
- 向下: 设置标签时,所有父节点对应偏移位都被设置
- 向上: 清除叶子标签时,如果该节点所有子标签都被清除,则清除父节点标签

### 2.5 迭代器

```c
// include/linux/radix-tree.h, 第449-452行
#define radix_tree_for_each_slot(slot, root, iter, start)   \
    for (slot = radix_tree_iter_init(iter, start) ;         \
         slot || (slot = radix_tree_next_chunk(root, iter, 0)) ; \
         slot = radix_tree_next_slot(slot, iter, 0))

// 标签迭代
#define radix_tree_for_each_tagged(slot, root, iter, start, tag)   \
    for (slot = radix_tree_iter_init(iter, start) ;                 \
         slot || (slot = radix_tree_next_chunk(root, iter,         \
                  RADIX_TREE_ITER_TAGGED | tag)) ;                 \
         slot = radix_tree_next_slot(slot, iter,                    \
                  RADIX_TREE_ITER_TAGGED | tag))
```

---

## 3. IDR (ID Radix)

### 3.1 概述

IDR是基于基数树的ID分配器,用于将整数ID映射到指针。与基数树不同的是,IDR专门优化了整数ID的分配,支持高效的ID申请和释放。

**源码位置**: `/Users/sphinx/github/linux/lib/idr.c`, `/Users/sphinx/github/linux/include/linux/idr.h`

### 3.2 核心数据结构

```c
// include/linux/idr.h, 第20-30行
struct idr {
    struct radix_tree_root idr_rt;    // 底层基数树
    unsigned int        idr_base;     // ID起始值
    unsigned int        idr_next;     // 下一个待分配ID (用于循环分配)
};

/* IDR使用标签0来跟踪空闲空间 */
#define IDR_FREE  0

/* IDR标记,用于区分IDR和普通基数树 */
#define IDR_RT_MARKER (ROOT_IS_IDR | (__force gfp_t) \
                (1 << (ROOT_TAG_SHIFT + IDR_FREE)))
```

**IDR与基数树的关系**:

```
IDR 结构
┌────────────────────────────────────┐
│           struct idr               │
├────────────────────────────────────┤
│  idr_rt (radix_tree_root/xarray)   │──→ 基数树节点
│  idr_base = 0                      │    (使用IDR_FREE标签)
│  idr_next = 0                     │
└────────────────────────────────────┘

ID分配示例:
  ID:    0    1    2    3    4    5    ...
  状态:  used used free free used free ...
  标签:   0    0    1    1    0    1    (1=空闲)
```

### 3.3 关键函数分析

#### 3.3.1 idr_alloc() - ID分配

```c
// lib/idr.c, 第81-95行
int idr_alloc(struct idr *idr, void *ptr, int start, int end, gfp_t gfp)
{
    u32 id = start;
    int ret;

    if (WARN_ON_ONCE(start < 0))
        return -EINVAL;

    ret = idr_alloc_u32(idr, ptr, &id, end > 0 ? end - 1 : INT_MAX, gfp);
    if (ret)
        return ret;

    return id;
}
```

```c
// lib/idr.c, 第33-58行
int idr_alloc_u32(struct idr *idr, void *ptr, u32 *nextid,
             unsigned long max, gfp_t gfp)
{
    struct radix_tree_iter iter;
    void __rcu **slot;
    unsigned int base = idr->idr_base;
    unsigned int id = *nextid;

    if (WARN_ON_ONCE(!(idr->idr_rt.xa_flags & ROOT_IS_IDR)))
        idr->idr_rt.xa_flags |= IDR_RT_MARKER;
    if (max < base)
        return -ENOSPC;

    id = (id < base) ? 0 : id - base;                 // 相对ID
    radix_tree_iter_init(&iter, id);
    slot = idr_get_free(&idr->idr_rt, &iter, gfp, max - base);
    if (IS_ERR(slot))
        return PTR_ERR(slot);

    *nextid = iter.index + base;                      // 返回绝对ID
    radix_tree_iter_replace(&idr->idr_rt, &iter, slot, ptr);
    radix_tree_iter_tag_clear(&idr->idr_rt, &iter, IDR_FREE); // 清除空闲标签

    return 0;
}
```

#### 3.3.2 idr_find() - ID查找

```c
// lib/idr.c, 第174-178行
void *idr_find(const struct idr *idr, unsigned long id)
{
    return radix_tree_lookup(&idr->idr_rt, id - idr->idr_base);
}
```

#### 3.3.3 idr_remove() - ID删除

```c
// lib/idr.c, 第154-158行
void *idr_remove(struct idr *idr, unsigned long id)
{
    return radix_tree_delete_item(&idr->idr_rt, id - idr->idr_base, NULL);
}
```

### 3.4 IDA (ID Allocator)

IDA是更轻量级的ID分配器,当不需要存储指针时使用。

```c
// include/linux/idr.h, 第255-265行
#define IDA_CHUNK_SIZE   128    /* 每块128字节 */
#define IDA_BITMAP_LONGS (IDA_CHUNK_SIZE / sizeof(long))
#define IDA_BITMAP_BITS  (IDA_BITMAP_LONGS * sizeof(long) * 8)
// 在64位系统: IDA_BITMAP_BITS = 128/8 * 64 = 1024

struct ida_bitmap {
    unsigned long bitmap[IDA_BITMAP_LONGS];
};

struct ida {
    struct xarray xa;
};
```

**IDA vs IDR**:

| 特性 | IDA | IDR |
|------|-----|-----|
| 存储指针 | 否 | 是 |
| 内存效率 | 高 (1 bit/ID) | 低 (需要树结构) |
| 并发安全 | 是 (自带锁) | 否 (需外部同步) |
| 适用场景 | 简单ID分配 | ID到指针映射 |

---

## 4. 命令行解析 (cmdline)

### 4.1 概述

命令行解析模块提供了解析内核启动参数和模块选项的实用函数。

**源码位置**: `/Users/sphinx/github/linux/lib/cmdline.c`

### 4.2 关键函数分析

#### 4.2.1 get_option() - 解析单个整数选项

```c
// lib/cmdline.c, 第56-79行
int get_option(char **str, int *pint)
{
    char *cur = *str;
    int value;

    if (!cur || !(*cur))
        return 0;
    if (*cur == '-')
        value = -simple_strtoull(++cur, str, 0);    // 负数处理
    else
        value = simple_strtoull(cur, str, 0);       // 正数解析

    if (pint)
        *pint = value;
    if (cur == *str)                               // 没有解析到数字
        return 0;
    if (**str == ',') {                            // 逗号分隔
        (*str)++;
        return 2;
    }
    if (**str == '-')                              // 范围M-N
        return 3;

    return 1;                                       // 正常解析
}
```

**返回值含义**:

| 返回值 | 含义 |
|--------|------|
| 0 | 字符串中没有整数 |
| 1 | 解析到整数,无逗号 |
| 2 | 解析到整数,有逗号跟随 |
| 3 | 发现连字符,表示范围 |

#### 4.2.2 get_options() - 解析整数列表

```c
// lib/cmdline.c, 第107-138行
char *get_options(const char *str, int nints, int *ints)
{
    bool validate = (nints == 0);
    int res, i = 1;

    while (i < nints || validate) {
        int *pint = validate ? ints : ints + i;

        res = get_option((char **)&str, pint);
        if (res == 0)
            break;
        if (res == 3) {                            // 处理范围
            int n = validate ? 0 : nints - i;
            int range_nums;

            range_nums = get_range((char **)&str, pint, n);
            if (range_nums < 0)
                break;
            i += (range_nums - 1);                  // 展开范围
        }
        i++;
        if (res == 1)
            break;                                  // 无逗号,解析结束
    }
    ints[0] = i - 1;                               // 返回解析的数量
    return (char *)str;                            // 返回剩余字符串
}
```

```c
// lib/cmdline.c, 第23-33行 - 范围处理
static int get_range(char **str, int *pint, int n)
{
    int x, inc_counter, upper_range;

    (*str)++;                                        // 跳过 '-'
    upper_range = simple_strtol((*str), NULL, 0);    // 解析范围上限
    inc_counter = upper_range - *pint;               // 计算增量
    for (x = *pint; n && x < upper_range; x++, n--)
        *pint++ = x;                                // 展开范围
    return inc_counter;
}
```

**解析示例**:

```
输入: "1,2,5-8,10"
解析结果:
  ints[0] = 7 (解析了7个数字)
  ints[1] = 1, ints[2] = 2
  ints[3] = 5, ints[4] = 6, ints[5] = 7, ints[6] = 8
  ints[7] = 10
```

#### 4.2.3 parse_option_str() - 检查选项是否存在

```c
// lib/cmdline.c, 第203-220行
bool parse_option_str(const char *str, const char *option)
{
    while (*str) {
        if (!strncmp(str, option, strlen(option))) { // 匹配选项
            str += strlen(option);
            if (!*str || *str == ',')               // 选项后是结束或逗号
                return true;
        }

        while (*str && *str != ',')                 // 跳到下一个选项
            str++;

        if (*str == ',')
            str++;
    }

    return false;
}
```

**使用示例**:

```
parse_option_str("mem=128M console=ttyS0", "mem")  → true
parse_option_str("mem=128M console=ttyS0", "debug") → false
```

#### 4.2.4 memparse() - 解析内存大小

```c
// lib/cmdline.c, 第150-190行
unsigned long long memparse(const char *ptr, char **retptr)
{
    char *endptr;
    unsigned long long ret = simple_strtoull(ptr, &endptr, 0);

    switch (*endptr) {
    case 'E':
    case 'e':
        ret <<= 10;                                 // *= 1024
        fallthrough;
    case 'P':
    case 'p':
        ret <<= 10;
        fallthrough;
    case 'T':
    case 't':
        ret <<= 10;
        fallthrough;
    case 'G':
    case 'g':
        ret <<= 10;
        fallthrough;
    case 'M':
    case 'm':
        ret <<= 10;
        fallthrough;
    case 'K':
    case 'k':
        ret <<= 10;
        endptr++;
        fallthrough;
    default:
        break;
    }

    if (retptr)
        *retptr = endptr;

    return ret;
}
```

**后缀表**:

| 后缀 | 乘数 |
|------|------|
| K/k | 1024 (2^10) |
| M/m | 1024^2 (2^20) |
| G/g | 1024^3 (2^30) |
| T/t | 1024^4 (2^40) |
| P/p | 1024^5 (2^50) |
| E/e | 1024^6 (2^60) |

#### 4.2.5 next_arg() - 解析参数键值对

```c
// lib/cmdline.c, 第227-274行
char *next_arg(char *args, char **param, char **val)
{
    unsigned int i, equals = 0;
    int in_quote = 0, quoted = 0;

    if (*args == '"') {                             // 处理引号
        args++;
        in_quote = 1;
        quoted = 1;
    }

    for (i = 0; args[i]; i++) {
        if (isspace(args[i]) && !in_quote)         // 空格分割
            break;
        if (equals == 0) {
            if (args[i] == '=')
                equals = i;                         // 记录 '=' 位置
        }
        if (args[i] == '"')
            in_quote = !in_quote;                   // 引号配对
    }

    *param = args;
    if (!equals)
        *val = NULL;                                // 无值
    else {
        args[equals] = '\0';
        *val = args + equals + 1;

        if (**val == '"') {                         // 去除值两端的引号
            (*val)++;
            if (args[i-1] == '"')
                args[i-1] = '\0';
        }
    }
    if (quoted && i > 0 && args[i-1] == '"')
        args[i-1] = '\0';

    if (args[i]) {
        args[i] = '\0';
        args += i + 1;
    } else
        args += i;

    return skip_spaces(args);                       // 返回下一参数
}
```

**解析示例**:

```
输入: "mem=128M console=ttyS0 \"key=value\" debug"
解析结果:
  第1次调用: param="mem", val="128M"
  第2次调用: param="console", val="ttyS0"
  第3次调用: param="key", val="value"
  第4次调用: param="debug", val=NULL
```

---

## 5. 其他通用库函数

### 5.1 字符串操作 (string.h)

**源码位置**: `/Users/sphinx/github/linux/include/linux/string.h`, `arch/*/include/asm/string.h`

#### 5.1.1 strscpy() - 安全字符串复制

```c
// include/linux/string.h, 第113-114行
#define strscpy(dst, src, ...) \
    CONCATENATE(__strscpy, COUNT_ARGS(__VA_ARGS__))(dst, src, __VA_ARGS__)
```

**特性**:
- 始终返回有效字符串
- 不强制填充尾部为零
- 返回复制字符数或 `-E2BIG`

#### 5.1.2 strscpy_pad() - 带填充的字符串复制

```c
// include/linux/string.h, 第116-126行
#define sized_strscpy_pad(dest, src, count)   ({         \
    char *__dst = (dest);                                \
    const char *__src = (src);                          \
    const size_t __count = (count);                      \
    ssize_t __wrote;                                    \
                                                        \
    __wrote = sized_strscpy(__dst, __src, __count);     \
    if (__wrote >= 0 && __wrote < __count)               \
        memset(__dst + __wrote + 1, 0, __count - __wrote - 1); \
    __wrote;                                            \
})
```

#### 5.1.3 kstrdup() - 内核字符串复制

```c
// 内核内存分配版本
extern char *kstrdup(const char *s, gfp_t gfp) __malloc;
extern char *kstrndup(const char *s, size_t len, gfp_t gfp);
```

### 5.2 GCD (最大公约数)

**源码位置**: `/Users/sphinx/github/linux/lib/math/gcd.c`

```c
// lib/math/gcd.c, 第50-87行
unsigned long gcd(unsigned long a, unsigned long b)
{
    unsigned long r = a | b;

    if (!a || !b)
        return r;

#if !defined(CONFIG_CPU_NO_EFFICIENT_FFS)
    if (static_branch_likely(&efficient_ffs_key))
        return binary_gcd(a, b);                        // 二进制GCD算法
#endif

    /* 标准欧几里得算法的二进制变体 */
    r &= -r;                                           // 提取最低设置位

    while (!(b & r))
        b >>= 1;
    if (b == r)
        return r;

    for (;;) {
        while (!(a & r))
            a >>= 1;
        if (a == r)
            return r;
        if (a == b)
            return a;

        if (a < b)
            swap(a, b);
        a -= b;
        a >>= 1;
        if (a & r)
            a += b;
        a >>= 1;
    }
}
```

**二进制GCD算法** (binary_gcd):

```c
// lib/math/gcd.c, 第20-39行
static unsigned long binary_gcd(unsigned long a, unsigned long b)
{
    unsigned long r = a | b;

    b >>= __ffs(b);                                    // b除以2的幂
    if (b == 1)
        return r & -r;

    for (;;) {
        a >>= __ffs(a);                                // a除以2的幂
        if (a == 1)
            return r & -r;
        if (a == b)
            return a << __ffs(r);

        if (a < b)
            swap(a, b);
        a -= b;
    }
}
```

**算法复杂度**: O(log(min(a,b)))

### 5.3 倒数除法 (Reciprocal Division)

**源码位置**: `/Users/sphinx/github/linux/lib/math/reciprocal_div.c`, `/Users/sphinx/github/linux/include/linux/reciprocal_div.h`

#### 5.3.1 背景

当除数 `d` 在运行时大多不变时,预先计算 `1/d` 的倒数,然后用乘法替代除法可以显著提升性能。

#### 5.3.2 数据结构

```c
// include/linux/reciprocal_div.h, 第23-26行
struct reciprocal_value {
    u32 m;          // 乘数 (multiplier)
    u8 sh1, sh2;    // 右移量
};
```

#### 5.3.3 倒数计算

```c
// lib/math/reciprocal_div.c, 第17-32行
struct reciprocal_value reciprocal_value(u32 d)
{
    struct reciprocal_value R;
    u64 m;
    int l;

    l = fls(d - 1);                                    // ceil(log2(d))
    m = ((1ULL << 32) * ((1ULL << l) - d));            // 计算乘数
    do_div(m, d);
    ++m;
    R.m = (u32)m;
    R.sh1 = min(l, 1);
    R.sh2 = max(l - 1, 0);

    return R;
}
```

#### 5.3.4 倒数除法运算

```c
// include/linux/reciprocal_div.h, 第33-37行
static inline u32 reciprocal_divide(u32 a, struct reciprocal_value R)
{
    u32 t = (u32)(((u64)a * R.m) >> 32);
    return (t + ((a - t) >> R.sh1)) >> R.sh2;
}
```

**使用示例**:

```c
// 计算 100 / 7
struct reciprocal_value r = reciprocal_value(7);
u32 result = reciprocal_divide(100, r);  // 结果 ≈ 14
```

#### 5.3.5 高级版本

```c
// include/linux/reciprocal_div.h, 第39-43行
struct reciprocal_value_adv {
    u32 m;
    u8 sh, exp;
    bool is_wide_m;
};
```

用于JIT代码生成等场景,可将模拟操作数从6个减少到3-4个。

---

## 附录

### A. 头文件汇总

| 功能 | 头文件 |
|------|--------|
| 位图 | `linux/bitmap.h` |
| 基数树 | `linux/radix-tree.h` |
| IDR | `linux/idr.h` |
| 字符串 | `linux/string.h` |
| GCD | `linux/gcd.h` |
| 倒数除法 | `linux/reciprocal_div.h` |

### B. 宏定义

```c
// 位图相关
#define BITS_TO_LONGS(nbits)  DIV_ROUND_UP(nbits, BITS_PER_LONG)
#define BIT_WORD(index)       (index / BITS_PER_LONG)
#define BITMAP_FIRST_WORD_MASK(start) (~0UL << ((start) & (BITS_PER_LONG - 1)))
#define BITMAP_LAST_WORD_MASK(nbits) (~0UL >> (-(nbits) & (BITS_PER_LONG - 1)))

// 基数树相关
#define RADIX_TREE_MAP_SHIFT  XA_CHUNK_SHIFT        // 通常为6
#define RADIX_TREE_MAP_SIZE   (1UL << RADIX_TREE_MAP_SHIFT)  // 64
#define RADIX_TREE_MAP_MASK   (RADIX_TREE_MAP_SIZE - 1)
#define RADIX_TREE_MAX_TAGS   XA_MAX_MARKS          // 通常为3
```

### C. 同步机制

| 数据结构 | 同步方式 |
|----------|----------|
| 位图 | 无内置同步,需外部锁定 |
| 基数树 | RCU (读), 锁 (写) |
| IDR | 无内置同步,需外部锁定 |
| IDA | 内置xa_lock |
| cmdline | 无状态,线程安全 |

---

*文档生成日期: 2026-04-26*
*Linux内核版本: master分支*
