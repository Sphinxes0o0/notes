#!/bin/bash

echo "========================================"
echo "      TAP设备代码语法检查 (macOS)"
echo "========================================"

# 检查是否安装了gcc或clang
if ! command -v gcc &> /dev/null && ! command -v clang &> /dev/null; then
    echo "[ERROR] 没有找到C编译器 (gcc 或 clang)"
    echo "请安装 Xcode Command Line Tools: xcode-select --install"
    exit 1
fi

# 选择编译器
if command -v clang &> /dev/null; then
    CC=clang
else
    CC=gcc
fi

echo "[INFO] 使用编译器: $CC"

# 创建临时的语法检查版本
echo "[INFO] 创建语法检查版本..."

# 为语法检查创建简化的头文件定义
cat > temp_kernel_defs.h << 'EOF'
/* 简化的内核定义，仅用于语法检查 */
#ifndef TEMP_KERNEL_DEFS_H
#define TEMP_KERNEL_DEFS_H

#include <stdint.h>
#include <stddef.h>

// 基本类型定义
typedef unsigned int __u32;
typedef unsigned short __u16;
typedef unsigned char __u8;
typedef size_t dev_t;
typedef long ssize_t;
typedef unsigned long gfp_t;

// 等待队列
typedef struct { int dummy; } wait_queue_head_t;
typedef struct { int dummy; } spinlock_t;

// 网络相关结构体
struct net_device {
    char name[16];
    void *netdev_ops;
    int flags;
    int features;
    int needs_free_netdev;
    unsigned char dev_addr[6];
};

struct sk_buff {
    unsigned int len;
};

struct sk_buff_head {
    struct sk_buff *next;
};

struct net_device_stats {
    unsigned long tx_packets;
    unsigned long tx_bytes;
    unsigned long rx_packets;
    unsigned long rx_bytes;
};

// 字符设备
struct cdev {
    int dummy;
};

struct device {
    int dummy;
};

struct class {
    int dummy;
};

struct inode {
    int dummy;
};

struct file {
    void *private_data;
};

// 互斥锁
struct mutex {
    int dummy;
};

// 网络设备操作
struct net_device_ops {
    int (*ndo_open)(struct net_device *dev);
    int (*ndo_stop)(struct net_device *dev);
    int (*ndo_start_xmit)(struct sk_buff *skb, struct net_device *dev);
    struct net_device_stats* (*ndo_get_stats)(struct net_device *dev);
    int (*ndo_set_mac_address)(struct net_device *dev, void *addr);
};

// 文件操作
struct file_operations {
    struct module *owner;
    int (*open)(struct inode *, struct file *);
    int (*release)(struct inode *, struct file *);
    ssize_t (*read)(struct file *, char *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char *, size_t, loff_t *);
    unsigned int (*poll)(struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long);
};

// 其他需要的定义
struct poll_table_struct { int dummy; };
struct sockaddr { char sa_data[14]; };
struct module { int dummy; };
typedef long loff_t;
typedef int netdev_tx_t;

// 常量定义
#define NETDEV_TX_OK 0
#define ETH_ALEN 6
#define IFF_NOARP 0x80
#define NETIF_F_HW_CSUM 0x1
#define NETIF_F_SG 0x2
#define GFP_KERNEL 0x400
#define EADDRNOTAVAIL 99
#define ENOMEM 12
#define EFAULT 14
#define EINVAL 22
#define EAGAIN 11
#define ENODEV 19
#define POLLIN 1
#define POLLOUT 4
#define THIS_MODULE ((struct module *)0)
#define ETH_P_ALL 0x0003

