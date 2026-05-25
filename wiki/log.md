
## [2026-05-25] ingest | Batch: android, network-traffic-analysis, ccpp-concurrency, kernel-handson

**批次 1: Android Treble 架构**
- 创建 source: wiki/sources/notes-android.md（15篇文档汇总）
- 创建 6 个 entity:
  - wiki/entities/android/treble-architecture.md — Treble 架构总览
  - wiki/entities/android/hidl.md — HIDL 接口定义语言
  - wiki/entities/android/vndk.md — VNDK 供应商原生开发套件
  - wiki/entities/android/vintf.md — VINTF 供应商接口对象
  - wiki/entities/android/stable-aidl.md — Stable AIDL 接口
  - wiki/entities/android/hal.md — HAL 硬件抽象层类型体系

**批次 2: 网络流量分析**
- 创建 source: wiki/sources/notes-network-traffic-analysis.md（62篇论文综述）
- 创建 4 个 entity:
  - wiki/entities/security/network-traffic-analysis.md — 网络流量分析总览
  - wiki/entities/security/ids-ml-survey.md — IDS 机器学习综述
  - wiki/entities/security/encrypted-traffic-analysis.md — TLS 加密流量侧信道分析
  - wiki/entities/security/traffic-deep-learning.md — CNN/LSTM/AutoEncoder/GNN 模型

**批次 3: C++ 并发 + Kernel 动手实验**
- 创建 source: wiki/sources/notes-ccpp-concurrency.md
- 创建 entity: wiki/entities/cpp/concurrency-demos.md — MPMC队列/内存序/future-promise
- 创建 source: wiki/sources/notes-kernel-handson.md
- 创建 entity: wiki/entities/linux/kernel/handson-hypervisor.md — Rust RISC-V 裸机管理程序

**更新**: wiki/home.md (Sources table +4行，页数 ~373→~385), wiki/log.md

**交叉引用**: 所有 entity 均含 ≥2 [[wikilinks]]

---

## [2026-05-25] source | lwip-source-index + 5 core entity pages

**操作:**
- 创建 5 个 lwIP 核心源文件 entity pages:
  - wiki/entities/linux/lwip/source/ip4.c.md (1307 行) — IPv4 input/output, routing, forwarding
  - wiki/entities/linux/lwip/source/tcp.c.md (2768 行) — TCP PCB management, timers, close
  - wiki/entities/linux/lwip/source/udp.c.md (1385 行) — UDP dispatch/send, PCB management
  - wiki/entities/linux/lwip/source/pbuf.c.md (1570 行) — pbuf alloc/free, chain operations, header manipulation
  - wiki/entities/linux/lwip/source/netif.c.md (1913 行) — netif management, addressing, loopback
- 创建索引页: wiki/lwip-source-index.md (源码阅读层入口)
- 更新 wiki/home.md (lwip-source-index 入口)

