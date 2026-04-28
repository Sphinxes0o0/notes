# Linux 内核安全模块分析文档

## Lockdown / LoadPin / Capabilities / IPE

---

## 1. Lockdown 模块

**源码位置**: `/Users/sphinx/github/linux/security/lockdown/lockdown.c`

### 1.1 概述

Lockdown 模块是 Linux 内核的一个安全模块,用于在运行时锁定内核,防止用户空间修改内核代码或提取敏感信息。当内核进入锁定状态时,某些内核功能会被限制使用。

### 1.2 核心数据结构

#### 锁定等级 (lockdown_levels)

```c
// lockdown.c:20-22
static const enum lockdown_reason lockdown_levels[] = {
    LOCKDOWN_NONE,              // 无锁定
    LOCKDOWN_INTEGRITY_MAX,     // 完整性保护等级
    LOCKDOWN_CONFIDENTIALITY_MAX // 机密性保护等级
};
```

#### 锁定原因枚举 (lockdown_reason)

定义于 `/Users/sphinx/github/linux/include/linux/security.h:127-158`:

```c
enum lockdown_reason {
    LOCKDOWN_NONE,                    // 0 - 无锁定

    /* 完整性保护原因 (LOCKDOWN_INTEGRITY_MAX 之前) */
    LOCKDOWN_MODULE_SIGNATURE,        // 1 - 要求模块签名
    LOCKDOWN_DEV_MEM,                 // 2 - 限制 /dev/mem 访问
    LOCKDOWN_EFI_TEST,                // 3 - 限制 EFI 测试接口
    LOCKDOWN_KEXEC,                   // 4 - 限制 kexec 系统调用
    LOCKDOWN_HIBERNATION,             // 5 - 限制hibernation
    LOCKDOWN_PCI_ACCESS,              // 6 - 限制 PCI 配置空间访问
    LOCKDOWN_IOPORT,                  // 7 - 限制 I/O 端口访问
    LOCKDOWN_MSR,                      // 8 - 限制 Model Specific Register 访问
    LOCKDOWN_ACPI_TABLES,              // 9 - 限制 ACPI 表修改
    LOCKDOWN_DEVICE_TREE,             // 10 - 限制设备树修改
    LOCKDOWN_PCMCIA_CIS,              // 11 - 限制 PCMCIA CIS 访问
    LOCKDOWN_TIOCSSERIAL,             // 12 - 限制串行端口配置
    LOCKDOWN_MODULE_PARAMETERS,       // 13 - 限制模块参数修改
    LOCKDOWN_MMIOTRACE,               // 14 - 限制 MMIO 追踪
    LOCKDOWN_DEBUGFS,                  // 15 - 限制 debugfs 访问
    LOCKDOWN_XMON_WR,                 // 16 - 限制 XMON 写访问
    LOCKDOWN_BPF_WRITE_USER,          // 17 - 限制用户空间 BPF 写
    LOCKDOWN_DBG_WRITE_KERNEL,        // 18 - 限制内核调试写
    LOCKDOWN_RTAS_ERROR_INJECTION,    // 19 - 限制 RTAS 错误注入
    LOCKDOWN_XEN_USER_ACTIONS,        // 20 - 限制 Xen 用户操作
    LOCKDOWN_INTEGRITY_MAX,           // 21 - 完整性保护上限

    /* 机密性保护原因 (LOCKDOWN_CONFIDENTIALITY_MAX 之前) */
    LOCKDOWN_KCORE,                   // 22 - 限制 /proc/kcore 访问
    LOCKDOWN_KPROBES,                 // 23 - 限制 kprobes 使用
    LOCKDOWN_BPF_READ_KERNEL,         // 24 - 限制内核 BPF 读取
    LOCKDOWN_DBG_READ_KERNEL,         // 25 - 限制内核调试读取
    LOCKDOWN_PERF,                     // 26 - 限制 perf 事件
    LOCKDOWN_TRACEFS,                  // 27 - 限制 tracefs 访问
    LOCKDOWN_XMON_RW,                  // 28 - XMON 读写
    LOCKDOWN_XFRM_SECRET,             // 29 - 限制 IPsec 密钥读取
    LOCKDOWN_CONFIDENTIALITY_MAX,     // 30 - 机密性保护上限
};
```

### 1.3 核心函数

#### lock_kernel_down()

```c
// lockdown.c:27-36
/**
 * 将内核置于锁定模式
 * @where: 锁定来源描述
 * @level: 锁定等级
 */
static int lock_kernel_down(const char *where, enum lockdown_reason level)
{
    if (kernel_locked_down >= level)
        return -EPERM;

    kernel_locked_down = level;
    pr_notice("Kernel is locked down from %s; see man kernel_lockdown.7\n",
              where);
    return 0;
}
```

#### lockdown_is_locked_down()

```c
// lockdown.c:59-73
/**
 * 检查内核是否处于锁定状态
 * @what: 锁定原因标签
 * 返回: 0 表示未锁定, -EPERM 表示已锁定
 */
static int lockdown_is_locked_down(enum lockdown_reason what)
{
    if (WARN(what >= LOCKDOWN_CONFIDENTIALITY_MAX, "Invalid lockdown reason"))
        return -EPERM;

    if (kernel_locked_down >= what) {
        if (lockdown_reasons[what])
            pr_notice_ratelimited("Lockdown: %s: %s is restricted; see man kernel_lockdown.7\n",
                  current->comm, lockdown_reasons[what]);
        return -EPERM;
    }

    return 0;
}
```

