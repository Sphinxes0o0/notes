---
type: source
source-type: paper
title: "eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More"
path: papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf
source-md5: 99f2802fa9c1ec185a29131f7763af3a
size: 275 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More

> Ingested from `papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.27 MB.

## Page 1

eBPF Library Ecosystem Overview


Go, Rust, Python, C and Other Languages



Kyle Quest

## Page 2

The Problem

## Page 3

_(no text content on this page)_

## Page 4

The Libraries

## Page 5

●  C: bcc, libbpf
●  Go: iovisor/gobpf, cilium/ebpf, dropbox/goebpf, libbpfgo
●  Python: bcc, pyebpf
●  Rust: libbpf-rs, redbpf, aya
●  Other: Lua (bcc), Node.js (bpf, bpfcc), Ruby (rbbcc)

## Page 6

A Bit of Background

## Page 7

● Program Types (loading and attaching)
● I/O (basic operations, additional abstractions)
● Writing Programs (helpers, native language support)
● Compiling Programs (external, clang integration, native)

## Page 8

Program Types

## Page 9

●  Tracing and Profiling (kprobes, uprobes, tracepoints, perf
   events)
●  Networking
  ○  XDP
  ○  TC
  ○  Socket Control and Filtering
●  Cgroup Resource Control (more socket control)
●  Security (LSM)
●  Other

## Page 10

C/C++ Libraries

## Page 11

BCC

## Page 12

●  Most popular eBPF library (direct/indirect use)
●  Program creation abstractions/helpers
●  I/O abstractions
●  Program compiler abstractions (LLVM/clang runtime dependency)
●  Lots of examples and tools
●  Biggest community
●  Supported program types:
  ○   Tracing and profiling programs
  ○   XDP, TC, Socket Filtering networking programs
  ○   Security (LSM) programs
●  Verdict: Good option if you want to leverage the power of BCC and
   you are building system or XDP/TC-based network tracing apps
●  https://github.com/iovisor/bcc

## Page 13

libbpf

## Page 14

●  Official eBPF library (eBPF linux kernel maintainers)
●  Focus on reusable eBPF programs (CO-RE)
●  No I/O, program or compiler abstractions
●  Template/starter project: https://github.com/libbpf/libbpf-bootstrap
●  Supported program types (explicit attach support):
  ○   Tracing and profiling programs
  ○   XDP networking programs
  ○   Security (LSM) programs
●  Support for generic program attach and link create calls
●  Verdict: Good option if you want to use the official eBPF library and
   you are ok using its low level interface and you don’t need the
   abstractions in BCC
●  https://github.com/libbpf/libbpf

## Page 15

Go Libraries

## Page 16

iovisor/gobpf

## Page 17

●  Official BCC wrapper
●  Supported program types:
  ○   Tracing and profiling programs
  ○   XDP networking programs
●  Partial (load only) support for TC and some Socket Control and Filtering
   program types
●  Verdict: Good option if you want to leverage the power of BCC and
   you are building tracing apps
●  https://github.com/iovisor/gobpf

## Page 18

cilium/ebpf

## Page 19

●  Pure Go library
●  Initial goal use case - networking (“packet wrangling in XDP and TC”)
●  Tracing/profiling wasn’t the initial goal, but now it’s supported
●  Strange/clever API (Collections, Specs)
●  “asm” - helper library to write eBPF programs (low level instructions)
●  “bpf2go” - embed compiled programs in Go code
●  You are responsible for attaching many/important networking program
   types (e.g., XDP, TC)
●  Exposes low level / raw attach program (BPF_PROG_ATTACH) and
   attach link (BPF_LINK_CREATE) interfaces (useful for some prog types)
●  Supported program types (explicit “attach” support):
  ○   Most tracing and profiling programs
  ○   Few other program types (based on the vendor use cases / needs)
●  Verdict: Interesting library if you want a pure Go library and you are ok
   with the library design
●  https://github.com/cilium/ebpf

## Page 20

dropbox/goebpf

## Page 21

●  Pure Go library
●  Focus on networking
●  Nice and clean
●  Strange/unnecessary use of CGo in some cases
●  Supported program types:
  ○   Basic tracing and profiling programs (kprobes/kretprobes only)
  ○   XDP networking programs
  ○   One of the Socket filtering program types (SOCKET_FILTER)
  ○   TC network program types (but only loading, no attach, so doesn’t count :-))
●  Verdict: Interesting library if it supports the program types you need
   and if you want to a pure Go library
●  https://github.com/dropbox/goebpf

## Page 22

libbpfgo

## Page 23

●  Thin libbpf wrapper
●  Focus on tracing and other product use cases for the library vendor
●  Supported program types:
  ○   Tracing and profiling programs
  ○   Security (LSM) programs
  ○   TC network program types
●  Verdict: Good library if it supports the program types you need and if
   you want to use libbpf in Go
●  https://github.com/aquasecurity/libbpfgo

## Page 24

Python Libraries

## Page 25

BCC

## Page 26

●  Official BCC wrapper
●  Program creation helpers
●  I/O abstractions
●  Most widely used eBPF library
●  Lots of examples and python-based tools
●  Verdict: Use this library if you want to leverage the power of BCC and
   its community
●  https://github.com/iovisor/bcc/tree/master/src/python/bcc

## Page 27

pyebpf

## Page 28

●  BCC wrapper (with extras)
●  Lets you write kprobes and I/O handlers in Python
●  Dated (python2 only) and requires extra work
●  Supported program types:
   ○ Only kprobe tracing and profiling programs
●  Verdict: Good library if you are looking for a project to contribute and
   you want to write kprobe eBPF programs in Python
●  https://pypi.org/project/pyebpf

## Page 29

Rust Libraries

## Page 30

libbpf-rs

## Page 31

●  Lightweight libbpf wrapper (almost official rust library for libbpf :-))
●  Needs good examples
●  Leverages “auto-attach” from libbpf
●  Explicitly supported program/attach types:
  ○   Most tracing and profiling programs (no raw tracepoint support)
  ○   XDP networking programs
  ○   Security/LSM programs
  ○   One of the Socket filtering program types (SK_SKB/sockmap/streamparser)
●  Verdict: Good option if you just want to use libbpf directly from Rust.
●  https://github.com/libbpf/libbpf-rs
●  https://github.com/libbpf/libbpf-bootstrap/tree/master/examples/rust

## Page 32

redbpf

## Page 33

●  libbpf wrapper (partial wrapper, with extras)
●  Focus on networking and other product use cases for the library
   creators
●  Supported program types:
  ○   Some tracing and profiling programs (no raw tracepoint support)
  ○   XDP networking programs
  ○   Two Socket filtering program types (SOCKET_FILTER, SK_SKB/sockmap)
●  “redbpf-probes” - helper library to generate eBPF programs
●  Verdict: Interesting library if it supports the program types you need
●  https://github.com/foniod/redbpf

## Page 34

aya

## Page 35

●  Pure Rust library
●  Supported program types:
  ○   Most tracing and profiling programs (raw tracepoint support is WIP)
  ○   XDP networking programs
  ○   TC classifier programs
  ○   Several socket control and filtering programs (SOCK_FILTER, SK_SKB, SOCK_OPS,
      SK_MSG)
  ○   Security/LSM (WIP)
  ○   Others
●  Planned support for rust-based eBPF programs (no clang)
●  Verdict: Early, but pretty impressive
●  https://github.com/alessandrod/aya

## Page 36

Other Languages

## Page 37

Lua

 ●  Official bcc wrapper library
 ●  Quite a few examples (some work as-is, some don’t)
 ●  Doesn't get enough attention
 ●  Verdict: Be ready to do extra work
 ●  https://github.com/iovisor/bcc/tree/master/src/lua
 ●  https://github.com/iovisor/bcc/tree/master/examples/lua

## Page 38

Ruby

 ●  BCC wrapper
 ●  Supports most tracing and profiling programs
 ●  Quite a few examples
 ●  Requires a specific libbcc version
 ●  Verdict: Be ready to do extra work to make it work
 ●  https://github.com/udzura/rbbcc

## Page 39

Node.js

 ●  node_bpf - libbpf wrapper
   ○   Experimental / only a few MAP related functions
 ●  node_bpfcc - bcc wrapper
   ○   Supports most tracing and profiling programs
   ○   No raw tracepoint support
 ●  Doesn't get enough attention.
 ●  Verdict: Cool experiment, but you are on your own if you try to use it.
 ●  https://github.com/mildsunrise/node_bpf
 ●  https://github.com/mildsunrise/node_bpfcc

## Page 40

Key Takeaways

## Page 41

  Thank You







https://twitter.com/kcqon
https://github.com/kcq

## Page 42

Program Type
Categories

## Page 43

Tracing and Profiling

## Page 44

●  BPF_PROG_TYPE_KPROBE (kprobe/kretprobe/uprobe/uretprobe)
●  BPF_PROG_TYPE_PERF_EVENT
●  BPF_PROG_TYPE_TRACEPOINT
●  BPF_PROG_TYPE_RAW_TRACEPOINT
●  BPF_PROG_TYPE_RAW_TRACEPOINT_WRITABLE

## Page 45

Networking

## Page 46

XDP

● BPF_PROG_TYPE_XDP

## Page 47

Traffic Control (TC)

 ●  BPF_PROG_TYPE_SCHED_CLS
 ●  BPF_PROG_TYPE_SCHED_ACT

## Page 48

Socket Control and Filtering

 ●  BPF_PROG_TYPE_SOCKET_FILTER
 ●  BPF_PROG_TYPE_SOCK_OPS
 ●  BPF_PROG_TYPE_SK_SKB
 ●  BPF_PROG_TYPE_SK_MSG
 ●  BPF_PROG_TYPE_SK_LOOKUP
 ●  BPF_PROG_TYPE_SK_REUSEPORT
 ●  BPF_PROG_TYPE_STRUCT_OPS

## Page 49

Flow Disector

● BPF_PROG_TYPE_FLOW_DISSECTOR

## Page 50

Lightweight Tunnel

 ●  BPF_PROG_TYPE_LWT_IN
 ●  BPF_PROG_TYPE_LWT_OUT
 ●  BPF_PROG_TYPE_LWT_XMIT
 ●  BPF_PROG_TYPE_LWT_SEG6LOCAL

## Page 51

Cgroup Resource Control

## Page 52

●  BPF_PROG_TYPE_CGROUP_SKB
●  BPF_PROG_TYPE_CGROUP_SOCK
●  BPF_PROG_TYPE_CGROUP_SOCKOPT
●  BPF_PROG_TYPE_CGROUP_SOCK_ADDR
●  BPF_PROG_TYPE_CGROUP_SYSCTL
●  BPF_PROG_TYPE_CGROUP_DEVICE

## Page 53

Security

## Page 54

● BPF_PROG_TYPE_LSM

## Related pages

- [[linux-ebpf-fundamentals]]

## Source

- Local path: `[[papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf]]`
