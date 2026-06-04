---
type: source
source-type: slide
title: "CS744_kernel-bypass_theory_slides"
path: slides/CS744_kernel-bypass_theory_slides.pdf
size: 383 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# CS744_kernel-bypass_theory_slides

> Ingested from `slides/CS744_kernel-bypass_theory_slides.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.37 MB.

## Page 1

       Kernel-bypass techniques for
high-speed network packet processing
        CS 744


Presenters: Rinku Shah, Priyanka Naik
    {rinku, ppnaik}@cse.iitb.ac.in

Course Instructor: Prof. Umesh Bellur


    Department of Computer Science & Engineering
    Indian Institute of Technology Bombay

## Page 2

Outline

●   The journey of a packet through the Linux network stack

●   Need for kernel bypass techniques for packet processing

●   Kernel-bypass techniques

    ○ User-space packet processing

       ■   Data Plane Development Kit (DPDK)

       ■   Netmap

    ○ User-space network stack

       ■   mTCP

●  What’s trending?

               2

## Page 3

Typical packet flow



TX                 RX

Application        Application

Transport (L4)     Transport (L4)

Network (L3)       Network (L3)

Data link (L2)     Data link (L2)

NIC driver         NIC driver

NIC hardware       NIC hardware





                   3

## Page 4

What does a packet contain?





Ethernet header IP header TCP header payload FCS



dest   src type
MAC    MAC


                                                                src      dst ... checksum ...
       ...  length  ...     IP       header     src     dst     port     port
                            type     csum       IP      IP



FCS: Frame Check Sequence                                                4

## Page 5

Outline

●   The journey of a packet through the Linux network stack

●   Need for kernel bypass techniques for packet processing

●   Kernel-bypass techniques

    ○ User-space packet processing

       ■   Data Plane Development Kit (DPDK)

       ■   Netmap

    ○ User-space network stack

       ■   mTCP

●  What’s next??
               5

## Page 6

    RX path: Packet arrives at the destination NIC


    Applications     User space      NIC receives the packet
                     Kernel space    ●     Match destination MAC address
                                     ●     Verify Ethernet checksum (FCS)
    NIC driver

                  packet
                  buffer             Packets accepted at the NIC
                  packet
    TX        RX  buffer             ●     DMA the packet to RX ring buffer
                    ...
                  packet             ●     NIC triggers an interrupt
                  buffer


                       TX/RX rings
    NIC                 ●   Circular queue
           Hardware     ●   Shared between NIC and NIC driver
           RX queue     ●   Content: Length + packet buffer pointer
                                               6










Hardware
 interrupt

## Page 7

Interrupt processing in the linux kernel

● Top-half
  ○ Minimal processing
● Bottom-half
  ○ Rest of interrupt processing



7

## Page 8

Top-half interrupt processing


RX                     CPU interrupts the process in execution
Application
Transport (L4)         Switch from user space to kernel space

Network (L3)      Top-half interrupt processing
Data link (L2)    ●  Lookup IDT (Interrupt Descriptor Table)
NIC driver        ●  Call corresponding ISR (Interrupt Service Routine)
NIC hardware        ○  Acknowledge the interrupt
                    ○  Schedule bottom-half processing
    ●     Switch back to user space


                       8

## Page 9

    Bottom-half processing

    Applications   User space     CPU initiates the bottom-half when it is free (soft-irq)
                                         Switch from user space to kernel space

                   Kernel space
                   s              Driver dynamically allocates an sk-buff (a.k.a., skb)
                   k
    NIC driver     b

             packet                      Oops!!
             buffer
             packet
             buffer
    TX      RX ...               sk-buff (sk-buff tutorial link)
             packet
             buffer              In-memory data structure that contains packet metadata
                                 ●     Pointers to packet headers and payload
                                 ●     More packet related information ...
        NIC

                                           9










Hardware
 interrupt

## Page 10

    Bottom-half processing

    Applications     User space      NIC driver processing

                     Kernel space    1.    Driver dynamically allocates an sk-buff
                    s
                    k                2.    Update sk-buff with packet metadata
    NIC driver      b
             packet                  3.    Remove the Ethernet header
             buffer
             packet                  4.    Pass sk-buff to the network stack
             buffer
    TX      RX ...
             packet
             buffer

                         Call L3 protocol handler


    NIC

                     10










Hardware
 interrupt










    For all packets
    in buffer

## Page 11

L3/L4 processing


                            L3-specific processing

RX                                                   1.    Route lookup

Application     Common processing                    2.    Combine fragmented packets
Transport (L4)   1.     Match destination IP/socket  3.    Call L4 protocol handler
Network (L3)     2.     Verify checksum        L4-specific processing
Data link (L2)
                 3.     Remove header
NIC driver

NIC hardware




                        11

## Page 12

    L3/L4 processing

    Application      User space    L3-specific processing

        Kernel space               1.     Route lookup

                                   2.     Combine fragmented packets
    Network stack     W    R
                      Q    Q       3.     Call L4 protocol handler
    NIC driver             skb

                        packet     L4-specific processing
                        buffer
                        packet     1.     Handle TCP state machine
    TX      RX          buffer
                          ...
                        packet     2.     Enqueue to socket read queue
                        buffer

                                   3.     Signal the socket

        NIC
                                              12










Hardware
 interrupt

## Page 13

    Application processing

    Application    User space    On socket read: user space to kernel space
        Kernel space             ●   Dequeue packet from socket receive queue
    System calls
                     W    R          (kernel space)
    Network stack    Q    Q
    NIC driver            skb    ●   Copy packet to application buffer (user space)
                       packet    ●   Release sk-buff
                       buffer
                       packet    ●   Return back to the application
    TX      RX         buffer
                         ...
                       packet        kernel space to user space
                       buffer




    NIC
                                     13










Hardware
interrupt

## Page 14

    Transmit path of an application packet

    Application  User space


    Kernel space
    System calls      On socket write: user space to kernel space
    Network stack
                       ●  Writes the packet to the kernel buffer
    NIC driver
              packet   ●  Calls socket’s send function (e.g., sendmsg)
              buffer
              packet
              buffer
    RX      TX  ...
              packet
              buffer




    NIC
                          14










Hardware
 interrupt

## Page 15

    L4/L3 processing

    Application      User space    L4-specific processing
                                   1.  Allocate sk-buff
        Kernel space               2.  Enqueue sk-buff to socket write queue
                                   3.  Call L3 protocol handler

    Network stack     W      R
                      Q      Q         Common processing
    NIC driver        skb              1.  Build header
                                       2.  Add header to packet buffer
                packet                 3.  Update sk-buff
                buffer
                packet
    RX      TX  buffer
                  ...            L3-specific processing
                packet
                buffer             1.  Fragment, if needed
                                   2.  Call L2 protocol handler

        NIC
                                           15










Hardware
 interrupt

## Page 16

    L2 processing

    Application    User space
                                   Enqueue packet to queue discipline (qdisc)
        Kernel space               ●     Hold packets in a queue
                                   ●     Apply scheduling policies (e.g. FIFO, priority)

                   R       W
                   Q       Q
    NIC driver        skb          qdisc
                                   ●     Dequeue sk-buff (if NIC has free buffers)
                      packet
                      buffer       ●     Post process sk-buff
                      packet
    RX      TX        buffer
   ...                    qdisc         ○  Calculate IP/TCP checksum
                          queue
                      packet            ○  … (tasks that h/w cannot do)
                      buffer
                                   ●     Call NIC driver’s send function

        NIC
                                             16










Hardware
interrupt

## Page 17

    NIC processing

                                 NIC driver
                    User space             ●     If hardware transmit queue full
    Application                                  ○    Stop qdisc queue
                                           ●     Otherwise:
                    Kernel space                 ○    Map packet data for DMA
    NIC driver                                   ○    Tells NIC to send the packet
                    packet  NIC
                    buffer                 ●     Calculates ethernet frame checksum (FCS)
                    packet
    RX        TX    buffer       qdisc     ●     Sends packet to the wire
                      ...        queue     ●     Sends an interrupt “Packet is sent” (kernel
                    packet
                    buffer                       space to user space)
                                           ●     Driver frees the sk-buff; starts the qdisc queue

        NIC        Hardware  Transmit and receive packet processing pipeline DONE!!
                   TX queue
                                                     17










Hardware
interrupt

## Page 18

Packet processing overheads in the kernel

●   Too many context switches!!

    ○ Pollutes CPU cache

●   Per-packet interrupt overhead

●   Dynamic allocation of sk-buff

●   Packet copy between kernel and user space

●   Shared data structures


Cannot achieve line-rate for recent high speed NICs!! (40Gbps/100Gbps)

        18

## Page 19

Optimizations to accelerate kernel packet processing

● NAPI (New API) Reading link

● GRO (Generic Receive Offload) GRO+GSO

● GSO (Generic Segmentation Offload) GRO+GSO with DPDK

● Use of multiple hardware queues Multiqueue NIC, Supplement: RSS+RPS+...

● ...






19

## Page 20

Outline

●   The journey of a packet through the Linux network stack

●   Need for kernel bypass techniques for packet processing

●   Kernel-bypass techniques

    ○ User-space packet processing

       ■   Data Plane Development Kit (DPDK)

       ■   Netmap

    ○ User-space network stack

       ■   mTCP

●  What’s trending?

               20

## Page 21

Packet Processing Overheads in Kernel


●  Context switch between kernel and userspace    Application read  user space



Kernel        kernel space


NIC









21

## Page 22

    Packet Processing Overheads in Kernel


                                                      Application buffer
    ●     Context switch between kernel and userspace    in userspace
              Application     read     user space
    ●     Packet copy between kernel and userspace


Buffer in kernel  Kernel        kernel space
     memory


          NIC










          22

## Page 23

Packet Processing Overheads in Kernel


●     Context switch between kernel and userspace    Application
●     Packet copy between kernel and userspace
●     Dynamic allocation of sk_buff
          skb      skb
●     Per packet interrupt        receive        Kernel        transmit
●     Shared data structures

          NIC









      23

## Page 24

Overcome Overheads in Kernel: Bypass the kernel



L2-L4 packet
Application    user space processing    Application
    Shared
    Pre-allocated                           buffers  user space
Kernel        kernel space        Packet processing


NIC    NIC



Context switch between kernel and userspace
Packet copy between kernel and userspace
Dynamic allocation of sk_buff

    24

## Page 25

Interrupt vs Poll Mode



Interrupt Mode    Poll Mode


CPU    NIC    CPU    NIC



●     NIC notifies it needs servicing       ●     CPU keeps checking the NIC
●     Interrupt is a hardware mechanism     ●     Polling is done with help of control
●     Handled using interrupt handler             bits (Command-ready bit)
●     Interrupt overhead for high speed     ●     Handled by the CPU
      traffic                               ●     Consumes CPU cycles but handles
●     Interrupt for a batch of packets            high speed traffic



                                                  25

## Page 26

Interrupt vs Poll Mode: Kernel bypass techniques



Interrupt Mode    Poll Mode


CPU    NIC    CPU    NIC



●     NIC notifies it needs servicing       ●     CPU keeps checking the NIC
●     Interrupt is a hardware mechanism     ●     Polling is done with help of control
●     Handled using interrupt handler             bits(Command-ready bit)
●     Interrupt overhead for high speed     ●     Handled by the CPU
      traffic                               ●     Consumes CPU cycles but handles
                                                  high speed traffic

          Netmap                                  DPDK
                                                      26

## Page 27

Outline

●   The journey of a packet through the Linux network stack

●   Need for kernel bypass techniques for packet processing

●   Kernel-bypass techniques

    ○ User-space packet processing

       ■   Data Plane Development Kit (DPDK)

       ■   Netmap

    ○ User-space network stack

       ■   mTCP

●  What’s trending?

               27

## Page 28

Intel Data Plane Development Kit (DPDK)

          User Space

•     Poll mode user space drivers (uio)    Application
      ○ Unbinds NIC from kernel
•     Mempool: HUGE pages to avoid TLB misses.        rte_mbuf

•     Rte_mbuf: metadata+ pkt buffer        rte_ring   rte_mempool

•     Cooperative multiprocessing
      ○ Safe for trusted application        Poll Mode Drivers

          28


      Kernel Space
      DPDK    NIC

## Page 29

    Netmap




    •     Netmap Rings are memory regions in     Application
          kernel space shared between application
          and kernel        User Space
    •     No extra copy of a packet        Sockets
    •     NIC can work with netmap as well as
          kernel drivers (transparent mode)    Kernel TCP
                                                  Stack


DPDK, netmap manage processing till    Netmap driver  Drivers (ixgbe)
        L2 of network stack        Kernel Space
    netmap        NIC        29

## Page 30

    What about L3-L7 processing?


    Application
    ● Overheads with L3-L7 processing in kernel
      ● Shared data structure


    ●     Userspace network stack
          ○ Over netmap or DPDK
    ●     mTCP: multicore TCP    Kernel network
              processing
Shared socket
and TCP data
  structure

              NIC


                                               CPU core

                                                   30

## Page 31

    Multiqueue NIC






    Application



    NIC                   Receive Side Scaling (RSS)

                          Hash of (src_ip, dst_ip, src_port, dst_port)
    Incoming packet to NIC

                                                    RX queue Application
Cores

                                                    TX queue

31

## Page 32

mTCP: Userspace network stack


               Application
●     Designed for multicore scalable application
●     Per core TCP data structures        Per core mTCP
     ○     E.g. accept queue, socket list    thread
     ○     Lock free
     ○     Connection locality        netmap/ DPDK
●    Leverages multiqueue support of NIC


      Shared data structures    NIC



      mTCP    Incoming packets
               32

## Page 33

Outline

●   The journey of a packet through the Linux network stack

●   Need for kernel bypass techniques for packet processing

●   Kernel-bypass techniques

    ○ User-space packet processing

       ■   Data Plane Development Kit (DPDK)

       ■   Netmap

    ○ User-space network stack

       ■   mTCP

●  What’s trending?

               33

## Page 34

What’s trending?

●  Offload application processing to the kernel
  ○   BPF (Berkeley Packet Filter)
  ○   eBPF (eXtended BPF) BPF+eBPF+XDP link-1, BPF+eBPF+XDP tutorial link-2
●  Offload application processing to the NIC driver
  ○   XDP (eXpress DataPath) Sample apps for eBPF + XDP
●  Offload application processing to programmable hardware
  ○   Programmable SmartNICs (NPU/DPU)
      ■   Netronome, Mellanox, Bluefield, Pensando Video on smartNIC architecture + Netronome
          NIC specifics
  ○   Programmable FPGAs
      ■   Xilinx, Altera
  ○   Programmable hardware ASICs Programmable network: Intro video , Detailed video link
      ■   Barefoot Tofino, Cisco’s Doppler, Intel Flexpipe, Cavium’s Xpliant

              34

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/CS744_kernel-bypass_theory_slides.pdf]]`
