---
type: index
tags: [linux-kernel, virtualization]
created: 2026-05-22
---

# Linux Kernel — Virtualization

> KVM hypervisor and Virtio paravirtual I/O framework

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] | KVM: hardware virtualization, struct kvm/vCPU, VM-Exit/Entry, EPT paging, Dirty Ring, guest_memfd | linux-kernel, virtualization, kvm |
| [[entities/linux/kernel/virt/linux-kernel-virt-virtio]] | Virtio: paravirtual I/O framework, virtqueue ring, device state machine, PCI/MMIO transport | linux-kernel, virtualization, virtio |

## Cross-References

- [[kernel-io-index]] — Virtio devices use VFS file_operations; KVM disk I/O flows through io_uring
- [[kernel-net-index]] — Virtio-net network device connects to kernel network stack
- [[qemu-index]] — QEMU as the userspace host for KVM + Virtio
