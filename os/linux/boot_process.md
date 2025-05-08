# Linux startup process

主要以Linux kernel 2.6.24的ARM架构的启动过程为例.

## bootloader
以Uboot为例, `bootm addr` , 从Linux kernel所在起始地址启动.

### head.S
`/arch/arm/kernel/head.S` 为kernel的起始代码,对CPU和Memory做一下汇编级的初始化,最后 `#include "head-common.S"`

在同目录下的 `head-common.S` 最后调用跳转指令 `b start_kernel`,进入C语言级architecture-independent的初始化.

### start_kernel
函数 `start_kernel()` 在 `linux/init/main.c` 中,它不会放回到它的调用者那,它最终调用死循环函数 `cpu_idle()` .

中断们 `local_irq_disable()`, 仍然被关闭此时.做写必要的准备工作,然后打开它们.先 lock_kernel();

若打开 CONFIG_TRACE_IRQFLAGS , `early_init_irq_lock_class()`; 为一个全局中断描述符表格 `struct irq_desc irq_desc[NR_IRQS];` 中所有locks映射到单一的一个lock-class.

若打开 CONFIG_HIGHMEM, `page_address_init(void)` 初始化页地址,用链表把它们串起来.

### printk(linux_banner);
`printk(linux_banner)`; 打印字符串 linux_banner (这字符串在 linux/init/version.c 中). 

> Note: printk() 此时并没有实际把这字符串打印到终端,它只是缓存字符串直到终端设备把自己注册到内核.然后内核把缓存的终端log内容传递给注册的终端设备.同时可以存在多个注册的终端设备.

printk() can be called very early because it doesn't actually print to anywhere. It just logs the message to "log_buf" , which is allocated statically in "linux/kernel/printk.c". The messages that are saved in "log_buf" are passed to registered console devices as they register.

## 架构有关的初始化 setup_arch
Call setup_arch(&command_line); :

This performs architecture-specific initializations (details below). Then back to architecture-independent initialization

The remainder of start_kernel() is done as follows for all processor architecures, although several of these function calls are to architecture-specific setup/init functions.

## 继续architecture-independent初始化
### setup_command_line(command_line);

```
/*
 * We need to store the untouched command line for future reference.
 * We also need to store the touched command line since the parameter
 * parsing is performed in place, and we should allow a component to
 * store reference of name/value for future reference.
 */
strcpy (saved_command_line, boot_command_line);
strcpy (static_command_line, command_line);
```

### setup_per_cpu_areas();
设置下SMP的每个CPU分配pre-cpu结构内存， 并将.data.percpu段的数据复制到其中.

### smp_prepare_boot_cpu();
SMP相关,ARM架构下只是简单设置了下idle进程:
```c
void __init smp_prepare_boot_cpu(void)
{
  unsigned int cpu = smp_processor_id();
  per_cpu(cpu_data, cpu).idle = current;
}
```

### sched_init();
/kernel/sched.c

- set the struct task_struct init_task = INIT_TASK(init_task);.
- init idle thread, init_idle(current, smp_processor_id());.

### Parsing command line options
parse_early_param(); parse "eary options", as parse_args("early options", tmp_cmdline, NULL, 0, do_early_param);

parse_args: Parse the kernel options on the command line. This is a simple kernel command line parsing function. It parses the command line and fills in the arguments and environment to init (thread) as appropriate. Any command-line option is taken to be an environment variable if it contains the character '='. It also checks for options meant for the kernel by calling unknown_bootoption, and in it call obsolete_checksetup() ,hich checks the command line for kernel parameters, these being specified by declaring them using "__setup", as in:
```
__setup("debug", debug_kernel);
```

This declaration causes the debug_kernel() function to be called when the string "debug" is scanned. See "linux/Documentation/kernel-parameters.txt" for the list of kernel parameters.

These options are not given to init – they are for internal kernel use only. The default argument list for the init thread is {"init", NULL}, with a maximum of 8 command-line arguments. The default environment list for the init thread is {"HOME=/", "TERM=linux", NULL}, with a maximum of 8 command-line environment variable settings.

### sort_main_extable();
Sort the kernel's built-in exception table.

