# Linux 内核 LSM (Linux Security Module) 框架分析

## 目录

1. [LSM 框架概述](#1-lsm-框架概述)
2. [核心数据结构](#2-核心数据结构)
3. [主要 LSM 模块](#3-主要-lsm-模块)
4. [钩子实现详解](#4-钩子实现详解)
5. [策略加载](#5-策略加载)
6. [架构图](#6-架构图)

---

## 1. LSM 框架概述

### 1.1 设计目标

LSM (Linux Security Module) 是 Linux 内核的安全模块框架,提供了一种可插拔的安全机制。设计目标包括:

- **统一接口**: 为各种安全模块提供统一的钩子接口
- **可扩展性**: 支持多个安全模块同时运行
- **最小化信任**: 核心框架不依赖任何特定安全策略
- **性能优化**: 使用静态调用(static call)机制减少开销

### 1.2 安全钩子机制

LSM 通过在内核关键路径上插入安全钩子来实现访问控制。当内核代码执行敏感操作时,会调用相应的 `security_XXX()` 函数,该函数再调用已注册的 LSM 钩子。

```c
// 安全操作函数示例 (security.c:1813)
int security_inode_permission(struct inode *inode, int mask)
{
    if (unlikely(IS_PRIVATE(inode)))
        return 0;
    return call_int_hook(inode_permission, inode, mask);  // 调用所有已注册的 LSM 钩子
}
```

### 1.3 框架初始化

LSM 框架的初始化流程 (`security/lsm_init.c`):

```
early_security_init()        --> early_initcall
security_init()             --> 初始化 blob 大小、创建缓存
security_initcall_pure()    --> pure_initcall
security_initcall_early()    --> early_initcall
security_initcall_core()    --> core_initcall
security_initcall_subsys()   --> subsys_initcall
security_initcall_fs()       --> fs_initcall
security_initcall_device()   --> device_initcall
security_initcall_late()    --> late_initcall
```

**关键代码** (`security/lsm_init.c:405-485`):

```c
int __init security_init(void)
{
    // 1. 解析 LSM 顺序列表
    if (lsm_order_cmdline)
        lsm_order_parse(lsm_order_cmdline, "cmdline");
    else
        lsm_order_parse(lsm_order_builtin, "builtin");

    // 2. 准备每个 LSM 的 blob 大小
    lsm_order_for_each(lsm)
        lsm_prepare(*lsm);

    // 3. 创建 LSM 缓存
    if (blob_sizes.lbs_file)
        lsm_file_cache = kmem_cache_create("lsm_file_cache", ...);
    if (blob_sizes.lbs_inode)
        lsm_inode_cache = kmem_cache_create("lsm_inode_cache", ...);

    // 4. 分配初始进程的 security blob
    if (lsm_cred_alloc(...))
        panic("early LSM cred alloc failed\n");
    if (lsm_task_alloc(current))
        panic("early LSM task alloc failed\n");

    // 5. 初始化每个 LSM
    lsm_order_for_each(lsm)
        lsm_init_single(*lsm);

    return 0;
}
```

---

## 2. 核心数据结构

### 2.1 LSM_HOOK 宏定义

钩子通过 `LSM_HOOK` 宏在 `include/linux/lsm_hook_defs.h` 中定义:

```c
// 来自 lsm_hook_defs.h:142
LSM_HOOK(int, 0, inode_permission, struct inode *inode, int mask)
LSM_HOOK(int, 0, inode_setattr, struct mnt_idmap *idmap, struct dentry *dentry,
         struct iattr *attr)
LSM_HOOK(int, 0, file_permission, struct file *file, int mask)
LSM_HOOK(int, 0, mmap_file, struct file *file, unsigned long reqprot,
         unsigned long prot, unsigned long flags)
```

**宏展开**:
```c
// 第一个参数: 返回类型
// 第二个参数: 默认值
// 第三个参数: 钩子名称
// 剩余参数: 函数参数
```

### 2.2 union security_list_options

定义在 `include/linux/lsm_hooks.h:38-43`,包含所有钩子函数指针:

```c
union security_list_options {
    #define LSM_HOOK(RET, DEFAULT, NAME, ...) RET (*NAME)(__VA_ARGS__);
    #include "lsm_hook_defs.h"
    #undef LSM_HOOK
    void *lsm_func_addr;  // 用于通用调用
};
```

### 2.3 struct security_hook_list

已注册钩子的链表节点 (`include/linux/lsm_hooks.h:95-99`):

```c
struct security_hook_list {
    struct lsm_static_call *scalls;  // 静态调用表
    union security_list_options hook; // 钩子函数
    const struct lsm_id *lsmid;     // LSM 标识
} __randomize_layout;
```

### 2.4 struct lsm_static_call

静态调用结构 (`include/linux/lsm_hooks.h:51-57`):

```c
struct lsm_static_call {
    struct static_call_key *key;      // 静态调用键
    void *trampoline;                  // 跳转桩
    struct security_hook_list *hl;     // 钩子列表
    struct static_key_false *active;   // 激活状态
} __randomize_layout;
```

### 2.5 struct lsm_info

LSM 模块信息 (`include/linux/lsm_hooks.h:170-184`):

```c
struct lsm_info {
    const struct lsm_id *id;           // LSM ID
    enum lsm_order order;               // 初始化顺序
    unsigned long flags;                // 标志 (LSM_FLAG_LEGACY_MAJOR, LSM_FLAG_EXCLUSIVE)
    struct lsm_blob_sizes *blobs;      // blob 大小
    int *enabled;                       // 是否启用
    int (*init)(void);                  // 初始化函数

    // 各阶段初始化回调
    int (*initcall_pure)(void);
    int (*initcall_early)(void);
    int (*initcall_core)(void);
    int (*initcall_subsys)(void);
    int (*initcall_fs)(void);
    int (*initcall_device)(void);
    int (*initcall_late)(void);
};
```

### 2.6 LSM 顺序枚举

```c
enum lsm_order {
    LSM_ORDER_FIRST = -1,     // capability (首先初始化)
    LSM_ORDER_MUTABLE = 0,   // 可变顺序 (通过 CONFIG_LSM 指定)
    LSM_ORDER_LAST = 1,      // integrity 模块 (最后初始化)
};
```

### 2.7 struct lsm_blob_sizes

定义在 `include/linux/lsm_hooks.h:104-122`,描述各对象的安全 blob 大小:

```c
struct lsm_blob_sizes {
    unsigned int lbs_cred;          // cred 结构
    unsigned int lbs_file;          // file 结构
    unsigned int lbs_ib;           // InfiniBand
    unsigned int lbs_inode;         // inode 结构
    unsigned int lbs_sock;          // socket 结构
    unsigned int lbs_superblock;    // super_block 结构
    unsigned int lbs_ipc;           // IPC
    unsigned int lbs_key;           // key
    unsigned int lbs_msg_msg;       // 消息
    unsigned int lbs_perf_event;     // 性能事件
    unsigned int lbs_task;          // task_struct
    unsigned int lbs_xattr_count;   // xattr 槽位数
    unsigned int lbs_tun_dev;       // tun 设备
    unsigned int lbs_bdev;          // 块设备
    unsigned int lbs_bpf_map;       // BPF map
    unsigned int lbs_bpf_prog;       // BPF program
    unsigned int lbs_bpf_token;     // BPF token
};
```

### 2.8 call_int_hook 和 call_void_hook 宏

```c
// security.c:454-471
#define __CALL_STATIC_INT(NUM, R, HOOK, LABEL, ...)                 \
do {                                                                   \
    if (static_branch_unlikely(&SECURITY_HOOK_ACTIVE_KEY(HOOK, NUM))) { \
        R = static_call(LSM_STATIC_CALL(HOOK, NUM))(__VA_ARGS__);     \
        if (R != LSM_RET_DEFAULT(HOOK))                               \
            goto LABEL;                                                \
    }                                                                  \
} while (0);

#define call_int_hook(HOOK, ...)                                       \
({                                                                      \
    __label__ OUT;                                                     \
    int RC = LSM_RET_DEFAULT(HOOK);                                    \
    LSM_LOOP_UNROLL(__CALL_STATIC_INT, RC, HOOK, OUT, __VA_ARGS__);    \
OUT:                                                                   \
    RC;                                                                \
})
```

---

## 3. 主要 LSM 模块

### 3.1 SELinux

**位置**: `security/selinux/`

**特点**: MAC (强制访问控制),基于标签的访问控制

**定义** (`security/selinux/hooks.c:7783-7791`):
```c
DEFINE_LSM(selinux) = {
    .id = &selinux_lsmid,
    .flags = LSM_FLAG_LEGACY_MAJOR | LSM_FLAG_EXCLUSIVE,  // 独占模式
    .enabled = &selinux_enabled_boot,
    .blobs = &selinux_blob_sizes,
    .init = selinux_init,
};
```

**核心数据结构**:
- `security_id`: 安全标识符 (SID)
- `task_security_struct`: 进程安全上下文
- `inode_security_struct`: inode 安全上下文
- `file_security_struct`: 文件安全上下文
- `avc`: 访问向量缓存

**策略加载** (`security/selinux/ss/services.c:2306`):
```c
int security_load_policy(void *data, size_t len,
                        struct selinux_load_state *load_state)
```

### 3.2 AppArmor

**位置**: `security/apparmor/`

**特点**: 基于路径的 MAC,使用文件系统路径进行访问控制

**定义** (`security/apparmor/lsm.c:2569-2577`):
```c
DEFINE_LSM(apparmor) = {
    .id = &apparmor_lsmid,
    .flags = LSM_FLAG_LEGACY_MAJOR | LSM_FLAG_EXCLUSIVE,
    .enabled = &apparmor_enabled,
    .blobs = &apparmor_blob_sizes,
    .init = apparmor_init,
};
```

**路径处理** (`security/apparmor/path.c:88-100`):
AppArmor 使用 `d_namespace_path()` 函数将路径解析为命名空间路径,然后与策略进行匹配。

### 3.3 Landlock

**位置**: `security/landlock/`

**特点**: 用户空间安全模块,用于限制进程的文件系统和网络访问

**定义** (`security/landlock/setup.c:77-81`):
```c
DEFINE_LSM(LANDLOCK_NAME) = {
    .id = &landlock_lsmid,
    .init = landlock_init,
    .blobs = &landlock_blob_sizes,
};
```

**核心结构**:
- `landlock_ruleset`: 规则集
- `landlock_domain`: 域(规则的集合)
- `landlock_object`: 受保护的对象

**钩子示例** (`security/landlock/fs.c:1823-1843`):
```c
static struct security_hook_list landlock_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(inode_free_security_rcu, hook_inode_free_security_rcu),
    LSM_HOOK_INIT(sb_delete, hook_sb_delete),
    LSM_HOOK_INIT(sb_mount, hook_sb_mount),
    LSM_HOOK_INIT(move_mount, hook_move_mount),
    // ... 更多文件系统钩子
};
```

### 3.4 LoadPin

**位置**: `security/loadpin/`

**特点**: 固件和模块加载固定,将加载固定到特定文件系统

**定义** (`security/loadpin/loadpin.c:430-437`):
```c
DEFINE_LSM(loadpin) = {
    .id = &loadpin_lsmid,
    .init = loadpin_init,
    .initcall_fs = init_loadpin_securityfs,
};
```

**核心逻辑** (`security/loadpin/loadpin.c:127-160`):
```c
static int loadpin_check(struct file *file, enum kernel_read_file_id id)
{
    struct super_block *load_root;
    const char *origin = kernel_read_file_id_str(id);
    bool first_root_pin = false;

    // 第一次加载,记录根文件系统
    if (!pinned_root) {
        pinned_root = file->f_path.mnt->mnt_sb;
        first_root_pin = true;
    }

    // 检查是否来自相同的已固定根
    if (file->f_path.mnt->mnt_sb != pinned_root) {
        if (enforce) {
            report_load(origin, file, "pinning-denied");
            return -EPERM;
        }
    }
    return 0;
}
```

### 3.5 Lockdown

**位置**: `security/lockdown/`

**特点**: 内核锁定,防止某些内核功能的滥用

**定义** (`security/lockdown/lockdown.c:165-171`):
```c
#ifdef CONFIG_SECURITY_LOCKDOWN_LSM_EARLY
DEFINE_EARLY_LSM(lockdown) = {
#else
DEFINE_LSM(lockdown) = {
#endif
    .id = &lockdown_lsmid,
    .init = lockdown_lsm_init,
    .initcall_core = lockdown_secfs_init,
};
```

**锁定级别**:
- `LOCKDOWN_NONE`: 无限制
- `LOCKDOWN_INTEGRITY_MAX`: 最大化完整性保护
- `LOCKDOWN_CONFIDENTIALITY_MAX`: 最大化机密性保护

**钩子实现** (`security/lockdown/lockdown.c:59-73`):
```c
static int lockdown_is_locked_down(enum lockdown_reason what)
{
    if (kernel_locked_down >= what) {
        if (lockdown_reasons[what])
            pr_notice_ratelimited("Lockdown: %s: %s is restricted; see man kernel_lockdown.7\n",
                  current->comm, lockdown_reasons[what]);
        return -EPERM;
    }
    return 0;
}
```

---

## 4. 钩子实现详解

### 4.1 inodeHooks

#### inode_permission

检查对 inode 的访问权限。

**SELinux 实现** (`security/selinux/hooks.c:3222-3275`):
```c
static int selinux_inode_permission(struct inode *inode, int requested)
{
    int mask;
    u32 perms;
    u32 sid = current_sid();
    struct task_security_struct *tsec;
    struct inode_security_struct *isec;

    // 将操作码转换为权限位
    mask = inode_mask_to_av(requested);

    // 获取当前进程和 inode 的安全上下文
    tsec = selinux_cred(current_cred())->tsec;
    isec = selinux_inode(inode);

    // 调用 AVC 检查权限
    return avc_has_perm(tsec->sid, isec->sid, isec->sclass, mask, NULL);
}
```

#### inode_setattr

检查设置 inode 属性的权限。

```c
int security_inode_setattr(struct mnt_idmap *idmap,
                           struct dentry *dentry, struct iattr *attr)
{
    if (unlikely(IS_PRIVATE(d_backing_inode(dentry))))
        return 0;
    return call_int_hook(inode_setattr, idmap, dentry, attr);
}
```

### 4.2 fileHooks

#### file_permission

检查文件访问权限。

```c
// security.c:2365-2368
int security_file_permission(struct file *file, int mask)
{
    return call_int_hook(file_permission, file, mask);
}
```

#### mmap_file

检查内存映射权限。

**关键代码** (`security.c:2500-2514`):
```c
int security_mmap_file(struct file *file, unsigned long prot,
                       unsigned long flags)
{
    int ret;

    ret = call_int_hook(mmap_file, file, reqprot, prot, flags);
    return ret;
}
```

#### file_open

文件打开时的检查。

```c
// security.c:2526-2535
int security_file_open(struct file *file)
{
    int ret;

    ret = call_int_hook(file_open, file);
    return ret;
}
```

### 4.3 taskHooks

#### ptrace_access_check

检查 ptrace 访问权限。

**SELinux 实现** (`security/selinux/hooks.c:1900-1928`):
```c
static int selinux_ptrace_access_check(struct task_struct *child,
                                        unsigned int mode)
{
    const struct task_security_struct *tsec = selinux_cred(current_cred())->tsec;
    const struct task_security_struct *csec = selinux_cred(__task_cred(child))->tsec;

    // PTRACE_MODE_READ 和 PTRACE_MODE_TRACE 权限检查
    return avc_has_perm(tsec->sid, csec->sid, SECCLASS_PROCESS,
                        PTRACE_MODE_ACCESS, NULL);
}
```

#### capget

获取进程能力集。

```c
// security.c:587-593
int security_capget(const struct task_struct *target,
                    kernel_cap_t *effective,
                    kernel_cap_t *inheritable,
                    kernel_cap_t *permitted)
{
    return call_int_hook(capget, target, effective, inheritable, permitted);
}
```

### 4.4 bprm_hooks

#### bprm_check_security

在执行二进制文件前进行检查。

```c
// security.c:793-796
int security_bprm_check(struct linux_binprm *bprm)
{
    return call_int_hook(bprm_check_security, bprm);
}
```

#### bprm_creds_for_exec

准备执行凭证。

```c
// security.c:752-755
int security_bprm_creds_for_exec(struct linux_binprm *bprm)
{
    return call_int_hook(bprm_creds_for_exec, bprm);
}
```

---

## 5. 策略加载

### 5.1 安全模块初始化顺序

LSM 通过 `CONFIG_LSM` 配置选项指定初始化顺序:

```makefile
# 来自 Kconfig
config LSM
    string "Order of LSM to initialize"
    default "landlock,lockdown,yama,loadpin,commoncap,selinux,apparmor,tomoyo,ima,eVM"
```

### 5.2 security_add_hooks

将 LSM 的钩子注册到框架 (`security/lsm_init.c:367-378`):

```c
void __init security_add_hooks(struct security_hook_list *hooks, int count,
                               const struct lsm_id *lsmid)
{
    int i;

    for (i = 0; i < count; i++) {
        hooks[i].lsmid = lsmid;
        if (lsm_static_call_init(&hooks[i]))
            panic("exhausted LSM callback slots with LSM %s\n",
                  lsmid->name);
    }
}
```

### 5.3 lsm_static_call_init

初始化静态调用 (`security/lsm_init.c:339-357`):

```c
static int __init lsm_static_call_init(struct security_hook_list *hl)
{
    struct lsm_static_call *scall = hl->scalls;
    int i;

    for (i = 0; i < MAX_LSM_COUNT; i++) {
        // 找到第一个未使用的静态调用槽位
        if (!scall->hl) {
            __static_call_update(scall->key, scall->trampoline,
                                 hl->hook.lsm_func_addr);
            scall->hl = hl;
            static_branch_enable(scall->active);
            return 0;
        }
        scall++;
    }
    return -ENOSPC;
}
```

### 5.4 LSM 策略加载示例 (SELinux)

```c
// security/selinux/ss/services.c:2306-2330
int security_load_policy(void *data, size_t len,
                        struct selinux_load_state *load_state)
{
    struct selinux_policy *newpolicy, *oldpolicy;
    struct selinux_policy_convert_data *convert_data;
    int rc = 0;

    // 1. 解析策略文件
    newpolicy = kzalloc_obj(*newpolicy);
    if (!newpolicy)
        return -ENOMEM;

    // 2. 读取和验证策略
    rc = policydb_read(&newpolicy->policydb, fp);
    if (rc)
        goto err;

    // 3. 分配 SID 表
    rc = sidtab_init(&newpolicy->sidtab);
    if (rc)
        goto err;

    // 4. 转换策略数据
    convert_data = selinux_policy_convert(...);

    // 5. 安装新策略
    oldpolicy = rcu_dereference_protected(state->policy, 1);
    rcu_assign_pointer(state->policy, newpolicy);

    // 6. 同步并释放旧策略
    synchronize_rcu();
    selinux_policy_free(oldpolicy);

    return 0;
}
```

### 5.5 LSM Hook 调用流程

```
应用程序
    |
    v
系统调用 (如 open())
    |
    v
VFS 层 (如 vfs_open())
    |
    v
security_file_open()          <-- LSM 钩子入口
    |
    v
call_int_hook(file_open, file)  <-- 遍历所有注册的 LSM
    |
    +---> SELinux: selinux_file_open()
    +---> AppArmor: apparmor_file_open()
    +---> Landlock: landlock_file_open()
    +---> ...
    |
    v
返回 0 表示允许,负值表示拒绝
```

---

## 6. 架构图

### 6.1 LSM 框架整体架构

```
+------------------------------------------------------------------+
|                         内核子系统                                 |
|  +------------------+  +------------------+  +------------------+  |
|  |   文件系统 (VFS)  |  |    进程管理      |  |     网络栈       |  |
|  +--------+---------+  +--------+---------+  +--------+---------+  |
|           |                    |                    |              |
|           v                    v                    v              |
|  +--------+---------+  +--------+---------+  +--------+---------+  |
|  | inode_hooks   |  | task_hooks    |  | socket_hooks   |         |
|  | file_hooks    |  | bprm_hooks   |  | netlink_hooks  |         |
|  | path_hooks   |  | cred_hooks   |  |                 |         |
|  +--------+---------+  +--------+---------+  +--------+---------+  |
|           |                    |                    |              |
+---------- | -------------------- | -------------------- | -----------+
            |                    |                    |
            v                    v                    v
+------------------------------------------------------------------+
|                     security.c (LSM 核心)                          |
|                                                                  |
|  call_int_hook(), call_void_hook()                                |
|  security_add_hooks()                                             |
|  lsm_static_call_init()                                           |
|                                                                  |
+------------------------------------------------------------------+
            |                    |                    |
            v                    v                    v
+------------------------------------------------------------------+
|                        LSM 模块                                    |
|  +----------+  +----------+  +----------+  +----------+          |
|  | SELinux  |  | AppArmor |  | Landlock |  | LoadPin  |          |
|  +----------+  +----------+  +----------+  +----------+          |
|  +----------+  +----------+  +----------+  +----------+          |
|  | Lockdown |  |   Yama   |  | Smack   |  |  Tomoyo  |          |
|  +----------+  +----------+  +----------+  +----------+          |
+------------------------------------------------------------------+
            |                    |                    |
            v                    v                    v
+------------------------------------------------------------------+
|                     安全策略 (策略文件)                             |
|  +----------+  +----------+  +----------+  +----------+          |
|  | SELinux  |  | AppArmor |  | Landlock |  |  IMA/EVM |          |
|  |  policy  |  |  policy  |  |  ruleset |  |  policies|          |
|  +----------+  +----------+  +----------+  +----------+          |
+------------------------------------------------------------------+
```

### 6.2 Hook 调用机制

```
                    static_calls_table
                    +------------------+
                    | inode_permission | ---> [SELinux] --> [AppArmor] --> [Landlock]
                    | file_open       | ---> [SELinux] --> [AppArmor]
                    | mmap_file       | ---> [SELinux] --> [Landlock]
                    | socket_connect  | ---> [SELinux] --> [Landlock]
                    | ...              |
                    +------------------+

调用过程:
1. 内核代码调用 security_xxx()
2. security_xxx() 调用 call_int_hook(HOOK, ...)
3. call_int_hook() 使用 UNROLL 宏展开为多个静态调用
4. 每个静态调用检查对应的 static_key 是否激活
5. 如果激活,调用该 LSM 的钩子函数
6. 如果返回非默认值,短路求值
```

### 6.3 Blob 内存布局

```
struct task_struct {
    ...
    void *security;  ---> +---------------------------+
                          | cred blob (LSM1)          |
                          | cred blob (LSM2)          |
                          | ...                       |
                          +---------------------------+
                          | task blob (LSM1)         |
                          | task blob (LSM2)         |
                          | ...                       |
                          +---------------------------+
}

struct inode {
    ...
    void *i_security; ---> +---------------------------+
                           | rcu_head                  |  (由 framework 添加)
                           | inode blob (LSM1)         |
                           | inode blob (LSM2)         |
                           | ...                       |
                           +---------------------------+
}
```

### 6.4 LSM 初始化序列

```
引导时序:
                                                 优先级
early_security_init()      [early LSM]         highest
    |
    +-- lsm_prepare()
    +-- lsm_init_single()
    |
    v
security_init()            [框架初始化]
    |
    +-- 解析 lsm_order
    +-- lsm_prepare() for all
    +-- 创建 slab 缓存
    +-- 分配初始进程的 security blob
    +-- lsm_init_single() for non-early LSMs
    |
    v
pure_initcall(security_initcall_pure)           highest
early_initcall(security_initcall_early)
core_initcall(security_initcall_core)
subsys_initcall(security_initcall_subsys)
fs_initcall(security_initcall_fs)
device_initcall(security_initcall_device)
late_initcall(security_initcall_late)           lowest
```

---

## 附录

### A. 关键文件列表

| 文件路径 | 描述 |
|---------|------|
| `security/security.c` | LSM 框架核心实现 |
| `security/lsm_init.c` | LSM 初始化逻辑 |
| `include/linux/lsm_hooks.h` | LSM 钩子数据结构 |
| `include/linux/lsm_hook_defs.h` | 钩子定义 |
| `security/selinux/` | SELinux 实现 |
| `security/apparmor/` | AppArmor 实现 |
| `security/landlock/` | Landlock 实现 |
| `security/loadpin/` | LoadPin 实现 |
| `security/lockdown/` | Lockdown 实现 |

### B. 重要宏

| 宏 | 位置 | 描述 |
|----|------|------|
| `LSM_HOOK_INIT(NAME, HOOK)` | `lsm_hooks.h:136` | 初始化 security_hook_list |
| `DEFINE_LSM(name)` | `lsm_hooks.h:186` | 定义 LSM 模块 |
| `DEFINE_EARLY_LSM(name)` | `lsm_hooks.h:191` | 定义早期 LSM |
| `call_int_hook(HOOK, ...)` | `security.c:463` | 调用整型返回钩子 |
| `call_void_hook(HOOK, ...)` | `security.c:448` | 调用 void 返回钩子 |

### C. LSM ID 定义

```c
// include/uapi/linux/lsm.h
#define LSM_ID_NONE           0
#define LSM_ID_CAPABILITY     1
#define LSM_ID_SELINUX        2
#define LSM_ID_SMACK           3
#define LSM_ID_TOMOYO         4
#define LSM_ID_APPARMOR        5
#define LSM_ID_YAMA           6
#define LSM_ID_LOADPIN        7
#define LSM_ID_LOCKDOWN       8
#define LSM_ID_LANDLOCK       9
#define LSM_ID_IMA            10
#define LSM_ID_EVM             11
#define LSM_ID_BPF             12
#define LSM_ID_SAFESETID       13
#define LSM_ID_BPF             14
#define LSM_ID_IPE             15
```

---

*文档版本: 1.0*
*生成时间: 2026-04-26*
*内核版本: Linux 7.0 (master branch)*
