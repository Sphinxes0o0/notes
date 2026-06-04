---
type: source
source-type: book
title: "Beginners_guide_to_eBPF_programming_for_networking"
path: books/Beginners_guide_to_eBPF_programming_for_networking.pdf
source-md5: 15f1e587e801356c25a822be862a075a
size: 1026 KB
category: book
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# Beginners_guide_to_eBPF_programming_for_networking

> Ingested from `books/Beginners_guide_to_eBPF_programming_for_networking.pdf` via `lit parse` on 2026-06-04.
> Source file: 1.0 MB.

## Page 1

A Beginner’s Guide to eBPF
Programming for networking
Liz Rice
Chief Open Source Officer, Isovalent
@lizrice

## Page 2

eBPF lets you run custom code in the kernel



  @lizrice

## Page 3

Attaching eBPF to events

eBPF programs  are  event-driven and are run when the kernel
or an application   passes a certain hook point. Pre-defined
hooks include system calls,  function entry/exit, kernel
tracepoints, network events, and  several others.






 @lizrice           ebpf.io/what-is-ebpf/

## Page 4

eBPF Hello World

    userspace
    app

    execve()
syscalls
    kernel

    event     “Hello world”



@lizrice

## Page 5

eBPF     Hello    World
SEC("kprobe/sys_execve")
int  hello(void *ctx)
{                              + userspace code to load eBPF
     bpf_printk("I'm alive!");   program
     return 0;
}                       Info about process that
$ sudo ./hello          called execve syscall
   bash-20241                 84210.752785:
   bash-20242                 84216.321993:
   bash-20243     [004] d...  84225.858880: 0: I'm alive!

    @lizrice

## Page 6

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE_TRACEPOINT,        BPF_PROG_TYPE_SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full list. */
    };

@lizrice

## Page 7

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE     eBPF - not just for syscalls! _SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full  list. */
    };

@lizrice

## Page 8

@lizrice

## Page 9

Also, many perf events


sudo perf list



  @lizrice

## Page 10

Network events
(a very non-comprehensive guide)



  @lizrice

## Page 11

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE_TRACEPOINT,        BPF_PROG_TYPE_SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full list. */
    };

@lizrice

## Page 12

Kprobes / kretprobes

Entry to / exit from a kernel function
Lots of kernel functions relate to networking

example
tcp_v4_connect() kernel function




@lizrice

## Page 13

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE_TRACEPOINT,        BPF_PROG_TYPE_SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full list. */
    };

@lizrice

## Page 14

Socket filter
    userspace  App
syscalls
    kernel     Socket

    TCP/UDP/ICMP

    IP

    Qdisc

    Raw socket
    Network connection
@lizrice

## Page 15

    Socket filter



“The filtering actions include dropping packets (if the program returns 0) or trimming packets (if
the program returns a length less than the original). … Note that we're not trimming or dropping
the original packet which would still reach the intended socket intact; we're working with a copy
of the packet metadata which raw sockets can access for observability. “







    @lizrice    https://blogs.oracle.com/linux/post/bpf-a-tour-of-program-types

## Page 16

Socket filter

Network packet data copy
Filters what gets sent to userspace, for performant observability

example
attach_raw_socket()




@lizrice

## Page 17

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE_TRACEPOINT,        BPF_PROG_TYPE_SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full list. */
    };

@lizrice

## Page 18

XDP Փ express data path

“What if we could run eBPF on the network interface card?”










@lizrice

## Page 19

    XDP  kernel

        network stack



NIC / driver
      packet  eBPF program
     arrives




    Physical network connection

    @lizrice

## Page 20

XDP  kernel
    network stack


                      packet eBPF program
                      arrives

Only some NICs /   NIC
drivers support XDP

    Physical network connection

@lizrice

## Page 21

    XDP  kernel
        network stack


    packet eBPF program
    arrives

eth0



    Virtual network connection

    @lizrice

## Page 22

XDP Փ express data path

Inbound packets
Pass / drop / manipulate / redirect packets

example
attach_xdp()




@lizrice

## Page 23

Program types

