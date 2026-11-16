---
type: source
source-type: web
title: "Writing an OS in Rust"
author: "Philipp Oppermann"
date: 2024
size: medium
path: https://os.phil-opp.com/
summary: "Progressive hands-on tutorial series building a minimal 64-bit x86 kernel in Rust, covering boot, VGA text, exceptions, paging, heap allocation, and async multitasking."
tags: [linux-kernel, rust, os-dev, kernel, boot, paging, interrupt, heap, async, x86_64, no_std]
created: 2026-05-29
---

# Writing an OS in Rust

## 核心内容

### Bare Bones
**Rust no_std binary:**
```rust
#![no_std]
#![no_main]

#[no_mangle]
pub extern "C" fn _start() -> ! {
    loop {}
}
```

**Cargo.toml essentials:**
```toml
[dependencies]
bootloader = "0.9"
rust-std = { version = "1.75", features = ["compiler-builtins-mangled-names"] }
[profile.dev]
panic = "abort"
lto = true
```

**Linker script** — kernel at 0x200000, stack at 0x8f000:
```ld
OUTPUT_FORMAT("elf64-x86-64")
ENTRY(_start)
SECTIONS { .text 0x200000 : { *(.text.*) } }
```

### VGA Text Mode
```rust
volatile::Volatile<u16>::new(0x1 << 12 | 0xf << 8 | b'X')
    .write(0xb8000 as *mut u16);
```

### Interrupt Descriptor Table (IDT)
```rust
#[repr(C)]
struct IdtDesc {
    limit: u16, base: u64,
}
```

### Paging (4-level tables)
- Virtual address: 48-bit VA → 4-level page walk
- 2MB huge pages via `PS` bit (bit 7) in PDE/PTE
- `cr3` register points to PML4

### Heap Allocation
```rust
// bump allocator → linked-list allocator
struct Allocator {
    head: AtomicPtr<Node>,
}
```

### Async/Await
```rust
async fn task() {
    Timer::new().await;
    println!("done");
}
```

## 与其他教程对比

| 方面 | 本教程 | LKMPG | 1000行C |
|------|--------|--------|---------|
| 语言 | Rust | C | C |
| 架构 | x86_64 | any | RISC-V |
| 复杂度 | 中 | 高 | 低 |
| 覆盖深度 | Boot→Async | Kernel模块 | 完整OS |

## NIDS 关联

- **Rust 内存安全** → 内核代码更安全（无 use-after-free, 数据竞争）
- **分页/虚拟内存** → 理解 IDS 沙箱隔离
- **中断处理** → 数据包到达的硬件中断驱动模型
- **堆分配器** → NIDS 缓冲区管理
- **eBPF + Rust**: `redbpf`, `aya` 项目使用 Rust 开发 eBPF 程序

## 来源详情

- **开源**: GitHub `phil-opp/os-blog`
- **翻译**: 10种语言（含中文）
- **工具**: `bootimage` crate, QEMU
- **相关**: [[entities/linux/kernel/mm/linux-kernel-mm]] — 分页/内存管理
- **相关**: [[entities/rust]] — Rust 语言