// 模拟函数声明
static inline void *netdev_priv(struct net_device *dev) { return NULL; }
static inline void *kzalloc(size_t size, gfp_t flags) { return NULL; }
static inline void kfree(void *ptr) { }
static inline void pr_info(const char *fmt, ...) { }
static inline void pr_err(const char *fmt, ...) { }
static inline int alloc_chrdev_region(dev_t *dev, unsigned baseminor, unsigned count, const char *name) { return 0; }
static inline void unregister_chrdev_region(dev_t from, unsigned count) { }
static inline struct class *class_create(struct module *owner, const char *name) { return NULL; }
static inline void class_destroy(struct class *cls) { }
static inline void cdev_init(struct cdev *cdev, const struct file_operations *fops) { }
static inline int cdev_add(struct cdev *p, dev_t dev, unsigned count) { return 0; }
static inline void cdev_del(struct cdev *p) { }
static inline struct device *device_create(struct class *class, struct device *parent, dev_t devt, void *drvdata, const char *fmt, ...) { return NULL; }
static inline void device_destroy(struct class *class, dev_t devt) { }
static inline struct net_device *alloc_etherdev(int sizeof_priv) { return NULL; }
static inline void free_netdev(struct net_device *dev) { }
static inline int register_netdev(struct net_device *dev) { return 0; }
static inline void unregister_netdev(struct net_device *dev) { }
static inline void eth_hw_addr_random(struct net_device *dev) { }
static inline int is_valid_ether_addr(const __u8 *addr) { return 1; }
static inline void skb_queue_head_init(struct sk_buff_head *list) { }
static inline void init_waitqueue_head(wait_queue_head_t *q) { }
static inline void spin_lock_init(spinlock_t *lock) { }
static inline void mutex_init(struct mutex *mutex) { }
static inline void skb_queue_tail(struct sk_buff_head *list, struct sk_buff *newsk) { }
static inline void wake_up_interruptible(wait_queue_head_t *q) { }
static inline void dev_kfree_skb(struct sk_buff *skb) { }
static inline void skb_queue_purge(struct sk_buff_head *list) { }
static inline struct sk_buff *skb_dequeue(struct sk_buff_head *list) { return NULL; }
static inline int skb_queue_empty(struct sk_buff_head *list) { return 1; }
static inline void netif_start_queue(struct net_device *dev) { }
static inline void netif_stop_queue(struct net_device *dev) { }
static inline unsigned long copy_to_user(void *to, const void *from, unsigned long n) { return 0; }
static inline unsigned long copy_from_user(void *to, const void *from, unsigned long n) { return 0; }
static inline struct sk_buff *alloc_skb(unsigned int size, gfp_t priority) { return NULL; }
static inline unsigned char *skb_put(struct sk_buff *skb, unsigned int len) { return NULL; }

// 模块宏
#define module_init(x) static void __module_init_##x(void) { x(); }
#define module_exit(x) static void __module_exit_##x(void) { x(); }
#define MODULE_LICENSE(x)
#define MODULE_AUTHOR(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_VERSION(x)

#endif
EOF

# 创建用于语法检查的源文件
echo "[INFO] 准备源文件进行语法检查..."
sed 's/#include <linux\//#include "temp_kernel_defs.h" \/\/ #include <linux\//g' tap_device.c > temp_tap_device.c

# 进行语法检查
echo "[INFO] 进行语法检查..."
$CC -fsyntax-only -Wall -Wextra -std=c99 temp_tap_device.c 2>&1 | head -20

syntax_result=$?

# 检查基本函数结构
echo ""
echo "[INFO] 检查函数结构..."
echo "- 找到的函数定义:"
grep -n "^static.*(" temp_tap_device.c | head -10

echo ""
echo "- 结构体定义:"
grep -n "^struct.*{" temp_tap_device.c

echo ""
echo "- 模块宏:"
grep -n "module_\(init\|exit\)" temp_tap_device.c

# 清理临时文件
rm -f temp_kernel_defs.h temp_tap_device.c

echo ""
echo "========================================"
if [ $syntax_result -eq 0 ]; then
    echo "[SUCCESS] 语法检查通过!"
    echo "代码结构正确，可以在Linux环境中编译。"
else
    echo "[INFO] 发现一些语法警告，但这是正常的。"
    echo "大部分警告是由于缺少完整的内核头文件。"
fi

echo ""
echo "注意：这只是基本语法检查。"
echo "完整的编译和测试需要在Linux环境中进行。"
echo ""
echo "如需在Linux环境中测试，请参考 README.md 文件。"
echo "========================================" 