### trap_init();
in /arch/arm/kernel/traps.c. 对中断向量表进行初始化,如下:

unsigned long vectors = CONFIG_VECTORS_BASE;
memcpy((void *)vectors, __vectors_start, __vectors_end - __vectors_start);
memcpy((void *)vectors + 0x200, __stubs_start, __stubs_end - __stubs_start);
memcpy((void *)vectors + 0x1000 - kuser_sz, __kuser_helper_start, kuser_sz);

### init_IRQ();
arch/arm/kernel/irq.c
```
for (irq = 0; irq < NR_IRQS; irq++)
                irq_desc[irq].status |= IRQ_NOREQUEST | IRQ_NOPROBE;
```

初始化了从中断向量表，不过，这时的中断响应程序由于中断控制器的引脚还未被占用，自然是空程序了。当我们确切地知道了一个引脚到底连接了什么设备，并知道了该设备的驱动程序后，填写该引脚对应的中断门时，中断响应程序的偏移地址才被填写进中断向量表。
```
// in =setup_arch()=
init_arch_irq = mdesc->init_irq;
init_arch_irq();
Run architecture-specific initial irq.
```

### pidhash_init();
The pid hash table is scaled according to the amount of memory in the machine.

### init_timers();
初始化定时器:
```
open_softirq(TIMER_SOFTIRQ, run_timer_softirq, NULL);
```
### hrtimers_init();
初始化高精度时钟.

### softirq_init();
kernel/softirq.c 打开两个softirq:
```
open_softirq(TASKLET_SOFTIRQ, tasklet_action, NULL);
open_softirq(HI_SOFTIRQ, tasklet_hi_action, NULL);
```

### timekeeping_init();
kernel/time/timekeeping.c

Initializes the clocksource and common timekeeping values.

### time_init();
/arch/arm/kernel/time.c
```
// setup_arch()
system_timer = mdesc->timer;
system_timer->init();
```
以ARM的mach-smdk2410为例,初始化 timer_startval , timer_usec_ticks 和安装 IRQ_TIMER4.
```
static void __init s3c2410_timer_init (void)
{
  s3c2410_timer_setup();
  setup_irq(IRQ_TIMER4, &s3c2410_timer_irq);
}
```

### console_init();
HACK ALERT! This is early. We're enabling the console before we've done PCI setups etc., and console_init() must be aware of this. But we do want output early, in case something goes wrong.

### lockdep_info();
=CONFIGLOCKDEP=打开,打印锁依赖信息.

### mem_init();
free each online node memory.
calculate the real number of pages we have in this system.
get_free_pages() can be used after mem_init().

### kmem_cache_init();
/mm/slab.c Called after the page allocator have been initialised and before smp_init().

create the cachecache.
create the kmalloc caches.
Replace the bootstrap head arrays.
Replace the bootstrap kmemlist3's.
resize the head arrays to their final sizes.
kmalloc() can be used after kmem_cache_sizes_init()

### calibrate_delay();
Calculate the "loops_per_jiffy" delay loop value and print it in BogoMIPS.

### some inits
pidmap_init();
pgtable_cache_init();
prio_tree_init();
anon_vma_init();

#### fork_init(num_physpages);
根据物理内存大小计算允许创建进程的数量. The default maximum number of threads is set to a safe value: the thread structures can take up at most half of memory.

max_threads = mempages / (8 * THREAD_SIZE / PAGE_SIZE);

#### proc_caches_init();
kernel/fork.c

Call kmem_cache_create() to create slab caches for signal_act (signal action), files_cache (files_struct), fs_cache (fs_struct), vm_area_struct, and mm_struct.

#### buffer_init(void)
/fs/buffer.c Call kmem_cache_create() to create slab caches for buffer_head.

#### vfs_caches_init(num_physpages);
vfs_caches_init(num_physpages);

Call kmem_cache_create() to create slab caches for names_cache, filp.
Call dcache_init() to create the dentry_cache and dentry_hashtable.

#### signals_init();
/kernel/signal.c

Call kmem_cache_create() to create the "sigqueue" SLAB cache.

#### proc_root_init();
linux/fs/proc/root.c

For CONFIG_PROC_FS configurations:

