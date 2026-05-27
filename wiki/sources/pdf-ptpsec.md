---
type: source
source-type: pdf
title: "PTPsec: Secure PTP for Time-Sensitive Networks"
author: "Unknown (INFOCOM 2024)"
date: 2024
size: medium
path: raw/PDFs/papers/2024-INFOCOM-PTPsec.pdf
summary: "PTPsec introduces cryptographic authentication to IEEE 1588 PTP to secure time synchronization in time-sensitive networks, addressing replay attacks and man-in-the-middle threats."
created: 2026-05-27
---

# PTPsec: Secure PTP for Time-Sensitive Networks

## Core Content

PTPsec is a security extension to IEEE 1588 Precision Time Protocol, designed for Time-Sensitive Networks (TSN) and 5G/6G fronthaul. It adds identity-based authentication using a novel key management scheme tailored to PTP's unicast/mixed communication model.

### Key Contributions

- **Threat Model**: Addresses replay attacks (delayed sync messages), man-in-the-middle attacks on path delay measurements, and spoofing of grandmaster clocks.
- **Authentication Mechanism**: Uses Elliptic Curve Digital Signature Algorithm (ECDSA) with lightweight certificates. Sync/Follow_Up messages are authenticated; Pdelay messages use a separate session key.
- **Key Management**: Hierarchical key structure with group keys for multicast domains and pairwise keys for unicast links. Keys distributed via a dedicated secure channel using a custom Handshake protocol.
- **Performance**: Designed for minimal latency overhead (<100ns added to sync intervals). Evaluated on FPGA-based PTP endstations.
- **Interoperability**: Backward compatible with standard IEEE 1588 — security is negotiated at startup and falls back to unauthenticated mode if peers don't support it.

### Key Findings

- Standard PTP has no built-in security — all timing messages are unauthenticated and can be forged.
- Symmetric key approaches fail at scale in large TSN networks due to key distribution complexity.
- Identity-based cryptography enables efficient group authentication for multicast sync messages.

## Source Details

- **Conference**: IEEE INFOCOM 2024
- **Path**: raw/PDFs/papers/2024-INFOCOM-PTPsec.pdf
- **Size**: 838.4 KB