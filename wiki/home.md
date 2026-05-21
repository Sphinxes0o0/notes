---
type: index
tags: [navigation]
created: 2026-01-01
updated: 2026-05-21
---

# LLM Wiki — 全局导航

> 本文件由 LLM 维护，每次 ingest 后自动更新。
>
> Last updated: 2026-05-20 | Total pages: 127

---

## Sources (来源摘要)

| 来源 | 描述 | 日期 | 类型 |
|------|------|------|------|
| [[sources/relay-neuron-supplements]] | 姜黄素与辅酶Q10补剂深度研究（~30篇文献）| 2026-04 | github |
| [[sources/relay-neuron-physiology]] | 运动生理学研究：肌肥大、mTOR、BFR、VO2max等（~25主题）| 2026-05 | github |
| [[sources/notes-network-fundamentals]] | Linux 网络协议实现笔记（~78 .md 文件）| 2026-05 | github |
| [[sources/notes-network-fundamentals]] | Linux 内核网络子系统深度分析（Socket/sk_buff/Netdevice/路由）| 2026-05 | github |
| [[sources/notes-netfilter]] | Linux Netfilter/iptables/nftables/conntrack 深度分析 | 2026-05 | github |
| [[sources/notes-os]] | Linux 内核深度分析：VFS、调度器、SLUB 分配器、cgroups 架构详解 | 2026-05 | github |
| [[sources/notes-os-fundamentals]] | 操作系统基础：进程/线程、内存管理、文件系统、IO模型 | 2026-05 | github |
| [[sources/notes-qemu]] | QEMU 模拟器架构：TCG、QOM、KVM 集成、块设备、迁移 | 2026-05 | github |
| [[sources/notes-overview]] | Sphinx 技术笔记索引页 | 2026-05 | github |
| [[sources/notes-kernel]] | Linux 内核各子系统深度分析：mm、sched、block、VFS、网络、虚拟化 | 2026-05 | github |
| [[sources/notes-kernel-crypto]] | Linux 内核密码学子系统：crypto_alg注册、skcipher、aead、ahash | 2026-05 | github |
| [[sources/notes-kernel-ipc]] | Linux 内核 IPC 子系统：msg、sem、shm、mqueue | 2026-05 | github |
| [[sources/notes-kernel-locking]] | Linux 内核锁子系统：spinlock、mutex、rwsem、percpu、lockdep | 2026-05 | github |
| [[sources/notes-kernel-rcu]] | Linux 内核 RCU：Read-Copy-Update、无锁同步、grace period | 2026-05 | github |
| [[sources/notes-kernel-sound]] | Linux 内核声音子系统：ALSA、PCM、ASoC、DAPM | 2026-05 | github |
| [[sources/notes-kernel-time]] | Linux 内核时间子系统：tick、hrtimer、timekeeping、posix-timers | 2026-05 | github |
| [[sources/notes-network-fundamentals]] | 计算机网络基础：TCP/UDP、IP、Socket 编程、HTTP、DNS | 2026-05 | github |
| [[sources/notes-os-fundamentals]] | 操作系统基础课程：进程/线程、内存管理、文件系统、IO模型、网络协议 | 2026-05 | github |
| [[sources/pdf-cpp-modern-tutorial]] | Modern C++ Tutorial (C++11/14/17/20)：Lambda、智能指针、RAII、并发、Move语义 | 2026-05 | pdf |
| [[sources/pdf-cpp-effective-stl]] | Effective STL (Scott Meyers)：50条STL最佳实践，容器/迭代器/算法/仿函数 | 2026-05 | pdf |

---

## Entities / Linux Kernel — Virtualization (虚拟化)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] | KVM: 硬件虚拟化，struct kvm/vCPU，VM-Exit/Entry，EPT 页表，Dirty Ring，guest_memfd | linux-kernel, virtualization, kvm |
| [[entities/linux/kernel/virt/linux-kernel-virt-virtio]] | Virtio: 半虚拟化 I/O 框架，virtqueue ring，设备状态机，PCI/MMIO 传输 | linux-kernel, virtualization, virtio |

