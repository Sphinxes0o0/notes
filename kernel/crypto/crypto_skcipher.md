# Linux 内核 Crypto 子系统同步加密机制分析

## 目录

1. [概述](#1-概述)
2. [SKCIPHER 接口](#2-skcipher-接口)
3. [LSKCIPHER 接口](#3-lskcipher-接口)
4. [块加密算法实现](#4-块加密算法实现)
5. [加密模式实现](#5-加密模式实现)
6. [加密流程分析](#6-加密流程分析)
7. [数据结构关系图](#7-数据结构关系图)

---

## 1. 概述

### 1.1 Crypto 子系统架构

Linux 内核 Crypto 子系统提供了一套统一的接口用于对称加密、非对称加密、哈希、AEAD 等密码学操作。本文档重点分析**同步对称加密**机制。

```
用户空间
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Crypto API 层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  skcipher  │  │  lskcipher  │  │    aead     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
    │                   │                   │
    ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   模式层 (ECB/CBC/CTR/GCM)                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │   ECB   │  │   CBC   │  │   CTR   │  │   GCM   │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
    │                   │                   │
    ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   底层算法层                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │   AES   │  │   DES   │  │   SM4   │  │   ...   │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
    │                   │                   │
    ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              硬件加速层 (ARCH-specific)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ x86/AES-NI│  │ ARM/NEON │  │  RISC-V  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心文件位置

| 文件 | 功能 |
|------|------|
| `/crypto/skcipher.c` | SKCIPHER 接口实现 |
| `/crypto/lskcipher.c` | LSKCIPHER 接口实现 |
| `/crypto/cipher.c` | 单块密码操作 |
| `/crypto/cbc.c` | CBC 模式 |
| `/crypto/ctr.c` | CTR 模式 |
| `/crypto/gcm.c` | GCM 模式 (AEAD) |
| `/crypto/aes.c` | AES 算法 |
| `/include/crypto/skcipher.h` | SKCIPHER 头文件 |
| `/include/crypto/internal/skcipher.h` | 内部 SKCIPHER 接口 |
| `/include/crypto/aes.h` | AES 头文件 |

---

## 2. SKCIPHER 接口

### 2.1 核心数据结构

#### struct skcipher_request (include/crypto/skcipher.h:40-51)

```c
struct skcipher_request {
    unsigned int cryptlen;    // 加密/解密数据长度

    u8 *iv;                  // 初始化向量

    struct scatterlist *src; // 源数据 scatter-gather 列表
    struct scatterlist *dst;  // 目标数据 scatter-gather 列表

    struct crypto_async_request base;  // 基础异步请求

    void *__ctx[] CRYPTO_MINALIGN_ATTR;  // 私有上下文
};
```

#### struct crypto_skcipher (include/crypto/skcipher.h:53-57)

```c
struct crypto_skcipher {
    unsigned int reqsize;     // 请求上下文大小
    struct crypto_tfm base;   // 基础 TFM (Transform)
};
```

#### struct skcipher_alg (include/crypto/skcipher.h:151-167)

```c
struct skcipher_alg {
    int (*setkey)(struct crypto_skcipher *tfm, const u8 *key,
                  unsigned int keylen);
    int (*encrypt)(struct skcipher_request *req);
    int (*decrypt)(struct skcipher_request *req);
    int (*export)(struct skcipher_request *req, void *out);
    int (*import)(struct skcipher_request *req, const void *in);
    int (*init)(struct crypto_skcipher *tfm);
    void (*exit)(struct crypto_skcipher *tfm);

    unsigned int walksize;

    union {
        struct SKCIPHER_ALG_COMMON;
        struct skcipher_alg_common co;
    };
};
```

### 2.2 crypto_alloc_skcipher()

**位置**: `crypto/skcipher.c:636-640`

```c
struct crypto_skcipher *crypto_alloc_skcipher(const char *alg_name,
                                              u32 type, u32 mask)
{
    return crypto_alloc_tfm(alg_name, &crypto_skcipher_type, type, mask);
}
```

此函数用于分配一个对称密钥密码算法实例。

**参数说明**:
- `alg_name`: 算法名称，如 "cbc(aes)"、"ecb(aes)" 等
- `type`: 算法类型标志
- `mask`: 算法掩码

**返回值**: 成功返回 `crypto_skcipher` 句柄，失败返回错误指针

### 2.3 crypto_skcipher_encrypt/decrypt()

**位置**: `crypto/skcipher.c:435-459`

```c
int crypto_skcipher_encrypt(struct skcipher_request *req)
{
    struct crypto_skcipher *tfm = crypto_skcipher_reqtfm(req);
    struct skcipher_alg *alg = crypto_skcipher_alg(tfm);

    if (crypto_skcipher_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;
    if (alg->co.base.cra_type != &crypto_skcipher_type)
        return crypto_lskcipher_encrypt_sg(req);
    return alg->encrypt(req);
}
EXPORT_SYMBOL_GPL(crypto_skcipher_encrypt);

int crypto_skcipher_decrypt(struct skcipher_request *req)
{
    struct crypto_skcipher *tfm = crypto_skcipher_reqtfm(req);
    struct skcipher_alg *alg = crypto_skcipher_alg(tfm);

    if (crypto_skcipher_get_flags(tfm) & CRYPTO_TFM_NEED_KEY)
        return -ENOKEY;
    if (alg->co.base.cra_type != &crypto_skcipher_type)
        return crypto_lskcipher_decrypt_sg(req);
    return alg->decrypt(req);
}
```

### 2.4 crypto_skcipher_setkey()

**位置**: `crypto/skcipher.c:398-432`

```c
int crypto_skcipher_setkey(struct crypto_skcipher *tfm, const u8 *key,
                           unsigned int keylen)
{
    struct skcipher_alg *cipher = crypto_skcipher_alg(tfm);
    unsigned long alignmask = crypto_skcipher_alignmask(tfm);
    int err;

    if (cipher->co.base.cra_type != &crypto_skcipher_type) {
        struct crypto_lskcipher **ctx = crypto_skcipher_ctx(tfm);
        crypto_lskcipher_clear_flags(*ctx, CRYPTO_TFM_REQ_MASK);
        crypto_lskcipher_set_flags(*ctx,
                       crypto_skcipher_get_flags(tfm) &
                       CRYPTO_TFM_REQ_MASK);
        err = crypto_lskcipher_setkey(*ctx, key, keylen);
        goto out;
    }

    if (keylen < cipher->min_keysize || keylen > cipher->max_keysize)
        return -EINVAL;

    if ((unsigned long)key & alignmask)
        err = skcipher_setkey_unaligned(tfm, key, keylen);
    else
        err = cipher->setkey(tfm, key, keylen);

out:
    if (unlikely(err)) {
        skcipher_set_needkey(tfm);
        return err;
    }

    crypto_skcipher_clear_flags(tfm, CRYPTO_TFM_NEED_KEY);
    return 0;
}
```

**密钥设置流程**:
1. 检查密钥长度是否在算法支持范围内
2. 处理未对齐的密钥（复制到对齐的缓冲区）
3. 调用算法的 `setkey` 回调
4. 成功清除 `CRYPTO_TFM_NEED_KEY` 标志

### 2.5 skcipher_walk 结构

**位置**: `include/crypto/internal/skcipher.h:57-96`

```c
struct skcipher_walk {
    union {
        struct {
            struct {
                const void *const addr;
            } virt;
        } src;
        struct scatter_walk in;    // 内部使用
    };

    union {
        struct {
            struct {
                void *const addr;
            } virt;
        } dst;
        struct scatter_walk out;   // 内部使用
    };

    unsigned int nbytes;           // 当前步骤处理的字节数
    unsigned int total;            // 剩余总字节数

    u8 *page;                      // 临时页面缓冲区
    u8 *buffer;                    // 临时对齐缓冲区
    u8 *oiv;                       // 原始 IV
    void *iv;                      // 当前 IV

    unsigned int ivsize;           // IV 大小
    int flags;                     // 行走标志
    unsigned int blocksize;         // 块大小
    unsigned int stride;            // 步进大小
    unsigned int alignmask;         // 对齐掩码
};
```

**SKCIPHER_WALK 标志** (crypto/skcipher.c:31-36):
```c
enum {
    SKCIPHER_WALK_SLOW = 1 << 0,   // 需要慢速路径
    SKCIPHER_WALK_COPY = 1 << 1,   // 需要复制
    SKCIPHER_WALK_DIFF = 1 << 2,   // 源和目标不同页
    SKCIPHER_WALK_SLEEP = 1 << 3,  // 允许睡眠
};
```

---

## 3. LSKCIPHER 接口

### 3.1 概念

LSKCIPHER (Linear Symmetric Key Cipher) 是 SKCIPHER 的简化版本，专门用于线性处理连续内存区域的同步加密操作。相比 SKCIPHER 的 scatter-gather 列表处理，LSKCIPHER 更适合直接内存块加密。

### 3.2 核心数据结构

#### struct lskcipher_alg (include/crypto/skcipher.h:202-213)

```c
struct lskcipher_alg {
    int (*setkey)(struct crypto_lskcipher *tfm, const u8 *key,
                  unsigned int keylen);
    int (*encrypt)(struct crypto_lskcipher *tfm, const u8 *src,
                   u8 *dst, unsigned len, u8 *siv, u32 flags);
    int (*decrypt)(struct crypto_lskcipher *tfm, const u8 *src,
                   u8 *dst, unsigned len, u8 *siv, u32 flags);
    int (*init)(struct crypto_lskcipher *tfm);
    void (*exit)(struct crypto_lskcipher *tfm);

    struct skcipher_alg_common co;
};
```

### 3.3 crypto_lskcipher_crypt_sg()

**位置**: `crypto/lskcipher.c:158-199`

LSKCIPHER 通过 scatter-gather 方式处理加密请求：

```c
static int crypto_lskcipher_crypt_sg(struct skcipher_request *req,
                     int (*crypt)(struct crypto_lskcipher *tfm,
                                  const u8 *src, u8 *dst,
                                  unsigned len, u8 *ivs,
                                  u32 flags))
{
    struct crypto_skcipher *skcipher = crypto_skcipher_reqtfm(req);
    struct crypto_lskcipher **ctx = crypto_skcipher_ctx(skcipher);
    u8 *ivs = skcipher_request_ctx(req);
    struct crypto_lskcipher *tfm = *ctx;
    struct skcipher_walk walk;
    unsigned ivsize;
    u32 flags;
    int err;

    ivsize = crypto_lskcipher_ivsize(tfm);
    ivs = PTR_ALIGN(ivs, crypto_skcipher_alignmask(skcipher) + 1);
    memcpy(ivs, req->iv, ivsize);

    flags = req->base.flags & CRYPTO_TFM_REQ_MAY_SLEEP;

    if (req->base.flags & CRYPTO_SKCIPHER_REQ_CONT)
        flags |= CRYPTO_LSKCIPHER_FLAG_CONT;

    if (!(req->base.flags & CRYPTO_SKCIPHER_REQ_NOTFINAL))
        flags |= CRYPTO_LSKCIPHER_FLAG_FINAL;

    err = skcipher_walk_virt(&walk, req, false);

    while (walk.nbytes) {
        err = crypt(tfm, walk.src.virt.addr, walk.dst.virt.addr,
                    walk.nbytes, ivs,
                    flags & ~(walk.nbytes == walk.total ?
                    0 : CRYPTO_LSKCIPHER_FLAG_FINAL));
        err = skcipher_walk_done(&walk, err);
        flags |= CRYPTO_LSKCIPHER_FLAG_CONT;
    }

    memcpy(req->iv, ivs, ivsize);

    return err;
}
```

---

## 4. 块加密算法实现

### 4.1 AES 算法

#### struct aes_key (include/crypto/aes.h:113-116)

```c
struct aes_key {
    struct aes_enckey;           // 加密密钥
    union aes_invkey_arch inv_k; // 解密密钥（等效逆 cipher）
};
```

#### aes_preparekey() (crypto/aes.c)

```c
int aes_preparekey(struct aes_key *key, const u8 *in_key, size_t key_len)
```

此函数根据 FIPS-197 标准扩展密钥:
- AES-128: 10 轮，16 字节密钥
- AES-192: 12 轮，24 字节密钥
- AES-256: 14 轮，32 字节密钥

#### aes_encrypt()/aes_decrypt()

**位置**: `crypto/aes.c:22-34`

```c
static void crypto_aes_encrypt(struct crypto_tfm *tfm, u8 *out, const u8 *in)
{
    const struct aes_key *key = crypto_tfm_ctx(tfm);
    aes_encrypt(key, out, in);
}

static void crypto_aes_decrypt(struct crypto_tfm *tfm, u8 *out, const u8 *in)
{
    const struct aes_key *key = crypto_tfm_ctx(tfm);
    aes_decrypt(key, out, in);
}
```

### 4.2 crypto_cipher_encrypt_one()

**位置**: `crypto/cipher.c:79-84`

```c
void crypto_cipher_encrypt_one(struct crypto_cipher *tfm,
                               u8 *dst, const u8 *src)
{
    cipher_crypt_one(tfm, dst, src, true);
}
EXPORT_SYMBOL_NS_GPL(crypto_cipher_encrypt_one, "CRYPTO_INTERNAL");
```

**cipher_crypt_one()** (crypto/cipher.c:58-77):

```c
static inline void cipher_crypt_one(struct crypto_cipher *tfm,
                    u8 *dst, const u8 *src, bool enc)
{
    unsigned long alignmask = crypto_cipher_alignmask(tfm);
    struct cipher_alg *cia = crypto_cipher_alg(tfm);
    void (*fn)(struct crypto_tfm *, u8 *, const u8 *) =
        enc ? cia->cia_encrypt : cia->cia_decrypt;

    if (unlikely(((unsigned long)dst | (unsigned long)src) & alignmask)) {
        unsigned int bs = crypto_cipher_blocksize(tfm);
        u8 buffer[MAX_CIPHER_BLOCKSIZE + MAX_CIPHER_ALIGNMASK];
        u8 *tmp = (u8 *)ALIGN((unsigned long)buffer, alignmask + 1);

        memcpy(tmp, src, bs);
        fn(crypto_cipher_tfm(tfm), tmp, tmp);
        memcpy(dst, tmp, bs);
    } else {
        fn(crypto_cipher_tfm(tfm), dst, src);
    }
}
```

**功能说明**:
- 检查源/目标地址是否对齐
- 如未对齐，使用临时缓冲区处理
- 调用底层加密/解密函数

---

## 5. 加密模式实现

### 5.1 ECB 模式 (Electronic Codebook)

ECB 是最简单的模式，将数据分成块，每块独立加密。

**特点**:
- 相同明文块产生相同密文块（安全性问题）
- 无法隐藏数据模式
- 适合小块数据或随机数据

### 5.2 CBC 模式 (Cipher Block Chaining)

#### 加密流程

```
P0 →───→ XOR ───→ [AES Encrypt] ───→ C0
                ↑
               IV

P1 →───→ XOR ───→ [AES Encrypt] ───→ C1
                ↑
               C0

P2 →───→ XOR ───→ [AES Encrypt] ───→ C2
                ↑
               C1
```

#### crypto_cbc_encrypt_segment() (crypto/cbc.c:15-28)

```c
static int crypto_cbc_encrypt_segment(struct crypto_lskcipher *tfm,
                      const u8 *src, u8 *dst, unsigned nbytes,
                      u8 *iv)
{
    unsigned int bsize = crypto_lskcipher_blocksize(tfm);

    for (; nbytes >= bsize; src += bsize, dst += bsize, nbytes -= bsize) {
        crypto_xor(iv, src, bsize);                      // 明文 XOR IV
        crypto_lskcipher_encrypt(tfm, iv, dst, bsize, NULL); // AES 加密
        memcpy(iv, dst, bsize);                          // 更新 IV
    }

    return nbytes;
}
```

#### crypto_cbc_encrypt_inplace() (crypto/cbc.c:30-51)

```c
static int crypto_cbc_encrypt_inplace(struct crypto_lskcipher *tfm,
                      u8 *src, unsigned nbytes, u8 *oiv)
{
    unsigned int bsize = crypto_lskcipher_blocksize(tfm);
    u8 *iv = oiv;

    if (nbytes < bsize)
        goto out;

    do {
        crypto_xor(src, iv, bsize);                      // XOR IV
        crypto_lskcipher_encrypt(tfm, src, src, bsize, NULL); // 原地加密
        iv = src;                                        // 更新 IV

        src += bsize;
    } while ((nbytes -= bsize) >= bsize);

    memcpy(oiv, iv, bsize);

out:
    return nbytes;
}
```

#### CBC 解密流程

```
C0 →───→ [AES Decrypt] ───→ XOR ───→ P0
                            ↑
                           IV

C1 →───→ [AES Decrypt] ───→ XOR ───→ P1
                            ↑
                           C0
```

**注意**: CBC 解密可以并行化（利用解密算法的特点）

#### crypto_cbc_decrypt_inplace() (crypto/cbc.c:94-120)

```c
static int crypto_cbc_decrypt_inplace(struct crypto_lskcipher *tfm,
                      u8 *src, unsigned nbytes, u8 *iv)
{
    unsigned int bsize = crypto_lskcipher_blocksize(tfm);
    u8 last_iv[MAX_CIPHER_BLOCKSIZE];

    if (nbytes < bsize)
        goto out;

    /* Start of the last block. */
    src += nbytes - (nbytes & (bsize - 1)) - bsize;
    memcpy(last_iv, src, bsize);

    for (;;) {
        crypto_lskcipher_decrypt(tfm, src, src, bsize, NULL);
        if ((nbytes -= bsize) < bsize)
            break;
        crypto_xor(src, src - bsize, bsize);
        src -= bsize;
    }

    crypto_xor(src, iv, bsize);
    memcpy(iv, last_iv, bsize);

out:
    return nbytes;
}
```

### 5.3 CTR 模式 (Counter Mode)

#### 特点
- 将块密码转换为流密码
- 支持随机访问（并行加密/解密）
- 无需填充

#### 加密流程

```
Counter → [AES Encrypt] → Keystream
                         ↓
Keystream XOR Plaintext → Ciphertext
```

#### crypto_ctr_crypt_segment() (crypto/ctr.c:46-70)

```c
static int crypto_ctr_crypt_segment(struct skcipher_walk *walk,
                    struct crypto_cipher *tfm)
{
    void (*fn)(struct crypto_tfm *, u8 *, const u8 *) =
           crypto_cipher_alg(tfm)->cia_encrypt;
    unsigned int bsize = crypto_cipher_blocksize(tfm);
    u8 *ctrblk = walk->iv;
    const u8 *src = walk->src.virt.addr;
    u8 *dst = walk->dst.virt.addr;
    unsigned int nbytes = walk->nbytes;

    do {
        /* create keystream */
        fn(crypto_cipher_tfm(tfm), dst, ctrblk);   // 生成密钥流
        crypto_xor(dst, src, bsize);               // XOR 明文

        /* increment counter in counterblock */
        crypto_inc(ctrblk, bsize);                 // 计数器递增

        src += bsize;
        dst += bsize;
    } while ((nbytes -= bsize) >= bsize);

    return nbytes;
}
```

#### crypto_ctr_crypt() (crypto/ctr.c:99-125)

```c
static int crypto_ctr_crypt(struct skcipher_request *req)
{
    struct crypto_skcipher *tfm = crypto_skcipher_reqtfm(req);
    struct crypto_cipher *cipher = skcipher_cipher_simple(tfm);
    const unsigned int bsize = crypto_cipher_blocksize(cipher);
    struct skcipher_walk walk;
    unsigned int nbytes;
    int err;

    err = skcipher_walk_virt(&walk, req, false);

    while (walk.nbytes >= bsize) {
        if (walk.src.virt.addr == walk.dst.virt.addr)
            nbytes = crypto_ctr_crypt_inplace(&walk, cipher);
        else
            nbytes = crypto_ctr_crypt_segment(&walk, cipher);

        err = skcipher_walk_done(&walk, nbytes);
    }

    if (walk.nbytes) {
        crypto_ctr_crypt_final(&walk, cipher);  // 处理最后的不完整块
        err = skcipher_walk_done(&walk, 0);
    }

    return err;
}
```

### 5.4 GCM 模式 (Galois/Counter Mode)

GCM 是提供认证加密 (AEAD) 的模式，结合了 CTR 加密和 GMAC 认证。

#### 核心结构

```c
struct crypto_gcm_ctx {
    struct crypto_skcipher *ctr;   // CTR 模式加密
    struct crypto_aead *ghash;     // GHASH 认证
};
```

#### crypto_gcm_encrypt() (crypto/gcm.c:445-457)

```c
static int crypto_gcm_encrypt(struct aead_request *req)
{
    struct crypto_gcm_req_priv_ctx *pctx = crypto_gcm_reqctx(req);
    struct skcipher_request *skreq = &pctx->u.skreq;
    u32 flags = aead_request_flags(req);

    crypto_gcm_init_common(req);      // 初始化
    crypto_gcm_init_crypt(req, req->cryptlen);
    skcipher_request_set_callback(skreq, flags, gcm_encrypt_done, req);

    return crypto_skcipher_encrypt(skreq) ?:
           gcm_encrypt_continue(req, flags);
}
```

#### GCM 加密流程

1. **J0 = IV || 0^31 || 1** - 形成初始计数器
2. **C = E(K, J0 || counter)** - CTR 模式加密
3. **S = GHASH(H, A || C || len(A) || len(C))** - 计算认证标签
4. **T = S XOR E(K, J0)** - 生成最终认证标签

---

## 6. 加密流程分析

### 6.1 完整加密流程图

```
用户空间调用
    │
    ▼
┌─────────────────────────────────────────┐
│  1. 分配算法实例                         │
│  crypto_alloc_skcipher("cbc(aes)", ...)   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  2. 设置密钥                             │
│  crypto_skcipher_setkey(tfm, key, ...)   │
│  ├── 验证密钥长度                         │
│  ├── 调用底层 setkey                      │
│  └── aes_expandkey() 扩展密钥             │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  3. 分配请求                             │
│  skcipher_request_alloc()                │
│  └── skcipher_request_set_crypt()        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  4. 执行加密                             │
│  crypto_skcipher_encrypt(req)            │
│  ├── 检查 NEED_KEY 标志                   │
│  ├── 调用 alg->encrypt()                  │
│  └── skcipher_walk_virt()                 │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  5. Scatter-Gather 行走                   │
│  skcipher_walk_virt()                    │
│  ├── scatterwalk_start()                 │
│  ├── 处理跨页数据                         │
│  └── skcipher_walk_next()                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  6. 模式加密                             │
│  crypto_cbc_encrypt_segment()            │
│  ├── crypto_xor() XOR 操作               │
│  └── crypto_lskcipher_encrypt()          │
│      └── aes_encrypt()  AES 块加密       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  7. 完成行走                             │
│  skcipher_walk_done()                    │
│  ├── 更新 scatterlist 位置                │
│  ├── 处理剩余数据                         │
│  └── 返回结果                            │
└─────────────────────────────────────────┘
```

### 6.2 setkey 详细流程

**位置**: `crypto/skcipher.c:398-432`

```
crypto_skcipher_setkey()
    │
    ├──► 检查算法类型是否为 skcipher_type
    │       │
    │       └──► 是: 直接调用 cipher->setkey()
    │           │
    │           └──► 否: 调用 crypto_lskcipher_setkey()
    │               └──► 处理未对齐密钥
    │
    ├──► 检查密钥长度 (min_keysize ~ max_keysize)
    │
    └──► 调用底层 setkey
            │
            └──► aes_preparekey()
                │
                ├──► aes_expandkey()
                │       │
                │       └──► 生成加密轮密钥
                │
                └──► 生成解密轮密钥 (inv_k)
```

### 6.3 加密操作详细流程

**CBC 模式加密示例**:

```
skcipher_walk_virt() 初始化
    │
    ▼
while (walk.nbytes > 0) {
    │
    ├──► crypto_cbc_encrypt_segment()
    │       │
    │       ├──► for each block:
    │       │       │
    │       │       ├──► crypto_xor(plaintext, iv) → tmp
    │       │       │
    │       │       └──► crypto_lskcipher_encrypt(tfm, tmp, tmp)
    │       │               │
    │       │               └──► cipher->encrypt()
    │       │                       │
    │       │                       └──► aes_encrypt()
    │       │                               │
    │       │                               └──► 轮密钥加 → 字节替换 → 行移位 → 列混合
    │       │
    │       └──► memcpy(iv, ciphertext)
    │
    └──► skcipher_walk_done()
            │
            ├──► scatterwalk_advance()
            │
            └──► skcipher_walk_next()
}
```

---

## 7. 数据结构关系图

### 7.1 核心数据结构关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        crypto_skcipher                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ unsigned int reqsize                                        ││
│  │ struct crypto_tfm base                                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ container_of
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      struct skcipher_alg                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ int (*setkey)(...)                                          ││
│  │ int (*encrypt)(struct skcipher_request *req)                 ││
│  │ int (*decrypt)(struct skcipher_request *req)                 ││
│  │ unsigned int walksize                                        ││
│  │ struct skcipher_alg_common co                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 实例化
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      struct skcipher_request                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ unsigned int cryptlen                                        ││
│  │ u8 *iv                                                      ││
│  │ struct scatterlist *src                                      ││
│  │ struct scatterlist *dst                                      ││
│  │ struct crypto_async_request base                             ││
│  │ void *__ctx[]                                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 用于遍历
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        struct skcipher_walk                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ union { src.virt.addr / scatter_walk in }                   ││
│  │ union { dst.virt.addr / scatter_walk out }                  ││
│  │ unsigned int nbytes                                         ││
│  │ unsigned int total                                          ││
│  │ u8 *page, *buffer, *oiv, *iv                                ││
│  │ unsigned int ivsize, blocksize, stride, alignmask            ││
│  │ int flags                                                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 算法注册与查找

```
crypto_register_skcipher(&alg)
    │
    ▼
skcipher_prepare_alg()
    │
    ├──► skcipher_prepare_alg_common()
    │       │
    │       └──► 验证 ivsize, chunksize, statesize
    │
    └──► 设置 cra_type = &crypto_skcipher_type
            │
            ▼
    crypto_register_alg()
        │
        ▼
    添加到 crypto_alg_list
        │
        ▼
    可通过 crypto_alloc_skcipher() 查找使用
```

### 7.3 Scatter-Gather 行走示意图

```
初始状态:
    src: [Page 0 ] [Page 1 ] [Page 2 ]
         ████████████

walk.nbytes = 4096 (一页)
walk.total = 12000
walk.src.virt.addr → Page 0

第一次 skcipher_walk_next():
    ├──► n = min(stride, total) = 4096
    ├──► scatterwalk_clamp() 确保在单页内
    └──► walk.nbytes = 4096

第二次 skcipher_walk_next():
    ├──► scatterwalk_done() 推进到下一页
    └──► walk.src.virt.addr → Page 1
```

---

## 8. 使用示例

### 8.1 同步 CBC-AES 加密

```c
#include <crypto/skcipher.h>
#include <linux/scatterlist.h>

int encrypt_example(void)
{
    struct crypto_skcipher *tfm;
    struct skcipher_request *req;
    struct scatterlist src, dst;
    u8 iv[AES_BLOCK_SIZE];
    u8 key[32];  // AES-256
    u8 plaintext[64];
    u8 ciphertext[64];
    int err;

    /* 1. 分配算法 */
    tfm = crypto_alloc_skcipher("cbc(aes)", 0, 0);
    if (IS_ERR(tfm))
        return PTR_ERR(tfm);

    /* 2. 设置密钥 */
    err = crypto_skcipher_setkey(tfm, key, 32);
    if (err)
        goto out_free_tfm;

    /* 3. 分配请求 */
    req = skcipher_request_alloc(tfm, GFP_KERNEL);
    if (!req) {
        err = -ENOMEM;
        goto out_free_tfm;
    }

    /* 4. 设置 IV */
    memcpy(iv, "\x00\x01\x02...", AES_BLOCK_SIZE);

    /* 5. 设置加密参数 */
    sg_init_one(&src, plaintext, 64);
    sg_init_one(&dst, ciphertext, 64);
    skcipher_request_set_crypt(req, &src, &dst, 64, iv);

    /* 6. 执行加密 */
    err = crypto_skcipher_encrypt(req);

    skcipher_request_free(req);
out_free_tfm:
    crypto_free_skcipher(tfm);
    return err;
}
```

### 8.2 同步 CTR-AES 加密

```c
int encrypt_ctr_example(void)
{
    struct crypto_skcipher *tfm;
    struct skcipher_request *req;
    struct scatterlist src, dst;
    u8 iv[16];  // CTR 模式使用 16 字节 IV
    u8 key[16]; // AES-128
    u8 plaintext[100];
    u8 ciphertext[100];
    int err;

    tfm = crypto_alloc_skcipher("ctr(aes)", 0, 0);
    if (IS_ERR(tfm))
        return PTR_ERR(tfm);

    err = crypto_skcipher_setkey(tfm, key, 16);
    if (err)
        goto out;

    req = skcipher_request_alloc(tfm, GFP_KERNEL);
    if (!req) {
        err = -ENOMEM;
        goto out;
    }

    memset(iv, 0, 16);  // 计数器初始值
    sg_init_one(&src, plaintext, 100);
    sg_init_one(&dst, ciphertext, 100);
    skcipher_request_set_crypt(req, &src, &dst, 100, iv);

    err = crypto_skcipher_encrypt(req);

    skcipher_request_free(req);
out:
    crypto_free_skcipher(tfm);
    return err;
}
```

---

## 9. 关键 API 总结

### 9.1 分配与释放

| API | 位置 | 功能 |
|-----|------|------|
| `crypto_alloc_skcipher()` | skcipher.c:636 | 分配 SKCIPHER 实例 |
| `crypto_free_skcipher()` | skcipher.h:327 | 释放 SKCIPHER 实例 |
| `crypto_alloc_sync_skcipher()` | skcipher.c:643 | 分配同步 SKCIPHER |
| `skcipher_request_alloc()` | skcipher.h:846 | 分配请求 |
| `skcipher_request_free()` | skcipher.h:865 | 释放请求 |

### 9.2 密钥操作

| API | 位置 | 功能 |
|-----|------|------|
| `crypto_skcipher_setkey()` | skcipher.c:398 | 设置密钥 |
| `crypto_sync_skcipher_setkey()` | skcipher.h:617 | 同步设置密钥 |

### 9.3 加密/解密操作

| API | 位置 | 功能 |
|-----|------|------|
| `crypto_skcipher_encrypt()` | skcipher.c:435 | 加密数据 |
| `crypto_skcipher_decrypt()` | skcipher.c:448 | 解密数据 |

### 9.4 Scatter-Gather 操作

| API | 位置 | 功能 |
|-----|------|------|
| `skcipher_walk_virt()` | skcipher.c:283 | 初始化 scatter-gather 行走 |
| `skcipher_walk_done()` | skcipher.c:71 | 完成行走步骤 |

---

## 10. 总结

Linux 内核 Crypto 子系统的同步加密机制通过 SKCIPHER 和 LSKCIPHER 接口提供了一套完整的对称加密抽象。主要特点包括:

1. **分层架构**: 从上到下分为 API 层、模式层、算法层和硬件加速层
2. **统一接口**: 通过 skcipher_request 结构支持各种加密模式和算法
3. **scatter-gather 支持**: 通过 skcipher_walk 机制高效处理跨页数据
4. **内存对齐处理**: 自动处理未对齐的密钥和数据
5. **模板机制**: 通过 crypto_template 支持运行时创建算法实例(如 `cbc(aes)`)

常用的加密模式:
- **ECB**: 简单但不安全，不推荐使用
- **CBC**: 适合常规加密，需要填充
- **CTR**: 流密码模式，无需填充，支持随机访问
- **GCM**: 提供认证加密 (AEAD)，适合网络安全协议
