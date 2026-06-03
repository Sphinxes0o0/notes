---
source-type: bookmark
title: "You Are The BIOS Now: Building A Hypervisor In Rust With KVM"
author: "Julian Goldstein"
date: 2025-07-29
url: https://yeet.cx/blog/you-are-the-bios-now
summary: "Building a Type-II hypervisor in Rust using KVM - a hands-on guide to virtualizing x86 from userspace."
---

# You Are The BIOS Now: Building A Hypervisor In Rust With KVM

**By: Julian Goldstein**
**Date:** July 29, 2025
**Read Time:** 20 min

## Introduction

In today's episode of *The Cursed Systems Programming Show* where the safety guarantees are fake and the `unsafe` blocks are real, we're going to write "Hello, World!" in the most cursed way imaginable.

Forget normal `syscalls`, let's tap into something even scarier: **x86's virtual machine extensions** and write a Type-II hypervisor in Rust.

There will be:

- No OS.
- Fake I/O ports.
- Just enough `unsafe` to get audited by the compiler and possibly the IRS.

After all, this is systems programming, where the guest is real, the devices are imaginary, and the pain is shared.

![Big Brain](attachments/you-are-the-bios-now-big-brain.png)

## Stepping Into The Singularity

Before we fire up the syringe with raw bytes and scream into fake hardware, we need to open a wormhole into the CPU itself, but not directly, because we're a Type-II hypervisor living in user space.

