---
type: source
source-type: paper
title: "2021-Secure_Namespaced_Kernel_Audit_for_Containers"
path: papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf
size: 773 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 2021-Secure_Namespaced_Kernel_Audit_for_Containers

> Ingested from `papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.75 MB.

## Page 1

    Secure Namespaced Kernel Audit for Containers

            Soo Yee Lim                        Bogdan Stelea
  University of British Columbia           University of Bristol
Vancouver, British Columbia, Canada       Bristol, United Kingdom
         sooyee@cs.ubc.ca                  bs17580@bristol.ac.uk

            Xueyuan Han                       Thomas Pasquier
        Harvard University            University of British Columbia
   Cambridge, Massachusetts, USA    Vancouver, British Columbia, Canada
        hanx@g.harvard.edu                    tfjmp@cs.ubc.ca

    ABSTRACT                                                                            ACM Reference Format:
    Despite the wide usage of container-based cloud comput-                             Soo Yee Lim, Bogdan Stelea, Xueyuan Han, and Thomas Pasquier.
    ing, container auditing for security analysis relies mostly                         2021. Secure Namespaced Kernel Audit for Containers. In Proceed-
    on built-in host audit systems, which often lack the abil-                          ings of ACM Symposium on Cloud Computing (SoCC ’21). ACM, New
    ity to capture high-fidelity container logs. State-of-the-art                       York, NY, USA, 15 pages. https://doi.org/10.1145/3472883.3486976
    reference-monitor-based audit techniques greatly improve                            1 INTRODUCTION
    the quality of audit logs, but their system-wide architecture is
    too costly to be adapted for individual containers. Moreover,                       In recent years, container-based cloud computing has gained
    these techniques typically require extensive kernel modifica-                       much traction. As a lightweight alternative to VM-based com-
    tions, making it difficult to deploy in practical settings.                         puting infrastructure, it provides an attractive multi-tenant
    In this paper, we present saBPF (secure audit BPF), an                              environment that supports the development of microservice
    extension of the eBPF framework capable of deploying secure                         architecture, where a monolithic application is organized
    system-level audit mechanisms at the container granularity.                         into a number of loosely-decoupled services for modularity,
    We demonstrate the practicality of saBPF in Kubernetes by                           scalability, and fault-tolerance [59].
    designing an audit framework, an intrusion detection system,                        Container security becomes a major concern as the popu-
    and a lightweight access control mechanism. We evaluate                             larity of container-based cloud continues to grow rapidly [64].
    saBPF and show that it is comparable in performance and                             For example, by sharing individual microservices across ap-
    security guarantees to audit systems from the literature that                       plications, the container ecosystem, as promoted by widely-
    are implemented directly in the kernel.                                             used container management and orchestration platforms,
                                                                                        such as Docker and Kubernetes, inadvertently spreads vul-
    CCS CONCEPTS                                                                        nerabilities that can widen an application’s attack surface [63].
                                                                                        Vulnerabilities in individual containers can facilitate the con-
    • Security and privacy → Operating systems security; In-                            struction of a cyber kill-chain, in which the attackers perform
    trusion detection systems; • Networks → Cloud computing.                            various attacks in steps on different microservices to achieve
                                                                                        their ultimate goal [37]. Information leakage between a host
    KEYWORDS                                                                            and a container and between two co-resident containers has
    eBPF, auditing, container, provenance                                               also been demonstrated to be possible [25].
                                                                                        Like in traditional security analysis, system-layer audit
                                                                                        logs are often considered to be an important information
    Permission to make digital or hard copies of all or part of this work for           source for addressing many container security concerns [29,
    personal or classroom use is granted without fee provided that copies are not       31, 44]. For example, to identify a misbehaving container
    made or distributed for profit or commercial advantage and that copies bear
    this notice and the full citation on the first page. Copyrights for components      from a cluster of replicated microservices, kernel audit logs
    of this work owned by others than ACM must be honored. Abstracting with             have been used to define process activity patterns and de-
    credit is permitted. To copy otherwise, or republish, to post on servers or to      scribe unusual activity that does not fit into any observed
    redistribute to lists, requires prior specific permission and/or a fee. Request     pattern [32]. Container-focused security systems typically
    permissions from permissions@acm.org.                                               use existing host audit tools, such as the Linux Audit Frame-
    SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                      work, to log system events, but research has shown that
    © 2021 Association for Computing Machinery.                                         these audit systems are insufficient to capture complete sys-
    ACM ISBN 978-1-4503-8638-8/21/11. . . $15.00
    https://doi.org/10.1145/3472883.3486976                                             tem activity necessary for security analysis [26]. Alternative

## Page 2

SoCC ’21, November 1–4, 2021, Seattle, WA, USA                           Lim et al.

reference-monitor-based approaches [51, 54] provide a more
complete picture by leveraging in-kernel monitoring hooks,
but they are not designed with container-based computing ar-
chitecture in mind. Specifically, reference-monitor-based ap-
proaches require extensive host kernel modification and per-
mit only host-wide policy specification. The former require-
ment is often forbidden by cloud infrastructure providers,
and the latter makes it difficult to satisfy the audit needs of
individual containers sharing the same host.
We present saBPF, a lightweight, secure kernel audit sys-
tem for containers. saBPF enables each container to cus-
tomize its auditing mechanism and policy, even if containers
specifying different policies and mechanisms are co-located              Figure 1: eBPF workflow.
on the same host. Audit data captured by saBPF is guaranteed
to have high fidelity, meaning that the data faithfully records
complete container-triggered system activity [54], free of
concurrency vulnerabilities [66] and missing records [26]            that instrument in-kernel hooks defined by the Linux Secu-
that are commonly present in existing audit tools. As such,          rity Modules (LSM) framework, which is the reference moni-
saBPF builds a solid foundation for future forensic applica-         tor implementation for Linux [46]. saBPF further leverages
tions in a containerized cloud environment. For example, to          namespaces to ensure that auditing can be customized for
deploy a cyber kill-chain detection system for a network of          individual containers. We provide some background knowl-
Kubernetes containers (or pods), we can follow the Sidecar           edge for each component.
design pattern, in which saBPF is configured for each pod
based on the characteristics of the microservice it provides.        2.1  Extended Berkeley Packet Filter
A specialized sidecar container is attached to capture and           eBPF is a Linux built-in framework that allows customized
analyze audit logs. Sidecar containers from different pods           extensions to the kernel without modifying the kernel’s core
can ship any suspicious events to a remote system where              trusted codebase. We illustrate how eBPF works in Fig. 1.
alert correlation is performed to detect the presence of a           Developers can write an eBPF program in C and compile
kill-chain [45]. We discuss this use case in more detail in § 4.     the program into eBPF bytecode using Clang. The kernel
saBPF is implemented as an extension of eBPF. Specifically,          uses a verifier to statically analyze the bytecode, minimiz-
we make the following contributions:                                 ing security and stability risks of running untrusted kernel
              • We expand Linux’s eBPF framework to support the      extensions [28]. After verification, a just-in-time (JIT) com-
             attachment of eBPF programs at the intersection of      piler dynamically translates the bytecode into efficient native
             the reference monitor and namespaces, which allows      machine code. The translated eBPF program is attached to
       fully-configurable, high-fidelity, system-level auditing      designated kernel locations (e.g., LSM hooks in our case) and
for individual containers (see § 3);                                 executed at runtime. eBPF programs can share data with
          • We develop functional proof-of-concept applications      user-space applications using special data structures such as
using saBPF to demonstrate its practicality (see § 4);               eBPF maps and ring buffers [3].
           • We conduct thorough performance analysis to under-      eBPF is frequently used as the underlying framework for
          stand the cost and benefits of using saBPF for secure      network security and performance monitoring. In a container
          audit; we show that our approach outperforms existing      environment, for example, eBPF enables Cilium [5], a popular
audit solutions of similar caliber (see § 5 and § 6);                network monitoring tool for platforms such as Kubernetes, to
        • We open source saBPF to facilitate the development of      secure application-level protocols with fine-grained firewall
         security applications for containers in the cloud (see      policies.
Appendix A).
                                                                     2.2  Linux Security Modules
2 BACKGROUND                                                         LSM consists of a set of in-kernel hooks that are strategi-
saBPF is built upon the extended Berkeley Packet Filter (eBPF)       cally placed where kernel objects (such as processes, files,
framework, a Linux subsystem that allows user-defined pro-           and sockets) are being accessed, created, or destroyed. LSM
grams to safely run inside the kernel [8]. To provide high-          hooks can be instrumented to enable diverse security func-
fidelity system audit data, saBPF implements eBPF programs           tionality, with the canonical usage being the implementation

## Page 3

Secure Namespaced Kernel Audit for Containers              SoCC ’21, November 1–4, 2021, Seattle, WA, USA

                                                 Name      Description
                                                 cgroup    Allocate system resource (e.g., CPU, memory,
                                                           and networking)
                                                 ipc       Isolate inter-process communications
                                                 network Virtualize the network stack
                                                 mount     Control mount points
                                                 process   Provide independent process IDs
                                                 user      Provide independent user IDs and group IDs,
                                                           and give privileges (or capabilities) associated
                                                           with those IDs within other namespaces
                                                 UTS       Change host and domain names
                                                 Time      See different system times

                                                     Table 1: Summary of Linux namespaces.


Figure 2: LSM hook architecture [46]. The green blocks              resources are not visible to processes outside the namespace.
are specific to saBPF, which is described in § 3. ○1 shows          We summarize available namespaces in Linux in Table 1.
programs attached to the root cgroup; ○2 shows two                  One prominent use of namespaces is to create contain-
programs attached to the child1 and child2 cgroup                   ers. For example, an application in a Docker container runs
respectively.                                                       within its own set of namespaces. Kubernetes “pods” contain
                                                                    one or more containers so that they share namespaces (and
                                                                    therefore system resources). Kubernetes makes it appear to
of mandatory access control scheme [56]. As a reference mon-        applications within a pod that they own a machine of their
itor, LSM has also been adapted to perform secure kernel log-       own (Fig. 3).
ging, which provides stronger completeness and faithfulness         saBPF modifies the kernel to enable per-container audit-
guarantees than traditional audit systems [17, 51, 54]. For         ing, selectively invoking eBPF programs on LSM hooks based
example, prior research has verified that LSM hooks capture         on cgroup membership (§ 3.1). cgroup isolates processes’
all meaningful interactions between kernel objects [22, 36]         resource usage in a hierarchical fashion, with a child group
and that information flow within the kernel can be observed         having additional restrictions to those of its parent. Since
by at least one LSM hook [27], which is necessary to achieve        cgroup v2 [35], this hierarchy is system-wide, and all pro-
completeness.                                                       cesses initially belong to the root cgroup. In a Kubernetes
The LSM framework does not use system call interposi-               pod, for example, containers can be organized in a hierarchi-
tion as older systems did. Syscall interposition is susceptible     cal structure and assigned various cgroup namespaces to set
to concurrency vulnerabilities, which in turn lead to time-         up further restrictions. Certain types of eBPF programs, such
of-check-to-time-of-use (TOCTTOU) attacks that result in            as the ones that are socket-related, can already be attached
discrepancies between the events as seen by the security            to cgroups (e.g., BPF_PROG_TYPE_CGROUP_SKB). This allows,
mechanism and the system call logic [66, 67]. This is why           for example, a packet filtering program to apply network
solutions such as kprobe-BPF, while useful for performance          filters to sockets of all processes within a particular con-
analysis, are not appropriate to build security tools. Instead,     tainer. saBPF makes it possible to attach eBPF programs at
LSM’s reference-monitor design ensures that the relevant            the intersection of cgroups and LSM hooks (§ 3.1) for audit
kernel states and objects are immutable when a hook is              purpose and beyond (§ 4).
triggered, which is necessary to achieve faithfulness. LSM-
BPF [57] is a recent extension to the eBPF framework that           3 SABPF: EXTENDING THE EBPF
provides a more secure mechanism to implement security              FRAMEWORK
functionalities on LSM hooks.                                       saBPF extends the eBPF framework to support secure ker-
    Namespaces in Linux                                             is minimally invasive, reusing existing components in the
2.3                                                                 nel auditing in a containerized environment. Our design
A namespace in the Linux kernel is an abstract environment          framework as much as possible and extending only what
in which processes within the namespace appear to own an            we deemed to be necessary. This is a conscious decision
independent instance of system resources. Changes to those          made to achieve two objectives: 1) by adhering closely to the

## Page 4

SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                                                                     Lim et al.

                                                  1   SEC ( " c g r o u p_l sm / f i l e _ o p e n " )
                                                  2   i n t c g r o u p _ f i l e _ o p e n ( s t r u c t b p f _ c g r o u p _l sm _ c t x ∗
                                                       c t x )
                                                  3   {
                                                  4    b p f _ t r a c e _ p r i n t k ( " H e l l o World ! \ n " ) ;
                                                  5    re turn 0 ;
                                                  6   }
                                                      Listing 1: A “Hello World!” saBPF program that can be
                                                      triggered on the file_open hook.


    Figure 3: Namespaces in Kubernetes.

                                                                          In the kernel, when an LSM hook is triggered, saBPF in-
                                                                   vokes appropriate eBPF programs through a customized se-
design philosophy of the eBPF framework, we ensure that            curity module. This module performs three main actions
saBPF can be readily integrated into the mainline kernel; 2)       for every hook. First, it prepares the parameters, which are
since saBPF is built upon the eBPF framework and adheres           passed from the hooks to the eBPF programs. It then re-
to its design philosophy, users already familiar with eBPF         trieves the cgroup associated with the current task. Finally,
can quickly develop new applications using saBPF, while            it traverses the cgroup hierarchy (§ 2.3) backwards from the
new users have access to eBPF’s documentations and forums,         current cgroup to the root cgroup and executes all programs
which makes saBPF easy to learn and use. In addition, any          associated with the LSM hook.
existing eBPF program can run in conjunction with our au-              Fig. 2 illustrates this process using the open system call
dit solution on the saBPF-enhanced platform for individual         as an example. The root cgroup has two child cgroups,
containers.                                                        child1 and child2. While the root cgroup has programs
                                                                   attached to both inode_create and file_open LSM hooks,
3.1  Namespacing LSM-BPF                                           child1 has only one program attached to file_open and
saBPF extends the use of cgroup (which in eBPF is used             child2 has one program attached to a different LSM hook,
mostly for network filtering) to LSM hooks. This extension         inode_setattr. As a result, any process that triggers the
allows saBPF to precisely control audit granularity. Recall        file_open hook leads to the invocation of the programs
that cgroups are arranged in a global hierarchy since cgroup       attached to that hook in the root cgroup. However, the pro-
v2, and all processes belong to the root cgroup by default.        grams attached to the same hook in child1 are only called if
                                                                   a process belonging to child1 (or one of its decedents) trig-
A Kubernetes pod, for example, defines a pod-level cgroup,         gers the hook. Note that this process still causes programs
which is the ancestor ofcontainer-level cgroups within which       in the root cgroup to be called.
individual containers in the pod reside (Fig. 3). By attach-             Early in the design phase, we considered creating a ded-
ing eBPF programs to container-level cgroups, saBPF can            icated namespace for system auditing. While this allows a
perform container-level auditing; at the same time, saBPF          clear separation of namespaces’ responsibilities, given that
can monitor activity inside the entire pod by attaching au-        cgroups are designed to control access to system resources,
dit programs to the pod’s root cgroup. While the design of         we eventually abandoned this design for two reasons. First,
Kubernetes makes it natural to follow this two-level audit         significant re-engineering of existing container solutions
scheme using cgroup, saBPF can support arbitrarily complex         would be required to make use of this new namespace. Sec-
cgroup hierarchy for customizable use.                             ond, existing namespaced eBPF already uses cgroup. We
Listing 1 illustrates how an saBPF program is defined by           believe that introducing a new namespace goes against the
developers. It is a program that simply prints “Hello World!”      current design philosophy of eBPF. However, we emphasize
when the file_open LSM hook is triggered. The statement            that based on our experience, it is relatively straightforward
in line 1 specifies where the program should be attached, and      to implement a new namespace should such a need arise in
the ctx variable in line 2 contains the parameters passed from     the future.
the file_open hook. The user attaches (and detaches) this
program to (and from) a cgroup through the bpf() system
call. Multiple eBPF programs can be attached to the same           3.2  Local Storages
cgroup-hook pair by setting the BPF_F_ALLOW_MULTI flag;            System auditing often requires associating data with ker-
they will be executed in FIFO order.                               nel objects [54].     In early prototypes, we considered using

## Page 5

Secure Namespaced Kernel Audit for Containers                          SoCC ’21, November 1–4, 2021, Seattle, WA, USA

    0.4                                                           Name                     Description
local                                                             bpf_inode_from_sock      Retrieve the inode associ-
    1.72                                                                                   ated with a socket
map                                                               bpf_file_from_fown       Retrieve the file associated
                                                                                           with a fown_struct
    0      0.5      1    1.5      2      2.5                      bpf_dentry_get           Retrieve the dentry associ-
Figure 4: Look-up time for the cred local storage and                                      ated with an inode
the eBPF map in s. Using local storage gives a 4x                 bpf_dentry_put           Release a dentry after use
speedup.                                                          bpf_[cred/msg/ipc/       Get a bpf_local_storage
                                                                  file]_storage_get        from a cred/msg/ipc/file
                                                                  bpf_[cred/msg/ipc/                    Delete a bpf_local_storage
eBPF maps, which are key-value stores shared among multi-         file]_storage_delete     from a cred/msg/ipc/file
ple eBPF programs across execution instances, but we aban-         Table 2: Summary of new eBPF helpers provided by
doned the idea due to poor maintainability. Specifically, when     saBPF.
using eBPF maps, developers must create an entry for each
new kernel object to store data associated with the object.
The key to the entry must be unique during the lifecycle
of the object. Ensuring uniqueness for all kernel objects is               A subset of functions return the inode associated to an
important, but prone to error. For example, it is insufficient     object of a certain type (e.g., bpf_inode_from_sock returns
to use just an inode number as the key for an inode object;        the inode of a socket object). This can be useful to understand
rather, a combination of the inode number and the file sys-        the interplay of system calls acting at different levels of
tem’s unique identifier is needed because inode numbers            kernel abstraction.
are guaranteed to be unique per file system only. Moreover,                bpf_dentry_get returns the directory entry of an inode,
developers must also take special care to remove map entries       which helps saBPF programs to retrieve the path associated
when objects reach the end of their lifecycle. This problem        with the inode. A directory entry is protected by a refer-
is exacerbated by the fact that eBPF maps are created with         ence counter when a program manipulates it. The reference
capacity limits.                                                   counter is increased when bpf_dentry_get is called and
saBPF uses a completely different approach to storing              must be decreased by calling bpf_dentry_put once the en-
such data, extending eBPF’s local storages, which are data         try is no longer used. To ensure correctness, we also modified
structures that are directly associated with kernel objects.       the eBPF verifier to verify that every bpf_dentry_get has
Local storages provide an interface similar to eBPF maps,          a corresponding bpf_dentry_put being called on the same
but they use the object reference as the key and store the         code path.
value locally with the kernel object. At the end of an ob-                The remaining helpers are used to manipulate local stor-
ject’s lifecycle when the object no longer has any reference,      ages (§ 3.2). We extended eBPF map helpers so that userspace
eBPF transparently removes the local storage associated with       programs can interact with those storages. In eBPF maps,
the object. This takes the responsibility of removing unused       userspace programs can access a set of helpers via system
entries away from developers, making it less error-prone.          calls to e.g., update or lookup map entries. Our extension
Furthermore, local storages incur less performance overhead        provides similar support for local storages: programs can
compared to eBPF maps, as shown in Fig. 4. At the time             manipulate data in the local storage of a particular kernel
of writing, eBPF provides local storages for only cgroup,          object using appropriate userspace identifiers. For example,
socket, inode and task. We implemented additional local            assuming appropriate privileges, we can lookup, update, and
storages for file, cred, ipc, superblock, and msg_msg to           delete data in a cred1 object’s local storage via its PID.
fully support LSM-based auditing. We give a practical illus-
tration in § 4.1.                                                  4 USE CASES
                                                                   A framework like saBPF is only useful if it is both practical
3.3      Extension of eBPF interface                               and performant. We discuss three meaningful use cases that
To access kernel data, eBPF programs rely on eBPF helpers,         we have implemented to demonstrate the types of application
which are an allowlist of kernel functions permitted by the        that saBPF can easily support, showcasing its practicality.
eBPF verifier to interact with the kernel. saBPF defines a         We evaluate saBPF’s performance in § 6.
number of extra eBPF helpers, as shown in Table 2, to facili-
tate system auditing.                                              1cred is the credential information associated with a process.

## Page 6

SoCC ’21, November 1–4, 2021, Seattle, WA, USA    Lim et al.










Figure 5: A simplified whole-system provenance sub-
graph.


4.1    Whole-system Provenance Capture                                Figure 6: ProvBPF overview.
We describe our implementation of ProvBPF, a provenance
capture mechanism that we developed atop saBPF. Prove-
nance has gained much traction in the security community,
notably with applications designed to understand intrusions           compilation of the Linux kernel would contain approximately
in a computer system [33, 34, 44], prevent data exfiltra-             a few million graph elements [47].
tion [17], and detect attacks [29–31, 42, 45, 65]. ProvBPF               The rest of our discussion focuses primarily on the novel
captures provenance at the thread granularity, recording              aspects of ProvBPF and the design choices we made as the
information such as security context, namespace, and per-             result of using saBPF to capture OS-level provenance (in-
formance metrics.                                                     stead of modifying the kernel). We compare ProvBPF’s per-
A Brief Provenance Introduction. Computing systems are                formance to that of a state-of-the-art provenance capture
too often opaque: they accept inputs and generate outputs,            system, CamFlow [51], in § 6.
but the visibility of their inner workings is at best partial,        Overview. Fig. 6 illustrates the architecture of ProvBPF
which poses many issues in fields ranging from algorith-              using the open system call as an example. In ProvBPF, eBPF
mic transparency to the detection of cybersecurity threats.           programs are executed on LSM hook invocations. ProvBPF’s
Unfortunately, traditional tracing mechanisms are inade-              eBPF programs generate provenance graph elements in bi-
quate in addressing these issues. Instead, whole-system prove-        nary and write them to an eBPF ring buffer [3]. A user-space
nance [54], which describes system execution by represent-            daemon serializes those graph elements and outputs them
ing information flows within and across systems as a directed         to disk (or to remote endpoints like Apache Kafka [1]) in a
acyclic graph, shows promise. Provenance records subsume              machine readable format such as W3C PROV-DM [18].
information contained in a traditional trace, while causality            We must associate states with kernel objects to guarantee
relationships between events can be inferred through graph            graph acyclicity and to implement graph compression algo-
analysis.                                                             rithms. For example, to guarantee acyclicity, we associate
           Fig. 5 shows a simple provenance graph. In this graph,     with each object a version counter which is updated when
two tasks (    and   ′     ) are associated with their respective     external information flows into an object and modifies its
memory ( and ′          ). The subscripts (e.g.,1 and2) represent     state. After the update, a new vertex is added to the graph
different versions of the same kernel object to guarantee             and connected to the previous version of the object through
graph acyclicity [48].  creates a pipe            and forks a new     a version edge, as illustrated in Fig. 5 as dashed lines.
process (corresponding to  ′ and  ′   ).    ′   reads information       We also associate an “opaque” flag to the state of certain
from a file    and writes information to    .     then reads from     kernel objects; opaque objects are not audited. This is partic-
this pipe. A versioned node is created every time an object           ularly useful for ProvBPF’s daemon-related objects, because
receives external information (e.g., when a task reads from           capturing their provenance would result in an infinite feed-
a file). This is a small subgraph representing a very simple          back loop. CamFlow uses security blobs from the LSM
scenario. In practice, for example, a graph representing the          framework associated with each kernel object to maintain

## Page 7

Secure Namespaced Kernel Audit for Containers                           SoCC ’21, November 1–4, 2021, Seattle, WA, USA

its associated states. In ProvBPF, we leverages the local stor-      hook in the subgraph with the corresponding graph motif.
age mechanism (§ 3) for this purpose. Local storage can be           The resulting subgraph – now containing only graph motifs
accessed by the ProvBPF daemon from userspace to set a               of LSM hooks – is the graph motif of the system call that
policy for each individual object (e.g., to set opacity).            summarizes what the provenance graph would look like
Graph Reduction. eBPF-based provenance capture offers                when the system call is executed.
exceptional flexibility in designing customized capture poli-        In addition, we build test programs and follow the same
cies that fulfill different objectives. Customization typically      steps above to create program-level graph motifs. For each
involves filtering, i.e., selecting kernel objects and system        program binary, we build a call graph which we then trans-
events that are relevant to a specific analysis. For example,        form into a syscall-only graph. We replace the syscalls in
Bates et al. [15] only record events related to objects associ-      the graph with the motifs we previously built. We run each
ated with specific SELinux policies. ProvBPF allows for the          test program and verify by inspection that our (statically-
filter logic to be built-in during compilation, thus reducing        produced) motif matches the (dynamically-produced) prove-
run-time overhead.                                                   nance graph generated by ProvBPF. We perform the same
ProvBPF implements additional graph reduction tech-                  steps in CamFlow [51] to verify that the graphs generated
niques other than filtering. It automatically merges consec-         by the two systems are equivalent.
utive events of the same type between two entities into a
single event and avoids object versioning as much as pos-            4.2
sible. Event merging reduces the number of edges between    An Intrusion Detection System for
two nodes without changing the semantics of the interac-                Kubernetes
tions they represent. For example, when a process reads a file       saBPF-based audit systems such as ProvBPF can be used as
piece-by-piece through a number of successive read system            an underlying framework for various security applications
calls, saBPF would create only one directed edge between             in the cloud. We demonstrate this feasibility through a con-
the process and the file to capture these read events, which         crete use case of deploying Unicorn [29], a state-of-the-art
is sufficient to describe the information flow from the file to      host-based intrusion detection system (IDS), in a Kubernetes
the process due to read. On the other hand, avoiding object          pod using ProvBPF as an upstream information provider.
versioning reduces the number of nodes, and ProvBPF does             Unicorn is an anomaly-based IDS that learns system behav-
so only when the semantics of an object have not changed.            ior from the provenance graph generated by benign system
These graph reduction techniques are completely agnostic             activity. Once a model is learned from the graph, detection
to specific downstream provenance analysis and can be eas-           is formulated as a graph comparison problem: if a running
ily configured at compilation time according to the needs            system’s provenance graph deviates significantly from the
of a particular application. More importantly, unlike previ-         model, Unicorn considers the system to be under attack. In
ous work [61] that performs graph compression as a costly            the remainder of this section, we focus our discussion on how
post-processing step (i.e., after recording the original graph),     ProvBPF facilitates deployment of an IDS in a containerized
ProvBPF employs those techniques during capture before               environment in a novel and elegant manner; in-depth evalu-
new edges are added to the graph.                                    ation of the performance of such an IDS is out of scope and
Verifying Capture Correctness. It is challenging to verify           left for future work.
the correctness of a provenance capture mechanism [19]. At a         Design & Implementation. ProvBPF makes it easy to
minimum, we must show that a provenance graph describing             run a provenance-based IDS at the pod level in Kubernetes,
system activity of a system call makes “intuitive” sense for a       which is challenging when provenance data is provided by a
human analyst inspecting the graph. We use both static and           reference-monitor-based audit system such as CamFlow [51].
dynamic analysis to verify that provenance graphs generated          For systems like CamFlow, provenance is always captured
by ProvBPF are reasonably correct.                                   system-wide; as a result, audit logs must be filtered to provide
Our static analysis generates a graph motif for each system          as input to the IDS provenance data relevant to a pod only,
call, which enables us to reason about the semantics of the          and filtering must be done on an individual pod basis. Unfor-
graph based on our understanding of the system call. We              tunately, this extra filtering step inevitably adds delay and
follow the same strategy as described by Pasquier et al. [52].       complexity to the entire detection pipeline, thus reducing
To generate a system call graph motif, we first analyze the          runtime detection efficacy.
kernel codebase to construct a call graph of a system call           Instead, we use ProvBPF and Kubernetes’ sidecar design
and extract a subgraph, within the call graph, that contains         pattern to attach the IDS to Kubernetes applications. A side-
only LSM hooks [27]. We then analyze ProvBPF’s codebase              car container is a container that runs alongside a main con-
to generate a graph motif for each LSM hook and augment              tainer (i.e., the one that provides core functionality) in a pod.
the subgraph from the previous step by replacing each LSM            In our design, for each pod, we include a sidecar container

## Page 8

SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                                                                                Lim et al.

that runs both ProvBPF and Unicorn. ProvBPF audits the                               rules, we do not build any rules enforcement program regard-
entire pod and generates a pod-level provenance graph; the                           ing network access. In general, our access control mechanism
graph is then used as input to Unicorn. We note that other                           generates a minimum set of programs needed to enforce a
detection systems such as StreamSpot [42] and log2vec [41]                           given policy, thus reducing complexity and improving per-
could be used in a similar fashion. In a microservice environ-                       formance.
ment, any misbehavior detected within a single pod can be                            Policy Example. Taking inspiration from the Open Policy
sent to a dedicated central service that performs alert cor-                         Agent [12] and AppArmor [2], we create a simple policy lan-
relation [45] to detect, for example, early stages of a cyber                        guage. A policy is expressed in JSON and parsed to generate
kill-chain.                                                                          a customized sidecar application that can be attached to a
Discussion. This deployment strategy, made possible by                               pod.
ProvBPF, have a number of advantages. First, we do not
need to modify applications to deploy our IDS thanks to                        1     {
the sidecar pattern. Second, we can easily deploy an IDS                       2      " t a r g e t " : " / u s r / bi n / f o o " ,
model specific to an application running in a pod, without                     3      " ne two rk " :   { " d e f a u l t " :    " deny " ,   " a l l o w _ e g r e s s " : [
taking into consideration extraneous activity of the rest of                              4 0 4 , 8 0 ] } ,
                                                                               4      " f i l e " : { " d e f a u l t " : " r "  ,  "rw " :   [ " / tmp / ∗ " ] , "mr" :
the system. Third, ProvBPF produces provenance graph                                      [ " / l i b / l d − ∗ . s o ∗ " ,
elements that can be analyzed directly, without introducing                    5          " / l i b / l i b ∗ . s o ∗ " ] }
filtering delays in the detection pipeline. Fourth, deploying                  6     }
ProvBPF imposes no cost on other pods running on the same                                 Listing 2: A simple policy example.
machine, since saBPF programs are only triggered within the
context of a single pod. This is in contrast to a classic system-
wide approach (e.g., Linux Auditd or CamFlow), which would                                                            Listing 2 shows an exemplar policy written in this lan-
negatively affect performance on the entire machine.                                 guage. A /usr/bin/foo process is by default denied access
                                                                                     to the network unless it is an outgoing connection through
4.3  Lightweight Ad-hoc Access Control                                               the http and https ports. Similarly, the process is denied
While saBPF was designed primarily to provide secure audit-                          write or execute by default. However, it has read and write
ing, it can also be used to implement simple access control                          access to the /tmp directory and is able to map system li-
policy within the scope of a container.2 We implemented a                            braries. This policy is inherited by any child process forked
proof-of-concept to demonstrate saBPF’s ability to enforce                           from the /usr/bin/foo process.
access control policy. Like in § 4.2, we consider a Kubernetes                       4.4  Discussion
environment and use the sidecar pattern to deploy access
control policy at the pod granularity.                                               We conclude this section by summarizing the advantages of
Design & Implementation. Using saBPF, we can easily                                  using saBPF, as repeatedly demonstrated by the three use
achieve separation of concerns in Kubernetes, such that each                         cases described above.
pod has its own set of security mechanisms and policies.                             Performance. saBPF is the first reference-monitor-based
We deploy a sidecar alongside unmodified applications to                             audit system that allows audit rule configuration at compila-
constrain their behavior. The sidecar runs a set of saBPF                            tion time, drastically minimizing run-time audit complexity
programs implementing the desired policy and attach them                             and improving overall performance. In stark contrast, other
to the root cgroup of the pod. We associate security contexts                        audit mechanisms such as CamFlow must evaluate complex
to kernel objects through local storage and define an eBPF                           audit rules at runtime to satisfy specific needs of different
map to store constraints applicable to those contexts. When                          downstream applications. For example, security tools such
an LSM hook is triggered, information is retrieved from the                          as SIGL [31] typically analyze only a small subset of host
map to determine whether or not an action is permitted.                              activity logs that an audit system like CamFlow provides. To
Policy violation can be sent to userspace via an eBPF ring                           monitor an application in a Kubernetes pod, Unicorn requires
buffer, which can then be logged or reported to the user                             provenance data generated only by activity in the pod. In
about the unexpected application behavior.                                           both cases, filtering is inevitable but it can sometimes become
We take advantage of the eBPF framework to optimize the                              a performance bottleneck that is difficult to overcome. To
sidecar at the time of its compilation based on the policy to                        make matters worse, as we have discussed in § 5.1, run-time
be enforced. For example, if the policy has no network access                        evaluation can have adverse and cumulative performance
                                                                                     impact, making existing reference monitors undesirable to
2Policy conflict resolution across cgroup hierarchy is out of scope of this          be even considered in practical settings. Similarly, a given
paper. We refer interested readers to § 8.                                           application may only enforce access control constraints on

## Page 9

Secure Namespaced Kernel Audit for Containers                                            SoCC ’21, November 1–4, 2021, Seattle, WA, USA

a subset of events. Through compilation-time policy evalu-           System Call     Security Hooks               Min Hook Calls
ation, saBPF can minimize run-time cost by running only              open            file_open+               1 + 1 × path depth
needed eBPF programs.                                                                inode_create
In practice, this means that given an equivalent policy, a                           inode_permission*
solution built using saBPF significantly outperforms current                         inode_post_setxattr
solutions developed through the built-in LSM mechanism.                              inode_setattr
Maintainability and Adoption. Maintaining out of tree                read            file_permission+                   1
LSMs requires significant effort and time investment. As             write           file_permission+                   1
LSMs are built in the kernel, rigorous testing is essential to       execve          bprm_check+              4 + 1 × path depth
avoid crashes or introducing unintended security vulnera-                            bprm_set_creds+
bilities. This makes exploring new mechanisms difficult. For                         file_open+
similar reasons, it is rare for third parties to further develop                     inode_permission*
on a custom kernel given the high risk of instability and                            file_permission+
vulnerability. We further discuss maintainability concerns           Table 3: Summary of LSM hooks called on successful
in § 7.                                                              system calls. Some hooks are only triggered in a par-
Decentralized Deployment. Standard LSM-based solutions               ticular system state or with specific syscall parameters
are generally deployed system-wide and centralized, and              (e.g., when creating a new file on open). + indicates that
must be managed by the host. By contrast, each containerized         hooks are always called, and * means hooks are called
environment (assuming proper privileges) can deploy its              on every directory in a path.
own LSM mechanisms using saBPF without affecting the
rest of the system. Each guest environment can run not only
different policies, but also a completely different mechanism.
Moreover, saBPF programs are only triggered within the               introduced by a specific LSM module would be constant. In
cgroup they are attached to, thus limiting data leakage across       reality, such an assumption is often an oversimplification.
containers (see § 7 for further discussion on security).             Consider an open system call. A number of LSM hooks, such
                                                                     as file_open and inode_permission, are triggered when
5 UNDERSTANDING POLICY OVERHEAD                                      open is called. If a new file is created because of open, addi-
The run-time performance overhead of any always-on audit             tional hooks such as inode_create and inode_setattr are
system is critical to its successful adoption. While the overall     called when the new file’s underlying inode is being created
performance is a function of a specific audit policy, which          and its attributes set. Of particular interest in this example is
varies across different needs and use cases, the run-time cost       the inode_permission hook, which is called on each direc-
of the underlying infrastructure can be reasonably analyzed,         tory composing the path of the file to be opened, since open
which we present in this section. Our analysis focuses on            must have the permission to search for the file to be opened.
two main components of saBPF, LSM and eBPF; the cost of                      To audit an open-file event, it is important to record all
running both together has not been widely studied, espe-             the permission checks (including the ones on the directo-
cially in the context of audit. We also compare our approach         ries) because it reveals file access patterns. For example, in a
with state-of-the-art reference-monitor-based auditing that          security context, a failed inode_permission check could in-
requires kernel modification.                                        dicate that a compromised application attempted to scan the
                                                                     file system to access sensitive data. The overhead introduced
5.1      LSM overhead                                                by such an audit mechanism on this particular event is a
                                                                     function of path length. For example, assume that invoking
It is difficult to precisely measure LSM overhead [68]. In gen-      file_open and inode_permission and running their call-
eral, there exist two sources of overhead when performing            back functions incur the same cost         . The total overhead of
audit (or other policy enforcement) through LSM: hooking             a file-open event on a path of length    is    × (     + 1). Given
and execution. Hooking refers to the cost of invoking a call-        two audit policies,  and        , such that        is one order of
back function associated with a specific LSM hook, which             magnitude higher than, the total overhead incurred by
incurs roughly constant overhead. Execution refers to the            is in fact two orders of magnitude higher than that by          on
cost of running the callback function, which is dependent on         a path of length 10. The open system call is not the only one
the specific audit (or other policy enforcement) mechanism           affected by such behavior; other system calls, such as chmod,
and can also vary by the (audit) policy itself.                      symlink, mmap, stat, and execve have similar patterns.
It is sometimes mistakenly assumed that for a given sys-                          Because this phenomenon can have a significant impact
tem call and a given policy on the system call, the overhead         on the overall system performance, we analyze the call graph

## Page 10

    SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                                             Lim et al.

    associated with each system call (see § 4.1) to understand                                                 20
    LSM hook invocation patterns. We show the results for a few              LSM      LSM-BPF      saBPF
    system calls in Table 3 (note that for readability, we do not
    include hooks that are called when a system call fails/errs).                                              15

    5.2 saBPF overhead
    saBPF’s sources of overhead are fundamentally the same as                                                  10
    those of standard LSM security modules, i.e., hooking and
    execution (§ 5.1). Therefore, if a standard security module
    and saBPF implement the same policy, they incur roughly
    the same total overhead, except that saBPF incurs some ad-                                                 5
    ditional cost to traverse the cgroup hierarchy and to invoke
    the relevant eBPF programs (§ 3.1).
    In practice, however, there exists significant differences                                                 0
    in policy overhead between a standard security module and            socket  bind      listen        accept
    saBPF; saBPF offers time-saving convenience and flexibil-
    ity that a standard security module is unable to provide.            Figure 7: Overhead of the LSM, LSM-BPF, and saBPF
    To run a customized in-kernel LSM module, the Linux ker-             invocation mechanisms.
    nel must be modified. This requires thorough testing before
    the deployment of the custom kernel. It is common for av-            saBPF rather than a state-of-the-art monitoring system that
    erage users to shy away from the mere idea of deploying              modifies the Linux kernel, when performing exactly the same
    a kernel running heavily-customized code, especially one             functionality. Appendix A has more details on reproducing
    where said customized code interacts with the OS security            the results reported in this section.
    framework. To mitigate those issues, standard modules are
    typically designed to be general-purpose. For example, an            6.1  Overhead of Namespacing
    auditing module (e.g., CamFlow [51]) must be able to satisfy         We compare the overhead associated with different mecha-
    different auditing needs without requiring users to compile          nisms responsible for calling LSM hooks. We are interested
    their own custom kernel. To that end, the module must eval-          in the following three strategies: 1) the native LSM mecha-
    uate at runtime an extensive audit policy to determine what          nism with built-in functions (LSM); 2) LSM-BPF that attaches
    information it should log. As a concrete example, Bates et           an eBPF function to an LSM hook (LSM-BPF); and 3) saBPF
    al. [15] deploy policies to record events based on their secu-       that attaches eBPF programs at the intersection of a cgroup
    rity context as provided by SELinux. For each object involved        and an LSM hook (saBPF). We use ftrace [9] to perform the
    in a given event, the audit mechanism needs to retrieve its          measurement. To measure exclusively the cost of each call-
    security ID and compare it with the specified policy. While          ing mechanism, the function or program that is attached to
    the policy is relatively simple, the cumulative effects (as dis-     each hook performs no operations and simply returns. We
    cussed in § 5.1) on the policy have a significant impact on          capture the overhead of four common functions associated
    performance.                                                         with a UNIX server: socket, bind, listen, and accept. The
    On the other hand, saBPF-based solutions take into ac-               overhead is associated with the following four LSM hooks:
    count audit policy at compilation time, which significantly          security_socket_[create/bind/listen/accept]. The re-
    reduces run-time complexity and thus improves performance.           sults are shown in Fig. 7. We report overhead relative to a
    Moreover, since saBPF allows users to attach programs based          single baseline and focus on order-of-magnitude comparison,
    on cgroups, there is virtually no overhead imposed on appli-         because ftrace (or any similar kernel instrumentation tool)
    cations running outside of the targeted cgroup. This means,          can introduce additional overhead [9]. We use the overhead
    for example, that if a Kubernetes pod deploys a complex audit        of native LSM on the socket_create hook to normalize
    mechanism, the other pods on the system remain unaffected.           experimental results.
    6 PERFORMANCE EVALUATION                                             We see in Fig. 7 that the invocation overhead is nearly
                                                                         constant and independent of the system call. It is roughly
    In this section, we evaluate saBPF performance on a bare             10 and 15 times more costly with LSM-BPF and saBPF than
    metal machine with 16GiB of RAM and an Intel i7 CPU.                 with native LSM, respectively. The built-in LSM simply finds
    In § 6.1, we analyze the cost of hook invocation on saBPF.           the address of the LSM function in a hook table and calls
    Next, in § 6.2, we explore the performance gain from using           the function. The extra cost of LSM-BPF is related to the










Time (relative)

## Page 11

Secure Namespaced Kernel Audit for Containers                                          SoCC ’21, November 1–4, 2021, Seattle, WA, USA

                                                                   Test Type      vanilla CamFlow Overhead ProvBPF Overhead
Algorithm 1: Execute an eBPF program (simplified).                               Process tests (in    , the smaller the better)
1 // disallow task core migration and preemption                   NULL call           0.30      0.32            0%      0.29       0%
                                                                   NULL I/O            0.39      0.75            92%     0.54       38%
2 migrate_disable();                                               stat                1.04      3.77           263%     1.40       35%
3 rcu_read_lock();                                                 fstat               0.52      1.40           169%     0.66       28%
                                                                   open/close file     1.80      5.89           227%     2.62       46%
4 rc = run_bpf_programs();                                         read file           0.40      0.73            84%     0.56       42%
5 rcu_read_unlock();                                               write file          0.36      0.70            92%     0.53       53%
6 // allow task core migration and preemption                      fork process       295.55     344.15          13%     317.78     8%
                                                                        File and memory latency (in , the smaller the better)
7 migrate_enable();                                                file create (0k)    10.31     21.20          106%     13.10      27%
8 return rc;                                                       file delete (0k)    11.25     23.35          108%     12.80      14%
                                                                   file create (10k)   16.55     40.75          146%     20.65      25%
                                                                   file delete (10k)   13.45     30.20          125%     15.55      16%
                                                                   pipe latency        6.06      10.45           72%     6.55       8%
Algorithm 2: Execute an saBPF program (simpli-                     AF_UNIX latency     6.60      16.43          149%     9.72       47%
fied).                                                                  Table 4: lmbench results.
1 hierarchy = get_cgroup_hierarchy(current_task,
    hook_reference);
2 // disallow task core migration and preemption
3 migrate_disable();                                                (§ 6.2.1) and macro-benchmarks (§ 6.2.2). We demonstrate
4 rcu_read_lock();                                                  that ProvBPF outperforms the state-of-the-art whole-system
5 foreach cgroup in hierarchy do                                    provenance solution CamFlow [51] and incurs minimal per-
6         rc = run_bpf_programs();                                  formance overhead.
7         if rc then                                                We choose standard benchmarks such as lmbench, so that
    8       return rc;                                              saBPF can be meaningfully compared with prior and fu-
9 rcu_read_unlock();                                                ture work. We run each benchmark on three different kernel
10 // allow task core migration and preemption                      configurations. The vanilla configuration runs on the un-
11 migrate_enable();                                                modified mainline Linux kernel v5.11.2, which serves as our
12 return rc;                                                       baseline. The CamFlow configuration uses the same kernel
                                                                    but additionally instrumented with CamFlow kernel patches
                                                                    (v0.7.2) [4]. Finally, the ProvBPF workload corresponds to
cost of invoking an eBPF program. We show the simplified            the same Linux kernel but running with our eBPF-based
logic to execute an eBPF program in Alg. 1. While the over-         provenance capture mechanism ProvBPF. We also ensure
head of executing the eBPF program itself is relatively low         that ProvBPF’s and CamFlow’s configurations are equiva-
(close to executing a native function), handling read-copy-         lent.
update (RCU) [14] synchronization primitives and manipu-            6.2.1   Microbenchmark. We use lmbench [43] to measure
lating scheduler migration and preemption flags accounts            ProvBPF’s performance overhead on raw system calls, as
for the majority of the overhead.                                   reported in Table 4. We show only a relevant subset of per-
         As shown in Alg. 2, saBPF follows a similar logic, ex-     formance metrics due to space constraints, but the complete
cept that it incurs additional overhead when retrieving and         results are available online (see Appendix A).
traversing the cgroup hierarchy.                                    The overhead of ProvBPF, when compared to the vanilla
       However, we emphasize that these relative overheads must     kernel, is relatively low. In addition to the overhead intro-
be considered with respect to the cost of policy evaluation.        duced by the invocation mechanism, ProvBPF also incurs the
As a point of comparison, SELinux’s policy evaluation cost          cost of building the provenance graph elements and sending
of the socket_create hook is 2, 000 times larger than the           them to the user-space program. It outperforms CamFlow
invocation cost of native LSM. To better understand the ac-         as it is significantly streamlined. Indeed, CamFlow uses a
tual cost of running saBPF and to contextualize its overhead,       complex set of capture policies to allow users to tailor data
we perform both micro- and macro-benchmarks in the next             capture to their specific needs [51]. Evaluating the policy
section.                                                            at runtime can be relatively costly, especially since the ef-
6.2       Evaluating ProvBPF                                        fects can be cumulative (§ 5). In the case of ProvBPF, policy
                                                                    evaluation is performed at compilation time, so that the com-
To contextualize saBPF’s performance with a realistic work-         piled code only captures the desired events, thus significantly
load, we perform an evaluation of ProvBPF through micro-            reducing overhead given equivalent policies.

## Page 12

SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                                                                  Lim et al.

Test Type vanilla CamFlow Overhead ProvBPF           Overhead                             Date            Release      Long Term Support Changes
                Execution time (in seconds, the smaller the better)                       April 2021       5.12             No      4
unpack          6.52    7.70           18%     6.59     1%
build         194.26    232.01         19%    203.70    5%                                February 2021    5.11             No      3
4kB to 1MB file, 10 subdirectories,4k5 simultaneous transactions, 1M5 transactions        December 2020    5.10             Yes     2
postmark 79.50          113.00         42%     92.50    16%
                                                                                          October 2020      5.9             No      0
                         Table 5: Macrobenchmark results.                                 August 2020       5.8             No      4
                                                                                          May 2020          5.7             No      0
                                                                                          March 2020        5.6             No      0
Test Type                  vanilla     CamFlow Overhead ProvBPF Overhead                  January 2020      5.5             No      5
               Request/Operation per second (the higher the better)                       November 2019     5.4             Yes     1
apache httpd                 14645     10682      27%     13487        8%
redis (LPOP)               2105221    1780868     15%    1894961       10%                 Table 7: Changes made to the LSM ABI in terms of
redis (SADD)            2073489 1721367           17%    1854162       11%                 the number of interface function modified (including
redis (LPUSH)  1630446                1401497     14%    1510000       7%
redis (GET)             2360694 1928276           18%    2102901       11%                 name changes, parameter modifications, and additions
redis (SET)             1873359 1569507           16%    1690189       10%                 and deletions) since the latest release. We note that
memcache (ADD)               44122     30444      31%     41362        6%                  there is a total of 236 LSM hooks as of release 5.12.
memcache (GET)               67895     41363      39%     62167        8%
memcache (SET)               44460     30346      32%     41355        7%
memcache (APPEND) 46730                31157      33%     43215        8%
memcache (DELETE)            67761     40735      40%     61755        9%
php                         690725    613296      11%    709476        0%                  solutions such as Hi-Fi [54] and LPM [17]. We are not able
                   Execution time (in ms, the lower the better)
pybench                       1246     1298       4%      1196         0%                  to provide direct comparison with these solutions since they
                     Table 6: Extended macrobenchmark results.                             were implemented for extremely outdated kernels (release
                                                                                           2.6.32 from 2009 for LPM [16] and release 3.2.0 from 2011
                                                                                           for Hi-Fi [53]); internal kernel changes make it practically
                                                                                           impossible for us to port them to a modern kernel release.
6.2.2                               Macrobenchmark. We present two sets of macrobench-
              marks. The first set, as shown in Table 5, measures the                      7 DISCUSSION
               performance impact on a single machine when unpacking                       Security. We are aware of a number of security issues with
              and building the kernel and running the Postmark bench-                      eBPF (e.g., CVE [6] and CVE [7]). In many known attack sce-
             mark [39]. These are the common benchmarks used in prior                      narios related to eBPF, an attacker exploits the eBPF verifier
           provenance literature ever since Muniswamy-Reddy et al. [48]                    to make illegal modifications of kernel data structures, e.g.,
            introduced the concept of system provenance. Table 6 shows                     to perform privilege escalation [6]. One clear solution is to
             the results of the second set of benchmarks focusing on a                     improve the verification of eBPF programs [28, 50]. While
           set of applications typically used to build web applications.                   this is an important problem worthy of investigation, it is
             These benchmarks are not intended to cover every possible                     orthogonal to saBPF and therefore out of scope for this paper.
             scenario, but rather to provide meaningful points of com-                     We note that, to the best of our knowledge, saBPF does not
            parison. We rely on the Phoronix Test Suite [13] to perform                    introduce new attack vectors and that any improvement to
               these benchmarks. Details on benchmark parameters and                       eBPF security will benefit saBPF.
settings are available in our repository, see Appendix A.                                  Layering. In this work, we focus on capturing kernel-level
                               From the first set of benchmarks (Table 5), we see that     audit data that describes low-level system interactions. How-
              ProvBPF introduces between 1% and 16% overhead. Unpack                       ever, to fully understand application behavior, it is often
            and build workloads are computation heavy, and most of the                     useful to analyze audit information from multiple sources,
          execution time is spent in userspace. On the other hand, post-                   preferably from different layers of abstraction. For exam-
           mark spends a more significant portion of its execution time                    ple, layering both low-level system traces and higher-level
              in system call code. As ProvBPF only adds overhead when                      application traces can often facilitate attack investigation
            system calls are executed, it unsurprisingly performs worse                    by enabling forensic experts to identify, in an iterative fash-
            in the Postmark benchmark. In the second set of benchmarks                     ion, an attack point of entry [40]. The application of such
             (Table 6), we evaluate the impact of ProvBPF on applica-                      techniques is beyond the scope of this paper, but saBPF and
            tions that are often deployed through containers. ProvBPF’s                    any application built atop can be seamlessly integrated with
             overhead is between 0% and 11%. In all scenarios, ProvBPF                     existing layering techniques.
outperforms CamFlow.                                                                       Maintainability. One of the key advantages in building au-
                               We also note that ProvBPF results are in the same order     dit tools through eBPF and by extension saBPF is that they
              of magnitude as similar whole-system provenance capture                      can be heavily customized to fulfill the needs of the user.

## Page 13

Secure Namespaced Kernel Audit for Containers                            SoCC ’21, November 1–4, 2021, Seattle, WA, USA

As we previously pointed out, maintaining bespoke built-in           allow their functionality to be extended to secure auditing.
audit tools requires the developers to, at a minimum, 1) main-       Indeed, while these frameworks provide a wealth of infor-
tain a custom kernel, 2) prepare a custom OS distribution, and       mation, their capture methodology does not provide strong
3) perform extensive testing before actual deployment. This          enough guarantees in the presence of an attacker. Further-
burden is greatly alleviated using our proposed solution. The        more, saBPF enables the implementation of decentralized
audit mechanism is neatly separated from the OS and can be           solutions that need not be managed by the host platform.
built and tested independently. Furthermore, with BTF and            LSM. The LSM framework [46] was introduced nearly two
CO-RE[49], any solution built with saBPF does not need to            decades ago to Linux for Mandatory Access Control (MAC).
be built against a specific version of the kernel; it only needs     Two of the most popular applications of LSM are AppAr-
to be rebuilt (and updated) when the kernel’s internal LSM           mor [2] and SELinux [58]. Over the years, the LSM frame-
ABI changes, which is rare (Table 7). We note that a number          work has seen its usage extended to implementing mecha-
of popular distributions ship only Long Term Support kernel          nisms such as the Linux Integrity Measurement Architec-
versions, which further simplifies maintenance.                      ture [55], which enables hardware-based integrity attesta-
                                                                     tion, and loadpin [20], which was developed to restrict the ori-
8 RELATED WORK                                                       gin of kernel-loaded code to read-only devices in ChromeOS.
                                                                     LSM has also been used to implement secure auditing as
saBPF is designed mostly for monitoring containers in the            previously mentioned [17, 51, 54]. These work is orthogonal
cloud and uses two major technologies, eBPF and LSM. We              to saBPF; instead, saBPF is closely related to prior work that
discuss related work in these areas.                                 attempted to allow namespacing and stacking of LSM mod-
eBPF-based Security. In system security, one of the well-            ules [38, 60]. They focused on enabling containers to define
known eBPF-enabled applications is seccomp-bpf, which                their own security policy within a system-wide MAC scheme.
filters system calls available for user-space applications to        For example, Sun et al. [60] make AppArmor namespace-
reduce kernel attack surface [21]. seccomp filters use BPF           aware so that each individual container can have its own
programs to decide, based on the system call number and              policy to be enforced by the host. This is a non-trivial task
arguments, whether a given call is allowed or not. A more            involving conflict resolution alongside the security names-
recent application of eBPF is LBM [62], which protects the           pace hierarchy. saBPF expends on such ideas by allowing
Linux kernel from malicious peripherals such as USB, Blue-           containers to provide not only their own policy, but also
tooth, and NFC. LBM places interposition hooks, through the          their own totally separate mechanisms.
implementation of new eBPF program types, right beneath
a peripheral’s protocol stack and above the peripheral’s con-
troller driver, so that it can guarantee that eBPF programs          9 CONCLUSION
can filter all inputs from the device and all outputs from the       We present saBPF, a lightweight system-level auditing frame-
host. LBM introduces a new filter language for peripherals           work for container-based cloud environments. saBPF is built
to enforce programmable security policies.                           upon the widely-used eBPF framework. It is simple to use
LSM-BPF is still a nascent eBPF extension, emerging from             and allows individual containers to deploy – in a decentral-
Kernel Runtime Security Instrumentation (KRSI) [57]. KRSI            ized manner – secure auditing tools. These tools in turn
enables privileged users to dynamically update MAC and               enable users to implement a wide range of security solutions
audit policies based on the state of the computing environ-          on container-oriented cloud platforms, such as intrusion de-
ment. bpfbox [24] uses LSM-BPF to create process sandboxes           tection systems for individual containers. Using saBPF, we
through a flexible policy language. BPFContain [23] uses             were able to re-implement a state-of-the-art audit system that
LSM-BPF to enforce system-wide policy to control container           provides exactly the same functionality while significantly
IPC, and file and network access. They both leverage eBPF            improving performance. We open-source saBPF, welcoming
because it is easier to maintain and further develop eBPF            the community to develop and deploy toolsets that leverage
programs than to use out-of-tree LSMs for their particular           our system, in hopes of further discovering the potentials of
needs. saBPF is orthogonal to these systems and focuses              saBPF.
on leveraging eBPF at the intersection of cgroup and LSM
hooks, mainly but not exclusively for secure auditing.
Monitoring Containers. There are a number of widely                  A AVAILABILITY
available solutions, such as Cilium [5], Grafana [10], and
Nagios [11], that monitor containers, but they focus primar-         Our implementation (§ 3) and instructions to reproduce the
ily on performance and/or network traffic monitoring. We             results presented (§ 6) are available at https://github.com/
design saBPF not to compete with these solutions, but to             saBPF-project.

## Page 14

SoCC ’21, November 1–4, 2021, Seattle, WA, USA                                                                                                      Lim et al.

REFERENCES                                                                                [26] Ashish Gehani and Dawood Tariq. 2012. SPADE: Support for Prove-
[1] [n.d.].     Apche Kafka. online (accessed 7th October 2021).        https:     nance Auditing in Distributed Environments. In International Middle-
//kafka.apache.org/.                                                               ware Conference. Springer-Verlag, 101–120.
[2] [n.d.].          AppArmor. online (accessed 7th October 2021).    https://         [27] Laurent Georget, Mathieu Jaume, Frédéric Tronel, Guillaume Piolle,
apparmor.net/.                                                                     and Valérie Viet Triem Tong. 2017. Verifying the reliability of operating
[3] [n.d.].        BPF ring buffer. online (accessed 7th October 2021). https:     system-level information flow control systems in linux. In International
//www.kernel.org/doc/html/latest/bpf/ringbuf.html.                                 FME Workshop on Formal Methods in Software Engineering (FormaliSE).
[4] [n.d.].     CamFlow.       online (accessed 7th October 2021).      https:     IEEE, 10–16.
//camflow.org/.                                                                             [28] Elazar Gershuni, Nadav Amit, Arie Gurfinkel, Nina Narodytska,
   [5] [n.d.]. Cilium. online (accessed 7th October 2021). https://cilium.io/.     Jorge A Navas, Noam Rinetzky, Leonid Ryzhyk, and Mooly Sagiv. 2019.
[6] [n.d.].          CVE-2020-8835. online (accessed 7th October 2021). https:     Simple and precise static analysis of untrusted linux kernel extensions.
//cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8835.                            In Conference on Programming Language Design and Implementation
[7] [n.d.].         CVE-2021-29154. online (accessed 7th October 2021). https:     (PLDI’19). ACM, 1069–1084.
//cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-29154.                                     [29] Xueyuan Han, Thomas Pasquier, Adam Bates, James Mickens, and
[8] [n.d.]. eBPF. online (accessed 7th October 2021). https://ebpf.io/.            Margo Seltzer. 2020. UNICORN: Runtime Provenance-based Detector
[9] [n.d.].          ftrace documentation. online (accessed 7th October 2021).     for Advanced Persistent Threats. In Network and Distributed System
https://www.kernel.org/doc/html/v4.17/trace/ftrace.html.                           Security Symposium (NDSS’20). Internet Society.
[10] [n.d.].     Grafana.      online (accessed 7th October 2021).      https:            [30] Xueyuan Han, Thomas Pasquier, Tanvi Ranjan, Mark Goldstein, and
//grafana.com/.                                                                    Margo Seltzer. 2017. Frappuccino: Fault-detection through runtime
[11] [n.d.].    Nagios.      online (accessed 7th October 2021).      https://     analysis of provenance. In Workshop on Hot Topics in Cloud Computing
www.nagios.org/.                                                                   (HotCloud’17). USENIX.
    [12] [n.d.]. Open Policy Agent. online (accessed 7th October 2021). https:             [31] Xueyuan Han, Xiao Yu, Thomas Pasquier, Ding Li, Junghwan Rhee,
//www.openpolicyagent.org/.                                                        James Mickens, Margo Seltzer, and Haifeng Chen. 2021. SIGL: Secur-
  [13] [n.d.]. Phoronix test suite. online (accessed 7th October 2021). https:     ing Software Installations Through Deep Graph Learning. In Security
//www.phoronix-test-suite.com/.                                                    Symposium. USENIX.
[14] 2021.      RCU.     online (accessed 7th October 2021).          https://               [32] Wajih Ul Hassan, Lemay Aguse, Nuraini Aguse, Adam Bates, and
www.kernel.org/doc/Documentation/RCU/whatisRCU.txt.                                Thomas Moyer. 2018. Towards scalable cluster auditing through gram-
           [15] Adam Bates, Kevin RB Butler, and Thomas Moyer. 2015. Take only     matical inference over provenance graphs. In Network and Distributed
what you need: leveraging mandatory access control policy to reduce                Systems Security Symposium (NDSS’18).
provenance storage costs. In Workshop on the Theory and Practice of                        [33] Wajih Ul Hassan, Adam Bates, and Daniel Marino. 2020. Tactical
Provenance (TaPP 15). USENIX.                                                      Provenance Analysis for Endpoint Detection and Response Systems.
           [16] Adam Bates, Dave Jing Tian, Kevin RB Butler, and Thomas Moyer.     In Symposium on Security and Privacy (S&P’20). IEEE.
[n.d.]. LPM source code. online (accessed 7th October 2021). https:                      [34] Wajih Ul Hassan, Mohammad Ali Noureddine, Pubali Datta, and Adam
//bitbucket.org/uf_sensei/redhat-linux-provenance-release/.                        Bates. 2020. OmegaLog: High-fidelity attack investigation via trans-
           [17] Adam Bates, Dave Jing Tian, Kevin RB Butler, and Thomas Moyer.     parent multi-layer log analysis. In Network and Distributed System
2015. Trustworthy whole-system provenance for the linux kernel. In                 Security Symposium. Internet Society.
Security Symposium. USENIX, 319–334.                                                      [35] Tejun Heo. [n.d.]. Control Group v2. online (accessed 7th Octo-
        [18] Khalid Belhajjame, Reza B’Far, James Cheney, Sam Coppens, Stephen     ber 2021).  https://www.kernel.org/doc/html/latest/admin-guide/
Cresswell, Yolanda Gil, Paul Groth, Graham Klyne, Timothy Lebo, Jim                cgroup-v2.html.
McCusker, Simon Miles, James Myers, and Satya Sahoo. 2013. PROV-                       [36] Trent Jaeger, Antony Edwards, and Xiaolan Zhang. 2004. Consistency
DM: The PROV Data Model. Technical Report. W3C.                                    analysis of authorization hook placement in the Linux security mod-
         [19] Sheung Chi Chan, James Cheney, Pramod Bhatotia, Thomas Pasquier,     ules framework. ACM Transactions on Information and System Security
Ashish Gehani, Hassaan Irshad, Lucian Carata, and Margo Seltzer.                   (TISSEC) 7, 2 (2004), 175–205.
2019. ProvMark: a provenance expressiveness benchmarking system.                      [37] Hai Jin, Zhi Li, Deqing Zou, and Bin Yuan. 2019. Dseom: A framework
In International Middleware Conference. ACM/IFIP, 268–279.                         for dynamic security evaluation and optimization of MTD in container-
      [20] Jonathan Corbet. 2016. LoadPin. online (accessed 7th October 2021).     based cloud. IEEE Transactions on Dependable and Secure Computing
https://lwn.net/Articles/682302/.                                                  (2019).
[21] Jake Edge. 2015. A seccomp overview. Linux Weekly News (2015).                     [38] John Johansen and Casey Schaufler. 2017. Namespacing and Stacking
           [22] Antony Edwards, Trent Jaeger, and Xiaolan Zhang. 2002. Runtime     the LSM. In Linux Plumbers Conference.
verification of authorization hook placement for the Linux security               [39] Jeffrey Katcher. 1997. Postmark: A new file system benchmark. Technical
modules framework. In Conference on Computer and Communications                    Report. Technical Report TR3022, Network Appliance.
Security (CCS’02). ACM, 225–234.                                                             [40] Kyu Hyung Lee, Xiangyu Zhang, and Dongyan Xu. 2013. High Ac-
     [23] William Findlay, David Barrera, and Anil Somayaji. 2021. BPFContain:     curacy Attack Provenance via Binary-based Execution Partition. In
Fixing the Soft Underbelly of Container Security. arXiv (2021).                    Network and Distributed System Security Symposium (NDSS’13). Inter-
         [24] William Findlay, Anil Somayaji, and David Barrera. 2020. bpfbox:     net Society.
Simple Precise Process Confinement with eBPF. In Cloud Computing                          [41] Fucheng Liu, Yu Wen, Dongxue Zhang, Xihe Jiang, Xinyu Xing, and
Security Workshop (CCSW). ACM, 91–103.                                             Dan Meng. 2019. Log2vec: a heterogeneous graph embedding based
         [25] Xing Gao, Zhongshu Gu, Mehmet Kayaalp, Dimitrios Pendarakis, and     approach for detecting cyber threats within enterprise. In Conference
Haining Wang. 2017. ContainerLeaks: Emerging security threats of                   on Computer and Communications Security (CCS’19). ACM, 1777–1794.
information leakages in container clouds. In International Conference                     [42] Emaad Manzoor, Sadegh M Milajerdi, and Leman Akoglu. 2016. Fast
on Dependable Systems and Networks (DSN’17). IEEE/IFIP, 237–248.                   memory-efficient anomaly detection in streaming heterogeneous
                                                                                   graphs. In International Conference on Knowledge Discovery and Data

## Page 15

Secure Namespaced Kernel Audit for Containers                                     SoCC ’21, November 1–4, 2021, Seattle, WA, USA

Mining (KDD’16). ACM, 1035–1044.                                                  [56] Z Cliffe Schreuders, Tanya McGill, and Christian Payne. 2011. Em-
   [43] Larry W McVoy, Carl Staelin, et al. 1996. lmbench: Portable Tools     powering end users to confine their own applications: The results of a
for Performance Analysis. In Annual Technical Conference (ATC’96).            usability study comparing SELinux, AppArmor, and FBAC-LSM. ACM
USENIX, 279–294.                                                              Transactions on Information and System Security (TISSEC) 14, 2 (2011),
       [44] Sadegh M. Milajerdi, Birhanu Eshete, Rigel Gjomemo, and V. N.     1–28.
Venkatakrishnan. 2019. Poirot: Aligning Attack Behavior with Kernel                 [57] KP Singh. 2019. Kernel Runtime Security Instrumentation. online
Audit Records for Cyber Threat Hunting. In Conference on Computer             (accessed 7th October 2021). https://lwn.net/Articles/798918/.
and Communications Security (CCS’19). ACM.                                        [58] Stephen Smalley, Chris Vance, and Wayne Salamon. 2001. Implement-
     [45] Sadegh M Milajerdi, Rigel Gjomemo, Birhanu Eshete, Ramachandran     ing SELinux as a Linux security module. NAI Labs Report 1, 43 (2001),
Sekar, and VN Venkatakrishnan. 2019. Holmes: real-time apt detection          139.
through correlation of suspicious information flows. In Symposium on            [59] Stephen Soltesz, Herbert Pötzl, Marc E Fiuczynski, Andy Bavier, and
Security and Privacy (S&P’19). IEEE, 1137–1152.                               Larry Peterson. 2007. Container-based operating system virtualization:
  [46] James Morris, Stephen Smalley, and Greg Kroah-Hartman. 2002. Linux     a scalable, high-performance alternative to hypervisors. In European
Security Modules: General Security Support for the Linux Kernel. In           Conference on Computer Systems (EuroSys’07). ACM, 275–287.
Security Symposium. USENIX.                                                    [60] Yuqiong Sun, David Safford, Mimi Zohar, Dimitrios Pendarakis, Zhong-
   [47] Thomas Moyer and Vijay Gadepally. 2016. High-throughput ingest of     shu Gu, and Trent Jaeger. 2018. Security namespace: making linux
data provenance records into Accumulo. In High Performance Extreme            security frameworks available to containers. In Security Symposium.
Computing Conference (HPEC’16). IEEE, 1–6.                                    USENIX.
        [48] Kiran-Kumar Muniswamy-Reddy, David A Holland, Uri Braun, and          [61] Yutao Tang, Ding Li, Zhichun Li, Mu Zhang, Kangkook Jee, Xusheng
Margo Seltzer. 2006. Provenance-aware Storage Systems. In Annual              Xiao, Zhenyu Wu, Junghwan Rhee, Fengyuan Xu, and Qun Li. 2018.
Technical Conference (ATC’06). USENIX, 43–56.                                 NodeMerge: Template Based Efficient Data Reduction For Big-Data
[49] Andrii Nakryiko. [n.d.]. BPF Portability and CO-RE. online (accessed     Causality Analysis. In Conference on Computer and Communications
7th October 2021).  https://facebookmicrosites.github.io/bpf/blog/            Security (CCS’18). ACM, 1324–1337.
2020/02/19/bpf-portability-and-co-re.html.                                   [62] Dave Jing Tian, Grant Hernandez, Joseph I Choi, Vanessa Frost, Peter C
     [50] Luke Nelson, Jacob Van Geffen, Emina Torlak, and Xi Wang. 2020.     Johnson, and Kevin RB Butler. 2019. LBM: a security framework for
Specification and verification in the field: Applying formal methods          peripherals within the linux kernel. In Symposium on Security and
to BPF just-in-time compilers in the Linux kernel. In Symposium on            Privacy (S&P’19). IEEE, 967–984.
Operating Systems Design and Implementation (OSDI’20). USENIX, 41–                    [63] Kennedy A Torkura, Muhammad IH Sukmana, and Christoph Meinel.
61.                                                                           2017. Integrating continuous security assessments in microservices
         [51] Thomas Pasquier, Xueyuan Han, Mark Goldstein, Thomas Moyer,     and cloud native applications. In International Conference on Utility
David Eyers, Margo Seltzer, and Jean Bacon. 2017. Practical Whole-            and Cloud Computing (UCC’17). IEEE/ACM, 171–180.
System Provenance Capture. In Symposium on Cloud Computing                   [64] Veritis. 2019.  State of Containers Report 2019: ‘Security’ Re-
(SoCC’17). ACM.                                                               mains A Challenge!  online (accessed 7th October 2021).
     [52] Thomas Pasquier, Xueyuan Han, Thomas Moyer, Adam Bates, Olivier     https://www.veritis.com/blog/state-of-containers-report-2019-
Hermant, David Eyers, Jean Bacon, and Margo Seltzer. 2018. Runtime            security-remains-a-challenge/.
Analysis of Whole-System Provenance. In Conference on Computer and                 [65] Qi Wang, Wajih Ul Hassan, Ding Li, Kangkook Jee, Xiao Yu, Kexuan
Communications Security (CCS’18). ACM.                                        Zou, Junghwan Rhee, Zhengzhang Chen, Wei Cheng, Carl A. Gunter,
      [53] Devin J Pohly, Stephen McLaughlin, Patrick McDaniel, and Kevin     and Haifeng Chen. 2020. You Are What You Do: Hunting Stealthy
Butler. [n.d.]. Hi-Fi source code. online (accessed 7th October 2021).        Malware via Data Provenance Analysis. In Network and Distributed
https://github.com/djpohly/linux.                                             System Security (NDSS’20). Internet Society.
      [54] Devin J Pohly, Stephen McLaughlin, Patrick McDaniel, and Kevin         [66] Robert NM Watson. 2007. Exploiting Concurrency Vulnerabilities in
Butler. 2012. Hi-Fi: Collecting High-fidelity Whole-system Provenance.        System Call Wrappers. Workshop on Offensive Technologies (WOOT’07)
In Annual Computer Security Applications Conference (ACSAC’12). ACM,          7 (2007), 1–8.
259–268.                                                                       [67] Robert NM Watson. 2013. A decade of OS access-control extensibility.
 [55] Reiner Sailer, Xiaolan Zhang, Trent Jaeger, and Leendert Van Doorn.     ACM Queue 11, 1 (2013), 20–41.
2004. Design and Implementation of a TCG-based Integrity Measure-               [68] Wenhui Zhang, Peng Liu, and Trent Jaeger. 2021. Analyzing the Over-
ment Architecture. In Security Symposium, Vol. 13. USENIX, 223–238.           head of File Protection by Linux Security Modules. In Asia Conference
                                                                              on Computer and Communications Security (AsiaCCS’21). ACM, 393–
                                                                              406.

## Related pages

- [[linux-ebpf-fundamentals]]

## Source

- Local path: `[[papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf]]`
