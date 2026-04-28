# Linux Security 子系统深度分析 R1

## 概述

Linux 内核安全子系统是一个多层次、可扩展的安全框架，为内核提供了统一的安全策略实施接口。该子系统采用模块化设计，支持多种安全模块（LSM）同时运行，通过 Hook 机制在关键内核路径上实施访问控制。

**源码位置**：
- LSM 框架核心：`security/security.c`、`security/lsm_init.c`
- SELinux：`security/selinux/hooks.c`、`security/selinux/avc.c`
- AppArmor：`security/apparmor/lsm.c`、`security/apparmor/policy.c`
- Landlock：`security/landlock/ruleset.c`、`security/landlock/fs.c`
- BPF Security：`security/bpf/hooks.c`

---

## 一、LSM（Linux Security Module）框架

### 1.1 核心数据结构

#### struct security_hook_list（安全钩子列表）

**定义位置**：`include/linux/lsm_hooks.h:95-99`

```c
struct security_hook_list {
    struct lsm_static_call *scalls;   // 静态调用数组
    union security_list_options hook;  // 钩子回调函数联合体
    const struct lsm_id *lsmid;      // LSM 标识信息
} __randomize_layout;
```

每个 LSM 模块通过 `security_hook_list` 结构注册其安全钩子回调。`lsm_static_call` 结构体（`lsm_hooks.h:51-57`）包含静态调用键、 trampoline 和活跃状态标志，实现内核级性能优化。

#### struct lsm_id（LSM 标识）

**定义位置**：`include/linux/lsm_hooks.h:81-84`

```c
struct lsm_id {
    const char *name;  // LSM 名称（如 "selinux", "apparmor"）
    u64 id;           // LSM ID 号（来自 uapi/linux/lsm.h）
};
```

#### union security_list_options（钩子函数联合体）

**定义位置**：`include/linux/lsm_hooks.h:38-43`

```c
union security_list_options {
    #define LSM_HOOK(RET, DEFAULT, NAME, ...) RET (*NAME)(__VA_ARGS__);
    #include "lsm_hook_defs.h"
    #undef LSM_HOOK
    void *lsm_func_addr;
};
```

该联合体通过宏展开包含所有 LSM 钩子函数的函数指针，所有安全模块共享同一套接口定义。

#### struct lsm_blob_sizes（Blob 大小）

**定义位置**：`include/linux/lsm_hooks.h:104-122`

```c
struct lsm_blob_sizes {
    unsigned int lbs_cred;       // cred 结构 blob
    unsigned int lbs_file;       // file 结构 blob
    unsigned int lbs_inode;      // inode 结构 blob
    unsigned int lbs_sock;       // sock 结构 blob
    unsigned int lbs_superblock; // super_block blob
    unsigned int lbs_task;       // task_struct blob
    unsigned int lbs_bpf_map;    // bpf_map blob
    unsigned int lbs_bpf_prog;   // bpf_prog blob
    unsigned int lbs_bpf_token;  // bpf_token blob
    // ... 更多 blob 类型
};
```

每个 LSM 可以为不同内核对象分配安全相关的私有数据（blob），这些 blob 大小在 LSM 初始化时注册。

### 1.2 LSM 初始化流程

#### security_add_hooks()（注册钩子）

**定义位置**：`security/lsm_init.c:367-378`

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

**流程说明**：
1. 遍历传入的 `hooks` 数组
2. 为每个钩子设置 `lsmid` 标识
3. 调用 `lsm_static_call_init()` 初始化静态调用，将钩子注册到静态调用表
4. 启用对应的 static_branch

#### LSM 钩子调用机制

**定义位置**：`security/security.c:448-471`

```c
#define call_void_hook(HOOK, ...)                                 \
    do {                                                      \
        LSM_LOOP_UNROLL(__CALL_STATIC_VOID, HOOK, __VA_ARGS__); \
    } while (0)

#define call_int_hook(HOOK, ...)					\
({									\
    __label__ OUT;							\
    int RC = LSM_RET_DEFAULT(HOOK);					\
    LSM_LOOP_UNROLL(__CALL_STATIC_INT, RC, HOOK, OUT, __VA_ARGS__);	\
OUT:									\
    RC;								\
})
```

内核使用 `static_call` 机制实现高性能的钩子调用。宏 `LSM_LOOP_UNROLL` 展开后调用所有已注册的 LSM 钩子。

### 1.3 LSM Hook 宏定义

**定义位置**：`include/linux/lsm_hook_defs.h`