enum bpf_prog_type {
BPF_PROG_TYPE_UNSPEC,            BPF_PROG_TYPE_LWT_OUT,
BPF_PROG_TYPE_SOCKET_FILTER,     BPF_PROG_TYPE_LWT_XMIT,
BPF_PROG_TYPE_KPROBE,            BPF_PROG_TYPE_SOCK_OPS,
BPF_PROG_TYPE_SCHED_CLS,         BPF_PROG_TYPE_SK_SKB,
BPF_PROG_TYPE_SCHED_ACT,         BPF_PROG_TYPE_CGROUP_DEVICE,
BPF_PROG_TYPE_TRACEPOINT,        BPF_PROG_TYPE_SK_MSG,
BPF_PROG_TYPE_XDP,               BPF_PROG_TYPE_RAW_TRACEPOINT,
BPF_PROG_TYPE_PERF_EVENT,        BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
BPF_PROG_TYPE_CGROUP_SKB,        BPF_PROG_TYPE_LWT_SEG6LOCAL,
BPF_PROG_TYPE_CGROUP_SOCK,       BPF_PROG_TYPE_LIRC_MODE2,
BPF_PROG_TYPE_LWT_IN,            BPF_PROG_TYPE_SK_REUSEPORT,
                                 BPF_PROG_TYPE_FLOW_DISSECTOR,
                                 /* See   /usr/include/linux/bpf.h for
                                     the  full list. */
    };

@lizrice

## Page 24

Traffic control  (ingress)
                 userspace  App
syscalls
                 kernel     Socket

                     TCP/UDP/ICMP

                     IP

                     Qdisc

                     Raw socket
    Network connection
@lizrice

## Page 25

Traffic control

Traffic filters, attached to queueing disciplines
Ingress / egress (separately)
Pass / drop / manipulate / redirect packets
example
tc(“add-filter)




@lizrice

## Page 26

Traffic control ingress - ping reply
            userspace  App
    syscalls
            kernel     Socket

                TCP/UDP/ICMP

                IP

                Qdisc

                Raw socket
    Network connection
    @lizrice

## Page 27

   Fewer perf events using TC pingpong


sudo perf trace -e “net:*” ping -c1 <addr>





    @lizrice

## Page 28

eBPF networking
enables efficiency & high performance



  @lizrice

## Page 29

        pod                  app
                         iptables INPUT socket

Linux routing
  iptables
 PREROUTING                             veth
   mangle

    iptables
    conntrack    iptables
        conntrack                       veth
  iptables    iptables       iptables
   FORWARD   POSTROUTING     POSTROUTING
               mangle                   nat

Linux routing
  iptables    iptables
 PREROUTING  PREROUTING
     nat       mangle
    host                     eth0
    @lizrice

## Page 30

    pod           app
              iptables INPUT socket

    iptables  Linux routing
    conntrack
 iptables
PREROUTING                   veth
  mangle

                             veth


    Linux routing


    host      eth0
    @lizrice

## Page 31

eBPF can instrument apps
without any app or config changes



 @lizrice

## Page 32

A sidecar has a view across
one pod    userspace
     pod
     container     container sidecar



@lizrice

## Page 33

Sidecars     need     YAML
containers:  my-app.yaml    userspace
-     name:  my-app        pod
      ...
-     name:  my-app-init    container  container  sidecar
      …
-     name: my-sidecar
      ...





@lizrice

## Page 34

eBPF does not need app changes
    containers:  my-app.yaml    userspace
    -     name:  my-app        pod
          ...
    -     name:  my-app-init    container  container
          …

                     kernel




    @lizrice

## Page 35

eBPF-enabled networking capabilities

Inspect packets → Observability
Identity-aware data flows, message parsing, security forensics...
Drop or modify packets → Security
Network policies, encryption...
Redirect packets → Networking functions
Load balancing, routing, service mesh...

@lizrice

## Page 36

eBPF enables next-gen service mesh
high performance
without any app or config changes


   @lizrice

## Page 37

Thank you
github.com/lizrice/ebpf-beginners
ebpf.io | cilium.io | isovalent.com



    @lizrice

## Related pages

- [[linux-ebpf-fundamentals]]

## Source

- Local path: `[[books/Beginners_guide_to_eBPF_programming_for_networking.pdf]]`

- [[entities/linux/ebpf/ebpf-networking]]
