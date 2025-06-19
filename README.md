# 📚 Technical Notes Repository

本仓库包含了操作系统、网络、系统编程、编程语言等技术领域的学习笔记和资料。

## 📁 目录结构

### 🖥️ Programming (编程)
- **Programming** - 编程相关
  - [C Programming](programming/c/c.md) - C语言基础
  - [C++ Programming](programming/cpp/cpp.md) - C++语言特性
  - [Object Creation](programming/cpp/object_creation_heap_or_stack.md) - 内存管理
  - [Bit Operations](programming/common_bit_operations.md) - 位运算技巧
  - [Compilation Process](programming/compilation_process.md) - 编译过程
  - [Serialization](programming/serialization.md) - 序列化技术

### ⚙️ Systems (系统)
- **Operating Systems** - 操作系统
  - **Linux**
    - [Kernel Development](os/Linux/kernel/linux_kernel_compile_debug.md) - 内核开发调试
    - [Driver Basics](os/Linux/drivers/linux_driver_basics.md) - 驱动开发基础
    - [VirtIO Network](os/Linux/drivers/virtio_network.md) - VirtIO网络驱动
    - [eBPF Basics](os/Linux/ebpf/basic.md) - eBPF技术入门

- **System Programming** - 系统编程
  - [Linux System Programming](systems/system_programming/linux_system_programming.md) - Linux系统编程
  - [ELF Format](systems/system_programming/elf.md) - ELF文件格式
  - [Computer Architecture](systems/computer_architecture_intro.md) - 计算机体系结构
  - [IPC](systems/ipc/linux_ipc.md) - 进程间通信

- **Networking** - 网络技术
  - [OSI/PHY/MAC](systems/networking/osi_phy_mac.md) - 网络协议栈
  - [PHY/MAC Layers](systems/networking/phy_mac.md) - 物理层和MAC层
  - [Linux Network Devices](systems/networking/linux_network_devices_ascii_flow.md) - Linux网络设备
  - **TCP/IP**
    - [TCP Protocol](systems/networking/tcpip/tcp.md) - TCP协议
    - [TCP Overview](systems/networking/tcpip/tcp_overview.md) - TCP概述
    - [IP Protocol](systems/networking/tcpip/ip.md) - IP协议
    - [BBR Algorithm](systems/networking/tcpip/bbr.md) - BBR拥塞控制
    - [DoIP](systems/networking/tcpip/doip.md) - DoIP协议
    - **SOME/IP**
      - [Overview](systems/networking/tcpip/someip/someip_overview.md) - SOME/IP概述
      - [vSOMEIP](systems/networking/tcpip/someip/someip_00_vsomeip.md) - vSOMEIP介绍
      - [Implementation](systems/networking/tcpip/someip/vsomeip.md) - vSOMEIP实现
      - [Source Reading](systems/networking/tcpip/someip/vsomeip_source_reading.md) - 源码阅读
      - [Source Analysis](systems/networking/tcpip/someip/someip_source_analysis.md) - 源码分析
      - [Configuration](systems/networking/tcpip/someip/someip_configuration.md) - 配置说明
      - [Service Discovery](systems/networking/tcpip/someip/service_discovery.md) - 服务发现
      - [Security](systems/networking/tcpip/someip/vsomeip_security.md) - 安全机制
      - [Adaptive Platform](systems/networking/tcpip/someip/someip_ap.md) - 自适应平台

- **Security & Cryptography** - 安全与密码学
  - [Crypto Algorithms](systems/cryptography/) - 密码学算法

### 📖 Courses (课程)

