# VFS Buffer Cache

## 1. 模块架构

### 1.1 功能概述

Buffer Cache 是 VFS 用于缓存磁盘块数据的机制。每个缓存的磁盘块称为 buffer_head，它将磁盘块映射到内存页面，提供同步 I/O 操作接口。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/buffer.c` | buffer cache 实现 |
| `include/linux/buffer_head.h` | buffer_head 定义 |
| `mm/page-writeback.c` | 页面回写 |
| `mm/page_io.c` | 页面 I/O |

## 2. 核心数据结构

### 2.1 struct buffer_head

```c
// include/linux/buffer_head.h:200
struct buffer_head {
    unsigned long b_state;              // 状态标志
    struct buffer_head *b_this_page;    // 同页面的其他 buffer
    struct page *b_page;                // 所属页面

    sector_t      b_blocknr;           // 块号
    size_t        b_size;              // 大小
    char          *b_data;             // 数据指针

    struct block_device *b_bdev;       // 块设备
    bh_end_io_t   *b_end_io;           // I/O 完成回调
    void          *b_private;          // 私有数据

    struct list_head b_assoc_buffers;  // 关联缓冲区
    struct address_space *b_assoc_map;  // 关联地址空间
    struct rcu_head b_rcuhead;
};
```

### 2.2 buffer_head 状态标志

```c
// include/linux/buffer_head.h:50
enum bh_state_bits {
    BH_Uptodate,       // 数据是最新的
    BH_Dirty,          // 数据是脏的
    BH_Lock,           // 正在 I/O
    BH_Req,            // 已被请求
    BH_Mapped,         // 已映射到磁盘
    BH_New,            // 新分配的
    BH_Async_Read,     // 异步读取
    BH_Async_Write,    // 异步写入
    BH_Delay,          // 延迟分配
    BH_Boundary,       // 块边界
    BH_Write_Error,    // 写错误
    BH_Ordered,        // 有序写
    BH_Eopnotsupp,     // 操作不支持
    BH_Unwritten,      // 未写入的extent
    BH_Quiet,          // 静默错误
};
```

## 3. Buffer Cache 查找

### 3.1 find_bh()

```c
// fs/buffer.c:100
struct buffer_head *find_bh(struct block_device *bdev,
                            sector_t blocknr)
{
    struct buffer_head *bh;

    spin_lock(&bdev->bd_bh_lock);
    list_for_each_entry(bh, &bdev->bd_bhs, b_bhs) {
        if (bh->b_blocknr == blocknr) {
            get_bh(bh);
            spin_unlock(&bdev->bd_bh_lock);
            return bh;
        }
    }
    spin_unlock(&bdev->bd_bh_lock);
    return NULL;
}
```

### 3.2 __find_get_block()

```c
// fs/buffer.c:150
struct buffer_head *__find_get_block(struct block_device *bdev,
                                     sector_t blocknr,
                                     unsigned size)
{
    struct buffer_head *bh;

    // 查找哈希表
    bh = lookup_bh(bdev, blocknr);
    if (bh) {
        // 检查大小是否匹配
        if (bh->b_size == size) {
            get_bh(bh);
            return bh;
        }
        // 大小不匹配，释放并返回 NULL
        put_bh(bh);
    }

    return NULL;
}
```

### 3.3 __getblk()

```c
// fs/buffer.c:300
struct buffer_head *__getblk(struct block_device *bdev,
                            sector_t blocknr,
                            unsigned size)
{
    struct buffer_head *bh;

    might_sleep();

    // 查找或分配 buffer_head
    bh = __find_get_block(bdev, blocknr, size);
    if (bh)
        return bh;

    // 分配新的 buffer_head
    bh = alloc_buffer_head(GFP_NOFS);
    if (!bh)
        return NULL;

    // 初始化
    bh->b_bdev = bdev;
    bh->b_blocknr = blocknr;
    bh->b_size = size;

    // 加入哈希表
    insert_into_bh_hash(bh);

    return bh;
}
```

## 4. Buffer I/O

### 4.1 sync_dirty_buffer()

```c
// fs/buffer.c:400
int sync_dirty_buffer(struct buffer_head *bh)
{
    int ret;

    WARN_ON(!buffer_dirty(bh));

    get_bh(bh);
    bh->b_end_io = end_buffer_write_sync;
    ret = submit_bh(WRITE, bh);
    wait_on_buffer(bh);

    if (buffer_write_io_error(bh))
        ret = -EIO;

    return ret;
}
```

### 4.2 submit_bh()

```c
// fs/buffer.c:500
int submit_bh(int op, struct buffer_head *bh)
{
    struct bio *bio;

    // 创建 bio
    bio = bio_alloc(bh->b_bdev, 1);
    bio->bi_iter.bi_sector = bh->b_blocknr * (bh->b_size >> 9);
    bio->bi_end_io = end_bio_bh_io_sync;

    // 添加 buffer 到 bio
    bio_add_page(bio, bh->b_page, bh->b_size, bh_offset(bh));

    // 提交 I/O
    submit_bio(bio);

    return 0;
}
```

### 4.3 end_buffer_write_sync()

```c
// fs/buffer.c:450
static void end_buffer_write_sync(struct buffer_head *bh, int uptodate)
{
    if (uptodate) {
        set_buffer_uptodate(bh);
    } else {
        buffer_io_error(bh);
        set_bit(BH_Write_Error, &bh->b_state);
    }

    // 唤醒等待者
    wake_up_buffer(bh);
}
```

## 5. 页面与 Buffer 关系

### 5.1 attach_nth_page()

```c
// fs/buffer.c:600
int attach_nth_page(struct buffer_head *bh, struct page *page)
{
    struct buffer_head **bhp = &page->b_page_buffers;

    if (!page->b_page_buffers)
        init_page_buffers(page, bh->b_bdev, bh->b_blocknr, bh->b_size);

    // 找到插入位置
    while (*bhp) {
        if ((*bhp)->b_this_page == bh)
            return 0;
        bhp = &(*bhp)->b_this_page;
    }

    // 链接到页面
    bh->b_this_page = page->b_page_buffers;
    page->b_page_buffers = bh;
    return 0;
}
```

### 5.2 init_page_buffers()

```c
// fs/buffer.c:550
static void init_page_buffers(struct page *page,
                             struct block_device *bdev,
                             sector_t blocknr,
                             int size)
{
    struct buffer_head *bh = page_buffers(page);
    struct buffer_head *head = bh;
    int blocksize = 1 << (PAGE_SHIFT + 1);

    do {
        bh->b_bdev = bdev;
        bh->b_blocknr = blocknr++;
        bh->b_size = size;
        bh->b_data = page_address(page) + (bh - head) * blocksize;
        bh->b_this_page = head;
    } while ((bh = bh->b_this_page) != head);
}
```

## 6. Buffer 写回

### 6.1 write_dirty_buffer()

```c
// fs/buffer.c:650
int write_dirty_buffer(struct buffer_head *bh, int submit)
{
    if (!buffer_dirty(bh))
        return 0;

    lock_buffer(bh);
    if (test_clear_buffer_dirty(bh)) {
        get_bh(bh);
        if (submit)
            submit_bh(WRITE, bh);
        else
            write_boundary_buffer(bh);
        return 0;
    }
    unlock_buffer(bh);
    return 1;
}
```

### 6.2 __sync_dirty_buffers()

```c
// fs/buffer.c:800
static int __sync_dirty_buffers(struct address_space *mapping)
{
    struct buffer_head *bh, *head;
    struct page *page;

    page = list_first_entry(&mapping->i_pages, struct page, lru);

    do {
        head = page_buffers(page);
        bh = head;
        do {
            if (!buffer_dirty(bh))
                continue;
            if (!trylock_buffer(bh))
                continue;
            write_dirty_buffer(bh, 1);
        } while ((bh = bh->b_this_page) != head);
    } while ((page = list_next_entry(page, lru)) != head);
}
```

## 7. Buffer LRU

### 7.1 bh_lru_install()

```c
// fs/buffer.c:200
static void bh_lru_install(struct buffer_head *bh)
{
    struct buffer_head **bhp = this_cpu_ptr(&bh_lrus);

    // 移出旧的
    if (*bhp)
        put_bh(*bhp);

    // 安装新的
    *bhp = bh;
    get_bh(bh);
}
```

### 7.2 bh_lru_lookup()

```c
// fs/buffer.c:250
struct buffer_head *bh_lru_lookup(struct block_device *bdev,
                                  sector_t block)
{
    struct buffer_head **bhp = this_cpu_ptr(&bh_lrus);
    struct buffer_head *bh = *bhp;

    if (bh && bh->b_bdev == bdev && bh->b_blocknr == block)
        return bh;

    return NULL;
}
```

## 8. 块设备接口

### 8.1 sb_bread()

```c
// fs/buffer.c:900
struct buffer_head *sb_bread(struct super_block *sb, sector_t block)
{
    struct buffer_head *bh;

