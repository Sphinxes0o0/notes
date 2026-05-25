# Log — LLM Wiki 操作日志

> Append-only。格式：`## [YYYY-MM-DD] action | detail`

---

## [2026-05-25] ingest | Batch I: Sogou Workflow Engine (C++ async framework)

- **来源**: raw/workflow/ (36 docs: 17 architecture + 18 tutorials + 1 xmake)
- **操作**:
  - 创建 17 个 architecture entity pages: workflow-async-model, workflow-go-task, workflow-counter, workflow-timer, workflow-selector, workflow-conditional, workflow-module-task, workflow-graph-task, workflow-resource-pool, workflow-config, workflow-error-handling, workflow-exit-handling, workflow-timeout, workflow-upstream, workflow-service-governance, workflow-tlv-message, workflow-dns, workflow-connection-context, workflow-benchmark, workflow-known-bugs
  - 创建 8 个 tutorial entity pages: workflow-network-client, workflow-parallel-tasks, workflow-compute-tasks, workflow-http-server, workflow-user-defined-protocol, workflow-name-service, workflow-redis-features, workflow-dns-server
  - 创建 1 个 source page: wiki/sources/workflow-engine.md
  - 创建 1 个 module index: wiki/workflow-index.md
- **更新**: index.md (workflow-index + workflow-engine source), log.md
- **核心概念**: Sogou Workflow C++ 异步引擎，13+ 协议支持 (HTTP/Redis/MySQL/Kafka/DNS)，DAG 任务模型，Upstream 负载均衡与熔断，性能 500K QPS

---

## [2026-05-25] ingest | Batch D: safeos-lwip-core lwIP Core Network Protocol

- **来源**: raw/safeos/lwip_*.md (~28 分析文档)
- **操作**:
  - 创建 27 个 entity 页面: lwip-netif, lwip-netif-add, lwip-ethernet-input, lwip-ethernet-output, lwip-pbuf, lwip-malloc, lwip-ip4-input, lwip-ip4-output, lwip-routing, lwip-ip-fragmentation, lwip-tcp-input, lwip-tcp-output, lwip-tcp-pcb, lwip-tcp-recv-queue, lwip-tcp-socket, lwip-tcpip-thread, lwip-udp-input, lwip-udp-output, lwip-udp-socket, lwip-igmp, lwip-dhcp, lwip-network-init, lwip-vlan-dispatch, lwip-vlan-dispatch-deep, lwip-vlan-hook, lwip-vlan-implementation, lwip-vlan-parsing
  - 创建 1 个 source 页面: wiki/sources/safeos-lwip-core.md
  - 创建 1 个 module index: wiki/lwip-index.md
- **更新**: wiki/home.md (lwip-index + safeos-lwip-core 入口), log.md
- **核心概念**: lwIP 嵌入式协议栈，LWIP_TCPIP_CORE_LOCKING=1 模式，VLAN 分发机制，TCP/UDP/IGMP/DHCP 协议实现

---

## [2026-05-22] restructure | 模块索引重构 + 全量 ingest

- **Phase 1**: 拆分 home.md → 21 个模块索引文件 (wiki/{module}-index.md)
- **Phase 2**: relay-neuron 肥胖文献 (23篇) → 6 entity + 1 source + 1 index
- **Phase 3**: notes 剩余 (OpenBMC 5 + tools 5 + net/network 10 + ccpp 4) → 12 entity + 4 source + 4 index
- **Phase 4**: .meta.md 确认已存在
- **Phase 5**: QA — Cross-Link Gate PASS (124/124), 0 broken wikilinks
- **总增长**: 127 → 185 pages (+58), entities 95 → 124 (+29), indexes 0 → 25

---

## [2026-05-22] ingest | relay-neuron 剩余内容 (technology/kinesiology-tape/population/training-methods)

- **技术 (10文件)**: 可穿戴设备、HRV监控、跑步功率计、AI/ML预测、实时生理监控、ACSM指南、SCSEPF会议、JESF/SMHS期刊
  - 3 entity: wearable-devices, hrv-training, running-power-meter
  - 1 source: relay-neuron-technology
- **肌贴 (6文件)**: 机制、肌肉力量、关节疼痛、临床应用、最新综述
  - 1 entity: kinesiology-tape (合并机制+临床)
  - 1 source: relay-neuron-kinesiology-tape
- **人群专项 (6文件)**: 青少年、中老年、女性、精英、休闲跑者、儿童体能认知
  - 4 entity: youth-runners, master-runners, female-runners, elite-athletes
  - 1 source: relay-neuron-population-specific
