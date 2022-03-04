
## 什么是eBPF？

Linux内核一直是实现监视/可观察性，网络和安全性的理想场所。不幸的是，这通常是不切实际的，因为它需要更改内核源代码或加载内核模块，并导致彼此堆叠的抽象层。
eBPF是一项革命性的技术，可以在Linux内核中运行沙盒程序，而无需更改内核源代码或加载内核模块。
通过使Linux内核可编程，基础架构软件可以利用现有的层，从而使它们更加智能和功能丰富，而无需继续为系统增加额外的复杂性层。

eBPF导致了网络，安全性，应用程序配置/跟踪和性能故障排除等领域的新一代工具的开发，这些工具不再依赖现有的内核功能，而是在不影响执行效率或安全性的情况下主动重新编程运行时行为。

如果直接解释eBPF，有点不明所以。那我们就看看有哪些基于eBPF的工程，这些工程或许你已经知道，或是已经经常使用，也许你会明白eBPF距离我们并不遥远。

## eBPF 发展

* BPF
Berkeley Packet Filter, capturing and filtering network packets that matched specific rules.
Filters are implemented as programs to be run on a register-based virtual machine.

-> tcpdump


## eBPF 运行机制简介
* 
* JIT


## 主要用途


## 横向扩展& 相关技术

## 基于eBPF的项目

1： bcc

BCC是用于创建基于eBPF的高效内核跟踪和操作程序的工具包，其中包括一些有用的命令行工具和示例。
BCC简化了用C进行内核检测的eBPF程序的编写，包括LLVM的包装器以及Python和Lua的前端。它还提供了用于直接集成到应用程序中的高级库。

2： bpftrace

bpftrace是Linux eBPF的高级跟踪语言。它的语言受awk和C以及DTrace和SystemTap等以前的跟踪程序的启发。 
bpftrace使用LLVM作为后端将脚本编译为eBPF字节码，并利用BCC作为与Linux eBPF子系统以及现有Linux跟踪功能和连接点进行交互的库。

3： Katran

Katran是一个C ++库和eBPF程序，用于构建高性能的第4层负载平衡转发平面。 
Katran利用Linux内核中的XDP基础结构来提供用于快速数据包处理的内核功能。它的性能与NIC接收队列的数量成线性比例，并且使用RSS友好的封装转发到L7负载平衡器。

6： Sysdig

Sysdig是提供深层系统可见性的简单工具，并具有对容器的原生支持。


## 如何编写一个eBPF程序？

在很多情况下，不是直接使用eBPF，而是通过Cilium，bcc或bpftrace等项目间接使用eBPF，这些项目在eBPF之上提供了抽象，并且不需要直接编写程序，而是提供了指定基于意图的定义的功能，然后使用eBPF实施。

如果不存在更高级别的抽象，则需要直接编写程序。 Linux内核希望eBPF程序以字节码的形式加载。
虽然当然可以直接编写字节码，但更常见的开发实践是利用LLVM之类的编译器套件将伪C代码编译为eBPF字节码。

在编写eBPF程序之前，需要简单了解几个概念。

1）map(映射) ： 
BPF最令人着迷的方面之一是，内核上运行的代码和加载了该代码的程序可以在运行时使用消息传递相互通信。

BPF映射是驻留在内核中的键/值存储。任何BPF程序都可以访问它们。在用户态中运行的程序也可以使用文件描述符访问这些映射。只要事先正确指定数据大小，就可以在映射中存储任何类型的数据。内核将键和值视为二进制 blobs，它并不关心您在映射中保留的内容。

BPF验证程序包括多种保护措施，以确保您创建和访问映射的方式是安全的。当我们解释如何访问这些映射中的数据时，我们也将解释这些保护措施。

当然BPF映射类型有很多，比如哈希表映射，数组映射，Cgroup 数组映射等，分别满足不同的场景。

2）验证器

BPF验证程序也是在您的系统上运行的程序，因此，对其进行严格审查是确保其正确执行工作的目标。

验证程序执行的第一项检查是对VM即将加载的代码的静态分析。第一次检查的目的是确保程序有预期的结果。
为此，验证程序将使用代码创建有向循环图（DAG）。验证程序分析的每个指令将成为图中的一个节点，并且每个节点都链接到下一条指令
。验证程序生成此图后，它将执行深度优先搜索（DFS），以确保程序完成并且代码不包含危险路径。这意味着它将遍历图的每个分支，一直到分支的底部，以确保没有递归循环。

这些是验证器在第一次检查期间可能拒绝您的代码的情形，要求有以下几个方面：

    该程序不包含控制循环。为确保程序不会陷入无限循环，验证程序会拒绝任何类型的控制循环。已经提出了在BPF程序中允许循环的建议，但是截至撰写本文时，没有一个被采用。
    该程序不会尝试执行超过内核允许的最大指令数的指令。此时，可执行的最大指令数为4,096。此限制是为了防止BPF永远运行。在第3章，我们讨论如何嵌套不同的BPF程序，以安全的方式解决此限制。
    该程序不包含任何无法访问的指令，例如从未执行过的条件或功能。这样可以防止在VM中加载无效代码，这也会延迟BPF程序的终止。
    该程序不会尝试越界。

