# Linux 内核 Block GenHD 与 Partition 分析

## 1. GenHD 概述

gendisk 是整个块设备子系统的核心结构，代表一个物理或虚拟磁盘设备。它包含分区表信息，并关联到具体的请求队列。

---

## 2. struct gendisk 详解

**文件**: `include/linux/blkdev.h:144-225`

```c
struct gendisk {
    int			major;           // 主设备号
    int			first_minor;     // 首个次设备号
    int			minors;          // 次设备号数量 (分区数)

    char			disk_name[DISK_NAME_LEN];  // 设备名 (如 "sda")

    struct xarray		part_tbl;       // 分区表 (xa_array)
    struct block_device	*part0;          // 整个磁盘的 block_device

    const struct block_device_operations *fops;  // 块设备操作
    struct request_queue	*queue;         // 请求队列

    void			*private_data;   // 私有数据

    int			flags;           // 标志
#define GD_NEED_PART_SCAN	0
#define GD_READ_ONLY		1
#define GD_DEAD			2

    struct mutex		open_mutex;     // 打开互斥锁
    unsigned		open_partitions; // 打开的分区数

    struct backing_dev_info	*bdi;          // 回写设备信息
    struct timer_rand_state	*random;       // 随机状态
    struct disk_events	*ev;            // 磁盘事件

    int			node_id;         // NUMA 节点 ID
    struct badblocks	*bb;            // 坏块列表
};
```

---

## 3. Block Device 操作

### 3.1 struct block_device_operations

**文件**: `include/linux/blkdev.h:180-260`

```c
struct block_device_operations {
    int (*open)(struct block_device *, fmode_t);
    void (*release)(struct gendisk *, fmode_t);
    int (*ioctl)(struct block_device *, fmode_t, unsigned, unsigned long);
    int (*compat_ioctl)(struct block_device *, fmode_t, unsigned,
                        unsigned long);
    unsigned int (*check_events)(struct disk_events *, unsigned int);

    // 媒体变更
    int (*media_changed)(struct gendisk *);
    void (*unlock_native_capacity)(struct gendisk *);

    // 重新读取分区表
    int (*revalidate_disk)(struct gendisk *);

    // 电源管理
    int (*getgeo)(struct block_device *, hd_geometry *);

    void (*swap_slot_free_notify)(struct block_device *, unsigned int);

    struct module *owner;
};
```

---

## 4. 分区结构

### 4.1 struct partition_meta_info

**文件**: `include/linux/blkdev.h:95-120`

```c
struct partition_meta_info {
    char uuid[36];                // GPT UUID 或其他标识
    u8 mac_name[256];            // MAC 地址名称 (用于 DM)
    struct label_uuid {
        __u8 uuid[16];
    } uuid_record;
};
```

### 4.2 hd_geometry - 几何信息

**文件**: `include/uapi/linux/hdreg.h:80-95`

```c
struct hd_geometry {
    unsigned char heads;          // 磁头数
    unsigned char sectors;        // 每磁道扇区数
    unsigned short cylinders;     // 柱面数
    unsigned long start;          // 起始扇区
};
```

---

## 5. 磁盘分配与注册

### 5.1 alloc_disk() - 分配磁盘

**文件**: `block/genhd.c:650-690`

```c
struct gendisk *alloc_disk(int minors)
{
    struct gendisk *disk;

    disk = kzalloc(sizeof(struct gendisk), GFP_KERNEL);
    if (!disk)
        return NULL;

    disk->minors = minors;
    INIT_RADIX_TREE(&disk->part_tbl, GFP_KERNEL);
    disk->part0 = bdev_alloc(disk, 0);
    if (!disk->part0) {
        kfree(disk);
        return NULL;
    }

    mutex_init(&disk->open_mutex);
    disk->random = alloc_timer_rand();
    disk->ev = disk_event_init(disk);

    return disk;
}
```

### 5.2 device_add_disk() - 添加磁盘到系统

**文件**: `block/genhd.c:700-780`