- **训练方法 (5文件)**: 间歇、节奏跑、LSD、阈值、坡度训练
  - 1 entity (update): training-methods.md 新增5种训练方法内容
  - 1 source: relay-neuron-training-methods
- **Indexes**: technology-index, kinesiology-tape-index, population-index
- **Hub更新**: home.md + index.md (3 indexes + 4 sources)
- **总增长**: +8 entity pages, +4 source pages, +3 module indexes

---

## [2026-05-20] init | Initialized llm-wiki structure

- 创建目录结构
- 创建 AGENT.md（维护手册）
## [2026-05-20] ingest | PDFs from ~/Documents

- 移动 58 个 PDF → `raw/PDFs/`
- 分类归档：books(3) + papers(10) + slides(37)，去重 7 本（已在 books/）
- 更新 AGENT.md：`docs` → `slides`
- 当前总计：books(61) + papers(10) + slides(37) = 108 PDFs

## [2026-05-20] ingest | relay-neuron-exercise-physiology

**来源**: raw/github/relay-neuron/research/exercise-physiology/ (25 .md files)
**操作**:
- 创建 10 个 entity 页面: muscle-hypertrophy, mtor-pathway, mps-muscle-protein-synthesis, vo2max, lactate-threshold, bfr-training, concurrent-training, training-frequency, fatigue-recovery, satellite-cells
- 创建 1 个 source 页面: github-relay-neuron-exercise-physiology
- 更新 wiki/index.md

**核心概念**: 肌肥大三大机制 (Schoenfeld), mTOR 通路, MPS, BFR训练, 并发训练协调效应, VO2max/乳酸阈值训练

## [2026-05-20] ingest | notes/qemu + notes/os + notes/os_fundamentals

**来源**: raw/github/notes/qemu/ (5 deep-dive files), raw/github/notes/os/ (4 deep-dive files), raw/github/notes/os_fundamentals/ (39 lectures)

**操作**:
- 创建 5 个 QEMU entity 页面: qemu-qom, qemu-memory, qemu-cpu, qemu-block-layer, qemu-migration
- 创建 7 个 OS entity 页面: linux-vfs, linux-scheduler, linux-memory-allocator, linux-cgroups, os-io-model, os-process-thread, os-virtual-memory
- 更新 wiki/index.md

**核心概念**:
- QEMU: QOM对象模型、AddressSpace/MemoryRegion内存管理、TCG CPU执行、BDS图结构、VMState迁移
- Linux: VFS RCU路径查找、CFS红黑树调度、SLUB sheaf/cmpxchg16b、Buddy分配器、cgroups CSS机制
- OS: 进程vs线程开销、虚拟内存/页表、select/poll/epoll对比

## [2026-05-20] ingest | relay-neuron-supplements (curcumin + CoQ10)


## [2026-05-20] ingest | notes/kernel (mm/sched/block subsystems)

**来源**: raw/github/notes/kernel/ — Linux 内核子系统索引
**操作**:
- 创建 12 个 MM/Sched/Block entity 页面
- 创建 1 个 source 导航页面: github-sphinxes0o0-notes-kernel
- 更新 wiki/index.md

**Entity 页面**:
- MM: linux-kernel-mm-slab-allocator, mm-page-fault, mm-swap, mm-page-reclaim, mm-mmap
- Sched: linux-kernel-sched-core, sched-cfs, sched-context-switch, sched-load-balance
- Block: linux-kernel-block-core, block-mq, block-scheduler

**核心概念**:
- MM: SLUB sheaf/barn, 缺页中断 do_page_fault, swap_cache XA tree, kswapd/Multi-Gen LRU, mmap VMA/Maple Tree
- Sched: CFS vruntime/EEVDF, __schedule/context_switch, sched_domain load_balance
- Block: bio/request/gendisk, blk-mq hctx/tags, mq-deadline/BFQ elevator



**来源**: raw/github/relay-neuron/research/supplements/ (姜黄素~20篇/7类 + 辅酶Q10~10篇/5类)

**操作**:
- 创建 7 个 curcumin entity 页面: curcumin-overview, curcumin-diabetes, curcumin-liver, curcumin-inflammation, curcumin-neuro, curcumin-kidney, curcumin-bioavailability
- 创建 5 个 CoQ10 entity 页面: coq10-overview, coq10-cardiovascular, coq10-neuro, coq10-statin-myopathy, coq10-bioavailability
- 创建 1 个 source 页面: github-relay-neuron-supplements
- 更新 wiki/index.md

