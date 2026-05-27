---
type: index
tags: [security, crypto, cryptography, tls, embedded-security]
created: 2026-05-23
updated: 2026-05-25
---

# Security & Cryptography

> Cryptographic algorithms, protocols, libraries, and security frameworks

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/security/commercial-cryptography]] | 商用密码：SM2/SM3/SM4/SM9 algorithms, 密码应用安全性评估 (密评) | security, crypto, china, commercial-cryptography, compliance |
| [[entities/security/mbedtls-crypto]] | mbedtls: lightweight TLS/DTLS library for IoT, X.509, PKCS#11 | security, crypto, mbedtls, iot, tls |
| [[entities/linux/security/bulletproof-tls-pki]] | TLS/DTLS/PKI权威指南：协议演进(TLS1.0→1.3)、密码学基础、PKI体系、攻击案例 | security, tls, pki, x509, cryptography |
| [[entities/linux/security/openssl-tls-library]] | OpenSSL：libcrypto密码算法库 + libssl TLS栈 + 命令行工具，vs mbedtls对比 | security, openssl, tls, ssl, pki |
| [[entities/linux/security/linux-security-observability-ebpf]] | eBPF内核安全可观测性：Apple Falco/Google KRSI/Isovalent/saBPF容器审计 | security, ebpf, observability, cloud-native, falco, krsi |
| [[entities/linux/security/linux-security-ptpsec]] | PTPsec：IEEE 1588延迟攻击检测，循环路径不对称性分析，INFOCOM 2024 | security, ptp, time-sync, ieee1588, delay-attack |

## Sources

| Source | Description | Date |
|--------|-------------|------|
| [[sources/pdf-security-crypto-books-updated]] | 安全与密码学更新3册：mbedtls开发实战、OpenSSL攻略、Bulletproof TLS/PKI | 2026-05 |
| [[sources/pdf-security-crypto-books]] | 安全与密码学6册（历史）：Bulletproof TLS/PKI、mbedtls、TrustZone/OP-TEE、商用密码考核 | 2026-05 |
| [[sources/pdf-security-papers-ebpf]] | eBPF安全论文3篇：Rootkit攻防、Apple Falco、Google KRSI BPF审计 | 2021-2024 |
| [[sources/pdf-isovalent-security-observability]] | Isovalent O'Reilly报告：eBPF Four Golden Signals云原生安全可观测性 | 2022 |
| [[sources/pdf-sabpf-container-audit]] | saBPF SoCC 2021论文：eBPF容器级LSM审计，零内核修改 | 2021 |
| [[sources/pdf-ptp-security]] | PTPsec INFOCOM 2024：IEEE 1588时间同步延迟攻击检测与缓解 | 2024 |
| [[sources/pdf-infocom-ptpsec]] | PTPsec 详解：循环路径不对称分析、Meas消息、冗余路径RTT测量、静态/增量攻击缓解 | 2024 |

## Cross-References

- [[kernel-subsystems-index]] — Linux kernel crypto subsystem (crypto_alg, skcipher, aead)
- [[arm-index]] — TrustZone & OP-TEE for hardware security isolation
- [[ebpf-index]] — eBPF security observability (Falco, KRSI, LSM)
- [[sources/notes-security]] — Security tools (Masscan, Falco, Snort)
