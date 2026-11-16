# Linux Security 子系统深度分析 R2

## 目录
1. [avc_hash 与 AVC 缓存结构](#1-avc_hash-与-avc-缓存结构)
2. [security_context_to_sid 与 SID 表](#2-security_context_to_sid-与-sid-表)
3. [security_compute_av 权限计算](#3-security_compute_av-权限计算)
4. [selinux_inode_permission 权限检查](#4-selinux_inode_permission-权限检查)
5. [avc_insert AVC 条目插入](#5-avc_insert-avc-条目插入)
6. [selinux_bprm_set_creds 凭证安全上下文转换](#6-selinux_bprm_set_creds-凭证安全上下文转换)
7. [知识点关联表格](#7-知识点关联表格)

---

## 1. avc_hash 与 AVC 缓存结构

### 1.1 AVC 缓存数据结构

AVC（Access Vector Cache）是 SELinux 的核心缓存机制，用于缓存访问决策结果，避免每次权限检查都查询策略数据库。

**核心数据结构** (`security/selinux/avc.c`):

```c
// avc_entry: 单个 AVC 条目
struct avc_entry {
    u32            ssid;       // 源安全标识符
    u32            tsid;       // 目标安全标识符
    u16            tclass;     // 目标安全类
    struct av_decision avd;     // 访问向量决策
    struct avc_xperms_node *xp_node;  // 扩展权限节点
};

// avc_node: AVC 缓存节点，包含 RCU 头
struct avc_node {
    struct avc_entry ae;
    struct hlist_node list;     // 链入 avc_cache->slots[i]
    struct rcu_head  rhead;    // RCU 延迟释放
};

// avc_cache: AVC 缓存主体
struct avc_cache {
    struct hlist_head slots[AVC_CACHE_SLOTS];  // hash 槽数组
    spinlock_t slots_lock[AVC_CACHE_SLOTS];     // 每个槽的锁
    atomic_t lru_hint;        // LRU 回收扫描提示
    atomic_t active_nodes;     // 活跃节点计数
    u32 latest_notif;         // 最新撤销通知序列号
};
```

**哈希表配置** (`security/selinux/avc.c:38-40`):
```c
#define AVC_CACHE_SLOTS     (1 << CONFIG_SECURITY_SELINUX_AVC_HASH_BITS)
#define AVC_DEF_CACHE_THRESHOLD AVC_CACHE_SLOTS
#define AVC_CACHE_RECLAIM   16
```

### 1.2 avc_hash 函数

**哈希函数实现** (`security/selinux/avc.c:126-129`):
```c
static inline u32 avc_hash(u32 ssid, u32 tsid, u16 tclass)
{
    return av_hash(ssid, tsid, (u32)tclass, (u32)(AVC_CACHE_SLOTS - 1));
}
```

哈希算法由 `av_hash()` 实现，将 (ssid, tsid, tclass) 三元组映射到 `[0, AVC_CACHE_SLOTS-1]` 范围内的槽索引。

**av_hash 实际位于** `security/selinux/hash.h`，采用混合哈希算法：
```c
static inline u32 av_hash(u32 ssid, u32 tsid, u32 tclass, u32 mask)
{
    u32 hash = (ssid ^ (tsid << 3) ^ (tsid >> 5) ^ (tclass << 5)) & mask;
    return hash;
}
```

### 1.3 Cache Lookup 流程

**avc_lookup 函数** (`security/selinux/avc.c:553-565`):
```c
static struct avc_node *avc_lookup(u32 ssid, u32 tsid, u16 tclass)
{
    struct avc_node *node;

    avc_cache_stats_incr(lookups);
    node = avc_search_node(ssid, tsid, tclass);  // 执行实际搜索

    if (node)
        return node;

    avc_cache_stats_incr(misses);  // 缓存未命中统计
    return NULL;
}
```

**avc_search_node 实现** (`security/selinux/avc.c:521-539`):
```c
static inline struct avc_node *avc_search_node(u32 ssid, u32 tsid, u16 tclass)
{
    struct avc_node *node, *ret = NULL;
    u32 hvalue;
    struct hlist_head *head;

    hvalue = avc_hash(ssid, tsid, tclass);  // 计算哈希值
    head = &selinux_avc.avc_cache.slots[hvalue];  // 获取槽头
    
    hlist_for_each_entry_rcu(node, head, list) {
        // 精确匹配 ssid, tclass, tsid
        if (ssid == node->ae.ssid &&
            tclass == node->ae.tclass &&
            tsid == node->ae.tsid) {
            ret = node;
            break;
        }
    }
    return ret;
}
```

**Cache Lookup 完整流程图**:
```
avc_has_perm_noaudit(ssid, tsid, tclass, requested)
    │
    ├── rcu_read_lock()           // 获取读锁
    │
    ├── node = avc_lookup()       // 缓存查找
    │       │
    │       ├── hvalue = avc_hash(ssid, tsid, tclass)
    │       ├── head = slots[hvalue]
    │       └── hlist_for_each_entry_rcu() 遍历链表
    │
    ├── if (node found)
    │       └── denied = requested & ~node->ae.avd.allowed
    │
    └── rcu_read_unlock()
```

---

## 2. security_context_to_sid 与 SID 表

### 2.1 SID 表核心结构

**sidtab 结构** (`security/selinux/ss/sidtab.h:77-105`):
```c
struct sidtab {
    // 无锁读取，仅通过 count 原子访问保证
    union sidtab_entry_inner roots[SIDTAB_MAX_LEVEL + 1];  // 树形结构根节点
    u32 count;                    // 条目计数，原子访问
    
    // 转换参数，策略加载时使用
    struct sidtab_convert_params *convert;
    bool frozen;                 // 冻结标志
    spinlock_t lock;             // 写操作锁

    // SID -> 字符串缓存 (可选)
#if CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE > 0
    u32 cache_free_slots;
    struct list_head cache_lru_list;
    spinlock_t cache_lock;
#endif

    // 初始 SID 表 (kernel, init 等)
    struct sidtab_isid_entry isids[SECINITSID_NUM];

    // 快速反向查找: context -> sid
    DECLARE_HASHTABLE(context_to_sid, SIDTAB_HASH_BITS);
};
```

**sidtab_entry 结构** (`security/selinux/ss/sidtab.h:21-29`):
```c
struct sidtab_entry {
    u32 sid;                     // 安全标识符
    u32 hash;                    // 上下文哈希值
    struct context context;      // 安全上下文结构
#if CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE > 0
    struct sidtab_str_cache __rcu *cache;  // 字符串缓存
#endif
    struct hlist_node list;      // 链入 context_to_sid 哈希表
};
```

**context 结构** (`security/selinux/ss/context.h:28-35`):
```c
struct context {
    u32 user;                    // 安全用户
    u32 role;                    // 角色
    u32 type;                   // 类型 (核心字段)
    u32 len;                    // 字符串表示长度
    struct mls_range range;      // MLS 范围
    char *str;                   // 字符串表示 (无法映射时)
};
```

### 2.2 context_to_sid_core 函数

**security_context_to_sid_core** (`security/selinux/ss/services.c:1552-1625`):

```c
static int security_context_to_sid_core(const char *scontext, u32 scontext_len,
                    u32 *sid, u32 def_sid, gfp_t gfp_flags, int force)
{
    struct selinux_policy *policy;
    struct policydb *policydb;
    struct sidtab *sidtab;
    char *scontext2, *str = NULL;
    struct context context;
    int rc = 0;

    // 1. 空上下文检查
    if (!scontext_len)
        return -EINVAL;

    // 2. 复制字符串以允许修改并确保 NUL 终止
    scontext2 = kmemdup_nul(scontext, scontext_len, gfp_flags);
    if (!scontext2)
        return -ENOMEM;

    // 3. 策略未初始化时，返回初始 SID
    if (!selinux_initialized()) {
        u32 i;
        for (i = 1; i < SECINITSID_NUM; i++) {
            const char *s = initial_sid_to_string[i];
            if (s && !strcmp(s, scontext2)) {
                *sid = i;
                goto out;
            }
        }
        *sid = SECINITSID_KERNEL;
        goto out;
    }

    // 4. 强制模式：保存字符串副本
    if (force) {
        str = kstrdup(scontext2, gfp_flags);
        if (!str)
            goto out;
    }

retry:
    // 5. RCU 保护读取策略
    rcu_read_lock();
    policy = rcu_dereference(selinux_state.policy);
    policydb = &policy->policydb;
    sidtab = policy->sidtab;

    // 6. 字符串到上下文结构转换
    rc = string_to_context_struct(policydb, sidtab, scontext2,
                  &context, def_sid);
    if (rc == -EINVAL && force) {
        // 强制模式下保存未解析字符串
        context.str = str;
        context.len = strlen(str) + 1;
        str = NULL;
    } else if (rc)
        goto out_unlock;

    // 7. 上下文到 SID 转换 (核心查找)
    rc = sidtab_context_to_sid(sidtab, &context, sid);
    if (rc == -ESTALE) {
        // 策略已更改，需要重试
        rcu_read_unlock();
        context_destroy(&context);
        goto retry;
    }
    context_destroy(&context);

out_unlock:
    rcu_read_unlock();
out:
    kfree(scontext2);
    kfree(str);
    return rc;
}
```

**sidtab_context_to_sid** (`security/selinux/ss/sidtab.c:268-361`):
```c
int sidtab_context_to_sid(struct sidtab *s, struct context *context, u32 *sid)
{
    unsigned long flags;
    u32 count, hash = context_compute_hash(context);
    struct sidtab_convert_params *convert;
    struct sidtab_entry *dst, *dst_convert;
    int rc;

    // 1. 锁-free 查找
    *sid = context_to_sid(s, context, hash);
    if (*sid)
        return 0;

    // 2. 获取锁，锁定后重新查找
    spin_lock_irqsave(&s->lock, flags);

    *sid = context_to_sid(s, context, hash);
    if (*sid)
        goto out_unlock;

    // 3. 检查是否冻结 (策略切换期间)
    if (unlikely(s->frozen)) {
        rc = -ESTALE;
        goto out_unlock;
    }

    count = s->count;

    // 4. 溢出检查
    rc = -EOVERFLOW;
    if (count >= SIDTAB_MAX)
        goto out_unlock;

    // 5. 分配新条目
    rc = -ENOMEM;
    dst = sidtab_do_lookup(s, count, 1);
    if (!dst)
        goto out_unlock;

    // 6. 设置新 SID
    dst->sid = index_to_sid(count);
    dst->hash = hash;
    context_cpy(&dst->context, context);

    // 7. 策略转换 (如果正在转换)
    convert = s->convert;
    if (convert) {
        dst_convert = sidtab_do_lookup(target, count, 1);
        // ... 转换逻辑
    }

    // 8. 发布新条目
    *sid = index_to_sid(count);
    smp_store_release(&s->count, count + 1);
    hash_add_rcu(s->context_to_sid, &dst->list, dst->hash);

    rc = 0;
out_unlock:
    spin_unlock_irqrestore(&s->lock, flags);
    return rc;
}
```

---

## 3. security_compute_av 权限计算

### 3.1 avc_has_perm_noaudit 函数

**avc_has_perm_noaudit** (`security/selinux/avc.c:1145-1171`) - 不审核权限检查:

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
    
    // 1. 尝试从 AVC 缓存获取
    node = avc_lookup(ssid, tsid, tclass);
    if (unlikely(!node)) {
        // 2. 缓存未命中，调用慢路径
        rcu_read_unlock();
        return avc_perm_nonode(ssid, tsid, tclass, requested,
                       flags, avd);
    }
    
    // 3. 缓存命中，计算拒绝权限
    denied = requested & ~node->ae.avd.allowed;
    memcpy(avd, &node->ae.avd, sizeof(*avd));
    rcu_read_unlock();

    // 4. 如果有拒绝权限，处理之
    if (unlikely(denied))
        return avc_denied(ssid, tsid, tclass, requested, 0, 0, 0,
                  flags, avd);
    return 0;
}
```

### 3.2 avc_compute_av 函数

**avc_compute_av** (`security/selinux/avc.c:987-994`) - AVC 计算入口:

```c
static noinline void avc_compute_av(u32 ssid, u32 tsid, u16 tclass,
                   struct av_decision *avd,
                   struct avc_xperms_node *xp_node)
{
    INIT_LIST_HEAD(&xp_node->xpd_head);
    // 调用安全服务器计算访问向量
    security_compute_av(ssid, tsid, tclass, avd, &xp_node->xp);
    // 将结果插入缓存
    avc_insert(ssid, tsid, tclass, avd, xp_node);
}
```

### 3.3 security_compute_av 函数

**security_compute_av** (`security/selinux/ss/services.c:1123-1189`) - 核心权限计算:

```c
void security_compute_av(u32 ssid,
             u32 tsid,
             u16 orig_tclass,
             struct av_decision *avd,
             struct extended_perms *xperms)
{
    struct selinux_policy *policy;
    struct policydb *policydb;
    struct sidtab *sidtab;
    u16 tclass;
    struct context *scontext = NULL, *tcontext = NULL;

    rcu_read_lock();
    policy = rcu_dereference(selinux_state.policy);
    avd_init(policy, avd);
    xperms->len = 0;
    
    // 策略未初始化：允许所有
    if (!selinux_initialized())
        goto allow;

    policydb = &policy->policydb;
    sidtab = policy->sidtab;

    // 1. 查找源上下文
    scontext = sidtab_search(sidtab, ssid);
    if (!scontext) {
        pr_err("SELinux: %s: unrecognized SID %d\n", __func__, ssid);
        goto out;
    }

    // 2. 检查 permissive 域
    if (ebitmap_get_bit(&policydb->permissive_map, scontext->type))
        avd->flags |= AVD_FLAGS_PERMISSIVE;

    // 3. 检查 neveraudit 域
    if (ebitmap_get_bit(&policydb->neveraudit_map, scontext->type))
        avd->flags |= AVD_FLAGS_NEVERAUDIT;

    // 4. 查找目标上下文
    tcontext = sidtab_search(sidtab, tsid);
    if (!tcontext) {
        pr_err("SELinux: %s: unrecognized SID %d\n", __func__, tsid);
        goto out;
    }

    // 5. 类映射转换
    tclass = unmap_class(&policy->map, orig_tclass);
    if (unlikely(orig_tclass && !tclass)) {
        if (policydb->allow_unknown)
            goto allow;
        goto out;
    }

    // 6. 核心计算: 使用 TE 规则计算访问向量
    context_struct_compute_av(policydb, scontext, tcontext, tclass, avd, xperms);
    
    // 7. 类映射回填
    map_decision(&policy->map, orig_tclass, avd, policydb->allow_unknown);

out:
    rcu_read_unlock();
    if (avd->flags & AVD_FLAGS_NEVERAUDIT)
        avd->auditallow = avd->auditdeny = 0;
    return;

allow:
    avd->allowed = 0xffffffff;  // 允许所有
    goto out;
}
```

### 3.4 security_compute_sid 函数

**security_compute_sid** (`security/selinux/ss/services.c:1753-1949`) - SID 计算 (用于类型转换):

```c
static int security_compute_sid(u32 ssid,
                u32 tsid,
                u16 orig_tclass,
                u16 specified,      // AVTAB_TRANSITION/CHANGE/MEMBER
                const char *objname,
                u32 *out_sid,
                bool kern)
{
    // ... 变量初始化 ...

    if (!selinux_initialized()) {
        switch (orig_tclass) {
        case SECCLASS_PROCESS:
            *out_sid = ssid;
            break;
        default:
            *out_sid = tsid;
            break;
        }
        goto out;
    }

retry:
    context_init(&newcontext);

    rcu_read_lock();
    policy = rcu_dereference(selinux_state.policy);
    
    // 类映射处理
    if (kern) {
        tclass = unmap_class(&policy->map, orig_tclass);
        sock = security_is_socket_class(orig_tclass);
    } else {
        tclass = orig_tclass;
        sock = security_is_socket_class(map_class(&policy->map, tclass));
    }

    policydb = &policy->policydb;
    sidtab = policy->sidtab;

    // 1. 查找源和目标 SID 条目
    sentry = sidtab_search_entry(sidtab, ssid);
    tentry = sidtab_search_entry(sidtab, tsid);
    
    scontext = &sentry->context;
    tcontext = &tentry->context;

    // 2. 设置用户身份
    switch (specified) {
    case AVTAB_TRANSITION:
    case AVTAB_CHANGE:
        if (cladatum && cladatum->default_user == DEFAULT_TARGET)
            newcontext.user = tcontext->user;
        else
            newcontext.user = scontext->user;
        break;
    case AVTAB_MEMBER:
        newcontext.user = tcontext->user;
        break;
    }

    // 3. 设置角色
    if (cladatum && cladatum->default_role == DEFAULT_SOURCE)
        newcontext.role = scontext->role;
    else if (cladatum && cladatum->default_role == DEFAULT_TARGET)
        newcontext.role = tcontext->role;
    else {
        if ((tclass == policydb->process_class) || sock)
            newcontext.role = scontext->role;
        else
            newcontext.role = OBJECT_R_VAL;
    }

    // 4. 设置类型 (查找类型转换规则)
    avkey.source_type = scontext->type;
    avkey.target_type = tcontext->type;
    avkey.target_class = tclass;
    avkey.specified = specified;
    avnode = avtab_search_node(&policydb->te_avtab, &avkey);

    // 查找条件规则
    if (!avnode) {
        node = avtab_search_node(&policydb->te_cond_avtab, &avkey);
        for (; node; node = avtab_search_node_next(node, specified)) {
            if (node->key.specified & AVTAB_ENABLED) {
                avnode = node;
                break;
            }
        }
    }

    // 应用规则或默认值
    if (avnode)
        newcontext.type = avnode->datum.u.data;
    else if (cladatum && cladatum->default_type == DEFAULT_SOURCE)
        newcontext.type = scontext->type;
    else if (cladatum && cladatum->default_type == DEFAULT_TARGET)
        newcontext.type = tcontext->type;
    else {
        if ((tclass == policydb->process_class) || sock)
            newcontext.type = scontext->type;
        else
            newcontext.type = tcontext->type;
    }

    // 5. MLS 属性计算
    rc = mls_compute_sid(policydb, scontext, tcontext, tclass, specified,
                 &newcontext, sock);
    if (rc)
        goto out_unlock;

    // 6. 验证上下文有效性
    if (!policydb_context_isvalid(policydb, &newcontext)) {
        rc = compute_sid_handle_invalid_context(...);
        if (rc)
            goto out_unlock;
    }

    // 7. 获取新 SID
    if (context_equal(scontext, &newcontext))
        *out_sid = ssid;
    else if (context_equal(tcontext, &newcontext))
        *out_sid = tsid;
    else
        rc = sidtab_context_to_sid(sidtab, &newcontext, out_sid);

    // ... 错误处理和清理 ...
}
```

---

## 4. selinux_inode_permission 权限检查

### 4.1 selinux_inode_permission 函数

**selinux_inode_permission** (`security/selinux/hooks.c:3222-3276`):

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

    // 1. 提取权限掩码
    mask = requested & (MAY_READ|MAY_WRITE|MAY_EXEC|MAY_APPEND);

    // 2. 无权限检查 = 存在性测试
    if (!mask)
        return 0;

    tsec = selinux_task(current);
    
    // 3. 检查任务 AVC 缓存 (快速路径)
    if (task_avdcache_permnoaudit(tsec, sid))
        return 0;

    // 4. 获取 inode 安全结构
    isec = inode_security_rcu(inode, requested & MAY_NOT_BLOCK);
    if (IS_ERR(isec))
        return PTR_ERR(isec);
    
    // 5. 将文件模式转换为权限位
    perms = file_mask_to_av(inode->i_mode, mask);

    // 6. 搜索任务 AVC 缓存
    rc = task_avdcache_search(tsec, isec, &avdc);
    if (likely(!rc)) {
        // 缓存命中
        audited = perms & avdc->audited;
        denied = perms & ~avdc->allowed;
        if (unlikely(denied && enforcing_enabled() && !avdc->permissive))
            rc = -EACCES;
    } else {
        // 缓存未命中，调用 AVC
        struct av_decision avd;
        rc = avc_has_perm_noaudit(sid, isec->sid, isec->sclass,
                      perms, 0, &avd);
        audited = avc_audit_required(perms, &avd, rc,
            (requested & MAY_ACCESS) ? FILE__AUDIT_ACCESS : 0,
            &denied);
        task_avdcache_update(tsec, isec, &avd, audited);
    }

    // 7. 审计
    if (likely(!audited))
        return rc;

    rc2 = audit_inode_permission(inode, perms, audited, denied, rc);
    if (rc2)
        return rc2;

    return rc;
}
```

### 4.2 inode_has_perm 函数

**inode_has_perm** (`security/selinux/hooks.c:1677-1692`):

```c
static int inode_has_perm(const struct cred *cred,
              struct inode *inode,
              u32 perms,
              struct common_audit_data *adp)
{
    struct inode_security_struct *isec;
    u32 sid;

    if (unlikely(IS_PRIVATE(inode)))
        return 0;

    sid = cred_sid(cred);
    isec = selinux_inode(inode);

    return avc_has_perm(sid, isec->sid, isec->sclass, perms, adp);
}
```

### 4.3 file_has_perm 函数

**file_has_perm** (`security/selinux/hooks.c:1756-1791`):

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

    // 1. 检查文件描述符 SID 与进程 SID
    if (sid != fsec->sid) {
        rc = avc_has_perm(sid, fsec->sid,
                  SECCLASS_FD,
                  FD__USE,
                  &ad);
        if (rc)
            goto out;
    }

#ifdef CONFIG_BPF_SYSCALL
    rc = bpf_fd_pass(file, cred_sid(cred));
    if (rc)
        return rc;
#endif

    // 2. 如果 av 非零，检查 inode 权限
    rc = 0;
    if (av)
        rc = inode_has_perm(cred, inode, av, &ad);

out:
    return rc;
}
```

### 4.4 avc_lookup 调用链

**avc_has_perm** (`security/selinux/avc.c:1189-1203`):

```c
int avc_has_perm(u32 ssid, u32 tsid, u16 tclass,
         u32 requested, struct common_audit_data *auditdata)
{
    struct av_decision avd;
    int rc, rc2;

    // 1. 不审核权限检查
    rc = avc_has_perm_noaudit(ssid, tsid, tclass, requested, 0, &avd);

    // 2. 审核检查
    rc2 = avc_audit(ssid, tsid, tclass, requested, &avd, rc, auditdata);
    if (rc2)
        return rc2;
    return rc;
}
```

---

## 5. avc_insert AVC 条目插入

### 5.1 avc_insert 函数

**avc_insert** (`security/selinux/avc.c:606-643`):

```c
static void avc_insert(u32 ssid, u32 tsid, u16 tclass,
           struct av_decision *avd, struct avc_xperms_node *xp_node)
{
    struct avc_node *pos, *node = NULL;
    u32 hvalue;
    unsigned long flag;
    spinlock_t *lock;
    struct hlist_head *head;

    // 1. 检查序列号是否过期
    if (avc_latest_notif_update(avd->seqno, 1))
        return;

    // 2. 分配新节点
    node = avc_alloc_node();
    if (!node)
        return;

    // 3. 填充节点数据
    avc_node_populate(node, ssid, tsid, tclass, avd);
    if (avc_xperms_populate(node, xp_node)) {
        avc_node_kill(node);
        return;
    }

    // 4. 计算哈希值并获取锁
    hvalue = avc_hash(ssid, tsid, tclass);
    head = &selinux_avc.avc_cache.slots[hvalue];
    lock = &selinux_avc.avc_cache.slots_lock[hvalue];
    spin_lock_irqsave(lock, flag);
    
    // 5. 查找并替换现有条目
    hlist_for_each_entry(pos, head, list) {
        if (pos->ae.ssid == ssid &&
            pos->ae.tsid == tsid &&
            pos->ae.tclass == tclass) {
            avc_node_replace(node, pos);
            goto found;
        }
    }
    
    // 6. 添加新节点到链表头
    hlist_add_head_rcu(&node->list, head);
    
found:
    spin_unlock_irqrestore(lock, flag);
}
```

### 5.2 avc_node 分配

**avc_alloc_node** (`security/selinux/avc.c:494-511`):

```c
static struct avc_node *avc_alloc_node(void)
{
    struct avc_node *node;

    // 1. 从 slab 缓存分配
    node = kmem_cache_zalloc(avc_node_cachep, GFP_NOWAIT);
    if (!node)
        goto out;

    INIT_HLIST_NODE(&node->list);
    avc_cache_stats_incr(allocations);

    // 2. 检查是否超过阈值，需要回收
    if (atomic_inc_return(&selinux_avc.avc_cache.active_nodes) >
        selinux_avc.avc_cache_threshold)
        avc_reclaim_node();

out:
    return node;
}
```

### 5.3 avc_node_populate 函数

**avc_node_populate** (`security/selinux/avc.c:513-519`):

```c
static void avc_node_populate(struct avc_node *node, u32 ssid, u32 tsid, 
                 u16 tclass, struct av_decision *avd)
{
    node->ae.ssid = ssid;
    node->ae.tsid = tsid;
    node->ae.tclass = tclass;
    memcpy(&node->ae.avd, avd, sizeof(node->ae.avd));
}
```

### 5.4 avc_node 回收机制

**avc_reclaim_node** (`security/selinux/avc.c:459-492`):

```c
static inline int avc_reclaim_node(void)
{
    struct avc_node *node;
    int hvalue, try, ecx;
    unsigned long flags;
    struct hlist_head *head;
    spinlock_t *lock;

    // 循环尝试回收节点
    for (try = 0, ecx = 0; try < AVC_CACHE_SLOTS; try++) {
        // LRU 提示：选择下一个槽
        hvalue = atomic_inc_return(&selinux_avc.avc_cache.lru_hint) &
            (AVC_CACHE_SLOTS - 1);
        head = &selinux_avc.avc_cache.slots[hvalue];
        lock = &selinux_avc.avc_cache.slots_lock[hvalue];

        if (!spin_trylock_irqsave(lock, flags))
            continue;

        rcu_read_lock();
        hlist_for_each_entry(node, head, list) {
            avc_node_delete(node);  // RCU 删除
            avc_cache_stats_incr(reclaims);
            ecx++;
            if (ecx >= AVC_CACHE_RECLAIM) {  // 每次回收 16 个
                rcu_read_unlock();
                spin_unlock_irqrestore(lock, flags);
                goto out;
            }
        }
        rcu_read_unlock();
        spin_unlock_irqrestore(lock, flags);
    }
out:
    return ecx;
}
```

### 5.5 avc_node_delete 与 RCU 释放

**avc_node_delete** (`security/selinux/avc.c:437-442`):

```c
static void avc_node_delete(struct avc_node *node)
{
    hlist_del_rcu(&node->list);
    call_rcu(&node->rhead, avc_node_free);  // RCU 延迟释放
    atomic_dec(&selinux_avc.avc_cache.active_nodes);
}
```

**avc_node_free** (`security/selinux/avc.c:429-435`):

```c
static void avc_node_free(struct rcu_head *rhead)
{
    struct avc_node *node = container_of(rhead, struct avc_node, rhead);
    avc_xperms_free(node->ae.xp_node);
    kmem_cache_free(avc_node_cachep, node);
    avc_cache_stats_incr(frees);
}
```

---

## 6. selinux_bprm_set_creds 凭证安全上下文转换

### 6.1 selinux_bprm_creds_for_exec 函数

**selinux_bprm_creds_for_exec** (`security/selinux/hooks.c:2312-2435`):

```c
static int selinux_bprm_creds_for_exec(struct linux_binprm *bprm)
{
    const struct cred_security_struct *old_crsec;
    struct cred_security_struct *new_crsec;
    struct inode_security_struct *isec;
    struct common_audit_data ad;
    struct inode *inode = file_inode(bprm->file);
    int rc;

    // 1. 获取新旧凭证安全结构
    old_crsec = selinux_cred(current_cred());
    new_crsec = selinux_cred(bprm->cred);
    isec = inode_security(inode);

    // 2. 类型检查
    if (WARN_ON(isec->sclass != SECCLASS_FILE &&
        isec->sclass != SECCLASS_MEMFD_FILE))
        return -EACCES;

    // 3. 默认继承旧 SID
    new_crsec->sid = old_crsec->sid;
    new_crsec->osid = old_crsec->sid;

    // 4. 重置 exec/key/sock 创建 SID
    new_crsec->create_sid = 0;
    new_crsec->keycreate_sid = 0;
    new_crsec->sockcreate_sid = 0;

    // 5. 策略未初始化时的特殊处理
    if (!selinux_initialized()) {
        new_crsec->sid = SECINITSID_INIT;
        new_crsec->exec_sid = 0;
        return 0;
    }

    // 6. 如果存在 exec_sid，使用它
    if (old_crsec->exec_sid) {
        new_crsec->sid = old_crsec->exec_sid;
        new_crsec->exec_sid = 0;

        // 检查 NNP/NOSUID 限制
        rc = check_nnp_nosuid(bprm, old_crsec, new_crsec);
        if (rc)
            return rc;
    } else {
        // 7. 否则查找默认转换
        rc = security_transition_sid(old_crsec->sid,
                         isec->sid, SECCLASS_PROCESS, NULL,
                         &new_crsec->sid);
        if (rc)
            return rc;

        // 8. NNP/NOSUID 检查
        rc = check_nnp_nosuid(bprm, old_crsec, new_crsec);
        if (rc)
            new_crsec->sid = old_crsec->sid;  // 回退到旧 SID
    }

    // 9. 权限检查
    ad.type = LSM_AUDIT_DATA_FILE;
    ad.u.file = bprm->file;

    if (new_crsec->sid == old_crsec->sid) {
        // 同 SID：检查无转换执行权限
        rc = avc_has_perm(old_crsec->sid, isec->sid, isec->sclass,
                  FILE__EXECUTE_NO_TRANS, &ad);
        if (rc)
            return rc;
    } else {
        // 跨 SID：检查转换和入口点权限
        rc = avc_has_perm(old_crsec->sid, new_crsec->sid,
                  SECCLASS_PROCESS, PROCESS__TRANSITION, &ad);
        if (rc)
            return rc;

        rc = avc_has_perm(new_crsec->sid, isec->sid, isec->sclass,
                  FILE__ENTRYPOINT, &ad);
        if (rc)
            return rc;

        // 共享状态检查
        if (bprm->unsafe & LSM_UNSAFE_SHARE) {
            rc = avc_has_perm(old_crsec->sid, new_crsec->sid,
                      SECCLASS_PROCESS, PROCESS__SHARE, NULL);
            if (rc)
                return -EPERM;
        }

        // Ptrace 检查
        if (bprm->unsafe & LSM_UNSAFE_PTRACE) {
            u32 ptsid = ptrace_parent_sid();
            if (ptsid != 0) {
                rc = avc_has_perm(ptsid, new_crsec->sid,
                          SECCLASS_PROCESS, PROCESS__PTRACE, NULL);
                if (rc)
                    return -EPERM;
            }
        }

        // 清除不安全的人格位
        bprm->per_clear |= PER_CLEAR_ON_SETID;

        // 10. 设置安全执行标志
        rc = avc_has_perm(old_crsec->sid, new_crsec->sid,
                  SECCLASS_PROCESS, PROCESS__NOATSECURE, NULL);
        bprm->secureexec |= !!rc;
    }

    return 0;
}
```

### 6.2 cred_security_struct 结构

**cred_security_struct** (`security/selinux/include/objsec.h:40-47`):

```c
struct cred_security_struct {
    u32 osid;        // 上次 execve 前的 SID
    u32 sid;         // 当前 SID
    u32 exec_sid;    // exec SID (用于指定执行时转换)
    u32 create_sid;   // fscreate SID (用于创建文件时)
    u32 keycreate_sid;  // keycreate SID
    u32 sockcreate_sid; // sockcreate SID
} __randomize_layout;
```

### 6.3 selinux_cred 辅助函数

**selinux_cred** (`security/selinux/include/objsec.h:182-185`):

```c
static inline struct cred_security_struct *selinux_cred(const struct cred *cred)
{
    return cred->security + selinux_blob_sizes.lbs_cred;
}
```

### 6.4 check_nnp_nosuid 函数

**check_nnp_nosuid** (`security/selinux/hooks.c:2259-2310`):

```c
static int check_nnp_nosuid(const struct linux_binprm *bprm,
                const struct cred_security_struct *old_crsec,
                const struct cred_security_struct *new_crsec)
{
    int nnp = (bprm->unsafe & LSM_UNSAFE_NO_NEW_PRIVS);
    int nosuid = !mnt_may_suid(bprm->file->f_path.mnt);
    int rc;
    u32 av;

    // 1. 如果既不是 NNP 也不是 nosuid，直接返回
    if (!nnp && !nosuid)
        return 0;

    // 2. SID 未变更，直接返回
    if (new_crsec->sid == old_crsec->sid)
        return 0;

    // 3. 策略支持 nnp_nosuid_transition 能力
    if (selinux_policycap_nnp_nosuid_transition()) {
        av = 0;
        if (nnp)
            av |= PROCESS2__NNP_TRANSITION;
        if (nosuid)
            av |= PROCESS2__NOSUID_TRANSITION;
        rc = avc_has_perm(old_crsec->sid, new_crsec->sid,
                  SECCLASS_PROCESS2, av, NULL);
        if (!rc)
            return 0;
    }

    // 4. 检查有界转换
    rc = security_bounded_transition(old_crsec->sid, new_crsec->sid);
    if (!rc)
        return 0;

    // 5. 失败：返回错误
    if (nnp)
        return -EPERM;
    return -EACCES;
}
```

### 6.5 安全上下文转换流程图

```
execve() 系统调用
    │
    ├── selinux_bprm_creds_for_exec()
    │       │
    │       ├── 获取 old_crsec = selinux_cred(current_cred())
    │       ├── 获取 new_crsec = selinux_cred(bprm->cred)
    │       ├── inode = file_inode(bprm->file)
    │       │
    │       ├── 默认: new_crsec->sid = old_crsec->sid
    │       │
    │       ├── 检查 old_crsec->exec_sid
    │       │       │
    │       │       ├── 有 exec_sid: new_crsec->sid = exec_sid
    │       │       └── 无 exec_sid: security_transition_sid() 计算
    │       │
    │       ├── check_nnp_nosuid() 验证
    │       │
    │       └── 权限检查:
    │               ├── 同 SID: FILE__EXECUTE_NO_TRANS
    │               └── 跨 SID: PROCESS__TRANSITION + FILE__ENTRYPOINT
    │
    ├── selinux_bprm_committing_creds()
    │       │
    │       ├── flush_unauthorized_files()
    │       └── 检查 PROCESS__RLIMITINH
    │
    └── selinux_bprm_committed_creds()
            │
            └── 检查 PROCESS__SIGINH
```

---

## 7. 知识点关联表格

### 7.1 核心数据结构关联

| 数据结构 | 文件位置 | 用途描述 |
|---------|---------|---------|
| `avc_entry` | avc.c:48-54 | 单个 AVC 条目，存储 (ssid, tsid, tclass) -> av_decision |
| `avc_node` | avc.c:56-60 | AVC 缓存节点，含 RCU 头用于延迟释放 |
| `avc_cache` | avc.c:72-78 | AVC 缓存主体，含哈希槽数组和锁 |
| `context` | context.h:28-35 | 安全上下文 (user, role, type, MLS range) |
| `sidtab` | sidtab.h:77-105 | SID 表，存储 SID -> context 映射 |
| `sidtab_entry` | sidtab.h:21-29 | SID 表条目 |
| `cred_security_struct` | objsec.h:40-47 | 凭证安全结构 |

### 7.2 关键函数调用链

| 函数入口 | 源文件:行号 | 下游调用 | 功能描述 |
|---------|------------|---------|---------|
| `avc_lookup` | avc.c:553 | `avc_search_node` | AVC 缓存查找 |
| `avc_has_perm_noaudit` | avc.c:1145 | `avc_lookup` -> `avc_compute_av` | 不审核权限检查 |
| `avc_compute_av` | avc.c:987 | `security_compute_av` | 计算 AVC 决策 |
| `security_compute_av` | services.c:1123 | `context_struct_compute_av` | 安全服务器计算 |
| `security_context_to_sid` | services.c:1639 | `context_to_sid_core` | 上下文转 SID |
| `sidtab_context_to_sid` | sidtab.c:268 | `context_to_sid` | SID 表插入/查找 |
| `security_compute_sid` | services.c:1753 | `sidtab_context_to_sid` | 计算新 SID |
| `selinux_inode_permission` | hooks.c:3222 | `avc_has_perm` | inode 权限检查 |
| `inode_has_perm` | hooks.c:1677 | `avc_has_perm` | inode 权限核心 |
| `file_has_perm` | hooks.c:1756 | `inode_has_perm` | 文件描述符权限 |
| `avc_insert` | avc.c:606 | `avc_alloc_node` | AVC 条目插入 |
| `selinux_bprm_creds_for_exec` | hooks.c:2312 | `security_transition_sid` | exec 凭证转换 |

### 7.3 哈希函数对比

| 哈希函数 | 位置 | 输入 | 输出范围 | 用途 |
|---------|------|-----|---------|------|
| `avc_hash` | avc.c:126-129 | (ssid, tsid, tclass) | [0, AVC_CACHE_SLOTS) | AVC 缓存槽索引 |
| `context_compute_hash` | context.c | context 结构 | u32 | sidtab 反向查找 |

### 7.4 锁机制总结

| 锁类型 | 位置 | 保护对象 | 注释 |
|-------|------|---------|------|
| `slots_lock[]` | avc.c:74 | 单个 AVC 哈希槽 | 每槽独立锁，允许多读 |
| RCU | avc.c:59 | AVC 节点遍历 | 无锁读，延迟删除 |
| `sidtab.lock` | sidtab.h:91 | sidtab 写入 | 转换期间冻结 |
| `notif_lock` | avc.c:570 | latest_notif | 序列号更新 |

### 7.5 关键缓存机制

| 缓存名称 | 结构 | 命中率优化 | 失效策略 |
|---------|------|----------|---------|
| AVC | avc_cache | hash 查找 + 任务局部缓存 | 策略变更通知 |
| sidtab context_to_sid | 哈希表 | RCU 保护 | 策略切换时重建 |
| sidtab sid2str | LRU 列表 | 字符串缓存 | 手动失效 |

### 7.6 知识点维度关联

```
                    ┌─────────────────────────────┐
                    │     SELinux Security       │
                    │        Subsystem            │
                    └─────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   AVC (Access     │    │   SID Table       │    │   Hooks           │
│   Vector Cache)   │    │   (sidtab)        │    │   (LSM Interface) │
└───────────────────┘    └───────────────────┘    └───────────────────┘
        │                          │                          │
        ├── avc_hash()            ├── context_to_sid()      ├── selinux_bprm_creds_for_exec()
        ├── avc_lookup()          ├── sidtab_context_to_sid()├── selinux_inode_permission()
        ├── avc_insert()           └── sidtab_search()       ├── inode_has_perm()
        ├── avc_compute_av()      └── security_compute_sid() └── file_has_perm()
        └── avc_has_perm_noaudit()└── security_compute_av()
                │                          │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Policy Database   │
                │ (te_avtab, etc.)    │
                └─────────────────────┘
```

---

## 参考源码文件

| 文件路径 | 关键内容 |
|---------|---------|
| `security/selinux/avc.c` | AVC 缓存实现，avc_hash/avc_lookup/avc_insert/avc_has_perm_noaudit |
| `security/selinux/ss/services.c` | 安全服务器，security_context_to_sid/security_compute_av/security_compute_sid |
| `security/selinux/hooks.c` | LSM Hooks，selinux_inode_permission/selinux_bprm_creds_for_exec |
| `security/selinux/ss/sidtab.c` | SID 表实现，sidtab_context_to_sid/sidtab_search |
| `security/selinux/ss/sidtab.h` | SID 表数据结构定义 |
| `security/selinux/ss/context.h` | 安全上下文结构定义 |
| `security/selinux/include/objsec.h` | 各安全结构体定义 (cred/inode/file security_struct) |
| `security/selinux/include/avc.h` | AVC 公开接口和统计数据 |