**核心概念**:
- 姜黄素: NF-κB/Nrf2/AMPK/PI3K多靶点; 糖尿病GSK-3β↓/IAPP↓(RCT n=272); MAFLD ALT↓5.6/AST↓3.9 IU/L(荟萃); 纳米递送是生物利用度瓶颈
- 辅酶Q10: 线粒体电子传递链核心组分; 心衰Q-SYMBIO死亡率↓(强RCT); 他汀肌病绕过甲羟戊酸通路; 泛醇vs泛醌，老人/患者选泛醇
## [2026-05-20] ingest | notes/datastructure + design_patterns + interview

**来源**: raw/github/notes/datastructure/ (21 .md), raw/github/notes/design_patterns/ (26 .md), raw/github/notes/interview/ (9 .md)

**操作**:
- 创建 7 个 datastructure entity 页面: algorithm-complexity, linear-data-structures, sorting-algorithms, dynamic-programming, recursion-and-divide-conquer, hash-table, trees-and-graphs
- 创建 5 个 design-patterns entity 页面: solid-principles, design-principles-advanced, creational-patterns, structural-patterns, behavioral-patterns
- 创建 3 个 interview entity 页面: interview-preparation, problem-solving-patterns, system-design-basics
- 更新 wiki/index.md

**核心概念**:
- Data Structure: 复杂度分析(O/n/log/n/n²), 线性表(数组/链表/栈/队列), 排序(冒泡/插入/归并/快排), DP(状态转移方程/最优子结构), 递归分治, 哈希表, 树图
- Design Patterns: SOLID五大原则, DIP/SoC进阶原则, 创建型(单例/工厂/建造者/原型), 结构型(适配器/桥接/组合/装饰/门面/享元/代理), 行为型(策略/状态/观察者/命令/模板/责任链)
- Interview: 边学边练方法论, 解题四步法, 系统设计CAP/一致性哈希

