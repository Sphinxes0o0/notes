以下是关于网页内容《Virtio on Linux》的详细笔记，涵盖了 Virtio 的核心概念、通信机制、设备发现与驱动加载过程等内容：


---
Virtio on Linux
1. 引言
- Virtio 是一个开放标准，定义了不同类型设备（如网络、存储、控制台等）的驱动程序与设备之间的通信协议。它最初是为虚拟化环境中的半虚拟化设备（paravirtualized devices）设计的，但也可以用于任何符合标准的设备（无论是真实设备还是模拟设备）。
- 本文档主要以 Linux 内核在虚拟机中运行，并使用由虚拟机监控程序（hypervisor）提供的半虚拟化设备为例进行说明。这些设备通过标准机制（如 PCI）暴露为 virtio 设备。

2. 设备与驱动通信：Virtqueues
- 通信机制：虽然 virtio 设备实际上是虚拟机监控程序中的抽象层，但它们通过特定的传输方法（如 PCI、MMIO 或 CCW）暴露给虚拟机，使其看起来像是物理设备。Virtio 规范详细定义了这些传输方法，包括设备发现、功能和中断处理。
- Virtqueues：驱动程序和设备之间的通信通过共享内存完成，这是 virtio 设备高效的原因。Virtqueues 是用于通信的特殊数据结构，实际上是环形缓冲区（ring buffers），类似于网络设备中使用的缓冲区描述符。
- Virtio 环形描述符（vring_desc）：
  - 定义：
struct vring_desc {
    __virtio64 addr;   // 缓冲区地址（虚拟机物理地址）
    __virtio32 len;    // 缓冲区长度
    __virtio16 flags;  // 描述符标志
    __virtio16 next;   // 链接到下一个描述符的索引
};
  - 描述符通过 next 字段链接，形成链表。
  - 所有描述符指向的缓冲区由虚拟机分配，主机用于读取或写入，但不能同时用于两者。
- Virtqueue 结构：
  - 定义：
struct virtqueue {
    struct list_head list;  // 设备的 virtqueue 链表
    void (*callback)(struct virtqueue *vq);  // 缓冲区被消费时的回调函数
    const char *name;       // virtqueue 名称（主要用于调试）
    struct virtio_device *vdev;  // 所属的 virtio 设备
    unsigned int index;     // 队列的序号
    unsigned int num_free;  // 预期可容纳的元素数量
    unsigned int num_max;   // 设备支持的最大元素数量
    bool reset;             // 是否处于重置状态
    void *priv;             // 供 virtqueue 实现使用的指针
};
  - num_free 的说明：如果使用间接缓冲区，则每个缓冲区需要一个队列元素；否则，每个缓冲区需要一个元素。
  - 回调函数由 hypervisor 触发的中断调用（通过 vring_interrupt()）。
- 中断处理：
  - 中断处理函数 vring_interrupt() 被注册到 virtqueue 中，当设备消费完驱动程序提供的缓冲区时，会触发回调函数。

3. 设备发现与驱动加载
- Virtio 核心：内核中的 virtio 核心包含 virtio 总线驱动程序和特定传输方法的驱动程序（如 virtio-pci 和 virtio-mmio）。此外，还有针对特定设备类型的 virtio 驱动程序，这些驱动程序注册到 virtio 总线驱动程序中。
- 设备发现：设备的发现和配置取决于虚拟机监控程序如何定义它。以 QEMU 的 virtio-console 设备为例，当使用 PCI 作为传输方法时，设备会在 PCI 总线上以供应商 ID 0x1af4（Red Hat, Inc.）和设备 ID 0x1003（virtio 控制台）呈现，内核会像检测其他 PCI 设备一样检测到它。
- 驱动加载：
  - 在 PCI 枚举过程中，如果设备匹配 virtio-pci 驱动程序（根据 virtio-pci 设备表，任何供应商 ID 为 0x1af4 的 PCI 设备）：
static const struct pci_device_id virtio_pci_id_table[] = {
    { PCI_DEVICE(PCI_VENDOR_ID_REDHAT_QUMRANET, PCI_ANY_ID) },
    { 0 }
};
  - 如果匹配成功，virtio-pci 驱动程序会被加载，并尝试以现代模式或遗留模式初始化设备：
static int virtio_pci_probe(struct pci_dev *pci_dev,
                            const struct pci_device_id *id)
{
    ...
    if (force_legacy) {
        rc = virtio_pci_legacy_probe(vp_dev);
        if (rc == -ENODEV || rc == -ENOMEM)
            rc = virtio_pci_modern_probe(vp_dev);
        if (rc)
            goto err_probe;
    } else {
        rc = virtio_pci_modern_probe(vp_dev);
        if (rc == -ENODEV)
            rc = virtio_pci_legacy_probe(vp_dev);
        if (rc)
            goto err_probe;
    }
    ...
    rc = register_virtio_device(&vp_dev->vdev);
}
  - 设备注册到 virtio 总线后，内核会查找能够处理该设备的驱动程序，并调用其 probe 方法。
  - 在此过程中，virtqueues 会被分配和配置，通过调用 virtio_find_single_vq() 或 virtio_find_vqs() 等辅助函数，最终调用特定传输方法的 find_vqs 方法。

4. 参考资料
- Virtio 规范 v1.2：https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html
- Virtqueues 和 virtio 环形：数据如何传输：https://www.redhat.com/en/blog/virtqueues-and-virtio-ring-how-data-travels


