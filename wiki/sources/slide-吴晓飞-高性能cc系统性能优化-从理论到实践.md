---
type: source
source-type: slide
title: "吴晓飞_高性能CC++系统性能优化 从理论到实践"
path: slides/吴晓飞_高性能CC++系统性能优化 从理论到实践.pdf
size: 6395 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 吴晓飞_高性能CC++系统性能优化 从理论到实践

> Ingested from `slides/吴晓飞_高性能CC++系统性能优化 从理论到实践.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.25 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

高性能C/C++系统性能优化：从理论到实践

 ——PolarDB TPCC登顶性能优化



    阿里云RDS MySQL内核负责人
    吴晓飞

## Page 7

目 录 CONTENTS

    1.  性能优化的理论支持

    2.  性能分析的工具支持

    3.  性能优化实战——以PolarDB TPCC为例

## Page 8

_(no text content on this page)_

## Page 9

性能优化的理论支持

1.学会“抓重点”—— Amdahl定律（Amdahl‘s Law）

系统整体加速受限于不可并行部分的比例  1
       S =     1 −   +
其中 是可并行部分比例， 是并行资源数量。

   a、提升可并行区并行度及并行效率，将资源尽可能充分利用
   b、降低串行区比例，减少系统瓶颈区

## Page 10

性能优化的理论支持

1.学会“抓重点”—— 90/10 法则


 程序 90% 的时间可能花在 10% 的代码上。


 a、应当执行“测量先行，再优化”策略，避免过早优化
 b、优化应当着眼于“热点（hot）”路径

## Page 11

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Memory Hierarchy

CPU —— 缓存 —— 内存 —— （磁盘/网络）
“越靠近 CPU 的存储越快、越小、越贵；越远离 CPU 的存储越慢、越大、越便宜”


层级                 典型延迟（Latency）           带宽（Bandwidth）         容量                  对程序优化的影响

寄存器（Registers）     ~0 cycles               极高                    几十~几百字节             编译器自动优化，尽量让
                                                                                     热点变量驻留寄存器

L1 Cache           ~1–4 ns（≈1–4 cycles     ~150 GB/s             64-512 KB/core      数据局部性、对齐、避免
                   @3GHz）                                                            false sharing

L2 Cache           ~10 ns                  ~50–100 GB/s          256 KB–16 MB/core   预取、循环展开、减少跨
                                                                                     cache line 访问

L3 Cache（共享）       ~20–50 ns               ~40–80 GB/s           8–512 MB（多核共享）      多线程数据布局避免争用

主存（DRAM）           ~60–120 ns              ~20–60 GB/s（DDR4/5）   GB 级                避免频繁分配/释放、使用
                                                                                     内存池
SSD（NVMe）          ~10–100 μs              ~1–8 GB/s             TB 级                I/O 是瓶颈时，需异步、
                                                                                     多线程、批量、提升缓存

## Page 12

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Memory Hierarchy

CPU —— 缓存 —— 内存 —— （磁盘/网络）


    每个核心有有限寄存器（如 x86-64 有 16 个通用寄存器）。
    指令流水线（Pipeline）、超标量（Superscalar）、乱序执行（OoO）提升吞吐。
•   批量指令向量化（SIMD）执行

    小循环、简单计算更容易被完全寄存器化。
•   避免过多局部变量或复杂控制流阻碍寄存器分配。
•   大部分依赖编译器、优化器进行底层优化（Compiler、LTO、PGO）

## Page 13

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Memory Hierarchy

CPU —— 缓存 —— 内存 —— （磁盘/网络）

•   缓存行（Cache Line）：常 64 字节，一次加载整 cache line。
•   缓存未命中（Miss）类型：
   Cold Miss（首次访问）
   Capacity Miss（容量不足）
   Conflict Miss（映射冲突）
•   写策略：
   Write-Through vs Write-Back（常见）。
•   伪共享（False Sharing）：
   不同线程修改同一 cache line 中不同变量 → 频繁无效化 → 性能下降。

•   多线程性能优化的核心战场，提升局部性、降低冲突性、结构体优化等等。

## Page 14

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Memory Hierarchy

CPU —— 缓存 —— 内存 —— （磁盘/网络）

    DRAM 访问非均匀（NUMA 架构下，远程内存更慢）。
    内存带宽有限，带宽瓶颈常出现在大数据拷贝场景。
•   有效带宽受访问模式影响（顺序 > 随机）

    避免不必要的内存拷贝（使用 move 语义、span/view）。
    使用内存池（Memory Pool）减少 new/delete 开销和碎片。
    NUMA 感知分配（如 numactl 或 libnuma）。
•   内存通道交错并联，提升吞吐利用率。

## Page 15

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Memory Hierarchy

CPU —— 缓存 —— 内存 —— （磁盘/网络）

• 延迟 vs 吞吐：
  磁盘/网络以延迟为主导（尤其是小I/O）。
  SSD 随机读写远优于 HDD，但仍比内存慢数百倍以上。
  大规模 raid 阵列下吞吐极限高，单不易实现

• IO 的充分利用和异步化
  使用异步逻辑，避免在热路径中进行请求。
  批量多线程处理、考虑压缩、缓存中间结果等。

## Page 16

性能优化的理论支持

2.清楚硬件的底层逻辑 —— Benchmarking

 做在前面：环境基准测试（Benchmarking）

 对 CPU / 内存 / 磁盘进行测试，了解硬件特性和能力极限；
 在硬件选型时就开始性能分析，测试结果指导选型流程。

## Page 17

_(no text content on this page)_

## Page 18

性能分析的工具支持

1.硬件测试工具

CPU 基准测试工具： Google Benchmark、 perf (Linux) 、sysbench --cpu


Memory 基准测试工具： Intel Memory Latency Checker (MLC)、 perf + custom code


SSD/存储基准测试工具： fio (Flexible I/O Tester)、 blktrace + btt

*其他：写一些更贴近业务特性的压测程序

## Page 19

性能分析的工具支持

2.1 C++程序分析工具       perf

利用性能计数器来提供硬件事件（如 CPU 周期、指令、缓存命中等）和软件事件（如上下文切换、页面错
误等）等的详细视图。

Hardware    Hardware cache                    Software             Kernel PMU        Tracepoint
cpu-cycles      L1-dcache-load-misses         context-switches     context-switches  内核插桩
instructions    L1-icache-load-misses         cpu-clock            cpu-clock
branch-misses   L1-dcache-loads / stores      task-clock           task-clock
cache-misses    branch-loads[-misses]         minor/major-faults   minor/major-faults
                dTLB-loads[-misses]           page-faults          page-faults
                dTLB-stores[-misses]          cpu-migrations
                iTLB-load-misses
Command
            stat: event counting
            record: profiling / static tracing
            reoprt: reporting
            top: profiling

## Page 20

性能分析的工具支持

2.2 C++程序分析工具 eBPF (bcc、bpftrace)
BPF（Berkeley Packet Filter）一种运行内核层的网络数据包过滤和捕获机制；
eBPF 扩展了传统BPF的功能，可基于程序事件在内核直接高效安全执行特定代码的能力 。

                            o kprobes：内核中动态跟踪。内核维护，理论上可动态跟踪到所有符号在 /proc/kallsyms 但
                            不在 /sys/kernel/debug/kprobes/blacklist 的
                            o uprobes：用户级别的动态跟踪。
                            o tracepoints：内核中静态跟踪。开发人员维护的跟踪点，能够提供稳定的 ABI 接口，但是
                            需维护，数量和场景受限。（用户静态探针 USDT ）
                            o perf_events：定时采样和PMC。
                              struct bpf_insn {  code;             /* opcode */
                              __u8               dst_reg:4;        /* dest register */
                              __s16              src_reg:4;        /* source register */
                              __s32              off;              /* signed offset */
                              msb                imm;              /* signed immediate constant */};
                              +---------------------+---------------+----+----+-------+|
字节码编译- 验证、加载 – 运行、写入缓冲 -                                           lsb
用户读取缓冲 、分析                    immediate                 |offset    |src |dst |opcode |
                              +---------------------+---------------+----+----+-------+|

                              支持从通用内存（map、栈、数据包缓冲区上下文）进行 1-8 字节的加载/存储；
                              前/后（非）条件跳转；算术/逻辑操作；函数调用等

## Page 21

性能分析的工具支持

2.2 C++程序分析工具     eBPF (bcc、bpftrace)

K/Uprobe：                             Tracepoint：
1）替换目标指令为断点指令BREAKPOINT               1）内核编译时，通过DECLARE_TRACE，在tracepoint位
2）断点异常                                置处留一个5Bytes的nop指令（x86），后续可静态替换
3）中断处理（检查kprobe注册表，调用pre_handler）     为jump
4）设置单步模式执行原有指令                        2）函数尾加上tracepoint handler (trampoline)，运
                                      行时用于扫描tracepoint handler数组看是否有注册的
5）完成后单步异常                             3）runtime当使能这个tracepoint时 ，增加注册函数，
6）调用post_handler                      4）nop会被替换为jump，跳到trampoline，运行注册函
7）正常运行                                数
（Linux text_poke机制）                   （Linux Jump Label/static-key、 text_poke机制 ）

Kretprobe （入口Kprobe+返回跳转Kprobe ）
数百ns～千ns 时序操作                         数十ns～数百ns 时序操作

## Page 22

    性能分析的工具支持

    2.2 C++程序分析工具 eBPF (bcc、bpftrace)
    eBPF 程序的高层次组件（bcc、bpftrace）
    BCC：
    后端和数据结构：用 “限制性 C” 编写。可以在单独的文件中，或直接作为多行字符串存储在加载器/前端的脚本中；
    加载器和前端：可用简单的高级语言 python/lua 脚本编写。










Bpftrace：
建立在 BCC 之上，可以作为在寻找 BCC 的全部功能之前的快速分析/调试使用
bpftrace -e 'tracepoint:raw_syscalls:sys_enter {@[pid, comm] = count();}'

## Page 23

性能分析的工具支持

2.2 C++程序分析工具 eBPF (bcc、bpftrace)    $ sudo python wakeup_latency.py -p 36780 -d 1 -u
                                     [ Attaching probes to pid 36780 for 5 seconds ]
                                     [ 4 wakeup point are set ]
                                     ===================================
                                     Graph of wakeup latency:
                                        [ wait_start ]
                                        | 298 usecs
                                        V
                                        [ wakeup 1 ]
                                        | 44 usecs
                                        V
                                        [ wakeup 2 ]
                                        | 948 usecs
                                        V
                                        [ wakeup 3 ]
                                        | 451 usecs
                                        V
                                        [ wakeup 4 ]
                                        | 1131 usecs
                                        V
                                        [ wait end ]
                                     average wait latency: 2656 usecs, cnt: 1453
                                     ...

一些MySQL BPF分析工具 https://github.com/mysqlperformance/bpf_tools.git

## Page 24

性能分析的工具支持

2.3 C++程序分析工具 PolarDB Fast Stack

 对于实际线上环境中，会经常使用 "pstack+进程ID" 的方式来输出进程当前各个线程的执行堆栈来
 查看：
 1）热点和长时间的函数调用；
 2）死锁检测；
 3）阻塞函数的检测。

 但 pstack 在运行过程会长时间中断运行程序，在中断期间，程序无法响应用户请求。阻塞时长与
 打印的函数堆栈数和并发数成正比。

## Page 25

性能分析的工具支持

2.3 C++程序分析工具 PolarDB Fast Stack

                                我们在PolarDB内部设计了stack print能力，
                                其整体由三部分组成:
                                1) monitor 核心监控与处理线程；
                                2) Thread set 集合，存储当前向 monitor 注册的
                                线程 tid， 包括 server 层的 worker 线程和
                                innodb 层的后台线程；
                                3) LRU cache 缓存，存储函数地址对应的 stack
                                info （函数信息），为了减少重复解析

## Page 26

性能分析的工具支持

2.3 C++程序分析工具 PolarDB Fast Stack

使用 sysbench 的 benchmark 进行模拟用户连接，当连接数为1000时，返回结果
时长为 pstack 的 1/131。

Sysbench 使用的是 read_write workload，其他也是类似的，我们可以发现
Polar Stack 不会完全停止线上处理，中断时间中只影响了当时约为 14% 的QPS，
与 pstack 的跌 0 相比优势明显。


pstack



polar stack

## Page 27

性能分析的工具支持

2.4 C++程序分析工具 Intel Processor Trace

Intel Processor Trace（IPT）是英特尔处理器中引入硬件级指令追踪技术，它通过硬件高效记录控
制流变化（如分支、中断、异常等），为调试、性能分析、安全监控等场景提供深度支持。

    Change of Flow Instruction (COFI) Tracing










满足亚ns 级别时序操作

## Page 28

性能分析的工具支持

2.4 C++程序分析工具 Intel Processor Trace

   Packet Stream Boundary (PSB) packets：周期性插入的同步包，用于数据流分割和错误恢复，提供解码起始点；
   Time-Stamp Counter (TSC) packets： 记录 wall-clock time，各个core独立，特定事件触发比如 PSB；
   Mini Time Counter (MTC) packets：周期的提供粗粒度的 wall-clock time，较为高频；
   （TMA = TSC/MTC Alignment packets：可以对齐 TSC 和 MTC）
   Cycle Count (CYC) packets： 记录 processor core 经过的 clock cycles，在周期精确模式下提供；
   Core Bus Ratio (CBR) packets：记录 core/bus 的比例，可以把 core 周期转换为时钟芯片周期；

   Taken Not-Taken (TNT) packets: 记录 direct conditional branches 的选择方向；
   Target IP (TIP) packets：记录 indirect branches, interrupts 的目标 IP 方向；
   Flow Update Packets (FUP):在异常、中断或特定事件后记录源 IP 地址；

   PTWRITE (PTW) packets: 软件指令写入包内容

## Page 29

性能分析的工具支持

2.4 C++程序分析工具                Intel Processor Trace

Intel PT 的高层使用工具             https://man7.org/linux/man-pages/man1/perf-intel-pt.1.html
PERF-INTEL-PT：
perf record -e intel_pt//        perf {report | script} --itrace=

record 配置： intel_pt/配置1/配置2      配置other
配置1     tsc mtc+mtc_period    cyc     noretcomp（TIP when return）  branch
psb_period /sys/bus/event_source/devices/intel_pt/caps/psb_periods
配置2     u userspace k kernel
--kcore 或 echo 'kernel.kptr_restrict=0' >> /etc/sysctl.conf
-m,16M           { 提前配置perf事件锁定在RAM中的内存量 echo $[32*1024] > /proc/sys/kernel/perf_event_mlock_kb }
-S snapshot模式，无回环
--aux-sample -e branch-misses:u     采样模式
--filter 'filter func @ /path/my_proc'

decode 配置： --itrace=配置（默认--itrace=cepwxy）

## Page 30

性能分析的工具支持

2.4 C++程序分析工具    Intel Processor Trace

Intel PT 的高层使用工具 并行perf script：
    https://github.com/mysqlperformance/pt_perf/blob/main/README_CN.md

perf 以 event 形式从硬件目标 buffer 采集（copy）的 raw PT packages ，并且封装成 AUXTRACE_INFO（含有所有auxtrace 数据的索引）、
AUXTRACE（含有 PT packages）、AUX （匹配AUXTRACE含有状态信息）三种 perf reocrd 包。
依赖 PSB packets，decoder 可以开始 PT Stream packages 解析的（decoder 第一个包定位）。










* perf 在解析事件时可能会需要更前面的上下文信息，导致数据不够完整。
常见是推导调用栈信息时可能会出现调用栈丢失栈底的情况

## Page 31

性能分析的工具支持

2.4 C++程序分析工具     Intel Processor Trace

       Intel PT 的高层使用工具 并行perf scripth：ttps://github.com/mysqlperformance/pt_perf/blob/main/README_CN.md

                                                                                          ======================================================================
ptfold_stack（函数/stack 分布统计）                                                               Histogram - Latency of [xxxxxx]:
                                                                                    ns                                : cnt          distribution
pt_flame (火焰图生成)                                                                128 -> 255                            : 1         |                          |
                                                                                256 -> 511                            : 91443     |********************|
                                                                                512 -> 1023                           : 66795       |**************          |
pt_func_perf（整合，单函数）                                                           1024 -> 2047                           : 14746     |***                       |
                                                                               2048 -> 4095                           : 10695     |**                        |
                                                                               4096 -> 8191                           : 1310      |                          |
                                                                               8192 -> 16383                          : 1147      |                          |
./func_latency -b "mysqld" -f "do_command" -d 1 -T tid1,tid2 -t -s [-i -o]    16384 -> 32767                          : 215       |                          |
./func_latency -b "mysqld" -f "do_command" -d 1 -p pid -t -s [-i -o]          32768 -> 65535                          : 36        |                          |
                                                                                          trace count: 186388, average latency: 869 ns
-i       需要510以上内核，开启ip_filter功能                                                          -------------------------------------------------------------------------------------
-o       查看函数执行时 oncpu 和 offcpu 时延比例                                                      Histogram - Child functions's Latency of [xxxxxx]:
                                                                                          name                                             : avg      cnt        distribution (total)
-t       perf 使用 per_thread模式                                                             std::_Hashtable<     : 2383            2778     |*                     |
-s       使用并发script                                                                       xxxxxx               : 262                181    |                     |
                                                                                          xxxxxx                                           : 184      397439     |********************|
. /func_latency -b "mysqld" -f "do_command" -d 5 -T tid -t -s --history=1                 xxxxxx                                           : 139      46866      |*        |
./func_latency -b "mysqld" -f "do_command" -d 1 -T tid -t -s [-o] --history=2             xxxxxx                                           : 120      46865      |*        |
                                                                                          xxxxxx                                           : 64       2022       |         |
--history=1 采集perf.data; --history=2使用perf.data                                           xxxxxx                                           : 30    1356404 |***********    |
                                                                                          xxxxxx                                           : 10       372775     |*        |
. /func_latency -b "mysqld" -f "trx_commit" -d 5 -T tid -t -s -l [--tu=100] --history=2   xxxxxx                                           : 4        186387     |         |
-l       函数时延的时间线timeline功能                                                               xxxxxx                                           : 2        181        |         |
--tu     每多少次取latency平均，默认是1                                                              xxxxxx                                           : 2        31374      |         |
                                                                                          xxxxxx                                           : 2        46866      |         |
                                                                                          xxxxxx               : 2               864588    |                     |
./func_latency --flamegraph="latency" -d 1 -p pid -t –s #latency火焰图                       xxxxxx                                           : 2        583827     |         |
                                                                                          xxxxxx                                           : 1        678202     |         |
./func_latency --flamegraph="CPU" -d 1 -p pid -t –s #cpu火焰图                               xxxxxx               : 1               186388          |                    |
                                                                                          ======================================================================
                                                                                                  pt_func_perf 函数效果效果展示
                                                                                                                                    (函数名脱敏为xxxxxx)

## Page 32

    性能分析的工具支持

    2.4 C++程序分析工具    Intel Processor Trace

    Intel PT 的高层使用工具 并行perf scripth：ttps://github.com/mysqlperformance/pt_perf/blob/main/README_CN.md

小幅度（5-15%）性能回退诊断

## Page 33

_(no text content on this page)_

## Page 34

性能优化实战——PolarDB-TPCC为例

 TPC-C 是由 TPC 组织发布的专门针对 OLTP系统 的规范。几乎所有在 OLTP 市场提供
 软硬平台的国外主流厂商都发布了相应的 TPC-C 测试结果。
 包括了 9 张相互关联的表，和 5 种包含复杂逻辑的事务，包含 ACID 的基本测试。
 从2025年1月至今，集群性能的最优成绩由阿里云保持，平均每个节点87.8w tpmc。

## Page 35

    性能优化实战——PolarDB-TPCC为例






                                                    Machine

    client     http 请求        存储过程          存储过程     Master 1      Standby
                          WebServer     Proxy        Master        Standby
    client                                          Machine      半同步物理复制

                                                     Master        Standby 1
    client
                                                     Master        Standby
                          WebServer     Proxy

                                                    Machine
client 模拟海量用户      WebServe 集群      路由代理                  Coord
     连接                                              C ord

                                                         PolarDB 集群

## Page 36

性能优化实战——PolarDB-TPCC为例

## Page 37

   性能优化实战——PolarDB-TPCC为例

   提升关键路径CPU效率

   • 后台CPU占用优化
   后台线程优先级适应。
   后台线程数量诊定，减少 CPU 调度开销。
   后台线程解耦合，减少后台线程 mutex spin 数量。
   升级AIO模块，提升吞吐能力。


     整体优化后
后台 CPU 占比减少 5%
  吞吐能力提升 40%

## Page 38

性能优化实战——PolarDB-TPCC为例

    Procedure
提升关键路径CPU效率        Procedure    对每条指令
• 前台执行效率优化      对每条指令        Has tables?  no
    Allocate 所有访问的 TABLE      DDL 或断开连接使得缓
乐观开表方式，减少每次重新构        存失效        yes
建和销毁 TABLE 操作以及重复        哈希表缓存
加放锁开销；TPCC 表数目较多、
线程数目多时收益非常明显。      给所有 TABLE 加 MDL 锁
    哈希表无缓存
对 p r o c e d u r e 中 非  S Q L
statement 的空 open table 操作        Allocate TABLE
进行延迟开表。        遍历并关闭所有 TABLE


给 TABLE 加 MDL 锁

优化前（悲观）    优化后 （乐观）

## Page 39

性能优化实战——PolarDB-TPCC为例

提升关键路径CPU效率

• 存储引擎调用路径预编译
bypass 大量 SQL parse 开销，预
先编译 procedure，生成对存储
引擎的直接调用，更轻量的维护
procedure 的中间结果，避免大
量 runtime context 的构建释放，
避免重复加锁。

## Page 40

性能优化实战——PolarDB-TPCC为例

索引数据结构优化        消除Index互斥锁
       消除Parent互斥锁

• PolarIndex
消除SMO并发锁冲突， 使索    B
       l
       o
       b     B
       l
       o
       b     B
       l
       o
引结构上可以 SMO 并发。        SMO Stage 1 b

       消除Index互斥锁







   B
   l
   o
   b B
     l
     o
     b B
       l
       o
   消B除Children互斥锁  b
     SMO Stage 2

## Page 41

性能优化实战——PolarDB-TPCC为例

二进制编译优化

•   PGO (Profile Guided Optimization)
•   BOLT (Binary Optimization and Layout Tool)

## Page 42

性能优化实战——PolarDB-TPCC为例

复制性能-传输优化


•   Batch化redo进行         parse,使得 Log
    apply worker 在应用 page 时并行起来。
•   优化 purge snapshot 等应用分割点，
    避免 redo batch 被切分。
•   提 高 关 键 p a r s e 线 程 优 先 级 、 增 加
    coordinator spin状态，快速响应。

## Page 43

性能优化实战——PolarDB-TPCC为例

复制性能-解析优化

• Ahead Parse
Apply 过程中， parse 线程可以提前
parse 下一个 batch 的 redo Log。使
流程 Pipeline 化。

• 多线程并行 Parse
全并行解析、 应用， 解决大 b a t c h
redo 的单点解析瓶颈。

## Page 44

Thank You

## Related pages

- [[linux-ebpf-fundamentals]]

## Source

- Local path: `[[slides/吴晓飞_高性能CC++系统性能优化 从理论到实践.pdf]]`
