# Linux 内核 Crypto 子系统基础设施分析

## 目录
1. [概述](#概述)
2. [algapi 基础设施](#1-algapi-基础设施)
3. [cryptd 异步加密守护进程](#2-cryptd-异步加密守护进程)
4. [散列函数基础设施](#3-散列函数基础设施)
5. [随机数生成](#4-随机数生成)
6. [压缩算法](#5-压缩算法)
7. [架构图](#架构图)

---

## 概述

Linux 内核 Crypto 子系统为内核和用户空间提供统一的密码学算法接口。核心设计采用以下层次结构：

```
用户空间/内核模块
       ↓
  Crypto API (include/crypto/*.h)
       ↓
  算法类型层 (skcipher, ahash, shash, aead, scompress, etc.)
       ↓
  算法实例层 (具体算法的实现)
       ↓
  基础设施层 (algapi.c, api.c)
       ↓
  硬件/驱动层
```

**关键源码位置：**
- `/Users/sphinx/github/linux/crypto/algapi.c` - 算法注册/查找基础设施
- `/Users/sphinx/github/linux/crypto/api.c` - 核心 Crypto API 实现
- `/Users/sphinx/github/linux/crypto/cryptd.c` - 异步加密守护进程
- `/Users/sphinx/github/linux/crypto/jitterentropy.c` - 抖动熵随机数生成器
- `/Users/sphinx/github/linux/include/crypto/` - 头文件目录

---

## 1. algapi 基础设施

### 1.1 struct crypto_larval (算法幼虫状态)

**位置：** `/Users/sphinx/github/linux/crypto/internal.h` 第 28-34 行

```c
struct crypto_larval {
    struct crypto_alg alg;           // 基础算法结构
    struct crypto_alg *adult;        // 成年算法(通过自检后)
    struct completion completion;     // 等待自检完成的completion
    u32 mask;                        // 算法掩码
    bool test_started;               // 自检是否已开始
};
```

**设计意图：**
- `crypto_larval` 是算法生命周期中的"幼虫"阶段
- 新注册的算法首先以 larval 形式存在，等待自检完成
- 自检通过后，`adult` 指向真实算法实例
- 使用 `completion` 机制同步等待自检结果

### 1.2 算法标志位 (crypto_flags)

**位置：** `/Users/sphinx/github/linux/include/linux/crypto.h` 第 24-141 行

```c
// 算法类型掩码
#define CRYPTO_ALG_TYPE_MASK        0x0000000f
#define CRYPTO_ALG_TYPE_CIPHER      0x00000001
#define CRYPTO_ALG_TYPE_AEAD        0x00000003
#define CRYPTO_ALG_TYPE_LSKCIPHER    0x00000004
#define CRYPTO_ALG_TYPE_SKCIPHER    0x00000005
#define CRYPTO_ALG_TYPE_AHASH       0x0000000f
#define CRYPTO_ALG_TYPE_SHASH       0x0000000e
#define CRYPTO_ALG_TYPE_ACOMPRESS   0x0000000a
#define CRYPTO_ALG_TYPE_SCOMPRESS   0x0000000b
#define CRYPTO_ALG_TYPE_RNG         0x0000000c

// 算法状态标志
#define CRYPTO_ALG_LARVAL           0x00000010  // 幼虫状态
#define CRYPTO_ALG_DEAD             0x00000020  // 已销毁
#define CRYPTO_ALG_DYING            0x00000040  // 正在销毁
#define CRYPTO_ALG_ASYNC            0x00000080  // 异步算法
#define CRYPTO_ALG_TESTED           0x00000400  // 已通过自检
#define CRYPTO_ALG_INTERNAL         0x00002000  // 内核内部算法
#define CRYPTO_ALG_FIPS_INTERNAL    0x00020000  // FIPS模式内部算法
```

### 1.3 crypto_alg_lookup() - 算法查找

**位置：** `/Users/sphinx/github/linux/crypto/api.c` 第 253-288 行

```c
static struct crypto_alg *crypto_alg_lookup(const char *name, u32 type,
                                            u32 mask)
{
    const u32 fips = CRYPTO_ALG_FIPS_INTERNAL;
    struct crypto_alg *alg;
    u32 test = 0;

    // 如果请求者和掩码都未标记为TESTED，则自动标记为需要测试
    if (!((type | mask) & CRYPTO_ALG_TESTED))
        test |= CRYPTO_ALG_TESTED;

    down_read(&crypto_alg_sem);
    alg = __crypto_alg_lookup(name, (type | test) & ~fips,
                              (mask | test) & ~fips);
    if (alg) {
        // FIPS模式检查
        if (((type | mask) ^ fips) & fips)
            mask |= fips;
        mask &= fips;

        // 检查算法是否在FIPS模式下被禁止
        if (!crypto_is_larval(alg) &&
            ((type ^ alg->cra_flags) & mask)) {
            crypto_mod_put(alg);
            alg = ERR_PTR(-ENOENT);
        }
    } else if (test) {
        // 查找未测试的算法（用于回退）
        alg = __crypto_alg_lookup(name, type, mask);
        if (alg && !crypto_is_larval(alg)) {
            crypto_mod_put(alg);
            alg = ERR_PTR(-ELIBBAD);
        }
    }
    up_read(&crypto_alg_sem);

    return alg;
}
```

**查找流程：**
1. 获取 `crypto_alg_sem` 读锁
2. 调用 `__crypto_alg_lookup()` 进行精确匹配和模糊匹配
3. 优先精确匹配 (`cra_driver_name`)，其次模糊匹配 (`cra_name`)
4. 按优先级 (`cra_priority`) 排序，返回最高优先级匹配
5. FIPS 模式检查

### 1.4 __crypto_alg_lookup() - 底层查找

**位置：** `/Users/sphinx/github/linux/crypto/api.c` 第 58-92 行

```c
static struct crypto_alg *__crypto_alg_lookup(const char *name, u32 type,
                                              u32 mask)
    __must_hold_shared(&crypto_alg_sem)
{
    struct crypto_alg *q, *alg = NULL;
    int best = -2;

    list_for_each_entry(q, &crypto_alg_list, cra_list) {
        int exact, fuzzy;

        // 跳过正在消亡的算法
        if (crypto_is_moribund(q))
            continue;

        // 类型掩码检查
        if ((q->cra_flags ^ type) & mask)
            continue;

        // 精确匹配 vs 模糊匹配
        exact = !strcmp(q->cra_driver_name, name);
        fuzzy = !strcmp(q->cra_name, name);
        if (!exact && !(fuzzy && q->cra_priority > best))
            continue;

        if (unlikely(!crypto_mod_get(q)))
            continue;

        best = q->cra_priority;
        if (alg)
            crypto_mod_put(alg);
        alg = q;

        if (exact)
            break;
    }

    return alg;
}
```

### 1.5 crypto_remove_final() - 算法移除

**位置：** `/Users/sphinx/github/linux/crypto/algapi.c` 第 410-420 行

```c
void crypto_remove_final(struct list_head *list)
{
    struct crypto_alg *alg;
    struct crypto_alg *n;

    list_for_each_entry_safe(alg, n, list, cra_list) {
        list_del_init(&alg->cra_list);     // 从crypto_alg_list移除
        crypto_alg_put(alg);               // 减少引用计数，释放
    }
}
EXPORT_SYMBOL_GPL(crypto_remove_final);
```

**调用链：**
```
crypto_unregister_alg()
    → crypto_remove_alg()      // 标记为DEAD，移除spawns
    → crypto_remove_final()    // 释放算法对象
```

### 1.6 crypto_remove_spawns() - 递归移除依赖算法

**位置：** `/Users/sphinx/github/linux/crypto/algapi.c` 第 165-242 行

该函数执行深度优先遍历，移除所有依赖指定算法的"spawn"（派生算法实例）。

**关键数据结构：**
```c
struct crypto_spawn {
    struct list_head list;
    struct crypto_alg *alg;          // 指向父算法
    union {
        struct crypto_instance *inst;    // 注册后的回指
        struct crypto_spawn *next;      // 注册前的链表
    };
    const struct crypto_type *frontend;
    u32 mask;
    bool dead;                        // 是否标记为死亡
    bool registered;                  // 是否已注册
};
```

### 1.7 算法注册流程

**位置：** `/Users/sphinx/github/linux/crypto/algapi.c` 第 431-476 行

```c
int crypto_register_alg(struct crypto_alg *alg)
{
    struct crypto_larval *larval;
    bool test_started = false;
    LIST_HEAD(algs_to_put);
    int err;

    alg->cra_flags &= ~CRYPTO_ALG_DEAD;
    err = crypto_check_alg(alg);         // 验证算法参数
    if (err)
        return err;

    down_write(&crypto_alg_sem);
    larval = __crypto_register_alg(alg, &algs_to_put);
    if (!IS_ERR_OR_NULL(larval)) {
        test_started = crypto_boot_test_finished();
        larval->test_started = test_started;
    }
    up_write(&crypto_alg_sem);

    if (IS_ERR(larval)) {
        crypto_alg_put(alg);
        return PTR_ERR(larval);
    }

    // 启动自检或直接完成注册
    if (test_started)
        crypto_schedule_test(larval);
    else
        crypto_remove_final(&algs_to_put);

    return 0;
}
```

---

## 2. cryptd 异步加密守护进程

### 2.1 概述

`cryptd` 是一个软件异步加密守护进程，用于：
- 将同步算法封装为异步接口
- 在进程上下文中处理加密操作（允许睡眠）
- 减轻硬件加密引擎压力

### 2.2 核心数据结构

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c`

```c
// cryptd队列 - 每CPU队列
struct cryptd_queue {
    struct cryptd_cpu_queue __percpu *cpu_queue;
};

// 每CPU加密队列
struct cryptd_cpu_queue {
    local_lock_t bh_lock;           // 禁用软中断的锁
    struct crypto_queue queue;      // 底层crypto队列
    struct work_struct work;       // 工作队列项
};
```

### 2.3 struct cryptd_ablkcipher

cryptd 包装的结构：
```c
// skcipher包装
struct cryptd_skcipher_ctx {
    refcount_t refcnt;
    struct crypto_skcipher *child;   // 底层同步算法
};

// 请求上下文
struct cryptd_skcipher_request_ctx {
    struct skcipher_request req;      // 子请求
};
```

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c` 第 70-77 行

### 2.4 cryptd_alloc_ablkcipher()

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c` 第 955-979 行

```c
struct cryptd_skcipher *cryptd_alloc_skcipher(const char *alg_name,
                                              u32 type, u32 mask)
{
    char cryptd_alg_name[CRYPTO_MAX_ALG_NAME];
    struct cryptd_skcipher_ctx *ctx;
    struct crypto_skcipher *tfm;

    // 构建cryptd算法名称: "cryptd(原算法名)"
    if (snprintf(cryptd_alg_name, CRYPTO_MAX_ALG_NAME,
                 "cryptd(%s)", alg_name) >= CRYPTO_MAX_ALG_NAME)
        return ERR_PTR(-EINVAL);

    tfm = crypto_alloc_skcipher(cryptd_alg_name, type, mask);
    if (IS_ERR(tfm))
        return ERR_CAST(tfm);

    // 验证确实是cryptd创建的
    if (tfm->base.__crt_alg->cra_module != THIS_MODULE) {
        crypto_free_skcipher(tfm);
        return ERR_PTR(-EINVAL);
    }

    ctx = crypto_skcipher_ctx(tfm);
    refcount_set(&ctx->refcnt, 1);

    return container_of(tfm, struct cryptd_skcipher, base);
}
```

### 2.5 cryptd_enqueue_job() - 作业入队

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c` 第 132-161 行

```c
static int cryptd_enqueue_request(struct cryptd_queue *queue,
                                  struct crypto_async_request *request)
{
    int err;
    struct cryptd_cpu_queue *cpu_queue;
    refcount_t *refcnt;

    local_bh_disable();                           // 禁用软中断
    local_lock_nested_bh(&queue->cpu_queue->bh_lock);
    cpu_queue = this_cpu_ptr(queue->cpu_queue);
    err = crypto_enqueue_request(&cpu_queue->queue, request);

    refcnt = crypto_tfm_ctx(request->tfm);

    if (err == -ENOSPC)
        goto out;

    // 调度工作队列处理
    queue_work_on(smp_processor_id(), cryptd_wq, &cpu_queue->work);

    if (!refcount_read(refcnt))
        goto out;

    refcount_inc(refcnt);

out:
    local_unlock_nested_bh(&queue->cpu_queue->bh_lock);
    local_bh_enable();

    return err;
}
```

### 2.6 cryptd队列工作线程

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c` 第 166-191 行

```c
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

    // 处理积压请求
    if (backlog)
        crypto_request_complete(backlog, -EINPROGRESS);
    // 执行实际加密操作
    crypto_request_complete(req, 0);

    // 继续处理更多请求
    if (cpu_queue->queue.qlen)
        queue_work(cryptd_wq, &cpu_queue->work);
}
```

### 2.7 cryptd初始化

**位置：** `/Users/sphinx/github/linux/crypto/cryptd.c` 第 1114-1139 行

```c
static int __init cryptd_init(void)
{
    int err;

    // 创建工作队列: WQ_MEM_RECLAIM - 内存回收时可睡眠
    // WQ_CPU_INTENSIVE - CPU密集型
    // WQ_PERCPU - 每CPU工作队列
    cryptd_wq = alloc_workqueue("cryptd",
                WQ_MEM_RECLAIM | WQ_CPU_INTENSIVE | WQ_PERCPU, 1);
    if (!cryptd_wq)
        return -ENOMEM;

    err = cryptd_init_queue(&queue, cryptd_max_cpu_qlen);
    if (err)
        goto err_destroy_wq;

    err = crypto_register_template(&cryptd_tmpl);
    if (err)
        goto err_fini_queue;

    return 0;

err_fini_queue:
    cryptd_fini_queue(&queue);
err_destroy_wq:
    destroy_workqueue(cryptd_wq);
    return err;
}
```

---

## 3. 散列函数基础设施

### 3.1 struct shash_desc - 同步哈希描述符

**位置：** `/Users/sphinx/github/linux/include/crypto/hash.h` 第 173-176 行

```c
struct shash_desc {
    struct crypto_shash *tfm;       // 哈希转换实例
    void *__ctx[] __aligned(ARCH_SLAB_MINALIGN);  // 算法特定上下文
};
```

**用途：**
- `shash_desc` 是同步哈希操作的核心描述符
- `__ctx` 包含算法实现所需的内部状态（如MD5的链接变量）
- 上下文大小由 `crypto_shash_descsize()` 返回

### 3.2 struct crypto_shash

**位置：** `/Users/sphinx/github/linux/include/crypto/hash.h` 第 284-286 行

```c
struct crypto_shash {
    struct crypto_tfm base;          // 基础转换结构
};
```

### 3.3 struct shash_alg - 同步哈希算法定义

**位置：** `/Users/sphinx/github/linux/include/crypto/hash.h` 第 249-274 行

```c
struct shash_alg {
    int (*init)(struct shash_desc *desc);
    int (*update)(struct shash_desc *desc, const u8 *data,
                  unsigned int len);
    int (*final)(struct shash_desc *desc, u8 *out);
    int (*finup)(struct shash_desc *desc, const u8 *data,
                 unsigned int len, u8 *out);
    int (*digest)(struct shash_desc *desc, const u8 *data,
                  unsigned int len, u8 *out);
    int (*export)(struct shash_desc *desc, void *out);
    int (*import)(struct shash_desc *desc, const void *in);
    int (*setkey)(struct crypto_shash *tfm, const u8 *key,
                  unsigned int keylen);
    int (*init_tfm)(struct crypto_shash *tfm);
    void (*exit_tfm)(struct crypto_shash *tfm);
    int (*clone_tfm)(struct crypto_shash *dst, struct crypto_shash *src);

    unsigned int descsize;           // 描述符上下文大小

    union {
        struct HASH_ALG_COMMON;
        struct hash_alg_common halg;
    };
};
```

### 3.4 shash_encrypt_digest()

`crypto_shash_digest()` 是同步一次性哈希计算函数：

**位置：** `/Users/sphinx/github/linux/crypto/shash.c` 第 183-194 行

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

**简化接口（不需要用户管理描述符）：**
```c
int crypto_shash_tfm_digest(struct crypto_shash *tfm, const u8 *data,
                            unsigned int len, u8 *out)
{
    SHASH_DESC_ON_STACK(desc, tfm);     // 栈上分配描述符

    desc->tfm = tfm;
    return crypto_shash_digest(desc, data, len, out);
}
```

### 3.5 异步哈希 (ahash)

**位置：** `/Users/sphinx/github/linux/include/crypto/hash.h` 第 58-73 行

```c
struct ahash_request {
    struct crypto_async_request base;

    unsigned int nbytes;
    union {
        struct scatterlist *src;
        const u8 *svirt;
    };
    u8 *result;

    struct scatterlist sg_head[2];
    crypto_completion_t saved_complete;
    void *saved_data;

    void *__ctx[] CRYPTO_MINALIGN_ATTR;
};
```

---

## 4. 随机数生成

### 4.1 jitterentropy - 抖动熵源

**位置：** `/Users/sphinx/github/linux/crypto/jitterentropy.c`

jitterentropy 是一种基于 CPU 指令执行时间抖动的硬件随机数生成器。

#### 4.1.1 核心数据结构

```c
// 熵收集器状态 (第64-106行)
struct rand_data {
    void *hash_state;              // SHA3-256 哈希状态作为熵池
    __u64 prev_time;               // 上次时间戳
    __u64 last_delta;               // 上次增量（用于卡住检测）
    __s64 last_delta2;             // 二次增量

    unsigned int flags;
    unsigned int osr;              // 过采样率

    unsigned char *mem;            // 内存访问位置
    unsigned int memlocation;       // 内存块内位置
    unsigned int memblocks;        // 内存块数量
    unsigned int memblocksize;     // 单块大小
    unsigned int memaccessloops;   // 每次随机位生成的内存访问次数

    // 重复计数测试
    unsigned int rct_count;

    // 自适应比例测试 (APT)
    unsigned int apt_observations;
    unsigned int apt_count;
    unsigned int apt_base;
    unsigned int health_failure;
    unsigned int apt_base_set:1;
};
```

#### 4.1.2 熵收集机制

**jent_measure_jitter()** (第520-549行):
```c
static int jent_measure_jitter(struct rand_data *ec, __u64 *ret_current_delta)
{
    __u64 time = 0;
    __u64 current_delta = 0;
    int stuck;

    // 1. 先访问内存引入变种
    jent_memaccess(ec, 0);

    // 2. 获取时间戳并计算与上次的增量
    jent_get_nstime(&time);
    current_delta = jent_delta(ec->prev_time, time);
    ec->prev_time = time;

    // 3. 卡住检测
    stuck = jent_stuck(ec, current_delta);

    // 4. 将时间增量注入熵池
    if (jent_condition_data(ec, current_delta, stuck))
        stuck = 1;

    if (ret_current_delta)
        *ret_current_delta = current_delta;

    return stuck;
}
```

#### 4.1.3 健康检测

**卡住检测 (RCT + APT)** (第322-346行):
```c
static int jent_stuck(struct rand_data *ec, __u64 current_delta)
{
    __u64 delta2 = jent_delta(ec->last_delta, current_delta);
    __u64 delta3 = jent_delta(ec->last_delta2, delta2);

    ec->last_delta = current_delta;
    ec->last_delta2 = delta2;

    // APT测试
    jent_apt_insert(ec, current_delta);

    if (!current_delta || !delta2 || !delta3) {
        // RCT测试 - 连续相同值
        jent_rct_insert(ec, 1);
        return 1;
    }

    jent_rct_insert(ec, 0);
    return 0;
}
```

### 4.2 get_random_bytes()

**位置：** `/Users/sphinx/github/linux/drivers/char/random.c`

```c
void get_random_bytes(void *buf, size_t len)
{
    _get_random_bytes(buf, len);
}
EXPORT_SYMBOL(get_random_bytes);
```

**架构：**
```
用户调用
    ↓
get_random_bytes()
    ↓
_get_random_bytes()
    ↓
/dev/urandom (CRNG - 快速密钥擦除RNG)
    ├── ChaCha20 流密码
    └── 每次调用后重新种子化
```

---

## 5. 压缩算法

### 5.1 压缩算法架构

Linux 内核支持两种压缩接口：
- **同步压缩 (scomp):** `crypto_scomp_*`
- **异步压缩 (acomp):** `crypto_acomp_*`

### 5.2 LZO 压缩

**位置：** `/Users/sphinx/github/linux/crypto/lzo.c`

```c
// LZO压缩上下文分配 (第12-21行)
static void *lzo_alloc_ctx(void)
{
    void *ctx;
    ctx = kvmalloc(LZO1X_MEM_COMPRESS, GFP_KERNEL);
    if (!ctx)
        return ERR_PTR(-ENOMEM);
    return ctx;
}

// 压缩函数 (第28-41行)
static int __lzo_compress(const u8 *src, unsigned int slen,
                          u8 *dst, unsigned int *dlen, void *ctx)
{
    size_t tmp_len = *dlen;
    int err;
    err = lzo1x_1_compress_safe(src, slen, dst, &tmp_len, ctx);
    if (err != LZO_E_OK)
        return -EINVAL;
    *dlen = tmp_len;
    return 0;
}

// scomp算法注册 (第72-84行)
static struct scomp_alg scomp = {
    .streams = {
        .alloc_ctx = lzo_alloc_ctx,
        .free_ctx = lzo_free_ctx,
    },
    .compress = lzo_scompress,
    .decompress = lzo_sdecompress,
    .base = {
        .cra_name = "lzo",
        .cra_driver_name = "lzo-scomp",
        .cra_module = THIS_MODULE,
    }
};
```

### 5.3 LZ4HC 压缩

**位置：** `/Users/sphinx/github/linux/crypto/lz4hc.c`

```c
// LZ4HC压缩 (第29-40行)
static int __lz4hc_compress_crypto(const u8 *src, unsigned int slen,
                                   u8 *dst, unsigned int *dlen, void *ctx)
{
    int out_len = LZ4_compress_HC(src, dst, slen,
        *dlen, LZ4HC_DEFAULT_CLEVEL, ctx);
    if (!out_len)
        return -EINVAL;
    *dlen = out_len;
    return 0;
}
```

### 5.4 Deflate (zlib) 压缩

**位置：** `/Users/sphinx/github/linux/crypto/deflate.c`

```c
// Deflate流结构 (第29-32行)
struct deflate_stream {
    struct z_stream_s stream;      // zlib流
    u8 workspace[];                // 工作区
};

// 压缩级别和窗口大小 (第25-27行)
#define DEFLATE_DEF_LEVEL      Z_DEFAULT_COMPRESSION
#define DEFLATE_DEF_WINBITS    11
#define DEFLATE_DEF_MEMLEVEL   MAX_MEM_LEVEL
```

---

## 架构图

### Crypto 子系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         用户空间/内核模块                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   crypto    │  │   crypto    │  │   crypto    │  │    AF_ALG   │    │
│  │   sysfs    │  │   netlink   │  │   chardev   │  │  (socket)  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Crypto API 层                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  crypto_alloc_*() / crypto_free_*() / crypto_register_*()       │   │
│  │  crypto_ahash_*() / crypto_shash_*() / crypto_skcipher_*()      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        算法类型层 (crypto_type)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  skcipher  │  │   ahash    │  │   shash    │  │   aead     │        │
│  │   type     │  │   type     │  │   type     │  │   type     │        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                        │
│  │ scompress  │  │ a compress │  │    rng     │                        │
│  │   type     │  │   type     │  │   type     │                        │
│  └────────────┘  └────────────┘  └────────────┘                        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      算法注册/查找基础设施                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  algapi.c / api.c                                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │crypto_alg   │  │crypto_larval│  │crypto_template│            │   │
│  │  │  _list      │  │  (幼虫)     │  │ (模板)       │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        软件实现层                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   cryptd   │  │  jitter-   │  │  deflate   │  │    lzo     │        │
│  │  (异步封装) │  │  entropy   │  │  (zlib)    │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      硬件/驱动层                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   x86     │  │   ARM     │  │   RISC-V   │  │  特定平台   │        │
│  │   AES-NI  │  │   Crypto  │  │   Crypto   │  │   驱动     │        │
│  │   SHA-NI  │  │   Extension│ │   Extension│  │            │        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 算法生命周期状态机

```
                    ┌─────────────────┐
                    │   已注册         │
                    │  (REGISTERED)   │
                    └────────┬────────┘
                             │
                             │ 发现更高优先级算法
                             ▼
                    ┌─────────────────┐
          ┌─────────│    幼虫态       │◄─────────┐
          │         │   (LARVAL)     │          │
          │         └────────┬────────┘          │
          │                  │                   │
          │                  │ 自检完成           │
          │                  ▼                   │
          │         ┌─────────────────┐          │
          │         │   已测试       │          │
          │         │   (TESTED)    │          │
          │         └────────┬────────┘          │
          │                  │                   │
          │                  │ 移除              │
          │                  ▼                   │
┌────────┴────────┐   ┌─────────────────┐          │
│     消亡中      │   │     死亡        │          │
│    (DYING)     │   │    (DEAD)      │          │
└─────────────────┘   └─────────────────┘          │
```

### cryptd 异步处理流程

```
用户请求                     cryptd队列                工作线程
   │                           │                        │
   │ cryptd_enqueue_request()  │                        │
   ├──────────────────────────►│                        │
   │                           │                        │
   │                     ┌─────┴─────┐                 │
   └──────────────────────│  队列满?  │                 │
                          └─────┬─────┘                 │
                          否    │    是                  │
   │                     ┌──────┴──────┐                 │
   │                     │ 返回-EBUSY │                 │
   │                     │ 或-EINPROGRESS                │
   │                     └────────────┘                 │
   │                                                   │
   │                    queue_work()                    │
   │◄──────────────────────────────────────────────────┤
   │                                                   │
   │                                    ┌──────────────┴──────┐
   │                                    │ crypto_dequeue_request()
   │                                    └──────────────┬──────┘
   │                                                  │
   │                                    ┌─────────────┴────────┐
   │                                    │ 调用child->encrypt()
   │                                    └─────────────┬────────┘
   │                                                  │
   │   crypto_request_complete()                       │
   ├──────────────────────────────────────────────────┤
   │                        │
   ▼                        ▼
```

### 随机数生成架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        熵源层                                       │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ 硬件RNG   │  │中断时间戳  │  │ 键盘/鼠标 │  │ CPU抖动   │       │
│  │ (HW RNG)  │  │(IRQ time) │  │  (input)  │  │(jitter)   │       │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
│        │              │              │              │              │
│        └──────────────┴──────────────┴──────────────┘              │
│                              │                                     │
└──────────────────────────────┼─────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     熵池 (输入池)                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                SHA-1 / BLAKE2 哈希池                        │    │
│  │  - 收集所有熵源的随机数据                                    │    │
│  │  - 当熵足够时提取密钥                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ 熵提取
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CRNG (ChaCha20 流密码)                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Fast Key Erasion RNG                                      │    │
│  │  - 使用熵提取的密钥                                        │    │
│  │  - 生成无限随机字节流                                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      接口层                                          │
│  get_random_bytes() / get_random_u32() / /dev/urandom              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 附录：关键文件索引

| 文件 | 功能 |
|------|------|
| `/Users/sphinx/github/linux/crypto/algapi.c` | 算法注册、查找、移除基础设施 |
| `/Users/sphinx/github/linux/crypto/api.c` | 核心Crypto API、算法分配 |
| `/Users/sphinx/github/linux/crypto/cryptd.c` | 异步加密守护进程 |
| `/Users/sphinx/github/linux/crypto/jitterentropy.c` | 抖动熵RNG实现 |
| `/Users/sphinx/github/linux/crypto/shash.c` | 同步哈希API实现 |
| `/Users/sphinx/github/linux/crypto/lzo.c` | LZO压缩算法 |
| `/Users/sphinx/github/linux/crypto/lz4hc.c` | LZ4HC压缩算法 |
| `/Users/sphinx/github/linux/crypto/deflate.c` | Deflate(zlib)压缩 |
| `/Users/sphinx/github/linux/include/linux/crypto.h` | 核心数据结构和标志 |
| `/Users/sphinx/github/linux/include/crypto/hash.h` | 哈希相关接口 |
| `/Users/sphinx/github/linux/include/crypto/algapi.h` | 算法API接口 |
| `/Users/sphinx/github/linux/include/crypto/internal.h` | 内部接口 |
| `/Users/sphinx/github/linux/drivers/char/random.c` | 随机数生成器实现 |
| `/Users/sphinx/github/linux/include/linux/random.h` | 随机数接口头文件 |
