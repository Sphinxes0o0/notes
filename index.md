---
type: index
created: 2026-05-22
---

# LLM Wiki

> **~95 pages. 15 module indexes.**
> Each module index acts as a sub-hub in the Obsidian graph view.

## Module Indexes

### Linux Kernel
| Index | Domain |
|-------|--------|
| [[wiki/kernel-virt-index]] | KVM, Virtio virtualization |
| [[wiki/kernel-io-index]] | io_uring, VFS |
| [[wiki/kernel-net-index]] | Socket/sk_buff, Netfilter, TCP/IP protocols |
| [[wiki/kernel-protocols-index]] | Protocol details, full-stack path, PHY/MAC layer |
| [[wiki/kernel-mm-index]] | SLUB, page fault, swap, page reclaim, mmap |
| [[wiki/kernel-sched-index]] | CFS, context switch, load balancing |
| [[wiki/kernel-block-index]] | bio/request, blk-mq, IO schedulers |
| [[wiki/kernel-subsystems-index]] | Crypto, locking, IPC, RCU, time, sound |
| [[wiki/kernel-books-index]] | Linux/Kernel书籍索引：内核/TLPI/APUE/CSAPP/网络/并发 (9 books) |
| [[wiki/ebpf-index]] | XDP, TC, Cilium, Falco, CO-RE, eBPF ecosystem |

### Emulation
| Index | Domain |
|-------|--------|
| [[wiki/qemu-index]] | QOM, memory, CPU, migration, block layer |

### Operating System
| Index | Domain |
|-------|--------|
| [[wiki/os-index]] | Process/thread, virtual memory, I/O models, Linux subsystems |

