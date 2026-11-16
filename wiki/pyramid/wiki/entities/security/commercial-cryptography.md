---
type: entity
tags: [security, crypto, china, commercial-cryptography, compliance]
created: 2026-05-23
sources: [pdf-security-crypto-books]
---

# Commercial Cryptography (商用密码)

## Definition

Commercial cryptography (商用密码) refers to cryptographic algorithms, products, and services used for non-national-secret purposes in China. The **Commercial Cryptography Administration** under the State Cryptography Administration (SCA/国密局) oversees standards, certification, and security assessment.

## Key Algorithms (国密标准)

| Algorithm | Type | Standard | Key Size |
|-----------|------|----------|----------|
| SM2 | Elliptic Curve PKC | GM/T 0003-2012 | 256-bit |
| SM3 | Cryptographic Hash | GM/T 0004-2012 | 256-bit digest |
| SM4 | Block Cipher | GM/T 0002-2012 | 128-bit key, 128-bit block |
| SM9 | Identity-Based Crypto | GM/T 0078-2019 | — |

## Security Assessment (密评)

The **Commercial Cryptography Application Security Assessment** (商用密码应用安全性评估) is a mandatory evaluation for critical information infrastructure in China:

- **Scope**: Government systems, finance, energy, transportation, telecommunications
- **Evaluation**: Cryptographic algorithm correctness, key management, protocol implementation
- **Levels**: Basic (1) → Advanced (4)
- **Certification**: Pass the national examination to become a certified assessor

## Related Pages

- [[entities/security/mbedtls-crypto]] — mbedtls supports SM2/SM3/SM4
- [[entities/arm/trustzone-op-tee]] — TEE for secure key storage (PKI/国密)
- [[entities/linux/kernel/index]] — Linux kernel crypto (SM algorithms support)

## Source Details

- [[sources/pdf-security-crypto-books]] — 商用密码应用安全性评估考核题
