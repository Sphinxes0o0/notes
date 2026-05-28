# 理解内核

Linux 内核既不是进程、守护进程（daemon），也不是应用程序。
它是一个具有特权的、驻留在内存中的环境，构成了操作系统的基础。
与用户程序不同，它不被调度，没有进程标识符（PID），也不像传统任务那样启动或停止。
相反，它始终存在——在引导时加载到内存中——并管理硬件和软件之间的所有交互。

内核在 start_kenrel() 中开始执行;
```c
// init/main.c
asmlinkage __visible __init __no_sanitize_address __noreturn __no_stack_protector
void start_kernel(void)
{
	char *command_line;
	char *after_dashes;

	set_task_stack_end_magic(&init_task);
	smp_setup_processor_id();
	debug_objects_early_init();
	init_vmlinux_build_id();
	cgroup_init_early();
	local_irq_disable();
	early_boot_irqs_disabled = true;
	/*
	 * Interrupts are still disabled. Do necessary setups, then
	 * enable them.
	 */
	boot_cpu_init();
	page_address_init();
	pr_notice("%s", linux_banner);
	setup_arch(&command_line);
	/* Static keys and static calls are needed by LSMs */
	jump_label_init();
	static_call_init();
	early_security_init();
	setup_boot_config();
	setup_command_line(command_line);
	setup_nr_cpu_ids();
	setup_per_cpu_areas();
	smp_prepare_boot_cpu();	/* arch-specific boot-cpu hooks */
	early_numa_node_init();
	boot_cpu_hotplug_init();

	pr_notice("Kernel command line: %s\n", saved_command_line);
	/* parameters may set static keys */
	parse_early_param();
	after_dashes = parse_args("Booting kernel",
				  static_command_line, __start___param,
				  __stop___param - __start___param,
				  -1, -1, NULL, &unknown_bootoption);
	print_unknown_bootoptions();
	if (!IS_ERR_OR_NULL(after_dashes))
		parse_args("Setting init args", after_dashes, NULL, 0, -1, -1,
			   NULL, set_init_arg);
	if (extra_init_args)
		parse_args("Setting extra init args", extra_init_args,
			   NULL, 0, -1, -1, NULL, set_init_arg);

	/* Architectural and non-timekeeping rng init, before allocator init */
	random_init_early(command_line);
	/*
	 * These use large bootmem allocations and must precede
	 * initalization of page allocator
	 */
	setup_log_buf(0);
	vfs_caches_init_early();
	sort_main_extable();
	trap_init();
	mm_core_init();
	poking_init();
	ftrace_init();
	/* trace_printk can be enabled here */
	early_trace_init();
	/*
	 * Set up the scheduler prior starting any interrupts (such as the
	 * timer interrupt). Full topology setup happens at smp_init()
	 * time - but meanwhile we still have a functioning scheduler.
	 */
	sched_init();
	if (WARN(!irqs_disabled(),
		 "Interrupts were enabled *very* early, fixing it\n"))
		local_irq_disable();
	radix_tree_init();
	maple_tree_init();
	/*
	 * Set up housekeeping before setting up workqueues to allow the unbound
	 * workqueue to take non-housekeeping into account.
	 */
	housekeeping_init();
	/*
	 * Allow workqueue creation and work item queueing/cancelling
	 * early.  Work item execution depends on kthreads and starts after
	 * workqueue_init().
	 */
	workqueue_init_early();
	rcu_init();
	kvfree_rcu_init();
	/* Trace events are available after this */
	trace_init();
	if (initcall_debug)
		initcall_debug_enable();

	context_tracking_init();
	/* init some links before init_ISA_irqs() */
	early_irq_init();
	init_IRQ();
	tick_init();
	rcu_init_nohz();
	timers_init();
	srcu_init();
	hrtimers_init();
	softirq_init();
	timekeeping_init();
	time_init();
	/* This must be after timekeeping is initialized */
	random_init();
	/* These make use of the fully initialized rng */
	kfence_init();
	boot_init_stack_canary();
	perf_event_init();
	profile_init();
	call_function_init();
	WARN(!irqs_disabled(), "Interrupts were enabled early\n");
	early_boot_irqs_disabled = false;
	local_irq_enable();
	kmem_cache_init_late();
	/*
	 * HACK ALERT! This is early. We're enabling the console before
	 * we've done PCI setups etc, and console_init() must be aware of
	 * this. But we do want output early, in case something goes wrong.
	 */
	console_init();
	if (panic_later)
		panic("Too many boot %s vars at `%s'", panic_later,
		      panic_param);

	lockdep_init();
	/*
	 * Need to run this when irqs are enabled, because it wants
	 * to self-test [hard/soft]-irqs on/off lock inversion bugs
	 * too:
	 */
	locking_selftest();
