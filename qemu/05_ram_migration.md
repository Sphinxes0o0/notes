---
title: RAM 迁移
---

# RAM 迁移分析

## Precopy 迁移

```c
// migration/ram.c
struct RAMState {
    PageSearchStatus pss[RAM_CHANNEL_MAX]; // 每通道页搜索状态
    uint64_t migration_dirty_pages;        // 剩余脏页数
    bool xbzrle_started;                  // XBZRLE 激活标志
    RAMBlock *last_seen_block;            // 上次看到的块
    ram_addr_t last_page;                 // 上次页面
};

// RAM_CHANNEL_MAX = 2: precopy + postcopy
```

### 脏位图管理

```c
// 每个 RAMBlock 的脏位图
block->bmap

// 延迟清除的 clear_bmap
clear_bitmap_shift

// 同步函数
migration_bitmap_sync()
```

### 页面保存流程

```
ram_find_and_save_block()      // 搜索脏页
  → ram_save_host_page()       // 处理主机页边界
    → ram_save_target_page()   // 路由到 XBZRLE/零页/普通
```

## Postcopy 迁移

```c
// migration/postcopy-ram.c

// 三个阶段
typedef enum {
    POSTCOPY_ADVISE,            // 协商页大小兼容性
    POSTCOPY_LISTEN,            // 设置 userfaultfd
    POSTCOPY_RUN,               // 目标运行，源传输剩余页
} PostcopyState;
```

### Userfaultfd (UFFD)

```c
// Linux 内核机制，处理缺失页
ram_write_tracking_start()     // 启用写保护跟踪
ram_write_tracking_stop()       // 停止跟踪

// VM 故障时通过返回路径请求页
```

## XBZRLE 压缩

```c
// migration/page_cache.c
struct PageCache {
    uint64_t *page_hash;        // 页哈希
    uint8_t *cached_pages;     // 缓存页
    uint16_t *page_age;         // 页年龄
    int64_t nb_cached;          // 缓存页数
};

#define CACHED_PAGE_LIFETIME 2  // 2 个周期内不替换
```

### XBZRLE 编码

```c
xbzrle_encode_buffer()         // 差分压缩
cache_insert()                 // 更新缓存
cache_is_cached()              // 检查缓存
xbzrle_cache_zero_page()       // 零页特殊处理
```

## 内存后端迁移

```c
struct RAMBlock {
    void *host;                 // 主机地址
    ram_addr_t used_length;    // 使用长度
    int fd;                     // 内存文件描述符
};

// 接收端跟踪
receivedmap                     // 接收页位图
ramblock_recv_bitmap_*()       // 接收位图管理
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `ram.c` | RAM 迁移主逻辑 |
| `postcopy-ram.c` | Postcopy 实现 |
| `page_cache.c` | XBZRLE 缓存 |
| `xbzrle.h` | XBZRLE 接口 |
