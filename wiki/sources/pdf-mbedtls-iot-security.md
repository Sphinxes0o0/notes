---
type: source
source-type: pdf
title: "密码技术与物联网安全：mbedtls开发实战"
author: "徐凯, 崔红鹏"
date: 2019
size: large
path: raw/PDFs/books/密码技术与物联网安全mbedtls开发实战.pdf
summary: "707页 mbedtls 嵌入式密码学实战指南（机械工业出版社），16章覆盖：密码学基础 → 单向散列/SHA → 对称加密AES → 消息认证码/CCM/GCM → 随机数/CTR_DRBG → RSA/ECDH/ECDSA → X.509证书 → TLS/DTLS/CoAPs 全栈，配套 Zephyr RTOS 移植示例"
tags: [security, cryptography, mbedtls, tls, iot, embedded, books]
created: 2026-05-27
sources: []
---

# 密码技术与物联网安全：mbedtls开发实战

## 概述

**Author:** 徐凯、崔红鹏（机械工业出版社，物联网核心技术丛书）
**Pages:** 707（含目录）
**Edition:** 2019
**Language:** Chinese (with code in C)
**Platform Focus:** Linux + Zephyr RTOS（物联网嵌入式场景）

不同于 OpenSSL 面向服务器场景，本书聚焦嵌入式/物联网端的密码学实现与 mbedtls 移植。

---

## 核心内容

### 第1章 物联网安全概述

**IoT vs Internet Security：**
- 物联网终端资源受限：CPU/内存/存储/电量/带宽均受限
- HTTPS 对受限终端过于复杂 → 探索更适合的轻量安全方案
- 密码学是 IoT 安全的核心基础

**柯克霍夫原则（Kerckhoffs's Principle）：**
- 密码系统的安全性依赖于密钥的保密性，而非算法的保密性
- 即便攻击者知道算法细节，只要密钥安全，系统仍安全

**攻击者模型：**
- Eve（被动窃听者）：Eavesdropper
- Mallory（主动攻击者）：Malicious active attacker

### 第2章 mbedtls 体系结构与移植

**mbedtls 模块划分：**
- `crypto`：纯软件实现的密码学原语（SHA/AES/RSA/ECDH/ECDSA/PRNG）
- `ssl`：TLS/DTLS 协议实现
- `x509`：证书解析与验证
- `net`：网络 I/O 抽象层（socket / DTLS over UDP）
- ` entropy`：熵源抽象（硬件 TRNG / OS / havege）

**移植层（Platform Layer）：**
- 时间接口：`mbedtls_platform_time()`
- 网络接口：`mbedtls_net_send()` / `mbedtls_net_recv()`
- 内存接口：`mbedtls_calloc()` / `mbedtls_free()` → 可自定义内存池
- entropy 接口：支持自定义熵源注入

**Zephyr RTOS 移植：**
- CMake 构建配置
- ST-LINK 调试器配置
- 资源消耗示例：TLS 双向认证仅占 14KB Flash / ~8KB RAM

### 第3章 数论基础

**群论（Group Theory）：**
- 群的基本概念：封闭性、结合律、单位元、逆元
- 循环群：存在生成元 g，g^n 遍历整个群
- 有限域 GF(p)（素域）和 GF(2^m)（二进制扩展域）

**离散对数问题（DLP）：**
- 在素域 GF(p) 中，给定 g, h = g^k mod p，求 k 在计算上不可行
- RSA / DH / ECDSA 的安全性均基于此

### 第4章 单向散列函数（Hash）

**Hash 函数性质：**
- 单向性（One-way）
- 抗碰撞（Collision Resistance）
- 抗第二原像（Second Preimage Resistance）

**SHA 家族：**
- SHA-1（160-bit，已不推荐）
- SHA-224/256/384/512（SHA-2）
- SHA-3（Keccak， sponge construction）

**mbedtls 实现：**
- `mbedtls_md_setup()` / `mbedtls_md_update()` / `mbedtls_md_finish()`
- `mbedtls_sha256()` 简化接口

### 第5章 对称加密（AES）

**Block Cipher Modes：**
- ECB（不推荐）：相同明文块产生相同密文块
- CBC：链接模式，需 IV，串行加密
- CTR：计数器模式，可并行加密，支持密文窃取
- GCM（推荐）：认证加密

**AES 算法细节：**
- 字节替换（SubBytes）→ 行移位（ShiftRows）→ 列混合（MixColumns）→ 轮密钥加（AddRoundKey）
- 10/12/14 轮（AES-128/192/256）
- 密钥扩展（Key Schedule）

**mbedtls 实现：**
- `mbedtls_aes_context` / `mbedtls_aes_crypt_cbc()`
- `pkcs7_check()` / `pkcs7_unpad()` 填充处理

