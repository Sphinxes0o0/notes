---
type: source
source-type: pdf
created: 2026-05-23
sources: [pdf-linux-sysprog]
title: "Linux System Programming (4 books)"
author: "Michael Kerrisk; W. Richard Stevens; Nick Parlante, Julie Zelenski; Randal E. Bryant, David R. O'Hallaron"
date: 2026-05-23
size: large
path: raw/PDFs/books/The Linux Programming Interface.pdf, raw/PDFs/books/UNIX环境高级编程(第三版).pdf, raw/PDFs/books/UnixProgrammingTools.pdf, raw/PDFs/books/computer_systems_a_programmers_perspective.pdf
summary: "4册Linux系统编程经典：TLPI Linux/UNIX系统编程接口、APUE UNIX环境高级编程（第三版·中文）、Stanford Unix编程工具(gcc/make/gdb/emacs)、CSAPP深入理解计算机系统(程序员视角)"
tags: [linux, system-programming, books]
---

# Linux System Programming (4 books)

## Core Content

### 1. The Linux Programming Interface (Michael Kerrisk, 1556 pages)

The definitive Linux/UNIX system programming reference, covering the complete Linux/POSIX API surface.

**System Programming Fundamentals:**
- File I/O: file descriptors, buffering, scatter-gather I/O, file locking
- Processes: fork, exec, process creation/termination, credentials, capabilities
- Memory: brk/sbrk, mmap, shared memory, memory locking
- Signals: signal handlers, reentrancy, async-signal safety, real-time signals
- Timers: interval timers, POSIX clocks/timers, timerfd
- Threads: pthreads, mutexes, condition variables, thread pools
- IPC: pipes, FIFOs, message queues, semaphores, shared memory, sockets
- Sockets: UNIX domain sockets, TCP/UDP sockets, socket options, I/O multiplexing (select/poll/epoll)
- Advanced I/O: async I/O, memory-mapped I/O, /dev/fd
- Linux-specific: epoll, inotify, signalfd, eventfd, timerfd, capabilities, cgroups, namespaces

**Key Themes:**
- Portability between Linux and other UNIX systems (SUSv3/POSIX)
- Complete C function-level API coverage with error handling patterns
- Linux-specific extensions beyond POSIX standard
- Thread safety and reentrancy considerations

### 2. Advanced Programming in the UNIX Environment (W. Richard Stevens, 3rd Ed, 822 pages, scanned)

A classic UNIX system programming textbook covering the full POSIX API surface.

**Content Areas:**
- UNIX standardization and implementations
- File I/O: unbuffered I/O, file sharing, /dev/fd
- Files and directories: stat, file types, directory traversal
- Standard I/O library: buffering, streams, temp files
- System data files and information
- Process environment: main function, memory layout, environment variables, setjmp/longjmp
- Process control: fork, vfork, exec variants, wait, process accounting
- Process relationships: sessions, process groups, controlling terminal
- Signals: signal concepts, unreliable signals, POSIX reliable signals, sigaction
- Threads: pthread_create/join, thread synchronization, thread-specific data
- Daemon processes: coding rules, logging, SIGHUP handling
- Advanced I/O: non-blocking I/O, record locking, I/O multiplexing (select/poll), asynchronous I/O
- IPC: pipes, FIFOs, XSI IPC (message queues/semaphores/shared memory), POSIX IPC, network IPC (sockets)
- Pseudo terminals: architecture, PTY implementations (BSD/System V)

### 3. Unix Programming Tools (Stanford CS Education Library, Parlante/Zelenski)

A concise 16-page guide to the core Unix developer toolchain.

**Tools Covered:**
- **gcc compiler/linker**: compile-link process, common flags (-c, -o, -g, -O, -Wall), library linking (-l, -L)
- **make project utility**: Makefile syntax, targets/dependencies, variables, typical build patterns
- **gdb debugger**: breakpoints, stepping, backtrace, inspecting variables, core dump analysis
- **emacs editor**: basic editing, compile integration, debugger interface
- **Unix shell**: essential commands for the edit-compile-link-debug cycle

### 4. Computer Systems: A Programmer's Perspective (Randal E. Bryant, David R. O'Hallaron, 1078 pages)

The definitive textbook bridging computer architecture and systems programming.

**Content Sections:**
- **Information representation**: bits/bytes/words, integer/float encoding, data sizes
- **Machine-level programming**: x86-64 instruction set, control flow, procedures, arrays/structs/unions
- **Processor architecture**: Y86-64 ISA, pipelining, hazard detection, branch prediction
- **Memory hierarchy**: SRAM/DRAM, cache memories, locality, cache-friendly programming
- **Linking**: ELF object files, symbol resolution, relocation, shared libraries, position-independent code
- **Exception control flow**: exceptions, interrupts, signals, non-local jumps
- **Virtual memory**: address translation, page tables, TLB, memory mapping, dynamic memory allocation
- **System-level I/O**: UNIX I/O, file descriptors, redirecting I/O
- **Concurrent programming**: threads, synchronization, race conditions, semaphores

## Key Quotes

- "The Linux Programming Interface is the definitive reference for Linux system programming" — Michael Kerrisk
- "The UNIX system is called a multiuser system because it allows multiple users to use the system simultaneously" — W. Richard Stevens, APUE

## Related Pages

- [[sys-prog-index]] — System programming module index
- [[os-index]] — Operating system fundamentals
- [[entities/os/os-process-thread]] — Process and thread model
- [[entities/os/os-virtual-memory]] — Virtual memory
- [[entities/os/os-io-model]] — I/O models (select/poll/epoll)
- [[entities/os/linux-vfs]] — VFS and file I/O
- [[entities/linux/kernel/linux-kernel-io-uring-core]] — io_uring async I/O
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] — Context switching
- [[entities/linux/kernel/linux-kernel-locking-core]] — Kernel locking
- [[entities/linux/kernel/linux-kernel-ipc-core]] — Kernel IPC
- [[entities/cpp/smart-pointers]] — RAII and resource management
- [[entities/cpp/concurrency]] — C++ concurrency
- [[entities/cpp/cpp-stl-containers]] — STL containers
- [[cpp-index]] — Modern C++ and STL
- [[entities/linux/kernel/index#networking]] — Kernel networking