    bh = __getblk(sb->s_bdev, block, sb->s_blocksize);
    if (!bh)
        return NULL;

    if (buffer_uptodate(bh))
        return bh;

    ll_rw_block(READ, 1, &bh);
    wait_on_buffer(bh);
    if (buffer_uptodate(bh))
        return bh;

    brelse(bh);
    return NULL;
}
```

### 8.2 sb_getblk()

```c
// fs/buffer.c:850
struct buffer_head *sb_getblk(struct super_block *sb, sector_t block)
{
    return __getblk(sb->s_bdev, block, sb->s_blocksize);
}
```

## 9. Buffer 与 Page Cache 整合

### 9.1 mark_buffer_dirty()

```c
// fs/buffer.c:700
void mark_buffer_dirty(struct buffer_head *bh)
{
    if (!buffer_dirty(bh)) {
        set_buffer_dirty(bh);
        if (!test_set_buffer_dirty(bh))
            __set_page_dirty_buffers(bh->b_page);
    }
}
```

### 9.2 __set_page_dirty_buffers()

```c
// fs/buffer.c:750
static void __set_page_dirty_buffers(struct page *page)
{
    struct buffer_head *bh = page_buffers(page);

    do {
        struct address_space *mapping = page_mapping(page);
        if (mapping)
            account_page_dirtied(page, mapping);
        set_buffer_dirty(bh);
    } while ((bh = bh->b_this_page) != page_buffers(page));
}
```

## 10. Buffer 操作流程图

```
读操作:
+----------------+
| __getblk()    |
+----------------+
        |
        v
