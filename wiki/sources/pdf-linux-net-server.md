---
type: source
source-type: pdf
title: "Linux Networking/Server Programming (3 books)"
author: "You Yugui; Chen Shuo (giantchen@gmail.com); Laowu (老衲五木)"
date: 2026-05-23
size: medium
path: raw/PDFs/books/Linux高性能服务器编程.pdf, raw/PDFs/books/Linux多线程服务端编程：使用muduo C++网络库.pdf, raw/PDFs/books/LwIP 协议栈源码详解.pdf
summary: "3册Linux网络与服务端编程：Linux高性能服务器编程（Linux服务器全栈技术）、陈硕 muduo多线程服务端编程（one loop per thread模型）、LwIP协议栈源码详解（嵌入式TCP/IP深度解析）"
---

# Linux Networking/Server Programming (3 books)

## Core Content

### 1. Linux High-Performance Server Programming (You Yugui, 363 pages, scanned)

Chinese comprehensive guide to Linux server-side programming covering TCP/IP protocol, I/O models, event-driven architecture, and multi-process/multi-thread server design.

**Topics covered:**
- TCP/IP protocol suite: IP/TCP/UDP protocol details, three-way handshake, state transition (RFC 793)
- I/O models: blocking/non-blocking, multiplexing (select/poll/epoll), signal-driven, async I/O
- Event-driven programming: reactor pattern, proactor pattern, event loop design
- Multi-process servers: fork-based models, process pools, inter-process communication
- Multi-thread servers: thread pools, thread synchronization (mutex/semaphore/rwlock)
- Timer management: timing wheels, timeouts, keep-alive mechanisms
- Signal handling: signal sets, sigaction, safe signal handling in servers
- Performance optimization: zero-copy (sendfile/splice/tee), buffer management
- HTTP protocol: request/response parsing, HTTP Keep-Alive, WebSocket
- Distributed system fundamentals: load balancing, session management, cache strategies

### 2. Linux Multi-Threaded Server Programming: Using Muduo C++ Network Library (Chen Shuo, 151 pages)

A practitioner's guide to building production-grade multi-threaded TCP network servers on x86-64 Linux using modern C++ and the muduo library.

**Part I — C++ Multi-Threaded System Programming:**
- Object lifetime management in multi-threaded environments: smart pointers (shared_ptr/weak_ptr), enable_shared_from_this
- Thread synchronization: mutex, condition variable, read-write lock, deadlock avoidance
- Thread-safe singleton, thread-local storage (__thread), lock-free programming basics
- Efficient multi-threaded logging: double buffering, asynchronous log writing

**Part II — Muduo Network Library:**
- Core architecture: one loop per thread + thread pool model
- Non-blocking event-driven: epoll-based EventLoop, Channel, Poller
- TCP connection management: TcpServer, TcpConnection, Acceptor
- Buffer design: muduo's zero-copy Buffer, scatter-gather I/O
- Timers: TimerQueue, timing wheel
- Protocol serialization: length-prefix framing, Protocol Buffers integration
- Concrete examples: echo server, file transfer, chat server

**Part III — Engineering Practices:**
- Distributed system essentials: heartbeat protocol, RPC design patterns
- Logging: what to log, log levels, performance impact considerations
- Library interface design: ABI compatibility, pimpl idiom, opaque pointers
- Network message format design: binary vs text, TLV encoding, versioning
- C++ project management: Makefile/CMake, unit testing, code review

**Part IV — Appendices:**
- Learning resources: recommended books on network programming and C++
- TCP state machine reference, muduo API reference

### 3. LwIP Protocol Stack Source Code Analysis (Laowu Wumu, 99 pages)

A detailed annotation of the LwIP (Lightweight TCP/IP) protocol stack, focusing on its core implementation for embedded systems.

**Memory Management:**
- Dynamic memory pools (memp): fixed-size pre-allocated pools for different protocol objects
- Dynamic memory heap (mem): general-purpose allocator for variable-size allocations
- Data packet management (pbuf): pbuf structure, pbuf types (RAM/ROM/REF/POOL), pbuf chaining, pbuf copy/free

**Network Interface Layer:**
- netif structure: interface registration, link-layer output functions
- Ethernet data reception: interrupt handler, input function chain, netif->input callback
- ARP layer: ARP table data structure, ARP cache management, ARP table lookup/update, ARP request/response

**IP Layer:**
- IP input: IP header parsing, header checksum verification, packet demultiplexing (protocol dispatch)
- IP forwarding: routing table lookup, TTL decrement, checksum update
- IP fragmentation and reassembly: ip_reass, reassembly data structures, reassembly timer

**TCP Layer:**
- TCP control block (tcp_pcb): connection state machine, send/receive buffers, window
- TCP connection establishment: three-way handshake implementation, listen/accept, SYN backlog
- TCP state machine: CLOSED/LISTEN/SYN_SENT/SYN_RCVD/ESTABLISHED/FIN_WAIT/CLOSE_WAIT/LAST_ACK/TIME_WAIT
- TCP input/output: segment processing, sequence number handling, window update
- Sliding window: send window, receive window, window advertisement, zero-window probing
- TCP timers: retransmission timer (RTO), persist timer, keepalive timer, TIME_WAIT timer
- Congestion control: slow start, congestion avoidance, fast retransmit, fast recovery
- Nagle algorithm, delayed ACK

**API Layer:**
- netconn API: sequential API based on message passing between thread contexts
- socket API: BSD socket compatibility layer over netconn

## Key Quotes

- "The essence of muduo is one loop per thread plus thread pool — the most mature model for native Linux high-performance server programming" — Chen Shuo
- "掌握两种基本的同步原语就可以满足各种多线程同步的功能需求，还能写出更易用的同步设施" — Chen Shuo

## Related Pages

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Linux kernel network subsystem
- [[entities/linux/network/linux-network-protocols]] — Network protocol implementation
- [[entities/linux/network/net-stack-deep-dive]] — Network stack deep dive
- [[entities/os/os-io-model]] — I/O models
- [[kernel-net-index]] — Kernel networking index
- [[kernel-protocols-index]] — Protocol details
- [[entities/cpp/concurrency]] — C++ concurrency
- [[entities/cpp/smart-pointers]] — Smart pointers for lifetime management
- [[entities/cpp/raii]] — RAII resource management
- [[entities/cpp/cpp-stl-string]] — String handling
- [[cpp-index]] — Modern C++ and STL
- [[sys-prog-index]] — System programming