---

## Entities / Linux Kernel — io_uring (异步 I/O)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core]] | io_uring: 高性能异步 I/O，SQ/CQ 环，65 操作码，mmap 共享内存，io-wq | linux-kernel, async-io |

---

## Entities / Linux Kernel — VFS (虚拟文件系统)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/vfs/linux-kernel-vfs-core]] | VFS: inode/dentry/super_block/file，namei 路径查找，dcache，6 种 operations 接口 | linux-kernel, vfs, filesystem |

---

## Entities / Linux Kernel — Net (网络子系统)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/net/linux-kernel-net-subsystem]] | Linux 内核网络子系统：Socket Layer、sk_buff、Netdevice、Routing、TCP/UDP 实现 | linux-kernel, networking, socket |
| [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] | Netfilter 框架：iptables、nftables、conntrack、NAT、Hook 点 | linux-kernel, networking, netfilter |

---

## Entities / Linux Kernel — Network Protocols (网络协议)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/network/linux-network-protocols]] | TCP/IP、IPv4/IPv6、BPF/XDP、桥接、路由、QoS | linux-kernel, networking, tcp |

---

## Entities / Linux Kernel — MM (内存管理)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] | SLUB 分配器：sheaf/cmpxchg16b、freelist、per-CPU 缓存 | linux-kernel, mm, slab |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] | 缺页异常：do_page_fault、handle_mm_fault、anon/file VMA | linux-kernel, mm, paging |
| [[entities/linux/kernel/mm/linux-kernel-mm-swap]] | Swap：swap_cache XA tree、kswapd、Multi-Gen LRU | linux-kernel, mm, swap |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] | 页面回收：LRU、refault distance、working set | linux-kernel, mm, reclaim |
| [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] | mmap：VMA、Maple Tree、vm_area_struct | linux-kernel, mm, mmap |

---

## Entities / Linux Kernel — Sched (调度器)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/sched/linux-kernel-sched-core]] | 调度器核心：__schedule、pick_next_task、sched_class | linux-kernel, sched |
| [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] | CFS：vruntime 红黑树、EEVDF、latency target | linux-kernel, sched, cfs |
| [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] | 上下文切换：switch_to、寄存器保存恢复、lazy tlb | linux-kernel, sched, context-switch |
| [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] | 负载均衡：sched_domain、load_balance、idle balance | linux-kernel, sched, load-balance |

---

## Entities / Linux Kernel — Block (块设备)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/block/linux-kernel-block-core]] | 块设备层：bio/request/gendisk、block_device | linux-kernel, block |
| [[entities/linux/kernel/block/linux-kernel-block-mq]] | blk-mq：hctx/tags、software queue、hardware queue | linux-kernel, block, mq |
| [[entities/linux/kernel/block/linux-kernel-block-scheduler]] | IO 调度：mq-deadline、BFQ、elevator | linux-kernel, block, scheduler |

---

## Entities / Linux Kernel — Crypto (密码学)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/crypto/linux-kernel-crypto-core]] | Crypto 子系统：crypto_alg 注册、skcipher、aead、模板机制 | linux-kernel, crypto |

---

## Entities / Linux Kernel — Locking (锁机制)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/locking/linux-kernel-locking-core]] | 锁子系统：spinlock、mutex、rwsem、percpu、lockdep | linux-kernel, locking |

---

## Entities / Linux Kernel — IPC (进程间通信)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/ipc/linux-kernel-ipc-core]] | IPC 子系统：msg、sem、shm、mqueue、管道化发送 | linux-kernel, ipc |

---

## Entities / Linux Kernel — RCU (同步机制)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] | RCU：Read-Copy-Update、无锁读取、grace period、srcu | linux-kernel, rcu |

---

## Entities / Linux Kernel — Time (时间管理)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/time/linux-kernel-time-core]] | 时间子系统：tick、hrtimer、timekeeping、NTP、posix-timers | linux-kernel, time |

