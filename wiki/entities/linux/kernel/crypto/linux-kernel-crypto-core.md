---
type: entity
tags: [Linux内核, 密码学, crypto子系统, 对称加密, 非对称加密, 哈希]
created: 2026-05-20
sources: [notes-overview-kernel-crypto]
---

# Linux Kernel Crypto Subsystem

## 定义

Linux内核统一的密码学算法框架，提供对称加密（AES/DES）、非对称加密（RSA）、哈希（SHA/MD5）、随机数生成、压缩等多种密码学功能的抽象接口和算法注册机制。

## 关键要点

### 核心架构

```
用户空间 → Crypto API → Template Layer → Core API → Algorithm Registry
                                   ↓
                          算法实现 (软件/硬件/模板组合)
```

**分层组件**:
- **High-Level API**: crypto_alloc_skcipher(), crypto_aead_init() 等
- **Template Layer**: CBC, GCM, PCRT 等模式模板
- **Core API**: crypto_register_alg(), crypto_alloc_tfm() 等
- **Registry**: crypto_alg_list 链表管理所有算法

### 核心数据结构

- **crypto_alg**: 算法基础结构（cra_name, cra_flags, cra_blocksize等）
- **crypto_tfm**: Transform运行时实例（算法上下文）
- **crypto_larval**: 幼虫状态，用于延迟自测
- **crypto_template**: 算法模板（如cbc模板实例化aes算法）
- **crypto_instance**: 模板创建的算法实例

### 关键机制

**Larval自测机制**:
- 算法注册时进入LARVAL状态，调度自测
- 测试通过后标记为TESTED，唤醒等待者
- 测试失败标记为DEAD

**Template模板机制**:
- 模板组合基础算法形成新算法（如 cbc(aes)）
- 模板实例通过crypto_register_instance()注册
- 生命周期：create→register→use→destroy

**同步 vs 异步**:
- 同步：blocking调用，如crypto_cipher_encrypt()
- 异步：callback机制，如crypto_ahash_init()

### 源码位置

| 组件 | 路径 |
|------|------|
| 核心API | crypto/api.c |
| 算法注册 | crypto/algapi.c |
| SKCIPHER | crypto/skcipher.c |
| AEAD | crypto/aead.c |
| AHASH | crypto/ahash.c |
| 算法实现 | crypto/aes.c, crypto/sha256.c, crypto/md5.c |

## 相关概念

- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — 内核锁机制保障加密操作原子性
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络协议栈加解密
- 对称加密: AES, DES, 3DES
- 非对称加密: RSA
- 哈希: SHA256, MD5
- AEAD: GCM, ChaCha20-Poly1305

## 来源详情
- [[sources/github-sphinxes0o0-notes-kernel-crypto]]