```c
// 示例：部分钩子定义
LSM_HOOK(int, 0, binder_set_context_mgr, const struct cred *mgr)
LSM_HOOK(int, 0, binder_transaction, const struct cred *from, const struct cred *to)
LSM_HOOK(int, 0, ptrace_access_check, struct task_struct *child, unsigned int mode)
LSM_HOOK(int, 0, capable, const struct cred *cred, struct user_namespace *ns, int cap, unsigned int opts)
// ... 200+ 钩子定义
```

每个钩子包含：
- 返回类型 `RET`
- 默认值 `DEFAULT`
- 钩子名称 `NAME`
- 参数列表 `__VA_ARGS__`

### 1.4 LSM 初始化顺序

**定义位置**：`security/lsm_init.c`

LSM 通过不同级别的 `initcall` 初始化：

1. **early_security_init()** - 早期 LSM 初始化
2. **security_init()** - 核心框架初始化
3. **pure_initcall** - 纯初始化
4. **early_initcall** - 早期初始化
5. **core_initcall** - 核心初始化
6. **subsys_initcall** - 子系统初始化
7. **fs_initcall** - 文件系统初始化
8. **device_initcall** - 设备初始化
9. **late_initcall** - 最后初始化

### 1.5 各 LSM 模块注册示例

#### SELinux 注册

**位置**：`security/selinux/hooks.c`

```c
static struct security_hook_list selinux_hooks[] __ro_after_init = {
    #define LSM_HOOK(RET, DEFAULT, NAME, ...) \
        LSM_HOOK_INIT(NAME, selinux_##NAME),
    #include <linux/lsm_hook_defs.h>
    #undef LSM_HOOK
};

static const struct lsm_id selinux_lsmid = {
    .name = "selinux",
    .id = LSM_ID_SELINUX,
};

// 在 selinux_enable 初始化时调用
security_add_hooks(selinux_hooks, ARRAY_SIZE(selinux_hooks), &selinux_lsmid);
```

#### AppArmor 注册

**位置**：`security/apparmor/lsm.c`

```c
static struct security_hook_list apparmor_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(cred_free, apparmor_cred_free),
    LSM_HOOK_INIT(cred_prepare, apparmor_cred_prepare),
    LSM_HOOK_INIT(binder_set_context_mgr, apparmor binder_set_context_mgr),
    LSM_HOOK_INIT(file_permission, apparmor_file_permission),
    // ... 更多钩子
};

static const struct lsm_id apparmor_lsmid = {
    .name = "apparmor",
    .id = LSM_ID_APPARMOR,
};
```

#### Landlock 注册

**位置**：`security/landlock/cred.c`, `security/landlock/fs.c` 等

Landlock 使用多个文件分散注册其钩子：

```c
// cred.c
static struct security_hook_list landlock_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(cred_prepare, landlock_cred_prepare),
    LSM_HOOK_INIT(cred_free, landlock_cred_free),
};

// fs.c
static struct security_hook_list landlock_fs_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(inode_permission, landlock_inode_permission),
    LSM_HOOK_INIT(file_permission, landlock_file_permission),
    // ...
};
```

#### BPF LSM 注册

**位置**：`security/bpf/hooks.c:10-16`

```c
static struct security_hook_list bpf_lsm_hooks[] __ro_after_init = {
    #define LSM_HOOK(RET, DEFAULT, NAME, ...) \
        LSM_HOOK_INIT(NAME, bpf_lsm_##NAME),
    #include <linux/lsm_hook_defs.h>
    #undef LSM_HOOK
    LSM_HOOK_INIT(inode_free_security, bpf_inode_storage_free),
};
```

---

## 二、SELinux（Security-Enhanced Linux）

### 2.1 核心状态结构

#### struct selinux_state

**定义位置**：`security/selinux/include/security.h:94-106`

```c
struct selinux_state {
#ifdef CONFIG_SECURITY_SELINUX_DEVELOP
    bool enforcing;              // 强制模式标志
#endif
    bool initialized;           // 初始化完成标志
    bool policycap[__POLICYDB_CAP_MAX];  // 策略能力位图

    struct page *status_page;   // 状态页（用于 userspace 通信）
    struct mutex status_lock;    // 状态锁

    struct selinux_policy __rcu *policy;  // 当前加载的策略
    struct mutex policy_mutex;    // 策略锁
} __randomize_layout;
```

全局单例 `selinux_state`（`security/selinux/hooks.c:112`）是 SELinux 的核心状态容器。

### 2.2 安全上下文结构

#### struct context

**定义位置**：`security/selinux/ss/context.h:28-35`

```c
struct context {
    u32 user;           // SELinux 用户 ID
    u32 role;           // 角色 ID
    u32 type;           // 类型 ID（访问控制核心）
    u32 len;            // 字符串表示长度
    struct mls_range range;  // MLS 范围
    char *str;          // 字符串表示（无法映射时）
};
```