---

## Entities / Linux Kernel — Sound (声音)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/kernel/sound/linux-kernel-sound-core]] | 声音子系统：ALSA、PCM、ASoC、DAPM widget、DAI | linux-kernel, sound |

---

## Entities / Linux Kernel — QEMU (虚拟机)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/linux/qemu/qemu-qom]] | QOM: QEMU 对象模型，TypeInfo 注册、继承、接口实现 | linux-kernel, qemu |
| [[entities/linux/qemu/qemu-memory]] | QEMU 内存管理：AddressSpace、MemoryRegion、FlatView 三层结构 | linux-kernel, qemu |
| [[entities/linux/qemu/qemu-cpu]] | QEMU CPU 执行：TCG 代码生成、KVM 集成、TranslationBlock | linux-kernel, qemu |
| [[entities/linux/qemu/qemu-migration]] | QEMU 迁移框架：VMState、QEMUFile、precopy/postcopy | linux-kernel, qemu |
| [[entities/linux/qemu/qemu-block-layer]] | QEMU 块设备层：BDS 图结构、QCOW2、协程异步 I/O | linux-kernel, qemu |

---

## Entities / OS (操作系统)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/os/os-process-thread]] | 进程与线程：资源分配、状态机、上下文切换 | os, process, thread |
| [[entities/os/os-virtual-memory]] | 虚拟内存：页表、MMU、缺页中断、swap | os, virtual-memory |
| [[entities/os/os-io-model]] | I/O 模型：select/poll/epoll、阻塞/非阻塞、同步/异步 | os, io-model |
| [[entities/os/linux-vfs]] | Linux VFS: dentry/inode 缓存、RCU 路径查找、页缓存 | linux, vfs |
| [[entities/os/linux-scheduler]] | Linux 调度器：CFS、RT、Deadline、负载均衡 | linux, scheduler |
| [[entities/os/linux-memory-allocator]] | Linux 内存分配：SLUB/Buddy、sheaf 机制、cmpxchg16b | linux, memory |
| [[entities/os/linux-cgroups]] | Linux cgroups: CSS 机制、v2 单层级、CPU/内存控制器 | linux, cgroups |

---

## Entities / Exercise Science — Supplements (补剂)

### Curcumin (姜黄素)

| 实体 | 描述 | 证据强度 |
|------|------|---------|
| [[entities/exercise-science/supplements/curcumin/curcumin-overview]] | 总览：NF-κB/Nrf2/AMPK/PI3K 多靶点，抗炎抗氧化 | — |
| [[entities/exercise-science/supplements/curcumin/curcumin-diabetes]] | 糖尿病：GSK-3β↓、IAPP↓、β细胞保护 | **强** (RCT n=272) |
| [[entities/exercise-science/supplements/curcumin/curcumin-liver]] | 肝脏/MAFLD：ALT↓5.6/AST↓3.9 IU/L（荟萃分析）| **强** (荟萃分析) |
| [[entities/exercise-science/supplements/curcumin/curcumin-inflammation]] | 炎症/RA：NF-κB 抑制，HA 纳米粒靶向关节 | 中等 |
| [[entities/exercise-science/supplements/curcumin/curcumin-neuro]] | 神经：AD/PD 保护，BBB 穿透是主要瓶颈 | 中等 |
| [[entities/exercise-science/supplements/curcumin/curcumin-kidney]] | 肾脏/DN：足细胞 EMT 抑制，AMPK/mTOR 自噬 | 中等 |
| [[entities/exercise-science/supplements/curcumin/curcumin-bioavailability]] | 生物利用度：四大障碍+纳米递送技术 | 明确（机制）|

### CoQ10 (辅酶Q10)

