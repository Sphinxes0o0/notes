---
type: entity
tags: [cpp, embedded, module-design, nuttx, iot]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# 董俊杰 — C++ in Xiaomi Vela: Application, Experience & Future

## 定义
小米工程师董俊杰分享C++在Xiaomi Vela嵌入式操作系统中的应用实践：基于clang的C++17支持、模块化设计原则（分层设计、Delegate模式、避免超级类）。

## 关键要点

### Xiaomi Vela系统架构
- **Vela Safety OS**：功能安全系统
- **Vela Hybrid OS**：融合系统
- **Vela IoT OS**：轻量物联网操作系统
- 内核：NuttX / Linux Kernel
- C++核心定位：通信中间件、应用框架、服务框架、基础库

### C++在Vela中的技术细节
- **编译器**：基于clang，支持C++17/20（但不宜过高）
- **STL限制**：需关闭RTTI和EXCEPTION以减少运行时开销
- **TLS问题**：std::thread_local不可使用；Slot限制（默认8个）；存在内存泄漏
- **代码size**：可通过宏控制和链接优化（-Os -lto）减少体积
- **RTOS特殊问题**：flat模式下全局/静态变量存在一次构造、多次析构问题

### 模块化设计常见误区与解决方案

**误区1：交叉引用（依赖外溢）**
- 问题：上层模块依赖非核心对象，导致网状依赖
- 解决：分层设计 — 上层依赖下层，下层不能依赖上层

**误区2：反向依赖**
- 解决：Delegate/Client模式 — 将底层依赖做成接口，通过继承解决

**误区3：接口过度设计**
- 问题：一个接口只有一个实现时，容易因维护者添加功能而膨胀
- 解决：果断删除接口，只对外提供API；严格按API规则管理

**误区4：超级类**
- 解决：Inner实现类 + 外部接口分离；化整为零，分割功能（每个类完成一个任务）

### 做好设计的真正难题
- 从一个类、一个函数做起
- 谨防代码维护和演进过程中的代码变味
- 加强团队教育 + 代码Review + 定期微重构

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — Vela中的容器使用限制
- [[entities/cpp/raii]] — 嵌入式环境资源管理

## 来源详情
- [[sources/pdf-cpp-slides]] — 董俊杰, C++在Xiaomi Vela中的应用