#ifdef CONFIG_BLK_DEV_INITRD
	if (initrd_start && !initrd_below_start_ok &&
	    page_to_pfn(virt_to_page((void *)initrd_start)) < min_low_pfn) {
		pr_crit("initrd overwritten (0x%08lx < 0x%08lx) - disabling it.\n",
		    page_to_pfn(virt_to_page((void *)initrd_start)),
		    min_low_pfn);
		initrd_start = 0;
	}
#endif
	setup_per_cpu_pageset();
	numa_policy_init();
	acpi_early_init();
	if (late_time_init)
		late_time_init();
	sched_clock_init();
	calibrate_delay();
	arch_cpu_finalize_init();
	pid_idr_init();
	anon_vma_init();
	thread_stack_cache_init();
	cred_init();
	fork_init();
	proc_caches_init();
	uts_ns_init();
	key_init();
	security_init();
	dbg_late_init();
	net_ns_init();
	vfs_caches_init();
	pagecache_init();
	signals_init();
	seq_file_init();
	proc_root_init();
	nsfs_init();
	pidfs_init();
	cpuset_init();
	mem_cgroup_init();
	cgroup_init();
	taskstats_init_early();
	delayacct_init();
	acpi_subsystem_init();
	arch_post_acpi_subsys_init();
	kcsan_init();
	/* Do the rest non-__init'ed, we're now alive */
	rest_init();
	/*
	 * Avoid stack canaries in callers of boot_init_stack_canary for gcc-10
	 * and older.
	 */
#if !__has_attribute(__no_stack_protector__)
	prevent_tail_call_optimization();