+----------------+
| 查找 buffer   |----> 存在?
|   hash 表     |
+----------------+
        |
   不存在
        |
        v
+----------------+
| alloc_buffer   |
|     _head()    |
+----------------+
        |
        v
+----------------+
| 插入 hash 表   |
+----------------+
        |
        v
+----------------+
| ll_rw_block() |-----> 提交 bio
+----------------+
        |
        v
+----------------+
|wait_on_buffer()|
+----------------+
        |
        v
+----------------+
|  返回 buffer   |
+----------------+

写操作:
+----------------+
| mark_buffer   |
|    _dirty()   |
+----------------+
        |
        v
+----------------+
| set BH_Dirty  |
+----------------+
        |
        v
+----------------+
| __set_page    |
| _dirty_buffers|
+----------------+
        |
        v
+----------------+
| write_dirty   |
|   _buffer()    |
+----------------+
        |
        v
+----------------+
| submit_bh()   |
+----------------+
        |
        v
+----------------+
|  I/O 完成回调 |
+----------------+
```

## 11. 常用宏

```c
// 状态检查
#define buffer_uptodate(bh)    test_bit(BH_Uptodate, &(bh)->b_state)
#define buffer_dirty(bh)       test_bit(BH_Dirty, &(bh)->b_state)
#define buffer_locked(bh)      test_bit(BH_Lock, &(bh)->b_state)
#define buffer_mapped(bh)      test_bit(BH_Mapped, &(bh)->b_state)

// 状态设置
#define set_buffer_uptodate(bh)    set_bit(BH_Uptodate, &(bh)->b_state)
#define set_buffer_dirty(bh)      set_bit(BH_Dirty, &(bh)->b_state)
#define clear_buffer_dirty(bh)    clear_bit(BH_Dirty, &(bh)->b_state)

// 引用计数
#define get_bh(bh)    atomic_inc(&(bh)->b_count)
#define put_bh(bh)    atomic_dec(&(bh)->b_count)
```
