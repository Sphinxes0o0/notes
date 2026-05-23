---
type: entity
tags: [os, linking, loading, elf, executable]
created: 2026-05-23
sources: [pdf-linux-sysprog]
---

# Linking and Loading

## Definition

The process of combining multiple object files into a single executable (linking), and the process of bringing that executable into memory for execution (loading). These mechanisms are fundamental to how modern operating systems build and run programs.

## Key Concepts

- **Static Linking**: At build time, the linker (ld) resolves symbol references across object files, performs relocation, and produces a complete executable. All library code is embedded in the output.
- **Dynamic Linking**: At load time or run time, the dynamic linker/loader (ld.so) resolves shared library symbols, enabling code sharing between processes and reducing executable size.
- **ELF Format**: The Executable and Linking Format (used on Linux) defines three views: relocatable object files (.o), executable files, and shared objects (.so). Headers include ELF header, program header table (segments for loading), and section header table (sections for linking).
- **Symbol Resolution**: The linker matches symbol references to definitions across object files and libraries, handling strong/weak symbols (global variables, functions).
- **Relocation**: The linker modifies code/data references (absolute addresses, PC-relative offsets) to reflect final memory layout. Relocation entries tell the linker what to patch.
- **Position-Independent Code (PIC)**: Code that can execute correctly regardless of its absolute memory address, using GOT (Global Offset Table) and PLT (Procedure Linkage Table) indirection.
- **Library Interpositioning**: Intercepting library calls by replacing symbols at link time, load time (LD_PRELOAD), or run time (ptrace).

## Machine-Level Implementation

- Static linking: linker produces flat executable with text/data/bss segments at fixed addresses
- Dynamic linking: loader maps shared libraries via mmap, lazy binding resolves PLT entries on first call
- Linux: execve() → kernel loads program headers → sets up initial stack (argc/argv/envp) → jumps to _start → __libc_start_main → main()

## Related Concepts

- [[entities/os/os-virtual-memory]] — Virtual memory and address space layout
- [[entities/os/linux-vfs]] — File I/O for executable loading
- [[entities/sys]] — ELF format, system-level programming
- [[os-index]] — Operating system fundamentals

## Source Details

- [[sources/pdf-linux-sysprog]] — CSAPP Chapter 7: Linking; TLPI process execution
