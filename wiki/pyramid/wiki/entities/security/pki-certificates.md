---
type: entity
tags: [security, pki, certificates, tls, ca, x509, cryptography]
created: 2026-05-28
sources: [arthurchiao-pki]
---

# PKI and Certificates

## Definition

PKI (Public Key Infrastructure) is the complete ecosystem for managing public key certificates — binding names to public keys through trusted Certificate Authorities. Certificates are the "driver's licenses for computers."

## Core Concepts

| Concept | Definition |
|---------|-----------|
| **Certificate** | Public Key + Name + CA Signature |
| **CA** | Trusted issuer that signs certificates |
| **Trust Store** | Pre-configured collection of trusted root certificates |
| **Trust Chain** | Hierarchical validation from root CA → intermediate → leaf |
| **CSR** | Certificate Signing Request (PKCS#10) |
| **SAN** | Subject Alternative Name — modern naming practice |
| **mTLS** | Mutual TLS — both client and server present certificates |

## Certificate Format Ecosystem
```
ASN.1 (abstract syntax) → DER (binary encoding) → PEM (base64 with headers)
X.509 v3 (certificate structure standard)
PKCS#7 (multiple certificates, Java)
PKCS#12 (cert chain + encrypted private key, Microsoft)
```

## PKI Types
- **Web PKI**: Browser-trusted CAs (Let's Encrypt, DigiCert) for public internet
- **Internal PKI**: Custom PKI for services, containers, VMs, enterprise

## Identity Validation
| Type | Verification | Trust Level |
|------|-------------|-------------|
| **DV** | Domain control (email/DNS/HTTP) | Basic |
| **OV** | Legal entity verification | Medium |
| **EV** | Strict verification + org name in browser | Highest |

## Trust Risks
- Web PKI trusts ANY CA for ANY domain (DigiNotar 2011 breach)
- Mitigations: CAA, Certificate Transparency (CT), HPKP

## Best Practices
1. Use **SANs** for naming (DNS for machines, email for people)
2. Prefer **short-lived certificates** (24 hours or less for internal PKI)
3. Keep **private keys on subscriber machines** — never transmit
4. Don't disable certificate path validation (`curl -k` = bad)
5. **Automate certificate rotation** — expiration failures cause major incidents

## Related Pages

- [[entities/security/tls-handshake]] — TLS protocol details
- [[entities/security/certificate-transparency]] — CT logs
- [[entities/linux/network/modern-lb-proxy]] — TLS termination in proxies
