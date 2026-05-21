---
type: entity
tags: [QEMU, CPU执行, TCG, 模拟器]
created: 2026-05-20
sources: [notes-qemu]
---

# QEMU CPU 执行架构

## 定义

QEMU 通过 Tiny Code Generator (TCG) 将 guest 指令翻译为 host 指令执行，配合 AccelClass 支持 KVM/HVF 等硬件加速。

## 关键要点

- **cpu_exec 主循环**: 检查停止请求 → 处理信号 → 执行 TCG 代码 → 处理返回值（EXCP_DEBUG/HLT/YIELD）
- **TranslationBlock**: 翻译块缓存，包含原始 PC、代码大小、跳转目标、host 代码指针
- **TCG 翻译流程**: `tb_gen_code()` → `tcg_func_create()` → `temp_alloc()` → `tcg_out_op()` → `patch_reloc()` → `tb_link_page()`
- **AccelClass**: 抽象加速器接口，`init_machine()` 初始化，`cpu_exec_enable/interrupt` 控制执行
- **KVM 集成**: `kvm_init_vcpu()` → `KVM_CREATE_VCPU` → `kvm_vcpu_init()`
- **翻译块缓存**: 通过 PC + CS_BASE + flags 的 hash 加速查找

## 设计模式

1. **解释器模式**: TCG 将 guest 代码解释为 host 代码
2. **缓存模式**: TB hash 缓存加速翻译
3. **策略模式**: AccelClass 支持多种加速器（TCG/KVM/HVF）
4. **模板方法**: cpu_exec 提供主循环框架

## 相关概念

- [[entities/linux/qemu/qemu-memory]] — CPU 执行涉及内存访问
- [[entities/linux/qemu/qemu-qom]] — CPUState 继承自 Object

## 来源详情

- [[sources/github-notes-qemu]]
