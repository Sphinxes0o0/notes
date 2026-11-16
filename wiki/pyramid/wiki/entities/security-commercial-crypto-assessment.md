---
type: entity
tags: [security, crypto, commercial-crypto, china, gm-cipher, pki, compliance]
created: 2026-05-27
sources: [pdf-commercial-crypto-assessment]
---

# Commercial Cryptographic Security Assessment (密评)

## Definition

Commercial Cryptographic Application Security Assessment (商用密码应用安全性评估，简称密评) is China's mandatory security evaluation framework for systems using commercial (domestic) cryptography. It ensures compliance with GM (Guomi) cipher algorithms and national security standards.

## Key Concepts

### Chinese Commercial Cipher Algorithms (国密)

| 算法 | 类型 | 标准 |
|------|------|------|
| **SM1** | 对称分组密码 | AES等价，硬件实现 |
| **SM2** | 公钥密码（椭圆曲线） | ECDSA等价，256-bit |
| **SM3** | 密码学哈希 | SHA-256等价 |
| **SM4** | 对称分组密码 | AES等价，128-bit |
| **SM9** | 标识密码 | IBC (Identity-Based Cryptography) |

### Assessment Coverage

- **Algorithm compliance**: SM2/SM3/SM4 correct implementation
- **Key lifecycle**: generation → distribution → storage → destruction
- **Protocol security**: TLS/SM9 protocol correctness
- **System integration**: cipher integration with application systems
- **Level protection 2.0**: 等级保护2.0密码应用要求

### Assessment Process

1. **Preparation phase**: scope definition, documentation review
2. **Plan drafting**: assessment criteria and test cases
3. **On-site evaluation**: penetration testing, key management audit
4. **Report generation**: compliance verdict with remediation recommendations

## Related Pages

- [[sources/pdf-security-crypto-books]] — 安全密码学书籍合集（SM系列算法参考）
- [[entities/linux/security/linux-security-observability-ebpf]] — 安全可观测性
- [[entities/linux/kernel/index]] — 内核密码学子系统
- [[sys-prog-index]] — 系统编程（密码学应用）

## Source Details

- [[sources/pdf-commercial-crypto-assessment]] — 商用密码应用安全性评估考核题