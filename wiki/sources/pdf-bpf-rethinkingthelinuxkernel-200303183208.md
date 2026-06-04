---
type: source
source-type: pdf
title: "bpf-rethinkingthelinuxkernel-200303183208"
path: papers/bpf-rethinkingthelinuxkernel-200303183208.pdf
size: 2807 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# bpf-rethinkingthelinuxkernel-200303183208

> Ingested from `papers/bpf-rethinkingthelinuxkernel-200303183208.pdf` via `lit parse` on 2026-06-04.
> Source file: 2.74 MB.

## Page 1

Rethinking the
Linux kernel
Thomas Graf
Cilium Project, Co-Founder & CTO, Isovalent

## Page 2

Remember
GeoCities?



Cameron Askin: Cameron’s World    2

## Page 3

What enabled this evolution?








Markup Only (HTML)    Programmable Platform



3

## Page 4

Programmability Essentials
    Safety              Continuous                Performance
                                    Delivery
Untrusted code runs     Allow evolution of        Programmability must
in the browser of the   logic without requiring   be provided with
user.                   to constantly ship new    minimal overhead.
                        browser versions.
→ Sandboxing                                      → Native Execution
                        → Deploy anytime with     (JIT compiler)
                        seamless upgrades

                                                      4

## Page 5

    Kernel Architecture


    Process        Admin    Process

    write()       read()    sendmsg()  recvmsg()
    Syscall        Configuration    Syscall
        (sysfs,netlink,procfs,...)

    L    File Descriptor            Sockets
    inux
    User
    H
    W
        Kerne
        l
        Sp
        ace  VFS                     TCP/IP
        Block Device        Network Device



 Storage     Network
Hardware    Hardware
        5

## Page 6

       Kernel Development 101

Option 1                          Option 2
Native Support                    Kernel Module
●  Change kernel source code       ●   Write kernel module
●  Expose configuration API        ●   Every kernel release will break it
●  Wait 5 years for your users    Cons:
   to upgrade                     ●  You likely need to ship a different
Cons:                                module for each kernel version
                                  ●  Might crash your kernel




                                       6

## Page 7

    How about we add
JavaScript-like capabilities
    to the Linux Kernel?

        7

## Page 8

8

## Page 9

Linux
Kernel










    Process
    execve()
    Syscall


    Scheduler










    9

## Page 10

    eBPF Runtime

    Controller                                     Process
                                  bytecode
    bpf()                          BPF
                                   Program         sendmsg()      recvmsg()
                       Syscall                     Syscall

                       Verifier                    Sockets
L                          approved
inuxKerne
    l                              BPF        x86_64        TCP/IP
                                   Program     BPF        Network Device
                                               Program
                                  JIT Compiler

Safety & Security                      Continuous Delivery             Performance
The verifier will reject any           Programs can be exchanged       The JIT compiler ensures
unsafe program and                     without disrupting workloads.   native execution
provides a sandbox.                                                    performance.
                                                                           10

## Page 11

    eBPF Hooks

    Process        Process

    write()  read()    sendmsg()  recvmsg()
    Syscall                Syscall

    File Descriptor        Sockets
    VFS                     TCP/IP
    Block Device       Network Device



                 Storage     Network
                Hardware    Hardware

    Where can you hook? kernel functions (kprobes), userspace functions (uprobes), system calls,
    fentry/fexit, tracepoints, network devices (tc/xdp), network routes, TCP congestion algorithms,  11
    sockets (data level)










Linux
Kernel

## Page 12

    eBPF Maps

    Controller      Admin        Process

    sendmsg()     recvmsg()
    Syscall        Syscall        Syscall

L        Sockets
inuxKerne
l
                             Map        TCP/IP
    Network Device

Map Types:        What are Maps used for?
- Hash tables, Arrays              ●    Program state
- LRU (Least Recently Used)        ●    Program configuration
- Ring Buffer                      ●    Share data between programs
- Stack Trace                      ●    Share state, metrics, and
- LPM (Longest Prefix match)        statistics with user space     12