安全上下文是 SELinux 访问控制的核心。格式为 `user:role:type:mls_range`，例如：
```
unconfined_u:unconfined_r:unconfined_t:s0
system_u:object_r:svirt_sandbox_file_t:s0:c0,c1023
```

### 2.3 AVC（Access Vector Cache）

#### struct avc_entry

**定义位置**：`security/selinux/avc.c:48-54`

```c
struct avc_entry {
    u32 ssid;           // 源安全标识符
    u32 tsid;           // 目标安全标识符
    u16 tclass;         // 目标安全类
    struct av_decision avd;  // 访问决策
    struct avc_xperms_node *xp_node;  // 扩展权限节点
};
```

#### struct avc_cache

**定义位置**：`security/selinux/avc.c:72-78`

```c
struct avc_cache {
    struct hlist_head slots[AVC_CACHE_SLOTS];  // 哈希槽（1 << CONFIG_SECURITY_SELINUX_AVC_HASH_BITS）
    spinlock_t slots_lock[AVC_CACHE_SLOTS];   // 每槽自旋锁
    atomic_t lru_hint;      // LRU 提示（用于回收扫描）
    atomic_t active_nodes;   // 活跃节点计数
    u32 latest_notif;       // 最新撤销通知序列号
};
```

#### avc_has_perm()（权限检查）

**定义位置**：`security/selinux/avc.c:1189-1203`

```c
int avc_has_perm(u32 ssid, u32 tsid, u16 tclass,
                 u32 requested, struct common_audit_data *auditdata)
{
    struct av_decision avd;
    int rc, rc2;

    rc = avc_has_perm_noaudit(ssid, tsid, tclass, requested, 0, &avd);
    rc2 = avc_audit(ssid, tsid, tclass, requested, &avd, rc, auditdata);
    if (rc2)
        return rc2;
    return rc;
}
```

**权限检查流程**：

```
avc_has_perm()
    ├── avc_has_perm_noaudit()  // 实际权限检查
    │   ├── avc_lookup()        // 查找 AVC 缓存
    │   │   └── avc_hash()      // 计算哈希值：(ssid ^ tsid ^ tclass) % AVC_CACHE_SLOTS
    │   ├── avc_compute_av()     // 缓存未命中，调用安全服务器
    │   │   └── security_compute_av()  // 计算访问向量
    │   └── avc_denied()         // 处理权限拒绝
    └── avc_audit()              // 审计日志记录
```

#### avc_hash()（哈希计算）

**定义位置**：`security/selinux/avc.c:126-129`

```c
static inline u32 avc_hash(u32 ssid, u32 tsid, u16 tclass)
{
    return av_hash(ssid, tsid, (u32)tclass, (u32)(AVC_CACHE_SLOTS - 1));
}
```

### 2.4 安全决策结构

#### struct av_decision

**定义位置**：`security/selinux/include/security.h:240-246`

```c
struct av_decision {
    u32 allowed;       // 允许的权限位图
    u32 auditallow;    // 审计允许位图
    u32 auditdeny;     // 审计拒绝位图（默认审计）
    u32 seqno;         // 策略序列号
    u32 flags;         // 决策标志（允许性/拒绝等）
};
```

### 2.5 SELinux 钩子实现示例

#### inode_permission 钩子

**位置**：`security/selinux/hooks.c`

SELinux 通过 `selinux_inode_permission()` 实现文件访问检查：

1. 获取 inode 的 SID（安全标识符）
2. 获取当前任务的 SID
3. 调用 `avc_has_perm()` 检查权限
4. 如需审计，调用 `avc_audit()` 记录

#### binder 钩子

SELinux 提供完整的 binder IPC 安全控制：

```c
static int selinux_binder_set_context_mgr(const struct cred *mgr)
{
    return avc_has_perm(0, cred_sid(mgr), SECCLASS_BINDER,
                        BINDER__SET_CONTEXT_MGR, NULL);
}

static int selinux_binder_transaction(const struct cred *from, const struct cred *to)
{
    u32 fromsid = cred_sid(from);
    u32 tosid = cred_sid(to);
    return avc_has_perm(fromsid, tosid, SECCLASS_BINDER,
                        BINDER__TRANSACTION, NULL);
}
```

---

## 三、AppArmor

### 3.1 标签结构

#### struct aa_label

**定义位置**：`security/apparmor/include/label.h:127-148`

