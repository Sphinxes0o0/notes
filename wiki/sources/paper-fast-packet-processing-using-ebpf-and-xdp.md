---
type: source
source-type: pdf
title: "Fast-Packet-Processing-using-eBPF-and-XDP"
path: papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf
size: 1402 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# Fast-Packet-Processing-using-eBPF-and-XDP

> Ingested from `papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf` via `lit parse` on 2026-06-04.
> Source file: 1.37 MB.

## Page 1

Fast Packet Processing using
eBPF and XDP
Prof. Marcos A. M. Vieira
mmvieira@dcc.ufmg.br
DCC - UFMG
EVComp 2020

## Page 2

Who is already using eBPF?

June 2018, Layer 4 Load Balancing at Facebook
Katran
https://github.com/facebookincubator/katran/

February 2018, BPF comes through firewalls
https://lwn.net/Articles/747551/
https://lwn.net/Articles/747504/
https://www.netronome.com/blog/frnog-30-faster-networking-la-francaise/

March 2018, Introducing AF_XDP support (to bring packets from
NIC driver directly to userspace)
https://lwn.net/Articles/750293/
http://mails.dpdk.org/archives/dev/2018-March/092164.html
https://twitter.com/DPDKProject/status/1004020084308836357
      April 2018, Add examples of ipv4 and ipv6 forwarding
      in XDP (to exploit the Linux routing table to forward
      packets in eBPF)
      https://patchwork.ozlabs.org/patch/904674/

## Page 3

       Tcpdump

•  Packet analyzer
•  Original use-case: tcpdump filter for raw
   packet sockets
•  Libpcap: captures packets
•  Might apply BPF-filter

## Page 4

Mr. Robot - tcpdump

## Page 5

Berkeley Packet Filter (BPF)

                                                            Linux
       • Generic in-kernel, event-based                     server User space
virtual CPU                                           User                   User
• Introduced in Linux kernel 2.1.75               Application (e.g.,  Application (e.g.,
(1997)                                            web browser)            Wireshark)
• Initially used as packet filter by
packet capture tool tcpdump (via                                      Libpcap + in-kernel
libpcap)                                          TCP/IP               components(e.g.,
                                                  stack                  buffers)
• In-kernel
• No syscalls overhead, kernel/user        Network
context switching                          Tap                        BPF
• Event-based                                  Network Interface Card
                                                      (NIC) driver           Linux
• Network packets                                                           kernel
• Virtual CPU

                                                                      5

## Page 6

  What is Berkeley Packet Filter (BPF)?

• tcpdump -i eno1 –d IPv4_TCP_packet

ldh [12]
jne #0x800, drop
ldb [23]
jneq #6, drop
ret #-1
drop: ret #0

## Page 7

BPF vs. eBPF machines










    • Number of registers increase from 2 to 11
    • Register width increases from 32-bit to 64-bit
    • Conditional jt/jf targets replaced with jt/fall-through

    • 11 64-bit registers, 512 bytes stack
    • Instructions 64-bit wide

## Page 8

        eBPF Instruction Set

• 7 classes:
• BPF_LD, BPF_LDX: hold instructions for byte /
  half-word / word / double-word load operations.
• BPF_ST, BPF_STX: Both classes are for store
  operations.
• BPF_ALU: ALU operations in 32 bit mode
• BPF_ALU64: ALU operations in 64 bit mode.
• BPF_JMP: This class is dedicated to jump
  operations. Jumps can be unconditional and
  conditional.

## Page 9

        eBPF Bytecode

    64-bit, 2 operand BPF bytecode instructions are split as follows

          op:8        dst_reg:4  src_reg:4  off:16      imm:32
BPF_JNE | BPF_K | BPF_JMP  0x1    0x0       0x001   0x00000800







    ALU/JMP                                         LD/STO

 operation:4  source:1  insn_class:3     mode:3     size:2  insn_class:3

  BPF_JNE     BPF_K     BPF_JMP          BPF_H     BPF_ABS  BPF_LD






                                                    9

## Page 10

       eBPF Registers

•  R0 : return value from function, and exit value
   for eBPF program
•  R1 - R5 : arguments from eBPF program
   function
•  R6 - R9 : callee saved registers that function
   preserve
•  R10 - read-only frame pointer to access stack

## Page 11

Workflow



Go    P4

## Page 12

        Restricted C for eBPF

• BPF has slightly different environment for C
• Subset of libraries (e.g. No printf())
• Helper functions and program context available
• Library functions all get inlined, no notion of function calls
   (yet)
