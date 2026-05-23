     1|---
     2|type: log
     3|tags: [log]
     4|created: 2026-01-01
     5|---
     6|
     7|## [2026-05-22] ingest | pdf-cpp-slides + pdf-cpp-perf-books
     8|
     9|Ingested 5 C++ conference slides (2025) + 2 performance/architecture books.
    10|
    11|Source pages created:
    12|- wiki/sources/pdf-cpp-slides.md — 彭博reflection、David Sankel/John Lakos safety、阿里云perf、xLLM inference
    13|- wiki/sources/pdf-cpp-perf-books.md — Optimized C++ (Kurt Guntheroth) + Large-Scale C++ Software Design (John Lakos)
    14|
    15|Entity pages created (NEW topics — no prior coverage):
    16|- wiki/entities/cpp/cpp-reflection.md — C++26 P2996 reflection: `^^`, `[: :]`, `std::meta::info`, meta functions, access context
    17|- wiki/entities/cpp/cpp-safety.md — Defense-in-depth (sandbox/harden/detect/prevent), C++26 Contracts P2900, memory safety CVEs
    18|- wiki/entities/cpp/cpp-perf-optimization.md — CPU cache, SIMD, NUMA, profiling tools (perf/eBPF/IPT)
    19|- wiki/entities/cpp/cpp-llm-inference.md — xLLM: PD/EPD separation, KV Cache pooling, async pipeline, SLO scheduling
    20|
    21|Updated wiki/cpp-index.md with 4 new entity rows under "Additional Topics".
    22|Cross-linked to existing entities: smart-pointers, raii, move-semantics, concurrency, constexpr, serialization.
    23|
    24|## [2026-05-22] ingest | notes-ccpp
    25|
    26|Ingested remaining C/C++ notes from raw/github/notes/ccpp/ (4 .md files). Filled gaps in existing cpp/ entity directory.
    27|
    28|Added source page:
    29|- wiki/sources/notes-ccpp.md — C/C++ 技术笔记：序列化、智能指针深度分析、堆栈对象创建策略、移动语义
    30|
    31|Added entity pages:
    32|- wiki/entities/cpp/cpp-serialization.md — C++ 序列化：JSON/XML/Protobuf/Boost/MessagePack 全方案对比
    33|- wiki/entities/cpp/cpp-object-lifetime.md — C++ 对象生命周期：堆-only/栈-only 分配限制策略
    34|
    35|Added new "Additional Topics" section to cpp-index.md with serialization and object-lifetime.
    36|Cross-linked new entities to smart-pointers, raii, move-semantics.
    37|Updated wiki/home.md (entity count 141→143, new source added) and index.md.
    38|
    39|## [2026-05-22] ingest | notes-openbmc
    40|
    41|Added source page:
    42|- wiki/sources/notes-openbmc.md — OpenBMC 深度技术分析：硬件控制、安全、Redfish、IPMI、启动更新（5篇）
    43|
    44|Added entity pages:
    45|- wiki/entities/linux/openbmc/openbmc-overview.md — OpenBMC 整体架构：硬件控制、安全子系统、技术栈
    46|- wiki/entities/linux/openbmc/openbmc-ipmi.md — IPMI 协议栈：KCS/SMIC、FRU/SEL/SDR、内核驱动
    47|- wiki/entities/linux/openbmc/openbmc-redfish.md — Redfish RESTful API：资源层级、认证、OEM 扩展
    48|- wiki/entities/linux/openbmc/openbmc-boot.md — 启动与固件更新：A/B 双镜像、Flash 布局、entity-manager
    49|
    50|Added module index:
    51|- wiki/openbmc-index.md — OpenBMC 模块导航
    52|
    53|Cross-linked openbmc entities to each other and to kernel (locking, sched, ipc, netfilter, mm).
    54|Updated wiki/home.md and index.md with OpenBMC module index and source entry.
    55|
    56|## [2026-05-22] ingest | notes-tools
    57|
    58|Added source page:
    59|- wiki/sources/notes-tools.md — 工具使用笔记：tcpdump、netcat、masscan/nmap、移除 Snap
    60|
    61|Added entity pages:
    62|- wiki/entities/tools/linux-network-tools.md — Linux 网络诊断工具（tcpdump 抓包 + netcat 网络瑞士军刀）
    63|- wiki/entities/tools/port-scanning.md — 端口扫描（masscan 高速异步 + nmap 全面深度检测）
    64|
    65|Added module index:
    66|- wiki/tools-index.md — 工具模块导航
    67|
    68|Cross-linked to kernel-net-index, security entity, os-io-model, cpp-index, sys-prog-index.
    69|Updated wiki/home.md and index.md with tools module index and source entry.
    70|
    71|## [2026-05-20] ingest | github-notes-ccpp, github-notes-sys, github-notes-midware, github-notes-tools, github-notes-security
    72|
    73|Added entity pages:
    74|- wiki/entities/cpp.md — C/C++ 系统编程（内存模型、STL容器、单例模式）
    75|- wiki/entities/sys.md — 系统编程（ELF格式、Linux IPC、设计模式）
    76|- wiki/entities/midware.md — 中间件（DoIP、SOME/IP、vSOMEIP）
    77|- wiki/entities/security.md — 安全工具（Masscan、Falco、Snort）
    78|
    79|Cross-linked between cpp↔sys↔security and midware↔sys.
    80|Updated wiki/index.md with new source entries.
    81|
    82|## [2026-05-20] ingest | github-notes-virt, github-notes-io_uring, github-notes-vfs
    83|
    84|Added entity pages:
    85|- wiki/entities/linux/kernel/virt/linux-kernel-virt-kvm.md — KVM 虚拟化核心
    86|- wiki/entities/linux/kernel/virt/linux-kernel-virt-virtio.md — Virtio 半虚拟化框架
    87|- wiki/entities/linux/kernel/io_uring/linux-kernel-io-uring-core.md — io_uring 异步 I/O
    88|- wiki/entities/linux/kernel/vfs/linux-kernel-vfs-core.md — VFS 虚拟文件系统
    89|
    90|Cross-linked to existing linux/kernel entities (sched, mm, block).
    91|Updated wiki/index.md with new sections and cross-reference index.
    92|
    93|## [2026-05-20] ingest | github-notes-net, github-notes-netfilter, github-notes-network
    94|
    95|Added entity pages:
    96|- wiki/entities/linux/kernel/net/linux-kernel-net-subsystem.md — Linux 网络子系统核心（Socket/sk_buff/Netdevice/Routing/TCP）
    97|- wiki/entities/linux/kernel/netfilter/linux-kernel-netfilter-framework.md — Netfilter 框架（iptables/nftables/conntrack/NAT）
    98|- wiki/entities/linux/network/linux-network-protocols.md — 网络协议实现（TCP/UDP/IPv4/IPv6/BPF/XDP/桥接）
    99|
   100|Added source pages:
   101|- wiki/sources/github-notes-net.md — Linux Net 子系统分析
   102|- wiki/sources/github-notes-netfilter.md — Netfilter 深度分析
   103|- wiki/sources/github-notes-network.md — 网络笔记总索引
   104|
   105|Cross-linked linux/kernel/net ↔ linux/kernel/netfilter ↔ linux/network.
   106|Updated wiki/index.md with new entities and cross-reference index.
   107|
   108|## [2026-05-20] ingest | pdf-modern-cpp-tutorial
   109|
   110|Added source page:
   111|- wiki/sources/pdf-modern-cpp-tutorial.md — Modern C++ Tutorial (C++11/14/17/20)
   112|
   113|Added entity pages:
   114|- wiki/entities/cpp/move-semantics.md — 移动语义与右值引用
   115|- wiki/entities/cpp/smart-pointers.md — 智能指针（shared_ptr/unique_ptr/weak_ptr）
   116|- wiki/entities/cpp/lambda-expressions.md — Lambda表达式与闭包
   117|- wiki/entities/cpp/auto-type-deduction.md — auto与decltype类型推导
   118|- wiki/entities/cpp/constexpr.md — constexpr编译时计算
   119|- wiki/entities/cpp/raii.md — RAII资源管理惯用法
   120|- wiki/entities/cpp/concurrency.md — C++并发编程
   121|- wiki/entities/cpp/variadic-templates.md — 模板变参与参数包展开
   122|- wiki/entities/cpp/if-constexpr.md — if constexpr编译时分支
   123|- wiki/entities/cpp/cpp20-features.md — C++20新特性（Concepts/Ranges/Coroutines）
   124|
   125|Cross-linked to existing entities/cpp.md.
   126|Updated wiki/index.md with new source and entity entries.
   127|
   128|## [2026-05-21] ingest | pdf-cpp-effective-stl
   129|
   130|Added source page:
   131|- wiki/sources/pdf-cpp-effective-stl.md — Effective STL (Scott Meyers) 简体中文版
   132|
   133|Added entity pages:
   134|- wiki/entities/cpp/cpp-stl-containers.md — STL容器（vector/deque/list/set/map/unordered_*）
   135|- wiki/entities/cpp/cpp-stl-algorithms.md — STL算法（sort/find/remove/transform/二分查找）
   136|- wiki/entities/cpp/cpp-stl-iterators.md — STL迭代器（类别/失效规则/适配器）
   137|- wiki/entities/cpp/cpp-stl-functors.md — STL函数对象（仿函数/Lambda/函数适配器）
   138|- wiki/entities/cpp/cpp-stl-string.md — STL字符串（string实现/string_view/高效操作）
   139|- wiki/entities/cpp/cpp-stl-allocators.md — STL分配器（内存管理/自定义分配器）
   140|
   141|Cross-linked to existing cpp entities (move-semantics, smart-pointers, lambda-expressions, cpp20-features).
   142|Updated wiki/home.md with new source and entity entries.
   143|
   144|## [2026-05-22] ingest | notes-net-deep
   145|
   146|Ingested remaining network deep-dive notes from raw/github/notes/net/linux_kernel/ and raw/github/notes/network/ (10+ .md files).
   147|
   148|Added source page:
   149|- wiki/sources/notes-net-deep.md — 网络深度笔记合并：skbuff 内存管理、Netfilter/iptables/nftables、IPv4 路由 Trie、PHY/MAC 物理层、Conntrack 连接跟踪、Socket 层架构、网络栈全路径
   150|
   151|Added entity pages:
   152|- wiki/entities/linux/kernel/net/skbuff-deep-dive.md — SKB 内存管理深度分析（四指针布局、clone/copy、scatter-gather、dataref、linearize、destructor）
   153|- wiki/entities/linux/network/osi-physical-layer.md — OSI 物理层/数据链路层（PHY/MAC 架构、MII/SMI、PCS/PMA/PMD、固件 vs 驱动）
   154|- wiki/entities/linux/network/net-stack-deep-dive.md — 网络栈全路径分析（Socket→TCP/UDP→IP→Netfilter→Device、Jacobson RTT、拥塞控制、分片）
   155|
   156|Added module index:
   157|- wiki/kernel-protocols-index.md — 网络协议与物理层导航（protocols + stack-deep-dive + osi-phy）
   158|
   159|Updated:
   160|- wiki/kernel-net-index.md — 新增 skbuff-deep-dive 条目和 kernel-protocols-index 交叉引用
   161|- wiki/home.md — 新增 kernel-protocols-index 模块和 notes-net-deep 来源
   162|- index.md — 同步 home.md 全部更新
   163|
   164|Cross-linked all new entities to existing linux-kernel-net-subsystem, linux-kernel-netfilter-framework, and linux-network-protocols.
   165|
   166|## [2026-05-23] split | Sport-health moved to atlas
   167|Split exercise science content into Sphinxes0o0/atlas — separate Obsidian vault.
   168|Removed: 11 module indexes, ~60 entity pages, 8 source pages (relay-neuron).
   169|Remaining: ~130 tech pages (Linux kernel, C++, networking, eBPF, tools, algorithms).
   170|
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
