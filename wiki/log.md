---
type: log
tags: [log]
created: 2026-01-01
---

## [2026-05-22] ingest | pdf-cpp-slides + pdf-cpp-perf-books

Ingested 5 C++ conference slides (2025) + 2 performance/architecture books.

Source pages created:
- wiki/sources/pdf-cpp-slides.md — 彭博reflection、David Sankel/John Lakos safety、阿里云perf、xLLM inference
- wiki/sources/pdf-cpp-perf-books.md — Optimized C++ (Kurt Guntheroth) + Large-Scale C++ Software Design (John Lakos)

Entity pages created (NEW topics — no prior coverage):
- wiki/entities/cpp/cpp-reflection.md — C++26 P2996 reflection: `^^`, `[: :]`, `std::meta::info`, meta functions, access context
- wiki/entities/cpp/cpp-safety.md — Defense-in-depth (sandbox/harden/detect/prevent), C++26 Contracts P2900, memory safety CVEs
- wiki/entities/cpp/cpp-perf-optimization.md — CPU cache, SIMD, NUMA, profiling tools (perf/eBPF/IPT)
- wiki/entities/cpp/cpp-llm-inference.md — xLLM: PD/EPD separation, KV Cache pooling, async pipeline, SLO scheduling

Updated wiki/cpp-index.md with 4 new entity rows under "Additional Topics".
Cross-linked to existing entities: smart-pointers, raii, move-semantics, concurrency, constexpr, serialization.

## [2026-05-22] ingest | notes-ccpp

Ingested remaining C/C++ notes from raw/github/notes/ccpp/ (4 .md files). Filled gaps in existing cpp/ entity directory.

Added source page:
- wiki/sources/notes-ccpp.md — C/C++ 技术笔记：序列化、智能指针深度分析、堆栈对象创建策略、移动语义

Added entity pages:
- wiki/entities/cpp/cpp-serialization.md — C++ 序列化：JSON/XML/Protobuf/Boost/MessagePack 全方案对比
- wiki/entities/cpp/cpp-object-lifetime.md — C++ 对象生命周期：堆-only/栈-only 分配限制策略

Added new "Additional Topics" section to cpp-index.md with serialization and object-lifetime.
Cross-linked new entities to smart-pointers, raii, move-semantics.
Updated wiki/home.md (entity count 141→143, new source added) and index.md.

## [2026-05-22] ingest | notes-openbmc

Added source page:
- wiki/sources/notes-openbmc.md — OpenBMC 深度技术分析：硬件控制、安全、Redfish、IPMI、启动更新（5篇）

Added entity pages:
- wiki/entities/linux/openbmc/openbmc-overview.md — OpenBMC 整体架构：硬件控制、安全子系统、技术栈
- wiki/entities/linux/openbmc/openbmc-ipmi.md — IPMI 协议栈：KCS/SMIC、FRU/SEL/SDR、内核驱动
- wiki/entities/linux/openbmc/openbmc-redfish.md — Redfish RESTful API：资源层级、认证、OEM 扩展
- wiki/entities/linux/openbmc/openbmc-boot.md — 启动与固件更新：A/B 双镜像、Flash 布局、entity-manager

Added module index:
- wiki/openbmc-index.md — OpenBMC 模块导航

Cross-linked openbmc entities to each other and to kernel (locking, sched, ipc, netfilter, mm).
Updated wiki/home.md and index.md with OpenBMC module index and source entry.

## [2026-05-22] ingest | notes-tools

Added source page:
- wiki/sources/notes-tools.md — 工具使用笔记：tcpdump、netcat、masscan/nmap、移除 Snap

Added entity pages:
- wiki/entities/tools/linux-network-tools.md — Linux 网络诊断工具（tcpdump 抓包 + netcat 网络瑞士军刀）
- wiki/entities/tools/port-scanning.md — 端口扫描（masscan 高速异步 + nmap 全面深度检测）

Added module index:
- wiki/tools-index.md — 工具模块导航

Cross-linked to kernel-net-index, security entity, os-io-model, cpp-index, sys-prog-index.
Updated wiki/home.md and index.md with tools module index and source entry.

## [2026-05-20] ingest | github-notes-ccpp, github-notes-sys, github-notes-midware, github-notes-tools, github-notes-security

Added entity pages:
- wiki/entities/cpp.md — C/C++ 系统编程（内存模型、STL容器、单例模式）
- wiki/entities/sys.md — 系统编程（ELF格式、Linux IPC、设计模式）
- wiki/entities/midware.md — 中间件（DoIP、SOME/IP、vSOMEIP）
- wiki/entities/security.md — 安全工具（Masscan、Falco、Snort）

Cross-linked between cpp↔sys↔security and midware↔sys.
Updated wiki/index.md with new source entries.

## [2026-05-20] ingest | github-notes-virt, github-notes-io_uring, github-notes-vfs

Added entity pages:
- wiki/entities/linux/kernel/virt/linux-kernel-virt-kvm.md — KVM 虚拟化核心
- wiki/entities/linux/kernel/virt/linux-kernel-virt-virtio.md — Virtio 半虚拟化框架
- wiki/entities/linux/kernel/io_uring/linux-kernel-io-uring-core.md — io_uring 异步 I/O
- wiki/entities/linux/kernel/vfs/linux-kernel-vfs-core.md — VFS 虚拟文件系统