Instead, we are going to summon the [KVM](https://www.kernel.org/doc/Documentation/virtual/kvm/api.txt): Linux's built-in virtualization layer.

KVM acts as a proxy between user space and a class of privileged instructions known as [VMX](https://linasm.sourceforge.net/docs/instructions/vmx.php#maintain) (on Intel) or [SVM](https://www.0x04.net/doc/amd/33047.pdf) (on AMD) **without** writing a kernel module, legally changing your name to `/dev/mem` or whispering "ring zero" into a cold boot and hoping the kernel answers.

Once activated, the KVM throws your CPU into a parallel dimension where code thinks it's running on bare metal, but you're standing right beside it in user space intercepting its every move.

Some call it a sandbox, I call it a dream machine because once you step in, nothing is real.

![Map to Guest](attachments/you-are-the-bios-now-map-to-guest.png)

## Opening The Gates To Hell

At a high level, we summon the KVM by cracking open `/dev/kvm` and shouting `ioctl`s at it until it is convinced our program is worthy of holding a VCPU file descriptor (`VcpuFd`).

A **VCPU** is a data structure and control loop managed by the KVM and represents one "core" inside the virtual machine. You can think of it like hiring an unpaid intern to sit in user-space and hallucinate that it's real hardware.

To keep things only *moderately cursed*, we'll use the `kvm-ioctls` crate to paper over some sharp edges and encapsulate everything into a struct called `CursedVm`.

```rust
pub struct CursedVm {
    vcpu: kvm_ioctls::VcpuFd,
    ...
}

impl CursedVm {
    pub fn new() -> anyhow::Result<Self> {
        // Open KVM
        let kvm = Kvm::new()?;

        // Create a VM
        let vm = kvm.create_vm()?;

        // Create VCPU
        let vcpu = vm.create_vcpu(0)?;

        // ...

        let mut me = Self { vcpu, ... };

        // ...

        Ok(me)
    }
}
```

With this short and simple snippet: The KVM has handed our hypervisor a VCPU which it can puppet from user space.

There's just one problem: **Our VM has no memory.**

A `VcpuFd` gives our VM the illusion of power, but without memory, it is about as valuable as a half-charged vape with no idea how to segfault properly.

To fix that, we'll use `mmap_anonymous` to carve out a slab of page-aligned memory and then dress it up as "real physical RAM" by placing it inside a `kvm_userspace_memory_region` struct.

Once it's in costume, we `ioctl` it over the KVM fence.

```rust
const GUEST_PHYS_ADDR: u64 = 0x1000;
const GUEST_SIZE: usize = 256 << 20;

pub struct CursedVm {
    vcpu: kvm_ioctls::VcpuFd,
    guest_mem: NonNull<c_void>,
}

impl CursedVm {
    pub fn new() -> anyhow::Result<Self> {
        // ... Get a VCPU ...

        // Allocate guest memory
        let guest_mem = unsafe {
            mman::mmap_anonymous(
                None,
                GUEST_SIZE.try_into()?,
                mman::ProtFlags::PROT_READ | mman::ProtFlags::PROT_WRITE,
                mman::MapFlags::MAP_PRIVATE | mman::MapFlags::MAP_ANONYMOUS,
            )?
        };

        // Set up memory region
        let mem_region = kvm_bindings::kvm_userspace_memory_region {
            guest_phys_addr: GUEST_PHYS_ADDR,
            memory_size: GUEST_SIZE as u64,
            userspace_addr: guest_mem.as_ptr() as u64,
            ..Default::default()
        };

        // ioctl it over the fence.
        unsafe {
            vm.set_user_memory_region(mem_region)?;
        }

        let mut me = Self { vcpu, guest_mem };

        // ...

        Ok(me)
    }
}
```

When we call `set_user_memory_region` that's what gives the KVM the go ahead to wire that mapped region from **our hypervisors virtual address space** into **the guest's "physical" address space.** From the guest's point of view, it looks like genuine RAM.

By now, we have duct-taped enough `ioctl`s together where the VM has a CPU *(sort of),* memory *(allegedly),* and is ready to boot into something terrible.

## Welcome to 1978: Real Mode Revival

One important thing to remember: When x86 wakes up, it thinks it's still 1978.

It boots in **[real mode](https://en.wikipedia.org/wiki/Real_mode)**, a surreal 16-bit LARP where:

- Memory is limited to 1MB.
- Segmentation is king.
- And `jmp far` is still a completely reasonable thing to do.

But unlike a real machine, our guest doesn't even get a BIOS to hold its hand. There's no firmware, no boot-loader, no magic `int $0x10` only lies and `vmexit`s.

![8086](attachments/you-are-the-bios-now-8086.jpg)

To snap our VM out of its nostalgic hallucination, we need to *gently* (read: violently, with a crowbar) shove it into a sane execution state.

That means manually:

- Copying code into guest memory and point `%rip` at it.
- Initializing the general purpose registers (`%rsp`, `%rbp` , ...)
- Enabling protected mode, PAE, and long mode via `%cr0`, `%cr4`, and `%efer`
- Filling in page tables
- And finally faking a global descriptor table ([GDT](https://en.wikipedia.org/wiki/Global_Descriptor_Table)) and initializing the segment selectors, because real mode still thinks segmentation is a foundational cosmic truth when in reality its just the asbestos of x86: we *know* it's bad, but it's *everywhere*, and removing it might actually make things worse.

Sanity is *(mostly)* restored with 3 `CursedVm` methods that run just before we hand ownership back to its caller.

```rust
impl CursedVm {
    pub fn new() -> anyhow::Result<Self> {
        // ... Get a VCPU and allocate / register guest memory ...

        let mut me = Self { vcpu, guest_mem };

        me.setup_long_mode()?;
        me.map_pages()?;
        me.init_registers()?;

        Ok(me)
    }
}
```

### Entering Long Mode

Entering long mode from real mode is a bit like slapping around an analog TV hoping the picture finally stabilizes.

There's no real BIOS or stage one boot loader, so it is entirely on us to convince the CPU that all the mandatory relics of the x86 boot process have somehow already happened.

We need to handcraft a GDT, populate the segment registers, and flip ancient flags inside of `%cr0`, `%cr4`, and `%efer`.

```rust
const GUEST_PHYS_ADDR: u64 = 0x1000;
const GDT_OFFSET: usize = 0x0; // We just throw it at the start, but you can move it

impl CursedVM {
    fn setup_long_mode(&mut self) -> anyhow::Result<()> {
        // Get current special registers
        let mut sregs = self.vcpu.get_sregs()?;

        // Set up GDT for long mode
        sregs.gdt.base = GUEST_PHYS_ADDR + GDT_OFFSET as u64;
        sregs.gdt.limit = 23; // 3 entries * 8 bytes - 1

        // Write GDT entries to guest memory
        //
        // Our VM is Ring-0 Only!
        unsafe {
            let gdt_ptr = self
                .guest_mem
                .as_ptr()
                .add(GDT_OFFSET) as *mut u64;

            // Null descriptor
            *gdt_ptr.add(0) = 0x0000000000000000;
            // Code segment (64-bit, executable, present)
            *gdt_ptr.add(1) = 0x00209A0000000000;
            // Data segment (64-bit, writable, present)
            *gdt_ptr.add(2) = 0x0000920000000000;
        }

        // Configure code segment for long mode
        sregs.cs.base = 0;               // Base address for the segment (ignored in long mode)
        sregs.cs.limit = 0xffffffff;     // Limit (also ignored in long mode)
        sregs.cs.selector = 1 << 3;      // GDT index
        sregs.cs.present = 1;            // Segment is present
        sregs.cs.type_ = 11;             // Code: execute/read, accessed
        sregs.cs.dpl = 0;                // Descriptor privilege level (kernel ring 0)
        sregs.cs.db = 0;                 // Must be 0 in long mode (64-bit code)
        sregs.cs.s = 1;                  // Descriptor type: 1 = Code / Data (0 = system)
        sregs.cs.l = 1;                  // Long mode active (64-bit segment)
        sregs.cs.g = 1;                  // Granularity = 4 KB units (ignored in long mode, but set anyway)

        // Configure data segments
        sregs.ds.base = 0;               // Base address for the segment (ignored in long mode)
        sregs.ds.limit = 0xffffffff;     // Limit (also ignored in long mode)
        sregs.ds.selector = 2 << 3;      // GDT index
        sregs.ds.present = 1;            // Segment is present
        sregs.ds.type_ = 3;              // Data: read/write, accessed
        sregs.ds.dpl = 0;                // Kernel mode
        sregs.ds.db = 1;                 // 32-bit segment (ignored in 64-bit mode)
        sregs.ds.s = 1;                  // Code/data segment
        sregs.ds.g = 1;                  // Granularity = 4 KiB units

        // Replicate for the other segments.
        sregs.es = sregs.ds;
        sregs.fs = sregs.ds;
        sregs.gs = sregs.ds;
        sregs.ss = sregs.ds;

        // Enable long mode
        sregs.efer |= 0x500;     // LME (Long Mode Enable) + LMA (Long Mode Active)
        sregs.cr0 |= 0x80000001; // PG (Paging) + PE (Protection Enable)
        sregs.cr4 |= 0x20;       // PAE (Physical Address Extension)

        // Set special registers
        self.vcpu.set_sregs(&sregs)?;

        Ok(())
     }
 }
```

### Mapping In Pages

To keep things simple (and the memory management unit happy), we identity map the first 1 GB of guest memory using 2 MB large pages.

That means virtual addresses match physical addresses exactly. No translation needed.

Now the guest can touch the first gigabyte of RAM without spiraling into a triple fault.

![Page Map](attachments/you-are-the-bios-now-page-map.png)

```rust
const PML4_OFFSET: usize = 0x1000;
const PAGE_TABLE_SIZE: usize = 0x1000;

impl CursedVm {
    fn map_pages(&mut self) -> anyhow::Result<()> {
        unsafe {
            // Zero out the entire area of memory.
            ptr::write_bytes(self.guest_mem.as_ptr().add(PML4_OFFSET), 0, 3 * PAGE_TABLE_SIZE);

            // PML4 entry - points to PDPT
            let pml4 = self.guest_mem.as_ptr().add(PML4_OFFSET) as *mut u64;

            // Present + Writable
            *pml4 = (GUEST_PHYS_ADDR + PML4_OFFSET as u64 + PAGE_TABLE_SIZE as u64) | 0x3;

            // PDPT entry - points to PD
            let pdpt = self.guest_mem.as_ptr().add(PML4_OFFSET + PAGE_TABLE_SIZE) as *mut u64;

            // Present + Writable
            *pdpt = (GUEST_PHYS_ADDR + PML4_OFFSET as u64 + 2 * PAGE_TABLE_SIZE as u64) | 0x3;

            let pd = self.guest_mem.as_ptr().add(PML4_OFFSET + 2 * PAGE_TABLE_SIZE) as *mut u64;

            // Mark every entry in the page table as: Present + Writable + Large Page
            (0..512).for_each(|i| *pd.add(i) = (i << 21) as u64 | 0x83);
        }

        // Set CR3 to point to PML4
        let mut sregs = self.vcpu.get_sregs()?;

        sregs.cr3 = GUEST_PHYS_ADDR + PML4_OFFSET as u64;

        self.vcpu.set_sregs(&sregs)?;

        Ok(())
    }
}
```

### Initializing The General Purpose Registers

Once we have finished gaslighting the hardware into thinking it's modern:

We initialize `%rip` , `%rsp` and `%rbp` and provide an interface for copying code into the guest's address space.

![Memory Layout](attachments/you-are-the-bios-now-mem-layout.png)

```rust
const GUEST_PHYS_ADDR: u64 = 0x1000;
const GUEST_SIZE: usize = 256 << 20; // Needs to be enough to fit everything.
const GDT_OFFSET: usize = 0x0; // We just throw it at the start, but you can move it
const PML4_OFFSET: usize = 0x1000;
const PAGE_TABLE_SIZE: usize = 0x1000;
const PAGE_SIZE: usize = 1 << 21;
const CODE_OFFSET: usize = PML4_OFFSET + 3 * PAGE_TABLE_SIZE;

impl CursedVm {
    fn init_registers(&mut self) -> anyhow::Result<()> {
        let mut regs: kvm_bindings::kvm_regs = unsafe { mem::zeroed() };

        // Set up the code's entrypoint and page align the stack.
        regs.rip = GUEST_PHYS_ADDR + CODE_OFFSET as u64;
        regs.rsp = (GUEST_PHYS_ADDR + GUEST_SIZE as u64) & !(PAGE_SIZE as u64 - 1);
        regs.rbp = (GUEST_PHYS_ADDR + GUEST_SIZE as u64) & !(PAGE_SIZE as u64 - 1);

        regs.rflags = 1 << 1; // Reserved bit that must be set

        self.vcpu.set_regs(&regs)?;

        Ok(())
    }

    pub fn write_guest_code(&mut self, code: &[u8]) {
        unsafe {
            ptr::copy_nonoverlapping(
                code.as_ptr(),
                self.guest_mem.as_ptr().add(CODE_OFFSET) as *mut _,
                code.len(),
            );
        }
    }
}
```

## Banging Your Head Against The Desk Until Something Happens

Armed with memory, registers, and a working illusion of modernity, our VM is finally ready to *do something*. But what?

How do we actually **run** the guest?

How do we **catch** it when it starts screaming through `outb` and realizes BIOS isn't coming to save it?

Enter: `CursedVm::run_with_io_handler`

```rust
impl CursedVm {
  pub fn run_with_io_handler<F>(&mut self, mut io_handler: F) -> anyhow::Result<()>
    where
        F: FnMut(u16, &[u8]),
    {
        loop {
            match self.vcpu.run()? {
                VcpuExit::IoOut(port, data) => {
                    io_handler(port, data);
                }
                exit => {
                    return Err(anyhow::anyhow!("Unhandled exit reason: {:?}", exit));
                }
            }
        }
    }
}
```

This function kicks off the guest's execution loop and listens for I/O exits, specifically `out` instructions which we treat as the guest's only way of communicating with the outside world.

Think of I/O ports as x86's equivalent of a **tin can phone**:

One end lives entirely inside the guest's imagination, the other in our Rust hypervisor, bonded together by nothing but trust, `ioctl`'s, and the unresolved trauma of 1970s computer engineering decisions.

![Tin Can Phone](attachments/you-are-the-bios-now-tin-can-phone.jpg)

## Terminal Illusions: Giving the Guest A Way To Cry For Help

Since there's no frame buffer, serial port, or `syscalls`, the only way our guest can speak to us is by pressing on a janky piano key labeled `out $0x10` and hoping we hear it in user space.

```rust
use std::io;
use std::io::Write;
use std::sync::mpsc;
use std::thread;

mod vm;

fn main() -> anyhow::Result<()> {
    let (tx, rx) = mpsc::channel();

    ctrlc::set_handler(move || {
        tx.send(()).ok();
    })?;

    // ... Obtain the guest code as a slice of bytes ...

    thread::spawn(move || {
        if let Ok(mut vm) = vm::CursedVm::new() {
            vm.write_guest_code(&guest_code);
            vm.run_with_io_handler(|port, data| {
                if port == 0x10 && data.len() == 1 {
                    print!("{}", data[0] as char);
                    io::stdout().flush().ok();
                }
            })
            .ok();
        }
    });

    // Wait here until signal.
    rx.recv().ok();

    Ok(())
}
```

This whole I/O pipeline is less like hardware and more like a deranged group chat between the guest, the kernel, our hypervisor and its controlling `tty`:

1. Guest: *"Alright chat, `outb $0x48, $0x10`"*
2. KVM: *(_screeches in `vmexit`)*
3. Hypervisor: *"Ah yes, the ol' `outb 0x48 -> 0x10`. Classic."*
4. TTY: *"A wild `'H'` has appeared!"*

## Saying "Hello, World!" from the Abyss

It's time to inject some code and see if this cursed contraption can speak.

We _**could**_ write a linker script and configure `cargo` to compile a proper binary then boot into something that resembles structure.

But let's be real: We're past the point of **_ "doing it right."_**

![Chris Farley](attachments/you-are-the-bios-now-chris-farley.gif)

Instead we'll write a guest program, **_by hand_,** in **raw x86-64 machine code.**

Our program will begin by pushing `"Hello, World!\n\0\0"` encoded as two 64-bit values `0x57202c6f6c6c6548` and `0x00000a21646c726f` onto the guest's stack to re-purpose it as a poor man's `.rodata`.

Once the data is on the stack, we point `%rsi` at `%rsp`, loop over the stack byte-by-byte, sending each character to I/O port `0x10` until we hit a `NULL`. Then we reset and do it again.

![Stack](attachments/you-are-the-bios-now-stack.png)

```rust
fn main() -> anyhow::Result<()> {
    // ... Instantiate the VM and setup Ctrl+C to exit ...

    //     xor %rax, %rax                ; Zero %rax (not necessary)                        [0x00]
    //     push %rax                     ; Pad the stack with zeros (not necessary)         [0x03]
    //     mov $0x00000a21646c726f, %rax ; Load 'o', 'r', 'l', 'd', '!', '\n', '\0', '\0'   [0x04]
    //     push %rax                     ; "orld\n\0\0" is now on the stack                 [0x0e]
    //     mov $0x57202c6f6c6c6548, %rbx ; Load 'H', 'e', 'l', 'l', 'o', ',', ' ', 'W'      [0x0f]
    //     push %rbx                     ; "Hello, W" is now on the stack                   [0x19]
    //     mov %rsp, %rsi                ; %rsi now points at the top of the stack          [0x1a]
    // .loop:
    //     mov (%rsi), %al               ; Read a byte from %rsi                            [0x1d]
    //     test %al, %al                 ; Set the flags to test if its zero                [0x1f]
    //     je .reset                     ; If it is zero we are done                        [0x21]
    //     out %al, $0x10                ; Write out the byte to I/O port 0x10              [0x23]
    //     inc %rsi                      ; Move %rsi to the next byte on the stack          [0x25]
    //     jmp .loop                     ; Do it again                                      [0x28]
    // .reset
    //     mov %rsp, %rsi                ; Reset %rsi to point back to the top of the stack [0x2a]
    //     jmp .loop                                                                        [0x2d]
    //     nop                           ; For the purposes of %rip-relative offset calcs   [0x2f]
    let guest_code = [
        0x48, 0x31, 0xc0,                                           // [0x00]
        0x50,                                                       // [0x03]
        0x48, 0xb8, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a, 0x00, 0x00, // [0x04]
        0x50,                                                       // [0x0e]
        0x48, 0xbb, 0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, 0x57, // [0x0f]
        0x53,                                                       // [0x19]
        0x48, 0x89, 0xe6,                                           // [0x1a]
        0x8a, 0x06,                                                 // [0x1d]
        0x84, 0xc0,                                                 // [0x1f]
        0x74, 0x07,                                                 // [0x21]
        0xe6, 0x10,                                                 // [0x23]
        0x48, 0xff, 0xc6,                                           // [0x25]
        0xeb, 0xf3,                                                 // [0x28]
        0x48, 0x89, 0xe6,                                           // [0x2a]
        0xeb, 0xee,                                                 // [0x2d]
        0x90,                                                       // [0x2f]
    ];

    // ... The VM execution loop

}
```

This is the part where you realize: you now control your own parallel universe. From userspace. No kernel modules. No permissions. Just the green pastures of Ring-0, identity mapped virtual addresses, and the serene horror of knowing **you are the BIOS now.**

![Hello World](attachments/you-are-the-bios-now-hello-world.gif)

## Measuring the Madness: Observability in the Void

At this point, there's only one reasonable thing left to do: **_Observe it._**

Enter yeet: **our extremely normal performance tool for extremely cursed software.**

In just a few clicks and under 10 seconds of setup, we can…

**Inspect in real-time how long the `CursedVm` thread spent spinning in byte code hell:**

![Guest Spin](attachments/you-are-the-bios-now-guest-spin.gif)

**Write and deploy a custom `bpf(2)` program to visualize, in real time, the number of `vmexit`s per second handled by the `CursedVm` thread, complete with an AI-generated-title:**

![VMExits](attachments/you-are-the-bios-now-vmexits.png)

You can check out more of our recipes [here.](/recipes)

## The End

If you made it this far: congratulations, you're now legally 5% `VcpuFd` and 95% `unsafe`. Take a nap, hydrate, and maybe don't open `/dev/kvm` again without supervision.

Or do. I'm not your kernel.

![Buy Me Coffee](attachments/buy-me-coffee.png)

![50 Cent](attachments/you-are-the-bios-now-50-cent.gif)

## Appendix

### main.rs

```rust
use std::io;
use std::io::Write;
use std::sync::mpsc;
use std::thread;

mod vm;

fn main() -> anyhow::Result<()> {
    let (tx, rx) = mpsc::channel();

    ctrlc::set_handler(move || {
        tx.send(()).ok();
    })?;

    //     xor %rax, %rax                ; Zero %rax (not necessary)                        [0x00]
    //     push %rax                     ; Pad the stack with zeros (not necessary)         [0x03]
    //     mov $0x00000a21646c726f, %rax ; Load 'o', 'r', 'l', 'd', '!', '\n', '\0', '\0'   [0x04]
    //     push %rax                     ; "orld\n\0\0" is now on the stack                 [0x0e]
    //     mov $0x57202c6f6c6c6548, %rbx ; Load 'H', 'e', 'l', 'l', 'o', ',', ' ', 'W'      [0x0f]
    //     push %rbx                     ; "Hello, W"         is now on the stack           [0x19]
    //     mov %rsp, %rsi                ; %rsi now points at the top of the stack          [0x1a]
    // .loop:
    //     mov (%rsi), %al               ; Read a byte from %rsi                            [0x1d]
    //     test %al, %al                 ; Set the flags to test if its zero                [0x1f]
    //     je .reset                     ; If it is zero we are done                        [0x21]
    //     out %al, $0x10                ; Write out the byte to I/O port 0x10              [0x23]
    //     inc %rsi                      ; Move %rsi to the next byte on the stack          [0x25]
    //     jmp .loop                     ; Do it again                                      [0x28]
    // .reset
    //     mov %rsp, %rsi                ; Reset %rsi to point back to the top of the stack [0x2a]
    //     jmp .loop                                                                        [0x2d]
    //     nop                           ; For the purposes of %rip-relative offset calcs   [0x2f]
    let guest_code = [
        0x48, 0x31, 0xc0,                                           // [0x00]
        0x50,                                                       // [0x03]
        0x48, 0xb8, 0x6f, 0x72, 0x6c, 0x64, 0x21, 0x0a, 0x00, 0x00, // [0x04]
        0x50,                                                       // [0x0e]
        0x48, 0xbb, 0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, 0x57, // [0x0f]
        0x53,                                                       // [0x19]
        0x48, 0x89, 0xe6,                                           // [0x1a]
        0x8a, 0x06,                                                 // [0x1d]
        0x84, 0xc0,                                                 // [0x1f]
        0x74, 0x07,                                                 // [0x21]
        0xe6, 0x10,                                                 // [0x23]
        0x48, 0xff, 0xc6,                                           // [0x25]
        0xeb, 0xf3,                                                 // [0x28]
        0x48, 0x89, 0xe6,                                           // [0x2a]
        0xeb, 0xee,                                                 // [0x2d]
        0x90,                                                       // [0x2f]
    ];

    thread::spawn(move || {
        if let Ok(mut vm) = vm::CursedVm::new() {
            vm.write_guest_code(&guest_code);
            vm.run_with_io_handler(|port, data| {
                if port == 0x10 && data.len() == 1 {
                    print!("{}", data[0] as char);
                    io::stdout().flush().ok();
                }
            })
            .ok();
        }
    });

    // Wait here until signal.
    rx.recv().ok();

    Ok(())
}
```

### vm.rs

```rust
use kvm_ioctls::{Kvm, VcpuExit};
use nix::sys::mman;
use std::ffi::c_void;
use std::mem;
use std::ptr::{self, NonNull};

const GUEST_PHYS_ADDR: u64 = 0x1000;
const GUEST_SIZE: usize = 256 << 20;
const GDT_OFFSET: usize = 0x0;
const PML4_OFFSET: usize = 0x1000;
const PAGE_TABLE_SIZE: usize = 0x1000;
const PAGE_SIZE: usize = 1 << 21;
const CODE_OFFSET: usize = PML4_OFFSET + (3 * PAGE_TABLE_SIZE);

/* Guest Memory Layout:
 *
 *  GUEST_PHYS_ADDR --> +-------------------------+
 *                      |        Available        |
 *    + GDT_OFFSET  --> +-------------------------+
 *                      | Global Descriptor Table |
 *    + PML4_OFFSET --> +-------------------------+
 *                      |                         |
 *                      |       Page Tables       |
 *                      |                         |
 *    + CODE_OFFSET --> +-------------------------+ <-- %rip
 *                      |                         |
 *                      |          Code           |
 *                      |                         |
 *                      +-------------------------+
 *                      |                         |
 *                      |                         |
 *                      |        Available        |
 *                      |                         |
 *                      |                         |
 *                      +-------------------------+ <-- %rsp
 *                      |                         |
 *                      |          Stack          |
 *                      |                         |
 *     + GUEST_SIZE --> +-------------------------+ <-- %rbp
 */

pub struct CursedVm {
    vcpu: kvm_ioctls::VcpuFd,
    guest_mem: NonNull<c_void>,
}

impl CursedVm {
    pub fn new() -> anyhow::Result<Self> {
        // Open KVM
        let kvm = Kvm::new()?;

        // Create VM
        let vm = kvm.create_vm()?;

        // Create VCPU
        let vcpu = vm.create_vcpu(0)?;

        // Allocate guest memory
        let guest_mem = unsafe {
            mman::mmap_anonymous(
                None,
                GUEST_SIZE.try_into()?,
                mman::ProtFlags::PROT_READ | mman::ProtFlags::PROT_WRITE,
                mman::MapFlags::MAP_PRIVATE | mman::MapFlags::MAP_ANONYMOUS,
            )?
        };

        // Set up memory region
        let mem_region = kvm_bindings::kvm_userspace_memory_region {
            guest_phys_addr: GUEST_PHYS_ADDR,
            memory_size: GUEST_SIZE as u64,
            userspace_addr: guest_mem.as_ptr() as u64,
            ..Default::default()
        };

        unsafe {
            vm.set_user_memory_region(mem_region)?;
        }

        let mut me = Self { vcpu, guest_mem };

        me.setup_long_mode()?;
        me.map_pages()?;
        me.init_registers()?;

        Ok(me)
    }

    fn setup_long_mode(&mut self) -> anyhow::Result<()> {
        // Get current special registers
        let mut sregs = self.vcpu.get_sregs()?;

        // Set up GDT for long mode
        sregs.gdt.base = GUEST_PHYS_ADDR + GDT_OFFSET as u64;
        sregs.gdt.limit = 23; // 3 entries * 8 bytes - 1

        // Write GDT entries to guest memory
        //
        // Our VM is Ring-0 Only!
        unsafe {
            let gdt_ptr = self.guest_mem.as_ptr().add(GDT_OFFSET) as *mut u64;

            // Null descriptor
            *gdt_ptr.add(0) = 0x0000000000000000;
            // Code segment (64-bit, executable, present)
            *gdt_ptr.add(1) = 0x00209A0000000000;
            // Data segment (64-bit, writable, present)
            *gdt_ptr.add(2) = 0x0000920000000000;
        }

        // Configure code segment for long mode
        sregs.cs.base = 0; // Base address for the segment (ignored in long mode)
        sregs.cs.limit = 0xffffffff; // Limit (also ignored in long mode)
        sregs.cs.selector = 1 << 3; // GDT index
        sregs.cs.present = 1; // Segment is present
        sregs.cs.type_ = 11; // Code: execute/read, accessed
        sregs.cs.dpl = 0; // Descriptor privilege level (kernel ring 0)
        sregs.cs.db = 0; // Must be 0 in long mode (64-bit code)
        sregs.cs.s = 1; // Descriptor type: 1 = Code / Data (0 = system)
        sregs.cs.l = 1; // Long mode active (64-bit segment)
        sregs.cs.g = 1; // Granularity = 4 KB units (ignored in long mode, but set anyway)

        // Configure data segments
        sregs.ds.base = 0; // Base address for the segment (ignored in long mode)
        sregs.ds.limit = 0xffffffff; // Limit (also ignored in long mode)
        sregs.ds.selector = 2 << 3; // GDT index
        sregs.ds.present = 1; // Segment is present
        sregs.ds.type_ = 3; // Data: read/write, accessed
        sregs.ds.dpl = 0; // Kernel mode
        sregs.ds.db = 1; // 32-bit segment (ignored in 64-bit mode)
        sregs.ds.s = 1; // Code/data segment
        sregs.ds.g = 1; // Granularity = 4 KiB units

        // Replicate for the other segments.
        sregs.es = sregs.ds;
        sregs.fs = sregs.ds;
        sregs.gs = sregs.ds;
        sregs.ss = sregs.ds;

        // Enable long mode
        sregs.efer |= 0x500; // LME (Long Mode Enable) + LMA (Long Mode Active)
        sregs.cr0 |= 0x80000001; // PG (Paging) + PE (Protection Enable)
        sregs.cr4 |= 0x20; // PAE (Physical Address Extension)

        // Set special registers
        self.vcpu.set_sregs(&sregs)?;

        Ok(())
    }

    fn map_pages(&mut self) -> anyhow::Result<()> {
        /* We are going to layout the guest's memory map in the following way:
         *
         * 0x0000000000000000 +-------------------+
         *                    |                   |
         *                    |  Identity Mapped  |
         *                    |                   |
         * 0x000000003FFFFFFF +-------------------+
         *                    |                   |
         *                    |                   |
         *                    |                   |
         *                    |    Don't Care     |
         *                    |                   |
         *                    |                   |
         *                    |                   |
         * 0xFFFFFFFFFFFFFFFF +-------------------+
         *
         * We will use large pages (2 MB) so 64-bit virtual addresses will
         * be segmented like so:
         *
         * +------------+------------+------------+------------------------------+
         * |-- 9 bits --|-- 9 bits --|-- 9 bits --|----------- 21 bits ----------|
         * +------------+------------+------------+------------------------------+
         * |    PML4    |    PDPT    |     PD     |       Page Offset (2 MB)     |
         * +------------+------------+------------+------------------------------+
         *
         * This configuration will simplify things a bit, given that there is currently
         * no operating system that would otherwise manage it.
         *
         *                                    L WP
         *                       +----------------+
         *  %cr3 -> &PML4[0]     |  &PDPT[0] |X|11| ---+
         *                       +----------------+    |
         *          &PML4[1..]   |0000000000000000|    |
         *                       +----------------+    |
         *          &PDPT[0] +-- |  &PD[0]   |X|11| <--+
         *                   |   +----------------+
         *                   |   |0000000000000000| &PDPT[1..]
         *                   |   +----------------+
         *                   +-> |  i << 21  |1|11| &PD[i] --> The Memory Page
         *                       +----------------+
         *
         *                       L = Large Page Bit
         *                       W = Writable
         *                       P = Present
         */
        unsafe {
            // Zero out the entire area of memory.
            ptr::write_bytes(
                self.guest_mem.as_ptr().add(PML4_OFFSET),
                0,
                3 * PAGE_TABLE_SIZE,
            );

            // PML4 entry - points to PDPT
            let pml4 = self.guest_mem.as_ptr().add(PML4_OFFSET) as *mut u64;

            // Present + Writable
            *pml4 = (GUEST_PHYS_ADDR + PML4_OFFSET as u64 + PAGE_TABLE_SIZE as u64) | 0x3;

            // PDPT entry - points to PD
            let pdpt = self.guest_mem.as_ptr().add(PML4_OFFSET + PAGE_TABLE_SIZE) as *mut u64;

            // Present + Writable
            *pdpt = (GUEST_PHYS_ADDR + PML4_OFFSET as u64 + 2 * PAGE_TABLE_SIZE as u64) | 0x3;

            let pd = self
                .guest_mem
                .as_ptr()
                .add(PML4_OFFSET + 2 * PAGE_TABLE_SIZE) as *mut u64;

            // Mark every entry in the page table as: Present + Writable + Large Page
            (0..512).for_each(|i| *pd.add(i) = (i << 21) as u64 | 0x83);
        }

        // Set CR3 to point to PML4
        let mut sregs = self.vcpu.get_sregs()?;

        sregs.cr3 = GUEST_PHYS_ADDR + PML4_OFFSET as u64;

        self.vcpu.set_sregs(&sregs)?;

        Ok(())
    }

    fn init_registers(&mut self) -> anyhow::Result<()> {
        let mut regs: kvm_bindings::kvm_regs = unsafe { mem::zeroed() };

        // Set up the code's entrypoint and page align the stack.
        regs.rip = GUEST_PHYS_ADDR + CODE_OFFSET as u64;
        regs.rsp = (GUEST_PHYS_ADDR + GUEST_SIZE as u64) & !(PAGE_SIZE as u64 - 1);
        regs.rbp = (GUEST_PHYS_ADDR + GUEST_SIZE as u64) & !(PAGE_SIZE as u64 - 1);

        regs.rflags = 1 << 1; // Reserved bit that must be set

        self.vcpu.set_regs(&regs)?;

        Ok(())
    }

    pub fn run_with_io_handler<F>(&mut self, mut io_handler: F) -> anyhow::Result<()>
    where
        F: FnMut(u16, &[u8]),
    {
        loop {
            match self.vcpu.run()? {
                VcpuExit::IoOut(port, data) => {
                    io_handler(port, data);
                }
                exit => {
                    return Err(anyhow::anyhow!("Unhandled exit reason: {:?}", exit));
                }
            }
        }
    }

    pub fn write_guest_code(&mut self, code: &[u8]) {
        unsafe {
            ptr::copy_nonoverlapping(
                code.as_ptr(),
                self.guest_mem.as_ptr().add(CODE_OFFSET) as *mut _,
                code.len(),
            );
        }
    }
}

impl Drop for CursedVm {
    fn drop(&mut self) {
        unsafe {
            mman::munmap(
                NonNull::new_unchecked(self.guest_mem.as_ptr() as *mut _),
                GUEST_SIZE,
            )
            .ok();
        }
    }
}
```

### Cargo.toml

```toml
[package]
name = "hyperv"
version = "0.1.0"
edition = "2024"

[dependencies]
anyhow = "1.0.98"
ctrlc = "3.4.7"
kvm-bindings = "0.13.0"
kvm-ioctls = "0.23.0"
nix = { version = "0.30.1", features = ["fs", "mman"] }
```
