/*
 * TAP Device Implementation
 * 基于文档的完整TAP设备实现，用于验证代码正确性
 */

#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/netdevice.h>
#include <linux/etherdevice.h>
#include <linux/skbuff.h>
#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/wait.h>
#include <linux/poll.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/device.h>
#include <linux/if_ether.h>
#include <net/net_namespace.h>

#define TAP_DEVICE_OPENED     0x01
#define TAP_MAX_DEVICES       8

struct tap_device {
    struct net_device *dev;          // 网络设备
    struct cdev cdev;                // 字符设备
    struct device *device;           // 设备对象
    
    // 数据缓冲区
    struct sk_buff_head read_queue;  // 读队列
    wait_queue_head_t wait_queue;    // 等待队列
    
    // 状态管理
    spinlock_t lock;                 // 自旋锁
    int flags;                       // 设备标志
    struct mutex mutex;              // 互斥锁
    
    // 统计信息
    struct net_device_stats stats;
    
    // 设备标识
    int minor;
};

static struct tap_device *global_tap_device;
static dev_t tap_dev_number;
static struct class *tap_class;

// 前向声明
static int tap_open(struct inode *inode, struct file *file);
static int tap_release(struct inode *inode, struct file *file);
static ssize_t tap_read(struct file *file, char __user *buf, size_t count, loff_t *pos);
static ssize_t tap_write(struct file *file, const char __user *buf, size_t count, loff_t *pos);
static unsigned int tap_poll(struct file *file, struct poll_table_struct *wait);
static long tap_ioctl(struct file *file, unsigned int cmd, unsigned long arg);

static int tap_net_open(struct net_device *dev);
static int tap_net_close(struct net_device *dev);
static netdev_tx_t tap_net_xmit(struct sk_buff *skb, struct net_device *dev);
static struct net_device_stats *tap_net_get_stats(struct net_device *dev);
static int tap_set_mac_address(struct net_device *dev, void *addr);

// 字符设备操作结构
static const struct file_operations tap_fops = {
    .owner = THIS_MODULE,
    .read = tap_read,
    .write = tap_write,
    .poll = tap_poll,
    .open = tap_open,
    .release = tap_release,
    .unlocked_ioctl = tap_ioctl,
    .llseek = no_llseek,
};

// 网络设备操作结构
static const struct net_device_ops tap_netdev_ops = {
    .ndo_open = tap_net_open,
    .ndo_stop = tap_net_close,
    .ndo_start_xmit = tap_net_xmit,
    .ndo_get_stats = tap_net_get_stats,
    .ndo_set_mac_address = tap_set_mac_address,
    .ndo_validate_addr = eth_validate_addr,
};

// 字符设备实现
static int tap_open(struct inode *inode, struct file *file)
{
    struct tap_device *tap;
    
    tap = container_of(inode->i_cdev, struct tap_device, cdev);
    file->private_data = tap;
    
    // 初始化设备状态
    mutex_lock(&tap->mutex);
    if (!(tap->flags & TAP_DEVICE_OPENED)) {
        tap->flags |= TAP_DEVICE_OPENED;
        if (tap->dev)
            netif_start_queue(tap->dev);
    }
    mutex_unlock(&tap->mutex);
    
    pr_info("TAP device opened\n");
    return 0;
}

static int tap_release(struct inode *inode, struct file *file)
{
    struct tap_device *tap = file->private_data;
    
    mutex_lock(&tap->mutex);
    tap->flags &= ~TAP_DEVICE_OPENED;
    if (tap->dev)
        netif_stop_queue(tap->dev);
    mutex_unlock(&tap->mutex);
    
    pr_info("TAP device released\n");
    return 0;
}

