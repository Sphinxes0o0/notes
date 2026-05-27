# Linux 内核 AppArmor 安全模块详细分析

## 目录

1. [AppArmor 概述](#1-apparmor-概述)
2. [AppArmor 策略](#2-apparmor-策略)
3. [文件权限](#3-文件权限)
4. [任务上下文](#4-任务上下文)
5. [网络控制](#5-网络控制)
6. [ LSM 钩子集成](#6-lsm-钩子集成)
7. [架构图](#7-架构图)

---

## 1. AppArmor 概述

### 1.1 基于路径的 MAC

AppArmor (Application Armor) 是一个基于**路径**的强制访问控制 (MAC) 安全模块，与传统的基于标签的 MAC 系统（如 SELinux）有本质区别。

**核心设计理念：**
- **路径匹配**: AppArmor 通过文件的完整路径而非 inode 或设备号来标识文件
- **配置文件 (Profile)**: 每个应用程序关联一个配置文件，定义其允许访问的资源
- **渐进式安全**: 支持 complain 模式（学习模式）和 enforce 模式（强制模式）

### 1.2 与 SELinux 的区别

| 特性 | AppArmor | SELinux |
|------|----------|---------|
| 标识方式 | 文件路径 | SELinux 上下文 (user:role:type) |
| 策略语言 | 文本配置 | SELinux 策略语言 (基于 MLS/MCS) |
| 复杂度 | 相对简单 | 复杂但功能强大 |
| 学习模式 | 原生支持 (complain 模式) | 需要 setroubleshoot |
| 文件系统覆盖 | 仅支持 AppArmor 标记的文件系统 | 支持所有文件系统 |
| 默认策略 | 允许所有，未列出的权限默认拒绝 | 拒绝所有 |

### 1.3 核心数据结构

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/include/`

```c
// apparmor.h (第19-43行)
//  mediation 类别定义
#define AA_CLASS_FILE       2   // 文件类
#define AA_CLASS_CAP        3   // 能力类
#define AA_CLASS_NET       14   // 网络类
#define AA_CLASS_NS        21   // 命名空间类
#define AA_CLASS_DBUS      32   // DBus 类

// policy.h (第258-282行)
// aa_profile - 基本限制数据结构
struct aa_profile {
    struct aa_policy base;           // 基础组件 (名称、引用计数、列表)
    struct aa_profile __rcu *parent; // 父 profile (支持 profile 继承/hats)
    struct aa_ns *ns;               // 所属命名空间
    enum audit_mode audit;          // 审计模式
    long mode;                      // 执行模式 (enforce/complain/kill/unconfined)
    u32 path_flags;                 // 路径标志
    struct aa_attachment attach;     // 附件规则
    struct aa_loaddata *rawdata;    // 原始策略数据
    int n_rules;
    struct aa_label label;          // 标签 (包含规则向量)
};

// label.h (第127-148行)
// aa_label - 标签结构 (可以包含多个 profile)
struct aa_label {
    struct aa_common_ref count;      // 引用计数
    struct rb_node node;            // 红黑树节点
    struct aa_proxy *proxy;         // 代理 (用于 label 更新)
    __counted char *hname;          // 人类可读的标签名
    long flags;                     // 标志 (FLAG_HAT, FLAG_UNCONFINED, FLAG_NULL 等)
    u32 secid;                      // 安全标识符
    int size;                       // vec 数组中的条目数
    u64 mediates;                   // 位掩码,表示该 label 调解的类别
    union {
        struct {
            struct aa_profile *profile[2];  // 内嵌在 profile 中时使用
            DECLARE_FLEX_ARRAY(struct aa_ruleset *, rules);
        };
        DECLARE_FLEX_ARRAY(struct aa_profile *, vec);  // 复合标签使用
    };
};
```

---

## 2. AppArmor 策略

### 2.1 struct aa_policy: 策略结构

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/policy.c`

```c
// policy.h (第82-121行)
// aa_policydb - 策略匹配引擎
struct aa_policydb {
    struct kref count;              // 引用计数
    struct aa_dfa *dfa;             // DFA 模式匹配
    struct {
        struct aa_perms *perms;     // 权限表
        u32 size;                   // 权限条目数
    };
    struct aa_str_table trans;      // 转换表
    struct aa_tags_struct tags;     // 标签表
    aa_state_t start[AA_CLASS_LAST + 1];  // 每种类别的起始状态
};

// aa_ruleset - 规则集 (第181-203行)
struct aa_ruleset {
    int size;
    struct aa_policydb *policy;      // 通用策略规则
    struct aa_policydb *file;       // 文件访问和域转换规则
    struct aa_caps caps;            // 能力规则
    struct aa_rlimit rlimits;       // 资源限制规则
    int secmark_count;
    struct aa_secmark *secmark;     // 安全标记
};
```

### 2.2 struct profile: 配置文件

**Profile 层次结构**:
```
Namespace (命名空间)
  |
  +-- unconfined profile (无限制配置)
  |
  +-- profile // 子 profile
  |     |
  |     +-- hat (帽子/子配置)
  |     +-- null-XXX (学习模式配置)
  |
  +-- profile // 另一个配置
```

**Profile 分配** (policy.c 第367-412行):

```c
struct aa_profile *aa_alloc_profile(const char *hname, struct aa_proxy *proxy,
                                   gfp_t gfp)
{
    struct aa_profile *profile;

    // 分配 flexible array, 为 label.rules 预留空间
    profile = kzalloc_flex(*profile, label.rules, 1, gfp);
    if (!profile)
        return NULL;

    // 初始化基础策略结构
    if (!aa_policy_init(&profile->base, NULL, hname, gfp))
        goto fail;
    // 初始化标签
    if (!aa_label_init(&profile->label, 1, gfp))
        goto fail;

    // 分配第一个规则集
    profile->label.rules[0] = aa_alloc_ruleset(gfp);
    if (!profile->label.rules[0])
        goto fail;
    profile->n_rules = 1;

    // 设置 proxy (用于 label 版本管理)
    if (!proxy) {
        proxy = aa_alloc_proxy(&profile->label, gfp);
        if (!proxy)
            goto fail;
    } else
        aa_get_proxy(proxy);
    profile->label.proxy = proxy;

    profile->label.hname = profile->base.hname;
    profile->label.flags |= FLAG_PROFILE;  // 标记为 profile
    profile->label.vec[0] = profile;

    profile->signal = SIGKILL;  // kill 模式下使用的信号

    return profile;

fail:
    aa_free_profile(profile);
    return NULL;
}
```

### 2.3 aa_load_policy(): 策略加载

**aa_replace_profiles()** (policy.c 第1162-1408行)

```c
ssize_t aa_replace_profiles(struct aa_ns *policy_ns, struct aa_label *label,
                            u32 mask, struct aa_loaddata *udata)
{
    // 策略加载流程:
    // 1. 解包序列化数据
    //    error = aa_unpack(udata, &lh, &ns_name);

    // 2. 验证所有 profile 属于同一命名空间
    //    list_for_each_entry(ent, &lh, list) { ... }

    // 3. 准备命名空间
    //    ns = aa_prepare_ns(policy_ns ? policy_ns : labels_ns(label), ns_name);

    // 4. 查找并替换/添加 profile
    //    mutex_lock_nested(&ns->lock, ns->level);
    //    list_for_each_entry(ent, &lh, list) {
    //        error = __lookup_replace(ns, ent->new->base.hname, ...);
    //        // 设置父 profile 和命名空间
    //        ent->new->ns = aa_get_ns(ns);
    //    }

    // 5. 更新命名空间版本号
    //    __aa_bump_ns_revision(ns);

    // 6. 执行替换或添加
    //    list_for_each_entry_safe(ent, tmp, &lh, list) {
    //        if (ent->old) {
    //            share_name(ent->old, ent->new);
    //            __replace_profile(ent->old, ent->new);
    //        } else {
    //            __add_profile(lh, ent->new);
    //        }
    //    }

    // 7. 更新标签集子树
    //    __aa_labelset_update_subtree(ns);
}
```

**策略管理权限检查** (policy.c 第971-1009行):

```c
int aa_may_manage_policy(const struct cred *subj_cred, struct aa_label *label,
                         struct aa_ns *ns, const struct cred *ocred, u32 mask)
{
    // 1. 检查策略是否被锁定
    if (aa_g_lock_policy)
        return audit_policy(label, op, NULL, NULL, "policy_locked", -EACCES);

    // 2. 检查对象权限
    if (ocred && !is_subset_of_obj_privilege(subj_cred, label, ocred))
        return audit_policy(label, op, NULL, NULL,
            "not privileged for target profile", -EACCES);

    // 3. 检查 MAC_ADMIN capability
    if (!aa_policy_admin_capable(subj_cred, label, ns))
        return audit_policy(label, op, NULL, NULL, "not policy admin", -EACCES);

    return 0;
}
```

---

## 3. 文件权限

### 3.1 aa_file_permission(): 文件权限检查

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/main.c`

**文件上下文缓存** (file.h 第37-46行):

```c
// aa_file_ctx - 文件打开时的 AppArmor 上下文
struct aa_file_ctx {
    spinlock_t lock;                    // 锁
    struct aa_label __rcu *label;       // 缓存的文件标签
    u32 allow;                          // 允许的权限
};
```

**aa_file_perm()** (main.c 第619-671行):

```c
int aa_file_perm(const char *op, const struct cred *subj_cred,
                 struct aa_label *label, struct file *file,
                 u32 request, bool in_atomic)
{
    struct aa_file_ctx *fctx;
    struct aa_label *flabel;
    u32 denied;
    int error = 0;

    // 获取文件的安全上下文
    fctx = file_ctx(file);
    rcu_read_lock();
    flabel = rcu_dereference(fctx->label);

    // 快速路径: 如果任务无限制或权限已缓存且足够,则跳过检查
    denied = request & ~fctx->allow;
    if (unconfined(label) || __file_is_delegated(flabel) ||
        (!denied && __is_unix_file(file) && !__unix_needs_revalidation(...)) ||
        (!denied && __aa_subj_label_is_cached(label, flabel))) {
        rcu_read_unlock();
        goto done;
    }

    // 慢速路径: 重新验证访问权限
    flabel = aa_get_newest_label(flabel);
    rcu_read_unlock();

    // 根据文件系统类型选择检查方法
    if (path_mediated_fs(file->f_path.dentry))
        error = __file_path_perm(op, subj_cred, label, flabel, file,
                                 request, denied, in_atomic);
    else if (S_ISSOCK(file_inode(file)->i_mode))
        error = __file_sock_perm(op, subj_cred, label, flabel, file,
                                  request, denied);

    aa_put_label(flabel);

done:
    return error;
}
```

**__file_path_perm()** (main.c 第483-542行):

```c
static int __file_path_perm(const char *op, const struct cred *subj_cred,
                            struct aa_label *label, struct aa_label *flabel,
                            struct file *file, u32 request, u32 denied,
                            bool in_atomic)
{
    // 获取文件所有者信息
    vfsuid_t vfsuid = i_uid_into_vfsuid(file_mnt_idmap(file),
                                        file_inode(file));
    struct path_cond cond = {
        .uid = vfsuid_into_kuid(vfsuid),
        .mode = file_inode(file)->i_mode
    };

    // 如果 label 是 flabel 的子集,且权限未被拒绝,则不需要重新检查
    if (!denied && aa_label_is_subset(flabel, label))
        return 0;

    // 检查每个 profile
    error = fn_for_each_not_in_set(flabel, label, profile,
            profile_path_perm(op, subj_cred, profile,
                              &file->f_path, buffer,
                              request, &cond, flags, &perms));

    // 更新文件上下文缓存
    if (!error)
        update_file_ctx(file_ctx(file), label, request);
}
```

**aa_path_perm()** (main.c 第280-302行):

```c
int aa_path_perm(const char *op, const struct cred *subj_cred,
                 struct aa_label *label, const struct path *path, int flags,
                 u32 request, struct path_cond *cond)
{
    struct aa_perms perms = {};
    struct aa_profile *profile;
    char *buffer = NULL;
    int error;

    // 设置额外标志
    flags |= PATH_DELEGATE_DELETED | (S_ISDIR(cond->mode) ? PATH_IS_DIR : 0);

    buffer = aa_get_buffer(false);
    if (!buffer)
        return -ENOMEM;

    // 为 label 中的每个受限 profile 检查权限
    error = fn_for_each_confined(label, profile,
            profile_path_perm(op, subj_cred, profile, path, buffer,
                              request, cond, flags, &perms));

    aa_put_buffer(buffer);
    return error;
}
```

### 3.2 aa_path_link(): 链接权限

**硬链接权限检查** (main.c 第430-460行):

```c
int aa_path_link(const struct cred *subj_cred, struct aa_label *label,
                 struct dentry *old_dentry, const struct path *new_dir,
                 struct dentry *new_dentry)
{
    struct path link = { .mnt = new_dir->mnt, .dentry = new_dentry };
    struct path target = { .mnt = new_dir->mnt, .dentry = old_dentry };
    struct inode *inode = d_backing_inode(old_dentry);
    vfsuid_t vfsuid = i_uid_into_vfsuid(mnt_idmap(target.mnt), inode);
    struct path_cond cond = {
        .uid = vfsuid_into_kuid(vfsuid),
        .mode = inode->i_mode,
    };

    // 检查链接和目标的路径权限
    error = fn_for_each_confined(label, profile,
            profile_path_link(subj_cred, profile, &link, buffer,
                              &target, buffer2, &cond));
}
```

**profile_path_link()** (main.c 第324-409行):

```c
static int profile_path_link(const struct cred *subj_cred,
                             struct aa_profile *profile,
                             const struct path *link, char *buffer,
                             const struct path *target, char *buffer2,
                             struct path_cond *cond)
{
    // 1. 获取链接名称
    error = path_name(OP_LINK, subj_cred, &profile->label, link, ...);

    // 2. 获取目标名称
    error = path_name(OP_LINK, subj_cred, &profile->label, target, ...);

    // 3. 检查链接权限
    state = aa_str_perms(rules->file, ..., lname, cond, &lperms);
    if (!(lperms.allow & AA_MAY_LINK))
        goto audit;

    // 4. 从链接状态继续检查目标权限
    state = aa_dfa_null_transition(rules->file->dfa, state);
    aa_str_perms(rules->file, state, tname, cond, &perms);

    // 5. 子集测试: 链接权限必须是目标权限的子集
    if (perms.allow & AA_LINK_SUBSET) {
        request = lperms.allow & ~AA_MAY_LINK;
        lperms.allow &= perms.allow | AA_MAY_LINK;
        // 检查执行权限
        if ((lperms.allow & MAY_EXEC) &&
            !xindex_is_subset(lperms.xindex, perms.xindex)) {
            // 链接不是目标的子集
        }
    }
}
```

### 3.3 aa_path_rmdir(): 删除权限

**通过 LSM 钩子集成** (lsm.c 第336-339行):

```c
static int apparmor_path_rmdir(const struct path *dir, struct dentry *dentry)
{
    return common_perm_rm(OP_RMDIR, dir, dentry, AA_MAY_DELETE);
}
```

**common_perm_rm()** (lsm.c 第286-301行):

```c
static int common_perm_rm(const char *op, const struct path *dir,
                          struct dentry *dentry, u32 mask)
{
    struct inode *inode = d_backing_inode(dentry);
    struct path_cond cond = {};
    vfsuid_t vfsuid;

    if (!inode || !path_mediated_fs(dentry))
        return 0;

    vfsuid = i_uid_into_vfsuid(mnt_idmap(dir->mnt), inode);
    cond.uid = vfsuid_into_kuid(vfsuid);
    cond.mode = inode->i_mode;

    return common_perm_dir_dentry(op, dir, dentry, mask, &cond);
}
```

---

## 4. 任务上下文

### 4.1 aa_bprm_set_creds(): exec 时设置凭证

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/domain.c`

**apparmor_bprm_creds_for_exec()** (domain.c 第919-1046行):

```c
int apparmor_bprm_creds_for_exec(struct linux_binprm *bprm)
{
    struct aa_task_ctx *ctx;
    struct aa_label *label, *new = NULL;
    const struct cred *subj_cred;
    char *buffer = NULL;
    int error = 0;
    bool unsafe = false;

    subj_cred = current_cred();
    ctx = task_ctx(current);

    label = aa_get_newest_label(cred_label(bprm->cred));

    // 检测 no_new_privs 并存储当时的 label
    if ((bprm->unsafe & LSM_UNSAFE_NO_NEW_PRIVS) && !unconfined(label) &&
        !ctx->nnp)
        ctx->nnp = aa_get_label(label);

    // 先检查 onexec 转换
    if (ctx->onexec)
        new = handle_onexec(subj_cred, label, ctx->onexec, ctx->token,
                            bprm, buffer, &cond, &unsafe);
    else
        new = fn_label_build(label, profile, GFP_KERNEL,
                profile_transition(subj_cred, profile, bprm,
                                   buffer, &cond, &unsafe));

    // no_new_privs 检查: 确保转换后的域是之前域的子集
    if ((bprm->unsafe & LSM_UNSAFE_NO_NEW_PRIVS) &&
        !unconfined(label) &&
        !aa_label_is_unconfined_subset(new, ctx->nnp)) {
        error = -EPERM;
        info = "no new privs";
        goto audit;
    }

    // ptrace 检查
    if (bprm->unsafe & (LSM_UNSAFE_PTRACE)) {
        error = may_change_ptraced_domain(bprm->cred, new, &info);
        if (error)
            goto audit;
    }

    // 设置 AT_SECURE 标志
    if (unsafe)
        bprm->secureexec = 1;

    // 更新 bprm 的 cred label
    aa_put_label(cred_label(bprm->cred));
    set_cred_label(bprm->cred, new);
}
```

**profile_transition()** (domain.c 第659-790行):

```c
static struct aa_label *profile_transition(const struct cred *subj_cred,
                                           struct aa_profile *profile,
                                           const struct linux_binprm *bprm,
                                           char *buffer, struct path_cond *cond,
                                           bool *secure_exec)
{
    // 1. 解析可执行文件路径
    error = aa_path_name(&bprm->file->f_path, profile->path_flags, buffer,
                         &name, &info, profile->disconnected);

    // 2. 如果是无限制 profile,查找附件配置
    if (profile_unconfined(profile)) {
        new = find_attach(bprm, profile->ns, &profile->ns->base.profiles,
                          name, &info);
        // ...
    }

    // 3. 查找 exec 权限
    state = aa_str_perms(rules->file, state, name, cond, &perms);

    // 4. 确定转换目标
    if (perms.allow & MAY_EXEC) {
        new = x_to_label(profile, bprm, name, perms.xindex, &target, &info);
        // ...
    }

    // 5. 如果是不安全 exec,设置 secure_exec 标志
    if (!(perms.xindex & AA_X_UNSAFE)) {
        *secure_exec = true;
    }
}
```

### 4.2 aa_task_perm(): 任务权限

**任务上下文结构** (task.h 第25-30行):

```c
// aa_task_ctx - 任务标签变更信息
struct aa_task_ctx {
    struct aa_label *nnp;       // no_new_privs 时的快照
    struct aa_label *onexec;    // 下一个 exec 时的转换目标
    struct aa_label *previous;  // 可返回的前一个 profile (用于 change_hat)
    u64 token;                  // change_hat 的魔数
};
```

**change_hat()** - 子域/帽子切换 (domain.c 第1107-1204行):

```c
static struct aa_label *change_hat(const struct cred *subj_cred,
                                   struct aa_label *label, const char *hats[],
                                   int count, int flags)
{
    // 在当前 label 中查找匹配的帽子
    for (i = 0; i < count && !hat; i++) {
        name = hats[i];
        label_for_each_in_scope(it, labels_ns(label), label, profile) {
            hat = aa_find_child(root, name);
            if (!hat && COMPLAIN_MODE(profile)) {
                // 创建学习模式的 null profile
                hat = aa_new_learning_profile(profile, true, name, GFP_KERNEL);
            }
        }
    }

    // 构建新的复合 label
    new = fn_label_build_in_scope(label, profile, GFP_KERNEL,
                   build_change_hat(subj_cred, profile, name, sibling),
                   aa_get_label(&profile->label));
}
```

**aa_change_hat()** (domain.c 第1223-1349行):

```c
int aa_change_hat(const char *hats[], int count, u64 token, int flags)
{
    // 1. 获取当前 label
    label = aa_get_newest_cred_label(subj_cred);
    previous = aa_get_newest_label(ctx->previous);

    // 2. 检测 no_new_privs
    if (task_no_new_privs(current) && !unconfined(label) && !ctx->nnp)
        ctx->nnp = aa_get_label(label);

    // 3. 如果 count > 0,切换到帽子
    if (count) {
        new = change_hat(subj_cred, label, hats, count, flags);
        error = may_change_ptraced_domain(subj_cred, new, &info);
        if (error)
            goto fail;
        target = new;
        error = aa_set_current_hat(new, token);
    }
    // 4. 如果 count == 0,恢复到之前的 profile
    else if (previous && !(flags & AA_CHANGE_TEST)) {
        target = previous;
        error = aa_restore_previous_label(token);
    }
}
```

---

## 5. 网络控制

### 5.1 aa_sock_perm(): 套接字权限

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/net.c`

**aa_sk_perm()** (net.c 第306-320行):

```c
int aa_sk_perm(const char *op, u32 request, struct sock *sk)
{
    struct aa_label *label;
    int error;

    label = begin_current_label_crit_section();
    error = aa_label_sk_perm(current_cred(), label, op, request, sk);
    end_current_label_crit_section(label);

    return error;
}
```

**aa_label_sk_perm()** (net.c 第283-304行):

```c
static int aa_label_sk_perm(const struct cred *subj_cred,
                            struct aa_label *label,
                            const char *op, u32 request,
                            struct sock *sk)
{
    struct aa_sk_ctx *ctx = aa_sock(sk);
    int error = 0;

    // 检查 socket 是否关联了非 kernel_t 的标签
    if (rcu_access_pointer(ctx->label) != kernel_t && !unconfined(label)) {
        struct aa_profile *profile;
        DEFINE_AUDIT_SK(ad, op, subj_cred, sk);

        ad.subj_cred = subj_cred;
        error = fn_for_each_confined(label, profile,
                aa_profile_af_sk_perm(profile, &ad, request, sk));
    }

    return error;
}
```

**aa_profile_af_perm()** (net.c 第250-270行):

```c
int aa_profile_af_perm(struct aa_profile *profile,
                       struct apparmor_audit_data *ad, u32 request,
                       u16 family, int type, int protocol)
{
    struct aa_ruleset *rules = profile->label.rules[0];
    struct aa_perms *p = NULL;
    aa_state_t state;

    if (profile_unconfined(profile))
        return 0;

    // 获取网络调解的起始状态
    state = RULE_MEDIATES_NET(rules);
    if (!state)
        return 0;

    // 匹配地址族、类型、协议
    state = aa_match_to_prot(rules->policy, state, request, family, type,
                             protocol, &p, &ad->info);
    return aa_do_perms(profile, rules->policy, state, request, p, ad);
}
```

**aa_match_to_prot()** (net.c 第224-247行):

```c
aa_state_t aa_match_to_prot(struct aa_policydb *policy, aa_state_t state,
                            u32 request, u16 af, int type, int protocol,
                            struct aa_perms **p, const char **info)
{
    // 1. 匹配地址族
    state = aa_dfa_match_be16(policy->dfa, state, (u16)af);
    if (!state) {
        *info = "failed af match";
        return state;
    }

    // 2. 匹配 socket 类型
    state = aa_dfa_match_be16(policy->dfa, state, (u16)type);
    if (state) {
        if (p)
            *p = early_match(policy, state, request);
        if (!p || !*p) {
            // 3. 匹配协议
            state = aa_dfa_match_be16(policy->dfa, state, (u16)protocol);
            if (!state)
                *info = "failed protocol match";
        }
    } else {
        *info = "failed type match";
    }

    return state;
}
```

**网络权限类别** (apparmor.h 第30-31行):

```c
#define AA_CLASS_NET    14   // 网络类 (v7/v8)
#define AA_CLASS_NETV9  15   // 网络类 (v9)
```

**网络权限掩码** (net.c 第34-74行):

```c
static const char * const net_mask_names[] = {
    "unknown",
    "send",              // AA_MAY_SEND
    "receive",           // AA_MAY_RECEIVE
    "unknown",
    "create",            // AA_MAY_CREATE
    "shutdown",          // AA_MAY_SHUTDOWN
    "connect",          // AA_MAY_CONNECT
    "unknown",
    "setattr",          // AA_MAY_SETATTR
    "getattr",          // AA_MAY_GETATTR
    "setcred",          // AA_MAY_SETCREDS
    "getcred",          // AA_MAY_GETCREDS
    // ...
    "accept",           // AA_MAY_ACCEPT
    "bind",             // AA_MAY_BIND
    "listen",           // AA_MAY_LISTEN
    // ...
    "setopt",           // AA_MAY_SETOPT
    "getopt",           // AA_MAY_GETOPT
};
```

**Unix 域套接字特殊处理** (lsm.c 第1366-1369行):

```c
static int apparmor_socket_bind(struct socket *sock,
                                struct sockaddr *address, int addrlen)
{
    if (sock->sk->sk_family == PF_UNIX)
        return aa_unix_bind_perm(sock, address, addrlen);
    return aa_sk_perm(OP_BIND, AA_MAY_BIND, sock->sk);
}
```

---

## 6. LSM 钩子集成

### 6.1 钩子注册

**源码位置**: `/Users/sphinx/github/linux/security/apparmor/lsm.c`

**安全钩子列表** (lsm.c 第1664-1769行):

```c
static struct security_hook_list apparmor_hooks[] __ro_after_init = {
    // PTrace 钩子
    LSM_HOOK_INIT(ptrace_access_check, apparmor_ptrace_access_check),
    LSM_HOOK_INIT(ptrace_traceme, apparmor_ptrace_traceme),

    // Capability 钩子
    LSM_HOOK_INIT(capget, apparmor_capget),
    LSM_HOOK_INIT(capable, apparmor_capable),

    // 文件系统钩子
    LSM_HOOK_INIT(sb_mount, apparmor_sb_mount),
    LSM_HOOK_INIT(sb_umount, apparmor_sb_umount),
    LSM_HOOK_INIT(sb_pivotroot, apparmor_sb_pivotroot),
    LSM_HOOK_INIT(move_mount, apparmor_move_mount),

    // Path 钩子
    LSM_HOOK_INIT(path_link, apparmor_path_link),
    LSM_HOOK_INIT(path_unlink, apparmor_path_unlink),
    LSM_HOOK_INIT(path_symlink, apparmor_path_symlink),
    LSM_HOOK_INIT(path_mkdir, apparmor_path_mkdir),
    LSM_HOOK_INIT(path_rmdir, apparmor_path_rmdir),
    LSM_HOOK_INIT(path_mknod, apparmor_path_mknod),
    LSM_HOOK_INIT(path_rename, apparmor_path_rename),
    LSM_HOOK_INIT(path_chmod, apparmor_path_chmod),
    LSM_HOOK_INIT(path_chown, apparmor_path_chown),
    LSM_HOOK_INIT(path_truncate, apparmor_path_truncate),

    // File 钩子
    LSM_HOOK_INIT(file_open, apparmor_file_open),
    LSM_HOOK_INIT(file_receive, apparmor_file_receive),
    LSM_HOOK_INIT(file_permission, apparmor_file_permission),
    LSM_HOOK_INIT(file_alloc_security, apparmor_file_alloc_security),
    LSM_HOOK_INIT(file_free_security, apparmor_file_free_security),
    LSM_HOOK_INIT(mmap_file, apparmor_mmap_file),
    LSM_HOOK_INIT(file_mprotect, apparmor_file_mprotect),
    LSM_HOOK_INIT(file_lock, apparmor_file_lock),
    LSM_HOOK_INIT(file_truncate, apparmor_file_truncate),

    // Socket 钩子
    LSM_HOOK_INIT(socket_create, apparmor_socket_create),
    LSM_HOOK_INIT(socket_post_create, apparmor_socket_post_create),
    LSM_HOOK_INIT(socket_bind, apparmor_socket_bind),
    LSM_HOOK_INIT(socket_connect, apparmor_socket_connect),
    LSM_HOOK_INIT(socket_listen, apparmor_socket_listen),
    LSM_HOOK_INIT(socket_accept, apparmor_socket_accept),
    LSM_HOOK_INIT(socket_sendmsg, apparmor_socket_sendmsg),
    LSM_HOOK_INIT(socket_recvmsg, apparmor_socket_recvmsg),
    LSM_HOOK_INIT(socket_getsockname, apparmor_socket_getsockname),
    LSM_HOOK_INIT(socket_getpeername, apparmor_socket_getpeername),
    LSM_HOOK_INIT(socket_getsockopt, apparmor_socket_getsockopt),
    LSM_HOOK_INIT(socket_setsockopt, apparmor_socket_setsockopt),
    LSM_HOOK_INIT(socket_shutdown, apparmor_socket_shutdown),
    LSM_HOOK_INIT(unix_stream_connect, apparmor_unix_stream_connect),
    LSM_HOOK_INIT(unix_may_send, apparmor_unix_may_send),

    // Task 钩子
    LSM_HOOK_INIT(bprm_creds_for_exec, apparmor_bprm_creds_for_exec),
    LSM_HOOK_INIT(bprm_committing_creds, apparmor_bprm_committing_creds),
    LSM_HOOK_INIT(bprm_committed_creds, apparmor_bprm_committed_creds),
    LSM_HOOK_INIT(task_free, apparmor_task_free),
    LSM_HOOK_INIT(task_alloc, apparmor_task_alloc),
    LSM_HOOK_INIT(task_kill, apparmor_task_kill),
    LSM_HOOK_INIT(task_setrlimit, apparmor_task_setrlimit),

    // Credential 钩子
    LSM_HOOK_INIT(cred_alloc_blank, apparmor_cred_alloc_blank),
    LSM_HOOK_INIT(cred_free, apparmor_cred_free),
    LSM_HOOK_INIT(cred_prepare, apparmor_cred_prepare),
    LSM_HOOK_INIT(cred_transfer, apparmor_cred_transfer),

    // ... 更多钩子
};
```

### 6.2 安全 blob 布局

```c
// lsm.c (第1652-1657行)
struct lsm_blob_sizes apparmor_blob_sizes __ro_after_init = {
    .lbs_cred = sizeof(struct aa_label *),      // credentials 中的 label 指针
    .lbs_file = sizeof(struct aa_file_ctx),     // 文件安全上下文
    .lbs_task = sizeof(struct aa_task_ctx),     // 任务上下文
    .lbs_sock = sizeof(struct aa_sk_ctx),      // socket 上下文
};
```

### 6.3 AppArmor 初始化

**apparmor_init()** (lsm.c 第2507-2567行):

```c
static int __init apparmor_init(void)
{
    int error;

    // 1. 设置 DFA 引擎
    error = aa_setup_dfa_engine();
    if (error) {
        AA_ERROR("Unable to setup dfa engine\n");
        goto alloc_out;
    }

    // 2. 分配根命名空间
    error = aa_alloc_root_ns();
    if (error) {
        AA_ERROR("Unable to allocate default profile namespace\n");
        goto alloc_out;
    }

    // 3. 注册 sysctl
    error = apparmor_init_sysctl();

    // 4. 分配缓冲区
    error = alloc_buffers();

    // 5. 设置 init 任务的上下文
    error = set_init_ctx();

    // 6. 注册安全钩子
    security_add_hooks(apparmor_hooks, ARRAY_SIZE(apparmor_hooks),
                      &apparmor_lsmid);

    apparmor_initialized = 1;

    return error;
}

// 定义 LSM
DEFINE_LSM(apparmor) = {
    .id = &apparmor_lsmid,
    .flags = LSM_FLAG_LEGACY_MAJOR | LSM_FLAG_EXCLUSIVE,
    .enabled = &apparmor_enabled,
    .blobs = &apparmor_blob_sizes,
    .init = apparmor_init,
    // ...
};
```

---

## 7. 架构图

### 7.1 AppArmor 整体架构

```
+-------------------+     +-------------------+     +-------------------+
|   User Space      |     |   Kernel Space    |     |   Policy Store    |
|                   |     |                   |     |                   |
| +---------------+ |     | +---------------+ |     | +---------------+ |
| |   Application | |     | |   LSM Hooks   | |     | | /sys/kernel/  | |
| |   (Profile)   |----->| | (apparmor.c)  | |     | | security/     | |
| +---------------+ |     | +---------------+ |     | | apparmor/     | |
|                   |     |        |          |     | +---------------+ |
| +---------------+ |     |        v          |     |                   |
| |   aa-status   | |     | +---------------+ |     | +---------------+ |
| |   aa-complain | |     | |   Policy      | |     | |   Policy      | |
| |   aa-enforce  | |     | |   Engine     | |     | |   Binary      | |
| +---------------+ |     | | (policy.c)   | |     | |   (packed)    | |
|                   |     | +---------------+ |     | +---------------+ |
+-------------------+     |        |          |     +-------------------+
                         |        v          |
                         | +---------------+ |
                         | |   DFA Engine  | |
                         | |  (match.c)    | |
                         | +---------------+ |
                         |        |          |
                         |        v          |
                         | +---------------+ |
                         | |   Label       | |
                         | |   Management  | |
                         | |  (label.c)    | |
                         | +---------------+ |
                         +-------------------+
```

### 7.2 策略加载流程

```
User Space                  Kernel Space                    Data Structures
-----------                 ------------                    --------------

aa_load_policy()
     |
     |  ioctl(fd, POLICY_LOAD, policy_data)
     v
apparmor_update_policy()
     |
     +---> aa_may_manage_policy()
     |           |
     |           +---> capability check (CAP_MAC_ADMIN)
     |           +---> aa_policy_admin_capable()
     |
     +---> aa_unpack()
     |           |
     |           +---> 解析序列化的策略数据
     |           +---> 创建 aa_profile 结构
     |           +---> 创建 aa_ruleset 结构
     |
     +---> aa_replace_profiles()
                 |
                 +---> __lookup_replace()
                 |           |
                 |           +---> 查找已存在的 profile
                 |           +---> 检查是否可替换
                 |
                 +---> __add_profile() 或 __replace_profile()
                             |
                             +---> 更新 namespace 的 profile 列表
                             +---> 更新 label 树
                             +---> __aa_labelset_update_subtree()
```

### 7.3 文件访问控制流程

```
Application                AppArmor LSM                    File System
-----------                --------------                    ------------

open("/path/to/file", O_RDONLY)
     |
     v
apparmor_file_open()
     |
     +---> aa_path_perm()
     |           |
     |           +---> path_name()        // 解析路径
     |           +---> __aa_path_perm()
     |                       |
     |                       +---> aa_str_perms()
     |                       |           |
     |                       |           +---> aa_dfa_match()  // DFA 匹配
     |                       |           +---> aa_lookup_condperms()
     |                       |
     |                       +---> aa_audit_file()
     |                                   |
     |                                   +---> 记录审计日志
     |
     +---> update_file_ctx()  // 缓存权限
```

### 7.4 域转换流程 (exec)

```
Application                AppArmor Domain                  Target Profile
-----------                ----------------                  --------------

execve("/bin/ls", ...)
     |
     v
apparmor_bprm_creds_for_exec()
     |
     +---> profile_transition()
     |           |
     |           +---> aa_path_name()           // 获取可执行文件路径
     |           +---> aa_str_perms()           // 检查 MAY_EXEC
     |           +---> x_to_label()             // 确定目标 label
     |                       |
     |                       +---> find_attach()      // 查找附件 profile
     |                       +---> x_table_lookup()  // 查转换表
     |
     +---> may_change_ptraced_domain()   // 检查 ptrace 限制
     |
     +---> set_cred_label()             // 更新 bprm->cred
```

### 7.5 网络访问控制流程

```
Application                AppArmor Network                 Policy Match
-----------                ----------------                 -------------

socket(PF_INET, SOCK_STREAM, 0)
     |
     v
apparmor_socket_create()
     |
     +---> aa_af_perm()
     |           |
     |           +---> aa_profile_af_perm()
     |                       |
     |                       +---> RULE_MEDIATES_NET()    // 获取起始状态
     |                       +---> aa_match_to_prot()
     |                                   |
     |                                   +---> aa_dfa_match_be16(af)    // 匹配地址族
     |                                   +---> aa_dfa_match_be16(type)  // 匹配类型
     |                                   +---> aa_dfa_match_be16(proto)// 匹配协议
     |
     +---> aa_do_perms()
                 |
                 +---> aa_check_perms()
```

---

## 附录 A: 关键文件索引

| 文件 | 功能 |
|------|------|
| `/security/apparmor/lsm.c` | LSM 钩子注册和主入口 |
| `/security/apparmor/policy.c` | 策略加载和管理 |
| `/security/apparmor/domain.c` | 域转换和 exec 钩子 |
| `/security/apparmor/main.c` | 文件权限检查 |
| `/security/apparmor/task.c` | 任务上下文管理 |
| `/security/apparmor/net.c` | 网络权限检查 |
| `/security/apparmor/include/policy.h` | 策略数据结构 |
| `/security/apparmor/include/label.h` | 标签数据结构 |
| `/security/apparmor/include/file.h` | 文件权限数据结构 |
| `/security/apparmor/include/task.h` | 任务上下文结构 |
| `/security/apparmor/include/apparmor.h` | 类别定义和常量 |

## 附录 B: 权限标志

```c
// 文件权限 (file.h)
#define AA_MAY_CREATE    0x0010   // 创建
#define AA_MAY_DELETE    0x0020   // 删除
#define AA_MAY_GETATTR   0x0100   // 获取属性
#define AA_MAY_SETATTR   0x0200   // 设置属性
#define AA_MAY_CHMOD      0x0400   // 修改权限
#define AA_MAY_CHOWN      0x0800   // 修改所有者
#define AA_MAY_LOCK       0x1000   // 文件锁
#define AA_EXEC_MMAP      0x2000   // mmap 执行
#define AA_MAY_LINK       0x4000   // 硬链接

// 网络权限
#define AA_MAY_SEND       0x0002   // 发送
#define AA_MAY_RECEIVE    0x0004   // 接收
#define AA_MAY_CREATE     0x0010   // 创建套接字
#define AA_MAY_SHUTDOWN   0x0020   // 关闭
#define AA_MAY_CONNECT    0x0040   // 连接
#define AA_MAY_BIND       0x0400   // 绑定地址
#define AA_MAY_LISTEN     0x0800   // 监听
#define AA_MAY_ACCEPT     0x1000   // 接受连接
```

---

*文档生成时间: 2026-04-26*
*分析基于 Linux 内核源码*