### Programming & Algorithms
| Index | Domain |
|-------|--------|
| [[wiki/datastructure-index]] | DSA: arrays, sorting, DP, trees, graphs |
| [[wiki/design-patterns-index]] | SOLID, creational, structural, behavioral |
| [[wiki/interview-index]] | Coding patterns, system design basics |
| [[wiki/cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms |
| [[wiki/sys-prog-index]] | C/C++, Linux, middleware, security |

### C++ Frameworks & Libraries
| Index | Domain |
|-------|--------|
| [[wiki/workflow-index]] | Sogou Workflow async engine: HTTP/Redis/MySQL/Kafka/DNS |
| [[wiki/cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms |

### Tools & BMC
| Index | Domain |
|-------|--------|
| [[wiki/tools-index]] | tcpdump, netcat, masscan, nmap |
| [[wiki/openbmc-index]] | IPMI, Redfish, boot/firmware update, hardware control |

### Snort3 IDS/IPS
| Index | Domain |
|-------|--------|
| [[wiki/entities/linux/snort3/snort3-framework]] | Plugin system, lifecycle, pig, shell |
| [[wiki/entities/linux/snort3/snort3-actions]] | Rule actions |
| [[wiki/entities/linux/snort3/snort3-connectors]] | Service connectors (TCP/UDP/file/popen) |
| [[wiki/entities/linux/snort3/snort3-events-filters]] | Event generation, 3-layer filter architecture |
| [[wiki/entities/linux/snort3/snort3-flow]] | Flow tracking |
| [[wiki/entities/linux/snort3/snort3-ips-options]] | IPS options |
| [[wiki/entities/linux/snort3/snort3-infrastructure]] | Hash tables, file_api, decompress, js_norm, helpers |
| [[wiki/entities/linux/snort3/snort3-control-startup]] | Control and startup |

## Sources
| Source | Description |
|--------|-------------|
| [[wiki/sources/notes-net-deep]] | 网络深度笔记：skbuff/NAT/路由 Trie/PHY-MAC/Conntrack/全栈 |
| [[wiki/sources/notes-network-fundamentals]] | Linux 网络协议实现笔记 |
| [[wiki/sources/notes-netfilter]] | Linux Netfilter/iptables/nftables/conntrack |
| [[wiki/sources/notes-os]] | Linux 内核深度分析：VFS、调度器、SLUB、cgroups |
| [[wiki/sources/notes-os-fundamentals]] | 操作系统基础：进程/线程、内存管理、文件系统、IO模型 |
| [[wiki/sources/notes-qemu]] | QEMU 模拟器架构：TCG、QOM、KVM 集成、块设备 |
| [[wiki/sources/notes-overview]] | Sphinx 技术笔记索引页 |
| [[wiki/sources/notes-kernel]] | Linux 内核各子系统深度分析 |
| [[wiki/sources/notes-kernel-crypto]] | Linux 内核密码学子系统 |
| [[wiki/sources/notes-kernel-ipc]] | Linux 内核 IPC 子系统 |
| [[wiki/sources/notes-kernel-locking]] | Linux 内核锁子系统 |
| [[wiki/sources/notes-kernel-rcu]] | Linux 内核 RCU |
| [[wiki/sources/notes-kernel-sound]] | Linux 内核声音子系统 |
| [[wiki/sources/notes-kernel-time]] | Linux 内核时间子系统 |
| [[wiki/sources/bookmark-wowotech-linux-kernel]] | 蜗窝科技 Linux内核分析：Kernel 4.14 ARM64，块设备/内存/调度/网络 |
| [[wiki/sources/bookmark-linux-inside]] | Linux Inside：内核入门经典，boot/interrupt/sync/memory/Cgroups |
| [[wiki/sources/bookmark-linux-source-code-analyze]] | Linux内核源码分析 (liexusong, 1.6k stars)：60+文档覆盖进程/内存/网络/容器/eBPF |
| [[wiki/sources/bookmark-linux-interrupt-loyenwang]] | Linux中断子系统 (LoyenWang)：ARM64 Kernel 4.14，控制器/softirq/tasklet/workqueue |
| [[wiki/sources/bookmark-linux-kernel-map]] | Interactive Kernel Map：SVG可缩放80倍，从硬件接口到系统调用的内核组件地图 |
| [[wiki/sources/bookmark-linux-kernel-labs]] | Linux内核教学 (中文)：理论+实验，内存/调度/系统调用/interrupt/lock/VM |
| [[wiki/sources/bookmark-linux-kernel-explorer]] | Linux Kernel Explorer (Reverser.dev)：在线内核源码浏览器，符号搜索/XREF导航 |
| [[wiki/sources/bookmark-edsionte-kernel-beginner]] | 内核新手区 (Edsionte)：最低门槛内核入门，进程/内存/VFS/设备驱动/系统调用 |
| [[wiki/sources/notes-tools]] | 工具使用笔记：tcpdump、netcat、masscan/nmap |
| [[wiki/sources/notes-openbmc]] | OpenBMC 深度技术分析 |
| [[wiki/sources/pdf-cpp-modern-tutorial]] | Modern C++ Tutorial (C++11/14/17/20) |
| [[wiki/sources/pdf-cpp-effective-stl]] | Effective STL (Scott Meyers) |
| [[wiki/sources/pdf-ebpf-books]] | eBPF书籍3册: 龙蜥白皮书+技术实践+Liz Rice入门 |
| [[wiki/sources/pdf-ebpf-papers]] | eBPF论文10篇: Thomas Graf微内核愿景+微服务感知OS+Apple Falco+Google KRSI+Black Hat Rootkit+UFMG XDP+生态库+saBPF容器审计+Isovalent安全可观测性+PTPsec |
| [[wiki/sources/workflow-engine]] | Sogou Workflow C++ 异步引擎：架构核心17篇+教程18篇，13种协议支持 |
| [[wiki/sources/notes-ccpp]] | C/C++ 技术笔记：序列化、智能指针、堆栈对象创建、移动语义 |
| [[wiki/sources/github-modern-cpp-features]] | Modern C++ Features Reference (C++11/14/17/20/23)：AnthonyCalandra 100+ features with examples |
| [[wiki/sources/notes-datastructure]] | 数据结构与算法：复杂度、线性结构、排序、DP、递归、哈希表、树与图 |
| [[wiki/sources/notes-design-patterns]] | 设计模式：SOLID、创建型5种、结构型7种、行为型11种共23种 |
| [[wiki/sources/notes-interview]] | 面试准备：方法论、问题解决模式、系统设计基础、NP完全性、位操作 |
| [[wiki/sources/notes-midware]] | 中间件：DoIP协议（ISO 13400）、SOME/IP服务通信、vSOME/IP开源实现 |
| [[wiki/sources/notes-security]] | 安全工具：Masscan高速端口扫描、Falco K8s安全监控、Snort 3 NIDS |
| [[wiki/sources/bookmark-cpp-core-guidelines]] | C++ Core Guidelines 中文版：Bjarne Stroustrup 官方安全规范（类型安全、资源管理、并发） |
| [[wiki/sources/bookmark-stl-source-analysis]] | STL 源码分析 (SGI STL 3.0)：52个文件覆盖配置器/迭代器/容器/算法/函数对象 |
| [[wiki/sources/bookmark-cpp-design-patterns]] | C++ 设计模式：GoF 23种+7种额外模式，30个C++实现，2.6k stars |
| [[wiki/sources/bookmark-modern-cmake]] | Modern CMake 教程（中文版）：3.1+ 构建系统最佳实践，纠正网上错误用法 |
| [[wiki/sources/bookmark-effective-modern-cpp]] | Effective Modern C++ 中文版：Scott Meyers 42条款覆盖移动语义/lambda/并发/智能指针 |
| [[wiki/sources/bookmark-cpp-concurrency-in-action]] | C++ Concurrency in Action 第2版 (Web版)：C++20 jthread/semaphore/barrier 补充 |
| [[wiki/sources/bookmark-modern-cpp-programming]] | Modern C++ Programming：Federico Busato 课程，29章节含性能优化/二进制大小/构建工程 |
| [[wiki/sources/bookmark-hacking-cpp]] | Hacking C++：代码示例+信息图表快速参考，可视化 cheat sheets |
| [[wiki/sources/github-snort3-infrastructure]] | Snort3 infrastructure: hash/XHash/ZHash, file_api, decompress, js_norm |
| [[wiki/sources/notes-sys]] | 系统编程：TTY/Shell/Console体系、ELF文件格式、Linux IPC |
| [[wiki/sources/pdf-the-linux-programming-interface]] | TLPI (Kerrisk, 1556页)：Linux/UNIX系统编程百科，500+系统调用 |
| [[wiki/sources/pdf-unix-environment-advanced-programming]] | APUE 第三版 (Stevens & Rago, 822页)：UNIX环境高级编程（扫描版）|
| [[wiki/sources/pdf-computer-systems-programmers-perspective]] | CS:APP (Bryant & O'Hallaron, 1078页)：计算机系统程序员视角，CMU 15-213 |
| [[wiki/sources/pdf-onedrive-batch1]] | OneDrive Batch P: OS concepts + C++ concurrency/high-performance/templates-v2 |
| [[wiki/sources/pdf-slides]] | C++ & Compiler Slides: 58 conference talks in 6 categories |
| [[wiki/sources/pdf-slides-cpp-standard]] | C++ Slides: 语言演进/标准化/反射/对象生命周期/嵌入式 (8 talks) |
| [[wiki/sources/pdf-slides-ai-coding]] | C++ Slides: AI Coding Agent/Coding/安全防御 (6 talks) |
| [[wiki/sources/pdf-slides-ai-compiler]] | C++ Slides: AI Compiler/MLIR/RISC-V生态 (5 talks) |
| [[wiki/sources/pdf-slides-llm-inference]] | C++ Slides: LLM推理/Mooncake/xLLM/DeepSeek/FlagScale/异构计算 (11 talks) |
| [[wiki/sources/pdf-slides-kernel]] | C++ Slides: Linux Kernel/调试/Btree/Kernel-bypass (4 talks) |
| [[wiki/sources/pdf-slides-tools]] | C++ Slides: EPI面试/Python刷题/Qoder CLI (2 talks) |
| [[wiki/sources/pdf-cpp-bjarne-40years]] | Bjarne Stroustrup C++ 40年演讲：成功因素、AI时代定位、C++26方向 |
| [[wiki/sources/pdf-mlir-fuzzing]] | MLIR编译器模糊测试：覆盖率引导fuzzing发现pass间bug |
| [[wiki/sources/pdf-ai-compiler-stack]] | AI编译器软件栈：SigInfer推理引擎/国产卡CUDA兼容/AI编译器自动生成 |
| [[wiki/sources/pdf-xllm-inference]] | xLLM大模型推理引擎：PD分离/EPD解耦/C++全栈/DAG调度 |
| [[wiki/sources/pdf-riscv-ai-compiler]] | RISC-V大模型推理AI编译器：软硬件协同设计/V扩展/代价模型 |
| [[wiki/sources/pdf-rtp-llm]] | RTP-LLM阿里大模型推理引擎：MoE专家模型/投机采样/分布式架构 |
| [[wiki/sources/pdf-mooncake]] | Mooncake解耦式大模型推理：KVCache Pool分层存储/以存换算 |
| [[wiki/sources/pdf-flagscale]] | FlagScale大模型训练推理框架：FlagCX统一通信库/FlagOS生态 |
| [[wiki/sources/pdf-llm-edge-storage]] | 端侧大模型部署：AIOS架构/存储系统挑战/KVCache分层 |
| [[wiki/sources/pdf-book-modern-cpp]] | The Book of Modern C++ 第二版：1053页多人合著C++20/23高级主题 |
| [[wiki/sources/pdf-trustzone-optee]] | TrustZone与OP-TEE技术详解：786页ARM硬件安全扩展权威著作 |
| [[wiki/sources/pdf-commercial-crypto-assessment]] | 商用密码应用安全性评估考核题：622页SM算法/密评/等级保护2.0 |
| [[wiki/sources/pdf-openssl-cookbook]] | OpenSSL Cookbook中文版：72页密钥生成/证书管理/SSL测试实用手册 |
| [[wiki/sources/pdf-ebpf-technical-practice]] | eBPF技术实践v2（龙蜥社区）：100页XDP/TC/CO-RE工具链 |
| [[wiki/sources/arthurchiao-linux-cpu-power-management]] | Linux CPU power management: P-states, C-states, TDP, hyperthreading |
| [[wiki/sources/arthurchiao-linux-net-stack]] | Linux network stack overview: IRQ/softirq, RX/TX, BPF/XDP, monitoring |
| [[wiki/sources/arthurchiao-linux-net-stack-implementation-rx]] | Linux network RX implementation: NAPI, DMA ring buffer, 9-stage pipeline |
| [[wiki/sources/arthurchiao-linux-net-stack-tuning-rx]] | Linux network RX tuning: ethtool, RSS, RPS, GRO, softirq budget |
| [[wiki/sources/arthurchiao-linux-irq-softirq]] | Linux IRQ/softirq: hard IRQ, softirq subsystem, tasklets, workqueues |
| [[wiki/sources/arthurchiao-bbr-paper]] | BBR congestion control: BtlBw/RTprop measurement, zero queue operation |
| [[wiki/sources/arthurchiao-facebook-xdp-to-socket]] | Facebook XDP/eBPF: Katran L4 LB, Maglev hashing, bpf_sk_reuseport |
| [[wiki/sources/arthurchiao-pki]] | PKI and certificates: CA hierarchy, trust stores, mTLS, certificate chain |
| [[wiki/sources/arthurchiao-modern-lb-proxy]] | Modern load balancing: L4 vs L7, topology, ECMP, service mesh |
| [[wiki/sources/arthurchiao-tc-da-mode]] | TC eBPF direct-action mode: clsact, action verdicts, cls_bpf filter |
| [[wiki/sources/arthurchiao-conntrack-design]] | Conntrack design: netfilter hooks, two-phase creation, NAT dependency |
| [[wiki/sources/arthurchiao-sockmap-ebpf]] | eBPF sockmap: socket redirection bypassing TCP/IP stack, sockops/sk_msg |
| [[wiki/sources/reading-ebpf-how-ebpf-work]] | eBPF深入理解 NoPanic：Verifier/JIT/Maps/Tail Call/XDP vs TC性能排名 |
| [[wiki/sources/reading-af-xdp-technical]] | AF_XDP技术详解：UMEM/ring/bpf_redirect_map/XSKMAP零拷贝 |
| [[wiki/sources/reading-linux-advanced-routing-tc]] | Linux Advanced Routing & TC HOWTO：iproute2/qdisc/netem/Netfilter/QoS |
| [[wiki/sources/reading-linux-tc-traffic-control]] | Linux TC流量控制 NoPanic：qdisc(netem/tbf)/NIDS测试仿真 |
| [[wiki/sources/reading-tcp-troubleshooting-plantegg]] | TCP疑难问题 plantegg：CLOSE_WAIT/queue溢出/TTL fingerprint/ss/netstat |
| [[wiki/sources/reading-tcp-self-connection-plantegg]] | TCP自连接 plantegg：simultaneous open/四元组/bind vs connect |
| [[wiki/sources/reading-software-performance-deep-thinking]] | 深入理解软件性能 NoPanic：profiling/latency/throughput/CPU+内存优化 |
| [[wiki/sources/reading-linux-performance-engineering]] | Linux性能优化实战：perf/bpftrace/tcpdump/sar/典型瓶颈场景 |
| [[wiki/sources/reading-lwip-bridge-implementation]] | LwIP网桥实现 catboy：二层转发/netif/packet flow |
| [[wiki/sources/achieved-arp-table-aging]] | Linux ARP表老化机制：三状态(delay/reachable/stale)与gc_thresh1 |
| [[wiki/sources/achieved-tcp-bypass-notes]] | TCP Bypass：RDMA/iWARP/RoCE/InfiniBand零拷贝与超低延迟 |
| [[wiki/sources/achieved-tcp-sack-dsack]] | TCP SACK/DSACK：Linux内核v18/v37实现对比与scoreboard标签 |
| [[wiki/sources/achieved-ebpf-android]] | Android eBPF Doze模式：tcp_v4_do_rcv钩子与UID流量控制 |
| [[wiki/sources/achieved-linux-packet-flow]] | Linux网络包流转：Ring Buffer/NAPI/sk_buff/SoftIRQ完整路径 |
| [[wiki/sources/achieved-plantegg-method]] | plantegg举三反一：TCP CLOSE_WAIT诊断案例 |
| [[wiki/sources/achieved-bluepuni-blog]] | Caturra's Blog: packetdrill TCP分析/Linux内核/eBPF/C++优化 |
| [[wiki/sources/pdf-ebpf-basics]] | eBPF基础：80页入门/11个64位寄存器/CO-RE/BTF/Pinning机制 |
| [[wiki/sources/pdf-computer-architecture-hp]] | Hennessy & Patterson计算机体系结构量化研究方法（第五版）612页 |

## Synthesis
| Topic | Description |
|-------|-------------|
| [[wiki/synthesis/topic-os-fundamentals]] | OS fundamentals synthesis |
| [[wiki/synthesis/topic-network-fundamentals]] | Network fundamentals synthesis |
