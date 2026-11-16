---
type: source
source-type: pdf
created: 2026-01-15
title: "安全与密码学书籍：Bulletproof TLS/PKI、mbedtls、TrustZone/OP-TEE、商用密码考核、OpenSSL Cookbook、图解密码技术"
author: "Ivan Ristić, 徐凯&崔红鹏, etc."
date: 2015-2024
size: large
path: raw/PDFs/books/
summary: "安全与密码学6册：Bulletproof TLS/PKI 2nd、mbedtls、TrustZone/OP-TEE、商用密码考核、OpenSSL Cookbook、图解密码技术"
tags: [security, crypto, tls, pki, mbedtls, trustzone, op-tee, openssl, sm2, sm3, sm4]
---

# 安全与密码学书籍（历史汇总）

> 安全与密码学经典书籍合集，包含 TLS/PKI、mbedtls 嵌入式安全、TrustZone/OP-TEE 可信执行环境、商用密码考核、OpenSSL Cookbook、图解密码技术。

## 核心内容

### 1. Bulletproof TLS and PKI (Ivan Ristić, 2nd Ed, 2022)

**Topics covered:**
- TLS 1.3 协议详解：0-RTT/1-RTT handshake、Encrypted Hello、PSK
- PKI 体系：X.509 证书、CA 层次结构、证书透明度(CT)、OCSP
- 密码学基础：对称加密(AES/ChaCha20)、非对称加密(RSA/ECDSA/ECDH)、哈希(SHA-2/SHA-3)
- 协议攻击：BEAST, POODLE, CRIME, BREACH, Lucky13, Sweet32, ROCA
- 部署最佳实践：协议版本选择、加密套件配置、HSTS、HPKP

### 2. 密码技术与物联网安全：mbedtls 开发实战 (徐凯&崔红鹏, 2019)

**Topics covered:**
- mbedtls 轻量级 TLS/DTLS 库架构
- 对称加密(AES/DES/3DES)、非对称加密(RSA/ECC)、哈希(MD5/SHA)
- X.509 证书与 PKI 体系
- mbedtls 在 Zephyr OS 上的移植

### 3. ARM TrustZone 与 OP-TEE 可信执行环境

**Topics covered:**
- ARM TrustZone 硬件安全隔离架构
- OP-TEE TEE OS 设计与实现
- 安全世界与普通世界的切换
- 可信应用(TA)开发

### 4. 商用密码考核 (SM2/SM3/SM4)

**Topics covered:**
- 国密 SM2 公钥密码算法
- SM3 密码杂凑算法
- SM4 分组密码算法
- 密评合规要求

### 5. OpenSSL Cookbook (Ivan Ristić, 2015-2017)

**Topics covered:**
- OpenSSL 密钥生成、证书创建、CA 构建
- SSL/TLS 服务器安全测试
- OpenSSL 命令行工具(dgst/enc/s_server)

### 6. 图解密码技术

**Topics covered:**
- 对称加密与非对称加密原理
- PKI 与数字证书
- TLS/SSL 协议工作流程
- 密码学数学基础

---

## 相关页面
- [[entities/security/mbedtls-crypto]]
- [[entities/security/commercial-cryptography]]
- [[security-index]]
- [[entities/linux/kernel/index]]
