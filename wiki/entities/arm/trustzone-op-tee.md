---
type: entity
tags: [security, arm, trustzone, tee, op-tee, mobile-security]
created: 2026-05-23
sources: [pdf-security-crypto-books]
---

# TrustZone & OP-TEE

## Definition

ARM TrustZone is a hardware security extension that creates a **Trusted Execution Environment (TEE)** — a secure, isolated region of the SoC where sensitive code and data can run protected from the main OS. OP-TEE is the open-source TEE implementation for TrustZone.

## Key Concepts

### TrustZone Architecture
- **Two Worlds**: Normal World (Rich OS: Linux/Android) vs Secure World (TEE OS: OP-TEE)
- **Monitor Mode**: Gatekeeper between worlds, entered via SMC (Secure Monitor Call)
- **Hardware Isolation**: AXI bus security state bit, TZASC (TrustZone Address Space Controller), TZMA, TZPC
- **Memory Isolation**: Secure RAM/ROM, DRAM partitioning via TZASC
- **Interrupt Isolation**: Secure interrupts handled in Secure World

### OP-TEE Components
- **TEE Kernel**: Secure OS kernel running in Secure World
- **Trusted Applications (TAs)**: Secure services (DRM, payment, biometrics)
- **Client Applications (CAs)**: Normal World apps requesting secure services
- **tee_supplicant**: Normal World daemon for TA loading and RPC
- **ATF (ARM Trusted Firmware)**: bl1/bl2/bl31/bl32 boot stages

### TrustZone on ARMv8
- **EL3** (Monitor): Highest privilege, world switching
- **S-EL1/S-EL2**: Secure World exception levels
- **NS-EL1/NS-EL2**: Normal World exception levels

## Related Pages

- [[sources/pdf-arm-architecture]] — ARM architecture reference
- [[entities/security]] — Security tools and concepts
- [[kernel-subsystems-index]] — Kernel crypto subsystem
- [[sources/pdf-trustzone-optee]] — 手机安全和可信应用开发指南（786页权威著作）
- [[sources/pdf-commercial-crypto-assessment]] — 商用密码评估考核题
- [[entities/security-commercial-crypto-assessment]] — 中国商用密码应用安全性评估

## Source Details

- [[sources/pdf-security-crypto-books]] — 手机安全和可信应用开发指南
