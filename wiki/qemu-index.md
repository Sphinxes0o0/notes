---
type: index
tags: [qemu, emulation]
created: 2026-05-22
---

# QEMU — Emulator Architecture

> QOM object model, memory management, CPU execution, migration, and block layer

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/qemu/qemu-qom]] | QOM: QEMU Object Model, TypeInfo registration, inheritance, interface implementation | qemu |
| [[entities/linux/qemu/qemu-memory]] | Memory management: AddressSpace, MemoryRegion, FlatView three-layer structure | qemu |
| [[entities/linux/qemu/qemu-cpu]] | CPU execution: TCG code generation, KVM integration, TranslationBlock | qemu |
| [[entities/linux/qemu/qemu-migration]] | Migration framework: VMState, QEMUFile, precopy/postcopy | qemu |
| [[entities/linux/qemu/qemu-block-layer]] | Block device layer: BDS graph structure, QCOW2, coroutine async I/O | qemu |

## Cross-References

- [[entities/linux/kernel/index#virtualization]] — QEMU runs KVM as the hypervisor backend; TCG for userspace emulation
- [[entities/linux/kernel/index#block-layer]] — QEMU block layer emulates storage controllers that interact with kernel block layer
- [[entities/linux/kernel/index#io-uring--vfs]] — QEMU virtio-blk backed by io_uring on the host for high-performance storage
- [[os-index]] — QEMU emulates full system; understanding OS concepts helps grasp its abstractions