| 实体 | 描述 | 证据强度 |
|------|------|---------|
| [[entities/exercise-science/supplements/coq10/coq10-overview]] | 总览：线粒体电子传递链+抗氧化双重角色 | — |
| [[entities/exercise-science/supplements/coq10/coq10-cardiovascular]] | 心血管：心衰 LVEF↑/死亡率↓（Q-SYMBIO）| **强** (RCT+荟萃) |
| [[entities/exercise-science/supplements/coq10/coq10-neuro]] | 神经：偏头痛预防（Neurology RCT），PD 支持 | 中等 |
| [[entities/exercise-science/supplements/coq10/coq10-statin-myopathy]] | 他汀肌病：绕过甲羟戊酸通路，支持线粒体 | **强** (RCT) |
| [[entities/exercise-science/supplements/coq10/coq10-bioavailability]] | 生物利用度：泛醇 vs 泛醌，老人/患者选泛醇 | 明确 |

---

## Entities / Exercise Science — Physiology (运动生理学)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/physiology/muscle-hypertrophy]] | 肌肥大三大机制：机械张力、代谢应激、肌肉损伤 | exercise-science, muscle-hypertrophy |
| [[entities/exercise-science/physiology/mtor-pathway]] | mTORC1 通路：蛋白质合成核心调控因子 | exercise-science, mtor |
| [[entities/exercise-science/physiology/mps-muscle-protein-synthesis]] | 肌肉蛋白合成（MPS）：亮氨酸阈值~2-3g/餐 | exercise-science, protein-metabolism |
| [[entities/exercise-science/physiology/vo2max]] | VO2max：有氧耐力的核心指标 | exercise-science, cardio |
| [[entities/exercise-science/physiology/lactate-threshold]] | 乳酸阈值：乳酸产生与清除的平衡点 | exercise-science, metabolism |
| [[entities/exercise-science/physiology/bfr-training]] | 血流限制训练：低负荷高合成代谢效应 | exercise-science, BFR |
| [[entities/exercise-science/physiology/concurrent-training]] | 并发训练：有氧+阻力组合与协调效应 | exercise-science, methodology |
| [[entities/exercise-science/physiology/training-frequency]] | 训练频率：每周训练次数与恢复 | exercise-science, programming |
| [[entities/exercise-science/physiology/fatigue-recovery]] | 疲劳与恢复：机制与策略 | exercise-science, recovery |
| [[entities/exercise-science/physiology/satellite-cells]] | 卫星细胞：肌肉再生与适应的干细胞 | exercise-science, stem-cells |

---

## Entities / Exercise Science — Nutrition (营养学)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/nutrition/protein]] | 蛋白质：亮氨酸阈值、蛋白质合成、每日摄入量 | exercise-science, nutrition |
| [[entities/exercise-science/nutrition/carb-periodization]] | 碳水 Periodization：训练前后糖原补充、碳水上瘾 | exercise-science, nutrition |
| [[entities/exercise-science/nutrition/omega3]] | Omega-3：抗炎、肌肉合成、认知功能 | exercise-science, nutrition |
| [[entities/exercise-science/nutrition/ketogenic-diet]] | 生酮饮食：碳水限制、酮体代谢、适应性 | exercise-science, nutrition |

---

## Entities / Exercise Science — Running (跑步)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/running/running-economy]] | Running Economy：跑步经济性，VO2max 效率 | exercise-science, running |
| [[entities/exercise-science/running/trail-running]] | 越野跑：技术地形、上下坡、装备选择 | exercise-science, running |
| [[entities/exercise-science/running/ultra-endurance]] | 超级马拉松：超长距离补给、适应性、恢复 | exercise-science, running |

---

## Entities / Exercise Science — Training (训练)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/training/periodization]] | Periodization：线性/波浪式/块状 periodization | exercise-science, training |
| [[entities/exercise-science/training/tapering]] | Tapering：比赛前减量、超级补偿 | exercise-science, training |
| [[entities/exercise-science/training/training-methods]] | 训练方法：EIA、乳酸阈值、间歇训练 | exercise-science, training |

---