call proc_misc_init().
mkdir /proc/net.
for CONFIG_SYSVIPC, mkdir /proc/sysvipc.
mkdir /proc/fs.
mkdir /proc/driver.
call proc_tty_init().
mkdir /proc/bus.
for CONFIG_SYSCTL, mkdir /proc/sys.

#### check_bugs();
include/asm-arm/bugs.h ARM仅仅做 check_writebuffer_bugs().

#### rest_init();
Do the rest non-_init'ed, we're now alive

### rest_init
#### start init thread
We count on the initial thread going OK.

Like idlers, init is an unlocked kernel thread, which will make syscalls (and thus be locked).

kernel_thread(kernel_init, NULL, CLONE_FS | CLONE_SIGHAND);

#### create kthreadd thread
pid = kernel_thread(kthreadd, NULL, CLONE_FS | CLONE_FILES);

##### unlock_kernel();
Release the BKL.

##### schedule(); and cpu_idle();
This function remains as process number 0. Its purpose is to use up idle CPU cycles. If the kernel is configured for APM support or ACPI support, cpu_idle() invokes the supported power-saving features of these specifications. Otherwise it nominally executes a "hlt" instruction.

##### setup_arch(&command_line)
/arch/arm/kernel/setup.c

##### setup_processor
use processor_id look up the processor type, and do the initials.

##### setup_machine
use machine_arch_type look up the machine type, get the struct machine_desc *mdesc;.

### Set memory limits
Set values for the start of kernel code, end of kernel code, end of kernel data, and "_end" (end of kernel code = the "brk" address).
```
init_mm.start_code = (unsigned long) &_text;
init_mm.end_code   = (unsigned long) &_etext;
init_mm.end_data   = (unsigned long) &_edata;
init_mm.brk        = (unsigned long) &_end;
```

#### parse_cmdline(cmdline_p, from);
parsing of the command line.

#### cpu_init();
cpu_init dumps the cache information, initialises SMP specific information, and sets up the per-CPU stacks.

#### Set up various architecture-specific pointers
init_arch_irq = mdesc->init_irq;
system_timer = mdesc->timer;
init_machine = mdesc->init_machine;

### kernel_init thread
/init/main.c

The kernel_init thread begins at the kernel_init() function in "linux/init/main.c". This is always expected to be process number 1.

kernel_init() first locks the kernel.
do some smp prepare and initials
do_pre_smp_initcalls();
smp_init();
sched_init_smp();
cpuset_init_smp();
calls do_basic_setup() to perform lots of bus and device initialization {more detail below}. After do_basic_setup(), most kernel initialization has been completed.
init_post(); call free_initmem(); frees any memory that was specified as being for initialization only [marked with "__init", "__initdata", "__init_call", or "__initsetup"]
unlocks the kernel (BKL).
init_post(); next opens /dev/console and duplicates that file descriptor two times to create stdin, stdout, and stderr files for init and all of its children.
Finally init_post(); tries to execute the command specified on the kernel parameters command line if there was one, or an init program or script if it can find one in {/sbin/init, /etc/init, /bin/init}, and lastly /bin/sh. If init_post(); cannot execute any of these, it panics("No init found. Try passing init= option to kernel.").

#### do_basic_setup
The machine is now initialized. None of the devices have been touched yet, but the CPU subsystem is up and running, and memory and process management works.

init_workqueues();
usermodehelper_init(); : khelper_wq = create_singlethread_workqueue("khelper");
driver_init();: initial many devices and buses.
void __init driver_init(void)
{
        /* These are the core pieces */
  devices_init();
  buses_init();
  classes_init();
  firmware_init();
  hypervisor_init();

  platform_bus_init();
  system_bus_init();
  cpu_dev_init();
  memory_dev_init();
  attribute_container_init();
}
init_irq_proc(); : create /proc/irq.
do_initcalls();: Call all functions marked as "_initcall"

#### do_initcalls
/init/main.c, this initializes many functions and some subsystems. The function is simple, just a loop call each initcall sub functions:

for (call = __initcall_start; call < __initcall_end; call++) {
}
__initcall_start and __initcall_end
They are in init section, in arch/xxx/kernel/vmlinux.lds.S:

 SECTIONS
 {
.init : {                       /* Init code and data           */
     __initcall_start = .;
     INITCALLS
         __initcall_end = .;
   }
 }
