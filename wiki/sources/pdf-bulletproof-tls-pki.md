---
type: source
source-type: pdf
title: "Bulletproof TLS and PKI, Second Edition"
author: "Ivan Ristić"
date: 2022
size: medium
path: raw/PDFs/books/bulletproof-tls-and-pki-2nbsped-9781907117091.pdf
summary: "Feisty Duck 权威 TLS/PKI 部署指南（504页），涵盖 SSL/TLS 密码学基础、TLS 1.2/1.3 协议、TLS 配置、HTTPS 部署、PKI 证书管理、OpenSSL 实战、安全评估与攻击防护"
tags: [security, tls, ssl, pki, cryptography, books]
created: 2026-05-27
sources: []
---

# Bulletproof TLS and PKI, Second Edition

## 概述

**Author:** Ivan Ristić（Qualys / FoxyProxy / Feisty Duck）
**Edition:** 2nd Edition (build 1121, January 2022)
**Pages:** 504
**Coverage:** SSL/TLS 完整生命周期 — 密码学基础、协议分析、安全配置、PKI 证书管理、部署实践

---

## 核心内容

### 第1章 SSL/TLS 与密码学基础

**Transport Layer Security 演进：**
- SSL 2.0（1994，已废弃）→ SSL 3.0（1996，已废弃）→ TLS 1.0 → TLS 1.1 → TLS 1.2 → TLS 1.3（2018）
- 每个版本的已知漏洞：POODLE（BSSL 3.0）、BEAST（TLS 1.0 CBC）、ROBOT（RSA PKCS#1 v1.5）、CRIME（TLS 压缩）等

**对称加密：**
- Block Cipher：AES（128/192/256-bit）、ChaCha20-Poly1305
- Mode of Operation：CBC（易受Padding Oracle攻击）、GCM（authenticated encryption）、CCM、Poly1305
- 认证加密（AEAD）：同时提供 Confidentiality + Integrity

**公钥密码学：**
- RSA：PKCS#1 v1.5 padding（危险，易受 Bleichenbacher 攻击）→ OAEP（安全替代）
- ECC：ECDHE/ECDSA，P-256/P-384/P-521 曲线
- Diffie-Hellman：DH 参数生成（安全素数 vs unsafe primes），ECDH 曲线推荐

**密钥派生：**
- HKDF（HMAC-based Key Derivation Function）：TLS 1.3 的核心 KDF
- PRF（Pseudo-Random Function）：TLS 1.2 的密钥派生
- TLS 1.3: `HKDF-Expand-Label` 标准化密钥派生

**数字签名与 MAC：**
- HMAC → AEAD 的演进（简化协议，减少攻击面）
- TLS 1.3 移除了 CBC 模式（彻底解决 Lucky13 等攻击）

### 第2章 TLS 协议详解

**TLS 1.3 改进：**
- 1-RTT（vs TLS 1.2 的 2-RTT）：连接建立更快
- 0-RTT（0-RTT Data）：允许在第一次握手中发送应用数据（replay 风险）
- 删除 CBC 模式、RC4、TLS 1.2 压缩、静态 RSA/DH 密钥交换
- 前向保密（Forward Secrecy）强制要求：仅支持 (EC)DHE 密钥交换
- 简化握手：ClientHello → ServerHello → [Encrypted Extensions] → [Certificate] → [CertificateVerify] → Finished

**Record Protocol：**
- TLS 1.3 统一使用 AEAD（AES-GCM、ChaCha20-Poly1305）
- 密钥更新机制（Key Update）

**Session Resumption：**
- TLS 1.2：Session ID / Session Ticket
- TLS 1.3：PSK（Pre-Shared Key）+ PSK Exchange

### 第3章 TLS 1.2 协议

**Handshake 流程：**
1. ClientHello → ServerHello → Certificate → ServerHelloDone
2. 可选：CertificateRequest（双向认证）
3. ClientKeyExchange → ChangeCipherSpec → Finished
4. Application Data

**DHE vs ECDHE：**
- DHE：基于离散对数，参数可复用，性能较低（~1-2x slower）
- ECDHE：基于椭圆曲线，性能更高，推荐使用 P-256/P-384

### 第4章 PKI（公钥基础设施）

**证书链：**
- Root CA → Intermediate CA → End-entity Certificate
- 证书验证路径：信任锚 → 中间 → 终端

**证书类型：**
- DV（Domain Validation）：域名验证，最快最便宜
- OV（Organization Validation）：组织验证
- EV（Extended Validation）：扩展验证（浏览器地址栏绿色，但 2020 年后大多数 CA 停止签发）

**证书格式：**
- DER（binary）/ PEM（base64）
- PKCS#12 / PFX（公钥+私钥+证书链）
- ACME 协议（Let's Encrypt 自动续期）

**OCSP（Online Certificate Status Protocol）：**
- 实时检查证书撤销状态
- Must-Staple 扩展：强制要求服务器提供 OCSP 响应

### 第5章 安全配置

**推荐配置（2022+）：**
- TLS 1.3 only（最佳安全）或 TLS 1.2 + TLS 1.3
- Cipher Suites：`TLS_AES_128_GCM_SHA256` / `TLS_AES_256_GCM_SHA384` / `TLS_CHACHA20_POLY1305_SHA256`
- Elliptic Curves：`secp256r1`（P-256）、`secp384r1`（P-384）、`x25519`

**Hardening Checklist：**
- 禁用 TLS 1.0/1.1、SSL 2.0/3.0
- 禁用 RC4、3DES、eNULL、aNULL
- 禁用 TLS 压缩（CRIME 攻击）
- 启用 HSTS（HTTP Strict Transport Security）
- 启用 OCSP Stapling
- 配置 ALPN（Application-Layer Protocol Negotiation）
- 正确配置 DH 参数（安全素数 ≥2048-bit）或切换到 ECDHE

### 第6章 HTTPS 部署

**服务器证书配置：**
- Nginx / Apache / HAProxy 配置示例
- 私钥保护：`chmod 600 private.key`，使用 HSM
- 证书链完整性验证

**HTTP/2 与 TLS：**
- HTTP/2 必须使用 TLS
- ALPN 协商：h2（HTTP/2）、http/1.1

**性能优化：**
- Session Tickets 多实例场景问题
- OCSP Stapling 减少 RTT
- 证书链长度影响 TLS 握手时间

### 第7章 测试与评估

**工具：**
- `openssl s_client`：连接测试、协议版本检测、证书链验证
- `testssl.sh`：全面 TLS 配置扫描
- `SSLyze`：Python TLS 分析库
- `Qualys SSL Labs SSL Test`：在线评分工具

**攻击场景：**
- POODLE：SSL 3.0 CBC 填充oracle
- BEAST：TLS 1.0 CBC 压缩边信道
- CRIME/BREACH：TLS 压缩攻击
- ROBOT：RSA PKCS#1 v1.5 Bleichenbacher oracle
- Heartbleed：OpenSSL 心跳扩展缓冲区溢出
- FREAK/Logjam：DH 参数出口限制攻击
- Sweet32：64-bit 块密码生日攻击
- ROBOT / Lucky13：填充oracle攻击

## 相关页面

- [[security-index]] — 安全与密码学导航
- [[sources/pdf-crypto-books]] — 图解密码技术 + OpenSSL Cookbook
- [[sources/pdf-security-crypto-books-updated]] — mbedtls / OpenSSL / Bulletproof TLS
- [[entities/security/commercial-cryptography]] — 国密算法 SM2/SM3/SM4
- [[kernel-subsystems-index]] — 内核密码学子系统（crypto API）