```c
int device_add_disk(struct device *parent, struct gendisk *disk,
                   struct attribute_group **groups)
{
    struct request_queue *q;

    // 分配设备号
    disk->major = register_blkdev(disk->major, disk->disk_name);
    if (disk->major < 0)
        return -EBUSY;

    // 初始化分区表
    xa_init_flags(&disk->part_tbl, XA_FLAGS_LOCK_IRQ);

    // 设置设备
    disk->part0->bd_start_sect = 0;
    disk->part0->bd_disk = disk;

    // 添加到设备模型
    device_add_disk(parent, disk, groups);

    // 扫描分区
    if (disk->flags & GD_NEED_PART_SCAN)
        rescan_partitions(disk, disk->part0);

    return 0;
}
```

### 5.3 del_gendisk() - 删除磁盘

**file**: `block/genhd.c:800-850`

```c
void del_gendisk(struct gendisk *disk)
{
    // 删除所有分区
    invalidate_partition(disk, 0);
    del_gendisk(disk);

    // 注销设备号
    unregister_blkdev(disk->major, disk->disk_name);

    // 清理资源
    disk_event_free(disk);
    free_timer_rand(disk->random);
}
```

---

## 6. 分区操作

### 6.1 add_partition() - 添加分区

**文件**: `block/partitions/core.c:100-200`

```c
int add_partition(struct gendisk *disk, int partno,
                 sector_t start, sector_t len,
                 int state, struct partition_meta_info *info)
{
    struct block_device *bdev;

    // 分配 block_device
    bdev = bdev_alloc(disk, partno);
    if (IS_ERR(bdev))
        return PTR_ERR(bdev);

    // 设置分区信息
    bdev->bd_start_sect = start;
    bdev->bd_nr_sectors = len;
    bdev->bd_partno = partno;

    // 加入分区表
    if (xa_insert(&disk->part_tbl, partno, bdev, GFP_KERNEL))
        return -ENOMEM;

    // 设置设备号
    bdev->bd_dev = MKDEV(disk->major, disk->first_minor + partno);

    // 创建设备节点
    device_add_partition(disk, bdev);

    return 0;
}
```

### 6.2 delete_partition() - 删除分区

**文件**: `block/partitions/core.c:200-250`

```c
void delete_partition(struct gendisk *disk, int partno)
{
    struct block_device *bdev;

    bdev = xa_load(&disk->part_tbl, partno);
    if (!bdev)
        return;

    // 移除设备节点
    device_del_partition(disk, bdev);

    // 从分区表移除
    xa_erase(&disk->part_tbl, partno);

    // 释放 block_device
    bdev_free(bdev);
}
```

---

## 7. 分区表扫描

### 7.1 rescan_partitions() - 重新扫描分区

**文件**: `block/partitions/core.c:300-400`

```c
void rescan_partitions(struct gendisk *disk, struct block_device *bdev)
{
    struct parsed_partitions *state;

    state = check_partition(disk, bdev);
    if (!state)
        return;

    // 删除旧分区
    invalidate_partition(disk, 0);

    // 解析新分区
    if (state->present) {
        for (int i = 0; i < state->limit; i++) {
            if (state->parts[i].size)
                add_partition(disk, i,
                    state->parts[i].start,
                    state->parts[i].size,
                    state->parts[i].flags,
                    &state->parts[i].info);
        }
    }

    free_partitions(state);
}
```

### 7.2 check_partition() - 检查分区表

**文件**: `block/partitions/check.c:50-100`

```c
struct parsed_partitions *check_partition(struct gendisk *disk,
        struct block_device *bdev)
{
    struct parsed_partitions *state;
    int ret = -1;

    state = kzalloc(sizeof(*state), GFP_KERNEL);

    // 尝试各类型分区解析器
    if (IS_ENABLED(CONFIG_MSDOS_PARTITION) && bdev->bd_partno == 0) {
        if (msdos_partition(state, bdev) == 0)
            ret = 0;
    }

    if (IS_ENABLED(CONFIG_GPT_PARTITION) && bdev->bd_partno == 0) {
        if (gpt_partition(state, bdev) == 0)
            ret = 0;
    }

    if (ret < 0)
        goto out;

    return state;

out:
    kfree(state);
    return NULL;
}
```

