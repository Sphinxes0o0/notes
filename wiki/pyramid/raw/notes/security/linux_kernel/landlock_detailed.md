# Linux Kernel Landlock 安全模块详细分析

## 目录

1. [Landlock 概述](#1-landlock-概述)
2. [核心数据结构](#2-核心数据结构)
3. [规则集管理](#3-规则集管理)
4. [文件系统访问控制](#4-文件系统访问控制)
5. [网络访问控制](#5-网络访问控制)
6. [作用域限制](#6-作用域限制)
7. [层级限制与继承模型](#7-层级限制与继承模型)
8. [系统调用接口](#8-系统调用接口)
9. [LSM Hooks 架构](#9-lsm-hooks-架构)
10. [审计日志](#10-审计日志)

---

## 1. Landlock 概述

### 1.1 什么是 Landlock

Landlock 是 Linux 内核中的一个 **用户空间安全模块 (Userspace Security Module)**，提供基于 **沙箱 (Sandbox)** 的访问控制机制。它允许非特权进程自愿限制自己对系统资源的访问能力。

**关键特性:**
- **无特权沙箱**: 不需要 CAP_SYS_ADMIN 即可创建基本限制
- **层级化策略**: 支持最多 16 层规则叠加 (LANDLOCK_MAX_NUM_LAYERS)
- **基于路径**: 通过文件系统路径而非 inode 来定义规则
- **不可绕过**: 一旦应用，限制无法被移除（只能叠加新层）

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Space                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │landlock_create│  │landlock_add │  │landlock_restrict_self  │ │
│  │  _ruleset() │  │   _rule()   │  │                         │ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     System Calls                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  sys_landlock_create_ruleset()                              ││
│  │  sys_landlock_add_rule()                                    ││
│  │  sys_landlock_restrict_self()                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Landlock LSM Core                              │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │   ruleset.c    │  │     fs.c       │  │     net.c      │  │
│  │  - 创建规则集  │  │ - 文件系统hooks│  │ - 网络hooks    │  │
│  │  - 添加规则   │  │ - 路径检查     │  │ - 端口检查     │  │
│  │  - 合并规则集 │  │ - inode管理    │  │               │  │
│  └───────┬────────┘  └───────┬────────┘  └────────┬────────┘  │
│          │                   │                    │            │
│  ┌───────▼───────────────────▼────────────────────▼──────────┐ │
│  │                    access.h / ruleset.h                   │ │
│  │              (核心数据结构和辅助函数)                       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kernel LSM Framework                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ inode hooks │  │  file hooks │  │ sock hooks  │             │
│  │ path hooks  │  │  sb hooks   │  │ cred hooks  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 访问权限类型

**文件系统访问权限** (定义于 `include/uapi/linux/landlock.h:319-336`):

```c
#define LANDLOCK_ACCESS_FS_EXECUTE         (1ULL << 0)  // 执行文件
#define LANDLOCK_ACCESS_FS_WRITE_FILE       (1ULL << 1)  // 写文件
#define LANDLOCK_ACCESS_FS_READ_FILE        (1ULL << 2)  // 读文件
#define LANDLOCK_ACCESS_FS_READ_DIR         (1ULL << 3)  // 读目录
#define LANDLOCK_ACCESS_FS_REMOVE_DIR       (1ULL << 4)  // 删除目录
#define LANDLOCK_ACCESS_FS_REMOVE_FILE      (1ULL << 5)  // 删除文件
#define LANDLOCK_ACCESS_FS_MAKE_CHAR        (1ULL << 6)  // 创建字符设备
#define LANDLOCK_ACCESS_FS_MAKE_DIR         (1ULL << 7)  // 创建目录
#define LANDLOCK_ACCESS_FS_MAKE_REG         (1ULL << 8)  // 创建普通文件
#define LANDLOCK_ACCESS_FS_MAKE_SOCK        (1ULL << 9)  // 创建套接字
#define LANDLOCK_ACCESS_FS_MAKE_FIFO        (1ULL << 10) // 创建命名管道
#define LANDLOCK_ACCESS_FS_MAKE_BLOCK      (1ULL << 11) // 创建块设备
#define LANDLOCK_ACCESS_FS_MAKE_SYM        (1ULL << 12) // 创建符号链接
#define LANDLOCK_ACCESS_FS_REFER            (1ULL << 13) // 重命名/链接(跨目录)
#define LANDLOCK_ACCESS_FS_TRUNCATE         (1ULL << 14) // 截断文件
#define LANDLOCK_ACCESS_FS_IOCTL_DEV        (1ULL << 15) // 设备IOCTL
```

**网络访问权限** (`landlock.h:354-357`):
```c
#define LANDLOCK_ACCESS_NET_BIND_TCP        (1ULL << 0)  // 绑定TCP端口
#define LANDLOCK_ACCESS_NET_CONNECT_TCP     (1ULL << 1)  // 连接TCP端口
```

**作用域标志** (`landlock.h:379-382`):
```c
#define LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET (1ULL << 0)  // 抽象Unix域套接字
#define LANDLOCK_SCOPE_SIGNAL               (1ULL << 1)  // 信号
```

---

## 2. 核心数据结构

### 2.1 landlock_object - 底层对象管理

**文件:** `security/landlock/object.h:29-77`

```c
struct landlock_object {
    refcount_t usage;              // 引用计数
    spinlock_t lock;                // 保护并发访问
    void *underobj;                 // 底层内核对象(如inode)
    union {
        struct rcu_head rcu_free;  // RCU释放
        const struct landlock_object_underops *underops;  // 底层对象操作
    };
};
```

**关键设计:**
- 使用引用计数管理生命周期
- RCU (Read-Copy-Update) 支持无锁读取
- `underops->release()` 释放底层对象 (如 inode)

### 2.2 landlock_ruleset - 规则集结构

**文件:** `security/landlock/ruleset.h:113-190`

```c
struct landlock_ruleset {
    // 红黑树根节点 - inode 类型规则
    struct rb_root root_inode;

#if IS_ENABLED(CONFIG_INET)
    // 红黑树根节点 - 网络端口类型规则
    struct rb_root root_net_port;
#endif

    // 层级结构 - 支持域继承和ptrace保护
    struct landlock_hierarchy *hierarchy;

    union {
        struct work_struct work_free;  // 延迟释放工作
        struct {
            struct mutex lock;         // 保护规则集修改
            refcount_t usage;          // 引用计数
            u32 num_rules;             // 规则数量
            u32 num_layers;            // 层级数量
            // 灵活数组成员 - 每层的访问掩码
            struct access_masks access_masks[];
        };
    };
};
```

### 2.3 landlock_rule - 单条规则

**文件:** `security/landlock/ruleset.h:86-111`

```c
struct landlock_rule {
    struct rb_node node;           // 红黑树节点
    union landlock_key key;        // 规则关键字(object或data)
    u32 num_layers;                // 层数
    // 灵活数组 - 每层允许的访问权限
    struct landlock_layer layers[] __counted_by(num_layers);
};

struct landlock_layer {
    u16 level;                     // 层级位置(从1开始)
    access_mask_t access;          // 允许的访问权限位域
};

union landlock_key {
    struct landlock_object *object; // inode对象指针
    uintptr_t data;                 // 原始数据(如TCP端口)
};
```

### 2.4 landlock_cred_security - 凭证安全 blob

**文件:** `security/landlock/cred.h:32-53`

```c
struct landlock_cred_security {
    struct landlock_ruleset *domain;  // 不可变规则集
#ifdef CONFIG_AUDIT
    u16 domain_exec;                  // 执行时域层位掩码
    u8 log_subdomains_off : 1;        // 子域日志开关
#endif
} __packed;
```

### 2.5 landlock_hierarchy - 层级继承

**文件:** `security/landlock/domain.h:73-118`

```c
struct landlock_hierarchy {
    struct landlock_hierarchy *parent;  // 父节点
    refcount_t usage;                   // 引用计数
#ifdef CONFIG_AUDIT
    enum landlock_log_status log_status;
    atomic64_t num_denials;             // 拒绝计数
    u64 id;                             // 域ID
    const struct landlock_details *details;
    u32 log_same_exec : 1;
    u32 log_new_exec : 1;
#endif
};
```

---

## 3. 规则集管理

### 3.1 创建规则集 - landlock_create_ruleset()

**文件:** `security/landlock/ruleset.c:56-76`

```c
struct landlock_ruleset *
landlock_create_ruleset(const access_mask_t fs_access_mask,
                      const access_mask_t net_access_mask,
                      const access_mask_t scope_mask)
{
    struct landlock_ruleset *new_ruleset;

    // 空规则集检查
    if (!fs_access_mask && !net_access_mask && !scope_mask)
        return ERR_PTR(-ENOMSG);

    // 创建单层规则集
    new_ruleset = create_ruleset(1);
    if (IS_ERR(new_ruleset))
        return new_ruleset;

    // 设置各类型访问掩码
    if (fs_access_mask)
        landlock_add_fs_access_mask(new_ruleset, fs_access_mask, 0);
    if (net_access_mask)
        landlock_add_net_access_mask(new_ruleset, net_access_mask, 0);
    if (scope_mask)
        landlock_add_scope_mask(new_ruleset, scope_mask, 0);

    return new_ruleset;
}
```

**create_ruleset()** 内部实现 (`ruleset.c:31-54`):

```c
static struct landlock_ruleset *create_ruleset(const u32 num_layers)
{
    struct landlock_ruleset *new_ruleset;

    // 使用灵活数组分配 - access_masks[num_layers]
    new_ruleset = kzalloc_flex(*new_ruleset, access_masks, num_layers,
                               GFP_KERNEL_ACCOUNT);
    if (!new_ruleset)
        return ERR_PTR(-ENOMEM);

    refcount_set(&new_ruleset->usage, 1);
    mutex_init(&new_ruleset->lock);
    new_ruleset->root_inode = RB_ROOT;

#if IS_ENABLED(CONFIG_INET)
    new_ruleset->root_net_port = RB_ROOT;
#endif

    new_ruleset->num_layers = num_layers;
    // hierarchy = NULL, num_rules = 0, access_masks[] = 0
    return new_ruleset;
}
```

### 3.2 插入规则 - landlock_insert_rule()

**文件:** `security/landlock/ruleset.c:304-316`

```c
int landlock_insert_rule(struct landlock_ruleset *const ruleset,
                        const struct landlock_id id,
                        const access_mask_t access)
{
    struct landlock_layer layers[] = { {
        .access = access,
        .level = 0,  // level=0 表示扩展规则集
    } };

    build_check_layer();
    return insert_rule(ruleset, id, &layers, ARRAY_SIZE(layers));
}
```

**insert_rule()** - 红黑树插入 (`ruleset.c:205-286`):

```c
static int insert_rule(struct landlock_ruleset *const ruleset,
                      const struct landlock_id id,
                      const struct landlock_layer (*const layers)[],
                      const size_t num_layers)
{
    struct rb_node **walker_node;
    struct rb_node *parent_node = NULL;
    struct landlock_rule *new_rule;
    struct rb_root *root;

    root = get_root(ruleset, id.type);
    if (IS_ERR(root))
        return PTR_ERR(root);

    walker_node = &root->rb_node;
    while (*walker_node) {
        struct landlock_rule *const this =
            rb_entry(*walker_node, struct landlock_rule, node);

        // 比较关键字 - 按data值排序
        if (this->key.data != id.key.data) {
            parent_node = *walker_node;
            if (this->key.data < id.key.data)
                walker_node = &((*walker_node)->rb_right);
            else
                walker_node = &((*walker_node)->rb_left);
            continue;
        }

        // 找到匹配规则 - level=0 表示扩展访问权限
        if ((*layers)[0].level == 0) {
            this->layers[0].access |= (*layers)[0].access;
            return 0;
        }

        // 层级合并 - 取交集
        new_rule = create_rule(id, &this->layers, this->num_layers,
                               &(*layers)[0]);
        rb_replace_node(&this->node, &new_rule->node, root);
        free_rule(this, id.type);
        return 0;
    }

    // 没有匹配规则 - 创建新规则
    new_rule = create_rule(id, layers, num_layers, NULL);
    rb_link_node(&new_rule->node, parent_node, walker_node);
    rb_insert_color(&new_rule->node, root);
    ruleset->num_rules++;
    return 0;
}
```

### 3.3 合并规则集 - landlock_merge_ruleset()

**文件:** `security/landlock/ruleset.c:536-583`

```c
struct landlock_ruleset *
landlock_merge_ruleset(struct landlock_ruleset *const parent,
                      struct landlock_ruleset *const ruleset)
{
    struct landlock_ruleset *new_dom = create_ruleset(num_layers);
    // ...
    // 1. 继承父规则集
    err = inherit_ruleset(parent, new_dom);

    // 2. 合并新规则集
    err = merge_ruleset(new_dom, ruleset);

    // 3. 初始化层级日志
    err = landlock_init_hierarchy_log(new_dom->hierarchy);

    return new_dom;
}
```

**inherit_ruleset()** - 复制父规则 (`ruleset.c:435-479`):

```c
static int inherit_ruleset(struct landlock_ruleset *parent,
                           struct landlock_ruleset *child)
{
    // 复制inode树
    err = inherit_tree(parent, child, LANDLOCK_KEY_INODE);

#if IS_ENABLED(CONFIG_INET)
    // 复制网络端口树
    err = inherit_tree(parent, child, LANDLOCK_KEY_NET_PORT);
#endif

    // 复制父层掩码
    memcpy(child->access_masks, parent->access_masks, ...);

    // 设置父子关系
    child->hierarchy->parent = parent->hierarchy;
    return 0;
}
```

### 3.4 层级掩码操作

**landlock_unmask_layers()** (`ruleset.c:628-658`):

```c
bool landlock_unmask_layers(const struct landlock_rule *rule,
                           struct layer_access_masks *masks)
{
    // 清除规则授予的访问权限
    for (size_t i = 0; i < rule->num_layers; i++) {
        const struct landlock_layer *layer = &rule->layers[i];
        masks->access[layer->level - 1] &= ~layer->access;
    }

    // 检查是否所有层级都满足
    for (size_t i = 0; i < ARRAY_SIZE(masks->access); i++) {
        if (masks->access[i])
            return false;  // 还有未满足的权限
    }
    return true;  // 所有权限都已满足
}
```

---

## 4. 文件系统访问控制

### 4.1 FS Hooks 初始化

**文件:** `security/landlock/fs.c:1823-1855`

```c
static struct security_hook_list landlock_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(inode_free_security_rcu, hook_inode_free_security_rcu),

    LSM_HOOK_INIT(sb_delete, hook_sb_delete),
    LSM_HOOK_INIT(sb_mount, hook_sb_mount),
    LSM_HOOK_INIT(move_mount, hook_move_mount),
    LSM_HOOK_INIT(sb_umount, hook_sb_umount),
    LSM_HOOK_INIT(sb_remount, hook_sb_remount),
    LSM_HOOK_INIT(sb_pivotroot, hook_sb_pivotroot),

    LSM_HOOK_INIT(path_link, hook_path_link),
    LSM_HOOK_INIT(path_rename, hook_path_rename),
    LSM_HOOK_INIT(path_mkdir, hook_path_mkdir),
    LSM_HOOK_INIT(path_mknod, hook_path_mknod),
    LSM_HOOK_INIT(path_symlink, hook_path_symlink),
    LSM_HOOK_INIT(path_unlink, hook_path_unlink),
    LSM_HOOK_INIT(path_rmdir, hook_path_rmdir),
    LSM_HOOK_INIT(path_truncate, hook_path_truncate),

    LSM_HOOK_INIT(file_alloc_security, hook_file_alloc_security),
    LSM_HOOK_INIT(file_open, hook_file_open),
    LSM_HOOK_INIT(file_truncate, hook_file_truncate),
    LSM_HOOK_INIT(file_ioctl, hook_file_ioctl),
    LSM_HOOK_INIT(file_ioctl_compat, hook_file_ioctl_compat),
    LSM_HOOK_INIT(file_set_fowner, hook_file_set_fowner),
    LSM_HOOK_INIT(file_free_security, hook_file_free_security),
};

__init void landlock_add_fs_hooks(void)
{
    security_add_hooks(landlock_hooks, ARRAY_SIZE(landlock_hooks),
                       &landlock_lsmid);
}
```

### 4.2 文件打开检查 - hook_file_open()

**文件:** `security/landlock/fs.c:1614-1680`

```c
static int hook_file_open(struct file *const file)
{
    access_mask_t open_access_request, full_access_request, allowed_access;
    const struct landlock_cred_security *subject =
        landlock_get_applicable_subject(file->f_cred, any_fs, NULL);

    // 获取打开文件所需的访问权限
    open_access_request = get_required_file_open_access(file);

    // 预取额外权限用于后续操作
    optional_access = LANDLOCK_ACCESS_FS_TRUNCATE;
    if (is_device(file))
        optional_access |= LANDLOCK_ACCESS_FS_IOCTL_DEV;

    full_access_request = open_access_request | optional_access;

    // 检查路径访问权限
    if (is_access_to_paths_allowed(...)) {
        allowed_access = full_access_request;
    } else {
        // 计算实际允许的访问权限
        allowed_access = full_access_request;
        for (size_t i = 0; i < ARRAY_SIZE(layer_masks.access); i++)
            allowed_access &= ~layer_masks.access[i];
    }

    // 记录在文件结构中供后续使用
    landlock_file(file)->allowed_access = allowed_access;

    if (access_mask_subset(open_access_request, allowed_access))
        return 0;

    // 权限不足 - 记录拒绝
    return -EACCES;
}
```

### 4.3 路径访问检查 - is_access_to_paths_allowed()

**文件:** `security/landlock/fs.c:741-944`

这是 Landlock 文件系统检查的核心函数,实现了 **多层安全 (MLS)** 检查:

```c
static bool is_access_to_paths_allowed(
    const struct landlock_ruleset *domain,
    const struct path *path,
    access_mask_t access_request_parent1,
    struct layer_access_masks *layer_masks_parent1,
    ...
    access_mask_t access_request_parent2,
    struct layer_access_masks *layer_masks_parent2,
    ...)
{
    // 遍历路径从叶节点到根
    while (true) {
        const struct landlock_rule *rule;

        // 查找当前dentry的规则
        rule = find_rule(domain, walker_path.dentry);

        // 检查每层是否满足访问请求
        allowed_parent1 = landlock_unmask_layers(rule, layer_masks_parent1);
        allowed_parent2 = landlock_unmask_layers(rule, layer_masks_parent2);

        if (allowed_parent1 && allowed_parent2)
            break;  // 所有层都满足,允许访问

        // 向上遍历到父目录
        if (walker_path.dentry == walker_path.mnt->mnt_root) {
            if (follow_up(&walker_path)) {
                goto jump_up;
            } else {
                break;  // 到达真实根目录
            }
        }
        // ...
    }

    return allowed_parent1 && allowed_parent2;
}
```

### 4.4 inode 对象管理

**get_inode_object()** (`fs.c:254-308`):

```c
static struct landlock_object *get_inode_object(struct inode *inode)
{
    struct landlock_object *object, *new_object;
    struct landlock_inode_security *inode_sec = landlock_inode(inode);

    rcu_read_lock();
retry:
    object = rcu_dereference(inode_sec->object);
    if (object) {
        if (likely(refcount_inc_not_zero(&object->usage))) {
            rcu_read_unlock();
            return object;
        }
        // 竞争 - 等待release_inode()完成
        spin_lock(&object->lock);
        spin_unlock(&object->lock);
        goto retry;
    }
    rcu_read_unlock();

    // 创建新对象
    new_object = landlock_create_object(&landlock_fs_underops, inode);
    if (IS_ERR(new_object))
        return new_object;

    spin_lock(&inode->i_lock);
    if (unlikely(rcu_access_pointer(inode_sec->object))) {
        spin_unlock(&inode->i_lock);
        kfree(new_object);
        goto retry;
    }

    ihold(inode);
    rcu_assign_pointer(inode_sec->object, new_object);
    spin_unlock(&inode->i_lock);
    return new_object;
}
```

**release_inode()** (`fs.c:55-92`):

```c
static void release_inode(struct landlock_object *object)
{
    struct inode *inode = object->underobj;

    object->underobj = NULL;

    sb = inode->i_sb;
    atomic_long_inc(&landlock_superblock(sb)->inode_refs);

    rcu_assign_pointer(landlock_inode(inode)->object, NULL);

    iput(inode);  // 释放inode引用

    if (atomic_long_dec_and_test(&landlock_superblock(sb)->inode_refs))
        wake_up_var(...);  // 唤醒等待者
}
```

### 4.5 挂载拓扑变更检测

**文件:** `security/landlock/fs.c:1420-1504`

Landlock 禁止沙箱进程修改文件系统拓扑:

```c
static int hook_sb_mount(const char *dev_name, const struct path *path,
                        const char *type, unsigned long flags, void *data)
{
    const struct landlock_cred_security *subject =
        landlock_get_applicable_subject(current_cred(), any_fs, &handle_layer);

    if (!subject)
        return 0;

    log_fs_change_topology_path(subject, handle_layer, path);
    return -EPERM;  // 永远拒绝
}
```

**受保护的挂载操作:**
- `hook_sb_mount()` - 挂载文件系统
- `hook_move_mount()` - 移动挂载点
- `hook_sb_umount()` - 卸载文件系统
- `hook_sb_remount()` - 重新挂载
- `hook_sb_pivotroot()` - pivot_root

---

## 5. 网络访问控制

### 5.1 网络 Hooks

**文件:** `security/landlock/net.c:241-250`

```c
static struct security_hook_list landlock_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(socket_bind, hook_socket_bind),
    LSM_HOOK_INIT(socket_connect, hook_socket_connect),
};

__init void landlock_add_net_hooks(void)
{
    security_add_hooks(landlock_hooks, ARRAY_SIZE(landlock_hooks),
                       &landlock_lsmid);
}
```

### 5.2 端口规则检查 - current_check_access_socket()

**文件:** `security/landlock/net.c:44-210`

```c
static int current_check_access_socket(struct socket *sock,
                                     struct sockaddr *address,
                                     int addrlen,
                                     access_mask_t access_request)
{
    __be16 port;
    struct layer_access_masks layer_masks = {};
    struct landlock_id id = {
        .type = LANDLOCK_KEY_NET_PORT,
    };

    // 从地址提取端口
    switch (address->sa_family) {
    case AF_INET: {
        const struct sockaddr_in *addr4 = (struct sockaddr_in *)address;
        port = addr4->sin_port;
        // 审计信息...
        break;
    }
#if IS_ENABLED(CONFIG_IPV6)
    case AF_INET6: {
        const struct sockaddr_in6 *addr6 = (struct sockaddr_in6 *)address;
        port = addr6->sin6_port;
        break;
    }
#endif
    default:
        return 0;
    }

    id.key.data = (__force uintptr_t)port;

    // 查找规则
    rule = landlock_find_rule(subject->domain, id);
    access_request = landlock_init_layer_masks(...);

    if (landlock_unmask_layers(rule, &layer_masks))
        return 0;  // 允许

    // 记录拒绝
    landlock_log_denial(subject, &request);
    return -EACCES;
}
```

### 5.3 添加网络规则 - landlock_append_net_rule()

**文件:** `security/landlock/net.c:22-42`

```c
int landlock_append_net_rule(struct landlock_ruleset *ruleset,
                            u16 port, access_mask_t access_rights)
{
    const struct landlock_id id = {
        .key.data = (__force uintptr_t)htons(port),
        .type = LANDLOCK_KEY_NET_PORT,
    };

    // 转换为绝对访问权限
    access_rights |= LANDLOCK_MASK_ACCESS_NET &
                     ~landlock_get_net_access_mask(ruleset, 0);

    mutex_lock(&ruleset->lock);
    err = landlock_insert_rule(ruleset, id, access_rights);
    mutex_unlock(&ruleset->lock);

    return err;
}
```

---

## 6. 作用域限制

### 6.1 作用域标志

**文件:** `security/landlock/task.c`

Landlock 支持两种作用域限制:

1. **LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET** - 限制访问抽象Unix域套接字
2. **LANDLOCK_SCOPE_SIGNAL** - 限制发送信号

### 6.2 作用域检查 - domain_is_scoped()

**文件:** `security/landlock/task.c:169-233`

```c
static bool domain_is_scoped(const struct landlock_ruleset *client,
                            const struct landlock_ruleset *server,
                            access_mask_t scope)
{
    int client_layer, server_layer;
    const struct landlock_hierarchy *client_walker, *server_walker;

    client_layer = client->num_layers - 1;
    client_walker = client->hierarchy;

    server_layer = server ? (server->num_layers - 1) : -1;
    server_walker = server ? server->hierarchy : NULL;

    // 遍历客户端的层级
    for (; client_layer > server_layer; client_layer--) {
        if (landlock_get_scope_mask(client, client_layer) & scope)
            return true;  // 客户端在作用域内
        client_walker = client_walker->parent;
    }

    // 遍历到相同层级
    for (; server_layer > client_layer; server_layer--)
        server_walker = server_walker->parent;

    for (; client_layer >= 0; client_layer--) {
        if (landlock_get_scope_mask(client, client_layer) & scope) {
            // 客户端和服务器在同一层级
            return server_walker != client_walker;
        }
        client_walker = client_walker->parent;
        server_walker = server_walker->parent;
    }
    return false;
}
```

### 6.3 信号限制 - hook_task_kill()

**文件:** `security/landlock/task.c:338-388`

```c
static int hook_task_kill(struct task_struct *p,
                         struct kernel_siginfo *info, int sig,
                         const struct cred *cred)
{
    const struct landlock_cred_security *subject;
    bool is_scoped;

    // 同线程组内始终允许
    if (same_thread_group(p, current))
        return 0;

    subject = landlock_get_applicable_subject(cred, signal_scope, ...);

    is_scoped = domain_is_scoped(subject->domain,
                                  landlock_get_task_domain(p),
                                  LANDLOCK_SCOPE_SIGNAL);

    if (!is_scoped)
        return 0;

    landlock_log_denial(subject, &request);
    return -EPERM;
}
```

### 6.4 Unix 域套接字限制

**hook_unix_stream_connect()** (`task.c:265-295`):

```c
static int hook_unix_stream_connect(struct sock *sock, struct sock *other,
                                   struct sock *newsk)
{
    if (!is_abstract_socket(other))
        return 0;

    if (!sock_is_scoped(other, subject->domain))
        return 0;

    return -EPERM;
}
```

---

## 7. 层级限制与继承模型

### 7.1 层级架构图

```
                    ┌─────────────────────────────────────────┐
                    │          Domain (层叠规则集)             │
                    │  ┌─────────────────────────────────────┐ │
                    │  │ Layer N (最新层)                    │ │
                    │  │  - access_masks[N]                 │ │
                    │  │  - 规则: /a/b -> rw                │ │
                    │  └─────────────────────────────────────┘ │
                    │  ┌─────────────────────────────────────┐ │
                    │  │ Layer N-1                           │ │
                    │  │  - access_masks[N-1]               │ │
                    │  │  - 规则: /a -> rwx                 │ │
                    │  └─────────────────────────────────────┘ │
                    │              ...                       │
                    │  ┌─────────────────────────────────────┐ │
                    │  │ Layer 0 (最初层)                     │ │
                    │  │  - access_masks[0]                  │ │
                    │  │  - 规则: / -> rx                    │ │
                    │  └─────────────────────────────────────┘ │
                    └─────────────────────────────────────────┘
                                    │
                                    │ inherit_ruleset()
                                    ▼
                    ┌─────────────────────────────────────────┐
                    │          Child Domain                   │
                    │  (继承所有父层 + 新增层)                 │
                    │  - num_layers = parent.num_layers + 1   │
                    │  - hierarchy.parent = parent.hierarchy   │
                    └─────────────────────────────────────────┘
```

### 7.2 访问检查语义

**关键规则:** 对于每一层(per-layer),必须至少有一条规则授予请求的访问权限。

```
请求: 对 /a/b/c 的读文件权限

Layer 2: /a/b 有 read 规则 ✓
Layer 1: /a 有 read 规则 ✓
Layer 0: / 有 read 规则 ✓

结果: 允许 (每层都满足)
```

### 7.3 Ptrace 保护

**文件:** `security/landlock/task.c:63-70`

```c
static int domain_ptrace(const struct landlock_ruleset *parent,
                        const struct landlock_ruleset *child)
{
    // 检查父域是否是子域的祖先
    if (domain_scope_le(parent, child))
        return 0;  // 允许 - parent是child的祖先

    return -EPERM;  // 拒绝
}
```

**domain_scope_le()** (`task.c:41-61`):

```c
static bool domain_scope_le(const struct landlock_ruleset *parent,
                           const struct landlock_ruleset *child)
{
    const struct landlock_hierarchy *walker;

    if (!parent)
        return true;  // 非沙箱进程可以追踪

    if (!child)
        return false;

    // 遍历子域的层级链
    for (walker = child->hierarchy; walker; walker = walker->parent) {
        if (walker == parent->hierarchy)
            return true;  // parent是child的祖先
    }
    return false;
}
```

---

## 8. 系统调用接口

### 8.1 landlock_create_ruleset()

**文件:** `security/landlock/syscalls.c:198-260`

```c
SYSCALL_DEFINE3(landlock_create_ruleset,
               const struct landlock_ruleset_attr __user *, attr,
               const size_t, size, const __u32, flags)
{
    struct landlock_ruleset_attr ruleset_attr;
    struct landlock_ruleset *ruleset;

    if (!is_initialized())
        return -EOPNOTSUPP;

    // 获取ABI版本
    if (flags == LANDLOCK_CREATE_RULESET_VERSION)
        return landlock_abi_version;

    // 获取errata
    if (flags == LANDLOCK_CREATE_RULESET_ERRATA)
        return landlock_errata;

    // 复制用户空间结构
    err = copy_min_struct_from_user(&ruleset_attr, sizeof(ruleset_attr), ...);
    if (err)
        return err;

    // 验证访问权限掩码
    if ((ruleset_attr.handled_access_fs | LANDLOCK_MASK_ACCESS_FS) !=
        LANDLOCK_MASK_ACCESS_FS)
        return -EINVAL;

    // 创建规则集
    ruleset = landlock_create_ruleset(ruleset_attr.handled_access_fs,
                                      ruleset_attr.handled_access_net,
                                      ruleset_attr.scoped);

    // 创建匿名FD
    ruleset_fd = anon_inode_getfd("[landlock-ruleset]", &ruleset_fops,
                                  ruleset, O_RDWR | O_CLOEXEC);
    return ruleset_fd;
}
```

### 8.2 landlock_add_rule()

**文件:** `security/landlock/syscalls.c:421-447`

```c
SYSCALL_DEFINE4(landlock_add_rule, const int, ruleset_fd,
               const enum landlock_rule_type, rule_type,
               const void __user *const, rule_attr, const __u32, flags)
{
    ruleset = get_ruleset_from_fd(ruleset_fd, FMODE_CAN_WRITE);
    if (IS_ERR(ruleset))
        return PTR_ERR(ruleset);

    switch (rule_type) {
    case LANDLOCK_RULE_PATH_BENEATH:
        return add_rule_path_beneath(ruleset, rule_attr);
    case LANDLOCK_RULE_NET_PORT:
        return add_rule_net_port(ruleset, rule_attr);
    default:
        return -EINVAL;
    }
}
```

### 8.3 landlock_restrict_self()

**文件:** `security/landlock/syscalls.c:482-583`

```c
SYSCALL_DEFINE2(landlock_restrict_self, const int, ruleset_fd, const __u32, flags)
{
    // 权限检查
    if (!task_no_new_privs(current) &&
        !ns_capable_noaudit(current_user_ns(), CAP_SYS_ADMIN))
        return -EPERM;

    // 获取规则集
    ruleset = get_ruleset_from_fd(ruleset_fd, FMODE_CAN_READ);

    // 准备新凭证
    new_cred = prepare_creds();
    new_llcred = landlock_cred(new_cred);

    // 合并规则集
    new_dom = landlock_merge_ruleset(new_llcred->domain, ruleset);

    // 更新凭证
    new_llcred->domain = new_dom;

    // 线程同步(如果需要)
    if (flags & LANDLOCK_RESTRICT_SELF_TSYNC) {
        err = landlock_restrict_sibling_threads(current_cred(), new_cred);
        if (err) {
            abort_creds(new_cred);
            return err;
        }
    }

    return commit_creds(new_cred);
}
```

---

## 9. LSM Hooks 架构

### 9.1 Hook 注册

**文件:** `security/landlock/setup.c`

```c
extern struct lsm_blob_sizes landlock_blob_sizes;
extern const struct lsm_id landlock_lsmid;
```

### 9.2 Blob 大小

在 `security/landlock/` 初始化时设置:

```c
landlock_blob_sizes.lbs_cred = sizeof(struct landlock_cred_security);
landlock_blob_sizes.lbs_file = sizeof(struct landlock_file_security);
landlock_blob_sizes.lbs_inode = sizeof(struct landlock_inode_security);
landlock_blob_sizes.lbs_superblock = sizeof(struct landlock_superblock_security);
```

### 9.3 Hook 调用流程

```
应用进程
    │
    ▼
sys_landlock_restrict_self()
    │
    ▼
commit_creds()  ─────────────────────────────────────┐
    │                                                │
    ▼                                                │
landlock_cred(new_cred)->domain = new_dom            │
    │                                                │
    ▼                                                │
进程执行系统调用                                      │
    │                                                │
    ▼                                                │
VFS 调用                                              │
    │                                                │
    ▼                                                │
Landlock LSM Hook (如 hook_file_open)                │
    │                                                │
    ├── landlock_get_applicable_subject()            │
    │     │                                         │
    │     └── 检查 domain 是否处理请求的访问权限     │
    │                                                │
    ├── is_access_to_paths_allowed()                │
    │     │                                         │
    │     ├── 从路径向下到根遍历                     │
    │     ├── 对每层检查规则                         │
    │     └── landlock_unmask_layers()              │
    │                                                │
    └── 返回 0 (允许) 或 -EACCES (拒绝)              │
                                                   │
                           ┌────────────────────────┘
                           │
                           ▼
                      hook_file_free_security()
                      清理资源
```

---

## 10. 审计日志

### 10.1 拒绝日志 - landlock_log_denial()

**文件:** `security/landlock/audit.c` (假设存在)

### 10.2 日志配置

**域层级日志状态:**

```c
enum landlock_log_status {
    LANDLOCK_LOG_PENDING = 0,
    LANDLOCK_LOG_RECORDED,
    LANDLOCK_LOG_DISABLED,
};
```

**日志标志:**

```c
#define LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF   (1U << 0)
#define LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON     (1U << 1)
#define LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF  (1U << 2)
```

---

## 11. 关键限制

### 11.1 系统限制

**文件:** `security/landlock/limits.h`

```c
#define LANDLOCK_MAX_NUM_LAYERS     16      // 最大层级数
#define LANDLOCK_MAX_NUM_RULES     U32_MAX // 最大规则数

// 访问权限数量
#define LANDLOCK_NUM_ACCESS_FS      __const_hweight64(LANDLOCK_MASK_ACCESS_FS)
#define LANDLOCK_NUM_ACCESS_NET    __const_hweight64(LANDLOCK_MASK_ACCESS_NET)
#define LANDLOCK_NUM_SCOPE         __const_hweight64(LANDLOCK_MASK_SCOPE)
```

### 11.2 ABI 版本

**当前版本:** `landlock_abi_version = 8` (`syscalls.c:167`)

---

## 12. 总结

### 12.1 核心设计原则

1. **层级化安全**: 每层必须独立满足访问请求
2. **基于路径**: 通过文件系统路径而非 inode 绑定规则
3. **不可绕过**: 限制一旦应用,无法移除
4. **最小权限**: 默认拒绝所有未明确允许的访问
5. **无特权沙箱**: 基本限制不需要 CAP_SYS_ADMIN

### 12.2 数据流

```
用户空间                    内核空间
   │                           │
   ├── landlock_create_ruleset() ──→ 创建规则集结构
   │                                 (分配 landlock_ruleset)
   │
   ├── landlock_add_rule() ──────→ 插入规则到规则集
   │                                 (添加到红黑树)
   │
   └── landlock_restrict_self() ─→ 合并规则集到域
                                     (创建新 domain)
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │   凭证更新           │
                              │ landlock_cred()->    │
                              │ domain = new_domain  │
                              └──────────────────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │   访问检查           │
                              │ hook_file_open()    │
                              │ is_access_to_paths  │
                              │ _allowed()          │
                              └──────────────────────┘
```

---

## 附录: 文件清单

| 文件 | 描述 |
|------|------|
| `security/landlock/ruleset.c` | 规则集管理核心实现 |
| `security/landlock/ruleset.h` | 规则集数据结构定义 |
| `security/landlock/fs.c` | 文件系统 LSM hooks |
| `security/landlock/fs.h` | 文件系统数据结构 |
| `security/landlock/net.c` | 网络 LSM hooks |
| `security/landlock/task.c` | Ptrace 和作用域 hooks |
| `security/landlock/cred.c/h` | 凭证管理 |
| `security/landlock/object.c/h` | 对象生命周期管理 |
| `security/landlock/domain.c/h` | 域和层级管理 |
| `security/landlock/access.h` | 访问权限定义 |
| `security/landlock/limits.h` | 系统限制常量 |
| `security/landlock/syscalls.c` | 系统调用实现 |
| `security/landlock/setup.c/h` | LSM 初始化 |
| `include/uapi/linux/landlock.h` | 用户空间 API |