```c
struct aa_label {
    struct aa_common_ref count;      // 引用计数
    struct rb_node node;             // 红黑树节点
    struct rcu_head rcu;             // RCU 回调
    struct aa_proxy *proxy;          // 代理指针（指向最新版本）
    __counted char *hname;          // 层次化名称
    long flags;                      // 标签标志
    u32 secid;                       // 安全标识符
    int size;                        // vec 数组大小
    u64 mediates;                     // 中介能力位图
    union {
        struct {
            struct aa_profile *profile[2];  // 内嵌 profile
            DECLARE_FLEX_ARRAY(struct aa_ruleset *, rules);
        };
        DECLARE_FLEX_ARRAY(struct aa_profile *, vec);
    };
};
```

**标志定义**（`label.h:81-101`）：

| 标志 | 值 | 说明 |
|------|-----|------|
| FLAG_HAT | 1 | profile 是一个帽子（子 profile） |
| FLAG_UNCONFINED | 2 | 标签完全无限制 |
| FLAG_NULL | 4 | null 学习 profile |
| FLAG_IMMUTIBLE | 0x10 | 不可更改 |
| FLAG_STALE | 0x800 | 已替换/移除 |

### 3.2 Profile 结构

#### struct aa_profile

**定义位置**：`security/apparmor/include/policy.h:258-282`

```c
struct aa_profile {
    struct aa_policy base;           // 基础策略组件
    struct aa_profile __rcu *parent; // 父 profile

    struct aa_ns *ns;               // 所属命名空间
    const char *rename;             // 重命名名称

    enum audit_mode audit;           // 审计模式
    long mode;                       // 执行模式
    u32 path_flags;                  // 路径标志
    int signal;                      // 信号处理
    const char *disconnected;        // 断开的路径前缀

    struct aa_attachment attach;     // 附件规则

    struct aa_loaddata *rawdata;    // 原始策略数据
    unsigned char *hash;            // 加密哈希
    char *dirname;                   // 目录名
    struct dentry *dents[AAFS_PROF_SIZEOF];
    struct rhashtable *data;        // 自由格式策略数据

    int n_rules;
    // 可变长度成员，必须是最后一个
    struct aa_label label;
};
```

**Profile 模式**（`policy.h:73-79`）：

```c
enum profile_mode {
    APPARMOR_ENFORCE,   // 强制执行访问规则
    APPARMOR_COMPLAIN,  // 允许但记录违规
    APPARMOR_KILL,      // 访问违规时杀死任务
    APPARMOR_UNCONFINED, // 无限制 profile
    APPARMOR_USER,      // 用户空间修改的 complain 模式
};
```

### 3.3 策略数据库

#### struct aa_policydb

**定义位置**：`security/apparmor/include/policy.h:111-121`

```c
struct aa_policydb {
    struct kref count;
    struct aa_dfa *dfa;              // DFA 模式匹配引擎
    struct {
        struct aa_perms *perms;
        u32 size;
    };
    struct aa_str_table trans;        // 转换表
    struct aa_tags_struct tags;       // 标签表
    aa_state_t start[AA_CLASS_LAST + 1];  // 各类别的起始状态
};
```

### 3.4 DFA 匹配引擎

#### struct aa_dfa

**定义位置**：`security/apparmor/include/match.h:100-105`

```c
struct aa_dfa {
    struct kref count;
    u16 flags;
    u32 max_oob;
    struct table_header *tables[YYTD_ID_TSIZE];  // DFA 表数组
};
```

**表类型**（`match.h:56-66`）：

| ID | 名称 | 说明 |
|----|------|------|
| YYTD_ID_ACCEPT | ACCEPT | 接受状态表 |
| YYTD_ID_BASE | BASE | 基本转换表 |
| YYTD_ID_CHK | CHECK | 检查表 |
| YYTD_ID_DEF | DEFAULT | 默认转换表 |
| YYTD_ID_NXT | NEXT | 下一转换表 |
| YYTD_ID_EC | EQUIV | 等价类表 |

#### aa_dfa_match_len()（DFA 匹配）

AppArmor 使用 DFA（确定有限自动机）进行路径名匹配：

```c
aa_state_t aa_dfa_match_len(struct aa_dfa *dfa, aa_state_t start,
                            const char *str, int len);
```

匹配算法核心流程：

```
对于路径名中的每个字符 c：
    state = base_table[state] + c 的索引偏移
    如果 check_table[state] == 当前状态：
        转换到 next_table[state]
    否则：
        使用 default_table[state]
```

### 3.5 路径匹配

#### aa_path_name()（路径名称解析）

**定义位置**：`security/apparmor/path.c:200-220`

AppArmor 的路径匹配流程：

1. **路径解析**（`d_namespace_path()`，`path.c:88-178`）

