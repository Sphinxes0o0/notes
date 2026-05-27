# Linux 内核 Crypto 子系统异步加密机制分析

## 目录

1. [概述](#1-概述)
2. [AEAD 接口](#2-aead-接口)
3. [AHASH 接口](#3-ahash-接口)
4. [SHASH 同步哈希接口](#4-shash-同步哈希接口)
5. [异步处理机制](#5-异步处理机制)
6. [哈希算法实现](#6-哈希算法实现)
7. [AEAD 算法实例](#7-aead-算法实例)
8. [架构图](#8-架构图)

---

## 1. 概述

Linux 内核 Crypto 子系统提供了两类加密接口：

| 类型 | 描述 | 特点 |
|------|------|------|
| **同步接口** | 操作立即完成并返回结果 | 简单直接，用于不需要并发的场景 |
| **异步接口** | 通过回调机制通知完成 | 支持硬件加速，适用于高性能场景 |

### 1.1 核心数据结构

```c
// include/linux/crypto.h:188-195
struct crypto_async_request {
    struct list_head list;           // 链表节点，用于请求队列
    crypto_completion_t complete;    // 完成回调函数指针
    void *data;                      // 用户数据指针
    struct crypto_tfm *tfm;          // 密码变换句柄
    u32 flags;                       // 标志位
};
```

```c
// include/linux/crypto.h:179
typedef void (*crypto_completion_t)(void *req, int err);
```

### 1.2 异步等待机制

```c
// include/linux/crypto.h:363-367
struct crypto_wait {
    struct completion completion;     // 内核完成量
    int err;                         // 错误码
};
```

---

## 2. AEAD 接口

AEAD (Authenticated Encryption with Associated Data) 提供带关联数据的认证加密，典型算法包括 GCM、CCM、ChaCha20-Poly1305。

### 2.1 AEAD 请求结构

```c
// include/crypto/aead.h:81-102
struct aead_request {
    struct crypto_async_request base;   // 基础异步请求

    unsigned int assoclen;               // 关联数据长度
    unsigned int cryptlen;               // 加密数据长度

    u8 *iv;                              // 初始化向量

    struct scatterlist *src;             // 源数据 scatter-gather 列表
    struct scatterlist *dst;             // 目标数据 scatter-gather 列表

    void *__ctx[] CRYPTO_MINALIGN_ATTR;  // 算法特定上下文
};
```

### 2.2 AEAD 算法定义

```c
// include/crypto/aead.h:105-153
struct aead_alg {
    int (*setkey)(struct crypto_aead *tfm, const u8 *key,
                  unsigned int keylen);      // 设置密钥
    int (*setauthsize)(struct crypto_aead *tfm, unsigned int authsize); // 设置认证标签大小
    int (*encrypt)(struct aead_request *req);  // 加密操作
    int (*decrypt)(struct aead_request *req);  // 解密操作
    int (*init)(struct crypto_aead *tfm);       // 初始化
    void (*exit)(struct crypto_aead *tfm);       // 退出清理

    unsigned int ivsize;                       // IV 大小
    unsigned int maxauthsize;                   // 最大认证标签大小
    unsigned int chunksize;                     // 块大小

    struct crypto_alg base;                     // 基础算法结构
};
```

### 2.3 AEAD 密码句柄

```c
// include/crypto/aead.h:155-160
struct crypto_aead {
    unsigned int authsize;     // 认证标签大小
    unsigned int reqsize;      // 请求上下文大小

    struct crypto_tfm base;    // 基础变换
};
```

### 2.4 crypto_alloc_aead()

```c
// crypto/aead.c:201-204
struct crypto_aead *crypto_alloc_aead(const char *alg_name, u32 type, u32 mask)
{
    return crypto_alloc_tfm(alg_name, &crypto_aead_type, type, mask);
}
```

通过 `crypto_alloc_tfm()` 分配 AEAD 密码变换句柄，支持按名称查找算法。

### 2.5 aead_request_alloc()

```c
// include/crypto/aead.h:518-529
static inline struct aead_request *aead_request_alloc(struct crypto_aead *tfm,
                                                      gfp_t gfp)
{
    struct aead_request *req;

    // 分配请求内存：请求结构 + 算法上下文
    req = kmalloc(sizeof(*req) + crypto_aead_reqsize(tfm), gfp);

    if (likely(req))
        aead_request_set_tfm(req, tfm);

    return req;
}
```

### 2.6 crypto_aead_encrypt()

```c
// crypto/aead.c:84-92
int crypto_aead_encrypt(struct aead_request *req)
{
    struct crypto_aead *aead = crypto_aead_reqtfm(req);

    // 检查是否需要密钥
    if (crypto_aead_get_flags(aead) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;

    // 调用算法特定的加密实现
    return crypto_aead_alg(aead)->encrypt(req);
}
```

### 2.7 crypto_aead_decrypt()

```c
// crypto/aead.c:95-106
int crypto_aead_decrypt(struct aead_request *req)
{
    struct crypto_aead *aead = crypto_aead_reqtfm(req);

    if (crypto_aead_get_flags(aead) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;

    // 解密时密文包含认证标签
    if (req->cryptlen < crypto_aead_authsize(aead))
        return -EINVAL;

    return crypto_aead_alg(aead)->decrypt(req);
}
```

---

## 3. AHASH 接口

AHASH (Asynchronous Hash) 是异步哈希接口，支持 scatter-gather 列表输入。

### 3.1 AHASH 请求结构

```c
// include/crypto/hash.h:58-73
struct ahash_request {
    struct crypto_async_request base;   // 基础异步请求

    unsigned int nbytes;                // 数据长度
    union {
        struct scatterlist *src;        // scatter-gather 源
        const u8 *svirt;               // 或虚拟地址
    };
    u8 *result;                          // 摘要结果缓冲区

    struct scatterlist sg_head[2];       // scatter-gather 头
    crypto_completion_t saved_complete;  // 保存的回调
    void *saved_data;                    // 保存的用户数据

    void *__ctx[] CRYPTO_MINALIGN_ATTR; // 算法上下文
};
```

### 3.2 AHASH 算法定义

```c
// include/crypto/hash.h:154-171
struct ahash_alg {
    int (*init)(struct ahash_request *req);          // 初始化
    int (*update)(struct ahash_request *req);       // 更新数据
    int (*final)(struct ahash_request *req);         // 获取最终摘要
    int (*finup)(struct ahash_request *req);         // 更新+最终（组合操作）
    int (*digest)(struct ahash_request *req);        // 完整摘要计算
    int (*export)(struct ahash_request *req, void *out);  // 导出状态
    int (*import)(struct ahash_request *req, const void *in); // 导入状态
    int (*setkey)(struct crypto_ahash *tfm, const u8 *key, unsigned int keylen);

    struct hash_alg_common halg;                     // 通用哈希属性
};
```

### 3.3 AHASH 密码句柄

```c
// include/crypto/hash.h:277-282
struct crypto_ahash {
    bool using_shash;        // 是否使用底层 shash 算法
    unsigned int statesize;  // 状态大小
    unsigned int reqsize;    // 请求上下文大小
    struct crypto_tfm base;
};
```

### 3.4 crypto_alloc_ahash()

```c
// crypto/ahash.c:841-845
struct crypto_ahash *crypto_alloc_ahash(const char *alg_name, u32 type, u32 mask)
{
    return crypto_alloc_tfm(alg_name, &crypto_ahash_type, type, mask);
}
```

### 3.5 ahash_request_alloc()

```c
// include/crypto/hash.h:618-631
static inline struct ahash_request *ahash_request_alloc_noprof(
    struct crypto_ahash *tfm, gfp_t gfp)
{
    struct ahash_request *req;

    req = kmalloc_noprof(sizeof(struct ahash_request) +
                         crypto_ahash_reqsize(tfm), gfp);

    if (likely(req))
        ahash_request_set_tfm(req, tfm);

    return req;
}
```

### 3.6 crypto_ahash_digest()

```c
// crypto/ahash.c:570-581
int crypto_ahash_digest(struct ahash_request *req)
{
    struct crypto_ahash *tfm = crypto_ahash_reqtfm(req);

    // 如果底层使用 shash，直接调用 shash 的 digest
    if (likely(tfm->using_shash))
        return shash_ahash_digest(req, prepare_shash_desc(req, tfm));

    if (ahash_req_on_stack(req) && ahash_is_async(tfm))
        return -EAGAIN;
    if (crypto_ahash_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;

    return ahash_do_req_chain(req, &crypto_ahash_alg(tfm)->digest);
}
```

---

## 4. SHASH 同步哈希接口

SHASH (Synchronous Hash) 是同步哈希接口，API 更简单但不支持真正的异步操作。

### 4.1 SHASH 描述符

```c
// include/crypto/hash.h:173-176
struct shash_desc {
    struct crypto_shash *tfm;    // 密码变换句柄
    void *__ctx[] __aligned(ARCH_SLAB_MINALIGN); // 算法上下文
};
```

### 4.2 SHASH 算法定义

```c
// include/crypto/hash.h:249-274
struct shash_alg {
    int (*init)(struct shash_desc *desc);
    int (*update)(struct shash_desc *desc, const u8 *data, unsigned int len);
    int (*final)(struct shash_desc *desc, u8 *out);
    int (*finup)(struct shash_desc *desc, const u8 *data, unsigned int len, u8 *out);
    int (*digest)(struct shash_desc *desc, const u8 *data, unsigned int len, u8 *out);
    int (*export)(struct shash_desc *desc, void *out);
    int (*import)(struct shash_desc *desc, const void *in);
    int (*setkey)(struct crypto_shash *tfm, const u8 *key, unsigned int keylen);

    unsigned int descsize;       // 描述符上下文大小

    union {
        struct HASH_ALG_COMMON;
        struct hash_alg_common halg;
    };
};
```

### 4.3 crypto_shash_digest()

```c
// crypto/shash.c:183-194
int crypto_shash_digest(struct shash_desc *desc, const u8 *data,
                        unsigned int len, u8 *out)
{
    struct crypto_shash *tfm = desc->tfm;

    if (crypto_shash_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;

    return crypto_shash_op_and_zero(crypto_shash_alg(tfm)->digest, desc,
                                    data, len, out);
}
```

---

## 5. 异步处理机制

### 5.1 crypto_wait 等待机制

```c
// include/linux/crypto.h:372-374
#define DECLARE_CRYPTO_WAIT(_wait) \
    struct crypto_wait _wait = { \
        COMPLETION_INITIALIZER_ONSTACK((_wait).completion), 0 }

// crypto/api.c:704-713
void crypto_req_done(void *data, int err)
{
    struct crypto_wait *wait = data;

    if (err == -EINPROGRESS)
        return;

    wait->err = err;
    complete(&wait->completion);
}

// include/linux/crypto.h:381-393
static inline int crypto_wait_req(int err, struct crypto_wait *wait)
{
    switch (err) {
    case -EINPROGRESS:
    case -EBUSY:
        wait_for_completion(&wait->completion);
        reinit_completion(&wait->completion);
        err = wait->err;
        break;
    }
    return err;
}
```

### 5.2 异步操作流程

```
用户空间
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. 分配请求: aead_request_alloc()       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 2. 设置回调: aead_request_set_callback() │
│    - complete = crypto_req_done        │
│    - data = &wait                       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 3. 设置数据: aead_request_set_crypt()    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 4. 发起操作: crypto_aead_encrypt()       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 5. 返回 -EINPROGRESS (硬件队列已满)      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 6. 等待: crypto_wait_req()              │
│    - wait_for_completion()              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 7. 硬件完成后调用 crypto_req_done()      │
│    - complete() 唤醒等待进程             │
└─────────────────────────────────────────┘
    │
    ▼
用户空间继续执行
```

### 5.3 回调保存与恢复机制

AHASH 使用保存/恢复机制来链接多个异步操作：

```c
// crypto/ahash.c:391-397
static void ahash_save_req(struct ahash_request *req, crypto_completion_t cplt)
{
    req->saved_complete = req->base.complete;  // 保存原始回调
    req->saved_data = req->base.data;         // 保存原始数据
    req->base.complete = cplt;                 // 设置新回调
    req->base.data = req;                      // 设置新数据
}

static void ahash_restore_req(struct ahash_request *req)
{
    req->base.complete = req->saved_complete;  // 恢复原始回调
    req->base.data = req->saved_data;         // 恢复原始数据
}
```

### 5.4 请求链机制

```c
// crypto/ahash.c:322-369
static int ahash_do_req_chain(struct ahash_request *req,
                              int (*const *op)(struct ahash_request *req))
{
    struct crypto_ahash *tfm = crypto_ahash_reqtfm(req);

    // 虚拟地址请求或非虚拟请求直接执行
    if (crypto_ahash_req_virt(tfm) || !ahash_request_isvirt(req))
        return (*op)(req);

    // 需要 fallback 的情况处理状态导出/导入
    if (crypto_ahash_need_fallback(tfm))
        return -ENOSYS;

    // 执行链式操作
    {
        u8 state[HASH_MAX_STATESIZE];

        if (op == &crypto_ahash_alg(tfm)->digest) {
            ahash_request_set_tfm(req, crypto_ahash_fb(tfm));
            err = crypto_ahash_digest(req);
            goto out_no_state;
        }

        err = crypto_ahash_export(req, state);
        ahash_request_set_tfm(req, crypto_ahash_fb(tfm));
        err = err ?: crypto_ahash_import(req, state);

        if (op == &crypto_ahash_alg(tfm)->finup) {
            err = err ?: crypto_ahash_finup(req);
            goto out_no_state;
        }

        err = err ?:
              crypto_ahash_update(req) ?:
              crypto_ahash_export(req, state);

        ahash_request_set_tfm(req, tfm);
        return err ?: crypto_ahash_import(req, state);
    }
}
```

---

## 6. 哈希算法实现

### 6.1 MD5 算法注册

```c
// crypto/md5.c:177-216
static struct shash_alg algs[] = {
    {
        .base.cra_name        = "md5",
        .base.cra_driver_name = "md5-lib",
        .base.cra_priority    = 300,
        .base.cra_blocksize   = MD5_BLOCK_SIZE,
        .base.cra_module      = THIS_MODULE,
        .digestsize           = MD5_DIGEST_SIZE,
        .init                 = crypto_md5_init,
        .update               = crypto_md5_update,
        .final                = crypto_md5_final,
        .digest               = crypto_md5_digest,
        .export               = crypto_md5_export,
        .import               = crypto_md5_import,
        .descsize             = sizeof(struct md5_ctx),
        .statesize            = MD5_SHASH_STATE_SIZE,
    },
    // ... HMAC-MD5 算法
};
```

### 6.2 SHA256 算法注册

```c
// crypto/sha256.c:318-395
static struct shash_alg algs[] = {
    {
        .base.cra_name        = "sha256",
        .base.cra_driver_name = "sha256-lib",
        .base.cra_priority    = 300,
        .base.cra_blocksize   = SHA256_BLOCK_SIZE,
        .base.cra_module      = THIS_MODULE,
        .digestsize           = SHA256_DIGEST_SIZE,
        .init                 = crypto_sha256_init,
        .update               = crypto_sha256_update,
        .final                = crypto_sha256_final,
        .digest               = crypto_sha256_digest,
        .descsize             = sizeof(struct sha256_ctx),
        .statesize            = SHA256_SHASH_STATE_SIZE,
    },
    // ... SHA224, HMAC-SHA224, HMAC-SHA256
};
```

### 6.3 摘要计算流程

```
                    ┌─────────────────────────────────────────┐
                    │        crypto_ahash_digest()            │
                    │         (AHASH 异步接口)                 │
                    └─────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
         ┌──────────────────┐               ┌──────────────────┐
         │  using_shash=true │               │ using_shash=false│
         └──────────────────┘               └──────────────────┘
                    │                                   │
                    ▼                                   ▼
    ┌───────────────────────────┐       ┌───────────────────────────┐
    │   shash_ahash_digest()    │       │  ahash_do_req_chain()    │
    │   (crypto/ahash.c:205)    │       │    状态链式处理           │
    └───────────────────────────┘       └───────────────────────────┘
                    │                                   │
                    ▼                                   ▼
    ┌───────────────────────────┐       ┌───────────────────────────┐
    │  crypto_shash_digest()    │       │  algorithm->digest()     │
    │   (crypto/shash.c:183)    │       │   异步硬件操作            │
    └───────────────────────────┘       └───────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
                    ┌───────────────────────────────────┐
                    │      回调链完成或同步返回           │
                    └───────────────────────────────────┘
```

### 6.4 状态导出/导入机制

哈希算法支持暂停和恢复计算：

```c
// 导出状态
int crypto_ahash_export(struct ahash_request *req, void *out)
{
    struct crypto_ahash *tfm = crypto_ahash_reqtfm(req);

    if (likely(tfm->using_shash))
        return crypto_shash_export(ahash_request_ctx(req), out);

    // ... 非 shash 情况处理
}

// 导入状态
int crypto_ahash_import(struct ahash_request *req, const void *in)
{
    struct crypto_ahash *tfm = crypto_ahash_reqtfm(req);

    if (likely(tfm->using_shash))
        return crypto_shash_import(prepare_shash_desc(req, tfm), in);

    // ... 非 shash 情况处理
}
```

---

## 7. AEAD 算法实例

### 7.1 GCM 加密流程

GCM (Galois/Counter Mode) 是典型的 AEAD 算法：

```c
// crypto/gcm.c:445-456
static int crypto_gcm_encrypt(struct aead_request *req)
{
    struct crypto_gcm_req_priv_ctx *pctx = crypto_gcm_reqctx(req);
    struct skcipher_request *skreq = &pctx->u.skreq;
    u32 flags = aead_request_flags(req);

    crypto_gcm_init_common(req);
    crypto_gcm_init_crypt(req, req->cryptlen);
    skcipher_request_set_callback(skreq, flags, gcm_encrypt_done, req);

    return crypto_skcipher_encrypt(skreq) ?:
           gcm_encrypt_continue(req, flags);
}
```

#### GCM 加密流程图

```
                    ┌─────────────────────────────────────────┐
                    │         crypto_gcm_encrypt()            │
                    └─────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │  CTR 模式加密数据      │           │  初始化 GHASH          │
        │  (skcipher)          │           │  (ahash)              │
        └───────────────────────┘           └───────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           GHASH 计算关联数据             │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           生成认证标签                   │
                    │    auth_tag = GHASH(ciphertext || len)  │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │        拼接: ciphertext || tag          │
                    └─────────────────────────────────────────┘
```

#### GCM 异步回调链

```c
// crypto/gcm.c:430-443
static void gcm_encrypt_done(void *data, int err)
{
    struct aead_request *req = data;

    if (err)
        goto out;

    // 继续执行 gcm_encrypt_continue
    err = gcm_encrypt_continue(req, 0);
    if (err == -EINPROGRESS)
        return;

out:
    aead_request_complete(req, err);
}

// crypto/gcm.c:418-428
static int gcm_encrypt_continue(struct aead_request *req, u32 flags)
{
    struct crypto_gcm_req_priv_ctx *pctx = crypto_gcm_reqctx(req);
    struct crypto_gcm_ghash_ctx *gctx = &pctx->ghash_ctx;

    gctx->src = sg_next(req->src == req->dst ? pctx->src : pctx->dst);
    gctx->cryptlen = req->cryptlen;
    gctx->complete = gcm_enc_copy_hash;  // 设置完成回调

    return gcm_hash(req, flags);  // 启动哈希操作
}
```

### 7.2 ChaCha20-Poly1305 加密

ChaCha20-Poly1305 是另一种 AEAD 算法：

```c
// crypto/chacha20poly1305.c:272-285
static int chachapoly_encrypt(struct aead_request *req)
{
    struct chachapoly_req_ctx *rctx = aead_request_ctx(req);

    rctx->cryptlen = req->cryptlen;
    rctx->flags = aead_request_flags(req);

    /* 加密调用链:
     * - chacha_encrypt/done()
     * - poly_genkey/done()
     * - poly_hash()
     */
    return chacha_encrypt(req);
}
```

#### ChaCha20-Poly1305 加密流程

```
                    ┌─────────────────────────────────────────┐
                    │       chachapoly_encrypt()             │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         chacha_encrypt()                │
                    │   使用 ChaCha20 加密数据                 │
                    └─────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │   加密完成回调        │           │   poly_genkey()       │
        │   chacha_encrypt_done │           │   生成 Poly1305 密钥  │
        └───────────────────────┘           └───────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           poly_hash()                  │
                    │   使用 Poly1305 计算认证标签             │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │   拼接: ciphertext || auth_tag          │
                    └─────────────────────────────────────────┘
```

#### 异步回调继续机制

```c
// crypto/chacha20poly1305.c:56-68
static inline void async_done_continue(struct aead_request *req, int err,
                                       int (*cont)(struct aead_request *))
{
    if (!err) {
        struct chachapoly_req_ctx *rctx = aead_request_ctx(req);

        rctx->flags &= ~CRYPTO_TFM_REQ_MAY_SLEEP;
        err = cont(req);  // 调用下一个操作
    }

    // 如果不是正在处理中，则完成请求
    if (err != -EINPROGRESS && err != -EBUSY)
        aead_request_complete(req, err);
}
```

---

## 8. 架构图

### 8.1 Crypto API 层次结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户空间 API                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   AEAD      │  │   AHASH     │  │   SHASH     │  │   SKCIPHER  │   │
│  │  认证加密   │  │  异步哈希   │  │  同步哈希   │  │  对称密钥   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         通用 Crypto API                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  crypto_alloc_aead() / crypto_alloc_ahash() / crypto_alloc_*   │   │
│  │  aead_request_alloc() / ahash_request_alloc()                   │   │
│  │  crypto_wait_req() / crypto_req_done()                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        算法类型层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   GCM       │  │  ChaCha20   │  │    MD5      │  │   SHA-256   │   │
│  │             │  │ -Poly1305   │  │             │  │             │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │    CCM      │  │    CBC      │  │    CRC32    │  │   AES       │   │
│  │             │  │             │  │             │  │             │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        驱动/硬件层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  软件实现   │  │  CPU 指令   │  │  硬件引擎   │  │   外部模块  │   │
│  │  (generic) │  │  (AES-NI)   │  │  (crypto    │  │  (PKCS#11)  │   │
│  │             │  │             │  │   engine)   │  │             │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 AEAD 数据流

```
输入数据:
┌─────────────────────────────────────────────────────────────────────────┐
│  assoc_data (关联数据)  │  plaintext (明文)                             │
└─────────────────────────────────────────────────────────────────────────┘

AEAD 加密:
┌─────────────────────────────────────────────────────────────────────────┐
│                              AEAD 加密引擎                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   关联数据      │───▶│   加密操作      │───▶│   生成认证标签   │     │
│  │   (不做修改)    │    │  (CTR/GCM 等)   │    │   (Poly1305/    │     │
│  │                 │    │                 │    │    GHASH)       │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                    │                      │             │
└────────────────────────────────────┼──────────────────────┼─────────────┘
                                     ▼                      ▼
输出数据:
┌─────────────────────────────────────────────────────────────────────────┐
│  assoc_data (关联数据)  │  ciphertext (密文)  │  auth_tag (认证标签)      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.3 异步请求状态机

```
                    ┌─────────────────────────────────────────┐
                    │              请求分配                   │
                    │   aead_request_alloc() / ahash_*       │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │            设置回调                     │
                    │   aead_request_set_callback(req,       │
                    │              complete, data)            │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           发起异步操作                   │
                    │   crypto_aead_encrypt(req)               │
                    │   或 crypto_ahash_digest(req)            │
                    └─────────────────────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
              ┌────────────────────┐    ┌────────────────────┐
              │  返回 0 (同步完成) │    │ 返回 -EINPROGRESS  │
              │                    │    │   (异步处理中)     │
              └────────────────────┘    └────────────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │    硬件/软件处理中      │
                                    │                         │
                                    │  可能多次回调:          │
                                    │  done1 → done2 → done3 │
                                    └─────────────────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │   crypto_req_done()    │
                                    │   complete() 被调用    │
                                    │   唤醒等待进程         │
                                    └─────────────────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │   crypto_wait_req()    │
                                    │   返回最终结果          │
                                    └─────────────────────────┘
```

### 8.4 AHASH 与 SHASH 关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AHASH (异步)                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        crypto_ahash_*                           │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │   │
│  │  │   init    │  │  update   │  │   final   │  │  digest   │    │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │   │
│  │                         │                                       │   │
│  │            ┌─────────────┴─────────────┐                         │   │
│  │            ▼                           ▼                         │   │
│  │  ┌─────────────────────┐    ┌─────────────────────┐             │   │
│  │  │   using_shash=true  │    │  using_shash=false  │             │   │
│  │  │   (底层同步实现)     │    │  (原生异步实现)     │             │   │
│  │  └─────────────────────┘    └─────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                   │
└────────────────────────────────────┼───────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SHASH (同步)                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        crypto_shash_*                          │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │   │
│  │  │   init    │  │  update   │  │   final   │  │  digest   │    │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │              直接调用算法实现 (同步)                      │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录: 关键 API 速查表

### AEAD API

| 函数 | 文件:行号 | 说明 |
|------|----------|------|
| `crypto_alloc_aead()` | crypto/aead.c:201 | 分配 AEAD 句柄 |
| `crypto_free_aead()` | include/crypto/aead.h:216 | 释放 AEAD 句柄 |
| `crypto_aead_setkey()` | crypto/aead.c:44 | 设置密钥 |
| `crypto_aead_setauthsize()` | crypto/aead.c:65 | 设置认证标签大小 |
| `crypto_aead_encrypt()` | crypto/aead.c:84 | 加密 |
| `crypto_aead_decrypt()` | crypto/aead.c:95 | 解密 |
| `aead_request_alloc()` | include/crypto/aead.h:518 | 分配请求 |
| `aead_request_free()` | include/crypto/aead.h:535 | 释放请求 |
| `aead_request_set_callback()` | include/crypto/aead.h:565 | 设置回调 |
| `aead_request_set_crypt()` | include/crypto/aead.h:605 | 设置加密数据 |
| `aead_request_set_ad()` | include/crypto/aead.h:624 | 设置关联数据 |

### AHASH API

| 函数 | 文件:行号 | 说明 |
|------|----------|------|
| `crypto_alloc_ahash()` | crypto/ahash.c:841 | 分配 AHASH 句柄 |
| `crypto_free_ahash()` | include/crypto/hash.h:338 | 释放 AHASH 句柄 |
| `crypto_ahash_setkey()` | crypto/ahash.c:290 | 设置密钥 |
| `crypto_ahash_digest()` | crypto/ahash.c:570 | 计算摘要 |
| `crypto_ahash_init()` | crypto/ahash.c:371 | 初始化 |
| `crypto_ahash_update()` | crypto/ahash.c:447 | 更新数据 |
| `crypto_ahash_finup()` | crypto/ahash.c:528 | 更新并获取结果 |
| `crypto_ahash_final()` | include/crypto/hash.h:510 | 获取最终结果 |
| `ahash_request_alloc()` | include/crypto/hash.h:618 | 分配请求 |
| `ahash_request_free()` | include/crypto/hash.h:637 | 释放请求 |
| `ahash_request_set_callback()` | include/crypto/hash.h:676 | 设置回调 |
| `ahash_request_set_crypt()` | include/crypto/hash.h:699 | 设置数据 |

### SHASH API

| 函数 | 文件:行号 | 说明 |
|------|----------|------|
| `crypto_alloc_shash()` | crypto/shash.c:385 | 分配 SHASH 句柄 |
| `crypto_free_shash()` | include/crypto/hash.h:777 | 释放 SHASH 句柄 |
| `crypto_shash_setkey()` | crypto/shash.c:50 | 设置密钥 |
| `crypto_shash_digest()` | crypto/shash.c:183 | 计算摘要 |
| `crypto_shash_init()` | crypto/shash.c:81 | 初始化 |
| `crypto_shash_update()` | include/crypto/hash.h:1003 | 更新数据 |
| `crypto_shash_final()` | include/crypto/hash.h:1023 | 获取结果 |
| `crypto_shash_tfm_digest()` | crypto/shash.c:196 | 使用 tfm 直接计算摘要 |

### 异步等待 API

| 函数 | 文件:行号 | 说明 |
|------|----------|------|
| `DECLARE_CRYPTO_WAIT()` | include/linux/crypto.h:372 | 声明等待变量 |
| `crypto_init_wait()` | include/linux/crypto.h:395 | 初始化等待 |
| `crypto_wait_req()` | include/linux/crypto.h:381 | 等待请求完成 |
| `crypto_req_done()` | crypto/api.c:704 | 请求完成回调 |

---

*文档版本: 1.0*
*生成日期: 2026-04-26*
*源码版本: Linux Kernel (最新 master 分支)*