## Entities / Exercise Science — Biomechanics (生物力学)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/biomechanics/gait-analysis]] | Gait Analysis：步态分析、触地时间、垂直振荡 | exercise-science, biomechanics |
| [[entities/exercise-science/biomechanics/running-shoes]] | Running Shoes：缓震、转弯支撑、碳板跑鞋 | exercise-science, biomechanics |

---

## Entities / Exercise Science — Health (健康)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/exercise-science/health/exercise-disease]] | Exercise as Medicine：运动与慢性病预防、处方 | exercise-science, health |

---

## Entities / Data Structures & Algorithms (数据结构与算法)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/datastructure/algorithm-complexity]] | 时间/空间复杂度分析，O(n)/O(log n)/O(n²) | datastructure, algorithm |
| [[entities/datastructure/linear-data-structures]] | 数组、链表、栈、队列 | datastructure, linear |
| [[entities/datastructure/sorting-algorithms]] | 冒泡/插入/归并/快排对比 | datastructure, sorting |
| [[entities/datastructure/dynamic-programming]] | 最短路径、状态转移方程、最优子结构 | algorithm, DP |
| [[entities/datastructure/recursion-and-divide-conquer]] | 汉诺塔、分治法、二分查找 | algorithm, recursion |
| [[entities/datastructure/hash-table]] | 哈希函数、冲突处理、O(1) 查找 | datastructure, hash |
| [[entities/datastructure/trees-and-graphs]] | 二叉树、BST、堆、BFS/DFS | datastructure, tree |

---

## Entities / Design Patterns (设计模式)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/design-patterns/solid-principles]] | SOLID 五大原则：SRP/OCP/LSP/ISP/DIP | design-pattern |
| [[entities/design-patterns/design-principles-advanced]] | DIP、关注点分离(SoC)、契约设计 | design-pattern, principles |
| [[entities/design-patterns/creational-patterns]] | 单例/工厂/建造者/原型模式 | design-pattern, creational |
| [[entities/design-patterns/structural-patterns]] | 适配器/桥接/组合/装饰/门面/享元/代理 | design-pattern, structural |
| [[entities/design-patterns/behavioral-patterns]] | 策略/状态/观察者/命令/模板方法/责任链 | design-pattern, behavioral |

---

## Entities / Interview Preparation (面试准备)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/interview/interview-preparation]] | 边学边练、白板编码、语言选择 | interview |
| [[entities/interview/problem-solving-patterns]] | 两指针/滑动窗口/BFS/DFS/DP 模式 | interview, algorithm |
| [[entities/interview/system-design-basics]] | 可扩展性、负载均衡、CAP 定理、一致性哈希 | interview, system-design |

---

## Entities / System Programming (系统编程)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/cpp]] | C/C++ 系统编程：内存模型、STL 容器、设计模式 | C, C++, 系统编程 |
| [[entities/sys]] | Linux 系统编程：ELF 格式、进程间通信、设计模式 | Linux, IPC, ELF |
| [[entities/midware]] | 中间件：DoIP 诊断协议、vSOMEIP 服务发现架构 | 汽车电子, SOME/IP |
| [[entities/security]] | 安全工具：Masscan 高速扫描、Falco 运行时监控、Snort NIDS | 安全, 扫描, 检测 |

---

## Entities / Modern C++ (现代C++特性)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/cpp/move-semantics]] | 移动语义：右值引用、std::move、std::forward、值类别 | cpp, modern-cpp |
| [[entities/cpp/smart-pointers]] | 智能指针：shared_ptr、unique_ptr、weak_ptr | cpp, modern-cpp |
| [[entities/cpp/lambda-expressions]] | Lambda表达式：捕获、mutable、泛型Lambda | cpp, modern-cpp |
| [[entities/cpp/auto-type-deduction]] | 类型推导：auto、decltype、decltype(auto) | cpp, modern-cpp |
| [[entities/cpp/constexpr]] | constexpr编译时计算：C++11/14的编译期求值 | cpp, modern-cpp |
| [[entities/cpp/raii]] | RAII资源管理：构造/析构自动管理资源 | cpp, modern-cpp |
| [[entities/cpp/concurrency]] | 并发编程：std::thread、mutex、atomic、future | cpp, modern-cpp |
| [[entities/cpp/variadic-templates]] | 模板变参：参数包展开、sizeof...、折叠表达式 | cpp, modern-cpp |
| [[entities/cpp/if-constexpr]] | if constexpr：编译时分支、编译期多态 | cpp, modern-cpp |
| [[entities/cpp/cpp20-features]] | C++20新特性：Concepts、Modules、Coroutines、Ranges | cpp, modern-cpp, cpp20 |

