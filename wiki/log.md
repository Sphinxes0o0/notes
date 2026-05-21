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
