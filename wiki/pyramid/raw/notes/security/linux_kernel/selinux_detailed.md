# Linux 内核 SELinux 详细实现分析

## 目录

1. [SELinux 架构概述](#1-selinux-架构概述)
2. [安全上下文 (Security Context)](#2-安全上下文-security-context)
3. [访问向量缓存 (AVC)](#3-访问向量缓存-avc)
4. [策略管理](#4-策略管理)
5. [钩子实现](#5-钩子实现)
6. [核心数据结构关系图](#6-核心数据结构关系图)

---

## 1. SELinux 架构概述

SELinux (Security-Enhanced Linux) 是 Linux 内核的安全模块,实现基于 Flask(Flux Advanced Security Kernel) 架构的强制访问控制(MAC)系统。

### 1.1 核心组件

```
security/selinux/
├── avc.c              # 访问向量缓存 (Access Vector Cache)
├── hooks.c            # LSM 钩子实现 (约 8000+ 行)
├── selinuxfs.c        # SELinux 文件系统接口
├── ss/                # 安全服务器 (Security Server)
│   ├── policydb.c/h   # 策略数据库
│   ├── sidtab.c/h     # SID 表
│   ├── avtab.c/h      # 访问向量表
│   ├── context.c/h    # 上下文管理
│   ├── mls.c/h        # MLS 策略处理
│   ├── services.c     # 核心安全服务
│   ├── ebitmap.c/h    # 扩展位图
│   └── hashtab.c/h    # 哈希表
└── include/           # 头文件
```

### 1.2 TE (Type Enforcement) 类型强制

TE 是 SELinux 的核心机制,通过类型来标记所有主体(进程)和客体(文件、套接字等)。

**关键结构体** (`policydb.h`, 第 111-116 行):

```c
/* Type attributes */
struct type_datum {
    u32 value;              // 内部类型值
    u32 bounds;             // 类型的边界约束
    unsigned char primary;   // 是否为主类型
    unsigned char attribute; // 是否为属性类型
};
```

### 1.3 MLS (Multi-Level Security) 多级安全

MLS 提供分层安全级别和类别集合,实现 Bell-LaPadula 模型。

**MLS 级别结构** (`mls_types.h`, 第 20-23 行):

```c
struct mls_level {
    u32 sens;               // 敏感度等级
    struct ebitmap cat;     // 类别集合 (位图)
};

struct mls_range {
    struct mls_level level[2];  // low == level[0], high == level[1]
};
```

### 1.4 RBAC (Role-Based Access Control) 基于角色的访问控制

**角色属性结构** (`policydb.h`, 第 75-80 行):

```c
struct role_datum {
    u32 value;              // 内部角色值
    u32 bounds;             // 角色边界
    struct ebitmap dominates;  // 该角色支配的角色集合
    struct ebitmap types;   // 角色授权的类型集合
};
```

---

## 2. 安全上下文 (Security Context)

### 2.1 context 结构体

安全上下文是 SELinux 控制所有主体和客体的安全属性集合。

**核心结构体** (`context.h`, 第 28-35 行):

```c
struct context {
    u32 user;               // 用户身份
    u32 role;               // 角色
    u32 type;               // 类型 (TE 的核心)
    u32 len;                // 字符串表示长度
    struct mls_range range; // MLS 范围
    char *str;              // 无法映射时的字符串表示
};
```

**上下文字符串格式**: `user:role:type:mls_range`
例如: `system_u:object_r:admin_t:s0-s15:c0.c1023`

### 2.2 security_compute_sid() - 计算安全 SID

该函数根据源上下文、目标上下文和安全类计算新的 SID。

**函数实现** (`services.c`, 第 1753-1949 行):

```c
static int security_compute_sid(u32 ssid,
                u32 tsid,
                u16 orig_tclass,
                u16 specified,
                const char *objname,
                u32 *out_sid,
                bool kern)
{
    // 1. 获取策略和 SID 表
    policy = rcu_dereference(selinux_state.policy);
    policydb = &policy->policydb;
    sidtab = policy->sidtab;

    // 2. 查找源和目标上下文
    scontext = &sentry->context;
    tcontext = &tentry->context;

    // 3. 设置用户身份 (根据 specified 类型)
    switch (specified) {
    case AVTAB_TRANSITION:
    case AVTAB_CHANGE:
        if (cladatum->default_user == DEFAULT_TARGET)
            newcontext.user = tcontext->user;  // 使用目标用户
        else
            newcontext.user = scontext->user; // 使用源用户
        break;
    case AVTAB_MEMBER:
        newcontext.user = tcontext->user;     // 使用关联对象所有者
        break;
    }

    // 4. 设置角色 (根据类型或默认值)
    if (tclass == policydb->process_class || sock)
        newcontext.role = scontext->role;      // 进程使用源角色
    else
        newcontext.role = OBJECT_R_VAL;        // 对象使用 object_r

    // 5. 查找类型转换规则
    avkey.source_type = scontext->type;
    avkey.target_type = tcontext->type;
    avkey.target_class = tclass;
    avkey.specified = specified;
    avnode = avtab_search_node(&policydb->te_avtab, &avkey);

    // 6. 设置类型 (从规则或默认值)
    if (avnode)
        newcontext.type = avnode->datum.u.data;
    else
        newcontext.type = scontext->type;      // 默认为源类型

    // 7. 计算 MLS 属性
    mls_compute_sid(policydb, scontext, tcontext, tclass,
                    specified, &newcontext, sock);

    // 8. 验证上下文有效性
    if (!policydb_context_isvalid(policydb, &newcontext))
        return -EINVAL;

    // 9. 转换为 SID
    if (context_equal(scontext, &newcontext))
        *out_sid = ssid;
    else if (context_equal(tcontext, &newcontext))
        *out_sid = tsid;
    else
        sidtab_context_to_sid(sidtab, &newcontext, out_sid);
}
```

**调用链**:

```
security_transition_sid()
└── security_compute_sid(ssid, tsid, tclass, AVTAB_TRANSITION, ...)
```

### 2.3 SID 表 (sidtab)

SID 表维护 SID 到安全上下文的映射。

**SID 表结构** (`sidtab.h`, 第 77-105 行):

```c
struct sidtab {
    union sidtab_entry_inner roots[SIDTAB_MAX_LEVEL + 1];  // 树形结构根节点
    u32 count;                    // 当前 SID 数量
    struct sidtab_convert_params *convert;  // 策略转换参数
    bool frozen;                  // 冻结标志
    spinlock_t lock;              // 自旋锁

    // SID -> 上下文字符串缓存
    u32 cache_free_slots;
    struct list_head cache_lru_list;
    spinlock_t cache_lock;

    // 初始 SID 条目 (index == SID - 1)
    struct sidtab_isid_entry isids[SECINITSID_NUM];

    // 哈希表用于快速反向查找
    DECLARE_HASHTABLE(context_to_sid, SIDTAB_HASH_BITS);
};
```

---

## 3. 访问向量缓存 (AVC)

AVC 是 SELinux 的核心缓存机制,用于缓存访问决策以提高性能。

### 3.1 AVC 缓存结构

**AVC 缓存结构** (`avc.c`, 第 72-78 行):

```c
struct avc_cache {
    struct hlist_head slots[AVC_CACHE_SLOTS];  // 哈希槽
    spinlock_t slots_lock[AVC_CACHE_SLOTS];    // 每个槽的锁
    atomic_t lru_hint;                         // LRU 回收提示
    atomic_t active_nodes;                      // 活跃节点数
    u32 latest_notif;                          // 最新通知序列号
};
```

**AVC 条目结构** (`avc.c`, 第 48-60 行):

```c
struct avc_entry {
    u32 ssid;              // 源 SID
    u32 tsid;              // 目标 SID
    u16 tclass;            // 目标安全类
    struct av_decision avd;  // 访问决策
    struct avc_xperms_node *xp_node;  // 扩展权限节点
};

struct avc_node {
    struct avc_entry ae;
    struct hlist_node list;  // 哈希链表节点
    struct rcu_head rhead;   // RCU 头
};
```

### 3.2 avc_has_perm() - 权限检查

这是 SELinux 最核心的权限检查函数。

**函数实现** (`avc.c`, 第 1189-1203 行):

```c
int avc_has_perm(u32 ssid, u32 tsid, u16 tclass,
         u32 requested, struct common_audit_data *auditdata)
{
    struct av_decision avd;
    int rc, rc2;

    // 1. 先进行无审计的权限检查
    rc = avc_has_perm_noaudit(ssid, tsid, tclass, requested, 0, &avd);

    // 2. 根据决策结果进行审计
    rc2 = avc_audit(ssid, tsid, tclass, requested, &avd, rc, auditdata);
    if (rc2)
        return rc2;
    return rc;
}
```

**无审计权限检查** (`avc.c`, 第 1145-1171 行):

```c
inline int avc_has_perm_noaudit(u32 ssid, u32 tsid,
                u16 tclass, u32 requested,
                unsigned int flags,
                struct av_decision *avd)
{
    u32 denied;
    struct avc_node *node;

    if (WARN_ON(!requested))
        return -EACCES;

    rcu_read_lock();

    // 1. 查找缓存条目
    node = avc_lookup(ssid, tsid, tclass);
    if (unlikely(!node)) {
        rcu_read_unlock();
        // 缓存未命中,调用安全服务器
        return avc_perm_nonode(ssid, tsid, tclass, requested,
                   flags, avd);
    }

    // 2. 检查请求的权限是否被允许
    denied = requested & ~node->ae.avd.allowed;
    memcpy(avd, &node->ae.avd, sizeof(*avd));
    rcu_read_unlock();

    // 3. 如果有拒绝的权限,调用 avc_denied 处理
    if (unlikely(denied))
        return avc_denied(ssid, tsid, tclass, requested, 0, 0, 0,
                  flags, avd);
    return 0;
}
```

### 3.3 avc_audit() - 审计函数

**慢路径审计函数** (`avc.c`, 第 754-781 行):

```c
noinline int slow_avc_audit(u32 ssid, u32 tsid, u16 tclass,
                u32 requested, u32 audited, u32 denied, int result,
                struct common_audit_data *a)
{
    struct common_audit_data stack_data;
    struct selinux_audit_data sad;

    if (WARN_ON(!tclass || tclass >= ARRAY_SIZE(secclass_map)))
        return -EINVAL;

    if (!a) {
        a = &stack_data;
        a->type = LSM_AUDIT_DATA_NONE;
    }

    // 设置 SELinux 审计数据
    sad.tclass = tclass;
    sad.requested = requested;
    sad.ssid = ssid;
    sad.tsid = tsid;
    sad.audited = audited;
    sad.denied = denied;
    sad.result = result;

    a->selinux_audit_data = &sad;

    // 调用通用 LSM 审计
    common_lsm_audit(a, avc_audit_pre_callback, avc_audit_post_callback);
    return 0;
}
```

### 3.4 访问决策结构

**av_decision** (`security.h`, 第 240-246 行):

```c
struct av_decision {
    u32 allowed;      // 允许的权限位掩码
    u32 auditallow;  // 审计允许的权限
    u32 auditdeny;   // 审计拒绝的权限 (用于 dontaudit)
    u32 seqno;        // 策略序列号
    u32 flags;        // 决策标志 (permissive, neveraudit)
};
```

---

## 4. 策略管理

### 4.1 policydb - 策略数据库

策略数据库存储编译后的安全策略。

**核心结构体** (`policydb.h`, 第 236-315 行):

```c
struct policydb {
    int mls_enabled;  // MLS 是否启用

    /* 符号表 - 存储各类策略元素 */
    struct symtab symtab[SYM_NUM];
#define p_commons   symtab[SYM_COMMONS]   // 公共权限
#define p_classes   symtab[SYM_CLASSES]   // 安全类
#define p_roles     symtab[SYM_ROLES]     // 角色
#define p_types     symtab[SYM_TYPES]     // 类型
#define p_users     symtab[SYM_USERS]     // 用户
#define p_bools     symtab[SYM_BOOLS]     // 布尔表达式
#define p_levels    symtab[SYM_LEVELS]    // 敏感度级别
#define p_cats      symtab[SYM_CATS]      // 类别

    /* 索引数组 */
    struct class_datum **class_val_to_struct;
    struct role_datum **role_val_to_struct;
    struct user_datum **user_val_to_struct;
    struct type_datum **type_val_to_struct;

    /* 类型强制访问向量表 */
    struct avtab te_avtab;

    /* 角色转换表 */
    struct hashtab role_tr;

    /* 文件名转换表 */
    struct hashtab filename_trans;

    /* 条件 TE 规则 */
    struct avtab te_cond_avtab;
    struct cond_node *cond_list;

    /* 角色允许规则 */
    struct role_allow *role_allow;

    /* 各种上下文 (初始 SID、文件系统、端口等) */
    struct ocontext *ocontexts[OCON_NUM];

    /* 范围转换表 */
    struct hashtab range_tr;

    /* 策略能力位图 */
    struct ebitmap policycaps;

    /* permissive 映射 */
    struct ebitmap permissive_map;

    /* neveraudit 映射 */
    struct ebitmap neveraudit_map;
} __randomize_layout;
```

### 4.2 AV 表 (avtab)

访问向量表是类型强制规则的核心存储结构。

**AV 表键结构** (`avtab.h`, 第 26-48 行):

```c
struct avtab_key {
    u16 source_type;   // 源类型
    u16 target_type;   // 目标类型
    u16 target_class;   // 目标对象类
    u16 specified;      // 指定的规则类型
};

// 规则类型标志
#define AVTAB_ALLOWED      0x0001  // allow 规则
#define AVTAB_AUDITALLOW   0x0002  // auditallow 规则
#define AVTAB_AUDITDENY    0x0004  // auditdeny 规则
#define AVTAB_TRANSITION   0x0010  // 类型转换规则
#define AVTAB_MEMBER       0x0020  // 成员关系规则
#define AVTAB_CHANGE       0x0040  // 属性更改规则
#define AVTAB_XPERMS_ALLOWED   0x0100  // 扩展权限 allow
```

### 4.3 context_struct_compute_av() - 计算访问向量

根据源上下文、目标上下文和安全类计算权限决策。

**函数实现** (`services.c`, 第 622-723 行):

```c
static void context_struct_compute_av(struct policydb *policydb,
                      struct context *scontext,
                      struct context *tcontext,
                      u16 tclass,
                      struct av_decision *avd,
                      struct extended_perms *xperms)
{
    struct constraint_node *constraint;
    struct role_allow *ra;
    struct avtab_key avkey;
    struct avtab_node *node;
    struct class_datum *tclass_datum;
    struct ebitmap *sattr, *tattr;

    // 1. 初始化访问决策
    avd->allowed = 0;
    avd->auditallow = 0;
    avd->auditdeny = 0xffffffff;

    // 2. 获取目标类 datum
    tclass_datum = policydb->class_val_to_struct[tclass - 1];

    // 3. 遍历源类型和目标类型的属性映射
    sattr = &policydb->type_attr_map_array[scontext->type - 1];
    tattr = &policydb->type_attr_map_array[tcontext->type - 1];

    ebitmap_for_each_positive_bit(sattr, snode, i) {
        ebitmap_for_each_positive_bit(tattr, tnode, j) {
            avkey.source_type = i + 1;
            avkey.target_type = j + 1;
            avkey.target_class = tclass;
            avkey.specified = AVTAB_AV | AVTAB_XPERMS;

            // 在 TE AV 表中查找规则
            for (node = avtab_search_node(&policydb->te_avtab, &avkey);
                 node;
                 node = avtab_search_node_next(node, avkey.specified)) {

                if (node->key.specified == AVTAB_ALLOWED)
                    avd->allowed |= node->datum.u.data;
                else if (node->key.specified == AVTAB_AUDITALLOW)
                    avd->auditallow |= node->datum.u.data;
                else if (node->key.specified == AVTAB_AUDITDENY)
                    avd->auditdeny &= node->datum.u.data;
            }

            // 检查条件 AV 表
            cond_compute_av(&policydb->te_cond_avtab, &avkey, avd, xperms);
        }
    }

    // 4. 应用约束 (包括 MLS 约束)
    constraint = tclass_datum->constraints;
    while (constraint) {
        if ((constraint->permissions & avd->allowed) &&
            !constraint_expr_eval(policydb, scontext, tcontext, NULL,
                      constraint->expr)) {
            // 约束表达式评估失败,移除该权限
            avd->allowed &= ~(constraint->permissions);
        }
        constraint = constraint->next;
    }

    // 5. 检查角色转换权限
    if (tclass == policydb->process_class &&
        (avd->allowed & policydb->process_trans_perms) &&
        scontext->role != tcontext->role) {
        // 检查角色是否允许转换
        for (ra = policydb->role_allow; ra; ra = ra->next) {
            if (scontext->role == ra->role &&
                tcontext->role == ra->new_role)
                break;
        }
        if (!ra)
            avd->allowed &= ~policydb->process_trans_perms;
    }

    // 6. 应用类型边界约束
    type_attribute_bounds_av(policydb, scontext, tcontext, tclass, avd);
}
```

### 4.4 security_compute_av() - 主入口

计算访问向量的公共接口。

**函数实现** (`services.c`, 第 1123-1189 行):

```c
void security_compute_av(u32 ssid, u32 tsid, u16 orig_tclass,
             struct av_decision *avd,
             struct extended_perms *xperms)
{
    struct selinux_policy *policy;
    struct policydb *policydb;
    struct sidtab *sidtab;
    struct context *scontext, *tcontext;

    rcu_read_lock();

    policy = rcu_dereference(selinux_state.policy);
    avd_init(policy, avd);

    if (!selinux_initialized())
        goto allow;  // 未初始化时允许所有

    policydb = &policy->policydb;
    sidtab = policy->sidtab;

    // 查找源和目标上下文
    scontext = sidtab_search(sidtab, ssid);
    tcontext = sidtab_search(sidtab, tsid);

    // 检查 permissive 域
    if (ebitmap_get_bit(&policydb->permissive_map, scontext->type))
        avd->flags |= AVD_FLAGS_PERMISSIVE;

    // 检查 neveraudit 域
    if (ebitmap_get_bit(&policydb->neveraudit_map, scontext->type))
        avd->flags |= AVD_FLAGS_NEVERAUDIT;

    // 映射并计算访问向量
    tclass = unmap_class(&policy->map, orig_tclass);
    context_struct_compute_av(policydb, scontext, tcontext, tclass, avd, xperms);
    map_decision(&policy->map, orig_tclass, avd, policydb->allow_unknown);

    rcu_read_unlock();
    return;

allow:
    avd->allowed = 0xffffffff;  // 允许所有权限
    goto out;
}
```

---

## 5. 钩子实现

### 5.1 inode_has_perm() - inode 权限检查

**函数实现** (`hooks.c`, 第 1677-1692 行):

```c
static int inode_has_perm(const struct cred *cred,
              struct inode *inode,
              u32 perms,
              struct common_audit_data *adp)
{
    struct inode_security_struct *isec;
    u32 sid;

    if (unlikely(IS_PRIVATE(inode)))
        return 0;  // 私有 inode 不检查

    sid = cred_sid(cred);
    isec = selinux_inode(inode);

    // 调用 AVC 检查权限
    return avc_has_perm(sid, isec->sid, isec->sclass, perms, adp);
}
```

### 5.2 file_has_perm() - 文件权限检查

**函数实现** (`hooks.c`, 第 1756-1792 行):

```c
static int file_has_perm(const struct cred *cred,
             struct file *file,
             u32 av)
{
    struct file_security_struct *fsec = selinux_file(file);
    struct inode *inode = file_inode(file);
    struct common_audit_data ad;
    u32 sid = cred_sid(cred);
    int rc;

    ad.type = LSM_AUDIT_DATA_FILE;
    ad.u.file = file;

    // 检查文件描述符 SID 与进程 SID 是否匹配
    if (sid != fsec->sid) {
        // 不匹配时检查 FD__USE 权限
        rc = avc_has_perm(sid, fsec->sid,
                  SECCLASS_FD,
                  FD__USE,
                  &ad);
        if (rc)
            goto out;
    }

    // 检查文件的实际权限
    rc = inode_has_perm(cred, inode, av, &ad);

out:
    return rc;
}
```

### 5.3 task_has_perm() - 任务权限检查

SELinux 使用 `avc_has_perm()` 直接检查任务权限:

**任务相关权限检查示例** (`hooks.c`, 第 4374-4491 行):

```c
static int selinux_task_setpgid(struct task_struct *p, pid_t pgid)
{
    return avc_has_perm(current_sid(), task_sid_obj(p), SECCLASS_PROCESS,
                PROCESS__SETPGID, NULL);
}

static int selinux_task_getpgid(struct task_struct *p)
{
    return avc_has_perm(current_sid(), task_sid_obj(p), SECCLASS_PROCESS,
                PROCESS__GETPGID, NULL);
}

static int selinux_task_getsid(struct task_struct *p)
{
    return avc_has_perm(current_sid(), task_sid_obj(p), SECCLASS_PROCESS,
                PROCESS__GETSESSION, NULL);
}

static int selinux_task_setnice(struct task_struct *p, int nice)
{
    return avc_has_perm(current_sid(), task_sid_obj(p), SECCLASS_PROCESS,
                PROCESS__SETSCHED, NULL);
}

static int selinux_task_kill(struct task_struct *p, struct kernel_siginfo *info,
                int sig, const struct cred *cred)
{
    u32 sid = cred_sid(cred);
    u32 tsid = task_sid_obj(p);

    return avc_has_perm(sid, tsid, SECCLASS_PROCESS, PROCESS__SIGINH, NULL);
}
```

### 5.4 superblock_has_perm() - 超级块权限检查

**函数实现** (`hooks.c`, 第 1965-1975 行):

```c
static int superblock_has_perm(const struct cred *cred,
                   const struct super_block *sb,
                   u32 perms,
                   struct common_audit_data *ad)
{
    struct superblock_security_struct *sbsec;
    u32 sid = cred_sid(cred);

    sbsec = selinux_superblock(sb);
    return avc_has_perm(sid, sbsec->sid, SECCLASS_FILESYSTEM, perms, ad);
}
```

### 5.5 selinux_inode_permission() - inode 权限钩子

**函数实现** (`hooks.c`, 第 3222-3274 行):

```c
static int selinux_inode_permission(struct inode *inode, int requested)
{
    int mask;
    u32 perms;
    u32 sid = current_sid();
    struct task_security_struct *tsec;
    struct inode_security_struct *isec;
    struct avdc_entry *avdc;
    int rc, rc2;
    u32 audited, denied;

    mask = requested & (MAY_READ|MAY_WRITE|MAY_EXEC|MAY_APPEND);

    // 无权限检查时为存在性测试
    if (!mask)
        return 0;

    tsec = selinux_task(current);

    // 检查任务 AVC 缓存 (permissive 且 neveraudit)
    if (task_avdcache_permnoaudit(tsec, sid))
        return 0;

    // 获取 inode 安全结构
    isec = inode_security_rcu(inode, requested & MAY_NOT_BLOCK);
    if (IS_ERR(isec))
        return PTR_ERR(isec);

    // 转换文件模式掩码为访问向量
    perms = file_mask_to_av(inode->i_mode, mask);

    // 在任务 AVC 缓存中搜索
    rc = task_avdcache_search(tsec, isec, &avdc);
    if (likely(!rc)) {
        // 缓存命中
        audited = perms & avdc->audited;
        denied = perms & ~avdc->allowed;
        if (unlikely(denied && enforcing_enabled() && !avdc->permissive))
            rc = -EACCES;
    } else {
        // 缓存未命中,调用 AVC
        struct av_decision avd;

        rc = avc_has_perm_noaudit(sid, isec->sid, isec->sclass,
                      perms, 0, &avd);
        audited = avc_audit_required(perms, &avd, rc,
            (requested & MAY_ACCESS) ? FILE__AUDIT_ACCESS : 0,
            &denied);
        task_avdcache_update(tsec, isec, &avd, audited);
    }

    if (likely(!audited))
        return rc;

    rc2 = audit_inode_permission(inode, perms, audited, denied, rc);
    if (rc2)
        return rc2;

    return rc;
}
```

---

## 6. 核心数据结构关系图

### 6.1 SELinux 架构层次图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户空间                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   setroublesc│  │   semanage   │  │   sealert            │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                     │
│                    ┌──────▼──────┐                             │
│                    │  /selinux   │  (selinuxfs)               │
│                    └──────┬──────┘                             │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     内核空间 - SELinux                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     hooks.c                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │ │
│  │  │ inode_*     │  │ file_*      │  │ task_*          │    │ │
│  │  │ permission  │  │ has_perm    │  │ has_perm        │    │ │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │ │
│  │         │                │                   │             │ │
│  │         └────────────────┴───────────────────┘             │ │
│  │                          │                                 │ │
│  │                   ┌──────▼──────┐                          │ │
│  │                   │ avc_has_perm│                          │ │
│  │                   └──────┬──────┘                          │ │
│  └──────────────────────────┼──────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │                        avc.c                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │ │
│  │  │ 缓存查找     │  │ 权限计算      │  │ 审计处理       │   │ │
│  │  │ avc_lookup   │  │ avc_denied   │  │ slow_avc_audit│   │ │
│  │  └──────────────┘  └──────────────┘  └────────────────┘   │ │
│  └──────────────────────────┬────────────────────────────────┘ │
│                             │ (缓存未命中)                       │
│  ┌──────────────────────────▼────────────────────────────────┐ │
│  │                     ss/services.c                         │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │          security_compute_av()                       │ │ │
│  │  │  ┌─────────────────┐  ┌─────────────────────────┐  │ │ │
│  │  │  │ sidtab_search()  │  │ context_struct_compute_ │  │ │ │
│  │  │  │  查找上下文      │  │ _av() 计算权限决策      │  │ │ │
│  │  │  └─────────────────┘  └─────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────┬────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼────────────────────────────────┐ │
│  │                    ss/policydb.c                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │ te_avtab │  │ role_tr  │  │filename_ │  │ range_tr │ │ │
│  │  │ TE规则表 │  │ 角色转换  │  │ trans    │  │ MLS范围  │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 权限检查流程图

```
进程访问文件
     │
     ▼
┌────────────────┐
│ inode_permission│ hooks.c:3222
│     钩子       │
└───────┬────────┘
        │
        ▼
┌────────────────────────────────────────┐
│  获取 current_sid() 和 isec->sid       │
│  (当前进程 SID 和 inode SID)            │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│  task_avdcache_search()                │
│  检查任务本地 AVC 缓存                  │
└───────┬────────────────────────────────┘
        │
   ┌────┴────┐
   │ 命中?   │
   └────┬────┘
    Yes │    No
        ▼         ▼
┌──────────┐  ┌─────────────────────────────────────┐
│检查 allowed│  │ avc_has_perm_noaudit()              │
│ 和 audited │  │ 1. avc_lookup() 查找 AVC 缓存       │
│ 位掩码     │  │ 2. 缓存未命中 → avc_perm_nonode()  │
└────┬─────┘  │    → 调用 security_compute_av()      │
     │        │ 3. 检查 denied 权限                  │
     │        └───────────────┬─────────────────────┘
     │                        │
     │         ┌─────────────▼─────────────┐
     │         │ security_compute_av()       │
     │         │ 1. sidtab_search() 查找上下文│
     │         │ 2. context_struct_compute_  │
     │         │    _av() 计算权限           │
     │         │ 3. 应用约束和 MLS 策略     │
     │         └─────────────┬───────────────┘
     │                       │
     ▼                       ▼
┌─────────────────────────────────────┐
│       avc_audit() 审计               │
│  (根据 auditallow/auditdeny 决定    │
│   是否记录审计日志)                 │
└─────────────────┬───────────────────┘
                  │
                  ▼
           ┌──────────────┐
           │   返回结果   │
           │ 0 = 允许     │
           │ -EACCES = 拒绝│
           └──────────────┘
```

### 6.3 关键数据结构关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                         struct policydb                             │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  mls_enabled          : MLS 是否启用                             │ │
│  │  symtab[]             : 符号表数组 (types, roles, users, classes) │ │
│  │  te_avtab             : 类型强制访问向量表                        │ │
│  │  role_tr              : 角色转换哈希表                            │ │
│  │  filename_trans      : 文件名转换哈希表                          │ │
│  │  range_tr             : MLS 范围转换哈希表                       │ │
│  │  role_allow           : 角色允许链表                             │ │
│  │  ocontexts[]          : 初始 SID 等上下文列表                    │ │
│  │  cond_list            : 条件策略链表                             │ │
│  │  permissive_map      : permissive 类型位图                      │ │
│  │  neveraudit_map      : neveraudit 类型位图                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ 被引用
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         struct sidtab                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  roots[]               : 树形结构的根节点                        │ │
│  │  count                 : 当前 SID 数量                          │ │
│  │  isids[]               : 初始 SID 条目                           │ │
│  │  context_to_sid        : 哈希表 (上下文 → SID 反向查找)         │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                │
│                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       struct sidtab_entry                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  sid                    : 安全标识符                             │ │
│  │  hash                  : 哈希值                                  │ │
│  │  context               : 安全上下文结构体                       │ │
│  │  cache                 : SID → 字符串缓存                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         struct context                              │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  user                   : 用户 ID                               │ │
│  │  role                   : 角色 ID                               │ │
│  │  type                   : 类型 ID (TE 核心)                     │ │
│  │  range                  : MLS 范围                               │ │
│  │  str                    : 字符串表示 (可选)                      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.4 安全对象标签结构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        内核对象                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │   inode    │  │    file    │  │ super_block│  │   task     │    │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │
│        │               │               │               │            │
│        ▼               ▼               ▼               ▼            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│  │ i_security│  │ f_security│  │ s_security│  │ t->security│         │
│  │ (blob)    │  │ (blob)    │  │ (blob)    │  │ (blob)    │         │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘         │
│        │               │               │               │            │
└────────┼───────────────┼───────────────┼───────────────┼────────────┘
         │               │               │               │
         ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│               SELinux 对象安全结构                                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐   │
│  │ inode_security  │ │ file_security   │ │ superblock_security │   │
│  │ _struct         │ │ _struct         │ │ _struct             │   │
│  ├─────────────────┤ ├─────────────────┤ ├─────────────────────┤   │
│  │ sid             │ │ sid             │ │ sid                 │   │
│  │ sclass          │ │ fown_sid        │ │ def_sid             │   │
│  │ task_sid        │ │ isid            │ │ mntpoint_sid        │   │
│  │ initialized     │ │ pseqno          │ │ behavior            │   │
│  └────────┬────────┘ └────────┬────────┘ └──────────┬──────────┘   │
│           │                   │                      │               │
└───────────┼───────────────────┼──────────────────────┼───────────────┘
            │                   │                      │
            └───────────────────┴──────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  SID (u32)     │
                    │  安全标识符    │
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │ policydb │───▶│ sidtab   │───▶│ context  │
     │ (规则)   │    │ (映射)   │    │ (属性)   │
     └──────────┘    └──────────┘    └──────────┘
```

---

## 附录 A: 文件位置汇总

| 文件 | 描述 | 关键行号 |
|------|------|----------|
| `security/selinux/hooks.c` | LSM 钩子实现 | 1677-1692 (inode_has_perm), 1756-1792 (file_has_perm), 3222-3274 (inode_permission) |
| `security/selinux/avc.c` | AVC 实现 | 1145-1171 (avc_has_perm_noaudit), 1189-1203 (avc_has_perm), 754-781 (slow_avc_audit) |
| `security/selinux/ss/services.c` | 安全服务 | 622-723 (context_struct_compute_av), 1123-1189 (security_compute_av), 1753-1949 (security_compute_sid) |
| `security/selinux/ss/policydb.h` | 策略数据库结构 | 236-315 (policydb) |
| `security/selinux/ss/context.h` | 上下文结构 | 28-35 (context) |
| `security/selinux/ss/sidtab.h` | SID 表结构 | 77-105 (sidtab) |
| `security/selinux/ss/avtab.h` | AV 表结构 | 26-48 (avtab_key) |
| `security/selinux/include/objsec.h` | 对象安全结构 | 40-59 (cred_security_struct, task_security_struct), 74-82 (inode_security_struct) |
| `security/selinux/include/security.h` | 安全接口 | 240-246 (av_decision) |
| `security/selinux/ss/mls_types.h` | MLS 类型 | 20-27 (mls_level, mls_range) |

---

## 附录 B: 核心宏和常量

```c
// SID 常量
#define SECSID_NULL   0x00000000  // 未指定 SID
#define SECSID_WILD   0xffffffff  // 通配符 SID

// AV 表规则类型
#define AVTAB_ALLOWED      0x0001
#define AVTAB_AUDITALLOW   0x0002
#define AVTAB_AUDITDENY    0x0004
#define AVTAB_TRANSITION   0x0010
#define AVTAB_MEMBER       0x0020
#define AVTAB_CHANGE       0x0040

// 决策标志
#define AVD_FLAGS_PERMISSIVE  0x0001
#define AVD_FLAGS_NEVERAUDIT  0x0002
```

---

*文档生成时间: 2026-04-26*
*Linux 内核版本: master 分支*
