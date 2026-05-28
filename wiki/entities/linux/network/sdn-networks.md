---
type: entity
tags: [linux, networking, sdn, openflow, control-plane, data-plane, network-operating-system, bare-metal-switch]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# Software-Defined Networks (SDN)

## Definition

SDN (Software-Defined Networking) is an **implementation strategy** that physically separates the **control plane** (where routing algorithms like OSPF, BGP run) from the **data plane** (where packet forwarding decisions are made). The control plane runs as software on commodity servers (the SDN controller), while the data plane (switches/routers) applies the installed flow rules.

## Core Concepts

### Control Plane vs Data Plane

**Data plane**: Per-packet processing — receiving a packet, looking up header fields in a forwarding table, and sending it toward the appropriate output. Performed at line rate; must be extremely fast.

**Control plane**: Distributed algorithms (OSPF, RIP, BGP) that compute the forwarding tables. Runs periodically or reacts to topology changes. Historically ran on the same device as the data plane.

SDN **decouples** these two, allowing the control plane to be centralized (logically) while data plane remains distributed at each switch.

### OpenFlow

The original SDN interface (circa 2008) between control and data planes. A switch maintains a **flow table** of `(match fields, actions)` rules. The controller programs these rules via the OpenFlow protocol (over TLS/SSL).

**Match fields**: Any packet header field — src/dst MAC, VLAN ID, IP src/dst, TCP/UDP ports, etc.

**Actions**: Forward to port(s), drop, send to controller, modify header fields, push/pop VLAN tags, etc.

**Flow table miss**: If no rule matches, the packet is typically sent to the controller (which may install a new rule or respond).

### Network Operating System (NOS)

A NOS (e.g., ONOS, OpenDaylight) is to a network what Linux/Windows is to a server. It:
- Maintains a **network-wide view** (the Network Map abstraction)
- Detects topology changes (switches/links up/down)
- Provides **northbound APIs** (REST, etc.) for control applications
- Programs forwarding rules into switches via southbound protocols (OpenFlow, P4)

The NOS abstracts the distributed nature of the network, allowing developers to write control apps that reason about the global topology.

### Bare-Metal Switches

A commodity switch with open hardware specs (e.g., via OCP — Open Compute Project) running a disaggregated, open-source switch OS (e.g., SONiC, OpenSwitch). The switch OS runs a full control plane stack (BGP, OSPF, etc.) and exposes OpenFlow/P4 interfaces for custom control apps.

**NPU-based switches**: Network Processing Units with programmable forwarding pipelines, TCAM for wildcard matching, SRAM buffering. P4 programs the pipeline for protocol-independent forwarding.

## Why SDN Matters for NIDS

- **Centralized policy enforcement**: An IDS/switch can have flow rules pushed by a security controller — dynamic quarantine of infected hosts, automatic insertion of inline inspection points.
- **In-band network telemetry**: SDN switches can mirror specific flows to IDS sensors without affecting the forwarding path.
- **Programmable parsing**: P4 switches can be programmed to extract specific header fields for deep inspection.
- See [[entities/linux/network/tc-ebpf-direct-action]] for Linux TC eBPF direct-action mode — a software SDN-like data plane approach.

## Related Pages

- [[entities/linux/network/tc-ebpf-direct-action]] — Linux TC eBPF direct-action (data plane programming)
- [[entities/linux/network/modern-lb-proxy]] — SDN-style load balancing with Katran (Facebook)
- [[sources/arthurchiao-facebook-xdp-to-socket]] — XDP/eBPF for programmable packet processing
- [[sources/arthurchiao-tc-da-mode]] — TC eBPF for policy enforcement
