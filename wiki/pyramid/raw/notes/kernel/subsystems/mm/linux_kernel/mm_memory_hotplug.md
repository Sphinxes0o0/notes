# MM Memory Hotplug

## 1. add_memory 内存添加

### 1.1 add_memory
**文件**: `mm/memory_hotplug.c:3000-3100`

```c
int add_memory(unsigned long start, unsigned long size, int nid, int online_type)
{
    struct memory_block *mem;
    int ret;

    // 验证内存范围
    if (!range_is_valid(start, size))
        return -EINVAL;

    // 分配 memory_block
    mem = register_memory(start, size, nid);
    if (IS_ERR(mem))
        return PTR_ERR(mem);

    // 在线页面
    ret = online_pages(start, size, online_type);
    if (ret)
        unregister_memory(mem);

    return ret;
}
```

### 1.2 __add_memory
**文件**: `mm/memory_hotplug.c:2900-3000`

```c
int __add_memory(unsigned long start, unsigned long size, int nid)
{
    struct pglist_data *pgdat;
    unsigned long start_pfn, end_pfn;
    int ret;

    start_pfn = PFN_DOWN(start);
    end_pfn = PFN_UP(start + size);

    // 获取节点
    pgdat = NODE_DATA(nid);
    if (!pgdat)
        return -EINVAL;

    // 添加内存到节点
    ret = arch_add_memory(pgdat, start, size);
    if (ret)
        return ret;

    // 更新节点信息
    node_set_online(nid);

    // 初始化新内存页面
    deferred_init(pgdat, start_pfn, end_pfn);

    return 0;
}
```

### 1.3 memory_block_online
**文件**: `drivers/base/memory.c:500-600`

```c
static int memory_block_online(struct memory_block *mem)
{
    unsigned long start_pfn = section_nr_to_pfn(mem->start_section_nr);
    unsigned long nr_pages = memory_block_size_bytes() / PAGE_SIZE;
    int ret;

    // 在线页面
    ret = online_pages(start_pfn, nr_pages, MEMOP_ONLINE);
    if (ret)
        return ret;

    // 更新状态
    mem->state = MEM_ONLINE;

    return 0;
}
```

## 2. remove_memory 内存移除

### 2.1 remove_memory
**文件**: `mm/memory_hotplug.c:3200-3300`

```c
int remove_memory(unsigned long start, unsigned long size)
{
    unsigned long start_pfn, end_pfn;
    struct memory_block *mem;
    int ret;

    start_pfn = PFN_DOWN(start);
    end_pfn = PFN_UP(start + size);

    // 查找 memory_block
    mem = find_memory_block(start_pfn);
    if (!mem)
        return -ENODEV;

    // 尝试离线页面
    ret = offline_pages(start_pfn, end_pfn - start_pfn);
    if (ret)
        return ret;

    // 移除内存
    ret = __remove_memory(start, size);
    if (ret)
        return ret;

    // 注销 memory_block
    unregister_memory(mem);

    return 0;
}
```

### 2.2 __remove_memory
**文件**: `mm/memory_hotplug.c:3100-3200`

```c
int __remove_memory(unsigned long start, unsigned long size)
{
    unsigned long start_pfn, end_pfn;

    start_pfn = PFN_DOWN(start);
    end_pfn = PFN_UP(start + size);

    // 检查是否有正在使用的页面
    if (mem_hotplug_begin())
        return -EBUSY;

    // 尝试隔离页面
    ret = isolate_movable_range(start_pfn, end_pfn);
    if (ret)
        goto done;

    // 释放页面到伙伴系统
    __offline_pages(start_pfn, end_pfn);

    // 移除内存区域
    arch_remove_memory(start, size);

    // 更新节点
    node_set_offline(nid);

done:
    mem_hotplug_done();
    return ret;
}
```

## 3. 页面初始化

### 3.1 deferred_init
**文件**: `mm/page_alloc.c:8000-8100`

```c
static int __init deferred_init(void *data)
{
    unsigned long start_pfn = 0, end_pfn = 0;
    struct zone *zone;
    pg_data_t *pgdat;
    int nid;
    unsigned int order;

    // 遍历所有节点
    for_each_online_node(nid) {
        pgdat = NODE_DATA(nid);

        // 初始化 ZONE_NORMAL
        zone = &pgdat->node_zones[ZONE_NORMAL];

        start_pfn = zone->zone_start_pfn;
        end_pfn = zone_end_pfn(zone);

        // 延迟初始化页面
        for (order = 0; order < MAX_ORDER; order++) {
            init_unavailable_range(start_pfn, end_pfn, order);
        }
    }

    return 0;
}
```

### 3.2 init_unavailable_range
**文件**: `mm/page_alloc.c:7900-8000`

```c
static void __init init_unavailable_range(unsigned long start_pfn,
                                          unsigned long end_pfn, int order)
{
    unsigned long pfn;

    for (pfn = start_pfn; pfn < end_pfn; pfn += (1 << order)) {
        struct page *page = pfn_to_page(pfn);

        // 初始化页面
        set_page_links(page, zone, nid, pfn);
        init_page_count(page);
        page_mapcount_reset(page);
        page_cpupid_reset_last(page);

        // 加入伙伴系统
        set_buddy_order(page, order);
    }
}
```

## 4. 页面 online/offline