### 1.4 锁定机制

```
                    +-------------------------+
                    |   kernel_locked_down    |
                    |   (全局锁定状态变量)     |
                    +-------------------------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
    LOCKDOWN_NONE      LOCKDOWN_INTEGRITY_MAX   LOCKDOWN_CONFIDENTIALITY_MAX
    (无锁定)           (完整性保护)              (机密性保护)
                              |                   |
                              v                   v
                    +---------------------+-------------------+
                    | 阻止修改内核代码    | 阻止读取内核数据 |
                    | (模块签名、内核调试)| (kcore、kprobes) |
                    +---------------------+-------------------+
```

### 1.5 初始化与配置

```c
// lockdown.c:38-53
/* 通过 kernel command line 启用锁定 */
static int __init lockdown_param(char *level)
{
    if (!level)
        return -EINVAL;

    if (strcmp(level, "integrity") == 0)
        lock_kernel_down("command line", LOCKDOWN_INTEGRITY_MAX);
    else if (strcmp(level, "confidentiality") == 0)
        lock_kernel_down("command line", LOCKDOWN_CONFIDENTIALITY_MAX);
    else
        return -EINVAL;

    return 0;
}
early_param("lockdown", lockdown_param);

// lockdown.c:84-94
/* 通过 Kconfig 配置强制启用 */
static int __init lockdown_lsm_init(void)
{
#if defined(CONFIG_LOCK_DOWN_KERNEL_FORCE_INTEGRITY)
    lock_kernel_down("Kernel configuration", LOCKDOWN_INTEGRITY_MAX);
#elif defined(CONFIG_LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY)
    lock_kernel_down("Kernel configuration", LOCKDOWN_CONFIDENTIALITY_MAX);
#endif
    security_add_hooks(lockdown_hooks, ARRAY_SIZE(lockdown_hooks), &lockdown_lsmid);
    return 0;
}
```

### 1.6 securityfs 接口

```c
// lockdown.c:96-153
/* 通过 /sys/kernel/security/lockdown 接口可读写当前锁定状态 */
static ssize_t lockdown_read(struct file *filp, char __user *buf, size_t count, loff_t *ppos)
{
    // 读取当前锁定状态,显示所有可能的锁定等级
}

static ssize_t lockdown_write(struct file *file, const char __user *buf,
                              size_t n, loff_t *ppos)
{
    // 写入 "integrity" 或 "confidentiality" 来启用对应等级的锁定
}
```

### 1.7 LSM Hook 注册

```c
// lockdown.c:75-77
static struct security_hook_list lockdown_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(locked_down, lockdown_is_locked_down),
};
```

### 1.8 文件系统限制

Lockdown 模块通过 `security_locked_down()` hook 限制以下文件系统操作:

| 锁定原因 | 限制的操作 |
|---------|-----------|
| LOCKDOWN_DEBUGFS | debugfs 文件创建/写入 |
| LOCKDOWN_KEXEC | kexec_load() 系统调用 |
| LOCKDOWN_HIBERNATION | hibernation 快照写入 |
| LOCKDOWN_MODULE_SIGNATURE | 加载未签名模块 |
| LOCKDOWN_BPF_WRITE_USER | bpf() 系统调用 (BPF_PROG_LOAD) |

---

## 2. LoadPin 模块

**源码位置**: `/Users/sphinx/github/linux/security/loadpin/loadpin.c`

### 2.1 概述

LoadPin 是一个内核安全模块,用于将模块和固件的加载固定(ping)到特定的文件系统(通常是只读文件系统)。这可以防止从不可信文件系统加载内核模块和固件,增强系统安全性。

### 2.2 核心设计思想

```
首次加载决定性 (First Pin Deterministic):
+------------------------------------------------------------------+
|                                                                  |
|  首次加载的模块/固件所在的文件系统 = "可信根"                       |
|                           |                                      |
|                           v                                      |
|  所有后续模块/固件加载必须来自同一文件系统                          |
|                           |                                      |
|                           v                                      |
|  如果来自不同文件系统:                                            |
|    - enforce=1: 拒绝加载,返回 -EPERM                              |
|    - enforce=0: 仅记录警告,允许加载                               |
|                                                                  |
+------------------------------------------------------------------+
```

### 2.3 核心变量

```c
// loadpin.c:47-57
static int enforce = IS_ENABLED(CONFIG_SECURITY_LOADPIN_ENFORCE);  // 强制执行标志
static char *exclude_read_files[READING_MAX_ID];                     // 排除的文件类型
static int ignore_read_file_id[READING_MAX_ID] __ro_after_init;     // 忽略的读取ID
static struct super_block *pinned_root;                             // 固定根文件系统
static DEFINE_SPINLOCK(pinned_root_spinlock);                       // 保护 pinned_root

// 初始化为 false,用于记录根文件系统是否可写
static bool loadpin_root_writable;
```

### 2.4 核心函数

#### loadpin_check()