---
总结
Virtio 是一种高效的半虚拟化设备通信机制，通过共享内存和 virtqueues 实现主机与虚拟机之间的高效数据传输。其核心功能依赖于 virtio 核心驱动程序和特定设备的驱动程序，设备发现和加载过程依赖于虚拟机监控程序的定义和内核的设备枚举机制。
Writing Vritio Drivers
以下是关于《Writing Virtio Drivers》文档的详尽笔记，总结了如何编写 Linux 内核中的 Virtio 驱动程序的关键点和细节：


---

1. 文档概述
- 目的：为驱动开发者提供编写或理解 Virtio 驱动程序的基本指南。
- 适用范围：适用于需要与虚拟设备（如虚拟机中的设备）交互的场景。
- 背景：Virtio 是一种标准化的虚拟设备接口，用于简化虚拟机与宿主机之间的设备通信。

2. Virtio 驱动程序的基本结构
- 注册到 Virtio 总线：驱动程序需要在 Virtio 总线上注册，并根据设备规范配置 Virtqueues（虚拟队列）。
- 设备私有数据：每个设备实例都有自己的私有数据结构，用于存储设备相关的状态和信息。
- 回调函数：驱动程序需要实现回调函数，用于处理设备通知的事件（如数据传输完成）。

3. 示例代码解析
文档提供了一个简单的 Virtio 驱动程序示例，展示了如何实现基本的驱动程序功能：

3.1 设备私有数据结构
struct virtio_dummy_dev {
    struct virtqueue *vq;  // 指向 Virtqueue 的指针
};
- 说明：每个设备实例都有一个私有数据结构，用于存储与设备相关的状态，例如 Virtqueue 的指针。

3.2 探测函数（**probe**）
static int virtio_dummy_probe(struct virtio_device *vdev)
{
    struct virtio_dummy_dev *dev = kzalloc(sizeof(struct virtio_dummy_dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;

    dev->vq = virtio_find_single_vq(vdev, virtio_dummy_recv_cb, "input");
    if (IS_ERR(dev->vq)) {
        kfree(dev);
        return PTR_ERR(dev->vq);
    }
    vdev->priv = dev;

    virtio_device_ready(vdev);  // 通知设备驱动程序已准备就绪
    return 0;
}
- 功能：
  - 分配设备私有数据结构。
  - 初始化 Virtqueue，并为其注册回调函数。
  - 调用 virtio_device_ready()，通知设备驱动程序已准备就绪。

3.3 移除函数（**remove**）
static void virtio_dummy_remove(struct virtio_device *vdev)
{
    struct virtio_dummy_dev *dev = vdev->priv;

    virtio_reset_device(vdev);  // 重置设备
    while ((buf = virtqueue_detach_unused_buf(dev->vq)) != NULL) {
        kfree(buf);  // 释放未使用的缓冲区
    }
    vdev->config->del_vqs(vdev);  // 删除 Virtqueues
    kfree(dev);  // 释放设备私有数据
}
- 功能：
  - 重置设备，禁用 Virtqueue 的中断。
  - 释放所有未使用的缓冲区。
  - 删除 Virtqueues 并释放设备私有数据。

3.4 回调函数
static void virtio_dummy_recv_cb(struct virtqueue *vq)
{
    struct virtio_dummy_dev *dev = vq->vdev->priv;
    char *buf;
    unsigned int len;

    while ((buf = virtqueue_get_buf(dev->vq, &len)) != NULL) {
        // 处理接收到的数据
    }
}
- 功能：
  - 从 Virtqueue 中获取已完成处理的缓冲区。
  - virtqueue_get_buf() 返回缓冲区指针和数据长度。

4. 数据传输
- 发送数据：
  - 使用 virtqueue_add_outbuf() 或 virtqueue_add_sgs() 将缓冲区添加到 Virtqueue。
  - 调用 virtqueue_kick() 通知设备开始处理。
- 接收数据：
  - 在回调函数中使用 virtqueue_get_buf() 获取设备写入的数据。
  - 如果设备写入了数据，len 参数会返回实际写入的长度。

5. Virtqueue 操作
- 禁用回调：virtqueue_disable_cb()，用于暂时禁用回调函数。
- 启用回调：virtqueue_enable_cb()，重新启用回调函数。
- 注意事项：某些操作（如禁用回调）可能不是同步的，因此需要谨慎使用。

6. 设备 ID 和注册
- 设备 ID：Virtio 驱动程序需要在 id_table 中定义支持的设备 ID。
- 注册驱动程序：使用 module_virtio_driver() 宏简化驱动程序的注册过程。

7. 参考资料
- Virtio 规范：文档建议参考 Virtio Spec v1.2 以获取更多细节和最新信息。


---

总结
- 核心概念：Virtio 驱动程序通过 Virtqueues 与虚拟设备进行通信，驱动程序需要管理缓冲区并处理设备的通知。
- 关键步骤：
  1. 初始化设备和 Virtqueues。
  2. 配置缓冲区并通知设备。
  3. 在回调函数中处理设备的通知。
  4. 清理资源并移除设备。
- 注意事项：
  - 确保 Virtqueue 操作的线程安全性。
  - 检查设备 ID 是否符合规范。
  - 关注 Virtio 规范的更新，以确保驱动程序的兼容性。


---

希望这些笔记能帮助你更好地理解和编写 Virtio 驱动程序！