### 4.1 online_pages
**文件**: `mm/memory_hotplug.c:1500-1700`

```c
int online_pages(unsigned long start_pfn, unsigned long nr_pages,
                  int online_type)
{
    struct zone *zone;
    unsigned long flags;
    int ret;

    // 获取目标区域
    zone = page_zone(pfn_to_page(start_pfn));

    // 获取锁
    write_lock_irqsave(&zone->lock, flags);

    // 初始化页面
    for (pfn = start_pfn; pfn < end_pfn; pfn++) {
        struct page *page = pfn_to_page(pfn);

        // 初始化页面结构
        init_page_contiguous(page);

        // 加入伙伴系统
        free_page_init(zone, page);
    }

    // 更新统计
    zone->present_pages += nr_pages;
    zone->managed_pages += nr_pages;

    write_unlock_irqrestore(&zone->lock, flags);

    // 触发内存通知
    memory_notify(MEM_ONLINE, ...);

    return 0;
}
```

### 4.2 offline_pages
**文件**: `mm/memory_hotplug.c:1700-1900`

```c
int offline_pages(unsigned long start_pfn, unsigned long nr_pages)
{
    struct zone *zone;
    unsigned long pfn, end_pfn;
    int ret;

    zone = page_zone(pfn_to_page(start_pfn));

    // 检查是否可以离线
    if (!can_offline_pages(zone))
        return -EBUSY;

    // 迁移或回收页面
    ret = migrate_pages(start_pfn, nr_pages);
    if (ret)
        return ret;

    // 等待页面稳定
    wait_event(zone->zone_wait_table,
                !has_active_pages(zone));

    // 从伙伴系统移除
    for (pfn = start_pfn; pfn < end_pfn; pfn++) {
        struct page *page = pfn_to_page(pfn);

        // 移除页面
        remove_fromBuddy(page);
    }

    // 更新统计
    zone->present_pages -= nr_pages;
    zone->managed_pages -= nr_pages;

    return 0;
}
```

## 5. memory_block 设备驱动

### 5.1 register_memory
**文件**: `drivers/base/memory.c:200-300`

```c
struct memory_block *register_memory(unsigned long start, unsigned long size, int nid)
{
    struct memory_block *mem;
    int ret;

    mem = kzalloc(sizeof(*mem), GFP_KERNEL);
    if (!mem)
        return ERR_PTR(-ENOMEM);

    mem->start_section_nr = start >> SECTION_SIZE_BITS;
    mem->end_section_nr = (start + size - 1) >> SECTION_SIZE_BITS;
    mem->state = MEM_OFFLINE;
    mem->nid = nid;

    // 添加到系统
    ret = device_register(&mem->dev);
    if (ret) {
        put_device(&mem->dev);
        return ERR_PTR(ret);
    }

    // 添加到内存块链表
    mutex_lock(&mem_sysfs_mutex);
    list_add(&mem->list, &memory_blocks);
    mutex_unlock(&mem_sysfs_mutex);

    return mem;
}
```

### 5.2 memory_block_change_state
**文件**: `drivers/base/memory.c:600-700`

```c
static int memory_block_change_state(struct memory_block *mem,
                                    unsigned long to_state)
{
    int ret;

    switch (to_state) {
    case MEM_ONLINE:
        ret = memory_block_online(mem);
        break;
    case MEM_OFFLINE:
        ret = memory_block_offline(mem);
        break;
    default:
        return -EINVAL;
    }

    if (!ret)
        mem->state = to_state;

    return ret;
}
```

## 6. 节点状态管理

### 6.1 node_set_online
**文件**: `mm/memory_hotplug.c:100-150`

```c
int node_set_online(int nid)
{
    pg_data_t *pgdat = NODE_DATA(nid);
    struct zone *zone;
    enum zone_type z;

    if (node_state(nid, N_ONLINE))
        return 0;

    // 设置节点在线
    node_set(nid, NODE_STATE_ONLINE);

    // 更新区域
    for (z = 0; z < MAX_NR_ZONES; z++) {
        zone = &pgdat->node_zones[z];
        zone->initialized = 1;
    }

    // 重新计算 kswapd 需求
    wakeup_kswapd(zone);

    return 0;
}
```

### 6.2 node_set_offline
**文件**: `mm/memory_hotplug.c:150-200`

```c
int node_set_offline(int nid)
{
    pg_data_t *pgdat = NODE_DATA(nid);

    if (!node_state(nid, N_ONLINE))
        return -EINVAL;

    // 设置节点离线
    node_clear(nid, NODE_STATE_ONLINE);

    // 停止 kswapd
    if (pgdat->kswapd)
        kthread_stop(pgdat->kswapd);

    return 0;
}
```

## 7. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| add_memory | mm/memory_hotplug.c | 3000 |
| __add_memory | mm/memory_hotplug.c | 2900 |
| remove_memory | mm/memory_hotplug.c | 3200 |
| __remove_memory | mm/memory_hotplug.c | 3100 |
| deferred_init | mm/page_alloc.c | 8000 |
| online_pages | mm/memory_hotplug.c | 1500 |
| offline_pages | mm/memory_hotplug.c | 1700 |
| register_memory | drivers/base/memory.c | 200 |
| memory_block_change_state | drivers/base/memory.c | 600 |