```c
// loadpin.c:127-184
/**
 * 检查文件是否从固定根文件系统加载
 * @file: 要加载的文件
 * @id: kernel_read_file_id 类型
 * 返回: 0 允许加载, -EPERM 拒绝加载
 */
static int loadpin_check(struct file *file, enum kernel_read_file_id id)
{
    struct super_block *load_root;
    const char *origin = kernel_read_file_id_str(id);
    bool first_root_pin = false;

    /* 1. 检查是否在排除列表中 */
    if ((unsigned int)id < ARRAY_SIZE(ignore_read_file_id) &&
        ignore_read_file_id[id]) {
        report_load(origin, file, "pinning-excluded");
        return 0;  // 跳过固定检查
    }

    /* 2. 处理旧的 init_module API (file 为 NULL) */
    if (!file) {
        if (!enforce) {
            report_load(origin, NULL, "old-api-pinning-ignored");
            return 0;
        }
        report_load(origin, NULL, "old-api-denied");
        return -EPERM;
    }

    /* 3. 获取文件所在文件系统 */
    load_root = file->f_path.mnt->mnt_sb;

    /* 4. 首次加载决定根文件系统 */
    spin_lock(&pinned_root_spinlock);
    if (!pinned_root) {
        pinned_root = load_root;       // 首次加载,设置根
        first_root_pin = true;         // 标记首次固定
    }
    spin_unlock(&pinned_root_spinlock);

    if (first_root_pin) {
        loadpin_root_writable = sb_is_writable(pinned_root);
        report_writable(pinned_root, loadpin_root_writable);
        report_load(origin, file, "pinned");
    }

    /* 5. 验证后续加载来自同一根 */
    if (IS_ERR_OR_NULL(pinned_root) ||
        ((load_root != pinned_root) &&
         !dm_verity_loadpin_is_bdev_trusted(load_root->s_bdev))) {
        if (unlikely(!enforce)) {
            report_load(origin, file, "pinning-ignored");
            return 0;
        }
        report_load(origin, file, "denied");
        return -EPERM;
    }

    return 0;
}
```

#### sb_is_writable()

```c
// loadpin.c:99-107
/**
 * 检查超级块是否可写
 * 基于块设备读取-only 标志判断
 */
static bool sb_is_writable(struct super_block *mnt_sb)
{
    bool writable = true;

    if (mnt_sb->s_bdev)
        writable = !bdev_read_only(mnt_sb->s_bdev);

    return writable;
}
```

#### loadpin_sb_free_security()

```c
// loadpin.c:109-125
/**
 * 超级块释放时的安全处理
 * 如果释放的是固定的根文件系统:
 *   - enforce=1: 拒绝后续所有加载
 *   - enforce=0: 允许重新建立固定根
 */
static void loadpin_sb_free_security(struct super_block *mnt_sb)
{
    if (!IS_ERR_OR_NULL(pinned_root) && mnt_sb == pinned_root) {
        if (enforce) {
            pinned_root = ERR_PTR(-EIO);
            pr_info("umount pinned fs: refusing further loads\n");
        } else {
            pinned_root = NULL;
        }
    }
}
```

### 2.5 LoadPin 状态机

```
                    +------------------+
                    |  初始化状态      |
                    |  pinned_root=NULL|
                    +------------------+
                            |
            +---------------+---------------+
            |                               |
            v                               v
    +---------------+               +------------------+
    | 首次模块加载  |               |  非首次模块加载  |
    +---------------+               +------------------+
            |                               |
            v                               v
    +---------------+               +------------------+
    | 设置根文件系统|               | 检查是否同一根   |
    | pinned_root=  |               | 或 dm-verity    |
    | load_root     |               | 信任块设备       |
    +---------------+               +------------------+
            |                               |
            |               +---------------+---------------+
            |               |               |               |
            v               v               v               v
    +---------------+  +-----------+  +-----------+  +-----------+
    | 根只读?记录   |  | 同一根    |  | DM-Verity |  | 不同根    |
    | loadpin_root  |  | allow=0   |  | 信任设备  |  | enforce=0 |
    | _writable     |  +-----------+  +-----------+  +-----------+
    +---------------+               |               |
            |               +-------+               |
            |               |                       |
            v               v                       v
    +---------------+  +-----------+           +-----------+
    | 报告 "pinned"|  | allow=0   |           | allow=0   |
    +---------------+  +-----------+           +-----------+
            |               |                       |
            +---------------+-----------------------+
                            |
                            v
                    +---------------+
                    | 返回最终结果  |
                    +---------------+
```

### 2.6 排除的可信文件类型

LoadPin 允许排除某些文件类型,不进行固定检查:

```c
// loadpin.c:218-252
module_param_array_named(exclude, exclude_read_files, charp, NULL, 0);
/*
 * 使用示例: loadpin.exclude=firmware,policy
 * 可排除的类型定义在 kernel_read_file_id 中:
 * - READING_FIRMWARE
 * - READING_POLICY
 * - READING_KEXEC_IMAGE
 * - READING_KEXEC_INITRAMFS
 * - READING_MODULE
 * - etc.
 */
```

### 2.7 DM-Verity 集成

当编译启用 `CONFIG_SECURITY_LOADPIN_VERITY`:

```c
// loadpin.c:269-428
/*
 * 支持从 dm-verity 保护的块设备加载
 * 通过 securityfs 接口:
 *   /sys/kernel/security/loadpin/dm-verity
 *
 * 允许设置可信的 verity root digests
 * 文件格式: # LOADPIN_TRUSTED_VERITY_ROOT_DIGESTS\n<hex digest>
 */
```

### 2.8 LSM Hooks

```c
// loadpin.c:212-216
static struct security_hook_list loadpin_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(sb_free_security, loadpin_sb_free_security),
    LSM_HOOK_INIT(kernel_read_file, loadpin_read_file),
    LSM_HOOK_INIT(kernel_load_data, loadpin_load_data),
};
```

---

## 3. Capabilities 模块 (commoncap.c)

**源码位置**: `/Users/sphinx/github/linux/security/commoncap.c`

### 3.1 概述

Capabilities 模块实现基于 Linux capabilities 的访问控制机制。这是内核最基础的权限检查模块,负责在各种操作前检查进程是否具有相应的能力。

### 3.2 核心数据结构

#### struct cred (凭证结构)

定义于 `/Users/sphinx/github/linux/include/linux/cred.h`:

```c
struct cred {
    atomic_t usage;                // 引用计数
    kuid_t uid;                    // 真实用户 ID
    kgid_t gid;                    // 真实组 ID
    kuid_t suid;                   // 保存的用户 ID
    kgid_t sgid;                   // 保存的组 ID
    kuid_t euid;                   // 有效用户 ID
    kgid_t egid;                   // 有效组 ID
    kuid_t fsuid;                  // 文件系统用户 ID
    kgid_t fsgid;                  // 文件系统组 ID
    kernel_cap_t cap_effective;    // 有效能力集
    kernel_cap_t cap_permitted;    // 允许能力集
    kernel_cap_t cap_inheritable; // 可继承能力集
    kernel_cap_t cap_bset;         // 边界集
    kernel_cap_t cap_ambient;      // 环境能力集
    struct user_namespace *user_ns;// 用户命名空间
    struct ratelimit_state signal_cred_ratelimit;
    ...
};
```

#### 能力集说明

| 能力集 | 说明 |
|-------|------|
| cap_effective | 进程当前实际使用的能力 |
| cap_permitted | 进程允许拥有的最大能力集 |
| cap_inheritable | exec 时可继承的能力集 |
| cap_bset | 边界集,限制可丢弃的能力 |
| cap_ambient | 环境能力,exec 时保留 |

### 3.3 核心函数

#### cap_capable()

```c
// commoncap.c:124-132
/**
 * 检查进程是否具有指定能力
 * @cred: 进程凭证
 * @target_ns: 目标用户命名空间
 * @cap: 要检查的能力
 * @opts: 选项标志
 * 返回: 0 表示有能力, -EPERM 表示无能力
 *
 * 注意: 返回值语义与 capable() 相反!
 * cap_capable() 返回 0 = 有权限
 * capable() 返回 true = 有权限
 */
int cap_capable(const struct cred *cred, struct user_namespace *target_ns,
                int cap, unsigned int opts)
{
    const struct user_namespace *cred_ns = cred->user_ns;
    int ret = cap_capable_helper(cred, target_ns, cred_ns, cap);

    trace_cap_capable(cred, target_ns, cred_ns, cap, ret);
    return ret;
}

// commoncap.c:68-106
/**
 * 能力检查辅助函数
 * 在用户命名空间层次结构中向上遍历检查
 */
static inline int cap_capable_helper(const struct cred *cred,
                     struct user_namespace *target_ns,
                     const struct user_namespace *cred_ns,
                     int cap)
{
    struct user_namespace *ns = target_ns;

    for (;;) {
        /* 在同一命名空间:检查 effective capabilities */
        if (likely(ns == cred_ns))
            return cap_raised(cred->cap_effective, cap) ? 0 : -EPERM;

        /* 已到达比凭证命名空间更低的层级 */
        if (ns->level <= cred_ns->level)
            return -EPERM;

        /* 父命名空间的所有者拥有所有能力 */
        if ((ns->parent == cred_ns) && uid_eq(ns->owner, cred->euid))
            return 0;

        /* 父命名空间的能力会传递给子命名空间 */
        ns = ns->parent;
    }
}
```

#### cap_bprm_creds_from_file()