• No global variables (use Maps)
• No loops (yet) unless unrolled by pragma or w/o verifier
• No const strings or data structures
• LLVM built-in functions usually available and inlined
• Partitioning processing path with tail calls
• Limited stack space up to 512 bytes

## Page 13

 Hooks




•  Code that handles intercepted function calls,
   events or messages between software
   components.
•  Allows for user space applications to bypass
   the networking stack

## Page 14

Hooks

## Page 15

    What is XDP?
                                                                   TCP Stack   Intended  Redirect
XDP allows packets to be reflected, filtered or redirected             socket            socket
                                                                   Netfilter (1 Mpps)
without traversing networking stack
▶ eBPF programs classify/modify traffic and return
XDP actions                                                        TC (5Mpps)
Note: cls_bpf in TC works in same manner          Kernel Space
▶ XDP Actions                                     Driver Space     XDP (20Mpps)
• XDP_PASS                                                                           XDP_DROP
• XDP_DROP                                                         XDP_PASS
• XDP_TX
• XDP_REDIRECT                                                         XDP
• XDP_ABORT - Something went wrong                                     Actions
▶ Currently hooks onto RX path only                                XDP_TX    Return      XDP_REDIRECT
                                                                               XDP
• Other hooks can also work on TX                                            action

                                                                       eBPF



                                                                   RX port           Redirect
                                                                                         port



1
5

## Page 16

    XDP Actions

    Register 0 denotes the return value


Value Action Description

 0 XDP_ABORTED Error, Block the packet

 1 XDP_DROP Block the packet

 2 XDP_PASS Allow packet to continue up to the
        kernel
 3 XDP_TX Bounce the packet







    10

## Page 17

 Hook example

• 1) Write C code:


• 2) Compile to target BPF

• Object
generated:

## Page 18

  Hook example (2)

• 3) Load hook:

• Status:




• 4) Unload:

## Page 19

XDP Offload


Core 1  Core 2

Core 3 Core 4


               eBPF
               running on
               Driver (XDP)
               Linux Kernel

               User Space

Network packets

## Page 20

  Hook example (3) - Offload

• 3) Offload:

• Status:




• 4) Unload:

## Page 21

         eBPF example

     Drop packets not EtherType 0x2222

#include <linux/bpf.h>
#include "bpf_api.h"
#include "bpf_helpers.h"
                                                      Clang Compiler
SEC(“xdp_prog1”)
int xdp_prog1(struct xdp_md *xdp)
{        xdp_prog1:
     unsigned char *data;                             0:       b7 00 00 00 00 00 00 00     r0 = 0
                                                      1:       61 12 04 00 00 00 00 00     r2 = *(u32 *)(r1 + 4)
                                                      2:       61 11 00 00 00 00 00 00     r1 = *(u32 *)(r1 + 0)
     data = (void *)(unsigned long)xdp->data;         3:       bf 13 00 00 00 00 00 00     r3 = r1
     if (data + 14 > (void *)(long)xdp->data_end)     4:       07 03 00 00 0e 00 00 00     r3 += 14
         return XDP_ABORTED;
                                                      5:       2d 23 07 00 00 00           if r3 > r2
     if (data[12] != 0x22 || data[13] != 0x22)        6:       00 00
         return XDP_DROP;                                                                  goto 7 r0 =
                                                               b7 00 00 00 01 00           1
                                                               00 00
     return XDP_PASS;                                 7:       71 12 0c 00 00 00           r2 = *(u8 *)(r1
}                                                     8:       00 00                       + 12) if r2 !=
                                                         10:   b7 00 00 00 02 00 00 00
                                                         11:   55 02 04 00 22 00           34 goto 4
                                                         12:   00 00                       r0 = 1
                                                      9:       71 11 0d 00 00 00           r1 = *(u8 *)(r1
                                                               00 00                       + 13)
         LBB0_4:
                                                         13:   95 00 00 00 00 00 00 00     exit


     © 2018 NETRONOME SYSTEMS, INC.

## Page 22

         Maps
Maps are key-value stores used to store state
         ▶ Up to 128 maps per program                                  Key       Value
 ▶ Infinite size
 ▶ Multiple different types-Non XDP                                    0         10.0.0.1
 -   BPF_MAP_TYPE_HASH              -    BPF_MAP_TYPE_LRU_HASH              19   10.0.0.6
 -   BPF_MAP_TYPE_ARRAY             -    BPF_MAP_TYPE_LRU_PERCPU_HASH       91   10.0.1.1
 -   BPF_MAP_TYPE_PROG_ARRAY        -    BPF_MAP_TYPE_LPM_TRIE
 -   BPF_MAP_TYPE_PERF_EVENT_ARRAY  -    BPF_MAP_TYPE_ARRAY_OF_MAPS
 -   BPF_MAP_TYPE_PERCPU_HASH       -    BPF_MAP_TYPE_HASH_OF_MAPS     4121     121.0.0.1
 -   BPF_MAP_TYPE_PERCPU_ARRAY      -    BPF_MAP_TYPE_DEVMAP
 -   BPF_MAP_TYPE_STACK_TRACE       -    BPF_MAP_TYPE_SOCKMAP          12111     5.0.2.12
 -   BPF_MAP_TYPE_CGROUP_ARRAY      -    BPF_MAP_TYPE_CPUMAP           ...       ...

 ▶ Accessed via map helpers