INITCALLS
It is defined in include/asm-generic/vmlinux.lds.h:

#define INITCALLS                                                       \
        *(.initcall0.init)                                              \
        *(.initcall0s.init)                                             \
        *(.initcall1.init)                                              \
        *(.initcall1s.init)                                             \
        *(.initcall2.init)                                              \
        *(.initcall2s.init)                                             \
        *(.initcall3.init)                                              \
        *(.initcall3s.init)                                             \
        *(.initcall4.init)                                              \
        *(.initcall4s.init)                                             \
        *(.initcall5.init)                                              \
        *(.initcall5s.init)                                             \
        *(.initcallrootfs.init)                                         \
        *(.initcall6.init)                                              \
        *(.initcall6s.init)                                             \
        *(.initcall7.init)                                              \
        *(.initcall7s.init)
initcall
Linux内核代码中有很多初始化标志 arch_initcall(fn), device_initcall(fn) 等,它们的定义在include/linux/init.h中:

#define pure_initcall(fn)               __define_initcall("0",fn,0)
#define core_initcall(fn)               __define_initcall("1",fn,1)
#define core_initcall_sync(fn)          __define_initcall("1s",fn,1s)
#define postcore_initcall(fn)           __define_initcall("2",fn,2)
#define postcore_initcall_sync(fn)      __define_initcall("2s",fn,2s)
#define arch_initcall(fn)               __define_initcall("3",fn,3)
#define arch_initcall_sync(fn)          __define_initcall("3s",fn,3s)
#define subsys_initcall(fn)             __define_initcall("4",fn,4)
#define subsys_initcall_sync(fn)        __define_initcall("4s",fn,4s)
#define fs_initcall(fn)                 __define_initcall("5",fn,5)
#define fs_initcall_sync(fn)            __define_initcall("5s",fn,5s)
#define rootfs_initcall(fn)             __define_initcall("rootfs",fn,rootfs)
#define device_initcall(fn)             __define_initcall("6",fn,6)
#define device_initcall_sync(fn)        __define_initcall("6s",fn,6s)
#define late_initcall(fn)               __define_initcall("7",fn,7)
#define late_initcall_sync(fn)          __define_initcall("7s",fn,7s)
__define_initcall 是个宏,如下:

#define __define_initcall(level,fn,id) \
        static initcall_t __initcall_##fn##id __attribute_used__ \
        __attribute__((__section__(".initcall" level ".init"))) = fn