```c
// commoncap.c:919-1009
/**
 * 在 execve() 时设置进程的凭证和能力
 * @bprm: 二进制程序描述符
 * @file: 要执行的文件
 * 返回: 0 成功, 负值错误码
 *
 * 核心逻辑:
 * 1. 从文件 xattr 获取 file capabilities
 * 2. 计算新的 capability sets
 * 3. 处理 setuid/setgid 程序
 * 4. 处理 securebits
 */
int cap_bprm_creds_from_file(struct linux_binprm *bprm, const struct file *file)
{
    const struct cred *old = current_cred();
    struct cred *new = bprm->cred;
    bool effective = false, has_fcap = false, id_changed;
    int ret;
    kuid_t root_uid;

    // 1. 获取文件 capabilities
    ret = get_file_caps(bprm, file, &effective, &has_fcap);
    if (ret < 0)
        return ret;

    root_uid = make_kuid(new->user_ns, 0);

    // 2. 处理特权 root 的情况
    handle_privileged_root(bprm, has_fcap, &effective, root_uid);

    // 3. 如果有 fs caps,清除危险 personality 标志
    if (__cap_gained(permitted, new, old))
        bprm->per_clear |= PER_CLEAR_ON_SETID;

    // 4. 处理 setuid/setgid 程序
    id_changed = !uid_eq(new->euid, old->euid) || !in_group_p(new->egid);
    if ((id_changed || __cap_gained(permitted, new, old)) &&
        ((bprm->unsafe & ~LSM_UNSAFE_PTRACE) ||
         !ptracer_capable(current, new->user_ns))) {
        /* 降级: 不给予超过原有的权限 */
        if (!ns_capable(new->user_ns, CAP_SETUID) ||
            (bprm->unsafe & LSM_UNSAFE_NO_NEW_PRIVS)) {
            new->euid = new->uid;
            new->egid = new->gid;
        }
        new->cap_permitted = cap_intersect(new->cap_permitted, old->cap_permitted);
    }

    // 5. 更新所有 UID/GID
    new->suid = new->fsuid = new->euid;
    new->sgid = new->fsgid = new->egid;

    // 6. File caps 或 setid 会清除 ambient capabilities
    if (has_fcap || id_changed)
        cap_clear(new->cap_ambient);

    // 7. 计算最终 permitted: pP' = (X & fP) | (pI & fI) | pA'
    new->cap_permitted = cap_combine(new->cap_permitted, new->cap_ambient);

    // 8. 设置 effective: pE' = (fE ? pP' : pA')
    if (effective)
        new->cap_effective = new->cap_permitted;
    else
        new->cap_effective = new->cap_ambient;

    // 9. 检查是否需要审计
    if (nonroot_raised_pE(new, old, root_uid, has_fcap)) {
        ret = audit_log_bprm_fcaps(bprm, new, old);
        if (ret < 0)
            return ret;
    }

    // 10. 清除 SECURE_KEEP_CAPS
    new->securebits &= ~issecure_mask(SECURE_KEEP_CAPS);

    // 11. 标记 secureexec
    if (id_changed ||
        !uid_eq(new->euid, old->uid) ||
        !gid_eq(new->egid, old->gid) ||
        (!__is_real(root_uid, new) &&
         (effective || __cap_grew(permitted, ambient, new))))
        bprm->secureexec = 1;

    return 0;
}
```

### 3.4 用户命名空间

```
+---------------------------+
|    init_user_ns           |
|    (初始用户命名空间)      |
|    level=0                 |
+---------------------------+
           ^
           |
+---------------------------+
|    user_ns_A              |
|    level=1                |
|    parent=init_user_ns    |
+---------------------------+
           ^
           |
+---------------------------+
|    user_ns_B              |
|    level=2                |
|    parent=user_ns_A       |
+---------------------------+

命名空间能力继承规则:
1. 在同一命名空间: 直接检查 cap_effective
2. 在子命名空间: 父命名空间 owner 拥有所有能力
3. 跨多级命名空间: 逐级向上遍历检查
```

### 3.5 LSM Hooks

```c
// commoncap.c:1490-1508
static struct security_hook_list capability_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(capable, cap_capable),
    LSM_HOOK_INIT(settime, cap_settime),
    LSM_HOOK_INIT(ptrace_access_check, cap_ptrace_access_check),
    LSM_HOOK_INIT(ptrace_traceme, cap_ptrace_traceme),
    LSM_HOOK_INIT(capget, cap_capget),
    LSM_HOOK_INIT(capset, cap_capset),
    LSM_HOOK_INIT(bprm_creds_from_file, cap_bprm_creds_from_file),
    LSM_HOOK_INIT(inode_need_killpriv, cap_inode_need_killpriv),
    LSM_HOOK_INIT(inode_killpriv, cap_inode_killpriv),
    LSM_HOOK_INIT(inode_getsecurity, cap_inode_getsecurity),
    LSM_HOOK_INIT(mmap_addr, cap_mmap_addr),
    LSM_HOOK_INIT(task_fix_setuid, cap_task_fix_setuid),
    LSM_HOOK_INIT(task_prctl, cap_task_prctl),
    LSM_HOOK_INIT(task_setscheduler, cap_task_setscheduler),
    LSM_HOOK_INIT(task_setioprio, cap_task_setioprio),
    LSM_HOOK_INIT(task_setnice, cap_task_setnice),
    LSM_HOOK_INIT(vm_enough_memory, cap_vm_enough_memory),
};
```

### 3.6 能力检查流程

```
                   +-----------------+
                   |  调用 capable() |
                   +-----------------+
                          |
                          v
                   +-----------------+
                   | security_ops    |
                   | ->capable()     |
                   +-----------------+
                          |
                          v
                   +-----------------+
                   | cap_capable()  |
                   +-----------------+
                          |
          +---------------+---------------+
          |                               |
          v                               v
    +---------------+               +---------------+
    | 同一命名空间   |               | 不同命名空间   |
    +---------------+               +---------------+
          |                               |
          v                               v
    +---------------+               +---------------+
    | 检查          |               | 向上遍历父    |
    | cap_effective |               | 命名空间链    |
    +---------------+               +---------------+
          |                               |
          |               +---------------+---------------+
          |               |               |               |
          v               v               v               v
    +-----------+  +-----------+  +-----------+  +-----------+
    | cap_raised|  | 是 owner? |  | level <=  |  | 已达顶级  |
    | = true?   |  +-----------+  | cred_ns?  |  +-----------+
    +-----------+         |       +-----------+         |
          |               |             |               |
          v               v             v               v
    +-----------+  +-----------+  +-----------+  +-----------+
    | 返回 0    |  | 返回 0    |  | 返回-EPERM|  | 返回-EPERM|
    | (有权限) |  | (有权限) |  | (无权限) |  | (无权限) |
    +-----------+  +-----------+  +-----------+  +-----------+
```