**交叉引用**:
- datastructure/algorithm-complexity → datastructure/sorting-algorithms → datastructure/dynamic-programming
- design-patterns/solid-principles → design-patterns/design-principles-advanced → design-patterns/creational-patterns
- interview/problem-solving-patterns → datastructure/* (DP/BFS/DFS模式)

## [2026-05-20] ingest | notes + relay-neuron 批量 (6x Claude Code concurrent)

- virt+io_uring+vfs: 4 entity pages (KVM, Virtio, io_uring, VFS)
- net+netfilter+network: 3 entity + 3 source pages
- ccpp+sys+midware+tools+security: 4 entity pages
- relay-neuron 剩余: 14 entity pages (nutrition, running, biomechanics, training)
- 总计新增 ~30 entity pages
- Wiki 当前 entity pages: 95

## [2026-05-20] ingest | notes/os_fundamentals + network_fundamentals + kernel subsystems

**来源**: raw/github/notes/os_fundamentals/ (39 lectures), raw/github/notes/network_fundamentals/ (21 lectures), raw/github/notes/crypto|locking|ipc|rcu|time|sound/linux_kernel/

**操作**:
- 创建 2 个 synthesis 页面: topic-os-fundamentals, topic-network-fundamentals
- 创建 6 个 kernel entity 页面: crypto-core, locking-core, ipc-core, rcu-core, time-core, sound-core
- 创建 8 个 source 页面: notes/os_fundamentals, notes/network_fundamentals, notes/kernel/{crypto,locking,ipc,rcu,time,sound}
- 更新 wiki/index.md

**Entity 页面**:
- Crypto: crypto_alg注册、skcipher同步加密、aead异步加密、模板机制
- Locking: spinlock忙等待、mutex乐观自旋MCS、rwsem读写分离、percpu、lockdep
- IPC: msg消息队列pipelined_send、sem信号量atomic_op+undo、shm共享内存mmap、mqueue红黑树
- RCU: Read-Copy-Update无锁读取、grace period宽限期、srcu、NOCB
- Time: tick周期中断、NO_HZ Dynamic Tick、hrtimer红黑树纳秒精度、timekeeping、NTP
- Sound: ALSA架构、PCM DMA、ASoC三层架构、DAPM widget power、DAl数字音频接口

**Synthesis 核心概念**:
- OS: 图灵机/计算理论、进程vs线程开销、虚拟内存/页表、epoll红黑树、TCP三次握手四次挥手
- Network: TCP/IP五层模型、滑动窗口、epoll vs select/poll、HTTP缓存、DNS解析

## [2026-05-23] ingest | pdf-cpp-slides (enhance) + pdf-epi-python + cpp-recsys-optimization

Enhanced existing source page `wiki/sources/pdf-cpp-slides.md` with richer detail from actual PDFs:
- David Sankel: sandboxing tools (Sandbox2/SAPI/RLBox/AppSandbox/AppContainer), hardening flags detail, sanitizer specifics
- John Lakos: C++ under pressure (Google/MS/Adobe migrating), Safe-Healthy-Efficient strategy details, contracts 20-year timeline
- 吴晓飞: memory hierarchy latency/bandwidth table, cache miss types, perf/eBPF/IPT tool specifics, hardware benchmarking
- 刘童旋: adaptive PD scheduling, business impact metrics (TP99↓50%, cost↓70%, UCVR↑5%)

Enhanced existing source page `wiki/sources/pdf-cpp-ai-inference.md`:
- 易慧民 RecIS: Four Walls (Python/CPU/Memory/Compute), GPU HashTable design, sparse fusion, 2-3X performance results

Created new source page:
- `wiki/sources/pdf-epi-python.md` — Elements of Programming Interviews in Python sampler (book, not a C++ slide)

Created new entity page:
- `wiki/entities/cpp/cpp-recsys-optimization.md` — C++ for recommendation system training optimization

Updated:
- `wiki/cpp-index.md` — added recsys-optimization row
| `wiki/home.md` — added pdf-epi-python source, updated cpp-index count 18→19, page estimate ~140→~142

## [2026-05-23] lint | 26 issues fixed

- Added missing `tags:` frontmatter to 26 source pages (including pdf-design-patterns-cpp, pdf-concurrency-perf, pdf-linux-sysprog, pdf-linux-kernel-books, pdf-linux-net-server, pdf-ds-cpp, pdf-epi-python, notes-net-deep, pdf-ebpf-papers, pdf-cpp-compiler-toolchain, pdf-cpp-safety-standards, pdf-cpp-perf-engineering, pdf-cpp-engineering-practices, pdf-cpp-slides, pdf-cpp-perf-books, pdf-cpp-ai-inference, pdf-ebpf-books, notes-sys, notes-midware, notes-openbmc, notes-design-patterns, notes-ccpp, notes-interview, notes-security, notes-tools, notes-datastructure)
- Verified orphan module indexes ([[rust-index]] and [[openbmc-index]]) already linked in home.md

---

## [2026-05-25] ingest | Batch N: C++ Slides 剩余25 PDFs

- **来源**: raw/PDFs/slides/ (25个新幻灯片加入原有12个)
- **操作**: 仅汇总 — 不提取文本，不创建 entity
- **更新**: sources/pdf-cpp-slides.md (条目 13-36 → 共37条，按主题分组: AI推理9/编译器5/工程实践6/异构计算3/其他4), wiki/home.md (source描述+index行), log.md
- **主题分组**:
  - AI推理: Mooncake/RTP-LLM/xLLM/DeepSeek/LazyLLM/RecIS/FlagScale/AI成熟度
  - 编译器: MLIR fuzz/AI软件栈/多元AI算子库/RISC-V AI编译器/RISC-V全栈
  - 工程实践: Crash诊断/Qoder CLI/Coding Agent/AI Coding实践/AI测试/具身机器人
  - 异构计算: 异构计算架构/异构传输库/统一智能计算
- **更新后**: pdf-cpp-slides 共37条，[[cpp-slides-index]] 更新为37 talks

---

## [2026-05-25] ingest | Batch K: Linux/Kernel/ARM PDFs (12 books)

- **来源**: raw/PDFs/books/ (12 PDFs: 3 网络/服务器 + 6 内核/系统 + 3 ARM)
- **操作**:
  - PyPDF2 扫描全部 12 册：其中 1 册（APUE 第三版）确认为扫描版，跳过文本提取
  - TLPI (1556页) + CSAPP (1078页) 完全可读，创建详细源页面
  - APUE 第三版（822页）扫描版，基于书籍结构创建源页面
  - 3 个 entity 页面: virtual-memory-systems, process-management-model, machine-code-programmers-perspective
  - 1 个 kernel-books-index.md 模块索引
  - 更新 pdf-linux-kernel-books.md（追加 Batch K 注记）
- **更新**: home.md (kernel-books-index + 3 新源页面 + 更新计数 359→367/25 indexes), index.md, log.md
- **核心概念**: TLPI 500+系统调用百科、CS:APP 计算机系统视角（机器码/缓存/虚拟内存/链接/并发）、APUE POSIX 标准编程、虚拟内存系统、进程管理模型、x86-64 机器码
- **扫描跳过**: UNIX环境高级编程(第三版).pdf — Adobe Acrobat Image Conversion Plug-in 生成，无可提取文本
