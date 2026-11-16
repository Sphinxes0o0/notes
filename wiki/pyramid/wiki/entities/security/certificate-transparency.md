---
type: entity
tags: [security, tls, ssl, certificate-transparency, pki, ct, cryptography]
created: 2026-05-28
sources: [arthurchiao-pki]
---

# Certificate Transparency (CT)

## 定义

Certificate Transparency（证书透明度）是 Google 提出的开源框架，通过公开的 CT Log 服务器记录所有公开信任的 SSL/TLS 证书，让域名所有者能够监控其域名证书的颁发情况，及时发现未经授权的证书。

## 核心组件

- **CT Log Server**: 记录证书的公开日志服务器，使用 Merkle Tree 结构
- **CT Monitor**: 监控 CT Log，发现可疑证书后告警
- **CT Auditor**: 验证证书是否被正确记录到 CT Log

## 用途

- **检测未授权证书**: 发现恶意第三方申请的证书
- **证书颁发审计**: 确保 CA 按规范颁发证书
- **浏览器信任验证**: Chrome 等浏览器要求 EV 证书必须嵌入 SCT

## 相关概念

- [[entities/security/pki-certificates]] — PKI 证书体系
- [[entities/security/tls-handshake]] — TLS 握手过程