---

## 4. IPE (Integrity Policy Enforcement) 模块

**源码位置**: `/Users/sphinx/github/linux/security/ipe/`

### 4.1 概述

IPE 是 Microsoft 开发的一个内核完整性策略实施模块,用于基于策略验证加载的固件、模块等资源的完整性。与 AppArmor/SELinux 不同,IPE 更专注于代码完整性而非访问控制。

### 4.2 核心数据结构

#### ipe_policy (策略结构)

定义于 `policy.h:78-88`:

```c
struct ipe_policy {
    const char *pkcs7;             // PKCS#7 签名
    size_t pkcs7len;               // 签名长度

    const char *text;              // 文本策略
    size_t textlen;                // 策略长度

    struct ipe_parsed_policy *parsed; // 解析后的策略

    struct dentry *policyfs;      // securityfs 节点
};
```

#### ipe_parsed_policy (解析后策略)

```c
// policy.h:65-76
struct ipe_parsed_policy {
    const char *name;              // 策略名称
    struct {
        u16 major;                // 版本号
        u16 minor;
        u16 rev;
    } version;

    enum ipe_action_type global_default_action; // 全局默认动作

    struct ipe_op_table rules[__IPE_OP_MAX];  // 操作规则表
};
```

#### 操作类型 (ipe_op_type)

```c
// policy.h:12-21
enum ipe_op_type {
    IPE_OP_EXEC = 0,              // 可执行文件
    IPE_OP_FIRMWARE,               // 固件
    IPE_OP_KERNEL_MODULE,          // 内核模块
    IPE_OP_KEXEC_IMAGE,            // kexec 镜像
    IPE_OP_KEXEC_INITRAMFS,        // kexec initramfs
    IPE_OP_POLICY,                 // IPE 策略
    IPE_OP_X509,                   // X509 证书
    __IPE_OP_MAX,
};
```

#### 动作类型 (ipe_action_type)

```c
// policy.h:25-29
enum ipe_action_type {
    IPE_ACTION_ALLOW = 0,          // 允许
    IPE_ACTION_DENY,               // 拒绝
    __IPE_ACTION_MAX
};
```

#### 属性类型 (ipe_prop_type)

```c
// policy.h:33-43
enum ipe_prop_type {
    IPE_PROP_BOOT_VERIFIED_FALSE,  // 启动未验证
    IPE_PROP_BOOT_VERIFIED_TRUE,   // 启动已验证 (initramfs)
    IPE_PROP_DMV_ROOTHASH,         // DM-Verity root hash
    IPE_PROP_DMV_SIG_FALSE,        // DM-Verity 无签名
    IPE_PROP_DMV_SIG_TRUE,         // DM-Verity 有签名
    IPE_PROP_FSV_DIGEST,           // fs-verity digest
    IPE_PROP_FSV_SIG_FALSE,        // fs-verity 无签名
    IPE_PROP_FSV_SIG_TRUE,         // fs-verity 有签名
    __IPE_PROP_MAX,
};
```

#### ipe_eval_ctx (评估上下文)

定义于 `eval.h:40-55`:

```c
struct ipe_eval_ctx {
    enum ipe_op_type op;           // 当前操作类型
    enum ipe_hook_type hook;       // 触发评估的 Hook

    const struct file *file;       // 相关文件
    bool initramfs;                // 是否来自 initramfs

#ifdef CONFIG_IPE_PROP_DM_VERITY
    const struct ipe_bdev *ipe_bdev; // 块设备信息
#endif
#ifdef CONFIG_IPE_PROP_FS_VERITY
    const struct inode *ino;        // inode 信息
#endif
#ifdef CONFIG_IPE_PROP_FS_VERITY_BUILTIN_SIG
    const struct ipe_inode *ipe_inode; // 文件 inode 信息
#endif
};
```

### 4.3 核心函数

#### ipe_build_eval_ctx()

```c
// eval.c:92-109
/**
 * 构建 IPE 评估上下文
 * 从文件对象中提取所有需要的信息
 */
void ipe_build_eval_ctx(struct ipe_eval_ctx *ctx,
                        const struct file *file,
                        enum ipe_op_type op,
                        enum ipe_hook_type hook)
{
    struct inode *ino;

    ctx->file = file;
    ctx->op = op;
    ctx->hook = hook;

    if (file) {
        build_ipe_sb_ctx(ctx, file);         // 构建 superblock 上下文
        ino = d_real_inode(file->f_path.dentry);
        build_ipe_bdev_ctx(ctx, ino);        // 构建块设备上下文
        build_ipe_inode_ctx(ctx, ino);       // 构建 inode 上下文
    }
}
```

#### ipe_evaluate_event()