## Page 13

           eBPF Helpers

               Process

               sendmsg()     recvmsg()
                                                          Syscall

L                                                         Sockets
inux Kerne
    l     [...]                                            TCP/IP
          num = bpf_get_prandom_u32();
          [...]        Network Device

What helpers exist?
     ●     Random numbers                  ●    Access socket data
     ●     Get current time                ●    Perform tail call
     ●     Map access                      ●    Access process stack
     ●     Get process/cgroup context      ●    Access syscall arguments
     ●     Manipulate network packets and  ●    ...        13
           forwarding

## Page 14

eBPF Tail and Function Calls


L
inuxKerne
 l



What are Tail Calls used for?        What are Functions Calls used for?
●     Chain programs together          ●     Reuse functionality inside of a
●     Split programs into independent        program
      logical components               ●     Reduce program size (avoid
●     Make BPF programs composable           inlining)



                                             14

## Page 15

    Community

287 contributors:
(Jan 2016 to Jan 2020)

●  466 Daniel Borkmann (Cilium; maintainer)
●  290 Andrii Nakryiko (Facebook)
●  279 Alexei Starovoitov (Facebook; maintainer)
●  217 Jakub Kicinski (Facebook)
●  173 Yonghong Song (Facebook)
●  168 Martin KaFai Lau (Facebook)
●  159 Stanislav Fomichev (Google)
●  148 Quentin Monnet (Cilium)
●  148 John Fastabend (Cilium)
●  118 Jesper Dangaard Brouer (Red Hat)
●  [...]
    15

## Page 16

    eBPF Projects

Katran                     Cilium                             bcc, bpftrace
High-performance L4        Networking, security and  et al.   Performance
Loadbalancer               load-balancing for k8s             troubleshooting &
facebookincubator/katran   cilium/cilium                      profiling
                                                              iovisor/bcc

Android & Security         Traffic Optimization               Falco
kernel runtime security    DDoS mitigation, QoS,              Container runtime
instrumentation (KRSI),    traffic optimization,              security, behavior
Android BPF loader,        load balancer                      analysis
eBPF traffic monitor       cloudflare/bpftools                falcosecurity/falco


                                                              16

## Page 17

     Tracing & Profiling with

             Python
                          BPF
                          Program              Process
             BCC                           sendmsg()     recvmsg()
         Syscall                               Syscall
         Verifier             BPF              Sockets
L                             Maps
inuxKerne
    l    JIT Compiler                          TCP/IP

                          # tcptop
                          Tracing...    Output every 1 secs. Hit Ctrl-C to end
 BCC:                     <screen clears>
 github.com/iovisor/bcc   19:46:24 loadavg: 1.86 2.67 2.91 3/362 16681
                          PID       COMM   LADDR             RADDR                    RX_KB TX_KB
                          16648 16648                                                      1    0
                          16647 sshd                                          .165:6684      2149
                          14374 sshd                                          .165:25219
                          14458 sshd       100.66.3.172:22   100.127.69.165:7165           0    0  17

## Page 18

bpftrace - DTrace for Linux

                         bpftrace
                         Program     Process
         bpftrace                    open()
         Syscall                     Syscall
         Verifier            BPF     File Descriptors
L                            Maps
inuxKerne
    l    JIT Compiler                VFS


bpftrace:                     # bpftrace -e 'kprobe:do_sys_open { printf("%s: %s\n", comm, str(arg1)) }'
github.com/iovisor/bpftrace   Attaching 1 probe...
                                    .git/objects/da
                              git:  .git/objects/pack
                              git: /etc/localtime
                              systemd-journal: /var/log/journal/72d0774c88dc4943ae3d34ac356125dd
                              DNS Res~ver #15: /etc/hosts
                              ^C         18

## Page 19