Cross-linked to existing linux/kernel entities (sched, mm, block).
Updated wiki/index.md with new sections and cross-reference index.

## [2026-05-20] ingest | github-notes-net, github-notes-netfilter, github-notes-network

Added entity pages:
- wiki/entities/linux/kernel/net/linux-kernel-net-subsystem.md — Linux 网络子系统核心（Socket/sk_buff/Netdevice/Routing/TCP）
- wiki/entities/linux/kernel/netfilter/linux-kernel-netfilter-framework.md — Netfilter 框架（iptables/nftables/conntrack/NAT）
- wiki/entities/linux/network/linux-network-protocols.md — 网络协议实现（TCP/UDP/IPv4/IPv6/BPF/XDP/桥接）

Added source pages:
- wiki/sources/github-notes-net.md — Linux Net 子系统分析
- wiki/sources/github-notes-netfilter.md — Netfilter 深度分析
- wiki/sources/github-notes-network.md — 网络笔记总索引

Cross-linked linux/kernel/net ↔ linux/kernel/netfilter ↔ linux/network.
Updated wiki/index.md with new entities and cross-reference index.

## [2026-05-20] ingest | pdf-modern-cpp-tutorial

Added source page:
- wiki/sources/pdf-modern-cpp-tutorial.md — Modern C++ Tutorial (C++11/14/17/20)

Added entity pages:
- wiki/entities/cpp/move-semantics.md — 移动语义与右值引用
- wiki/entities/cpp/smart-pointers.md — 智能指针（shared_ptr/unique_ptr/weak_ptr）
- wiki/entities/cpp/lambda-expressions.md — Lambda表达式与闭包
- wiki/entities/cpp/auto-type-deduction.md — auto与decltype类型推导
- wiki/entities/cpp/constexpr.md — constexpr编译时计算
- wiki/entities/cpp/raii.md — RAII资源管理惯用法
- wiki/entities/cpp/concurrency.md — C++并发编程
- wiki/entities/cpp/variadic-templates.md — 模板变参与参数包展开
- wiki/entities/cpp/if-constexpr.md — if constexpr编译时分支
- wiki/entities/cpp/cpp20-features.md — C++20新特性（Concepts/Ranges/Coroutines）

Cross-linked to existing entities/cpp.md.
Updated wiki/index.md with new source and entity entries.

## [2026-05-21] ingest | pdf-cpp-effective-stl

Added source page:
- wiki/sources/pdf-cpp-effective-stl.md — Effective STL (Scott Meyers) 简体中文版

Added entity pages:
- wiki/entities/cpp/cpp-stl-containers.md — STL容器（vector/deque/list/set/map/unordered_*）
- wiki/entities/cpp/cpp-stl-algorithms.md — STL算法（sort/find/remove/transform/二分查找）
- wiki/entities/cpp/cpp-stl-iterators.md — STL迭代器（类别/失效规则/适配器）
- wiki/entities/cpp/cpp-stl-functors.md — STL函数对象（仿函数/Lambda/函数适配器）
- wiki/entities/cpp/cpp-stl-string.md — STL字符串（string实现/string_view/高效操作）
- wiki/entities/cpp/cpp-stl-allocators.md — STL分配器（内存管理/自定义分配器）

Cross-linked to existing cpp entities (move-semantics, smart-pointers, lambda-expressions, cpp20-features).
Updated wiki/home.md with new source and entity entries.

## [2026-05-22] ingest | notes-net-deep

Ingested remaining network deep-dive notes from raw/github/notes/net/linux_kernel/ and raw/github/notes/network/ (10+ .md files).

Added source page:
- wiki/sources/notes-net-deep.md — 网络深度笔记合并：skbuff 内存管理、Netfilter/iptables/nftables、IPv4 路由 Trie、PHY/MAC 物理层、Conntrack 连接跟踪、Socket 层架构、网络栈全路径

Added entity pages:
- wiki/entities/linux/kernel/net/skbuff-deep-dive.md — SKB 内存管理深度分析（四指针布局、clone/copy、scatter-gather、dataref、linearize、destructor）
- wiki/entities/linux/network/osi-physical-layer.md — OSI 物理层/数据链路层（PHY/MAC 架构、MII/SMI、PCS/PMA/PMD、固件 vs 驱动）
- wiki/entities/linux/network/net-stack-deep-dive.md — 网络栈全路径分析（Socket→TCP/UDP→IP→Netfilter→Device、Jacobson RTT、拥塞控制、分片）

Added module index:
- wiki/kernel-protocols-index.md — 网络协议与物理层导航（protocols + stack-deep-dive + osi-phy）

Updated:
- wiki/kernel-net-index.md — 新增 skbuff-deep-dive 条目和 kernel-protocols-index 交叉引用
- wiki/home.md — 新增 kernel-protocols-index 模块和 notes-net-deep 来源
- index.md — 同步 home.md 全部更新

Cross-linked all new entities to existing linux-kernel-net-subsystem, linux-kernel-netfilter-framework, and linux-network-protocols.