```c
static int d_namespace_path(const struct path *path, char *buf, char **name,
                           int flags, const char *disconnected)
{
    // 处理挂载命名空间相对路径
    // 处理 chroot 相对路径
    // 处理断开的路径（前缀 "disconnected"）
}
```

2. **路径规则匹配**

路径被转换为 DFA 可处理的格式，与策略中的路径规则进行模式匹配。支持通配符（`*`, `**`, `?`）和字符类（`[...]`）。

### 3.6 profile_load()（策略加载）

**位置**：`security/apparmor/policy.c`

```c
ssize_t aa_replace_profiles(struct aa_ns *view, struct aa_label *label,
                            u32 mask, struct aa_loaddata *udata)
{
    // 1. 解包策略数据（policy_unpack.c）
    // 2. 验证策略哈希
    // 3. 创建/更新 profile
    // 4. 更新命名空间标签树
}
```

---

## 四、Landlock

### 4.1 规则集结构

#### struct landlock_ruleset

**定义位置**：`security/landlock/ruleset.h:119-190`

```c
struct landlock_ruleset {
    // 文件系统规则红黑树
    struct rb_root root_inode;

#if IS_ENABLED(CONFIG_INET)
    // 网络端口规则红黑树
    struct rb_root root_net_port;
#endif

    // 层级结构（用于 ptrace 保护）
    struct landlock_hierarchy *hierarchy;

    union {
        struct work_struct work_free;  // 延迟释放
        struct {
            struct mutex lock;         // 规则集锁
            refcount_t usage;          // 引用计数
            u32 num_rules;             // 规则数量
            u32 num_layers;            // 层级数量
            struct access_masks access_masks[];  // 访问掩码数组
        };
    };
};
```

### 4.2 规则结构

#### struct landlock_rule

**定义位置**：`security/landlock/ruleset.h:89-111`

```c
struct landlock_rule {
    struct rb_node node;              // 红黑树节点
    union landlock_key key;           // 规则键（inode 指针或端口号）
    u32 num_layers;                   // layers 数组长度
    struct landlock_layer layers[] __counted_by(num_layers);  // 层级栈
};
```

#### struct landlock_layer

**定义位置**：`security/landlock/ruleset.h:28-38`

```c
struct landlock_layer {
    u16 level;           // 层级位置（从 1 开始）
    access_mask_t access;  // 允许的访问位图
};
```

### 4.3 规则添加流程

#### landlock_add_rule()（系统调用）

**定义位置**：`security/landlock/syscalls.c:421-447`

```c
SYSCALL_DEFINE4(landlock_add_rule, const int, ruleset_fd,
                const enum landlock_rule_type, rule_type,
                const void __user *const, rule_attr, const __u32, flags)
{
    struct landlock_ruleset *ruleset;

    ruleset = get_ruleset_from_fd(ruleset_fd, FMODE_CAN_WRITE);
    switch (rule_type) {
    case LANDLOCK_RULE_PATH_BENEATH:
        return add_rule_path_beneath(ruleset, rule_attr);
    case LANDLOCK_RULE_NET_PORT:
        return add_rule_net_port(ruleset, rule_attr);
    }
}
```

#### add_rule_path_beneath()

**位置**：`security/landlock/syscalls.c:317-353`

```c
static int add_rule_path_beneath(struct landlock_ruleset *const ruleset,
                                 const void __user *const rule_attr)
{
    struct landlock_path_beneath_attr path_beneath_attr;
    struct path path;
    
    // 1. 复制用户空间属性
    copy_from_user(&path_beneath_attr, rule_attr, sizeof(path_beneath_attr));
    
    // 2. 验证 allowed_access 是规则集约束的子集
    mask = ruleset->access_masks[0].fs;
    if ((path_beneath_attr.allowed_access | mask) != mask)
        return -EINVAL;
    
    // 3. 获取路径对应的 inode 对象
    err = get_path_from_fd(path_beneath_attr.parent_fd, &path);
    
    // 4. 追加规则到规则集
    return landlock_append_fs_rule(ruleset, &path,
                                   path_beneath_attr.allowed_access);
}
```

#### insert_rule()（规则插入核心）

