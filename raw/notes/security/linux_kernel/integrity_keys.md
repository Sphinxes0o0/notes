# Linux 内核完整性测量与密钥管理子系统分析

## 目录

1. [概述](#概述)
2. [IMA (Integrity Measurement Architecture)](#ima-integrity-measurement-architecture)
3. [EVM (Extended Verification Module)](#evm-extended-verification-module)
4. [密钥管理子系统 (keys/)](#密钥管理子系统-keys)
5. [密钥类型](#密钥类型)
6. [密钥环](#密钥环)
7. [架构图](#架构图)

---

## 概述

Linux 内核的安全子系统包含两个紧密协作的模块：

- **IMA (Integrity Measurement Architecture)**: 负责测量文件的完整性，在文件被访问、执行、映射时计算并存储哈希值
- **EVM (Extended Verification Module)**: 负责验证文件元数据（扩展属性）的完整性，通过 HMAC 保护 security.* xattr

密钥管理系统则为上述模块提供密钥存储和检索能力，同时支持用户密钥、密钥环、可信密钥等各类密钥的管理。

---

## IMA (Integrity Measurement Architecture)

### 源码位置

```
/Users/sphinx/github/linux/security/integrity/ima/
├── ima.h              # IMA 核心头文件
├── ima_main.c         # IMA LSM hooks 实现
├── ima_api.c          # IMA 测量/存储 API
├── ima_policy.c       # IMA 策略处理
├── ima_crypto.c       # 哈希计算
├── ima_appraise.c     # 文件评估
└── ima_iint.c         # inode integrity cache
```

### 核心数据结构

#### `struct ima_iint_cache` (ima.h:188-200)

```c
/* IMA integrity metadata associated with an inode */
struct ima_iint_cache {
    struct mutex mutex;                  /* protects: version, flags, digest */
    struct integrity_inode_attributes real_inode;
    unsigned long flags;                /* IMA_MEASURE, IMA_APPRAISE, etc. */
    unsigned long measured_pcrs;
    unsigned long atomic_flags;
    enum integrity_status ima_file_status:4;   /* 文件状态: INTEGRITY_PASS/FAIL */
    enum integrity_status ima_mmap_status:4;
    enum integrity_status ima_bprm_status:4;
    enum integrity_status ima_read_status:4;
    enum integrity_status ima_creds_status:4;
    struct ima_digest_data *ima_hash;    /* 文件内容哈希 */
};
```

#### `struct ima_template_entry` (ima.h:106-112)

```c
struct ima_template_entry {
    int pcr;                            /* TPM PCR 索引 */
    struct tpm_digest *digests;         /* 各 TPM bank 的摘要 */
    struct ima_template_desc *template_desc; /* 模板描述符 */
    u32 template_data_len;
    struct ima_field_data template_data[]; /* 模板数据 */
};
```

#### IMA 动作标志 (ima.h:131-159)

```c
/* IMA iint action cache flags */
#define IMA_MEASURE       0x00000001   /* 需要测量 */
#define IMA_MEASURED      0x00000002   /* 已测量 */
#define IMA_APPRAISE      0x00000004   /* 需要评估 */
#define IMA_APPRAISED     0x00000008   /* 已评估 */
#define IMA_COLLECTED     0x00000020   /* 已收集哈希 */
#define IMA_AUDIT         0x00000040   /* 需要审计 */
#define IMA_HASH          0x00000100   /* 需要哈希 */
#define IMA_HASHED        0x00000200   /* 已哈希 */
```

### 核心函数

#### `ima_file_hash()` (ima_main.c:749-756)

获取文件哈希值的主接口：

```c
/**
 * ima_file_hash - return a measurement of the file
 * @file: pointer to the file
 * @buf: buffer in which to store the hash
 * @buf_size: length of the buffer
 *
 * On success, return the hash algorithm (as defined in the enum hash_algo).
 * If buf is not NULL, this function also outputs the hash into buf.
 */
int ima_file_hash(struct file *file, char *buf, size_t buf_size)
{
    if (!file)
        return -EINVAL;

    return __ima_inode_hash(file_inode(file), file, buf, buf_size);
}
EXPORT_SYMBOL_GPL(ima_file_hash);
```

#### `process_measurement()` (ima_main.c:236-470)

IMA 测量的核心函数，处理文件的测量、评估和审计：

```c
static int process_measurement(struct file *file, const struct cred *cred,
               struct lsm_prop *prop, char *buf, loff_t size,
               int mask, enum ima_hooks func,
               enum kernel_read_file_id read_id,
               bool bprm_is_check)
{
    // 1. 获取策略动作 (measurement, appraisal, audit)
    action = ima_get_action(...);

    // 2. 获取或创建 inode integrity cache
    iint = ima_inode_get(inode);

    // 3. 检查 ToMToU 违规 (Time-of-Measure, Time-of-Use)
    ima_rdwr_violation_check(...);

    // 4. 重新评估如果 xattr 改变或文件系统不支持 i_version
    if (test_and_clear_bit(IMA_CHANGE_XATTR, &iint->atomic_flags) ||
        ((inode->i_sb->s_iflags & SB_I_IMA_UNVERIFIABLE_SIGNATURE) && ...))
        iint->flags &= ~IMA_DONE_MASK;

    // 5. 收集文件哈希
    rc = ima_collect_measurement(iint, file, buf, size, hash_algo, modsig);

    // 6. 存储测量结果
    if (action & IMA_MEASURE)
        ima_store_measurement(iint, file, pathname, ...);

    // 7. 评估文件完整性
    if (action & IMA_APPRAISE_SUBMASK)
        rc = ima_appraise_measurement(func, iint, file, ...);

    // 8. 审计测量
    if (action & IMA_AUDIT)
        ima_audit_measurement(iint, pathname);
}
```

#### `ima_collect_measurement()` (ima_api.c:243-333)

收集文件的完整性测量：

```c
int ima_collect_measurement(struct ima_iint_cache *iint, struct file *file,
            void *buf, loff_t size, enum hash_algo algo,
            struct modsig *modsig)
{
    // 计算文件哈希
    if (buf) {
        result = ima_calc_buffer_hash(buf, size, hash_hdr);
    } else {
        result = ima_calc_file_hash(file, hash_hdr);
    }

    // 存储到 iint
    iint->ima_hash = tmpbuf;
    memcpy(iint->ima_hash, &hash, length);

    // 标记已收集
    if (!result)
        iint->flags |= IMA_COLLECTED;
}
```

#### `ima_get_action()` (ima_api.c:191-204)

根据策略决定对文件的动作：

```c
int ima_get_action(struct mnt_idmap *idmap, struct inode *inode,
           const struct cred *cred, struct lsm_prop *prop, int mask,
           enum ima_hooks func, int *pcr,
           struct ima_template_desc **template_desc,
           const char *func_data, unsigned int *allowed_algos)
{
    int flags = IMA_MEASURE | IMA_AUDIT | IMA_APPRAISE | IMA_HASH;
    flags &= ima_policy_flag;

    return ima_match_policy(idmap, inode, cred, prop, func, mask,
                flags, pcr, template_desc, func_data,
                allowed_algos);
}
```

### IMA LSM Hooks (ima_main.c:1277-1298)

```c
static struct security_hook_list ima_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(bprm_check_security, ima_bprm_check),           /* 执行前检查 */
    LSM_HOOK_INIT(bprm_creds_for_exec, ima_creds_check),        /* 凭证检查 */
    LSM_HOOK_INIT(file_post_open, ima_file_check),               /* 文件打开后 */
    LSM_HOOK_INIT(inode_post_create_tmpfile, ima_post_create_tmpfile),
    LSM_HOOK_INIT(file_release, ima_file_free),                  /* 文件释放 */
    LSM_HOOK_INIT(mmap_file, ima_file_mmap),                     /* 内存映射 */
    LSM_HOOK_INIT(file_mprotect, ima_file_mprotect),             /* 保护变化 */
    LSM_HOOK_INIT(kernel_load_data, ima_load_data),              /* 内核加载数据 */
    LSM_HOOK_INIT(kernel_post_load_data, ima_post_load_data),
    LSM_HOOK_INIT(kernel_read_file, ima_read_file),
    LSM_HOOK_INIT(kernel_post_read_file, ima_post_read_file),
    LSM_HOOK_INIT(path_post_mknod, ima_post_path_mknod),
#ifdef CONFIG_IMA_MEASURE_ASYMMETRIC_KEYS
    LSM_HOOK_INIT(key_post_create_or_update, ima_post_key_create_or_update),
#endif
    LSM_HOOK_INIT(inode_free_security_rcu, ima_inode_free_rcu),
};
```

---

## EVM (Extended Verification Module)

### 源码位置

```
/Users/sphinx/github/linux/security/integrity/evm/
├── evm.h              # EVM 核心头文件
├── evm_main.c         # EVM 主实现
├── evm_crypto.c       # HMAC 计算
└── evm_secfs.c       # 安全文件系统接口
```

### 核心数据结构

#### `struct evm_iint_cache` (evm.h:39-43)

```c
/* EVM integrity metadata associated with an inode */
struct evm_iint_cache {
    unsigned long flags;
    enum integrity_status evm_status:4;   /* EVM 验证状态 */
    struct integrity_inode_attributes metadata_inode;
};
```

#### EVM 初始化标志 (evm.h:20-27)

```c
#define EVM_INIT_HMAC      0x0001   /* HMAC 密钥已加载 */
#define EVM_INIT_X509      0x0002   /* X509 证书已加载 */
#define EVM_ALLOW_METADATA_WRITES  0x0004   /* 允许元数据写入 */
#define EVM_SETUP_COMPLETE 0x80000000 /* 用户空间已加载密钥 */
```

#### EVM 状态 (integrity.h 中定义)

```c
enum integrity_status {
    INTEGRITY_UNKNOWN = 0,
    INTEGRITY_PASS,           /* 验证通过 */
    INTEGRITY_PASS_IMMUTABLE, /* 验证通过（不可变签名）*/
    INTEGRITY_FAIL,          /* 验证失败 */
    INTEGRITY_FAIL_IMMUTABLE,/* 验证失败（不可变）*/
    INTEGRITY_NO_LABEL,      /* 缺少安全属性 */
    INTEGRITY_NO_XATTRS,     /* 缺少扩展属性 */
};
```

### 核心函数

#### `evm_verifyxattr()` (evm_main.c:421-431)

验证扩展属性的完整性：

```c
/**
 * evm_verifyxattr - verify the integrity of the requested xattr
 * @dentry: object of the verify xattr
 * @xattr_name: requested xattr
 * @xattr_value: requested xattr value
 * @xattr_value_len: requested xattr value length
 *
 * Calculate the HMAC for the given dentry and verify it against the stored
 * security.evm xattr.
 *
 * Returns the xattr integrity status.
 */
enum integrity_status evm_verifyxattr(struct dentry *dentry,
                      const char *xattr_name,
                      void *xattr_value, size_t xattr_value_len)
{
    if (!evm_key_loaded() || !evm_protected_xattr(xattr_name))
        return INTEGRITY_UNKNOWN;

    return evm_verify_hmac(dentry, xattr_name, xattr_value,
                   xattr_value_len);
}
EXPORT_SYMBOL_GPL(evm_verifyxattr);
```

#### `evm_verify_hmac()` (evm_main.c:178-297)

核心 HMAC 验证逻辑：

```c
static enum integrity_status evm_verify_hmac(struct dentry *dentry,
                         const char *xattr_name,
                         char *xattr_value,
                         size_t xattr_value_len)
{
    // 获取 security.evm xattr
    rc = vfs_getxattr_alloc(&nop_mnt_idmap, dentry, XATTR_NAME_EVM,
                (char **)&xattr_data, 0, GFP_NOFS);

    switch (xattr_data->type) {
    case EVM_XATTR_HMAC:
        // 计算 HMAC 并比较
        rc = evm_calc_hmac(dentry, xattr_name, xattr_value,
                   xattr_value_len, &digest, iint);
        rc = crypto_memneq(xattr_data->data, digest.digest,
                   SHA1_DIGEST_SIZE);
        break;

    case EVM_XATTR_PORTABLE_DIGSIG:
    case EVM_IMA_XATTR_DIGSIG:
        // 使用公钥验证签名
        rc = integrity_digsig_verify(INTEGRITY_KEYRING_EVM,
                (const char *)xattr_data, xattr_len,
                digest.digest, digest.hdr.length);
        break;
    }
}
```

#### `evm_inode_init_security()` (evm_main.c:1013-1065)

初始化新文件的 EVM HMAC：

```c
int evm_inode_init_security(struct inode *inode, struct inode *dir,
            const struct qstr *qstr, struct xattr *xattrs,
            int *xattr_count)
{
    if (!(evm_initialized & EVM_INIT_HMAC) || !xattrs)
        return 0;

    // 检查是否有受保护的 xattr
    for (xattr = xattrs; xattr->name; xattr++) {
        if (evm_protected_xattr(xattr->name))
            evm_protected_xattrs = true;
    }

    xattr_data->data.type = EVM_XATTR_HMAC;
    rc = evm_init_hmac(inode, xattrs, xattr_data->digest);

    evm_xattr->value = xattr_data;
    evm_xattr->value_len = sizeof(*xattr_data);
    evm_xattr->name = XATTR_EVM_SUFFIX;
}
```

#### EVM LSM Hooks (evm_main.c:1143-1159)

```c
static struct security_hook_list evm_hooks[] __ro_after_init = {
    LSM_HOOK_INIT(inode_setattr, evm_inode_setattr),
    LSM_HOOK_INIT(inode_post_setattr, evm_inode_post_setattr),
    LSM_HOOK_INIT(inode_copy_up_xattr, evm_inode_copy_up_xattr),
    LSM_HOOK_INIT(inode_setxattr, evm_inode_setxattr),
    LSM_HOOK_INIT(inode_post_setxattr, evm_inode_post_setxattr),
    LSM_HOOK_INIT(inode_set_acl, evm_inode_set_acl),
    LSM_HOOK_INIT(inode_post_set_acl, evm_inode_post_set_acl),
    LSM_HOOK_INIT(inode_remove_acl, evm_inode_remove_acl),
    LSM_HOOK_INIT(inode_post_remove_acl, evm_inode_post_remove_acl),
    LSM_HOOK_INIT(inode_removexattr, evm_inode_removexattr),
    LSM_HOOK_INIT(inode_post_removexattr, evm_inode_post_removexattr),
    LSM_HOOK_INIT(inode_init_security, evm_inode_init_security),
    LSM_HOOK_INIT(inode_alloc_security, evm_inode_alloc_security),
    LSM_HOOK_INIT(file_release, evm_file_release),
    LSM_HOOK_INIT(path_post_mknod, evm_post_path_mknod),
};
```

---

## 密钥管理子系统 (keys/)

### 源码位置

```
/Users/sphinx/github/linux/security/keys/
├── key.c              # 密钥分配、实例化
├── keyring.c          # 密钥环管理
├── request_key.c      # 密钥请求
├── user_defined.c     # user/logon 密钥类型
├── big_key.c          # 大数据密钥
├── trusted-keys/      # 可信密钥 (TPM/REE)
│   └── trusted_core.c
├── encrypted-keys/    # 加密密钥
├── process_keys.c     # 进程密钥管理
├── keyctl.c           # keyctl 系统调用
└── internal.h         # 内部接口
```

### 核心数据结构

#### `struct key` (include/linux/keys.h)

```c
struct key {
    union {
        struct list_head graveyard_link;    /* 废弃密钥链表 */
        struct rb_node serial_node;        /* 按序列号的红黑树节点 */
    };
    struct key_type __rcu *type;           /* 密钥类型 */
    struct key_tag __rcu *domain_tag;      /* 密钥域标签 */
    struct assoc_array keys;               /* 密钥环关联数组 */
    struct rw_semaphore sem;               /* 密钥读写信号量 */
    struct key_user *user;                 /* 密钥所有者信息 */
    void *security;                        /* LSM 安全模块数据 */

    /* 密钥描述信息 - 用于搜索 */
    struct keyring_index_key index_key;

    /* 密钥有效负载 */
    union {
        unsigned long value;               /* 简单值 */
        void *payload[4];                  /* 复杂数据指针 */
    };

    /* 密钥元数据 */
    kuid_t uid;                           /* 所有者 UID */
    kgid_t gid;                           /* 所有者 GID */
    key_perm_t perm;                      /* 权限掩码 */
    unsigned short quotalen;              /* 配额长度 */
    unsigned short datalen;               /* 数据长度 */

    /* 状态和标志 */
    time64_t expiry;                      /* 过期时间 */
    time64_t revoked_at;                  /* 撤销时间 */
    refcount_t usage;                      /* 引用计数 */
    short state;                          /* KEY_IS_*, 见下文 */

    unsigned long flags;                  /* 密钥标志 */
#define KEY_FLAG_DEAD                      (1 << 0)   /* 密钥已废弃 */
#define KEY_FLAG_REVOKED                   (1 << 1)   /* 密钥已撤销 */
#define KEY_FLAG_INVALIDATED               (1 << 2)   /* 密钥已失效 */
#define KEY_FLAG_USER_CONSTRUCT            (1 << 3)   /* 用户空间构造中 */
#define KEY_FLAG_NEGATIVE                  (1 << 4)   /* 负密钥 */
#define KEY_FLAG_ROOT_CAN_CLEAR            (1 << 5)   /* root 可清除 */
#define KEY_FLAG_INVALIDATED_KEYRING       (1 << 6)   /* 密钥环已失效 */

    /* ... 其他字段 ... */
} __randomize_layout;
```

#### `struct key_type` (include/linux/key-type.h)

```c
struct key_type {
    const char *name;                      /* 密钥类型名称 */
    size_t def_datalen;                   /* 默认数据长度 */
    unsigned int flags;                   /* 类型标志 */
#define KEY_TYPE_NET_DOMAIN    0x00000001  /* 网络域密钥 */

    /* 密钥操作函数 */
    int (*preparse)(struct key_preparsed_payload *prep);
    void (*free_preparse)(struct key_preparsed_payload *prep);

    int (*instantiate)(struct key *key, struct key_preparsed_payload *prep);
    int (*update)(struct key *key, struct key_preparsed_payload *prep);
    int (*match_preparse)(struct key_match_data *match_data);
    void (*match_free)(struct key_match_data *match_data);

    void (*revoke)(struct key *key);
    void (*destroy)(struct key *key);
    void (*describe)(const struct key *key, struct seq_file *m);
    long (*read)(const struct key *key, char *buffer, size_t buflen);

    /* 用于请求式创建密钥 */
    int (*request_key)(struct key *authkey, void *aux);

    /* 描述符验证 */
    int (*vet_description)(const char *description);

    /* 限制查找 */
    struct key_restriction *(*lookup_restriction)(const char *params);

    struct lock_class_key lock_class;
    struct list_head link;                /* 链接到类型列表 */
};
```

#### `struct keyring_index_key` (keys.h)

```c
struct keyring_index_key {
    struct key_type *type;                /* 密钥类型 */
    struct key_tag *domain_tag;          /* 域标签 */
    union {
        struct {
            u16 desc_len;                /* 描述符长度 */
            char description[MAX_DESCRIPTION_LEN]; /* 描述符 */
        };
        unsigned long hash;               /* 哈希值 */
    };
};
```

#### 密钥状态 (keys.h)

```c
enum key_state {
    KEY_IS_UNINSTANTIATED,               /* 未实例化 */
    KEY_IS_NEGATIVE,                     /* 负密钥（不存在）*/
    KEY_IS_POSITIVE,                     /* 正密钥（存在且有效）*/
};
```

### 核心函数

#### `key_alloc()` (key.c:224-360)

分配新密钥：

```c
/**
 * key_alloc - Allocate a key of the specified type.
 * @type: The type of key to allocate.
 * @desc: The key description to allow the key to be searched out.
 * @uid: The owner of the new key.
 * @gid: The group ID for the new key's group permissions.
 * @cred: The credentials specifying UID namespace.
 * @perm: The permissions mask of the new key.
 * @flags: Flags specifying quota properties.
 * @restrict_link: Optional link restriction for new keyrings.
 */
struct key *key_alloc(struct key_type *type, const char *desc,
              kuid_t uid, kgid_t gid, const struct cred *cred,
              key_perm_t perm, unsigned long flags,
              struct key_restriction *restrict_link)
{
    // 1. 获取密钥用户结构
    user = key_user_lookup(uid);

    // 2. 检查配额
    if (!(flags & KEY_ALLOC_NOT_IN_QUOTA)) {
        if (user->qnkeys + 1 > maxkeys ||
            user->qnbytes + quotalen > maxbytes)
            goto no_quota;
    }

    // 3. 分配并初始化密钥
    key = kmem_cache_zalloc(key_jar, GFP_KERNEL);
    key->index_key.type = type;
    key->index_key.description = kmemdup(desc, desclen + 1, GFP_KERNEL);
    refcount_set(&key->usage, 1);
    init_rwsem(&key->sem);

    // 4. LSM 安全检查
    ret = security_key_alloc(key, cred, flags);
    if (ret < 0)
        goto security_error;

    // 5. 分配序列号
    key_alloc_serial(key);

    return key;
}
```

#### `key_instantiate_and_link()` (key.c:499-552)

实例化密钥并链接到密钥环：

```c
int key_instantiate_and_link(struct key *key,
                 const void *data,
                 size_t datalen,
                 struct key *keyring,
                 struct key *authkey)
{
    // 1. 准备数据
    prep.data = data;
    prep.datalen = datalen;

    if (key->type->preparse)
        key->type->preparse(&prep);

    // 2. 锁定密钥环并准备链接
    if (keyring) {
        ret = __key_link_lock(keyring, &key->index_key);
        ret = __key_link_begin(keyring, &key->index_key, &edit);

        // 检查限制
        if (keyring->restrict_link && keyring->restrict_link->check)
            ret = keyring->restrict_link->check(...);
    }

    // 3. 调用类型特定的实例化函数
    ret = key->type->instantiate(key, &prep);

    // 4. 标记为已实例化
    mark_key_instantiated(key, 0);

    // 5. 链接到密钥环
    if (keyring)
        __key_link(keyring, key, &edit);

    // 6. 禁用授权密钥
    if (authkey)
        key_invalidate(authkey);
}
```

#### `key_put()` (key.c:647-668)

释放密钥引用：

```c
void key_put(struct key *key)
{
    if (key) {
        key_check(key);

        if (refcount_dec_and_test(&key->usage)) {
            // 更新配额
            if (test_bit(KEY_FLAG_IN_QUOTA, &key->flags)) {
                spin_lock_irqsave(&key->user->lock, flags);
                key->user->qnkeys--;
                key->user->qnbytes -= key->quotalen;
                spin_unlock_irqrestore(&key->user->lock, flags);
            }
            clear_bit_unlock(KEY_FLAG_USER_ALIVE, &key->flags);
            schedule_work(&key_gc_work);  // 调度 GC
        }
    }
}
```

---

## 密钥类型

### user 类型 (user_defined.c)

存储用户定义的任意数据：

```c
struct key_type key_type_user = {
    .name       = "user",
    .preparse   = user_preparse,
    .free_preparse = user_free_preparse,
    .instantiate = generic_key_instantiate,
    .update     = user_update,
    .revoke     = user_revoke,
    .destroy    = user_destroy,
    .describe   = user_describe,
    .read       = user_read,
};
```

**user_preparse()** (user_defined.c:59-77):
```c
int user_preparse(struct key_preparsed_payload *prep)
{
    // 限制数据长度 0-32767 字节
    if (datalen == 0 || datalen > 32767 || !prep->data)
        return -EINVAL;

    upayload = kmalloc(sizeof(*upayload) + datalen, GFP_KERNEL);
    prep->quotalen = datalen;
    prep->payload.data[0] = upayload;
    upayload->datalen = datalen;
    memcpy(upayload->data, prep->data, datalen);
    return 0;
}
```

### logon 类型 (user_defined.c)

与 user 类型类似，但不可从用户空间读取：

```c
struct key_type key_type_logon = {
    .name       = "logon",
    .preparse   = user_preparse,
    .free_preparse = user_free_preparse,
    .instantiate = generic_key_instantiate,
    .update     = user_update,
    .revoke     = user_revoke,
    .destroy    = user_destroy,
    .describe   = user_describe,
    .vet_description = logon_vet_description,  /* 要求有 ":" 分隔符 */
};
```

### big_key 类型 (big_key.c)

用于存储大于默认值的大数据密钥（> 约 600 字节阈值）：

```c
struct key_type key_type_big_key = {
    .name       = "big_key",
    .preparse   = big_key_preparse,
    .free_preparse = big_key_free_preparse,
    .instantiate = generic_key_instantiate,
    .revoke     = big_key_revoke,
    .destroy    = big_key_destroy,
    .describe   = big_key_describe,
    .read       = big_key_read,
    .update     = big_key_update,
};
```

**big_key_preparse()** (big_key.c:57-147):
```c
int big_key_preparse(struct key_preparsed_payload *prep)
{
    // 数据大小限制 1 byte - 1 MB
    if (datalen == 0 || datalen > 1024 * 1024 || !prep->data)
        return -EINVAL;

    if (datalen > BIG_KEY_FILE_THRESHOLD) {
        // 大数据：存储在 shmem 文件中
        // 使用 chacha20poly1305 加密
        buf = kvmalloc(enclen, GFP_KERNEL);
        get_random_bytes_wait(enckey, CHACHA20POLY1305_KEY_SIZE);
        chacha20poly1305_encrypt(buf, prep->data, datalen, NULL, 0, 0, enckey);

        // 创建 shmem 文件
        file = shmem_kernel_file_setup("", enclen, EMPTY_VMA_FLAGS);
        kernel_write(file, buf, enclen, &pos);

        payload->data = enckey;
        payload->path = file->f_path;
    } else {
        // 小数据：直接存储在内存
        payload->data = kmalloc(datalen, GFP_KERNEL);
        memcpy(data, prep->data, prep->datalen);
    }
}
```

### trusted 类型 (trusted_core.c)

使用 TPM 或其他可信执行环境密封的密钥：

```c
struct key_type key_type_trusted = {
    .name = "trusted",
    .instantiate = trusted_instantiate,
    .update = trusted_update,
    .destroy = trusted_destroy,
    .describe = user_describe,
    .read = trusted_read,
};
```

**trusted_instantiate()** (trusted_core.c:155-222):
```c
static int trusted_instantiate(struct key *key,
               struct key_preparsed_payload *prep)
{
    datablob_parse(&datablob, payload);

    switch (key_cmd) {
    case Opt_load:
        // 解密封
        ret = static_call(trusted_key_unseal)(payload, datablob);
        break;
    case Opt_new:
        // 生成随机密钥并密封
        ret = static_call(trusted_key_get_random)(payload->key, key_len);
        ret = static_call(trusted_key_seal)(payload, datablob);
        break;
    }
}
```

### asymmetric 类型

用于非对称密钥（RSA、ECDSA 等）的签名验证：

```c
// 使用 crypto/public_key.h 中的接口
int asymmetric_verify(struct key *keyring, const char *sig,
             int siglen, const char *data, int datalen)
{
    struct public_key_signature pks;
    struct signature_v2_hdr *hdr = (struct signature_v2_hdr *)sig;

    // 获取密钥
    key = request_asymmetric_key(keyring, be32_to_cpu(hdr->keyid));

    // 设置签名信息
    pks.hash_algo = hash_algo_name[hdr->hash_algo];
    pk = asymmetric_key_public_key(key);
    pks.pkey_algo = pk->pkey_algo;

    // 验证签名
    return verify_signature(key, &pks);
}
```

---

## 密钥环

### 核心数据结构

#### `struct key_restriction` (keys.h)

```c
struct key_restriction {
    key_restrict_link_func_t check;     /* 限制检查函数 */
    struct key *key;                     /* 关联的密钥 */
    const struct key_type *keytype;     /* 密钥类型 */
    unsigned long flags;
};
```

### 核心函数

#### `keyring_alloc()` (keyring.c:517-538)

创建新密钥环：

```c
struct key *keyring_alloc(const char *description, kuid_t uid, kgid_t gid,
              const struct cred *cred, key_perm_t perm,
              unsigned long flags,
              struct key_restriction *restrict_link,
              struct key *dest)
{
    keyring = key_alloc(&key_type_keyring, description,
                uid, gid, cred, perm, flags, restrict_link);
    if (!IS_ERR(keyring)) {
        ret = key_instantiate_and_link(keyring, NULL, 0, dest, NULL);
        if (ret < 0) {
            key_put(keyring);
            keyring = ERR_PTR(ret);
        }
    }
    return keyring;
}
```

#### `key_link()` (keyring.c:1438-1469)

将密钥链接到密钥环：

```c
int key_link(struct key *keyring, struct key *key)
{
    ret = __key_link_lock(keyring, &key->index_key);
    if (ret < 0)
        goto error;

    ret = __key_link_begin(keyring, &key->index_key, &edit);
    if (ret < 0)
        goto error_end;

    // 检查限制
    ret = __key_link_check_restriction(keyring, key);
    if (ret == 0)
        ret = __key_link_check_live_key(keyring, key);
    if (ret == 0)
        __key_link(keyring, key, &edit);

error_end:
    __key_link_end(keyring, &key->index_key, edit);
error:
    return ret;
}
```

#### `key_unlink()` (keyring.c:1548-1566)

从密钥环解除链接：

```c
int key_unlink(struct key *keyring, struct key *key)
{
    ret = __key_unlink_lock(keyring);
    if (ret < 0)
        return ret;

    ret = __key_unlink_begin(keyring, key, &edit);
    if (ret == 0)
        __key_unlink(keyring, key, &edit);
    __key_unlink_end(keyring, key, edit);
    return ret;
}
```

#### `keyring_search()` (keyring.c:940-974)

在密钥环中搜索密钥：

```c
key_ref_t keyring_search(key_ref_t keyring,
             struct key_type *type,
             const char *description,
             bool recurse)
{
    struct keyring_search_context ctx = {
        .index_key.type     = type,
        .index_key.description = description,
        .cred         = current_cred(),
        .match_data.cmp     = key_default_cmp,
        .flags         = KEYRING_SEARCH_DO_STATE_CHECK,
    };

    if (recurse)
        ctx.flags |= KEYRING_SEARCH_RECURSE;

    rcu_read_lock();
    key = keyring_search_rcu(keyring, &ctx);
    rcu_read_unlock();

    return key;
}
```

### 密钥搜索上下文 (internal.h:112-132)

```c
struct keyring_search_context {
    struct keyring_index_key index_key;
    const struct cred *cred;
    struct key_match_data match_data;
    unsigned flags;
#define KEYRING_SEARCH_NO_STATE_CHECK  0x0001  /* 跳过状态检查 */
#define KEYRING_SEARCH_DO_STATE_CHECK  0x0002  /* 执行状态检查 */
#define KEYRING_SEARCH_NO_UPDATE_TIME  0x0004  /* 不更新时间 */
#define KEYRING_SEARCH_NO_CHECK_PERM   0x0008  /* 不检查权限 */
#define KEYRING_SEARCH_DETECT_TOO_DEEP 0x0010  /* 检测深度 */
#define KEYRING_SEARCH_SKIP_EXPIRED    0x0020  /* 跳过过期密钥 */
#define KEYRING_SEARCH_RECURSE         0x0040  /* 递归搜索子密钥环 */

    int (*iterator)(const void *object, void *iterator_data);
    int skipped_ret;
    bool possessed;
    key_ref_t result;
    time64_t now;
};
```

### 密钥请求 (request_key.c)

#### `request_key_and_link()` (request_key.c:574-663)

请求密钥，必要时调用用户空间构造：

```c
struct key *request_key_and_link(struct key_type *type,
                 const char *description,
                 struct key_tag *domain_tag,
                 const void *callout_info,
                 size_t callout_len,
                 void *aux,
                 struct key *dest_keyring,
                 unsigned long flags)
{
    // 1. 构造搜索上下文
    struct keyring_search_context ctx = {
        .index_key.type = type,
        .index_key.description = description,
        .flags = KEYRING_SEARCH_DO_STATE_CHECK | KEYRING_SEARCH_RECURSE,
    };

    // 2. 检查缓存的密钥
    key = check_cached_key(&ctx);

    // 3. 搜索进程密钥环
    rcu_read_lock();
    key_ref = search_process_keyrings_rcu(&ctx);
    rcu_read_unlock();

    if (!IS_ERR(key_ref)) {
        // 找到密钥，链接到目标密钥环
        key = key_ref_to_ptr(key_ref);
        if (dest_keyring)
            key_link(dest_keyring, key);
    } else if (PTR_ERR(key_ref) == -EAGAIN) {
        // 未找到，调用用户空间构造
        if (callout_info)
            key = construct_key_and_link(&ctx, callout_info,
                             callout_len, aux, dest_keyring, flags);
    }
}
```

---

## 架构图

### IMA/EVM 整体架构

```
+-------------------+     +-------------------+     +------------------+
|   Application     |     |   Application     |     |   Application    |
+-------------------+     +-------------------+     +------------------+
         |                        |                        |
         v                        v                        v
+-------------------+     +-------------------+     +------------------+
|   File Open       |     |   Execute         |     |   mmap           |
+-------------------+     +-------------------+     +------------------+
         |                        |                        |
         v                        v                        v
+--------+-------+        +-------+--------+        +-------+--------+
| IMA File Hook    |      | IMA BPRM Hook    |       | IMA MMAP Hook   |
+--------+-------+        +-------+--------+        +-------+--------+
         |                        |                        |
         v                        v                        v
+------------------------------------------------------------------+
|                     process_measurement()                          |
|  +------------+  +------------+  +------------+  +------------+  |
|  | ima_get_action | | ima_collect_ | | ima_store_  | | ima_appraise_ | |
|  | (策略匹配)    | | measurement | | measurement | | measurement  | |
|  +------------+  | (收集哈希)  | | (存储测量)  | | (评估完整性) | |
|                  +------------+  +------------+  +------------+  |
+------------------------------------------------------------------+
         |                        |                        |
         v                        v                        v
+------------------------------------------------------------------+
|                        IMA Measurement List                        |
|  /sys/kernel/security/ima/ascii_runtime_measurements               |
+------------------------------------------------------------------+
         |
         v
+------------------+
|   TPM PCR Extend  |
+------------------+
         ^
         |
+-------------------------------------------------------------------+
|  security_inode_init_security() -> evm_inode_init_security()     |
+-------------------------------------------------------------------+
         |
         v
+------------------+
|   EVM HMAC Calc  |
+------------------+
         |
         v
+------------------+
| security.evm     |
| (xattr)          |
+------------------+
```

### 密钥管理架构

```
+------------------------------------------------------------------+
|                         Userspace                                  |
|  +---------------+  +----------------+  +----------------------+    |
|  | keyctl syscall |  | /sbin/request-key |  | keyring operations  |    |
|  +---------------+  +----------------+  +----------------------+    |
+------------------------------------------------------------------+
         |                      |                       |
         v                      v                       v
+------------------------------------------------------------------+
|                        Kernel                                      |
|                                                                   |
|  +--------------------------------------------------------------+ |
|  |                      key.c                                    | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  |  | key_alloc()|  |key_instantiate_|  | key_put()           |  | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  +--------------------------------------------------------------+ |
|                                                                   |
|  +--------------------------------------------------------------+ |
|  |                    keyring.c                                  | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  |  |keyring_alloc| | key_link()    |  | keyring_search()     |  | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  |  |key_unlink() |  | key_move()    |  | keyring_gc()        |  | |
|  |  +------------+  +--------------+  +----------------------+  | |
|  +--------------------------------------------------------------+ |
|                                                                   |
|  +--------------------------------------------------------------+ |
|  |                    request_key.c                              | |
|  |  +----------------------------+  +-------------------------+ | |
|  |  | request_key_and_link()    |  | construct_key_and_link()| | |
|  |  +----------------------------+  +-------------------------+ | |
|  +--------------------------------------------------------------+ |
|                                                                   |
|  +------------+  +------------+  +------------+  +---------------+ |
|  | user_type  |  | big_key    |  | trusted    |  | asymmetric    | |
|  +------------+  +------------+  +------------+  +---------------+ |
|                                                                   |
|  +--------------------------------------------------------------+ |
|  |                    trusted-keys/                              | |
|  |  +------------+  +------------+  +------------+               | |
|  |  | trusted_tpm|  | trusted_tee|  | trusted_caam|               | |
|  |  +------------+  +------------+  +------------+               | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
         |
         v
+------------------+
|  Key Serial Tree |
|  (rb_root)       |
+------------------+
         |
         v
+------------------+
| Key User Tree    |
| (per-UID quota)  |
+------------------+
```

### IMA 策略处理流程

```
+------------------+
| ima_policy_flag  |
+------------------+
         ^
         |
+--------+---------+
| ima_get_action() |
+--------+---------+
         |
         v
+-------------------------+
| ima_match_policy()      |
| (匹配策略规则)           |
+-------------------------+
         |
    +----+----+
    |         |
    v         v
+-------+  +--------+
| IMA_   |  | IMA_   |
| MEASURE|  | APPRAISE|
+-------+  +--------+
    |         |
    v         v
+-------+  +--------+
| ima_  |  | ima_   |
| store_|  | check_  |
| measure|  | blacklist|
+-------+  +--------+
    |         |
    v         v
+-------+  +--------+
| ima_  |  | ima_   |
| add_  |  | verify_ |
| template| | xattr() |
+-------+  +--------+
```

### EVM 元数据保护流程

```
+-------------+      +------------------+      +------------------+
| setxattr()  | ---> | evm_inode_setxattr() | -> | evm_verify_hmac()|
+-------------+      +------------------+      +------------------+
                                                     |
                                                     v
                                             +------------------+
                                             | 计算 HMAC        |
                                             | (evm_calc_hmac) |
                                             +------------------+
                                                     |
                                                     v
                                             +------------------+
                                             | 比较 HMAC        |
                                             | crypto_memneq() |
                                             +------------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                           |                           |
                         v                           v                           v
               +------------------+         +------------------+         +------------------+
               | INTEGRITY_PASS   |         | INTEGRITY_FAIL   |         | INTEGRITY_UNKNOWN|
               +------------------+         +------------------+         +------------------+
```

---

## 完整性密钥环

IMA/EVM 使用以下专用密钥环 (`integrity.h:120-124`):

```c
#define INTEGRITY_KEYRING_EVM      0  /* EVM HMAC/签名密钥环 */
#define INTEGRITY_KEYRING_IMA      1  /* IMA 测量签名密钥环 */
#define INTEGRITY_KEYRING_PLATFORM 2  /* 平台证书密钥环 */
#define INTEGRITY_KEYRING_MACHINE  3  /* 机器密钥环 */
#define INTEGRITY_KEYRING_MAX      4
```

---

## 关键文件列表

| 文件路径 | 功能描述 |
|---------|----------|
| `security/integrity/ima/ima.h` | IMA 核心数据结构定义 |
| `security/integrity/ima/ima_main.c` | IMA LSM hooks 实现 |
| `security/integrity/ima/ima_api.c` | IMA 测量/存储 API |
| `security/integrity/ima/ima_policy.c` | IMA 策略处理 |
| `security/integrity/ima/ima_crypto.c` | 哈希计算 |
| `security/integrity/ima/ima_appraise.c` | 文件完整性评估 |
| `security/integrity/evm/evm.h` | EVM 核心数据结构 |
| `security/integrity/evm/evm_main.c` | EVM 主实现 |
| `security/integrity/evm/evm_crypto.c` | HMAC 计算 |
| `security/integrity/digsig_asymmetric.c` | 非对称签名验证 |
| `security/keys/key.c` | 密钥分配和实例化 |
| `security/keys/keyring.c` | 密钥环管理 |
| `security/keys/request_key.c` | 密钥请求 |
| `security/keys/user_defined.c` | user/logon 密钥类型 |
| `security/keys/big_key.c` | 大数据密钥类型 |
| `security/keys/trusted-keys/trusted_core.c` | 可信密钥核心 |
| `include/linux/keys.h` | 密钥结构定义 |
| `include/linux/key-type.h` | 密钥类型定义 |

---

## 参考

- `Documentation/security/ima-design.rst` - IMA 设计文档
- `Documentation/security/keys-trusted-encrypted.rst` - 可信密钥文档
- `Documentation/security/keys-request-key.rst` - 密钥请求文档