> **学习声明**：本节所有课程内容均来源于网络公开教育资源，仅供个人学习研究使用，不用于任何商业用途。如有侵权，请联系删除。所有版权归原作者和出版方所有。
- **Data Structures & Algorithms** - 数据结构与算法
  - [开篇词](courses/datastructure/开篇词_数据结构与算法_应该这样学.md)
  - [01 复杂度](courses/datastructure/01_复杂度_如何衡量程序运行的效率.md)
  - [02 数据结构](courses/datastructure/02_数据结构_将昂贵的时间复杂度转换成廉价的空间复杂度.md)
  - [03 增删查](courses/datastructure/03_增删查_掌握数据处理的基本操作_以不变应万变.md)
  - [04 线性表](courses/datastructure/04_如何完成线性表结构下的增删查.md)
  - [05 栈](courses/datastructure/05_栈_后进先出的线性表_如何实现增删查.md)
  - [06 队列](courses/datastructure/06_队列_先进先出的线性表_如何实现增删查.md)
  - [07 数组](courses/datastructure/07_数组_如何实现基于索引的查找.md)
  - [08 字符串](courses/datastructure/08_字符串_如何正确回答面试中高频考察的字符串匹配算法.md)
  - [09 树和二叉树](courses/datastructure/09_树和二叉树_分支关系与层次结构下_如何有效实现增删查.md)
  - [10 哈希表](courses/datastructure/10_哈希表_如何利用好高效率查找的"利器".md)
  - [11 递归](courses/datastructure/11_递归_如何利用递归求解汉诺塔问题.md)
  - [12 分治](courses/datastructure/12_分治_如何利用分治法完成数据查找.md)
  - [13 排序](courses/datastructure/13_排序_经典排序算法原理解析与优劣对比.md)
  - [14 动态规划](courses/datastructure/14_动态规划_如何通过最优子结构_完成复杂问题求解.md)
  - [15 复杂度分析](courses/datastructure/15_定位问题才能更好地解决问题_开发前的复杂度分析与技术选型.md)
  - [Memory Management](courses/datastructure/memory.md)
  - [Array & LinkedList](courses/datastructure/array_linkedlist.md)
  - [练习题详解](courses/datastructure/加餐_课后练习题详解.md)

- **Operating Systems Fundamentals** - 操作系统基础
  - [01 计算机是什么](courses/os_fundamentals/01_计算机是什么.md)
  - [02 程序执行(上)](courses/os_fundamentals/02_程序的执行_相比_32_位_64_位的优势是什么(上).md)
  - [03 程序执行(下)](courses/os_fundamentals/03_程序的执行_相比_32_位_64_位的优势是什么(下).md)
  - [04 构造复杂程序](courses/os_fundamentals/04_构造复杂的程序_将一个递归函数转成非递归函数的通用方法.md)
  - [05 存储器分级](courses/os_fundamentals/05_存储器分级_L1_Cache_比内存和_SSD_快多少倍.md)
  - [39 Linux架构](courses/os_fundamentals/39_Linux_架构优秀在哪里.md)

- **Network Fundamentals** - 网络基础
  - [01 移动网络](courses/network_fundamentals/01_漫游互联网_什么是蜂窝移动网络.md)
  - [02 TCP协议](courses/network_fundamentals/02_传输层协议_TCP_TCP_为什么握手是_3_次_挥手是_4_次.md)
  - [03 TCP封包](courses/network_fundamentals/03_TCP_的封包格式_TCP_为什么要粘包和拆包.md)
  - [04 TCP稳定性](courses/network_fundamentals/04_TCP_的稳定性_滑动窗口和流速控制是怎么回事.md)
  - [05 UDP协议](courses/network_fundamentals/05_UDP_协议_TCP_协议和_UDP_协议的优势和劣势.md)

### 🛠️ Tools (工具)
- [Netcat](tools/netcat.md) - 网络工具
- [Vim Config](tools/vim_config.rc) - Vim配置
- [Manjaro Swap](tools/manjaro_swap.md) - Manjaro交换分区
- [Remove Snap](tools/remove_snap.md) - 移除Snap

### 📦 Resources (资源)
- [Images](resources/imgs/) - 图片资源
  - 技术图解、架构图
  - 课程配图
- [Documents](resources/docs/) - 文档资源
  - [Networking PDFs](resources/docs/networking/) - 网络技术PDF
  - [SOME/IP PDFs](resources/docs/someip/) - SOME/IP相关PDF
  - [Rust PDFs](resources/docs/rust/) - Rust学习资料

## 🚀 重构说明

本仓库已完成目录结构重构，主要改进：

1. **清晰分类**：按照编程、系统、课程、工具的逻辑进行分类
2. **层次化组织**：相关内容集中管理，便于查找
3. **统一命名**：采用一致的目录和文件命名规范
4. **资源整合**：图片等资源文件统一管理
5. **链接导航**：所有文档都可以直接点击访问

## 📚 主要内容

- **Linux系统编程**：从基础系统调用到内核机制的深入分析
- **网络技术**：TCP/IP、SOME/IP等协议的详细解读
- **C/C++编程**：现代C++特性、STL使用、内存管理
- **操作系统理论**：完整的OS课程体系
- **嵌入式开发**：QNX、汽车电子等领域的技术资料

---

