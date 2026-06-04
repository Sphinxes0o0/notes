---
type: source
source-type: paper
title: "bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737"
path: papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf
source-md5: fc529bada5bc975cce0a74fbddc60f6a
size: 878 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737

> Ingested from `papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.86 MB.

## Page 1

BPF
Turning Linux into a
Microservices-aware
Operating System

## Page 2

About the Speaker

Thomas Graf
●   Linux kernel developer for ~15 years working on
    networking and security
●   Helped write one of the biggest monoliths ever
●   Worked on many Linux components over the years (IP,
    TCP, routing, netfilter/iptables, tc, Open vSwitch, …)
●   Creator of Cilium to leverage BPF in a cloud native and
    microservices context
●   Co-Founder & CTO of the company building Cilium





    2

## Page 3

Agenda

●  Evolution of running applications
  ○   From single task processes to microservices
●  Problems of the Linux kernel
  ○   The kernel
●  What is BPF?
  ○   Turning Linux into a modern, microservices-aware operating system
●  Cilium - BPF-based networking security for microservices
  ○   What is Cilium?
  ○   Use Cases & Deep Dive
●  Q&A


      3

## Page 4

    Evolution: Running applications


   Dark Age:      Microservices
Single tasking    Multi tasking    Virtualization    Containers


    The simple age.     Split the CPU and      Ship the OS together      Back to a shared
                        memory. Shared         with application and run  operating system.
                        libraries, package     it in a VM for better     Applications directly
                        management, Linux      resource isolation.       interact with the host
                        distributions.         Virtualized hardware      operating system again.
                                               and software defined
                                               infrastructure.


                                               4

## Page 5

Problems of the
Linux Kernel in the
age of microservices

        5

## Page 6

Problem #1: Abstractions

Process    Process             The Linux kernel is split into layers to
System Call Interface          provide strong abstractions.
    Sockets                    Pros:
TCP      UDP   Raw             ●     Strong userspace API compatibility
Netfilter                            guarantee. A 20 years old binary still
IPv4      IPv6                       works.
                               ●     Majority of Linux source code is not
    Ethernet                         hardware specific.
    Traffic Shaping
Netdevice / Drivers      Cons:
                               ●     Every layer pays the cost of the
HW     Bridge     OVS    ..          layers above and below.
                               ●     Very hard to bypass layers.
                                         6

## Page 7

Problem #2: Per subsystem APIs
ethtool ip    Process    Process  seccomp iptables tc tcpdump  brctl /
    System Call Interface                                      ovsctl
    Sockets
    TCP     UDP     Raw
    Netfilter
    IPv4     IPv6
    Ethernet
    Traffic Shaping
    Netdevice / Drivers
    HW     Bridge     OVS     ..

                                                                   7

## Page 8

Problem #3: Development Process

The Good:        The Bad:
●     Open and transparent process      ●     Hard to change
●     Excellent code quality            ●     Shouting is involved (getting better)
●     Stability                         ●     Large and complicated codebase
●     Available everywhere              ●     Upstreaming code is hard, consensus has to
●     Almost entirely vendor neutral          be found.
                                        ●     Upstreaming is time consuming
                                        ●     Depending on the Linux distribution,
                                              merged code can take years to become
                                              generally available
                                        ●     Everybody maintains forks with 100-1000s
                                              backports


                                              8

## Page 9

    Problem #4: What is a container?
    What the kernel knows about:      What the kernel does not know:
    ●     Processes & thread groups                   ●  Containers or Kubernetes pods
    ●     Cgroups                                        ○     There is no container ID in the kernel
         ○     Limits and accounting of CPU,          ●  Exposure requirements
               memory, network, … Configured by          ○     The kernel no longer knows whether
               container runtime.                              an application should be exposed
    ●     Namespaces                                           outside of the host or not.
         ○     Isolation of process, CPU, mount,      ●  API calls made between containers/pods
               user, network, IPC, cgroup, UTS           ○     Awareness stops at layer 4 (ports).
               (hostname). Configured by container             While SELinux can control IPC, it can’t
         ○     runtime                                         control service to service API calls.
    ●     IP addresses & port numbers                 ●  Servicemesh, huh?
         ○     Configured by container networking
    ●     System calls made & SELinux context
         ○     Optionally configured by container
               runtime
9

## Page 10

    What now? Alternatives?

  Give user     Move OS to    Rewrite
space access    Unikernel    Userspace    Everything?
 to hardware


    Expose the hardware         Linus was wrong. The       We don’t need kernel         Total Estimated Cost
    directly to user space.     app should provide its     mode for most of the         to Develop Linux
    It will be fine.            own OS.                    logic. Build on top of a     (average salary =
                                                           minimal Linux.               $75,662.08/year,
                                                                                        overhead = 2.40).
    Examples: DPDK,      Examples: ClickOS,                Examples: User mode          $1,372,340,206
    UDMA, ..        MirageOS, Rumprun, ...                 Linux, gVisor, ...

10

## Page 11

    What is     BPF?
    Highly efficient sandboxed
    virtual machine in the Linux
    kernel making the Linux kernel
    programmable at native
    execution speed.                 $ clang -target bpf -emit-llvm -S \
                                     32-bit-example.c
    Jointly maintained by Cilium     $ llc -march=bpf 32-bit-example.ll
                                     $ cat 32-bit-example.s
    and Facebook with                cal:
                                     r1 = *(u32 *)(r1 + 0)
    collaborations from Google,      r2 = *(u32 *)(r2 + 0)
    Red Hat, Netflix, Netronome,     r2 += r1
                                     *(u32 *)(r3 + 0) = r2
    and many others.                 exit
11

## Page 12

The Linux kernel is event driven

Process   Process Process     Process
              System calls
          System Call Interface

    12M lines of source code


          Drivers    Interrupts

CPU  RAM  MMU  NIC   Disk  Disk  USB

              12

## Page 13

Run BPF program on event

Process        Process        Attachment points
                                       ●  Kernel functions (kprobes)
    BPF        BPF                     ●  Userspace functions (uprobe)
                                       ●  System calls
File Descriptor    TCP    Sockets      ●  Tracepoints
               retrans                 ●  Network devices (packet level)
VFS        TCP/IP                      ●  Sockets (data level)
Block Device        Network Device     ●  Network device (DMA level) [XDP]
IO                                     ●  ...
Readread()        connect() Send
    networkpacket

    BPF        BPF

Disk        NIC
                                           13










BPF

## Page 14

BPF Maps
    BPF map use cases:
                ●  Hold program state
    Process     ●  Share state between programs
                ●  Share state with user space
                ●  Export metrics & statistics
                ●  Configure programs
BPF
    Map types:
BPF    Maps     ●  Hash tables
                ●  Arrays
                ●  LRU (Least recently used)
                ●  Ring buffer
                ●  Stack trace
                ●  LPM (Longest prefix match)

                    14

## Page 15

BPF Helpers

    BPF helpers:
       bpf_get_prandom_u32()      ●     Stable kernel API exposed to BPF
BPF    bpf_skb_store_bytes()            programs to interact with the kernel
                                  ●     Includes ability to:
    bpf_redirect()                     ○     Get process/cgroup context
    bpf_get_current_pid_tgid()         ○     Manipulate network packets
                                             and forwarding
    bpf_perf_event_output()            ○     Access BPF maps
                                       ○     Access socket data
                                       ○     Send metrics to user space
                                       ○     ...





                                             15

## Page 16

BPF Tail Calls

                   BPF tail calls:
       BPF     BPF     ●  Chain logical programs together
                       ●  Implement function calls
BPF                    ●  Must be within same program type
       BPF     BPF








                       16

## Page 17

BPF JIT Compiler

Byte    generic         JIT Compiler
code                              ●     Ensures native execution
                                        performance without requiring to
                                        understand CPU
                                  ●     Compiles BPF bytecode to CPU
Byte    generic     Bytex86_64          architecture specific instruction set
code    JIT         code
                        Supported architectures:
                                  ●     X86_64, arm64, ppc64, s390x, mips64,
                                        sparc64, arm

                                            17

## Page 18

BPF Contributors

380 Daniel Borkmann (Cilium, Maintainer)
161 Alexei Starovoitov (Facebook, Maintainer)     Top contributors of
160 Jakub Kicinski Netronome                      the total 186
110 John Fastabend (Cilium)                       contributors to BPF
96 Yonghong Song (Facebook)                       from January 2016 to
95 Martin KaFai Lau (Facebook)                    November 2018.
94 Jesper Dangaard Brouer (Red Hat)
74 Quentin Monnet (Netronome)
45 Roman Gushchin (Facebook)
45 Andrey Ignatov (Facebook)


                                                  18

## Page 19

BPF Use Cases

●     L3-L4 Load balancing      ●     Replacing iptables with BPF
●     Network security                (bpfilter)
●     Traffic optimization      ●     NFV & Load balancing (XDP)
●     Profiling                 ●     Profiling & Tracing

      https://code.fb.com/open-s
      ource/linux/


●  QoS & Traffic optimization    ●    Performance
●  Network Security                 Troubleshooting
●  Profiling                     ●    Tracing & Systems Monitoring
                                 ●    Networking


                                      19

## Page 20

Simple Kprobe Example

Example: BPF program using gobpf/bcc:










20

## Page 21

What is Cilium?
Cilium is open source software for transparently
providing and securing the network and API
connectivity between application services deployed
using Linux container management platforms like
Kubernetes, Docker, and Mesos.

At the foundation of Cilium is the new Linux kernel
technology BPF, which enables the dynamic insertion
of powerful security, visibility, and networking control
logic within Linux itself. Besides providing traditional
network level security, the flexibility of BPF enables
security on API and process level to secure
communication within a container or pod.
Read More


21

## Page 22

Project Goals

Approachable BPF        Security
●     Make the efficiency and flexibility of BPF      ●     Use the additional visibility of BPF to
      available in an approachable way                      provide security for microservices
●     Automate program creation and                         including:
      management                                           ○     API awareness
●     Provide an extendable platform                       ○     Identity based enforcement
                                                           ○     Process level context enforcement
Microservices-aware Linux        Performance
●     Use the flexibility of BPF to make the Linux          Leverage the execution performance and
      kernel aware of cloud native concepts        ●
      such as containers and APIs.                          JIT compiler to provide a highly efficient
                                                            implementation.


                                                                 22

## Page 23

Cilium Use Cases

Container Networking        Microservices Security
●     Highly efficient and flexible            ●     Identity-based L3-L4 network security
      networking                               ●     Accelerated API-aware security via
●     CNI and CMM plugins                            Envoy (HTTP, gRPC, Kafka, Cassandra,
●     IPv4, IPv6, NAT46, direct routing,             memcached, ..)
      encapsulation                            ●     DNS aware policies
●     Multi cluster routing                    ●     SSL data visibility via kTLS

Service Load balancing:        Servicemesh acceleration:
●     Highly scalable L3-L4 load balancing     ●     Minimize overhead when injecting
      implementation                                 servicemesh sidecar proxies
●     Kubernetes service implementation or
      API driven.

                                                         23

## Page 24

BPF-based servicemesh
Acceleration    How it really looks:

Service    Service
Container    Container

Sidecar proxy    Sidecar proxy








24

## Page 25

BPF-based servicemesh
Acceleration      ~3.5x performance improvement

Accelerate the service to
sidecar communication










25

## Page 26

Other BPF projects

Tracing / Profiling:                              Load balancing:
●     BPFTrace - DTrace for Linux (Brendan        ●     Katran - Source code of Facebook’s
      Gregg, et al.)                                    primary L3-L4 LB (Facebook team)
●     bpfd - Load BPF programs into entire        Security:
      clusters (Joel Fernandes, Google)
Frameworks:                                       ●     Seccomp - Advanced BPF version of
                                                        Seccomp (Kernel team)
●     gobpf - Go based framework to write BPF     DDoS mitigation:
      programs
●     BCC - Python framework to write BPF         ●     bpftools - DDOS mitigation tool with
      programs                                          iptables like syntax (Cloudflare)

                                                  … and many more

                                                            26

## Page 27

Thank you!

Source Code:
https://github.com/cilium/cilium
BPF reference guide:
http://docs.cilium.io/en/stable/bpf/
Twitter:
@ciliumproject
Website:
https://cilium.io/

## Related pages

- 

## Source

- Local path: `[[papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf]]`
