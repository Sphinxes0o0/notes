---
type: index
tags: [dashboard, tech]
created: 2026-05-21
---

# 💻 技术

> Linux 内核、虚拟化、C++、数据结构、设计模式知识网络

## 内容地图

### Linux 内核
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator|SLUB 分配器]]
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault|缺页中断]]
- [[entities/linux/kernel/mm/linux-kernel-mm-swap|Swap]]
- [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim|页面回收]]
- [[entities/linux/kernel/mm/linux-kernel-mm-mmap|mmap]]
- [[entities/linux/kernel/sched/linux-kernel-sched-core|调度核心]]
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs|CFS]]
- [[entities/linux/kernel/sched/linux-kernel-sched-load-balance|负载均衡]]
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch|上下文切换]]
- [[entities/linux/kernel/block/linux-kernel-block-core|块设备层]]
- [[entities/linux/kernel/block/linux-kernel-block-mq|blk-mq]]
- [[entities/linux/kernel/block/linux-kernel-block-scheduler|IO 调度器]]
- [[entities/linux/kernel/virt/linux-kernel-virt-kvm|KVM]]
- [[entities/linux/kernel/virt/linux-kernel-virt-virtio|Virtio]]
- [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core|io_uring]]
- [[entities/linux/kernel/vfs/linux-kernel-vfs-core|VFS]]
- [[entities/linux/kernel/net/linux-kernel-net-subsystem|网络子系统]]
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework|Netfilter]]
- [[entities/linux/kernel/crypto/linux-kernel-crypto-core|加密]]
- [[entities/linux/kernel/locking/linux-kernel-locking-core|锁]]
- [[entities/linux/kernel/ipc/linux-kernel-ipc-core|IPC]]
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core|RCU]]
- [[entities/linux/kernel/time/linux-kernel-time-core|时间子系统]]
- [[entities/linux/kernel/sound/linux-kernel-sound-core|音频]]

### QEMU
- [[entities/linux/qemu/qemu-qom|QOM]]
- [[entities/linux/qemu/qemu-memory|内存]]
- [[entities/linux/qemu/qemu-cpu|CPU]]
- [[entities/linux/qemu/qemu-block-layer|块层]]
- [[entities/linux/qemu/qemu-migration|热迁移]]

### 网络
- [[entities/linux/network/linux-network-protocols|TCP/IP 协议栈]]

### OS 基础
- [[entities/os/linux-vfs|VFS]]
- [[entities/os/linux-scheduler|调度器]]
- [[entities/os/linux-memory-allocator|内存分配器]]
- [[entities/os/linux-cgroups|cgroups]]
- [[entities/os/os-io-model|IO 模型]]
- [[entities/os/os-process-thread|进程线程]]
- [[entities/os/os-virtual-memory|虚拟内存]]

### C++
- [[entities/cpp/move-semantics|移动语义]]
- [[entities/cpp/smart-pointers|智能指针]]
- [[entities/cpp/lambda-expressions|Lambda]]
- [[entities/cpp/auto-type-deduction|auto/decltype]]
- [[entities/cpp/constexpr|constexpr]]
- [[entities/cpp/concurrency|并发]]
- [[entities/cpp/raii|RAII]]
- [[entities/cpp/variadic-templates|变参模板]]
- [[entities/cpp/if-constexpr|if constexpr]]
- [[entities/cpp/cpp20-features|C++20]]

### 数据结构
- [[entities/datastructure/algorithm-complexity|复杂度分析]]
- [[entities/datastructure/linear-data-structures|线性结构]]
- [[entities/datastructure/sorting-algorithms|排序]]
- [[entities/datastructure/dynamic-programming|动态规划]]
- [[entities/datastructure/recursion-and-divide-conquer|递归分治]]
- [[entities/datastructure/hash-table|哈希表]]
- [[entities/datastructure/trees-and-graphs|树与图]]

### 设计模式
- [[entities/design-patterns/solid-principles|SOLID]]
- [[entities/design-patterns/creational-patterns|创建型]]
- [[entities/design-patterns/structural-patterns|结构型]]
- [[entities/design-patterns/behavioral-patterns|行为型]]

### 面试
- [[entities/interview/interview-preparation|准备方法论]]
- [[entities/interview/problem-solving-patterns|解题模式]]
- [[entities/interview/system-design-basics|系统设计]]

---

## 局部图谱

```dataview
TABLE file.tags AS "标签"
FROM "entities/linux" OR "entities/os" OR "entities/cpp" OR "entities/datastructure" OR "entities/design-patterns" OR "entities/interview"
SORT file.name ASC
```