#endif
}
```

## 内核代码执行

通常的执行路径是：
1. 通过用户进程发起的系统调用（system call）
2. 通过硬件触发的中断处理程序（interrupt handlers）
3. 在内核空间中运行的长期存在的内核线程（kernel threads)

> 由内核自身创建和管理的线程处理后台任务，例如内存回收、I/O 调度和同步。
> 尽管它们出现在进程列表中（通常用方括号括起来），但它们不是用户空间的守护进程，也从不执行用户空间代码。

第一个这样的线程是 kthreadd，分配的 PID 为 2。
它在 rest_init() 函数的初始化最后阶段创建，负责生成所有其他内核线程。
就像 PID 1（init 或 systemd）启动用户空间一样，PID 2 标志着内核线程运行时的开始。

内核线程的数量不是固定的。
在系统启动时，系统可能会创建 20-40 个基本线程——每个核心对应一个用于软中断（soft IRQs）、 watchdog、迁移助手和早期工作队列的线程。
随着系统变得活跃，会根据需要为 I/O、内存管理、文件系统和设备驱动程序创建额外的线程。
在典型的现代 Linux 系统上，可能会同时运行 100-150 个内核线程，并随着工作负载动态扩展。

尽管可见，但内核线程不是独立程序。
内核本身不是运行的任务——它是一个永远存在的执行环境。
它是被进入的，而不是被调度的。它提供结构、控制和特权——使所有任务能够运行，同时作为任务本身保持不可见。

```
+-----------------------------------------------------------------------------------------+
|                                      User Space (Ring 3)                                |
|                                                                                         |
|   +------------------------------------+                                                |
|   |           User Process             |                                                |
|   |  PID > 1 | Virtual Memory | Stack  |                                                |
|   +------------------------------------+                                                |
|                                                                                         |
|   System Call Return (open(), read(), write(), ...)                                     |
|                                                                                         |
+----------------------------------------|------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------------+
|                                     Kernel Space (Ring 0)                               |
|                                                                                         |
|   +--------------------------------------------------------------------------+          |
|   |                          Linux Kernel                                    |          |
|   |                                                                          |          |
|   |  +----------------+  +----------------+  +----------------+  +----------------+     |
|   |  | Memory Mgmt    |  |   Scheduler    |  | Syscall Intf   |  | Interrupt Hdlr |     |
|   |  |     (mm/)      |  |  (kernel/sched)|  | (arch/, kernel)|  | (irq/, drivers)|     |
|   |  +----------------+  +----------------+  +----------------+  +----------------+     |
|   |                                                                          |          |
|   |  +----------------+  +----------------+  +----------------+               |          |
|   |  |   Filesystems  |  |   Networking   |  |    Security    |               |          |
|   |  +----------------+  +----------------+  +----------------+               |          |
|   +--------------------------------------------------------------------------+          |
|                                                                                         |
|   +------------------------------------+  +------------------------------------+        |
|   |        kthreadd (PID 2)           |  |           Kernel Threads           |        |
|   |     (Spawns kernel threads)       |  |  (kworker/*, I/O tasks, rcu_sched) |        |
|   +------------------------------------+  +------------------------------------+        |
|                                                                                         |
|   Hardware Interrupt (IRQ) Entry  <-----  Timer, Keyboard, NIC, ...                     |
|                                                                                         |
+----------------------------------------|------------------------------------------------+
                                         |
                                         V
+-----------------------------------------------------------------------------------------+
|                                      Hardware Layer                                     |
|                                                                                         |
|   +----------------+            +----------------+            +----------------+      |
|   |     CPU        |            |    Devices     |            |    Memory       |      |
|   |  (Cores)       |            |  (Disk, NIC,   |            |   (DRAM)        |      |
|   | Ring 0 & 3     |            |     USB)       |            |                 |      |
|   +----------------+            +----------------+            +----------------+      |
|                                                                                         |
+-----------------------------------------------------------------------------------------+

```

## 首要职责

内核存在的意义是为用户进程服务。
确保每个进程可靠、安全且高效地运行。如果内核未能响应系统调用、分配内存、访问存储或实施隔离机制，则意味着其核心目标的失败。

即使是一个简单的读取调用也会跨越多个边界。
系统调用处理程序会从进程的任务结构（task structure）中验证文件描述符。
虚拟文件系统（Virtual File System，VFS）会定位关联的文件对象。
根据文件类型的不同，读取请求可能会发往普通文件、管道或套接字。
如果内存缓冲区位于未映射的页面上，内存管理器必须先解决缺页（page fault）问题，然后才能复制数据。
只有当所有这些操作都成功完成后，内核才会返回用户空间。

相同的模式适用于所有 I/O、网络和进程间通信。用户的每一个操作都会引发一系列内部协调工作。
内核的任何一个部分都无法单独交付结果，始终需要整个系统协同工作。

内核线程也不例外。当回收内存或刷新脏缓冲区时，它们并非为自身行动，而是为了保持系统健康，使用户进程能够持续运行。
它们的工作直接支持用户空间中正在进行或未来的执行。

这就是 Linux 内核的结构。每个子系统都围绕进程支持进行组织，每项内部服务的存在都是为了响应、支持或保护进程的执行。
它不是一个闲置的核心，而是一个响应式、协作式的系统。 内核的重要性并非在于它执行了许多任务，而在于它为其他事物提供服务时执行这些任务。

![linux runtime system](../resources/imgs/linux/101/kernel_runtime.png)

![syscall entry](../resources/imgs/linux/101/system_call_entry.png)

![hardware interrupt](../resources/imgs/linux/101/hardinterrupt.png)


## 分层: 虚拟、映射、隔离、控制

Linux 内核并未呈现单一、统一的系统视图，而是公开了许多受控视图——每个视图都与任务绑定，由上下文塑造，并受策略约束。这些视图并非动态组装而成，而是通过虚拟、映射、抽象、隔离和控制等层次构建而来。

这种结构的存在是为了在并发、抢占和硬件故障情况下使行为可预测。每个层都有定义好的作用域，没有任何一层是单独运行的。内核避免使用全局状态，而是依赖映射、间接和抽象，从而使访问是有意为之的，执行是受限的。

执行始于硬件边界。特定于体系结构的代码处理陷阱、故障和中断，定义了 CPU 如何响应系统调用或页面故障而进入内核。从一开始，内核就将执行与当前任务和调度上下文绑定。

任务并非自主运行，它们被排队、分配给 CPU，并根据需要被抢占。调度器执行策略和公平性。定时器、RCU（读-复制-更新）和延迟工作限制了并发性和时间安排。

抽象定义了内核公开功能的方式。系统调用作用于实现标准接口的内核对象。VFS（虚拟文件系统）抽象文件系统，块层抽象设备，网络栈抽象协议。像 file_operations 和 netdev_ops 这样的接口定义了行为，而不暴露实现。

调度遵循接口表。文件、套接字和设备不暴露内部结构。read() 或 ioctl() 等操作通过函数指针路由。行为是动态选择的，支持替换和模块化重用。

访问通过映射解析。文件描述符变为 file struct，虚拟地址变为物理页面，路径变为 dentry 和 inode。这些转换是任务范围的且经过验证，没有任何内容是直接访问的。

间接性强制分离。内核通过引用——函数表、 per - 任务指针、页表——而非直接访问来路由行为和访问。即使用户空间内存也被视为请求，通过 copy_from_user() 等助手函数解析。间接性确保所有访问都经过中介且具有上下文意识。

每个任务携带自己的上下文：内存映射、文件表、凭据、命名空间。这些结构定义了它能看到什么和做什么。Cgroups 限制使用，LSM（Linux 安全模块）执行策略。默认情况下不相信任何输入，每个转换都经过验证。

```
+----------------------------------------------------------------------------------------------------+
| LAYER 7 - USER SPACE INTERFACES                                                                    |
|                                                                                                    |
|   +----------------+  Syscall Stubs (glibc)   +-----------------+                                  |
|   | User Process   | -----------------------> | Syscall Entry:  |                                  |
|   | (read, execve) | <----------------------- | int 0x80/syscall|                                  |
|   +----------------+   Return Value          +-----------------+                                  |
|         |                                                     |                                    |
|         | Uses: VMA, signals, file descriptors                |                                    |
|         | Visible: /proc, /dev, namespaces                    |                                    |
+---------|-----------------------------------------------------|------------------------------------+
          |                                                     |
          |                                                     V
+---------|----------------------------------------------------------------------------------------+
|         |         LAYER 6 - CONTEXT & ISOLATION                                                 |
|         |                                                                                       |
|         |         +---------------------------+                                                 |
|         |         |        task_struct         |                                                 |
|         +-------> |---------------------------|                                                 |
|                   | - mm_struct (memory map)  |                                                 |
|                   | - files_struct (FDs)      |-----> Namespaces (PID, NET, USER...)            |
|                   | - cred (credentials)       |-----> Cgroups (CPU, memory, I/O)               |
|                   | - nsproxy (namespaces)    |-----> LSM & seccomp (SELinux, AppArmor)        |
|                   +---------------------------+                                                 |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
+--------------------------------------------------------------------------------------------------+
| LAYER 5 - MAPPING                                                                                |
|                                                                                                  |
|  +--------+    Page Tables     +-------+    VFS Lookup     +---------+                          |
|  | Virtual|------------------->|Physical|----------------->|  Inode   |                          |
|  | Address|    (MMU)           | Page  |  (dentry cache)   |---------|                          |
|  +--------+                    +-------+                   | - Blocks|---> Block Device           |
|       |                                                  | - Socket |---> Network Socket         |
|       | IOMMU (DMA)                                      | - Pipe   |---> Pipe/FIFO              |
|       |                                                  +---------+                          |
|       | Per-process: memory maps, FDs, device handles via VFS                                  |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
+--------------------------------------------------------------------------------------------------+
| LAYER 4 - INDIRECTION (Permeates all layers)                                                     |
|                                                                                                  |
|  +----------------+     +------------------+     +-----------------+                            |
|  | 'current' macro|     | Page Table Walk: |     | Deferred Work:  |                            |
|  | (per-CPU task) |     | PGD->PUD->PMD->PTE|     | softirqs,       |                            |
|  +----------------+     +------------------+     | workqueues      |                            |
|          |                  |                    +-----------------+                            |
|          |                  |                         |                                         |
|          V                  V                         V                                         |
|  +----------------+  +----------------+       +-------------------+                              |
|  | Operator ->/*  |  | Struct ops     |       | Jump Tables       |                              |
|  | (overloaded)   |  | (file_ops, etc)|       | (syscall table)   |                              |
|  +----------------+  +----------------+       +-------------------+                              |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
+--------------------------------------------------------------------------------------------------+
| LAYER 3 - ABSTRACTION                                                                            |
|                                                                                                  |
|  +--------------------------------------------------------------------+                         |
|  |                         Virtual File System (VFS)                  |                         |
|  | +-------------+  +-------------+  +-------------+  +-------------+ |                         |
|  | |    ext4     |  |   tmpfs     |  |    NFS      |  |   procfs    | |                         |
|  | +-------------+  +-------------+  +-------------+  +-------------+ |                         |
|  +--------------------------------------------------------------------+                         |
|                                                                                                  |
|  +--------------------------------------------------------------------+                         |
|  |                         Block Layer                              |                         |
|  | +-------------+  +-------------+  +-------------+                |                         |
|  | |    NVMe     |  |    SCSI     |  |   loopback  |                |                         |
|  | +-------------+  +-------------+  +-------------+                |                         |
|  +--------------------------------------------------------------------+                         |
|                                                                                                  |
|  +--------------------------------------------------------------------+                         |
|  |                         Network Stack                             |                         |
|  | +-------------+  +-------------+  +-------------+                |                         |
|  | |   AF_INET   |  |  AF_UNIX    |  |    VLANs    |                |                         |
|  | +-------------+  +-------------+  +-------------+                |                         |
|  +--------------------------------------------------------------------+                         |
|                                                                                                  |
|  Syscall Interface: read, write, ioctl --> Uniform access to all abstractions                    |
|  Devices: Exposed in /dev via major/minor numbers (devtmpfs)                                    |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
+--------------------------------------------------------------------------------------------------+
| LAYER 2 - SCHEDULING & EXECUTION CONTROL                                                         |
|                                                                                                  |
|  +----------------+     +----------------+     +-----------------+                               |
|  |   Scheduler    |     |   Runqueues    |     |   Context       |                               |
|  | (CFS, RT, DL)  |<-->| (per-CPU)      |<-->|   Switch        |                               |
|  +----------------+     +----------------+     +-----------------+                               |
|          ^                                                                                      |
|          |                                                                                      |
|  +----------------+     +----------------+     +-----------------+                               |
|  |   Preemption   |     |  Kernel Timer  |     |  Synchronization|                               |
|  |               |     | (jiffies, hrtimer)| | (locks, shared   |                               |
|  +----------------+     +----------------+     |    state)       |                               |
|                                                +-----------------+                               |
|                                                                                                  |
|  Background Mechanisms: softirqs, tasklets, workqueues for deferred execution                  |
|  Goals: Fairness, low latency, load balancing, per-task accounting                              |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
+--------------------------------------------------------------------------------------------------+
| LAYER 1 - HARDWARE INTERFACE & LOW-LEVEL ENTRY                                                   |
|                                                                                                  |
|  +----------------+     +----------------+     +-----------------+                               |
|  |   Trap &       |     |     MMU       |     |     IOMMU       |                               |
|  | Exception      |     |  Management   |     |  Management     |                               |
|  | Handlers       |     | (Paging,       |     | (DMA isolation) |                               |
|  | (syscall, page |     |  Protection)   |     |                 |                               |
|  | fault)         |     |               |     |                 |                               |
|  +----------------+     +----------------+     +-----------------+                               |
|          ^                                                                                      |
|          |                                                                                      |
|  +----------------+     +----------------+                                                       |
|  | Arch-Specific  |     |   Firmware    |                                                       |
|  | Boot & CPU Init|     | (ACPI, DT)    |                                                       |
|  | (vectors, seg) |     |               |                                                       |
|  +----------------+     +----------------+                                                       |
|                                                                                                  |
|  The Foundation: First code to run, sets up the environment for all higher layers.              |
+--------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  V
                                                                          
                                                                  []
                                                               (Hardware)
```

## 单体架构
Linux 内核在结构上是单体的。其核心子系统——调度、内存管理、文件系统、网络和驱动程序——被编译成单个二进制文件。
它们共享一个地址空间，以特权模式运行，并直接相互调用。在结构上没有隔离来分隔组件。
但在运行时，内核行为由所有子系统都必须遵循的系统级约束所塑造。

执行上下文决定了内何在任何时刻可以执行的操作。
代码在进程、内核线程、中断或软中断（softirq）上下文中运行。
进程和内核线程上下文允许睡眠、阻塞、用户内存访问和页面故障（page faults）处理。
中断和软中断上下文则不允许。
这些路径对时间敏感，并且不能阻塞或进行调度，因为这样做会延迟其他任务。
页面故障处理是不允许的，因为解决故障可能涉及 I/O、内存分配或回收，所有这些都需要睡眠。这些约束是全局适用的，并影响每个内核决策。

子系统通过这些共享规则进行交互。
调度器避免抢占原子路径。分配器在阻塞前检查上下文和标志。
文件系统通过从非阻塞状态到阻塞状态的有序转换来执行 I/O。
网络栈从中断上下文开始，经过软中断和工作队列。
设备驱动程序延迟无法安全就地完成的工作。
这不是惯例，而是设计。子系统将工作通过有效阶段进行处理，而不是一次性处理所有事情。

同步机制也反映了相同的原则。
自旋锁（spinlocks）用于原子路径。互斥锁（mutexes）仅在允许睡眠的地方使用。
RCU（读-复制-更新）使读取者能够在不锁定的情况下继续操作。顺序锁（Seqlocks）允许对更新进行快速重试。这些原语是基于上下文和访问模式选择的，而不是开发人员的偏好。用法通过宏、断言和在内核中一致执行的规则来验证。

内存访问遵循相同的模型。
访问用户内存需要进程上下文。
故障处理只能在允许睡眠的地方进行，因为解决故障可能涉及磁盘 I/O 或内存回收。
分配行为取决于标志和上下文。
同一个函数可能会阻塞、立即返回或失败，具体取决于它在哪里运行。内存管理要考虑可见性、局部性和上下文。

延迟执行将这些层连接起来。从中断开始的工作被传递到软中断，然后到工作队列，最后到内核线程。
每个步骤的设计都满足下一步的约束。这种分阶段模型支持 I/O、网络、定时器和驱动程序。

内核被构建为一个二进制文件，但它作为一个协同系统运行。
子系统不能独立运行。它们遵循由上下文、时间和并发性定义的共享模型。
它在形式上是单体的，但在执行上是模块化和有原则的。

```
=======================================================================
              LINUX KERNEL - CONSOLIDATED RUNTIME MODEL
=======================================================================

+-----------------------------+
|   [ Monolithic Binary ]     |
| Single compiled image (vmlinux) |
| All subsystems statically linked |
| One address space, shared kernel memory |
+-----------------------------+
              ↓
+-----------------------------+
|    [ Execution Contexts ]   |
+-----------------------------+
| • Process Context           |
|   → sleep, block, access user memory, handle faults |
| • Kernel Thread             |
|   → sleep, block, kernel-only memory |
| • SoftIRQ / Tasklet         |
|   → Non-blocking, limited scheduling |
| • IRQ Handler               |
|   → Non-blocking, atomic only |
+-----------------------------+
              ↓
+-----------------------------+
| [ Constraints by Context ]  |
+-----------------------------+
| • Blocking allowed only in sleepable context |
| • Page faults only where I/O and reclaim are legal |
| • spinlocks: atomic contexts only |
| • mutexes: sleepable contexts only |
| • User memory access forbidden in IRQ/SoftIRQ |
+-----------------------------+
              ↓
+-----------------------------+
|  [ Subsystem Interaction ]  |
+-----------------------------+
| • Scheduler avoids atomic preemption |
| • Memory allocator checks flags + context before sleep |
| • Filesystems defer blocking I/O via workqueues |
| • Networking: IRQ → SoftIRQ → Workqueue → Kernel thread |
| • Drivers schedule deferred work to continue safely |
+-----------------------------+
              ↓
+-----------------------------+
| [ Synchronization Mechanisms ] |
+-----------------------------+
| • spinlock  → atomic paths only |
| • mutex     → schedulable/sleepable paths only |
| • RCU       → lockless readers, synchronized updates |
| • seqlock   → fast retry-based reads |
+-----------------------------+
              ↓
+-----------------------------+
|      [ Memory Access ]      |
+-----------------------------+
| • Access user memory only in process context |
| • Fault handling disallowed in non-sleepable paths |
| • Allocation APIs vary by context and flags |
+-----------------------------+
              ↓
+-----------------------------+
| [ Deferred Execution Pipeline ] |
+-----------------------------+
| IRQ Handler → SoftIRQ → Workqueue → Kernel Thread |
| Each stage defers to the next to meet timing & blocking rules |
| The kernel is a monolith in code, but behavior is modular, |
| constrained, and context-driven. |
+-----------------------------+
```

## 并发安全

内核是围绕间接性、上下文感知，以及关键的无状态代码而设计的。

大多数内核代码避免使用持久的全局状态，不在函数内部跟踪“谁在调用”。
相反，它依赖外部上下文：一个通常通过 current 宏访问的 per - 线程指针，该指针告诉内核调用者的身份、可以访问的内存，以及拥有的文件或凭据。

这使得内核代码在功能上是无状态的。每次调用不依赖全局变量，仅对从调用线程上下文解析的数据进行操作。
这就是内核可重入的原因：同一个函数可以在多个 CPU 上为多个线程运行，而不会产生干扰。

以 sys_read() 为例，该函数对每个调用者来说看起来都一样。但在内部，它访问 current->files，使用线程自己的内核模式栈，并写入映射到该进程内存的缓冲区。代码路径是相同的，但每次运行看到的东西不同。

什么发生了变化？

输入、指针、引用。

这就是关键。逻辑保持共享，但数据是私有的。内核不会为每个线程重写函数，它只是遵循作用于活动任务的正确指针。

对于管道、缓存或套接字等共享数据，内核应用细粒度锁：自旋锁（spinlocks）、互斥锁（mutexes）和 per - CPU 结构，以最小化争用。在极高热度的路径中，它使用 RCU（读 - 复制 - 更新），这是一种无锁同步策略，允许读取者在更新并行发生时并发访问数据。RCU 是现代内核中可扩展读取性能的基石。

这种设计很强大，但它依赖于正确性。

如果内核跟随了错误的指针，一切都会崩溃。一个使用后释放（use - after - free）漏洞可能会留下对已重新用途内存的引用。缓冲区溢出可能会损坏相邻结构，改变线程所看到的内容，甚至劫持其身份。

这些漏洞会颠覆模型，违反上下文是私有的、隔离的和可信赖的保证。

但当设计得以维持时——当内存受到保护且指针有效时——内核会非常健壮。它能同时安全且高效地处理数千个线程。

内核并不避免并发，而是为并发而构建。

它的代码是通用的，但执行始终是特定的——由间接性驱动，由隔离保护，并且结构上避免假设。
```
=======================================================================
          MULTI-THREAD CONCURRENCY + REENTRANT KERNEL CODE
=======================================================================

+----------------+               +----------------+
| User Process A |               | User Process B |
| Thread A1      |               | Thread B1      |
+--------+-------+               +--------+-------+
         |                                |
   syscall: read()                    syscall: read()
         |                                |
         v                                v
+--------+-------+               +--------+-------+
| CPU 0 switches |               | CPU 1 switches |
| to kernel mode |               | to kernel mode |
+--------+-------+               +--------+-------+
         |                                |
         v                                v
+----------------+               +----------------+
| Kernel Stack   |               | Kernel Stack   |
| (Thread A1)    |               | (Thread B1)    |
| · local vars   |               | · local vars   |
| · saved regs   |               | · saved regs   |
+----------------+               +----------------+
         |                                |
         |      +------------------------+     |
         |      | SHARED KERNEL CODE     |     |
         +----> | (e.g. sys_read())      | <---+
                |                        |
                | fdtable = current->files
                | buf   = current->mm->buf
                | check = current->cred
                |                        |
                | [ Stateless: uses local stack, no globals ] |
                | [ Reentrant: runs safely on many threads ]  |
                +------------------------+
                         /\
                        /  \
 current (CPU 0 stack) /    \ current (CPU 1 stack)
          |            /      \           |
          v           /        \          v
   Task Struct A1    /          \   Task Struct B1
                     > Both CPUs run the SAME CODE
                       Each gets its OWN CONTEXT via 'current'
                       No shared stack or globals used
=======================================================================
```

## 硬件到`/dev`

磁盘驱动器不知道/dev/sda是什么，网卡也不知道eth0是什么。

而内核也不指望它们知道。

相反，内核维护着一个结构化模型——一个抽象的层级体系——弥合了物理硬件和用户空间可见的逻辑接口之间的差距。
从总线和中断到文件描述符和套接字API，这个模型定义了设备如何被发现、命名和使用。

这一切都始于总线。PCIe、USB、I²C——这些是设备用来自我宣告的通道。
内核的总线子系统（drivers/pci/、drivers/usb/等）扫描每条总线，探测连接的设备。
如果设备用可识别的厂商和类别响应，内核就会创建一个相应的内部对象（struct pci_dev、usb_device或i2c_client）并注册它。

## 内存

学习内存时，通常从图表入手：虚拟与物理、用户空间与内核空间、低内存与高内存。
这些图表很有帮助，它们为我们提供了一幅地图——内存的布局、地址空间中各部分的位置，以及系统的宏观架构。

但这种视角仍然是静态的。

它没有展示系统运行时内存的行为，没有展示页面如何分配、回收或移动，没有揭示内存如何在子系统之间共享或为硬件锁定，也没有解释为何某些内存永远不能交换，或为何一个分配器与另一个并存。
这些视图描述了内存的形态，却未说明内存的意义，以及内核如何有目的地使用它。

内核不将内存视为平坦空间来管理，而是将其视为责任。它根据每个子系统的工作方式，响应其需求。
内存不是以通用块的形式分配的，而是根据手头任务赋予相应的形式、结构和规则。

这就是内核称它们为子系统的原因。每个子系统本身就是一个系统。调度器移动线程并管理上下文，网络栈缓冲数据包并处理流控制，文件系统管理元数据、缓存和日志记录，驱动程序分配硬件可见的缓冲区，甚至内存管理器也会跟踪自身——区域、使用情况和回收策略。每个子系统请求内存时，不仅关注大小，还关注意图——如何使用、生命周期长短以及必须遵循的约束。

内核会倾听，并通过专注、轻量级的接口回应。kmalloc返回快速、对齐的内存供内核内部使用，Slab缓存为可重用的结构化固定大小对象提供服务，vmalloc从分散的物理页面创建虚拟连续的缓冲区，DMA API确保硬件访问的物理安全性，mmap为用户进程提供灵活、受保护的内存视图，并通过陷阱延迟填充和保护。这些不仅仅是API，更是代码与系统行为之间的契约。

每个请求都流经相同的核心分配器，但带有不同的标志、约束和假设。调用可以阻塞吗？内存需要固定吗？它是可移动的还是可回收的？是短期还是长期存在的？内核跟踪此上下文并相应地分配——无声、高效、持续地进行。

从外部看，内存似乎很简单：一个指针、一个段、一个页面。但在内核内部，内存不是平坦的——它是分层的、有形状的，并由需求决定。每个子系统不仅仅需要内存，还需要一个适合其功能的工作空间。内核不仅仅是分配，更是理解。

这就是它维持系统运行的方式。

从系统启动的那一刻起，内核就通过结构化方式管理内存。固件表定义可用区域，内核将其注册为物理段，分类到区域（zone）中，并为每个页面映射元数据。vmemmap区域为不连续的物理内存提供页面描述符的线性视图。分配器基础设施在用户空间启动前完成初始化。

每个物理页面由一个struct page表示。这些描述符被所有内存子系统使用——包括匿名内存、文件映射内存、slab、vmalloc、页面缓存和回收系统。它们始终被引用，任何分配、映射或回收操作都离不开它们。

每个进程被分配一个由mm_struct跟踪的虚拟地址空间，其中的区域由定义了边界和标志的vm_area_struct描述。这些区域在发生缺页（page fault）时延迟填充。内核遍历页表，安装中间层级，检查权限，并根据需要分配物理内存。匿名缺页分配新页面，文件映射缺页实例化folio并填充页面缓存。相同的匿名页面可通过KSM合并，大页面可通过THP提升。

回收是异步且分代的。内核扫描LRU列表或评估MGLRU代际。在压力下触发直接回收，Cgroups隔离内存域，收缩器（shrinker）释放子系统特定的缓存。回收的页面被逐出、交换或回写，DAMON可观察访问模式以优化策略。

ZSWAP和ZRAM提供压缩交换功能，页面在到达磁盘前在RAM中压缩。通过延迟分配和回收减少内存压力，页面迁移和NUMA平衡根据访问局部性重新定位页面，迁移由缺页或后台扫描触发。内存热插拔（memory hotplug）在运行时更新区域边界，ZONE_DEVICE支持CPU无法直接寻址的内存。

内核通过专用内部接口分配内存：页面分配器返回大块内存，slab分配器服务小对象，vmalloc提供虚拟连续区域，vmap将物理页面列表映射到连续虚拟范围，get_user_pages为内核或设备访问固定用户内存，ioremap创建内核可访问的设备内存映射。

内核不被动观察内存使用，而是在分配时强制边界，通过元数据跟踪所有权，并通过定义的规则恢复可用性。缺页解决访问问题，保护机制引发陷阱，回收解决不平衡，交换、压缩和迁移响应系统状态。没有轮询，没有被动监控。

内核将内存作为所有权和重用的分层系统进行管理——从启动到关闭，跨越架构、配置和工作负载。

一切都经过它，没有它则无物运行。