## Entities / STL (标准模板库)

| 实体 | 描述 | 标签 |
|------|------|------|
| [[entities/cpp/cpp-stl-containers]] | STL容器：vector/deque/list/set/map，无序容器 | cpp, stl |
| [[entities/cpp/cpp-stl-algorithms]] | STL算法：sort/find/remove/transform，迭代器配合 | cpp, stl |
| [[entities/cpp/cpp-stl-iterators]] | STL迭代器：类别、失效规则、适配器 | cpp, stl |
| [[entities/cpp/cpp-stl-functors]] | STL函数对象：仿函数、Lambda、函数适配器 | cpp, stl |
| [[entities/cpp/cpp-stl-string]] | STL字符串：string实现、string_view、高效操作 | cpp, stl |
| [[entities/cpp/cpp-stl-allocators]] | STL分配器：内存管理、自定义分配器、allocator_traits | cpp, stl |

---

## Synthesis (综合分析)

| 主题 | 描述 | 日期 |
|------|------|------|
| [[synthesis/topic-os-fundamentals]] | 操作系统基础综合：进程/线程、内存管理、文件系统、网络、并发 | 2026-05 |
| [[synthesis/topic-network-fundamentals]] | 计算机网络基础综合：TCP/IP 五层模型、Socket 编程、HTTP 缓存、安全 | 2026-05 |

---

## Journal (日记)

> 待补充

---

## 交叉引用索引

### Linux Kernel × 虚拟化

- [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] → [[entities/linux/kernel/virt/linux-kernel-virt-virtio]]：KVM 通常作为 Virtio 的 host 端
- [[entities/linux/kernel/virt/linux-kernel-virt-virtio]] → [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core]]：Virtio 设备可与 io_uring 协同工作
- [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] → [[entities/linux/kernel/vfs/linux-kernel-vfs-core]]：KVM 虚拟机的磁盘 I/O 最终通过 VFS
- [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core]] → [[entities/linux/kernel/vfs/linux-kernel-vfs-core]]：io_uring 操作调用 VFS 的 file_operations

### Linux Kernel × 网络

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] → [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]]：Socket → sk_buff → Netfilter Hooks 数据路径
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] → [[entities/linux/network/linux-network-protocols]]：TCP/UDP/Routing 协议实现
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] → [[entities/linux/network/linux-network-protocols]]：conntrack 集成于协议栈

### 补剂 × 运动生理学

- [[entities/exercise-science/supplements/curcumin/curcumin-overview]] → [[entities/exercise-science/physiology/fatigue-recovery]]：姜黄素抗炎支持运动恢复
- [[entities/exercise-science/supplements/coq10/coq10-overview]] → [[entities/exercise-science/physiology/fatigue-recovery]]：CoQ10 线粒体能量支持运动恢复
- [[entities/exercise-science/supplements/coq10/coq10-overview]] → [[entities/exercise-science/physiology/muscle-hypertrophy]]：CoQ10 对肌肉能量代谢的影响

### 补剂 × 代谢疾病

- [[entities/exercise-science/supplements/curcumin/curcumin-diabetes]] ↔ [[entities/exercise-science/supplements/curcumin/curcumin-liver]]：MAFLD 与 T2DM 高度相关
- [[entities/exercise-science/supplements/curcumin/curcumin-diabetes]] ↔ [[entities/exercise-science/supplements/curcumin/curcumin-kidney]]：糖尿病并发症连续体
