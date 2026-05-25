---
type: entity
tags: [security, tls, dtls, pki, x509, ssl, cryptography, certificate, 加密套件]
created: 2026-05-25
sources: [pdf-security-crypto-books-updated]
---

# Bulletproof TLS and PKI

## 定义
Bulletproof TLS and PKI是Ivan Ristić(Feisty Duck)所著的权威TLS/DTLS/PKI部署指南，涵盖从密码学基础到生产环境部署的完整知识体系。

## 关键要点

### SSL/TLS协议演进
| 版本 | 年份 | 关键特性 |
|------|------|---------|
| SSL 2.0 | 1994 | 首个SSL实现，已废弃(多项漏洞) |
| SSL 3.0 | 1996 | 重写，POODLE攻击废弃 |
| TLS 1.0 | 1999 | 首个标准版本，BEAST攻击风险 |
| TLS 1.1 | 2006 | IV显式化，防BEAST |
| TLS 1.2 | 2008 | AEAD加密(GCM/CCM)，SHA-2 |
| TLS 1.3 | 2018 | 0-RTT, 1-RTT, 加密握手, 废弃RSA/3DES |

### 密码学基础
- **对称加密**: AES(首选, 256-bit)/ChaCha20(移动设备首选)/3DES(废弃)
- **非对称加密**: RSA(密钥交换+签名)/ECDSA/ECDH(椭圆曲线)
- **哈希**: SHA-2(SHA-256/384/512, TLS 1.2+)/SHA-3
- **MAC/HMAC**: 消息认证，HMAC-SHA-256
- **密钥派生**: PBKDF2(密码存储), HKDF(TLS密钥导出)

### TLS 1.3关键改进
- **Encrypted Hello**: 服务器证书加密传输
- **PSK (Pre-Shared Key)**: 0-RTT恢复，延迟极低
- **废弃算法**: RSA密钥交换、3DES、静态DH、RC4、AES-CBC
- **仅支持AEAD**: AES-GCM、ChaCha20-Poly1305
- **握手从2-RTT→1-RTT**: 性能显著提升

### PKI体系
- **X.509证书**: Subject/Issuer, 公钥, 有效期, 签名
- **证书链**: Root CA → Intermediate CA → End-entity
- **证书透明度(CT)**: Certificate Transparency日志防CA欺诈
- **OCSP**: 在线证书状态协议，替代CRL
- **HSTS**: HTTP Strict Transport Security

### 常见协议攻击
- **BEAST**(TLS 1.0): CBC初始化向量可预测
- **POODLE**(SSL 3.0): CBC填充oracle
- **CRIME**(TLS压缩): 压缩侧信道
- **BREACH**(HTTP压缩): gzip侧信道
- **Lucky13**: CBC填充时序攻击
- **Sweet32**: 3DES 64-bit块大小碰撞
- **ROCA**: RSA密钥生成软肋(ROCA漏洞)

## 相关概念
- [[entities/linux/security/openssl-tls-library]] — OpenSSL TLS实现
- [[entities/security/mbedtls-crypto]] — 嵌入式TLS/DTLS库
- [[entities/security/commercial-cryptography]] — 国密SM2/SM3/SM4
- [[security-index]] — 安全模块总览
- [[kernel-subsystems-index]] — Linux内核crypto子系统

## 来源
- [[sources/pdf-security-crypto-books-updated]] — Bulletproof TLS/PKI, OpenSSL攻略, mbedtls开发实战
