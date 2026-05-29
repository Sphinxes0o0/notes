---
type: entity
tags: [security, openssl, tls, ssl, pki, x509, cryptography, command-line]
created: 2026-05-25
sources: [pdf-security-crypto-books-updated]
---

# OpenSSL TLS Library

## 定义
OpenSSL是互联网基础设施中最重要、最广泛使用的开源密码学库和SSL/TLS/PKI实现，包括高性能密码学算法、完整SSL/TLS/DTLS栈和命令行工具。

## 关键要点

### OpenSSL项目组成
1. **libcrypto**: 密码学算法库
   - 对称加密(AES, DES, 3DES, ChaCha20, Blowfish)
   - 非对称加密(RSA, DSA, ECDSA, ECDH, DH)
   - 哈希函数(MD5, SHA-1, SHA-2, SHA-3)
   - 密钥派生(PBKDF2, HKDF, ECKDF)
   - 随机数生成(Fortuna, /dev/urandom)
   - X.509证书处理

2. **libssl**: SSL/TLS/DTLS协议栈
   - SSL 2.0/3.0, TLS 1.0/1.1/1.2/1.3
   - DTLS 1.0/1.2
   - 客户端/服务器端实现

3. **openssl命令行工具**
   - `openssl genrsa`, `openssl genpkey` — 密钥生成
   - `openssl req` — CSR生成
   - `openssl x509` — 证书操作
   - `openssl dgst` — 摘要计算
   - `openssl enc` — 对称加密
   - `openssl s_server`, `openssl s_client` — SSL测试服务器/客户端
   - `openssl s_time` — TLS性能测试

### OpenSSL的缺点
- 文档质量差(互联网上大量过时/错误资料)
- 历史代码包袱(SSL 2.0/3.0遗留)
- Heartbleed漏洞(2014)暴露维护问题
- 配置复杂，容易误用

### OpenSSL测试工具链
- **SSL Labs SSL Test**: 在线TLS配置检测 (ssllabs.com/ssltest)
- **testssl.sh**: 命令行TLS审计
- **openssl s_client**: 手动TLS握手测试
- **openssl s_server**: 临时HTTPS服务器

### OpenSSL vs mbedTLS
| 方面 | OpenSSL | mbedTLS |
|------|---------|---------|
| 目标平台 | 服务器/桌面 | 嵌入式/IoT |
| 代码规模 | ~500K行 | ~60K行 |
| 证书格式 | X.509, PKCS#12, PEM | X.509, PKCS#12, PEM |
| TLS版本 | TLS 1.0-1.3 | TLS 1.2, DTLS 1.2 |
| 认证 | 商业认证支持 | 仅GPL许可 |

## 相关概念
- [[entities/linux/security/bulletproof-tls-pki]] — TLS/PKI部署权威指南
- [[entities/security/mbedtls-crypto]] — 嵌入式TLS/DTLS
- [[entities/security/commercial-cryptography]] — 国密SM2/SM3/SM4
- [[security-index]] — 安全模块总览
- [[entities/linux/kernel/index]] — Linux内核crypto子系统

## 来源
- [[sources/pdf-security-crypto-books-updated]] — OpenSSL攻略(Bulletproof TLS/PKI同作者)