typedef int (*initcall_t)(void);
initcall 是函数指针,所以定义了名为 __initcall_##fn##id 的函数指针.
函数指针指向函数fn.
__attribute__((__section__(".initcall" level ".init")) 表示编译的时候把这个函数指针变量放置到名为 (".initcall" level ".init") 的 section中.
reference
cpu_idle

void cpu_idle(void) {
  local_fiq_enable();
  /* endless idle loop with no priority at all */
  while (1) {
    void (*idle)(void) = pm_idle;
    if (!idle)
      idle = default_idle;
    leds_event(led_idle_start);
    tick_nohz_stop_sched_tick();
    while (!need_resched())
      idle();
    leds_event(led_idle_end);
    tick_nohz_restart_sched_tick();
    preempt_enable_no_resched();
    schedule();
    preempt_disable();
  }
}
setup_arch
arch/arm/kernel/setup.c

void __init setup_arch(char **cmdline_p)
{
        struct tag *tags = (struct tag *)&init_tags;
        struct machine_desc *mdesc;
        char *from = default_command_line;

        setup_processor();
        mdesc = setup_machine(machine_arch_type);
        machine_name = mdesc->name;

        if (mdesc->soft_reboot)
                reboot_setup("s");

        if (__atags_pointer)
                tags = phys_to_virt(__atags_pointer);
        else if (mdesc->boot_params)
                tags = phys_to_virt(mdesc->boot_params);

#ifdef CONFIG_KEXEC
        kexec_boot_params_copy = virt_to_phys(kexec_boot_params_buf);
        kexec_boot_params = (unsigned long)kexec_boot_params_buf;
        if (__atags_pointer) {
                kexec_boot_params_address = __atags_pointer;
                memcpy((void *)kexec_boot_params, tags, KEXEC_BOOT_PARAMS_SIZE);
        } else if (mdesc->boot_params) {
                kexec_boot_params_address = mdesc->boot_params;
                memcpy((void *)kexec_boot_params, tags, KEXEC_BOOT_PARAMS_SIZE);
        }
#endif

        /*
         * If we have the old style parameters, convert them to
         * a tag list.
         */
        if (tags->hdr.tag != ATAG_CORE)
                convert_to_tag_list(tags);
        if (tags->hdr.tag != ATAG_CORE)
                tags = (struct tag *)&init_tags;

        if (mdesc->fixup)
                mdesc->fixup(mdesc, tags, &from, &meminfo);

        if (tags->hdr.tag == ATAG_CORE) {
                if (meminfo.nr_banks != 0)
                        squash_mem_tags(tags);
                parse_tags(tags);
        }

        init_mm.start_code = (unsigned long) &_text;
        init_mm.end_code   = (unsigned long) &_etext;
        init_mm.end_data   = (unsigned long) &_edata;
        init_mm.brk        = (unsigned long) &_end;

        memcpy(boot_command_line, from, COMMAND_LINE_SIZE);
        boot_command_line[COMMAND_LINE_SIZE-1] = '\0';
        parse_cmdline(cmdline_p, from);
        paging_init(&meminfo, mdesc);
        request_standard_resources(&meminfo, mdesc);

#ifdef CONFIG_SMP
        smp_init_cpus();
#endif

        cpu_init();

        /*
         * Set up various architecture-specific pointers
         */
        init_arch_irq = mdesc->init_irq;
        system_timer = mdesc->timer;
        init_machine = mdesc->init_machine;

#ifdef CONFIG_VT
#if defined(CONFIG_VGA_CONSOLE)
        conswitchp = &vga_con;
#elif defined(CONFIG_DUMMY_CONSOLE)
        conswitchp = &dummy_con;
#endif
#endif
}
kernel_init
/init/main.c

static int __init kernel_init(void * unused)
{
  lock_kernel();
  set_cpus_allowed(current, CPU_MASK_ALL);
  init_pid_ns.child_reaper = current;

  __set_special_pids(1, 1);
  cad_pid = task_pid(current);

  smp_prepare_cpus(max_cpus);

  do_pre_smp_initcalls();

  smp_init();
  sched_init_smp();

  cpuset_init_smp();

  do_basic_setup();

  if (!ramdisk_execute_command)
    ramdisk_execute_command = "/init";

  if (sys_access((const char __user *) ramdisk_execute_command, 0) != 0) {
    ramdisk_execute_command = NULL;
    prepare_namespace();
  }
  init_post();
  return 0;
}
init_post
static int noinline init_post(void)
{
  free_initmem();
  unlock_kernel();
  mark_rodata_ro();
  system_state = SYSTEM_RUNNING;
  numa_default_policy();

  if (sys_open((const char __user *) "/dev/console", O_RDWR, 0) < 0)
    printk(KERN_WARNING "Warning: unable to open an initial console.\n");

  (void) sys_dup(0);
  (void) sys_dup(0);

  if (ramdisk_execute_command) {
          run_init_process(ramdisk_execute_command);
          printk(KERN_WARNING "Failed to execute %s\n",
                 ramdisk_execute_command);
  }

  if (execute_command) {
    run_init_process(execute_command);
    printk(KERN_WARNING "Failed to execute %s.  Attempting "
           "defaults...\n", execute_command);
  }
  run_init_process("/sbin/init");
  run_init_process("/etc/init");
  run_init_process("/bin/init");
  run_init_process("/bin/sh");

  panic("No init found.  Try passing init= option to kernel.");
}
do_basic_setup
static void __init do_basic_setup(void)
{
  init_workqueues();
  usermodehelper_init();
  driver_init();
  init_irq_proc();
  do_initcalls();
}

copy from https://wiki.dreamrunner.org/public_html/Embedded-System/kernel/Linux-startup-process.html
