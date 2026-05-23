---
type: entity
tags: [security, crypto, mbedtls, iot, tls]
created: 2026-05-23
sources: [pdf-security-crypto-books]
---

# mbedtls Cryptographic Library

## Definition

mbedtls (formerly PolarSSL) is a lightweight, portable cryptographic library designed specifically for **IoT and embedded systems**. It implements SSL/TLS/DTLS protocols, X.509 certificate handling, and a full suite of cryptographic primitives.

## Key Concepts

### Architecture
- **TLS/DTLS Protocol**: Low-footprint implementation of TLS 1.2/1.3 and DTLS
- **X.509 Certificate**: Certificate parsing, chain verification, CRL/OCSP
- **Cryptographic Primitives**: AES, RSA, ECC, SHA, HMAC, etc.
- **PKCS#11 Interface**: Hardware security module abstraction

### Comparison with OpenSSL

| Aspect | mbedtls | OpenSSL |
|--------|---------|---------|
| Footprint | ~50KB | ~2MB+ |
| Ideal Use | IoT/Embedded | Server/Desktop |
| Thread Safety | Per-context locking | Global locking |
| License | Apache 2.0 | OpenSSL/SSLeay |
| Language | C | C |

### IoT Security Stack
- **Zephyr OS**: RTOS with mbedtls integration
- **CoAP/DTLS**: Constrained application protocol over DTLS
- **TLS-PSK**: Pre-Shared Key mode for resource-constrained devices
- **Secure Boot**: ATF + OP-TEE + mbedtls for chain of trust

## Related Pages

- [[entities/arm/trustzone-op-tee]] — Hardware TEE for IoT
- [[entities/security]] — Security tools
- [[kernel-subsystems-index]] — Kernel crypto subsystem (comparison with mbedtls)

## Source Details

- [[sources/pdf-security-crypto-books]] — 密码技术与物联网安全：mbedtls开发实战
