# Linux Crypto 子系统文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [crypto_core.md](crypto_core.md) | 核心框架: crypto_alg, crypto_tfm, 算法注册 | crypto/api.c |
| [crypto_skcipher.md](crypto_skcipher.md) | 同步加密: skcipher, ablkcipher, AES/DES | crypto/skcipher.c |
| [crypto_async.md](crypto_async.md) | 异步加密: aead, ahash, 哈希, GCM | crypto/aead.c, ahash.c |
| [crypto_infra.md](crypto_infra.md) | 基础设施: algapi, cryptd, 随机数 | crypto/algapi.c |

---

## 1. Crypto 核心框架 (crypto_core.md)

### 关键内容
- struct crypto_alg: 算法基础结构
- struct crypto_tfm: Transform 结构
- struct crypto_larval: 幼虫状态机制
- 算法注册: crypto_register_alg()

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| crypto_register_alg | crypto/api.c |
| crypto_alg_lookup | crypto/algapi.c |

---

## 2. 同步加密 (crypto_skcipher.md)

### 关键内容
- SKCIPHER 接口: crypto_alloc_skcipher()
- ABLKCIPHER: ablkcipher_request
- 块加密算法: AES, DES, 3DES
- 加密模式: ECB, CBC, CTR

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| crypto_alloc_skcipher | crypto/skcipher.c |
| skcipher_crypt | crypto/skcipher.c |

---

## 3. 异步加密 (crypto_async.md)

### 关键内容
- AEAD: aead_request, crypto_aead_encrypt()
- AHASH: ahash_request, crypto_ahash_digest()
- 哈希算法: MD5, SHA1, SHA256
- GCM, ChaCha20-Poly1305

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| crypto_alloc_aead | crypto/aead.c |
| crypto_ahash_digest | crypto/ahash.c |

---

## 4. 基础设施 (crypto_infra.md)

### 关键内容
- algapi: 算法查找和移除
- cryptd: 同步转异步包装
- 随机数: jitterentropy
- 压缩: deflate, lz4

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| crypto_alg_lookup | crypto/algapi.c |
| cryptd_alloc_ablkcipher | crypto/cryptd.c |

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         用户空间                        │
                    └─────────────────┬───────────────────────┘
                                      │ crypto_xxx()
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         Crypto API                     │
                    │   crypto_alloc_xxx()                  │
                    │   crypto_register_alg()                │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   Sync API          │               │   Async API        │
        │   (skcipher)        │               │   (aead/ahash)    │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   Algorithm         │               │   Algorithm         │
        │   (AES, DES...)     │               │   (GCM, SHA...)    │
        └─────────────────────┘               └─────────────────────┘
```

---

## 源码位置索引

| 组件 | 路径 |
|------|------|
| 核心 API | crypto/api.c |
| SKCIPHER | crypto/skcipher.c |
| AEAD | crypto/aead.c |
| AHASH | crypto/ahash.c |
| SHASH | crypto/shash.c |
| algapi | crypto/algapi.c |
| cryptd | crypto/cryptd.c |
| AES | crypto/aes.c |
| SHA | crypto/sha256.c |
| MD5 | crypto/md5.c |
| GCM | crypto/gcm.c |
| 随机数 | crypto/jitterentropy.c |
