---
type: entity
tags: [linux, networking, vpn, tls, ipsec, tls, ssl, ssh, pgp, firewall, pki, cryptography, key-exchange]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# Network Virtualization and Security

## Definition

This entity covers two interrelated topics from the Systems Approach textbook: (1) **network virtualization** (VPNs, tunnels, overlays) for creating logical networks over shared physical infrastructure, and (2) **network security** (cryptographic building blocks, key distribution, authentication protocols, and security systems).

## Network Virtualization

### Tunnels and VPN

A **virtual private network (VPN)** creates a private logical network over a shared public network. The key mechanism is **tunneling**: encapsulating one protocol (inner IP) inside another (outer IP), with optional encryption.

**IP Tunnel**: Router at tunnel entrance encapsulates `inner IP(packet)` inside `outer IP(header)` with the tunnel endpoint's address as the destination. At the tunnel exit, the outer header is stripped and the inner packet is forwarded normally.

**Tunnel vs Transport mode**: In **tunnel mode**, the entire original packet (including original IP header) is encrypted and encapsulated. In **transport mode**, only the payload is encrypted; the original IP header is left intact (used for IPsec host-to-host).

### Overlay Networks

Overlay networks (VXLAN, Geneve, NVGRE) create virtual L2 segments over L3 infrastructure — critical for virtualized data centers where VMs need to communicate across hosts as if on the same physical L2.

**VXLAN**: Stretches an L2 segment over an L3 network using UDP encapsulation. A 24-bit **VNI** (VXLAN Network Identifier) replaces the VLAN ID, allowing 16M virtual segments vs 4096 VLANs.

## Cryptographic Building Blocks

### Secret-Key (Symmetric) Ciphers

Both parties share a key `K`. Encryption and decryption are both `O(1)` operations — fast. Used to encrypt bulk data.

**Block ciphers**: AES, DES. Operate on fixed-size blocks (128 bits for AES). Modes: ECB (insecure), CBC (block chaining), GCM (authenticated encryption).

**Stream ciphers**: RC4 (broken), ChaCha20. XOR keystream with plaintext. Must never reuse a keystream ( nonce + key must be unique per message).

### Public-Key (Asymmetric) Ciphers

Each party has a key pair: **public key** (known to all) and **private key** (secret). RSA, ECC. Operations are expensive (~1000× slower than symmetric). Used for: key exchange, digital signatures, encrypting small messages (e.g., session keys).

**Hybrid encryption**: Generate a random session key `S`; encrypt `S` with the recipient's public key. Encrypt bulk data with `S` using a symmetric cipher. The recipient decrypts `S` with their private key, then decrypts the data.

### Authenticators (MAC / Hash-based)

An **authenticator** (MAC — Message Authentication Code) allows a recipient to verify that a message was not tampered with and originated from someone who knows the shared key.

- **HMAC**: Hash-based MAC using a cryptographic hash function + secret key
- **CMAC/GMAC**: Block cipher-based MAC (AES-GCM provides authenticated encryption)

**Digital signatures**: Like a MAC but uses the sender's private key — allows anyone with the public key to verify, proving the signer authored the message.

### Cryptographic Hash Functions

SHA-256, SHA-3. One-way function producing a fixed-size digest. Used in: MAC constructions, commitment schemes, proof-of-work, integrity verification.

## Key Distribution

### PKI (Public Key Infrastructure)

A **certification authority (CA)** signs certificates binding a public key to an identity (hostname, organization). Trust stores (browsers, OS) contain root CA certificates. Certificate chain validation walks from root → intermediate → leaf.

**mTLS**: Mutual TLS — both client and server present certificates, each authenticating the other. Used for [[sources/arthurchiao-pki]]-based service mesh authentication.

### Diffie-Hellman Key Exchange

Allows two parties to establish a shared secret over a public channel without prior shared secrets. Based on the hardness of the discrete logarithm problem.

**Elliptic Curve DH (ECDH)**: Same idea but over elliptic curve groups — smaller key sizes for equivalent security.

## Authentication Protocols

- **Needham-Schroeder**: Classic mutual authentication protocol using a trusted key distribution center (KDC). Basis for Kerberos.
- **Kerberos**: Enterprise authentication using a KDC (AS + TGS), ticket-granting tickets, time-limited credentials.
- **SSH / TLS Handshake**: Diffie-Hellman or ECDHE for key exchange, certificate-based server authentication, optional client certificates.

## Security Systems

| System | Scope | Key Mechanism |
|--------|-------|--------------|
| **TLS/SSL/HTTPS** | Transport layer | Hybrid encryption, PKI certificates, symmetric session keys |
| **IPsec** | Network layer | ESP (encryption + authentication), AH (authentication only), IKEv2 key exchange |
| **SSH** | Application layer | Public key or password auth, encrypted channel |
| **PGP/GPG** | Email | Web of trust, RSA/AES hybrid, signed then encrypted |
| **802.11i (WPA2/WPA3)** | Wireless | 4-way handshake with PTK, AES-CCMP or GCMP encryption |

### Firewalls

A **firewall** enforces access control policies by filtering traffic at the network boundary. Types:
- **Stateless packet filter**: Rules based on IP addresses, ports, TCP flags
- **Stateful firewall**: Tracks connection state (TCP state machine, UDP flows viaconntrack); rejects out-of-state packets
- **Application-layer (proxy) firewall**: Terminates and re-originates connections; understands application protocols
- **Next-generation firewall**: Deep packet inspection (DPI), intrusion prevention, application awareness

Linux Netfilter (iptables/nftables) provides the underlying primitives. See [[sources/notes-netfilter]].

## NIDS-Relevant Points

- **Encrypted traffic inspection**: TLS/HTTPS encryption hides payload content from NIDS. Solutions: TLS interception (mitm proxy), encrypted SNI/ certificate analysis, passive DPI on TLS handshake metadata.
- **IPsec tunnel mode**: Inner packets are encrypted; NIDS sees only outer IP headers unless it has the IPsec SA keys.
- **Covert channels**: DNS tunneling, ICMP tunneling, HTTP tunneling — protocols that carry data in unexpected protocol fields to bypass firewalls.
- **Firewall evasion**: Fragmentation (overlapping IP fragments), source routing, IP options, TTL manipulation.

## Related Pages

- [[sources/arthurchiao-pki]] — PKI and certificate chain analysis
- [[sources/notes-netfilter]] — Linux Netfilter/iptables/nftables/conntrack
- [[sources/pdf-openssl-cookbook]] — OpenSSL practical guide
- [[sources/pdf-commercial-crypto-assessment]] — SM密评体系
- [[entities/linux/network/tcp-congestion-control]] — ECN (congestion signaling interacts with security policies)