Linux
Kernel










    Networking, load-balancing
    and security for Kubernetes

    Kubernetes

    Clium        Container    Container

    Syscall        Syscall        Syscall
    Verifier        BPF    Sockets        Sockets
        Maps
    JIT Compiler        TCP/IP        TCP/IP
        Network Device      Network Device

                               Network
                              Hardware        19

## Page 20

Container Networking        Container Security
●     Highly efficient and flexible networking     ●     Identity-based network security
●     Routing, Overlay, Cloud-provider native      ●     API-aware security (HTTP, gRPC, Kafka,
●     IPv4, IPv6, NAT46                                  Cassandra, memcached, ..)
●     Multi cluster routing                        ●     DNS-aware policies
                                                   ●     Encryption
Service Load balancing:                            ●     SSL data visibility via kTLS
●     Highly scalable L3-L4 load balancing        Visibility
●     Kubernetes services (replaces                      Service topology map & live visualization
      kube-proxy)                                  ●
●     Multi-cluster                                ●     Advanced network metrics & alerting
●     Service affinity (prefer zones)
          Servicemesh:
                                                   ●     Minimize overhead when injecting
                                                         servicemesh sidecar proxies
                                                   ●     Istio integration        20

## Page 21

    Hubble: eBPF Visibility for Kubernetes










# hubble observe --since=1m -t l7 -j \
   | jq 'select(.l7.dns.rcode==3) | .destination.namespace + "/" + .destination.pod_name' \
   | sort | uniq -c | sort -r
  42 "starwars/jar-jar-binks-6f5847c97c-qmggv"
        21

## Page 22

Go Development Toolchain

C source        bytecode
BPF                  BPF
Program         Program

clang -target bpf        Program Maps Process
Development

                Go Library sendmsg() recvmsg()
            Syscall Syscall

                                              BPF
L           Verifier                          Map Sockets
inux Kerne
    l     JIT Compiler TCP/IP

Runtime

Go Library: https://github.com/cilium/ebpf 22

## Page 23

              Outlook: Future of

              is turning the Linux                            could enable the Linux kernel
    kernel into a microkernel.        hotpatching we always dreamed about.

    ●     An increasing amount of new kernel        Problem:
          functionality is implemented with eBPF.       ●     Linux kernel vulnerability requires to
    ●     100% modular and composable.                        patch kernel.
    ●     New additions can evolve at a rapid pace.     ●     Rebooting 20’000 servers takes a very
          Much quicker than normal kernel                     long time without risking extensive
          development.                                        downtime.

    Example: The linux kernel is not aware of                  Function
    containers and microservices (it only knows        L
                  inuxKerne
    about namespaces).    Cilium is making the              l  Function Hotfix
    Linux kernel container and    Kubernetes
    aware.                                                     Function
23

## Page 24

Thank You
eBPF Maintainers
Daniel Borkmann, Alexei Starovoitov
Cilium Team
André Martins, Jarno Rajahalme, Joe Stringer,
John Fastabend, Maciej Kwiek, Martynas
Pumputis, Paul Chaignon, Quentin Monnet,
Ray Bejjani, Tobias Klauser
Facebook Team
Andrii Nakryiko, Andrey Ignatov, Jakub
Kicinski, Martin KaFai Lau, Roman Gushchin,     ●  BPF Getting Started Guide
Song Liu, Yonghong Song
Google Team                                        BPF and XDP Reference Guide
Chenbo Feng, KP Singh, Lorenzo Colitti,         ●  Cilium
Maciej Żenczykowski, Stanislav Fomichev,           github.com/cilium/cilium
BCC & bpftrace
Alastair Robertson, Brendan Gregg, Brenden      ●  Twitter
Blanco
Kernel Team                                        @ciliumproject
Björn Töpel, David S. Miller, Edward Cree,      ●  Contact the speaker
Jesper Brouer, Toke Høiland-Jørgensen              @tgraf__
                                                   All images: Pixabay      24

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[papers/bpf-rethinkingthelinuxkernel-200303183208.pdf]]`