验证者执行的第二项检查是BPF程序的空运行。这意味着验证者将尝试分析程序将要执行的每条指令，以确保它不会执行任何无效的指令。
此执行还将检查所有内存指针是否均已正确访问和取消引用。最后，空运行向验证程序通知程序中的控制流，以确保无论程序采用哪个控制路径，它都会到达BPF_EXIT指令。
为此，验证程序会跟踪堆栈中所有访问过的分支路径，并在采用新路径之前对其进行评估，以确保它不会多次访问特定路径。
经过这两项检查后，验证者认为程序可以安全执行。

3) hook ： 
由于eBPF是事件驱动的，所以ebpf是作用于具体的hook的。根据不同的作用，常用的有XDP，trace，套接字等。

4）帮助函数：
eBPF程序无法调用任意内核功能。允许这样做会将eBPF程序绑定到特定的内核版本，并使程序的兼容性复杂化。
取而代之的是，eBPF程序可以调用帮助函数，该函数是内核提供的众所周知且稳定的API。
总结

安全，网络，负载均衡，故障分析，追踪等领域都是eBPF的主战场。

### Q&A
```c
SEC("tracepoint/xdp/xdp_devmap_xmit")
```

类型为tracepoint的BPF程序的节名采用以下格式：

```c
tracepoint/<category>/<name>
```

name是跟踪点本身的名称。跟踪点按类别组织。您可以使用`bpftrace list '<category>:*'`列出类别的所有跟踪点。


## tracing

### dynamic tracing
kprobe / kretprobes
* 用于跟踪内核函数调用，是一种功能强大的探针类型
* Kprobes通常在内核函数执行前插入eBPF程序
* kretprobes则在内核函数执行完毕返回之后，插入相应的eBPF程序

> 如果对tcp_connect()使用kprobes探针，则对应的eBPF程序会在tcp_connect() 被调用时执行，
> 而如果是使用kretprobes探针，则eBPF程序会在tcp_connect() 执行返回时执行
> 可能在内核不同的版本之间发生变化。如果内核版本不同，内核函数名、参数、返回值等可能会变化

Uprobes/Uretprobes
在用户态对函数进行

### static tracing
tracepoints  
* 在内核代码中所做的一种静态标记
* 在`/sys/kernel/debug/tracing/events/`目录下，可以查看当前版本的内核支持的所有Tracepoints，在每一个具体Tracepoint目录下，都会有一系列对其进行配置说明的文件，比如可以通过enable中的值，来设置该Tracepoint探针的开关等。

与Kprobes相比，他们的主要区别在于，Tracepoints是内核开发人员已经在内核代码中提前埋好的，这也是为什么称它们为静态探针的原因。而kprobes更多的是跟踪内核函数的进入和返回，因此将其称为动态的探针。但是内核函数会随着内核的发展而出现或者消失，因此kprobes对内核版本有着相对较强的依赖性，前文也有提到，针对某个内核版本实现的追踪代码，对于其它版本的内核，很有可能就不工作了。



* BCC 提供了更高阶的抽象，可以让用户采用 Python、C++ 和 Lua 等高级语言快速开发 BPF 程序；
* BPFTrace 采用类似于 awk 语言快速编写 eBPF 程序；


## android

FirewallController.cpp里enableChildChains发现调用的是bpf，而不是传统的iptables

Andoird 9以后的网络统计和网络收发数据管控（过滤）功能实现主要是使用了eBPF中skfilter和cgroupskb的program type。这部分代码都是在system/netd/bpf_progs/netd.c 中实现的。


# 统计进程调用 sys_enter 的次数
#bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'

# 统计内核中函数堆栈的次数
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'



## android R 

map_clatd_clat_egress_map      
map_netd_uid_owner_map                 
map_time_in_state_policy_nr_active_map      
prog_netd_cgroupsock_inet_create
map_clatd_clat_ingress_map     
map_netd_uid_permission_map            
map_time_in_state_uid_concurrent_times_map  
prog_netd_skfilter_blacklist_xtbpf
map_netd_app_uid_stats_map     
map_offload_tether_ingress_map         
map_time_in_state_uid_last_update_map       
prog_netd_skfilter_egress_xtbpf
map_netd_configuration_map     
map_offload_tether_limit_map           
map_time_in_state_uid_time_in_state_map     
prog_netd_skfilter_ingress_xtbpf
map_netd_cookie_tag_map        
map_offload_tether_stats_map           
prog_clatd_schedcls_egress_clat_ether       
prog_netd_skfilter_whitelist_xtbpf
map_netd_iface_index_name_map  
map_time_in_state_cpu_last_update_map  
prog_clatd_schedcls_egress_clat_rawip       
prog_offload_schedcls_ingress_tether_ether
map_netd_iface_stats_map       
map_time_in_state_cpu_policy_map       
prog_clatd_schedcls_ingress_clat_ether      
prog_offload_schedcls_ingress_tether_rawip
map_netd_stats_map_A           
map_time_in_state_freq_to_idx_map      
prog_clatd_schedcls_ingress_clat_rawip      
prog_time_in_state_tracepoint_power_cpu_frequency
map_netd_stats_map_B           
map_time_in_state_nr_active_map        
prog_netd_cgroupskb_egress_stats            
prog_time_in_state_tracepoint_sched_sched_switch