### 第6章 消息认证码（MAC）

**HMAC：** Hash-based MAC，K⊕ipad || K⊕opad || message
**CMAC：** Cipher-based MAC，使用 AES-CBC
**CCM：** Counter with CBC-MAC，认证 + 加密
**GCM：** Galois/Counter Mode，GHASH + CTR → AEAD

**mbedtls API：**
- `mbedtls_md_hmac_starts()` → `_update()` → `_finish()`
- `mbedtls_cipher_cmac()`（CMAC）
- `mbedtls_cipher_auth_encrypt()`（GCM/CCM AEAD）

### 第7章 随机数生成（CTR_DRBG）

**TRNG vs PRNG：**
- 真随机数生成器（TRNG）：物理噪声源，熵收集慢
- 伪随机数生成器（PRNG）：确定性算法，需要种子

**CTR_DRBG（ANSI X9.62）：**
- AES-256-CTR 作为核心
- 熵源注入，状态可重置
- 适用于安全敏感的密钥生成

**mbedtls 实现：**
- `mbedtls_ctr_drbg_seed()` / `mbedtls_ctr_drbg_random()`
- 支持自定义 entropy source 回调

### 第8章 RSA 算法

**CRT 加速（中国剩余数定理）：**
- 计算 d_p = d mod (p-1), d_q = d mod (q-1)
- 分别在 p 和 q 上解密再合并 → ~4x 加速

**Padding 方法：**
- PKCS#1 v1.5（传统，已知攻击面）
- OAEP（Optimal Asymmetric Encryption Padding，推荐）
- PSS（Probabilistic Signature Scheme）

### 第9-10章 DH / ECDH 密钥协商

**DH：** 离散对数假设，参数可复用（需安全素数）
**ECDH：** 椭圆曲线 Diffie-Hellman，更短密钥等价安全性

**mbedtls 曲线支持：** P-256, P-384, P-521, Curve25519, secp256k1

### 第11章 数字签名（RSA/DSA/ECDSA）

**ECDSA：** 椭圆曲线数字签名算法，比 RSA/DSA 更快更短
- 签名：(r, s) 元组
- 验证：e = u1 = r mod n, e2 = u2 = g·r^{-1} mod n

### 第12章 X.509 证书

**证书结构：** TBSCertificate + SignatureAlgorithm + SignatureValue
**证书链验证：** 信任锚 → 中间 CA → 终端实体
**mbedtls：** `mbedtls_x509_crt_parse()` → 解析 PEM/DER，验证签名链

### 第13章 移植与性能

**移植要点：**
- entropy 源（硬件 TRNG）
- 网络发送/接收回调
- 内存分配（可使用静态内存池）

**性能数据（STM32F4 平台）：**
| 算法 | 操作 | 性能 |
|------|------|------|
| SHA-256 | 1KB | ~0.1 ms |
| AES-128-GCM | 1KB | ~0.3 ms |
| RSA-2048 sign | — | ~300 ms |
| ECDSA P-256 sign | — | ~15 ms |

### 第14章 TLS

**TLS 设计目标：** 身份认证、机密性、完整性
**密码套件协商：** ClientHello 发送偏好列表，ServerHello 选定
**握手过程：**
1. ClientHello → ServerHello → Certificate → ServerHelloDone
2. ClientKeyExchange → ChangeCipherSpec → Finished
3. Application Data

**mbedtls TLS 客户端/服务器示例：**
- `ssl_client2` / `ssl_server2` 测试工具
- 自定义配置：启用/禁用特定协议版本和密码套件

### 第15章 DTLS

**DTLS vs TLS 的关键差异：**
- 无连接（UDP），需要处理丢包和重排序
- Cookie 机制防止 DoS
- 添加 Epoch 和 Sequence Number 处理重放
- Handshake 消息需要分片和重组

**PSK（Pre-Shared Key）模式：** 无需证书，适合资源受限的 IoT 设备

### 第16章 CoAPs

**CoAP（Constrained Application Protocol）：**
- 类似 HTTP 的 REST 协议，专为 IoT 设计
- CoAPs = CoAP + DTLS，安全传输层
- 对比 HTTPS：更轻量，无 TCP 开销

## 相关页面

- [[security-index]] — 安全与密码学导航
- [[sources/pdf-security-crypto-books-updated]] — mbedtls/OpenSSL/Bulletproof TLS 系列
- [[sources/pdf-crypto-books]] — 图解密码技术 + OpenSSL Cookbook
- [[entities/security/commercial-cryptography]] — 国密算法 SM2/SM3/SM4
- [[kernel-subsystems-index]] — 内核密码学子系统（crypto API）
- [[lwip-index]] — lwIP 嵌入式协议栈（可与 mbedtls 集成）