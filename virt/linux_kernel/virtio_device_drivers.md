# Linux 内核 Virtio 设备驱动深入分析

## 目录

1. [Virtio 框架概述](#1-virtio-框架概述)
2. [Virtio Block 驱动 (virtio_blk.c)](#2-virtio-block-驱动-virtio_blkc)
3. [Virtio Net 驱动 (virtio_net.c)](#3-virtio-net-驱动-virtio_netc)
4. [Virtio Console 驱动 (virtio_console.c)](#4-virtio-console-驱动-virtio_consolec)
5. [Virtio SCSI 驱动 (virtio_scsi.c)](#5-virtio-scsi-驱动-virtio_scsic)
6. [Virtio Balloon 驱动 (virtio_balloon.c)](#6-virtio-balloon-驱动-virtio_balloonc)
7. [Virtio GPU 驱动 (virtio_gpu)](#7-virtio-gpu-驱动-virtio_gpu)
8. [通用驱动框架分析](#8-通用驱动框架分析)
9. [总结](#9-总结)

---

## 1. Virtio 框架概述

Virtio 是 Linux 内核中用于虚拟化环境的半虚拟化设备接口规范。它允许Guest虚拟机无需模拟真实硬件，通过共享内存队列(virtqueue)与宿主机(Hypervisor)高效通信。

### 1.1 核心数据结构

```c
// include/linux/virtio.h
struct virtqueue {
    struct virtqueue_ops *ops;    // 操作函数集
    struct virtio_device *vdev;   // 所属设备
    unsigned int index;          // 队列索引
    unsigned int num_free;       // 可用缓冲区数量
    void *priv;                  // 私有数据
};
```

### 1.2 Virtqueue 工作原理

Virtqueue 是 Virtio 驱动的核心，包含三个关键操作：

| 操作 | 描述 |
|------|------|
| `add_buf` | 添加缓冲区到 virtqueue |
| `kick` | 通知宿主机有新数据 |
| `get_buf` | 获取宿主机处理完的缓冲区 |

---

## 2. Virtio Block 驱动 (virtio_blk.c)

**文件路径**: `/Users/sphinx/github/linux/drivers/block/virtio_blk.c`

### 2.1 设备结构体

```c
// 第 49-86 行
struct virtio_blk_vq {
    struct virtqueue *vq;        // Virtqueue 指针
    spinlock_t lock;             // 自旋锁保护
    char name[VQ_NAME_LEN];      // 队列名称
} ____cacheline_aligned_in_smp;

struct virtio_blk {
    struct mutex vdev_mutex;     // 保护设备访问
    struct virtio_device *vdev;  // Virtio 设备
    struct gendisk *disk;       // 块设备磁盘
    struct blk_mq_tag_set tag_set; // BLK-MQ 标签集
    struct work_struct config_work; // 配置更新工作
    int index;                   // 设备索引
    int num_vqs;                 // Virtqueue 数量
    int io_queues[HCTX_MAX_TYPES]; // IO 队列类型
    struct virtio_blk_vq *vqs;   // Virtqueue 数组
    unsigned int zone_sectors;   // 区域大小(分区设备)
};
```

### 2.2 请求结构体

```c
// 第 88-111 行
struct virtblk_req {
    struct virtio_blk_outhdr out_hdr;  // 输出头(请求参数)
    union {
        u8 status;                     // 状态字节
        struct {
            __virtio64 sector;        // 区域追加的扇区号
            u8 status;
        } zone_append;
    } in_hdr;
    size_t in_hdr_len;
    struct sg_table sg_table;          // 散列表
    struct scatterlist sg[];            // 散列表元素
};
```

### 2.3 特征位协商

```c
// 第 1659-1673 行
static unsigned int features_legacy[] = {
    VIRTIO_BLK_F_SEG_MAX, VIRTIO_BLK_F_SIZE_MAX, VIRTIO_BLK_F_GEOMETRY,
    VIRTIO_BLK_F_RO, VIRTIO_BLK_F_BLK_SIZE,
    VIRTIO_BLK_F_FLUSH, VIRTIO_BLK_F_TOPOLOGY, VIRTIO_BLK_F_CONFIG_WCE,
    VIRTIO_BLK_F_MQ, VIRTIO_BLK_F_DISCARD, VIRTIO_BLK_F_WRITE_ZEROES,
    VIRTIO_BLK_F_SECURE_ERASE,
};

static unsigned int features[] = {
    VIRTIO_BLK_F_SEG_MAX, VIRTIO_BLK_F_SIZE_MAX, VIRTIO_BLK_F_GEOMETRY,
    VIRTIO_BLK_F_RO, VIRTIO_BLK_F_BLK_SIZE,
    VIRTIO_BLK_F_FLUSH, VIRTIO_BLK_F_TOPOLOGY, VIRTIO_BLK_F_CONFIG_WCE,
    VIRTIO_BLK_F_MQ, VIRTIO_BLK_F_DISCARD, VIRTIO_BLK_F_WRITE_ZEROES,
    VIRTIO_BLK_F_SECURE_ERASE, VIRTIO_BLK_F_ZONED,  // 新增 ZONED 支持
};
```

**主要特征位说明**:

| 特征位 | 描述 |
|--------|------|
| `VIRTIO_BLK_F_RO` | 设备只读 |
| `VIRTIO_BLK_F_BLK_SIZE` | 支持块大小配置 |
| `VIRTIO_BLK_F_FLUSH` | 支持 FLUSH 命令 |
| `VIRTIO_BLK_F_MQ` | 支持多队列 |
| `VIRTIO_BLK_F_DISCARD` | 支持 DISCARD 命令 |
| `VIRTIO_BLK_F_WRITE_ZEROES` | 支持写零操作 |
| `VIRTIO_BLK_F_ZONED` | 支持分区块设备(ZBC) |

### 2.4 请求处理流程

```
virtio_queue_rq()                    // 块层请求入口 (第426行)
    |
    +-- virtblk_prep_rq()            // 准备请求
    |       |
    |       +-- virtblk_setup_cmd()  // 设置命令类型 (READ/WRITE/DISCARD等)
    |       +-- virtblk_map_data()   // 映射数据到散列表
    |
    +-- virtblk_add_req()            // 添加请求到virtqueue (第139行)
    |       |
    |       +-- sg_init_one()        // 初始化散列表
    |       +-- virtqueue_add_sgs()  // 添加到virtqueue
    |
    +-- virtqueue_kick()             // 通知宿主机
```

### 2.5 读写请求结构体

Virtio Block 请求由三部分组成：

```
+------------------+     +------------------+     +--------------+
|  out_hdr (24B)  | --> |  data (可变)     | --> |  status (1B) |
|  virtio_blk_outhdr|     |  读/写数据       |     |  返回状态     |
+------------------+     +------------------+     +--------------+
```

```c
// include/uapi/linux/virtio_blk.h
struct virtio_blk_outhdr {
    __virtio32 type;     // 请求类型 (READ=0, WRITE=1, etc.)
    __virtio32 ioprio;   // IO优先级
    __virtio64 sector;   // 起始扇区号
};
```

### 2.6 Probe/Remove 流程

```c
// 第1436-1560 行: virtblk_probe()
virtblk_probe(struct virtio_device *vdev)
{
    // 1. 分配virtio_blk结构
    vblk = kmalloc(...);

    // 2. 初始化virtqueue (第958行 init_vq)
    init_vq(vblk)
        // - 获取队列数量 (MQ特性)
        // - 分配vqs数组
        // - 调用virtio_find_vqs()创建队列

    // 3. 创建BLK-MQ标签集
    blk_mq_alloc_tag_set(&vblk->tag_set);

    // 4. 读取设备限制
    virtblk_read_limits(vblk, &lim);

    // 5. 分配gendisk
    vblk->disk = blk_mq_alloc_disk(&vblk->tag_set, &lim, vblk);

    // 6. 注册块设备
    device_add_disk(&vdev->dev, vblk->disk, ...);

    // 7. 标记设备就绪
    virtio_device_ready(vdev);
}

// 第1562-1586 行: virtblk_remove()
virtblk_remove(struct virtio_device *vdev)
{
    // 1. 刷新配置工作
    flush_work(&vblk->config_work);

    // 2. 删除gendisk
    del_gendisk(vblk->disk);
    blk_mq_free_tag_set(&vblk->tag_set);

    // 3. 重置设备
    virtio_reset_device(vdev);
    vblk->vdev = NULL;

    // 4. 删除virtqueue
    vdev->config->del_vqs(vdev);
}
```

### 2.7 架构图

```
+------------------+     +------------------+     +------------------+
|   Block Layer    | --> |   virtio_blk     | --> |  virtqueue       |
|   (bio/request)   |     |   driver        |     |  (shared memory)  |
+------------------+     +------------------+     +------------------+
                               |                           |
                               v                           v
                        +------------------+     +------------------+
                        |  virtio_blk      |     |   Hypervisor     |
                        |  _outhdr + data  | --> |   (QEMU/VBox)    |
                        +------------------+     +------------------+
```

---

## 3. Virtio Net 驱动 (virtio_net.c)

**文件路径**: `/Users/sphinx/github/linux/drivers/net/virtio_net.c`

### 3.1 设备结构体

```c
// 第390-489 行
struct virtnet_info {
    struct virtio_device *vdev;        // Virtio设备
    struct virtqueue *cvq;              // 控制virtqueue
    struct net_device *dev;             // 网络设备
    struct send_queue *sq;              // 发送队列数组
    struct receive_queue *rq;            // 接收队列数组
    unsigned int status;

    u16 max_queue_pairs;               // 最大队列对数
    u16 curr_queue_pairs;              // 当前使用队列对数
    u16 xdp_queue_pairs;               // XDP队列对数
    bool xdp_enabled;                  // XDP是否启用

    bool big_packets;                   // 大数据包模式
    unsigned int big_packets_num_skbfrags; // skb_frag数量
    bool mergeable_rx_bufs;            // 合并接收缓冲区

    bool has_rss;                      // RSS支持
    bool has_cvq;                      // 控制队列存在
    struct mutex cvq_lock;              // 控制队列锁
    bool any_header_sg;                // 头部分离

    u8 hdr_len;                        // Virtio头长度
    unsigned long guest_offloads;       // Guest卸载特性

    struct control_buf *ctrl;           // 控制缓冲区
    struct work_struct config_work;     // 配置工作
    struct work_struct rx_mode_work;    // RX模式工作
};
```

### 3.2 发送队列结构体

```c
// 第301-324 行
struct send_queue {
    struct virtqueue *vq;              // Virtqueue指针
    struct scatterlist sg[MAX_SKB_FRAGS + 2]; // 散列表(片段+头)
    char name[16];                      // 队列名称
    struct virtnet_sq_stats stats;      // 发送统计
    struct virtnet_interrupt_coalesce intr_coal; // 中断合并
    struct napi_struct napi;            // NAPI结构
    bool reset;                         // 队列是否重置
    struct xsk_buff_pool *xsk_pool;     // XSK池(AF_XDP)
    dma_addr_t xsk_hdr_dma_addr;        // XSK头DMA地址
};
```

### 3.3 接收队列结构体

```c
// 第326-382 行
struct receive_queue {
    struct virtqueue *vq;              // Virtqueue指针
    struct napi_struct napi;            // NAPI结构
    struct bpf_prog __rcu *xdp_prog;   // XDP程序
    struct virtnet_rq_stats stats;      // 接收统计
    u16 calls;                          // 接收通知计数
    bool dim_enabled;                   // 动态中断合并
    struct dim dim;                     // 中断动态调节
    struct page *pages;                // 页面链
    struct ewma_pkt_len mrg_avg_pkt_len; // 平均包长EWMA
    struct page_frag alloc_frag;       // 页面片段分配
    struct scatterlist sg[MAX_SKB_FRAGS + 2]; // 散列表
    unsigned int min_buf_len;          // 最小缓冲区长度
    char name[16];                      // 队列名称
    struct xdp_rxq_info xdp_rxq;       // XDP接收队列信息
    struct virtnet_rq_dma *last_dma;   // 最后DMA信息
    struct xsk_buff_pool *xsk_pool;    // XSK池
    struct xdp_buff **xsk_buffs;       // XSK缓冲区数组
};
```

### 3.4 发送流程 (xmit)

```c
// 第3319行: start_xmit()
static netdev_tx_t start_xmit(struct sk_buff *skb, struct net_device *dev)
{
    struct virtnet_info *vi = netdev_priv(dev);
    int qnum = skb_get_queue_mapping(skb);  // 获取队列编号
    struct send_queue *sq = &vi->sq[qnum];  // 获取发送队列

    // 1. 释放已完成的发送缓冲区
    free_old_xmit(sq, netdev_get_tx_queue(dev, qnum), true);

    // 2. 检查队列是否满
    check_sq_full_and_disable(vi, dev, sq);

    // 3. 添加skb到发送队列
    err = virtnet_send_command(vi, sq, skb);

    // 4. 通知Hypervisor
    if (virtqueue_kick_prepare(sq->vq))
        virtqueue_notify(sq->vq);

    return NETDEV_TX_OK;
}
```

**数据包发送流程图**:

```
+------------------+     +------------------+     +------------------+
|   Network Stack  | --> |   start_xmit()   | --> |   virtqueue      |
|   (skb)          |     |   (第3319行)     |     |   (shared mem)    |
+------------------+     +------------------+     +------------------+
                                |                          |
                                v                          v
                        +------------------+     +------------------+
                        |  skb + hdr       | --> |   Hypervisor     |
                        |  (virtio_net_hdr)|     |   receives skb   |
                        +------------------+     +------------------+
```

### 3.5 接收流程 (recv)

```c
// 第2573行: virtnet_receive_done()
static void virtnet_receive_done(struct virtnet_info *vi, ...)
{
    // 1. 设置RSS哈希
    if (dev->features & NETIF_F_RXHASH && vi->has_rss_hash_report)
        virtio_skb_set_hash(&hdr->hash_v1_hdr, skb);

    // 2. 处理校验和卸载
    if (virtio_net_handle_csum_offload(...))
        goto frame_err;

    // 3. 隧道包处理(GRO/GSO)
    if (virtio_net_hdr_tnl_to_skb(...))
        goto frame_err;

    // 4. 提交到NAPI(GRO接收)
    napi_gro_receive(&rq->napi, skb);
}
```

### 3.6 Big Packet 合并

Virtio Net 支持大数据包合并，通过 `mergeable_rx_bufs` 特性：

```c
// 第2458行: receive_mergeable()
static struct sk_buff *receive_mergeable(...)
{
    // 1. 获取头缓冲区
    buf = virtqueue_get_buf(rq->vq, &len);
    hdr = buf;

    // 2. 获取缓冲区数量
    num_buf = virtio16_to_cpu(vi->vdev, hdr->num_buffers);

    // 3. 循环收集所有片段
    while (--num_buf) {
        buf = virtqueue_get_buf(rq->vq, &len);
        // 添加到skb片段
        skb = virtnet_skb_append_frag(head_skb, curr_skb, page, buf, len, truesize);
    }

    return head_skb;
}
```

### 3.7 控制 virtqueue

```c
// 第384-388 行
struct control_buf {
    struct virtio_net_ctrl_hdr hdr;    // 控制头
    virtio_net_ctrl_ack status;        // 状态
};
```

控制命令用于设置MAC地址、RX模式、VLAN等：

| 命令 | 描述 |
|------|------|
| `VIRTIO_NET_CTRL_MACADDR_SET` | 设置MAC地址 |
| `VIRTIO_NET_CTRL_VLAN_ADD` | 添加VLAN ID |
| `VIRTIO_NET_CTRL_VLAN_DEL` | 删除VLAN ID |
| `VIRTIO_NET_CTRL_RX_MODE` | 设置接收模式 |

### 3.8 Probe/Remove 流程

```c
// 第6702行: virtnet_probe()
static int virtnet_probe(struct virtio_device *vdev)
{
    // 1. 分配virtnet_info
    vi = netdev_priv(alloc_netdev_mqs(...));

    // 2. 初始化virtqueue
    virtnet_find_vqs(vi);

    // 3. 设置特性
    vi->big_packets = virtio_has_feature(vdev, VIRTIO_NET_F_MRG_RXBUF);
    vi->mergeable_rx_bufs = virtio_has_feature(vdev, VIRTIO_NET_F_MRG_RXBUF);

    // 4. 注册网络设备
    register_netdev(dev);

    // 5. 标记设备就绪
    virtio_device_ready(vdev);
}

// 第7113行: virtnet_remove()
static void virtnet_remove(struct virtio_device *vdev)
{
    // 1. 清理CPU通知
    virtnet_cpu_notif_remove(vi);

    // 2. 关闭所有队列
    for (i = 0; i < vi->max_queue_pairs; i++) {
        napi_disable(&vi->rq[i].napi);
        napi_disable(&vi->sq[i].napi);
    }

    // 3. 注销网络设备
    unregister_netdev(vi->dev);

    // 4. 释放virtqueue
    virtnet_del_vqs(vi);

    // 5. 释放内存
    free_netdev(vi->dev);
}
```

### 3.9 架构图

```
+------------------------------------------------------------------+
|                      virtio_net 架构                              |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+        +-------------------+                |
|  |   send_queue[]   |        |  receive_queue[] |                |
|  |   (TX NAPI)      |        |  (RX NAPI)       |                |
|  +--------+----------+        +--------+----------+                |
|           |                            |                            |
|           v                            v                            |
|  +-------------------------------------------------+               |
|  |              virtqueue (shared memory)          |               |
|  |  +------------+  +------------+  +-----------+ |               |
|  |  | skb + hdr  |  | skb + hdr  |  | skb + hdr | |               |
|  |  +------------+  +------------+  +-----------+ |               |
|  +-------------------------------------------------+               |
|                         |                                             |
+-------------------------|---------------------------------------------+
                          |
                          v
                  +------------------+
                  |   Hypervisor     |
                  |   (QEMU/VBox)   |
                  +------------------+
```

---

## 4. Virtio Console 驱动 (virtio_console.c)

**文件路径**: `/Users/sphinx/github/linux/drivers/char/virtio_console.c`

### 4.1 核心数据结构

```c
// 第117-160 行
struct ports_device {
    struct list_head list;              // 设备链表
    struct work_struct control_work;     // 控制工作
    struct work_struct config_work;      // 配置工作
    struct list_head ports;              // 端口列表
    spinlock_t ports_lock;               // 端口列表锁
    spinlock_t c_ivq_lock;              // 控制输入队列锁
    spinlock_t c_ovq_lock;              // 控制输出队列锁
    u32 max_nr_ports;                   // 最大端口数
    struct virtio_device *vdev;          // Virtio设备
    struct virtqueue *c_ivq, *c_ovq;    // 控制队列
    struct virtio_console_control cpkt;  // 控制包
    struct virtqueue **in_vqs, **out_vqs; // IO端口队列
    int chr_major;                       // 字符设备主号
};

// 第167-232 行
struct port {
    struct list_head list;               // 端口链表
    struct ports_device *portdev;        // 所属设备
    struct port_buffer *inbuf;          // 输入缓冲区
    spinlock_t inbuf_lock;              // 输入缓冲锁
    spinlock_t outvq_lock;              // 输出队列锁
    struct virtqueue *in_vq, *out_vq;   // IO队列
    struct port_stats stats;            // 统计信息
    struct console cons;                 // 控制台端口
    struct cdev *cdev;                  // 字符设备
    struct device *dev;                 // 设备
    struct kref kref;                   // 引用计数
    wait_queue_head_t waitqueue;        // 等待队列
    char *name;                         // 端口名称
    struct fasync_struct *async_queue;  // 异步通知
    u32 id;                             // 端口ID
    bool outvq_full;                    // 输出队列满
    bool host_connected;                // 主机连接
    bool guest_connected;               // 客户机连接
};
```

### 4.2 多端口支持

```c
// 第1322-1442 行: add_port()
static int add_port(struct ports_device *portdev, u32 id)
{
    // 1. 分配port结构
    port = kmalloc(sizeof(*port), ...);
    kref_init(&port->kref);

    // 2. 设置端口队列
    port->in_vq = portdev->in_vqs[port->id];
    port->out_vq = portdev->out_vqs[port->id];

    // 3. 创建字符设备
    port->cdev = cdev_alloc();
    port->cdev->ops = &port_fops;
    devt = MKDEV(portdev->chr_major, id);
    cdev_add(port->cdev, devt, 1);

    // 4. 创建设备节点
    port->dev = device_create(&port_class, ..., "vport%up%u", ...);

    // 5. 初始化缓冲区队列
    fill_queue(port->in_vq, &port->inbuf_lock);

    // 6. 如果是控制台端口，初始化hvc
    if (!use_multiport(portdev))
        init_port_console(port);

    // 7. 通知主机端口就绪
    send_control_msg(port, VIRTIO_CONSOLE_PORT_READY, 1);
}
```

### 4.3 动态添加/移除端口

```c
// 第1523-1658 行: handle_control_message()
static void handle_control_message(...)
{
    switch (event) {
    case VIRTIO_CONSOLE_PORT_ADD:        // 添加端口
        add_port(portdev, id);
        break;

    case VIRTIO_CONSOLE_PORT_REMOVE:    // 移除端口
        unplug_port(port);
        break;

    case VIRTIO_CONSOLE_CONSOLE_PORT:   // 控制台端口
        init_port_console(port);
        break;

    case VIRTIO_CONSOLE_RESIZE:         // 控制台大小改变
        set_console_size(port, rows, cols);
        hvc_resize(port->cons.hvc, port->cons.ws);
        break;

    case VIRTIO_CONSOLE_PORT_OPEN:      // 端口打开状态
        port->host_connected = value;
        wake_up_interruptible(&port->waitqueue);
        break;

    case VIRTIO_CONSOLE_PORT_NAME:      // 端口名称
        port->name = kmalloc(name_size, ...);
        break;
    }
}

// 第1471-1520 行: unplug_port()
static void unplug_port(struct port *port)
{
    // 1. 从列表移除
    list_del(&port->list);

    // 2. 通知应用程序
    if (port->guest_connected) {
        send_sigio_to_port(port);
        port->guest_connected = false;
        port->host_connected = false;
        wake_up_interruptible(&port->waitqueue);
    }

    // 3. 移除hvc控制台
    if (is_console_port(port)) {
        hvc_remove(port->cons.hvc);
        ida_free(&vtermno_ida, port->cons.vtermno);
    }

    // 4. 释放端口数据
    remove_port_data(port);

    // 5. 销毁设备
    device_destroy(&port_class, port->dev->devt);
    cdev_del(port->cdev);
    kref_put(&port->kref, remove_port);
}
```

### 4.4 架构图

```
+------------------------------------------------------------------+
|                    virtio_console 架构                            |
+------------------------------------------------------------------+

  +-------------+       +-------------+       +-------------+
  |  /dev/vport0p0 |   |  /dev/vport0p1 |   |  /dev/hvc0  |
  |  (serial)      |   |  (serial)      |   |  (console)  |
  +-------+---------+   +-------+---------+   +-------+---------+
          |                      |                      |
          v                      v                      v
  +---------------------------------------------------------------+
  |                      port_fops                                 |
  |  .read = port_fops_read, .write = port_fops_write, etc.       |
  +-------------------------------+-------------------------------+
                                  |
  +-------------------------------+-------------------------------+
  |                          port struct                          |
  |  - in_vq, out_vq (IO virtqueue)                              |
  |  - port->host_connected, guest_connected                     |
  |  - waitqueue for blocking I/O                                |
  +---------------------------------------------------------------+
                                  |
  +---------------------------------------------------------------+
  |                    ports_device struct                        |
  |  - c_ivq, c_ovq (control virtqueue)                         |
  |  - control_work (handle control messages)                     |
  |  - max_nr_ports (maximum ports)                               |
  +---------------------------------------------------------------+
                                  |
                                  v
                          +------------------+
                          |   Hypervisor     |
                          +------------------+
```

---

## 5. Virtio SCSI 驱动 (virtio_scsi.c)

**文件路径**: `/Users/sphinx/github/linux/drivers/scsi/virtio_scsi.c`

### 5.1 设备结构体

```c
// 第46-99 行
struct virtio_scsi_cmd {
    struct scsi_cmnd *sc;               // SCSI命令
    struct completion *comp;            // 完成通知
    union {
        struct virtio_scsi_cmd_req cmd;        // 普通请求
        struct virtio_scsi_cmd_req_pi cmd_pi;  // 带PI的请求
        struct virtio_scsi_ctrl_tmf_req tmf;   // TMF请求
        struct virtio_scsi_ctrl_an_req an;     // 异步通知请求
    } req;
    union {
        struct virtio_scsi_cmd_resp cmd;        // 命令响应
        struct virtio_scsi_ctrl_tmf_resp tmf;   // TMF响应
        struct virtio_scsi_ctrl_an_resp an;     // 异步通知响应
        struct virtio_scsi_event evt;            // 事件
    } resp;
} ____cacheline_aligned_in_smp;

struct virtio_scsi {
    struct virtio_device *vdev;        // Virtio设备
    struct virtio_scsi_event_node event_list[VIRTIO_SCSI_EVENT_LEN]; // 事件列表
    u32 num_queues;                    // 队列数量
    int io_queues[HCTX_MAX_TYPES];     // IO队列类型
    struct hlist_node node;            // 节点
    bool stop_events;                  // 停止事件标志
    struct virtio_scsi_vq ctrl_vq;     // 控制队列
    struct virtio_scsi_vq event_vq;    // 事件队列
    struct virtio_scsi_vq req_vqs[];   // 请求队列数组
};

struct virtio_scsi_vq {
    spinlock_t vq_lock;               // 队列锁
    struct virtqueue *vq;              // Virtqueue
};
```

### 5.2 命令处理流程

```c
// 第571-618 行: virtscsi_queuecommand()
static enum scsi_qc_status virtscsi_queuecommand(struct Scsi_Host *shost, ...)
{
    // 1. 选择virtqueue (多队列)
    req_vq = virtscsi_pick_vq_mq(vscsi, sc);

    // 2. 初始化命令头
    if (virtio_has_feature(vscsi->vdev, VIRTIO_SCSI_F_T10_PI))
        virtio_scsi_init_hdr_pi(..., &cmd->req.cmd_pi, sc);
    else
        virtio_scsi_init_hdr(..., &cmd->req.cmd, sc);

    // 3. 添加到virtqueue
    ret = virtscsi_add_cmd(req_vq, cmd, req_size, resp_size, kick);

    if (ret == -EIO) {
        cmd->resp.cmd.response = VIRTIO_SCSI_S_BAD_TARGET;
        virtscsi_complete_cmd(vscsi, cmd);
    } else if (ret != 0)
        return SCSI_MLQUEUE_HOST_BUSY;

    return 0;
}

// 第435-478 行: __virtscsi_add_cmd()
static int __virtscsi_add_cmd(struct virtqueue *vq, ...)
{
    // 构建散列表: [req header] [data-out] [resp header] [data-in]
    sg_init_one(&req, &cmd->req, req_size);
    sgs[out_num++] = &req;

    if (out)
        sgs[out_num++] = out->sgl;    // 数据输出

    sg_init_one(&resp, &cmd->resp, resp_size);
    sgs[out_num + in_num++] = &resp;  // 响应

    if (in)
        sgs[out_num + in_num++] = in->sgl; // 数据输入

    return virtqueue_add_sgs(vq, sgs, out_num, in_num, cmd, GFP_ATOMIC);
}
```

### 5.3 事件处理

```c
// 第385-417 行: virtscsi_handle_event()
static void virtscsi_handle_event(struct work_struct *work)
{
    // 1. 检查事件是否遗漏
    if (event->event & VIRTIO_SCSI_T_EVENTS_MISSED) {
        // 重新扫描热插拔设备
        virtscsi_rescan_hotunplug(vscsi);
        scsi_scan_host(shost);
    }

    switch (event->event) {
    case VIRTIO_SCSI_T_TRANSPORT_RESET:  // 传输层重置
        virtscsi_handle_transport_reset(vscsi, event);
        break;

    case VIRTIO_SCSI_T_PARAM_CHANGE:      // 参数改变
        virtscsi_handle_param_change(vscsi, event);
        break;
    }

    // 重新加入事件缓冲区
    virtscsi_kick_event(vscsi, event_node);
}
```

### 5.4 热插拔支持

```c
// 第260-271 行: virtscsi_kick_event_all()
static int virtscsi_kick_event_all(struct virtio_scsi *vscsi)
{
    // 为每个事件节点添加缓冲区到事件队列
    for (i = 0; i < VIRTIO_SCSI_EVENT_LEN; i++) {
        vscsi->event_list[i].vscsi = vscsi;
        vscsi->event_list[i].event = &vscsi->events[i];
        virtscsi_kick_event(vscsi, &vscsi->event_list[i]);
    }
    return 0;
}

// 第343-383 行: virtscsi_rescan_hotunplug()
static int virtscsi_rescan_hotunplug(struct virtio_scsi *vscsi)
{
    // 对每个SCSI设备执行INQUIRY命令
    shost_for_each_device(sdev, shost) {
        result = scsi_execute_cmd(sdev, scsi_cmd, REQ_OP_DRV_IN, ...);
        // 如果LUN不存在，移除设备
        if (result == 0 && (inq_result[0] >> 5) == 0) {
            scsi_remove_device(sdev);
        } else if (result > 0 && host_byte(result) == DID_BAD_TARGET) {
            scsi_remove_device(sdev);
        }
    }
}
```

### 5.5 架构图

```
+------------------------------------------------------------------+
|                     virtio_scsi 架构                              |
+------------------------------------------------------------------+

  +-------------------+        +-------------------+
  |   SCSI Mid Layer  | <----> |   scsi_host_template |
  |   (scsi_queuecmd) |        |   virtscsi_xxx   |
  +--------+----------+        +-------------------+
           |                             |
           v                             v
  +---------------------------------------------------------------+
  |                     virtio_scsi 结构                          |
  |  +------------+  +------------+  +------------+               |
  |  |  ctrl_vq   |  |  event_vq  |  |  req_vqs[] |               |
  |  | (TMF/AN)   |  | (热插拔事件) |  | (IO命令)   |               |
  |  +------------+  +------------+  +------------+               |
  +---------------------------------------------------------------+
                               |
                               v
                       +------------------+
                       |   Hypervisor     |
                       |   (QEMU/SCSI)   |
                       +------------------+
```

---

## 6. Virtio Balloon 驱动 (virtio_balloon.c)

**文件路径**: `/Users/sphinx/github/linux/virt/virtio/virtio_balloon.c`

### 6.1 内存气球机制

Virtio Balloon 通过"充气"和"放气"来动态调整虚拟机的内存使用：

| 状态 | 描述 |
|------|------|
| **Inflate** | Guest将页面借给宿主机，页面被锁定 |
| **Deflate** | 宿主机归还页面，Guest可以重新使用 |

### 6.2 核心数据结构

```c
// virtio_balloon.c (基于内核标准结构)
struct virtio_balloon {
    struct virtio_device *vdev;        // Virtio设备
    struct virtqueue *inflate_vq;      // 充气队列
    struct virtqueue *deflate_vq;     // 放气队列
    struct virtqueue *stats_vq;        // 统计队列
    struct virtqueue *ack_vq;          // 确认队列

    __u32 num_pages;                   // 当前气球页数
    __u32 actual;                      // 实际分配页数

    struct balloon_dev_info info;      // 气球设备信息

    wait_queue_head_t queue_wait;      // 等待队列

    struct work_struct update_balloon_stats_work;
    struct work_struct update_balloon_size_work;
};
```

### 6.3 Inflate/Deflate 流程

**充气 (Inflate)** - 回收页面给宿主机：

```c
// 典型流程
static void virtballoon_balloon_up(struct virtio_balloon *vb)
{
    // 1. 计算需要回收的页面数
    num_pages = vb->num_pfns;

    // 2. 将页面添加到inflate_vq
    for (i = 0; i < num_pages; i++) {
        virtqueue_add_outbuf(inflate_vq, page_to_balloon(pfn), ...);
    }

    // 3. 通知宿主机
    virtqueue_kick(inflate_vq);

    // 4. 更新统计
    vb->num_pages -= num_pages;
}
```

**放气 (Deflate)** - 回收页面归还给Guest：

```c
static void virtballoon_balloon_down(struct virtio_balloon *vb)
{
    // 1. 从deflate_vq获取页面
    while ((buf = virtqueue_get_buf(deflate_vq, &len)) != NULL) {
        // 2. 将页面恢复到Guest可用列表
        balloon_page_put(page);
        vb->num_pages += len / sizeof(struct page *);
    }
}
```

### 6.4 与宿主机协作

```
+------------------------------------------------------------------+
|                    Virtio Balloon 机制                            |
+------------------------------------------------------------------+

  Guest 内核                              Host (Hypervisor)
  +-------------+                        +------------------+
  | Balloon     |  <--- inflate_vq ---> | Host reclaims   |
  | (页面回收)   |                        | pages for other  |
  +-------------+                        | VMs              |
        |                                      |
        |  <--- deflate_vq ---                 |
        | (返回页面)                            |
  +-------------+                        +------------------+
  | Guest可用    |  <--- stats_vq ----> | Memory stats     |
  | 页面增加     |                        | reporting        |
  +-------------+                        +------------------+
```

---

## 7. Virtio GPU 驱动 (virtio_gpu)

**文件路径**: `/Users/sphinx/github/linux/drivers/gpu/drm/virtio/`

### 7.1 驱动结构

Virtio GPU 是一个 DRM (Direct Rendering Manager) 驱动，支持虚拟显示和 3D 加速。

**主要文件**:

| 文件 | 描述 |
|------|------|
| `virtgpu_drv.c` | 驱动注册和probe/remove |
| `virtgpu_kms.c` | KMS (Kernel Mode Setting) 初始化 |
| `virtgpu_vq.c` | Virtqueue 操作和命令处理 |
| `virtgpu_fence.c` | Fence 同步机制 |
| `virtgpu_display.c` | 显示输出管理 |
| `virtgpu_object.c` | GEM 对象管理 |

### 7.2 设备结构体

```c
// virtgpu_drv.h 第228-278 行
struct virtio_gpu_device {
    struct drm_device *ddev;            // DRM设备

    struct virtio_device *vdev;         // Virtio设备

    struct virtio_gpu_output outputs[VIRTIO_GPU_MAX_SCANOUTS]; // 显示输出
    uint32_t num_scanouts;              // 扫描输出数量

    struct virtio_gpu_queue ctrlq;       // 控制队列
    struct virtio_gpu_queue cursorq;    // 光标队列
    struct kmem_cache *vbufs;           // 命令缓存

    atomic_t pending_commands;          // 待处理命令计数

    struct virtio_gpu_fence_driver fence_drv; // Fence驱动

    bool has_virgl_3d;                  // Virgl 3D支持
    bool has_edid;                      // EDID支持
    bool has_indirect;                  // 间接描述符
    bool has_resource_assign_uuid;       // 资源UUID
    bool has_resource_blob;             // Blob资源
    struct virtio_shm_region host_visible_region; // 共享内存
};
```

### 7.3 Virtqueue 操作

```c
// virtgpu_vq.c 第73-88 行
int virtio_gpu_alloc_vbufs(struct virtio_gpu_device *vgdev)
{
    // 创建命令缓冲区缓存
    vgdev->vbufs = kmem_cache_create("virtio-gpu-vbufs",
                                      VBUFFER_SIZE, ...);
}

// 第202-209 行
static void free_vbuf(struct virtio_gpu_device *vgdev,
                     struct virtio_gpu_vbuffer *vbuf)
{
    if (vbuf->resp_size > MAX_INLINE_RESP_SIZE)
        kfree(vbuf->resp_buf);
    kvfree(vbuf->data_buf);
    kmem_cache_free(vgdev->vbufs, vbuf);
}
```

### 7.4 命令处理

```c
// virtgpu_vq.c 第225-275 行
void virtio_gpu_dequeue_ctrl_func(struct work_struct *work)
{
    // 1. 获取完成的vbuffer列表
    reclaim_vbufs(vgdev->ctrlq.vq, &reclaim_list);

    // 2. 处理每个响应
    list_for_each_entry(entry, &reclaim_list, list) {
        resp = entry->resp_buf;

        // 3. 检查fence
        if (resp->flags & VIRTIO_GPU_FLAG_FENCE) {
            fence_id = le64_to_cpu(resp->fence_id);
            virtio_gpu_fence_event_process(vgdev, fence_id);
        }

        // 4. 调用回调
        if (entry->resp_cb)
            entry->resp_cb(vgdev, entry);
    }

    // 5. 释放vbuffer
    list_for_each_entry_safe(entry, tmp, &reclaim_list, list) {
        virtio_gpu_array_put_free_delayed(vgdev, entry->objs);
        free_vbuf(vgdev, entry);
    }
}
```

### 7.5 Probe 流程

```c
// virtgpu_drv.c 第74-120 行
static int virtio_gpu_probe(struct virtio_device *vdev)
{
    // 1. 分配DRM设备
    dev = drm_dev_alloc(&driver, vdev->dev.parent);
    if (IS_ERR(dev))
        return PTR_ERR(dev);
    vdev->priv = dev;

    // 2. PCI兼容处理
    if (dev_is_pci(vdev->dev.parent))
        virtio_gpu_pci_quirk(dev);

    // 3. 设置DMA参数
    dma_set_max_seg_size(dev->dev, ...);

    // 4. 初始化virtio-gpu
    ret = virtio_gpu_init(vdev, dev);
    if (ret)
        goto err_free;

    // 5. 注册DRM设备
    ret = drm_dev_register(dev, 0);
    if (ret)
        goto err_deinit;

    // 6. 初始化客户端
    drm_client_setup(vdev->priv, NULL);

    return 0;

err_deinit:
    virtio_gpu_deinit(dev);
err_free:
    drm_dev_put(dev);
    return ret;
}
```

### 7.6 架构图

```
+------------------------------------------------------------------+
|                      virtio_gpu 架构                              |
+------------------------------------------------------------------+

  +------------------+        +------------------+
  |   DRM Core       | <----> |   drm_driver    |
  |   (ioctls/fops)  |        |   virtgpu_xxx   |
  +--------+---------+        +------------------+
           |                             |
           v                             v
  +---------------------------------------------------------------+
  |                  virtio_gpu_device                            |
  |  +------------+  +------------+  +------------+               |
  |  |  ctrlq     |  |  cursorq   |  |  fence_drv |               |
  |  | (GPU命令)  |  | (光标更新) |  | (同步)     |               |
  |  +------------+  +------------+  +------------+               |
  +---------------------------------------------------------------+
                               |
                               v
                       +------------------+
                       |   Hypervisor     |
                       |   (virgl/3D)    |
                       +------------------+
```

---

## 8. 通用驱动框架分析

### 8.1 Virtio Driver 注册

所有 Virtio 驱动都遵循相同的注册模式：

```c
// virtio_blk.c 第1675-1691 行
static struct virtio_driver virtio_blk = {
    .feature_table          = features,              // 特性表
    .feature_table_size     = ARRAY_SIZE(features),
    .feature_table_legacy   = features_legacy,      // 传统特性表
    .feature_table_size_legacy = ARRAY_SIZE(features_legacy),
    .driver.name            = KBUILD_MODNAME,        // 驱动名称
    .id_table               = id_table,              // 设备ID表
    .probe                  = virtblk_probe,         // 探测函数
    .remove                 = virtblk_remove,        // 移除函数
    .config_changed         = virtblk_config_changed, // 配置改变回调
#ifdef CONFIG_PM_SLEEP
    .freeze                 = virtblk_freeze,        // 冻结(休眠)
    .restore                = virtblk_restore,       // 恢复
#endif
    .reset_prepare          = virtblk_reset_prepare, // 重置准备
    .reset_done             = virtblk_reset_done,    // 重置完成
};
```

### 8.2 设备 ID 匹配表

```c
// virtio_blk.c 第1654-1657 行
static const struct virtio_device_id id_table[] = {
    { VIRTIO_ID_BLOCK, VIRTIO_DEV_ANY_ID },  // 块设备ID=2
    { 0 },
};

// virtio_net.c
static const struct virtio_device_id id_table[] = {
    { VIRTIO_ID_NETWORK, VIRTIO_DEV_ANY_ID },  // 网卡ID=1
    { 0 },
};

// virtio_console.c 第2065-2068 行
static const struct virtio_device_id id_table[] = {
    { VIRTIO_ID_CONSOLE, VIRTIO_DEV_ANY_ID },  // 控制台ID=3
    { 0 },
};

// virtio_scsi.c 第1039-1042 行
static const struct virtio_device_id id_table[] = {
    { VIRTIO_ID_SCSI, VIRTIO_DEV_ANY_ID },    // SCSI ID=8
    { 0 },
};
```

**Virtio 设备 ID 定义** (`include/linux/virtio_ids.h`)：

| ID | 设备类型 |
|----|----------|
| 1 | network |
| 2 | block |
| 3 | console |
| 4 | 保留 |
| 5 | rng (随机数生成器) |
| 6 | balloning |
| 7 | gpudrm |
| 8 | scsi |
| 9 | 保留 |

### 8.3 Probe 典型流程

```c
static int xxx_probe(struct virtio_device *vdev)
{
    // 1. 检查config访问
    if (!vdev->config->get) {
        dev_err(&vdev->dev, "config access disabled\n");
        return -EINVAL;
    }

    // 2. 分配设备结构
    dev = kmalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;

    // 3. 初始化设备
    dev->vdev = vdev;
    vdev->priv = dev;

    // 4. 初始化virtqueue
    err = init_vqs(dev);
    if (err)
        goto free_dev;

    // 5. 读取设备配置
    read_device_config(dev);

    // 6. 注册设备
    register_device(dev);

    // 7. 标记设备就绪
    virtio_device_ready(vdev);

    return 0;

free_dev:
    kfree(dev);
    return err;
}
```

### 8.4 Remove 典型流程

```c
static void xxx_remove(struct virtio_device *vdev)
{
    struct xxx_dev *dev = vdev->priv;

    // 1. 停止新请求
    device_shutdown(dev);

    // 2. 重置设备
    virtio_reset_device(vdev);

    // 3. 删除virtqueue
    vdev->config->del_vqs(vdev);

    // 4. 注销设备
    unregister_device(dev);

    // 5. 释放内存
    kfree(dev);
}
```

### 8.5 特征位协商

```c
// 驱动声明支持的特性
static unsigned int features[] = {
    VIRTIO_F_XXX,  // 特性位
    ...
};

// 协商流程
virtio_finalize_features(vdev)
    |
    +-- for each feature in drv->feature_table
    |       |
    |       +-- if (feature in device)
    |               set bit in dev->features
    |
    +-- vdev->config->finalize_features(vdev)
```

### 8.6 PM (电源管理) 支持

```c
#ifdef CONFIG_PM_SLEEP
static int xxx_freeze(struct virtio_device *vdev)
{
    // 1. 停止设备
    virtio_reset_device(vdev);

    // 2. 删除virtqueue
    vdev->config->del_vqs(vdev);

    return 0;
}

static int xxx_restore(struct virtio_device *vdev)
{
    struct xxx_dev *dev = vdev->priv;

    // 1. 重新初始化virtqueue
    init_vqs(dev);

    // 2. 重新协商特性
    virtio_device_ready(vdev);

    return 0;
}
#endif
```

---

## 9. 总结

### 9.1 Virtio 驱动通用模式

| 组件 | 描述 |
|------|------|
| **设备结构** | 包含 `virtio_device *vdev` 和特定功能结构 |
| **Virtqueue** | 共享内存环形缓冲区，用于高速通信 |
| **特征协商** | 通过 `feature_table` 声明支持的特性 |
| **Probe/Remove** | 标准的设备生命周期管理 |
| **PM** | 支持冻结/恢复和重置 |

### 9.2 性能优化技术

1. **多队列支持**: Block(blk-mq)、Net(multiqueue)、SCSI(multi-queue)
2. **中断合并**: 动态中断调节(DIM)
3. **批处理**: 合并多个请求减少通知开销
4. **XDP/AF_XDP**: Net驱动支持快速数据包处理
5. **Big Packet**: Net驱动支持大数据包合并
6. **DMA映射**: 直接内存访问减少拷贝

### 9.3 驱动对比

| 驱动 | 用途 | Virtqueue数量 | 特殊功能 |
|------|------|---------------|----------|
| virtio_blk | 块存储 | N (请求队列) | 多队列blk-mq |
| virtio_net | 网络 | 2N+1 (TX+RX+控制) | XDP, GSO, RSS |
| virtio_console | 串口/控制台 | 2M+2 (M端口+控制) | 多端口, hvc |
| virtio_scsi | SCSI存储 | N+2 (请求+控制+事件) | 热插拔, TMF |
| virtio_balloon | 内存管理 | 4 (充/放气/统计/确认) | 动态内存 |
| virtio_gpu | 图形 | 2+ (控制+光标) | Virgl 3D |

### 9.4 源码位置汇总

```
/Users/sphinx/github/linux/
├── drivers/block/virtio_blk.c          # 块设备驱动
├── drivers/net/virtio_net.c            # 网络驱动
├── drivers/char/virtio_console.c       # 控制台驱动
├── drivers/scsi/virtio_scsi.c          # SCSI驱动
├── virt/virtio/virtio_balloon.c        # 气球驱动
└── drivers/gpu/drm/virtio/             # GPU驱动
    ├── virtgpu_drv.c
    ├── virtgpu_kms.c
    ├── virtgpu_vq.c
    ├── virtgpu_fence.c
    └── ...
```

---

*文档生成时间: 2026-04-26*
*分析基于 Linux 内核源码*