```c
// eval.c:315-382
/**
 * 对事件进行策略评估
 * @ctx: 评估上下文
 * 返回: 0 允许, -EACCES 拒绝
 *
 * 评估流程:
 * 1. 获取当前活动策略
 * 2. 根据操作类型查找对应规则表
 * 3. 遍历规则,检查属性匹配
 * 4. 返回最终动作 (ALLOW/DENY)
 */
int ipe_evaluate_event(const struct ipe_eval_ctx *const ctx)
{
    const struct ipe_op_table *rules = NULL;
    const struct ipe_rule *rule = NULL;
    struct ipe_policy *pol = NULL;
    struct ipe_prop *prop = NULL;
    enum ipe_action_type action;
    enum ipe_match match_type;
    bool match = false;
    int rc = 0;

    rcu_read_lock();

    pol = rcu_dereference(ipe_active_policy);
    if (!pol) {
        rcu_read_unlock();
        return 0;  // 无策略,允许
    }

    // 处理未知操作
    if (ctx->op == IPE_OP_INVALID) {
        if (pol->parsed->global_default_action == IPE_ACTION_INVALID) {
            WARN(1, "no default rule set for unknown op, ALLOW it");
            action = IPE_ACTION_ALLOW;
        } else {
            action = pol->parsed->global_default_action;
        }
        match_type = IPE_MATCH_GLOBAL;
        goto eval;
    }

    rules = &pol->parsed->rules[ctx->op];

    // 遍历规则列表
    list_for_each_entry(rule, &rules->rules, next) {
        match = true;

        // 检查所有属性是否匹配
        list_for_each_entry(prop, &rule->props, next) {
            match = evaluate_property(ctx, prop);
            if (!match)
                break;
        }

        if (match)
            break;  // 找到匹配的规则
    }

    // 确定最终动作
    if (match) {
        action = rule->action;
        match_type = IPE_MATCH_RULE;
    } else if (rules->default_action != IPE_ACTION_INVALID) {
        action = rules->default_action;
        match_type = IPE_MATCH_TABLE;
    } else {
        action = pol->parsed->global_default_action;
        match_type = IPE_MATCH_GLOBAL;
    }

eval:
    ipe_audit_match(ctx, match_type, action, rule);
    rcu_read_unlock();

    if (action == IPE_ACTION_DENY)
        rc = -EACCES;

    // permissive 模式
    if (!READ_ONCE(enforce))
        rc = 0;

    return rc;
}
```

#### 属性评估函数

```c
// eval.c:280-303
static bool evaluate_property(const struct ipe_eval_ctx *const ctx,
                              struct ipe_prop *p)
{
    switch (p->type) {
    case IPE_PROP_BOOT_VERIFIED_FALSE:
        return !evaluate_boot_verified(ctx);
    case IPE_PROP_BOOT_VERIFIED_TRUE:
        return evaluate_boot_verified(ctx);
    case IPE_PROP_DMV_ROOTHASH:
        return evaluate_dmv_roothash(ctx, p);
    case IPE_PROP_DMV_SIG_FALSE:
        return evaluate_dmv_sig_false(ctx);
    case IPE_PROP_DMV_SIG_TRUE:
        return evaluate_dmv_sig_true(ctx);
    case IPE_PROP_FSV_DIGEST:
        return evaluate_fsv_digest(ctx, p);
    case IPE_PROP_FSV_SIG_FALSE:
        return evaluate_fsv_sig_false(ctx);
    case IPE_PROP_FSV_SIG_TRUE:
        return evaluate_fsv_sig_true(ctx);
    default:
        return false;
    }
}
```

### 4.4 IPE 策略格式示例

```
# IPE 策略示例
@version 1.0

global_default_action allow

op=EXEC
    props { boot_verified=TRUE }
    action allow

op=KERNEL_MODULE
    props { dmv_sig=TRUE }
    action allow
    props { boot_verified=TRUE }
    action allow

op=FIRMWARE
    props { fsv_sig=TRUE }
    action allow
```

### 4.5 IPE 架构图

```
+------------------------------------------------------------------+
|                     IPE (Integrity Policy Enforcement)            |
+------------------------------------------------------------------+
|                                                                   |
|  +----------------+     +-------------------+     +------------+ |
|  |   Policy       |     |   Hooks          |     |  Eval     | |
|  |   Manager      |     |   (bprm_check,   |     |  Engine   | |
|  |   (策略管理)   |     |    mmap,         |     |  (评估)   | |
|  +--------+-------+     |    kernel_read)  |     +-----+----+ |
|           |             +-------------------+           |        |
|           v                                         v         |
|  +----------------+                          +---------------+  |
|  | ipe_policy    |  -------------------->   | ipe_eval_ctx  |  |
|  | (解析后策略)  |                          | (评估上下文)  |  |
|  +----------------+                          +---------------+  |
|                                                     |            |
+------------------------------------------------------------------+
                            |
                            v
+------------------------------------------------------------------+
|                      属性验证层                                    |
+------------------------------------------------------------------+
|                                                                    |
|  +----------------+  +----------------+  +--------------------+  |
|  | Boot Verified  |  | DM-Verity      |  | FS-Verity          |  |
|  | (initramfs?)  |  | (roothash,     |  | (digest,           |  |
|  +----------------+  |  signature)   |  |  signature)        |  |
|                      +----------------+  +--------------------+  |
+------------------------------------------------------------------+
```

