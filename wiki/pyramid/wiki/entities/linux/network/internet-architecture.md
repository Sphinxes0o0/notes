---
type: entity
tags: [linux, networking, ip, tcp, udp, arp, dhcp, icmp, subnetting, cidr, vpn, tunnel]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# Internet Architecture

## Definition

The Internet architecture (TCP/IP architecture) is a layered network architecture that interconnecting heterogeneous networks via the Internet Protocol (IP). Its defining feature is the "hourglass" narrow-waist design — IP is the single mandatory layer that all hosts and networks must implement, enabling upper-layer protocols (TCP/UDP) and lower-layer technologies (Ethernet, WiFi, etc.) to evolve independently.

## Core Concepts

### Layering and Protocol Graph

Networks use **layering** to decompose complexity: each layer provides service to the layer above, implemented using services from the layer below. A **protocol graph** represents the dependency tree of protocol modules — e.g., HTTP → TCP → IP → Ethernet.

**Encapsulation**: Each protocol prepends a header (or appends a trailer) as it passes down the stack. The payload of each header is the complete packet from the layer above. This creates the nesting structure: `Ethernet(IP(TCP(HTTP data)))`.

**Demultiplexing keys (demux keys)**: Each protocol header contains a field that identifies which higher-level protocol or application should receive the data. TCP uses port numbers; IP uses the Protocol field.

### Internet Protocol (IP)

**Best-effort service model**: IP makes no guarantees about delivery — packets may be lost, duplicated, or reordered. Higher layers (TCP) must handle these failures.

**Datagram forwarding**: Every IP packet carries the full destination address. Routers consult a forwarding table (mapping network prefixes → next hop) to make per-packet forwarding decisions. No connection state is maintained.

**Fragmentation & Reassembly**: Different networks have different MTUs. If a packet exceeds the outgoing link MTU, the router fragments it. Fragments are reassembled only at the final destination host — not at intermediate routers.

**Global hierarchical addressing**: IP addresses have two parts — network prefix (routing) and host part (delivery). Original classful addressing (A/B/C) was replaced by **CIDR** (Classless Interdomain Routing), which uses variable-length prefix notation (e.g., `192.168.0.0/24`). Longest-prefix-match lookup enables route aggregation and scalability.

### Key Supporting Protocols

| Protocol | Role |
|----------|------|
| **ARP** | Maps IP addresses → link-layer (MAC) addresses on a single broadcast domain |
| **DHCP** | Dynamically assigns IP addresses, subnet masks, default routers to hosts |
| **ICMP** | Reports errors (destination unreachable, TTL expired) and provides `ping`/`traceroute` |
| **DNS** | Hierarchical name-to-address resolution (beyond textbook scope) |

### Subnetting & CIDR

**Subnetting** divides a classful network into smaller subnets using a subnet mask. All hosts within a subnet share the same network prefix; the subnet mask determines the boundary.

**CIDR** aggregates multiple contiguous classful networks into a single supernet with a common prefix. Enables Internet routers to store one route entry for an organization's entire address block, dramatically reducing global routing table size.

### Tunneling & VPN

An **IP tunnel** creates a virtual point-to-point link between two routers separated by arbitrary networks. The tunnel endpoint encapsulates each packet in a new IP header (outer), decapsulates at the far end, and forwards the inner packet normally.

Commonly used for: VPN security (IPsec tunnel mode), multicast routing over unicast networks, IPv6 over IPv4, and policy-based routing.

## NIDS-Relevant Points

- **Fragmentation attacks**: IP fragmentation enables evading detection — overlapping fragment payloads can bypass stateless filters. NIDS must implement proper reassembly before pattern matching.
- **Tunneling evasion**: Attackers tunnel malicious traffic inside IP tunnels or inside protocols like DNS, HTTP. [[entities/linux/network/net-stack-implementation-rx]] shows where Linux GRO/fragmentation processing occurs in the RX path.
- **ARP spoofing**: Local network man-in-the-middle via forged ARP replies — relevant to [[entities/linux/network/arp-neighbor]].
- **ICMP tunneling**: ICMP packets can carry arbitrary payloads, used for covert channels (e.g., `ping` tunnels).

## Related Pages

- [[entities/linux/network/linux-network-protocols]] — Linux IPv4/IPv6/TCP/UDP implementation
- [[entities/linux/network/network-switching]] — Switching paradigms (datagram vs virtual circuit)
- [[entities/linux/network/arp-neighbor]] — Linux ARP/neighbor subsystem
- [[entities/linux/network/congestion-control]] — BBR congestion control (related to IP best-effort)
- [[sources/arthurchiao-conntrack-design]] — Conntrack/NAT interactions with IP
- [[sources/arthurchiao-linux-net-stack-implementation-rx]] — Linux IP layer RX processing
- [[sources/reading-linux-advanced-routing-tc]] — Linux routing and TC for packet processing
