# DPDK

## DPDK简介

Intel DPDK全称Intel Data Plane Development Kit，是Intel提供的数据平面开发工具集，为Intel architecture（IA）处理器架构下用户空间高效的数据包处理提供库函数和驱动的支持，它不同于Linux系统以通用性设计为目的，而是专注于网络应用中数据包的高性能处理。DPDK应用程序运行在用户空间，利用自身提供的数据平面库来收发数据包，绕过了Linux内核协议栈对数据包处理过程。

## 基本组件

- **EAL（Environment Abstraction Layer）** - 环境抽象层，为应用提供通用接口，隐藏底层库与设备交互细节，实现DPDK运行初始化、大页表内存分配、多核亲缘性设置、原子和锁操作、PCI设备地址映射到用户空间
- **Buffer Manager API** - 通过预先分配固定大小的内存对象，避免动态内存分配和回收，提高效率
- **Queue Manager API** - 实现无锁FIFO环形队列，支持单生产者多消费者、单消费者多生产者模型，支持批量无锁操作
- **Flow Classification API** - 基于Intel SSE实现高效hash算法，用于数据包分类处理
- **PMD** - 实现Intel 1GbE、10GbE和40GbE网卡基于轮询收发包工作模式

## DPDK核心思想

1. **PMD (Poll Mode Drivers)** - DPDK针对Intel网卡实现基于轮询方式的PMD驱动，使用无中断方式直接操作网卡收发队列，通过DMA方式传输数据包到预分配内存

2. **hugetlbfs** - 使用大页表有两个好处：减少页表项开销、降低TLB miss开销。DPDK支持2M和1G两种hugepage，可提高性能10%~15%

3. **CPU亲缘性** - 多核CPU架构，每个核一个线程，核心间访问数据无需上锁，需考虑NUMA架构避免访问远端内存

4. **减少内存访问** - 少用数组和指针，多用局部变量；少用全局变量；一次多访问数据；自己管理内存分配；进程间传递指针而非整个数据块

5. **Cache有效性** - 得益于空间局部性和时间局部性原理，合理使用cache可大幅提升性能

6. **避免False Sharing** - 多核CPU中当两个线程访问同一cache line数据时会产生冲突，导致cache line无效。应多使用线程本地变量

7. **内存对齐** - 根据存储硬件配置优化程序，确保对象位于不同channel和rank的起始地址以便并行加载

8. **NUMA** - NUMA系统节点由CPU和本地内存组成，NUMA调度器负责将进程在同一节点CPU间调度

9. **减少进程上下文切换** - 可控场景包括：休眠当前进程、唤醒其它进程、加锁函数等；不可控场景需保证活跃进程数目不超过CPU个数

10. **分支预测机制** - 错误分支预测会导致流水线回退，产生10%~30%性能影响

11. **利用流水线并发** - Pentium处理器有U/V两条流水线，可将指令安排在不同流水线执行

12. **预取Prefetch** - 在数据被用到之前将其调入缓存，使数据加载与CPU执行指令并行进行

## 架构

在内核态(Linux Kernel) DPDK有两个模块：
- **KNI** - 提供使用Linux内核态协议栈及传统Linux网络工具
- **IGB_UIO** - 借助UIO技术，将网卡硬件寄存器映射到用户态

用户态包括：
- 核心部件库(Core Libraries)
- 平台相关模块(Platform)
- 网卡轮询模式驱动模块(PMD-Natives & Virtual)
- QoS库
- 报文转发分类算法(Classify)

## 应用

- SPDK (http://www.spdk.io/)
- OPNFV (https://wiki.opnfv.org/)
- Open vSwitch for NFV
- Data Plane Acceleration (DPACC)
- OVS-DPDK
- VPP (http://fd.io) 和 TLDK
- Seastar (http://www.seastar-project.org/)
- F-Stack (http://www.f-stack.org/) - 结合DPDK、FreeBSD协议栈、POSIX API，支持coroutine

## 图片

![dpdk_lib图](https://cloud.githubusercontent.com/assets/676637/14767274/70bb59c8-0a54-11e6-862d-2f19c721c45d.png)
![DPDK架构图](https://cloud.githubusercontent.com/assets/676637/14767276/7dfb9ed8-0a54-11e6-914f-b041ddcdd40d.png)
![DPDK应用图](images/14893934528742.jpg)

## 参考文档

- 《深入浅出DPDK》
- http://dpdk.org
- http://intel.com/go/dpdk
- https://fd.io
- https://github.com/lagopus/lagopus
- Data Plane Performance Demonstrators (DPPD)
