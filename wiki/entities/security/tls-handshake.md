---
type: entity
tags: [security, tls, ssl, handshake, pki, cryptography]
created: 2026-05-28
sources: [arthurchiao-pki]
---

# TLS Handshake

## 定义

TLS Handshake 是 TLS 协议建立安全连接时的协商过程，包括协议版本协商、密码套件选择、服务器认证（可选双向认证）、密钥交换等步骤。

## 握手过程

1. **ClientHello**: 客户端发送支持的 TLS 版本、密码套件列表、随机数
2. **ServerHello**: 服务器选择版本和密码套件，发送证书和随机数
3. **(CertificateRequest)**: 服务器请求客户端证书（双向认证时）
4. **(Certificate)**: 客户端发送证书（双向认证时）
5. **ClientKeyExchange**: 客户端发送预主密钥（RSA 或 DH）
6. **(CertificateVerify)**: 客户端用私钥签名摘要验证身份
7. **Finished**: 双方切换到加密通信

## 相关概念

- [[entities/security/pki-certificates]] — PKI 证书体系
- [[entities/security/certificate-transparency]] — 证书透明度
- [[entities/security/mbedtls-crypto]] — mbedTLS 加密库