static ssize_t tap_read(struct file *file, char __user *buf, 
                       size_t count, loff_t *pos)
{
    struct tap_device *tap = file->private_data;
    struct sk_buff *skb;
    ssize_t ret = 0;
    
    // 等待数据包到达
    if (skb_queue_empty(&tap->read_queue)) {
        if (file->f_flags & O_NONBLOCK)
            return -EAGAIN;
            
        ret = wait_event_interruptible(tap->wait_queue,
                                     !skb_queue_empty(&tap->read_queue));
        if (ret)
            return ret;
    }
    
    // 从队列中取出数据包
    spin_lock_bh(&tap->read_queue.lock);
    skb = __skb_dequeue(&tap->read_queue);
    spin_unlock_bh(&tap->read_queue.lock);
    
    if (!skb)
        return -EAGAIN;
    
    // 复制数据到用户空间
    if (count < skb->len) {
        ret = -EINVAL;
        goto free_skb;
    }
    
    if (copy_to_user(buf, skb->data, skb->len)) {
        ret = -EFAULT;
        goto free_skb;
    }
    
    ret = skb->len;

free_skb:
    kfree_skb(skb);
    return ret;
}

static ssize_t tap_write(struct file *file, const char __user *buf,
                        size_t count, loff_t *pos)
{
    struct tap_device *tap = file->private_data;
    struct sk_buff *skb;
    
    if (!tap->dev)
        return -ENODEV;
    
    if (count > tap->dev->mtu + ETH_HLEN)
        return -EINVAL;
    
    // 分配socket buffer
    skb = alloc_skb(count + NET_IP_ALIGN, GFP_KERNEL);
    if (!skb)
        return -ENOMEM;
    
    skb_reserve(skb, NET_IP_ALIGN);
    
    // 从用户空间复制数据
    if (copy_from_user(skb_put(skb, count), buf, count)) {
        kfree_skb(skb);
        return -EFAULT;
    }
    
    // 设置网络设备信息
    skb->dev = tap->dev;
    skb->protocol = eth_type_trans(skb, tap->dev);
    skb_reset_network_header(skb);
    
    // 更新统计信息
    tap->stats.rx_packets++;
    tap->stats.rx_bytes += count;
    
    // 将数据包传递给网络协议栈
    netif_rx(skb);
    
    return count;
}

static unsigned int tap_poll(struct file *file, struct poll_table_struct *wait)
{
    struct tap_device *tap = file->private_data;
    unsigned int mask = 0;
    
    poll_wait(file, &tap->wait_queue, wait);
    
    if (!skb_queue_empty(&tap->read_queue))
        mask |= POLLIN | POLLRDNORM;
    
    mask |= POLLOUT | POLLWRNORM;
    
    return mask;
}

static long tap_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    // 简化实现，实际应该处理各种ioctl命令
    return -ENOTTY;
}

// 网络设备实现
static int tap_net_open(struct net_device *dev)
{
    netif_start_queue(dev);
    pr_info("TAP network interface opened\n");
    return 0;
}

static int tap_net_close(struct net_device *dev)
{
    netif_stop_queue(dev);
    pr_info("TAP network interface closed\n");
    return 0;
}

static netdev_tx_t tap_net_xmit(struct sk_buff *skb, struct net_device *dev)
{
    struct tap_device *tap = global_tap_device;
    
    if (!tap) {
        dev_kfree_skb(skb);
        return NETDEV_TX_OK;
    }
    
    // 更新统计信息
    tap->stats.tx_packets++;
    tap->stats.tx_bytes += skb->len;
    
    // 将数据包放入读队列，供用户空间读取
    skb_queue_tail(&tap->read_queue, skb);
    wake_up_interruptible(&tap->wait_queue);
    
    return NETDEV_TX_OK;
}

static struct net_device_stats *tap_net_get_stats(struct net_device *dev)
{
    struct tap_device *tap = global_tap_device;
    return tap ? &tap->stats : NULL;
}

static int tap_set_mac_address(struct net_device *dev, void *addr)
{
    struct sockaddr *sa = addr;
    
    if (!is_valid_ether_addr(sa->sa_data))
        return -EADDRNOTAVAIL;
    
    memcpy(dev->dev_addr, sa->sa_data, ETH_ALEN);
    return 0;
}

