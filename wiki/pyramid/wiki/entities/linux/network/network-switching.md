---
type: entity
tags: [linux, networking, switching, datagram, virtual-circuit, ethernet, learning-bridge, spanning-tree, vlan]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# Network Switching

## Definition

Switching refers to the mechanism by which a multi-input, multi-output network device (switch) transfers packets from an input port to one or more output ports. The switch makes forwarding decisions by examining packet headers. Three primary switching paradigms exist: **datagram** (connectionless), **virtual circuit** (connection-oriented), and **source routing**.

## Switching Paradigms

### Datagram (Connectionless)

Each packet contains the complete destination address. Switches consult a **forwarding table** (routing table) to decide output port per-packet. No connection state is established beforehand.

**Characteristics**:
- Any packet can be sent at any time
- Each packet is independently routed — two consecutive packets may take different paths
- Failure resilience: if a link fails, packets can be rerouted via alternate paths
- Used by IP (the Internet)

**Trade-off**: Switches must do a per-packet table lookup; no per-flow QoS guarantees.

### Virtual Circuit (Connection-Oriented)

Two-phase model: **connection setup** (signalling) then **data transfer**. During setup, VC table entries are installed in each switch along the path. Each packet carries a short **VCI** (Virtual Circuit Identifier) — link-local scope — instead of a full address.

**VC table entry**: `(Incoming interface, Incoming VCI) → (Outgoing interface, Outgoing VCI)`

**Characteristics**:
- Setup delay of at least one RTT before data can be sent
- Per-packet overhead is low (VCI is a small integer, used as table index)
- Resources (buffers, bandwidth) can be reserved at setup time → QoS possible
- Failure of any switch/link breaks the connection
- Historical examples: X.25, Frame Relay, ATM

**Signalling**: PVC (permanent, admin-configured) or SVC (switched, dynamically established by hosts).

### Source Routing

The source host embeds the complete path (ordered list of switch ports) in each packet header. Switches read and strip/rotate the port list as the packet traverses.

**Strict source route**: every node specified. **Loose source route**: only waypoints specified.

## Ethernet Switching (L2)

### Learning Bridges

An Ethernet switch (learning bridge) automatically learns which MAC addresses are reachable on which ports by observing source addresses of incoming frames. The **forwarding table** maps `MAC address → port`.

**Processing**:
1. Frame arrives on port P
2. If destination MAC is in table → forward to that port only (unicast)
3. If destination is unknown → **flood** to all ports except P
4. Learn: record `(source MAC, port P)` in table

### Spanning Tree Algorithm (STP)

To prevent loops in a switched Ethernet with redundant links, IEEE 802.1D STP elects a **root bridge**, then computes a minimum-cost spanning tree. Ports not in the tree are **blocked** (neither forward nor learn).

**States**: Blocking → Listening → Learning → Forwarding.

Convergence after topology change takes 30-50 seconds with classic STP — relevant for [[entities/linux/network/load-balancing]] in networks with redundant L2 paths.

### VLANs (802.1Q)

**VLAN** (Virtual LAN) segments a single physical switch into multiple logical switches. Frames are tagged with a 12-bit VLAN ID at the ingress port; only ports in the same VLAN receive tagged frames.

Benefits: broadcast domain isolation, security, easier network segmentation without new wiring.

## Switching Implementation

**Software switch**: General-purpose CPU with NICs. Packets DMA'd into main memory; CPU inspects headers and programs output NIC. Bottlenecks: memory bandwidth (~100 Gbps peak) and per-packet processing rate (~20 Gbps for minimum-size packets).

**Hardware switch (NPU-based)**: Network Processing Unit with specialized instruction set for header parsing and forwarding. Uses SRAM for buffering, **TCAM** for longest-prefix-match and wildcard lookups, and a pipelined ASIC forwarding engine. Capable of terabits per second.

**P4**: Programming language for protocol-independent forwarding pipelines on programmable ASICs/NPUs. Defines `(Match, Action)` rules for the forwarding pipeline.

## Related Pages

- [[entities/linux/network/internet-architecture]] — Datagram forwarding in IP, contrasted with L2 switching
- [[entities/linux/network/linux-network-protocols]] — Linux bridge (net/bridge/) and Open vSwitch implementation
- [[entities/linux/network/net-stack-overview]] — Where switching fits in the Linux network stack
- [[entities/linux/network/load-balancing]] — L2/L3 load balancing, ECMP, consistent hashing
- [[sources/reading-lwip-bridge-implementation]] — LwIP二层网桥实现参考