**每个 source entity page 包含:**
- 函数索引表 (函数名 + 行号 + 功能一句话)
- 关键数据结构 (struct 字段说明)
- 调用链 (调用者/被调用者)
- 交叉引用 (→ wiki/entities/linux/lwip/*)

**对应源码:** external/lwip_ds_mcu/src/core/

---

## [2026-05-25] ingest | Batch N+O: Remaining Slides & Books
- N: Updated sources/pdf-cpp-slides.md (12→37 talks)
- O: Created sources/pdf-remaining-books.md (13 volumes)
---
type: journal
tags: [log]
created: 2026-05-22
---


## [2026-05-25] ingest | Batch M: C++ Slides
- Created sources/pdf-cpp-slides.md (18 conference talks)
- C++ evolution (Bjarne/Michael), AI security (David Sankel), compilers (MLIR/RISC-V)
---
type: log
tags: [log]
created: 2026-01-01
---

## [2026-05-25] ingest | Batch K: Linux/Kernel/ARM Books (11 PDFs) — summary only

**来源**: raw/PDFs/books/ (11 PDFs assessed, summary only)

**Linux/Kernel Books (7):**
- Linux高性能服务器编程.pdf — 高性能服务器, 网络编程
- Linux多线程服务端编程：使用muduo C++网络库.pdf — 多线程, muduo, C++
- The Linux Programming Interface.pdf — TLPI, Michael Kerrisk, 1556p
- UNIX环境高级编程(第三版).pdf — APUE, Stevens & Rago, 822p
- linux内核注释.pdf — 内核0.12源码注释
- 深入理解Linuxkenrle.pdf — 内核深入分析
- perfbook-e2-rc11.pdf — Linux性能优化, RCU

**ARM Books (4):**
- DDI0388H_cortex_a9_r4p0_trm.pdf — Cortex-A9 TRM
- DDI0487Fc_armv8_arm.pdf — ARMv8 ARM
- DDI0487_M_a_a_a-profile_architecture_reference_manual.pdf — ARM A-profile
- 手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解.pdf — TrustZone/OP-TEE

**操作**:
- 创建 1 个 source 页面: wiki/sources/pdf-linux-kernel-books.md (汇总页)
- 更新 wiki/kernel-books-index.md (添加 ARM 章节 + ARM Entities)
- 现有 home.md source entry 已存在 (pdf-linux-kernel-books 2026-05-25 entry)

**Note**: Batch K 仅做汇总，未提取 PDF 文本，未创建 entity 页面

## [2026-05-25] ingest | Batch L: Algorithms & Interviews (8 PDFs)

**来源**: raw/PDFs/books/ (8 PDFs)

**书目**:
- Data Structures & Algorithms in C++, 2nd Ed — Goodrich/Tamassia/Mount (17.8 MB, 文本)
- Data Structures & Algorithms in C++, 3rd Ed — Goodrich/Tamassia/Mount (44.0 MB, 文本)
- Algorithms in C, 3rd Ed (Full) — Robert Sedgewick (30.4 MB, 扫描)
- Algorithms in C, 3rd Ed — Part 5: Graph Algorithms — Robert Sedgewick (1.1 MB, 扫描)
- The Art of Computer Programming, Vol.1: Fundamental Algorithms, 3rd Ed — Donald E. Knuth (6.7 MB, 文本)
- 我的第一本算法书 — 石田保辉/宫崎修一 (8.9 MB, 文本)
- Cracking the Coding Interview, 6th Ed — Gayle Laakmann McDowell (56.4 MB, 文本)
- Elements of Programming Interviews (EPI) — Aziz/Lee/Prakash (1.1 MB, 文本)

**操作**:
- 更新 1 个 source 页面: wiki/sources/pdf-algorithms-books.md (修正书名/作者/大小信息)

**核心概念覆盖**:
- DS&A: 数组/链表/栈/队列/哈希/树/图 + O(n)分析
- 图算法: DFS/BFS/MST/最短路径/网络流
- 面试: CTCI 189题 + EPI 16章 + 双指针/滑动窗口/DP模式
- TAOCP: MMIX/信息结构/递归/栈与子程序

**交叉引用**: datastructure-index (graph-algorithms/entity), interview-index (pdf-algorithms-books)

## [2026-05-25] ingest | Batch J: C/C++ Core Programming (16 PDFs) — 15 extracted, 1 scanned skip

**来源**: raw/PDFs/books/ (16 PDFs assessed, 15 text-extracted, 1 image-only)

**C++ Modern (6 books):**
- Cpp17.pdf → merged to pdf-cpp-modern-books.md (C++17 Complete Guide)
- ModernC.pdf → merged to pdf-cpp-modern-books.md (Modern C by Jens Gustedt)
- Professional-C++-6ed-zh-20241122.pdf → merged to pdf-cpp-modern-books.md
- The.Book.of.Modern.C++.-.Electronic.Edition.pdf → merged to pdf-cpp-modern-books.md
- 21st-Century-C++.pdf → merged to pdf-cpp-modern-books.md
- modern-cpp-tutorial-zh-cn.pdf → existing source pdf-cpp-modern-tutorial.md (83p, C++11/14/17/20)

**C++ Templates (3 books):**
- C++模板_第二版.pdf → merged to pdf-cpp-templates-books.md
- C++-Templates-The-Complete-Guide-zh-20220903.pdf → merged to pdf-cpp-templates-books.md
- Template-Metaprogramming-with-C++-cn-20230401.pdf → merged to pdf-cpp-templates-books.md

**C++ Concurrency (3 books):**
- Concurrency.with.Modern.C++-zh.pdf → merged to pdf-cpp-concurrency.md
- C++并发编程指南.pdf → merged to pdf-cpp-concurrency.md (C++ Concurrency in Action)
- threads-locks.pdf → merged to pdf-concurrency-perf.md (OSEP Threads & Locks)

**C++ Performance & Memory (4 books):**
- C++性能优化指南.pdf → merged to pdf-cpp-perf-memory.md + pdf-cpp-perf-books.md
- Advanced_Memory_Management_in_Modern_Cpp.pdf → merged to pdf-cpp-perf-memory.md
- Large-Scale C++ Software Design.pdf → merged to pdf-cpp-modern-books.md + pdf-cpp-perf-books.md

**Skipped (Image-Only):**
- STL源码剖析简体中文完整版(清晰扫描带目录).pdf → **扫描版，无法提取文本，跳过**

**操作:**
- 创建 1 个 module index: wiki/cpp-books-index.md (C++ Books 聚合索引)
- 更新 wiki/home.md (添加 cpp-books-index 入口，页数 ~296→~297，indexes 23→24)

**Source 页面状态:**
- pdf-cpp-modern-books.md: 6册已覆盖
- pdf-cpp-modern-tutorial.md: 已存在
- pdf-cpp-templates-books.md: 3册已覆盖
- pdf-cpp-concurrency.md: 2册已覆盖
- pdf-concurrency-perf.md: threads-locks 已合并
- pdf-cpp-perf-memory.md: 4册已覆盖
- pdf-cpp-perf-books.md: 2册已覆盖

## [2026-05-25] ingest | Batch I: Security/Crypto PDFs — eBPF安全 papers + TLS/mbedtls books

**来源**: raw/PDFs/papers/ + raw/PDFs/books/ (11 PDFs assessed, 9 extracted)

**Papers (6 PDFs):**
- 2024-INFOCOM-PTPsec.pdf → source: pdf-ptp-security (更新现有)
- isovalent_security_observability.pdf → source: pdf-isovalent-security-observability (新建)
- 2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf → source: pdf-sabpf-container-audit (新建)
- Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf → 合并到 pdf-security-papers-ebpf
- Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf → 合并到 pdf-security-papers-ebpf
- Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf → 合并到 pdf-security-papers-ebpf

**Books (5 PDFs):**
- 密码技术与物联网安全mbedtls开发实战.pdf → 合并到 pdf-security-crypto-books-updated
- openssl-cookbook-中文版.pdf → 合并到 pdf-security-crypto-books-updated
- 图解密码技术 第三版.pdf → **image-only，无法提取文本，跳过**
- bulletproof-tls-and-pki-2nbsped-9781907117091.pdf → 合并到 pdf-security-crypto-books-updated
- 商用密码应用安全性评估考核题.pdf → **AES加密阻挡提取，跳过**

**操作:**
- 创建 4 个 entity 页面: linux-security-observability-ebpf, linux-security-ptpsec, bulletproof-tls-pki, openssl-tls-library
- 创建 4 个 source 页面: pdf-security-papers-ebpf, pdf-isovalent-security-observability, pdf-sabpf-container-audit, pdf-security-crypto-books-updated
- 更新 security-index.md (entity 2→6, source 1→6)
- 更新 wiki/home.md (Sources table +4行, page count ~285→~296)

**核心概念:**
- eBPF安全可观测性：Falco运行时检测、Apple BPF优势、KRSI BPF LSM、Google BPF Atomics/Ringbuffer
- saBPF容器审计：cgroup命名空间感知、provenance追踪、零内核修改
- PTPsec时间同步安全：循环路径不对称性分析检测延迟攻击
- TLS/PKI: TLS 1.3 0-RTT/1-RTT、AEAD、PSK；PKI X.509/证书链/OCSP/CT；常见攻击(BEAST/POODLE/CRIME/BREACH/Sweet32)
- OpenSSL vs mbedtls: 服务器/桌面 vs 嵌入式/IoT；libcrypto + libssl架构

**交叉引用:** 与 ebpf-index (saBPF/Falco/Isovalent)、kernel-subsystems-index (crypto/time)、security-index 互链

## [2026-05-25] ingest | Batch H: Modern-Cpp-Skills C++17 + Master (26 skills)

- **来源**: raw/Modern-Cpp-Skills/ (26 SKILL.md files)
  - C++17 skills (13): c17-01-ownership, c17-02-resource, c17-03-mutability, c17-04-templates, c17-05-type-driven, c17-06-error-handling, c17-07-concurrency, c17-09-domain, c17-10-performance, c17-11-ecosystem, c17-12-lifecycle, c17-13-domain-error, cpp-skill-creator
  - Master skills (15): m01-ownership, m02-resource, m03-mutability, m04-zero-cost, m05-type-driven, m06-error-handling, m07-concurrency, m09-domain, m10-performance, m11-ecosystem, m12-lifecycle, m13-domain-error, m14-mental-model, m15-anti-pattern
- **操作**:
  - 创建 28 个 entity 页面: wiki/entities/cpp/modern/{c17-01..13, m01..15, cpp-skill-creator}.md
  - 创建 1 个 source 页面: wiki/sources/cpp-modern-skills.md
  - 创建 1 个 module index: wiki/cpp-modern-index.md
- **更新**: wiki/home.md (cpp-modern-index 入口 + cpp-modern-skills 源 + 頁面數 ~257→~285), log.md
- **核心概念**: 
  - C++17 Skills: if constexpr, std::variant, std::string_view, std::shared_mutex, scoped_lock, CTAD, PMR, DDD (Value Object/Entity/Aggregate), type-state pattern, domain events, exception hierarchies
  - Master Skills: Error → Design Question 框架, Trace Up/Down 推理, Core Question 模式, ownership/resource/mutability/zero-cost/type-driven/error/concurrency/domain/performance/ecosystem/lifecycle/mental-model/anti-pattern 思維模型
- **交叉引用策略**: 與現有 cpp entity（move-semantics, raii, smart-pointers, concurrency, constexpr, if-constexpr, variadic-templates, cpp20-features, cpp-safety, cpp-perf-optimization, stl-containers, stl-string）互鏈，確保 ≥2 wikilinks 每 entity

## [2026-05-25] ingest | Batch G: safeos-architecture SafeOS Architecture & Design

- **来源**: raw/safeos/ (7 篇文档)
  - architecture_notes.md, plan.md, NSv_analysis.md, network_implementation_analysis.md
  - packet_mmap_design.md, af_packet_mmap_summary.md, memory/safeos_vdf_nids.md
- **操作**:
  - 创建 4 个 entity 页面: safeos-nsv, safeos-network-implementation, safeos-packet-mmap, safeos-vdf-nids-relation
  - 创建 1 个 source 页面: wiki/sources/safeos-architecture.md
  - 创建 1 个 module index: wiki/safeos-index.md
  - 更新 wiki/home.md (safeos-index 入口 + safeos-architecture 源, page count ~250→~257)
- **核心概念**: SafeOS NSv 用户态网络栈架构：3线程模型(event_loop/nic_rx_thread/tcpip_thread)、CMA 96MB+elem_ring 4环、AF-PACKET自定义混合方案(TPACKET+DSPACE，非Linux标准)、VDF nids适配需重写capture backend
- **关键发现**: SafeOS AF-PACKET非标准实现(tpacket_recv写入DSPACE)、API稳定性差(内部头文件暴露)、无TPACKET_V3支持、无零拷贝(nids decoder兼容但capture层需重写)

## [2026-05-25] ingest | Batch F: safeos-lwfw LWFW Firewall Analysis

- **来源**: raw/safeos/lwfw_*.md + raw/safeos/lwfw_analysis/ (27 篇文档)
- **操作**:
  - 创建 26 个 entity 页面: lwfw-architecture, lwfw-core-filtering, lwfw-data-structure, lwfw-classification, lwfw-filter-flow, lwfw-list-search, lwfw-tree-search, lwfw-hook-injection, lwfw-tcpip-thread, lwfw-lwct, lwfw-lwct-gc-analysis, lwfw-lwct-interaction, lwfw-config-parsing, lwfw-parser, lwfw-parser-concurrency, lwfw-notif, lwfw-ipc-mechanism, lwfw-stats, lwfw-agent, lwfw-agent-log-system, lwfw-vlan-interception-flow, lwfw-vlan-isolation-guide, lwfw-hotswap-analysis, lwfw-rule-matching, lwfw-optimization, lwfw-lwct (root-level)
  - 创建 1 个 source 页面: wiki/sources/safeos-lwfw.md
  - 创建 1 个 module index: wiki/lwfw-index.md
- **更新**: wiki/home.md (lwfw-index + safeos-lwfw 入口), log.md
- **核心概念**: SafeOS LWFW 状态ful 防火墙，5-tuple/L2/L3/L4 匹配，双过滤引擎(list/tree)，LWCT 连接追踪，seL4 IPC + 共享内存 FIFO 事件通知，VLAN 隔离，P0-P3 优化问题汇总
- **关键发现**: 位标志冲突(P0)，热重载窗口期无防护(P0)，静态解析器状态(P1)，GC 线程退出无重启(P1)

## [2026-05-25] ingest | Batch E: safeos-lwip-extensions lwIP Extensions & Integration

- **来源**: raw/safeos/lwip_*_analysis.md (19 篇分析文档)
- **操作**:
  - 创建 19 个 entity 页面: lwip-analysis-summary, lwip-arp-filter-netif-fn, lwip-bridgeif, lwip-cma-buffer, lwip-elem-ring, lwip-firewall, lwip-ipcif, lwip-lwfw-filter-hooks, lwip-nsv-event-loop, lwip-packet-mmap, lwip-raw-socket, lwip-sel4-function, lwip-sel4-interaction, lwip-sel4-ipc, lwip-sel4-performance-boundary, lwip-sys-net-ctl, lwip-sys-net-send-recv, lwip-sys-net-socket-api, lwip-virt-brg
  - 创建 1 个 source 页面: wiki/sources/safeos-lwip-extensions.md
  - 更新 wiki/lwip-index.md (新增基础设施/LWFW/RAW/Socket API/seL4/概览章节)
  - 更新 wiki/home.md (lwip-index 入口 + safeos-lwip-extensions 源)
- **核心概念**: SafeOS lwIP 扩展模块集：LWFW 三层安全架构、CMA/elem_ring 基础设施、seL4 微内核集成（~3x 单核性能损失）、packet_mmap/AF-PACKET 零拷贝、VIRT_BRG/IPCIF 虚拟化、NSv Socket API
- **更新**: lwip-index.md (entity count 27→46), home.md (total pages ~203→~222), log.md

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

## [2026-05-23] split | Sport-health moved to atlas

Split exercise science content into Sphinxes0o0/atlas — separate Obsidian vault.
Removed: 11 module indexes, ~60 entity pages, 8 source pages (relay-neuron).
Remaining: ~130 tech pages (Linux kernel, C++, networking, eBPF, tools, algorithms).

## [2026-05-23] ingest | C++ conference slides batch 2 (~32 slides)

Ingested remaining 32 C++ conference slides. Grouped into 5 thematic source pages.

Source pages created:
- wiki/sources/pdf-cpp-ai-inference.md — AI/ML 推理（7篇）：Mooncake 解耦架构、RTP-LLM、DeepSeek 性能优化、LazyLLM 三阶段框架、端侧部署挑战、FlagScale 统一推理、RecIS 推荐训练
- wiki/sources/pdf-cpp-safety-standards.md — C++ 安全与标准化（3篇）：Bjarne Profiles、Michael Wong 三层 AI 栈、David Sankel AI 代码风险
- wiki/sources/pdf-cpp-compiler-toolchain.md — 编译器/工具链（6篇）：MLIR 模糊测试、RISC-V AI 编译器、开源生态策略、多芯片算子库、编译在 AI 栈中、统一异构计算
- wiki/sources/pdf-cpp-perf-engineering.md — 性能工程（5篇）：内核旁路 DPDK/Netmap/mTCP、Bcache Btree 索引、分布式缓存/编译加速、RDMA 异构传输、CRASH_NG AI 诊断
- wiki/sources/pdf-cpp-engineering-practices.md — 工程实践（10篇）：Baidu Comate/Meituan AI Coding、AI 原生成熟度、小米 Vela C++、Parasoft AI 测试、CodeBuddy/Qoder CLI、SWE 金字塔、对象生命周期、具身机器人构建

Entity pages created:
- wiki/entities/ai-mlir-compilation.md — AI 编译与 MLIR 基础设施
- wiki/entities/risc-v-ai-ecosystem.md — RISC-V 开源指令集 + AI 软件生态
- wiki/entities/kernel-bypass-dpdk.md — 内核旁路技术（DPDK/Netmap/XDP）

Updated: wiki/cpp-index.md (cross-references), wiki/home.md (Sources table + page count ~130→~140)

## [2026-05-23] lint | pyramid wiki health check

Ran full lint on wiki (154 files). Results:

### Issues Found (after auto-fix)

**Orphan pages (3)** — pages with zero inbound [[wikilinks]]:
- wiki/sources/notes-net.md — only referenced in entity frontmatter `sources:` fields, no [[wikilinks]]
- wiki/sources/notes-network.md — same issue
- wiki/sources/pdf-cpp-perf-books.md — no references from any page

**Broken wikilinks (0)** — 5 found and fixed:
- cpp-index.md: [[ai-mlir-compilation]], [[risc-v-ai-ecosystem]], [[kernel-bypass-dpdk]] → added `entities/` prefix
- entities/ai-mlir-compilation.md → [[risc-v-ai-ecosystem]] → [[entities/risc-v-ai-ecosystem]]
- entities/risc-v-ai-ecosystem.md → [[ai-mlir-compilation]] → [[entities/ai-mlir-compilation]]

**Index completeness missing (3)** — source pages not in home.md sources table:
- sources/notes-net — present as files, referenced in entity frontmatter but not listed in home.md
- sources/notes-network — same
- sources/pdf-cpp-perf-books — same

**Frontmatter issues (19)** — source pages missing `tags` field:
- sources/notes-ccpp.md, notes-datastructure.md, notes-design-patterns.md, notes-interview.md
- sources/notes-midware.md, notes-net-deep.md, notes-openbmc.md, notes-security.md
- sources/notes-sys.md, notes-tools.md, pdf-cpp-ai-inference.md, pdf-cpp-compiler-toolchain.md
- sources/pdf-cpp-engineering-practices.md, pdf-cpp-perf-books.md, pdf-cpp-perf-engineering.md
- sources/pdf-cpp-safety-standards.md, pdf-cpp-slides.md, pdf-ebpf-books.md, pdf-ebpf-papers.md

*4 entity pages (cpp.md, sys.md, midware.md, security.md) had malformed frontmatter (closing `---` on same line as last field) — fixed.*

**Stale content (0)** — no pages have `updated` field; stale detection requires `updated` dates in frontmatter

**Large pages (1)** — pages over 200 lines:
- wiki/sources/pdf-cpp-engineering-practices.md (231 lines) — consider splitting into sub-pages

### Additional Issues Found & Fixed
- **Corrupt files (2)**: wiki/home.md and wiki/log.md had line-number prefixes embedded in file content — repaired

### Recommendations
1. Add `tags` to all 19 source pages for consistency
2. Add `notes-net`, `notes-network`, and `pdf-cpp-perf-books` to home.md Sources table
3. Add `updated` field to pages when content changes to enable stale detection
4. Consider splitting pdf-cpp-engineering-practices.md into thematic sub-pages

## [2026-05-23] ingest | 7 new C++ slides
- Created: wiki/sources/pdf-epi-python.md (EPI Python sampler source)
- Created: wiki/entities/cpp/cpp-recsys-optimization.md (C++ recsys optimization entity)
- Enhanced: pdf-cpp-slides.md (David Sankel, John Lakos, 吴晓飞, 刘童旋 sections)
- Enhanced: pdf-cpp-ai-inference.md (RecIS section)
- Enhanced: cpp-index.md, home.md

## [2026-05-23] ingest | 3 eBPF papers + notes/docs PDFs

Ingested 3 new eBPF/security papers + notes/docs PDFs into pyramid wiki.

### eBPF Papers (merged into pdf-ebpf-papers.md)
- saBPF: Secure Namespaced Kernel Audit for Containers (Soo Yee Lim, SoCC 2021) — container-level eBPF audit via LSM + cgroup
- Security Observability with eBPF (Jed Salazar & Natalia Reka Ivanko, O'Reilly 2022) — Four Golden Signals for K8s security
- PTPsec (INFOCOM 2024) — NOT eBPF, created separate source pdf-ptp-security.md

Source pages updated:
- wiki/sources/pdf-ebpf-papers.md — 7→9 papers, added saBPF + Isovalent sections

New entity pages:
- wiki/entities/linux/ebpf/ebpf-container-audit.md — saBPF container audit framework
- wiki/entities/linux/ebpf/ebpf-security-observability.md — eBPF Four Golden Signals

New non-eBPF source page:
- wiki/sources/pdf-ptp-security.md — PTPsec: IEEE 1588 delay attack detection

### Notes/docs PDFs assessed and ingested

**C++ PDFs (5)** — 2 image-only, 3 extracted:
- wiki/sources/pdf-cpp-templates.md — C++ Templates 2nd Edition
- wiki/sources/pdf-cpp-nginx-module.md — Nginx module dev with C++11+Boost
- wiki/sources/pdf-crypto-books.md — OpenSSL Cookbook + Illustrated Cryptography
- wiki/entities/cpp/cpp-templates.md — C++ templates entity page
- 泛型编程与STL中文版.pdf + 图解密码技术.pdf — image-only, noted

**Rust PDFs (2)** — new domain:
- wiki/sources/pdf-rust-intro.md — Rust 入门指北 (infrastructure + language)
- wiki/entities/rust/rust-language.md — Rust language entity
- wiki/rust-index.md — Rust module index

**Networking PDFs (3)** — 1 new, 2 duplicates:
- wiki/sources/pdf-af-xdp-quic.md — B站 AF_XDP + QUIC practice
- linux_network_stack.pdf — duplicates notes-net-deep
- tcp_protocol_rfc_design_implementation.pdf — duplicates existing content

**SOME/IP PDFs (6)** — consolidated:
- wiki/sources/pdf-someip-docs.md — CommonAPI/Franca/SOME/IP-SD/vSomeIP/netmap

Updated: wiki/home.md (Sources table + Rust index), wiki/ebpf-index.md (new entities), wiki/cpp-index.md (new sources + entity), wiki/entities/linux/ebpf/ebpf-security.md (source refs)

## [2026-05-23] ingest | 5 book source pages (algo/interview/security/ARM/misc)

Ingested ~22 books into pyramid wiki, grouped into 5 thematic source pages.

Source pages created:
- wiki/sources/pdf-algo-ds-books.md — 算法与数据结构7册：Sedgewick图算法、TAOCP Vol.1、邓俊辉数据结构、基础集合论
- wiki/sources/pdf-interview-books.md — 编程面试2册：Cracking the Coding Interview 6th + EPI
- wiki/sources/pdf-security-crypto-books.md — 安全与密码学6册：Bulletproof TLS/PKI 2nd、mbedtls、TrustZone/OP-TEE、商用密码考核、OpenSSL Cookbook、图解密码技术
- wiki/sources/pdf-arm-architecture.md — ARM体系结构4册：Armv8/Armv9参考手册、Cortex-A9 TRM、量化研究方法
- wiki/sources/pdf-misc-books.md — 杂项3册：人月神话、非线性动力学与混沌、偏微分方程

Entity pages created (10 new):
- wiki/entities/datastructure/graph-algorithms.md — Graph traversal, shortest path, MST, network flow (Sedgewick)
- wiki/entities/datastructure/set-theory-basics.md — Sets, relations, functions, cardinality (基础集合论)
- wiki/entities/arm/trustzone-op-tee.md — ARM TrustZone & OP-TEE TEE architecture
- wiki/entities/security/mbedtls-crypto.md — mbedtls embedded TLS/crypto library
- wiki/entities/security/commercial-cryptography.md — 商用密码（国密SM2/SM3/SM4 + 密评）
- wiki/entities/arm/armv8-architecture.md — ARMv8-A (AArch64) architecture reference
- wiki/entities/arm/arm-cortex-a9.md — Cortex-A9 processor microarchitecture
- wiki/entities/arm/computer-architecture.md — Hennessy & Patterson quantitative approach
- wiki/entities/software-engineering/mythical-man-month.md — Brooks' Law, No Silver Bullet
- wiki/entities/math/nonlinear-dynamics-chaos.md — Strogatz nonlinear dynamics & chaos

Updated:
- wiki/home.md — Sources table (+5 rows), page count 152→167
- wiki/datastructure-index.md — Added graph-algorithms + set-theory-basics entity rows
- wiki/interview-index.md — Added pdf-interview-books cross-reference

Cross-linked all new entities (2+ wikilinks per page verified).