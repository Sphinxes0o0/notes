# Linux Crypto 子系统深度分析 R1

## 目录
1. [Crypto Core (核心层)](#1-crypto-core-核心层)
2. [skcipher (对称密匙密码)](#2-skcipher-对称密匙密码)
3. [aead (认证加密)](#3-aead-认证加密)
4. [ahash/shash (异步/同步哈希)](#4-ahashshash-异步同步哈希)
5. [cryptd (异步加密封装)](#5-cryptd-异步加密封装)
6. [Jitter RNG (抖动熵源)](#6-jitter-rng-抖动熵源随机数生成器)
7. [知识点关联表](#7-知识点关联表)

---

## 1. Crypto Core (核心层)

### 1.1 struct crypto_alg 核心算法结构

`crypto_alg` 是所有加密算法的基类结构，定义于 `/Users/sphinx/github/linux/include/linux/crypto.h:332`:

```c
struct crypto_alg {
    struct list_head cra_list;      // 算法注册链表节点
    struct list_head cra_users;    // 使用该算法的用户列表
    
    u32 cra_flags;                 // 算法标志 (CRYPTO_ALG_TYPE_MASK, CRYPTO_ALG_ASYNC等)
    unsigned int cra_blocksize;     // 块大小
    unsigned int cra_ctxsize;      // 上下文/状态大小
    unsigned int cra_alignmask;     // 对齐掩码
    unsigned int cra_reqsize;      // 请求结构大小
    
    int cra_priority;              // 算法优先级
    refcount_t cra_refcnt;         // 引用计数
    
    char cra_name[CRYPTO_MAX_ALG_NAME];        // 算法通用名称
    char cra_driver_name[CRYPTO_MAX_ALG_NAME]; // 驱动名称
    
    const struct crypto_type *cra_type;  // 算法类型
    
    union {
        struct cipher_alg cipher;
    } cra_u;
    
    int (*cra_init)(struct crypto_tfm *tfm);     // 初始化回调
    void (*cra_exit)(struct crypto_tfm *tfm);    // 退出回调
    void (*cra_destroy)(struct crypto_alg *alg);  // 销毁回调
    
    struct module *cra_module;  // 所属模块
} CRYPTO_MINALIGN_ATTR;
```

### 1.2 算法注册流程 (crypto_register_alg)

`crypto_register_alg()` 函数负责将算法注册到全局算法列表，源码位于 `/Users/sphinx/github/linux/crypto/api.c`:

**关键流程 (api.c:324-336):**
```c
int crypto_probing_notify(unsigned long val, void *v)
{
    int ok;
    ok = blocking_notifier_call_chain(&crypto_chain, val, v);
    if (ok == NOTIFY_DONE) {
        request_module("cryptomgr");
        ok = blocking_notifier_call_chain(&crypto_chain, val, v);
    }
    return ok;
}
```

**算法查找机制 (api.c:338-369):**
```c
struct crypto_alg *crypto_alg_mod_lookup(const char *name, u32 type, u32 mask)
{
    struct crypto_alg *alg;
    struct crypto_alg *larval;
    
    // 1. larval lookup - 如果没找到，创建一个 larval (幼虫状态)
    larval = crypto_larval_lookup(name, type, mask);
    
    // 2. 触发探测通知，让 cryptd 或其他模块尝试提供算法
    ok = crypto_probing_notify(CRYPTO_MSG_ALG_REQUEST, larval);
    
    // 3. 等待 larval 成熟或返回错误
    if (ok == NOTIFY_STOP)
        alg = crypto_larval_wait(larval, type, mask);
    else
        alg = ERR_PTR(-ENOENT);
        
    return alg;
}
```

### 1.3 Larval 机制与算法延迟初始化

`crypto_larval` 是算法注册的核心机制，确保算法在真正需要时才进行完整初始化:

```c
// api.c:104-123 - larval 数据结构
struct crypto_larval {
    struct crypto_alg alg;           // 继承 crypto_alg
    u32 mask;                        // 类型掩码
    struct crypto_alg *adult;        // 成熟的算法实例
    struct completion completion;     // 等待完成信号
    bool test_started;               // 自测是否已开始
};

// api.c:126-153 - larval 添加流程
static struct crypto_alg *crypto_larval_add(const char *name, u32 type, u32 mask)
{
    // 1. 分配 larval
    larval = crypto_larval_alloc(name, type, mask);
    
    // 2. 加入全局链表
    down_write(&crypto_alg_sem);
    alg = __crypto_alg_lookup(name, type, mask);
    if (!alg) {
        alg = &larval->alg;
        list_add(&alg->cra_list, &crypto_alg_list);
    }
    up_write(&crypto_alg_sem);
    
    // 3. 如果找到的是 larval，等待成熟
    if (alg != &larval->alg) {
        kfree(larval);
        if (crypto_is_larval(alg))
            alg = crypto_larval_wait(alg, type, mask);
    }
    return alg;
}
```

### 1.4 crypto_tfm (Transform) 生命周期

`crypto_tfm` 是加密操作的句柄/上下文:

```c
// api.c:408-437 - TFM 分配
struct crypto_tfm *__crypto_alloc_tfmgfp(struct crypto_alg *alg, u32 type,
                                        u32 mask, gfp_t gfp)
{
    // 1. 计算需要的内存大小
    tfm_size = sizeof(*tfm) + crypto_ctxsize(alg, type, mask);
    tfm = kzalloc(tfm_size, gfp);
    
    // 2. 初始化
    tfm->__crt_alg = alg;
    refcount_set(&tfm->refcnt, 1);
    
    // 3. 调用算法的 cra_init
    if (!tfm->exit && alg->cra_init && (err = alg->cra_init(tfm)))
        goto cra_init_failed;
        
    return tfm;
}
```

---

## 2. skcipher (对称密匙密码)

### 2.1 struct skcipher_alg 数据结构

`skcipher_alg` 定义于 `/Users/sphinx/github/linux/include/crypto/skcipher.h:151`:

```c
struct skcipher_alg {
    // 核心操作函数
    int (*setkey)(struct crypto_skcipher *tfm, const u8 *key,
                  unsigned int keylen);
    int (*encrypt)(struct skcipher_request *req);
    int (*decrypt)(struct skcipher_request *req);
    
    // 状态导入/导出 (用于增量计算)
    int (*export)(struct skcipher_request *req, void *out);
    int (*import)(struct skcipher_request *req, const void *in);
    
    // 生命周期钩子
    int (*init)(struct crypto_skcipher *tfm);
    void (*exit)(struct crypto_skcipher *tfm);
    
    unsigned int walksize;  // 步进大小 (用于并行处理)
    
    union {
        struct SKCIPHER_ALG_COMMON;
        struct skcipher_alg_common co;
    };
};
```

### 2.2 crypto_skcipher_setkey() 流程分析

源码位于 `/Users/sphinx/github/linux/crypto/skcipher.c:398-433`:

```c
int crypto_skcipher_setkey(struct crypto_skcipher *tfm, const u8 *key,
                           unsigned int keylen)
{
    struct skcipher_alg *cipher = crypto_skcipher_alg(tfm);
    unsigned long alignmask = crypto_skcipher_alignmask(tfm);
    int err;
    
    // 处理非标准类型 (lskcipher) 的情况
    if (cipher->co.base.cra_type != &crypto_skcipher_type) {
        struct crypto_lskcipher **ctx = crypto_skcipher_ctx(tfm);
        crypto_lskcipher_clear_flags(*ctx, CRYPTO_TFM_REQ_MASK);
        crypto_lskcipher_set_flags(*ctx,
                     crypto_skcipher_get_flags(tfm) & CRYPTO_TFM_REQ_MASK);
        err = crypto_lskcipher_setkey(*ctx, key, keylen);
        goto out;
    }
    
    // 密钥长度验证
    if (keylen < cipher->min_keysize || keylen > cipher->max_keysize)
        return -EINVAL;
    
    // 处理非对齐密钥
    if ((unsigned long)key & alignmask)
        err = skcipher_setkey_unaligned(tfm, key, keylen);
    else
        err = cipher->setkey(tfm, key, keylen);
    
out:
    if (unlikely(err)) {
        skcipher_set_needkey(tfm);  // 设置需要密钥标志
        return err;
    }
    
    crypto_skcipher_clear_flags(tfm, CRYPTO_TFM_NEED_KEY);
    return 0;
}
```

### 2.3 skcipher 加密/解密流程

```c
// skcipher.c:435-446 - 加密
int crypto_skcipher_encrypt(struct skcipher_request *req)
{
    struct crypto_skcipher *tfm = crypto_skcipher_reqtfm(req);
    struct skcipher_alg *alg = crypto_skcipher_alg(tfm);
    
    if (crypto_skcipher_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;
    
    return alg->encrypt(req);
}

// skcipher.c:448-459 - 解密
int crypto_skcipher_decrypt(struct skcipher_request *req)
{
    struct crypto_skcipher *tfm = crypto_skcipher_reqtfm(req);
    struct skcipher_alg *alg = crypto_skcipher_alg(tfm);
    
    if (crypto_skcipher_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;
    
    return alg->decrypt(req);
}
```

### 2.4 Scatter-Gather Walk 机制

`skcipher_walk` 是处理分散-聚集列表的核心机制:

```c
// skcipher.c:71-141 - skcipher_walk_done
int skcipher_walk_done(struct skcipher_walk *walk, int res)
{
    unsigned int n = walk->nbytes;  // 本次处理字节数
    
    if (!n)
        goto finish;
    
    if (likely(res >= 0)) {
        n -= res;  // 减去未处理的字节
        total = walk->total - n;
    }
    
    // 根据标志处理不同的 walk 模式
    if (likely(!(walk->flags & (SKCIPHER_WALK_SLOW |
                                SKCIPHER_WALK_COPY |
                                SKCIPHER_WALK_DIFF)))) {
        scatterwalk_advance(&walk->in, n);
    } else if (walk->flags & SKCIPHER_WALK_DIFF) {
        scatterwalk_done_src(&walk->in, n);
    } else if (walk->flags & SKCIPHER_WALK_COPY) {
        scatterwalk_advance(&walk->in, n);
        scatterwalk_map(&walk->out);
        memcpy(walk->out.addr, walk->page, n);
    } else { /* SKCIPHER_WALK_SLOW */
        if (res > 0)
            res = -EINVAL;
        else
            memcpy_to_scatterwalk(&walk->out, walk->out.addr, n);
        goto dst_done;
    }
    
    scatterwalk_done_dst(&walk->out, n);
    
dst_done:
    if (res > 0)
        res = 0;
    
    walk->total = total;
    walk->nbytes = 0;
    
    if (total) {
        if (walk->flags & SKCIPHER_WALK_SLEEP)
            cond_resched();
        return skcipher_walk_next(walk);
    }
    
finish:
    if (!((unsigned long)walk->buffer | (unsigned long)walk->page))
        goto out;
    
    if (walk->iv != walk->oiv)
        memcpy(walk->oiv, walk->iv, walk->ivsize);
    if (walk->buffer != walk->page)
        kfree(walk->buffer);
    if (walk->page)
        free_page((unsigned long)walk->page);
    
out:
    return res;
}
```

---

## 3. aead (认证加密)

### 3.1 struct aead_alg 数据结构

定义于 `/Users/sphinx/github/linux/include/crypto/aead.h:139`:

```c
struct aead_alg {
    // 核心操作
    int (*setkey)(struct crypto_aead *tfm, const u8 *key,
                  unsigned int keylen);
    int (*setauthsize)(struct crypto_aead *tfm, unsigned int authsize);
    int (*encrypt)(struct aead_request *req);
    int (*decrypt)(struct aead_request *req);
    
    // 生命周期
    int (*init)(struct crypto_aead *tfm);
    void (*exit)(struct crypto_aead *tfm);
    
    unsigned int ivsize;         // IV 大小
    unsigned int maxauthsize;    // 最大认证标签大小
    unsigned int chunksize;      // 块处理大小
    
    struct crypto_alg base;      // 基类
};
```

### 3.2 aead_request 结构

```c
// aead.h:90-102
struct aead_request {
    struct crypto_async_request base;
    
    unsigned int assoclen;    // 关联数据长度
    unsigned int cryptlen;    // 加密数据长度
    
    u8 *iv;                   // 初始化向量
    
    struct scatterlist *src;  // 源数据
    struct scatterlist *dst;  // 目标数据
    
    void *__ctx[] CRYPTO_MINALIGN_ATTR;  // 私有上下文
};
```

### 3.3 crypto_aead_setkey() 流程

源码位于 `/Users/sphinx/github/linux/crypto/aead.c:44-62`:

```c
int crypto_aead_setkey(struct crypto_aead *tfm,
                      const u8 *key, unsigned int keylen)
{
    unsigned long alignmask = crypto_aead_alignmask(tfm);
    int err;
    
    if ((unsigned long)key & alignmask)
        err = setkey_unaligned(tfm, key, keylen);
    else
        err = crypto_aead_alg(tfm)->setkey(tfm, key, keylen);
    
    if (unlikely(err)) {
        crypto_aead_set_flags(tfm, CRYPTO_TFM_NEED_KEY);
        return err;
    }
    
    crypto_aead_clear_flags(tfm, CRYPTO_TFM_NEED_KEY);
    return 0;
}
```

---

## 4. ahash/shash (异步/同步哈希)

### 4.1 struct ahash_alg 数据结构

定义于 `/Users/sphinx/github/linux/include/crypto/hash.h:154`:

```c
struct ahash_alg {
    // 异步哈希操作
    int (*init)(struct ahash_request *req);
    int (*update)(struct ahash_request *req);
    int (*final)(struct ahash_request *req);
    int (*finup)(struct ahash_request *req);
    int (*digest)(struct ahash_request *req);
    
    // 状态导入/导出
    int (*export)(struct ahash_request *req, void *out);
    int (*import)(struct ahash_request *req, const void *in);
    
    // 密钥操作 (HMAC 等需要)
    int (*setkey)(struct crypto_ahash *tfm, const u8 *key,
                  unsigned int keylen);
    
    // 生命周期
    int (*init_tfm)(struct crypto_ahash *tfm);
    void (*exit_tfm)(struct crypto_ahash *tfm);
    
    struct hash_alg_common halg;
};
```

### 4.2 struct shash_alg (同步哈希)

定义于 `/Users/sphinx/github/linux/include/crypto/hash.h:249`:

```c
struct shash_alg {
    // 同步哈希操作 (使用 shash_desc)
    int (*init)(struct shash_desc *desc);
    int (*update)(struct shash_desc *desc, const u8 *data,
                  unsigned int len);
    int (*final)(struct shash_desc *desc, u8 *out);
    int (*finup)(struct shash_desc *desc, const u8 *data,
                 unsigned int len, u8 *out);
    int (*digest)(struct shash_desc *desc, const u8 *data,
                  unsigned int len, u8 *out);
    
    // 状态导入/导出
    int (*export)(struct shash_desc *desc, void *out);
    int (*import)(struct shash_desc *desc, const void *in);
    
    // 密钥操作
    int (*setkey)(struct crypto_shash *tfm, const u8 *key,
                  unsigned int keylen);
    
    unsigned int descsize;  // 描述符大小
    
    union {
        struct HASH_ALG_COMMON;
        struct hash_alg_common halg;
    };
};
```

### 4.3 shash_desc 结构

```c
// hash.h:173-176
struct shash_desc {
    struct crypto_shash *tfm;  // 变换句柄
    void *__ctx[] __aligned(ARCH_SLAB_MINALIGN);  // 算法特定上下文
};
```

### 4.4 crypto_shash_digest() 流程

源码位于 `/Users/sphinx/github/linux/crypto/shash.c:183-194`:

```c
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

## 5. cryptd (异步加密封装)

### 5.1 cryptd 架构概述

`cryptd` 是一个软件异步加密守护进程，将同步加密算法封装为异步接口。源码位于 `/Users/sphinx/github/linux/crypto/cryptd.c`。

**核心数据结构:**

```c
// cryptd.c:36-48 - CPU 队列
struct cryptd_cpu_queue {
    local_lock_t bh_lock;
    struct crypto_queue queue;
    struct work_struct work;
};

struct cryptd_queue {
    struct cryptd_cpu_queue __percpu *cpu_queue;
};

// cryptd.c:70-73 - skcipher 上下文
struct cryptd_skcipher_ctx {
    refcount_t refcnt;
    struct crypto_skcipher *child;  // 封装的底层算法
};

// cryptd.c:75-77 - skcipher 请求上下文
struct cryptd_skcipher_request_ctx {
    struct skcipher_request req;  // 子请求
};
```

### 5.2 cryptd 加密流程 (skcipher)

```c
// cryptd.c:294-304 - 异步加密入口
static void cryptd_skcipher_encrypt(void *data, int err)
{
    struct skcipher_request *req = data;
    struct skcipher_request *subreq;
    
    subreq = cryptd_skcipher_prepare(req, err);
    if (likely(subreq))
        err = crypto_skcipher_encrypt(subreq);
    
    cryptd_skcipher_complete(req, err, cryptd_skcipher_encrypt);
}
```

### 5.3 工作队列处理

```c
// cryptd.c:166-191 - 工作队列处理函数
static void cryptd_queue_worker(struct work_struct *work)
{
    struct cryptd_cpu_queue *cpu_queue;
    struct crypto_async_request *req, *backlog;
    
    cpu_queue = container_of(work, struct cryptd_cpu_queue, work);
    
    local_bh_disable();
    __local_lock_nested_bh(&cpu_queue->bh_lock);
    backlog = crypto_get_backlog(&cpu_queue->queue);
    req = crypto_dequeue_request(&cpu_queue->queue);
    __local_unlock_nested_bh(&cpu_queue->bh_lock);
    local_bh_enable();
    
    if (!req)
        return;
    
    if (backlog)
        crypto_request_complete(backlog, -EINPROGRESS);
    
    crypto_request_complete(req, 0);
    
    if (cpu_queue->queue.qlen)
        queue_work(cryptd_wq, &cpu_queue->work);
}
```

---

## 6. Jitter RNG (抖动熵源随机数生成器)

### 6.1 Jitter Entropy 核心结构

源码位于 `/Users/sphinx/github/linux/crypto/jitterentropy.c`:

```c
// jitterentropy.c:64-106 - 熵收集器结构
struct rand_data {
    // SHA3-256 用作条件处理
    #define DATA_SIZE_BITS 256
    
    void *hash_state;           // 哈希状态 (敏感)
    __u64 prev_time;            // 上次时间戳 (敏感)
    __u64 last_delta;           // 上次增量 (敏感)
    __s64 last_delta2;          // 增量增量 (敏感)
    
    unsigned int flags;          // 初始化标志
    unsigned int osr;            // 过采样率
    
    // 内存访问相关
    unsigned char *mem;          // 内存块
    unsigned int memlocation;    // 当前访问位置
    unsigned int memblocks;      // 内存块数量
    unsigned int memblocksize;   // 单块大小
    unsigned int memaccessloops; // 每次访问循环数
    
    // RCT (重复计数测试)
    unsigned int rct_count;      // 粘滞值计数
    
    // APT (自适应比例测试)
    unsigned int apt_cutoff;
    #define JENT_APT_WINDOW_SIZE 512
    unsigned int apt_observations;
    unsigned int apt_count;
    unsigned int apt_base;
    unsigned int apt_base_set:1;
    unsigned int health_failure;
};
```

### 6.2 RCT (重复计数测试) 实现

```c
// jitterentropy.c:260-298 - RCT 插入
static void jent_rct_insert(struct rand_data *ec, int stuck)
{
    if (stuck) {
        ec->rct_count++;
        
        // cutoff = 30*osr (alpha=2^-30) 或 60*osr (alpha=2^-60)
        if ((unsigned int)ec->rct_count >= (60 * ec->osr)) {
            ec->rct_count = -1;
            ec->health_failure |= JENT_RCT_FAILURE_PERMANENT;
        } else if ((unsigned int)ec->rct_count >= (30 * ec->osr)) {
            ec->rct_count = -1;
            ec->health_failure |= JENT_RCT_FAILURE;
        }
    } else {
        ec->rct_count = 0;
    }
}

// jitterentropy.c:322-346 - 粘滞检测
static int jent_stuck(struct rand_data *ec, __u64 current_delta)
{
    __u64 delta2 = jent_delta(ec->last_delta, current_delta);
    __u64 delta3 = jent_delta(ec->last_delta2, delta2);
    
    ec->last_delta = current_delta;
    ec->last_delta2 = delta2;
    
    jent_apt_insert(ec, current_delta);
    
    if (!current_delta || !delta2 || !delta3) {
        jent_rct_insert(ec, 1);
        return 1;
    }
    
    jent_rct_insert(ec, 0);
    return 0;
}
```

### 6.3 熵采集循环

```c
// jitterentropy.c:520-549 - 测量抖动
static int jent_measure_jitter(struct rand_data *ec, __u64 *ret_current_delta)
{
    __u64 time = 0;
    __u64 current_delta = 0;
    int stuck;
    
    jent_memaccess(ec, 0);
    jent_get_nstime(&time);
    current_delta = jent_delta(ec->prev_time, time);
    ec->prev_time = time;
    
    stuck = jent_stuck(ec, current_delta);
    
    if (jent_condition_data(ec, current_delta, stuck))
        stuck = 1;
    
    if (ret_current_delta)
        *ret_current_delta = current_delta;
    
    return stuck;
}

// jitterentropy.c:557-579 - 生成熵
static void jent_gen_entropy(struct rand_data *ec)
{
    unsigned int k = 0, safety_factor = 0;
    
    if (fips_enabled)
        safety_factor = JENT_ENTROPY_SAFETY_FACTOR;
    
    jent_measure_jitter(ec, NULL);
    
    while (!jent_health_failure(ec)) {
        if (jent_measure_jitter(ec, NULL))
            continue;
        
        if (++k >= ((DATA_SIZE_BITS + safety_factor) * ec->osr))
            break;
    }
}
```

### 6.4 内存访问噪声源

```c
// jitterentropy.c:466-502 - 内存访问
static void jent_memaccess(struct rand_data *ec, __u64 loop_cnt)
{
    unsigned int wrap = 0;
    __u64 i = 0;
    
    if (NULL == ec || NULL == ec->mem)
        return;
    
    wrap = ec->memblocksize * ec->memblocks;
    
    for (i = 0; i < (ec->memaccessloops + acc_loop_cnt); i++) {
        unsigned char *tmpval = ec->mem + ec->memlocation;
        
        *tmpval = (*tmpval + 1) & 0xff;
        
        ec->memlocation = ec->memlocation + ec->memblocksize - 1;
        ec->memlocation = ec->memlocation % wrap;
    }
}
```

---

## 7. 知识点关联表

| 模块 | 核心结构体 | 注册函数 | 核心操作函数 | 源码位置 |
|------|-----------|---------|-------------|---------|
| **Crypto Core** | `struct crypto_alg` | `crypto_register_alg()` | N/A (基础设施) | `crypto/api.c` |
| | `struct crypto_tfm` | N/A | `crypto_alloc_tfm()` | `crypto/api.c:408` |
| | `struct crypto_larval` | N/A | `crypto_larval_add()` | `crypto/api.c:126` |
| **skcipher** | `struct skcipher_alg` | `crypto_register_skcipher()` | `crypto_skcipher_setkey()` | `crypto/skcipher.c:718` |
| | `struct skcipher_request` | N/A | `crypto_skcipher_encrypt/decrypt()` | `crypto/skcipher.c:435/448` |
| | `struct skcipher_walk` | N/A | `skcipher_walk_done()` | `crypto/skcipher.c:71` |
| **aead** | `struct aead_alg` | `crypto_register_aead()` | `crypto_aead_setkey()` | `crypto/aead.c:250` |
| | `struct aead_request` | N/A | `crypto_aead_encrypt/decrypt()` | `crypto/aead.c:84/95` |
| **ahash** | `struct ahash_alg` | `crypto_register_ahash()` | `crypto_ahash_setkey()` | `crypto/ahash.c:997` |
| | `struct ahash_request` | N/A | `crypto_ahash_digest()` | `crypto/ahash.c:570` |
| **shash** | `struct shash_alg` | `crypto_register_shash()` | `crypto_shash_digest()` | `crypto/shash.c:519` |
| | `struct shash_desc` | N/A | `shash_ahash_digest()` | `crypto/ahash.c:205` |
| **cryptd** | `struct cryptd_queue` | `cryptd_init()` | `cryptd_enqueue_request()` | `crypto/cryptd.c:132` |
| | `struct cryptd_skcipher_ctx` | N/A | `cryptd_skcipher_encrypt()` | `crypto/cryptd.c:294` |
| **Jitter RNG** | `struct rand_data` | `jent_entropy_init()` | `jent_measure_jitter()` | `crypto/jitterentropy.c:520` |
| | N/A | N/A | `jent_rct_insert()` | `crypto/jitterentropy.c:266` |
| **af_alg** | `struct alg_sock` | `af_alg_register_type()` | `af_alg_sendmsg()` | `crypto/af_alg.c:62` |

### 关键调用关系图

```
应用程序
    |
    v
[AF_ALG] <-- 用户空间接口 (socket)
    |
    v
[Crypto API] <-- crypto_alloc_*() / crypto_register_*()
    |
    +---> [skcipher] ----> [cipher] (ECB, CBC, CTR, XTS...)
    |
    +---> [aead] ----> [gcm, ccm, chacha20poly1305...]
    |
    +---> [ahash/shash] ----> [sha*, md5, blake2*, sm3...]
    |
    v
[Cryptd] <-- 异步软件封装 (workqueue)
    |
    v
[Hardware] <-- HWRNG, crypto hardware drivers
```

---

## 总结

Linux Kernel Crypto 子系统是一个精心设计的分层架构:

1. **Crypto Core** 提供了算法注册、查找、生命周期管理的核心框架，通过 `crypto_alg` 基类和多态类型系统支持多种加密算法类型。

2. **skcipher** 层处理对称加密，通过 scatter-gather walk 机制高效处理跨页面边界的数据，并支持状态导出/导入实现增量加密。

3. **aead** 层在对称加密基础上增加了认证功能，通过 `authsize` 参数控制认证标签大小，`-EBADMSG` 错误表示认证失败。

4. **ahash/shash** 提供同步和异步哈希接口，`shash` 使用 `shash_desc` 直接持有状态，`ahash` 可委托给 `shash` 实现或使用原生异步实现。

5. **cryptd** 将同步算法异步化，通过 per-CPU 工作队列和 `crypto_queue` 实现请求调度，利用 BH 锁保证在软中断上下文的线程安全。

6. **Jitter RNG** 是基于 CPU 抖动的高质量熵源，通过 RCT 和 APT 两种健康测试确保输出质量，符合 NIST SP 800-90B 标准。

---

**文档版本**: R1  
**分析源码版本**: Linux Kernel (latest)  
**生成时间**: 2026-04-27