### 4.6 IPE Hook 类型

```c
// hooks.h:14-22
enum ipe_hook_type {
    IPE_HOOK_BPRM_CHECK = 0,         // execve 检查
    IPE_HOOK_BPRM_CREDS_FOR_EXEC,   // execve 凭证设置
    IPE_HOOK_MMAP,                   // mmap 检查
    IPE_HOOK_MPROTECT,               // mprotect 检查
    IPE_HOOK_KERNEL_READ,            // 内核读取文件
    IPE_HOOK_KERNEL_LOAD,            // 内核加载数据
    __IPE_HOOK_MAX
};
```

---

## 5. 整体安全架构

```
+-------------------------------------------------------------------+
|                    Linux Kernel Security Architecture              |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                         User Space                                  |
+-------------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                    System Call Interface                            |
+-------------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                      LSM Hooks Layer                                |
+-------------------------------------------------------------------+
        |                |                |                |
        v                v                v                v
+----------+      +----------+      +----------+      +----------+
| Lockdown |      | LoadPin  |      |   Cap    |      |   IPE    |
|          |      |          |      |          |      |          |
+----------+      +----------+      +----------+      +----------+
     |                |                |                |
     v                v                v                v
+----------+      +----------+      +----------+      +----------+
| 检查内核 |      | 检查模块 |      | 检查     |      | 检查代码 |
| 是否锁定 |      | 加载位置 |      | 能力集   |      | 完整性   |
+----------+      +----------+      +----------+      +----------+
```

### 5.1 安全模块协同

```
1. Lockdown: 基础安全框架
   - 定义锁定等级 (integrity/confidentiality)
   - 提供 lockdown_is_locked_down() 接口

2. LoadPin: 模块/固件来源验证
   - 固定加载位置到可信文件系统
   - 依赖 block device 的 read-only 状态

3. Capabilities: 基础权限检查
   - 所有安全模块的最终 fallback
   - 提供 capable() 接口供其他模块调用

4. IPE: 完整性策略实施
   - 基于属性的策略引擎
   - 支持 DM-Verity、fs-verity 验证
```

### 5.2 模块加载检查顺序

```
kernel_read_file() 或 kernel_load_data()
                    |
                    v
+------------------------------------------+
|  1. LoadPin Check                        |
|     - 检查文件来自 pinned_root            |
|     - 或 dm-verity 信任设备              |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|  2. IPE Policy Evaluation               |
|     - 检查 boot_verified 属性            |
|     - 检查 dm-verity 签名/digest         |
|     - 检查 fs-verity 签名/digest         |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|  3. Lockdown Check (特定操作)           |
|     - bprm_check: 检查 setuid/bpf       |
|     - kernel_read_file: 检查 debugfs     |
+------------------------------------------+
                    |
                    v
+------------------------------------------+
|  4. Capabilities Check                   |
|     - 验证调用者具有必要能力              |
+------------------------------------------+
                    |
                    v
                  ALLOW
```

---

## 6. 配置选项

### 6.1 Lockdown 配置

```
CONFIG_SECURITY_LOCKDOWN_LSM=y          # 启用 Lockdown LSM
CONFIG_LOCK_DOWN_KERNEL_FORCE_INTEGRITY  # 强制 integrity 锁定
CONFIG_LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY # 强制 confidentiality 锁定
```

### 6.2 LoadPin 配置

```
CONFIG_SECURITY_LOADPIN=y                 # 启用 LoadPin
CONFIG_SECURITY_LOADPIN_ENFORCE=y        # 强制执行(默认开启)
CONFIG_SECURITY_LOADPIN_VERITY=y         # 支持 dm-verity
CONFIG_SECURITY_LOADPIN_VERITY_SIGNATURE # 支持 dm-verity 签名
```

### 6.3 IPE 配置

```
CONFIG_IPE=y                              # 启用 IPE
CONFIG_IPE_PROP_DM_VERITY=y              # 支持 DM-Verity 属性
CONFIG_IPE_PROP_DM_VERITY_SIGNATURE=y    # 支持 DM-Verity 签名验证
CONFIG_IPE_PROP_FS_VERITY=y               # 支持 FS-Verity 属性
CONFIG_IPE_PROP_FS_VERITY_BUILTIN_SIG=y  # 支持 FS-Verity 内置签名
```

---

## 7. 参考文件路径

| 文件 | 路径 |
|-----|------|
| Lockdown 主体 | `/Users/sphinx/github/linux/security/lockdown/lockdown.c` |
| LoadPin 主体 | `/Users/sphinx/github/linux/security/loadpin/loadpin.c` |
| Capabilities | `/Users/sphinx/github/linux/security/commoncap.c` |
| IPE 主体 | `/Users/sphinx/github/linux/security/ipe/ipe.c` |
| IPE 策略 | `/Users/sphinx/github/linux/security/ipe/policy.h` |
| IPE 评估 | `/Users/sphinx/github/linux/security/ipe/eval.c` |
| IPE Hooks | `/Users/sphinx/github/linux/security/ipe/hooks.c` |
| 安全头文件 | `/Users/sphinx/github/linux/include/linux/security.h` |