---

## 8. MSDOS 分区表解析

### 8.1 msdos_partition() - MSDOS/MBR 分区解析

**文件**: `block/partitions/msdos.c:50-150`

```c
int msdos_partition(struct parsed_partitions *state,
                    struct block_device *bdev)
{
    struct msdos_partition *p;
    sector_t offset = 0;
    Sector sect;
    unsigned char *data;

    // 读取 MBR
    data = read_part_sector(bdev, 0, &sect);
    if (!data)
        return -1;

    // 检查有效性
    if (data[510] != 0x55 || data[511] != 0xAA)
        goto done;

    p = (struct msdos_partition *)(data + 0xBE);

    for (int i = 0; i < 4; i++) {
        if (p[i].sys_type == 0)  // 空分区
            continue;

        state->parts[i + 1].start = start_sect(p[i]);
        state->parts[i + 1].size = nsec(p[i]);
        state->parts[i + 1].flags = 0;

        // 检查是否需要读取 EBR
        if (p[i].sys_type == 0x05) {  // 扩展分区
            offset = start_sect(p[i]);
            // 处理逻辑分区
        }
    }

done:
    put_part_sector(sect);
    return 0;
}
```

---

## 9. GPT 分区表解析

### 9.1 gpt_partition() - GPT 分区解析

**文件**: `block/partitions/efi.c:100-200`

```c
int gpt_partition(struct parsed_partitions *state,
                  struct block_device *bdev)
{
    struct gpt_header *gpt;
    struct gpt_entry *entry;
    sector_t offset = 1;  // GPT LBA 1

    // 读取 GPT 头
    gpt = read_gpt_header(bdev);
    if (!gpt)
        return -1;

    // 读取分区表
    entry = read_entries(bdev, gpt->partition_entry_lba,
                          gpt->num_partitions);

    for (int i = 0; i < gpt->num_partitions; i++) {
        if (is_empty(&entry[i]))
            continue;

        state->parts[i + 1].start = le64_to_cpu(entry[i].starting_lba);
        state->parts[i + 1].size = le64_to_cpu(entry[i].ending_lba)
                                   - le64_to_cpu(entry[i].starting_lba) + 1;

        // 复制 UUID
        memcpy(state->parts[i + 1].info.uuid,
               entry[i].unique_partition_guid.b, 16);
    }

    return 0;
}
```

---

## 10. 数据结构关系图

```
gendisk
  ├── major / first_minor / minors
  ├── part_tbl (xa_array) ──► block_device[]
  │     ├── part0 ──► 整个磁盘
  │     └── part1-N ──► 各分区
  ├── queue ──► request_queue
  ├── fops ──► block_device_operations
  └── part0 ◄── bd_disk ──► 分区反向引用

block_device
  ├── bd_start_sect ── 起始扇区
  ├── bd_nr_sectors ── 扇区数
  ├── bd_disk ──► 所属 gendisk
  ├── bd_partno ── 分区号 (0=整个磁盘)
  └── bd_dev ── 设备号 (MAJOR:MINOR)
```

---

## 11. 关键源码位置

| 函数/结构 | 文件 | 行号 |
|----------|------|------|
| struct gendisk | include/linux/blkdev.h | 144-225 |
| struct block_device_operations | include/linux/blkdev.h | 180-260 |
| struct partition_meta_info | include/linux/blkdev.h | 95-120 |
| alloc_disk | block/genhd.c | 650-690 |
| device_add_disk | block/genhd.c | 700-780 |
| del_gendisk | block/genhd.c | 800-850 |
| add_partition | block/partitions/core.c | 100-200 |
| delete_partition | block/partitions/core.c | 200-250 |
| rescan_partitions | block/partitions/core.c | 300-400 |
| check_partition | block/partitions/check.c | 50-100 |
| msdos_partition | block/partitions/msdos.c | 50-150 |
| gpt_partition | block/partitions/efi.c | 100-200 |
