---
type: source
source-type: pdf
created: 2026-05-25
title: "安全与密码学书籍更新：mbedtls开发实战、OpenSSL攻略、Bulletproof TLS"
author: "徐凯&崔红鹏, Ivan Ristić, etc."
date: 2019-2024
size: large
path: raw/PDFs/books/
summary: "IoT密码安全：mbedtls/TLS/DTLS/X.509；OpenSSL命令指南；Bulletproof TLS/PKI部署"
tags: [security, crypto, mbedtls, tls, dtls, openssl, iot, pkcs, x509, pki]
---

# 安全与密码学书籍：mbedtls开发实战、OpenSSL攻略、Bulletproof TLS

## 核心内容

### 1. 密码技术与物联网安全：mbedtls开发实战 (徐凯&崔红鹏, 2019)

**Topics covered:**
- **密码学工具箱**: 对称加密(AES/DES/3DES)、非对称加密(RSA/ECC)、哈希(MD5/SHA)、MAC、随机数
- **mbedtls架构**: 轻量级TLS/DTLS库，Zephyr/嵌入式Linux支持
- **TLS/DTLS协议**: SSL 3.0 → TLS 1.3演进，握手流程，会话恢复
- **X.509证书**: PKI体系，证书格式，证书链验证
- **密码学数学基础**: 数论(素数/模运算/群/域/有限域GF(2^m))，欧拉函数
- **mbedtls在Zephyr OS上的移植**: CMakeLists.txt, prj.conf, 硬件平台
- **OpenSSL简介**: 源码安装，命令行工具(dgst/enc/s_server)

### 2. OpenSSL攻略 / OpenSSL Cookbook (Ivan Ristić, 2015-2017)

**Topics covered:**
- OpenSSL是互联网基础设施安全最重要的开源项目
- **第1章**: 常规任务——密钥生成、证书生成、CA创建、SSL/TLS程序配置
- **第2章**: 测试服务器安全——底层的SSL/TLS测试方法
- 截取自《HTTPS权威指南》——SSL/TLS/PKI完整部署指南
- OpenSSL缺点：文档差、互联网上很多过时/错误资料
- SSL Labs: 作者创建的在线SSL/TLS检测工具

### 3. Bulletproof TLS and PKI (Ivan Ristić, 2nd Ed, 2022)

**Topics covered:**
- **SSL/TLS协议历史**: SSL 2.0 → SSL 3.0 → TLS 1.0/1.1/1.2/1.3
- **密码学基础**: 对称加密(AES/ChaCha20/3DES)、非对称加密(RSA/ECDSA/ECDH)、哈希(SHA-2/SHA-3)、MAC/HMAC/CMAC、密钥派生函数(PBKDF2/HKDF)
- **TLS 1.3**: 0-RTT handshake, 1-RTT handshake, Encrypted Hello, PSK
- **PKI体系**: 证书类型(X.509/CSR)、CA层次结构、证书透明度(CT)、OCSP
- **协议攻击**: BEAST, POODLE, CRIME, BREACH, Lucky13, Sweet32, ROCA
- **部署最佳实践**: 协议版本选择、加密套件配置、HSTS、HPKP、CSP
- **Active/Passive网络攻击**: MITM, replay, downgrade attacks

---

## 关键引用

> "OpenSSL虽然有很多缺点，但依旧是最成功、最重要的开源项目之一，因为大部分互联网基础设施的安全都依赖于它。" — OpenSSL攻略

> "密码学是一个独特的领域，你学的东西越多，就会发现知道的东西越少。" — Ivan Ristić

---

## 相关页面
- [[entities/security/mbedtls-crypto]]
- [[entities/linux/security/bulletproof-tls-pki]]
- [[entities/linux/security/openssl-tls-library]]
- [[entities/security/commercial-cryptography]]
- [[security-index]]
- [[kernel-subsystems-index]]