**定义位置**：`security/landlock/ruleset.c:205-286`

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
    
    // 红黑树查找
    walker_node = &root->rb_node;
    while (*walker_node) {
        struct landlock_rule *this = rb_entry(*walker_node, ...);
        
        if (this->key.data != id.key.data) {
            // 沿树下降
            if (this->key.data < id.key.data)
                walker_node = &((*walker_node)->rb_right);
            else
                walker_node = &((*walker_node)->rb_left);
            continue;
        }
        
        // 找到匹配规则：扩展或交集
        if ((*layers)[0].level == 0) {
            // 扩展访问权限（来自 landlock_add_rule）
            this->layers[0].access |= (*layers)[0].access;
            return 0;
        } else {
            // 交集（来自规则集合并）
            new_rule = create_rule(id, &this->layers, this->num_layers,
                                   &(*layers)[0]);
            rb_replace_node(&this->node, &new_rule->node, root);
            return 0;
        }
    }
    
    // 未找到匹配：插入新规则
    new_rule = create_rule(id, layers, num_layers, NULL);
    rb_link_node(&new_rule->node, parent_node, walker_node);
    rb_insert_color(&new_rule->node, root);
    ruleset->num_rules++;
    return 0;
}
```

### 4.4 规则层级与沙箱机制

#### landlock_merge_ruleset()（规则集合并）

**定义位置**：`security/landlock/ruleset.c:536-583`

```c
struct landlock_ruleset *
landlock_merge_ruleset(struct landlock_ruleset *const parent,
                      struct landlock_ruleset *const ruleset)
{
    // 1. 创建新域（包含 num_layers = parent->num_layers + 1）
    new_dom = create_ruleset(num_layers);
    
    // 2. 继承父规则集
    inherit_ruleset(parent, new_dom);
    
    // 3. 合并新规则集
    merge_ruleset(new_dom, ruleset);
    
    // 4. 初始化层级日志
    landlock_init_hierarchy_log(new_dom->hierarchy);
    
    return new_dom;
}
```

**关键特性**：
- **层级限制**：`LANDLOCK_MAX_NUM_LAYERS`（当前为 16）限制最大堆叠层数
- **访问权限交集**：每层规则的权限进行 AND 操作
- **继承与合并**：子域继承父域所有规则，新规则与现有规则取交集

### 4.5 Landlock 文件系统钩子

#### landlock_inode_permission()

**位置**：`security/landlock/fs.c`

```c
static int landlock_inode_permission(struct inode *inode, int mask)
{
    // 1. 获取当前进程的 landlock 域
    // 2. 查找 inode 对应的规则
    // 3. 检查请求的访问是否在规则允许范围内
    // 4. 验证所有层级都允许该访问
}
```

### 4.6 沙箱执行流程

```
用户空间调用 landlock_restrict_self()
    │
    ├── landlock_create_ruleset() 创建空规则集
    │       │
    │       └── create_ruleset(num_layers=1)
    │
    ├── landlock_add_rule() 添加路径规则
    │       │
    │       └── insert_rule() → 红黑树插入
    │
    └── landlock_restrict_self() 强制规则集
            │
            ├── 检查 CAP_SYS_ADMIN 或 no_new_privs
            ├── landlock_merge_ruleset() 合并到当前域
            │       │
            │       ├── 创建新域（num_layers = parent + 1）
            │       ├── inherit_ruleset() 复制父规则
            │       └── merge_ruleset() 合并新规则（取交集）
            │
            └── 更新当前任务的 credentials
```

---

## 五、BPF Security

### 5.1 BPF LSM 钩子

#### bpf_lsm_hooks

**定义位置**：`security/bpf/hooks.c:10-16`

```c
static struct security_hook_list bpf_lsm_hooks[] __ro_after_init = {
    #define LSM_HOOK(RET, DEFAULT, NAME, ...) \
        LSM_HOOK_INIT(NAME, bpf_lsm_##NAME),
    #include <linux/lsm_hook_defs.h>
    #undef LSM_HOOK
    LSM_HOOK_INIT(inode_free_security, bpf_inode_storage_free),
};
```

BPF LSM 通过宏展开自动注册大部分标准钩子，仅对 `inode_free_security` 有自定义实现。

### 5.2 BPF 安全 blob

#### struct bpf_storage_blob

BPF LSM 为 inode 提供附加的 BPF 存储：

```c
struct bpf_storage_blob {
    struct bpf_local_storage __rcu *storage;  // BPF 本地存储
};
```

**定义位置**：`security/bpf/hooks.c:32-33`

```c
struct lsm_blob_sizes bpf_lsm_blob_sizes __ro_after_init = {
    .lbs_inode = sizeof(struct bpf_storage_blob),
};
```

### 5.3 BPF 程序加载验证

#### security_bpf_prog_load()

**定义位置**：`security/security.c:5249-5262`

```c
int security_bpf_prog_load(struct bpf_prog *prog, union bpf_attr *attr,
                          struct bpf_token *token, bool kernel)
{
    int rc;

    rc = lsm_bpf_prog_alloc(prog);  // 分配 LSM blob
    if (unlikely(rc))
        return rc;