## Page 23

        Maps types

• BPF_MAP_TYPE_HASH: a hash table
• BPF_MAP_TYPE_ARRAY: an array map, optimized for fast lookup speeds, often used for counters
• BPF_MAP_TYPE_PROG_ARRAY: an array of file descriptors corresponding to eBPF programs; used to
    implement jump tables and sub-programs to handle specific packet protocols
• BPF_MAP_TYPE_PERCPU_ARRAY: a per-CPU array, used to implement histograms of latency
• BPF_MAP_TYPE_PERF_EVENT_ARRAY: stores pointers to struct perf_event, used to read and store
    perf event counters
• BPF_MAP_TYPE_CGROUP_ARRAY: stores pointers to control groups
• BPF_MAP_TYPE_PERCPU_HASH: a per-CPU hash table
• BPF_MAP_TYPE_LRU_HASH: a hash table that only retains the most recently used items
• BPF_MAP_TYPE_LRU_PERCPU_HASH: a per-CPU hash table that only retains the most recently used
    items
• BPF_MAP_TYPE_LPM_TRIE: a longest-prefix match trie, good for matching IP addresses to a range
• BPF_MAP_TYPE_STACK_TRACE: stores stack traces
• BPF_MAP_TYPE_ARRAY_OF_MAPS: a map-in-map data structure
• BPF_MAP_TYPE_HASH_OF_MAPS: a map-in-map data structure
• BPF_MAP_TYPE_DEVICE_MAP: for storing and looking up network device references
• BPF_MAP_TYPE_SOCKET_MAP: stores and looks up sockets and allows socket redirection with BPF
    helper functions

## Page 24

      Maps

• The map is defined by:
  – Type
  – key size in bytes
  – value size in bytes
  – max number of elements

      Key (MAC address)                 Value (output
                                        port number)
                          0123456789AB   6
                          CAFEDEADFF     1
                          ...            ...

## Page 25

Helpers

   Helpers are used to add functionality that would otherwise be difficult
    ▶ Key XDP Map helpers
    -  bpf_map_lookup_elem
    -  bpf_map_update_elem
    -  bpf_map_delete_elem
    -  bpf_redirect_map
    ▶ Head Extend
    -  bpf_xdp_adjust_head
    -  bpf_xdp_adjust_meta
▶ Others
    -  bpf_ktime_get_ns
    -  bpf_trace_printk
    -  bpf_tail_call
    -  Bpf_redirect
   https://github.com/torvalds/linux/blob/master/include/uapi/linux/bpf.h

## Page 26

Bpftool    Open Source Tools
  ▶ Lists active bpf programs and maps
  ▶ Interactions with eBPF maps (lookups or updates)
  ▶ Dump assembly code (JIT and Pre-JIT)

Iproute2
  ▶ Can load and attach eBPF programs to TC, XDP or XDP offload (SmartNIC)

Libbpf
  ▶ BPF library allowing for user space program access to eBPF api

## Page 27

    Kernel Offload - Multi-Stage
        Processing
▶ Use of offloads does not preclude standard in-driver XDP use
▶ Offload some programs, leave some running on the host
▶ Maximize efficiency by playing to NFPs and host’s strengths
▶ Communication between programs via XDP/SKB metadata

## Page 28

Use Cases

   • Load Balacing
   • DDoS mitigation
   • Monitoring
   • Distributed Firewall
   • Intruction Detection System
   • NIC Behavior (Receive Side Scaling)

## Page 29

Projects





Layer      Hardware                    Software
NIC        Netronome                   XDP/Kernel
Switch     Developing a project with   BPFabric
           NetFPGA-SUME

## Page 30

    A Programmable Protocol-
Independent Hardware Switch with
  Dynamic Parsing, Matching, and
        Actions

## Page 31

    A Programmable Protocol-
Independent Hardware Switch with
  Dynamic Parsing, Matching, and
        Actions

## Page 32

      P4 limitations