// 设备初始化和清理
static int tap_device_init(struct tap_device *tap, const char *name)
{
    struct net_device *dev;
    int err;
    
    // 分配网络设备，不需要额外的私有数据（我们用全局的tap结构）
    dev = alloc_etherdev(0);
    if (!dev)
        return -ENOMEM;
    
    // 设置网络设备参数
    dev->netdev_ops = &tap_netdev_ops;
    dev->needs_free_netdev = true;
    strcpy(dev->name, name);
    
    // 生成随机MAC地址
    eth_hw_addr_random(dev);
    
    // 设置设备特性
    dev->features |= NETIF_F_HW_CSUM | NETIF_F_SG;
    dev->flags |= IFF_NOARP;
    
    // 初始化TAP设备结构
    tap->dev = dev;
    skb_queue_head_init(&tap->read_queue);
    init_waitqueue_head(&tap->wait_queue);
    spin_lock_init(&tap->lock);
    mutex_init(&tap->mutex);
    memset(&tap->stats, 0, sizeof(tap->stats));
    
    // 注册网络设备
    err = register_netdev(dev);
    if (err) {
        free_netdev(dev);
        return err;
    }
    
    pr_info("TAP network device %s registered\n", name);
    return 0;
}

static void tap_device_cleanup(struct tap_device *tap)
{
    if (tap->dev) {
        unregister_netdev(tap->dev);
        // free_netdev 会在 needs_free_netdev 中自动调用
        tap->dev = NULL;
    }
    
    // 清理读队列中的数据包
    skb_queue_purge(&tap->read_queue);
}

// 模块加载和卸载
static int __init tap_module_init(void)
{
    int err;
    
    pr_info("Loading TAP device module\n");
    
    // 分配设备号
    err = alloc_chrdev_region(&tap_dev_number, 0, TAP_MAX_DEVICES, "tap");
    if (err) {
        pr_err("Failed to allocate char device region\n");
        return err;
    }
    
    // 创建设备类
    tap_class = class_create(THIS_MODULE, "tap");
    if (IS_ERR(tap_class)) {
        err = PTR_ERR(tap_class);
        pr_err("Failed to create device class\n");
        goto fail_class;
    }
    
    // 分配TAP设备结构
    global_tap_device = kzalloc(sizeof(struct tap_device), GFP_KERNEL);
    if (!global_tap_device) {
        err = -ENOMEM;
        pr_err("Failed to allocate device structure\n");
        goto fail_alloc;
    }
    
    global_tap_device->minor = 0;
    
    // 初始化字符设备
    cdev_init(&global_tap_device->cdev, &tap_fops);
    global_tap_device->cdev.owner = THIS_MODULE;
    
    err = cdev_add(&global_tap_device->cdev, tap_dev_number, 1);
    if (err) {
        pr_err("Failed to add char device\n");
        goto fail_cdev;
    }
    
    // 创建设备节点
    global_tap_device->device = device_create(tap_class, NULL, 
                                            tap_dev_number, NULL, "tap0");
    if (IS_ERR(global_tap_device->device)) {
        err = PTR_ERR(global_tap_device->device);
        pr_err("Failed to create device node\n");
        goto fail_device;
    }
    
    // 初始化TAP设备
    err = tap_device_init(global_tap_device, "tap0");
    if (err) {
        pr_err("Failed to initialize TAP device\n");
        goto fail_tap_init;
    }
    
    pr_info("TAP device module loaded successfully\n");
    return 0;

fail_tap_init:
    device_destroy(tap_class, tap_dev_number);
fail_device:
    cdev_del(&global_tap_device->cdev);
fail_cdev:
    kfree(global_tap_device);
fail_alloc:
    class_destroy(tap_class);
fail_class:
    unregister_chrdev_region(tap_dev_number, TAP_MAX_DEVICES);
    return err;
}

static void __exit tap_module_exit(void)
{
    pr_info("Unloading TAP device module\n");
    
    if (global_tap_device) {
        tap_device_cleanup(global_tap_device);
        device_destroy(tap_class, tap_dev_number);
        cdev_del(&global_tap_device->cdev);
        kfree(global_tap_device);
    }
    
    if (tap_class)
        class_destroy(tap_class);
    
    unregister_chrdev_region(tap_dev_number, TAP_MAX_DEVICES);
    
    pr_info("TAP device module unloaded\n");
}

module_init(tap_module_init);
module_exit(tap_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("TAP Device Implementation");
MODULE_DESCRIPTION("Simple TAP Device Driver for Verification");
MODULE_VERSION("1.0"); 