    rc = call_int_hook(bpf_prog_load, prog, attr, token, kernel);
    if (unlikely(rc))
        security_bpf_prog_free(prog);
    return rc;
}
```

#### lsm_bpf_prog_alloc()

**定义位置**：`security/security.c:326-329`

```c
static int lsm_bpf_prog_alloc(struct bpf_prog *prog)
{
    return lsm_blob_alloc(&prog->aux->security, blob_sizes.lbs_bpf_prog, GFP_KERNEL);
}
```

### 5.4 BPF Token 权限委托

BPF Token（`BPF token`）允许委托特定的 BPF 操作权限：

```c
int security_bpf_token_cmd(const struct bpf_token *token, enum bpf_cmd cmd)
{
    return call_int_hook(bpf_token_cmd, token, cmd);
}

int security_bpf_token_capable(const struct bpf_token *token, int cap)
{
    return call_int_hook(bpf_token_capable, token, cap);
}
```

---

## 六、数据结构关联图

### 6.1 LSM 框架整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Linux Kernel Core                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         security/security.c (LSM Hooks API)          │  │
│  │                                                     │  │
│  │  call_int_hook(binder_transaction, ...)              │  │
│  │  call_int_hook(ptrace_access_check, ...)             │  │
│  │  call_int_hook(file_permission, ...)                 │  │
│  │  ...                                                │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│         ┌────────────────┼────────────────┐                │
│         ▼                ▼                ▼                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   SELinux   │  │  AppArmor  │  │  Landlock   │        │
│  │             │  │            │  │             │        │
│  │ hooks.c     │  │   lsm.c    │  │  fs.c       │        │
│  │ avc.c       │  │ policy.c   │  │  cred.c     │        │
│  │ ss/context.c│  │  label.c   │  │  net.c      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 SELinux 数据结构关系

```
┌──────────────────────────────────────────────────────┐
│                   selinux_state                       │
│  ┌────────────────────────────────────────────────┐ │
│  │ policy ──► selinux_policy                       │ │
│  │           ┌─────────────────────────────────┐   │ │
│  │           │ policydb (策略数据库)            │   │ │
│  │           │   ├── sidtab (SID 表)            │   │ │
│  │           │   ├── avtab (访问向量表)        │   │ │
│  │           │   └── context_struct            │   │ │
│  │           └─────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│                    avc_cache                          │
│  ┌────────────────────────────────────────────────┐ │
│  │ slots[] ──► avc_node                           │ │
│  │           ┌─────────────────────────────────┐   │ │
│  │           │ avc_entry                       │   │ │
│  │           │   ├── ssid (源 SID)             │   │ │
│  │           │   ├── tsid (目标 SID)           │   │ │
│  │           │   ├── tclass (目标类)           │   │ │
│  │           │   └── av_decision               │   │ │
│  │           └─────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 6.3 AppArmor 数据结构关系

```
┌──────────────────────────────────────────────────────┐
│                     aa_label                          │
│  ┌────────────────────────────────────────────────┐ │
│  │ vec[] ──► aa_profile[] (profile 向量)          │ │
│  │           ┌─────────────────────────────────┐   │ │
│  │           │ aa_ruleset                      │   │ │
│  │           │   ├── file (aa_policydb)        │   │ │
│  │           │   ├── policy (aa_policydb)      │   │ │
│  │           │   └── caps (aa_caps)            │   │ │
│  │           └─────────────────────────────────┘   │ │
│  │                                                  │ │
│  │ hname (层次化名称如 ":ns:/profile//hat")        │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│                     aa_dfa                            │
│  ┌────────────────────────────────────────────────┐ │
│  │ tables[YYTD_ID_TSIZE]                         │ │
│  │   ├── ACCEPT  ──► 接受状态表                    │ │
│  │   ├── BASE    ──► 基本转换表                   │ │
│  │   ├── CHECK   ──► 检查表                       │ │
│  │   ├── DEFAULT ──► 默认转换表                   │ │
│  │   └── NEXT    ──► 下一转换表                   │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 6.4 Landlock 数据结构关系

```
┌──────────────────────────────────────────────────────┐
│                 landlock_ruleset                       │
│  ┌────────────────────────────────────────────────┐ │
│  │ root_inode ──► rb_tree ──► landlock_rule      │ │
│  │               ┌────────────────────────────┐   │ │
│  │               │ key (inode object 指针)    │   │ │
│  │               │ layers[]                  │   │ │
│  │               │   ├── layer[0]: level=1   │   │ │
│  │               │   └── layer[1]: level=2   │   │ │
│  │               └────────────────────────────┘   │ │
│  │                                                  │ │
│  │ num_layers (层级数，最大 16)                    │ │
│  │ hierarchy ──► landlock_hierarchy (父链)        │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│                 landlock_hierarchy                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ parent ──► 父 landlock_hierarchy               │ │
│  │ children ──► 子 ruleset 列表                    │ │
│  │ depth (当前深度)                               │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## 七、知识点关联表格

### 7.1 LSM 框架核心概念

| 概念 | 源码位置 | 说明 |
|------|----------|------|
| `struct security_hook_list` | `lsm_hooks.h:95` | LSM 钩子回调容器 |
| `struct lsm_id` | `lsm_hooks.h:81` | LSM 标识符（名称+ID） |
| `struct lsm_blob_sizes` | `lsm_hooks.h:104` | LSM 数据块大小 |
| `security_add_hooks()` | `lsm_init.c:367` | 注册 LSM 钩子 |
| `call_int_hook()` | `security.c:463` | 调用整型返回值钩子 |
| `call_void_hook()` | `security.c:448` | 调用无返回值钩子 |

### 7.2 SELinux 核心概念

| 概念 | 源码位置 | 说明 |
|------|----------|------|
| `struct selinux_state` | `selinux/include/security.h:94` | SELinux 全局状态 |
| `struct context` | `selinux/ss/context.h:28` | 安全上下文结构 |
| `struct avc_entry` | `selinux/avc.c:48` | AVC 缓存条目 |
| `struct avc_cache` | `selinux/avc.c:72` | AVC 缓存容器 |
| `struct av_decision` | `selinux/include/security.h:240` | 访问决策结果 |
| `avc_has_perm()` | `selinux/avc.c:1189` | 权限检查主函数 |
| `avc_hash()` | `selinux/avc.c:126` | AVC 哈希计算 |

### 7.3 AppArmor 核心概念

| 概念 | 源码位置 | 说明 |
|------|----------|------|
| `struct aa_label` | `apparmor/include/label.h:127` | AppArmor 标签 |
| `struct aa_profile` | `apparmor/include/policy.h:258` | AppArmor profile |
| `struct aa_policydb` | `apparmor/include/policy.h:111` | 策略数据库 |
| `struct aa_dfa` | `apparmor/include/match.h:100` | DFA 匹配引擎 |
| `aa_dfa_match_len()` | `apparmor/match.c:129` | DFA 路径匹配 |
| `aa_path_name()` | `apparmor/path.c:200` | 路径名称解析 |

### 7.4 Landlock 核心概念

| 概念 | 源码位置 | 说明 |
|------|----------|------|
| `struct landlock_ruleset` | `landlock/ruleset.h:119` | Landlock 规则集 |
| `struct landlock_rule` | `landlock/ruleset.h:89` | 单条规则 |
| `struct landlock_layer` | `landlock/ruleset.h:28` | 规则层级 |
| `landlock_add_rule()` | `landlock/syscalls.c:421` | 添加规则系统调用 |
| `landlock_merge_ruleset()` | `landlock/ruleset.c:536` | 规则集合并 |
| `insert_rule()` | `landlock/ruleset.c:205` | 红黑树规则插入 |

### 7.5 BPF Security 核心概念

| 概念 | 源码位置 | 说明 |
|------|----------|------|
| `bpf_lsm_hooks` | `bpf/hooks.c:10` | BPF LSM 钩子数组 |
| `lsm_bpf_prog_alloc()` | `security.c:326` | BPF 程序 blob 分配 |
| `lsm_bpf_map_alloc()` | `security.c:313` | BPF 映射 blob 分配 |
| `security_bpf_prog_load()` | `security.c:5249` | BPF 程序加载验证 |

---

## 八、总结

Linux 内核安全子系统通过 LSM 框架提供了一个统一、灵活且高性能的安全机制。各安全模块在此框架下协同工作：

1. **LSM 框架**以模块化方式管理安全钩子，通过 `static_call` 实现零开销调用，支持多 LSM 同时启用。

2. **SELinux** 是功能最全面的安全模块，采用 Flask 架构，通过 SID、安全上下文和 AVC 缓存实现细粒度强制访问控制。

3. **AppArmor** 采用基于路径的 DFA 匹配引擎，专注于应用沙箱化，通过 profile 限制程序能力。

4. **Landlock** 是轻量级的沙箱机制，使用红黑树管理规则，强调层级叠加和最小权限原则。

5. **BPF Security** 将 BPF 程序与 LSM 框架结合，允许通过 BPF 程序实现动态安全策略。

这些模块共同构成了 Linux 内核的多层次安全防护体系，从不同的角度保护系统资源免受未授权访问。

---

**文档版本**：R1  
**生成时间**：2026-04-26  
**源码版本参考**：Linux Kernel Mainline (latest)