• ▪P4-14 has some essential restrictions.
  – If-else statement can only be used in the control
  block.
  – It does not support for-loop.
  – It has only a limited set of primitive actions.

• P4 to eBPF
• https://github.com/iovisor/bcc/tree/master/src/cc/frontends/p4

## Page 33

  Why is eBPF cool?

• You can do whatever you want
  – E.g. sketches (telemetry)
  – Timers (Management)
• Program in C, P4
• Change in real-time

## Page 34

      Conclusions

• Fast (relatively) easy to use, potentially very powerful
  • Monitoring and (likely) network processing
• Many use cases
  • Packet filters (copy packet and pass to user space)
  • Used by tcpdump/libpcap, wireshark, nmap, dhcp, arpd, ...
  • In-kernel networking subsystems
  • cls_bpf (TC classifier) – QoS subsystem- , xt_bpf, ppp,...
  • seccomp (chrome sandboxing)
  • Introduced in 2012 to filter syscall arguments with bpf program
  • Tracing, Networking, Security, …
• Several “big names” here
• Need to enlarge the community, particularly with respect to
• end-users and application (e.g., non-kernel) developers


  53

## Page 35

Join us

• mmvieira@dcc.ufmg.br

## Page 36

Kernel Security and Stability
eBPF code injected into the kernel must be safe
▶ Potential risks
• Infinite loops could crash the kernel
• Buffer overflows
• Uninitialized variables
• Large programs may cause performance issues
• Compiler errors

## Page 37

    eBPF Verifier
The verifier checks for the validity of programs
▶ Ensure that no back edges (loops) exist
• Mitigated through the use #pragma unroll
▶ Ensure that the program has no more than 4,000 instructions
▶ There are also a number of other checks on the validity of register
usage
• These are done by traversing each path through the program
▶ If there are too many possible paths the program will also be rejected
• 1K branches
• 130K complexity of total instructions

## Page 38

    eBPF Verifier

The verifier checks for the DAG property     check_cfg()       0
▶ Ensures that no back edges (loops)
exist                                        Any program
▶ Backward jumps are allowed                 with a loop is    1
• Only if they do not cause loops            rejected
▶ Handled by check_cfg() in verifier.c

                                                 2        4





                                                 3        5





                                             6

## Page 39

    DAG


   #include <linux/bpf.h>                               xdp_prog1:
   #include "bpf_api.h"                                           r0 = 0
   #include "bpf_helpers.h"                                       r2 = *(u32 *)(r1
                                                        + 4)
   SEC(“xdp_prog1”)                                               r1 = *(u32 *)(r1
   int xdp_prog1(struct xdp_md *xdp)                    + 0)
   {                                                              r3 = r1
        unsigned char *data;                                      r3 += 14
                                                                  if r3 > r2 goto 7
        data = (void *)(unsigned long)xdp->data;                  r0 = 1
        if (data + 14 > (void *)(long)xdp->data_end)              r2 = *(u8 *)(r1 +
            return XDP_ABORTED;                         12)
                                                                  if r2 != 34 goto
        if (data[12] != 0x22 || data[13] != 0x22)       4
return XDP_DROP;                                                  r1 = *(u8 *)(r1 +
                                                        13)
        return XDP_PASS;                                          r0 = 2
   }                                                              if r1 == 34 goto
                                                        1
                                                                  r0 = 1





   DAG shown with bpftool and dot graph generator
    # bpftool prog dump xlated id 13 visual > cfg.txt
    # dot -Tps cfg.txt -o cfg.ps

## Page 40

  What is Berkeley Packet Filter (BPF)?

• tcpdump -i eno1 –ddd IPv4
12
40 0 0 12
21 0 2 2048
48 0 0 23
21 6 7 1
21 0 6 34525
48 0 0 20
21 3 0 58
21 0 3 44
48 0 0 54
21 0 1 58
6 0 0 262144
6 0 0 0

    Original use-case: tcpdump filter for raw packet sockets

## Page 41

    What is BPF?

• tcpdump -i eno1 -d icmp or icmp6
(000) ldh [12]               #ethertype field
(001) jeq #0x800 jt 2 jf 4   # IPv4?
(002) ldb [23]
(003) jeq #0x1 jt 10 jf 11   # ICMP==1?
(004) jeq #0x86dd jt 5 jf 11 #IPv6?
(005) ldb [20]
(006) jeq #0x3a jt 10 jf 7 # ICMPv6==58?
(007) jeq #0x2c jt 8 jf 11 # IPv6-Frag
(008) ldb [54]
(009) jeq #0x3a jt 10 jf 11 # ICMPv6
(010) ret #262144
(011) ret #0

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf]]`
