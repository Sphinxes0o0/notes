---
title: QEMU 架构分析
index: false
---

# QEMU 架构分析

本部分深入分析 QEMU 模拟器的内部架构、实现细节、设计模式和实现技巧。

## 目录

### Phase 1-3: 核心子系统

- [QOM (QEMU 对象模型)](./01_qom.md)
- [内存管理](./02_memory.md)
- [CPU 执行](./03_cpu.md)

### Phase 4: 块设备层

- [BlockDriverState 图结构](./04_block_bs_graph.md)
- [QCOW2 格式实现](./04_qcow2.md)
- [Coroutine 和 I/O 线程](./04_coroutine_io.md)
- [块任务与实时迁移](./04_block_job.md)

### Phase 5: 迁移

- [迁移框架](./05_migration_framework.md)
- [RAM 迁移](./05_ram_migration.md)
- [Multifd 和压缩](./05_multifd_compression.md)

### Phase 6: 网络

- [网络核心架构](./06_network_core.md)
- [VLAN 和 Hub](./06_vlan_hub.md)

### Phase 7: 用户模式

- [系统调用模拟](./07_syscall.md)
- [信号处理](./07_signal.md)

### Phase 8: QAPI

- [QAPI Schema 和代码生成](./08_qapi.md)

### Phase 9: UI

- [VNC 服务器架构](./09_vnc.md)

## 关键架构模式

1. **处理器/回调调度**: QOM、迁移、块设备都使用注册的处理程序表
2. **访问者模式**: QAPI 代码生成广泛使用访问者模式
3. **状态机**: 迁移、块任务使用显式状态转换
4. **双缓冲**: VNC 服务器表面 vs 访客表面
5. **基于协程的异步 I/O**: 块设备层使用协程进行非阻塞操作
6. **点对点链接**: NetClientState 使用 `peer` 指针进行连接
7. **两阶段信号传递**: 捕获主机信号，转换，排队，稍后传递
8. **从 Schema 生成代码**: QAPI 从 JSON 描述生成 C 代码
